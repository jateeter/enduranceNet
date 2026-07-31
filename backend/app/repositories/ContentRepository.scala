package repositories

import models.{Event, HomepageAsset, LegacyRedirect, News, StreamEntry, StreamSource}
import play.api.db.slick.DatabaseConfigProvider
import slick.jdbc.JdbcProfile

import javax.inject.{Inject, Singleton}
import scala.concurrent.Future

@Singleton
class ContentRepository @Inject()(databaseConfigProvider: DatabaseConfigProvider) {
  private val dbConfig = databaseConfigProvider.get[JdbcProfile]

  import dbConfig._
  import profile.api._

  private class NewsTable(tag: Tag) extends Table[News](tag, "news") {
    def id = column[Long]("id", O.PrimaryKey)
    def title = column[String]("title")
    def summary = column[String]("summary")
    def content = column[String]("content")
    def author = column[String]("author")
    def publishedAt = column[String]("published_at")
    def category = column[String]("category")
    def imageUrl = column[Option[String]]("image_url")

    def * = (id, title, summary, content, author, publishedAt, category, imageUrl) <> ((News.apply _).tupled, News.unapply)
  }

  private class EventsTable(tag: Tag) extends Table[Event](tag, "events") {
    def id = column[Long]("id", O.PrimaryKey)
    def name = column[String]("name")
    def eventType = column[String]("event_type")
    def date = column[String]("event_date")
    def location = column[String]("location")
    def distance = column[String]("distance")
    def description = column[String]("description")
    def registrationUrl = column[Option[String]]("registration_url")

    def * = (id, name, eventType, date, location, distance, description, registrationUrl) <> ((Event.apply _).tupled, Event.unapply)
  }

  private class HomepageAssetsTable(tag: Tag) extends Table[HomepageAsset](tag, "homepage_assets") {
    def id = column[Long]("id", O.PrimaryKey)
    def placement = column[String]("placement")
    def title = column[String]("title")
    def imageUrl = column[String]("image_url")
    def linkUrl = column[String]("link_url")
    def altText = column[String]("alt_text")
    def sourceLegacyUrl = column[String]("source_legacy_url")
    def sourcePath = column[String]("source_path")
    def sortOrder = column[Int]("sort_order")

    def * = (id, placement, title, imageUrl, linkUrl, altText, sourceLegacyUrl, sourcePath, sortOrder) <> ((HomepageAsset.apply _).tupled, HomepageAsset.unapply)
  }

  private class LegacyRedirectsTable(tag: Tag) extends Table[LegacyRedirect](tag, "legacy_redirects") {
    def id = column[Long]("id", O.PrimaryKey)
    def legacyUrl = column[String]("legacy_url")
    def targetUrl = column[String]("target_url")
    def statusCode = column[Int]("status_code")
    def reason = column[String]("reason")

    def * = (id, legacyUrl, targetUrl, statusCode, reason) <> ((LegacyRedirect.apply _).tupled, LegacyRedirect.unapply)
  }

  private class StreamSourcesTable(tag: Tag) extends Table[StreamSource](tag, "stream_sources") {
    def id = column[Long]("id", O.PrimaryKey)
    def slug = column[String]("slug")
    def title = column[String]("title")
    def provider = column[String]("provider")
    def feedFormat = column[String]("feed_format")
    def remoteUrl = column[Option[String]]("remote_url")
    def localCachePath = column[Option[String]]("local_cache_path")
    def legacyUrl = column[Option[String]]("legacy_url")
    def defaultPresentation = column[String]("default_presentation")
    def active = column[Boolean]("active")
    def bloggerBlogId = column[Option[String]]("blogger_blog_id")
    def canonicalAtomUrl = column[Option[String]]("canonical_atom_url")
    def canonicalRssUrl = column[Option[String]]("canonical_rss_url")
    def latestCachedEntry = column[Option[String]]("latest_cached_entry")
    def streamGroup = column[Option[String]]("stream_group")
    def notes = column[Option[String]]("notes")

    def * = (id, slug, title, provider, feedFormat, remoteUrl, localCachePath, legacyUrl, defaultPresentation, active, bloggerBlogId, canonicalAtomUrl, canonicalRssUrl, latestCachedEntry, streamGroup, notes) <> ((StreamSource.apply _).tupled, StreamSource.unapply)
  }

  private class StreamEntriesTable(tag: Tag) extends Table[StreamEntry](tag, "stream_entries") {
    def id = column[Long]("id", O.PrimaryKey)
    def sourceId = column[Long]("source_id")
    def providerEntryId = column[String]("provider_entry_id")
    def title = column[String]("title")
    def summaryHtml = column[Option[String]]("summary_html")
    def contentHtml = column[Option[String]]("content_html")
    def author = column[Option[String]]("author")
    def publishedAt = column[Option[String]]("published_at")
    def updatedAt = column[Option[String]]("updated_at")
    def alternateUrl = column[Option[String]]("alternate_url")
    def selfUrl = column[Option[String]]("self_url")
    def relatedUrl = column[Option[String]]("related_url")
    def commentsUrl = column[Option[String]]("comments_url")
    def checksumSha256 = column[Option[String]]("checksum_sha256")

    def source = foreignKey("stream_entries_source_fk", sourceId, streamSources)(_.id)
    def * = (id, sourceId, providerEntryId, title, summaryHtml, contentHtml, author, publishedAt, updatedAt, alternateUrl, selfUrl, relatedUrl, commentsUrl, checksumSha256) <> ((StreamEntry.apply _).tupled, StreamEntry.unapply)
  }

  private val news = TableQuery[NewsTable]
  private val events = TableQuery[EventsTable]
  private val homepageAssets = TableQuery[HomepageAssetsTable]
  private val legacyRedirects = TableQuery[LegacyRedirectsTable]
  private val streamSources = TableQuery[StreamSourcesTable]
  private val streamEntries = TableQuery[StreamEntriesTable]

  def listNews(): Future[Seq[News]] =
    db.run(news.sortBy(item => (item.publishedAt.desc, item.id.desc)).result)

  def getNews(id: Long): Future[Option[News]] =
    db.run(news.filter(_.id === id).result.headOption)

  def listEvents(): Future[Seq[Event]] =
    db.run(events.sortBy(item => (item.date.asc, item.id.asc)).result)

  def getEvent(id: Long): Future[Option[Event]] =
    db.run(events.filter(_.id === id).result.headOption)

  def listHomepageAssets(): Future[Seq[HomepageAsset]] =
    db.run(homepageAssets.sortBy(asset => (asset.placement.asc, asset.sortOrder.asc, asset.id.asc)).result)

  def listLegacyRedirects(): Future[Seq[LegacyRedirect]] =
    db.run(legacyRedirects.sortBy(redirect => (redirect.legacyUrl.asc, redirect.id.asc)).result)

  def resolveLegacyRedirect(legacyUrl: String): Future[Option[LegacyRedirect]] =
    db.run(legacyRedirects.filter(_.legacyUrl === legacyUrl).result.headOption)

  def listStreamSources(): Future[Seq[StreamSource]] =
    db.run(streamSources.sortBy(source => (source.active.desc, source.title.asc, source.id.asc)).result)

  def getStreamSource(slug: String): Future[Option[StreamSource]] =
    db.run(streamSources.filter(_.slug === slug).result.headOption)

  def listStreamEntries(): Future[Seq[StreamEntry]] =
    db.run(streamEntries.sortBy(entry => (entry.publishedAt.desc.nullsLast, entry.id.desc)).result)

  def listStreamEntriesBySource(slug: String): Future[Seq[StreamEntry]] = {
    val query = for {
      source <- streamSources if source.slug === slug
      entry <- streamEntries if entry.sourceId === source.id
    } yield entry

    db.run(query.sortBy(entry => (entry.publishedAt.desc.nullsLast, entry.id.desc)).result)
  }
}

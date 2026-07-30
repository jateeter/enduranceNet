package repositories

import models.{Event, HomepageAsset, LegacyRedirect, News}
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

  private val news = TableQuery[NewsTable]
  private val events = TableQuery[EventsTable]
  private val homepageAssets = TableQuery[HomepageAssetsTable]
  private val legacyRedirects = TableQuery[LegacyRedirectsTable]

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
}

package repositories

import models.{Event, News}
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

  private val news = TableQuery[NewsTable]
  private val events = TableQuery[EventsTable]

  def listNews(): Future[Seq[News]] =
    db.run(news.sortBy(item => (item.publishedAt.desc, item.id.desc)).result)

  def getNews(id: Long): Future[Option[News]] =
    db.run(news.filter(_.id === id).result.headOption)

  def listEvents(): Future[Seq[Event]] =
    db.run(events.sortBy(item => (item.date.asc, item.id.asc)).result)

  def getEvent(id: Long): Future[Option[Event]] =
    db.run(events.filter(_.id === id).result.headOption)
}

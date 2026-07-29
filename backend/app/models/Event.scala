package models

import play.api.libs.json._

case class Event(
  id: Long,
  name: String,
  eventType: String,
  date: String,
  location: String,
  distance: String,
  description: String,
  registrationUrl: Option[String]
)

object Event {
  implicit val format: OFormat[Event] = Json.format[Event]

  val sampleEvents: List[Event] = List(
    Event(1, "Western States 100", "Ultra Running", "2025-06-28", "Squaw Valley, CA", "100 miles",
      "The world's oldest 100-mile trail running race through the Sierra Nevada mountains.", Some("https://www.wser.org")),
    Event(2, "IRONMAN World Championship", "Triathlon", "2025-10-11", "Kailua-Kona, HI", "140.6 miles",
      "The pinnacle of endurance sport - 2.4 mile swim, 112 mile bike, 26.2 mile run.", Some("https://www.ironman.com")),
    Event(3, "Tour de France", "Cycling", "2025-07-05", "Various, France", "3,400 km",
      "The most prestigious cycling race in the world spanning 21 stages.", None),
    Event(4, "Boston Marathon", "Running", "2026-04-20", "Boston, MA", "26.2 miles",
      "The world's oldest annual marathon and one of the six World Marathon Majors.", Some("https://www.baa.org")),
    Event(5, "Leadville Trail 100 Run", "Ultra Running", "2025-08-16", "Leadville, CO", "100 miles",
      "Race across the sky - high altitude ultramarathon at elevations above 10,000 feet.", Some("https://www.leadvilleraceseries.com")),
    Event(6, "IRONMAN 70.3 World Championship", "Triathlon", "2025-09-05", "Taupo, New Zealand", "70.3 miles",
      "Half IRONMAN world championship featuring top age group and professional athletes.", Some("https://www.ironman.com"))
  )
}

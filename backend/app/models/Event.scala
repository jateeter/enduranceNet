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
    Event(1, "Tevis Cup", "Endurance Ride", "2026-07-18", "California, USA", "100 miles",
      "Western States Trail Ride coverage with legacy event pages, photos, news anchors, and archive material.", Some("/international/USA/2026TevisCup/")),
    Event(2, "City of Rocks Pioneer", "Endurance Ride", "2026-06-01", "Idaho, USA", "25/50/55 miles",
      "Recurring Idaho endurance ride represented in the legacy tree by yearly microsites, stories, and galleries.", Some("/international/USA/2026CityOfRocks/")),
    Event(3, "Mongol Derby", "Expedition Endurance", "2026-08-01", "Mongolia", "1000 km",
      "International endurance adventure coverage with news, rider stories, and event archive pages.", Some("/international/Mongolia/2026MongolDerby/")),
    Event(4, "Tom Quilty Gold Cup", "Endurance Championship", "2026-07-01", "Australia", "160 km",
      "Australian championship coverage represented by event pages, news references, and historical archive entries.", Some("/international/Australia/2026TomQuilty/")),
    Event(5, "FEI Endurance World Championship", "Championship", "2026-11-01", "AlUla, Saudi Arabia", "160 km",
      "World championship coverage hub with team analyses, qualification explainers, and related Current News entries.", Some("/international/SaudiArabia/2026WorldEnduranceChampionship/")),
    Event(6, "Owyhee Endurance Rides", "Endurance Ride Series", "2026-10-01", "Idaho, USA", "Multiple distances",
      "Local ride-series content connected to advertiser pages, event archives, and gallery media.", Some("/oreana/owyheeendurancerides.html"))
  )
}

package models

import play.api.libs.json._

case class Athlete(
  id: Long,
  name: String,
  sport: String,
  country: String,
  bio: String,
  achievements: List[String],
  imageUrl: Option[String]
)

object Athlete {
  implicit val format: OFormat[Athlete] = Json.format[Athlete]

  val sampleAthletes: List[Athlete] = List(
    Athlete(1, "Steph Teeter", "Endurance Riding", "USA",
      "Endurance.Net publisher and long-time endurance riding organizer, photographer, and storyteller.",
      List("Endurance.Net publisher", "Owyhee endurance ride organizer", "International endurance coverage"),
      None),
    Athlete(2, "Merri Melde", "Endurance Riding", "USA",
      "Photographer and writer whose ride stories and galleries appear throughout the legacy archive.",
      List("Merri Travels archive", "Ride photographer", "Tevis Cup Magic author"),
      None),
    Athlete(3, "Arlene Morris", "Endurance Riding", "USA",
      "Southwest Idaho Trail & Distance Riders founder and accomplished AERC rider represented in legacy memorial content.",
      List("16,605 endurance miles", "AERC Hall of Fame horse Champagne", "USA squad member at 1990 WEG"),
      None),
    Athlete(4, "Angie Field Rochna", "Endurance Riding", "USA",
      "Endurance rider and community member represented in Featured Stories memorial content.",
      List("Featured Stories archive", "Ridecamp community history"),
      None),
    Athlete(5, "Sierra Fadwah", "Endurance Horse", "USA",
      "Legendary endurance sire with a dedicated legacy page in the source tree.",
      List("Dedicated legacy horse page", "Endurance breeding history"),
      None)
  )
}

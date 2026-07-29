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
    Athlete(1, "Kristian Blummenfelt", "Triathlon", "Norway",
      "Olympic champion and IRONMAN World Record holder. Known for his exceptional running ability off the bike.",
      List("2020 Olympic Champion", "2021 IRONMAN World Champion", "IRONMAN World Record Holder"),
      None),
    Athlete(2, "Courtney Dauwalter", "Ultra Running", "USA",
      "Dominant force in ultramarathon running, known for competing without pacing charts or GPS.",
      List("2x Western States Champion", "UTMB Champion", "Hardrock 100 Champion"),
      None),
    Athlete(3, "Jonas Vingegaard", "Cycling", "Denmark",
      "Two-time Tour de France champion who announced himself to the world with a stunning performance in 2022.",
      List("2022 Tour de France Champion", "2023 Tour de France Champion", "2025 Tour de France Champion"),
      None),
    Athlete(4, "Chelsea Sodaro", "Triathlon", "USA",
      "Professional triathlete and IRONMAN World Champion who triumphed at Kona on her debut.",
      List("2022 IRONMAN World Champion"),
      None),
    Athlete(5, "Jim Walmsley", "Ultra Running", "USA",
      "Record-setting ultrarunner known for his aggressive front-running style at Western States.",
      List("3x Western States Champion", "Hardrock 100 Course Record Holder", "UTMB Podium"),
      None)
  )
}

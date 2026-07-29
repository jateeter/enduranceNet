package models

import play.api.libs.json._

case class Result(
  id: Long,
  eventId: Long,
  eventName: String,
  athleteName: String,
  finishTime: String,
  place: Int,
  category: String,
  year: Int
)

object Result {
  implicit val format: OFormat[Result] = Json.format[Result]

  val sampleResults: List[Result] = List(
    Result(1, 1, "Tevis Cup", "Legacy results import pending", "TBD", 1, "100 Mile", 2026),
    Result(2, 2, "City of Rocks Pioneer", "Legacy results import pending", "TBD", 1, "50 Mile", 2026),
    Result(3, 3, "Mongol Derby", "Legacy results import pending", "TBD", 1, "Expedition", 2026),
    Result(4, 4, "Tom Quilty Gold Cup", "Legacy results import pending", "TBD", 1, "160 km", 2026),
    Result(5, 5, "FEI Endurance World Championship", "Legacy results import pending", "TBD", 1, "Championship", 2026),
    Result(6, 6, "Owyhee Endurance Rides", "Legacy results import pending", "TBD", 1, "Ride Series", 2026)
  )
}

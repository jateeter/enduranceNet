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
    Result(1, 1, "Western States 100", "Courtney Dauwalter", "14:53:09", 1, "Female Overall", 2025),
    Result(2, 1, "Western States 100", "Jim Walmsley", "14:46:27", 1, "Male Overall", 2025),
    Result(3, 2, "IRONMAN World Championship", "Kristian Blummenfelt", "7:27:53", 1, "Male Pro", 2024),
    Result(4, 2, "IRONMAN World Championship", "Chelsea Sodaro", "8:33:46", 1, "Female Pro", 2024),
    Result(5, 3, "Tour de France", "Jonas Vingegaard", "82:49:45", 1, "General Classification", 2025),
    Result(6, 4, "Boston Marathon", "Sisay Lemma", "2:06:17", 1, "Male Overall", 2025),
    Result(7, 4, "Boston Marathon", "Hellen Obiri", "2:20:54", 1, "Female Overall", 2025),
    Result(8, 5, "Leadville Trail 100 Run", "Dylan Bowman", "16:01:42", 1, "Male Overall", 2025)
  )
}

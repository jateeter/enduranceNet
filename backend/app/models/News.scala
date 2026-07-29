package models

import play.api.libs.json._

case class News(
  id: Long,
  title: String,
  summary: String,
  content: String,
  author: String,
  publishedAt: String,
  category: String,
  imageUrl: Option[String]
)

object News {
  implicit val format: OFormat[News] = Json.format[News]

  val sampleNews: List[News] = List(
    News(1, "Kristian Blummenfelt Breaks IRONMAN World Record",
      "Norwegian triathlete shatters the course record at Kona with a stunning performance.",
      "In a breathtaking display of athletic excellence, Kristian Blummenfelt of Norway shattered the IRONMAN World Championship course record in Kona, Hawaii. The Olympic champion crossed the finish line in 7:27:53, beating the previous record by over 10 minutes. Blummenfelt led from the bike leg, posting a blistering 4:03:00 bike split before a remarkable 2:41:20 marathon to seal his historic victory.",
      "Sarah Mitchell", "2025-10-12", "Triathlon", None),
    News(2, "Courtney Dauwalter Dominates Western States",
      "Ultrarunning superstar sets new course record at the prestigious 100-mile classic.",
      "Courtney Dauwalter cemented her legacy as one of the greatest ultrarunners of all time with a stunning course record performance at Western States 100. Running through the night across the Sierra Nevada, Dauwalter finished in 14:53:09, shattering the previous women's course record by nearly 50 minutes and finishing ahead of the majority of male competitors.",
      "James Chen", "2025-06-29", "Ultra Running", None),
    News(3, "Tour de France 2025: Stage-by-Stage Recap",
      "Jonas Vingegaard defends his title in an epic three-week battle through France.",
      "The 2025 Tour de France delivered three weeks of spectacular racing through the French countryside. Jonas Vingegaard of Denmark successfully defended his title, surviving challenges from Tadej Pogačar and Remco Evenepoel. The race featured 21 stages covering over 3,400 kilometers, with decisive moments in the Pyrenees and Alps mountain stages.",
      "Marie Dubois", "2025-07-28", "Cycling", None),
    News(4, "Running Shoe Technology in 2025: Carbon Plate Revolution Continues",
      "New super shoes are pushing the boundaries of what's possible in distance running.",
      "The carbon plate shoe revolution that began with Nike's Vaporfly continues to evolve at a rapid pace. Major manufacturers including Adidas, HOKA, and Saucony have released next-generation models featuring multi-layered foam compounds and redesigned carbon fiber plates that offer unprecedented energy return. Studies show these shoes can improve marathon times by 2-4% compared to traditional racing flats.",
      "Dr. Alex Thompson", "2025-06-15", "Gear", None),
    News(5, "Training Zones: Understanding Heart Rate Training for Endurance Athletes",
      "A comprehensive guide to polarized training and how to structure your training week.",
      "Heart rate zone training has become the cornerstone of effective endurance programming. Understanding how to balance easy, moderate, and hard efforts is crucial for long-term development without injury or burnout. The polarized model, advocated by researchers like Stephen Seiler, suggests spending approximately 80% of training time in Zone 1-2, with the remaining 20% at high intensity.",
      "Coach Jennifer Park", "2025-05-20", "Training", None)
  )
}

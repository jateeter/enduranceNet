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
    News(1, "2026 Tevis Cup Coverage",
      "Legacy event coverage for the Western States Trail Ride will migrate as an event microsite.",
      "The Tevis Cup is one of Endurance.Net's recurring high-value coverage areas. In the NextGen model it belongs to the event, event-page, gallery, result, and media asset domains rather than a generic endurance-sport news bucket.",
      "Endurance.Net", "2026-07-29", "Event Coverage", Some("/international/USA/2026TevisCup/banner_block.jpg")),
    News(2, "Current News Digest",
      "The live Current News page is a curated digest backed by PHP wrappers and internal content fragments.",
      "The legacy /CurrentNews/ route sets page metadata, includes the shared site header, renders indexInternal.html, and then includes the site trailer. Imported records must preserve anchors and source provenance for deep links.",
      "Endurance.Net", "2026-07-29", "Current News", Some("/images/banner_sm_right_newsblogs.jpg")),
    News(3, "2026 World Endurance Championship Hub",
      "Saudi Arabia WEC coverage spans a hub page, analysis pages, and current-news references.",
      "The WEC material should migrate as structured event coverage while retaining static analysis-page legacy URLs such as team analyses and qualification requirements.",
      "Endurance.Net", "2026-07-29", "International", Some("/international/SaudiArabia/2026WorldEnduranceChampionship/banner.jpg")),
    News(4, "Advertiser And Sponsor Content",
      "Advertiser records combine XML lists, logos, ad placements, and sponsor pages.",
      "The legacy advertiser surface is both editorial and commercial content. The canonical model separates advertiser metadata, media assets, placement, and provenance so active sponsors can be maintained without losing archive context.",
      "Endurance.Net", "2026-07-29", "Advertisers", Some("/ads/AdvertiserLogos/StephTeeterArt_100.jpg")),
    News(5, "Ridecamp Archive Preservation",
      "Ridecamp is a large static community archive with date and thread navigation.",
      "Ridecamp messages should remain addressable by legacy URL and be modeled separately from news articles so moderation, privacy, and archive-navigation concerns can be handled explicitly.",
      "Endurance.Net", "2026-07-29", "Ridecamp", None)
  )
}

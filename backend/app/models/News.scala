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
    News(4, "Butheeb selected as replacement host for the FEI Endurance World Championship 2026",
      "Featured WEC coverage from the legacy homepage and Featured Stories surface.",
      "The legacy homepage promotes the 2026 World Endurance Championship host update as both a current-news item and a featured story. The NextGen migration keeps that dual editorial role visible while preserving source provenance in later importer passes.",
      "Endurance.Net", "2026-07-29", "Featured Stories", Some("/international/SaudiArabia/2026WorldEnduranceChampionship/banner.jpg")),
    News(5, "Ann Kratochvil Passes Away",
      "Featured memorial content from the legacy Featured Stories page.",
      "Memorial and community-history pieces are a distinct part of Endurance.Net. They should remain discoverable beside event coverage and current news rather than being flattened into generic sport news.",
      "Endurance.Net", "2026-07-29", "Featured Stories", Some("/merri/102615/0909OC_430.jpg")),
    News(6, "Angie Field Rochna 1965 - 2026",
      "Featured memorial content from the legacy Featured Stories page.",
      "Featured Stories includes personal histories, memorials, and community records that need stable legacy deep links and careful archive treatment.",
      "Endurance.Net", "2026-07-29", "Featured Stories", None),
    News(7, "2026 Tahoe Rim photos by Bill Gore",
      "Current News photo coverage surfaced from the legacy weekly digest.",
      "Photo-led current-news entries should connect article summaries to gallery and media-asset records as the importer matures.",
      "Endurance.Net", "2026-07-29", "Current News", None),
    News(8, "China Equestrian endurance riding competition opens in north China county",
      "International current-news item from the legacy digest.",
      "Current News aggregates external reporting, local ride coverage, international competition updates, and Endurance.Net archive links.",
      "Endurance.Net", "2026-07-29", "Current News", None)
  )
}

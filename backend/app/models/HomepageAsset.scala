package models

import play.api.libs.json._

case class HomepageAsset(
  id: Long,
  placement: String,
  title: String,
  imageUrl: String,
  linkUrl: String,
  altText: String,
  sourceLegacyUrl: String,
  sourcePath: String,
  sortOrder: Int
)

object HomepageAsset {
  implicit val format: OFormat[HomepageAsset] = Json.format[HomepageAsset]
}

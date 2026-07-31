package models

import play.api.libs.json._

case class StreamSource(
  id: Long,
  slug: String,
  title: String,
  provider: String,
  feedFormat: String,
  remoteUrl: Option[String],
  localCachePath: Option[String],
  legacyUrl: Option[String],
  defaultPresentation: String,
  active: Boolean,
  bloggerBlogId: Option[String],
  canonicalAtomUrl: Option[String],
  canonicalRssUrl: Option[String],
  latestCachedEntry: Option[String],
  streamGroup: Option[String],
  notes: Option[String]
)

object StreamSource {
  implicit val format: OFormat[StreamSource] = Json.format[StreamSource]
}

case class StreamEntry(
  id: Long,
  sourceId: Long,
  providerEntryId: String,
  title: String,
  summaryHtml: Option[String],
  contentHtml: Option[String],
  author: Option[String],
  publishedAt: Option[String],
  updatedAt: Option[String],
  alternateUrl: Option[String],
  selfUrl: Option[String],
  relatedUrl: Option[String],
  commentsUrl: Option[String],
  checksumSha256: Option[String]
)

object StreamEntry {
  implicit val format: OFormat[StreamEntry] = Json.format[StreamEntry]
}

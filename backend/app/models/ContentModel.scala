package models

import play.api.libs.json._

case class SourceProvenance(
  sourcePath: String,
  legacyUrl: String,
  checksumSha256: Option[String],
  importBatchId: Option[String],
  parserVersion: Option[String]
)

object SourceProvenance {
  implicit val format: OFormat[SourceProvenance] = Json.format[SourceProvenance]
}

case class LegacySourceFile(
  id: Long,
  sourcePath: String,
  legacyUrl: Option[String],
  classification: String,
  sizeBytes: Option[Long],
  checksumSha256: Option[String],
  readable: Boolean,
  permissionMode: Option[String],
  lastScannedAt: String
)

object LegacySourceFile {
  implicit val format: OFormat[LegacySourceFile] = Json.format[LegacySourceFile]
}

case class MediaAsset(
  id: Long,
  sourcePath: String,
  legacyUrl: Option[String],
  mimeType: Option[String],
  width: Option[Int],
  height: Option[Int],
  checksumSha256: Option[String],
  title: Option[String],
  credit: Option[String],
  provenance: SourceProvenance
)

object MediaAsset {
  implicit val format: OFormat[MediaAsset] = Json.format[MediaAsset]
}

case class ContentReference(
  contentType: String,
  id: Long,
  title: String,
  legacyUrl: Option[String]
)

object ContentReference {
  implicit val format: OFormat[ContentReference] = Json.format[ContentReference]
}

case class ArticleContent(
  id: Long,
  title: String,
  summary: Option[String],
  bodyHtml: String,
  author: Option[String],
  publishedAt: Option[String],
  category: String,
  tags: List[String],
  heroImage: Option[MediaAsset],
  externalSourceUrl: Option[String],
  provenance: SourceProvenance
)

object ArticleContent {
  implicit val format: OFormat[ArticleContent] = Json.format[ArticleContent]
}

case class EventPage(
  id: Long,
  eventId: Long,
  title: String,
  bodyHtml: String,
  pageKind: String,
  legacyUrl: String,
  provenance: SourceProvenance
)

object EventPage {
  implicit val format: OFormat[EventPage] = Json.format[EventPage]
}

case class Gallery(
  id: Long,
  title: String,
  legacyUrl: String,
  eventId: Option[Long],
  assets: List[MediaAsset],
  provenance: SourceProvenance
)

object Gallery {
  implicit val format: OFormat[Gallery] = Json.format[Gallery]
}

case class Advertiser(
  id: Long,
  name: String,
  description: Option[String],
  websiteUrl: Option[String],
  logo: Option[MediaAsset],
  active: Boolean,
  placement: Option[String],
  provenance: SourceProvenance
)

object Advertiser {
  implicit val format: OFormat[Advertiser] = Json.format[Advertiser]
}

case class ClassifiedListing(
  id: Long,
  category: String,
  title: String,
  bodyHtml: String,
  status: Option[String],
  contactText: Option[String],
  media: List[MediaAsset],
  provenance: SourceProvenance
)

object ClassifiedListing {
  implicit val format: OFormat[ClassifiedListing] = Json.format[ClassifiedListing]
}

case class RidecampMessage(
  id: Long,
  subject: String,
  authorDisplay: Option[String],
  postedAt: Option[String],
  bodyHtml: String,
  archivePath: String,
  previousByDateUrl: Option[String],
  nextByDateUrl: Option[String],
  previousByThreadUrl: Option[String],
  nextByThreadUrl: Option[String],
  provenance: SourceProvenance
)

object RidecampMessage {
  implicit val format: OFormat[RidecampMessage] = Json.format[RidecampMessage]
}

case class StaticPage(
  id: Long,
  title: String,
  bodyHtml: String,
  legacyUrl: String,
  pageKind: String,
  provenance: SourceProvenance
)

object StaticPage {
  implicit val format: OFormat[StaticPage] = Json.format[StaticPage]
}

case class FeedEntry(
  id: Long,
  feedName: String,
  title: String,
  publishedAt: Option[String],
  sourceUrl: Option[String],
  summaryHtml: Option[String],
  relatedContent: Option[ContentReference],
  provenance: SourceProvenance
)

object FeedEntry {
  implicit val format: OFormat[FeedEntry] = Json.format[FeedEntry]
}

case class LegacyRedirect(
  id: Long,
  legacyUrl: String,
  targetUrl: String,
  statusCode: Int,
  reason: String
)

object LegacyRedirect {
  implicit val format: OFormat[LegacyRedirect] = Json.format[LegacyRedirect]
}

case class ImportBatch(
  id: String,
  sourceRoot: String,
  parserVersion: String,
  startedAt: String,
  completedAt: Option[String],
  filesSeen: Long,
  recordsImported: Long,
  failures: Long
)

object ImportBatch {
  implicit val format: OFormat[ImportBatch] = Json.format[ImportBatch]
}

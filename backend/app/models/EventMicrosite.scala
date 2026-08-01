package models

import play.api.libs.json._

case class EventMicrositeSection(
  id: String,
  title: String,
  kind: String,
  legacyUrl: String,
  summary: String,
  body: String,
  ctaLabel: String
)

case class EventMicrositeMedia(
  id: String,
  title: String,
  kind: String,
  publicUrl: String,
  sourcePath: String,
  altText: String,
  status: String
)

case class EventMicrositeBlocker(
  sourcePath: String,
  reason: String,
  status: String
)

case class EventMicrosite(
  eventId: Long,
  slug: String,
  title: String,
  subtitle: String,
  date: String,
  location: String,
  distance: String,
  heroImageUrl: String,
  legacyRootUrl: String,
  overview: String,
  sections: Seq[EventMicrositeSection],
  media: Seq[EventMicrositeMedia],
  blockers: Seq[EventMicrositeBlocker],
  legacyUrls: Seq[String]
)

object EventMicrosite {
  implicit val sectionFormat: OFormat[EventMicrositeSection] = Json.format[EventMicrositeSection]
  implicit val mediaFormat: OFormat[EventMicrositeMedia] = Json.format[EventMicrositeMedia]
  implicit val blockerFormat: OFormat[EventMicrositeBlocker] = Json.format[EventMicrositeBlocker]
  implicit val format: OFormat[EventMicrosite] = Json.format[EventMicrosite]

  val tevis2026: EventMicrosite = EventMicrosite(
    eventId = 1,
    slug = "2026-tevis-cup",
    title = "2026 Tevis Cup",
    subtitle = "Western States Trail Ride coverage hub",
    date = "2026-07-18",
    location = "California, USA",
    distance = "100 miles",
    heroImageUrl = "/international/USA/2026TevisCup/banner_block.jpg",
    legacyRootUrl = "/international/USA/2026TevisCup/",
    overview = "The 2026 Tevis Cup coverage is migrated as a cohesive event microsite that keeps the legacy Western States Trail Ride pages, notes, stories, photos, gallery wrappers, and results entry points together under one navigable event experience.",
    sections = Seq(
      EventMicrositeSection(
        id = "overview",
        title = "Event Hub",
        kind = "Overview",
        legacyUrl = "/international/USA/2026TevisCup/index.html",
        summary = "The legacy Tevis wrapper and internal content become the canonical overview for the event microsite.",
        body = "The migrated hub preserves the event identity, Tevis-specific masthead graphics, and source provenance while moving navigation into a consistent React event page.",
        ctaLabel = "Open Legacy Hub"
      ),
      EventMicrositeSection(
        id = "notes",
        title = "Ride Notes",
        kind = "Notes",
        legacyUrl = "/international/USA/2026TevisCup/notes.html",
        summary = "Notes pages and internal fragments are grouped as event reporting instead of detached PHP includes.",
        body = "The notes stream includes notes.html, notes01.html, notesInternal.html, and notes01Internal.html so reviewers can validate the content corpus before fuller editorial transformation.",
        ctaLabel = "Review Notes"
      ),
      EventMicrositeSection(
        id = "stories",
        title = "Stories",
        kind = "Stories",
        legacyUrl = "/international/USA/2026TevisCup/storyIndex.html",
        summary = "Story index and rider story pages are represented as a microsite section with direct legacy provenance.",
        body = "The current import tracks JayMero.html, JayMeroInternal.html, Virginia.html, VirginiaInternal.html, and storyIndex.html as the Tevis story set.",
        ctaLabel = "Browse Stories"
      ),
      EventMicrositeSection(
        id = "gallery",
        title = "Gallery And Media",
        kind = "Gallery",
        legacyUrl = "/international/USA/2026TevisCup/gallery.html",
        summary = "Gallery wrappers, photo indexes, rotator includes, and readable event media are surfaced as one visual section.",
        body = "The section gathers gallery.html, gallery/index.html, galleryInternal.html, galleryHeader.html, galleryTrailer.html, photoIndex.html, thumbnailRotator.html, specialGallery/index.html, and readable photo assets.",
        ctaLabel = "Open Gallery"
      ),
      EventMicrositeSection(
        id = "results",
        title = "Results Navigation",
        kind = "Results",
        legacyUrl = "/international/USA/2026TevisCup/resultsIndex.html",
        summary = "The results entry point remains visible while structured result rows continue to mature in the database.",
        body = "The microsite connects the legacy resultsIndex.html page to the NextGen results table so review can happen before the full results corpus is normalized.",
        ctaLabel = "View Results"
      )
    ),
    media = Seq(
      EventMicrositeMedia("tevis-logo", "Tevis Logo", "logo", "/international/USA/2026TevisCup/TevisLogo.jpg", "/Volumes/webstore/endurance.net/international/USA/2026TevisCup/TevisLogo.jpg", "Tevis Cup logo from the legacy event source tree.", "readable"),
      EventMicrositeMedia("buckle", "Tevis Buckle", "image", "/international/USA/2026TevisCup/Buckle.jpg", "/Volumes/webstore/endurance.net/international/USA/2026TevisCup/Buckle.jpg", "Tevis buckle event graphic.", "readable"),
      EventMicrositeMedia("banner", "Event Banner", "banner", "/international/USA/2026TevisCup/banner.png", "/Volumes/webstore/endurance.net/international/USA/2026TevisCup/banner.png", "2026 Tevis event banner source.", "readable"),
      EventMicrositeMedia("banner-block", "Homepage Banner Block", "banner", "/international/USA/2026TevisCup/banner_block.jpg", "/Volumes/webstore/endurance.net/international/USA/2026TevisCup/banner_block.jpg", "Readable Tevis banner block used by the event microsite hero.", "readable"),
      EventMicrositeMedia("flyover", "Trail Flyover", "image", "/international/USA/2026TevisCup/flyover.png", "/Volumes/webstore/endurance.net/international/USA/2026TevisCup/flyover.png", "Tevis trail flyover graphic.", "readable"),
      EventMicrositeMedia("chuck", "Photo: Chuck", "photo", "/international/USA/2026TevisCup/photos/Chuck.jpg", "/Volumes/webstore/endurance.net/international/USA/2026TevisCup/photos/Chuck.jpg", "Readable Tevis photo asset from the legacy photos directory.", "readable")
    ),
    blockers = Seq(
      EventMicrositeBlocker("/Volumes/webstore/endurance.net/international/USA/2026TevisCup/banner.jpg", "Permission denied during legacy media sweep.", "blocked"),
      EventMicrositeBlocker("/Volumes/webstore/endurance.net/international/USA/2026TevisCup/banner.psd", "Permission denied during legacy media sweep.", "blocked"),
      EventMicrositeBlocker("/Volumes/webstore/endurance.net/international/USA/2026TevisCup/banner_150.jpg", "Permission denied during legacy media sweep.", "blocked"),
      EventMicrositeBlocker("/Volumes/webstore/endurance.net/international/USA/2026TevisCup/banner_300.jpg", "Permission denied during legacy media sweep.", "blocked"),
      EventMicrositeBlocker("/Volumes/webstore/endurance.net/international/USA/2026TevisCup/banner_opaque.jpg", "Permission denied during legacy media sweep.", "blocked")
    ),
    legacyUrls = Seq(
      "/international/USA/2026TevisCup/",
      "/international/USA/2026TevisCup/index.html",
      "/international/USA/2026TevisCup/indexInternal.html",
      "/international/USA/2026TevisCup/eventHeader.html",
      "/international/USA/2026TevisCup/eventTrailer.html",
      "/international/USA/2026TevisCup/menuIndex.html",
      "/international/USA/2026TevisCup/storyIndex.html",
      "/international/USA/2026TevisCup/notes.html",
      "/international/USA/2026TevisCup/notes01.html",
      "/international/USA/2026TevisCup/gallery.html",
      "/international/USA/2026TevisCup/gallery/index.html",
      "/international/USA/2026TevisCup/galleryInternal.html",
      "/international/USA/2026TevisCup/photoIndex.html",
      "/international/USA/2026TevisCup/resultsIndex.html",
      "/international/USA/2026TevisCup/rightDiv.html",
      "/international/USA/2026TevisCup/thumbnailRotator.html",
      "/international/USA/2026TevisCup/specialGallery/index.html"
    )
  )

  def findByEventId(eventId: Long): Option[EventMicrosite] =
    Option.when(eventId == tevis2026.eventId)(tevis2026)
}

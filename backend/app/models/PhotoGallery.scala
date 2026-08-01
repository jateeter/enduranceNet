package models

import play.api.libs.json.{Json, OFormat}

case class PhotoGalleryItem(
  id: String,
  position: Int,
  caption: String,
  thumbnailUrl: String,
  fullImageUrl: String,
  thumbnailSourcePath: String,
  fullImageSourcePath: String,
  itemPageSourcePath: String
)

object PhotoGalleryItem {
  implicit val format: OFormat[PhotoGalleryItem] = Json.format[PhotoGalleryItem]
}

case class PhotoGallery(
  id: String,
  slug: String,
  title: String,
  sourceRoot: String,
  legacyUrl: String,
  pattern: String,
  itemCount: Int,
  parserVersion: String,
  items: Seq[PhotoGalleryItem]
)

object PhotoGallery {
  implicit val format: OFormat[PhotoGallery] = Json.format[PhotoGallery]

  val sampleGalleries: Seq[PhotoGallery] = Seq(
    PhotoGallery(
      id = "gallery-e26bdc94e93622b5",
      slug = "2005pac-gallery-asadorss",
      title = "2005 PAC: Asadors Loop",
      sourceRoot = "2005PAC/Gallery/AsadorsS",
      legacyUrl = "/2005PAC/Gallery/AsadorsS/ThumbnailFrame.html",
      pattern = "framed-thumbnail",
      itemCount = 6,
      parserVersion = "photoshop-gallery-manifest-v1",
      items = Seq(
        item("gallery-e26bdc94e93622b5", "2005pac-gallery-asadorss", 1, "IMG 0005", "2005PAC/Gallery/AsadorsS", "IMG_0005"),
        item("gallery-e26bdc94e93622b5", "2005pac-gallery-asadorss", 2, "IMG 0006", "2005PAC/Gallery/AsadorsS", "IMG_0006"),
        item("gallery-e26bdc94e93622b5", "2005pac-gallery-asadorss", 3, "IMG 4748", "2005PAC/Gallery/AsadorsS", "IMG_4748"),
        item("gallery-e26bdc94e93622b5", "2005pac-gallery-asadorss", 4, "IMG 4749", "2005PAC/Gallery/AsadorsS", "IMG_4749"),
        item("gallery-e26bdc94e93622b5", "2005pac-gallery-asadorss", 5, "IMG 4750", "2005PAC/Gallery/AsadorsS", "IMG_4750"),
        item("gallery-e26bdc94e93622b5", "2005pac-gallery-asadorss", 6, "IMG 4751", "2005PAC/Gallery/AsadorsS", "IMG_4751")
      )
    ),
    PhotoGallery(
      id = "gallery-8d8c99b1819e0c2a",
      slug = "gallery-nov4-welcomereception",
      title = "November 3 - Welcome Reception",
      sourceRoot = "gallery/Nov4_WelcomeReception",
      legacyUrl = "/gallery/Nov4_WelcomeReception/index.html",
      pattern = "paginated-index",
      itemCount = 6,
      parserVersion = "photoshop-gallery-manifest-v1",
      items = Seq(
        item("gallery-8d8c99b1819e0c2a", "gallery-nov4-welcomereception", 1, "IMG 6570", "gallery/Nov4_WelcomeReception", "IMG_6570"),
        item("gallery-8d8c99b1819e0c2a", "gallery-nov4-welcomereception", 2, "IMG 6571", "gallery/Nov4_WelcomeReception", "IMG_6571"),
        item("gallery-8d8c99b1819e0c2a", "gallery-nov4-welcomereception", 3, "IMG 6572", "gallery/Nov4_WelcomeReception", "IMG_6572"),
        item("gallery-8d8c99b1819e0c2a", "gallery-nov4-welcomereception", 4, "IMG 6573", "gallery/Nov4_WelcomeReception", "IMG_6573"),
        item("gallery-8d8c99b1819e0c2a", "gallery-nov4-welcomereception", 5, "IMG 6574", "gallery/Nov4_WelcomeReception", "IMG_6574"),
        item("gallery-8d8c99b1819e0c2a", "gallery-nov4-welcomereception", 6, "IMG 6575", "gallery/Nov4_WelcomeReception", "IMG_6575")
      )
    )
  )

  private def item(galleryId: String, slug: String, position: Int, caption: String, root: String, stem: String): PhotoGalleryItem =
    PhotoGalleryItem(
      id = s"$galleryId-$position",
      position = position,
      caption = caption,
      thumbnailUrl = s"/media/galleries/$slug/thumbnails/$stem.jpg",
      fullImageUrl = s"/media/galleries/$slug/images/$stem.jpg",
      thumbnailSourcePath = s"$root/thumbnails/$stem.jpg",
      fullImageSourcePath = s"$root/images/$stem.jpg",
      itemPageSourcePath = s"$root/pages/$stem.html"
    )
}

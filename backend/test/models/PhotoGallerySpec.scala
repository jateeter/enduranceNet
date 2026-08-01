package models

import org.scalatestplus.play.PlaySpec

class PhotoGallerySpec extends PlaySpec {
  "PhotoGallery sampleGalleries" should {
    "use CMS media URLs for visible gallery images" in {
      val imageUrls = PhotoGallery.sampleGalleries.flatMap(_.items.flatMap(item => Seq(item.thumbnailUrl, item.fullImageUrl)))

      imageUrls must not be empty
      all(imageUrls) must startWith("/media/galleries/")
    }

    "preserve legacy source paths for provenance" in {
      val sourcePaths = PhotoGallery.sampleGalleries.flatMap(_.items.flatMap(item => Seq(item.thumbnailSourcePath, item.fullImageSourcePath)))

      sourcePaths must contain("2005PAC/Gallery/AsadorsS/thumbnails/IMG_0005.jpg")
      sourcePaths must contain("gallery/Nov4_WelcomeReception/thumbnails/IMG_6570.jpg")
    }
  }
}

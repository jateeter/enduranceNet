package controllers

import org.scalatestplus.play._
import org.scalatestplus.play.guice._
import play.api.test._
import play.api.test.Helpers._

class LegacyControllerSpec extends PlaySpec with GuiceOneAppPerTest with Injecting {

  "LegacyController#homepageAssets" should {
    "return migrated homepage asset manifest records" in {
      val controller = inject[LegacyController]
      val result = controller.homepageAssets().apply(FakeRequest(GET, "/api/homepage-assets"))
      val json = contentAsJson(result)

      status(result) mustBe OK
      contentType(result) mustBe Some("application/json")
      (json \\ "placement").map(_.as[String]) must contain("current_news_sponsor")
      (json \\ "placement").map(_.as[String]) must contain("advertiser")
    }
  }

  "LegacyController#redirects" should {
    "return known legacy deep-link redirect mappings" in {
      val controller = inject[LegacyController]
      val result = controller.redirects().apply(FakeRequest(GET, "/api/legacy-redirects"))
      val json = contentAsJson(result)

      status(result) mustBe OK
      contentType(result) mustBe Some("application/json")
      (json \\ "legacyUrl").map(_.as[String]) must contain("/FeaturedStories/#AnnKratochvil")
      (json \\ "legacyUrl").map(_.as[String]) must contain("/2005PAC/Gallery/AsadorsS/ThumbnailFrame.html")
      (json \\ "targetUrl").map(_.as[String]) must contain("/news/5")
      (json \\ "targetUrl").map(_.as[String]) must contain("/galleries/2005pac-gallery-asadorss")
    }
  }

  "LegacyController#resolveRedirect" should {
    "resolve a legacy wrapper path from the redirect table" in {
      val controller = inject[LegacyController]
      val result = controller.resolveRedirect().apply(FakeRequest(GET, "/api/legacy-redirects/resolve?url=/CurrentNews/"))
      val json = contentAsJson(result)

      status(result) mustBe OK
      (json \ "legacyUrl").as[String] mustBe "/CurrentNews/"
      (json \ "targetUrl").as[String] mustBe "/news"
      (json \ "statusCode").as[Int] mustBe 301
    }

    "resolve a known legacy anchor when the hash is encoded in the query value" in {
      val controller = inject[LegacyController]
      val result = controller.resolveRedirect().apply(FakeRequest(GET, "/api/legacy-redirects/resolve?url=/FeaturedStories/%23AnnKratochvil"))
      val json = contentAsJson(result)

      status(result) mustBe OK
      (json \ "legacyUrl").as[String] mustBe "/FeaturedStories/#AnnKratochvil"
      (json \ "targetUrl").as[String] mustBe "/news/5"
    }

    "resolve representative Photoshop gallery wrapper paths" in {
      val controller = inject[LegacyController]
      val result = controller.resolveRedirect().apply(FakeRequest(GET, "/api/legacy-redirects/resolve?url=/gallery/Nov4_WelcomeReception/index_2.html"))
      val json = contentAsJson(result)

      status(result) mustBe OK
      (json \ "legacyUrl").as[String] mustBe "/gallery/Nov4_WelcomeReception/index_2.html"
      (json \ "targetUrl").as[String] mustBe "/galleries/gallery-nov4-welcomereception"
      (json \ "statusCode").as[Int] mustBe 301
    }

    "return 404 for an unknown legacy path" in {
      val controller = inject[LegacyController]
      val result = controller.resolveRedirect().apply(FakeRequest(GET, "/api/legacy-redirects/resolve?url=/not-migrated.html"))

      status(result) mustBe NOT_FOUND
    }
  }
}

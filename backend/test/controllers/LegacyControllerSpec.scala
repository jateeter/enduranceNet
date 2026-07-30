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
      (json \\ "targetUrl").map(_.as[String]) must contain("/news/5")
    }
  }
}

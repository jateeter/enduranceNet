package controllers

import org.scalatestplus.play._
import org.scalatestplus.play.guice._
import play.api.test._
import play.api.test.Helpers._

class ApiControllerSpec extends PlaySpec with GuiceOneAppPerTest with Injecting {

  "ApiController#health" should {
    "return healthy status" in {
      val controller = inject[ApiController]
      val result = controller.health().apply(FakeRequest(GET, "/api/health"))
      status(result) mustBe OK
      contentType(result) mustBe Some("application/json")
      (contentAsJson(result) \\ "status").as[String] mustBe "healthy"
    }
  }
}

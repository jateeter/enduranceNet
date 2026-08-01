package controllers

import org.scalatestplus.play._
import org.scalatestplus.play.guice._
import play.api.test._
import play.api.test.Helpers._

class EventControllerSpec extends PlaySpec with GuiceOneAppPerTest with Injecting {

  "EventController#list" should {
    "return a list of events" in {
      val controller = inject[EventController]
      val result = controller.list().apply(FakeRequest(GET, "/api/events"))
      status(result) mustBe OK
      contentType(result) mustBe Some("application/json")
    }
  }

  "EventController#get" should {
    "return an event by ID" in {
      val controller = inject[EventController]
      val result = controller.get(1L).apply(FakeRequest(GET, "/api/events/1"))
      status(result) mustBe OK
    }

    "return 404 for unknown ID" in {
      val controller = inject[EventController]
      val result = controller.get(999L).apply(FakeRequest(GET, "/api/events/999"))
      status(result) mustBe NOT_FOUND
    }
  }

  "EventController#microsite" should {
    "return the 2026 Tevis microsite corpus" in {
      val controller = inject[EventController]
      val result = controller.microsite(1L).apply(FakeRequest(GET, "/api/events/1/microsite"))
      val json = contentAsJson(result)

      status(result) mustBe OK
      contentType(result) mustBe Some("application/json")
      (json \ "slug").as[String] mustBe "2026-tevis-cup"
      (json \\ "publicUrl").map(_.as[String]) must contain("/international/USA/2026TevisCup/banner_block.jpg")
      (json \\ "sourcePath").map(_.as[String]) must contain("/Volumes/webstore/endurance.net/international/USA/2026TevisCup/banner_150.jpg")
      (json \\ "legacyUrls").head.as[Seq[String]] must contain("/international/USA/2026TevisCup/resultsIndex.html")
    }

    "return 404 for events without a migrated microsite" in {
      val controller = inject[EventController]
      val result = controller.microsite(999L).apply(FakeRequest(GET, "/api/events/999/microsite"))

      status(result) mustBe NOT_FOUND
    }
  }
}

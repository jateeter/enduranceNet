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
}

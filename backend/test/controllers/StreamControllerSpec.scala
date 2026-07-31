package controllers

import org.scalatestplus.play._
import org.scalatestplus.play.guice._
import play.api.test._
import play.api.test.Helpers._

class StreamControllerSpec extends PlaySpec with GuiceOneAppPerTest with Injecting {

  "StreamController#sources" should {
    "return seeded Blogger and RSS stream sources" in {
      val controller = inject[StreamController]
      val result = controller.sources().apply(FakeRequest(GET, "/api/streams"))
      val json = contentAsJson(result)

      status(result) mustBe OK
      contentType(result) mustBe Some("application/json")
      (json \\ "slug").map(_.as[String]) must contain("where-in-the-world")
      (json \\ "defaultPresentation").map(_.as[String]) must contain("popup-channel-card")
    }
  }

  "StreamController#source" should {
    "return a stream source by slug" in {
      val controller = inject[StreamController]
      val result = controller.source("merri-travels").apply(FakeRequest(GET, "/api/streams/merri-travels"))
      val json = contentAsJson(result)

      status(result) mustBe OK
      (json \ "provider").as[String] mustBe "blogger-local-cache"
      (json \ "localCachePath").as[String] mustBe "/merri/MerriTravels.xml"
    }

    "return 404 for an unknown stream source" in {
      val controller = inject[StreamController]
      val result = controller.source("unknown").apply(FakeRequest(GET, "/api/streams/unknown"))

      status(result) mustBe NOT_FOUND
    }
  }

  "StreamController#entriesForSource" should {
    "return entries for a stream source" in {
      val controller = inject[StreamController]
      val result = controller.entriesForSource("wec-news").apply(FakeRequest(GET, "/api/streams/wec-news/entries"))
      val json = contentAsJson(result)

      status(result) mustBe OK
      (json \\ "providerEntryId").map(_.as[String]) must contain("tag:blogger.com,1999:blog-6751438")
      (json \\ "title").map(_.as[String]) must contain("2006 WEC Blogger archive")
    }
  }
}

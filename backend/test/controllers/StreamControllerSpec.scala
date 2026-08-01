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
      (json \\ "slug").map(_.as[String]) must contain("endurance-riding-news")
      (json \\ "canonicalRssUrl").map(_.as[String]) must contain("https://www.blogger.com/feeds/5099696/posts/default?alt=rss")
      (json \\ "streamGroup").map(_.as[String]) must contain("Active News")
    }
  }

  "StreamController#source" should {
    "return a stream source by slug" in {
      val controller = inject[StreamController]
      val result = controller.source("merri-travels").apply(FakeRequest(GET, "/api/streams/merri-travels"))
      val json = contentAsJson(result)

      status(result) mustBe OK
      (json \ "provider").as[String] mustBe "blogger"
      (json \ "bloggerBlogId").as[String] mustBe "4301230285143488965"
      (json \ "canonicalRssUrl").as[String] mustBe "https://www.blogger.com/feeds/4301230285143488965/posts/default?alt=rss"
      (json \ "streamGroup").as[String] mustBe "Photo & Travel Journals"
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
      val result = controller.entriesForSource("wec-reports").apply(FakeRequest(GET, "/api/streams/wec-reports/entries"))
      val json = contentAsJson(result)

      status(result) mustBe OK
      (json \\ "providerEntryId").map(_.as[String]) must contain("tag:blogger.com,1999:blog-6751438.post-5543622793139836893")
      (json \\ "title").map(_.as[String]) must contain("2026 Qualification Calendar: The Road to AlUla")
    }
  }

  "StreamController#searchEntries" should {
    "return entry results with source provenance" in {
      val controller = inject[StreamController]
      val result = controller.searchEntries().apply(FakeRequest(GET, "/api/stream-entries/search?q=wec"))
      val json = contentAsJson(result)

      status(result) mustBe OK
      (json \\ "title").map(_.as[String]) must contain("2026 Qualification Calendar: The Road to AlUla")
      (json \\ "slug").map(_.as[String]) must contain("wec-reports")
      (json \\ "streamGroup").map(_.as[String]) must contain("Event & Team Archives")
    }

    "filter entries by source group and archive status" in {
      val controller = inject[StreamController]
      val result = controller.searchEntries().apply(FakeRequest(GET, "/api/stream-entries/search?group=Photo%20%26%20Travel%20Journals&active=false"))
      val json = contentAsJson(result)

      status(result) mustBe OK
      (json \\ "slug").map(_.as[String]) must contain("where-in-the-world")
      (json \\ "slug").map(_.as[String]) must contain("merri-travels")
      (json \\ "streamGroup").map(_.as[String]).distinct mustBe Seq("Photo & Travel Journals")
    }
  }
}

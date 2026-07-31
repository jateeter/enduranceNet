package controllers

import play.api.libs.json._
import play.api.mvc._
import repositories.ContentRepository

import javax.inject._
import scala.concurrent.ExecutionContext

@Singleton
class StreamController @Inject()(val controllerComponents: ControllerComponents, contentRepository: ContentRepository)(implicit ec: ExecutionContext)
  extends BaseController {

  def sources(): Action[AnyContent] = Action.async {
    contentRepository.listStreamSources().map(sources => Ok(Json.toJson(sources)))
  }

  def source(slug: String): Action[AnyContent] = Action.async {
    contentRepository.getStreamSource(slug).map {
      case Some(source) => Ok(Json.toJson(source))
      case None         => NotFound(Json.obj("error" -> s"Stream source $slug not found"))
    }
  }

  def entries(): Action[AnyContent] = Action.async {
    contentRepository.listStreamEntries().map(entries => Ok(Json.toJson(entries)))
  }

  def searchEntries(): Action[AnyContent] = Action.async { request =>
    val active = request.getQueryString("active").flatMap {
      case "true" | "active"   => Some(true)
      case "false" | "archive" => Some(false)
      case _                    => None
    }

    contentRepository.searchStreamEntries(
      q = request.getQueryString("q"),
      group = request.getQueryString("group"),
      active = active,
      year = request.getQueryString("year")
    ).map(results => Ok(Json.toJson(results)))
  }

  def entriesForSource(slug: String): Action[AnyContent] = Action.async {
    contentRepository.getStreamSource(slug).flatMap {
      case Some(_) => contentRepository.listStreamEntriesBySource(slug).map(entries => Ok(Json.toJson(entries)))
      case None    => scala.concurrent.Future.successful(NotFound(Json.obj("error" -> s"Stream source $slug not found")))
    }
  }
}

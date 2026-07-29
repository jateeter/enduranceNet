package controllers

import models.News
import repositories.ContentRepository
import play.api.mvc._
import play.api.libs.json._
import javax.inject._
import scala.concurrent.ExecutionContext

@Singleton
class NewsController @Inject()(val controllerComponents: ControllerComponents, contentRepository: ContentRepository)(implicit ec: ExecutionContext)
  extends BaseController {

  def list(): Action[AnyContent] = Action.async {
    contentRepository.listNews().map(news => Ok(Json.toJson(news)))
  }

  def get(id: Long): Action[AnyContent] = Action.async {
    contentRepository.getNews(id).map {
      case Some(news) => Ok(Json.toJson(news))
      case None       => NotFound(Json.obj("error" -> s"News $id not found"))
    }
  }
}

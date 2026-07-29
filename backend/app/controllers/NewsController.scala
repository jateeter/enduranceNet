package controllers

import models.News
import play.api.mvc._
import play.api.libs.json._
import javax.inject._

@Singleton
class NewsController @Inject()(val controllerComponents: ControllerComponents)
  extends BaseController {

  def list(): Action[AnyContent] = Action {
    Ok(Json.toJson(News.sampleNews))
  }

  def get(id: Long): Action[AnyContent] = Action {
    News.sampleNews.find(_.id == id) match {
      case Some(news) => Ok(Json.toJson(news))
      case None       => NotFound(Json.obj("error" -> s"News $id not found"))
    }
  }
}

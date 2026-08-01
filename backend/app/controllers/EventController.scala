package controllers

import models.EventMicrosite
import repositories.ContentRepository
import play.api.mvc._
import play.api.libs.json._
import javax.inject._
import scala.concurrent.ExecutionContext

@Singleton
class EventController @Inject()(val controllerComponents: ControllerComponents, contentRepository: ContentRepository)(implicit ec: ExecutionContext)
  extends BaseController {

  def list(): Action[AnyContent] = Action.async {
    contentRepository.listEvents().map(events => Ok(Json.toJson(events)))
  }

  def get(id: Long): Action[AnyContent] = Action.async {
    contentRepository.getEvent(id).map {
      case Some(event) => Ok(Json.toJson(event))
      case None        => NotFound(Json.obj("error" -> s"Event $id not found"))
    }
  }

  def microsite(id: Long): Action[AnyContent] = Action {
    EventMicrosite.findByEventId(id) match {
      case Some(microsite) => Ok(Json.toJson(microsite))
      case None            => NotFound(Json.obj("error" -> s"Event microsite $id not found"))
    }
  }
}

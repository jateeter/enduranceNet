package controllers

import models.Event
import play.api.mvc._
import play.api.libs.json._
import javax.inject._

@Singleton
class EventController @Inject()(val controllerComponents: ControllerComponents)
  extends BaseController {

  def list(): Action[AnyContent] = Action {
    Ok(Json.toJson(Event.sampleEvents))
  }

  def get(id: Long): Action[AnyContent] = Action {
    Event.sampleEvents.find(_.id == id) match {
      case Some(event) => Ok(Json.toJson(event))
      case None        => NotFound(Json.obj("error" -> s"Event $id not found"))
    }
  }
}

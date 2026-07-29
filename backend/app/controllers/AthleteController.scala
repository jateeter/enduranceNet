package controllers

import models.Athlete
import play.api.mvc._
import play.api.libs.json._
import javax.inject._

@Singleton
class AthleteController @Inject()(val controllerComponents: ControllerComponents)
  extends BaseController {

  def list(): Action[AnyContent] = Action {
    Ok(Json.toJson(Athlete.sampleAthletes))
  }

  def get(id: Long): Action[AnyContent] = Action {
    Athlete.sampleAthletes.find(_.id == id) match {
      case Some(athlete) => Ok(Json.toJson(athlete))
      case None          => NotFound(Json.obj("error" -> s"Athlete $id not found"))
    }
  }
}

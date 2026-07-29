package controllers

import models.Result
import play.api.mvc._
import play.api.libs.json._
import javax.inject._

@Singleton
class ResultController @Inject()(val controllerComponents: ControllerComponents)
  extends BaseController {

  def list(): Action[AnyContent] = Action {
    Ok(Json.toJson(Result.sampleResults))
  }

  def byEvent(eventId: Long): Action[AnyContent] = Action {
    val results = Result.sampleResults.filter(_.eventId == eventId)
    Ok(Json.toJson(results))
  }
}

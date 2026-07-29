package controllers

import play.api.mvc._
import play.api.libs.json._
import javax.inject._

@Singleton
class HomeController @Inject()(val controllerComponents: ControllerComponents)
  extends BaseController {

  def index(): Action[AnyContent] = Action {
    Ok(Json.obj(
      "service" -> "endurancenet-api",
      "status" -> "running",
      "version" -> "1.0.0",
      "description" -> "EnduranceNet API - The next generation endurance sports platform"
    ))
  }
}

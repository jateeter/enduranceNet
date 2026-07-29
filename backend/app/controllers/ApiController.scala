package controllers

import play.api.mvc._
import play.api.libs.json._
import javax.inject._
import java.time.Instant

@Singleton
class ApiController @Inject()(val controllerComponents: ControllerComponents)
  extends BaseController {

  def health(): Action[AnyContent] = Action {
    Ok(Json.obj(
      "status" -> "healthy",
      "service" -> "endurancenet-api",
      "version" -> "1.0.0",
      "timestamp" -> Instant.now().toString
    ))
  }

  def preflight(path: String): Action[AnyContent] = Action {
    Ok("").withHeaders(
      "Access-Control-Allow-Origin" -> "*",
      "Access-Control-Allow-Methods" -> "GET, POST, PUT, DELETE, OPTIONS",
      "Access-Control-Allow-Headers" -> "Accept, Content-Type, Authorization"
    )
  }
}

package controllers

import repositories.ContentRepository
import play.api.libs.json._
import play.api.mvc._

import javax.inject._
import scala.concurrent.ExecutionContext

@Singleton
class LegacyController @Inject()(val controllerComponents: ControllerComponents, contentRepository: ContentRepository)(implicit ec: ExecutionContext)
  extends BaseController {

  def homepageAssets(): Action[AnyContent] = Action.async {
    contentRepository.listHomepageAssets().map(assets => Ok(Json.toJson(assets)))
  }

  def redirects(): Action[AnyContent] = Action.async {
    contentRepository.listLegacyRedirects().map(redirects => Ok(Json.toJson(redirects)))
  }

  def resolveRedirect(): Action[AnyContent] = Action.async { request =>
    request.getQueryString("url") match {
      case Some(legacyUrl) if legacyUrl.trim.nonEmpty =>
        contentRepository.resolveLegacyRedirect(legacyUrl.trim).map {
          case Some(redirect) => Ok(Json.toJson(redirect))
          case None           => NotFound(Json.obj("error" -> s"No legacy redirect for $legacyUrl"))
        }
      case _ =>
        scala.concurrent.Future.successful(BadRequest(Json.obj("error" -> "Missing required url query parameter")))
    }
  }
}

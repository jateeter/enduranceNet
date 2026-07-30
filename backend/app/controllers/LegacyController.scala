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
}

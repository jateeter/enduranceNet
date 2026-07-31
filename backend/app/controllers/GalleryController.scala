package controllers

import models.PhotoGallery
import play.api.libs.json.Json
import play.api.mvc.{AbstractController, Action, AnyContent, ControllerComponents}

import javax.inject.{Inject, Singleton}

@Singleton
class GalleryController @Inject()(cc: ControllerComponents) extends AbstractController(cc) {
  def list(): Action[AnyContent] = Action {
    Ok(Json.toJson(PhotoGallery.sampleGalleries))
  }

  def get(slug: String): Action[AnyContent] = Action {
    PhotoGallery.sampleGalleries.find(_.slug == slug) match {
      case Some(gallery) => Ok(Json.toJson(gallery))
      case None          => NotFound(Json.obj("error" -> s"Gallery $slug not found"))
    }
  }
}

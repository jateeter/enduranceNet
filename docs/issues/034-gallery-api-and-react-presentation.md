# Gallery API and React presentation

## Problem

The NextGen deployment needs a provable gallery presentation backed by migrated
gallery records rather than static legacy frames.

## Scope

- Add Scala API endpoints for gallery list and gallery detail records.
- Seed or import representative Photoshop gallery records for local preview.
- Add React routes for gallery index and detail views.
- Present thumbnails in a card/list grid with title, source context, item
  counts, and click-through full-image views.
- Reuse canonical legacy/CMS media URL helpers.

## Acceptance Criteria

- `GET /api/galleries` returns representative migrated gallery records.
- `GET /api/galleries/:slug` returns item-level thumbnail/full-image data.
- React route `/galleries` lists migrated galleries.
- React route `/galleries/:slug` presents a migrated gallery from the API.
- Localhost verification proves the gallery view renders without route errors.

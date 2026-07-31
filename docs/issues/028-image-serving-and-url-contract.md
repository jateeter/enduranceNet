# Image serving and URL contract

## Problem

NextGen currently relies on `/legacy-media/...` compatibility serving from the
legacy source mount. The image migration needs a clear runtime contract for both
compatibility URLs and future CMS-owned `/media/...` URLs so production is not
tied forever to `/Volumes/webstore/endurance.net/`.

## Scope

- Document and validate the container mount or object-storage shape for
  migrated images.
- Define how `/legacy-media/<source-path>` and `/media/<asset-id>/<filename>`
  are served in local, staging, and production.
- Add configuration checks that detect missing image roots before deployment
  claims are made.
- Preserve cache and content-type safeguards for served image assets.

## Acceptance Criteria

- Runtime docs identify the required image root variables and mount paths.
- Local/deployment verification can prove representative image URLs resolve.
- Missing image roots or broken mounts fail clearly.
- The contract supports eventual CMS/object-storage backing without changing
  public React routes.

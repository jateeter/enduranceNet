# Image Asset Migration Roadmap

The image migration now has enough foundation to move from compatibility
serving toward a durable NextGen asset platform. The current pipeline can
inventory legacy media, generate CMS-ready records, expose `/legacy-media/...`,
and report broken image elements in visual checks. Completion requires turning
that into an image-first corpus, deployment-safe serving, frontend rewrite
coverage, CMS synchronization, and release gates.

## Current State

- `/Volumes/webstore/endurance.net/` remains the authoritative source for
  legacy images.
- `scripts/media_asset_manifest.py` emits media/CMS manifests, duplicate
  reports, blocker reports, and optional staging copies.
- Docker/Nginx can serve `/legacy-media/<source-path>` from a read-only legacy
  media root in containerized deployment.
- React rewrites `endurance.net` and relative media URLs through
  `legacyAssetUrl`.
- Production visual checks report broken image elements across key routes.

## Completion Path

1. Generate an image-only staged corpus with stable IDs, checksums, dimensions,
   source paths, CMS URLs, duplicate groups, and copy/blocker reports.
2. Make container/runtime serving explicit for both compatibility
   `/legacy-media/...` URLs and future `/media/...` CMS URLs.
3. Expand frontend URL rewriting so all legacy image hosts and imported stream
   HTML use one canonical image URL pathway.
4. Add CMS/Directus handoff scripts or SQL for image records, blocker review,
   duplicate aliases, and editorial metadata fields.
5. Promote visual/media checks into release criteria, with reports that show
   route, viewport, image URL, source path, and screenshot artifact.
6. Run bounded and full-corpus import/staging jobs as deployment operations,
   not git commits; generated images remain outside the repository.

## Open Issue Map

- `027-image-only-corpus-staging.md`: image-only staged corpus and manifest
  outputs.
- `028-image-serving-and-url-contract.md`: runtime `/legacy-media` and `/media`
  serving contract.
- `029-frontend-image-url-rewrite-coverage.md`: frontend/imported HTML image
  URL rewriting coverage.
- `030-cms-image-sync-and-review.md`: CMS/Directus image sync and review model.
- `031-image-release-verification.md`: release gates for broken images and
  visual/media reports.

## Done Means

- Every readable legacy image has a stable asset ID and staged file location.
- Every unreadable, missing, duplicate, or externally hosted image is visible in
  a reviewable report.
- NextGen pages use canonical image URLs instead of ad hoc legacy paths.
- Containerized deployments can serve migrated image URLs without local-only
  assumptions.
- Visual/media regression checks fail releases on unwaived broken image loads.

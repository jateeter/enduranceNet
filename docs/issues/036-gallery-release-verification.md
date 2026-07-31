# Gallery release verification

## Problem

Gallery migration needs release checks that prove migrated gallery routes,
thumbnail images, full-size images, and blocker/waiver handling work in the
deployed app.

## Scope

- Add gallery routes to the production visual/media regression suite.
- Validate representative thumbnails and full-size images.
- Surface source path, gallery ID, item ID, image URL, waiver state, and
  screenshot artifact for failures.
- Document local and deployed verification commands.

## Acceptance Criteria

- Visual/media reports include `/galleries` and at least one gallery detail
  route.
- Strict mode fails on unwaived broken gallery images.
- Report-only mode remains available for exploratory corpus runs.
- Release docs name gallery artifact paths and waiver format.

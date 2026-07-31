# Image release verification gate

## Problem

Local visual checks can report broken images, but image migration needs a
release gate that distinguishes route failures, missing compatibility assets,
unimported CMS images, external image failures, and waived legacy blockers.

## Scope

- Extend visual/media regression reporting with image source path and canonical
  asset ID where available.
- Support waiver files for known unavailable legacy images.
- Fail releases on unwaived broken image elements or failed image requests.
- Preserve desktop/mobile screenshots for review.
- Document the exact command sequence for local and deployed verification.

## Acceptance Criteria

- Regression reports identify route, viewport, image URL, source path, status,
  waiver state, and screenshot artifact.
- The strict mode fails on unwaived image failures.
- Report-only mode remains available for exploratory migration runs.
- The release checklist names the image verification command and artifact path.

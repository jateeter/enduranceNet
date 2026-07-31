# Production visual and media regression checks

## Problem

The landing page and stream presentation modes now have local visual checks, but
the deployment still needs a repeatable production-facing walkthrough that
detects broken media, missing routes, and major visual regressions across the
most important migrated surfaces.

## Scope

- Add a production-capable Playwright smoke suite for landing, streams,
  stream-detail pages, search, events, galleries, advertisers/classifieds,
  Ridecamp archives, and representative legacy redirects.
- Capture desktop and mobile screenshots for visual review.
- Fail or report when migrated media returns 404, external image loads are
  blocked, or legacy redirects miss their target.
- Keep screenshots and reports in ignored artifact directories while publishing
  summary evidence in CI/deployment logs.
- Document the manual visual walkthrough checklist for releases.

## Acceptance Criteria

- The regression suite can run against local preview and deployed URLs.
- Reports identify page URL, viewport, missing image URL, redirect target, and
  screenshot artifact path for each failure.
- Representative migrated pages pass the suite before release claims are made.
- The release checklist names the visual/media command and expected artifact
  directory.

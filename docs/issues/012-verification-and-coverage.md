# Add migration verification and coverage reports

## Goal

Make completeness measurable before any production cutover.

## Scope

- Compare source inventory to imported records and asset manifests.
- Report skipped, failed, unreadable, duplicate, backup/temp, and waived files.
- Run link checks against migrated pages.
- Run media availability checks.
- Add Playwright smoke tests for core public routes.
- Document evidence buckets: static source inventory, import results, local
  runtime, and production deployment.

## Acceptance Criteria

- Coverage reports can be generated repeatably.
- No production-readiness claim is made without source, import, link, media, and
  runtime evidence.
- The reports identify remaining work by content domain.


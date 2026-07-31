# Media corpus CMS migration

## Problem

Legacy image and document URLs still generate 404s in the deployed NextGen
experience. The media bridge can detect and rewrite references, but the actual
corpus must be imported, verified, and eventually addressable through CMS-owned
asset records.

## Scope

- Inventory all media references from imported Blogger/RSS entries, legacy PHP
  pages, galleries, event microsites, advertisers, classifieds, and Ridecamp
  archives.
- Copy readable assets from `/Volumes/webstore/endurance.net/` into a controlled
  import staging area with checksums and source provenance.
- Record unreadable, missing, or permission-denied assets as explicit blockers.
- Create CMS-ready asset records with stable IDs, legacy URLs, MIME type, size,
  checksum, dimensions where available, and source context.
- Update rendering and redirect rules so migrated media resolves through the
  NextGen app while source links remain auditable.

## Acceptance Criteria

- A media import report lists imported, missing, unreadable, duplicate, and
  externally hosted assets.
- Each imported media asset has a CMS-ready record and a stable NextGen URL.
- Representative landing page, RSS stream, gallery, event, and archive media
  references resolve without 404s in local visual checks.
- Remaining permission-denied assets are linked to blocker records instead of
  being silently skipped.

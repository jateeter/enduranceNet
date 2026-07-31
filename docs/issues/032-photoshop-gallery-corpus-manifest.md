# Photoshop gallery corpus manifest

## Problem

Legacy Photoshop galleries are currently represented only as coarse gallery
manifest rows. The migration needs item-level records for thumbnails, full-size
images, page links, captions, ordering, gallery title, and source provenance.

## Scope

- Detect `ThumbnailFrame.html` and paginated `index*.html` Photoshop galleries.
- Parse thumbnail links, gallery item pages, full-size images, captions, and
  display order.
- Resolve relative paths to stable legacy source paths and `/legacy-media/...`
  URLs.
- Emit gallery manifests, gallery item manifests, blockers, duplicate/root
  summaries, and CMS-ready SQL/JSONL.
- Support bounded runs for smoke tests and full-corpus runs for deployment.

## Acceptance Criteria

- Fixture tests cover framed and paginated Photoshop gallery patterns.
- Operators can generate gallery and item JSONL reports from the inventory DB.
- Missing thumbnails/full images are reported as blockers.
- Summary output records gallery count, item count, blocker count, parser
  version, and bounded-run status.

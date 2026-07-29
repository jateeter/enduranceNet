# Resolve permission-denied source and media files

## Goal

Make every file needed for complete NextGen content migration readable, or mark
it with an explicit waiver and replacement plan.

## Background

Initial scans found permission-denied files under paths such as
`/Volumes/webstore/endurance.net/ClassifiedAds/photos/...`. These cannot be
ignored because classifieds, galleries, and archive pages may reference them.

## Scope

- Use the source inventory crawler report as the authoritative unreadable list.
- Group unreadable files by directory, owner, permission mode, and content area.
- Fix mount, filesystem, or source permissions outside the app code as needed.
- Re-run checksum and MIME classification after access is restored.
- Record waivers for any intentionally excluded files.

## Acceptance Criteria

- The unreadable-file report is empty, or every remaining file has a documented
  waiver.
- Media references from migrated pages can be resolved to readable assets.
- Completeness reports distinguish missing, unreadable, and intentionally
  excluded files.


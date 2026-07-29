# Define canonical content and provenance model

## Goal

Replace the placeholder multi-sport sample model with an Endurance.Net content
model that can represent the legacy site and the NextGen editorial workflow.

## Scope

- Define canonical entities for news, featured stories, events, event pages,
  galleries, media assets, advertisers, classifieds, Ridecamp messages, books,
  static pages, feeds, redirects, and legacy source files.
- Preserve source provenance on every imported record.
- Include legacy URL, source path, checksum, import batch, parser version, and
  publication status.
- Decide which entities are editable in NextGen and which are immutable archive
  records.

## Acceptance Criteria

- The schema can represent homepage news, event microsites, gallery pages,
  advertiser listings, and Ridecamp archive pages.
- No migrated record loses the original source path or legacy URL.
- Placeholder triathlon/running/cycling sample entities are removed or replaced.


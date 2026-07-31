# CMS image sync and review workflow

## Problem

The CMS media table and manifest records exist, but image migration completion
requires a repeatable handoff into Directus/CMS review workflows for alt text,
copyright/source notes, duplicate handling, missing files, and replacement
assets.

## Scope

- Generate CMS import SQL or JSON scoped to image assets.
- Include blocker rows for missing, unreadable, copy-failed, and externally
  hosted images.
- Define duplicate-image alias/replacement review fields.
- Document Directus collection/role expectations for image review.
- Keep provenance fields immutable during editorial correction.

## Acceptance Criteria

- Image records can be imported into `cms_media_assets` without non-image rows.
- Blocker records are importable or reviewable by image source path.
- Duplicate groups preserve source paths and checksums for editorial review.
- Documentation describes the Directus review workflow and required fields.

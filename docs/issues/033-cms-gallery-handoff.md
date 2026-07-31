# CMS gallery handoff

## Problem

Directus/CMS needs importable gallery collections, item collections, review
fields, and blocker workflows for the Photoshop gallery corpus.

## Scope

- Generate CMS/Directus JSONL or SQL for `cms_galleries`,
  `cms_gallery_items`, and `cms_gallery_blockers`.
- Preserve immutable provenance fields: source path, legacy URL, checksum,
  parser version, gallery root, thumbnail source, full-image source, and source
  page.
- Add editorial fields for title, caption, credit, copyright notes, review
  status, canonical media asset, and replacement asset.
- Document Directus collection and role expectations.

## Acceptance Criteria

- Gallery and item records can be imported without non-gallery rows.
- Blockers are reviewable by gallery ID and source path.
- Duplicate or replacement image review fields are present.
- Documentation defines immutable provenance versus editable fields.

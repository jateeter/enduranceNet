# CMS Gallery Review Workflow

Issue: https://github.com/jateeter/enduranceNet/issues/79

Build the Photoshop gallery manifest first:

```bash
python3 scripts/photoshop_gallery_manifest.py
```

Then build the Directus/CMS handoff bundle:

```bash
python3 scripts/cms_gallery_handoff.py --gallery-dir migration/galleries
```

Generated files are ignored under `migration/galleries/cms-handoff/`:

- `directus-galleries.jsonl`
- `directus-gallery-items.jsonl`
- `directus-gallery-blockers.jsonl`
- `directus-gallery-handoff-summary.json`

## Directus Collections

| Collection | Purpose |
| --- | --- |
| `cms_galleries` | Gallery root records and legacy provenance. |
| `cms_gallery_items` | Ordered thumbnail/full-image records. |
| `cms_gallery_blockers` | Missing, unreadable, or unresolved gallery assets. |

## Field Ownership

Immutable provenance fields:

- `id`
- `source_root`
- `entry_source_path`
- `legacy_url`
- `thumbnail_source_path`
- `item_page_source_path`
- `full_image_source_path`
- `checksum_sha256`
- `parser_version`

Editable review fields:

- `title`
- `caption`
- `credit`
- `copyright_notes`
- `review_status`
- `canonical_media_asset_id`
- `replacement_asset_id`
- `editor_notes`

Review blockers before publishing galleries. A blocker should stay open until
the source image is recovered, waived, or linked to a replacement CMS asset.

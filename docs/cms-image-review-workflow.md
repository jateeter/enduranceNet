# CMS Image Review Workflow

Issue: https://github.com/jateeter/enduranceNet/issues/69

The image CMS handoff starts from an image-only media manifest:

```bash
python3 scripts/media_asset_manifest.py --image-only --stage-assets --output-dir migration/media/images --staging-dir migration/media/images
python3 scripts/cms_image_handoff.py --media-dir migration/media/images
```

For full-corpus local review on a checkout that cannot hold another complete
copy of the legacy image tree, use link-backed CMS staging:

```bash
python3 scripts/media_asset_manifest.py \
  --image-only \
  --stage-assets \
  --stage-mode symlink \
  --symlink-root /var/www/legacy-media \
  --output-dir migration/media/images \
  --staging-dir migration/media/images
python3 scripts/cms_image_handoff.py --media-dir migration/media/images
```

The handoff writes ignored operational files under
`migration/media/images/cms-handoff/`:

- `directus-image-assets.jsonl`: image asset rows scoped to Directus/CMS import.
- `directus-image-blockers.jsonl`: missing, unreadable, copy-failed, or
  otherwise unresolved image rows for review.
- `directus-image-duplicates.jsonl`: checksum-based duplicate groups for
  canonical/replacement decisions.
- `directus-image-handoff-summary.json`: counts and field ownership notes.

## Directus Collections

Create or map these collections in Directus:

| Collection | Purpose |
| --- | --- |
| `cms_media_assets` | Imported image assets and immutable provenance. |
| `cms_media_blockers` | Open image migration blockers by source path or URL. |
| `cms_media_duplicate_groups` | Duplicate-image review groups keyed by checksum. |

## Field Ownership

Treat these provenance fields as immutable after import:

- `id`
- `source_path`
- `legacy_url`
- `public_url`
- `cms_public_url`
- `storage_key`
- `checksum_sha256`
- `source_context`
- `scanned_at`

Editors may update these review fields:

- `title`
- `alt_text`
- `credit`
- `copyright_notes`
- `review_status`
- `duplicate_group_id`
- `replacement_asset_id`
- `editor_notes`

## Review Flow

1. Import `directus-image-assets.jsonl` into `cms_media_assets`.
2. Import `directus-image-blockers.jsonl` into `cms_media_blockers`.
3. Import `directus-image-duplicates.jsonl` into
   `cms_media_duplicate_groups`.
4. Review blockers first; add `replacement_asset_id` or close rows only after
   the replacement file is present in the CMS media root.
5. Review duplicates by selecting one canonical image or recording a replacement
   image for each group.
6. Review editorial metadata: title, alt text, credit, and copyright notes.

The CMS workflow must preserve the generated public URLs. React pages can keep
using `/legacy-media/...` during compatibility serving and `/media/...` for
staged CMS images without route changes.

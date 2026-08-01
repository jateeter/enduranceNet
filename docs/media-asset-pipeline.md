# Media Asset Pipeline

`scripts/media_asset_manifest.py` turns the legacy source inventory into durable
media records and compares imported page references against those records.

## Usage

Generate a manifest from the current inventory and import staging database:

```bash
python3 scripts/media_asset_manifest.py
```

Generate CMS-ready asset records and copy readable media into an import staging
directory:

```bash
python3 scripts/media_asset_manifest.py --stage-assets --staging-dir migration/media/legacy-media
```

Generate an image-only corpus for the NextGen visual migration:

```bash
python3 scripts/media_asset_manifest.py --image-only --stage-assets --staging-dir migration/media/images
```

Generate the full image corpus with stable CMS URLs but without duplicating the
entire legacy image byte payload on local disk:

```bash
python3 scripts/media_asset_manifest.py \
  --image-only \
  --stage-assets \
  --stage-mode symlink \
  --symlink-root /var/www/legacy-media \
  --output-dir migration/media/images \
  --staging-dir migration/media/images
```

The symlink mode is intended for local/container review when the legacy media
root is mounted read-only at `/var/www/legacy-media`. It creates CMS storage
paths under `migration/media/images/legacy/...` that resolve inside the Nginx
container while avoiding a large duplicate copy in the repository checkout.

Run a bounded image-only smoke copy before launching the full corpus operation:

```bash
python3 scripts/media_asset_manifest.py --image-only --stage-assets --max-assets 100 --staging-dir migration/media/images-smoke
```

Optional PNG/GIF header probing:

```bash
python3 scripts/media_asset_manifest.py --probe-dimensions
```

Dimension probing is intentionally opt-in because checking every historical
image over the mounted legacy volume is much slower than source-inventory
accounting.

Fixture smoke test:

```bash
python3 scripts/test_media_asset_manifest.py
python3 scripts/test_cms_image_handoff.py
```

Generated files are intentionally ignored under `migration/media/`:

- `media-manifest.jsonl`: one asset/document record per readable legacy media
  file.
- `cms-media-assets.jsonl`: CMS-ready asset records with stable asset IDs,
  current `/legacy-media/...` URLs, future `/media/...` URLs, storage keys,
  staging status, provenance context, dimensions, checksums, and editor-facing
  metadata fields.
- `cms-media-import.sql`: Postgres import SQL for the `cms_media_assets` table.
- `cms-media-blockers.jsonl`: missing references, unreadable source media, and
  staging copy failures that need operator review.
- `media-summary.json`: counts by asset kind plus resolved, missing, external,
  unreadable, duplicate, blocker, staging, and waived reference totals.
- `missing-media-references.jsonl`: imported media references that do not
  resolve to a manifest entry.
- `external-media-references.jsonl`: remote HTTP(S) media references that are
  tracked separately from the local legacy media catalog.
- `unreadable-media.jsonl`: media/document source files that were inventoried
  but not readable.
- `duplicate-media-assets.jsonl`: same-checksum assets that may be collapsed or
  aliased by a future CMS workflow after editorial review.

Each manifest entry includes the source path, legacy URL, checksum, MIME type,
size, scanned timestamp, asset kind, optional PNG/GIF dimensions when probing is
enabled, a stable CMS asset ID, a durable public URL under `/legacy-media/`, and
a future CMS URL under `/media/`.

Use `--image-only` when preparing the visual corpus. In that mode manifest
rows, CMS records, duplicate reports, blocker reports, unreadable reports,
external reference reports, and staging copies are limited to image assets.
Use `--max-assets` for bounded smoke runs; `media-summary.json` records the
asset kind filter, the max asset limit, and whether the manifest is bounded.

## Runtime URL Contract

The Docker/Nginx stack serves compatibility and migrated media from explicit
read-only roots:

| Public URL | Container alias | Host variable | Default |
| --- | --- | --- | --- |
| `/legacy-media/<source-path>` | `/var/www/legacy-media/<source-path>` | `LEGACY_MEDIA_ROOT` | `/Volumes/webstore/endurance.net` |
| `/media/<asset-id>/<filename>` | `/var/www/cms-media/legacy/<asset-id>/<filename>` | `CMS_MEDIA_ROOT` | `./migration/media/images` |

The `/media/...` alias matches the generator's `cms_storage_key` value
`legacy/<asset-id>/<filename>`. That lets staged CMS media serve through stable
React-facing URLs now, and keeps the same public route available later if the
backing store moves to Directus-managed files or object storage.

For a full local sweep where disk space is not sufficient for a copied corpus,
use `--stage-mode symlink --symlink-root /var/www/legacy-media` and keep
`LEGACY_MEDIA_ROOT` mounted in the Nginx service. For durable production CMS
storage, rerun the same manifest with copy/object-storage ingestion so the CMS
owns the binary payload.

Set both roots before running containerized deployments:

```bash
LEGACY_MEDIA_ROOT=/Volumes/webstore/endurance.net \
CMS_MEDIA_ROOT=./migration/media/images \
docker compose up --build
```

Validate the roots and, when a staged manifest is available, representative
legacy and CMS image mappings:

```bash
python3 scripts/check_media_roots.py
python3 scripts/check_media_roots.py --manifest migration/media/images/media-manifest.jsonl --sample-size 10 --base-url http://localhost
```

`scripts/deploy.sh` runs the root-only check before rebuilding containers so
missing mounts fail clearly. The repo includes only `.gitkeep` placeholders
under `migration/media/legacy-media/` and `migration/media/images/`. Historical
images, documents, audio, and video must not be committed to git.

## CMS Image Handoff

After generating an image-only manifest, build Directus/CMS review bundles:

```bash
python3 scripts/cms_image_handoff.py --media-dir migration/media/images
```

See `docs/cms-image-review-workflow.md` for the Directus collection model,
immutable provenance fields, editable review fields, blocker handling, and
duplicate-image review flow.

## Release Gate

Before release, run the image manifest, media-root checks, and visual/media
regression gate together. See `docs/image-release-verification.md` for the
strict command sequence, waiver format, and report artifacts.

## Waivers

Known intentional gaps can be listed in a JSONL waiver file:

```json
{"referenced_path":"images/retired-logo.jpg","reason":"legacy source file intentionally withheld"}
```

Pass it with `--waivers path/to/waivers.jsonl`. Waived references remain visible
in `missing-media-references.jsonl` with a `waived: ...` reason so they are not
silently skipped.

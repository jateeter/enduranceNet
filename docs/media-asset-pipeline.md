# Media Asset Pipeline

`scripts/media_asset_manifest.py` turns the legacy source inventory into durable
media records and compares imported page references against those records.

## Usage

Generate a manifest from the current inventory and import staging database:

```bash
python3 scripts/media_asset_manifest.py
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
```

Generated files are intentionally ignored under `migration/media/`:

- `media-manifest.jsonl`: one asset/document record per readable legacy media
  file.
- `media-summary.json`: counts by asset kind plus resolved, missing, external,
  unreadable, and waived reference totals.
- `missing-media-references.jsonl`: imported media references that do not
  resolve to a manifest entry.
- `external-media-references.jsonl`: remote HTTP(S) media references that are
  tracked separately from the local legacy media catalog.
- `unreadable-media.jsonl`: media/document source files that were inventoried
  but not readable.

Each manifest entry includes the source path, legacy URL, checksum, MIME type,
size, scanned timestamp, asset kind, optional PNG/GIF dimensions when probing is
enabled, and a durable public URL under `/legacy-media/`.

## Runtime URL Contract

The Docker/Nginx stack serves `/legacy-media/<source-path>` from a read-only
mount at `/var/www/legacy-media/`. The default compose mount uses the local live
source tree at `/Volumes/webstore/endurance.net`. Set `LEGACY_MEDIA_ROOT` when
running somewhere else, or when serving from a copied media artifact directory:

```bash
LEGACY_MEDIA_ROOT=/Volumes/webstore/endurance.net docker compose up --build
```

The repo includes `migration/media/legacy-media/.gitkeep` only as an empty
local placeholder. Historical images, documents, audio, and video must not be
committed to git.

## Waivers

Known intentional gaps can be listed in a JSONL waiver file:

```json
{"referenced_path":"images/retired-logo.jpg","reason":"legacy source file intentionally withheld"}
```

Pass it with `--waivers path/to/waivers.jsonl`. Waived references remain visible
in `missing-media-references.jsonl` with a `waived: ...` reason so they are not
silently skipped.

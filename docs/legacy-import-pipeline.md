# Legacy Import Pipeline

`scripts/legacy_import.py` is the first migration import pipeline for the
mounted legacy Endurance.Net source tree.

It reads `migration/inventory/source-inventory.sqlite`, produced by
`scripts/source_inventory.py`, and writes an ignored staging database under
`migration/imports/`.

## Usage

Smoke test:

```bash
python3 scripts/legacy_import.py --reset --max-records 500
```

Full import from the current inventory snapshot:

```bash
python3 scripts/legacy_import.py --reset
```

## Imported Staging Tables

- `import_batches`: idempotent import batch metadata and parser version.
- `import_failures`: non-fatal file-level failures.
- `legacy_source_files`: provenance-preserving source manifest.
- `media_assets`: media records derived from inventory classifications.
- `template_pages`: PHP-capable `.html`, `.htm`, and `.php` route/template
  metadata.
- `content_fragments`: imported internal fragment bodies such as
  `indexInternal.html`.
- `feed_entries`: parsed XML/RSS/Atom entry records where feeds are readable.
- `media_references`: image/audio/video links found inside templates.

Generated outputs:

- `legacy-import.sqlite`
- `import-summary.json`
- `import-failures.jsonl`

The importer does not mutate `/Volumes/webstore/endurance.net/` and does not
write production content tables directly. The staging database is a reviewable
handoff point for later Postgres loading and domain-specific importers.


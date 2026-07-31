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

Unit smoke test:

```bash
python3 scripts/test_legacy_import.py
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
- `feed_entries`: parsed XML/RSS/Atom and OPML outline entry records where
  feeds are readable.
- `stream_sources`: Blogger/RSS/Atom/OPML source-level registry records with
  local cache paths, remote feed URLs where discoverable, default presentation
  modes, active/archive hints, checksums, and parser provenance.
- `stream_snapshots`: raw feed snapshot metadata, including feed ID, title,
  self/alternate/next links, item count, and checksum.
- `stream_entries_v2`: richer canonical stream entries with provider IDs,
  Blogger/RSS links, author, timestamps, summary/content HTML, and parser
  provenance.
- `structured_data_files`: XML/OPML/XSL/XSLT provenance, root tags, and parsed
  item counts, including files that do not expose feed entries directly.
- `media_references`: image/audio/video links found inside templates.
- `gallery_manifests`: gallery/index pages and their discovered media
  reference counts.
- `advertiser_records`: advertiser and sponsorship source pages with website
  and logo-reference hints.
- `classified_records`: classified/market archive pages with media-reference
  hints.
- `ridecamp_messages`: Ridecamp archive pages with message subject, body, and
  navigation link hints.

Generated outputs:

- `legacy-import.sqlite`
- `import-summary.json`
- `import-failures.jsonl`

The importer does not mutate `/Volumes/webstore/endurance.net/` and does not
write production content tables directly. The staging database is a reviewable
handoff point for later Postgres loading and domain-specific importers.

Every staging record keeps source path, legacy URL, parser version, import
batch ID, and checksum when available. Import failures are recorded without
aborting the batch so coverage reports can compare imported records to the
source inventory and expose remaining domain backlogs.

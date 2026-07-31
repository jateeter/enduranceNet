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

Full import plus active-feed polling:

```bash
python3 scripts/legacy_import.py --reset --poll-active
```

`--poll-active` reads the staging `stream_poll_targets` table after local feed
import, fetches targets marked `ready`, stores raw remote snapshots, upserts
normalized stream entries by provider entry ID, and records per-target failures
without aborting the import run. The default import remains network-free.

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
- `stream_raw_snapshots`: local-cache and remote-poll raw feed bodies with
  fetch URL, HTTP status, checksum, ETag, Last-Modified, parser version, and
  import batch provenance.
- `stream_poll_targets`: active feed refresh manifest with canonical poll URL,
  `rel="next"` paging hints, last checksum, ETag, Last-Modified, and
  ready/blocked status.
- `stream_entries_v2`: richer canonical stream entries with provider IDs,
  Blogger/RSS links, author, timestamps, summary/content HTML, and parser
  provenance.
- `structured_data_files`: XML/OPML/XSL/XSLT provenance, root tags, and parsed
  item counts, including files that do not expose feed entries directly.
- `media_references`: image/audio/video links found inside templates.
- `stream_media_references`: media and document links found inside imported
  stream entry HTML, including normalized `/legacy-media/...` URLs, referenced
  legacy paths, blocker text for unresolved/unreadable source assets, and a
  nullable `cms_asset_id` handoff field for the future CMS.
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

The staging poll manifest is intended as the cron handoff point. Existing
legacy cron jobs can be replaced by a scheduled `legacy_import.py --poll-active`
run once deployment storage and network policy are finalized. Poll failures are
also written to `import_failures` with importer `stream-poll`, so a failed live
feed does not block local archival import or unrelated feeds.

## Scheduled Poll Worker

After a staging database exists, scheduled jobs should use the focused poll
worker rather than re-running the full importer:

```bash
python3 scripts/poll_active_streams.py --staging-db migration/imports/legacy-import.sqlite --output-dir migration/imports
```

The worker reads `stream_poll_targets` rows marked `ready`, sends ETag and
Last-Modified headers when available, stores every successful remote response in
`stream_raw_snapshots`, and upserts normalized entries in `stream_entries_v2`.
It writes:

- `stream-poll-report.json`: batch ID, ready/blocked counts, imported entry
  count, raw snapshot deltas, latest HTTP status/checksum metadata, and target
  status details.
- `stream-poll-failures.jsonl`: per-target fetch or parse failures from the
  `import_failures` table.

By default the command exits non-zero when any target fails, which is useful for
cron or container scheduler alerting. Use `--allow-target-failures` when the
operator wants failed feeds recorded in the report without failing the outer job.

Example cron cadence matching the legacy background-refresh workflow:

```cron
*/30 * * * * cd /srv/enduranceNet && python3 scripts/poll_active_streams.py --staging-db migration/imports/legacy-import.sqlite --output-dir migration/imports
```

The importer does not mutate `/Volumes/webstore/endurance.net/` and does not
write production content tables directly. The staging database is a reviewable
handoff point for later Postgres loading and domain-specific importers.

Every staging record keeps source path, legacy URL, parser version, import
batch ID, and checksum when available. Import failures are recorded without
aborting the batch so coverage reports can compare imported records to the
source inventory and expose remaining domain backlogs.

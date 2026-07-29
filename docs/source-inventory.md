# Source Inventory Crawler

`scripts/source_inventory.py` inventories the mounted legacy source tree at
`/Volumes/webstore/endurance.net/`.

The crawler is intentionally read-only against the mounted site. It writes
resume state and reports under `migration/inventory/`, which is ignored except
for the placeholder `.gitkeep`.

## Usage

Smoke test:

```bash
python3 scripts/source_inventory.py --max-files 500 --reset
```

Full crawl:

```bash
python3 scripts/source_inventory.py --reset
```

Resume an interrupted crawl:

```bash
python3 scripts/source_inventory.py
```

Skip checksums when a fast structural pass is enough:

```bash
python3 scripts/source_inventory.py --no-checksum
```

## Outputs

- `source-inventory.sqlite`: resumable crawler database.
- `files.jsonl`: complete file/directory manifest.
- `unreadable.jsonl`: permission-denied and other unreadable entries.
- `unreadable.csv`: spreadsheet-friendly unreadable report.
- `template-includes.jsonl`: PHP include/require edges found in executable
  templates.
- `template-variables.jsonl`: common page variable assignments.
- `template-routes.jsonl`: executable-template route candidates with page
  metadata and common wrapper/include flags.
- `template-include-problems.jsonl`: dynamic, unresolved, or missing include
  targets that need follow-up.
- `summary.json`: counts by status and classification.

## Classification Rules

- `.html`, `.htm`, and `.php` are classified as executable templates.
- Common image, video, and audio extensions are classified as media assets.
- XML, Atom/RSS-like, XSLT, JSON, CSV, and text files are data files.
- Office/PDF files are documents.
- Editor backups and temp files are kept in the manifest but classified as
  backup/temp artifacts so they are not promoted into public content by default.

# Permission Access Resolution

Issue #5 tracked permission-denied source and media files from the mounted
legacy tree at `/Volumes/webstore/endurance.net`.

The current source-inventory SQLite database shows no unreadable records:

```sql
SELECT status, COUNT(*) FROM files GROUP BY status ORDER BY status;
-- ok|205058

SELECT classification, status, COUNT(*)
FROM files
WHERE status != 'ok'
GROUP BY classification, status;
-- no rows
```

File-level inventory breadth from the same database:

```sql
SELECT COUNT(*) FROM files WHERE kind = 'file';
-- 203211
```

The media manifest pipeline also reports no unreadable media/document records
against the current inventory:

```json
{
  "manifest_entries": 28449,
  "unreadable_media": 0,
  "resolved_media_references": 2878,
  "missing_media_references": 36,
  "external_media_references": 71
}
```

The remaining 36 local missing media references are content-reference backlog,
not permission-denied files. They are reported by
`missing-media-references.jsonl` and stay visible in the migration coverage
workflow until resolved or waived.

Re-run evidence commands:

```bash
sqlite3 'file:migration/inventory/source-inventory.sqlite?mode=ro&immutable=1' \
  "select status, count(*) from files group by status order by status;"

python3 scripts/media_asset_manifest.py \
  --inventory-db migration/inventory/source-inventory.sqlite \
  --import-db /private/tmp/endurance-import-smoke/legacy-import.sqlite \
  --source-root /Volumes/webstore/endurance.net \
  --output-dir /private/tmp/endurance-media-smoke
```

# Migration Coverage Reports

`scripts/migration_coverage.py` summarizes the source inventory database into
repeatable coverage reports.

Run it after an inventory crawl:

```bash
python3 scripts/migration_coverage.py
```

Outputs are written under `migration/coverage/`, which is ignored except for
`.gitkeep`.

Generated files:

- `coverage-summary.json`: machine-readable counts.
- `coverage-report.md`: human-readable source coverage summary.
- `unreadable-report.md`: permission-denied and unreadable source entries.
- `include-problems.md`: unresolved include edges from executable templates.

The report is intentionally evidence-oriented. It does not claim migration
completion by itself; it gives later importers and runtime checks a stable
source-inventory baseline to compare against.


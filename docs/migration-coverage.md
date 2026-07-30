# Migration Coverage Reports

`scripts/migration_coverage.py` summarizes the source inventory database and
current import summary into repeatable coverage reports.

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
- `domain-backlog.md`: source/import comparison by content domain.
- `verification-matrix.md`: evidence buckets required before a production
  readiness claim.

The report is intentionally evidence-oriented. It does not claim migration
completion by itself; it gives later importers and runtime checks a stable
source-inventory baseline to compare against.

## Link Checks

Use the legacy redirect checker from #12 against a running frontend and/or API:

```bash
python3 scripts/check_legacy_redirects.py --base-url http://localhost
python3 scripts/check_legacy_redirects.py --api-base-url http://localhost:9000
```

## Media Checks

Use the media manifest checker against a running API:

```bash
python3 scripts/check_media_manifest.py --api-base-url http://localhost:9000
```

This verifies the currently manifested homepage media URLs. It does not prove
the full legacy media catalog has been imported; that remains part of #11.

## Runtime Smoke

Use Playwright smoke screenshots against a running frontend:

```bash
python3 scripts/playwright_smoke.py --base-url http://127.0.0.1:18655
python3 scripts/playwright_smoke.py --base-url http://127.0.0.1:18655 --mobile
```

Screenshots are written under `output/playwright/`, which is intentionally
ignored by git.

## Evidence Rule

Do not claim production readiness unless current source, import, link, media,
and runtime evidence are all available and passing. Local checks, generated
reports, hosted CI, and production deployment proof must be described as
separate evidence buckets.

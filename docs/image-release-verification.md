# Image Release Verification

Issue: https://github.com/jateeter/enduranceNet/issues/70

Run the image release gate before claiming a migrated deployment is ready:

```bash
python3 scripts/media_asset_manifest.py --image-only --stage-assets --output-dir migration/media/images --staging-dir migration/media/images
python3 scripts/check_media_roots.py --manifest migration/media/images/media-manifest.jsonl --sample-size 10 --base-url http://localhost
cd frontend
MEDIA_MANIFEST=../migration/media/images/media-manifest.jsonl \
GALLERY_MANIFEST=../migration/galleries/photoshop-gallery-items.jsonl \
MEDIA_WAIVERS=../migration/media/image-waivers.jsonl \
APP_URL=http://localhost \
npm run visual:production
```

The visual/media report is written to:

```text
output/playwright/production-regression/report.json
```

Screenshots are written beside the report, one per route and viewport.

## Waiver Format

Waivers are JSONL rows. Each row can match by `url`, `referenced_url`,
`referenced_path`, `source_path`, or `cms_asset_id`:

```json
{"source_path":"images/retired-logo.jpg","reason":"legacy source file intentionally withheld"}
```

Strict mode is the default. The command exits non-zero for route failures,
unwaived image requests, and unwaived broken `img` elements. Use
`ALLOW_MEDIA_FAILURES=true` only for exploratory report-only migration runs.

## Report Fields

Each route report includes:

- `route`
- `viewport`
- `status`
- `screenshot`
- `mediaFailures`
- `requestFailures`
- `brokenImages`

Each image failure includes:

- `url` or `src`
- `status` or request error
- `sourcePath`
- `cmsAssetId`
- `assetKind`
- `checksumSha256`
- `galleryId`
- `gallerySlug`
- `galleryItemId`
- `galleryPosition`
- `galleryImageRole`
- `itemPageSourcePath`
- `waived`
- `waiverReason`
- `waiverKey`
- `screenshot`

Unwaived failures appear in `failures`. Waived image failures appear in
`waivedFailures` so they remain visible without blocking a strict release.

Provide `GALLERY_MANIFEST=../migration/galleries/photoshop-gallery-items.jsonl`
when verifying gallery routes so failures on thumbnails and full-size images
carry the source gallery and item identifiers.

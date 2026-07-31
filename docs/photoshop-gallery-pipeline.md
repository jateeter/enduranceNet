# Photoshop Gallery Pipeline

`scripts/photoshop_gallery_manifest.py` converts legacy Adobe Photoshop image
gallery exports into CMS-ready gallery and gallery-item records.

## Usage

Run a bounded smoke manifest:

```bash
python3 scripts/photoshop_gallery_manifest.py --max-galleries 10
```

Run the full gallery corpus manifest:

```bash
python3 scripts/photoshop_gallery_manifest.py
```

Generated files are ignored under `migration/galleries/`:

- `photoshop-galleries.jsonl`: one record per detected gallery root.
- `photoshop-gallery-items.jsonl`: ordered thumbnail/full-image records.
- `photoshop-gallery-blockers.jsonl`: missing thumbnails, item pages,
  full-size images, unreadable roots, and parse failures.
- `cms-gallery-import.sql`: starter SQL for `cms_galleries` and
  `cms_gallery_items`.
- `photoshop-gallery-summary.json`: gallery, item, blocker, pattern, parser,
  and bounded-run counts.

Fixture smoke test:

```bash
python3 scripts/test_photoshop_gallery_manifest.py
```

## Legacy Patterns

The importer handles the two dominant Photoshop export shapes:

- framed galleries with `ThumbnailFrame.html`, `pages/*.html`,
  `thumbnails/*.jpg`, and `images/*.jpg`
- paginated galleries with `index.html`, `index_2.html`, `pages/*.html`,
  `thumbnails/*.jpg`, and `images/*.jpg`

Every emitted record preserves legacy source paths and stable
`/legacy-media/...` URLs. Missing or unreadable media becomes a blocker row so
the CMS review workflow can resolve it explicitly.

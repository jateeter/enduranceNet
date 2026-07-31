# Image-only corpus staging manifest

## Problem

The current media manifest includes images, documents, audio, video, and other
assets. The image migration needs an image-only staging mode so operators can
copy and verify the visual corpus independently from documents and other media.

## Scope

- Add an image-only manifest/staging option to `scripts/media_asset_manifest.py`.
- Preserve stable CMS asset IDs, checksums, legacy URL, `/legacy-media/...`
  compatibility URL, `/media/...` CMS URL, storage key, dimensions, and source
  provenance.
- Produce image-specific duplicate, blocker, and summary reports.
- Support bounded staging runs for smoke tests and full-corpus staging runs for
  deployment operations.

## Acceptance Criteria

- Operators can generate image-only manifests without document/audio/video rows.
- Staging copy reports distinguish copied, planned, and failed image assets.
- Tests cover image-only filtering and copy/blocker behavior.
- The image-only command is documented.

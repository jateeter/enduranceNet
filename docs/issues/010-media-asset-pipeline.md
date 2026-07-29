# Build media asset pipeline

## Goal

Make images, PDFs, audio, video, documents, and gallery assets available to the
NextGen site with durable manifests and predictable URLs.

## Scope

- Generate asset manifest from the source inventory.
- Record checksums, dimensions where practical, MIME types, source paths, and
  public references.
- Preserve original assets and optionally generate web-optimized derivatives.
- Detect broken references in imported pages.
- Support large historical galleries without loading all media eagerly.

## Acceptance Criteria

- Every migrated media reference resolves to an asset manifest entry or a
  documented missing/waived file.
- Permission-denied files are blocked from being silently skipped.
- The frontend can render responsive images and link to documents safely.


# Legacy gallery URL redirects

## Problem

Legacy gallery entry points such as `ThumbnailFrame.html`, paginated
`index.html`, and `pages/*.html` should lead users to canonical NextGen gallery
routes.

## Scope

- Generate redirect mapping candidates from the Photoshop gallery manifest.
- Add representative redirect rules for high-value gallery roots.
- Preserve old URLs as provenance fields in the gallery API.
- Keep page-level image URLs available as metadata or anchors when possible.

## Acceptance Criteria

- Representative legacy gallery URLs redirect to `/galleries/:slug`.
- Redirect checks cover framed and paginated gallery variants.
- The gallery detail view links back to original source URLs for audit.

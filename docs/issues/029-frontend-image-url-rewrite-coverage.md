# Frontend image URL rewrite coverage

## Problem

Imported content and legacy templates reference images through relative paths,
`endurance.net`, `www.endurance.net`, `feeds.endurance.net`, and externally
hosted Blogger/CDN URLs. React and stream rendering need one canonical rewrite
path so migrated images load consistently.

## Scope

- Extend frontend legacy asset URL rewriting to all known legacy image hosts.
- Preserve external Blogger/CDN image URLs unless they have been imported into
  the CMS image corpus.
- Add tests or fixtures for absolute legacy URLs, relative URLs, query strings,
  anchors, and already-canonical `/legacy-media` or `/media` URLs.
- Use the same rewrite helper in landing, event, story, stream, community, and
  archive surfaces.

## Acceptance Criteria

- `feeds.endurance.net` image URLs rewrite through the canonical compatibility
  path.
- `/legacy-media/...` and `/media/...` URLs are not double-prefixed.
- Query strings survive rewriting.
- Frontend tests or focused script checks cover the URL matrix.

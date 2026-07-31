# RSS entry cards and stream detail pages

## Problem

The stream directory exposes source-level navigation, but readers need normalized
entry lists and consistent story cards across every Blogger/RSS stream.

## Scope

- Add `/streams/:slug` pages.
- Pull normalized entries from the Scala API.
- Render entry cards with title, source stream, date, summary, canonical link,
  and legacy link where available.
- Support hover/focus summary expansion in the same style as the current
  homepage headline tooltips.
- Preserve XSLT-derived presentation semantics where they affect ordering,
  display count, or detail routing.

## Acceptance Criteria

- Each stream source can render a detail page.
- Entry cards use a shared component and consistent styles.
- Empty/unimported archival streams have a useful source-level view rather than
  a dead end.

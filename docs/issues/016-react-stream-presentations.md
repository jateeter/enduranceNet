# React stream presentation modes

## Problem

The NextGen UI needs to render imported Blogger/RSS streams in the thematic
style of the legacy site while using accessible React components instead of
PHP/XSLT-generated HTML.

## Scope

- Implement React components for `atom-list`, `popup-channel-card`,
  `single-entry-html`, `event-story-list`, `rss-list`, and
  `google-reader-frontpage` compatibility mode.
- Convert legacy popup mouseover behavior to accessible hover/focus popovers.
- Keep legacy category labels, display limits, and iconic/bullet branding where
  appropriate.
- Sanitize imported HTML and rewrite legacy `endurance.net` and
  `feeds.endurance.net` links.

## Acceptance Criteria

- Stream cards and lists can render from `/api/streams` and
  `/api/streams/:slug/entries`.
- Popup previews work with mouse, keyboard focus, and mobile-safe fallback.
- Imported Blogger HTML does not execute unsafe scripts.
- Playwright screenshots cover the major presentation modes.

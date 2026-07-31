# Blogger/RSS stream registry and API foundation

## Problem

The legacy site uses Blogger-hosted Atom feeds, RSS feeds, local feed snapshots,
OPML files, and PHP/XSLT rendering as a lightweight content-management workflow.
The NextGen app needs a canonical registry before importer and React rendering
work can proceed.

## Scope

- Model stream sources and stream entries in Postgres.
- Preserve provider, feed format, remote URL, local cache path, legacy URL,
  default presentation mode, active/archive state, and source notes.
- Preserve canonical Blogger/RSS entry IDs, links, authors, timestamps, raw HTML
  snippets, and provenance fields.
- Add read-only Scala API endpoints for stream sources and entries.
- Seed representative streams from the mounted legacy evidence.

## Acceptance Criteria

- `/api/streams` lists known Blogger/RSS stream sources.
- `/api/streams/:slug` returns one stream source by slug.
- `/api/streams/:slug/entries` returns entries for a stream.
- `/api/stream-entries` returns the seeded entry set across streams.
- Tests cover the stream listing and source-specific entry behavior.

## Legacy Evidence

- `/Volumes/webstore/endurance.net/channels/EnduranceNetFeeds.xml`
- `/Volumes/webstore/endurance.net/channels/whereintheworld/atom.xml`
- `/Volumes/webstore/endurance.net/blogger/index_content.html`
- `/Volumes/webstore/endurance.net/channels/xslTemplates/atomlist_Items.xsl`
- `/Volumes/webstore/endurance.net/channels/xslTemplates/atomlist_popup.xsl`

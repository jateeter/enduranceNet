# Feed importers, snapshots, and active Blogger polling

## Problem

The legacy content workflow depends on a mix of live Blogger feeds and cached
local XML/HTML snapshots. NextGen must import historical content from local
snapshots first, then poll active feeds without losing raw source evidence.

## Scope

- Build importers for Atom 1.0, older Blogger Atom variants, RSS 2.0, OPML, and
  local cached XML.
- Store raw feed snapshots with fetch metadata, checksums, ETag/Last-Modified
  values when available, and parser version.
- Dedupe entries by canonical Blogger blog/post IDs or stable feed item links.
- Support Blogger paging through `rel="next"` links and `start-index` /
  `max-results` parameters.
- Mark unavailable or permission-denied feeds as explicit blockers.

## Acceptance Criteria

- Import runs are idempotent.
- Historical local XML can be imported without network access.
- Active Blogger feeds can be refreshed without duplicating entries.
- Failed feeds produce structured import errors and do not stop the entire run.

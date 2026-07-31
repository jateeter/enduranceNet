# Validated Blogger registry seed

## Problem

The initial stream source table only contains representative feeds. The validated
Blogger registry identifies 35 pull-ready Blogger blog IDs, and all of them are
part of the Endurance.Net corpus.

## Scope

- Extend stream source records with Blogger blog ID, canonical Atom URL,
  canonical RSS URL, latest cached entry timestamp, and editorial group.
- Seed all validated Blogger-backed streams.
- Keep archival streams visible but mark them inactive when their cache is not
  current.
- Preserve local cache path provenance for each stream.

## Acceptance Criteria

- `/api/streams` returns all 35 validated Blogger streams plus the OPML registry
  record.
- Current streams are marked active and sort ahead of archive streams.
- Tests cover a current stream and an archival stream.
- The legacy `https://www.blogger.com/atom/{blogId}` URI form is not used as the
  canonical pull URL.

# RSS corpus search and filtering

## Problem

Once active and archival feed entries are imported, readers need one way to
search and filter across the full Endurance.Net stream corpus.

## Scope

- Add source group, active/archive, year, and text filters.
- Search across normalized entry title, summary, author, stream title, and
  provenance.
- Keep active streams discoverable while preserving archive depth.
- Expose API query parameters that can later be backed by Postgres full-text
  search.

## Acceptance Criteria

- Combined stream search returns entries from multiple feeds.
- Filters are reflected in the URL.
- Results retain legacy source provenance and canonical stream links.

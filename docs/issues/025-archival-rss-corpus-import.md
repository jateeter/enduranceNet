# Archival RSS corpus import completion

## Problem

The validated Blogger registry includes active feeds and many archival or
section-specific streams. The full Endurance.Net corpus requires importing the
archival cached Blogger/RSS/Atom material, including streams that no longer have
recent live updates.

## Scope

- Import cached XML/Atom/RSS/HTML snapshots for all validated archival streams.
- Support Blogger paging and legacy local snapshot variants where available.
- Preserve raw source snapshots, canonical entry IDs, authors, timestamps,
  alternate links, comments links, HTML content, media references, and source
  provenance.
- Dedupe entries across canonical Blogger feeds and local snapshot copies.
- Produce coverage reports by stream group and source cache path.

## Acceptance Criteria

- Every validated archival Blogger-backed stream has imported entries or an
  explicit no-content/blocker status.
- Imported entries remain traceable to their local cache path and canonical
  Blogger/RSS URI.
- Duplicate local snapshots do not create duplicate public entries.
- The stream directory and search surfaces include archival corpus entries with
  consistent style and navigation.

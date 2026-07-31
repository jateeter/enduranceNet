# Stream media extraction and future CMS bridge

## Problem

Blogger entries contain image and document links that currently point at legacy
media paths, Blogger-hosted assets, and `feeds.endurance.net` archive URLs. This
work should prepare for a fuller CMS/media migration without blocking stream
import.

## Scope

- Extract media and document references from imported stream HTML.
- Normalize old `http://www.endurance.net/...` and `feeds.endurance.net/...`
  references.
- Record unresolved, unreadable, or permission-denied media as blockers.
- Preserve source links until CMS asset IDs are available.
- Define the handoff model from stream media references into the future CMS.

## Acceptance Criteria

- Each imported entry can report the media references found in its body.
- Broken or permission-denied media references are visible in migration reports.
- NextGen rendering can use rewritten legacy media URLs now and CMS asset IDs
  later.

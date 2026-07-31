# XSLT presentation parity matrix

## Problem

Legacy XSLT templates encode more than formatting. They define category labels,
display counts, popup behavior, event-story routes, special Tevis/WEC behavior,
and raw Blogger HTML rendering. NextGen needs React presentation modes that
preserve these semantics.

## Scope

- Inventory XSLT templates under `channels/xslTemplates/` and special section
  folders such as Biltmore, WEC, Tevis, and versioned legacy directories.
- Generate golden HTML fixtures from representative XML/XSLT pairs.
- Define a transform matrix mapping legacy XSL files to NextGen presentation
  modes.
- Implement parity checks for entry count, order, title, link target, category
  title, and sanitized HTML body behavior.

## Acceptance Criteria

- The matrix identifies each XSLT template as migrated, compatibility-only, or
  retired with redirect coverage.
- At least one fixture covers Atom list, popup list, single entry, event-story
  list, RSS list, and Google Reader-era presentation behavior.
- React presentation work can consume the matrix without re-reading the legacy
  PHP/XSLT implementation.

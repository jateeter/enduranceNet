# Map executable route and include graph

## Goal

Build a graph of all executable PHP templates and their include dependencies.

## Scope

- Parse `.html`, `.htm`, and `.php` as PHP-capable templates.
- Extract `include`, `include_once`, `require`, `require_once`, and common
  `getenv("DOCUMENT_ROOT")` include paths.
- Detect wrapper pages that include `include/siteHeader.html`,
  `indexInternal.html`, and `include/siteTrailer.html`.
- Record page-level variables such as `$pageTitle`, `$secondaryBanner`,
  `$NavBar`, `$sectionHead_String`, `$hasFeed`, and `$useTableSort`.
- Emit route graph and include graph artifacts.

## Acceptance Criteria

- The graph identifies shared layout roots such as `include/commonHeader.html`
  and `include/siteHeader.html`.
- Broken or dynamic includes are reported with source file and line.
- Backup/temp files are marked and excluded from the default public route graph.


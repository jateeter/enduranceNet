# Blogger/RSS Stream Migration Roadmap

The legacy site uses Blogger and RSS/Atom streams as a content-management
workflow. Many feeds are rendered through PHP `XsltProcessor` calls against XSLT
templates under `channels/xslTemplates/`, so the NextGen migration must preserve
both the stream data and the thematic presentation semantics.

## Legacy Evidence

- `channels/EnduranceNetFeeds.xml` is an OPML feed registry for channel groups.
- `blogger/index_content.html` renders `merri/MerriTravels.xml` with
  `channels/xslTemplates/atomlist_Items.xsl`.
- `channels/whereintheworld/atom.xml` is a Blogger Atom snapshot with Blogger
  blog/post IDs, alternate links, self links, comment links, authors, and HTML
  content.
- `channels/xslTemplates/atomlist_popup.xsl` renders themed channel lists with
  category-specific titles, bullet images, popup previews, and display limits.
- `channels/xslTemplates/atom_eventStoryList.xsl` renders event-story indexes
  that link to `eventStoryInternal.html?storyURL=<self-link>`.
- `channels/xslTemplates/atomsingle.xsl` renders the first Atom entry content
  with `disable-output-escaping`.
- `channels/xslTemplates/rssList.xsl` and related templates render RSS headline
  lists.
- `channels/xslTemplates/googleReaderAtom_frontPage.xsl` and Tevis variants
  contain special historical presentation behavior that must be treated as
  compatibility modes.

## Target Architecture

Treat streams as a first-class subsystem:

- `feed_sources` records the source stream, provider, local cache path, legacy
  URL, feed format, active/archive state, and default presentation.
- `feed_entries` records canonical Blogger/RSS entries with stable provider
  IDs, content, links, timestamps, checksums, and source provenance.
- `feed_media_refs` will track images and linked media extracted from entry
  HTML for the later CMS/media migration.
- `feed_presentations` maps legacy XSL templates to React/Scala presentation
  modes.

The Scala API exposes stream sources and entries. React renders entries through
named presentation components instead of running browser-side XSLT.

## Uniform Stream Experience

The validated Blogger registry is now the navigation backbone for the RSS
corpus. The new site should present every current and archival stream through
one consistent information architecture:

- Active streams appear first as the daily/weekly information surface: World
  News, USA News, Snapshots, Consider This, Ride Stories, and Trails Matter.
- Archival streams remain visible as corpus sections, not hidden implementation
  leftovers.
- Each stream page/card uses the same title, freshness, source, and action
  vocabulary, with the same Endurance.Net color palette and legacy banner
  rhythm already used on the landing page.
- The navigation model groups streams by editorial purpose: Active News,
  Community, Event & Team Archives, News Archives, Photo & Travel Journals, and
  Resources.
- The canonical pull URI is the validated Blogger RSS endpoint:
  `https://www.blogger.com/feeds/{blogId}/posts/default?alt=rss`. The matching
  Atom endpoint is retained for importer compatibility and entry-level links.

The first user-facing surface should be a scan-friendly stream directory. The
next slice should add per-stream pages with normalized entries and legacy-style
headline/summary cards. Later slices should add combined archive search,
cross-stream filters, media extraction, and CMS handoff.

## XSLT Translation Strategy

Use XSLT as a behavioral specification, not as the runtime rendering layer.

- Generate fixture output from representative legacy XML and XSLT pairs.
- Translate each XSL template into a named presentation mode.
- Compare NextGen output for title order, display count, links, category labels,
  and sanitized body HTML.
- Preserve special-case transforms as compatibility modes until the associated
  legacy sections are fully migrated.

Initial presentation modes:

- `atom-list`: compact Atom headline list.
- `popup-channel-card`: legacy hover/focus preview card from
  `atomlist_popup.xsl`.
- `single-entry-html`: single Blogger entry renderer from `atomsingle.xsl`.
- `event-story-list`: event-story index from `atom_eventStoryList.xsl`.
- `rss-list`: RSS headline list from `rssList.xsl`.
- `google-reader-frontpage`: compatibility renderer for Google Reader-era feeds.

## Implementation Phases

1. Create stream registry tables, seed representative legacy streams, and expose
   read-only API endpoints.
2. Inventory every Blogger/RSS/Atom/OPML/XSLT reference in the mounted legacy
   tree and load it into the registry.
3. Build importer support for Atom 1.0, Blogger Atom variants, RSS 2.0, OPML,
   and local cached XML.
4. Build XSLT parity fixtures and a transform matrix.
5. Implement React presentation modes for the most common XSL templates.
6. Add media/link extraction and rewrite rules for imported Blogger HTML.
7. Enable scheduled polling for active Blogger streams while preserving raw
   snapshots for auditability.
8. Import archival cached Blogger HTML/XML for feeds that are no longer live.
9. Seed the full validated Blogger registry into the Scala/Postgres source
   model, including canonical Atom/RSS URLs and editorial grouping.
10. Build a uniform React stream directory and per-stream navigation surface.
11. Add normalized headline lists and story cards for pulled stream entries.
12. Add combined stream search/filtering across active and archival feeds.
13. Integrate stream-linked media references with the future CMS asset bridge.
14. Use the importer `stream_poll_targets` manifest as the scheduled polling
    contract for active Blogger streams, with raw remote snapshots preserved in
    `stream_raw_snapshots`.
15. Populate `stream_media_references` from imported entry HTML so legacy media
    paths can render through `/legacy-media/...` now and receive CMS asset IDs
    later.

## Verification

- Unit test stream source and entry API output.
- Fixture-test parser support against `whereintheworld/atom.xml`,
  `merri/MerriTravels.xml`, `2006WEC/wecnews_atom.xml`, and representative RSS
  files.
- Golden-test XSLT translations against legacy transform output.
- Generate `migration/coverage/xslt-parity-matrix.json` with
  `scripts/xslt_parity_matrix.py` to classify XSLT templates by NextGen
  presentation mode, migration status, output settings, parameters, variables,
  template matches, and legacy behavior flags.
- Run Playwright visual checks for stream lists, popup cards, event-story lists,
  and single-entry pages.
- Keep media 404 and permission-denied reporting linked to the future CMS/media
  migration.

# Endurance.Net NextGen Translation Roadmap

This roadmap treats `/Volumes/webstore/endurance.net/` as the authoritative live
source tree for the current site. The Apache configuration executes PHP for
`.php`, `.html`, and `.htm` file types, so all of those extensions must be
handled as executable PHP templates unless proven otherwise.

## Current Source Read

The live source tree is a long-lived PHP/XHTML publication system with a large
amount of hand-authored content and media. The visible site is only the top of
the tree; the mounted source includes event microsites, galleries, channel
archives, advertiser content, classifieds, Ridecamp/community material, backup
copies, temporary editor files, and raw media.

Important observed patterns:

- Route wrappers set page variables such as `$pageTitle`, `$secondaryBanner`,
  `$NavBar`, `$sectionHead_String`, and then include shared templates.
- Many route wrappers include `include/siteHeader.html`, a local
  `indexInternal.html` content fragment, and `include/siteTrailer.html`.
- `include/commonHeader.html` starts the PHP session and emits global metadata,
  banners, feed links, keywords, and default layout settings.
- XML/XSLT transforms are used for feeds, ad lists, navigation, gallery helpers,
  and channel fragments.
- No relational database dependency has been identified in the sampled critical
  paths. Postgres should be introduced for the new canonical content model, not
  as a one-for-one legacy dependency.
- Some media files are unreadable from the current mounted permissions. These
  must be inventoried and resolved before claiming complete migration coverage.

## Translation Strategy

The migration should preserve all legacy content first, then progressively turn
high-value areas into structured React and Scala experiences.

1. Build a complete read-only inventory of the mounted source tree.
2. Produce a route graph and include graph for all executable `.html`, `.htm`,
   and `.php` files.
3. Record unreadable media and source files as explicit blockers until
   permissions are fixed or replacement assets are supplied.
4. Mirror raw legacy source and assets into a controlled migration input area,
   excluding editor backups and dangerous runtime artifacts by policy.
5. Classify content into canonical domains: news, featured stories, events,
   event pages, galleries, advertisers, classifieds, Ridecamp archives, books,
   static pages, feeds, and media assets.
6. Define Postgres schema and Scala data-access boundaries for canonical
   content while keeping immutable legacy pages addressable.
7. Build importers that convert PHP wrapper metadata, internal fragments, XML
   feeds, and gallery manifests into structured records.
8. Build redirect and legacy URL resolution so existing public URLs remain
   stable.
9. Rebuild the public UI in React around endurance riding content, not the
   placeholder multi-sport scaffold currently in the repo.
10. Verify coverage by comparing source inventory, imported records, rendered
    URLs, media availability, and redirects.

The CMS/editorial layer is now scoped in
`docs/cms-platform-decision.md`: Directus is the preferred back office over the
existing Postgres repository, with Scala Play remaining the public API and
migration authority.

## Phases

### Phase 0: Source Access And Evidence

Deliverables:

- Background crawler that can safely walk `/Volumes/webstore/endurance.net/`.
- Manifests for files, directories, sizes, MIME types, checksums, permissions,
  and parse classification.
- Separate unreadable-file report for permission remediation.
- Snapshot of high-value source examples showing the PHP-on-HTML execution
  model.

Acceptance:

- The crawler can resume after interruption.
- Permission-denied files are reported with full paths.
- Static media, executable templates, data files, and backups are separated.

### Phase 1: Legacy Structure Model

Deliverables:

- Route graph for executable templates.
- Include dependency graph.
- Content-domain classification report.
- URL preservation plan for legacy public paths.

Acceptance:

- `.html`, `.htm`, and `.php` are all parsed as PHP-capable files.
- `indexInternal.html` and shared include patterns are detected.
- Backup and temp files are not accidentally promoted into public content.

### Phase 2: Canonical Data Model

Deliverables:

- Postgres schema for canonical content.
- Scala Play API boundaries for content, media, search, redirects, and imports.
- Import staging model that records original source path and legacy URL.

Acceptance:

- Every imported record preserves provenance.
- Legacy URLs can resolve to either structured content or archived raw pages.
- The model supports galleries, advertisers, classifieds, Ridecamp archives, and
  event microsites without flattening everything into a single page table.

### Phase 3: Importers

Deliverables:

- PHP wrapper metadata extractor.
- HTML fragment importer for `indexInternal.html` style content.
- XML/Atom/XSLT feed importer.
- Gallery and media manifest importer.
- Advertiser and classified importers.
- Ridecamp archive importer.

Acceptance:

- Import runs are idempotent.
- Failed files are reported without stopping the whole import.
- Each import can be traced back to source path, checksum, and import version.

### Phase 4: NextGen User Experience

Deliverables:

- React IA matching the actual endurance.net taxonomy.
- Home page rebuilt from real news, featured stories, events, ads, and gallery
  data.
- Event microsite and gallery views.
- News archive and search views.
- Advertiser, classifieds, Ridecamp, and static archive views.

Acceptance:

- The placeholder multi-sport content is removed.
- The first viewport clearly signals Endurance.Net and endurance riding.
- Legacy URLs redirect or render with no dead ends for migrated content.

### Phase 5: Deployment And Verification

Deliverables:

- Docker Compose stack with optional Postgres.
- Import job container or admin command.
- Coverage reports.
- Link checker and media availability checker.
- Production redirect tests.

Acceptance:

- The NextGen stack can be rebuilt from source, database dump, and asset
  manifest.
- Permission gaps are zero or explicitly waived.
- A representative public crawl verifies migrated pages, media, and redirects.

## Initial Content Domains

- `news_article`
- `featured_story`
- `event`
- `event_page`
- `gallery`
- `media_asset`
- `advertiser`
- `classified_listing`
- `ridecamp_message`
- `book`
- `static_page`
- `feed_entry`
- `redirect`
- `legacy_source_file`

## Immediate Risks

- Permission-denied media files can silently break completeness unless they are
  tracked as first-class blockers.
- The mounted tree contains backup and temp files that look like public pages.
- The existing repo scaffold has placeholder endurance-sport content that does
  not match the endurance.net domain.
- PHP execution hidden behind `.html` makes naive static import unsafe.
- Some legacy paths may depend on request URI, sessions, or server environment.

# CMS Platform Decision

Status: Accepted for NextGen planning
Date: 2026-07-31
Issue: https://github.com/jateeter/enduranceNet/issues/55

## Decision

Use Directus as the preferred CMS/editorial back office for the Endurance.Net
NextGen migration, connected to the existing Postgres repository that already
backs the Scala Play API. Directus should manage editorial screens, permissions,
asset metadata, and operator workflows, while the public website continues to
read through the Scala API and React UI.

This keeps the canonical content database inside the current deployment model
instead of introducing a separate hosted content store. Repo-owned migrations
remain the authority for schema changes. Directus is an operator interface over
that schema, not a replacement for the migration pipeline, provenance records,
or public API.

## Why Directus

Directus fits the current migration constraints better than a standalone CMS
whose own content model would need to become the new source of truth:

- It is designed to connect to an existing SQL database and expose editorial UI,
  REST, and GraphQL over that database.
- It can be self-hosted beside the React, Scala Play, and Postgres containers.
- It lets NextGen keep source provenance, legacy redirect tables, stream
  snapshots, and importer-owned records in one database.
- It avoids forcing the Blogger/RSS, PHP-on-HTML, gallery, Ridecamp, advertiser,
  and media corpus into a separate CMS storage abstraction before import
  completeness is known.
- It gives editors a practical UI earlier than building every admin workflow in
  Scala and React from scratch.

## Architecture Boundary

The CMS boundary is intentionally narrow:

- Postgres stores canonical content, media, provenance, taxonomy, stream, and
  redirect records.
- Scala Play owns public read APIs, redirect resolution, import commands, and
  scheduled feed refresh behavior.
- React owns public presentation and visual regression checks.
- Directus owns editorial/admin workflows, draft-review fields, asset metadata
  curation, role-based access, and operator correction of imported records.
- Importers remain idempotent and write provenance-rich records before editors
  make corrections through the CMS.

Directus should not serve the public Endurance.Net UI directly. Public traffic
should continue through the NextGen frontend/backend so legacy redirects,
sanitization, media rewriting, caching, and theme consistency remain under the
same application controls.

## Canonical CMS Model

The CMS layer must cover these objects:

| Object | Purpose | Owner |
| --- | --- | --- |
| `cms_content_items` | News, featured stories, static pages, event pages, classifieds, advertisers, books, Ridecamp imports, and curated landing-page features. | Importer first, editor after import |
| `cms_media_assets` | Images, documents, thumbnails, dimensions, checksums, MIME type, alt text, copyright/source notes, replacement status, and stable NextGen URLs. | Importer and editor |
| `cms_authors` | Blogger authors, legacy bylines, editorial accounts, and normalized display names. | Importer and editor |
| `cms_taxonomy_terms` | Editorial groups, regions, event categories, stream groups, legacy sections, and topic tags. | Editor |
| `cms_source_provenance` | Original source path, legacy URL, checksum, import run, feed URI, Blogger IDs, and raw snapshot pointers. | Importer |
| `cms_redirect_bindings` | Legacy URL to content/media/stream targets plus HTTP status and notes. | Importer and editor |
| `stream_sources` | Blogger/RSS source registry, poll configuration, active/archive state, and presentation mode. | Importer and scheduler |
| `stream_entries` | Normalized Blogger/RSS entries and HTML summaries/content. | Importer and scheduler |
| `stream_media_references` | Media references extracted from stream body HTML, including rewritten URLs and future CMS asset IDs. | Importer and CMS bridge |

Existing stream tables should remain first-class tables. They can be exposed in
Directus for editorial visibility, but stream polling and dedupe behavior remain
application-owned.

## Editorial Workflows

The first CMS workflow set should be small and migration-focused:

1. Review imported content by source domain, import run, and legacy URL.
2. Replace or annotate broken media and permission-denied assets.
3. Curate landing-page feature placement without changing importer records.
4. Correct titles, dates, authors, categories, and summaries while preserving
   original raw content.
5. Mark archival content as published, hidden, redirected, duplicate, or blocked.
6. Review active Blogger stream entries after scheduled polling.

Every editor-visible record needs provenance fields that cannot be lost during
manual correction.

## Fallback Option

If Directus proves too heavy operationally or cannot safely share the production
Postgres schema, use a minimal Scala/React admin console backed by the same
tables as the fallback. The fallback should implement only the workflows needed
to unblock migration: media blocker review, content publication state, landing
page curation, and redirect correction.

Payload CMS is the second external fallback if a separate Node CMS service is
acceptable. It supports Postgres through its database adapter, but adopting it
would make the Payload configuration another schema authority. That is less
attractive while the repo's Play evolutions and import scripts are still the
migration contract.

Decap CMS is not recommended for the corpus migration. It is useful for small
Git-backed static collections, but the Endurance.Net corpus needs relational
queries, media provenance, scheduled feed polling, and legacy redirect/media
resolution at database scale.

Strapi is not the preferred option for this project. It is mature and
self-hostable, but it would introduce a separate Node application and content
model that competes with the existing Scala/Postgres migration model.

## Deployment Shape

The target deployment adds a `cms` service to Docker Compose only after the
schema and access rules are ready:

- `frontend`: public React site.
- `backend`: Scala Play public API, import commands, redirects, and stream
  polling.
- `postgres`: canonical content and CMS metadata.
- `cms`: Directus admin service, private/admin routed, connected to Postgres.
- optional object storage or mounted asset volume for migrated media files.

The CMS service should not be exposed publicly until authentication, backups,
roles, and media storage are configured.

## Follow-On Implementation Issues

- #56: migrate the media corpus into CMS-ready asset records and stable
  NextGen URLs.
- #57: implement the scheduled Blogger polling worker that updates stream
  tables and raw snapshots.
- #58: complete archival RSS corpus import into the canonical tables.
- #59: add production visual and media regression checks for the migrated
  surfaces.

Additional issues should be opened after #56 clarifies storage volume/object
storage needs:

- Add Directus service and admin routing to Docker Compose.
- Add CMS schema evolutions for content items, media assets, taxonomy,
  provenance, and editor state.
- Add role/permission bootstrap and backup/restore documentation.

## References

- Directus describes itself as a backend/CMS that connects to an existing
  database and generates REST and GraphQL APIs: https://directus.com/
- Directus self-hosted CLI documentation describes bootstrapping and migrating
  an on-prem instance: https://docs.directus.io/self-hosted/cli
- Strapi documents self-hosting and bring-your-own SQL database support:
  https://strapi.io/hosting
- Payload documents Postgres support through the `@payloadcms/db-postgres`
  adapter: https://payloadcms.com/docs/database/postgres
- Decap CMS documents Git-host-backed content editing:
  https://decapcms.org/docs/backends-overview/

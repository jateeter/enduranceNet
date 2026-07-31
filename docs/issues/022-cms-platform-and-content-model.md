# CMS platform and content model selection

## Problem

The current NextGen stack can rewrite some legacy media references, but the
site still needs a durable CMS strategy for the full Endurance.Net content and
image corpus. Blogger streams, PHP-authored pages, event microsites, galleries,
classifieds, advertiser records, and Ridecamp archives all need a shared
editorial and asset-management model before the migration can move beyond
seeded structured slices.

## Scope

- Compare pragmatic CMS options against the existing React, Scala Play, and
  Postgres stack.
- Define the canonical content, media, author, source, taxonomy, and redirect
  objects that must be owned by the CMS layer.
- Specify how Blogger/RSS feed entries and legacy PHP/HTML imports map into the
  CMS model without losing provenance.
- Identify editor workflows for active news streams, archival correction, media
  replacement, and future story publication.
- Produce a migration decision record with integration boundaries, deployment
  impact, and data portability requirements.

## Acceptance Criteria

- A CMS recommendation is documented with at least one viable fallback option.
- The CMS model covers feed entries, legacy pages, galleries, media assets,
  redirects, taxonomy, provenance, and permissions.
- The recommendation explains whether CMS data remains in the existing Postgres
  database or is synchronized from a separate repository/service.
- Follow-on implementation issues can be estimated from the selected model.

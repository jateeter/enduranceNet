# Build legacy import pipeline

## Goal

Create import jobs that transform the live PHP/XML/media source tree into
NextGen content records and asset manifests.

## Scope

- Import PHP wrapper metadata and internal content fragments.
- Import XML, Atom, OPML, and XSLT-backed feed content.
- Import gallery manifests and media references.
- Import advertisers and classifieds.
- Import Ridecamp archive indexes and messages.
- Record failures without aborting the entire batch.

## Acceptance Criteria

- Importers are idempotent and versioned.
- Each imported record stores source path, checksum, parser version, and import
  batch.
- Failed imports produce actionable reports.
- Import coverage can be compared against the source inventory manifest.


# Add Postgres-backed Scala content API

## Goal

Introduce Postgres-backed persistence and Scala Play API endpoints for migrated
Endurance.Net content.

## Scope

- Add optional Postgres service to the Docker Compose stack.
- Add database migration tooling.
- Implement repositories and controllers for canonical content.
- Add endpoints for content lookup, archives, search, media metadata, and legacy
  URL resolution.
- Keep imports idempotent and provenance-aware.

## Acceptance Criteria

- The app can run locally with Postgres through Docker Compose.
- API responses are backed by persisted content rather than in-memory samples.
- Tests cover content lookup, legacy URL resolution, and not-found behavior.


# Scheduled Blogger polling worker

## Problem

The legacy site refreshes Blogger/RSS stream snapshots through background cron
jobs. NextGen now has a stream registry and poll-target manifest, but it still
needs an operational worker that can refresh active streams on schedule,
preserve raw snapshots, and update normalized entries without duplication.

## Scope

- Implement a scheduled feed-polling command or container entrypoint using the
  `stream_poll_targets` contract.
- Preserve raw remote responses in `stream_raw_snapshots` before normalization.
- Update stream entries idempotently using canonical Blogger IDs and stable
  links.
- Record poll timing, HTTP status, checksums, entry counts, and failures for
  auditability.
- Document how the worker maps onto deployment cron, container scheduling, or a
  future job runner.

## Acceptance Criteria

- Active Blogger streams can be refreshed repeatedly without duplicate entries.
- Poll outcomes are queryable through logs, database records, or reports.
- Failed feed pulls preserve enough detail for retry and operator diagnosis.
- Deployment documentation explains how to run the worker on the same cadence as
  the legacy cron workflow or a clearly chosen replacement cadence.

# Build complete source inventory crawler

## Goal

Create a resumable read-only crawler for `/Volumes/webstore/endurance.net/` that
produces a complete manifest of the live source tree.

## Scope

- Walk all directories under the mounted source root.
- Record path, type, extension, size, modification time, permissions, MIME guess,
  checksum where readable, and crawl status.
- Classify files as executable template, media asset, data file, backup/temp
  artifact, document, unknown, or unreadable.
- Treat `.html`, `.htm`, and `.php` as PHP-capable executable templates.
- Run safely in the background and resume from the last successful checkpoint.

## Acceptance Criteria

- A full manifest can be generated without losing progress after interruption.
- Permission-denied files are captured in a separate report.
- The crawler never modifies the mounted live source tree.
- The manifest can be used by later importers without rescanning everything.


#!/usr/bin/env python3
"""Run scheduled Blogger/RSS polling against the legacy import staging database."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import legacy_import


@dataclass(frozen=True)
class PollWorkerConfig:
    staging_db: Path
    output_dir: Path
    fail_on_target_errors: bool


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, values: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for value in values:
            handle.write(json.dumps(value, sort_keys=True) + "\n")


def count(conn: sqlite3.Connection, sql: str) -> int:
    return int(legacy_import.one(conn, sql) or 0)


def target_statuses(conn: sqlite3.Connection) -> list[dict[str, object]]:
    return legacy_import.rows(
        conn,
        """
        SELECT source_path, title, provider, feed_format, poll_url, active,
               poll_status, blocker, last_checksum_sha256, etag, last_modified
        FROM stream_poll_targets
        ORDER BY active DESC, poll_status ASC, source_path ASC
        """,
    )


def ensure_required_tables(conn: sqlite3.Connection) -> None:
    required = {
        "import_batches",
        "import_failures",
        "stream_entries_v2",
        "stream_poll_targets",
        "stream_raw_snapshots",
    }
    existing = {
        str(row["name"])
        for row in legacy_import.rows(
            conn,
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """,
        )
    }
    missing = sorted(required - existing)
    if missing:
        raise RuntimeError(
            "staging database is missing stream polling tables "
            + ", ".join(missing)
            + "; run scripts/legacy_import.py --reset before scheduling polls"
        )


def latest_remote_snapshots(conn: sqlite3.Connection, batch_id: str) -> list[dict[str, object]]:
    return legacy_import.rows(
        conn,
        """
        SELECT source_path, fetch_url, fetched_at, http_status, etag,
               last_modified, checksum_sha256
        FROM stream_raw_snapshots
        WHERE import_batch_id = ?
          AND source_kind = 'remote-poll'
        ORDER BY fetched_at DESC, source_path ASC
        """,
        (batch_id,),
    )


def run_poll(
    config: PollWorkerConfig,
    fetcher: Callable[[str, object, object], legacy_import.FetchResult] = legacy_import.fetch_stream_url,
) -> dict[str, object]:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    if not config.staging_db.exists():
        raise FileNotFoundError(f"staging database not found: {config.staging_db}")

    with sqlite3.connect(config.staging_db) as conn:
        ensure_required_tables(conn)
        batch_config = legacy_import.ImportConfig(
            inventory_db=Path(""),
            source_root=Path(""),
            output_dir=config.output_dir,
            staging_db=config.staging_db,
            max_records=None,
            reset=False,
            poll_active=True,
        )
        batch_id = legacy_import.start_batch(conn, batch_config)
        started_at = legacy_import.utc_now()
        before_raw = count(conn, "SELECT COUNT(*) FROM stream_raw_snapshots")
        before_entries = count(conn, "SELECT COUNT(*) FROM stream_entries_v2")
        before_ready = count(conn, "SELECT COUNT(*) FROM stream_poll_targets WHERE poll_status = 'ready'")
        before_blocked = count(conn, "SELECT COUNT(*) FROM stream_poll_targets WHERE poll_status = 'blocked'")

        imported_entries = legacy_import.poll_active_streams(conn, batch_id, fetcher)
        failures = legacy_import.rows(
            conn,
            """
            SELECT source_path, importer, error, created_at
            FROM import_failures
            WHERE batch_id = ?
            ORDER BY source_path
            """,
            (batch_id,),
        )
        completed_at = legacy_import.utc_now()
        after_raw = count(conn, "SELECT COUNT(*) FROM stream_raw_snapshots")
        after_entries = count(conn, "SELECT COUNT(*) FROM stream_entries_v2")
        after_ready = count(conn, "SELECT COUNT(*) FROM stream_poll_targets WHERE poll_status = 'ready'")
        after_blocked = count(conn, "SELECT COUNT(*) FROM stream_poll_targets WHERE poll_status = 'blocked'")
        conn.execute(
            """
            UPDATE import_batches
            SET completed_at = ?, files_seen = ?, records_imported = ?, failures = ?
            WHERE id = ?
            """,
            (completed_at, before_ready, imported_entries, len(failures), batch_id),
        )
        conn.commit()

        report = {
            "generated_at": completed_at,
            "batch_id": batch_id,
            "parser_version": legacy_import.PARSER_VERSION,
            "staging_db": str(config.staging_db),
            "started_at": started_at,
            "completed_at": completed_at,
            "ready_targets_before": before_ready,
            "blocked_targets_before": before_blocked,
            "ready_targets_after": after_ready,
            "blocked_targets_after": after_blocked,
            "imported_entries": imported_entries,
            "stream_entries_before": before_entries,
            "stream_entries_after": after_entries,
            "raw_snapshots_before": before_raw,
            "raw_snapshots_after": after_raw,
            "raw_snapshots_added": after_raw - before_raw,
            "failures": len(failures),
            "target_statuses": target_statuses(conn),
            "remote_snapshots": latest_remote_snapshots(conn, batch_id),
        }

    write_json(config.output_dir / "stream-poll-report.json", report)
    write_jsonl(config.output_dir / "stream-poll-failures.jsonl", failures)
    return report


def parse_args(argv: list[str]) -> PollWorkerConfig:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staging-db", default="migration/imports/legacy-import.sqlite")
    parser.add_argument("--output-dir", default="migration/imports")
    parser.add_argument(
        "--allow-target-failures",
        action="store_true",
        help="Exit 0 even when one or more feed targets failed and were recorded in the report.",
    )
    args = parser.parse_args(argv)
    return PollWorkerConfig(
        staging_db=Path(args.staging_db).resolve(),
        output_dir=Path(args.output_dir).resolve(),
        fail_on_target_errors=not args.allow_target_failures,
    )


def main(argv: list[str]) -> int:
    config = parse_args(argv)
    try:
        report = run_poll(config)
    except Exception as exc:
        print(f"stream poll worker failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    print(f"Wrote stream poll report to {config.output_dir / 'stream-poll-report.json'}")
    if config.fail_on_target_errors and int(report["failures"]) > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

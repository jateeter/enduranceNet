#!/usr/bin/env python3
"""Generate migration coverage reports from a source inventory database."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class CoverageConfig:
    inventory_db: Path
    output_dir: Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def rows(conn: sqlite3.Connection, sql: str, params: tuple[object, ...] = ()) -> list[dict[str, object]]:
    conn.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in conn.execute(sql, params).fetchall()]
    finally:
        conn.row_factory = None


def scalar(conn: sqlite3.Connection, sql: str, params: tuple[object, ...] = ()) -> int:
    value = conn.execute(sql, params).fetchone()[0]
    return int(value or 0)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def markdown_table(headers: list[str], data: list[dict[str, object]]) -> str:
    if not data:
        return "_None._\n"
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in data:
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    return "\n".join(lines) + "\n"


def generate(config: CoverageConfig) -> None:
    if not config.inventory_db.exists():
        raise FileNotFoundError(f"inventory database not found: {config.inventory_db}")

    config.output_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.inventory_db)
    try:
        total_entries = scalar(conn, "SELECT COUNT(*) FROM files")
        readable_entries = scalar(conn, "SELECT COUNT(*) FROM files WHERE status = 'ok'")
        unreadable_entries = scalar(conn, "SELECT COUNT(*) FROM files WHERE status != 'ok' OR classification = 'unreadable'")
        executable_templates = scalar(conn, "SELECT COUNT(*) FROM files WHERE classification = 'executable_template'")
        media_assets = scalar(conn, "SELECT COUNT(*) FROM files WHERE classification = 'media_asset'")
        data_files = scalar(conn, "SELECT COUNT(*) FROM files WHERE classification = 'data_file'")
        documents = scalar(conn, "SELECT COUNT(*) FROM files WHERE classification = 'document'")
        backup_temp = scalar(conn, "SELECT COUNT(*) FROM files WHERE classification = 'backup_temp'")
        include_edges = scalar(conn, "SELECT COUNT(*) FROM includes")
        unresolved_includes = scalar(
            conn,
            """
            SELECT COUNT(*)
            FROM includes
            WHERE resolved_path = ''
            """,
        )

        classifications = rows(
            conn,
            """
            SELECT classification, COUNT(*) AS count
            FROM files
            GROUP BY classification
            ORDER BY count DESC, classification
            """,
        )
        statuses = rows(
            conn,
            """
            SELECT status, COUNT(*) AS count
            FROM files
            GROUP BY status
            ORDER BY status
            """,
        )
        top_extensions = rows(
            conn,
            """
            SELECT COALESCE(NULLIF(extension, ''), '[none]') AS extension, COUNT(*) AS count
            FROM files
            WHERE kind = 'file'
            GROUP BY extension
            ORDER BY count DESC, extension
            LIMIT 30
            """,
        )
        unreadable = rows(
            conn,
            """
            SELECT path, classification, error
            FROM files
            WHERE status != 'ok' OR classification = 'unreadable'
            ORDER BY path
            """
        )
        include_problems = rows(
            conn,
            """
            SELECT source_path, line, include_kind, expression, resolved_path
            FROM includes
            WHERE resolved_path = ''
            ORDER BY source_path, line
            """
        )
        route_candidates = rows(
            conn,
            """
            SELECT path, classification
            FROM files
            WHERE classification IN ('executable_template', 'backup_temp')
              AND extension IN ('.html', '.htm', '.php')
            ORDER BY path
            LIMIT 50
            """
        )
    finally:
        conn.close()

    summary = {
        "generated_at": utc_now(),
        "inventory_db": str(config.inventory_db),
        "total_entries": total_entries,
        "readable_entries": readable_entries,
        "unreadable_entries": unreadable_entries,
        "executable_templates": executable_templates,
        "media_assets": media_assets,
        "data_files": data_files,
        "documents": documents,
        "backup_temp_artifacts": backup_temp,
        "include_edges": include_edges,
        "unresolved_include_edges": unresolved_includes,
        "classification_counts": classifications,
        "status_counts": statuses,
        "top_extensions": top_extensions,
    }
    write_json(config.output_dir / "coverage-summary.json", summary)

    report = [
        "# Migration Coverage Report",
        "",
        f"Generated: `{summary['generated_at']}`",
        f"Inventory DB: `{config.inventory_db}`",
        "",
        "## Summary",
        "",
        f"- Total entries: `{total_entries}`",
        f"- Readable entries: `{readable_entries}`",
        f"- Unreadable entries: `{unreadable_entries}`",
        f"- Executable templates: `{executable_templates}`",
        f"- Media assets: `{media_assets}`",
        f"- Data files: `{data_files}`",
        f"- Documents: `{documents}`",
        f"- Backup/temp artifacts: `{backup_temp}`",
        f"- Include edges: `{include_edges}`",
        f"- Unresolved include edges: `{unresolved_includes}`",
        "",
        "## Classification Counts",
        "",
        markdown_table(["classification", "count"], classifications),
        "## Status Counts",
        "",
        markdown_table(["status", "count"], statuses),
        "## Top Extensions",
        "",
        markdown_table(["extension", "count"], top_extensions),
        "## Route Candidate Sample",
        "",
        markdown_table(["path", "classification"], route_candidates),
    ]
    (config.output_dir / "coverage-report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    unreadable_report = [
        "# Unreadable Source Entries",
        "",
        markdown_table(["path", "classification", "error"], unreadable),
    ]
    (config.output_dir / "unreadable-report.md").write_text("\n".join(unreadable_report) + "\n", encoding="utf-8")

    include_report = [
        "# Unresolved Include Edges",
        "",
        markdown_table(["source_path", "line", "include_kind", "expression", "resolved_path"], include_problems),
    ]
    (config.output_dir / "include-problems.md").write_text("\n".join(include_report) + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> CoverageConfig:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--inventory-db",
        default="migration/inventory/source-inventory.sqlite",
        help="SQLite database produced by scripts/source_inventory.py.",
    )
    parser.add_argument(
        "--output-dir",
        default="migration/coverage",
        help="Directory for generated coverage reports.",
    )
    args = parser.parse_args(argv)
    return CoverageConfig(Path(args.inventory_db).resolve(), Path(args.output_dir).resolve())


def main(argv: list[str]) -> int:
    try:
        config = parse_args(argv)
        generate(config)
    except Exception as exc:
        print(f"coverage report failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote coverage reports to {config.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

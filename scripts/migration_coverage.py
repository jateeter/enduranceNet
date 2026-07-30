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
    import_summary: Path


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


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def content_domain(path: str) -> str:
    lower = path.lower()
    if lower.startswith("currentnews/"):
        return "current_news"
    if lower.startswith("featuredstories/"):
        return "featured_story"
    if lower.startswith("international/") or lower.startswith("events/") or lower[:4].isdigit():
        return "event"
    if lower.startswith("advertisers/") or lower.startswith("ads/") or lower == "advertisers.xml":
        return "advertiser"
    if lower.startswith("classified") or lower.startswith("market/"):
        return "classified"
    if lower.startswith("ridecamp") or lower.startswith("ridecampfriend/"):
        return "ridecamp"
    if lower.startswith(("gallery/", "gallaries", "pictures/", "images/")):
        return "gallery"
    if lower.startswith("channels/"):
        return "feed"
    return "static_page"


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
        domain_counts = rows(
            conn,
            """
            SELECT path, classification, status
            FROM files
            WHERE kind = 'file'
            ORDER BY path
            """,
        )
        domain_summary: dict[str, dict[str, int]] = {}
        for row in domain_counts:
            domain = content_domain(str(row["path"]))
            domain_summary.setdefault(domain, {"source_files": 0, "readable": 0, "unreadable": 0, "media_assets": 0, "templates": 0})
            domain_summary[domain]["source_files"] += 1
            if row["status"] == "ok":
                domain_summary[domain]["readable"] += 1
            else:
                domain_summary[domain]["unreadable"] += 1
            if row["classification"] == "media_asset":
                domain_summary[domain]["media_assets"] += 1
            if row["classification"] == "executable_template":
                domain_summary[domain]["templates"] += 1

        duplicate_checksums = rows(
            conn,
            """
            SELECT checksum_sha256, COUNT(*) AS count
            FROM files
            WHERE checksum_sha256 != ''
            GROUP BY checksum_sha256
            HAVING COUNT(*) > 1
            ORDER BY count DESC, checksum_sha256
            LIMIT 50
            """,
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

    import_summary = read_json(config.import_summary)
    imported_domain_counts = {
        str(row["content_domain"]): int(row["count"])
        for row in import_summary.get("domain_counts", [])
        if isinstance(row, dict) and "content_domain" in row and "count" in row
    }
    domain_rows = []
    for domain, counts in sorted(domain_summary.items()):
        imported = imported_domain_counts.get(domain, 0)
        domain_rows.append(
            {
                "domain": domain,
                "source_files": counts["source_files"],
                "readable": counts["readable"],
                "unreadable": counts["unreadable"],
                "templates": counts["templates"],
                "media_assets": counts["media_assets"],
                "imported_records": imported,
                "remaining_source_files": max(counts["source_files"] - imported, 0),
            }
        )

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
        "duplicate_checksum_groups": len(duplicate_checksums),
        "import_summary": import_summary,
        "domain_coverage": domain_rows,
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
        "## Import Summary",
        "",
        f"- Import summary file: `{config.import_summary}`",
        f"- Import batch: `{import_summary.get('batch_id', '[missing]')}`",
        f"- Legacy source files imported: `{import_summary.get('legacy_source_files', 0)}`",
        f"- Template pages imported: `{import_summary.get('template_pages', 0)}`",
        f"- Content fragments imported: `{import_summary.get('content_fragments', 0)}`",
        f"- Media assets imported: `{import_summary.get('media_assets', 0)}`",
        f"- Media references imported: `{import_summary.get('media_references', 0)}`",
        f"- Import failures: `{import_summary.get('failures', 0)}`",
        "",
        "## Domain Coverage",
        "",
        markdown_table(
            ["domain", "source_files", "readable", "unreadable", "templates", "media_assets", "imported_records", "remaining_source_files"],
            domain_rows,
        ),
        "## Duplicate Checksum Groups",
        "",
        markdown_table(["checksum_sha256", "count"], duplicate_checksums),
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

    domain_report = [
        "# Migration Domain Backlog",
        "",
        "This report compares source-inventory domains with the current import summary.",
        "",
        markdown_table(
            ["domain", "source_files", "readable", "unreadable", "templates", "media_assets", "imported_records", "remaining_source_files"],
            domain_rows,
        ),
    ]
    (config.output_dir / "domain-backlog.md").write_text("\n".join(domain_report) + "\n", encoding="utf-8")

    evidence_report = [
        "# Verification Evidence Matrix",
        "",
        "| Evidence bucket | Current source | What it proves | What it does not prove |",
        "| --- | --- | --- | --- |",
        f"| Static source inventory | `{config.inventory_db}` | Source tree breadth, unreadable files, template/include shape | Imported content completeness or runtime behavior |",
        f"| Import results | `{config.import_summary}` | Staging importer coverage, failures, domain-level records | Production database parity |",
        "| Link checks | `scripts/check_legacy_redirects.py` | Representative legacy URL redirect behavior for a running deployment | Full-site link exhaustiveness |",
        "| Media checks | `scripts/check_media_manifest.py` | Manifested media URL availability for a running deployment or remote asset host | Full media catalog import completeness |",
        "| Runtime smoke | `scripts/playwright_smoke.py` | Browser-load proof for core public React routes | Hosted production readiness |",
        "",
        "Do not claim production readiness unless all five buckets have current passing evidence.",
    ]
    (config.output_dir / "verification-matrix.md").write_text("\n".join(evidence_report) + "\n", encoding="utf-8")


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
    parser.add_argument(
        "--import-summary",
        default="migration/imports/import-summary.json",
        help="JSON summary produced by scripts/legacy_import.py.",
    )
    args = parser.parse_args(argv)
    return CoverageConfig(Path(args.inventory_db).resolve(), Path(args.output_dir).resolve(), Path(args.import_summary).resolve())


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

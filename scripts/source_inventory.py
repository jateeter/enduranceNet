#!/usr/bin/env python3
"""Inventory the legacy Endurance.Net source tree.

The legacy Apache host executes PHP for .php, .html, and .htm files. This
crawler therefore treats all three extensions as executable templates, records
their include dependencies, and reports permission failures as migration
blockers instead of silently skipping them.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import mimetypes
import os
import re
import sqlite3
import stat
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


EXECUTABLE_EXTENSIONS = {".html", ".htm", ".php"}
DATA_EXTENSIONS = {".xml", ".xsl", ".xslt", ".json", ".csv", ".txt", ".rss", ".atom"}
DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".rtf"}
MEDIA_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".svg",
    ".ico",
    ".mp3",
    ".wav",
    ".mov",
    ".mp4",
    ".m4v",
    ".avi",
    ".psd",
}

PUBLIC_VARIABLES = (
    "pageTitle",
    "secondaryBanner",
    "primaryBanner",
    "NavBar",
    "sectionHead_String",
    "sectionHead_Image",
    "hasFeed",
    "useTableSort",
    "useGeoSelector",
    "isHomePage",
    "domainBase",
    "domainBaseNew",
)

INCLUDE_RE = re.compile(
    r"(?<![A-Za-z0-9_/'\".\-])(?P<kind>include|include_once|require|require_once)"
    r"\s*(?:\(\s*)?(?P<expr>[^;\n]+)",
    re.IGNORECASE,
)
LITERAL_RE = re.compile(r"['\"]([^'\"]+)['\"]")
PHP_BLOCK_RE = re.compile(r"<\?(?:php|=)?(?P<body>.*?)(?:\?>|$)", re.IGNORECASE | re.DOTALL)
ASSIGNMENT_RE = re.compile(
    r"\$(?P<name>"
    + "|".join(re.escape(name) for name in PUBLIC_VARIABLES)
    + r")\s*=\s*(?P<value>[^;\n]+)",
)


@dataclass(frozen=True)
class ScanConfig:
    source_root: Path
    output_dir: Path
    db_path: Path
    max_files: int | None
    checksum: bool
    reset: bool


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_path(path: Path) -> str:
    return str(path).replace(os.sep, "/")


def rel_path(root: Path, path: Path) -> str:
    try:
        return normalize_path(path.relative_to(root))
    except ValueError:
        return normalize_path(path)


def mode_string(mode: int | None) -> str:
    if mode is None:
        return ""
    return stat.filemode(mode)


def octal_mode(mode: int | None) -> str:
    if mode is None:
        return ""
    return oct(mode & 0o7777)


def classify_file(path: Path) -> str:
    name = path.name
    lower_name = name.lower()
    suffix = path.suffix.lower()

    if name.startswith("#") or name.endswith("~") or lower_name.endswith((".bak", ".old", ".save")):
        return "backup_temp"
    if ".bak." in lower_name or "_bak" in lower_name or "_backup" in lower_name:
        return "backup_temp"
    if suffix in EXECUTABLE_EXTENSIONS:
        return "executable_template"
    if suffix in MEDIA_EXTENSIONS:
        return "media_asset"
    if suffix in DATA_EXTENSIONS:
        return "data_file"
    if suffix in DOCUMENT_EXTENSIONS:
        return "document"
    return "unknown"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def open_db(config: ScanConfig) -> sqlite3.Connection:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    if config.reset and config.db_path.exists():
        config.db_path.unlink()
    conn = sqlite3.connect(config.db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS files (
          path TEXT PRIMARY KEY,
          absolute_path TEXT NOT NULL,
          parent_path TEXT NOT NULL,
          kind TEXT NOT NULL,
          classification TEXT NOT NULL,
          extension TEXT NOT NULL,
          size INTEGER,
          mtime REAL,
          mode_octal TEXT NOT NULL,
          mode_string TEXT NOT NULL,
          uid INTEGER,
          gid INTEGER,
          mime_type TEXT NOT NULL,
          checksum_sha256 TEXT NOT NULL,
          status TEXT NOT NULL,
          error TEXT NOT NULL,
          scanned_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS includes (
          source_path TEXT NOT NULL,
          include_kind TEXT NOT NULL,
          expression TEXT NOT NULL,
          target_hint TEXT NOT NULL,
          resolved_path TEXT NOT NULL,
          line INTEGER NOT NULL,
          scanned_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS template_variables (
          source_path TEXT NOT NULL,
          variable_name TEXT NOT NULL,
          value_expression TEXT NOT NULL,
          line INTEGER NOT NULL,
          scanned_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS scan_meta (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        );
        """
    )
    return conn


def record_file(conn: sqlite3.Connection, row: dict[str, object]) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO files (
          path, absolute_path, parent_path, kind, classification, extension,
          size, mtime, mode_octal, mode_string, uid, gid, mime_type,
          checksum_sha256, status, error, scanned_at
        ) VALUES (
          :path, :absolute_path, :parent_path, :kind, :classification,
          :extension, :size, :mtime, :mode_octal, :mode_string, :uid, :gid,
          :mime_type, :checksum_sha256, :status, :error, :scanned_at
        )
        """,
        row,
    )


def is_unchanged(conn: sqlite3.Connection, rel: str, size: int | None, mtime: float | None) -> bool:
    row = conn.execute("SELECT size, mtime, status FROM files WHERE path = ?", (rel,)).fetchone()
    if row is None:
        return False
    old_size, old_mtime, old_status = row
    return old_status == "ok" and old_size == size and old_mtime == mtime


def remove_template_details(conn: sqlite3.Connection, rel: str) -> None:
    conn.execute("DELETE FROM includes WHERE source_path = ?", (rel,))
    conn.execute("DELETE FROM template_variables WHERE source_path = ?", (rel,))


def strip_expression(expr: str) -> str:
    return expr.strip().rstrip(")").strip()


def resolve_include_expression(source_root: Path, source_file: Path, expr: str) -> tuple[str, str]:
    literals = [literal for literal in LITERAL_RE.findall(expr) if literal != "DOCUMENT_ROOT"]
    target_hint = "".join(literals)
    if not target_hint:
        return "", ""

    if "DOCUMENT_ROOT" in expr or target_hint.startswith("/"):
        resolved = source_root / target_hint.lstrip("/")
    else:
        resolved = source_file.parent / target_hint

    return target_hint, rel_path(source_root, resolved)


def php_segments(text: str) -> Iterable[tuple[int, str]]:
    found = False
    for match in PHP_BLOCK_RE.finditer(text):
        found = True
        line_offset = text[: match.start("body")].count("\n")
        yield line_offset, match.group("body")

    if not found:
        return


def parse_template(conn: sqlite3.Connection, config: ScanConfig, path: Path, rel: str, scanned_at: str) -> None:
    remove_template_details(conn, rel)
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return

    for line_offset, segment in php_segments(text):
        for segment_line_no, line in enumerate(segment.splitlines(), 1):
            line_no = line_offset + segment_line_no
            for match in INCLUDE_RE.finditer(line):
                expr = strip_expression(match.group("expr"))
                target_hint, resolved = resolve_include_expression(config.source_root, path, expr)
                conn.execute(
                    """
                    INSERT INTO includes (
                      source_path, include_kind, expression, target_hint,
                      resolved_path, line, scanned_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (rel, match.group("kind"), expr, target_hint, resolved, line_no, scanned_at),
                )
            for match in ASSIGNMENT_RE.finditer(line):
                conn.execute(
                    """
                    INSERT INTO template_variables (
                      source_path, variable_name, value_expression, line, scanned_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        rel,
                        match.group("name"),
                        match.group("value").strip(),
                        line_no,
                        scanned_at,
                    ),
                )


def walk_source(config: ScanConfig, conn: sqlite3.Connection) -> None:
    scanned_at = utc_now()
    conn.execute(
        "INSERT OR REPLACE INTO scan_meta (key, value) VALUES (?, ?)",
        ("source_root", str(config.source_root)),
    )
    conn.execute(
        "INSERT OR REPLACE INTO scan_meta (key, value) VALUES (?, ?)",
        ("last_started_at", scanned_at),
    )

    processed_files = 0
    stack = [config.source_root]
    while stack:
        current = stack.pop()
        current_rel = rel_path(config.source_root, current)
        try:
            with os.scandir(current) as iterator:
                entries = list(iterator)
        except OSError as exc:
            record_file(
                conn,
                {
                    "path": current_rel,
                    "absolute_path": str(current),
                    "parent_path": rel_path(config.source_root, current.parent),
                    "kind": "directory",
                    "classification": "unreadable",
                    "extension": "",
                    "size": None,
                    "mtime": None,
                    "mode_octal": "",
                    "mode_string": "",
                    "uid": None,
                    "gid": None,
                    "mime_type": "",
                    "checksum_sha256": "",
                    "status": "error",
                    "error": f"{type(exc).__name__}: {exc}",
                    "scanned_at": scanned_at,
                },
            )
            conn.commit()
            continue

        for entry in sorted(entries, key=lambda item: item.name.lower()):
            path = Path(entry.path)
            item_rel = rel_path(config.source_root, path)
            try:
                info = entry.stat(follow_symlinks=False)
            except OSError as exc:
                record_file(
                    conn,
                    {
                        "path": item_rel,
                        "absolute_path": str(path),
                        "parent_path": current_rel,
                        "kind": "unknown",
                        "classification": "unreadable",
                        "extension": path.suffix.lower(),
                        "size": None,
                        "mtime": None,
                        "mode_octal": "",
                        "mode_string": "",
                        "uid": None,
                        "gid": None,
                        "mime_type": mimetypes.guess_type(path.name)[0] or "",
                        "checksum_sha256": "",
                        "status": "error",
                        "error": f"{type(exc).__name__}: {exc}",
                        "scanned_at": scanned_at,
                    },
                )
                conn.commit()
                continue

            if stat.S_ISDIR(info.st_mode):
                record_file(
                    conn,
                    {
                        "path": item_rel,
                        "absolute_path": str(path),
                        "parent_path": current_rel,
                        "kind": "directory",
                        "classification": "directory",
                        "extension": "",
                        "size": info.st_size,
                        "mtime": info.st_mtime,
                        "mode_octal": octal_mode(info.st_mode),
                        "mode_string": mode_string(info.st_mode),
                        "uid": info.st_uid,
                        "gid": info.st_gid,
                        "mime_type": "",
                        "checksum_sha256": "",
                        "status": "ok",
                        "error": "",
                        "scanned_at": scanned_at,
                    },
                )
                stack.append(path)
                continue

            kind = "symlink" if stat.S_ISLNK(info.st_mode) else "file"
            classification = classify_file(path) if kind == "file" else "symlink"
            suffix = path.suffix.lower()
            mime_type = mimetypes.guess_type(path.name)[0] or ""

            if is_unchanged(conn, item_rel, info.st_size, info.st_mtime):
                processed_files += 1
                if config.max_files is not None and processed_files >= config.max_files:
                    conn.commit()
                    return
                continue

            checksum = ""
            status = "ok"
            error = ""
            if kind == "file" and config.checksum:
                try:
                    checksum = sha256_file(path)
                except OSError as exc:
                    status = "error"
                    classification = "unreadable"
                    error = f"{type(exc).__name__}: {exc}"

            record_file(
                conn,
                {
                    "path": item_rel,
                    "absolute_path": str(path),
                    "parent_path": current_rel,
                    "kind": kind,
                    "classification": classification,
                    "extension": suffix,
                    "size": info.st_size,
                    "mtime": info.st_mtime,
                    "mode_octal": octal_mode(info.st_mode),
                    "mode_string": mode_string(info.st_mode),
                    "uid": info.st_uid,
                    "gid": info.st_gid,
                    "mime_type": mime_type,
                    "checksum_sha256": checksum,
                    "status": status,
                    "error": error,
                    "scanned_at": scanned_at,
                },
            )

            if status == "ok" and classification == "executable_template":
                parse_template(conn, config, path, item_rel, scanned_at)

            processed_files += 1
            if processed_files % 250 == 0:
                conn.commit()
            if config.max_files is not None and processed_files >= config.max_files:
                conn.commit()
                return

    conn.execute(
        "INSERT OR REPLACE INTO scan_meta (key, value) VALUES (?, ?)",
        ("last_completed_at", utc_now()),
    )
    conn.commit()


def rows_as_dicts(conn: sqlite3.Connection, sql: str, params: Iterable[object] = ()) -> list[dict[str, object]]:
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(sql, tuple(params)).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.row_factory = None


def write_jsonl(path: Path, rows: Iterable[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def legacy_url_for(path: str) -> str:
    if path == ".":
        return "/"
    return "/" + path


def build_route_rows(conn: sqlite3.Connection) -> list[dict[str, object]]:
    templates = rows_as_dicts(
        conn,
        """
        SELECT path, classification
        FROM files
        WHERE classification IN ('executable_template', 'backup_temp')
          AND extension IN ('.html', '.htm', '.php')
        ORDER BY path
        """,
    )
    include_rows = rows_as_dicts(conn, "SELECT source_path, resolved_path FROM includes")
    variable_rows = rows_as_dicts(
        conn,
        "SELECT source_path, variable_name, value_expression FROM template_variables",
    )

    includes_by_source: dict[str, list[str]] = {}
    for row in include_rows:
        includes_by_source.setdefault(str(row["source_path"]), []).append(str(row["resolved_path"]))

    variables_by_source: dict[str, dict[str, str]] = {}
    for row in variable_rows:
        variables_by_source.setdefault(str(row["source_path"]), {})[
            str(row["variable_name"])
        ] = str(row["value_expression"]).strip("'\"")

    route_rows: list[dict[str, object]] = []
    for template in templates:
        path = str(template["path"])
        includes = includes_by_source.get(path, [])
        variables = variables_by_source.get(path, {})
        route_rows.append(
            {
                "source_path": path,
                "legacy_url": legacy_url_for(path),
                "classification": template["classification"],
                "is_default_public_candidate": template["classification"] == "executable_template",
                "page_title": variables.get("pageTitle", ""),
                "section_head": variables.get("sectionHead_String", ""),
                "includes_site_header": any(item.endswith("include/siteHeader.html") for item in includes),
                "includes_common_header": any(item.endswith("include/commonHeader.html") for item in includes),
                "includes_internal_fragment": any(item.endswith("indexInternal.html") for item in includes),
                "includes_site_trailer": any(item.endswith("include/siteTrailer.html") for item in includes),
                "include_count": len(includes),
            }
        )
    return route_rows


def build_include_problem_rows(config: ScanConfig, conn: sqlite3.Connection) -> list[dict[str, object]]:
    include_rows = rows_as_dicts(
        conn,
        """
        SELECT source_path, include_kind, expression, target_hint, resolved_path, line
        FROM includes
        ORDER BY source_path, line
        """,
    )
    problems: list[dict[str, object]] = []
    for row in include_rows:
        resolved = str(row["resolved_path"])
        if not resolved:
            reason = "dynamic_or_unresolved"
        elif not (config.source_root / resolved).exists():
            reason = "target_not_found"
        else:
            continue
        problem = dict(row)
        problem["reason"] = reason
        problems.append(problem)
    return problems


def export_reports(config: ScanConfig, conn: sqlite3.Connection) -> None:
    files = rows_as_dicts(conn, "SELECT * FROM files ORDER BY path")
    unreadable = rows_as_dicts(
        conn,
        "SELECT * FROM files WHERE status != 'ok' OR classification = 'unreadable' ORDER BY path",
    )
    includes = rows_as_dicts(conn, "SELECT * FROM includes ORDER BY source_path, line")
    variables = rows_as_dicts(
        conn,
        "SELECT * FROM template_variables ORDER BY source_path, line, variable_name",
    )
    routes = build_route_rows(conn)
    include_problems = build_include_problem_rows(config, conn)
    classifications = rows_as_dicts(
        conn,
        """
        SELECT classification, COUNT(*) AS count
        FROM files
        GROUP BY classification
        ORDER BY count DESC, classification
        """,
    )
    statuses = rows_as_dicts(
        conn,
        """
        SELECT status, COUNT(*) AS count
        FROM files
        GROUP BY status
        ORDER BY status
        """,
    )

    write_jsonl(config.output_dir / "files.jsonl", files)
    write_jsonl(config.output_dir / "unreadable.jsonl", unreadable)
    write_jsonl(config.output_dir / "template-includes.jsonl", includes)
    write_jsonl(config.output_dir / "template-variables.jsonl", variables)
    write_jsonl(config.output_dir / "template-routes.jsonl", routes)
    write_jsonl(config.output_dir / "template-include-problems.jsonl", include_problems)
    write_csv(config.output_dir / "unreadable.csv", unreadable)

    summary = {
        "generated_at": utc_now(),
        "source_root": str(config.source_root),
        "db_path": str(config.db_path),
        "total_entries": len(files),
        "unreadable_entries": len(unreadable),
        "include_edges": len(includes),
        "include_problems": len(include_problems),
        "template_routes": len(routes),
        "template_variable_assignments": len(variables),
        "classification_counts": classifications,
        "status_counts": statuses,
    }
    (config.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def parse_args(argv: list[str]) -> ScanConfig:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root",
        default="/Volumes/webstore/endurance.net",
        help="Mounted legacy source root.",
    )
    parser.add_argument(
        "--output-dir",
        default="migration/inventory",
        help="Directory for SQLite state and exported reports.",
    )
    parser.add_argument("--max-files", type=int, help="Stop after N files for smoke tests.")
    parser.add_argument("--no-checksum", action="store_true", help="Skip SHA-256 checksums.")
    parser.add_argument("--reset", action="store_true", help="Delete the existing crawler DB first.")
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir).resolve()
    return ScanConfig(
        source_root=Path(args.source_root).resolve(),
        output_dir=output_dir,
        db_path=output_dir / "source-inventory.sqlite",
        max_files=args.max_files,
        checksum=not args.no_checksum,
        reset=args.reset,
    )


def main(argv: list[str]) -> int:
    config = parse_args(argv)
    if not config.source_root.exists():
        print(f"source root does not exist: {config.source_root}", file=sys.stderr)
        return 2

    conn = open_db(config)
    try:
        walk_source(config, conn)
        export_reports(config, conn)
    finally:
        conn.close()

    summary_path = config.output_dir / "summary.json"
    print(f"Wrote inventory reports to {config.output_dir}")
    print(f"Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

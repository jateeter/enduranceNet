#!/usr/bin/env python3
"""Import legacy Endurance.Net inventory records into migration staging tables.

This is the first import-pipeline slice. It reads the source inventory SQLite
database produced by scripts/source_inventory.py, imports provenance-preserving
records into an ignored staging SQLite database, and emits actionable reports.
"""

from __future__ import annotations

import argparse
import html.parser
import json
import os
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


PARSER_VERSION = "legacy-import-v1"
MAX_TEXT_BYTES = 512 * 1024
MEDIA_EXTENSIONS = {
    ".jpg", ".jpeg", ".jpe", ".png", ".gif", ".webp", ".svg", ".ico",
    ".mp3", ".wav", ".mov", ".mp4", ".m4v", ".avi", ".psd",
}
FEED_EXTENSIONS = {".xml", ".rss", ".atom"}
CONTENT_FRAGMENT_NAMES = {"indexinternal.html", "index_content.html", "newsitems.html"}


@dataclass(frozen=True)
class ImportConfig:
    inventory_db: Path
    source_root: Path
    output_dir: Path
    staging_db: Path
    max_records: int | None
    reset: bool


class LinkExtractor(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []
        self.title_parts: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self._in_title = True
        for name, value in attrs:
            if value and name.lower() in {"src", "href"}:
                self.links.append((name.lower(), value.strip()))

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            stripped = " ".join(data.split())
            if stripped:
                self.title_parts.append(stripped)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def rows(conn: sqlite3.Connection, sql: str, params: Iterable[object] = ()) -> list[dict[str, object]]:
    conn.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in conn.execute(sql, tuple(params)).fetchall()]
    finally:
        conn.row_factory = None


def one(conn: sqlite3.Connection, sql: str, params: Iterable[object] = ()) -> object:
    row = conn.execute(sql, tuple(params)).fetchone()
    return row[0] if row else None


def read_text(path: Path) -> str:
    with path.open("rb") as handle:
        data = handle.read(MAX_TEXT_BYTES + 1)
    if len(data) > MAX_TEXT_BYTES:
        data = data[:MAX_TEXT_BYTES]
    return data.decode("utf-8", errors="replace")


def normalize_legacy_url(path: str) -> str:
    if path == ".":
        return "/"
    return "/" + path.replace(os.sep, "/")


def content_domain(path: str) -> str:
    lower = path.lower()
    if lower.startswith("currentnews/"):
        return "current_news"
    if lower.startswith("featuredstories/"):
        return "featured_story"
    if lower.startswith("international/") or lower.startswith("events/") or re.match(r"^\d{4}", lower):
        return "event"
    if lower.startswith("advertisers/") or lower.startswith("ads/") or lower == "advertisers.xml":
        return "advertiser"
    if lower.startswith("classified") or lower.startswith("market/"):
        return "classified"
    if lower.startswith("ridecamp") or lower.startswith("ridecampfriend/"):
        return "ridecamp"
    if lower.startswith("books/"):
        return "book"
    if lower.startswith("channels/"):
        return "feed"
    if lower.startswith(("gallery/", "gallaries", "pictures/", "images/")):
        return "gallery"
    return "static_page"


def init_db(config: ImportConfig) -> sqlite3.Connection:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    if config.reset and config.staging_db.exists():
        config.staging_db.unlink()
    conn = sqlite3.connect(config.staging_db)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS import_batches (
          id TEXT PRIMARY KEY,
          parser_version TEXT NOT NULL,
          inventory_db TEXT NOT NULL,
          source_root TEXT NOT NULL,
          started_at TEXT NOT NULL,
          completed_at TEXT,
          files_seen INTEGER NOT NULL DEFAULT 0,
          records_imported INTEGER NOT NULL DEFAULT 0,
          failures INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS import_failures (
          batch_id TEXT NOT NULL,
          source_path TEXT NOT NULL,
          importer TEXT NOT NULL,
          error TEXT NOT NULL,
          created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS legacy_source_files (
          source_path TEXT PRIMARY KEY,
          legacy_url TEXT NOT NULL,
          classification TEXT NOT NULL,
          content_domain TEXT NOT NULL,
          extension TEXT NOT NULL,
          size INTEGER,
          checksum_sha256 TEXT,
          readable INTEGER NOT NULL,
          permission_mode TEXT,
          scanned_at TEXT NOT NULL,
          import_batch_id TEXT NOT NULL,
          parser_version TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS media_assets (
          source_path TEXT PRIMARY KEY,
          legacy_url TEXT NOT NULL,
          content_domain TEXT NOT NULL,
          mime_type TEXT,
          size INTEGER,
          checksum_sha256 TEXT,
          import_batch_id TEXT NOT NULL,
          parser_version TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS template_pages (
          source_path TEXT PRIMARY KEY,
          legacy_url TEXT NOT NULL,
          content_domain TEXT NOT NULL,
          page_title TEXT,
          section_head TEXT,
          includes_site_header INTEGER NOT NULL,
          includes_internal_fragment INTEGER NOT NULL,
          include_count INTEGER NOT NULL,
          import_batch_id TEXT NOT NULL,
          parser_version TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS content_fragments (
          source_path TEXT PRIMARY KEY,
          legacy_url TEXT NOT NULL,
          content_domain TEXT NOT NULL,
          title TEXT,
          body_html TEXT NOT NULL,
          body_truncated INTEGER NOT NULL,
          import_batch_id TEXT NOT NULL,
          parser_version TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS feed_entries (
          source_path TEXT NOT NULL,
          entry_index INTEGER NOT NULL,
          feed_name TEXT NOT NULL,
          title TEXT,
          link TEXT,
          published_at TEXT,
          summary_html TEXT,
          import_batch_id TEXT NOT NULL,
          parser_version TEXT NOT NULL,
          PRIMARY KEY (source_path, entry_index)
        );

        CREATE TABLE IF NOT EXISTS media_references (
          source_path TEXT NOT NULL,
          referenced_url TEXT NOT NULL,
          referenced_path TEXT,
          attribute TEXT NOT NULL,
          import_batch_id TEXT NOT NULL,
          parser_version TEXT NOT NULL,
          PRIMARY KEY (source_path, referenced_url, attribute)
        );
        """
    )
    return conn


def start_batch(conn: sqlite3.Connection, config: ImportConfig) -> str:
    batch_id = f"{PARSER_VERSION}-{utc_now()}"
    conn.execute(
        """
        INSERT INTO import_batches (id, parser_version, inventory_db, source_root, started_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (batch_id, PARSER_VERSION, str(config.inventory_db), str(config.source_root), utc_now()),
    )
    return batch_id


def record_failure(conn: sqlite3.Connection, batch_id: str, source_path: str, importer: str, exc: Exception) -> None:
    conn.execute(
        """
        INSERT INTO import_failures (batch_id, source_path, importer, error, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (batch_id, source_path, importer, f"{type(exc).__name__}: {exc}", utc_now()),
    )


def import_source_files(inv: sqlite3.Connection, out: sqlite3.Connection, batch_id: str, max_records: int | None) -> int:
    file_rows = rows(inv, "SELECT * FROM files ORDER BY path")
    imported = 0
    for row in file_rows:
        if max_records is not None and imported >= max_records:
            break
        source_path = str(row["path"])
        out.execute(
            """
            INSERT OR REPLACE INTO legacy_source_files (
              source_path, legacy_url, classification, content_domain, extension,
              size, checksum_sha256, readable, permission_mode, scanned_at,
              import_batch_id, parser_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_path,
                normalize_legacy_url(source_path),
                row["classification"],
                content_domain(source_path),
                row["extension"],
                row["size"],
                row["checksum_sha256"],
                1 if row["status"] == "ok" else 0,
                row["mode_octal"],
                row["scanned_at"],
                batch_id,
                PARSER_VERSION,
            ),
        )
        imported += 1
    return imported

def limit_sql(base_sql: str, max_records: int | None) -> str:
    if max_records is None:
        return base_sql
    return f"{base_sql} LIMIT {max_records}"


def import_media_assets(inv: sqlite3.Connection, out: sqlite3.Connection, batch_id: str, max_records: int | None) -> int:
    media_rows = rows(
        inv,
        limit_sql("SELECT * FROM files WHERE classification = 'media_asset' ORDER BY path", max_records),
    )
    for row in media_rows:
        source_path = str(row["path"])
        out.execute(
            """
            INSERT OR REPLACE INTO media_assets (
              source_path, legacy_url, content_domain, mime_type, size,
              checksum_sha256, import_batch_id, parser_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_path,
                normalize_legacy_url(source_path),
                content_domain(source_path),
                row["mime_type"],
                row["size"],
                row["checksum_sha256"],
                batch_id,
                PARSER_VERSION,
            ),
        )
    return len(media_rows)


def variable_map(inv: sqlite3.Connection) -> dict[str, dict[str, str]]:
    mapping: dict[str, dict[str, str]] = {}
    for row in rows(inv, "SELECT source_path, variable_name, value_expression FROM template_variables"):
        value = str(row["value_expression"]).strip().strip("'\"")
        mapping.setdefault(str(row["source_path"]), {})[str(row["variable_name"])] = value
    return mapping


def include_counts(inv: sqlite3.Connection) -> dict[str, dict[str, object]]:
    mapping: dict[str, dict[str, object]] = {}
    for row in rows(inv, "SELECT source_path, resolved_path FROM includes"):
        source = str(row["source_path"])
        resolved = str(row["resolved_path"])
        data = mapping.setdefault(source, {"count": 0, "site_header": False, "internal": False})
        data["count"] = int(data["count"]) + 1
        data["site_header"] = bool(data["site_header"]) or resolved.endswith("include/siteHeader.html")
        data["internal"] = bool(data["internal"]) or resolved.endswith("indexInternal.html")
    return mapping


def import_templates(inv: sqlite3.Connection, out: sqlite3.Connection, config: ImportConfig, batch_id: str) -> int:
    vars_by_source = variable_map(inv)
    includes_by_source = include_counts(inv)
    template_rows = rows(
        inv,
        limit_sql(
        """
        SELECT path, classification
        FROM files
        WHERE classification = 'executable_template'
        ORDER BY path
        """,
        config.max_records,
        ),
    )
    imported = 0
    for row in template_rows:
        source_path = str(row["path"])
        source_file = config.source_root / source_path
        title = vars_by_source.get(source_path, {}).get("pageTitle", "")
        body = ""
        html_title = ""
        truncated = 0
        try:
            text = read_text(source_file)
            truncated = 1 if source_file.stat().st_size > MAX_TEXT_BYTES else 0
            extractor = LinkExtractor()
            extractor.feed(text)
            html_title = " ".join(extractor.title_parts)
            title = title or html_title
            if source_file.name.lower() in CONTENT_FRAGMENT_NAMES or "indexinternal" in source_file.name.lower():
                body = text
            for attribute, url in extractor.links:
                if Path(url.split("?", 1)[0].split("#", 1)[0]).suffix.lower() in MEDIA_EXTENSIONS:
                    referenced_path = url.lstrip("/") if not re.match(r"^[a-z]+://", url, re.I) else None
                    out.execute(
                        """
                        INSERT OR REPLACE INTO media_references (
                          source_path, referenced_url, referenced_path, attribute,
                          import_batch_id, parser_version
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (source_path, url, referenced_path, attribute, batch_id, PARSER_VERSION),
                    )
        except Exception as exc:
            record_failure(out, batch_id, source_path, "template", exc)

        include_data = includes_by_source.get(source_path, {"count": 0, "site_header": False, "internal": False})
        out.execute(
            """
            INSERT OR REPLACE INTO template_pages (
              source_path, legacy_url, content_domain, page_title, section_head,
              includes_site_header, includes_internal_fragment, include_count,
              import_batch_id, parser_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_path,
                normalize_legacy_url(source_path),
                content_domain(source_path),
                title,
                vars_by_source.get(source_path, {}).get("sectionHead_String", ""),
                1 if include_data["site_header"] else 0,
                1 if include_data["internal"] else 0,
                include_data["count"],
                batch_id,
                PARSER_VERSION,
            ),
        )
        if body:
            out.execute(
                """
                INSERT OR REPLACE INTO content_fragments (
                  source_path, legacy_url, content_domain, title, body_html,
                  body_truncated, import_batch_id, parser_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source_path,
                    normalize_legacy_url(source_path),
                    content_domain(source_path),
                    title,
                    body,
                    truncated,
                    batch_id,
                    PARSER_VERSION,
                ),
            )
        imported += 1
    return imported


def text_of(element: ET.Element, names: tuple[str, ...]) -> str:
    for name in names:
        found = element.find(name)
        if found is not None and found.text:
            return " ".join(found.text.split())
        found = element.find(f"{{*}}{name}")
        if found is not None and found.text:
            return " ".join(found.text.split())
    return ""


def link_of(element: ET.Element) -> str:
    link = text_of(element, ("link",))
    if link:
        return link
    for child in list(element):
        if child.tag.endswith("link") and child.attrib.get("href"):
            return child.attrib["href"]
    return ""


def import_feeds(inv: sqlite3.Connection, out: sqlite3.Connection, config: ImportConfig, batch_id: str) -> int:
    feed_rows = rows(
        inv,
        limit_sql(
        """
        SELECT path
        FROM files
        WHERE classification = 'data_file'
          AND extension IN ('.xml', '.rss', '.atom')
        ORDER BY path
        """,
        config.max_records,
        ),
    )
    imported = 0
    for row in feed_rows:
        source_path = str(row["path"])
        source_file = config.source_root / source_path
        try:
            root = ET.fromstring(read_text(source_file))
            entries = [
                element for element in root.iter()
                if element.tag.endswith("entry") or element.tag.endswith("item")
            ]
            for index, entry in enumerate(entries):
                out.execute(
                    """
                    INSERT OR REPLACE INTO feed_entries (
                      source_path, entry_index, feed_name, title, link,
                      published_at, summary_html, import_batch_id, parser_version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        source_path,
                        index,
                        Path(source_path).stem,
                        text_of(entry, ("title",)),
                        link_of(entry),
                        text_of(entry, ("published", "updated", "pubDate")),
                        text_of(entry, ("summary", "description", "content")),
                        batch_id,
                        PARSER_VERSION,
                    ),
                )
                imported += 1
        except Exception as exc:
            record_failure(out, batch_id, source_path, "feed", exc)
    return imported


def write_reports(out: sqlite3.Connection, config: ImportConfig, batch_id: str) -> None:
    summary = {
        "generated_at": utc_now(),
        "batch_id": batch_id,
        "parser_version": PARSER_VERSION,
        "staging_db": str(config.staging_db),
        "legacy_source_files": one(out, "SELECT COUNT(*) FROM legacy_source_files"),
        "media_assets": one(out, "SELECT COUNT(*) FROM media_assets"),
        "template_pages": one(out, "SELECT COUNT(*) FROM template_pages"),
        "content_fragments": one(out, "SELECT COUNT(*) FROM content_fragments"),
        "feed_entries": one(out, "SELECT COUNT(*) FROM feed_entries"),
        "media_references": one(out, "SELECT COUNT(*) FROM media_references"),
        "failures": one(out, "SELECT COUNT(*) FROM import_failures WHERE batch_id = ?", (batch_id,)),
        "domain_counts": rows(
            out,
            """
            SELECT content_domain, COUNT(*) AS count
            FROM legacy_source_files
            GROUP BY content_domain
            ORDER BY count DESC, content_domain
            """,
        ),
    }
    (config.output_dir / "import-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    failures = rows(
        out,
        """
        SELECT source_path, importer, error
        FROM import_failures
        WHERE batch_id = ?
        ORDER BY source_path
        """,
        (batch_id,),
    )
    with (config.output_dir / "import-failures.jsonl").open("w", encoding="utf-8") as handle:
        for failure in failures:
            handle.write(json.dumps(failure, sort_keys=True) + "\n")


def parse_args(argv: list[str]) -> ImportConfig:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory-db", default="migration/inventory/source-inventory.sqlite")
    parser.add_argument("--source-root", default="/Volumes/webstore/endurance.net")
    parser.add_argument("--output-dir", default="migration/imports")
    parser.add_argument("--max-records", type=int, help="Limit legacy_source_file imports for smoke tests.")
    parser.add_argument("--reset", action="store_true", help="Delete existing staging DB first.")
    args = parser.parse_args(argv)
    output_dir = Path(args.output_dir).resolve()
    return ImportConfig(
        inventory_db=Path(args.inventory_db).resolve(),
        source_root=Path(args.source_root).resolve(),
        output_dir=output_dir,
        staging_db=output_dir / "legacy-import.sqlite",
        max_records=args.max_records,
        reset=args.reset,
    )


def main(argv: list[str]) -> int:
    config = parse_args(argv)
    if not config.inventory_db.exists():
        print(f"inventory database not found: {config.inventory_db}", file=sys.stderr)
        return 2
    if not config.source_root.exists():
        print(f"source root not found: {config.source_root}", file=sys.stderr)
        return 2

    inv = sqlite3.connect(config.inventory_db)
    out = init_db(config)
    try:
        batch_id = start_batch(out, config)
        source_count = import_source_files(inv, out, batch_id, config.max_records)
        media_count = import_media_assets(inv, out, batch_id, config.max_records)
        template_count = import_templates(inv, out, config, batch_id)
        feed_count = import_feeds(inv, out, config, batch_id)
        failures = int(one(out, "SELECT COUNT(*) FROM import_failures WHERE batch_id = ?", (batch_id,)) or 0)
        records_imported = source_count + media_count + template_count + feed_count
        out.execute(
            """
            UPDATE import_batches
            SET completed_at = ?, files_seen = ?, records_imported = ?, failures = ?
            WHERE id = ?
            """,
            (utc_now(), source_count, records_imported, failures, batch_id),
        )
        out.commit()
        write_reports(out, config, batch_id)
    finally:
        inv.close()
        out.close()

    print(f"Wrote import staging database to {config.staging_db}")
    print(f"Wrote import reports to {config.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

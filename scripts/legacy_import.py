#!/usr/bin/env python3
"""Import legacy Endurance.Net inventory records into migration staging tables.

This is the first import-pipeline slice. It reads the source inventory SQLite
database produced by scripts/source_inventory.py, imports provenance-preserving
records into an ignored staging SQLite database, and emits actionable reports.
"""

from __future__ import annotations

import argparse
import hashlib
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
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


PARSER_VERSION = "legacy-import-v3"
MAX_TEXT_BYTES = 512 * 1024
MAX_DOMAIN_TEXT_BYTES = 64 * 1024
MEDIA_EXTENSIONS = {
    ".jpg", ".jpeg", ".jpe", ".png", ".gif", ".webp", ".svg", ".ico",
    ".mp3", ".wav", ".mov", ".mp4", ".m4v", ".avi", ".psd",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt",
}
FEED_EXTENSIONS = {".xml", ".rss", ".atom", ".opml", ".xsl", ".xslt"}
CONTENT_FRAGMENT_NAMES = {"indexinternal.html", "index_content.html", "newsitems.html"}
LEGACY_MEDIA_HOSTS = {"endurance.net", "www.endurance.net", "feeds.endurance.net"}


@dataclass(frozen=True)
class ImportConfig:
    inventory_db: Path
    source_root: Path
    output_dir: Path
    staging_db: Path
    max_records: int | None
    reset: bool
    poll_active: bool
    feeds_only: bool


@dataclass(frozen=True)
class FetchResult:
    url: str
    status: int
    body: str
    etag: str | None = None
    last_modified: str | None = None


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
    return read_text_limited(path, MAX_TEXT_BYTES)


def read_text_limited(path: Path, max_bytes: int) -> str:
    with path.open("rb") as handle:
        data = handle.read(max_bytes + 1)
    if len(data) > max_bytes:
        data = data[:max_bytes]
    return data.decode("utf-8", errors="replace")


def checksum_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


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

        CREATE TABLE IF NOT EXISTS stream_sources (
          source_path TEXT PRIMARY KEY,
          title TEXT NOT NULL,
          provider TEXT NOT NULL,
          feed_format TEXT NOT NULL,
          remote_url TEXT,
          local_cache_path TEXT NOT NULL,
          legacy_url TEXT NOT NULL,
          default_presentation TEXT NOT NULL,
          active INTEGER NOT NULL,
          checksum_sha256 TEXT,
          import_batch_id TEXT NOT NULL,
          parser_version TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS stream_snapshots (
          source_path TEXT PRIMARY KEY,
          root_tag TEXT NOT NULL,
          feed_id TEXT,
          title TEXT NOT NULL,
          self_url TEXT,
          alternate_url TEXT,
          next_url TEXT,
          entry_count INTEGER NOT NULL,
          checksum_sha256 TEXT,
          import_batch_id TEXT NOT NULL,
          parser_version TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS stream_raw_snapshots (
          snapshot_id TEXT PRIMARY KEY,
          source_path TEXT NOT NULL,
          source_kind TEXT NOT NULL,
          fetch_url TEXT,
          fetched_at TEXT NOT NULL,
          http_status INTEGER,
          etag TEXT,
          last_modified TEXT,
          checksum_sha256 TEXT,
          raw_text TEXT NOT NULL,
          import_batch_id TEXT NOT NULL,
          parser_version TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS stream_poll_targets (
          source_path TEXT PRIMARY KEY,
          title TEXT NOT NULL,
          provider TEXT NOT NULL,
          feed_format TEXT NOT NULL,
          poll_url TEXT,
          next_url TEXT,
          local_cache_path TEXT NOT NULL,
          active INTEGER NOT NULL,
          poll_status TEXT NOT NULL,
          blocker TEXT,
          last_checksum_sha256 TEXT,
          etag TEXT,
          last_modified TEXT,
          import_batch_id TEXT NOT NULL,
          parser_version TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS stream_entries_v2 (
          source_path TEXT NOT NULL,
          provider_entry_id TEXT NOT NULL,
          entry_index INTEGER NOT NULL,
          title TEXT NOT NULL,
          summary_html TEXT,
          content_html TEXT,
          author TEXT,
          published_at TEXT,
          updated_at TEXT,
          alternate_url TEXT,
          self_url TEXT,
          related_url TEXT,
          comments_url TEXT,
          import_batch_id TEXT NOT NULL,
          parser_version TEXT NOT NULL,
          PRIMARY KEY (source_path, provider_entry_id)
        );

        CREATE TABLE IF NOT EXISTS stream_entries_canonical (
          canonical_entry_id TEXT PRIMARY KEY,
          title TEXT NOT NULL,
          summary_html TEXT,
          content_html TEXT,
          author TEXT,
          published_at TEXT,
          updated_at TEXT,
          alternate_url TEXT,
          self_url TEXT,
          first_source_path TEXT NOT NULL,
          source_count INTEGER NOT NULL,
          first_import_batch_id TEXT NOT NULL,
          last_import_batch_id TEXT NOT NULL,
          parser_version TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS stream_entry_sources (
          canonical_entry_id TEXT NOT NULL,
          source_path TEXT NOT NULL,
          provider_entry_id TEXT NOT NULL,
          import_batch_id TEXT NOT NULL,
          parser_version TEXT NOT NULL,
          PRIMARY KEY (canonical_entry_id, source_path, provider_entry_id)
        );

        CREATE TABLE IF NOT EXISTS structured_data_files (
          source_path TEXT PRIMARY KEY,
          legacy_url TEXT NOT NULL,
          content_domain TEXT NOT NULL,
          format TEXT NOT NULL,
          root_tag TEXT,
          item_count INTEGER NOT NULL,
          checksum_sha256 TEXT,
          import_batch_id TEXT NOT NULL,
          parser_version TEXT NOT NULL
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

        CREATE TABLE IF NOT EXISTS stream_media_references (
          source_path TEXT NOT NULL,
          provider_entry_id TEXT NOT NULL,
          entry_index INTEGER NOT NULL,
          entry_title TEXT NOT NULL,
          referenced_url TEXT NOT NULL,
          normalized_url TEXT NOT NULL,
          referenced_path TEXT,
          media_kind TEXT NOT NULL,
          attribute TEXT NOT NULL,
          blocker TEXT,
          cms_asset_id TEXT,
          import_batch_id TEXT NOT NULL,
          parser_version TEXT NOT NULL,
          PRIMARY KEY (source_path, provider_entry_id, referenced_url, attribute)
        );

        CREATE TABLE IF NOT EXISTS gallery_manifests (
          source_path TEXT PRIMARY KEY,
          legacy_url TEXT NOT NULL,
          title TEXT,
          media_reference_count INTEGER NOT NULL,
          checksum_sha256 TEXT,
          import_batch_id TEXT NOT NULL,
          parser_version TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS advertiser_records (
          source_path TEXT PRIMARY KEY,
          legacy_url TEXT NOT NULL,
          name TEXT NOT NULL,
          website_url TEXT,
          body_html TEXT,
          body_truncated INTEGER NOT NULL,
          logo_reference_count INTEGER NOT NULL,
          checksum_sha256 TEXT,
          import_batch_id TEXT NOT NULL,
          parser_version TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS classified_records (
          source_path TEXT PRIMARY KEY,
          legacy_url TEXT NOT NULL,
          category TEXT NOT NULL,
          title TEXT NOT NULL,
          body_html TEXT,
          body_truncated INTEGER NOT NULL,
          media_reference_count INTEGER NOT NULL,
          checksum_sha256 TEXT,
          import_batch_id TEXT NOT NULL,
          parser_version TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS ridecamp_messages (
          source_path TEXT PRIMARY KEY,
          legacy_url TEXT NOT NULL,
          subject TEXT NOT NULL,
          author_display TEXT,
          posted_at TEXT,
          body_html TEXT,
          body_truncated INTEGER NOT NULL,
          previous_by_date_url TEXT,
          next_by_date_url TEXT,
          previous_by_thread_url TEXT,
          next_by_thread_url TEXT,
          checksum_sha256 TEXT,
          import_batch_id TEXT NOT NULL,
          parser_version TEXT NOT NULL
        );
        """
    )
    return conn


def start_batch(conn: sqlite3.Connection, config: ImportConfig) -> str:
    precise_stamp = datetime.now(timezone.utc).isoformat(timespec="microseconds")
    batch_id = f"{PARSER_VERSION}-{precise_stamp}"
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


def child_elements(element: ET.Element, child_name: str) -> list[ET.Element]:
    return [child for child in list(element) if local_name(child.tag) == child_name]


def atom_link_map(element: ET.Element) -> dict[str, str]:
    links: dict[str, str] = {}
    for child in child_elements(element, "link"):
        rel = child.attrib.get("rel") or "alternate"
        href = child.attrib.get("href") or (child.text or "")
        if href and rel not in links:
            links[rel] = href.strip()
    text_link = text_of(element, ("link",))
    if text_link and "alternate" not in links:
        links["alternate"] = text_link
    return links


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def feed_entry_elements(root: ET.Element) -> list[ET.Element]:
    return [
        element for element in root.iter()
        if local_name(element.tag) in {"entry", "item"}
    ]


def opml_outline_elements(root: ET.Element) -> list[ET.Element]:
    return [
        element for element in root.iter()
        if local_name(element.tag) == "outline"
        and (element.attrib.get("xmlUrl") or element.attrib.get("htmlUrl") or element.attrib.get("url"))
    ]


def feed_title(root: ET.Element, source_path: str) -> str:
    title = text_of(root, ("title",))
    if title:
        return title
    return title_from_path(source_path)


def feed_format(root: ET.Element, source_path: str) -> str:
    root_name = local_name(root.tag)
    if root_name == "feed":
        namespace = root.tag.split("}", 1)[0].lstrip("{") if root.tag.startswith("{") else ""
        if namespace == "http://purl.org/atom/ns#":
            return "atom-blogger"
        return "atom-1.0"
    if root_name == "rss":
        version = root.attrib.get("version", "2.0")
        return f"rss-{version}"
    if root_name == "opml":
        return "opml"
    if root_name == "stylesheet":
        return "xslt"
    return Path(source_path).suffix.lower().lstrip(".") or root_name


def feed_provider(root: ET.Element, source_path: str) -> str:
    root_name = local_name(root.tag)
    if root_name == "opml":
        return "opml"
    if root_name == "stylesheet":
        return "xslt"
    values = " ".join(
        value.lower()
        for value in [text_of(root, ("generator", "id")), source_path]
        if value
    )
    if "blogger" in values or "blogspot" in values or "tag:blogger.com" in values:
        return "blogger"
    if root_name == "rss":
        return "rss"
    if root_name == "feed":
        return "atom"
    return "xml"


def default_presentation_for(source_path: str, detected_format: str) -> str:
    lower = source_path.lower()
    if detected_format == "opml":
        return "stream-directory"
    if detected_format == "xslt":
        return "xslt-template"
    if "whereintheworld" in lower:
        return "popup-channel-card"
    if "wec" in lower or "event" in lower:
        return "event-story-list"
    if detected_format.startswith("rss"):
        return "rss-list"
    return "atom-list"


def entry_author(entry: ET.Element) -> str:
    for author in child_elements(entry, "author"):
        name = text_of(author, ("name",))
        if name:
            return name
    return text_of(entry, ("author", "creator"))


def entry_provider_id(entry: ET.Element, source_path: str, index: int) -> str:
    entry_id = text_of(entry, ("id", "guid"))
    if entry_id:
        return entry_id
    link = link_of(entry)
    if link:
        return link
    return f"{source_path}#{index}"


def entry_content(entry: ET.Element) -> str:
    for name in ("content", "encoded", "description"):
        value = text_of(entry, (name,))
        if value:
            return value
    return ""


def insert_stream_source(
    inv: sqlite3.Connection,
    out: sqlite3.Connection,
    batch_id: str,
    source_path: str,
    source_text: str,
    root: ET.Element,
    entries: list[ET.Element],
    outlines: list[ET.Element],
) -> None:
    links = atom_link_map(root)
    detected_format = feed_format(root, source_path)
    provider = feed_provider(root, source_path)
    title = feed_title(root, source_path)
    remote_url = links.get("self") or links.get("alternate")
    checksum = one(inv, "SELECT checksum_sha256 FROM files WHERE path = ?", (source_path,))
    out.execute(
        """
        INSERT OR REPLACE INTO stream_sources (
          source_path, title, provider, feed_format, remote_url,
          local_cache_path, legacy_url, default_presentation, active,
          checksum_sha256, import_batch_id, parser_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            source_path,
            title,
            provider,
            detected_format,
            remote_url,
            source_path,
            normalize_legacy_url(source_path),
            default_presentation_for(source_path, detected_format),
            1 if provider in {"blogger", "rss", "atom"} and bool(remote_url) else 0,
            checksum,
            batch_id,
            PARSER_VERSION,
        ),
    )
    out.execute(
        """
        INSERT OR REPLACE INTO stream_snapshots (
          source_path, root_tag, feed_id, title, self_url, alternate_url,
          next_url, entry_count, checksum_sha256, import_batch_id, parser_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            source_path,
            local_name(root.tag),
            text_of(root, ("id",)),
            title,
            links.get("self"),
            links.get("alternate"),
            links.get("next"),
            len(entries) if entries else len(outlines),
            checksum,
            batch_id,
            PARSER_VERSION,
        ),
    )
    out.execute(
        """
        INSERT OR REPLACE INTO stream_raw_snapshots (
          snapshot_id, source_path, source_kind, fetch_url, fetched_at,
          http_status, etag, last_modified, checksum_sha256, raw_text,
          import_batch_id, parser_version
        ) VALUES (?, ?, 'local-cache', ?, ?, NULL, NULL, NULL, ?, ?, ?, ?)
        """,
        (
            f"local:{source_path}:{checksum}",
            source_path,
            remote_url,
            utc_now(),
            checksum,
            source_text,
            batch_id,
            PARSER_VERSION,
        ),
    )
    insert_stream_poll_target(
        out,
        batch_id,
        source_path,
        title,
        provider,
        detected_format,
        remote_url,
        links.get("next"),
        checksum,
        1 if provider in {"blogger", "rss", "atom"} and bool(remote_url) else 0,
    )


def canonical_poll_url(provider: str, remote_url: str | None) -> str | None:
    if not remote_url:
        return None
    if provider != "blogger":
        return remote_url
    secure = remote_url.replace("http://www.blogger.com/", "https://www.blogger.com/")
    if "alt=" in secure:
        return secure
    separator = "&" if "?" in secure else "?"
    return f"{secure}{separator}alt=rss"


def insert_stream_poll_target(
    out: sqlite3.Connection,
    batch_id: str,
    source_path: str,
    title: str,
    provider: str,
    detected_format: str,
    remote_url: str | None,
    next_url: str | None,
    checksum: object,
    active: int,
) -> None:
    poll_url = canonical_poll_url(provider, remote_url)
    blocker = None if active and poll_url else "no remote poll URL discovered from local feed snapshot"
    out.execute(
        """
        INSERT OR REPLACE INTO stream_poll_targets (
          source_path, title, provider, feed_format, poll_url, next_url,
          local_cache_path, active, poll_status, blocker, last_checksum_sha256,
          etag, last_modified, import_batch_id, parser_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?)
        """,
        (
            source_path,
            title,
            provider,
            detected_format,
            poll_url,
            next_url,
            source_path,
            active,
            "ready" if active and poll_url else "blocked",
            blocker,
            checksum,
            batch_id,
            PARSER_VERSION,
        ),
    )


def fetch_stream_url(url: str, etag: str | None = None, last_modified: str | None = None) -> FetchResult:
    headers = {"User-Agent": "EnduranceNetNextGenImporter/1.0"}
    if etag:
        headers["If-None-Match"] = etag
    if last_modified:
        headers["If-Modified-Since"] = last_modified
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=30) as response:
            body = response.read(MAX_TEXT_BYTES).decode("utf-8", errors="replace")
            return FetchResult(
                url=response.geturl(),
                status=getattr(response, "status", 200),
                body=body,
                etag=response.headers.get("ETag"),
                last_modified=response.headers.get("Last-Modified"),
            )
    except HTTPError as exc:
        if exc.code == 304:
            return FetchResult(url=url, status=304, body="", etag=etag, last_modified=last_modified)
        raise


def insert_raw_stream_snapshot(
    out: sqlite3.Connection,
    batch_id: str,
    source_path: str,
    source_kind: str,
    fetch_url: str | None,
    http_status: int | None,
    etag: str | None,
    last_modified: str | None,
    checksum: str | None,
    source_text: str,
) -> None:
    snapshot_id = f"{source_kind}:{source_path}:{checksum or 'no-checksum'}"
    out.execute(
        """
        INSERT OR REPLACE INTO stream_raw_snapshots (
          snapshot_id, source_path, source_kind, fetch_url, fetched_at,
          http_status, etag, last_modified, checksum_sha256, raw_text,
          import_batch_id, parser_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            snapshot_id,
            source_path,
            source_kind,
            fetch_url,
            utc_now(),
            http_status,
            etag,
            last_modified,
            checksum,
            source_text,
            batch_id,
            PARSER_VERSION,
        ),
    )


def poll_active_streams(
    out: sqlite3.Connection,
    batch_id: str,
    fetcher=fetch_stream_url,
) -> int:
    targets = rows(
        out,
        """
        SELECT source_path, poll_url, etag, last_modified
        FROM stream_poll_targets
        WHERE active = 1
          AND poll_status = 'ready'
          AND poll_url IS NOT NULL
        ORDER BY source_path
        """,
    )
    imported = 0
    for target in targets:
        source_path = str(target["source_path"])
        poll_url = str(target["poll_url"])
        try:
            result = fetcher(poll_url, target.get("etag"), target.get("last_modified"))
            if result.status == 304:
                continue
            root = ET.fromstring(result.body)
            entries = feed_entry_elements(root)
            outlines = opml_outline_elements(root)
            links = atom_link_map(root)
            checksum = checksum_text(result.body)
            insert_raw_stream_snapshot(
                out,
                batch_id,
                source_path,
                "remote-poll",
                result.url,
                result.status,
                result.etag,
                result.last_modified,
                checksum,
                result.body,
            )
            out.execute(
                """
                INSERT OR REPLACE INTO stream_snapshots (
                  source_path, root_tag, feed_id, title, self_url, alternate_url,
                  next_url, entry_count, checksum_sha256, import_batch_id, parser_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source_path,
                    local_name(root.tag),
                    text_of(root, ("id",)),
                    feed_title(root, source_path),
                    links.get("self"),
                    links.get("alternate"),
                    links.get("next"),
                    len(entries) if entries else len(outlines),
                    checksum,
                    batch_id,
                    PARSER_VERSION,
                ),
            )
            for index, entry in enumerate(entries):
                insert_stream_entry(None, out, batch_id, source_path, index, entry)
                imported += 1
            for index, outline in enumerate(outlines):
                insert_stream_outline(out, batch_id, source_path, index, outline)
                imported += 1
            out.execute(
                """
                UPDATE stream_poll_targets
                SET next_url = ?, poll_status = 'ready', blocker = NULL,
                    last_checksum_sha256 = ?, etag = ?, last_modified = ?,
                    import_batch_id = ?, parser_version = ?
                WHERE source_path = ?
                """,
                (
                    links.get("next"),
                    checksum,
                    result.etag,
                    result.last_modified,
                    batch_id,
                    PARSER_VERSION,
                    source_path,
                ),
            )
        except Exception as exc:
            record_failure(out, batch_id, source_path, "stream-poll", exc)
            out.execute(
                """
                UPDATE stream_poll_targets
                SET poll_status = 'blocked', blocker = ?, import_batch_id = ?,
                    parser_version = ?
                WHERE source_path = ?
                """,
                (f"{type(exc).__name__}: {exc}", batch_id, PARSER_VERSION, source_path),
            )
    return imported


def insert_stream_entry(
    inv: sqlite3.Connection | None,
    out: sqlite3.Connection,
    batch_id: str,
    source_path: str,
    index: int,
    entry: ET.Element,
) -> None:
    links = atom_link_map(entry)
    provider_entry_id = entry_provider_id(entry, source_path, index)
    title = text_of(entry, ("title",)) or title_from_path(source_path)
    summary_html = text_of(entry, ("summary", "description"))
    content_html = entry_content(entry)
    out.execute(
        "DELETE FROM stream_media_references WHERE source_path = ? AND provider_entry_id = ?",
        (source_path, provider_entry_id),
    )
    out.execute(
        """
        INSERT OR REPLACE INTO stream_entries_v2 (
          source_path, provider_entry_id, entry_index, title, summary_html,
          content_html, author, published_at, updated_at, alternate_url,
          self_url, related_url, comments_url, import_batch_id, parser_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            source_path,
            provider_entry_id,
            index,
            title,
            summary_html,
            content_html,
            entry_author(entry),
            text_of(entry, ("published", "pubDate")),
            text_of(entry, ("updated",)),
            links.get("alternate"),
            links.get("self"),
            links.get("related"),
            links.get("replies"),
            batch_id,
            PARSER_VERSION,
        ),
    )
    insert_canonical_stream_entry(
        out,
        batch_id,
        provider_entry_id,
        source_path,
        provider_entry_id,
        title,
        summary_html,
        content_html,
        entry_author(entry),
        text_of(entry, ("published", "pubDate")),
        text_of(entry, ("updated",)),
        links.get("alternate"),
        links.get("self"),
    )
    record_stream_media_references(
        inv,
        out,
        batch_id,
        source_path,
        provider_entry_id,
        index,
        title,
        " ".join(value for value in (summary_html, content_html) if value),
    )


def insert_stream_outline(
    out: sqlite3.Connection,
    batch_id: str,
    source_path: str,
    index: int,
    outline: ET.Element,
) -> None:
    link = outline.attrib.get("xmlUrl") or outline.attrib.get("htmlUrl") or outline.attrib.get("url") or ""
    title = outline.attrib.get("text") or outline.attrib.get("title") or title_from_path(link or source_path)
    out.execute(
        """
        INSERT OR REPLACE INTO stream_entries_v2 (
          source_path, provider_entry_id, entry_index, title, summary_html,
          content_html, author, published_at, updated_at, alternate_url,
          self_url, related_url, comments_url, import_batch_id, parser_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            source_path,
            link or f"{source_path}#{index}",
            index,
            title,
            outline.attrib.get("description") or "",
            "",
            "",
            "",
            "",
            link,
            outline.attrib.get("xmlUrl") or "",
            "",
            "",
            batch_id,
            PARSER_VERSION,
        ),
    )
    insert_canonical_stream_entry(
        out,
        batch_id,
        link or f"{source_path}#{index}",
        source_path,
        link or f"{source_path}#{index}",
        title,
        outline.attrib.get("description") or "",
        "",
        "",
        "",
        "",
        link,
        outline.attrib.get("xmlUrl") or "",
    )


def insert_canonical_stream_entry(
    out: sqlite3.Connection,
    batch_id: str,
    canonical_entry_id: str,
    source_path: str,
    provider_entry_id: str,
    title: str,
    summary_html: str,
    content_html: str,
    author: str,
    published_at: str,
    updated_at: str,
    alternate_url: str | None,
    self_url: str | None,
) -> None:
    out.execute(
        """
        INSERT OR IGNORE INTO stream_entries_canonical (
          canonical_entry_id, title, summary_html, content_html, author,
          published_at, updated_at, alternate_url, self_url, first_source_path,
          source_count, first_import_batch_id, last_import_batch_id,
          parser_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
        """,
        (
            canonical_entry_id,
            title,
            summary_html,
            content_html,
            author,
            published_at,
            updated_at,
            alternate_url,
            self_url,
            source_path,
            batch_id,
            batch_id,
            PARSER_VERSION,
        ),
    )
    out.execute(
        """
        INSERT OR IGNORE INTO stream_entry_sources (
          canonical_entry_id, source_path, provider_entry_id,
          import_batch_id, parser_version
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (canonical_entry_id, source_path, provider_entry_id, batch_id, PARSER_VERSION),
    )
    out.execute(
        """
        UPDATE stream_entries_canonical
        SET source_count = (
              SELECT COUNT(*)
              FROM stream_entry_sources
              WHERE canonical_entry_id = ?
            ),
            last_import_batch_id = ?,
            parser_version = ?
        WHERE canonical_entry_id = ?
        """,
        (canonical_entry_id, batch_id, PARSER_VERSION, canonical_entry_id),
    )


def import_feeds(inv: sqlite3.Connection, out: sqlite3.Connection, config: ImportConfig, batch_id: str) -> int:
    extension_list = ", ".join(f"'{extension}'" for extension in sorted(FEED_EXTENSIONS))
    feed_rows = rows(
        inv,
        limit_sql(
        f"""
        SELECT path
        FROM files
        WHERE classification IN ('data_file', 'unknown')
          AND extension IN ({extension_list})
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
            source_text = read_text(source_file)
            root = ET.fromstring(source_text)
            entries = feed_entry_elements(root)
            outlines = opml_outline_elements(root)
            item_count = len(entries) if entries else len(outlines)
            insert_stream_source(inv, out, batch_id, source_path, source_text, root, entries, outlines)
            out.execute(
                """
                INSERT OR REPLACE INTO structured_data_files (
                  source_path, legacy_url, content_domain, format, root_tag,
                  item_count, checksum_sha256, import_batch_id, parser_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source_path,
                    normalize_legacy_url(source_path),
                    content_domain(source_path),
                    Path(source_path).suffix.lower().lstrip("."),
                    local_name(root.tag),
                    item_count,
                    one(inv, "SELECT checksum_sha256 FROM files WHERE path = ?", (source_path,)),
                    batch_id,
                    PARSER_VERSION,
                ),
            )
            for index, entry in enumerate(entries):
                insert_stream_entry(inv, out, batch_id, source_path, index, entry)
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
            for index, outline in enumerate(outlines):
                insert_stream_outline(out, batch_id, source_path, index, outline)
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
                        outline.attrib.get("text") or outline.attrib.get("title") or "",
                        outline.attrib.get("xmlUrl") or outline.attrib.get("htmlUrl") or outline.attrib.get("url") or "",
                        "",
                        outline.attrib.get("description") or "",
                        batch_id,
                        PARSER_VERSION,
                    ),
                )
                imported += 1
        except Exception as exc:
            record_failure(out, batch_id, source_path, "feed", exc)
    return imported


def relative_rows(inv: sqlite3.Connection, where_sql: str, max_records: int | None) -> list[dict[str, object]]:
    return rows(
        inv,
        limit_sql(
            f"""
            SELECT *
            FROM files
            WHERE kind = 'file'
              AND status = 'ok'
              AND ({where_sql})
            ORDER BY path
            """,
            max_records,
        ),
    )


def media_link_count(links: list[tuple[str, str]]) -> int:
    return sum(
        1 for _, url in links
        if Path(url.split("?", 1)[0].split("#", 1)[0]).suffix.lower() in MEDIA_EXTENSIONS
    )


def media_reference_kind(url: str) -> str:
    suffix = Path(url.split("?", 1)[0].split("#", 1)[0]).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".jpe", ".png", ".gif", ".webp", ".svg", ".ico", ".psd"}:
        return "image"
    if suffix in {".mp3", ".wav"}:
        return "audio"
    if suffix in {".mov", ".mp4", ".m4v", ".avi"}:
        return "video"
    if suffix:
        return "document"
    return "unknown"


def is_media_reference(url: str) -> bool:
    return Path(url.split("?", 1)[0].split("#", 1)[0]).suffix.lower() in MEDIA_EXTENSIONS


def normalize_media_url(url: str) -> tuple[str, str | None]:
    if re.match(r"^https?://", url, re.I):
        parsed = urlparse(url)
        if parsed.hostname and parsed.hostname.lower() in LEGACY_MEDIA_HOSTS:
            normalized = f"/legacy-media{parsed.path}"
            if parsed.query:
                normalized = f"{normalized}?{parsed.query}"
            return normalized, parsed.path.lstrip("/")
        return url, None
    if url.startswith("/"):
        return f"/legacy-media{url}", url.lstrip("/")
    return f"/legacy-media/{url}", url


def media_blocker(inv: sqlite3.Connection | None, referenced_path: str | None) -> str | None:
    if not inv or not referenced_path:
        return None
    row = inv.execute("SELECT status FROM files WHERE path = ?", (referenced_path,)).fetchone()
    if not row:
        return "unresolved legacy media path"
    if row[0] != "ok":
        return f"legacy media status: {row[0]}"
    return None


def record_stream_media_references(
    inv: sqlite3.Connection | None,
    out: sqlite3.Connection,
    batch_id: str,
    source_path: str,
    provider_entry_id: str,
    entry_index: int,
    entry_title: str,
    html_text: str,
) -> None:
    if not html_text:
        return
    extractor = LinkExtractor()
    extractor.feed(html_text)
    for attribute, url in extractor.links:
        if not is_media_reference(url):
            continue
        normalized_url, referenced_path = normalize_media_url(url)
        out.execute(
            """
            INSERT OR REPLACE INTO stream_media_references (
              source_path, provider_entry_id, entry_index, entry_title,
              referenced_url, normalized_url, referenced_path, media_kind,
              attribute, blocker, cms_asset_id, import_batch_id, parser_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?)
            """,
            (
                source_path,
                provider_entry_id,
                entry_index,
                entry_title,
                url,
                normalized_url,
                referenced_path,
                media_reference_kind(url),
                attribute,
                media_blocker(inv, referenced_path),
                batch_id,
                PARSER_VERSION,
            ),
        )


def first_external_link(links: list[tuple[str, str]]) -> str:
    for _, url in links:
        if re.match(r"^https?://", url, re.I):
            return url
    return ""


def extract_page(path: Path) -> tuple[str, list[tuple[str, str]], str, int]:
    size = path.stat().st_size
    text = read_text_limited(path, MAX_DOMAIN_TEXT_BYTES)
    extractor = LinkExtractor()
    extractor.feed(text)
    return " ".join(extractor.title_parts), extractor.links, text, 1 if size > MAX_DOMAIN_TEXT_BYTES else 0


def title_from_path(source_path: str) -> str:
    stem = Path(source_path).stem.replace("_", " ").replace("-", " ").strip()
    return " ".join(stem.split()) or source_path


def import_gallery_manifests(inv: sqlite3.Connection, out: sqlite3.Connection, config: ImportConfig, batch_id: str) -> int:
    gallery_rows = relative_rows(
        inv,
        "lower(path) LIKE 'gallery/%' OR lower(path) LIKE 'gallaries/%' OR lower(path) LIKE 'pictures/%' OR lower(path) LIKE 'images/%'",
        config.max_records,
    )
    imported = 0
    for row in gallery_rows:
        source_path = str(row["path"])
        if str(row["classification"]) == "media_asset":
            continue
        try:
            title, links, _, _ = extract_page(config.source_root / source_path)
            out.execute(
                """
                INSERT OR REPLACE INTO gallery_manifests (
                  source_path, legacy_url, title, media_reference_count,
                  checksum_sha256, import_batch_id, parser_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source_path,
                    normalize_legacy_url(source_path),
                    title or title_from_path(source_path),
                    media_link_count(links),
                    row["checksum_sha256"],
                    batch_id,
                    PARSER_VERSION,
                ),
            )
            imported += 1
        except Exception as exc:
            record_failure(out, batch_id, source_path, "gallery", exc)
    return imported


def import_advertisers(inv: sqlite3.Connection, out: sqlite3.Connection, config: ImportConfig, batch_id: str) -> int:
    advertiser_rows = relative_rows(
        inv,
        "lower(path) LIKE 'advertisers/%' OR lower(path) LIKE 'ads/%' OR lower(path) = 'advertisers.xml'",
        config.max_records,
    )
    imported = 0
    for row in advertiser_rows:
        source_path = str(row["path"])
        if str(row["classification"]) == "media_asset":
            continue
        try:
            title, links, body, truncated = extract_page(config.source_root / source_path)
            out.execute(
                """
                INSERT OR REPLACE INTO advertiser_records (
                  source_path, legacy_url, name, website_url, body_html,
                  body_truncated, logo_reference_count, checksum_sha256,
                  import_batch_id, parser_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source_path,
                    normalize_legacy_url(source_path),
                    title or title_from_path(source_path),
                    first_external_link(links),
                    body,
                    truncated,
                    media_link_count(links),
                    row["checksum_sha256"],
                    batch_id,
                    PARSER_VERSION,
                ),
            )
            imported += 1
        except Exception as exc:
            record_failure(out, batch_id, source_path, "advertiser", exc)
    return imported


def import_classifieds(inv: sqlite3.Connection, out: sqlite3.Connection, config: ImportConfig, batch_id: str) -> int:
    classified_rows = relative_rows(
        inv,
        "lower(path) LIKE 'classified%' OR lower(path) LIKE 'market/%'",
        config.max_records,
    )
    imported = 0
    for row in classified_rows:
        source_path = str(row["path"])
        if str(row["classification"]) == "media_asset":
            continue
        try:
            title, links, body, truncated = extract_page(config.source_root / source_path)
            out.execute(
                """
                INSERT OR REPLACE INTO classified_records (
                  source_path, legacy_url, category, title, body_html,
                  body_truncated, media_reference_count, checksum_sha256,
                  import_batch_id, parser_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source_path,
                    normalize_legacy_url(source_path),
                    Path(source_path).parts[0] if Path(source_path).parts else "classified",
                    title or title_from_path(source_path),
                    body,
                    truncated,
                    media_link_count(links),
                    row["checksum_sha256"],
                    batch_id,
                    PARSER_VERSION,
                ),
            )
            imported += 1
        except Exception as exc:
            record_failure(out, batch_id, source_path, "classified", exc)
    return imported


def import_ridecamp_messages(inv: sqlite3.Connection, out: sqlite3.Connection, config: ImportConfig, batch_id: str) -> int:
    ridecamp_rows = relative_rows(
        inv,
        "lower(path) LIKE 'ridecamp%' OR lower(path) LIKE 'ridecampfriend/%'",
        config.max_records,
    )
    imported = 0
    for row in ridecamp_rows:
        source_path = str(row["path"])
        if str(row["classification"]) == "media_asset":
            continue
        try:
            title, links, body, truncated = extract_page(config.source_root / source_path)
            hrefs = [url for _, url in links]
            out.execute(
                """
                INSERT OR REPLACE INTO ridecamp_messages (
                  source_path, legacy_url, subject, author_display, posted_at,
                  body_html, body_truncated, previous_by_date_url, next_by_date_url,
                  previous_by_thread_url, next_by_thread_url, checksum_sha256,
                  import_batch_id, parser_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source_path,
                    normalize_legacy_url(source_path),
                    title or title_from_path(source_path),
                    "",
                    "",
                    body,
                    truncated,
                    hrefs[0] if len(hrefs) > 0 else "",
                    hrefs[1] if len(hrefs) > 1 else "",
                    hrefs[2] if len(hrefs) > 2 else "",
                    hrefs[3] if len(hrefs) > 3 else "",
                    row["checksum_sha256"],
                    batch_id,
                    PARSER_VERSION,
                ),
            )
            imported += 1
        except Exception as exc:
            record_failure(out, batch_id, source_path, "ridecamp", exc)
    return imported


def write_reports(out: sqlite3.Connection, config: ImportConfig, batch_id: str) -> None:
    archival_stream_coverage = rows(
        out,
        """
        SELECT
          source.source_path,
          source.title,
          source.provider,
          source.feed_format,
          source.remote_url,
          source.local_cache_path,
          source.legacy_url,
          source.default_presentation,
          source.active,
          target.poll_status,
          target.blocker,
          COALESCE(source_entries.entry_count, 0) AS source_entry_count,
          COALESCE(canonical_entries.entry_count, 0) AS canonical_entry_count
        FROM stream_sources source
        LEFT JOIN stream_poll_targets target
          ON target.source_path = source.source_path
        LEFT JOIN (
          SELECT source_path, COUNT(*) AS entry_count
          FROM stream_entries_v2
          GROUP BY source_path
        ) source_entries
          ON source_entries.source_path = source.source_path
        LEFT JOIN (
          SELECT source_path, COUNT(DISTINCT canonical_entry_id) AS entry_count
          FROM stream_entry_sources
          GROUP BY source_path
        ) canonical_entries
          ON canonical_entries.source_path = source.source_path
        ORDER BY source.active DESC, source.title ASC, source.source_path ASC
        """,
    )
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
        "stream_sources": one(out, "SELECT COUNT(*) FROM stream_sources"),
        "stream_snapshots": one(out, "SELECT COUNT(*) FROM stream_snapshots"),
        "stream_raw_snapshots": one(out, "SELECT COUNT(*) FROM stream_raw_snapshots"),
        "stream_poll_targets": one(out, "SELECT COUNT(*) FROM stream_poll_targets"),
        "stream_poll_ready": one(out, "SELECT COUNT(*) FROM stream_poll_targets WHERE poll_status = 'ready'"),
        "stream_poll_blocked": one(out, "SELECT COUNT(*) FROM stream_poll_targets WHERE poll_status = 'blocked'"),
        "stream_entries_v2": one(out, "SELECT COUNT(*) FROM stream_entries_v2"),
        "stream_entries_canonical": one(out, "SELECT COUNT(*) FROM stream_entries_canonical"),
        "stream_entry_duplicate_sources": one(out, "SELECT COUNT(*) FROM stream_entries_canonical WHERE source_count > 1"),
        "archival_stream_sources": len(archival_stream_coverage),
        "archival_stream_sources_with_entries": sum(1 for row in archival_stream_coverage if int(row["source_entry_count"]) > 0),
        "archival_stream_sources_without_entries": sum(1 for row in archival_stream_coverage if int(row["source_entry_count"]) == 0),
        "structured_data_files": one(out, "SELECT COUNT(*) FROM structured_data_files"),
        "media_references": one(out, "SELECT COUNT(*) FROM media_references"),
        "stream_media_references": one(out, "SELECT COUNT(*) FROM stream_media_references"),
        "stream_media_blockers": one(out, "SELECT COUNT(*) FROM stream_media_references WHERE blocker IS NOT NULL"),
        "gallery_manifests": one(out, "SELECT COUNT(*) FROM gallery_manifests"),
        "advertiser_records": one(out, "SELECT COUNT(*) FROM advertiser_records"),
        "classified_records": one(out, "SELECT COUNT(*) FROM classified_records"),
        "ridecamp_messages": one(out, "SELECT COUNT(*) FROM ridecamp_messages"),
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
    (config.output_dir / "archival-stream-coverage.json").write_text(
        json.dumps(archival_stream_coverage, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def parse_args(argv: list[str]) -> ImportConfig:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory-db", default="migration/inventory/source-inventory.sqlite")
    parser.add_argument("--source-root", default="/Volumes/webstore/endurance.net")
    parser.add_argument("--output-dir", default="migration/imports")
    parser.add_argument("--max-records", type=int, help="Limit legacy_source_file imports for smoke tests.")
    parser.add_argument("--poll-active", action="store_true", help="Fetch ready active stream poll targets after local import.")
    parser.add_argument("--feeds-only", action="store_true", help="Only import XML/RSS/Atom/OPML/XSLT stream files.")
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
        poll_active=args.poll_active,
        feeds_only=args.feeds_only,
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
        source_count = 0 if config.feeds_only else import_source_files(inv, out, batch_id, config.max_records)
        media_count = 0 if config.feeds_only else import_media_assets(inv, out, batch_id, config.max_records)
        template_count = 0 if config.feeds_only else import_templates(inv, out, config, batch_id)
        feed_count = import_feeds(inv, out, config, batch_id)
        poll_count = poll_active_streams(out, batch_id) if config.poll_active else 0
        gallery_count = 0 if config.feeds_only else import_gallery_manifests(inv, out, config, batch_id)
        advertiser_count = 0 if config.feeds_only else import_advertisers(inv, out, config, batch_id)
        classified_count = 0 if config.feeds_only else import_classifieds(inv, out, config, batch_id)
        ridecamp_count = 0 if config.feeds_only else import_ridecamp_messages(inv, out, config, batch_id)
        failures = int(one(out, "SELECT COUNT(*) FROM import_failures WHERE batch_id = ?", (batch_id,)) or 0)
        records_imported = (
            source_count + media_count + template_count + feed_count
            + poll_count + gallery_count + advertiser_count + classified_count + ridecamp_count
        )
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

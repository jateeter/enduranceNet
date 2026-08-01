#!/usr/bin/env python3
"""Generate a Play evolution that seeds the refreshed RSS stream corpus."""

from __future__ import annotations

import argparse
import hashlib
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STAGING_DB = REPO_ROOT / "migration/imports/legacy-import.sqlite"
DEFAULT_OUTPUT = REPO_ROOT / "backend/conf/evolutions/default/11.sql"
ACTIVE_SOURCE_HINTS = {
    "channels/considerThis.xml",
    "channels/news.xml",
    "channels/snapshots.xml",
    "channels/stories.xml",
    "channels/tracks.xml",
    "channels/trailsMatter.xml",
}
MAX_VARCHAR = {
    "slug": 128,
    "title": 512,
    "provider_entry_id": 512,
    "author": 255,
    "url": 1024,
    "checksum": 64,
}


@dataclass(frozen=True)
class SourceSeed:
    id: int
    source_path: str
    slug: str
    title: str
    provider: str
    feed_format: str
    remote_url: str | None
    local_cache_path: str | None
    legacy_url: str | None
    default_presentation: str
    active: bool
    blogger_blog_id: str | None
    canonical_atom_url: str | None
    canonical_rss_url: str | None
    latest_cached_entry: str | None
    stream_group: str | None
    notes: str | None


def rows(conn: sqlite3.Connection, sql: str, params: tuple[object, ...] = ()) -> list[sqlite3.Row]:
    return list(conn.execute(sql, params))


def one(conn: sqlite3.Connection, sql: str, params: tuple[object, ...] = ()) -> object:
    row = conn.execute(sql, params).fetchone()
    return row[0] if row else None


def truncate(value: str | None, length: int) -> str | None:
    if value is None:
        return None
    return value[:length]


def sql_string(value: object) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int):
        return str(value)
    normalized = str(value).replace(";", ",")
    return "'" + normalized.replace("'", "''") + "'"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:MAX_VARCHAR["slug"]].strip("-") or hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def unique_slug(base: str, used: set[str], source_path: str) -> str:
    slug = slugify(base)
    if slug not in used:
        used.add(slug)
        return slug
    suffix = hashlib.sha256(source_path.encode("utf-8")).hexdigest()[:8]
    trimmed = slug[: MAX_VARCHAR["slug"] - len(suffix) - 1].strip("-")
    candidate = f"{trimmed}-{suffix}"
    used.add(candidate)
    return candidate


def blogger_id(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"/feeds/(\d+)/posts/default", value)
    return match.group(1) if match else None


def canonical_atom_url(value: str | None) -> str | None:
    blog_id = blogger_id(value)
    return f"https://www.blogger.com/feeds/{blog_id}/posts/default" if blog_id else None


def canonical_rss_url(value: str | None, provider: str) -> str | None:
    if provider != "blogger" or not value:
        return value
    atom = canonical_atom_url(value)
    return f"{atom}?alt=rss" if atom else value


def stream_group(title: str, source_path: str, active: bool) -> str:
    lower = f"{title} {source_path}".lower()
    if active:
        return "Active News"
    if any(token in lower for token in ("ridecamp", "riders", "publish2ridecamp")):
        return "Community"
    if any(token in lower for token in ("wec", "team", "biltmore", "championship", "kathy", "becky", "dutch")):
        return "Event & Team Archives"
    if any(token in lower for token in ("feature", "headline", "bulletin", "news")):
        return "News Archives"
    if any(token in lower for token in ("merri", "photo", "snapshot", "travel", "whereintheworld")):
        return "Photo & Travel Journals"
    if any(token in lower for token in ("saddle", "training", "feed", "breeder", "video")):
        return "Resources"
    return "Archive"


def presentation_mode(row: sqlite3.Row) -> str:
    current = str(row["default_presentation"] or "")
    source_path = str(row["source_path"] or "").lower()
    feed_format = str(row["feed_format"] or "").lower()
    provider = str(row["provider"] or "").lower()
    if current in {
        "popup-channel-card",
        "single-entry-html",
        "event-story-list",
        "google-reader-frontpage",
        "stream-directory",
    }:
        return current
    if "googlereader" in source_path or "google_reader" in source_path:
        return "google-reader-frontpage"
    if feed_format == "opml":
        return "stream-directory"
    if "entry" in feed_format:
        return "single-entry-html"
    if "wec" in source_path or "event" in source_path:
        return "event-story-list"
    if provider in {"blogger", "rss"} or feed_format.startswith("rss"):
        return "rss-list"
    return "atom-list"


def load_sources(conn: sqlite3.Connection) -> list[SourceSeed]:
    used_slugs: set[str] = set()
    seeds: list[SourceSeed] = []
    source_rows = rows(
        conn,
        """
        SELECT source.source_path, source.title, source.provider, source.feed_format,
               source.remote_url, source.local_cache_path, source.legacy_url,
               source.default_presentation, source.active, source.checksum_sha256,
               snapshot.self_url, snapshot.alternate_url, snapshot.next_url,
               target.poll_url, target.poll_status, target.blocker,
               MAX(COALESCE(NULLIF(entry.published_at, ''), NULLIF(entry.updated_at, ''))) AS latest_entry
        FROM stream_sources source
        LEFT JOIN stream_snapshots snapshot ON snapshot.source_path = source.source_path
        LEFT JOIN stream_poll_targets target ON target.source_path = source.source_path
        LEFT JOIN stream_entries_v2 entry ON entry.source_path = source.source_path
        WHERE source.provider IN ('blogger', 'rss', 'atom', 'opml')
        GROUP BY source.source_path
        ORDER BY source.active DESC, source.title COLLATE NOCASE ASC, source.source_path ASC
        """,
    )
    for index, row in enumerate(source_rows, start=1):
        title = str(row["title"] or row["source_path"])
        source_path = str(row["source_path"])
        provider = str(row["provider"])
        active = source_path in ACTIVE_SOURCE_HINTS and str(row["poll_status"] or "ready") == "ready"
        remote_url = str(row["poll_url"] or row["remote_url"] or "") or None
        atom_url = canonical_atom_url(remote_url or row["self_url"])
        rss_url = canonical_rss_url(remote_url or row["self_url"], provider)
        notes = (
            f"Seeded from refreshed RSS corpus. Source path: /{source_path}. "
            f"Poll status: {row['poll_status'] or 'untracked'}. "
            f"XSLT presentation: {presentation_mode(row)}."
        )
        if row["blocker"]:
            notes = f"{notes} Blocker: {row['blocker']}."
        seeds.append(
            SourceSeed(
                id=index,
                source_path=source_path,
                slug=unique_slug(title, used_slugs, source_path),
                title=truncate(title, 255) or source_path,
                provider=provider,
                feed_format=str(row["feed_format"] or "rss"),
                remote_url=truncate(remote_url, MAX_VARCHAR["url"]),
                local_cache_path=truncate(f"/{source_path}", MAX_VARCHAR["url"]),
                legacy_url=truncate(str(row["legacy_url"] or row["alternate_url"] or "") or None, MAX_VARCHAR["url"]),
                default_presentation=presentation_mode(row),
                active=active,
                blogger_blog_id=blogger_id(remote_url or row["self_url"]),
                canonical_atom_url=truncate(atom_url, MAX_VARCHAR["url"]),
                canonical_rss_url=truncate(rss_url, MAX_VARCHAR["url"]),
                latest_cached_entry=truncate(str(row["latest_entry"] or "") or None, 64),
                stream_group=stream_group(title, source_path, active),
                notes=notes,
            )
        )
    return seeds


def source_values(seed: SourceSeed) -> list[object]:
    return [
        seed.id,
        seed.slug,
        seed.title,
        seed.provider,
        seed.feed_format,
        seed.remote_url,
        seed.local_cache_path,
        seed.legacy_url,
        seed.default_presentation,
        seed.active,
        seed.notes,
        seed.blogger_blog_id,
        seed.canonical_atom_url,
        seed.canonical_rss_url,
        seed.latest_cached_entry,
        seed.stream_group,
    ]


def entry_rows(conn: sqlite3.Connection, source_ids: dict[str, int]) -> list[list[object]]:
    output: list[list[object]] = []
    if not source_ids:
        return output
    query_rows = rows(
        conn,
        """
        SELECT source_path, provider_entry_id, title, summary_html, content_html,
               author, published_at, updated_at, alternate_url, self_url,
               related_url, comments_url
        FROM stream_entries_v2
        WHERE source_path IN ({placeholders})
        ORDER BY source_path ASC, entry_index ASC, provider_entry_id ASC
        """.replace("{placeholders}", ",".join("?" for _ in source_ids)),
        tuple(source_ids.keys()),
    )
    for index, row in enumerate(query_rows, start=1):
        source_path = str(row["source_path"])
        source_id = source_ids[source_path]
        checksum_seed = "|".join(str(row[key] or "") for key in ("source_path", "provider_entry_id", "title", "updated_at"))
        checksum = hashlib.sha256(checksum_seed.encode("utf-8")).hexdigest()
        output.append(
            [
                index,
                source_id,
                truncate(str(row["provider_entry_id"] or f"{source_path}#{index}"), MAX_VARCHAR["provider_entry_id"]),
                truncate(str(row["title"] or "Untitled stream entry"), MAX_VARCHAR["title"]),
                row["summary_html"],
                row["content_html"],
                truncate(str(row["author"] or "") or None, MAX_VARCHAR["author"]),
                truncate(str(row["published_at"] or "") or None, 64),
                truncate(str(row["updated_at"] or "") or None, 64),
                truncate(str(row["alternate_url"] or "") or None, MAX_VARCHAR["url"]),
                truncate(str(row["self_url"] or "") or None, MAX_VARCHAR["url"]),
                truncate(str(row["related_url"] or "") or None, MAX_VARCHAR["url"]),
                truncate(str(row["comments_url"] or "") or None, MAX_VARCHAR["url"]),
                checksum,
            ]
        )
    return output


def values_sql(values: list[object]) -> str:
    return "(" + ", ".join(sql_string(value) for value in values) + ")"


def write_insert(handle, table: str, columns: list[str], values: list[list[object]], chunk_size: int = 80) -> None:
    if not values:
        return
    for start in range(0, len(values), chunk_size):
        chunk = values[start : start + chunk_size]
        handle.write(f"INSERT INTO {table} ({', '.join(columns)}) VALUES\n")
        handle.write(",\n".join(f"  {values_sql(row)}" for row in chunk))
        handle.write(";\n\n")


def generate(staging_db: Path, output: Path) -> tuple[int, int]:
    conn = sqlite3.connect(staging_db)
    conn.row_factory = sqlite3.Row
    try:
        sources = load_sources(conn)
        source_ids = {source.source_path: source.id for source in sources}
        entries = entry_rows(conn, source_ids)
    finally:
        conn.close()

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        handle.write("# --- !Ups\n\n")
        handle.write("-- Generated by scripts/generate_stream_evolution.py from migration/imports/legacy-import.sqlite.\n")
        handle.write("-- Refresh source before regenerating with scripts/legacy_import.py --feeds-only and scripts/poll_active_streams.py --allow-target-failures.\n\n")
        handle.write("DELETE FROM stream_entries;\n")
        handle.write("DELETE FROM stream_sources;\n\n")
        write_insert(
            handle,
            "stream_sources",
            [
                "id",
                "slug",
                "title",
                "provider",
                "feed_format",
                "remote_url",
                "local_cache_path",
                "legacy_url",
                "default_presentation",
                "active",
                "notes",
                "blogger_blog_id",
                "canonical_atom_url",
                "canonical_rss_url",
                "latest_cached_entry",
                "stream_group",
            ],
            [source_values(source) for source in sources],
        )
        write_insert(
            handle,
            "stream_entries",
            [
                "id",
                "source_id",
                "provider_entry_id",
                "title",
                "summary_html",
                "content_html",
                "author",
                "published_at",
                "updated_at",
                "alternate_url",
                "self_url",
                "related_url",
                "comments_url",
                "checksum_sha256",
            ],
            entries,
            chunk_size=40,
        )
        handle.write("# --- !Downs\n\n")
        handle.write("DELETE FROM stream_entries;\n")
        handle.write("DELETE FROM stream_sources;\n")
    return len(sources), len(entries)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staging-db", default=str(DEFAULT_STAGING_DB))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    staging_db = Path(args.staging_db).resolve()
    output = Path(args.output).resolve()
    if not staging_db.exists():
        print(f"staging database not found: {staging_db}", file=sys.stderr)
        return 2
    source_count, entry_count = generate(staging_db, output)
    print(f"Wrote {output}")
    print(f"Seeded {source_count} stream sources and {entry_count} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

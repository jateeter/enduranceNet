#!/usr/bin/env python3
"""Generate item-level manifests for legacy Photoshop image galleries."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import quote, unquote, urlparse


PARSER_VERSION = "photoshop-gallery-manifest-v1"
PUBLIC_MEDIA_PREFIX = "/legacy-media/"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".jpe", ".png", ".gif", ".webp"}
NAV_IMAGE_NAMES = {"home.gif", "next.gif", "previous.gif", "prev.gif", "contents.gif"}


@dataclass(frozen=True)
class GalleryConfig:
    inventory_db: Path
    source_root: Path
    output_dir: Path
    max_galleries: int | None


def rows(conn: sqlite3.Connection, sql: str, params: Iterable[object] = ()) -> list[dict[str, object]]:
    conn.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in conn.execute(sql, tuple(params)).fetchall()]
    finally:
        conn.row_factory = None


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, values: Iterable[dict[str, object]]) -> int:
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for value in values:
            handle.write(json.dumps(value, sort_keys=True) + "\n")
            count += 1
    return count


def sql_literal(value: object) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def legacy_url(source_path: str) -> str:
    return "/" + source_path.lstrip("/")


def public_url(source_path: str) -> str:
    return PUBLIC_MEDIA_PREFIX + quote(source_path.lstrip("/"), safe="/")


def stable_id(prefix: str, value: str) -> str:
    return f"{prefix}-" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def clean_text(value: str) -> str:
    return " ".join(value.replace("\xa0", " ").split())


def normalize_reference(source_path: str, reference: str) -> str:
    parsed = urlparse(reference)
    if parsed.scheme in {"http", "https"}:
        return parsed.path.lstrip("/")
    candidate = unquote(reference.split("?", 1)[0].split("#", 1)[0])
    if candidate.startswith("/"):
        return os.path.normpath(candidate.lstrip("/")).replace(os.sep, "/")
    return os.path.normpath(str(Path(source_path).parent / candidate)).replace(os.sep, "/")


def image_like(path: str) -> bool:
    return Path(path.split("?", 1)[0].split("#", 1)[0]).suffix.lower() in IMAGE_EXTENSIONS


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


class GalleryHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.heading_parts: list[str] = []
        self.links: list[dict[str, object]] = []
        self.images: list[dict[str, object]] = []
        self._active_anchor: dict[str, object] | None = None
        self._text_target: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key.lower(): value or "" for key, value in attrs}
        lower_tag = tag.lower()
        if lower_tag == "title":
            self._text_target = "title"
        elif lower_tag in {"h1", "h2", "h3"}:
            self._text_target = "heading"
        elif lower_tag == "a":
            self._active_anchor = {"href": attr.get("href", ""), "target": attr.get("target", ""), "text": ""}
        elif lower_tag == "img":
            image = {
                "src": attr.get("src", ""),
                "alt": attr.get("alt", ""),
                "width": int(attr["width"]) if attr.get("width", "").isdigit() else None,
                "height": int(attr["height"]) if attr.get("height", "").isdigit() else None,
                "anchor_href": self._active_anchor.get("href", "") if self._active_anchor else "",
                "anchor_target": self._active_anchor.get("target", "") if self._active_anchor else "",
            }
            self.images.append(image)

    def handle_data(self, data: str) -> None:
        text = clean_text(data)
        if not text:
            return
        if self._text_target == "title":
            self.title_parts.append(text)
        elif self._text_target == "heading":
            self.heading_parts.append(text)
        if self._active_anchor is not None:
            existing = str(self._active_anchor.get("text") or "")
            self._active_anchor["text"] = clean_text(f"{existing} {text}")

    def handle_endtag(self, tag: str) -> None:
        lower_tag = tag.lower()
        if lower_tag in {"title", "h1", "h2", "h3"}:
            self._text_target = None
        elif lower_tag == "a" and self._active_anchor is not None:
            self.links.append(self._active_anchor)
            self._active_anchor = None


def parse_html(path: Path) -> GalleryHtmlParser:
    parser = GalleryHtmlParser()
    parser.feed(read_text(path))
    return parser


def discover_gallery_roots(inventory_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_path = {str(row["path"]): row for row in inventory_rows}
    roots: dict[str, dict[str, object]] = {}
    paths = set(by_path)
    thumbnail_roots = {str(Path(path).parent.parent / "thumbnails").replace(os.sep, "/") for path in paths}
    page_roots = {str(Path(path).parent.parent / "pages").replace(os.sep, "/") for path in paths}

    for row in inventory_rows:
        path = str(row["path"])
        lower = path.lower()
        if lower.endswith("/thumbnailframe.html"):
            root = path.rsplit("/", 1)[0]
            roots[root] = {"root": root, "entry_path": path, "pattern": "framed-thumbnail"}

    for path in sorted(paths):
        lower = path.lower()
        if not lower.endswith("/index.html"):
            continue
        root = path.rsplit("/", 1)[0]
        if f"{root}/thumbnails" in thumbnail_roots and f"{root}/pages" in page_roots:
            roots.setdefault(root, {"root": root, "entry_path": path, "pattern": "paginated-index"})

    return [roots[key] for key in sorted(roots)]


def path_exists_under(conn: sqlite3.Connection, prefix: str) -> bool:
    return (
        rows(
            conn,
            "SELECT 1 FROM files WHERE kind = 'file' AND path LIKE ? LIMIT 1",
            (f"{prefix}/%",),
        )
        != []
    )


def discover_gallery_roots_from_db(conn: sqlite3.Connection, max_galleries: int | None) -> list[dict[str, object]]:
    roots: dict[str, dict[str, object]] = {}
    thumbnail_rows = rows(
        conn,
        """
        SELECT path
        FROM files
        WHERE kind = 'file'
          AND lower(path) LIKE '%/thumbnailframe.html'
        ORDER BY path
        """,
    )
    for row in thumbnail_rows:
        path = str(row["path"])
        root = path.rsplit("/", 1)[0]
        roots[root] = {"root": root, "entry_path": path, "pattern": "framed-thumbnail"}
        if max_galleries is not None and len(roots) >= max_galleries:
            return [roots[key] for key in sorted(roots)]

    index_rows = rows(
        conn,
        """
        SELECT path
        FROM files
        WHERE kind = 'file'
          AND lower(path) LIKE '%/index.html'
        ORDER BY path
        """,
    )
    for row in index_rows:
        path = str(row["path"])
        root = path.rsplit("/", 1)[0]
        if root in roots:
            continue
        if path_exists_under(conn, f"{root}/thumbnails") and path_exists_under(conn, f"{root}/pages"):
            roots[root] = {"root": root, "entry_path": path, "pattern": "paginated-index"}
            if max_galleries is not None and len(roots) >= max_galleries:
                return [roots[key] for key in sorted(roots)]
    return [roots[key] for key in sorted(roots)]


def inventory_rows_for_roots(conn: sqlite3.Connection, roots: list[dict[str, object]]) -> list[dict[str, object]]:
    root_paths = [str(root["root"]) for root in roots]
    loaded: dict[str, dict[str, object]] = {}
    for root in root_paths:
        for row in rows(
            conn,
            """
            SELECT path, kind, classification, extension, mime_type, size,
                   checksum_sha256, status, mode_octal, scanned_at
            FROM files
            WHERE kind = 'file'
              AND path LIKE ?
            ORDER BY path
            """,
            (f"{root}/%",),
        ):
            loaded[str(row["path"])] = row
    return [loaded[key] for key in sorted(loaded)]


def derive_full_image_path(item_page_path: str, thumbnail_path: str) -> str:
    return str(Path(thumbnail_path).parent.parent / "images" / Path(thumbnail_path).name).replace(os.sep, "/")


def full_image_from_page(
    source_root: Path,
    item_page_path: str,
    fallback_path: str,
    inventory_by_path: dict[str, dict[str, object]],
) -> str:
    if fallback_path in inventory_by_path:
        return fallback_path
    page_file = source_root / item_page_path
    if not page_file.exists():
        return fallback_path
    try:
        parser = parse_html(page_file)
    except OSError:
        return fallback_path
    for image in parser.images:
        src = str(image.get("src") or "")
        if not src:
            continue
        candidate = normalize_reference(item_page_path, src)
        if not image_like(candidate):
            continue
        if Path(candidate).name.lower() in NAV_IMAGE_NAMES:
            continue
        if "/images/" in f"/{candidate}" or candidate != fallback_path:
            return candidate
    return fallback_path


def gallery_items_from_entry(
    source_root: Path,
    entry_path: str,
    inventory_by_path: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    parser = parse_html(source_root / entry_path)
    items: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for image in parser.images:
        thumbnail_src = str(image.get("src") or "")
        item_href = str(image.get("anchor_href") or "")
        if not thumbnail_src or not item_href:
            continue
        thumbnail_path = normalize_reference(entry_path, thumbnail_src)
        item_page_path = normalize_reference(entry_path, item_href)
        if not image_like(thumbnail_path):
            continue
        if "/thumbnails/" not in f"/{thumbnail_path}" and not item_page_path.endswith(".html"):
            continue
        key = (thumbnail_path, item_page_path)
        if key in seen:
            continue
        seen.add(key)
        full_image_path = full_image_from_page(
            source_root,
            item_page_path,
            derive_full_image_path(item_page_path, thumbnail_path),
            inventory_by_path,
        )
        row = inventory_by_path.get(full_image_path) or {}
        items.append(
            {
                "thumbnail_source_path": thumbnail_path,
                "thumbnail_public_url": public_url(thumbnail_path),
                "item_page_source_path": item_page_path,
                "item_page_legacy_url": legacy_url(item_page_path),
                "full_image_source_path": full_image_path,
                "full_image_public_url": public_url(full_image_path),
                "caption": clean_text(str(image.get("alt") or "")),
                "thumbnail_width": image.get("width"),
                "thumbnail_height": image.get("height"),
                "checksum_sha256": row.get("checksum_sha256") or "",
            }
        )
    return items


def write_cms_sql(path: Path, gallery_rows: list[dict[str, object]], item_rows: list[dict[str, object]]) -> None:
    lines = [
        "-- Generated by scripts/photoshop_gallery_manifest.py.",
        "-- Import after reviewing photoshop-gallery-blockers.jsonl.",
    ]
    if gallery_rows:
        gallery_columns = [
            "id",
            "slug",
            "title",
            "source_root",
            "entry_source_path",
            "legacy_url",
            "pattern",
            "item_count",
            "parser_version",
        ]
        lines.append(f"INSERT INTO cms_galleries ({', '.join(gallery_columns)}) VALUES")
        values = []
        for row in gallery_rows:
            values.append(
                "  ("
                + ", ".join(
                    sql_literal(row[key])
                    for key in [
                        "gallery_id",
                        "slug",
                        "title",
                        "source_root",
                        "entry_source_path",
                        "legacy_url",
                        "pattern",
                        "item_count",
                        "parser_version",
                    ]
                )
                + ")"
            )
        lines.append(",\n".join(values))
        lines.append("ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title, item_count = EXCLUDED.item_count;")
    if item_rows:
        item_columns = [
            "id",
            "gallery_id",
            "position",
            "caption",
            "thumbnail_source_path",
            "thumbnail_public_url",
            "item_page_source_path",
            "full_image_source_path",
            "full_image_public_url",
            "checksum_sha256",
            "parser_version",
        ]
        lines.append("")
        lines.append(f"INSERT INTO cms_gallery_items ({', '.join(item_columns)}) VALUES")
        values = []
        for row in item_rows:
            values.append(
                "  ("
                + ", ".join(
                    sql_literal(row[key])
                    for key in [
                        "item_id",
                        "gallery_id",
                        "position",
                        "caption",
                        "thumbnail_source_path",
                        "thumbnail_public_url",
                        "item_page_source_path",
                        "full_image_source_path",
                        "full_image_public_url",
                        "checksum_sha256",
                        "parser_version",
                    ]
                )
                + ")"
            )
        lines.append(",\n".join(values))
        lines.append("ON CONFLICT (id) DO UPDATE SET caption = EXCLUDED.caption, position = EXCLUDED.position;")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate(config: GalleryConfig) -> dict[str, object]:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    inv = sqlite3.connect(config.inventory_db)
    try:
        gallery_roots = discover_gallery_roots_from_db(inv, config.max_galleries)
        inventory_rows = inventory_rows_for_roots(inv, gallery_roots)
    finally:
        inv.close()

    inventory_by_path = {str(row["path"]): row for row in inventory_rows}

    gallery_rows: list[dict[str, object]] = []
    item_rows: list[dict[str, object]] = []
    blocker_rows: list[dict[str, object]] = []
    for root in gallery_roots:
        entry_path = str(root["entry_path"])
        source_root = str(root["root"])
        try:
            parser = parse_html(config.source_root / entry_path)
            title = clean_text(" ".join(parser.heading_parts) or " ".join(parser.title_parts)) or source_root
            items = gallery_items_from_entry(config.source_root, entry_path, inventory_by_path)
        except Exception as exc:
            blocker_rows.append(
                {
                    "blocker_type": "gallery_parse_failure",
                    "source_root": source_root,
                    "source_path": entry_path,
                    "reason": str(exc),
                    "status": "open",
                }
            )
            continue

        gallery_id = stable_id("gallery", source_root)
        gallery_row = {
            "gallery_id": gallery_id,
            "slug": slugify(source_root),
            "title": title,
            "source_root": source_root,
            "entry_source_path": entry_path,
            "legacy_url": legacy_url(entry_path),
            "pattern": root["pattern"],
            "item_count": len(items),
            "parser_version": PARSER_VERSION,
        }
        gallery_rows.append(gallery_row)

        for position, item in enumerate(items, start=1):
            item_id = stable_id("gallery-item", f"{gallery_id}:{position}:{item['full_image_source_path']}")
            item_row = {
                **item,
                "item_id": item_id,
                "gallery_id": gallery_id,
                "gallery_slug": gallery_row["slug"],
                "position": position,
                "parser_version": PARSER_VERSION,
            }
            item_rows.append(item_row)
            for field, blocker_type in [
                ("thumbnail_source_path", "missing_thumbnail"),
                ("item_page_source_path", "missing_item_page"),
                ("full_image_source_path", "missing_full_image"),
            ]:
                source_path = str(item[field])
                inventory_row = inventory_by_path.get(source_path)
                if not inventory_row:
                    reason = "not_in_inventory"
                elif inventory_row.get("status") != "ok":
                    reason = str(inventory_row.get("status") or "not_ok")
                else:
                    continue
                blocker_rows.append(
                    {
                        "blocker_type": blocker_type,
                        "gallery_id": gallery_id,
                        "gallery_slug": gallery_row["slug"],
                        "source_root": source_root,
                        "source_path": source_path,
                        "item_id": item_id,
                        "position": position,
                        "reason": reason,
                        "status": "open",
                    }
                )

    gallery_count = write_jsonl(config.output_dir / "photoshop-galleries.jsonl", gallery_rows)
    item_count = write_jsonl(config.output_dir / "photoshop-gallery-items.jsonl", item_rows)
    blocker_count = write_jsonl(config.output_dir / "photoshop-gallery-blockers.jsonl", blocker_rows)
    write_cms_sql(config.output_dir / "cms-gallery-import.sql", gallery_rows, item_rows)
    summary = {
        "inventory_db": str(config.inventory_db),
        "source_root": str(config.source_root),
        "output_dir": str(config.output_dir),
        "parser_version": PARSER_VERSION,
        "gallery_count": gallery_count,
        "item_count": item_count,
        "blocker_count": blocker_count,
        "max_galleries": config.max_galleries,
        "bounded_manifest": config.max_galleries is not None,
        "patterns": {},
    }
    for row in gallery_rows:
        pattern = str(row["pattern"])
        summary["patterns"][pattern] = int(summary["patterns"].get(pattern, 0)) + 1
    write_json(config.output_dir / "photoshop-gallery-summary.json", summary)
    return summary


def parse_args(argv: list[str] | None = None) -> GalleryConfig:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory-db", default="migration/inventory/source-inventory.sqlite")
    parser.add_argument("--source-root", default="/Volumes/webstore/endurance.net")
    parser.add_argument("--output-dir", default="migration/galleries")
    parser.add_argument("--max-galleries", type=int, help="Limit gallery roots for bounded smoke runs.")
    args = parser.parse_args(argv)
    if args.max_galleries is not None and args.max_galleries < 1:
        parser.error("--max-galleries must be greater than zero")
    return GalleryConfig(
        inventory_db=Path(args.inventory_db).resolve(),
        source_root=Path(args.source_root).resolve(),
        output_dir=Path(args.output_dir).resolve(),
        max_galleries=args.max_galleries,
    )


def main(argv: list[str] | None = None) -> int:
    config = parse_args(argv)
    if not config.inventory_db.exists():
        raise SystemExit(f"inventory database not found: {config.inventory_db}")
    summary = generate(config)
    print(f"Wrote Photoshop gallery manifest reports to {config.output_dir} ({summary['gallery_count']} galleries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

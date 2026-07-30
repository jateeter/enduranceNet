#!/usr/bin/env python3
"""Generate durable media manifests from inventory and imported references."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import quote, unquote, urlparse


PUBLIC_MEDIA_PREFIX = "/legacy-media/"
MEDIA_CLASSIFICATIONS = {"media_asset", "document"}


@dataclass(frozen=True)
class MediaManifestConfig:
    inventory_db: Path
    import_db: Path | None
    source_root: Path
    output_dir: Path
    waivers: Path | None
    probe_dimensions: bool


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


def public_url(source_path: str) -> str:
    return PUBLIC_MEDIA_PREFIX + quote(source_path.lstrip("/"), safe="/")


def legacy_url(source_path: str) -> str:
    return "/" + source_path.lstrip("/")


def asset_kind(extension: str, mime_type: str) -> str:
    lower_ext = extension.lower()
    lower_mime = mime_type.lower()
    if lower_mime.startswith("image/") or lower_ext in {".jpg", ".jpeg", ".jpe", ".png", ".gif", ".webp", ".svg", ".ico"}:
        return "image"
    if lower_mime.startswith("audio/") or lower_ext in {".mp3", ".wav"}:
        return "audio"
    if lower_mime.startswith("video/") or lower_ext in {".mov", ".mp4", ".m4v", ".avi"}:
        return "video"
    if lower_ext in {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt"}:
        return "document"
    return "other"


def image_dimensions(path: Path) -> tuple[int | None, int | None]:
    if not path.exists() or not path.is_file():
        return None, None
    try:
        data = path.read_bytes()[:32]
        if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
            return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
        if data.startswith((b"GIF87a", b"GIF89a")) and len(data) >= 10:
            return int.from_bytes(data[6:8], "little"), int.from_bytes(data[8:10], "little")
    except OSError:
        return None, None
    return None, None


def load_waivers(path: Path | None) -> dict[str, str]:
    if path is None or not path.exists():
        return {}
    waivers: dict[str, str] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            key = str(row.get("referenced_path") or row.get("referenced_url") or "")
            if key:
                waivers[key] = str(row.get("reason") or "waived")
    return waivers


def normalized_reference(source_path: str, referenced_url: str, referenced_path: str | None) -> tuple[str | None, bool]:
    parsed = urlparse(referenced_url)
    if parsed.scheme in {"http", "https", "mailto", "javascript"}:
        return None, True
    candidate = referenced_path or referenced_url
    candidate = unquote(candidate.split("?", 1)[0].split("#", 1)[0])
    if not candidate:
        return None, False
    if candidate.startswith("/"):
        return os.path.normpath(candidate.lstrip("/")).replace(os.sep, "/"), False
    if referenced_path and referenced_path != referenced_url:
        return os.path.normpath(referenced_path.lstrip("/")).replace(os.sep, "/"), False
    return os.path.normpath(str(Path(source_path).parent / candidate)).replace(os.sep, "/"), False


def generate(config: MediaManifestConfig) -> None:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    waivers = load_waivers(config.waivers)

    inv = sqlite3.connect(config.inventory_db)
    try:
        file_rows = rows(
            inv,
            """
            SELECT path, classification, extension, mime_type, size, checksum_sha256, status, mode_octal, scanned_at
            FROM files
            WHERE kind = 'file'
              AND classification IN ('media_asset', 'document')
            ORDER BY path
            """,
        )
    finally:
        inv.close()

    inventory_by_path = {str(row["path"]): row for row in file_rows}
    readable_asset_rows = [row for row in file_rows if row["status"] == "ok"]
    unreadable_asset_rows = [row for row in file_rows if row["status"] != "ok"]

    manifest_rows: list[dict[str, object]] = []
    for row in readable_asset_rows:
        source_path = str(row["path"])
        width, height = image_dimensions(config.source_root / source_path) if config.probe_dimensions else (None, None)
        manifest_rows.append(
            {
                "source_path": source_path,
                "legacy_url": legacy_url(source_path),
                "public_url": public_url(source_path),
                "asset_kind": asset_kind(str(row["extension"] or ""), str(row["mime_type"] or "")),
                "mime_type": row["mime_type"] or "",
                "extension": row["extension"] or "",
                "size": row["size"],
                "checksum_sha256": row["checksum_sha256"] or "",
                "width": width,
                "height": height,
                "scanned_at": row["scanned_at"],
            }
        )

    manifest_paths = {str(row["source_path"]) for row in manifest_rows}
    missing_refs: list[dict[str, object]] = []
    external_refs: list[dict[str, object]] = []
    resolved_refs = 0
    waived_refs = 0

    if config.import_db and config.import_db.exists():
        imported = sqlite3.connect(config.import_db)
        try:
            references = rows(
                imported,
                """
                SELECT source_path, referenced_url, referenced_path, attribute
                FROM media_references
                ORDER BY source_path, referenced_url
                """,
            )
        finally:
            imported.close()
        for reference in references:
            source_path = str(reference["source_path"])
            referenced_url = str(reference["referenced_url"])
            normalized, external = normalized_reference(source_path, referenced_url, reference.get("referenced_path"))
            if external:
                external_refs.append(reference)
                continue
            if normalized in manifest_paths:
                resolved_refs += 1
                continue
            waiver_reason = waivers.get(normalized or "") or waivers.get(referenced_url)
            inventory_row = inventory_by_path.get(normalized or "")
            reason = "not_in_manifest"
            if inventory_row and inventory_row["status"] != "ok":
                reason = "unreadable"
            if waiver_reason:
                waived_refs += 1
                reason = f"waived: {waiver_reason}"
            missing_refs.append(
                {
                    "source_path": source_path,
                    "referenced_url": referenced_url,
                    "resolved_path": normalized or "",
                    "attribute": reference["attribute"],
                    "reason": reason,
                }
            )

    unreadable_rows = [
        {
            "source_path": row["path"],
            "legacy_url": legacy_url(str(row["path"])),
            "classification": row["classification"],
            "status": row["status"],
            "mode_octal": row["mode_octal"] or "",
        }
        for row in unreadable_asset_rows
    ]

    manifest_count = write_jsonl(config.output_dir / "media-manifest.jsonl", manifest_rows)
    missing_count = write_jsonl(config.output_dir / "missing-media-references.jsonl", missing_refs)
    external_count = write_jsonl(config.output_dir / "external-media-references.jsonl", external_refs)
    unreadable_count = write_jsonl(config.output_dir / "unreadable-media.jsonl", unreadable_rows)

    summary = {
        "inventory_db": str(config.inventory_db),
        "import_db": str(config.import_db) if config.import_db else "",
        "source_root": str(config.source_root),
        "public_media_prefix": PUBLIC_MEDIA_PREFIX,
        "dimension_probe_enabled": config.probe_dimensions,
        "manifest_entries": manifest_count,
        "unreadable_media": unreadable_count,
        "resolved_media_references": resolved_refs,
        "missing_media_references": missing_count,
        "external_media_references": external_count,
        "waived_media_references": waived_refs,
        "asset_kind_counts": {},
    }
    for row in manifest_rows:
        kind = str(row["asset_kind"])
        summary["asset_kind_counts"][kind] = int(summary["asset_kind_counts"].get(kind, 0)) + 1
    write_json(config.output_dir / "media-summary.json", summary)


def parse_args() -> MediaManifestConfig:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory-db", default="migration/inventory/source-inventory.sqlite")
    parser.add_argument("--import-db", default="migration/imports/legacy-import.sqlite")
    parser.add_argument("--source-root", default="/Volumes/webstore/endurance.net")
    parser.add_argument("--output-dir", default="migration/media")
    parser.add_argument("--waivers", help="Optional JSONL waiver file for known missing media references.")
    parser.add_argument("--probe-dimensions", action="store_true", help="Read image headers for PNG/GIF dimensions. Slower on mounted legacy media.")
    args = parser.parse_args()
    import_db = Path(args.import_db).resolve() if args.import_db else None
    return MediaManifestConfig(
        inventory_db=Path(args.inventory_db).resolve(),
        import_db=import_db,
        source_root=Path(args.source_root).resolve(),
        output_dir=Path(args.output_dir).resolve(),
        waivers=Path(args.waivers).resolve() if args.waivers else None,
        probe_dimensions=args.probe_dimensions,
    )


def main() -> int:
    config = parse_args()
    if not config.inventory_db.exists():
        raise SystemExit(f"inventory database not found: {config.inventory_db}")
    generate(config)
    print(f"Wrote media manifest reports to {config.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

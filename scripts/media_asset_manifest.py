#!/usr/bin/env python3
"""Generate durable media manifests from inventory and imported references."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import quote, unquote, urlparse


PUBLIC_MEDIA_PREFIX = "/legacy-media/"
CMS_MEDIA_PREFIX = "/media/"
MEDIA_CLASSIFICATIONS = {"media_asset", "document"}


@dataclass(frozen=True)
class MediaManifestConfig:
    inventory_db: Path
    import_db: Path | None
    source_root: Path
    output_dir: Path
    waivers: Path | None
    probe_dimensions: bool
    staging_dir: Path | None
    stage_assets: bool
    asset_kinds: frozenset[str] | None
    max_assets: int | None
    stage_mode: str = "copy"
    symlink_root: Path | None = None


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


def public_url(source_path: str) -> str:
    return PUBLIC_MEDIA_PREFIX + quote(source_path.lstrip("/"), safe="/")


def cms_asset_id(source_path: str) -> str:
    return "legacy-" + hashlib.sha256(source_path.encode("utf-8")).hexdigest()[:16]


def cms_public_url(asset_id: str, source_path: str) -> str:
    filename = Path(source_path).name or "asset"
    return CMS_MEDIA_PREFIX + quote(f"{asset_id}/{filename}", safe="/")


def cms_storage_key(asset_id: str, source_path: str) -> str:
    filename = Path(source_path).name or "asset"
    return quote(f"legacy/{asset_id}/{filename}", safe="/")


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


def asset_kind_allowed(kind: str, allowed: frozenset[str] | None) -> bool:
    return allowed is None or kind in allowed


def row_asset_kind(row: dict[str, object]) -> str:
    return asset_kind(str(row["extension"] or ""), str(row["mime_type"] or ""))


def reference_asset_kind(
    referenced_url: str,
    referenced_path: str | None,
    normalized_path: str | None,
    inventory_by_path: dict[str, dict[str, object]],
) -> str:
    if normalized_path and normalized_path in inventory_by_path:
        return row_asset_kind(inventory_by_path[normalized_path])
    parsed = urlparse(referenced_url)
    candidate = normalized_path or referenced_path or parsed.path or referenced_url
    suffix = Path(unquote(candidate.split("?", 1)[0].split("#", 1)[0])).suffix
    return asset_kind(suffix, "")


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


def copy_to_staging(
    source_root: Path,
    staging_dir: Path | None,
    source_path: str,
    storage_key: str,
    enabled: bool,
    stage_mode: str,
    symlink_root: Path | None,
) -> tuple[str, str]:
    if staging_dir is None:
        return "", "not_configured"
    destination = staging_dir / storage_key
    if not enabled:
        return str(destination), "planned"
    if stage_mode == "symlink":
        target_root = symlink_root if symlink_root is not None else source_root
        target = target_root / source_path
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.is_symlink():
                if os.readlink(destination) == str(target):
                    return str(destination), "symlinked"
                destination.unlink()
            elif destination.exists():
                return str(destination), "existing"
            destination.symlink_to(target)
            return str(destination), "symlinked"
        except OSError as exc:
            return str(destination), f"symlink_failed: {exc}"
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_root / source_path, destination)
        return str(destination), "copied"
    except OSError as exc:
        return str(destination), f"copy_failed: {exc}"


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
    if config.stage_assets and config.staging_dir:
        config.staging_dir.mkdir(parents=True, exist_ok=True)
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
    filtered_file_rows = [row for row in file_rows if asset_kind_allowed(row_asset_kind(row), config.asset_kinds)]
    readable_asset_rows = [row for row in filtered_file_rows if row["status"] == "ok"]
    unreadable_asset_rows = [row for row in filtered_file_rows if row["status"] != "ok"]
    if config.max_assets is not None:
        readable_asset_rows = readable_asset_rows[: config.max_assets]

    manifest_rows: list[dict[str, object]] = []
    copy_failures: list[dict[str, object]] = []
    for row in readable_asset_rows:
        source_path = str(row["path"])
        width, height = image_dimensions(config.source_root / source_path) if config.probe_dimensions else (None, None)
        asset_id = cms_asset_id(source_path)
        storage_key = cms_storage_key(asset_id, source_path)
        staged_path, stage_status = copy_to_staging(
            config.source_root,
            config.staging_dir,
            source_path,
            storage_key,
            config.stage_assets,
            config.stage_mode,
            config.symlink_root,
        )
        if stage_status.startswith(("copy_failed", "symlink_failed")):
            copy_failures.append({"source_path": source_path, "staged_path": staged_path, "reason": stage_status})
        manifest_rows.append(
            {
                "cms_asset_id": asset_id,
                "source_path": source_path,
                "legacy_url": legacy_url(source_path),
                "public_url": public_url(source_path),
                "cms_public_url": cms_public_url(asset_id, source_path),
                "cms_storage_key": storage_key,
                "asset_kind": row_asset_kind(row),
                "mime_type": row["mime_type"] or "",
                "extension": row["extension"] or "",
                "size": row["size"],
                "checksum_sha256": row["checksum_sha256"] or "",
                "width": width,
                "height": height,
                "title": Path(source_path).stem.replace("_", " ").replace("-", " ").strip(),
                "alt_text": "",
                "credit": "",
                "cms_status": "imported",
                "cms_source_context": "legacy-source-inventory",
                "staged_path": staged_path,
                "stage_status": stage_status,
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
            ref_kind = reference_asset_kind(
                referenced_url,
                str(reference["referenced_path"] or ""),
                normalized,
                inventory_by_path,
            )
            if not asset_kind_allowed(ref_kind, config.asset_kinds):
                continue
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

    duplicates: list[dict[str, object]] = []
    checksum_groups: dict[str, list[dict[str, object]]] = {}
    for row in manifest_rows:
        checksum = str(row["checksum_sha256"])
        if checksum:
            checksum_groups.setdefault(checksum, []).append(row)
    for checksum, items in sorted(checksum_groups.items()):
        if len(items) > 1:
            duplicates.append(
                {
                    "checksum_sha256": checksum,
                    "asset_count": len(items),
                    "source_paths": [item["source_path"] for item in items],
                    "cms_asset_ids": [item["cms_asset_id"] for item in items],
                }
            )

    cms_blockers: list[dict[str, object]] = []
    for item in missing_refs:
        cms_blockers.append(
            {
                "blocker_type": "missing_reference",
                "source_path": item["source_path"],
                "referenced_url": item["referenced_url"],
                "resolved_path": item["resolved_path"],
                "reason": item["reason"],
                "status": "open" if not str(item["reason"]).startswith("waived:") else "waived",
            }
        )
    for item in unreadable_rows:
        cms_blockers.append(
            {
                "blocker_type": "unreadable_source",
                "source_path": item["source_path"],
                "referenced_url": item["legacy_url"],
                "resolved_path": item["source_path"],
                "reason": item["status"],
                "status": "open",
            }
        )
    for item in copy_failures:
        cms_blockers.append(
            {
                "blocker_type": "copy_failure",
                "source_path": item["source_path"],
                "referenced_url": "",
                "resolved_path": item["staged_path"],
                "reason": item["reason"],
                "status": "open",
            }
        )

    manifest_count = write_jsonl(config.output_dir / "media-manifest.jsonl", manifest_rows)
    cms_count = write_jsonl(config.output_dir / "cms-media-assets.jsonl", manifest_rows)
    missing_count = write_jsonl(config.output_dir / "missing-media-references.jsonl", missing_refs)
    external_count = write_jsonl(config.output_dir / "external-media-references.jsonl", external_refs)
    unreadable_count = write_jsonl(config.output_dir / "unreadable-media.jsonl", unreadable_rows)
    duplicate_count = write_jsonl(config.output_dir / "duplicate-media-assets.jsonl", duplicates)
    blocker_count = write_jsonl(config.output_dir / "cms-media-blockers.jsonl", cms_blockers)
    write_cms_sql(config.output_dir / "cms-media-import.sql", manifest_rows)

    summary = {
        "inventory_db": str(config.inventory_db),
        "import_db": str(config.import_db) if config.import_db else "",
        "source_root": str(config.source_root),
        "public_media_prefix": PUBLIC_MEDIA_PREFIX,
        "cms_media_prefix": CMS_MEDIA_PREFIX,
        "staging_dir": str(config.staging_dir) if config.staging_dir else "",
        "stage_assets_enabled": config.stage_assets,
        "stage_mode": config.stage_mode,
        "symlink_root": str(config.symlink_root) if config.symlink_root else "",
        "dimension_probe_enabled": config.probe_dimensions,
        "asset_kind_filter": sorted(config.asset_kinds) if config.asset_kinds else [],
        "max_assets": config.max_assets,
        "bounded_manifest": config.max_assets is not None,
        "manifest_entries": manifest_count,
        "cms_media_assets": cms_count,
        "unreadable_media": unreadable_count,
        "resolved_media_references": resolved_refs,
        "missing_media_references": missing_count,
        "external_media_references": external_count,
        "duplicate_media_assets": duplicate_count,
        "cms_media_blockers": blocker_count,
        "asset_copy_failures": len(copy_failures),
        "waived_media_references": waived_refs,
        "asset_kind_counts": {},
    }
    for row in manifest_rows:
        kind = str(row["asset_kind"])
        summary["asset_kind_counts"][kind] = int(summary["asset_kind_counts"].get(kind, 0)) + 1
    write_json(config.output_dir / "media-summary.json", summary)


def write_cms_sql(path: Path, manifest_rows: list[dict[str, object]]) -> None:
    columns = [
        "id",
        "source_path",
        "legacy_url",
        "public_url",
        "cms_public_url",
        "storage_key",
        "asset_kind",
        "mime_type",
        "extension",
        "size_bytes",
        "checksum_sha256",
        "width",
        "height",
        "title",
        "alt_text",
        "credit",
        "source_context",
        "import_status",
        "staged_path",
        "scanned_at",
    ]
    lines = [
        "-- Generated by scripts/media_asset_manifest.py.",
        "-- Import into the cms_media_assets table after reviewing blockers.",
    ]
    if manifest_rows:
        lines.append(f"INSERT INTO cms_media_assets ({', '.join(columns)}) VALUES")
        values: list[str] = []
        for row in manifest_rows:
            values.append(
                "  ("
                + ", ".join(
                    sql_literal(value)
                    for value in [
                        row["cms_asset_id"],
                        row["source_path"],
                        row["legacy_url"],
                        row["public_url"],
                        row["cms_public_url"],
                        row["cms_storage_key"],
                        row["asset_kind"],
                        row["mime_type"],
                        row["extension"],
                        row["size"],
                        row["checksum_sha256"],
                        row["width"],
                        row["height"],
                        row["title"],
                        row["alt_text"],
                        row["credit"],
                        row["cms_source_context"],
                        row["cms_status"],
                        row["staged_path"],
                        row["scanned_at"],
                    ]
                )
                + ")"
            )
        lines.append(",\n".join(values))
        lines.append("ON CONFLICT (id) DO UPDATE SET")
        lines.append("  source_path = EXCLUDED.source_path,")
        lines.append("  legacy_url = EXCLUDED.legacy_url,")
        lines.append("  public_url = EXCLUDED.public_url,")
        lines.append("  cms_public_url = EXCLUDED.cms_public_url,")
        lines.append("  storage_key = EXCLUDED.storage_key,")
        lines.append("  asset_kind = EXCLUDED.asset_kind,")
        lines.append("  mime_type = EXCLUDED.mime_type,")
        lines.append("  extension = EXCLUDED.extension,")
        lines.append("  size_bytes = EXCLUDED.size_bytes,")
        lines.append("  checksum_sha256 = EXCLUDED.checksum_sha256,")
        lines.append("  width = EXCLUDED.width,")
        lines.append("  height = EXCLUDED.height,")
        lines.append("  title = EXCLUDED.title,")
        lines.append("  alt_text = EXCLUDED.alt_text,")
        lines.append("  credit = EXCLUDED.credit,")
        lines.append("  source_context = EXCLUDED.source_context,")
        lines.append("  import_status = EXCLUDED.import_status,")
        lines.append("  staged_path = EXCLUDED.staged_path,")
        lines.append("  scanned_at = EXCLUDED.scanned_at;")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> MediaManifestConfig:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory-db", default="migration/inventory/source-inventory.sqlite")
    parser.add_argument("--import-db", default="migration/imports/legacy-import.sqlite")
    parser.add_argument("--source-root", default="/Volumes/webstore/endurance.net")
    parser.add_argument("--output-dir", default="migration/media")
    parser.add_argument("--waivers", help="Optional JSONL waiver file for known missing media references.")
    parser.add_argument("--probe-dimensions", action="store_true", help="Read image headers for PNG/GIF dimensions. Slower on mounted legacy media.")
    parser.add_argument("--staging-dir", help="Optional CMS asset staging directory. Defaults to output-dir/legacy-media when --stage-assets is set.")
    parser.add_argument("--stage-assets", action="store_true", help="Copy readable media into the CMS staging directory.")
    parser.add_argument(
        "--stage-mode",
        choices=("copy", "symlink"),
        default="copy",
        help="How --stage-assets materializes files. copy duplicates bytes; symlink creates CMS storage links.",
    )
    parser.add_argument(
        "--symlink-root",
        help="Root used for symlink targets in --stage-mode symlink. Defaults to --source-root; use /var/www/legacy-media for container-mounted review.",
    )
    parser.add_argument("--image-only", action="store_true", help="Limit manifests, blockers, duplicate reports, and staging copies to image assets.")
    parser.add_argument("--max-assets", type=int, help="Limit readable manifest/staging rows for bounded smoke runs.")
    args = parser.parse_args()
    if args.max_assets is not None and args.max_assets < 1:
        parser.error("--max-assets must be greater than zero")
    import_db = Path(args.import_db).resolve() if args.import_db else None
    output_dir = Path(args.output_dir).resolve()
    staging_dir = Path(args.staging_dir).resolve() if args.staging_dir else (output_dir / "legacy-media" if args.stage_assets else None)
    asset_kinds = frozenset({"image"}) if args.image_only else None
    return MediaManifestConfig(
        inventory_db=Path(args.inventory_db).resolve(),
        import_db=import_db,
        source_root=Path(args.source_root).resolve(),
        output_dir=output_dir,
        waivers=Path(args.waivers).resolve() if args.waivers else None,
        probe_dimensions=args.probe_dimensions,
        staging_dir=staging_dir,
        stage_assets=args.stage_assets,
        asset_kinds=asset_kinds,
        max_assets=args.max_assets,
        stage_mode=args.stage_mode,
        symlink_root=Path(args.symlink_root) if args.symlink_root else None,
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

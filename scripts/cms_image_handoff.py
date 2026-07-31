#!/usr/bin/env python3
"""Build CMS/Directus review bundles from an image-only media manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".jpe", ".png", ".gif", ".webp", ".svg", ".ico"}


def read_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: Iterable[dict[str, object]]) -> int:
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
            count += 1
    return count


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def image_like(value: object) -> bool:
    suffix = Path(str(value or "").split("?", 1)[0].split("#", 1)[0]).suffix.lower()
    return suffix in IMAGE_EXTENSIONS


def duplicate_group_id(checksum: str) -> str:
    return "dup-" + hashlib.sha256(checksum.encode("utf-8")).hexdigest()[:16]


def build_duplicate_lookup(duplicates: list[dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, str]]:
    duplicate_rows: list[dict[str, object]] = []
    source_to_group: dict[str, str] = {}
    for duplicate in duplicates:
        checksum = str(duplicate.get("checksum_sha256") or "")
        source_paths = [str(path) for path in duplicate.get("source_paths", [])]
        image_paths = [path for path in source_paths if image_like(path)]
        if not checksum or len(image_paths) < 2:
            continue
        group_id = duplicate_group_id(checksum)
        for path in image_paths:
            source_to_group[path] = group_id
        duplicate_rows.append(
            {
                "id": group_id,
                "checksum_sha256": checksum,
                "asset_count": len(image_paths),
                "source_paths": image_paths,
                "review_status": "needs_review",
                "canonical_asset_id": "",
                "replacement_asset_id": "",
                "editor_notes": "",
            }
        )
    return duplicate_rows, source_to_group


def build_asset_rows(manifest_rows: list[dict[str, object]], source_to_duplicate_group: dict[str, str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in manifest_rows:
        if row.get("asset_kind") != "image":
            continue
        source_path = str(row.get("source_path") or "")
        rows.append(
            {
                "id": row.get("cms_asset_id") or "",
                "source_path": source_path,
                "legacy_url": row.get("legacy_url") or "",
                "public_url": row.get("public_url") or "",
                "cms_public_url": row.get("cms_public_url") or "",
                "storage_key": row.get("cms_storage_key") or "",
                "mime_type": row.get("mime_type") or "",
                "extension": row.get("extension") or "",
                "size_bytes": row.get("size") or 0,
                "checksum_sha256": row.get("checksum_sha256") or "",
                "width": row.get("width"),
                "height": row.get("height"),
                "title": row.get("title") or "",
                "alt_text": row.get("alt_text") or "",
                "credit": row.get("credit") or "",
                "copyright_notes": "",
                "review_status": "needs_editorial_review",
                "duplicate_group_id": source_to_duplicate_group.get(source_path, ""),
                "replacement_asset_id": "",
                "source_context": row.get("cms_source_context") or "legacy-source-inventory",
                "import_status": row.get("cms_status") or "imported",
                "staged_path": row.get("staged_path") or "",
                "scanned_at": row.get("scanned_at") or "",
            }
        )
    return rows


def build_blocker_rows(blockers: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for blocker in blockers:
        source_path = blocker.get("source_path") or ""
        referenced_url = blocker.get("referenced_url") or ""
        resolved_path = blocker.get("resolved_path") or ""
        if not (image_like(source_path) or image_like(referenced_url) or image_like(resolved_path)):
            continue
        rows.append(
            {
                "blocker_type": blocker.get("blocker_type") or "",
                "source_path": source_path,
                "referenced_url": referenced_url,
                "resolved_path": resolved_path,
                "reason": blocker.get("reason") or "",
                "status": blocker.get("status") or "open",
                "review_status": "needs_resolution",
                "replacement_asset_id": "",
                "editor_notes": "",
            }
        )
    return rows


def generate(media_dir: Path, output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_rows = read_jsonl(media_dir / "media-manifest.jsonl")
    blocker_rows = read_jsonl(media_dir / "cms-media-blockers.jsonl")
    duplicate_rows = read_jsonl(media_dir / "duplicate-media-assets.jsonl")

    duplicates, source_to_duplicate_group = build_duplicate_lookup(duplicate_rows)
    assets = build_asset_rows(manifest_rows, source_to_duplicate_group)
    blockers = build_blocker_rows(blocker_rows)

    asset_count = write_jsonl(output_dir / "directus-image-assets.jsonl", assets)
    blocker_count = write_jsonl(output_dir / "directus-image-blockers.jsonl", blockers)
    duplicate_count = write_jsonl(output_dir / "directus-image-duplicates.jsonl", duplicates)
    summary = {
        "media_dir": str(media_dir),
        "output_dir": str(output_dir),
        "image_assets": asset_count,
        "image_blockers": blocker_count,
        "duplicate_image_groups": duplicate_count,
        "provenance_fields": [
            "id",
            "source_path",
            "legacy_url",
            "public_url",
            "cms_public_url",
            "storage_key",
            "checksum_sha256",
            "source_context",
            "scanned_at",
        ],
        "editorial_fields": [
            "title",
            "alt_text",
            "credit",
            "copyright_notes",
            "review_status",
            "duplicate_group_id",
            "replacement_asset_id",
            "editor_notes",
        ],
    }
    write_json(output_dir / "directus-image-handoff-summary.json", summary)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--media-dir", default="migration/media/images", help="Directory containing image-only media manifest reports.")
    parser.add_argument("--output-dir", help="Output directory for CMS handoff JSONL files. Defaults to media-dir/cms-handoff.")
    args = parser.parse_args(argv)
    media_dir = Path(args.media_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else media_dir / "cms-handoff"
    summary = generate(media_dir, output_dir)
    print(f"Wrote CMS image handoff bundle to {output_dir} ({summary['image_assets']} image assets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

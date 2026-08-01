#!/usr/bin/env python3
"""Build CMS/Directus review bundles from Photoshop gallery manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


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


def gallery_records(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for row in rows:
        records.append(
            {
                "id": row.get("gallery_id") or "",
                "slug": row.get("slug") or "",
                "title": row.get("title") or "",
                "source_root": row.get("source_root") or "",
                "entry_source_path": row.get("entry_source_path") or "",
                "legacy_url": row.get("legacy_url") or "",
                "pattern": row.get("pattern") or "",
                "item_count": row.get("item_count") or 0,
                "parser_version": row.get("parser_version") or "",
                "review_status": "needs_editorial_review",
                "credit": "",
                "copyright_notes": "",
                "editor_notes": "",
            }
        )
    return records


def item_records(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for row in rows:
        records.append(
            {
                "id": row.get("item_id") or "",
                "gallery_id": row.get("gallery_id") or "",
                "gallery_slug": row.get("gallery_slug") or "",
                "position": row.get("position") or 0,
                "caption": row.get("caption") or "",
                "thumbnail_source_path": row.get("thumbnail_source_path") or "",
                "thumbnail_public_url": row.get("thumbnail_public_url") or "",
                "item_page_source_path": row.get("item_page_source_path") or "",
                "item_page_legacy_url": row.get("item_page_legacy_url") or "",
                "full_image_source_path": row.get("full_image_source_path") or "",
                "full_image_public_url": row.get("full_image_public_url") or "",
                "checksum_sha256": row.get("checksum_sha256") or "",
                "parser_version": row.get("parser_version") or "",
                "review_status": "needs_editorial_review",
                "canonical_media_asset_id": "",
                "replacement_asset_id": "",
                "credit": "",
                "copyright_notes": "",
                "editor_notes": "",
            }
        )
    return records


def blocker_records(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for row in rows:
        records.append(
            {
                "blocker_type": row.get("blocker_type") or "",
                "gallery_id": row.get("gallery_id") or "",
                "gallery_slug": row.get("gallery_slug") or "",
                "source_root": row.get("source_root") or "",
                "source_path": row.get("source_path") or "",
                "item_id": row.get("item_id") or "",
                "position": row.get("position") or 0,
                "reason": row.get("reason") or "",
                "status": row.get("status") or "open",
                "review_status": "needs_resolution",
                "replacement_asset_id": "",
                "editor_notes": "",
            }
        )
    return records


def generate(gallery_dir: Path, output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    galleries = gallery_records(read_jsonl(gallery_dir / "photoshop-galleries.jsonl"))
    items = item_records(read_jsonl(gallery_dir / "photoshop-gallery-items.jsonl"))
    blockers = blocker_records(read_jsonl(gallery_dir / "photoshop-gallery-blockers.jsonl"))

    gallery_count = write_jsonl(output_dir / "directus-galleries.jsonl", galleries)
    item_count = write_jsonl(output_dir / "directus-gallery-items.jsonl", items)
    blocker_count = write_jsonl(output_dir / "directus-gallery-blockers.jsonl", blockers)
    summary = {
        "gallery_dir": str(gallery_dir),
        "output_dir": str(output_dir),
        "galleries": gallery_count,
        "gallery_items": item_count,
        "gallery_blockers": blocker_count,
        "provenance_fields": [
            "id",
            "source_root",
            "entry_source_path",
            "legacy_url",
            "thumbnail_source_path",
            "item_page_source_path",
            "full_image_source_path",
            "checksum_sha256",
            "parser_version",
        ],
        "editorial_fields": [
            "title",
            "caption",
            "credit",
            "copyright_notes",
            "review_status",
            "canonical_media_asset_id",
            "replacement_asset_id",
            "editor_notes",
        ],
    }
    write_json(output_dir / "directus-gallery-handoff-summary.json", summary)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gallery-dir", default="migration/galleries", help="Directory containing Photoshop gallery manifest outputs.")
    parser.add_argument("--output-dir", help="Output directory for CMS handoff JSONL files. Defaults to gallery-dir/cms-handoff.")
    args = parser.parse_args(argv)
    gallery_dir = Path(args.gallery_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else gallery_dir / "cms-handoff"
    summary = generate(gallery_dir, output_dir)
    print(f"Wrote CMS gallery handoff bundle to {output_dir} ({summary['galleries']} galleries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

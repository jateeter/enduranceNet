#!/usr/bin/env python3
"""Smoke tests for CMS image handoff bundles."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HANDOFF_PATH = REPO_ROOT / "scripts" / "cms_image_handoff.py"

spec = importlib.util.spec_from_file_location("cms_image_handoff", HANDOFF_PATH)
cms_image_handoff = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["cms_image_handoff"] = cms_image_handoff
spec.loader.exec_module(cms_image_handoff)


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class CmsImageHandoffTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.media_dir = self.root / "media"
        self.output_dir = self.root / "handoff"
        self.media_dir.mkdir()
        write_jsonl(
            self.media_dir / "media-manifest.jsonl",
            [
                {
                    "cms_asset_id": "legacy-one",
                    "source_path": "images/one.jpg",
                    "legacy_url": "/images/one.jpg",
                    "public_url": "/legacy-media/images/one.jpg",
                    "cms_public_url": "/media/legacy-one/one.jpg",
                    "cms_storage_key": "legacy/legacy-one/one.jpg",
                    "asset_kind": "image",
                    "mime_type": "image/jpeg",
                    "extension": ".jpg",
                    "size": 12,
                    "checksum_sha256": "sha-image",
                    "width": None,
                    "height": None,
                    "title": "one",
                    "alt_text": "",
                    "credit": "",
                    "cms_source_context": "legacy-source-inventory",
                    "cms_status": "imported",
                    "staged_path": "/tmp/one.jpg",
                    "scanned_at": "2026-07-31T00:00:00Z",
                },
                {"cms_asset_id": "legacy-doc", "source_path": "docs/ride.pdf", "asset_kind": "document"},
                {
                    "cms_asset_id": "legacy-copy",
                    "source_path": "images/one-copy.jpg",
                    "asset_kind": "image",
                    "checksum_sha256": "sha-image",
                },
            ],
        )
        write_jsonl(
            self.media_dir / "cms-media-blockers.jsonl",
            [
                {
                    "blocker_type": "missing_reference",
                    "source_path": "pages/index.html",
                    "referenced_url": "missing.jpg",
                    "resolved_path": "pages/missing.jpg",
                    "reason": "not_in_manifest",
                    "status": "open",
                },
                {
                    "blocker_type": "missing_reference",
                    "source_path": "pages/index.html",
                    "referenced_url": "missing.pdf",
                    "resolved_path": "pages/missing.pdf",
                    "reason": "not_in_manifest",
                    "status": "open",
                },
            ],
        )
        write_jsonl(
            self.media_dir / "duplicate-media-assets.jsonl",
            [
                {
                    "checksum_sha256": "sha-image",
                    "asset_count": 2,
                    "source_paths": ["images/one.jpg", "images/one-copy.jpg"],
                    "cms_asset_ids": ["legacy-one", "legacy-copy"],
                }
            ],
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_handoff_filters_to_images_and_adds_review_fields(self) -> None:
        summary = cms_image_handoff.generate(self.media_dir, self.output_dir)
        self.assertEqual(2, summary["image_assets"])
        self.assertEqual(1, summary["image_blockers"])
        self.assertEqual(1, summary["duplicate_image_groups"])

        assets = read_jsonl(self.output_dir / "directus-image-assets.jsonl")
        self.assertEqual({"legacy-one", "legacy-copy"}, {item["id"] for item in assets})
        self.assertEqual({"needs_editorial_review"}, {item["review_status"] for item in assets})
        self.assertTrue(all("source_path" in item for item in assets))

        blockers = read_jsonl(self.output_dir / "directus-image-blockers.jsonl")
        self.assertEqual(["pages/missing.jpg"], [item["resolved_path"] for item in blockers])

        duplicates = read_jsonl(self.output_dir / "directus-image-duplicates.jsonl")
        self.assertEqual(1, len(duplicates))
        self.assertEqual("needs_review", duplicates[0]["review_status"])


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Smoke tests for CMS gallery handoff bundles."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HANDOFF_PATH = REPO_ROOT / "scripts" / "cms_gallery_handoff.py"

spec = importlib.util.spec_from_file_location("cms_gallery_handoff", HANDOFF_PATH)
cms_gallery_handoff = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["cms_gallery_handoff"] = cms_gallery_handoff
spec.loader.exec_module(cms_gallery_handoff)


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class CmsGalleryHandoffTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.gallery_dir = self.root / "galleries"
        self.output_dir = self.root / "handoff"
        self.gallery_dir.mkdir()
        write_jsonl(
            self.gallery_dir / "photoshop-galleries.jsonl",
            [
                {
                    "gallery_id": "gallery-one",
                    "slug": "gallery-one",
                    "title": "Gallery One",
                    "source_root": "gallery/one",
                    "entry_source_path": "gallery/one/index.html",
                    "legacy_url": "/gallery/one/index.html",
                    "pattern": "paginated-index",
                    "item_count": 1,
                    "parser_version": "photoshop-gallery-manifest-v1",
                }
            ],
        )
        write_jsonl(
            self.gallery_dir / "photoshop-gallery-items.jsonl",
            [
                {
                    "item_id": "item-one",
                    "gallery_id": "gallery-one",
                    "gallery_slug": "gallery-one",
                    "position": 1,
                    "caption": "First image",
                    "thumbnail_source_path": "gallery/one/thumbnails/IMG_1.jpg",
                    "thumbnail_public_url": "/legacy-media/gallery/one/thumbnails/IMG_1.jpg",
                    "item_page_source_path": "gallery/one/pages/IMG_1.html",
                    "item_page_legacy_url": "/gallery/one/pages/IMG_1.html",
                    "full_image_source_path": "gallery/one/images/IMG_1.jpg",
                    "full_image_public_url": "/legacy-media/gallery/one/images/IMG_1.jpg",
                    "checksum_sha256": "sha-one",
                    "parser_version": "photoshop-gallery-manifest-v1",
                }
            ],
        )
        write_jsonl(
            self.gallery_dir / "photoshop-gallery-blockers.jsonl",
            [
                {
                    "blocker_type": "missing_full_image",
                    "gallery_id": "gallery-one",
                    "gallery_slug": "gallery-one",
                    "source_root": "gallery/one",
                    "source_path": "gallery/one/images/IMG_2.jpg",
                    "item_id": "item-two",
                    "position": 2,
                    "reason": "not_in_inventory",
                    "status": "open",
                }
            ],
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_handoff_adds_review_fields_and_preserves_provenance(self) -> None:
        summary = cms_gallery_handoff.generate(self.gallery_dir, self.output_dir)

        self.assertEqual(1, summary["galleries"])
        self.assertEqual(1, summary["gallery_items"])
        self.assertEqual(1, summary["gallery_blockers"])
        galleries = read_jsonl(self.output_dir / "directus-galleries.jsonl")
        self.assertEqual("needs_editorial_review", galleries[0]["review_status"])
        self.assertEqual("gallery/one", galleries[0]["source_root"])
        items = read_jsonl(self.output_dir / "directus-gallery-items.jsonl")
        self.assertEqual("", items[0]["canonical_media_asset_id"])
        self.assertEqual("sha-one", items[0]["checksum_sha256"])
        blockers = read_jsonl(self.output_dir / "directus-gallery-blockers.jsonl")
        self.assertEqual("needs_resolution", blockers[0]["review_status"])


if __name__ == "__main__":
    unittest.main()

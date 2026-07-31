#!/usr/bin/env python3
"""Smoke tests for Photoshop gallery manifest generation."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "scripts" / "photoshop_gallery_manifest.py"

spec = importlib.util.spec_from_file_location("photoshop_gallery_manifest", MANIFEST_PATH)
photoshop_gallery_manifest = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["photoshop_gallery_manifest"] = photoshop_gallery_manifest
spec.loader.exec_module(photoshop_gallery_manifest)


class PhotoshopGalleryManifestTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.source_root = self.root / "source"
        self.output_dir = self.root / "galleries"
        self.inventory_db = self.root / "inventory.sqlite"
        self.source_root.mkdir()
        self._write_sources()
        self._write_inventory()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _write_file(self, relative_path: str, content: str = "x") -> None:
        target = self.source_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def _write_sources(self) -> None:
        self._write_file(
            "2005PAC/Gallery/AsadorsS/ThumbnailFrame.html",
            """
            <html><head><title>Asadors</title></head><body>
              <h3>Asadors Loop</h3>
              <a href="pages/IMG_0005.html" target="RightFrame">
                <img src="thumbnails/IMG_0005.jpg" alt="First rider" />
              </a>
              <a href="pages/IMG_0006.html" target="RightFrame">
                <img src="thumbnails/IMG_0006.jpg" alt="Second rider" />
              </a>
            </body></html>
            """,
        )
        self._write_file(
            "2005PAC/Gallery/AsadorsS/pages/IMG_0005.html",
            '<html><body><img src="../images/IMG_0005.jpg" alt="First rider" /></body></html>',
        )
        self._write_file(
            "2005PAC/Gallery/AsadorsS/pages/IMG_0006.html",
            '<html><body><img src="../images/IMG_0006.jpg" alt="Second rider" /></body></html>',
        )
        self._write_file("2005PAC/Gallery/AsadorsS/thumbnails/IMG_0005.jpg")
        self._write_file("2005PAC/Gallery/AsadorsS/thumbnails/IMG_0006.jpg")
        self._write_file("2005PAC/Gallery/AsadorsS/images/IMG_0005.jpg")
        self._write_file("2005PAC/Gallery/AsadorsS/images/IMG_0006.jpg")

        self._write_file(
            "gallery/Welcome/index.html",
            """
            <html><body><h3>Welcome Reception</h3>
              <a href="pages/IMG_1000.html"><img src="thumbnails/IMG_1000.jpg" width="200" height="149" alt="Welcome" /></a>
              <a href="pages/IMG_1001.html"><img src="thumbnails/IMG_1001.jpg" width="200" height="149" alt="Missing full image" /></a>
            </body></html>
            """,
        )
        self._write_file(
            "gallery/Welcome/pages/IMG_1000.html",
            '<html><body><img src="../images/IMG_1000.jpg" /></body></html>',
        )
        self._write_file(
            "gallery/Welcome/pages/IMG_1001.html",
            '<html><body><img src="../images/IMG_1001.jpg" /></body></html>',
        )
        self._write_file("gallery/Welcome/thumbnails/IMG_1000.jpg")
        self._write_file("gallery/Welcome/thumbnails/IMG_1001.jpg")
        self._write_file("gallery/Welcome/images/IMG_1000.jpg")

    def _write_inventory(self) -> None:
        conn = sqlite3.connect(self.inventory_db)
        try:
            conn.execute(
                """
                CREATE TABLE files (
                  path TEXT PRIMARY KEY,
                  kind TEXT,
                  classification TEXT,
                  extension TEXT,
                  mime_type TEXT,
                  size INTEGER,
                  checksum_sha256 TEXT,
                  status TEXT,
                  mode_octal TEXT,
                  scanned_at TEXT
                )
                """
            )
            for path in sorted(item.relative_to(self.source_root).as_posix() for item in self.source_root.rglob("*") if item.is_file()):
                extension = Path(path).suffix.lower()
                classification = "media_asset" if extension in {".jpg", ".gif", ".png"} else "executable_template"
                conn.execute(
                    """
                    INSERT INTO files VALUES (?, 'file', ?, ?, ?, ?, ?, 'ok', '0644', '2026-07-31T00:00:00Z')
                    """,
                    (
                        path,
                        classification,
                        extension,
                        "image/jpeg" if classification == "media_asset" else "text/html",
                        10,
                        f"sha-{path}",
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    def _jsonl(self, filename: str) -> list[dict[str, object]]:
        return [
            json.loads(line)
            for line in (self.output_dir / filename).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def test_manifest_parses_framed_and_paginated_galleries(self) -> None:
        config = photoshop_gallery_manifest.GalleryConfig(
            inventory_db=self.inventory_db,
            source_root=self.source_root,
            output_dir=self.output_dir,
            max_galleries=None,
        )

        summary = photoshop_gallery_manifest.generate(config)

        self.assertEqual(2, summary["gallery_count"])
        self.assertEqual(4, summary["item_count"])
        galleries = self._jsonl("photoshop-galleries.jsonl")
        self.assertEqual({"framed-thumbnail", "paginated-index"}, {item["pattern"] for item in galleries})
        self.assertEqual({"Asadors Loop", "Welcome Reception"}, {item["title"] for item in galleries})

        items = self._jsonl("photoshop-gallery-items.jsonl")
        self.assertEqual(4, len(items))
        first = next(item for item in items if item["caption"] == "First rider")
        self.assertEqual("2005PAC/Gallery/AsadorsS/thumbnails/IMG_0005.jpg", first["thumbnail_source_path"])
        self.assertEqual("2005PAC/Gallery/AsadorsS/images/IMG_0005.jpg", first["full_image_source_path"])
        self.assertTrue(str(first["thumbnail_public_url"]).startswith("/legacy-media/"))
        self.assertTrue(str(first["full_image_public_url"]).startswith("/legacy-media/"))

        blockers = self._jsonl("photoshop-gallery-blockers.jsonl")
        self.assertEqual(1, len(blockers))
        self.assertEqual("missing_full_image", blockers[0]["blocker_type"])
        self.assertEqual("gallery/Welcome/images/IMG_1001.jpg", blockers[0]["source_path"])
        self.assertIn("INSERT INTO cms_galleries", (self.output_dir / "cms-gallery-import.sql").read_text(encoding="utf-8"))

    def test_max_galleries_supports_bounded_runs(self) -> None:
        config = photoshop_gallery_manifest.GalleryConfig(
            inventory_db=self.inventory_db,
            source_root=self.source_root,
            output_dir=self.output_dir,
            max_galleries=1,
        )

        summary = photoshop_gallery_manifest.generate(config)

        self.assertEqual(1, summary["gallery_count"])
        self.assertTrue(summary["bounded_manifest"])
        self.assertEqual(1, summary["max_galleries"])


if __name__ == "__main__":
    unittest.main()

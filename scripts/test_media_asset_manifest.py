#!/usr/bin/env python3
"""Smoke tests for the media asset manifest generator."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MEDIA_MANIFEST_PATH = REPO_ROOT / "scripts" / "media_asset_manifest.py"

spec = importlib.util.spec_from_file_location("media_asset_manifest", MEDIA_MANIFEST_PATH)
media_asset_manifest = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["media_asset_manifest"] = media_asset_manifest
spec.loader.exec_module(media_asset_manifest)


PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00"
)


class MediaAssetManifestTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.source_root = self.root / "source"
        self.output_dir = self.root / "media"
        self.inventory_db = self.root / "inventory.sqlite"
        self.import_db = self.root / "import.sqlite"
        self.source_root.mkdir()
        self._write_sources()
        self._write_inventory()
        self._write_import_db()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _write_sources(self) -> None:
        (self.source_root / "images").mkdir()
        (self.source_root / "docs").mkdir()
        (self.source_root / "images" / "one.png").write_bytes(PNG_1X1)
        (self.source_root / "docs" / "ride.pdf").write_bytes(b"%PDF-1.4")

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
            conn.executemany(
                """
                INSERT INTO files VALUES (?, 'file', ?, ?, ?, ?, ?, ?, ?, '2026-07-29T00:00:00Z')
                """,
                [
                    ("images/one.png", "media_asset", ".png", "image/png", 25, "sha-one", "ok", "0644"),
                    ("docs/ride.pdf", "document", ".pdf", "application/pdf", 8, "sha-pdf", "ok", "0644"),
                    ("images/secret.jpg", "media_asset", ".jpg", "image/jpeg", 10, "sha-secret", "permission_denied", "0000"),
                ],
            )
            conn.commit()
        finally:
            conn.close()

    def _write_import_db(self) -> None:
        conn = sqlite3.connect(self.import_db)
        try:
            conn.execute(
                """
                CREATE TABLE media_references (
                  source_path TEXT,
                  referenced_url TEXT,
                  referenced_path TEXT,
                  attribute TEXT
                )
                """
            )
            conn.executemany(
                "INSERT INTO media_references VALUES (?, ?, ?, ?)",
                [
                    ("pages/index.html", "/images/one.png", "images/one.png", "src"),
                    ("pages/index.html", "missing.jpg", "", "src"),
                    ("pages/index.html", "https://cdn.example/remote.jpg", "", "src"),
                    ("pages/index.html", "/images/secret.jpg", "images/secret.jpg", "src"),
                ],
            )
            conn.commit()
        finally:
            conn.close()

    def _jsonl(self, filename: str) -> list[dict[str, object]]:
        path = self.output_dir / filename
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def test_manifest_reports_assets_missing_external_and_unreadable_media(self) -> None:
        config = media_asset_manifest.MediaManifestConfig(
            inventory_db=self.inventory_db,
            import_db=self.import_db,
            source_root=self.source_root,
            output_dir=self.output_dir,
            waivers=None,
            probe_dimensions=True,
        )

        media_asset_manifest.generate(config)

        manifest = self._jsonl("media-manifest.jsonl")
        self.assertEqual(2, len(manifest))
        png = next(item for item in manifest if item["source_path"] == "images/one.png")
        self.assertEqual("/legacy-media/images/one.png", png["public_url"])
        self.assertEqual(1, png["width"])
        self.assertEqual(1, png["height"])

        missing = self._jsonl("missing-media-references.jsonl")
        self.assertEqual({"images/secret.jpg", "pages/missing.jpg"}, {item["resolved_path"] for item in missing})
        secret = next(item for item in missing if item["resolved_path"] == "images/secret.jpg")
        self.assertEqual("unreadable", secret["reason"])

        self.assertEqual(1, len(self._jsonl("external-media-references.jsonl")))
        self.assertEqual(1, len(self._jsonl("unreadable-media.jsonl")))

        summary = json.loads((self.output_dir / "media-summary.json").read_text(encoding="utf-8"))
        self.assertEqual(2, summary["manifest_entries"])
        self.assertEqual(1, summary["resolved_media_references"])
        self.assertEqual(2, summary["missing_media_references"])


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Smoke tests for media root contract validation."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_MEDIA_ROOTS_PATH = REPO_ROOT / "scripts" / "check_media_roots.py"

spec = importlib.util.spec_from_file_location("check_media_roots", CHECK_MEDIA_ROOTS_PATH)
check_media_roots = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["check_media_roots"] = check_media_roots
spec.loader.exec_module(check_media_roots)


class CheckMediaRootsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.legacy_root = self.root / "legacy"
        self.cms_root = self.root / "cms"
        (self.legacy_root / "images").mkdir(parents=True)
        (self.cms_root / "legacy" / "legacy-asset").mkdir(parents=True)
        (self.legacy_root / "images" / "photo.jpg").write_bytes(b"jpg")
        (self.cms_root / "legacy" / "legacy-asset" / "photo.jpg").write_bytes(b"jpg")
        self.manifest = self.root / "media-manifest.jsonl"
        self.manifest.write_text(
            json.dumps(
                {
                    "asset_kind": "image",
                    "source_path": "images/photo.jpg",
                    "public_url": "/legacy-media/images/photo.jpg",
                    "cms_public_url": "/media/legacy-asset/photo.jpg",
                    "cms_storage_key": "legacy/legacy-asset/photo.jpg",
                }
            )
            + "\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_manifest_rows_validate_legacy_and_cms_paths(self) -> None:
        rows = check_media_roots.load_manifest_rows(self.manifest, 5)
        failures = check_media_roots.verify_manifest_rows(rows, self.legacy_root, self.cms_root, "/var/www/legacy-media", None)
        self.assertEqual([], failures)

    def test_missing_cms_file_fails_clearly(self) -> None:
        (self.cms_root / "legacy" / "legacy-asset" / "photo.jpg").unlink()
        rows = check_media_roots.load_manifest_rows(self.manifest, 5)
        failures = check_media_roots.verify_manifest_rows(rows, self.legacy_root, self.cms_root, "/var/www/legacy-media", None)
        self.assertEqual(1, len(failures))
        self.assertIn("cms media missing", failures[0])

    def test_container_symlink_targets_are_valid_cms_paths(self) -> None:
        (self.cms_root / "legacy" / "legacy-asset" / "photo.jpg").unlink()
        (self.cms_root / "legacy" / "legacy-asset" / "photo.jpg").symlink_to("/var/www/legacy-media/images/photo.jpg")
        rows = check_media_roots.load_manifest_rows(self.manifest, 5)
        failures = check_media_roots.verify_manifest_rows(rows, self.legacy_root, self.cms_root, "/var/www/legacy-media", None)
        self.assertEqual([], failures)

    def test_root_check_reports_missing_directory(self) -> None:
        ok, detail = check_media_roots.readable_directory(self.root / "missing")
        self.assertFalse(ok)
        self.assertEqual("missing", detail)


if __name__ == "__main__":
    unittest.main()

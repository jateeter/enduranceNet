#!/usr/bin/env python3
"""Smoke tests for the legacy import staging pipeline."""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LEGACY_IMPORT_PATH = REPO_ROOT / "scripts" / "legacy_import.py"

spec = importlib.util.spec_from_file_location("legacy_import", LEGACY_IMPORT_PATH)
legacy_import = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["legacy_import"] = legacy_import
spec.loader.exec_module(legacy_import)


FILE_COLUMNS = """
  path TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  classification TEXT NOT NULL,
  extension TEXT NOT NULL,
  size INTEGER,
  checksum_sha256 TEXT,
  status TEXT NOT NULL,
  mode_octal TEXT,
  scanned_at TEXT NOT NULL,
  mime_type TEXT
"""


class LegacyImportTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.source_root = self.root / "source"
        self.output_dir = self.root / "imports"
        self.inventory_db = self.root / "source-inventory.sqlite"
        self.source_root.mkdir()
        self._write_sources()
        self._write_inventory()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _write_file(self, relative_path: str, content: str) -> None:
        target = self.source_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def _write_sources(self) -> None:
        self._write_file(
            "CurrentNews/indexInternal.html",
            "<html><head><title>Current News</title></head><body><img src='/images/news.jpg'></body></html>",
        )
        self._write_file(
            "channels/news.xml",
            "<rss><channel><item><title>Feed Item</title><link>https://example.com/item</link></item></channel></rss>",
        )
        self._write_file(
            "channels/feeds.opml",
            "<opml><body><outline text='Ridecamp' xmlUrl='https://example.com/ridecamp.xml' /></body></opml>",
        )
        self._write_file("channels/transform.xsl", "<xsl:stylesheet xmlns:xsl='http://www.w3.org/1999/XSL/Transform' />")
        self._write_file("channels/bad.xml", "<rss><channel>")
        self._write_file(
            "advertisers/sponsor.html",
            "<html><head><title>Trail Sponsor</title></head><body><a href='https://sponsor.example'>Sponsor</a><img src='logo.jpg'></body></html>",
        )
        self._write_file(
            "classifieds/tack.html",
            "<html><head><title>Used Saddle</title></head><body><img src='saddle.jpg'></body></html>",
        )
        self._write_file(
            "ridecamp/archives/past/9801/msg00001.html",
            "<html><head><title>Ridecamp Message</title></head><body><a href='msg00000.html'>Prev</a><a href='msg00002.html'>Next</a></body></html>",
        )
        self._write_file(
            "gallery/index.html",
            "<html><head><title>Gallery</title></head><body><img src='one.jpg'><img src='two.jpg'></body></html>",
        )
        self._write_file("images/news.jpg", "fake image")

    def _insert_file(self, conn: sqlite3.Connection, relative_path: str, classification: str, mime_type: str = "") -> None:
        source_path = self.source_root / relative_path
        conn.execute(
            """
            INSERT INTO files (
              path, kind, classification, extension, size, checksum_sha256,
              status, mode_octal, scanned_at, mime_type
            ) VALUES (?, 'file', ?, ?, ?, ?, 'ok', '0644', '2026-07-29T00:00:00Z', ?)
            """,
            (
                relative_path,
                classification,
                source_path.suffix.lower(),
                source_path.stat().st_size,
                f"checksum-{relative_path}",
                mime_type,
            ),
        )

    def _write_inventory(self) -> None:
        conn = sqlite3.connect(self.inventory_db)
        try:
            conn.execute(f"CREATE TABLE files ({FILE_COLUMNS})")
            conn.execute("CREATE TABLE template_variables (source_path TEXT, variable_name TEXT, value_expression TEXT)")
            conn.execute("CREATE TABLE includes (source_path TEXT, resolved_path TEXT)")
            self._insert_file(conn, "CurrentNews/indexInternal.html", "executable_template", "text/html")
            self._insert_file(conn, "channels/news.xml", "data_file", "application/xml")
            self._insert_file(conn, "channels/feeds.opml", "data_file", "application/xml")
            self._insert_file(conn, "channels/transform.xsl", "data_file", "application/xml")
            self._insert_file(conn, "channels/bad.xml", "data_file", "application/xml")
            self._insert_file(conn, "advertisers/sponsor.html", "executable_template", "text/html")
            self._insert_file(conn, "classifieds/tack.html", "executable_template", "text/html")
            self._insert_file(conn, "ridecamp/archives/past/9801/msg00001.html", "executable_template", "text/html")
            self._insert_file(conn, "gallery/index.html", "executable_template", "text/html")
            self._insert_file(conn, "images/news.jpg", "media_asset", "image/jpeg")
            conn.execute(
                "INSERT INTO template_variables VALUES ('CurrentNews/indexInternal.html', 'pageTitle', 'Current News')"
            )
            conn.execute(
                "INSERT INTO includes VALUES ('CurrentNews/indexInternal.html', 'include/siteHeader.html')"
            )
            conn.commit()
        finally:
            conn.close()

    def _run_import(self, reset: bool = False) -> None:
        args = [
            "--inventory-db",
            str(self.inventory_db),
            "--source-root",
            str(self.source_root),
            "--output-dir",
            str(self.output_dir),
        ]
        if reset:
            args.append("--reset")
        self.assertEqual(0, legacy_import.main(args))

    def _count(self, table: str) -> int:
        with sqlite3.connect(self.output_dir / "legacy-import.sqlite") as conn:
            return int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])

    def test_importer_creates_versioned_idempotent_domain_staging_records(self) -> None:
        self._run_import(reset=True)
        first_batch_count = self._count("import_batches")
        self._run_import()

        self.assertEqual(first_batch_count + 1, self._count("import_batches"))
        self.assertEqual(10, self._count("legacy_source_files"))
        self.assertEqual(1, self._count("media_assets"))
        self.assertEqual(2, self._count("feed_entries"))
        self.assertEqual(3, self._count("structured_data_files"))
        self.assertEqual(1, self._count("advertiser_records"))
        self.assertEqual(1, self._count("classified_records"))
        self.assertEqual(1, self._count("ridecamp_messages"))
        self.assertEqual(1, self._count("gallery_manifests"))

        with sqlite3.connect(self.output_dir / "legacy-import.sqlite") as conn:
            parser_version = conn.execute(
                "SELECT parser_version FROM legacy_source_files WHERE source_path = 'CurrentNews/indexInternal.html'"
            ).fetchone()[0]
            failures = conn.execute(
                "SELECT COUNT(*) FROM import_failures WHERE source_path = 'channels/bad.xml'"
            ).fetchone()[0]

        self.assertEqual(legacy_import.PARSER_VERSION, parser_version)
        self.assertEqual(2, failures)


if __name__ == "__main__":
    unittest.main()

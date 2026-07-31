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
POLL_WORKER_PATH = REPO_ROOT / "scripts" / "poll_active_streams.py"

spec = importlib.util.spec_from_file_location("legacy_import", LEGACY_IMPORT_PATH)
legacy_import = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["legacy_import"] = legacy_import
spec.loader.exec_module(legacy_import)

poll_spec = importlib.util.spec_from_file_location("poll_active_streams", POLL_WORKER_PATH)
poll_active_streams = importlib.util.module_from_spec(poll_spec)
assert poll_spec.loader is not None
sys.modules["poll_active_streams"] = poll_active_streams
poll_spec.loader.exec_module(poll_active_streams)


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
            "channels/whereintheworld/atom.xml",
            """
            <feed xmlns='http://www.w3.org/2005/Atom'>
              <id>tag:blogger.com,1999:blog-7290526037745122441</id>
              <title>Where in the World</title>
              <generator>Blogger</generator>
              <link rel='self' href='http://www.blogger.com/feeds/7290526037745122441/posts/default' />
              <link rel='alternate' href='http://feeds.endurance.net/whereintheworld/' />
              <link rel='next' href='http://www.blogger.com/feeds/7290526037745122441/posts/default?start-index=26' />
              <entry>
                <id>tag:blogger.com,1999:blog-7290526037745122441.post-123</id>
                <title>Travel Dispatch</title>
                <published>2026-07-29T00:00:00Z</published>
                <updated>2026-07-30T00:00:00Z</updated>
                <author><name>Steph Teeter</name></author>
                <content type='html'>&lt;p&gt;A first paragraph with an image.&lt;/p&gt;&lt;img src='http://www.endurance.net/images/news.jpg' /&gt;&lt;a href='http://feeds.endurance.net/docs/missing.pdf'&gt;PDF&lt;/a&gt;</content>
                <link rel='alternate' href='http://feeds.endurance.net/whereintheworld/travel-dispatch.html' />
                <link rel='self' href='http://www.blogger.com/feeds/7290526037745122441/posts/default/123' />
                <link rel='replies' href='http://www.blogger.com/comment.g?blogID=7290526037745122441&amp;postID=123' />
              </entry>
            </feed>
            """,
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
            self._insert_file(conn, "channels/whereintheworld/atom.xml", "data_file", "application/xml")
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
        self.assertEqual(11, self._count("legacy_source_files"))
        self.assertEqual(1, self._count("media_assets"))
        self.assertEqual(2, self._count("stream_media_references"))
        self.assertEqual(3, self._count("feed_entries"))
        self.assertEqual(4, self._count("stream_sources"))
        self.assertEqual(4, self._count("stream_snapshots"))
        self.assertEqual(4, self._count("stream_raw_snapshots"))
        self.assertEqual(4, self._count("stream_poll_targets"))
        self.assertEqual(3, self._count("stream_entries_v2"))
        self.assertEqual(4, self._count("structured_data_files"))
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
            stream_source = conn.execute(
                """
                SELECT provider, feed_format, remote_url, default_presentation
                FROM stream_sources
                WHERE source_path = 'channels/whereintheworld/atom.xml'
                """
            ).fetchone()
            stream_entry = conn.execute(
                """
                SELECT provider_entry_id, author, alternate_url, self_url, comments_url
                FROM stream_entries_v2
                WHERE source_path = 'channels/whereintheworld/atom.xml'
                """
            ).fetchone()
            poll_target = conn.execute(
                """
                SELECT poll_url, next_url, poll_status, blocker
                FROM stream_poll_targets
                WHERE source_path = 'channels/whereintheworld/atom.xml'
                """
            ).fetchone()
            blocked_target = conn.execute(
                """
                SELECT poll_status, blocker
                FROM stream_poll_targets
                WHERE source_path = 'channels/news.xml'
                """
            ).fetchone()
            raw_snapshot = conn.execute(
                """
                SELECT source_kind, http_status, etag, last_modified, raw_text
                FROM stream_raw_snapshots
                WHERE source_path = 'channels/whereintheworld/atom.xml'
                """
            ).fetchone()
            stream_media = conn.execute(
                """
                SELECT referenced_url, normalized_url, referenced_path, media_kind, blocker, cms_asset_id
                FROM stream_media_references
                WHERE source_path = 'channels/whereintheworld/atom.xml'
                ORDER BY referenced_url
                """
            ).fetchall()

        self.assertEqual(legacy_import.PARSER_VERSION, parser_version)
        self.assertEqual(2, failures)
        self.assertEqual(("blogger", "atom-1.0", "http://www.blogger.com/feeds/7290526037745122441/posts/default", "popup-channel-card"), stream_source)
        self.assertEqual(
            (
                "tag:blogger.com,1999:blog-7290526037745122441.post-123",
                "Steph Teeter",
                "http://feeds.endurance.net/whereintheworld/travel-dispatch.html",
                "http://www.blogger.com/feeds/7290526037745122441/posts/default/123",
                "http://www.blogger.com/comment.g?blogID=7290526037745122441&postID=123",
            ),
            stream_entry,
        )
        self.assertEqual(
            (
                "https://www.blogger.com/feeds/7290526037745122441/posts/default?alt=rss",
                "http://www.blogger.com/feeds/7290526037745122441/posts/default?start-index=26",
                "ready",
                None,
            ),
            poll_target,
        )
        self.assertEqual(("blocked", "no remote poll URL discovered from local feed snapshot"), blocked_target)
        self.assertEqual("local-cache", raw_snapshot[0])
        self.assertIsNone(raw_snapshot[1])
        self.assertIsNone(raw_snapshot[2])
        self.assertIsNone(raw_snapshot[3])
        self.assertIn("Where in the World", raw_snapshot[4])
        self.assertEqual(
            [
                (
                    "http://feeds.endurance.net/docs/missing.pdf",
                    "/legacy-media/docs/missing.pdf",
                    "docs/missing.pdf",
                    "document",
                    "unresolved legacy media path",
                    None,
                ),
                (
                    "http://www.endurance.net/images/news.jpg",
                    "/legacy-media/images/news.jpg",
                    "images/news.jpg",
                    "image",
                    None,
                    None,
                ),
            ],
            stream_media,
        )

    def test_active_stream_polling_is_idempotent_and_updates_snapshot_metadata(self) -> None:
        self._run_import(reset=True)

        polled_body = """
        <feed xmlns='http://www.w3.org/2005/Atom'>
          <id>tag:blogger.com,1999:blog-7290526037745122441</id>
          <title>Where in the World</title>
          <generator>Blogger</generator>
          <link rel='self' href='https://www.blogger.com/feeds/7290526037745122441/posts/default?alt=rss' />
          <entry>
            <id>tag:blogger.com,1999:blog-7290526037745122441.post-123</id>
            <title>Travel Dispatch Updated</title>
            <updated>2026-07-31T00:00:00Z</updated>
            <link rel='alternate' href='http://feeds.endurance.net/whereintheworld/travel-dispatch.html' />
          </entry>
        </feed>
        """
        fetched: list[tuple[str, object, object]] = []

        def fake_fetcher(url: str, etag: object = None, last_modified: object = None) -> object:
            fetched.append((url, etag, last_modified))
            return legacy_import.FetchResult(
                url=url,
                status=200,
                body=polled_body,
                etag='"poll-etag"',
                last_modified="Fri, 31 Jul 2026 00:00:00 GMT",
            )

        with sqlite3.connect(self.output_dir / "legacy-import.sqlite") as conn:
            batch_id = conn.execute("SELECT id FROM import_batches ORDER BY started_at DESC LIMIT 1").fetchone()[0]
            self.assertEqual(1, legacy_import.poll_active_streams(conn, batch_id, fake_fetcher))
            self.assertEqual(1, legacy_import.poll_active_streams(conn, batch_id, fake_fetcher))
            conn.commit()

            stream_entry_count = conn.execute(
                "SELECT COUNT(*) FROM stream_entries_v2 WHERE source_path = 'channels/whereintheworld/atom.xml'"
            ).fetchone()[0]
            raw_snapshot_count = conn.execute(
                "SELECT COUNT(*) FROM stream_raw_snapshots WHERE source_path = 'channels/whereintheworld/atom.xml'"
            ).fetchone()[0]
            poll_target = conn.execute(
                """
                SELECT poll_status, blocker, etag, last_modified, last_checksum_sha256
                FROM stream_poll_targets
                WHERE source_path = 'channels/whereintheworld/atom.xml'
                """
            ).fetchone()

        self.assertEqual(2, len(fetched))
        self.assertEqual(
            "https://www.blogger.com/feeds/7290526037745122441/posts/default?alt=rss",
            fetched[0][0],
        )
        self.assertEqual(1, stream_entry_count)
        self.assertEqual(2, raw_snapshot_count)
        self.assertEqual("ready", poll_target[0])
        self.assertIsNone(poll_target[1])
        self.assertEqual('"poll-etag"', poll_target[2])
        self.assertEqual("Fri, 31 Jul 2026 00:00:00 GMT", poll_target[3])
        self.assertIsNotNone(poll_target[4])

    def test_scheduled_poll_worker_writes_operator_report(self) -> None:
        self._run_import(reset=True)

        polled_body = """
        <feed xmlns='http://www.w3.org/2005/Atom'>
          <id>tag:blogger.com,1999:blog-7290526037745122441</id>
          <title>Where in the World</title>
          <generator>Blogger</generator>
          <link rel='self' href='https://www.blogger.com/feeds/7290526037745122441/posts/default?alt=rss' />
          <entry>
            <id>tag:blogger.com,1999:blog-7290526037745122441.post-456</id>
            <title>Scheduled Poll Dispatch</title>
            <updated>2026-07-31T01:00:00Z</updated>
            <link rel='alternate' href='http://feeds.endurance.net/whereintheworld/scheduled.html' />
          </entry>
        </feed>
        """

        def fake_fetcher(url: str, etag: object = None, last_modified: object = None) -> object:
            return legacy_import.FetchResult(
                url=url,
                status=200,
                body=polled_body,
                etag='"worker-etag"',
                last_modified="Fri, 31 Jul 2026 01:00:00 GMT",
            )

        config = poll_active_streams.PollWorkerConfig(
            staging_db=self.output_dir / "legacy-import.sqlite",
            output_dir=self.output_dir,
            fail_on_target_errors=True,
        )
        report = poll_active_streams.run_poll(config, fake_fetcher)

        self.assertEqual(1, report["ready_targets_before"])
        self.assertEqual(0, report["failures"])
        self.assertEqual(1, report["imported_entries"])
        self.assertEqual(1, report["raw_snapshots_added"])
        self.assertEqual(1, len(report["remote_snapshots"]))
        self.assertEqual(200, report["remote_snapshots"][0]["http_status"])
        self.assertTrue((self.output_dir / "stream-poll-report.json").exists())
        self.assertEqual("", (self.output_dir / "stream-poll-failures.jsonl").read_text(encoding="utf-8"))

    def test_scheduled_poll_worker_reports_failed_targets(self) -> None:
        self._run_import(reset=True)

        def failing_fetcher(url: str, etag: object = None, last_modified: object = None) -> object:
            raise RuntimeError("feed unavailable")

        config = poll_active_streams.PollWorkerConfig(
            staging_db=self.output_dir / "legacy-import.sqlite",
            output_dir=self.output_dir,
            fail_on_target_errors=True,
        )
        report = poll_active_streams.run_poll(config, failing_fetcher)

        self.assertEqual(1, report["failures"])
        self.assertEqual(report["blocked_targets_before"] + 1, report["blocked_targets_after"])
        self.assertIn("RuntimeError: feed unavailable", report["target_statuses"][0]["blocker"])
        failures = (self.output_dir / "stream-poll-failures.jsonl").read_text(encoding="utf-8")
        self.assertIn("feed unavailable", failures)


if __name__ == "__main__":
    unittest.main()

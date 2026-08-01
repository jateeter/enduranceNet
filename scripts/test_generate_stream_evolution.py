#!/usr/bin/env python3
"""Unit tests for stream evolution generation."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

import generate_stream_evolution


class GenerateStreamEvolutionTest(unittest.TestCase):
    def test_generates_presentation_ready_seed_sql(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "legacy-import.sqlite"
            output_path = Path(tmp) / "11.sql"
            with sqlite3.connect(db_path) as conn:
                conn.executescript(
                    """
                    CREATE TABLE stream_sources (
                      source_path TEXT PRIMARY KEY,
                      title TEXT,
                      provider TEXT,
                      feed_format TEXT,
                      remote_url TEXT,
                      local_cache_path TEXT,
                      legacy_url TEXT,
                      default_presentation TEXT,
                      active INTEGER,
                      checksum_sha256 TEXT,
                      import_batch_id TEXT,
                      parser_version TEXT
                    );
                    CREATE TABLE stream_snapshots (
                      source_path TEXT PRIMARY KEY,
                      self_url TEXT,
                      alternate_url TEXT,
                      next_url TEXT
                    );
                    CREATE TABLE stream_poll_targets (
                      source_path TEXT PRIMARY KEY,
                      poll_url TEXT,
                      poll_status TEXT,
                      blocker TEXT
                    );
                    CREATE TABLE stream_entries_v2 (
                      source_path TEXT,
                      provider_entry_id TEXT,
                      entry_index INTEGER,
                      title TEXT,
                      summary_html TEXT,
                      content_html TEXT,
                      author TEXT,
                      published_at TEXT,
                      updated_at TEXT,
                      alternate_url TEXT,
                      self_url TEXT,
                      related_url TEXT,
                      comments_url TEXT
                    );
                    """
                )
                conn.execute(
                    """
                    INSERT INTO stream_sources VALUES (
                      'channels/news.xml', 'Endurance.Net: World News',
                      'blogger', 'atom-1.0',
                      'http://www.blogger.com/feeds/5099696/posts/default',
                      'channels/news.xml', 'http://news.endurance.net/',
                      'atom-list', 1, 'abc', 'batch', 'parser'
                    )
                    """
                )
                conn.execute(
                    "INSERT INTO stream_snapshots VALUES ('channels/news.xml', 'http://www.blogger.com/feeds/5099696/posts/default', 'http://news.endurance.net/', NULL)"
                )
                conn.execute(
                    "INSERT INTO stream_poll_targets VALUES ('channels/news.xml', 'https://www.blogger.com/feeds/5099696/posts/default?alt=rss', 'ready', NULL)"
                )
                conn.execute(
                    """
                    INSERT INTO stream_entries_v2 VALUES (
                      'channels/news.xml', 'tag:blogger.com,1999:blog-5099696.post-1',
                      0, 'A current headline', '<p>Summary&nbsp;</p>', '<p>Body;</p>',
                      'Endurance.Net', '2026-08-01T08:00:00-07:00',
                      '2026-08-01T08:10:00-07:00',
                      'http://news.endurance.net/item.html',
                      'https://www.blogger.com/feeds/5099696/posts/default/1',
                      NULL, NULL
                    )
                    """
                )
                conn.commit()

            source_count, entry_count = generate_stream_evolution.generate(db_path, output_path)
            sql = output_path.read_text(encoding="utf-8")

            self.assertEqual(1, source_count)
            self.assertEqual(1, entry_count)
            self.assertIn("INSERT INTO stream_sources", sql)
            self.assertIn("'rss-list'", sql)
            self.assertIn("'Active News'", sql)
            self.assertIn("https://www.blogger.com/feeds/5099696/posts/default?alt=rss", sql)
            self.assertIn("INSERT INTO stream_entries", sql)
            self.assertNotIn("&nbsp;", sql)


if __name__ == "__main__":
    unittest.main()

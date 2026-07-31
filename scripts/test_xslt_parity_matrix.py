#!/usr/bin/env python3
"""Smoke tests for the XSLT parity matrix generator."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = REPO_ROOT / "scripts" / "xslt_parity_matrix.py"

spec = importlib.util.spec_from_file_location("xslt_parity_matrix", MATRIX_PATH)
xslt_parity_matrix = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["xslt_parity_matrix"] = xslt_parity_matrix
spec.loader.exec_module(xslt_parity_matrix)


class XsltParityMatrixTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.source_root = self.root / "legacy"
        self.output_path = self.root / "matrix.json"
        self.source_root.mkdir()
        self._write_sources()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _write_file(self, relative_path: str, content: str) -> None:
        target = self.source_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def _write_sources(self) -> None:
        self._write_file(
            "channels/xslTemplates/atomlist_popup.xsl",
            """
            <xsl:stylesheet xmlns:xsl='http://www.w3.org/1999/XSL/Transform'
              xmlns:atom='http://www.w3.org/2005/Atom'>
              <xsl:output method='html' encoding='ISO-8859-1' />
              <xsl:variable name='displayCount'>8</xsl:variable>
              <xsl:template match='/'>
                <img src='/channels/news/bulletImage.gif' />
                <a onmouseover="overlay(this, 'content', 'leftbottom')">
                  <xsl:value-of select='atom:feed/atom:title' />
                </a>
              </xsl:template>
            </xsl:stylesheet>
            """,
        )
        self._write_file(
            "channels/xslTemplates/rssList.xsl",
            """
            <xsl:stylesheet xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>
              <xsl:template match='/rss/channel'>
                <xsl:for-each select='item'><xsl:value-of select='title' /></xsl:for-each>
              </xsl:template>
            </xsl:stylesheet>
            """,
        )
        self._write_file(
            "channels/xslTemplates/atomList.xsl",
            """
            <xsl:stylesheet xmlns:xsl='http://www.w3.org/1999/XSL/Transform'
              xmlns:atom='http://www.w3.org/2005/Atom'>
              <xsl:template match='/atom:feed'>
                <xsl:for-each select='atom:entry'><xsl:value-of select='atom:title' /></xsl:for-each>
              </xsl:template>
            </xsl:stylesheet>
            """,
        )
        self._write_file(
            "channels/xslTemplates/singleEntry.xsl",
            """
            <xsl:stylesheet xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>
              <xsl:template match='/'>
                <xsl:value-of select='content' disable-output-escaping='yes' />
              </xsl:template>
            </xsl:stylesheet>
            """,
        )
        self._write_file(
            "2006WEC/EventStoryInternal.xsl",
            """
            <xsl:stylesheet xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>
              <xsl:template match='/'>EventStoryInternal route</xsl:template>
            </xsl:stylesheet>
            """,
        )
        self._write_file(
            "tevis/googleReaderFrontpage.xsl",
            """
            <xsl:stylesheet xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>
              <xsl:template match='/'>Google Reader compatibility</xsl:template>
            </xsl:stylesheet>
            """,
        )

    def test_matrix_classifies_legacy_presentation_modes(self) -> None:
        result = xslt_parity_matrix.main([
            "--source-root",
            str(self.source_root),
            "--output",
            str(self.output_path),
        ])

        self.assertEqual(0, result)
        matrix = json.loads(self.output_path.read_text(encoding="utf-8"))
        modes = {record["sourcePath"]: record["presentationMode"] for record in matrix["transforms"]}
        popup = next(record for record in matrix["transforms"] if record["sourcePath"].endswith("atomlist_popup.xsl"))

        self.assertEqual(6, matrix["recordCount"])
        self.assertEqual([], matrix["fixtureCoverage"]["missing"])
        self.assertEqual(
            [
                "atom-list",
                "event-story-list",
                "google-reader-frontpage",
                "popup-list",
                "rss-list",
                "single-entry",
            ],
            matrix["fixtureCoverage"]["covered"],
        )
        self.assertEqual("atom-list", modes["channels/xslTemplates/atomList.xsl"])
        self.assertEqual("single-entry-html", modes["channels/xslTemplates/singleEntry.xsl"])
        self.assertEqual("event-story-list", modes["2006WEC/EventStoryInternal.xsl"])
        self.assertEqual("google-reader-frontpage", modes["tevis/googleReaderFrontpage.xsl"])
        self.assertEqual("popup-channel-card", modes["channels/xslTemplates/atomlist_popup.xsl"])
        self.assertEqual("rss-list", modes["channels/xslTemplates/rssList.xsl"])
        self.assertEqual("popup-list", popup["fixtureRole"])
        self.assertEqual("migrated", popup["migrationStatus"])
        self.assertIn("display_limit", popup["parityChecks"])
        self.assertIn("popup_preview", popup["parityChecks"])
        self.assertTrue(popup["flags"]["uses_popup_overlay"])
        self.assertTrue(popup["flags"]["uses_bullet_images"])
        self.assertEqual(["displayCount"], popup["variables"])


if __name__ == "__main__":
    unittest.main()

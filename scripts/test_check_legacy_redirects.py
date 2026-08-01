#!/usr/bin/env python3
"""Unit checks for the legacy redirect checker."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_legacy_redirects.py"

spec = importlib.util.spec_from_file_location("check_legacy_redirects", SCRIPT_PATH)
check_legacy_redirects = importlib.util.module_from_spec(spec)
sys.modules["check_legacy_redirects"] = check_legacy_redirects
assert spec.loader is not None
spec.loader.exec_module(check_legacy_redirects)


class LegacyRedirectCheckerTest(unittest.TestCase):
    def test_normalize_same_origin_absolute_location(self) -> None:
        location = check_legacy_redirects.normalize_location("http://localhost/news", "http://localhost")

        self.assertEqual("/news", location)

    def test_normalize_preserves_hash_and_query(self) -> None:
        location = check_legacy_redirects.normalize_location(
            "http://localhost/community?tab=old#ridecamp",
            "http://localhost",
        )

        self.assertEqual("/community?tab=old#ridecamp", location)

    def test_normalize_keeps_relative_location(self) -> None:
        location = check_legacy_redirects.normalize_location("/galleries/sample", "http://localhost")

        self.assertEqual("/galleries/sample", location)

    def test_normalize_keeps_external_location(self) -> None:
        location = check_legacy_redirects.normalize_location(
            "https://legacy.example.org/news",
            "http://localhost",
        )

        self.assertEqual("https://legacy.example.org/news", location)

    def test_normalize_missing_location(self) -> None:
        location = check_legacy_redirects.normalize_location(None, "http://localhost")

        self.assertEqual("", location)


if __name__ == "__main__":
    unittest.main()

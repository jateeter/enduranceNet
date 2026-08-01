#!/usr/bin/env python3
"""Validate runtime media roots and representative media URL mappings."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


DEFAULT_LEGACY_ROOT = "/Volumes/webstore/endurance.net"
DEFAULT_CMS_ROOT = "migration/media/images"
DEFAULT_CONTAINER_LEGACY_ROOT = "/var/www/legacy-media"
USER_AGENT = "endurancenet-media-root-check/1.0"


def readable_directory(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, "missing"
    if not path.is_dir():
        return False, "not_a_directory"
    try:
        next(path.iterdir(), None)
    except OSError as exc:
        return False, f"unreadable: {exc}"
    return True, "ok"


def load_manifest_rows(path: Path, sample_size: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("asset_kind") != "image":
                continue
            rows.append(row)
            if len(rows) >= sample_size:
                break
    return rows


def url_available(url: str) -> tuple[bool, str]:
    request = Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=15) as response:
            return 200 <= response.status < 400, str(response.status)
    except HTTPError as exc:
        if exc.code in {403, 405}:
            get_request = Request(url, method="GET", headers={"User-Agent": USER_AGENT, "Range": "bytes=0-0"})
            try:
                with urlopen(get_request, timeout=15) as response:
                    return 200 <= response.status < 400, str(response.status)
            except HTTPError as get_exc:
                return False, str(get_exc.code)
        return False, str(exc.code)
    except URLError as exc:
        return False, str(exc.reason)


def verify_manifest_rows(
    rows: list[dict[str, object]],
    legacy_root: Path,
    cms_root: Path,
    container_legacy_root: str,
    base_url: str | None,
) -> list[str]:
    failures: list[str] = []
    for row in rows:
        source_path = str(row.get("source_path") or "")
        storage_key = str(row.get("cms_storage_key") or "")
        public_url = str(row.get("public_url") or "")
        cms_public_url = str(row.get("cms_public_url") or "")
        if not source_path:
            failures.append("manifest row is missing source_path")
        elif not (legacy_root / source_path).is_file():
            failures.append(f"legacy source missing: {legacy_root / source_path}")
        if not storage_key:
            failures.append(f"{source_path}: manifest row is missing cms_storage_key")
        elif not (cms_root / storage_key).is_file():
            staged = cms_root / storage_key
            if not staged.is_symlink() or not os.readlink(staged).startswith(container_legacy_root.rstrip("/") + "/"):
                failures.append(f"cms media missing: {staged}")
        if base_url:
            for label, media_url in [("legacy", public_url), ("cms", cms_public_url)]:
                if not media_url:
                    failures.append(f"{source_path}: missing {label} public URL")
                    continue
                ok, detail = url_available(urljoin(base_url.rstrip("/") + "/", media_url.lstrip("/")))
                if not ok:
                    failures.append(f"{label} URL unavailable for {source_path}: {media_url} ({detail})")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy-root", default=os.environ.get("LEGACY_MEDIA_ROOT", DEFAULT_LEGACY_ROOT))
    parser.add_argument("--cms-root", default=os.environ.get("CMS_MEDIA_ROOT", DEFAULT_CMS_ROOT))
    parser.add_argument("--manifest", help="Optional media-manifest.jsonl used to verify representative image files.")
    parser.add_argument("--sample-size", type=int, default=5, help="Number of image manifest rows to verify.")
    parser.add_argument(
        "--container-legacy-root",
        default=DEFAULT_CONTAINER_LEGACY_ROOT,
        help="Container path allowed for CMS media symlink targets.",
    )
    parser.add_argument("--base-url", help="Optional running app base URL used to verify public media URLs.")
    args = parser.parse_args()

    if args.sample_size < 1:
        parser.error("--sample-size must be greater than zero")

    legacy_root = Path(args.legacy_root).expanduser().resolve()
    cms_root = Path(args.cms_root).expanduser().resolve()
    failures: list[str] = []
    for label, root in [("LEGACY_MEDIA_ROOT", legacy_root), ("CMS_MEDIA_ROOT", cms_root)]:
        ok, detail = readable_directory(root)
        if not ok:
            failures.append(f"{label} invalid ({detail}): {root}")

    rows: list[dict[str, object]] = []
    if args.manifest:
        try:
            rows = load_manifest_rows(Path(args.manifest).expanduser().resolve(), args.sample_size)
        except (FileNotFoundError, OSError, json.JSONDecodeError) as exc:
            failures.append(f"manifest invalid: {exc}")
        if not rows:
            failures.append(f"manifest has no image rows: {args.manifest}")

    if rows and not failures:
        failures.extend(verify_manifest_rows(rows, legacy_root, cms_root, args.container_legacy_root, args.base_url))

    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1

    if rows:
        print(f"media root checks passed ({len(rows)} manifest image rows)")
    else:
        print("media root checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

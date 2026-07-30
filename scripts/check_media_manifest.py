#!/usr/bin/env python3
"""Check manifested homepage media URLs from the Scala API."""

from __future__ import annotations

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


LEGACY_ASSET_BASE = "http://www.endurance.net"


def absolute_media_url(url: str) -> str:
    if url.startswith(("http://", "https://", "data:")):
        return url
    return urljoin(LEGACY_ASSET_BASE + "/", url.lstrip("/"))


def fetch_json(url: str) -> list[dict[str, object]]:
    req = Request(url, headers={"User-Agent": "endurancenet-media-check/1.0"})
    with urlopen(req, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def media_available(url: str) -> tuple[bool, str]:
    req = Request(url, method="HEAD", headers={"User-Agent": "endurancenet-media-check/1.0"})
    try:
        with urlopen(req, timeout=15) as response:
            return 200 <= response.status < 400, str(response.status)
    except HTTPError as exc:
        if exc.code in {403, 405}:
            get_req = Request(url, method="GET", headers={"User-Agent": "endurancenet-media-check/1.0", "Range": "bytes=0-0"})
            try:
                with urlopen(get_req, timeout=15) as response:
                    return 200 <= response.status < 400, str(response.status)
            except HTTPError as get_exc:
                return False, str(get_exc.code)
        return False, str(exc.code)
    except URLError as exc:
        return False, str(exc.reason)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-base-url", required=True, help="Backend/API base URL, for example http://localhost:9000.")
    args = parser.parse_args()

    endpoint = urljoin(args.api_base_url.rstrip("/") + "/", "api/homepage-assets")
    try:
        assets = fetch_json(endpoint)
    except Exception as exc:
        print(f"FAIL unable to load homepage assets from {endpoint}: {exc}", file=sys.stderr)
        return 1

    failures: list[str] = []
    checked = 0
    for asset in assets:
        image_url = asset.get("imageUrl")
        title = asset.get("title", "[untitled]")
        if not isinstance(image_url, str) or image_url.startswith("data:"):
            continue
        checked += 1
        absolute_url = absolute_media_url(image_url)
        ok, detail = media_available(absolute_url)
        if not ok:
            failures.append(f"{title}: {absolute_url} unavailable ({detail})")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1

    print(f"media manifest checks passed ({checked} URLs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

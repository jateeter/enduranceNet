#!/usr/bin/env python3
"""Check representative legacy URL redirects against a running deployment."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


@dataclass(frozen=True)
class LegacyCheck:
    path: str
    target: str
    status: int = 301


CHECKS = [
    LegacyCheck("/index.html", "/"),
    LegacyCheck("/index_content.html", "/"),
    LegacyCheck("/CurrentNews/", "/news"),
    LegacyCheck("/CurrentNews/index.html", "/news"),
    LegacyCheck("/CurrentNews/indexInternal.html", "/news"),
    LegacyCheck("/FeaturedStories/", "/featured-stories"),
    LegacyCheck("/FeaturedStories/index.html", "/featured-stories"),
    LegacyCheck("/FeaturedStories/indexInternal.html", "/featured-stories"),
    LegacyCheck("/newsblogs/", "/news"),
    LegacyCheck("/newsblogs/index.html", "/news"),
    LegacyCheck("/events/", "/events"),
    LegacyCheck("/events/index.html", "/events"),
    LegacyCheck("/ClassifiedAds/", "/community#classifieds"),
    LegacyCheck("/ClassifiedAds/index.html", "/community#classifieds"),
    LegacyCheck("/RidecampFriend/", "/community#ridecamp"),
    LegacyCheck("/RidecampFriend/index.html", "/community#ridecamp"),
    LegacyCheck("/2005PAC/Gallery/AsadorsS/", "/galleries/2005pac-gallery-asadorss"),
    LegacyCheck("/2005PAC/Gallery/AsadorsS/ThumbnailFrame.html", "/galleries/2005pac-gallery-asadorss"),
    LegacyCheck("/2005PAC/Gallery/AsadorsS/index.html", "/galleries/2005pac-gallery-asadorss"),
    LegacyCheck("/2005PAC/Gallery/AsadorsS/pages/IMG_0005.html", "/galleries/2005pac-gallery-asadorss"),
    LegacyCheck("/gallery/Nov4_WelcomeReception/", "/galleries/gallery-nov4-welcomereception"),
    LegacyCheck("/gallery/Nov4_WelcomeReception/index.html", "/galleries/gallery-nov4-welcomereception"),
    LegacyCheck("/gallery/Nov4_WelcomeReception/index_2.html", "/galleries/gallery-nov4-welcomereception"),
    LegacyCheck("/gallery/Nov4_WelcomeReception/pages/IMG_6570.html", "/galleries/gallery-nov4-welcomereception"),
]


class NoRedirect(HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        return fp

    http_error_302 = http_error_301
    http_error_303 = http_error_301
    http_error_307 = http_error_301
    http_error_308 = http_error_301


def request(url: str) -> tuple[int, str | None, bytes]:
    opener = build_opener(NoRedirect)
    req = Request(url, method="GET", headers={"User-Agent": "endurancenet-redirect-check/1.0"})
    try:
        with opener.open(req, timeout=10) as response:
            return response.status, response.headers.get("Location"), response.read()
    except HTTPError as exc:
        return exc.code, exc.headers.get("Location"), exc.read()


def normalize_location(location: str | None, base_url: str) -> str:
    if not location:
        return ""
    parsed_location = urlparse(location)
    if not parsed_location.scheme and not parsed_location.netloc:
        return location

    parsed_base = urlparse(base_url)
    if (
        parsed_location.scheme == parsed_base.scheme
        and parsed_location.netloc == parsed_base.netloc
    ):
        normalized = parsed_location.path or "/"
        if parsed_location.query:
            normalized = f"{normalized}?{parsed_location.query}"
        if parsed_location.fragment:
            normalized = f"{normalized}#{parsed_location.fragment}"
        return normalized
    return location


def check_redirects(base_url: str) -> list[str]:
    failures: list[str] = []
    for check in CHECKS:
        url = urljoin(base_url.rstrip("/") + "/", check.path.lstrip("/"))
        try:
            status, location, _ = request(url)
        except URLError as exc:
            failures.append(f"{check.path}: request failed: {exc.reason}")
            continue

        if status != check.status:
            failures.append(f"{check.path}: expected {check.status}, got {status}")
            continue
        normalized_location = normalize_location(location, base_url)
        if normalized_location != check.target:
            failures.append(f"{check.path}: expected Location {check.target!r}, got {location!r}")
    return failures


def check_resolver(api_base_url: str) -> list[str]:
    failures: list[str] = []
    for check in CHECKS:
        url = urljoin(
            api_base_url.rstrip("/") + "/",
            f"api/legacy-redirects/resolve?url={quote(check.path)}",
        )
        try:
            status, _, body = request(url)
        except URLError as exc:
            failures.append(f"resolver {check.path}: request failed: {exc.reason}")
            continue

        if status != 200:
            failures.append(f"resolver {check.path}: expected 200, got {status}")
            continue
        payload = json.loads(body.decode("utf-8"))
        if payload.get("targetUrl") != check.target or payload.get("statusCode") != check.status:
            failures.append(f"resolver {check.path}: unexpected payload {payload}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", help="Deployment/frontend URL to check for HTTP redirects.")
    parser.add_argument("--api-base-url", help="Backend/API URL to check the Scala redirect resolver.")
    args = parser.parse_args()

    if not args.base_url and not args.api_base_url:
        parser.error("at least one of --base-url or --api-base-url is required")

    failures: list[str] = []
    if args.base_url:
        failures.extend(check_redirects(args.base_url))
    if args.api_base_url:
        failures.extend(check_resolver(args.api_base_url))

    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1

    print("legacy redirect checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

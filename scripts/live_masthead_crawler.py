#!/usr/bin/env python3
"""Crawl the live Endurance.Net site for masthead and event banner assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import time
from collections import deque
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_START_URL = "http://www.endurance.net/"
ALLOWED_HOSTS = {"endurance.net", "www.endurance.net"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
STATIC_EXTENSIONS = IMAGE_EXTENSIONS | {
    ".css",
    ".js",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".zip",
    ".mp3",
    ".mp4",
    ".mov",
}
MASTHEAD_RE = re.compile(r"(?:^|/)(?:en)?banner(?:_|-)?(?:sm|small)?|masthead|siteheader", re.I)
EVENT_BANNER_RE = re.compile(r"(?:^|/)banner(?:_block)?\.(?:jpe?g|png|gif|webp)$", re.I)
CSS_URL_RE = re.compile(r"url\(([^)]+)\)", re.I)


@dataclass(frozen=True)
class Candidate:
    url: str
    source_page: str
    kind: str
    reason: str


class LinkExtractor(HTMLParser):
    def __init__(self, page_url: str) -> None:
        super().__init__()
        self.page_url = page_url
        self.page_links: set[str] = set()
        self.asset_links: list[str] = []
        self.stylesheet_links: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {name.lower(): value for name, value in attrs if value}
        if tag == "a" and attr.get("href"):
            self.page_links.add(urljoin(self.page_url, attr["href"]))
        if tag in {"img", "script"} and attr.get("src"):
            self.asset_links.append(urljoin(self.page_url, attr["src"]))
        if tag == "source" and attr.get("srcset"):
            self.asset_links.extend(extract_srcset(self.page_url, attr["srcset"]))
        if tag == "link" and attr.get("href"):
            rel = attr.get("rel", "")
            href = urljoin(self.page_url, attr["href"])
            if "stylesheet" in rel.lower():
                self.stylesheet_links.add(href)
            else:
                self.asset_links.append(href)
        if attr.get("style"):
            self.asset_links.extend(extract_css_urls(self.page_url, attr["style"]))


def extract_srcset(base_url: str, srcset: str) -> list[str]:
    urls = []
    for part in srcset.split(","):
        candidate = part.strip().split(" ", 1)[0]
        if candidate:
            urls.append(urljoin(base_url, candidate))
    return urls


def extract_css_urls(base_url: str, css_text: str) -> list[str]:
    urls = []
    for match in CSS_URL_RE.finditer(css_text):
        raw = match.group(1).strip().strip("'\"")
        if raw and not raw.startswith("data:"):
            urls.append(urljoin(base_url, raw))
    return urls


def normalize_url(url: str) -> str:
    clean, _fragment = urldefrag(url)
    parsed = urlparse(clean)
    if parsed.scheme not in {"http", "https"}:
        return clean
    host = parsed.hostname.lower() if parsed.hostname else ""
    path = parsed.path or "/"
    return parsed._replace(netloc=host, path=path).geturl()


def is_internal(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and (parsed.hostname or "").lower() in ALLOWED_HOSTS


def is_probable_html(url: str) -> bool:
    path = urlparse(url).path
    suffix = Path(path).suffix.lower()
    return suffix not in STATIC_EXTENSIONS


def request_bytes(url: str, timeout: int, max_bytes: int | None = None) -> tuple[bytes, str, int]:
    request = Request(url, headers={"User-Agent": "EnduranceNetNextGenMastheadCrawler/1.0"})
    with urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        status = getattr(response, "status", 200)
        if max_bytes:
            return response.read(max_bytes), content_type, status
        return response.read(), content_type, status


def classify_asset(asset_url: str) -> tuple[str, str] | None:
    parsed = urlparse(asset_url)
    path = parsed.path
    suffix = Path(path).suffix.lower()
    if suffix not in IMAGE_EXTENSIONS:
        return None
    if EVENT_BANNER_RE.search(path) and "/international/" in path:
        return "event_banner", "event microsite banner image"
    if EVENT_BANNER_RE.search(path) and any(part.isdigit() for part in path.split("/")):
        return "event_banner", "dated event banner image"
    if MASTHEAD_RE.search(path):
        return "masthead", "filename matches legacy masthead/banner naming"
    return None


def asset_id_for(url: str) -> str:
    parsed = urlparse(url)
    source_path = parsed.path.lstrip("/")
    return "live-" + hashlib.sha256(source_path.encode("utf-8")).hexdigest()[:16]


def candidate_rows(candidates: Iterable[Candidate]) -> list[Candidate]:
    by_url: dict[str, Candidate] = {}
    for candidate in candidates:
        by_url.setdefault(candidate.url, candidate)
    return sorted(by_url.values(), key=lambda item: (item.kind, item.url))


def write_jsonl(path: Path, rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def crawl(args: argparse.Namespace) -> tuple[list[Candidate], list[dict[str, object]]]:
    start_url = normalize_url(args.start_url)
    queue: deque[tuple[str, int]] = deque([(start_url, 0)])
    seen_pages: set[str] = set()
    seen_stylesheets: set[str] = set()
    candidates: list[Candidate] = []
    crawl_log: list[dict[str, object]] = []

    while queue and len(seen_pages) < args.max_pages:
        page_url, depth = queue.popleft()
        page_url = normalize_url(page_url)
        if page_url in seen_pages or not is_internal(page_url) or not is_probable_html(page_url):
            continue
        seen_pages.add(page_url)

        try:
            body, content_type, status = request_bytes(page_url, args.timeout, args.max_page_bytes)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            crawl_log.append({"url": page_url, "depth": depth, "status": "error", "error": str(exc)})
            continue

        if "html" not in content_type.lower() and not page_url.endswith((".html", ".htm", ".php", "/")):
            crawl_log.append({"url": page_url, "depth": depth, "status": status, "content_type": content_type, "skipped": "not-html"})
            continue

        html = body.decode("utf-8", errors="replace")
        extractor = LinkExtractor(page_url)
        extractor.feed(html)

        for asset_url in extractor.asset_links:
            normalized_asset = normalize_url(asset_url)
            classification = classify_asset(normalized_asset)
            if classification:
                kind, reason = classification
                candidates.append(Candidate(normalized_asset, page_url, kind, reason))

        for stylesheet_url in extractor.stylesheet_links:
            normalized_stylesheet = normalize_url(stylesheet_url)
            if normalized_stylesheet in seen_stylesheets or not is_internal(normalized_stylesheet):
                continue
            seen_stylesheets.add(normalized_stylesheet)
            try:
                css_body, _css_type, _css_status = request_bytes(normalized_stylesheet, args.timeout, args.max_page_bytes)
            except (HTTPError, URLError, TimeoutError, OSError):
                continue
            for asset_url in extract_css_urls(normalized_stylesheet, css_body.decode("utf-8", errors="replace")):
                normalized_asset = normalize_url(asset_url)
                classification = classify_asset(normalized_asset)
                if classification:
                    kind, reason = classification
                    candidates.append(Candidate(normalized_asset, page_url, kind, reason))

        if depth < args.max_depth:
            for link in sorted(extractor.page_links):
                normalized_link = normalize_url(link)
                if normalized_link not in seen_pages and is_internal(normalized_link) and is_probable_html(normalized_link):
                    queue.append((normalized_link, depth + 1))

        crawl_log.append(
            {
                "url": page_url,
                "depth": depth,
                "status": status,
                "content_type": content_type,
                "page_links": len(extractor.page_links),
                "asset_links": len(extractor.asset_links),
            }
        )
        if args.delay:
            time.sleep(args.delay)

    return candidate_rows(candidates), crawl_log


def download_candidates(args: argparse.Namespace, candidates: list[Candidate]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    staging_root = args.output_dir / "legacy"

    for candidate in candidates:
        parsed = urlparse(candidate.url)
        filename = Path(parsed.path).name or "asset"
        asset_id = asset_id_for(candidate.url)
        storage_path = staging_root / asset_id / filename
        public_url = f"/legacy-media/{parsed.path.lstrip('/')}"
        cms_public_url = f"/media/{asset_id}/{filename}"
        row = {
            "asset_kind": "image",
            "cms_asset_id": asset_id,
            "cms_public_url": cms_public_url,
            "cms_source_context": "live-legacy-masthead-crawl",
            "cms_storage_key": f"legacy/{asset_id}/{filename}",
            "kind": candidate.kind,
            "legacy_url": parsed.path,
            "live_url": candidate.url,
            "mime_type": mimetypes.guess_type(filename)[0] or "application/octet-stream",
            "public_url": public_url,
            "reason": candidate.reason,
            "source_page": candidate.source_page,
            "source_path": parsed.path.lstrip("/"),
            "stage_status": "pending",
            "staged_path": str(storage_path),
            "title": Path(filename).stem.replace("_", " ").replace("-", " ").strip(),
        }

        try:
            data, content_type, status = request_bytes(candidate.url, args.timeout)
            storage_path.parent.mkdir(parents=True, exist_ok=True)
            storage_path.write_bytes(data)
            row.update(
                {
                    "checksum_sha256": hashlib.sha256(data).hexdigest(),
                    "download_status": status,
                    "mime_type": content_type.split(";", 1)[0] or row["mime_type"],
                    "size": len(data),
                    "stage_status": "copied",
                }
            )
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            row.update({"stage_status": "blocked", "error": str(exc)})
        rows.append(row)
        if args.delay:
            time.sleep(args.delay)

    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-url", default=DEFAULT_START_URL)
    parser.add_argument("--output-dir", type=Path, default=Path("migration/media/images"))
    parser.add_argument("--manifest-name", default="live-mastheads-manifest.jsonl")
    parser.add_argument("--crawl-log-name", default="live-mastheads-crawl-log.jsonl")
    parser.add_argument("--max-depth", type=int, default=4)
    parser.add_argument("--max-pages", type=int, default=600)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--delay", type=float, default=0.02)
    parser.add_argument("--max-page-bytes", type=int, default=1048576)
    parser.add_argument(
        "--asset-url",
        action="append",
        default=[],
        help="Direct live masthead/banner asset URL to validate and download. May be repeated.",
    )
    args = parser.parse_args()

    candidates, crawl_log = crawl(args)
    for asset_url in args.asset_url:
        normalized_asset = normalize_url(urljoin(args.start_url, asset_url))
        classification = classify_asset(normalized_asset)
        if classification:
            kind, reason = classification
            candidates.append(Candidate(normalized_asset, args.start_url, kind, reason))
    candidates = candidate_rows(candidates)
    rows = download_candidates(args, candidates)

    manifest_path = args.output_dir / args.manifest_name
    crawl_log_path = args.output_dir / args.crawl_log_name
    write_jsonl(manifest_path, rows)
    write_jsonl(crawl_log_path, crawl_log)

    summary = {
        "start_url": args.start_url,
        "max_depth": args.max_depth,
        "max_pages": args.max_pages,
        "pages_crawled": len(crawl_log),
        "candidates": len(candidates),
        "copied": sum(1 for row in rows if row["stage_status"] == "copied"),
        "blocked": sum(1 for row in rows if row["stage_status"] == "blocked"),
        "manifest": str(manifest_path),
        "crawl_log": str(crawl_log_path),
    }
    (args.output_dir / "live-mastheads-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 1 if summary["blocked"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

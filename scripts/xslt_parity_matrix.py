#!/usr/bin/env python3
"""Inventory legacy XSLT transforms and emit a presentation parity matrix."""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


XSL_NS = "{http://www.w3.org/1999/XSL/Transform}"


@dataclass(frozen=True)
class MatrixConfig:
    source_root: Path
    output_path: Path
    max_files: int | None
    include_paths: tuple[str, ...]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def rel_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("/", "/")
    except ValueError:
        return str(path)


def text_flags(text: str) -> dict[str, bool]:
    lower = text.lower()
    return {
        "uses_atom": "atom:" in lower or "www.w3.org/2005/atom" in lower or "purl.org/atom/ns" in lower,
        "uses_rss": "rss/" in lower or "rss:" in lower or "channel/item" in lower,
        "uses_opml": "opml" in lower or "outline" in lower,
        "uses_disable_output_escaping": "disable-output-escaping" in lower,
        "uses_popup_overlay": "overlay(" in lower or "testclose(" in lower or "icon_popup" in lower,
        "uses_bullet_images": "bulletimage" in lower,
        "uses_event_story_route": "eventstoryinternal" in lower,
        "uses_google_reader_compat": "googlereader" in lower or "google reader" in lower,
    }


def presentation_mode(path: Path, flags: dict[str, bool]) -> str:
    lower = path.name.lower()
    if flags["uses_event_story_route"] or "eventstory" in lower:
        return "event-story-list"
    if flags["uses_popup_overlay"] or "popup" in lower:
        return "popup-channel-card"
    if flags["uses_disable_output_escaping"] or "single" in lower:
        return "single-entry-html"
    if flags["uses_google_reader_compat"] or "tevis" in lower:
        return "google-reader-frontpage"
    if lower.startswith("rss") or flags["uses_rss"]:
        return "rss-list"
    if "summary" in lower:
        return "atom-summary"
    if "list" in lower or flags["uses_atom"]:
        return "atom-list"
    return "xslt-compatibility"


def migration_status(mode: str) -> str:
    if mode in {"atom-list", "popup-channel-card", "single-entry-html", "event-story-list", "rss-list", "google-reader-frontpage"}:
        return "planned"
    return "triage"


def xsl_children(root: ET.Element, name: str) -> list[ET.Element]:
    return [
        element for element in root.iter()
        if element.tag == f"{XSL_NS}{name}" or local_name(element.tag) == name
    ]


def attr_values(elements: list[ET.Element], attr: str) -> list[str]:
    values: list[str] = []
    for element in elements:
        value = element.attrib.get(attr)
        if value:
            values.append(value)
    return values


def literal_references(text: str) -> list[str]:
    refs = sorted(set(re.findall(r"['\"]([^'\"]+\.(?:gif|jpg|jpeg|png|xml|xsl|html?)(?:\?[^'\"]*)?)['\"]", text, re.I)))
    return refs[:50]


def analyze_xslt(source_root: Path, path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="replace")
    flags = text_flags(text)
    try:
        root = ET.fromstring(text)
        parse_error = ""
    except ET.ParseError as exc:
        root = None
        parse_error = str(exc)

    params: list[str] = []
    variables: list[str] = []
    templates: list[str] = []
    output: dict[str, str] = {}
    namespace_uris: list[str] = []

    if root is not None:
        params = attr_values(xsl_children(root, "param"), "name")
        variables = attr_values(xsl_children(root, "variable"), "name")
        templates = attr_values(xsl_children(root, "template"), "match")
        output_elements = xsl_children(root, "output")
        if output_elements:
            output = dict(output_elements[0].attrib)
        namespace_uris = sorted(set(re.findall(r"\{([^}]+)\}", " ".join(element.tag for element in root.iter()))))

    mode = presentation_mode(path, flags)
    return {
        "sourcePath": rel_path(source_root, path),
        "presentationMode": mode,
        "migrationStatus": migration_status(mode),
        "parseError": parse_error,
        "output": output,
        "params": sorted(set(params)),
        "variables": sorted(set(variables)),
        "templateMatches": sorted(set(templates)),
        "namespaceUris": namespace_uris,
        "literalReferences": literal_references(text),
        "flags": flags,
    }


def xslt_files(source_root: Path, max_files: int | None, include_paths: tuple[str, ...]) -> list[Path]:
    found: list[Path] = []
    for include_path in include_paths:
        include_root = (source_root / include_path).resolve()
        if include_root.is_file() and include_root.suffix.lower() in {".xsl", ".xslt"}:
            found.append(include_root)
            continue
        if not include_root.exists():
            continue
        found.extend(
            path for path in include_root.rglob("*")
            if path.is_file() and path.suffix.lower() in {".xsl", ".xslt"}
        )
    files = sorted(set(found))
    if max_files is not None:
        return files[:max_files]
    return files


def build_matrix(config: MatrixConfig) -> dict[str, object]:
    records = [
        analyze_xslt(config.source_root, path)
        for path in xslt_files(config.source_root, config.max_files, config.include_paths)
    ]
    mode_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    for record in records:
        mode = str(record["presentationMode"])
        status = str(record["migrationStatus"])
        mode_counts[mode] = mode_counts.get(mode, 0) + 1
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "generatedAt": utc_now(),
        "sourceRoot": str(config.source_root),
        "includePaths": list(config.include_paths),
        "recordCount": len(records),
        "presentationModeCounts": dict(sorted(mode_counts.items())),
        "migrationStatusCounts": dict(sorted(status_counts.items())),
        "transforms": records,
    }


def parse_args(argv: list[str]) -> MatrixConfig:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", default="/Volumes/webstore/endurance.net")
    parser.add_argument("--output", default="migration/coverage/xslt-parity-matrix.json")
    parser.add_argument("--max-files", type=int, help="Limit transform scans for smoke checks.")
    parser.add_argument(
        "--include",
        action="append",
        dest="include_paths",
        help="Relative file or directory to scan. Can be repeated. Defaults to the full source root.",
    )
    args = parser.parse_args(argv)
    return MatrixConfig(
        source_root=Path(args.source_root).resolve(),
        output_path=Path(args.output).resolve(),
        max_files=args.max_files,
        include_paths=tuple(args.include_paths or ["."]),
    )


def main(argv: list[str]) -> int:
    config = parse_args(argv)
    if not config.source_root.exists():
        print(f"source root not found: {config.source_root}", file=sys.stderr)
        return 2
    matrix = build_matrix(config)
    config.output_path.parent.mkdir(parents=True, exist_ok=True)
    config.output_path.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote XSLT parity matrix to {config.output_path}")
    print(f"Inventoried {matrix['recordCount']} transforms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

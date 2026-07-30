#!/usr/bin/env python3
"""Capture Playwright smoke screenshots for core public routes."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urljoin


ROUTES = ["/", "/news", "/featured-stories", "/events", "/athletes", "/results"]


def run(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="Frontend base URL, for example http://127.0.0.1:18655.")
    parser.add_argument("--output-dir", default="output/playwright", help="Directory for screenshots.")
    parser.add_argument("--mobile", action="store_true", help="Use Playwright CLI generic mobile emulation.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    output_dir = (repo_root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    pwcli = Path(os.environ.get("PWCLI", Path.home() / ".codex/skills/playwright/scripts/playwright_cli.sh"))
    if not pwcli.exists():
        print(f"FAIL Playwright CLI wrapper not found: {pwcli}", file=sys.stderr)
        return 1

    mode = "mobile" if args.mobile else "desktop"
    try:
        for route in ROUTES:
            url = urljoin(args.base_url.rstrip("/") + "/", route.lstrip("/"))
            slug = "home" if route == "/" else route.strip("/").replace("/", "-")
            open_command = ["bash", str(pwcli), "open", url]
            if args.mobile:
                open_command.append("--mobile")
            run(open_command, repo_root)
            run(["bash", str(pwcli), "snapshot"], repo_root)
            run(
                [
                    "bash",
                    str(pwcli),
                    "screenshot",
                    "--filename",
                    str(output_dir / f"smoke-{slug}-{mode}.png"),
                    "--full-page",
                ],
                repo_root,
            )
    except subprocess.CalledProcessError as exc:
        print(f"FAIL Playwright smoke command failed with exit code {exc.returncode}", file=sys.stderr)
        return exc.returncode

    print(f"Playwright smoke screenshots written to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

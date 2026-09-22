#!/usr/bin/env python3
"""Check markdown links in the tree.

Local links must resolve to an existing file, and an #anchor must match a heading in
the target markdown file. External links are fetched with GET (10 s timeout) and
classified: `ok`, `broken` (HTTP 404 or 410) or `inconclusive` (timeouts, 403, 429, 5xx,
DNS or connection failures). Only confirmed `broken` fails the check; `inconclusive` is
listed for a human to resolve. Reference-style links, autolinks and HTML links are not parsed. `--offline` skips external links entirely.
"""
from __future__ import annotations

import argparse
import os
import re
import socket
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINK = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*$", re.M)
SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules"}


def slugify(h: str) -> str:
    s = h.strip().lower()
    s = re.sub(r"[^\w\- ]+", "", s)
    return re.sub(r"\s", "-", s)


def md_files():
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".md"):
                yield os.path.join(root, f)


def anchors_of(path: str) -> set[str]:
    text = open(path, encoding="utf-8").read()
    seen: dict[str, int] = {}
    out = set()
    for h in HEADING.findall(text):
        h = re.sub(r"`", "", h)
        s = slugify(h)
        n = seen.get(s, 0)
        out.add(s if n == 0 else f"{s}-{n}")
        seen[s] = n + 1
    return out


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (link-check; +https://github.com/kyle-chalmers/agentic-coding-lessons)"}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return "ok" if r.status < 400 else "inconclusive"
    except urllib.error.HTTPError as e:
        return "broken" if e.code in (404, 410) else "inconclusive"
    except urllib.error.URLError as e:
        return "inconclusive"  # DNS and connection failures may be environmental; a human resolves them
    except (socket.timeout, ConnectionError, OSError):
        return "inconclusive"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    a = ap.parse_args()
    broken, inconclusive, checked = [], [], 0
    cache: dict[str, str] = {}
    for md in md_files():
        text = open(md, encoding="utf-8").read()
        for _label, target in LINK.findall(text):
            checked += 1
            if target.startswith(("http://", "https://")):
                if a.offline:
                    continue
                if target not in cache:
                    cache[target] = fetch(target)
                status = cache[target]
                if status == "broken":
                    broken.append(f"{os.path.relpath(md, ROOT)} -> {target}")
                elif status == "inconclusive":
                    inconclusive.append(f"{os.path.relpath(md, ROOT)} -> {target}")
                continue
            if target.startswith("mailto:"):
                continue
            path_part, _, anchor = target.partition("#")
            tgt = md if not path_part else os.path.normpath(os.path.join(os.path.dirname(md), path_part))
            if not os.path.exists(tgt):
                broken.append(f"{os.path.relpath(md, ROOT)} -> {target} (missing file)")
                continue
            if anchor and tgt.endswith(".md") and anchor not in anchors_of(tgt):
                broken.append(f"{os.path.relpath(md, ROOT)} -> {target} (missing anchor)")
    for b in broken:
        print("BROKEN:", b)
    for i in inconclusive:
        print("INCONCLUSIVE:", i)
    print(f"check_links: {checked} links, {len(broken)} broken, {len(inconclusive)} inconclusive")
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Leak scanner for the published tree.

Two layers:
  1. Structural rules, committed here because they reveal nothing about anyone:
     ticket-key-shaped tokens, uppercase dotted database identifiers, issue-tracker and
     chat-archive URLs, cloud-drive URLs, email addresses, absolute home-directory paths.
  2. A literal denylist supplied at run time with --denylist-file. It is never committed.
     In --release mode the scan FAILS (exit 2) if no denylist is supplied, so a release
     check can never pass by accident. Without --release the literal layer is skipped and
     only the structural layer runs (what CI can do).

Matching is case-insensitive over NFKC-normalized text with zero-width characters removed;
multiword denylist terms are also matched over the whole file with all whitespace collapsed,
so a term split across a line break is still caught. Exit 0 = clean, 1 = hits, 2 = usage error.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import unicodedata

SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules"}
TEXT_EXT = {".md", ".json", ".sh", ".py", ".yml", ".yaml", ".txt", ".toml", ""}

# Tokens that look like ticket keys but are ordinary technical vocabulary.
SAFE_KEY_PREFIXES = re.compile(
    r"^(SHA|UTF|ISO|RFC|AES|CVE|MD|HTTP|HTTPS|TLS|SSL|PEP|L|GPT|X|ID|UUID|OAUTH|ERR|E|W)-", re.I)

STRUCTURAL = [
    ("ticket-key", re.compile(r"\b[A-Z]{2,12}-\d{1,6}\b")),
    ("dotted-upper-identifier", re.compile(r"\b[A-Z][A-Z0-9_]{2,}\.[A-Z][A-Z0-9_]{2,}(?:\.[A-Z][A-Z0-9_]{2,})?\b")),
    ("issue-tracker-url", re.compile(r"https?://[a-z0-9.-]*atlassian\.net\S*", re.I)),
    ("chat-archive-url", re.compile(r"https?://[a-z0-9.-]*slack\.com/archives\S*", re.I)),
    ("cloud-drive-url", re.compile(r"https?://(drive|docs)\.google\.com\S*", re.I)),
    ("email-address", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("home-path", re.compile(r"/(?:Users|home)/[A-Za-z0-9._-]+/|[A-Za-z]:\\\\Users\\\\")),
]
SAFE_EMAILS = re.compile(r"(users\.noreply\.github\.com|noreply@anthropic\.com|example\.com)$", re.I)
ZERO_WIDTH = re.compile(r"[​‌‍⁠﻿]")


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = ZERO_WIDTH.sub("", text)
    return re.sub(r"[ \t]+", " ", text)


def load_denylist(path: str) -> list[tuple[str, re.Pattern]]:
    terms = []
    for raw in open(path, encoding="utf-8"):
        t = raw.strip()
        if not t or t.startswith("#"):
            continue
        t = normalize(t).lower()
        if " " in t:
            pat = re.compile(re.escape(t).replace(r"\ ", r"\s+"), re.I)
        else:
            pat = re.compile(r"(?<![a-z0-9])" + re.escape(t) + r"(?![a-z0-9])", re.I)
        terms.append((t, pat))
    return terms


def iter_files(paths: list[str]):
    for p in paths:
        if os.path.isfile(p):
            yield p
            continue
        for root, dirs, files in os.walk(p):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for f in files:
                fp = os.path.join(root, f)
                if os.path.splitext(f)[1].lower() in TEXT_EXT:
                    yield fp


def scan_file(path: str, terms, release: bool) -> list[str]:
    hits = []
    try:
        raw = open(path, encoding="utf-8").read()
    except (UnicodeDecodeError, OSError):
        return hits
    for lineno, line in enumerate(normalize(raw).splitlines(), 1):
        for name, rx in STRUCTURAL:
            for m in rx.finditer(line):
                tok = m.group(0)
                if name == "ticket-key" and SAFE_KEY_PREFIXES.match(tok):
                    continue
                if name == "email-address" and SAFE_EMAILS.search(tok):
                    continue
                hits.append(f"{path}:{lineno}:{name}:{tok}")
        if release:
            low = line.lower()
            for t, pat in terms:
                if pat.search(low):
                    hits.append(f"{path}:{lineno}:denylist:{t}")
    if release and terms:
        # multiword terms can straddle a line break: scan the whole file with newlines collapsed too
        flat = re.sub(r"\s+", " ", normalize(raw)).lower()
        line_starts = [0]
        for i, ch in enumerate(normalize(raw)):
            if ch == "\n":
                line_starts.append(i + 1)
        for t, pat in terms:
            if " " in t:
                for m in pat.finditer(flat):
                    if not any(h.endswith(f":denylist:{t}") for h in hits):
                        hits.append(f"{path}:~:denylist:{t} (multiline)")
                    break
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--release", action="store_true", help="also apply the literal denylist; fail if none given")
    ap.add_argument("--denylist-file")
    ap.add_argument("--exclude", action="append", default=[], help="path substring to skip (repeatable)")
    a = ap.parse_args()
    if a.release and not a.denylist_file:
        print("scrub_check: --release requires --denylist-file (refusing to pass without it)", file=sys.stderr)
        return 2
    terms = load_denylist(a.denylist_file) if a.denylist_file else []
    if a.denylist_file and not terms:
        print("scrub_check: denylist file is empty; refusing", file=sys.stderr)
        return 2
    total = 0
    for fp in iter_files(a.paths):
        if any(x in fp for x in a.exclude):
            continue
        for h in scan_file(fp, terms, bool(a.denylist_file)):
            print(h)
            total += 1
    mode = "release" if a.release else ("denylist" if a.denylist_file else "structural")
    print(f"scrub_check: {total} hit(s) [{mode} mode, {len(terms)} literal terms]", file=sys.stderr)
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())

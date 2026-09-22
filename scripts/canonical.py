#!/usr/bin/env python3
"""The one canonicalization and hashing implementation for lessons.json entries.

Canonical form follows RFC 8785 (JSON Canonicalization Scheme) for the value shapes
used here (objects, arrays, strings, integers, booleans): keys sorted, no whitespace,
non-ASCII left unescaped, UTF-8 encoded. Every writer, reviewer, reducer and verifier
imports this module; nothing else may serialize an entry for hashing.

content_hash covers the lesson text. digest_hash covers only the README-digest fields, so
adding or changing a digest blurb never invalidates lesson verdicts. Neither hash includes
the id on purpose: every verdict record carries the id it was written for (in its filename
and its body), and the verifier matches on both id and hash, so a hash cannot be reused for
a different lesson without that mismatch showing up.
"""
from __future__ import annotations

import hashlib
import json
import sys
from typing import Any

CONTENT_FIELDS = [
    "title", "tier", "theme", "symptom", "rule", "why", "confidence", "confidence_note",
    "first_seen", "applies_to", "last_verified", "tool_scope", "other_agents", "related",
    "adds_beyond_docs",
]
DIGEST_FIELDS = ["digest_rank", "digest_blurb"]


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _subset(entry: dict, fields: list[str]) -> dict:
    return {k: entry[k] for k in fields if k in entry and entry[k] is not None}


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def content_hash(entry: dict) -> str:
    return _sha(canonical(_subset(entry, CONTENT_FIELDS)))


def digest_hash(entry: dict) -> str | None:
    sub = _subset(entry, DIGEST_FIELDS)
    return _sha(canonical(sub)) if sub else None


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: canonical.py <lessons.json | entry.json>", file=sys.stderr)
        return 2
    data = json.load(open(argv[1], encoding="utf-8"))
    entries = data["lessons"] if isinstance(data, dict) and "lessons" in data else (
        data if isinstance(data, list) else [data])
    for e in entries:
        print(f"{e.get('id','?')}\t{content_hash(e)}\t{digest_hash(e) or '-'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

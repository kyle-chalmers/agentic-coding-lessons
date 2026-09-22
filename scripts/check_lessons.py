#!/usr/bin/env python3
"""Validate lessons/lessons.json: JSON Schema plus the cross-entry rules a schema cannot state.

Cross-entry rules: unique IDs; every {lesson: L-NNN} reference resolves; exactly 20
digest entries ranked 1..20 with no gaps; every lesson's theme exists and its tier
matches; no em or en dash in any string; `why` is one sentence. Exit 1 on any failure.
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from canonical import content_hash, digest_hash  # noqa: E402

DASHES = re.compile("[\u2013\u2014]")


def walk_strings(obj, path="$"):
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_strings(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_strings(v, f"{path}[{i}]")


ABBREV = ("e.g", "i.e", "etc", "vs", "cf")


def one_sentence(text: str) -> bool:
    """Exactly one sentence: ends with a terminator, and no terminator followed by whitespace
    appears inside it except after a known abbreviation. Digits are rejected outright because a
    why must carry no counts or dates."""
    body = text.strip()
    if not body.endswith((".", "!", "?")) or re.search(r"\d", body):
        return False
    for m in re.finditer(r"[.!?]\s+\S", body[:-1]):
        before = body[:m.start()].rstrip().lower()
        if not any(before.endswith(a) for a in ABBREV):
            return False
    return True


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "lessons", "lessons.json")
    schema = json.load(open(os.path.join(ROOT, "scripts", "lessons.schema.json"), encoding="utf-8"))
    data = json.load(open(path, encoding="utf-8"))
    errors: list[str] = []
    try:
        import jsonschema  # type: ignore
        v = jsonschema.Draft202012Validator(schema)
        for err in sorted(v.iter_errors(data), key=lambda e: list(e.absolute_path)):
            loc = "/".join(str(p) for p in err.absolute_path) or "<root>"
            errors.append(f"schema: {loc}: {err.message}")
    except ImportError:
        errors.append("jsonschema not installed (pip install jsonschema); schema validation skipped")

    lessons = data.get("lessons", [])
    themes = data.get("themes", {})
    ids = [e.get("id") for e in lessons]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        errors.append(f"duplicate ids: {sorted(dupes)}")
    idset = set(ids)
    for e in lessons:
        eid = e.get("id", "?")
        for r in e.get("related", []):
            if "lesson" in r and r["lesson"] not in idset:
                errors.append(f"{eid}: related lesson {r['lesson']} does not exist")
            if "lesson" in r and r["lesson"] == eid:
                errors.append(f"{eid}: relates to itself")
        if e.get("theme") not in themes:
            errors.append(f"{eid}: theme {e.get('theme')} not in themes")
        elif themes[e["theme"]]["tier"] != e.get("tier"):
            errors.append(f"{eid}: tier mismatch with theme {e['theme']}")
        if "why" in e and not one_sentence(e["why"]):
            errors.append(f"{eid}: why must be exactly one sentence with no digits")
        if e.get("tool_scope") == "agent-agnostic" and e.get("other_agents"):
            errors.append(f"{eid}: other_agents not allowed on agent-agnostic lessons")
        if any("url" in r for r in e.get("related", [])) and not e.get("adds_beyond_docs"):
            errors.append(f"{eid}: adds_beyond_docs required when a doc URL is related")
    ranks = sorted(e["digest_rank"] for e in lessons if "digest_rank" in e)
    if ranks != list(range(1, 21)):
        errors.append(f"digest ranks must be exactly 1..20, got {ranks}")
    for p, s in walk_strings(data):
        if DASHES.search(s):
            errors.append(f"dash: {p}")
    used = {e.get("theme") for e in lessons}
    for slug in themes:
        if slug not in used:
            errors.append(f"theme {slug} has no lessons")
    for err in errors:
        print("FAIL:", err)
    if not errors:
        print(f"check_lessons: OK ({len(lessons)} lessons, {len(themes)} themes, "
              f"{sum(1 for e in lessons if 'digest_rank' in e)} digest entries)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

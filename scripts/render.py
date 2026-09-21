#!/usr/bin/env python3
"""Render lessons/lessons.json into theme markdown files and the README digest block.

Deterministic: the same JSON always produces the same bytes. `--check` renders in
memory and fails if any rendered file differs from what is on disk, if a rendered
file is missing, or if a stale theme file exists that the JSON no longer produces.
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LESSONS_JSON = os.path.join(ROOT, "lessons", "lessons.json")
README = os.path.join(ROOT, "README.md")
DIGEST_BEGIN = "<!-- digest:begin -->"
DIGEST_END = "<!-- digest:end -->"
TIER_DIR = {"agentic-practice": "lessons", "engineering": "engineering-lessons"}


def slugify(heading: str) -> str:
    s = heading.strip().lower()
    s = re.sub(r"[^\w\- ]+", "", s)
    s = re.sub(r"\s", "-", s)
    return s


def heading(e: dict) -> str:
    return f"{e['id']} {e['title']}"


def theme_path(themes: dict, slug: str) -> str:
    return f"{TIER_DIR[themes[slug]['tier']]}/{slug}.md"


def render_links(e: dict, index: dict, from_path: str) -> str:
    parts = []
    for r in e.get("related", []):
        if "url" in r:
            parts.append(f"[{r['label']}]({r['url']})")
        else:
            tgt = index[r["lesson"]]
            rel = os.path.relpath(tgt["path"], os.path.dirname(from_path)) if os.path.dirname(from_path) else tgt["path"]
            parts.append(f"[{r['lesson']}]({rel}#{tgt['anchor']})")
    return ", ".join(parts)


def render_entry(e: dict, index: dict, from_path: str) -> str:
    out = [f"### {heading(e)}", ""]
    out += [f"**Symptom:** {e['symptom']}", ""]
    out += [f"**Rule:** {e['rule']}", ""]
    out += [f"**Why:** {e['why']}", ""]
    meta = (f"**Confidence:** {e['confidence'].capitalize()} ({e['confidence_note']}). "
            f"**First seen:** {e['first_seen']}. **Applies to:** {e['applies_to']}. "
            f"**Scope:** {e['tool_scope']}.")
    if e.get("last_verified"):
        meta += f" **Last verified:** {e['last_verified']}."
    out.append(meta)
    if e.get("other_agents"):
        out.append(f"**Other agents:** {e['other_agents']}")
    if e.get("adds_beyond_docs"):
        out.append(f"**Beyond the docs:** {e['adds_beyond_docs']}")
    links = render_links(e, index, from_path)
    if links:
        out.append(f"**Related:** {links}")
    out.append("")
    return "\n".join(out)


def build_index(data: dict) -> dict:
    themes = data["themes"]
    idx = {}
    for e in data["lessons"]:
        idx[e["id"]] = {"path": theme_path(themes, e["theme"]), "anchor": slugify(heading(e)), "title": e["title"]}
    return idx


def render_theme(slug: str, theme: dict, entries: list, index: dict) -> str:
    path = theme_path({slug: theme}, slug)
    lines = [f"# {theme['title']}", "", f"**Scope:** {theme['scope']}", "", theme["intro"], "",
             f"Lessons in this file: {len(entries)}", ""]
    for e in entries:
        lines.append(f"- [{heading(e)}](#{index[e['id']]['anchor']})")
    lines += ["", "---", ""]
    for e in entries:
        lines.append(render_entry(e, index, path))
    text = "\n".join(lines).rstrip("\n") + "\n"
    return text


def render_digest(data: dict, index: dict) -> str:
    digest = sorted((e for e in data["lessons"] if "digest_rank" in e), key=lambda e: e["digest_rank"])
    lines = []
    for e in digest:
        t = index[e["id"]]
        lines.append(f"{e['digest_rank']}. **[{heading(e)}]({t['path']}#{t['anchor']})**: {e['digest_blurb']}")
    return "\n".join(lines) + ("\n" if lines else "")


def splice_digest(readme_text: str, block: str) -> str:
    if DIGEST_BEGIN not in readme_text or DIGEST_END not in readme_text:
        raise SystemExit("README.md lacks digest markers")
    pre, rest = readme_text.split(DIGEST_BEGIN, 1)
    _, post = rest.split(DIGEST_END, 1)
    return f"{pre}{DIGEST_BEGIN}\n{block}{DIGEST_END}{post}"


def render_all(data: dict) -> dict:
    themes = data["themes"]
    index = build_index(data)
    by_theme: dict[str, list] = {slug: [] for slug in themes}
    for e in data["lessons"]:
        if e["theme"] not in themes:
            raise SystemExit(f"{e['id']}: unknown theme {e['theme']}")
        if themes[e["theme"]]["tier"] != e["tier"]:
            raise SystemExit(f"{e['id']}: tier {e['tier']} does not match theme tier")
        by_theme[e["theme"]].append(e)
    files = {}
    for slug, theme in themes.items():
        entries = sorted(by_theme[slug], key=lambda e: e["id"])
        if not entries:
            raise SystemExit(f"theme {slug} has no lessons")
        files[theme_path(themes, slug)] = render_theme(slug, theme, entries, index)
    if os.path.exists(README):
        files["README.md"] = splice_digest(open(README, encoding="utf-8").read(), render_digest(data, index))
    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    data = json.load(open(LESSONS_JSON, encoding="utf-8"))
    files = render_all(data)
    rendered_theme_files = {p for p in files if p != "README.md"}
    failures = 0
    for d in TIER_DIR.values():
        dd = os.path.join(ROOT, d)
        if os.path.isdir(dd):
            for f in sorted(os.listdir(dd)):
                rel = f"{d}/{f}"
                if f.endswith(".md") and rel not in rendered_theme_files:
                    print(f"STALE: {rel} is not produced by lessons.json")
                    failures += 1
    for rel, text in files.items():
        fp = os.path.join(ROOT, rel)
        if a.check:
            cur = open(fp, encoding="utf-8").read() if os.path.exists(fp) else None
            if cur != text:
                failures += 1
                print(f"DIFF: {rel}")
                for line in difflib.unified_diff((cur or "").splitlines(), text.splitlines(), "on-disk", "rendered", lineterm="", n=1):
                    print("  " + line)
        else:
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            open(fp, "w", encoding="utf-8").write(text)
    if a.check:
        print(f"render --check: {'OK' if not failures else str(failures) + ' problem(s)'}")
        return 1 if failures else 0
    print(f"rendered {len(files)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

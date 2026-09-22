# Roadmap and build status

Last updated 2026-09-21. This file says what is in the repo today, what is
still in the pipeline, and the exact order of steps to finish a release, so
the state of the project is never a guess.

## What is published now

- `starter-kit/`: portable working-style rules (`AGENTS.md` with `CLAUDE.md`
  and `GEMINI.md` stubs), a read-only reconnaissance subagent, an advisory
  post-edit lint hook, the hook wiring example, and two pattern writeups
  (memory conventions, session-start injection). Written clean-room from
  principle lists, not copied from any private config.
- `usage-audit/README.md`: how I measured my own usage with `/insights`,
  `/doctor`, `claude doctor`, `/skill-doctor`, `/usage`, `/context`, and a
  homegrown monthly audit, and what I changed because of it.
- `SOURCES.md` and `CONTRIBUTING.md`: where lessons come from, how the
  pipeline scrubs them, and how to add one.
- `scripts/`: the schema, canonical hashing, deterministic renderer, link
  checker, structural leak scanner, and the `verify.sh` gate that CI runs.

## What is in the pipeline

The lesson corpus itself. From my own session logs the pipeline produced
1,862 candidates, merged them into 373 lessons, and an editor pass plus an
independent second-model review cut that to 197 curated lessons across 16
themes (10 about using coding agents, 6 general engineering). Each lesson
must clear three independent review lenses bound to a content hash, and a
stricter fourth lens where the sources were domain-heavy, before it renders.

Status at last update: 108 lessons have cleared every lens, 2 were rejected
by the lenses (one because the vendor docs already say it, one because its
only evidence was employer-specific configuration), and the remainder are
mid-verification. Lessons land in `lessons/lessons.json` only after all of
their verdicts are in, so a lesson you cannot find here has not passed yet,
not slipped through.

## Release checklist (maintainer)

In order. Every step is a script in this repo except the review agents,
which run outside it and write their verdicts next to the private build
state.

1. Finish verification for lessons still missing a verdict, then reduce the
   passed set into `lessons/lessons.json` (private reducer; only public
   fields survive).
2. Pick the 20 digest entries and write their one-line blurbs; the blurbs get
   the same three lenses as a lesson, bound to their own hash.
3. `python3 scripts/render.py` to render theme files and the README digest.
4. Semantic duplicate pass over the rendered tree; drop or merge, re-render.
5. `python3 scripts/make_manifest.py` equivalent: regenerate `MANIFEST`.
6. `bash scripts/verify.sh` (CI mode) and `bash scripts/verify.sh --release
   --denylist-file <private file>` (adds the private term denylist and the
   verdict-binding check). Both must exit 0.
7. Stranger read by a reviewer with no source context, plus a second-model
   review of the whole tree. Fix, re-render, re-verify.
8. Update `CHANGELOG.md`, commit, push. CI runs `verify.sh` in CI mode.

## After the first lesson batch

- Add a `last_verified` refresh cadence for lessons about platform quirks
  (quarterly re-check against current tool versions).
- Port the remaining portable skills as installable skills with per-tool
  install steps (ship-a-branch, usage audit, workspace janitor, resume
  handoff). The starter kit links to the ones already public.
- Expand the "Other agents" notes as I verify equivalents in Codex and
  Gemini CLI first-hand rather than from documentation.
- Consider a CI-side release attestation so the private denylist check can
  run in CI without committing the denylist.

## Known limitations

- Until the lesson batch lands, `scripts/verify.sh` fails in CI on the
  missing `lessons/lessons.json` and digest. That is intentional: the gate
  is honest, and the badge goes green when the content is real.
- The private denylist and provenance ledger live outside this repo on
  purpose; CI runs every check that needs no private input.

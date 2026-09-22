# Contributing

## What a lesson is

A lesson is one entry in `lessons/lessons.json`, validated against
`scripts/lessons.schema.json`. Read that schema file before writing one; the
rules below are the ones worth calling out on their own rather than a
restatement of every field in it. The remaining required fields (id, title,
theme, symptom, rule, confidence, confidence_note, first_seen, applies_to,
related) are explained by the schema itself and by the entries already in
the repo.

- `why` is exactly one sentence, with no numbers and no dates in it. It
  states the reason the rule holds, not the story that produced it.
- `tool_scope` is one of three values: `agent-agnostic` (works the same
  regardless of which coding agent you use), `claude-code-primary` (useful
  elsewhere too, but written with Claude Code specifically in mind), or
  `claude-code-specific` (the mechanism it describes only exists in Claude
  Code).
- `other_agents` only appears on a lesson that is not `agent-agnostic`, and
  only when there is an actual basis behind the claim, meaning you tried it
  yourself in another agent or read that agent's own documentation, not a
  guess that it probably also applies there.
- `adds_beyond_docs` is required whenever a lesson links to a vendor's own
  documentation. State plainly what the lesson tells you that the doc does
  not: a gotcha the doc omits, a mechanism it never mentions, a workaround
  it does not offer. If there is nothing to add beyond what the doc already
  says, the lesson does not belong here; link the doc from wherever else you
  were going to cite it instead.

## Generating the markdown

Every theme file under `lessons/` and `engineering-lessons/`, along with the
digest block in the root README, is generated output. Edit
`lessons/lessons.json` directly, then run:

    python3 scripts/render.py

Never hand-edit a rendered file. Anything typed into a theme file by hand
gets silently overwritten, or flagged as stale, the next time someone runs
the renderer, and `python3 scripts/render.py --check` catches any rendered
file that has drifted from the JSON either way.

## Before you open a pull request

Run:

    bash scripts/verify.sh

CI (continuous integration, meaning the checks that run automatically
against a pull request) runs the identical script in its default mode. It
checks the file manifest, the schema, that the rendered markdown matches the
JSON, that there are no em or en dashes anywhere in the tree, that there are
no absolute home-directory paths, secrets, or structural leaks, and that
there are no confirmed broken links (external links the checker cannot
reach are listed for a human to resolve). As the maintainer, I additionally run

    bash scripts/verify.sh --release --denylist-file <private denylist> --verdicts-dir <private results> --ledger <private ledger>

before every push. Those files live outside the repo and are never
committed: the denylist names terms that must never appear here, and the
results and ledger hold the review verdicts that `--release` binds to each
entry's content hash. Release mode refuses to run without all three, so it is
not something another contributor can run, and it is not part of the CI gate.

## Voice

No em dashes, no en dashes, anywhere, in any file. Plain, ordinary words
over ornamental ones. Every claim carries its own scope: say what you
actually saw and how confident you are in it, rather than writing a rule as
though it applies universally to everyone who reads it.

## What will not be accepted

- Anything that names a company, a person, or a customer, or that makes one
  identifiable from context even without naming them directly.
- An anecdote with no generic rule behind it. If a lesson only makes sense
  as "this one time, this exact thing happened to me," it is not ready yet.
- A restatement of a vendor's own documentation with nothing added. Link the
  doc, and only add a lesson alongside it when there is a gotcha, a
  mechanism, or a workaround the doc itself does not cover.

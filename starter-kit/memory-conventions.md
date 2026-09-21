# Memory conventions

This is the pattern I use for letting an agent keep facts across sessions
instead of relearning them every time: a directory of small memory files
plus one index file that points at them.

## Shape of a memory

Each memory is one markdown file, named with a kebab-case slug, holding one
fact. It starts with frontmatter:

```yaml
---
name: kebab-case-slug
description: one line, written so it helps a future search decide this memory is relevant
metadata:
  type: user | feedback | project | reference
---
```

- `user` is a fact about the person (preferences, environment, standing
  instructions).
- `feedback` is guidance on how the agent should work: a correction, or a
  confirmed approach worth repeating, always with the reason attached.
- `project` is a fact about ongoing work, a goal, or a constraint that the
  code and git history do not record on their own.
- `reference` is a pointer to something that lives elsewhere (a URL, a
  dashboard, a ticket, a document) plus the one line of context that makes
  it findable again.

For `feedback` and `project` memories, add a `Why:` line explaining why the
fact matters and a `How to apply:` line saying what the agent should do
differently because of it. Link related memories to each other with
`[[other-memory-name]]` instead of repeating their content.

## The index

Keep one index file (I call mine MEMORY.md) with exactly one pointer line
per memory: its name and a short description of what it covers. The index
never holds the content itself, only the pointer. That keeps the always-loaded
file small even as the number of memories grows, since the agent greps or
scans the index to decide which memory files to actually open.

## Write-time rules

- Before writing a new memory, check whether one already exists for this
  fact. Update it in place rather than creating a near-duplicate.
- When a memory turns out to be wrong, delete it rather than leaving it to
  contradict a newer one.
- Convert relative dates ("yesterday", "last week") to absolute ones before
  writing. A memory read six weeks later has no other way to know when
  "yesterday" was.
- Do not save what the repository already records: code structure, git
  history, and anything already written down in an instructions file. A
  memory earns its place by holding something no other artifact holds.
- When recalling a memory that names a file, a flag, or a function, verify
  it still exists before acting on it or recommending it. Code moves on;
  memory files do not update themselves.

## State versus event

Every fact you might write down is one of two kinds, and the two need
different treatment:

- **State**: a current value that can change. Overwrite it in place when it
  changes, and move the old value to a dated log line underneath if the
  history is worth keeping. Example: "the deploy target is X" is state.
- **Event**: something that happened at a point in time. Append it, and
  never edit it afterward. Example: "shipped the migration on 2026-03-01"
  is an event.

The test at write time is: would this line be wrong if the world changed
tomorrow? If yes, it is state, and it needs a place to be overwritten. If
no, it is an event, and it belongs in an append-only log.

Watch for the accretion smell: a memory that reads "did X; then did Y; then
found Z," carrying three different dates in one summary. That is a sign
state and events got mixed into the same file and it is time to split them.

Prose reminders to "keep this updated" are not enough on their own; in
practice, a documented run of prose-only staleness instructions was
followed only a small fraction of the time. Enforce the split
mechanically, with a schema or a lint check on the frontmatter, rather than
relying on an instruction the agent has to remember to reapply every time.

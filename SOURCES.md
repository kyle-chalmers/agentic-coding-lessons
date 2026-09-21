# Sources

Where these lessons come from, described by category rather than by
specific instance, and what is deliberately left out of that description.

## What feeds this repo

Every lesson here started as something that actually happened in my own use
of a coding agent, not as a hypothetical someone thought sounded plausible.
Four kinds of source feed the pipeline that turns that into a lesson:

- My own coding-agent session logs: a personal knowledge base compiled
  nightly from session transcripts across Claude Code and other agents I
  use, already abstracted into named incidents, meaning what happened, what
  fixed it, and whether it generalizes, before anything gets near this repo.
- Auto-memory files: the durable notes an agent carries forward across
  sessions on its own, which surface a recurring gotcha faster than reading
  back through raw transcripts would.
- Monthly usage audits: a homegrown report that classifies how I actually
  use a coding agent, session to session, and flags the gap between what I
  built and what I actually reach for.
- Direct tool output: `/insights` and `/doctor` runs, which analyze session
  shape and session setup respectively and hand back structured findings
  rather than raw transcript.

## The pipeline

Turning any of that into a published lesson goes through one pipeline every
time: sweep every source above for candidate incidents, abstract each one
away from the specifics of what actually happened, dedupe it against
lessons that already exist, run an editor pass that ranks the survivors and cuts the weakest, then
rewrite each keeper into this repo's schema. Every lesson then gets three
independent review passes, each one bound to the exact content it reviewed
by a content hash (a fingerprint of the entry's text) so a later silent edit
cannot outrun its own review, plus a stricter fourth pass for any lesson
whose source material leaned on specifics that had to be abstracted away by
hand rather than by a repeatable rule. Turning the schema into published
markdown is a deterministic script, not a rewrite, so the page you read
always matches the underlying entry byte for byte. Before anything ships it
passes a structural leak scanner that looks for shapes like ticket-style
identifiers and internal-looking database names, a private denylist of
specific terms that never gets committed to this repo, a secrets scan, a
read by someone with no context on the source material, and a second model
reviewing the first model's work.

## What is deliberately absent

- Any date more specific than a month, even inside a short sketch of an
  incident.
- Counts: how many of anything, how often, how large.
- Names: people, teams, or tools that would identify where a lesson came
  from, along with file paths and project names.
- The incident narratives themselves. A lesson states the rule and the
  reason it holds; it does not tell the story that produced it.

There is no path, timeline, employer, or industry recoverable from anything
published here. That is a constraint the pipeline enforces at every stage,
not a pass applied once at the end.

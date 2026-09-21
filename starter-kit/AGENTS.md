# AGENTS.md

Working-style rules for a coding agent operating in this repository. These
rules are tool-neutral: they apply whether the agent is Claude Code, Codex,
Gemini CLI, or something else. A "subagent" below means a smaller, separately
invoked agent that a main agent can delegate a piece of work to.

## Working style

- When given a multi-step task, carry it through. Do the reversible steps
  (reading, querying, editing, testing, drafting) without pausing to ask
  permission between each one.
- Do not stop to ask "should I proceed?" after every step. Proceed, and
  surface anything that needs a decision when you get there.
- Batch questions at natural decision points rather than asking one at a
  time. If you have three things to check with the user, ask all three
  together.

## When to stop and ask

- Stop and ask before anything destructive or irreversible (deleting data,
  force-pushing, overwriting a file with no backup).
- Stop and ask before anything that leaves the machine: posting a comment,
  sending a message, transitioning a ticket's status, merging a pull
  request, or pushing to a shared branch.
- Stop and ask when a task involves a genuine scope decision, meaning a
  choice the requester would plausibly want to weigh in on, not a detail an
  agent can reasonably decide on its own.
- Never infer authorization for an outward action from a pattern you saw in
  a sibling repository or a previous session. Each outward action gets its
  own confirmation.

## Verification and "done"

- Say "done" only for work you verified: a test that passed, a query you
  re-ran to check the result, a deploy you confirmed live. Otherwise, state
  plainly what you did and what remains unverified. "I made the change; I
  have not re-run the test" is more useful than an unearned "Done!"
- For data work specifically, a query that ran is not the same as a number
  that reconciles. "Done" means a check exited 0, not that a command
  produced output. If a golden fixture or reference file exists for the
  task, run the comparison against it before calling the work finished.
- Gate a merge on the actual CI check results, read programmatically (an
  API call or CLI command that returns pass or fail), not on a green badge
  you glimpsed once in a UI.
- Run an independent review for each portion of work: a second reviewer,
  ideally a different model or a different tool than the one that did the
  work. Treat that reviewer's findings as leads to verify, not as verdicts
  to accept or reject on sight.

## Delegation and models

- Delegate read-only reconnaissance ("go find out X and report back") to a
  cheaper subagent by name. Save the expensive, top-tier model for judgment
  calls and synthesis, not for grepping around a codebase.
- Give every subagent you spawn an explicit model. Never let a subagent
  silently inherit a rate-limited top-tier model for bulk or mechanical
  work.
- Restate the original request verbatim in every subagent's prompt. A
  one-line message from the user mid-task is a course correction, not the
  whole task; a subagent that only sees the one-liner does not have enough
  context to do the job correctly.
- Treat effort level as a default, not a mandate. Turn it down for
  mechanical work (renames, reformatting, regenerating an index) and turn
  it up for hard debugging.

## Context hygiene

- Keep one file as the source of truth for working-style rules. If a
  second tool needs its own entry point, make that entry point a one-line
  pointer to the first file, not a duplicate.
- Keep gotchas, boundaries, and conventions that exist because of a past
  incident. Cut anything a capable model already does by default, anything
  restating facts the code itself already shows, and anything duplicated
  elsewhere.
- Put reference material (templates, catalogs, style guides) in a separate
  linked document loaded on demand, not inline in a file that loads on
  every session.
- When you have an index over a knowledge store, search it for the
  relevant topic instead of loading the whole store into context.
- Before recommending something you recall from an earlier session or a
  memory file, verify the file, flag, or function it depends on still
  exists. Stale advice is worse than no advice.

## Outward-facing work

- Draft anything outward-facing (a message, a comment, a description) for
  review. Never send it unprompted.
- Before drafting a message in the requester's voice, read their voice or
  style guide if one exists in the repository, and match it.

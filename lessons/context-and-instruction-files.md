# Context and Instruction Files

**Scope:** Applies to any coding agent that loads instruction files at session start.

These lessons cover the files an agent reads before it does anything. Most of them are about what to leave out, and how to tell which rules still earn their place.

Lessons in this file: 8

- [L-012 Treat an embedded diff in a handoff or review prompt as possibly truncated](#l-012-treat-an-embedded-diff-in-a-handoff-or-review-prompt-as-possibly-truncated)
- [L-013 A config edit only changes future sessions, not the one that just wrote it](#l-013-a-config-edit-only-changes-future-sessions-not-the-one-that-just-wrote-it)
- [L-014 Periodically audit long-lived instruction files for restated rules](#l-014-periodically-audit-long-lived-instruction-files-for-restated-rules)
- [L-015 Centralize shared backend connection config across multiple AI coding assistants instead of duplicating it](#l-015-centralize-shared-backend-connection-config-across-multiple-ai-coding-assistants-instead-of-duplicating-it)
- [L-016 Keep personal preferences out of shared team config; put them in your user-scoped file](#l-016-keep-personal-preferences-out-of-shared-team-config-put-them-in-your-user-scoped-file)
- [L-017 Map an integration's real capability boundaries before relying on it](#l-017-map-an-integrations-real-capability-boundaries-before-relying-on-it)
- [L-018 Write a runtime gotcha into every file an agent would load, not just a code comment](#l-018-write-a-runtime-gotcha-into-every-file-an-agent-would-load-not-just-a-code-comment)
- [L-020 Scale an automated pipeline's prompt with what changed, not with total accumulated history](#l-020-scale-an-automated-pipelines-prompt-with-what-changed-not-with-total-accumulated-history)

---

### L-012 Treat an embedded diff in a handoff or review prompt as possibly truncated

**Symptom:** A review or handoff prompt embeds a large diff or text block, but the copy cuts off partway through, and whoever picks up the prompt works from incomplete evidence without noticing.

**Rule:** Never trust an embedded copy of a diff or large text block inside a prompt or handoff file at face value. Pull the live diff or source yourself, for example by rerunning the diff command, and treat the embedded copy as a convenience that may be truncated, not as ground truth.

**Why:** A prompt-embedded copy of a large text block passes through context windows and formatting steps that can silently drop content past some length, so the copy can look complete while missing its tail, and this recurred.

**Confidence:** High (The same failure mode recurred independently across separate reviews.). **First seen:** 2026-07. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-013 A config edit only changes future sessions, not the one that just wrote it

**Symptom:** You add a new rule to an always-loaded instructions or config file to change working style or automation behavior, and the same session that just wrote the rule keeps behaving the old way, so the edit looks like it silently failed.

**Rule:** After editing a persistent instructions or config file to change behavior, do not expect the current session to pick it up. Restart the session, or state the new rule directly in the conversation, if you need it applied right away.

**Why:** Instruction files are loaded once at session start, so a change made mid-session sits unread until a later session loads the file fresh.

**Confidence:** High (directly observed and noted the same day it happened). **First seen:** 2026-07. **Applies to:** any coding agent that loads instruction or config files at session start; not version-specific. **Scope:** claude-code-primary.
**Beyond the docs:** The docs describe how memory files are loaded but not that an edit made mid-session is invisible to that same session until it restarts.
**Related:** [Memory](https://code.claude.com/docs/en/memory)

### L-014 Periodically audit long-lived instruction files for restated rules

**Symptom:** An agent instructions file that has grown over many sessions ends up restating the same rule in several places, mixed with generic background text that never changes behavior.

**Rule:** Periodically re-read a long-lived instruction file end to end, merge duplicate restatements of the same rule into one place, and cut generic background that does not drive any behavior, while keeping every specific rule intact.

**Why:** Instruction files accrete edits over time as sessions append reminders without checking what is already there, so one rule ends up encoded in several places while the ones that matter get buried in restated boilerplate.

**Confidence:** Medium (Directly executed and measured once, with all specific rules verified preserved; not yet independently repeated on a separate long-lived file.). **First seen:** 2026-05. **Applies to:** not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs describe how memory files are loaded, not that they need periodic consolidation passes to remove duplicate restatements as they grow.
**Related:** [Memory](https://code.claude.com/docs/en/memory)

### L-015 Centralize shared backend connection config across multiple AI coding assistants instead of duplicating it

**Symptom:** Several AI coding tools each need to reach the same shared backend service, and keeping a per-tool copy of that connection configuration risks one copy falling out of sync after a credential or auth-method change.

**Rule:** When several AI coding assistants need the same shared backend service, point each one's connector at a single shared connection config file instead of duplicating credentials per tool, so a change like switching auth method propagates everywhere at once. Weigh this against the tradeoff: one shared file is also a single point of failure and concentrates the credential blast radius if that file is ever exposed.

**Why:** When several coding assistants each hold their own copy of the same connection config, an auth or credential change has to be applied once per copy, and a copy that gets missed keeps working on stale credentials until something fails against it.

**Confidence:** Medium (Reflects one documented architecture rather than a proven benefit under an actual failure.). **First seen:** 2026-05. **Applies to:** Any setup running multiple AI coding assistants that each need the same shared backend connector; not version-specific. **Scope:** agent-agnostic.

### L-016 Keep personal preferences out of shared team config; put them in your user-scoped file

**Symptom:** You're about to add a personal habit or tone preference into a config file that loads for an entire team, which would push your own style onto everyone else's sessions.

**Rule:** Before editing a shared or team-level instruction file to add a personal preference, check whether a user-scoped config location exists that loads only for your own sessions, and put personal customization there instead.

**Why:** A team-level instruction file loads for every session that touches that repo, so anything written there becomes an ambient default for other people's sessions rather than a private preference.

**Confidence:** Medium (One confirmed course-correction.). **First seen:** 2026-07. **Applies to:** Any agent with both a repo or team-scoped and a user-scoped instruction file, such as Claude Code's project versus user CLAUDE.md; not version-specific.. **Scope:** claude-code-primary.
**Beyond the docs:** The docs describe the project versus user memory file hierarchy but not the specific failure mode of a personal preference landing in the shared file by default habit and needing to be moved once noticed.
**Related:** [Memory](https://code.claude.com/docs/en/memory)

### L-017 Map an integration's real capability boundaries before relying on it

**Symptom:** You assume a connector, CLI, or API supports an action because it supports adjacent actions on the same object type, then hit a dead end mid task after you have already built around the assumption.

**Rule:** Before a task depends on an action you have not confirmed a tool supports, check its actual tool or command inventory first instead of discovering the gap after building around it, and once you find a real gap, write down the manual fallback so the next session does not rediscover it.

**Why:** Tool suites that share one object model rarely expose a uniform set of actions on every object type, so an agent that infers support from sibling actions can build a working plan around a capability that silently does not exist.

**Confidence:** High (Reconfirmed independently a month later on a different task with the same tool.). **First seen:** 2026-06. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-018 Write a runtime gotcha into every file an agent would load, not just a code comment

**Symptom:** A non-obvious bug's cause and fix are understood, but a later session touching the same code path never sees the warning because it lives only in a commit message or an inline comment the agent has no reason to open.

**Rule:** When you understand a non-obvious runtime gotcha, add it to every always-loaded context file and packaged guide a future session would read before touching that code path, not only the code comment or commit message where you first found the fix.

**Why:** An agent only sees what its current context window loads, so a warning that lives solely in a comment or commit message is invisible unless that exact file happens to be read again.

**Confidence:** Medium (Single observed instance, consistent with a broader stated norm but not independently repeated.). **First seen:** 2026-05. **Applies to:** not version-specific. **Scope:** claude-code-primary.
**Beyond the docs:** The docs describe how memory files are loaded, but not that a fix's explanation needs to be actively copied into every loaded file and skill guide that touches the affected code path, since none of them auto-propagate a warning written in just one place.
**Related:** [Memory](https://code.claude.com/docs/en/memory)

### L-020 Scale an automated pipeline's prompt with what changed, not with total accumulated history

**Symptom:** A recurring automation job that reprocesses a growing knowledge base or corpus inlines the full accumulated body of prior material into every run, so per run cost climbs steadily and the job eventually fails outright once the corpus is large enough, even though each run only needs a small slice of new material.

**Rule:** When an automated pipeline reprocesses an accumulating knowledge base or corpus on every run, give it an index or manifest by default and let it fetch only the entries the current input actually touches, instead of concatenating the entire corpus into every prompt.

**Why:** Inlining the whole accumulated corpus into every run ties per run cost to total history rather than to the size of the current input, so cost climbs with every addition until it crosses a hard ceiling and the run fails outright.

**Confidence:** High (Root caused and the fix verified with a concrete before and after cost comparison.). **First seen:** 2026-07. **Applies to:** not version-specific. **Scope:** agent-agnostic.

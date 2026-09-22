# Headless & Scheduled Automation

**Scope:** Running a coding agent unattended on a schedule or in the background: auth, polling, retries, and autonomy limits, independent of Claude Code specifically.

I run agent sessions unattended on schedules and in the background, and that mode breaks assumptions an interactive session never tests, like login prompts, browser profile locks, and turn budgets. These lessons cover the failure patterns I hit running an agent headless and how I now design automation so it fails loud instead of silently.

Lessons in this file: 14

- [L-021 Headless or scheduled automation cannot complete an interactive MFA or SSO login](#l-021-headless-or-scheduled-automation-cannot-complete-an-interactive-mfa-or-sso-login)
- [L-022 Give a subprocess CLI call stdin redirection and a hard timeout](#l-022-give-a-subprocess-cli-call-stdin-redirection-and-a-hard-timeout)
- [L-024 Non-interactive shells don't source your interactive shell profile](#l-024-non-interactive-shells-dont-source-your-interactive-shell-profile)
- [L-025 A background polling loop can outlast the agent's own tool-call timeout](#l-025-a-background-polling-loop-can-outlast-the-agents-own-tool-call-timeout)
- [L-026 A high bash-to-edit ratio signals a repeated CLI sequence worth scripting](#l-026-a-high-bash-to-edit-ratio-signals-a-repeated-cli-sequence-worth-scripting)
- [L-027 Guard scheduled automation that invokes a coding agent on its own logs against feedback loops](#l-027-guard-scheduled-automation-that-invokes-a-coding-agent-on-its-own-logs-against-feedback-loops)
- [L-028 Design shared automation state for hooks that can fire twice and sessions that run at once](#l-028-design-shared-automation-state-for-hooks-that-can-fire-twice-and-sessions-that-run-at-once)
- [L-029 Replace an LLM call with deterministic parsing when the input is structured and fixed](#l-029-replace-an-llm-call-with-deterministic-parsing-when-the-input-is-structured-and-fixed)
- [L-030 A tight tool allowlist burns an unattended agent's turn budget on denials](#l-030-a-tight-tool-allowlist-burns-an-unattended-agents-turn-budget-on-denials)
- [L-031 Autonomous runs need an instruction to leave a status note before they hit their limit](#l-031-autonomous-runs-need-an-instruction-to-leave-a-status-note-before-they-hit-their-limit)
- [L-032 Don't extrapolate a validated automation pattern to a new target without asking](#l-032-dont-extrapolate-a-validated-automation-pattern-to-a-new-target-without-asking)
- [L-033 Hiding a headless run's full output by default makes failures undebuggable](#l-033-hiding-a-headless-runs-full-output-by-default-makes-failures-undebuggable)
- [L-034 Never retry into a hard MFA or SSO denial](#l-034-never-retry-into-a-hard-mfa-or-sso-denial)
- [L-036 Surface a paid or quota-consuming automated step before running it](#l-036-surface-a-paid-or-quota-consuming-automated-step-before-running-it)

---

### L-021 Headless or scheduled automation cannot complete an interactive MFA or SSO login

**Symptom:** A scheduled or unattended job that depends on a service gated by browser based MFA or SSO stalls, hangs, or silently produces incomplete output once its cached session expires, because no human is present to answer the interactive prompt.

**Rule:** Before relying on headless or scheduled automation against an MFA or SSO gated service, build in a preflight check that confirms the cached session is still valid, a non interactive auth fallback where one exists, and a visible degrade and hand off to a human when neither works, rather than letting the job hang or silently return partial results.

**Why:** Browser based MFA and SSO require a human to complete a challenge, so any cached session backing an unattended job will eventually expire with nothing available to answer the prompt in its place.

**Confidence:** Medium (Recurred across several unrelated jobs and services over multiple months.). **First seen:** 2026-06. **Applies to:** not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs describe how to run an agent headlessly but not that a browser based MFA or SSO login cannot be completed unattended, or that a job needs a preflight session check and an explicit fallback for when the cached session expires.
**Related:** [Claude Code headless mode](https://code.claude.com/docs/en/headless)

### L-022 Give a subprocess CLI call stdin redirection and a hard timeout

**Symptom:** A CLI shelled out to non-interactively (another coding agent, a review tool, a linter) hangs indefinitely with no output, forcing a full session restart to recover.

**Rule:** Whenever you invoke a CLI subprocess non-interactively, including another coding agent's CLI for review or automation, explicitly redirect its stdin (for example with < /dev/null) and wrap the call in a hard timeout. Do not assume a CLI you didn't write will detect it has no terminal and exit gracefully.

**Why:** A process launched without a terminal can still block on an open stdin file descriptor waiting for input that will never arrive, since the OS gives it a real (if empty) stream rather than signaling EOF or absence of a terminal.

**Confidence:** Medium (Observed across multiple recurring incidents of the same failure mode over several months.). **First seen:** 2026-07. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-024 Non-interactive shells don't source your interactive shell profile

**Symptom:** A script or CLI call that depends on an environment variable normally set in your shell profile reads it as empty in an agent or automation context, silently falling back to a different default (for example, the wrong account), even though the same variable works fine in an interactive terminal.

**Rule:** Never assume an agent's or automation's shell inherits your interactive profile. Load required environment variables explicitly, for example through an explicit env file or a non-interactive-safe sourcing step, rather than relying on your rc file having run.

**Why:** Non-interactive shells (cron, headless agent runs, CI steps) skip the login/interactive startup files that set the variable, so any code that reads it just sees an empty value instead of an error, and silently falls through to a different default.

**Confidence:** High (Recurred across multiple independent incidents describing the same generic shell-sourcing gap.). **First seen:** 2026-07. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-025 A background polling loop can outlast the agent's own tool-call timeout

**Symptom:** A polling task meant to watch a long-running process, such as a deploy or a CI run, over tens of minutes gets killed mid-wait even though the process it is watching is still healthy.

**Rule:** For any wait that could run longer than a few minutes, launch it as a genuinely backgrounded process and check back on it, rather than blocking a single foreground tool call. The agent's own tool-call timeout is usually shorter than real infrastructure waits.

**Why:** A foreground wait is bound to the tool call's own timeout, so it gets killed before a long external process finishes even when that process itself is fine, and this recurred.

**Confidence:** High (Confirmed across two independent incidents.). **First seen:** 2026-05. **Applies to:** not version-specific. **Scope:** claude-code-primary.

### L-026 A high bash-to-edit ratio signals a repeated CLI sequence worth scripting

**Symptom:** When you review how a session spent its tool calls, the same four or five setup-then-verify-then-ship shell commands turn up re-run from scratch across many sessions, with a lopsided ratio of raw shell calls to file edits.

**Rule:** When you notice yourself or an agent re-driving the same multi-step CLI sequence session after session, check it into a script or skill instead of re-typing it. A lopsided bash-to-edit ratio when you review tool-call activity is the signal to look for this.

**Why:** A repeated multi-step CLI sequence that is retyped from scratch each session multiplies the number of chances for an auth failure or a step done out of order, instead of running through one tested path.

**Confidence:** Medium (Observed in two independent incidents describing the same generic pattern.). **First seen:** 2026-09. **Applies to:** any coding agent run from a shell, not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs describe how to build slash commands and skills, but not the diagnostic signal (a bash-heavy tool-call ratio when you review a session's activity) that tells you a given sequence has crossed the threshold worth scripting.
**Related:** [Claude Code common workflows](https://code.claude.com/docs/en/common-workflows)

### L-027 Guard scheduled automation that invokes a coding agent on its own logs against feedback loops

**Symptom:** A scheduled job invokes a coding agent to summarize or triage its own logs or memory, and the same logging or memory-capture system that watches interactive sessions picks up that job's own output, feeding it back into the source material on the next run.

**Rule:** When an unattended job invokes an agent SDK to act on your own logs or memory, add an explicit guard, such as an invoked-by marker or an exclusion filter, so the job's own output is never folded back into the source material it reads on the next run or counted as interactive usage.

**Why:** A logging or memory-capture system built to watch interactive sessions cannot tell a scheduled job's synthetic output from real activity unless the job marks itself, so the two get merged into a loop that recurred.

**Confidence:** High (Observed independently across two separate incidents converging on the same fix.). **First seen:** 2026-07. **Applies to:** any agent SDK or CLI invoked non-interactively on a recurring schedule, not version-specific. **Scope:** claude-code-primary.
**Beyond the docs:** The headless docs describe how to invoke a session non-interactively but not that the invocation itself needs a self-identifying guard to avoid being ingested by your own logging or memory pipeline.
**Related:** [Claude Code headless mode](https://code.claude.com/docs/en/headless)

### L-028 Design shared automation state for hooks that can fire twice and sessions that run at once

**Symptom:** A lifecycle hook fires more than once for what looks like a single session exit, and separate concurrent runs write into one shared state slot instead of their own.

**Rule:** Dedupe lifecycle-hook handling by a stable event key rather than trusting first-fire-wins, and give each concurrent automation run its own state slot instead of one shared one.

**Why:** A session-exit hook can retry or re-fire for the same logical event, and a single shared state slot has no way to tell two concurrent writers apart, so this recurred because the state design lacked per-event and per-session identity.

**Confidence:** Medium (Two related incidents observed together, corroborating the same root cause.). **First seen:** 2026-05. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-029 Replace an LLM call with deterministic parsing when the input is structured and fixed

**Symptom:** A pipeline step routes a value through a model call even though that value sits at a fixed, structured location in the input, such as a known field or a known bullet, and could be pulled out with plain parsing instead.

**Rule:** Before wiring a model call into an automated pipeline step, check whether the input is actually structured enough for deterministic parsing (a regex, an index, a fixed key). Reserve the model call for steps that need judgment, and use plain code for anything you could extract by position or pattern.

**Why:** An unattended pipeline defaults to spending a model call on every step, so a value that lives at a predictable, structured location gets routed through the model instead of being extracted with plain parsing, and this pattern recurred.

**Confidence:** Medium (Seen twice in separate automation contexts; not yet confirmed as a general pattern across more pipelines.). **First seen:** 2026-08. **Applies to:** not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs explain how token usage is priced, but not that a pipeline's default step design can silently spend a call on an extraction that structured input makes free with plain parsing.
**Related:** [Costs](https://code.claude.com/docs/en/costs)

### L-030 A tight tool allowlist burns an unattended agent's turn budget on denials

**Symptom:** An agent running unattended against a fixed turn or step budget keeps requesting a tool it is not permitted to use, and each denial consumes one of those turns without producing any investigation.

**Rule:** Before you launch an agent unattended against a turn or step budget, check that its tool allowlist actually covers what the task needs. Test the allowlist against a real run first, not just against the task description, since a permission gap that would prompt a quick approval interactively instead quietly eats the whole budget when nobody is there to grant it.

**Why:** A permission denial still consumes a turn in an unattended run the same way a real step would, so a mismatch between the allowlist and the task can spend most of the budget on rejected requests before any actual work happens.

**Confidence:** High (Single incident, but the mechanism (denials counting against the same budget as real steps) is structural, not situational.). **First seen:** 2026-05. **Applies to:** Claude Code running headless or unattended with a fixed turn/step budget and a restricted tool allowlist. **Scope:** claude-code-primary.
**Beyond the docs:** The docs describe how to configure permission modes and allowlists for headless runs, but not that a denial silently consumes the same turn budget as a productive step, so an overly narrow allowlist fails by starvation rather than by an obvious error.
**Related:** [Headless mode](https://code.claude.com/docs/en/headless), [Permission modes](https://code.claude.com/docs/en/permission-modes)

### L-031 Autonomous runs need an instruction to leave a status note before they hit their limit

**Symptom:** A long unattended agent run hits its turn or time budget without finding a fix, then stops with no trace of what it tried, leaving nothing for a human to pick up on.

**Rule:** Tell any long-running or autonomous agent to write a short status or handoff note as soon as it senses it might run out of turns or time, before it actually hits the limit, so budget exhaustion does not look identical to a silent crash.

**Why:** An agent that runs out of turns or wall-clock time simply stops mid-task, and without an explicit instruction to checkpoint its progress first, that stop is indistinguishable from a crash and forces a human to reconstruct what happened from scratch.

**Confidence:** High (single incident, but the failure mode is structural to any turn-limited agent.). **First seen:** 2026-05. **Applies to:** any agent framework or harness with a turn or time budget, not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs describe how to invoke a headless run but not that hitting the turn or time budget is silent, so the checkpoint-before-you-die convention has to be added by the operator.
**Related:** [Headless mode](https://code.claude.com/docs/en/headless)

### L-032 Don't extrapolate a validated automation pattern to a new target without asking

**Symptom:** An agent starts repeating a successful automated setup on a new repo or system purely because a similar prior run went well, without checking whether the user actually wants it run there too.

**Rule:** Treat a successful automation pattern as validated only for the target it was built and confirmed on. Ask before extending it to a new repo or system, even when the prior run's success makes it tempting to just repeat.

**Why:** A pattern proven safe on one target carries no evidence about a different target's auth, data, or blast radius, so repeating it there is an unverified assumption dressed up as a track record.

**Confidence:** High (Based on one incident, but the mechanism (success on A treated as license for B) is a common trap in unattended agent work.). **First seen:** 2026-07. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-033 Hiding a headless run's full output by default makes failures undebuggable

**Symptom:** A background, CI, or headless agent run is configured to hide its full output or reasoning trail by default, so when it stalls or fails there is no way to tell whether it was blocked by missing tool access or by genuine task complexity.

**Rule:** Keep the full output or log of any headless or scheduled agent run retrievable, even if a summary is what a human sees by default, so a stalled or failed run can still be diagnosed after the fact.

**Why:** Suppressing a headless run's own reasoning trail removes the only signal that distinguishes a permissions block from genuine task difficulty once the run has already finished.

**Confidence:** High (Directly root-caused from a single reproduced incident.). **First seen:** 2026-05. **Applies to:** not version-specific. **Scope:** claude-code-primary.
**Beyond the docs:** The docs describe how to run headless and on a schedule but not that hiding the run's full output removes your only way to tell a permissions block from real task difficulty after the fact.
**Related:** [Headless mode](https://code.claude.com/docs/en/headless), [Scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks)

### L-034 Never retry into a hard MFA or SSO denial

**Symptom:** An unattended agent hits an MFA or SSO prompt, the prompt is denied, and the agent immediately retries the same login instead of stopping.

**Rule:** The moment an MFA or SSO prompt comes back denied, stop retrying that login path immediately. Back off, surface the failure to a human, and wait for a person to clear it rather than hammering the prompt again.

**Why:** Retrying a denied auth challenge does not change the reason it was denied, it only adds more failed attempts against the same lockout counter that a human would otherwise rely on to sign in themselves.

**Confidence:** Medium (Single documented incident, but the failure mode (retry-into-lockout) is structural to any polling auth loop.). **First seen:** 2026-07. **Applies to:** any unattended or scheduled agent that authenticates through MFA or SSO, not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs describe how to run headless, not the failure mode of a denied auth prompt triggering a retry loop that risks locking the account out for everyone, including the human owner.
**Related:** [Claude Code headless mode](https://code.claude.com/docs/en/headless)

### L-036 Surface a paid or quota-consuming automated step before running it

**Symptom:** A plan or workflow is about to invoke another AI CLI or a paid API call as one step of a larger automation, consuming separate quota or billing from the current session, without telling the human first.

**Rule:** Before a workflow triggers a step that spends separate paid quota or billing, such as calling out to another agent's CLI or an external paid API, surface that cost to the human and get confirmation rather than letting it fire silently as part of a larger approved plan.

**Why:** Approving a workflow once does not mean approving every billed sub-step buried inside it, so a plan that quietly invokes a separate paid tool spends money the human never specifically saw or agreed to.

**Confidence:** Medium (Based on one incident; tier reflects the more cautious of the underlying candidates.). **First seen:** 2026-09. **Applies to:** Any agent workflow that can invoke a separate paid CLI or API as a sub-step; not version-specific. **Scope:** claude-code-primary.
**Other agents:** The same risk applies to any workflow that shells out to a separate paid CLI or API, such as one agent invoking another agent's command-line tool for review.
**Beyond the docs:** The docs describe how to run headless and scheduled automation but not that a sub-step spending separate paid quota needs its own explicit surfacing, distinct from approving the outer workflow.
**Related:** [Headless mode](https://code.claude.com/docs/en/headless)

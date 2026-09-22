# Session Continuity & Usage Management

**Scope:** Preserving work across context limits and usage caps, and sizing the cost and effort level a session runs at.

A session ends before the work does, whether from a context limit, a usage cap, or a deliberate handoff, and what survives that boundary depends on what I wrote down before it happened. These lessons cover checkpointing, resuming, and sizing effort and cost so a stopped session is a pause, not a loss.

Lessons in this file: 5

- [L-072 Checkpoint long-running work to a tracked file as you go, before a usage or context limit forces a stop](#l-072-checkpoint-long-running-work-to-a-tracked-file-as-you-go-before-a-usage-or-context-limit-forces-a-stop)
- [L-074 Treat a saved handoff or task prompt as a snapshot, not current truth](#l-074-treat-a-saved-handoff-or-task-prompt-as-a-snapshot-not-current-truth)
- [L-076 Treat a standing autonomy policy as something to audit, not set and forget](#l-076-treat-a-standing-autonomy-policy-as-something-to-audit-not-set-and-forget)
- [L-078 A background or detached process can be silently orphaned across a session boundary](#l-078-a-background-or-detached-process-can-be-silently-orphaned-across-a-session-boundary)
- [L-081 When a long-running session hits its usage limit, check the output file before assuming it failed](#l-081-when-a-long-running-session-hits-its-usage-limit-check-the-output-file-before-assuming-it-failed)

---

### L-072 Checkpoint long-running work to a tracked file as you go, before a usage or context limit forces a stop

**Symptom:** A long investigation or multi-step task ends abruptly, from a usage limit, a crash, or a hung background step, and everything done up to that point is lost because it only existed in the conversation or in a still-in-progress branch.

**Rule:** For any long-running investigation or multi-step task, write each verified finding or completed step to a file on disk that will outlive the session the moment it is confirmed (tracked in the repo when the work belongs there, and committed or pushed when the machine or environment is ephemeral): what was checked, the evidence, the conclusion, and a running next-steps section. Treat that file as the deliverable, so a killed session becomes resumable instead of a total loss. Keep the boundary clear: verified findings and working notes that must survive a killed session belong in a tracked file, while ephemeral resume prompts and scratch handoffs stay gitignored.

**Why:** A session can end at any point through a usage cap, a crash, or a hung step, and anything that exists only in the live conversation disappears with it, while in an ephemeral environment anything uncommitted disappears too, so only state written to durable storage survives.

**Confidence:** High (Corroborated across five independent incidents over several months.). **First seen:** 2026-05. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-074 Treat a saved handoff or task prompt as a snapshot, not current truth

**Symptom:** Work resumes from a previously written handoff or task prompt, or from state a prior session recorded as confirmed, and partway through it turns out the repo, data, or deploy status has moved on since it was written.

**Rule:** Before implementing from or trusting a saved handoff or task prompt, re-check the current state of the repo, data, or deploy status directly rather than trusting the prior snapshot, and where feasible design the implementation to derive its behavior from live state instead of a hard-coded count or assumption carried over from the prompt.

**Why:** A handoff prompt captures a single moment, so any assumption it encodes, such as how many items still need changing or what has already shipped, can silently go stale in the time between when it was written and when it is acted on.

**Confidence:** High (Recurred across at least three independent occurrences, corroborating the pattern.). **First seen:** 2026-05. **Applies to:** Any agent workflow that resumes from a saved handoff, task prompt, or session summary after a context limit or usage break; not version-specific.. **Scope:** claude-code-primary.

### L-076 Treat a standing autonomy policy as something to audit, not set and forget

**Symptom:** You've told the agent, in a standing instruction, to proceed through reversible steps without asking, but a recurring share of sessions still stop mid-task to ask for approval on steps that policy already covers.

**Rule:** When you write a standing autonomy rule, periodically sample recent sessions for stop-and-ask moments on reversible steps and compare the rate against your intent. If the gap persists across more than one audit despite restating the rule, treat it as an unresolved reinforcement problem, not a one-off reminder, and consider sharpening the rule's wording or moving the boundary into a hook or permission setting instead of relying on the model to recall it every time.

**Why:** A standing instruction to proceed autonomously competes with the model's own default caution on each turn, so without periodic re-verification the stated policy and the agent's actual behavior can drift apart and the drift goes unnoticed because nothing forces a comparison.

**Confidence:** Medium (Corroborated across two independent recurring-audit occurrences rather than a single incident.). **First seen:** 2026-08. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-078 A background or detached process can be silently orphaned across a session boundary

**Symptom:** A background watcher or detached process started mid-session is still running, or was silently stopped, by the time the session ends, with no completion record visible to whoever picks the work up next.

**Rule:** Track any background or detached process you start by its ID and explicitly check its status before assuming it completed. Session boundaries can silently orphan or kill background work without leaving a record.

**Why:** A process detached from its parent session has no guaranteed mechanism to report its outcome once that session ends, so its completion or failure goes unrecorded unless something checks it explicitly.

**Confidence:** Medium (Observed twice in near-identical form across sessions describing the same work.). **First seen:** 2026-07. **Applies to:** Claude Code background/detached shell tasks, not version-specific. **Scope:** claude-code-primary.

### L-081 When a long-running session hits its usage limit, check the output file before assuming it failed

**Symptom:** A background or long-running agent session terminates mid-transcript when it hits a usage or session limit, and the visible transcript looks cut off with no clear sign whether the task actually finished.

**Rule:** When a session ends mid-transcript on a usage limit, check the actual output file or artifact for completeness before assuming the task failed. The write can complete just before the session is cut off even though the transcript itself looks truncated.

**Why:** A usage or session limit can cut the transcript stream at any point, including right after the last write already landed on disk, so the transcript's apparent truncation says nothing about whether the underlying task completed.

**Confidence:** Medium (Single observed instance, confirmed by directly checking the output file.). **First seen:** 2026-07. **Applies to:** not version-specific. **Scope:** agent-agnostic.

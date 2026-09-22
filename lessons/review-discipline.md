# Review Discipline & Claiming Done

**Scope:** Treating an agent's own claims of completion, and other agents' review findings, as something to verify rather than trust.

An agent tells me a task is done, a review passed, or a capability does not exist, and I have learned to treat each of those as a claim to check, not a fact to relay. These lessons are the verification habits that catch what a first pass, or a confident wrong answer, would otherwise let through.

Lessons in this file: 6

- [L-064 Verify secondhand status claims against the primary source before acting](#l-064-verify-secondhand-status-claims-against-the-primary-source-before-acting)
- [L-066 Automated review findings are leads, not verdicts](#l-066-automated-review-findings-are-leads-not-verdicts)
- [L-067 Pre-flight multi-tool review setups before trusting their coverage](#l-067-pre-flight-multi-tool-review-setups-before-trusting-their-coverage)
- [L-068 Review the plan before code is written, not just the diff after](#l-068-review-the-plan-before-code-is-written-not-just-the-diff-after)
- [L-069 Draft outward-facing communications for approval, and re-present after every edit, never auto-send](#l-069-draft-outward-facing-communications-for-approval-and-re-present-after-every-edit-never-auto-send)
- [L-071 Independent reviewers converging on the same finding is a stronger signal than either alone](#l-071-independent-reviewers-converging-on-the-same-finding-is-a-stronger-signal-than-either-alone)

---

### L-064 Verify secondhand status claims against the primary source before acting

**Symptom:** A subagent's summary, a peer session's narrative, a fetched-page summary, or a claim that something already exists or already shipped gets relayed and acted on without anyone opening the actual file, log, commit, or ticket it describes.

**Rule:** Before acting on or relaying any secondhand claim about system state, open the primary source yourself, the actual file, commit, log, or ticket, rather than trusting a summary of it; when a reference can't be pinned down directly, ask for a canonical identifier or proof instead of guessing, and retract your own claim once asked for proof rather than defending it.

**Why:** A summary compresses away the details that would reveal whether it is wrong, so any layer between the reader and the primary record, whether a subagent, a peer session, or a fetched page, can carry forward an error that only checking the underlying source would catch.

**Confidence:** High (Reproduced independently across subagents, fetched web content, other agent sessions, and human-relayed escalations.). **First seen:** 2026-06. **Applies to:** Any workflow where an agent or person relays another party's summary of system state; not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs describe how to delegate work to subagents but not that their summaries need independent verification against the primary source before anyone acts on them.
**Related:** [Sub-agents](https://code.claude.com/docs/en/sub-agents)

### L-066 Automated review findings are leads, not verdicts

**Symptom:** A finding from an AI code reviewer, a static analyzer, or an aggregated multi-tool review report gets acted on, or repeated to someone else, as if it were already confirmed true.

**Rule:** Treat every automated or AI-generated review finding as a claim to verify against the current source before acting on it or repeating it. Check that it is not a stale diff, a scope error, a misparsed artifact, or a restatement of a pre-existing issue rather than something the change introduced.

**Why:** A review tool reasons over a snapshot of the diff and its own parsing of it, so a finding can point at code that already changed, sit outside the actual scope, or restate a bug the change did not introduce, and only a check against the live source can tell which.

**Confidence:** High (recurred across many independent sessions and tool combinations, with each false positive or misdiagnosis independently traced to its root cause). **First seen:** 2026-05. **Applies to:** any agent or tool that treats another agent's or reviewer's findings as input; not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs describe how to configure a reviewing sub-agent but not that its output still needs the same skepticism as an unverified human report before you act on it.
**Related:** [Sub-agents](https://code.claude.com/docs/en/sub-agents)

### L-067 Pre-flight multi-tool review setups before trusting their coverage

**Symptom:** A multi-AI or multi-tool review pass is treated as full panel coverage, but individual reviewer CLIs are flaky, blocked by sandboxing or resource limits, or fail silently, so a partial run looks identical to a complete one.

**Rule:** Before starting a multi-reviewer pass, confirm each tool actually executes rather than assuming it will. Track which tool is currently reliable instead of assuming panel coverage, treat the review itself, not any one CLI, as the invariant when a tool turns out flaky, and keep a manual or static fallback ready for when a review tool is blocked by sandboxing, resource contention, or read-only constraints.

**Why:** A review CLI can be blocked or degraded by the same sandboxing, temp-file, or resource constraints as the main session without raising a visible error, so a silently partial review is indistinguishable from a complete one unless each tool's execution is checked directly.

**Confidence:** High (Recurred across many different review CLIs and sandboxed environments.). **First seen:** 2026-05. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-068 Review the plan before code is written, not just the diff after

**Symptom:** An adversarial or design review happens only after the implementation is built, so a structural mistake is caught late and costs a rewrite instead of a plan revision.

**Rule:** Get an adversarial or design review of the plan itself, as a pass separate from reviewing the resulting diff, and do this before any code is written, especially for structural or visual and UX work.

**Why:** Reviewing only the finished diff checks whether the code matches the plan rather than whether the plan itself was sound, so a structural flaw baked into the design survives until fixing it costs far more.

**Confidence:** High (Reproduced across multiple independent projects, including migrations, UI redesigns, and plugin builds.). **First seen:** 2026-06. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-069 Draft outward-facing communications for approval, and re-present after every edit, never auto-send

**Symptom:** An ambiguous instruction like post this turns into an actual send, or a draft gets edited and then sent without being re-shown, or a QC pass catches overclaiming language only after it nearly went out.

**Rule:** Default any ambiguous outward-communication instruction to drafting, not sending. Re-present the draft for explicit approval after every edit, even a small one, and review outward text for overclaiming, not just the underlying data.

**Why:** An ambiguous instruction to communicate outward defaults toward sending rather than drafting, and editing an already-approved draft does not reset any approval state, so a modified copy of a message can pass through a review gate that only ever checked its earlier version; this recurred.

**Confidence:** High (Large, consistent cluster reinforced by an explicit standing user rule about outward-facing communications.). **First seen:** 2026-05. **Applies to:** Any agentic workflow that drafts outward-facing communications, such as messages, comments, or posts, for a human to approve; not version-specific. **Scope:** agent-agnostic.

### L-071 Independent reviewers converging on the same finding is a stronger signal than either alone

**Symptom:** Two separately run reviewers, whether different tools, different agents, or a human and an agent, flag the identical issue without having seen each other's output.

**Rule:** When two genuinely independent review passes converge on the same finding without cross contamination, weight that finding much higher than either pass alone, but still verify it, since correlated blind spots can produce false convergence too.

**Why:** The pattern recurred: two review passes that reach the same finding independently, without seeing each other's output, correlate with a genuine defect far more reliably than either pass alone, since false convergence would require both passes to share the same blind spot by coincidence.

**Confidence:** Medium (Consistent pattern across several incidents, though the underlying claim that convergence implies signal is itself unverified in a couple of the sources.). **First seen:** 2026-06. **Applies to:** not version-specific. **Scope:** agent-agnostic.

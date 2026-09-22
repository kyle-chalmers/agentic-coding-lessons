# Subagents & Model Selection

**Scope:** Delegating work to subagents and choosing models deliberately, including how to make delegation and multi-agent review pay off.

Delegating to a subagent or a different model only helps if I scope the handoff narrowly, pin the model on purpose, and ask for independent judgment rather than agreement. These lessons cover how I split work across models and agents and how I get a genuine second opinion out of it.

Lessons in this file: 8

- [L-095 Run a real usage audit periodically instead of trusting cost intuition about where spend goes](#l-095-run-a-real-usage-audit-periodically-instead-of-trusting-cost-intuition-about-where-spend-goes)
- [L-098 Pin an explicit model on every subagent instead of letting it inherit the parent's default](#l-098-pin-an-explicit-model-on-every-subagent-instead-of-letting-it-inherit-the-parents-default)
- [L-099 Plan for parallel subagents sharing a rate limit to fail together, not independently](#l-099-plan-for-parallel-subagents-sharing-a-rate-limit-to-fail-together-not-independently)
- [L-100 Reserve unattended autonomous loops for machine-checkable work, give judgment calls an investigate-then-surface pattern](#l-100-reserve-unattended-autonomous-loops-for-machine-checkable-work-give-judgment-calls-an-investigate-then-surface-pattern)
- [L-101 Restate the original task at the top of every subagent prompt in a long workflow](#l-101-restate-the-original-task-at-the-top-of-every-subagent-prompt-in-a-long-workflow)
- [L-103 Scope parallel subagents narrowly so a session limit still leaves usable partial output](#l-103-scope-parallel-subagents-narrowly-so-a-session-limit-still-leaves-usable-partial-output)
- [L-104 Validate a cost-downgrade decision with a quality signal, not just the cost surprise](#l-104-validate-a-cost-downgrade-decision-with-a-quality-signal-not-just-the-cost-surprise)
- [L-105 When handing work to a different model for a fresh take, make the handoff self-contained and ask for critique, not adoption](#l-105-when-handing-work-to-a-different-model-for-a-fresh-take-make-the-handoff-self-contained-and-ask-for-critique-not-adoption)

---

### L-095 Run a real usage audit periodically instead of trusting cost intuition about where spend goes

**Symptom:** A cost line item assumed to be minor turns out, once actually measured, to be much larger than the item everyone was watching.

**Rule:** Periodically measure actual agent usage and cost with a real audit rather than relying on impression. The biggest cost driver is often not the one that gets the most attention, and only a measured audit reveals it.

**Why:** Interactive usage accrues in many small, unlogged increments while an automated job's cost sits visibly in one line item, so intuition anchors on the visible cost and discounts the diffuse one until an audit tallies both together, and this recurred whenever assumed cost drivers were finally checked against measurement.

**Confidence:** High (measured directly with a dedicated audit script run against real session data.). **First seen:** 2026-07. **Applies to:** not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** the docs explain how to view cost data but don't warn that intuition about which usage category dominates is frequently wrong until an actual audit is run.
**Related:** [Costs reference](https://code.claude.com/docs/en/costs)

### L-098 Pin an explicit model on every subagent instead of letting it inherit the parent's default

**Symptom:** A fleet of background or workflow subagents all inherit one shared default model, and several fail or disappear at once when that model hits a usage cap, killing an entire multi-agent run mid-flight.

**Rule:** Set an explicit, appropriately sized model on every subagent or hook invocation rather than letting it inherit the parent session's model. Reserve the expensive or capped model for the main reasoning loop, and use a cheaper model for review, condensing, fact-checking, and other sub-tasks that do not need frontier reasoning.

**Why:** Inheriting the parent's default model couples every subagent's availability to the same usage cap, so one cap event takes down the whole fleet at once instead of degrading gracefully.

**Confidence:** High (the same incident recurred twice within two days before the fix was applied and then broadened.). **First seen:** 2026-09. **Applies to:** Claude Code subagents and workflow orchestration, not version-specific. **Scope:** claude-code-primary.
**Beyond the docs:** The docs cover how to configure a subagent's model but do not call out that letting several subagents share the parent's default model creates a single point of failure against usage caps.
**Related:** [Subagents](https://code.claude.com/docs/en/sub-agents)

### L-099 Plan for parallel subagents sharing a rate limit to fail together, not independently

**Symptom:** Several parallel subagents launched to divide up one review or task all hit the same rate or usage limit at the same moment, so none complete and the work is lost entirely, rather than partially finishing as independent failures would suggest.

**Rule:** When fanning a review or verification task out across several parallel subagents, plan for correlated failure such as a shared rate limit taking all of them down at once, and keep a fallback ready, such as running the pass sequentially or as one broader single agent, for any decision that genuinely depends on the review completing.

**Why:** Parallel subagents that share one underlying rate limit can all be throttled at the same instant, so a fan-out meant to add resilience instead turns one limit hit into a total loss of the work.

**Confidence:** High (this exact failure recurred across multiple log entries describing the same session). **First seen:** 2026-06. **Applies to:** Claude Code subagents, not version-specific. **Scope:** claude-code-primary.
**Beyond the docs:** The sub-agents docs describe how to configure parallel delegation but do not warn that parallel agents sharing one account or session rate limit can fail together at the exact same moment, losing the whole review rather than degrading gracefully.
**Related:** [Sub-agents](https://code.claude.com/docs/en/sub-agents), [Costs](https://code.claude.com/docs/en/costs)

### L-100 Reserve unattended autonomous loops for machine-checkable work, give judgment calls an investigate-then-surface pattern

**Symptom:** An automation is built to run unattended end to end, but part of the work actually needs a human judgment call, so full autonomy either stalls waiting for input it cannot get or makes a call on its own that it shouldn't.

**Rule:** Split automated work into two patterns: an unattended loop-until-done automation only for queue-shaped, machine-verifiable work, and a separate read-only investigation run for decision-heavy priorities that ends by presenting a clear choice rather than acting on it.

**Why:** Full unattended autonomy assumes every step has a checkable pass or fail condition, so routing a judgment call through the same loop either strands it waiting on input the loop cannot supply or lets the loop decide something it has no basis to decide.

**Confidence:** High (Explicit design decision documented with rationale and applied consistently.). **First seen:** 2026-07. **Applies to:** Any subagent or automation pipeline; not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs cover how to define and invoke a subagent but not when to withhold full autonomy: this splits automation by whether the work has a machine-checkable stop condition versus a decision only a person should make.
**Related:** [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)

### L-101 Restate the original task at the top of every subagent prompt in a long workflow

**Symptom:** During a long multi agent workflow, a short one off message sent partway through gets treated by newly spawned subagents as the authoritative task, so they refuse the real assignment or answer the aside instead.

**Rule:** When orchestrating subagents mid workflow, restate the original task and any interim messages, including what they meant and that they do not narrow scope, at the top of every subagent prompt, since the harness may otherwise frame a stray message as the real request without telling you.

**Why:** A subagent only sees what its own prompt contains, so if the harness surfaces the most recent conversational aside as context, that aside displaces the actual task in the subagent's view unless the orchestrator explicitly restates it.

**Confidence:** High (Reproduced across two consecutive rounds before the framing fix worked.). **First seen:** 2026-09. **Applies to:** Claude Code subagent orchestration (Task tool), not version-specific. **Scope:** claude-code-primary.
**Beyond the docs:** The docs describe how to define and invoke subagents but not that a mid workflow message can get relayed to them as the operative task, or that the fix is to explicitly restate the original task in every spawned prompt.
**Related:** [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)

### L-103 Scope parallel subagents narrowly so a session limit still leaves usable partial output

**Symptom:** A fan-out of several parallel review or analysis subagents hits a session or time limit partway through. Some finish, some are cut off with nothing, and it's tempting to treat the whole run as wasted.

**Rule:** Split a broad review or analysis task into several narrowly scoped, independently run subagents, one per dimension, so a session limit or timeout on some of them doesn't erase the value the others produced. When a fan-out is interrupted, act on the concrete findings the completed subagents already left, and run a focused, cheaper follow-up on just the remaining dimensions instead of restarting the whole fan-out.

**Why:** Independently scoped subagents each commit their own output as they finish, so a limit that cuts off some of them still leaves the completed ones' findings intact and usable, whereas one broad agent doing everything in a single pass loses its entire in-progress result to the same cutoff.

**Confidence:** High (The pattern was observed and then reused successfully across multiple separate review runs.). **First seen:** 2026-07. **Applies to:** Claude Code sub-agents feature, not version-specific. **Scope:** claude-code-primary.
**Beyond the docs:** The docs describe how to define and invoke subagents, but not that narrow per-dimension scoping is itself a resilience strategy against session limits and timeouts during a fan-out.
**Related:** [Subagents](https://code.claude.com/docs/en/sub-agents)

### L-104 Validate a cost-downgrade decision with a quality signal, not just the cost surprise

**Symptom:** A cost review finds spend on a premium model much higher than expected, creating pressure to blanket downgrade the model or a related setting across every use case.

**Rule:** Before reacting to a surprising cost finding with a blanket downgrade, measure an actual quality or error signal, such as how often that model's output needs correction, to check whether the spend is landing on genuinely hard work. Downgrade selectively, one setting at a time, based on what the evidence supports rather than on the cost number alone.

**Why:** A cost total says nothing about whether the spend was justified, so treating a high number as proof of waste skips the one measurement, an actual error or correction rate, that would show whether the harder setting is earning its cost.

**Confidence:** High (measured directly with a correction-rate check over a large sample before deciding). **First seen:** 2026-07. **Applies to:** Claude Code primarily; applies to any setup where model or effort tier is chosen per task and cost is later audited. **Scope:** claude-code-primary.
**Beyond the docs:** The docs explain how to track and reduce cost but not how to validate whether a downgrade is actually warranted; this adds pairing the cost signal with a quality or correction-rate check before downgrading.
**Related:** [Claude Code costs docs](https://code.claude.com/docs/en/costs)

### L-105 When handing work to a different model for a fresh take, make the handoff self-contained and ask for critique, not adoption

**Symptom:** A second model given a prior design tends to anchor to it and build on top rather than genuinely reconsidering it from scratch.

**Rule:** When routing a task to a different model or session for an independent second opinion or a ground-up redesign, bundle all setup steps, environment notes, and verified facts directly into the handoff prompt, and explicitly instruct it to critique and be willing to replace the existing approach rather than build on top of it.

**Why:** A model handed only a prior design tends to anchor on it and extend it rather than reconsidering from first principles, so a handoff meant to get an independent second opinion needs every setup detail bundled in and an explicit instruction to critique or replace the approach instead of building on it.

**Confidence:** High (The same lesson was independently reaffirmed across separate write-ups of the same handoff.). **First seen:** 2026-07. **Applies to:** Routing work between different models or sessions for independent review; not version-specific. **Scope:** claude-code-primary.
**Beyond the docs:** The sub-agents docs describe how to configure and invoke a subagent, not that a second model needs the prior design framed as something to critique rather than inherit to avoid anchoring on it.
**Related:** [Claude Code sub-agents docs](https://code.claude.com/docs/en/sub-agents)

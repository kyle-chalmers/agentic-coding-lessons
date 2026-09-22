# Agent Security & Untrusted Data

**Scope:** Treating an agent's file access, ingested content, and installed skills or plugins as a security surface, not a convenience.

An agent that can read files on disk is not stopped by a gitignore entry, and a transcript or document it ingests can carry instructions I never wrote. These lessons cover how I vet what an agent installs and trusts, and how I treat ingested content as data rather than commands.

Lessons in this file: 6

- [L-001 Gitignore or secret-scanner exclusion does not stop an agent from reading that file on disk](#l-001-gitignore-or-secret-scanner-exclusion-does-not-stop-an-agent-from-reading-that-file-on-disk)
- [L-002 Audit your own scrub or redaction replacement values, they can be real names too](#l-002-audit-your-own-scrub-or-redaction-replacement-values-they-can-be-real-names-too)
- [L-003 Treat ingested transcripts, logs, and documents as data, never as instructions](#l-003-treat-ingested-transcripts-logs-and-documents-as-data-never-as-instructions)
- [L-004 A global trust or auto-approve flag removes consent for everything routed through it, not just one case](#l-004-a-global-trust-or-auto-approve-flag-removes-consent-for-everything-routed-through-it-not-just-one-case)
- [L-005 A trailing wildcard on a tool allow-rule can grant far more than the intended command](#l-005-a-trailing-wildcard-on-a-tool-allow-rule-can-grant-far-more-than-the-intended-command)
- [L-006 Treat safe to publish and authorized to publish as two separate gates](#l-006-treat-safe-to-publish-and-authorized-to-publish-as-two-separate-gates)

---

### L-001 Gitignore or secret-scanner exclusion does not stop an agent from reading that file on disk

**Symptom:** A secrets scanner reports a codebase as clean because the sensitive file is excluded from git, while a coding agent with normal filesystem access can still open and read that same file directly.

**Rule:** Do not treat .gitignore, git-history exclusion, or "it isn't committed" as a control against an agent reading a file. Add any path the agent must never see to the agent's own tool-permission deny list, and remember a deny rule set at the agent's tool layer does not automatically bind subprocesses the agent spawns.

**Why:** Excluding a file from git only removes it from version control, not from the separate filesystem read path an agent's own tools use to open a file directly.

**Confidence:** High (The same gap was found independently in two unrelated projects, converging on the same fix.). **First seen:** 2026-07. **Applies to:** Claude Code and any coding agent with filesystem read tools; not version-specific. **Scope:** claude-code-primary.
**Beyond the docs:** The docs describe how to configure permission deny rules but do not warn that git-based exclusion (.gitignore, history scrubbing) is a separate control that leaves an agent's direct filesystem reads untouched.
**Related:** [Claude Code settings](https://code.claude.com/docs/en/settings)

### L-002 Audit your own scrub or redaction replacement values, they can be real names too

**Symptom:** A placeholder chosen to replace a scrubbed sensitive term turns out to be another real company or product name rather than a fictional one.

**Rule:** After scrubbing sensitive strings from a codebase or its history, review the replacement values themselves for accidental real-world references before publishing. Pick an obviously fictional placeholder instead of the first real-sounding name that comes to mind, since a real company name can itself imply a relationship you did not mean to disclose.

**Why:** Redaction tooling and reviewers typically check that the original sensitive string is gone, not that its replacement is itself safe, so a plausible-sounding stand-in slips through as a new, unnoticed leak.

**Confidence:** Medium (the same mistake was independently found in two separate scrubbing efforts.). **First seen:** 2026-06. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-003 Treat ingested transcripts, logs, and documents as data, never as instructions

**Symptom:** A prompt or pipeline that extracts, summarizes, or compiles content from a pasted transcript, log, or document has no explicit line telling it that directives, links, or commands embedded in that source text are inert, so the agent may act on text it was only supposed to read.

**Rule:** When a prompt or workflow processes untrusted text such as meeting transcripts, prior conversation logs, or fetched documents, state explicitly that embedded directives, links, or commands are data to report, not instructions to obey, and require a source citation for every extracted item so injected content stands out.

**Why:** Feeding a model its own prior text or a third party document blurs the boundary between content and command, so text embedded in that source can redirect the agent's behavior unless the prompt explicitly marks ingested content as inert.

**Confidence:** High (Two independent projects hit the same generic vulnerability and converged on the same fix.). **First seen:** 2026-07. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-004 A global trust or auto-approve flag removes consent for everything routed through it, not just one case

**Symptom:** A tool or MCP integration exposes a single boolean trust or auto-approve setting, and once it is turned on, the agent stops asking for confirmation on every later call that goes through that integration, not only the one call the setting was meant to cover.

**Rule:** Search your agent and tool configs for any global trust or auto-approve flag and treat each one as a standing risk. Assume it removes per-call consent for the entire integration, and prefer a narrower, per-command allowlist over a blanket trust switch.

**Why:** A single boolean setting can collapse an agent's per-action consent layer into a one-time approval that silently covers every future call through that integration.

**Confidence:** Medium (based on one configuration review, not yet an observed incident of unwanted action). **First seen:** 2026-07. **Applies to:** not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The MCP docs describe a project-scoped trust flag that only skips a one-time connection dialog for a helper script; they do not warn that a differently-scoped boolean trust or auto-approve setting on a tool or integration can instead silently cover every subsequent call routed through it.
**Related:** [Permission modes](https://code.claude.com/docs/en/permission-modes), [MCP](https://code.claude.com/docs/en/mcp)

### L-005 A trailing wildcard on a tool allow-rule can grant far more than the intended command

**Symptom:** A permission config allows a command with a trailing wildcard, such as a package runner with any arguments, and on review this turns out to permit arbitrary code execution through that command's own argument surface, not just the intended use.

**Rule:** Avoid wildcard suffixes on allow-rules for any command that can itself execute arbitrary code or scripts, such as package runners or interpreters. Allowlist specific subcommands or argument patterns instead of the whole command surface, and review existing wildcard allow-rules for the same trap.

**Why:** A trailing wildcard on an allow-rule matches any argument string, so a command that can itself interpret or execute its arguments turns a narrow-looking rule into unrestricted code execution.

**Confidence:** Medium (Based on a single permissions-review finding, not a confirmed exploit.). **First seen:** 2026-07. **Applies to:** Claude Code permission allow-rules; not version-specific. **Scope:** claude-code-primary.
**Beyond the docs:** The docs show the allow-rule syntax but do not flag that a wildcard on a command capable of running arbitrary code collapses the rule into effectively unrestricted execution.
**Related:** [Claude Code settings](https://code.claude.com/docs/en/settings)

### L-006 Treat safe to publish and authorized to publish as two separate gates

**Symptom:** A plan to publish or extract code built in a sensitive or proprietary context carefully covers clean git history and scrubbed secrets, but has no step confirming that publishing it was ever actually authorized by whoever owns the rights.

**Rule:** Before publishing or extracting code from a sensitive or proprietary codebase, add an explicit ownership and authorization checkpoint as its own gate, separate from secret scrubbing and history rewriting. A clean, secret free repo does not by itself mean you are allowed to publish it.

**Why:** Sanitizing history and scrubbing secrets answers whether a repo is safe to expose, which is a separate question from whether the rights holder has actually authorized exposing it at all.

**Confidence:** Medium (Identified in a single structured adversarial plan review, not an incident of unauthorized publication actually occurring.). **First seen:** 2026-09. **Applies to:** not version-specific. **Scope:** agent-agnostic.

# Hooks, Guardrails & Enforcement

**Scope:** Designing hooks and permission gates for a coding agent so they hold under bypass modes, compound commands, and other agents' proprietary flags.

I built hooks to stop an agent from doing something dangerous, and I kept finding gaps: a bypass mode that ignored them, a regex that missed shell quoting, a gate that only covered one access path. These lessons are the enforcement patterns that survive contact with a careless or overly autonomous agent session.

Lessons in this file: 10

- [L-038 Structural enforcement holds; prose instructions and standing rules erode over time](#l-038-structural-enforcement-holds-prose-instructions-and-standing-rules-erode-over-time)
- [L-040 Any command-matching safety gate must use a real shell tokenizer, not regex or whitespace splitting](#l-040-any-command-matching-safety-gate-must-use-a-real-shell-tokenizer-not-regex-or-whitespace-splitting)
- [L-041 An approval gate must sit before the first persistent side effect, and be enforced by something every runtime honors](#l-041-an-approval-gate-must-sit-before-the-first-persistent-side-effect-and-be-enforced-by-something-every-runtime-honors)
- [L-046 A guardrail hook installed only in .git/hooks protects nobody but you](#l-046-a-guardrail-hook-installed-only-in-githooks-protects-nobody-but-you)
- [L-047 Add a pre tool use hook that blocks irreversible commands pending explicit confirmation](#l-047-add-a-pre-tool-use-hook-that-blocks-irreversible-commands-pending-explicit-confirmation)
- [L-048 Check external tool auth before real work begins, not after it is done](#l-048-check-external-tool-auth-before-real-work-begins-not-after-it-is-done)
- [L-050 Don't carve a trivial-case exception into a safety or isolation rule](#l-050-dont-carve-a-trivial-case-exception-into-a-safety-or-isolation-rule)
- [L-052 Split destructive or remote steps out of a batched cleanup command](#l-052-split-destructive-or-remote-steps-out-of-a-batched-cleanup-command)
- [L-053 Measure a hook's latency, not just whether it fires correctly](#l-053-measure-a-hooks-latency-not-just-whether-it-fires-correctly)
- [L-054 Repeated prompts on one command usually mean a missing allowlist entry, not a reason to drop the tool](#l-054-repeated-prompts-on-one-command-usually-mean-a-missing-allowlist-entry-not-a-reason-to-drop-the-tool)

---

### L-038 Structural enforcement holds; prose instructions and standing rules erode over time

**Symptom:** A policy is written down as an instruction, a documented convention, or a standing always-do-X rule, and it holds inconsistently because it depends entirely on a person or a model remembering and applying it every single time.

**Rule:** For any rule that genuinely must hold, do not leave it as prose in an instruction file, README, or config comment. Encode it as something mechanical that runs automatically, such as a hook, a generator step, a linter, a required classification field, or a script the workflow cannot skip, so compliance does not depend on memory.

**Why:** A written rule alone produces partial, inconsistent compliance because it relies on the agent or person re-noticing and re-applying it every time, while the same rule wired into a hook, template, or mechanical check fires the same way regardless of who is operating or how much context they are holding.

**Confidence:** High (the same structural-vs-prose contrast was independently observed across several separate incidents; one of them measured it directly, with a built tool available but bypassed in the large majority of matching sessions across two consecutive monthly reviews). **First seen:** 2026-06. **Applies to:** not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs describe how to configure a hook; they do not make the argument that prose rules and standing instructions degrade under memory load while the identical rule expressed as a hook or generator step does not.
**Related:** [Hooks reference](https://code.claude.com/docs/en/hooks)

### L-040 Any command-matching safety gate must use a real shell tokenizer, not regex or whitespace splitting

**Symptom:** A hook or guard that pattern-matches shell commands for a safety decision, such as blocking a dangerous command or auto-approving a safe one, is bypassed by ordinary shell quoting, subshells, or newline-separated commands, or it false-triggers on a quoted string that merely contains the matched words.

**Rule:** Never match shell commands for a safety decision using regex or naive whitespace splitting. Parse the command line with a real shell tokenizer that understands quoting, subshells, and command separators before comparing against any pattern, and re-audit any heuristic classifier for these bypasses before promoting it from advisory to auto-approval.

**Why:** Regex and whitespace splitting operate on the raw text of a command line, so they cannot distinguish an operator or quote that changes what actually executes from one that appears only inside a quoted string, letting a bypass evade the match or an unrelated string trigger it falsely.

**Confidence:** High (the same tokenization fix confirmed the bypass across independent guards in separate codebases). **First seen:** 2026-08. **Applies to:** not version-specific; applies to any shell-command-matching hook or guard, including bypass-permission and auto-approval modes. **Scope:** agent-agnostic.
**Beyond the docs:** The docs describe how to configure hook matchers and permission modes but not that naive text matching on the command string is exploitable; this adds the specific tokenization requirement for any safety relevant pattern match.
**Related:** [Claude Code hooks docs](https://code.claude.com/docs/en/hooks), [Claude Code permission modes docs](https://code.claude.com/docs/en/permission-modes)

### L-041 An approval gate must sit before the first persistent side effect, and be enforced by something every runtime honors

**Symptom:** The agent writes plan files, creates branches, or edits tracked files before the user has approved a plan, or skips the approval step entirely on a runtime that ignores the flag the gate relied on; the user asks why they never got a plan to approve.

**Rule:** Place the approval checkpoint before the first action that persists anything (a file, a branch, a commit, a message), not only before push, merge, or send. State the gate in the instructions body so every runtime sees the intent, and enforce it with a hook or policy on each runtime you use, never only with one agent's proprietary enforcement flag.

**Why:** A gate enforced only through one agent runtime's proprietary invocation flag silently stops applying on any other runtime, and in any session where that flag goes unhonored, because the flag lives outside the portable instructions text the gate should actually depend on.

**Confidence:** Medium (two independent signals: a portability refactor of a plugin's gate mechanism, and a usage-insights finding of skipped plan approvals). **First seen:** 2026-08. **Applies to:** Claude Code hooks and permission-gate design; not version-specific. **Scope:** claude-code-primary. **Last verified:** 2026-09.
**Other agents:** Other runtimes do not honor Claude Code's model-invocation flag; on them the shared instructions carry the intent and a runtime-specific hook or policy has to carry the enforcement.
**Beyond the docs:** The docs explain how to configure hooks and permission modes but not that a gate expressed only through one runtime's model-invocation flag fails silently on other agent runtimes that never read that flag.
**Related:** [Hooks](https://code.claude.com/docs/en/hooks), [Permission modes](https://code.claude.com/docs/en/permission-modes)

### L-046 A guardrail hook installed only in .git/hooks protects nobody but you

**Symptom:** A hook meant to catch a known regression works fine locally, but it was added straight into the local .git/hooks directory rather than committed to the repo.

**Rule:** Build any guardrail meant to protect a team or future clones as a committed, shared mechanism, such as a tracked hooksPath, a CI check, or a packaged plugin hook, not as a file dropped directly into .git/hooks.

**Why:** Git hooks written straight into a repo's local .git/hooks directory are not tracked by version control, so the protection they provide never travels with a clone, a fresh checkout, or a teammate's machine.

**Confidence:** Medium (single observed instance, and the fix (commit the hook or move it to a shared mechanism) was left as an open decision rather than verified in practice). **First seen:** 2026-09. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-047 Add a pre tool use hook that blocks irreversible commands pending explicit confirmation

**Symptom:** A destructive command such as a force push, a recursive delete, or a production job launch executes as an ordinary step inside a larger automated sequence, with nothing distinguishing it from the reversible steps around it.

**Rule:** Configure a pre tool use hook that parses the command with a real shell tokenizer and matches destructive or production-affecting operations and blocks execution with a clear message unless the user has explicitly confirmed that specific action, so an irreversible step can never ride along inside a batch of otherwise safe ones.

**Why:** Automated sequences that run under one approval extend the same trust to every step in the batch, so a destructive command executes like any other unless it is checked and gated individually before it runs.

**Confidence:** Medium (The triggering incidents are confirmed, but the guard itself is a proposed mitigation, not yet verified in production use.). **First seen:** 2026-09. **Applies to:** Claude Code hooks (PreToolUse), not version-specific. **Scope:** claude-code-specific.
**Beyond the docs:** The docs already show a PreToolUse hook that blocks a destructive command like rm -rf with a plain always-deny rule. This adds the narrower point that irreversible or production-affecting commands need their own confirmation gate, distinct from the reversible steps riding along in the same approved batch, rather than a single blanket deny rule that treats every matched command the same.
**Related:** [Claude Code hooks](https://code.claude.com/docs/en/hooks), [L-040](hooks-and-guardrails.md#l-040-any-command-matching-safety-gate-must-use-a-real-shell-tokenizer-not-regex-or-whitespace-splitting)

### L-048 Check external tool auth before real work begins, not after it is done

**Symptom:** A session runs a full investigation or analysis and only discovers at the very end that a CLI tool's credentials were broken or its library wasn't importable the whole time, turning a completed piece of work into a dead end.

**Rule:** Before the first call to an external tool in a session, run a preflight that confirms the CLI is authenticated and the client library imports from the active interpreter, and stop with a clear message if either fails. In Claude Code a SessionStart hook can run the CLI-level checks; anything that needs a live tool connection belongs in a PreToolUse hook or in the first step of the task itself.

**Why:** A broken credential or interpreter mismatch only fails at the moment a tool call is actually made rather than automatically at launch, so without a check placed where the relevant client context already exists, real analysis work gets sunk in before the failure ever surfaces.

**Confidence:** High (Named as a recurring, structural friction source across multiple distinct sessions, not a one-off.). **First seen:** 2026-09. **Applies to:** Claude Code SessionStart and PreToolUse hooks; the preflight idea applies to any agent that can run a script before work starts. **Scope:** claude-code-primary.
**Beyond the docs:** The docs describe SessionStart and PreToolUse hooks and when each fires; they do not suggest using them as an authentication and import preflight so a session cannot sink real work before a broken credential surfaces.
**Related:** [Hooks](https://code.claude.com/docs/en/hooks)

### L-050 Don't carve a trivial-case exception into a safety or isolation rule

**Symptom:** A rule requiring an isolated workspace, a review step, or some other safeguard for every change has a carve-out for small or docs-only cases, and that exception later gets invoked to justify exactly the risky shortcut the rule existed to prevent.

**Rule:** When a rule exists specifically to force a review, isolation, or confirmation step, avoid scope-based exceptions like unless it's small or unless it's docs-only. Carve-outs get invoked for exactly the case the rule existed to catch, so make the rule unconditional if it actually matters.

**Why:** A safety or isolation rule that carries an exception for small or low-risk cases invites that exception to be stretched to justify the exact shortcut the rule exists to block, because small is a judgment call and the rule's own carve-out gives that judgment call a foothold.

**Confidence:** High (The incident was directly observed and the rule change was adopted immediately afterward as a persisted policy.). **First seen:** 2026-05. **Applies to:** Any coding agent workflow with configurable isolation or review rules; not version-specific. **Scope:** claude-code-primary.

### L-052 Split destructive or remote steps out of a batched cleanup command

**Symptom:** A single compound command bundles harmless, reversible, local steps together with one remote or destructive step, such as deleting a remote branch or dropping a table, and the whole command gets blocked or denied even though most of it was safe.

**Rule:** When batching cleanup work, keep local or reversible operations in one command and remote or destructive operations in a separate one, so a permission gate or safety classifier can evaluate the risky part on its own instead of blocking the entire batch over one clause.

**Why:** A permission gate or safety classifier that scans a command for its riskiest clause treats the whole compound command as that risk level, so bundling one destructive or remote step into an otherwise-safe batch makes the classifier deny the safe steps along with it.

**Confidence:** Medium (Single observed incident.). **First seen:** 2026-06. **Applies to:** Any coding agent with a permission gate or safety classifier that evaluates whole shell commands; not version-specific. **Scope:** claude-code-primary.
**Beyond the docs:** The docs describe how permission modes gate individual actions but not that a compound command is judged as a whole, so splitting risky clauses out changes what gets approved.
**Related:** [Permission modes](https://code.claude.com/docs/en/permission-modes)

### L-053 Measure a hook's latency, not just whether it fires correctly

**Symptom:** A hook fires correctly and does the right thing on every matching tool call, but it also adds noticeable delay each time, and this goes unnoticed because correctness is usually the only thing anyone checks.

**Rule:** When you add a hook to a coding agent, measure its typical and worst case latency, not only whether it fires and behaves correctly. A hook runs on every matching tool call, so a slow one silently taxes the whole session.

**Why:** A hook sits in the synchronous path of every matching tool call, so any added latency in it compounds across a session in a way that a one-time correctness check never surfaces, and this recurred until a dedicated pass measured it directly.

**Confidence:** High (Directly measured with median and worst-case latency numbers during a dedicated audit.). **First seen:** 2026-07. **Applies to:** Claude Code hooks, any version. **Scope:** claude-code-specific.
**Beyond the docs:** The hooks reference documents how to wire a hook up, but not that its latency needs to be measured on its own; that only surfaced from a dedicated workspace-health audit.
**Related:** [Claude Code hooks](https://code.claude.com/docs/en/hooks)

### L-054 Repeated prompts on one command usually mean a missing allowlist entry, not a reason to drop the tool

**Symptom:** A CLI tool triggers a permission prompt on every single invocation, and the friction builds to the point where dropping the tool entirely starts to look like the fix, even though the tool's own safety behavior is what makes it worth keeping.

**Rule:** Before removing a tool to stop approval-prompt friction, check whether your agent has a per-command allowlist setting that fixes it with one config entry. Treat repeated prompts on the same command pattern as a missing-allowlist symptom first, not a reason to abandon the tool.

**Why:** A permission gate that matches a command pattern too narrowly re-prompts on every call, and the fix is a single allowlist entry rather than removing the tool the gate was protecting.

**Confidence:** High (root-caused, fixed with a one-line config change, and the same cause reproduced when the symptom recurred in a second repository). **First seen:** 2026-07. **Applies to:** Claude Code permission allowlists; not version-specific. **Scope:** claude-code-primary.
**Beyond the docs:** The docs describe how allowlist entries work but not that recurring friction on one specific command is itself the diagnostic signal to check the allowlist before giving up on the tool.
**Related:** [Permission modes](https://code.claude.com/docs/en/permission-modes), [Settings](https://code.claude.com/docs/en/settings)

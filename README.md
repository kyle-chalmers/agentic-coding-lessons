# Agentic Coding Lessons

> 🌐 **[KC Labs](https://www.kclabs.ai/)** | 📺 **[Kyle Chalmers Data & AI YouTube](https://youtube.com/@kylechalmersdataai)**

[![verify](https://github.com/kyle-chalmers/agentic-coding-lessons/actions/workflows/ci.yml/badge.svg)](https://github.com/kyle-chalmers/agentic-coding-lessons/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Field-tested lessons on working with coding agents, mined from my own session logs and verified before publishing.**

I run Claude Code most of the day, with Codex and Gemini CLI alongside it, and
every session leaves a trail: what went wrong, what I asked for and did not
get, what a hook or a plugin or a worktree did that I did not expect. A
personal knowledge base compiles those trails nightly. This repo is the part
of that knowledge base that has nothing to do with any one employer or
codebase: the traps, the rules that survived, and the habits that turned out
to matter, each one stated so a stranger can apply it.

**151 lessons across 16 themes, every one verified before publishing.**

## Who this is for

- ✅ People who use a coding agent daily and want the mistakes already made for them.
- ✅ People setting up hooks, skills, subagents, or scheduled agent runs for the first time.
- ✅ Engineers who want the general lessons (git, CI, secrets, debugging) the agent work surfaced.
- ❌ Anyone looking for an introduction to Claude Code. Start with my [Claude Code for data teams guide](https://github.com/kyle-chalmers/data-ai-reference) and come back.

## The twenty I would read first

Ranked by how many distinct incidents stand behind each one and how widely it applies.

<!-- digest:begin -->
1. **[L-067 Pre-flight multi-tool review setups before trusting their coverage](lessons/review-discipline.md#l-067-pre-flight-multi-tool-review-setups-before-trusting-their-coverage)**: Reviewers that quietly fail to run give you a clean-looking pass with no coverage; check that each one executed before trusting the panel.
2. **[L-066 Automated review findings are leads, not verdicts](lessons/review-discipline.md#l-066-automated-review-findings-are-leads-not-verdicts)**: Treat every automated finding as a claim to check against the current source, because stale diffs and misread artifacts produce confident nonsense.
3. **[L-190 Verify against actual live system state, not a migration file, manifest, snapshot, or convenient checkout](engineering-lessons/verification-tooling-rigor.md#l-190-verify-against-actual-live-system-state-not-a-migration-file-manifest-snapshot-or-convenient-checkout)**: Migration files, manifests, and snapshots describe intent; only the running system tells you what is actually true.
4. **[L-189 A live, rendered walkthrough catches UI defects that code review and text checks never will](engineering-lessons/verification-tooling-rigor.md#l-189-a-live-rendered-walkthrough-catches-ui-defects-that-code-review-and-text-checks-never-will)**: Static review cannot see a chart that truncates, a legend that lies, or a layout that collides, so walk the live UI before calling a visual change done.
5. **[L-168 Merge succeeding, CI passing, or a scheduled job running are different claims from the change being live](engineering-lessons/git-ci-and-release-mechanics.md#l-168-merge-succeeding-ci-passing-or-a-scheduled-job-running-are-different-claims-from-the-change-being-live)**: Merged, deployed, and job ran are three separate claims, and none of them is the claim that the change is live and working; verify that one on its own.
6. **[L-167 An admin or force merge override bypasses only one layer of branch protection, not all of them](engineering-lessons/git-ci-and-release-mechanics.md#l-167-an-admin-or-force-merge-override-bypasses-only-one-layer-of-branch-protection-not-all-of-them)**: An admin override defeats one protection layer while rulesets and org policy keep enforcing; know every layer before you reach for it.
7. **[L-135 An unexpectedly clean or complete-looking result is a signal to dig deeper, not proof of correctness](engineering-lessons/debugging-methodology.md#l-135-an-unexpectedly-clean-or-complete-looking-result-is-a-signal-to-dig-deeper-not-proof-of-correctness)**: An all-clear result that arrives too easily usually means the failing cases were filtered out upstream; force the check onto a case that must fail.
8. **[L-134 Sanity-check a computed number against a source that is structurally independent of it](engineering-lessons/debugging-methodology.md#l-134-sanity-check-a-computed-number-against-a-source-that-is-structurally-independent-of-it)**: A number reconciled against its own predecessor proves nothing; check it against a source that cannot share the same mistake.
9. **[L-106 Give each concurrent agent session its own worktree; a shared checkout lets one session strand another's work](lessons/worktrees-and-concurrent-sessions.md#l-106-give-each-concurrent-agent-session-its-own-worktree-a-shared-checkout-lets-one-session-strand-anothers-work)**: Two sessions in one checkout will strand each other's branches; give every concurrent task its own worktree by default.
10. **[L-149 Never name a shell variable after one of the shell's special or read-only parameters](engineering-lessons/general-engineering-gotchas.md#l-149-never-name-a-shell-variable-after-one-of-the-shells-special-or-read-only-parameters)**: A loop or status variable named after one of the shell's special parameters fails outright in one shell and silently misbehaves in another; check the special-parameter list first.
11. **[L-118 When two systems track the same fact, assign one authoritative source per field](engineering-lessons/data-and-sql-correctness.md#l-118-when-two-systems-track-the-same-fact-assign-one-authoritative-source-per-field)**: When two systems both hold a fact, pick one authoritative source per field before comparing, or every disagreement becomes a debate.
12. **[L-117 NULL does not behave the way SQL and dataframe operators imply](engineering-lessons/data-and-sql-correctness.md#l-117-null-does-not-behave-the-way-sql-and-dataframe-operators-imply)**: NULL breaks equality, IN, aggregates, and array functions in ways that look like missing data; decide explicitly what each operator should do with it.
13. **[L-108 A locked local port, browser profile, or dev server may belong to a sibling session, so use a different one rather than forcing it](lessons/worktrees-and-concurrent-sessions.md#l-108-a-locked-local-port-browser-profile-or-dev-server-may-belong-to-a-sibling-session-so-use-a-different-one-rather-than-forcing-it)**: A busy port or locked browser profile is often a sibling session, not a stale process; take a different one instead of killing it.
14. **[L-021 Headless or scheduled automation cannot complete an interactive MFA or SSO login](lessons/headless-and-scheduled-automation.md#l-021-headless-or-scheduled-automation-cannot-complete-an-interactive-mfa-or-sso-login)**: Unattended runs cannot answer an MFA prompt; preflight the cached session and design the fallback before the schedule fires.
15. **[L-072 Checkpoint long-running work to a tracked file as you go, before a usage or context limit forces a stop](lessons/session-continuity-and-usage.md#l-072-checkpoint-long-running-work-to-a-tracked-file-as-you-go-before-a-usage-or-context-limit-forces-a-stop)**: A killed session keeps nothing you did not write down; checkpoint each verified finding to a tracked file as you go.
16. **[L-038 Structural enforcement holds; prose instructions and standing rules erode over time](lessons/hooks-and-guardrails.md#l-038-structural-enforcement-holds-prose-instructions-and-standing-rules-erode-over-time)**: Rules that live only in prose erode as sessions and models change; encode anything that must hold as a hook, lint, or generator step.
17. **[L-163 Squash merges break git's own ancestry-based merge detection](engineering-lessons/git-ci-and-release-mechanics.md#l-163-squash-merges-break-gits-own-ancestry-based-merge-detection)**: In a squash-merge workflow, branch --merged and cherry cannot tell you a branch has landed; ask the pull request, not the commit graph, before you delete anything.
18. **[L-179 Route secrets through stdin or a file, never through chat text or a CLI argument](engineering-lessons/secrets-and-access-control.md#l-179-route-secrets-through-stdin-or-a-file-never-through-chat-text-or-a-cli-argument)**: Secrets pasted into chat or passed as CLI arguments land in transcripts, shell history, and process lists; route them through stdin or a file.
19. **[L-178 Code that works under your own elevated local credentials can break once deployed](engineering-lessons/secrets-and-access-control.md#l-178-code-that-works-under-your-own-elevated-local-credentials-can-break-once-deployed)**: Your personal credentials are broader than the deployed identity, so test under the real service account or app role before calling a permission-dependent change done.
20. **[L-150 A scheduled job can silently self-disarm or fail with no alert](engineering-lessons/general-engineering-gotchas.md#l-150-a-scheduled-job-can-silently-self-disarm-or-fail-with-no-alert)**: A job gated on its own last success can disarm itself forever, and its log is not an alert; pair every schedule with an independent check.
<!-- digest:end -->

## All lessons by theme

Lessons about using coding agents:

| Theme | File |
|---|---|
| Context and Instruction Files | [lessons/context-and-instruction-files.md](lessons/context-and-instruction-files.md) |
| Knowledge Bases, Memory and Source of Truth | [lessons/knowledge-and-source-of-truth.md](lessons/knowledge-and-source-of-truth.md) |
| Hooks, Guardrails and Enforcement | [lessons/hooks-and-guardrails.md](lessons/hooks-and-guardrails.md) |
| Skills and Plugin Management | [lessons/skills-and-plugin-management.md](lessons/skills-and-plugin-management.md) |
| Subagents and Model Selection | [lessons/subagents-and-model-selection.md](lessons/subagents-and-model-selection.md) |
| Session Continuity and Usage Management | [lessons/session-continuity-and-usage.md](lessons/session-continuity-and-usage.md) |
| Worktrees and Concurrent Sessions | [lessons/worktrees-and-concurrent-sessions.md](lessons/worktrees-and-concurrent-sessions.md) |
| Review Discipline and Claiming Done | [lessons/review-discipline.md](lessons/review-discipline.md) |
| Headless and Scheduled Automation | [lessons/headless-and-scheduled-automation.md](lessons/headless-and-scheduled-automation.md) |
| Agent Security and Untrusted Data | [lessons/agent-security-and-untrusted-data.md](lessons/agent-security-and-untrusted-data.md) |

General engineering lessons the agent work surfaced:

| Theme | File |
|---|---|
| Debugging Methodology | [engineering-lessons/debugging-methodology.md](engineering-lessons/debugging-methodology.md) |
| Verification Tooling and Test Rigor | [engineering-lessons/verification-tooling-rigor.md](engineering-lessons/verification-tooling-rigor.md) |
| Git, CI and Release Mechanics | [engineering-lessons/git-ci-and-release-mechanics.md](engineering-lessons/git-ci-and-release-mechanics.md) |
| Secrets, Credentials and Access Control | [engineering-lessons/secrets-and-access-control.md](engineering-lessons/secrets-and-access-control.md) |
| Data and SQL Correctness | [engineering-lessons/data-and-sql-correctness.md](engineering-lessons/data-and-sql-correctness.md) |
| General Engineering Gotchas | [engineering-lessons/general-engineering-gotchas.md](engineering-lessons/general-engineering-gotchas.md) |

## How to read a lesson

Every entry has the same shape, so you can skim by symptom:

- **Symptom**: what you observe when the trap bites.
- **Rule**: the one thing to do about it, written as an instruction.
- **Why**: one sentence on the mechanism, with no names, dates, or counts, on purpose.
- **Confidence**, **First seen**, **Applies to**, **Scope**: how much to trust it, when it first showed up, which tools or versions it holds for, and whether it is agent-agnostic, Claude Code first, or Claude Code only.
- **Beyond the docs**: when a lesson links vendor documentation, what the incident adds that the docs do not say.

Lesson IDs are stable and deliberately not contiguous: an ID that is missing
belongs to a lesson that is still in verification or was retired, and it will
not be reused.

The source of truth is [lessons/lessons.json](lessons/lessons.json); the
markdown is rendered from it, so you can also load the JSON straight into an
agent. See [CONTRIBUTING.md](CONTRIBUTING.md) for the field rules.

## Using this with other coding agents

Most lessons are tagged `agent-agnostic`. Where a lesson is Claude Code
specific (a hook schema quirk, a plugin manifest rule, a settings key) it says
so in its Scope line, and where I have evidence of an equivalent elsewhere it
carries an "Other agents" note. The starter kit ships its working-style rules
as `AGENTS.md`, which Codex reads natively and Claude Code and Gemini CLI reach
through one-line stub files. Hook wiring and subagent frontmatter are Claude
Code only; the patterns behind them are not.

## Starter kit

[starter-kit/](starter-kit/) holds the portable config I actually use:
tool-neutral working-style rules, a reconnaissance subagent that is told never to edit (by instruction, not enforcement), an
advisory post-edit lint hook with its settings wiring, and two pattern
writeups (cross-session memory conventions, budgeted session-start context
injection). Its [README](starter-kit/README.md) has per-tool install steps
and says what to edit first.

## How I measured my own usage

[usage-audit/README.md](usage-audit/README.md) covers `/insights`, `/doctor`,
`claude doctor`, `/skill-doctor`, `/usage`, `/context`, and a homegrown monthly
audit: what each is good for, what I found, and what I changed.

## How this repo was built

Lessons were swept from my own session logs and memory files, abstracted by
incident, deduplicated, cut by an editor pass and a second-model review, then
rewritten into the schema. Each published lesson cleared independent privacy,
genericity, and evidence reviews bound to a content hash, plus a stricter
fourth review where the sources were domain-heavy. The tree passes a
structural leak scanner, a private term denylist, a secrets scan, a read by a
reviewer with no context, and a second-model review before it ships.
[SOURCES.md](SOURCES.md) has the details and what is deliberately absent.
[ROADMAP.md](ROADMAP.md) has the current build status and what comes next.

## Related repos

- [data-ai-reference](https://github.com/kyle-chalmers/data-ai-reference): the teaching repo, including a complete Claude Code guide for data teams.
- [next-session-prompt](https://github.com/kyle-chalmers/next-session-prompt): save a session as a resume prompt before context runs out.
- [skill-chain](https://github.com/kyle-chalmers/skill-chain): turn a repeated workflow into a chain of small skills.
- [ai-friend-review](https://github.com/kyle-chalmers/ai-friend-review): have other local AI coding agents review your work.
- [clean-claude-code-debug-logs](https://github.com/kyle-chalmers/clean-claude-code-debug-logs): keep the debug log directory from eating your disk.

## Contributing and license

Read [CONTRIBUTING.md](CONTRIBUTING.md) first; `bash scripts/verify.sh` is the
gate every change has to pass. MIT licensed, see [LICENSE](LICENSE).

# Worktrees & Concurrent Sessions

**Scope:** Running several coding-agent sessions in parallel on the same machine and repo without one silently stepping on another.

I run more than one agent session at a time, each in its own git worktree, and that setup has its own failure modes: a stale local branch, a force-push that strands a sibling session, a port or browser profile two sessions both think they own. These lessons are the isolation rules that keep parallel sessions from corrupting each other's work.

Lessons in this file: 7

- [L-106 Give each concurrent agent session its own worktree; a shared checkout lets one session strand another's work](#l-106-give-each-concurrent-agent-session-its-own-worktree-a-shared-checkout-lets-one-session-strand-anothers-work)
- [L-108 A locked local port, browser profile, or dev server may belong to a sibling session, so use a different one rather than forcing it](#l-108-a-locked-local-port-browser-profile-or-dev-server-may-belong-to-a-sibling-session-so-use-a-different-one-rather-than-forcing-it)
- [L-109 Confirm a worktree is truly inert before deleting it: clean tree, no unpushed commits, PR actually merged](#l-109-confirm-a-worktree-is-truly-inert-before-deleting-it-clean-tree-no-unpushed-commits-pr-actually-merged)
- [L-110 A coding agent's worktree-cleanup command only removes worktrees it created itself this session](#l-110-a-coding-agents-worktree-cleanup-command-only-removes-worktrees-it-created-itself-this-session)
- [L-111 Treat git-clean and session-attached as separate cleanup signals](#l-111-treat-git-clean-and-session-attached-as-separate-cleanup-signals)
- [L-112 Confirm the working directory and branch before editing when several worktrees or repos are open](#l-112-confirm-the-working-directory-and-branch-before-editing-when-several-worktrees-or-repos-are-open)
- [L-115 Rebase onto a shared branch instead of force-pushing over it](#l-115-rebase-onto-a-shared-branch-instead-of-force-pushing-over-it)

---

### L-106 Give each concurrent agent session its own worktree; a shared checkout lets one session strand another's work

**Symptom:** Two or more sessions, agent or human, work against the same shared repository checkout at the same time. One switches the checkout's branch, or lands work against a shared target branch, while another still has uncommitted changes sitting there.

**Rule:** In any workflow where more than one session might touch the same repository concurrently, including your own parallel sessions, give each concurrent task its own isolated worktree or clone by default rather than sharing one working directory or relying on turn taking. Budget for extra rebase cycles as sibling sessions land ahead of each other on a shared target branch, and commit work before removing a worktree, pushing it when the machine or environment is ephemeral so nothing depends on the local checkout surviving.

**Why:** Sharing one working directory across concurrent sessions lets any session's branch switch or checkout change silently overwrite or strand another session's in progress, uncommitted work, and the collision recurs across separate projects until per task worktrees become the default.

**Confidence:** High (Recurred across many independent projects and sessions.). **First seen:** 2026-05. **Applies to:** any coding agent workflow running multiple concurrent sessions against the same repository, not version specific. **Scope:** agent-agnostic.
**Beyond the docs:** The git docs explain how to create a worktree but not that skipping this in a multi session agent workflow is what actually causes stranded work and repeated rebase churn.
**Related:** [git worktree](https://git-scm.com/docs/git-worktree)

### L-108 A locked local port, browser profile, or dev server may belong to a sibling session, so use a different one rather than forcing it

**Symptom:** Parallel agent sessions on the same machine collide on shared local resources: a default port is already bound, an automation profile is exclusively locked, or a preview looks unchanged after an edit because a different session's process is still serving old content on that same port.

**Rule:** When a default local port, browser profile, or other exclusive resource is already taken by a process you don't recognize as your own, switch to a distinct port or profile, or verify what is actually being served, rather than killing or forcing a resource you can't be sure is safe to kill.

**Why:** Concurrent sessions on one machine share the operating system's pool of ports and locks, so one session's process can silently occupy a resource another session assumes is free, and this recurred.

**Confidence:** High (Corroborated across multiple independent occurrences involving different kinds of shared resources.). **First seen:** 2026-05. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-109 Confirm a worktree is truly inert before deleting it: clean tree, no unpushed commits, PR actually merged

**Symptom:** A worktree looks stale, for example it is old or its branch name suggests it is done, and a cleanup pass is tempted to remove it based on age or a merged-looking branch alone.

**Rule:** Before deleting any worktree, explicitly verify three things: the working tree is clean, there are no unpushed commits, and its associated PR is confirmed merged upstream via the hosting platform, not local git state or branch age alone. Any one check failing means leave it alone.

**Why:** Local git state such as branch name or last-modified time carries no guarantee about whether a branch's work has actually landed upstream, so relying on it to judge a worktree safe to delete can discard commits that were never pushed or merged.

**Confidence:** High (Corroborated across six independent incidents in different repos.). **First seen:** 2026-05. **Applies to:** git worktrees, not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs describe worktree mechanics but not the three-part safety checklist an agent needs to avoid deleting a worktree that only looks finished.
**Related:** [git worktree](https://git-scm.com/docs/git-worktree)

### L-110 A coding agent's worktree-cleanup command only removes worktrees it created itself this session

**Symptom:** Running the agent's own worktree-exit or cleanup command reports success but leaves the worktree directory in place when that worktree was set up by the outer harness at launch, or created manually with the underlying VCS command, instead of by that same tool mid-session.

**Rule:** Before trusting a coding agent's built-in worktree teardown command, check whether that same tool created the worktree earlier in this session; if it was provisioned at launch or made manually, expect the cleanup call to silently no-op and remove the worktree with the underlying git command instead.

**Why:** A worktree-teardown tool that only tracks worktrees it provisioned itself has no record of ones created outside its own session, so it reports success while leaving them on disk.

**Confidence:** High (Recurred across five separate incidents over two months, consistently the same failure mode.). **First seen:** 2026-06. **Applies to:** Claude Code's worktree exit and cleanup tooling; check whether other agents' equivalent commands share the same session-scoped limitation. **Scope:** claude-code-specific. **Last verified:** 2026-09.

### L-111 Treat git-clean and session-attached as separate cleanup signals

**Symptom:** An automated cleanup tool flags a worktree or branch for deletion because it is merged and has no uncommitted changes, even while a coding-agent session is still actively working inside that directory.

**Rule:** When automating cleanup of shared working directories or branches, check for an attached or active process as its own signal, separate from git merge-cleanliness, before proposing or performing a delete.

**Why:** A cleanliness check based only on git state (merged, no diff) cannot detect a live process working in that directory, so it treats an in-progress session as abandoned.

**Confidence:** High (Corroborated across multiple independent occurrences of the same gap.). **First seen:** 2026-07. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-112 Confirm the working directory and branch before editing when several worktrees or repos are open

**Symptom:** A batch of edits, or a create, commit, or push action, lands cleanly but turns out to have happened in the wrong local checkout, on the wrong branch, or in the wrong repository, because the working directory wasn't what was assumed at that point.

**Rule:** Before starting an edit session or any repo-scoped action when multiple worktrees, checkouts, or sibling repositories are open, confirm the actual current working directory and branch match your intended target, not just that a shell in the general area is open.

**Why:** A shell or session can silently retain a working directory from an earlier command instead of the one the operator intends, so edits and repo-scoped actions land wherever that stale directory points rather than where they were meant to go, and this recurred across different sessions.

**Confidence:** Medium (Merged from three independent incidents, corroborating the same failure mode.). **First seen:** 2026-06. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-115 Rebase onto a shared branch instead of force-pushing over it

**Symptom:** Two sessions, agent or human, push commits to the same branch independently, and a force-push from either one would silently discard the other's work with no warning.

**Rule:** When you discover a branch might be shared with another active session or collaborator, rebase your own not-yet-pushed local commits onto the current origin HEAD before you push, instead of force-pushing over whatever is there. This is about updating your own unshared work onto the latest remote tip, not about rewriting a branch that others have already pulled or built on, which carries its own separate risk.

**Why:** A force-push overwrites whatever is on the remote branch at that moment, so if another session pushed in between, its commits are simply gone with no conflict or warning to catch it, while rebasing your own unpushed commits onto the current remote tip incorporates both sides instead of discarding one.

**Confidence:** High (Directly observed and stated as a rule in the source.). **First seen:** 2026-06. **Applies to:** not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The git docs explain what rebase and force-push do mechanically, and separately warn against rebasing a branch others have already based work on; they do not cover the concurrent-session trigger addressed here, that a branch might currently be shared with another active agent session, not just a human collaborator, which is why the rule is scoped to rebasing your own unpushed commits rather than rewriting shared history.
**Related:** [git rebase](https://git-scm.com/docs/git-rebase)

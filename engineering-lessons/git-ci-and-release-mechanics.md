# Git, CI & Release Mechanics

**Scope:** Git and CI/CD mechanics that behave differently from how they read: merges, branch protection, deploy pipelines, and identity.

Git and CI hide a lot of behavior that only shows up once: a squash merge that breaks history detection, a required check that becomes permanently unrunnable, a merge that is itself the deploy step. These lessons are the mechanics I now check before I trust a pipeline or a merge to mean what it looks like it means.

Lessons in this file: 15

- [L-161 Piping a command, wrapping it in a subshell, or letting a hook rewrite a file can hide its real exit code](#l-161-piping-a-command-wrapping-it-in-a-subshell-or-letting-a-hook-rewrite-a-file-can-hide-its-real-exit-code)
- [L-162 A green CI check is not proof it is wired up, enforced, or checking what it claims](#l-162-a-green-ci-check-is-not-proof-it-is-wired-up-enforced-or-checking-what-it-claims)
- [L-163 Squash merges break git's own ancestry-based merge detection](#l-163-squash-merges-break-gits-own-ancestry-based-merge-detection)
- [L-164 A stalled auto-merge or 'behind base' status is usually expected rebase-cycle behavior, not a dead trigger](#l-164-a-stalled-auto-merge-or-behind-base-status-is-usually-expected-rebase-cycle-behavior-not-a-dead-trigger)
- [L-165 Dependency and CVE scans or unpinned tool versions can fail a PR for reasons unrelated to its diff](#l-165-dependency-and-cve-scans-or-unpinned-tool-versions-can-fail-a-pr-for-reasons-unrelated-to-its-diff)
- [L-166 Auto-generated or aggregated files must be regenerated on conflict, never hand-merged](#l-166-auto-generated-or-aggregated-files-must-be-regenerated-on-conflict-never-hand-merged)
- [L-167 An admin or force merge override bypasses only one layer of branch protection, not all of them](#l-167-an-admin-or-force-merge-override-bypasses-only-one-layer-of-branch-protection-not-all-of-them)
- [L-168 Merge succeeding, CI passing, or a scheduled job running are different claims from the change being live](#l-168-merge-succeeding-ci-passing-or-a-scheduled-job-running-are-different-claims-from-the-change-being-live)
- [L-170 A branch checked out in a worktree can silently block merge cleanup, branch deletion, or history rewrites](#l-170-a-branch-checked-out-in-a-worktree-can-silently-block-merge-cleanup-branch-deletion-or-history-rewrites)
- [L-171 A clean rebase --onto can still silently drop a scaffolding dependency or leave generated files stale](#l-171-a-clean-rebase---onto-can-still-silently-drop-a-scaffolding-dependency-or-leave-generated-files-stale)
- [L-173 A machine can hold several git or GitHub identities that silently diverge, so verify which one is active](#l-173-a-machine-can-hold-several-git-or-github-identities-that-silently-diverge-so-verify-which-one-is-active)
- [L-174 Whether a push dismisses PR approval or auto-merge is a per-repo setting, not universal git behavior](#l-174-whether-a-push-dismisses-pr-approval-or-auto-merge-is-a-per-repo-setting-not-universal-git-behavior)
- [L-175 Automated or bulk code changes need behavioral verification beyond a clean diff review](#l-175-automated-or-bulk-code-changes-need-behavioral-verification-beyond-a-clean-diff-review)
- [L-176 Blanket stage-everything commands in a shared or dirty checkout sweep in unrelated junk](#l-176-blanket-stage-everything-commands-in-a-shared-or-dirty-checkout-sweep-in-unrelated-junk)
- [L-177 Local git state (branch, main, or worktree) goes stale silently and misleads decisions](#l-177-local-git-state-branch-main-or-worktree-goes-stale-silently-and-misleads-decisions)

---

### L-161 Piping a command, wrapping it in a subshell, or letting a hook rewrite a file can hide its real exit code

**Symptom:** A commit, test run, or CI status check reports success in the terminal even though the guarded step actually failed, because the visible output came from a later stage in a pipe or wrapper rather than from the command whose result actually matters.

**Rule:** Capture and check the exit status of the command you actually care about, not the last thing in a pipeline or subshell: avoid piping a status-bearing command through a filter (or use a pipefail-aware shell and inspect PIPESTATUS), avoid subshell wrappers that discard $?, and after any auto-formatting pre-commit hook fires, re-stage its rewrite and re-run the check rather than trusting the first pass or amending past it.

**Why:** A shell pipeline or subshell reports the exit status of its last stage, and an auto-reformatting pre-commit hook rewrites the file after the outer command already captured a status, so in each case the status the caller sees describes the wrapper or the hook rather than the actual step being verified.

**Confidence:** High (Recurred across many independent shell-scripting, CI-watch, and pre-commit hook contexts over several months.). **First seen:** 2026-06. **Applies to:** POSIX shells (bash/zsh) and CI runners, not version-specific. **Scope:** agent-agnostic.

### L-162 A green CI check is not proof it is wired up, enforced, or checking what it claims

**Symptom:** Documentation says a check is required, or a check's name implies it validates something, but in practice the check was never registered as a branch protection requirement, was quietly removed from the workflow, only self tests its own presence rather than real content, or a checkout mode silently skips a step so the pipeline stays green without having verified anything.

**Rule:** Treat a green CI badge or a required check label as a claim to verify, not a fact: confirm the check is actually registered as a branch protection requirement, confirm it read a checkout with the credentials and depth it needs, and confirm a self test exercises real behavior rather than just checking that a file exists. A check with no history of ever failing is unverified, not passing.

**Why:** A workflow file, a branch protection rule, and a check's own test logic are three separate configurations that can drift out of sync, so a badge can stay green even after the thing it names has stopped being enforced or stopped checking real content.

**Confidence:** High (Recurred many times across multiple repositories and months, converging on the same green does not mean enforced rule across many different kinds of gates.). **First seen:** 2026-06. **Applies to:** not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs explain how to configure workflows and required checks but not that these three layers, the workflow file, the branch protection setting, and the check's own test content, drift independently and each needs separate verification.
**Related:** [GitHub Actions](https://docs.github.com/en/actions)

### L-163 Squash merges break git's own ancestry-based merge detection

**Symptom:** Commands like git branch --merged, git cherry, ancestry-based log checks, and even a merge tool's own exit code report a branch as unmerged, or fail to confirm it landed, after it was actually squash merged, because the squashed commit has no ancestry link back to the source branch's own commits.

**Rule:** In a squash-merge workflow, do not trust commit-ancestry tools such as branch --merged, cherry, or a commit graph to decide whether a branch is safe to delete or a fix has landed. Check the pull request platform's own merge record instead, and treat a stale, un-fetched local main as an added source of false negatives.

**Why:** A squash merge writes one new commit onto the target branch that has no parent link to the source branch's individual commits, so any tool that decides mergedness by walking commit ancestry sees no connection and reports the branch as unmerged even though its content already landed.

**Confidence:** High (A high number of independent write-ups of the same trap across many months and repos indicates this is a durable, well-confirmed pattern rather than a one-off.). **First seen:** 2026-05. **Applies to:** any repo using GitHub squash merge, or an equivalent squash workflow, not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs describe what --merged and cherry compute but do not warn that squash merging makes their ancestry check return false negatives, so a passing or failing result from either command cannot be trusted on its own in a squash-merge repo.
**Related:** [git-branch](https://git-scm.com/docs/git-branch), [git-cherry](https://git-scm.com/docs/git-cherry)

### L-164 A stalled auto-merge or 'behind base' status is usually expected rebase-cycle behavior, not a dead trigger

**Symptom:** An armed auto-merge pull request, or a 'mergeable' status, sits blocked because the branch has fallen behind the base branch under a require-branches-up-to-date rule. This looks identical to a genuinely dead or stuck CI trigger and is easy to misdiagnose as broken automation needing a manual override, when it only needs a rebase or more time for CI dispatch lag to clear.

**Rule:** When an auto-merge or required check looks stuck, first check whether the branch is simply behind the base branch under a require-up-to-date rule, then rebase and wait for checks, before concluding the CI trigger is dead. Also cancel a genuinely stale pending run before approving a newer one, and check the PR's actual status before pushing more commits to a shared branch.

**Why:** A require-up-to-date branch protection rule and a dead CI trigger produce the same visible symptom, a pull request that will not merge, so the two causes are indistinguishable without checking the branch's actual position relative to the base.

**Confidence:** High (Recurred often across multiple repositories over several months.). **First seen:** 2026-05. **Applies to:** GitHub branch protection with a require-branches-up-to-date rule, not version-specific. **Scope:** agent-agnostic. **Last verified:** 2026-09.
**Beyond the docs:** The docs describe branch protection settings but not that a stalled auto-merge from a stale branch is visually indistinguishable from a dead CI trigger, which leads to unnecessary manual overrides.
**Related:** [GitHub Actions docs](https://docs.github.com/en/actions)

### L-165 Dependency and CVE scans or unpinned tool versions can fail a PR for reasons unrelated to its diff

**Symptom:** A newly disclosed CVE, a time dependent vulnerability scan, or an unpinned CI action, lint tool, or dependency silently auto upgrading can fail CI on a pull request that changed none of the affected code, sometimes across many unrelated pull requests at once, and a skipped scan result must not be read as passing rather than as a blocker.

**Rule:** When a dependency scan or version pinned CI step fails on a PR that touches unrelated code, first check whether it is a time dependent scan reacting to a new CVE or an unpinned tool or action drifting version, rather than assuming your change caused it; then either accept or patch the finding or pin the tool. Investigate why an existing version cap exists before removing it, and pin third party CI actions to a commit SHA rather than a mutable tag to prevent this from recurring.

**Why:** A CI step that scans live vulnerability databases or resolves an unpinned dependency, action, or tool version evaluates the state of the outside world at run time rather than the diff under review, so it can start failing or passing independent of any code change and recurred across unrelated pull requests as a result.

**Confidence:** High (One of the largest recurring clusters observed, spanning many repositories with a consistent root cause.). **First seen:** 2026-06. **Applies to:** CI/CD pipelines with dependency or CVE scanning steps, or unpinned third party actions or tools; not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs explain how to reference an action by tag or SHA; they do not say that a mutable tag drifting or a live CVE scan can fail unrelated PRs on the same day with no code change, which is the failure mode to triage for before assuming the diff is at fault.
**Related:** [GitHub Actions documentation](https://docs.github.com/en/actions)

### L-166 Auto-generated or aggregated files must be regenerated on conflict, never hand-merged

**Symptom:** Merge conflicts or rebases touching an auto-generated index, catalog, or aggregate file get resolved by hand-editing the generated file, which then silently drifts from what the generator would actually produce: sometimes passing CI green while being wrong, reverting real content, or causing a rebase to loop forever if a hook keeps re-touching the file.

**Rule:** Never hand-merge conflicts in a generated file. Rebase, don't reset, onto the latest version of a fast-moving generated or shared file, then re-run the generator and commit its output. Add a CI check that regenerates the file and diffs it against what is committed, so drift cannot go green.

**Why:** A generated file's committed content is a derived artifact of its inputs and generator logic, so editing it by hand resolves the textual conflict without reproducing what the generator would actually output from the merged inputs, leaving the two silently out of sync.

**Confidence:** High (Recurred repeatedly across multiple repositories over several months, converging on the same regenerate-don't-hand-merge rule.). **First seen:** 2026-07. **Applies to:** not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs explain how rebase replays commits, but not that a fast-moving generated file specifically needs its generator re-run after the rebase rather than its conflicts hand-resolved.
**Related:** [git rebase](https://git-scm.com/docs/git-rebase)

### L-167 An admin or force merge override bypasses only one layer of branch protection, not all of them

**Symptom:** A repository can have multiple independent enforcement layers, such as classic branch protection, a repository ruleset, and an org wide policy, and an admin or bypass merge flag that overrides one layer, for example required status checks, does not override another, so a merge that looks admin forced can still be blocked or can still violate policy. Separately, branch protection settings are often updated through an API that does a full replace, so a partial update silently drops any field left out of the request.

**Rule:** Before reaching for an admin or bypass merge override, identify every enforcement layer on the repo, branch protection, ruleset, and org policy, and confirm which ones the override actually affects. Reserve overrides for genuine failures rather than transient lag, and route changes around protection through a normal pull request instead of force pushing. When updating branch protection settings through an API, always send the full desired configuration, since a replace style update drops anything not included.

**Why:** An admin or bypass merge override defeats only the specific enforcement layer it targets, such as required status checks, so a separate independent layer like an org wide ruleset or approval policy can still block the merge or still be silently violated even after the override succeeds, and the pattern recurs across many repositories.

**Confidence:** High (Recurred across many independent repositories and ruleset configurations.). **First seen:** 2026-06. **Applies to:** GitHub repositories with more than one enforcement layer, such as branch protection plus a repository or org ruleset, not version specific. **Scope:** agent-agnostic. **Last verified:** 2026-09.
**Beyond the docs:** The docs describe the branch protection endpoints but not that an admin or bypass merge override only defeats the specific layer it targets while a separate independent layer such as an org ruleset can still block or be violated, nor do they call out that an update through this API replaces rather than merges the settings you send.
**Related:** [GitHub branch protection REST API](https://docs.github.com/en/rest/branches/branch-protection)

### L-168 Merge succeeding, CI passing, or a scheduled job running are different claims from the change being live

**Symptom:** A merge landing, a deploy pipeline reporting success, a scheduled job executing, or a ticket being marked deployed are each treated as proof the intended change is now live and working, but a deploy can report success while the pointer that selects the running version never moves to the new build, a scheduled job can run without including a specific fix, a merge shortly before a scheduled run may or may not make that cycle, and a fix in one system doesn't guarantee a related manual or dependent system got fixed too.

**Rule:** Verify live and working as a claim separate from merged, deployed successfully, or job ran. Confirm the running version actually advanced, confirm a scheduled run specifically included your change rather than just that the schedule fired, and check any manually maintained system that depends on the automated fix before calling the whole thing resolved.

**Why:** Each of these systems reports success at its own boundary (the merge committed, the pipeline exited zero, the cron fired), none of which observes whether the artifact that boundary produced actually reached the running system or included the intended change, so the gap between them stays invisible until someone checks live behavior directly.

**Confidence:** High (Recurred across many incidents spanning deploy pointers, scheduled jobs, and cross-system fixes.). **First seen:** 2026-05. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-170 A branch checked out in a worktree can silently block merge cleanup, branch deletion, or history rewrites

**Symptom:** A merge tool's own post-merge cleanup step, a branch-delete command, or a history-rewrite tool fails or refuses to run, not because the underlying git operation is wrong, but because a linked worktree still has that branch checked out, which git treats as in-use.

**Rule:** Before deleting a branch, running a history-rewrite tool, or trusting an automated merge tool's full cleanup, check for and remove or detach any worktree that has the branch checked out. A failure at this step does not mean the merge or rewrite itself failed.

**Why:** Git refuses to delete or rewrite a branch that is checked out in any linked worktree, so a cleanup or rewrite step can fail purely on that lock even after the underlying merge or history change already succeeded elsewhere.

**Confidence:** High (Confirmed across ten incidents spanning merge cleanup and history-rewrite contexts.). **First seen:** 2026-05. **Applies to:** git worktrees, not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs state that a checked-out branch cannot be deleted, but not that this same lock silently derails an automated merge tool's cleanup step or a history-rewrite tool, producing a failure that looks unrelated to worktrees.
**Related:** [git worktree](https://git-scm.com/docs/git-worktree), [git branch](https://git-scm.com/docs/git-branch)

### L-171 A clean rebase --onto can still silently drop a scaffolding dependency or leave generated files stale

**Symptom:** A rebase or rebase --onto completes with zero textual conflicts, yet a commit that got skipped turns out to have been a genuine dependency for the commits that followed it, or derived and generated files are left semantically stale even though nothing conflicted.

**Rule:** Before committing to a rebase strategy, run a merge-tree dry run to preview the actual result, and specifically check whether any commit you plan to skip in a rebase --onto is a true dependency of the commits that follow it. On a collaborator's still-open branch, prefer a merge-update over a rebase, since rebase rewrites history they may already have pulled.

**Why:** Rebase resolves conflicts at the text level, so it can complete cleanly while dropping a commit that later work still depended on for reasons git's conflict detection has no way to see.

**Confidence:** High (Recurred across ten incidents over several months, all describing the same rebase-hazard mechanism.). **First seen:** 2026-05. **Applies to:** git rebase and rebase --onto, any version; agent-agnostic. **Scope:** agent-agnostic.
**Beyond the docs:** The git docs describe rebase --onto's mechanics but don't warn that a clean, conflict-free result can still be semantically wrong when a skipped commit was actually a dependency of later work.
**Related:** [git-rebase](https://git-scm.com/docs/git-rebase), [git-merge-tree](https://git-scm.com/docs/git-merge-tree)

### L-173 A machine can hold several git or GitHub identities that silently diverge, so verify which one is active

**Symptom:** git push, a CLI tool's own auth, and stored credentials such as env-var tokens, keychain OAuth entries, or credential helpers can each authenticate as a different account on the same machine, and a resumed session or a credential-helper's precedence order can flip which account is active without any explicit signal. A credential that is enough to push may still lack a narrower permission such as creating a release, and several failures at once can mean one session-level auth block rather than several separately bad credentials.

**Rule:** Before trusting a push, a pull request creation, or a release action, check which account or token is actually authenticating. Do not assume a CLI tool's own auth and git's push auth are the same account, do not assume a resumed session kept the identity you expect, and pin credential-helper precedence explicitly whenever more than one identity exists on a machine.

**Why:** Multiple stored credentials and helpers on one machine can each resolve to a different identity, and a resumed session or helper precedence order can flip which one is active without warning, so the same class of silent identity mismatch recurred across pushes, PR creation, and release actions.

**Confidence:** High (Recurred across many incidents spanning session resume, credential-helper precedence, and env-var identity conflicts.). **First seen:** 2026-06. **Applies to:** not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs describe how credential helpers are invoked but not that a resumed CLI session or an unpinned helper order can silently authenticate as the wrong account, or that a token can push while still lacking a narrower permission like creating a release.
**Related:** [git-credential](https://git-scm.com/docs/git-credential)

### L-174 Whether a push dismisses PR approval or auto-merge is a per-repo setting, not universal git behavior

**Symptom:** Pushing a new commit onto an already-approved PR, whether a rebase, a force-push, or a small docs or formatting fixup, dismisses the existing approval or clears an armed auto-merge flag on one repo but not on another, even though the same kind of push was made both times.

**Rule:** Check a specific repo's branch protection settings for 'dismiss stale reviews on push' and its auto-merge behavior before assuming a rebase, force-push, or fixup commit will or will not need re-review. Do not generalize from one repo's behavior to another, and where an approve-then-push race is possible, arm auto-merge before pushing rather than after.

**Why:** Whether a push clears an existing approval or auto-merge flag is controlled by a branch protection setting configured per repository, so the same git operation can produce opposite outcomes depending on which repo it runs against.

**Confidence:** High (Nine independent incidents converge on the same per-repo-configurable-setting explanation.). **First seen:** 2026-06. **Applies to:** GitHub repositories with branch protection rules, review dismissal and auto-merge behavior vary by repo configuration. **Scope:** agent-agnostic.

### L-175 Automated or bulk code changes need behavioral verification beyond a clean diff review

**Symptom:** An automated transformation, a large auto-generated diff, or a faithfully-ported migration reads as entirely correct in diff review, then breaks at runtime, quietly reintroduces a bug an earlier fix had already removed, or gets flagged as a regression by comparison tooling when the deviation was actually intentional; running only a scoped test subset on such a change can also miss cross-module collisions the full suite would catch.

**Rule:** For any automated transform, large auto-generated diff, or ported migration: run the full test command the CI pipeline runs, not a scoped subset; split a large risky diff into safe and risky parts and apply them separately; document intentional deviations inline so comparison tooling does not misflag them as regressions; and treat a clean diff review as necessary but not sufficient.

**Why:** A diff that reads as correct can still change runtime behavior, since diff review only checks what the text says changed while executing the code is what exposes what actually happens, and a scoped test subset carries the same blind spot against cross-module effects that only the full suite would catch.

**Confidence:** High (seven incidents across independent automated-change contexts converge on the same gap). **First seen:** 2026-06. **Applies to:** any automated code transform, generated diff, or ported migration, regardless of language or CI system. **Scope:** agent-agnostic.

### L-176 Blanket stage-everything commands in a shared or dirty checkout sweep in unrelated junk

**Symptom:** Running a broad add-all or an equivalent bulk restore or cleanup step in a working copy that has other unrelated dirty files, during conflict resolution, a baseline update, or a general commit, stages or discards files that don't belong to the current change, sometimes re-introducing a file that was deliberately removed or destroying someone else's unrelated in-progress edit.

**Rule:** In a shared or already-dirty checkout, stage explicit file paths or hunks for the current task, never a blanket add-all. Before committing, check for other unrelated dirty files and exclude them explicitly, and never let an automated restore-working-tree cleanup step run in a shared checkout without checking what it would discard.

**Why:** A blanket stage-all or restore command operates on the whole working tree by scope, so it cannot distinguish the current task's changes from someone else's unrelated edits sitting in the same checkout, and it recurred across both conflict resolution and routine commits.

**Confidence:** High (Seven incidents observed across secrets-handling and general commit contexts.). **First seen:** 2026-06. **Applies to:** git, in any shared or multi-branch working copy. **Scope:** agent-agnostic.
**Beyond the docs:** The docs describe what add-all and restore do to the tree but not that running them in a shared or already-dirty checkout will sweep in or discard files that belong to a different, unrelated change.
**Related:** [git-add](https://git-scm.com/docs/git-add), [git-restore](https://git-scm.com/docs/git-restore)

### L-177 Local git state (branch, main, or worktree) goes stale silently and misleads decisions

**Symptom:** Work is planned, diffed, or previewed against a local checkout of main, a branch, or a worktree that has not been fetched recently, and once someone else merges to the remote the local copy no longer matches it, with no warning from any of the normal git commands.

**Rule:** Fetch and verify against the live remote branch before diffing, rebuilding, or previewing anything, and never treat a local checkout, worktree, or 'current branch' assumption as accurate on its own, especially in a long-running or resumed session.

**Why:** A local checkout only reflects the remote as of its last fetch, so once anyone else pushes to that branch the local copy silently diverges and every diff, build, or preview run against it answers a question that no longer matches reality.

**Confidence:** High (Same stale-local-state root cause recurred across several distinct tasks (diffing, previewing, rebuilding).). **First seen:** 2026-05. **Applies to:** not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs explain what fetch does mechanically but not that skipping it before a diff, build, or preview produces a wrong answer with no error, especially across a resumed or long-running session.
**Related:** [git-fetch](https://git-scm.com/docs/git-fetch)

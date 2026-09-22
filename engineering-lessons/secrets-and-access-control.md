# Secrets, Credentials & Access Control

**Scope:** Handling secrets, credentials, and access grants so a leak, a stale token, or an overbroad permission does not go unnoticed.

A secret in git history, a credential that quietly expired, or a permission grant broader than it reads all fail the same way: nothing errors until the damage is already done. These lessons are how I handle credentials and access so those failures surface early instead of after the fact.

Lessons in this file: 9

- [L-178 Code that works under your own elevated local credentials can break once deployed](#l-178-code-that-works-under-your-own-elevated-local-credentials-can-break-once-deployed)
- [L-179 Route secrets through stdin or a file, never through chat text or a CLI argument](#l-179-route-secrets-through-stdin-or-a-file-never-through-chat-text-or-a-cli-argument)
- [L-180 Denylist, allowlist, and filename matching for security decisions must be exact and normalized](#l-180-denylist-allowlist-and-filename-matching-for-security-decisions-must-be-exact-and-normalized)
- [L-181 Path-containment checks must resolve real paths, not just collapse '..' or check only the parent](#l-181-path-containment-checks-must-resolve-real-paths-not-just-collapse--or-check-only-the-parent)
- [L-182 Run an automated, fail-closed leak scan across the whole tree before any internal code goes public](#l-182-run-an-automated-fail-closed-leak-scan-across-the-whole-tree-before-any-internal-code-goes-public)
- [L-183 Validating a file by its path and then reopening it to read it is a check-then-use race](#l-183-validating-a-file-by-its-path-and-then-reopening-it-to-read-it-is-a-check-then-use-race)
- [L-184 A long-lived credential that unattended automation depends on needs monitored rotation, not discovery after failure](#l-184-a-long-lived-credential-that-unattended-automation-depends-on-needs-monitored-rotation-not-discovery-after-failure)
- [L-185 A secrets sweep must check untracked working-tree files, not only committed history](#l-185-a-secrets-sweep-must-check-untracked-working-tree-files-not-only-committed-history)
- [L-187 Scrubbing sensitive strings from a repo you plan to make public requires rewriting history, not just current files](#l-187-scrubbing-sensitive-strings-from-a-repo-you-plan-to-make-public-requires-rewriting-history-not-just-current-files)

---

### L-178 Code that works under your own elevated local credentials can break once deployed

**Symptom:** A query, dashboard, or feature works fine in local development, then fails, returns empty results, or throws an authorization error only after deployment, with no local reproduction.

**Rule:** When a query or call depends on a permission-restricted resource, test it under the actual deployed identity, such as a service account or an app's owner role, not just your own broad personal credentials. Verify that runtime identity empirically rather than trusting documentation about how the app runs, since a resource being visible to you personally does not mean the running application can see it.

**Why:** Local development commonly runs under a broad personal credential while the deployed identity, whether a service account or an owner-rights execution model, can carry narrower or simply different access, so the gap only surfaces once the real runtime identity makes the call instead of yours.

**Confidence:** High (The same root cause recurred across several different platforms and projects, each time confirmed by reproducing the failure under the real runtime identity.). **First seen:** 2026-06. **Applies to:** any app, dashboard, or query that reads a permission-restricted resource and runs under a different identity than the developer's own, not version-specific. **Scope:** agent-agnostic.

### L-179 Route secrets through stdin or a file, never through chat text or a CLI argument

**Symptom:** A setup or automation plan has someone paste a password, API token, or webhook URL directly into an agent chat session, or pass it as a command-line flag or argument.

**Rule:** Route any secret into a system through a non-echoed prompt, stdin, a local file, or a secret manager's own input path. Never pass one as a CLI argument and never type or paste one into an agent chat. Treat any secret that was typed into chat or passed as a CLI argument as compromised and rotate it right away.

**Why:** A CLI argument and a chat message both get persisted, in shell history and process listings for the former and in the session transcript for the latter, so anything entered there stops being a secret the moment it's typed.

**Confidence:** High (Recurred across five independent sources spanning several months, all converging on the same fix.). **First seen:** 2026-06. **Applies to:** any credential entry into a CLI tool or coding agent chat, not version-specific. **Scope:** agent-agnostic.

### L-180 Denylist, allowlist, and filename matching for security decisions must be exact and normalized

**Symptom:** A security check meant to match one exact identifier or filename instead matches, or misses, other strings that merely share a prefix, differ in case, are quoted, or have whitespace or comments inserted, letting a forbidden pattern through or blocking an innocent one.

**Rule:** Build any allowlist, denylist, or sensitive-filename check on identifiers, table or schema names, or paths as an exact match or explicit token/boundary match, with inputs normalized (case folded, quoting and comments stripped, whitespace collapsed) on both sides before comparison, never a bare substring or prefix match. Normalize at the matching layer up front rather than patching one bypass class at a time, which will not converge.

**Why:** A security check implemented as a raw substring or prefix comparison treats any input sharing that pattern as equivalent, so a longer name with the same prefix, a different case, added quoting, or inserted comments each slip past the intended boundary until the comparison is normalized and matched exactly.

**Confidence:** High (Corroborated across three independent incidents, including a multi-round adversarial hardening effort and a matching false-positive case.). **First seen:** 2026-06. **Applies to:** Allowlist, denylist, and filename or identifier security checks in scanners and governance tooling; not version-specific. **Scope:** agent-agnostic.

### L-181 Path-containment checks must resolve real paths, not just collapse '..' or check only the parent

**Symptom:** A path-safety check that lexically strips '..' segments or only resolves a path's parent directory lets a crafted or symlinked path pass a containment test even though the actual target lies outside the allowed root.

**Rule:** When checking that a path stays inside an allowed root or sandbox, resolve the full real path first, following symlinks and verifying every intermediate segment actually exists, then compare that resolved path to the resolved root. Do not rely on a purely lexical collapse of '..' segments, and do not resolve only the parent directory while leaving the final component unresolved.

**Why:** A lexical '..'-collapsing check can be satisfied by a path through a directory that never existed, and a check that resolves only the parent directory misses a symlink placed inside the allowed area that itself points outside it, so both approaches can affirm containment for a path that ultimately resolves elsewhere.

**Confidence:** High (The same class of mistake, lexical or partial path resolution instead of full real-path resolution, recurred across independent features in the same codebase.). **First seen:** 2026-08. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-182 Run an automated, fail-closed leak scan across the whole tree before any internal code goes public

**Symptom:** A private file path, proprietary term, or internal schema or system name almost gets published because it was only caught by chance, or because fresh git history and denylists were handled but the tree was never swept automatically before the first public push.

**Rule:** Add an automated CI gate, or a one-time fail-closed scrub pass with negative test fixtures, that scans the entire working tree for proprietary terms, personal paths, secrets, and internal identifier prefixes before any public release or before the first commit or push of code extracted from an internal project, rather than relying on a human checklist or catching it by luck.

**Why:** A human checklist or a manual pass over a large tree misses instances that a systematic scan across every file would catch, so relying on it leaves a near-miss chance of publishing something private until the check is automated and fail-closed.

**Confidence:** High (The near-miss pattern and its systematic fix were independently arrived at in two unrelated extraction and release efforts.). **First seen:** 2026-06. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-183 Validating a file by its path and then reopening it to read it is a check-then-use race

**Symptom:** A file-read hardening routine calls stat, or checks type or size, on a path, then reopens that same path to actually read it, leaving a window in which the file at that path can be swapped or grown between the check and the read.

**Rule:** When a file must be validated for type or size before reading, open the file descriptor first, run the validation such as fstat against that already-open descriptor, and read from that same descriptor. Never validate by path and then reopen the path, since that gap is a classic check-then-use (TOCTOU) race.

**Why:** A guard that validates a path and then reopens the same path to read it leaves a window where the underlying file can be swapped or grown between the two steps, and this exact pattern recurred in a separate hardening pass.

**Confidence:** Medium (The identical pattern was independently found and fixed twice in separate hardening passes on related tooling.). **First seen:** 2026-08. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-184 A long-lived credential that unattended automation depends on needs monitored rotation, not discovery after failure

**Symptom:** A scheduled or headless job that authenticates with a long-lived key or token, rather than a session that gets refreshed interactively, starts silently failing its verification steps, and the underlying cause turns out to be that the credential itself expired or was invalidated with no one tracking its lifecycle.

**Rule:** For any long-lived credential that unattended automation depends on, set up an explicit, monitored expiry and rotation process before you rely on it. Do not treat 'it will fail loudly when it expires' as a plan, because it often fails quietly first, inside a verification step nobody is watching.

**Why:** A long-lived credential with no owner tracking its lifecycle can expire silently between runs, so the job's downstream verification steps start failing before anyone notices the credential itself is the cause.

**Confidence:** Medium (Based on a single incident, but the expire-silently mechanism generalizes beyond that one case.). **First seen:** 2026-07. **Applies to:** Scheduled or headless automation authenticating with long-lived keys or tokens, not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs describe how to set up a scheduled task, but not that a long-lived credential the task relies on needs its own monitored rotation process, since the task itself will not surface a silently expired key until a downstream verification step breaks.
**Related:** [Scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks)

### L-185 A secrets sweep must check untracked working-tree files, not only committed history

**Symptom:** A plaintext credential turns up sitting in a file that was never committed, untracked and unprotected, one careless bulk-add away from being pushed, inside a repo that is otherwise public or public-adjacent.

**Rule:** Run any security or credential sweep across untracked working-tree files as well as tracked and committed history, and run it across every repo in the workspace rather than just the one you are actively in, since an uncommitted file with a live credential is a real exposure sitting on disk and in any full-tree backup.

**Why:** A credential sweep that only diffs tracked or committed history has a blind spot for files that were never staged, so a live secret can sit exposed on disk, in backups, and one accidental add away from a push without any tracked-only or single-repo review ever catching it.

**Confidence:** High (the same event is corroborated across multiple independent write-ups, each emphasizing a different facet of the gap). **First seen:** 2026-07. **Applies to:** any git working tree or workspace-wide credential sweep; not version-specific. **Scope:** agent-agnostic.

### L-187 Scrubbing sensitive strings from a repo you plan to make public requires rewriting history, not just current files

**Symptom:** Proprietary names or personal data are removed from the current working tree of a repo destined for public release, but remain fully visible in `git log -p`, a host's code search, or any clone made before the cleanup.

**Rule:** When removing sensitive strings from a repo you plan to make public, rewrite git history, not only the current files, and plan for every existing clone to need a hard reset after the force-push that follows.

**Why:** Editing or deleting a string in the working tree leaves every prior commit that touched it unchanged, so the string stays fully recoverable through history until the history itself is rewritten.

**Confidence:** High (Directly confirmed by inspecting git history and old clones before publishing.). **First seen:** 2026-06. **Applies to:** not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs describe how to rewrite history mechanically but not that a working-tree-only fix leaves the string fully recoverable, or that every existing clone needs a hard reset once you force-push the rewrite.
**Related:** [git-filter-branch](https://git-scm.com/docs/git-filter-branch)

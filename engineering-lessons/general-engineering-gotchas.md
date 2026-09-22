# General Engineering Gotchas

**Scope:** Applies to any codebase; nothing here depends on a particular agent or stack.

Traps the agent work surfaced that have nothing to do with agents: documentation that drifts from the code it describes, interpreters and credentials that fight each other, and defaults that lie. Each entry names the symptom first.

Lessons in this file: 11

- [L-149 Never name a shell variable after one of the shell's special or read-only parameters](#l-149-never-name-a-shell-variable-after-one-of-the-shells-special-or-read-only-parameters)
- [L-150 A scheduled job can silently self-disarm or fail with no alert](#l-150-a-scheduled-job-can-silently-self-disarm-or-fail-with-no-alert)
- [L-152 Multiple local interpreters writing to the same OS credential store cause recurring auth prompts](#l-152-multiple-local-interpreters-writing-to-the-same-os-credential-store-cause-recurring-auth-prompts)
- [L-153 A heredoc feeding an interpreter can steal the stdin that interpreter's own code expects to read](#l-153-a-heredoc-feeding-an-interpreter-can-steal-the-stdin-that-interpreters-own-code-expects-to-read)
- [L-154 A path based tool runner cache can silently keep serving stale code after an update](#l-154-a-path-based-tool-runner-cache-can-silently-keep-serving-stale-code-after-an-update)
- [L-155 A shell builtin's availability can depend on the OS's stock shell version, not just the shell language](#l-155-a-shell-builtins-availability-can-depend-on-the-oss-stock-shell-version-not-just-the-shell-language)
- [L-156 A test fixture that skips on a missing optional dependency can skip exactly the case that most needs testing](#l-156-a-test-fixture-that-skips-on-a-missing-optional-dependency-can-skip-exactly-the-case-that-most-needs-testing)
- [L-157 Document what a third-party tool can do at the mechanism level, not the pricing-tier level](#l-157-document-what-a-third-party-tool-can-do-at-the-mechanism-level-not-the-pricing-tier-level)
- [L-158 Independently rounded displayed values can visibly fail to add up](#l-158-independently-rounded-displayed-values-can-visibly-fail-to-add-up)
- [L-159 macOS privacy protection (TCC) can block a shell subprocess from reading a file it can list](#l-159-macos-privacy-protection-tcc-can-block-a-shell-subprocess-from-reading-a-file-it-can-list)
- [L-160 macOS screenshot filenames contain an invisible character that breaks literal shell path matching](#l-160-macos-screenshot-filenames-contain-an-invisible-character-that-breaks-literal-shell-path-matching)

---

### L-149 Never name a shell variable after one of the shell's special or read-only parameters

**Symptom:** A shell script assigns to a variable sharing its name with a shell builtin or reserved word, such as status in zsh, and the assignment is silently ignored or misbehaves, producing a failure that looks unrelated to the actual cause.

**Rule:** Check the target shell's special-parameter and builtin list before naming loop, exit-code, or status variables in a script (for example, status is a read-only parameter in zsh, and names like PATH or IFS change behavior everywhere), never reuse one of those names for an ordinary variable, and test the script under the shell it will actually run in, because the failure mode differs by shell.

**Why:** A shell's special or read-only parameters carry built-in meaning, so an ordinary assignment to one is rejected outright in one shell and silently reinterpreted in another, instead of failing clearly at the point of the mistake.

**Confidence:** Medium (the same specific gotcha caused two separate incidents months apart despite being previously documented). **First seen:** 2026-05. **Applies to:** bash and zsh scripts; the specific reserved names differ per shell. **Scope:** agent-agnostic.

### L-150 A scheduled job can silently self-disarm or fail with no alert

**Symptom:** A scheduled pipeline configured to run only if its previous run succeeded stops firing entirely after one failure with no alert, or a background job fails the same way repeatedly, logged each time but never surfaced to a person.

**Rule:** Never let a scheduled job's own success gate whether it runs again without an escape hatch, and never rely on the job's own log as the alerting mechanism; pair scheduled automation with an independent check that notices when it stops firing or keeps failing, and pages a human.

**Why:** A run-only-if-previous-succeeded gate turns one failure into permanent silence, because the job that would report the failure is the same job that stopped running, so nothing outside its own log ever notices.

**Confidence:** High (Based on multiple incidents across different jobs and tools, all showing the same failure mode.). **First seen:** 2026-06. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-152 Multiple local interpreters writing to the same OS credential store cause recurring auth prompts

**Symptom:** The OS repeatedly asks to allow access to a stored credential even after it was already approved, because the prompt reappears after every credential refresh.

**Rule:** If a recurring OS keychain or credential store prompt will not stay dismissed, check whether more than one local interpreter or binary version independently authenticates and writes the same credential, and consolidate every client that touches that credential onto one pinned interpreter or version.

**Why:** When more than one local interpreter independently authenticates and writes the same OS level credential, each refresh hands ownership to whichever one ran most recently, which resets the stored access grant and reopens the permission prompt.

**Confidence:** High (Root cause confirmed by identifying the distinct interpreters involved and reproducing the prompt pattern; fix applied and shipped.). **First seen:** 2026-09. **Applies to:** macOS Keychain accessed by more than one local interpreter or client binary version. **Scope:** agent-agnostic. **Last verified:** 2026-09.

### L-153 A heredoc feeding an interpreter can steal the stdin that interpreter's own code expects to read

**Symptom:** A script pipes data into an interpreter invoked via a heredoc, and the interpreter's own stdin read gets empty or unexpected content instead of the piped data.

**Rule:** Remember that a heredoc occupies the invoked interpreter's stdin. If the invoked code also needs to read piped data from stdin, capture that data to a temp file or a variable first, before starting the heredoc invocation.

**Why:** A heredoc and a piped stream both attach to the same single stdin file descriptor of the invoked process, so whichever one the shell wires up wins and the other is never seen by the interpreter's own read call.

**Confidence:** Medium (Single observed incident, root-caused and fixed in the same session.). **First seen:** 2026-06. **Applies to:** bash and any interpreter invoked through a shell heredoc, not version-specific. **Scope:** agent-agnostic.

### L-154 A path based tool runner cache can silently keep serving stale code after an update

**Symptom:** A package runner invocation resolves and caches a CLI by filesystem path rather than by version, so updating the package during testing can continue silently executing the old cached code with no error.

**Rule:** When a package runner or tool cache resolves by path instead of version, force a cache bust or pin and verify the version explicitly after any update. A stale path keyed cache keeps serving old behavior with no error to flag it.

**Why:** A path keyed cache resolves and reuses a previously cached binary by its filesystem location rather than by version, so updating the underlying package does not invalidate the cache entry and the old code keeps running silently.

**Confidence:** Medium (Single incident, but the caching mechanism is generic and well understood.). **First seen:** 2026-08. **Applies to:** any package runner or tool cache that keys on filesystem path rather than package version, not version specific. **Scope:** agent-agnostic.

### L-155 A shell builtin's availability can depend on the OS's stock shell version, not just the shell language

**Symptom:** A bash script using a builtin such as mapfile or associative arrays runs fine in CI but fails for a contributor running it locally on macOS, with an error that the builtin or syntax is not recognized.

**Rule:** Before relying on a bash builtin introduced after bash 3.2, such as mapfile or associative arrays, check whether the script needs to run on macOS's stock shell, which stays pinned to an old bash version for licensing reasons; use a portable POSIX-sh alternative or require Homebrew bash explicitly and reference it by full path.

**Why:** macOS ships an old, frozen version of bash as its default shell for licensing reasons, so a script that only exercises newer bash builtins in a Linux CI environment can run cleanly there while still failing on a contributor's Mac.

**Confidence:** Medium (Single observed instance, root cause confirmed by checking bash version.). **First seen:** 2026-06. **Applies to:** bash scripts that may run under macOS's default /bin/bash (frozen at 3.2), not version-specific to any particular repo or language. **Scope:** agent-agnostic.

### L-156 A test fixture that skips on a missing optional dependency can skip exactly the case that most needs testing

**Symptom:** A test suite marks a scenario as skipped when an optional dependency isn't installed in the test environment, and that scenario happens to be the specific edge case the test was written to guard against.

**Rule:** When a test conditionally skips because an optional dependency is absent, check what code path that skip is hiding. If it is the fallback or degraded-mode path a feature depends on, either install the dependency in CI or replace the skip with a stub that still exercises the logic.

**Why:** A conditional skip and a passing test look identical in CI output, so a suite can report all green while the one branch meant to catch a regression in degraded-mode behavior never actually executes.

**Confidence:** Medium (Single observed instance, root cause and fix both directly confirmed.). **First seen:** 2026-09. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-157 Document what a third-party tool can do at the mechanism level, not the pricing-tier level

**Symptom:** A reference document's claims about a vendor product are correct at the underlying-capability level but wrong at the plan, SKU, or pricing-tier level, because vendors change tier boundaries and paid gating far more often than the underlying feature itself changes.

**Rule:** When documenting a third-party tool's capabilities for others to rely on, phrase claims around the underlying mechanism, whether the capability exists and how it is accessed, rather than which pricing tier or plan currently includes it, since tier details go stale fastest.

**Why:** Vendors move which pricing tier gates a capability far more often than they change whether the underlying capability exists at all, so a claim anchored to a tier goes stale long before a claim anchored to the mechanism does.

**Confidence:** High (Confirmed by a structured verification pass against primary vendor docs plus an independent second review.). **First seen:** 2026-07. **Applies to:** Any documentation of a third-party vendor tool's capabilities written for others to rely on; not version-specific. **Scope:** agent-agnostic.

### L-158 Independently rounded displayed values can visibly fail to add up

**Symptom:** A UI or report shows a decomposition, such as parts summing to a total or a caption stating two figures sum to a third, where each value was rounded separately for display, so the displayed numbers do not actually sum even though the underlying data does.

**Rule:** When displaying values alongside a stated sum or total, do not round every term independently. Round only the most-scrutinized value or values and derive the remaining term by subtraction from the already-rounded displayed values, so the shown equation is always exactly true.

**Why:** Rounding each term of a sum independently before display can leave the rounded parts no longer matching the rounded total, because rounding error accumulates differently across the separate terms.

**Confidence:** Medium (Same underlying bug diagnosed once and independently generalized to the broader pattern, which corroborates it but is a thinner basis than a second, independently observed incident.). **First seen:** 2026-06. **Applies to:** Any UI, report, or dashboard that displays rounded figures alongside a stated sum or total, regardless of stack; not version-specific.. **Scope:** agent-agnostic.

### L-159 macOS privacy protection (TCC) can block a shell subprocess from reading a file it can list

**Symptom:** A shell command can list a file inside a protected macOS directory such as the Desktop, but every attempt to read its actual contents fails with a permission-style error that looks like an authentication or scripting bug.

**Rule:** When a shell subprocess can see a file but not read its bytes inside a protected macOS directory, treat it as a TCC privacy restriction rather than a scripting bug. Copy the file to an unprotected location first, or grant the terminal or agent app the needed permission in System Settings.

**Why:** macOS TCC privacy protections gate file content reads separately from directory listing on a per app basis, so a subprocess can enumerate a protected folder yet still be denied when it opens a file inside it, and this recurred.

**Confidence:** High (Confirmed twice, including against a different protected folder.). **First seen:** 2026-06. **Applies to:** macOS with TCC privacy protections, any shell or terminal app. **Scope:** agent-agnostic. **Last verified:** 2026-09.

### L-160 macOS screenshot filenames contain an invisible character that breaks literal shell path matching

**Symptom:** A shell command referencing a macOS screenshot filename by its typed-out path fails with a no-such-file error, even though the file clearly exists and the path looks correct in a terminal or Finder listing.

**Rule:** When a shell command fails against a macOS screenshot filename with a plausible-looking path, use a wildcard glob around the distinctive part of the name instead of typing the full name literally. The space before AM or PM in that filename is a different, invisible Unicode character, not a regular space.

**Why:** macOS generates screenshot filenames with a narrow no-break space character before the AM/PM marker, which renders visually identical to a normal space but does not match one when typed literally in a shell command.

**Confidence:** High (Reproduced and worked around directly; a long-standing macOS filename behavior.). **First seen:** 2026-06. **Applies to:** macOS screenshot filenames, any shell. **Scope:** agent-agnostic. **Last verified:** 2026-09.

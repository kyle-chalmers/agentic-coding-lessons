# Debugging Methodology

**Scope:** General instincts for finding the real cause of a bug: what counts as proof, what to trust, and where to look next.

A green exit code, a passing test, or a clean-looking result is not proof that the intended effect happened, and I keep having to relearn that in a new form. These lessons are the checks I now run before I believe a fix worked or a system is healthy.

Lessons in this file: 15

- [L-132 A green exit code or success status does not prove the intended effect actually happened](#l-132-a-green-exit-code-or-success-status-does-not-prove-the-intended-effect-actually-happened)
- [L-133 Trace the actual mechanism before proposing a fix or prioritizing work](#l-133-trace-the-actual-mechanism-before-proposing-a-fix-or-prioritizing-work)
- [L-134 Sanity-check a computed number against a source that is structurally independent of it](#l-134-sanity-check-a-computed-number-against-a-source-that-is-structurally-independent-of-it)
- [L-135 An unexpectedly clean or complete-looking result is a signal to dig deeper, not proof of correctness](#l-135-an-unexpectedly-clean-or-complete-looking-result-is-a-signal-to-dig-deeper-not-proof-of-correctness)
- [L-136 Verify real usage from access logs over a long window before retiring or repurposing anything shared](#l-136-verify-real-usage-from-access-logs-over-a-long-window-before-retiring-or-repurposing-anything-shared)
- [L-137 After fixing a bug in shared or copied code, sweep every other instance](#l-137-after-fixing-a-bug-in-shared-or-copied-code-sweep-every-other-instance)
- [L-139 A single shared dependency can silently break many unrelated things at once](#l-139-a-single-shared-dependency-can-silently-break-many-unrelated-things-at-once)
- [L-140 Check for a documentation or naming mixup before escalating an apparent data conflict](#l-140-check-for-a-documentation-or-naming-mixup-before-escalating-an-apparent-data-conflict)
- [L-141 The same value can come back as a different type or shape across client libraries](#l-141-the-same-value-can-come-back-as-a-different-type-or-shape-across-client-libraries)
- [L-142 A shell tool's comment, delimiter, and word-splitting rules are not standard: verify them](#l-142-a-shell-tools-comment-delimiter-and-word-splitting-rules-are-not-standard-verify-them)
- [L-143 Pin the exact execution environment for test and automation tooling](#l-143-pin-the-exact-execution-environment-for-test-and-automation-tooling)
- [L-144 A long-running daemon can silently serve stale state that was only ever computed at process start](#l-144-a-long-running-daemon-can-silently-serve-stale-state-that-was-only-ever-computed-at-process-start)
- [L-145 Verify what a static-analysis or inventory tool actually scans before trusting a clean result](#l-145-verify-what-a-static-analysis-or-inventory-tool-actually-scans-before-trusting-a-clean-result)
- [L-146 Audit the test harness itself before trusting a surprising pass or fail](#l-146-audit-the-test-harness-itself-before-trusting-a-surprising-pass-or-fail)
- [L-148 Give an internal error a different outcome than a legitimate no-op in gate or alerting logic](#l-148-give-an-internal-error-a-different-outcome-than-a-legitimate-no-op-in-gate-or-alerting-logic)

---

### L-132 A green exit code or success status does not prove the intended effect actually happened

**Symptom:** A build, deploy, permission grant, or scheduled job reports success, such as exit 0, a passing CI run, or a job-level SUCCESS status, but the real artifact is missing, unchanged, or a step inside it actually failed silently.

**Rule:** After any automated run reports success, verify the actual output independently: check real artifact, row, or file counts, the status of each individual step rather than only the roll-up status of the run that contains them, an external service's own activity log rather than a try or except wrapped success flag, and a transferred file's actual size or hash rather than mere presence at the destination. Launch anything whose parameters matter through the full parameter form, not a shortcut that can submit with an empty or defaulted config, and confirm a permission or config grant took effect via a specific success signal, not just a clean exit.

**Why:** A success signal often only reflects that a wrapper function returned without raising, not that the underlying operation it wrapped did what it was supposed to, so a swallowed exception, a silent no-op on bad input, or a check that only confirms presence rather than correctness all report the same green.

**Confidence:** High (the single most repeated pattern in the corpus, spanning builds, deploys, grants, and job monitoring.). **First seen:** 2026-05. **Applies to:** any automated pipeline, job scheduler, or CLI tool, not version-specific. **Scope:** agent-agnostic.

### L-133 Trace the actual mechanism before proposing a fix or prioritizing work

**Symptom:** An investigation starts from a plausible surface signal, such as a matching folder name, an adjacent domain, or an error message's wording, and that assumption turns out wrong once the actual code path, dependency, or data is traced directly.

**Rule:** Before proposing a fix, prioritizing a repair, or answering how two systems relate, trace the actual code path, dependency graph, invoking callers, join key, or data format directly, instead of inferring it from naming, folder structure, an error message's wording, or domain adjacency. Something can be broken and still irrelevant if nothing live actually depends on it.

**Why:** Surface signals like file paths, naming, and error wording describe an intended or apparent structure rather than the runtime path a system actually exercises, so a component can look connected while nothing live calls it, or look guilty while it never touches the affected data.

**Confidence:** High (one of the most repeated patterns across many separate, unrelated incidents). **First seen:** 2026-05. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-134 Sanity-check a computed number against a source that is structurally independent of it

**Symptom:** A regression check, self-check, or denominator is built from the same source, the same flawed logic, or the system's own filtered output as the thing it is meant to validate, so agreement between them proves nothing. A weak timing-based correlation gets treated as a real join key, and a number pulled from a live dataset is not timestamped, so a later comparison looks like a regression when it is really just drift.

**Rule:** Before trusting a computed or reconciled number, verify it against a source that is structurally independent of the value being checked, not the same predecessor system, the same filtered output, or the same single field. Look for a second, independently derived corroborating source when possible, never promote an unverified timing-based correlation into a production join key, and always timestamp a number pulled from a live or refreshed dataset with its snapshot date.

**Why:** A parity or self-check test built from the same upstream logic as the value it validates can only prove the two sides agree, not that either one is correct, so a shared flaw or a shared blind spot survives the check undetected and recurred across independent debugging efforts.

**Confidence:** High (one of the most repeated patterns in the corpus, spanning parity tests, denominators, and cross-source reconciliation). **First seen:** 2026-07. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-135 An unexpectedly clean or complete-looking result is a signal to dig deeper, not proof of correctness

**Symptom:** A metric reads as suspiciously healthy, such as zero missing values, a near-perfect match between two counts, an empty-versus-empty parity comparison, a short sample window with zero occurrences, one favorable period, or a single aggregate that hides one broken segment, and that clean result gets treated as confirmation rather than investigated further.

**Rule:** Treat an unexpectedly clean, complete, or all-clear result with suspicion. Check whether upstream filtering removed the very rows that would show a problem, force any equivalence or parity test onto a case where the condition actually fires, measure impact over the full affected window rather than a short or favorable sample, check each segment individually rather than trusting an aggregate, and look outside the wired-in check set for what a "complete" deliverable might still be missing.

**Why:** A chain of filters or a narrow comparison window can remove or hide the exact cases that would reveal a defect, so the absence of a signal in a filtered or narrow view gets mistaken for the absence of the defect itself.

**Confidence:** High (The underlying mechanism, that a filtered or narrow view can only show a defect that survives the filter, holds regardless of what is being checked.). **First seen:** 2026-07. **Applies to:** Any data QC, testing, or debugging workflow; not version-specific. **Scope:** agent-agnostic.

### L-136 Verify real usage from access logs over a long window before retiring or repurposing anything shared

**Symptom:** An object, field, or view looks safe to delete or repurpose because it is undocumented, described as legacy, or shows low activity over a short observation window, but a longer usage check reveals a consumer that only calls it infrequently.

**Rule:** Before deleting, retiring, or repurposing anything shared, confirm it is unused using at least two independent signals over a window at least as long as the longest expected caller cadence, exclude your own auditing activity from the results, treat keep this for X comments and legacy sounding names as claims to verify rather than facts, and check every consumer or adapter of a field rather than only the main pipeline that looks unused from your current feature's point of view.

**Why:** A short observation window or a single usage signal misses a consumer that calls on a longer cycle, and an audit that fails to exclude its own queries inflates the very activity it is trying to measure.

**Confidence:** High (One of the most repeated patterns in the corpus, spanning many separate retirement and field reuse incidents.). **First seen:** 2026-06. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-137 After fixing a bug in shared or copied code, sweep every other instance

**Symptom:** A bug is fixed in one instance of a reused query, template, or code fragment, or in one output path a generator emits to, but sibling copies, the shared source it was copied from, downstream derived tables or views, and other emit points carrying the identical latent defect go unchecked and later resurface as if they were new findings.

**Rule:** When a bug traces to a shared or copied fragment, a template, or a general class of defect, propagate the fix back into the shared source immediately and grep every other use, every downstream derived object, and every fallback or default lookup for a new value across the codebase, checking first whether the codebase already has an established fix pattern for that failure class before inventing a new one.

**Why:** A fix applied only where the symptom happened to surface leaves every sibling copy carrying the identical defect untouched, so the same root cause recurred and reappeared as though it were a separate, new bug each time.

**Confidence:** High (Recurs across template propagation, downstream-table, and fallback-lookup incidents.). **First seen:** 2026-06. **Applies to:** Any codebase with copied templates, reused query fragments, generated outputs, or keyed fallback lookups; not version-specific. **Scope:** agent-agnostic.

### L-139 A single shared dependency can silently break many unrelated things at once

**Symptom:** Several independent jobs, tools, or integrations start failing around the same time, and each failure looks like its own unrelated bug when examined in isolation.

**Rule:** When multiple independent things break at once, or the same category of failure keeps recurring across sessions, check the shared layer underneath them, such as a credential, network path, or infrastructure gate, before you debug each occurrence on its own; also verify that any monitor built to catch this class of failure does not itself depend on the exact path it is meant to watch.

**Why:** Several unrelated jobs and tools shared one underlying dependency, so when that dependency changed, the failures surfaced separately and looked like unrelated problems until someone traced them back to the same root mechanism.

**Confidence:** High (pattern recurred across multiple distinct incidents involving different shared dependencies). **First seen:** 2026-05. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-140 Check for a documentation or naming mixup before escalating an apparent data conflict

**Symptom:** Two fields, systems, or reports appear to disagree or duplicate the same issue, and the instinct is to escalate for arbitration or assume they share one root cause.

**Rule:** Before escalating an apparent cross source disagreement, filing a near duplicate bug, or recommending a fix, check directly whether it is a genuine conflict or one of: a documented rule over generalized to the wrong field, a naming collision between an unrelated convention and a literal object, confusion about which specific object is being discussed, an issue that already shipped a fix, or a correctly computed metric that is simply mislabeled by where it is placed.

**Why:** Two sources can disagree on the surface while both are computed correctly, because the actual fault sits one level away, in a label, a name, or a scope assumption, so escalating on the surface disagreement skips the check that would reveal it.

**Confidence:** High (recurs across data reconciliation, naming, and audit recommendation incidents). **First seen:** 2026-07. **Applies to:** not version-specific; applies to any debugging or data-reconciliation workflow, human or agent-driven. **Scope:** agent-agnostic.

### L-141 The same value can come back as a different type or shape across client libraries

**Symptom:** Arithmetic or binding against a database column raises a type error in one client or connector path but not another, a rounding result differs by the smallest representable unit between two languages, or a parameterized query with no matching placeholder silently discards a bound value.

**Rule:** When the same logical operation runs through two different client libraries, connectors, or languages, don't assume they treat a value identically: normalize numeric or type handling explicitly at the boundary, check each engine's default rounding mode before treating a smallest-representable-unit mismatch as a bug, and verify that a query's literal text actually contains a placeholder for every bound parameter.

**Why:** The same underlying value can surface as a different type, precision, or rounding behavior depending on which client library or language reads it, and a parameterized query can silently drop a bound value if its literal text lacks a matching placeholder, a mismatch that recurred across multiple connector paths.

**Confidence:** High (Recurring across driver, parameter-binding, and rounding-mode incidents in different client paths.). **First seen:** 2026-05. **Applies to:** Any client library, driver, or connector reading the same data source; not version-specific. **Scope:** agent-agnostic.

### L-142 A shell tool's comment, delimiter, and word-splitting rules are not standard: verify them

**Symptom:** A script written assuming a target CLI or shell parses input the way a standard shell does fails silently: the CLI strips or treats a comment differently than expected and splits a multi-statement script in an unintended place, word-splitting under a stricter shell mode reshapes an argument, a regex anchor doesn't mean true end-of-string, and a word-boundary doesn't fire before a hyphen, each looking like ordinary shell or regex behavior locally but isn't for that specific tool.

**Rule:** Before relying on how a specific CLI, shell, or regex engine parses input, test it directly against a representative real example rather than assuming standard behavior: confirm what the CLI actually treats as a comment or statement separator, verify word-splitting under the exact shell mode that will run the script, and confirm a regex anchor or word-boundary fires where you think it does rather than assuming it from general regex knowledge.

**Why:** Command-line tools, shells, and regex engines each define their own parsing rules for comments, delimiters, word-splitting, and anchors, so code that assumes one tool's conventions match general expectations can silently misinterpret input instead of raising an error.

**Confidence:** Medium (Recurring across CLI-parsing, word-splitting, and regex-anchor incidents that each failed silently; split out from a broader shell-scripting lesson to isolate this mechanism.). **First seen:** 2026-05. **Applies to:** Any CLI, shell, or regex engine invoked by a coding agent; not version-specific. **Scope:** agent-agnostic.

### L-143 Pin the exact execution environment for test and automation tooling

**Symptom:** A test or automation tool infers its environment implicitly and gets it wrong: an assumed working directory produces a false negative once the caller's directory changes, or a bare command resolves to a different shadow interpreter than the one intended.

**Rule:** Do not let a test or automation tool infer its environment implicitly. Pass explicit paths instead of relying on the current working directory, and invoke a test runner through the target interpreter's own module form instead of a bare command that might resolve to a different shadow interpreter.

**Why:** A tool that infers its working directory or interpreter from ambient state rather than pinning it explicitly keeps working by coincidence until the caller's environment shifts, at which point it fails silently or checks the wrong thing instead of raising an error.

**Confidence:** Medium (Recurring across working-directory-assumption and shadow-interpreter incidents; split out from a broader tooling-infrastructure lesson.). **First seen:** 2026-07. **Applies to:** Any test runner or validation script invoked by a coding agent; not version-specific. **Scope:** agent-agnostic.

### L-144 A long-running daemon can silently serve stale state that was only ever computed at process start

**Symptom:** A long-running monitor, daemon, or agent process caches something once at startup, such as a streak counter, a restart-safety flag, or a set of loaded prompts, that should instead be resolved fresh per invocation, so a value that changed after the process started keeps being served as if it were still current.

**Rule:** Audit any long-running daemon or monitor process for anything cached at process start that should instead be resolved per invocation, and explicitly design a restart to reset or re-derive that state rather than assume it stays correct across the process's lifetime.

**Why:** A value computed once when a long-running process starts keeps being served as current for the rest of that process's life because nothing re-derives or invalidates it on later invocations, so it silently goes stale the moment the real condition changes; this recurred across different kinds of monitor state.

**Confidence:** Medium (Observed across multiple long-running monitor processes.). **First seen:** 2026-09. **Applies to:** Any long-running daemon, monitor, or background agent process; not version-specific. **Scope:** agent-agnostic.

### L-145 Verify what a static-analysis or inventory tool actually scans before trusting a clean result

**Symptom:** A linter, scanner, or code-inventory tool reports a clean or complete result, but a variable-form or multi-line match, an out-of-order import, or a scan that silently stopped at a bound it never enforced, all pass through undetected.

**Rule:** Before trusting a scanner's clean result, confirm what it actually covers: prefer AST-based parsing over regex for anything beyond a trivial single-line pattern, check ordering as well as presence for anything order-sensitive such as imports, and confirm any bound placed on a scan's traversal actually limits it and fails closed rather than silently truncating what gets reported.

**Why:** A scanner built on pattern matching or a partial traversal can report success while covering only a subset of the real input space, so a clean result proves the tool did not find a problem, not that none exists.

**Confidence:** Medium (Observed across three distinct incidents.). **First seen:** 2026-08. **Applies to:** Any custom-built static-analysis, linting, or code-inventory tooling, regardless of language or agent; not version-specific.. **Scope:** agent-agnostic.

### L-146 Audit the test harness itself before trusting a surprising pass or fail

**Symptom:** A test suite passes or fails in a way that has nothing to do with the code under test: a fixture does not survive the loader intact, an assertion checks only that a string is present rather than that the behavior is correct, or the harness's own argument parsing has a bug, and each produces a clean-looking result that proves nothing about the actual logic.

**Rule:** Whenever a test result looks surprisingly right or wrong, audit the harness itself, not just the code under test. Verify a fixture actually survives the loader unchanged, replace string-presence assertions with assertions on real behavior, and check the harness's own argument parsing and fixture setup for bugs before trusting what it reports.

**Why:** A test harness sits between the code under test and the reported result, so a bug in its fixture loading, argument parsing, or assertion logic can produce a clean pass or fail that reflects the harness rather than the logic it claims to be checking, and this recurred across unrelated parts of the same codebase.

**Confidence:** Medium (Several distinct incidents observed, split out from a broader test-infrastructure lesson.). **First seen:** 2026-08. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-148 Give an internal error a different outcome than a legitimate no-op in gate or alerting logic

**Symptom:** An automated gate, alert, or middleware layer that can legitimately skip work produces the exact same silent outcome when it hits an internal error as when it correctly finds nothing to do, so a real failure inside the gate looks identical to normal behavior.

**Rule:** When building gate, alerting, or middleware logic that has a legitimate no-op path, make its internal-error path visibly different, such as a log line, a distinct return code, or a raised exception, from that no-op, so a broken check cannot hide behind normal-looking silence.

**Why:** When an error handler and a legitimate skip both resolve to the same silent outcome, nothing distinguishes a bug in the gate's own logic from correct behavior until someone notices an expected side effect never happened and goes looking for why.

**Confidence:** Medium (Two distinct incidents observed, split out from a larger monitors and gates pattern.). **First seen:** 2026-05. **Applies to:** not version-specific. **Scope:** agent-agnostic.

# Verification Tooling & Test Rigor

**Scope:** Building checks, gates, and tests that prove what they claim instead of passing vacuously.

A check that only tests for presence, shares its source with the logic it verifies, or reimplements what it should run instead proves nothing when it matters. These lessons are how I build and mutation-test verification tooling so a passing gate means what I think it means.

Lessons in this file: 10

- [L-188 A check that only confirms presence, or shares its source with the logic it checks, proves nothing](#l-188-a-check-that-only-confirms-presence-or-shares-its-source-with-the-logic-it-checks-proves-nothing)
- [L-189 A live, rendered walkthrough catches UI defects that code review and text checks never will](#l-189-a-live-rendered-walkthrough-catches-ui-defects-that-code-review-and-text-checks-never-will)
- [L-190 Verify against actual live system state, not a migration file, manifest, snapshot, or convenient checkout](#l-190-verify-against-actual-live-system-state-not-a-migration-file-manifest-snapshot-or-convenient-checkout)
- [L-191 After any fix, re-check the surrounding context it touched, not just the finding it addressed](#l-191-after-any-fix-re-check-the-surrounding-context-it-touched-not-just-the-finding-it-addressed)
- [L-192 Validate against a known-good fixture or by dogfooding on real code, not just internal self-consistency](#l-192-validate-against-a-known-good-fixture-or-by-dogfooding-on-real-code-not-just-internal-self-consistency)
- [L-193 Trace every headline number in a deliverable back to its source before presenting it](#l-193-trace-every-headline-number-in-a-deliverable-back-to-its-source-before-presenting-it)
- [L-194 Mutation-test a new safety or health check by deliberately breaking what it watches](#l-194-mutation-test-a-new-safety-or-health-check-by-deliberately-breaking-what-it-watches)
- [L-195 A pre-commit parity hook catches silent drift between two representations of the same logic](#l-195-a-pre-commit-parity-hook-catches-silent-drift-between-two-representations-of-the-same-logic)
- [L-196 A feature's logic can be fully built but never wired into its trigger point](#l-196-a-features-logic-can-be-fully-built-but-never-wired-into-its-trigger-point)
- [L-197 A hermetic test-isolation mechanism must not have an environment-variable override escape hatch](#l-197-a-hermetic-test-isolation-mechanism-must-not-have-an-environment-variable-override-escape-hatch)

---

### L-188 A check that only confirms presence, or shares its source with the logic it checks, proves nothing

**Symptom:** A health check, QC check, selftest, or doc test reports healthy, such as 'key is present' or 'field is non-empty', while the actual value, config, or documented behavior it claims to verify is wrong, because the check never independently exercised the real logic or an independent data source.

**Rule:** Design checks to assert on the actual parsed or executed value from a source independent of the logic being tested, not on mere presence or a proxy field that shares its blind spots with the thing it checks. A check's name or its describing comment is not proof of what it gates: read what it actually does and compare that against the coverage it claims.

**Why:** A check that only reads a proxy signal, such as whether a field exists or a string appears, cannot distinguish a correct value from an incorrect one that happens to share the same proxy, so it stays green through the exact failures it was meant to catch.

**Confidence:** High (very large, consistent cluster spanning grep-based selftests, doctest reimplementation, and proxy-field QC checks across many independent projects). **First seen:** 2026-06. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-189 A live, rendered walkthrough catches UI defects that code review and text checks never will

**Symptom:** Code review, static analysis, and even automated tests pass, but a chart truncates values, a legend is wrong, a layout collides, or a virtualized table's content is invisible to a text-based check, and none of it shows up until someone actually looks at the rendered page. A recurring layout collision keeps slipping back through even after being fixed because verification each time was another one-off manual look.

**Rule:** For any UI, chart, or dashboard change, verify it by actually rendering and looking at, or browser-walking, the live result, including edge cases like large numbers, empty states, and virtualized content, rather than relying on code review or automated checks that only see markup or text, not rendered pixels. A reviewing agent may not even be able to see a private repo's rendered assets the way a human does, so do not assume it has looked. Once a visual or layout defect class has recurred, add a programmatic geometric or collision check for it instead of relying on repeated manual visual passes.

**Why:** Code review, static analysis, and text-extraction checks all inspect markup or source rather than the rendered pixels, so a defect that only exists in the rendered layout, such as truncation, a wrong legend, a collision, or virtualized content with no text node, has nothing to trip on until a human or a rendering tool actually looks at the live page.

**Confidence:** High (one of the largest and most consistent clusters in the corpus, spanning many different UI stacks and defect types over several months). **First seen:** 2026-05. **Applies to:** any UI, chart, or dashboard change, not version-specific. **Scope:** agent-agnostic.

### L-190 Verify against actual live system state, not a migration file, manifest, snapshot, or convenient checkout

**Symptom:** A change is declared verified because a migration file exists, a manifest says so, a scheduled job ran on time, or a review used a default or override parameter, while the actual live state (database, deployed package, background process, default code path) was never checked directly and turns out to differ.

**Rule:** Verify claims against the actual live system: query the live database rather than trust a migration comment, check the deployed package from outside the source tree, confirm a scheduled job's automation actually shipped the intended code, exercise the real default code path rather than a convenient override, and reproduce a bug before and after any fix rather than reasoning about it.

**Why:** A migration file, manifest, scheduled-job log, or convenient checkout records intent rather than the live system's current contents, so treating it as proof that a change took effect recurred as a verification gap until the live state was queried directly.

**Confidence:** High (large cluster where the same failure mode, trusting a proxy for live state, repeats across many different specific artifacts.). **First seen:** 2026-05. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-191 After any fix, re-check the surrounding context it touched, not just the finding it addressed

**Symptom:** A fix resolves the flagged finding but introduces a new contradiction nearby, leaves a second bypass of the same check unaddressed, fixes a symptom at one level while the same flaw persists at another, or a component meant to enforce a rule quietly becomes a second, drifting source of truth for it.

**Rule:** After landing any fix, re-check the surrounding code or data it touched for new contradictions or remaining instances of the same flaw at a different level. Treat a footgun hit twice as a signal to add an automated check rather than just a memory note, and confirm a fix is actually right before merging it, even when it looks plausible and harmless.

**Why:** A patch that satisfies the one finding it targeted was never checked against the rest of the surroundings it touched, so a locally correct fix can leave a new contradiction, an unaddressed duplicate, or the same flaw recurring one level away.

**Confidence:** Medium (Consistent cluster of incidents where a first fix was locally correct but incomplete.). **First seen:** 2026-06. **Applies to:** any code review, bug-fix, or automated-check workflow where a fix is applied to one flagged instance, not version-specific. **Scope:** agent-agnostic.

### L-192 Validate against a known-good fixture or by dogfooding on real code, not just internal self-consistency

**Symptom:** A rewritten pipeline, a new governance or lint tool, or a suppression justification is trusted because it is internally consistent, without ever being checked against an independently audited result or run against real, messy code.

**Rule:** Validate a rewritten pipeline against a previously audited golden result, dogfood a new governance or scanning tool against real code before trusting its output, verify a suppression comment's stated justification rather than taking it at face value, and build review materials by running the actual production code path on synthetic data rather than pointing reviewers at test fixtures.

**Why:** Internal self-consistency only confirms that a tool or pipeline agrees with itself, not that it matches an independently audited result or holds up against real, messy input, so a class of errors that only shows up against ground truth or production code passes every internal check unnoticed.

**Confidence:** Medium (consistent cluster across pipeline rewrites and new tooling rollouts). **First seen:** 2026-05. **Applies to:** verification tooling, lint or governance checks, and pipeline rewrites; not version-specific. **Scope:** agent-agnostic.

### L-193 Trace every headline number in a deliverable back to its source before presenting it

**Symptom:** A presentation, report, or comms deliverable states a headline number, coverage claim, or impact estimate that turns out to contradict the deliverable's own supporting table, fall outside the actual reporting window, or simply be guessed.

**Rule:** Trace every headline metric back to its source before presenting it, cross-check it against the deliverable's own supporting tables, confirm any cited change actually landed inside the stated reporting window, quantify a proposed change's impact before asking for sign-off, and re-issue the corrected figure to everyone who saw the original rather than quietly editing it in place.

**Why:** A headline claim that skips being traced back to its underlying source or cross-checked against the deliverable's own supporting data can drift out of sync with what that data actually shows, and this same drift recurred across separate reporting cycles.

**Confidence:** High (consistent cluster across multiple separate reporting cycles). **First seen:** 2026-07. **Applies to:** reporting and deliverable review workflows, not version-specific. **Scope:** agent-agnostic.

### L-194 Mutation-test a new safety or health check by deliberately breaking what it watches

**Symptom:** A newly built guard, scanner, or eval harness is trusted on the strength of passing on known-good input, without anyone ever confirming it actually fails on known-bad input.

**Rule:** Before trusting any new detection, scanning, health-check, or eval harness, deliberately introduce the failure it's supposed to catch and confirm it actually fires or vetoes. A harness that has never seen a negative case is unproven.

**Why:** A check that has only ever been run against passing input has never demonstrated that it can distinguish a failing case from a passing one, so a bug in its own logic can let everything through and go unnoticed until the exact failure it exists to catch occurs for real.

**Confidence:** High (Reproduced across six independent incidents spanning health checks, scanning gates, safety gates, and eval harnesses.). **First seen:** 2026-05. **Applies to:** Any newly built detection, scanning, health-check, or eval harness; not version-specific. **Scope:** agent-agnostic.

### L-195 A pre-commit parity hook catches silent drift between two representations of the same logic

**Symptom:** Two copies or representations of the same underlying logic, such as a generated artifact and a hand-maintained one, or two parallel systems meant to behave identically, drift apart over time with no error surfacing until something breaks downstream.

**Rule:** When a codebase must keep two representations of the same logic in sync, add a pre-commit hook that fails the commit the moment they diverge, rather than relying on developers to remember to update both every time.

**Why:** Two representations of the same logic stay identical only as long as every change touches both, and without a check run at commit time nothing forces that discipline, so drift accumulates silently until a downstream consumer hits the mismatch.

**Confidence:** Medium (small number of observations, but each described the check as the deciding factor in an otherwise recurring drift problem). **First seen:** 2026-05. **Applies to:** not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** Git's own hook docs explain the hook mechanism but not the specific use of a pre-commit parity check to guard two representations of the same logic against silent divergence.
**Related:** [Git hooks](https://git-scm.com/docs/githooks)

### L-196 A feature's logic can be fully built but never wired into its trigger point

**Symptom:** A feature's application logic is fully written and even embeds the data it needs, but the one integration point that would trigger it, such as a workflow step or a hook call, was never added, so it never runs and never errors, and looks finished on inspection.

**Rule:** After building a feature meant to fire from an existing pipeline or hook, verify the trigger point itself was actually wired in. A feature that is complete in isolation but never invoked fails by simply never running, with no error to notice.

**Why:** A feature's logic sits behind a single call site that connects it to the pipeline or hook that should fire it, so when that call site is never added the feature has nothing to error on, no stack trace and no failed test, and it looks complete to anyone reading only the feature's own code.

**Confidence:** High (based on one incident in the corpus, so tier reflects the more cautious reading). **First seen:** 2026-08. **Applies to:** any feature meant to fire from an existing pipeline, workflow, or hook, not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs describe how to register a hook; they do not warn that a fully built handler wired to nothing produces no error at all, which is why this class of gap survives normal testing.
**Related:** [Hooks reference](https://code.claude.com/docs/en/hooks)

### L-197 A hermetic test-isolation mechanism must not have an environment-variable override escape hatch

**Symptom:** A hermetic-PATH mechanism used to prevent tests from invoking real CLIs gets an environment-variable override added by analogy to an existing pattern, quietly defeating the isolation it was built to guarantee.

**Rule:** Keep a hermetic or isolation mechanism free of any override escape hatch, even one added for consistency with another pattern. An override that can be set from outside the test defeats the guarantee the isolation exists to provide.

**Why:** An environment-variable override added to a hermetic-PATH mechanism by analogy with another pattern creates a switch that code outside the test can flip, which quietly defeats the isolation guarantee the mechanism was built to provide.

**Confidence:** Medium (Traced to a single incident; the mechanism by which the override defeats isolation is unambiguous, but only one occurrence is on record.). **First seen:** 2026-08. **Applies to:** not version-specific. **Scope:** agent-agnostic.

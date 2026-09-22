# Data & SQL Correctness

**Scope:** Silent correctness traps in SQL and data pipelines: nulls, joins, dedup, grain mismatches, and metrics that look fine but are not.

Most of the data bugs I have chased never threw an error: a join fanned out, a metric blended two different grains, a view quietly dropped a whole category of rows, and everything downstream still ran clean. These lessons are the specific shapes those silent failures take, independent of any warehouse or company.

Lessons in this file: 15

- [L-117 NULL does not behave the way SQL and dataframe operators imply](#l-117-null-does-not-behave-the-way-sql-and-dataframe-operators-imply)
- [L-118 When two systems track the same fact, assign one authoritative source per field](#l-118-when-two-systems-track-the-same-fact-assign-one-authoritative-source-per-field)
- [L-119 A field's name, flag, or denormalized label can silently misrepresent what happened](#l-119-a-fields-name-flag-or-denormalized-label-can-silently-misrepresent-what-happened)
- [L-120 A join can silently fan out when the key is not as unique as it looks](#l-120-a-join-can-silently-fan-out-when-the-key-is-not-as-unique-as-it-looks)
- [L-121 A view or table you trust as complete can be silently missing a whole category of rows](#l-121-a-view-or-table-you-trust-as-complete-can-be-silently-missing-a-whole-category-of-rows)
- [L-122 Fixing or evolving an incremental pipeline doesn't retroactively fix its history](#l-122-fixing-or-evolving-an-incremental-pipeline-doesnt-retroactively-fix-its-history)
- [L-123 SQL and DDL syntax edge cases fail silently instead of raising an error](#l-123-sql-and-ddl-syntax-edge-cases-fail-silently-instead-of-raising-an-error)
- [L-124 Recreating or joining through a view carries hidden costs beyond its SELECT logic](#l-124-recreating-or-joining-through-a-view-carries-hidden-costs-beyond-its-select-logic)
- [L-125 Cron and scheduled-job safety guards such as dev flags, dry runs, and halts can be fake](#l-125-cron-and-scheduled-job-safety-guards-such-as-dev-flags-dry-runs-and-halts-can-be-fake)
- [L-126 MAX() or 'pick the latest row' logic can silently pick the wrong record](#l-126-max-or-pick-the-latest-row-logic-can-silently-pick-the-wrong-record)
- [L-127 Missing an explicit tiebreaker makes ordering, dedup, and exports nondeterministic](#l-127-missing-an-explicit-tiebreaker-makes-ordering-dedup-and-exports-nondeterministic)
- [L-128 Ratio and rate metrics silently break when numerator and denominator use different grains](#l-128-ratio-and-rate-metrics-silently-break-when-numerator-and-denominator-use-different-grains)
- [L-129 A label's existence or a row's existence is not proof of the condition it's assumed to represent](#l-129-a-labels-existence-or-a-rows-existence-is-not-proof-of-the-condition-its-assumed-to-represent)
- [L-130 Filter order and filter target both change what a filter actually verifies](#l-130-filter-order-and-filter-target-both-change-what-a-filter-actually-verifies)
- [L-131 Show a genuine data gap honestly instead of masking it with a default value](#l-131-show-a-genuine-data-gap-honestly-instead-of-masking-it-with-a-default-value)

---

### L-117 NULL does not behave the way SQL and dataframe operators imply

**Symptom:** A query or dataframe pipeline that reads as correct silently drops rows, undercounts, or reports a false zero, and the root cause is a NULL interacting with an operator such as IN, a join, SUM, AVG, ARRAY_AGG, COALESCE, or groupby in a way that was not obvious from reading the code.

**Rule:** Wherever a column or field can be NULL, work out explicitly what each operator applied to it does with NULL (equality and IN predicates, joins, SUM and AVG, ARRAY_AGG, COALESCE argument order, and any boundary where the value crosses from one language or system to another) rather than assuming NULL is inert, and add an explicit NULL-handling step at the point where NULL can first appear rather than after the operation that already consumed it.

**Why:** NULL fails equality and IN comparisons, drops out of joins, gets silently skipped by aggregate functions, and can be represented inconsistently when a value crosses a language or system boundary, so an operator chain that looks complete quietly excludes or miscounts the NULL rows and recurred across independent pipelines built by different people.

**Confidence:** High (merged from many independently generated observations across several distinct incidents in the corpus). **First seen:** 2026-07. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-118 When two systems track the same fact, assign one authoritative source per field

**Symptom:** Two systems, teams, or tables that are each individually correct disagree on a status, label, or metric, because they read from different sources of truth, different snapshot times, or a field that is convenient rather than authoritative, and the mismatch keeps getting copied forward into later reports.

**Rule:** For any fact that more than one system or field can represent, name one authoritative source per field before comparing them. When two sources disagree, check snapshot timing and field semantics before assuming either one is wrong, and do not let the tool a team happens to be comfortable in become the system of record by default.

**Why:** When no single field is designated authoritative, two systems that are each locally correct end up disagreeing because they read different snapshot times or different underlying fields, and the resulting mismatched value gets copied into new reports, so the drift recurred and compounded.

**Confidence:** High (Recurred across many independent incidents in different data domains.). **First seen:** 2026-05. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-119 A field's name, flag, or denormalized label can silently misrepresent what happened

**Symptom:** A structured boolean flag, a denormalized display field, a field's plain-language name, or a summary audit log looks authoritative, but it captures only part of the real signal that the underlying free text, the true join key, or the source record actually holds.

**Rule:** Do not trust a field's name, a flag, or a denormalized label to mean what it appears to mean. Check a structured flag against the free text or record it is supposed to summarize, join on the real attribution key instead of a denormalized display field, validate any proxy signal for sensitive or compliance-relevant data against ground truth before it ships, and prefer a visible flag over silent filtering so the judgment call stays inspectable later.

**Why:** A structured flag, denormalized label, or field name is a summary someone chose to write down, not the underlying event itself, so it can drift from or omit what actually happened without any error being raised.

**Confidence:** Medium (Pattern recurred across multiple independent incidents and data domains, which raises confidence even though each individual case was low-signal on its own.). **First seen:** 2026-06. **Applies to:** SQL and data pipeline work involving structured flags, denormalized fields, or proxy signals, not version-specific. **Scope:** agent-agnostic.

### L-120 A join can silently fan out when the key is not as unique as it looks

**Symptom:** A join, especially through a shared entity ID, a slowly-changing-dimension or history table, or a case-varying GUID, multiplies rows far beyond what is expected, and a downstream dedup step quietly absorbs the extra rows instead of surfacing the underlying grain violation.

**Rule:** Join on a compound key or an explicitly deduplicated, current-only version of a table rather than trusting a shared entity ID alone; add a uniqueness check on the join key even when the source should already be unique; and normalize case on ID or GUID columns before joining instead of treating case as a cosmetic difference.

**Why:** A join key that looks unique but is not, whether because it is shared across entities, drawn from an unfiltered history table, or varies only in case, multiplies matching rows during the join, and a downstream dedup step can absorb those extra rows without ever exposing that the join itself violated the intended grain.

**Confidence:** High (merged from many independently generated observations across several distinct incidents). **First seen:** 2026-06. **Applies to:** any SQL join across a shared entity ID, an SCD or history table, or a GUID/ID column; not version-specific. **Scope:** agent-agnostic.

### L-121 A view or table you trust as complete can be silently missing a whole category of rows

**Symptom:** A canonical view, a convenience wrapper, a lookup or mapping table, or a historical log table returns plausible-looking rows but is massively undercounting, or a record's category simply disappears with no error when its lookup entry is missing.

**Rule:** Don't assume a long-standing canonical view, a wrapper over a base table, a hardcoded or scattered ID lookup list, or a historical log-style table has full coverage of the population you need. Measure its actual coverage against the base table or source system, and centralize ad hoc lookup lists into one governed table with an explicit fallback for missing rows.

**Why:** A view or lookup built at one point in time keeps returning clean, plausible-looking results even after the source population grows or changes shape around it, because an inner join or a stale filter drops the uncovered rows silently instead of erroring.

**Confidence:** High (Merged from many independently observed incidents across a large number of distinct cases in the corpus.). **First seen:** 2026-05. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-122 Fixing or evolving an incremental pipeline doesn't retroactively fix its history

**Symptom:** A bug fix, schema-evolution setting, or upsert logic deployed to an incremental or append-only pipeline corrects new data going forward, but rows already materialized stay wrong, missing new columns, or duplicated, and a state or checkpoint table migration can silently reset processing.

**Rule:** Treat any fix to an incremental or append-only pipeline as forward-only unless you explicitly backfill history: check whether schema-evolution defaults quietly drop new columns from existing incremental tables, confirm a state or checkpoint table migration carries its history forward instead of resetting processing, and use upsert semantics rather than blind append for any feed capable of sending corrections.

**Why:** An incremental pipeline processes only new input by design, so a fix applied to its logic changes what happens to future rows without touching rows it already wrote, and that gap recurred across schema-evolution settings, checkpoint migrations, and correction-bearing feeds.

**Confidence:** High (merged from multiple independently generated candidates across several distinct incidents). **First seen:** 2026-06. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-123 SQL and DDL syntax edge cases fail silently instead of raising an error

**Symptom:** A SQL statement, such as a reserved word used as an alias, a template expression left inside a comment, an alias that shares a name with a joined table's real column, or a multi-column guarded DDL clause, parses and runs without error but behaves unexpectedly, and only in some clients or engines.

**Rule:** Treat SQL syntax corners, reserved words as aliases, templated text inside comments, aliases that shadow a joined column, and multi-column conditional DDL, as latent correctness bugs rather than style choices; qualify aliases explicitly and test any templated or guarded SQL against the exact client and engine version that will run it in production.

**Why:** A parser that accepts an ambiguous or shadowed identifier without complaint lets the query keep running while silently resolving to the wrong value or a different execution path depending on the specific client or engine.

**Confidence:** High (Merged from multiple independent incidents sharing the same silent-parse root cause.). **First seen:** 2026-06. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-124 Recreating or joining through a view carries hidden costs beyond its SELECT logic

**Symptom:** After a view is recreated with CREATE OR REPLACE, or a query starts joining through it instead of the base table, columns silently stop appearing, downstream consumers lose access, or the query planner stops pruning partitions, none of which is visible from re-reading the view's own SQL.

**Rule:** Treat a view as more than its SELECT statement. A SELECT * view freezes its column list at creation time and needs the full dependency chain rebuilt to pick up new columns, recreating a view drops its grants unless you explicitly re-apply them, and joining through a view instead of the base table can silently disable filter pushdown and partition pruning. Check all three before touching a production view.

**Why:** A view's column list, grants, and query-plan behavior are decided at creation or rebuild time rather than derived fresh from its SELECT text each time it runs, so none of those three effects shows up when you simply re-read the view's definition.

**Confidence:** High (Merged from multiple independently reported incidents covering the column-freeze, grant-loss, and pruning failure modes separately.). **First seen:** 2026-06. **Applies to:** SQL views in warehouses that support SELECT * column freezing and grant-copy semantics, such as Snowflake, not version-specific. **Scope:** agent-agnostic. **Last verified:** 2026-09.

### L-125 Cron and scheduled-job safety guards such as dev flags, dry runs, and halts can be fake

**Symptom:** A job's dev flag doesn't actually isolate writes from production, a blocked dry-run mode gets worked around with a read-only rewrite, a rerun guard checks a count instead of actually halting, a duplicate job launches without checking for an in-flight run, or a destructive operation's safety window closes silently over time.

**Rule:** Verify that a scheduled job's safety mechanisms do what their name implies. Test that a dev flag truly isolates writes, confirm a dry run is genuinely read-only rather than blocked-and-worked-around, make a rerun guard an actual halt rather than a soft count check, check for an in-flight run before launching a scheduled job, and periodically re-verify that a destructive-operation safety window hasn't quietly closed.

**Why:** A safety mechanism's name, such as a dev flag, dry-run mode, rerun guard, or safety window, is often trusted to work as described without ever being exercised against the exact failure it claims to prevent, so it can pass review while a dev flag still writes to production, a dry run gets rerouted around instead of blocked, a rerun guard only logs instead of halting, or its protective window closes as surrounding code changes.

**Confidence:** High (Merged from six independently observed incidents across distinct jobs and safety-mechanism types.). **First seen:** 2026-06. **Applies to:** Scheduled or automated data jobs with named safety mechanisms (dev flags, dry runs, rerun guards, safety windows); not version-specific. **Scope:** agent-agnostic.

### L-126 MAX() or 'pick the latest row' logic can silently pick the wrong record

**Symptom:** A query meant to return the most recent record instead returns one that is lexically largest, chronologically stale, or left over from before a bulk backfill, while the query itself runs without error and looks like it answered the question.

**Rule:** Do not use a plain MAX() or ORDER BY on an ID or timestamp column to mean 'most recent' without first confirming that column is monotonic and reflects true recency. A bulk backfill, a shared 'last modified' column, or a GUID-style ID can each break the 'latest wins' assumption, so prefer an explicit, audited sequencing key over an assumed one.

**Why:** An identifier or timestamp column only encodes recency when nothing else ever rewrites or reassigns it, and a backfill or a shared audit column breaks that assumption without changing the query's shape.

**Confidence:** High (the same failure shape recurred across several distinct datasets and pipelines). **First seen:** 2026-06. **Applies to:** not version-specific, SQL and dataframe pipelines generally. **Scope:** agent-agnostic.

### L-127 Missing an explicit tiebreaker makes ordering, dedup, and exports nondeterministic

**Symptom:** An ORDER BY, ROW_NUMBER, dedup, or exported file produces a different arbitrary row or row order between runs, even though the query text has not changed.

**Rule:** Any query that orders, deduplicates, or trims rows needs an explicit, monotonic, uniquely discriminating tiebreaker column. A constant-valued column, an upstream field with tie-breaking gaps, or an unordered export will otherwise pick a different row silently as the underlying data or execution plan shifts.

**Why:** An ordering or dedup step relies on a column that is not guaranteed unique or monotonic across ties, so the engine is free to pick a different winning row each time the underlying data or execution plan shifts even though nothing in the query changed.

**Confidence:** High (merged from six independently generated candidate observations across six distinct incidents in the corpus). **First seen:** 2026-06. **Applies to:** any SQL engine with ORDER BY, window functions, or row-trimming logic, not version-specific. **Scope:** agent-agnostic.

### L-128 Ratio and rate metrics silently break when numerator and denominator use different grains

**Symptom:** A rate or ratio metric compared across two dashboards or two time periods doesn't match, or mathematically exceeds 100%, or one 'more accurate' recomputation drops most of the intended population, even though each side of the calculation is individually correct.

**Rule:** Before comparing or shipping any ratio or rate metric, verify the numerator and denominator share the same population, grain, and date cohort. If a rate can exceed 100% or a denominator is scoped to a status subset, surface that as a defined edge case rather than silently fixing or hiding it.

**Why:** A rate metric's numerator and denominator can each be computed correctly in isolation and still diverge from another version of the same metric, because one side quietly filters to a different population, grain, or date cohort than the other, and this recurred across otherwise unrelated metrics.

**Confidence:** Medium (merged from many independently generated candidates across distinct incidents in the corpus.). **First seen:** 2026-06. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-129 A label's existence or a row's existence is not proof of the condition it's assumed to represent

**Symptom:** A string label is used as a filter without checking it against live data first, a row's mere existence is treated as proof a condition holds rather than as a necessary but not sufficient signal, and a safeguard that relies on the absence of a row is invisible; nobody can see it is protecting anything until it silently stops.

**Rule:** Verify a string label against live data before using it as a filter, treat row-existence checks as necessary but not sufficient for validity, and do not rely on the mere absence of a row as your only safeguard. Each of these gives false confidence that a check verified more than it did.

**Why:** A label or a row's mere presence only correlates with the condition it is assumed to represent, so both can drift out of sync with the live data, or a protective absence can quietly disappear, without any check ever noticing.

**Confidence:** Medium (several distinct incidents; split out from a larger filter and check-honesty composite lesson). **First seen:** 2026-05. **Applies to:** SQL and data-pipeline filters and validation checks; not version-specific. **Scope:** agent-agnostic.

### L-130 Filter order and filter target both change what a filter actually verifies

**Symptom:** An exclusion filter applied before deduplication lets rows through that dedup would otherwise have removed, and a filter applied to a display column a join produced, rather than the join key underneath it, silently matches or misses rows the underlying key would not.

**Rule:** Apply exclusion filters after deduplication, not before, and filter on the actual join key rather than a display column a join happened to produce. Both mistakes look correct in isolation but change which rows a filter actually keeps.

**Why:** Filtering before deduplication runs, or filtering on a derived display column instead of the key underneath it, changes which population a filter is really evaluated against, so a check that looks right on its own can still admit or drop rows it was meant to catch.

**Confidence:** Medium (two distinct incidents, split out from a larger composite filter and check-honesty lesson). **First seen:** 2026-05. **Applies to:** SQL and data pipeline filter and join construction, not version-specific. **Scope:** agent-agnostic.

### L-131 Show a genuine data gap honestly instead of masking it with a default value

**Symptom:** A pipeline or report fills a real gap in the data with a default value instead of surfacing the gap, so an absence of data becomes indistinguishable from a legitimate zero or a normally-filled value, and any downstream comparison across segments quietly treats the empty one as if it matched the rest.

**Rule:** When a genuine data gap exists, represent it explicitly (null, missing, or a flagged state) rather than defaulting it to a normal-looking value, and check that every segment in a comparison actually has data before assuming the same logic holds across all of them.

**Why:** Filling a missing value with a default instead of flagging the gap made a segment with no real data look, to downstream comparison logic, like it matched the pattern of segments that had data.

**Confidence:** Medium (based on a single incident, but the masking-a-gap-with-a-default mechanism generalizes across pipelines). **First seen:** 2026-06. **Applies to:** not version-specific. **Scope:** agent-agnostic.

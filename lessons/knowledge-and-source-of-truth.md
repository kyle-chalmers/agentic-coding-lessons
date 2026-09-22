# Knowledge Bases, Memory and Source of Truth

**Scope:** Applies to any setup where an agent keeps notes, memory files, or docs across sessions, whatever the host tool.

These lessons are about the notes an agent keeps and the docs it trusts: how to structure them so they stay true, how to search them, and how to keep a document from quietly diverging from the thing it describes.

Lessons in this file: 4

- [L-056 Check existing knowledge base coverage before writing a new note](#l-056-check-existing-knowledge-base-coverage-before-writing-a-new-note)
- [L-058 Write deferred decisions into a durable file the moment you make them, not into session memory](#l-058-write-deferred-decisions-into-a-durable-file-the-moment-you-make-them-not-into-session-memory)
- [L-060 Describe a fixed bug's pattern in documentation, not the exact identifier that triggered it](#l-060-describe-a-fixed-bugs-pattern-in-documentation-not-the-exact-identifier-that-triggered-it)
- [L-061 Separate mutable current state from append only history in knowledge entries](#l-061-separate-mutable-current-state-from-append-only-history-in-knowledge-entries)

---

### L-056 Check existing knowledge base coverage before writing a new note

**Symptom:** Compiling raw session logs into a curated knowledge base risks creating a new standalone article for every session that touches a topic, even when the content just continues something already documented, fragmenting the base with near duplicates.

**Rule:** Before adding a new article to a compiled knowledge base, check it against recently written notes on the same period or topic; fold incremental content into an existing article and reserve new standalone articles for genuinely new concepts.

**Why:** Treating each session's notes as a fresh article instead of checking for an existing one on the same topic silently fragments a knowledge base into near duplicate entries that drift out of sync with each other.

**Confidence:** High (The same editorial decision was independently reached in two separate compilation passes about a month apart.). **First seen:** 2026-06. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-058 Write deferred decisions into a durable file the moment you make them, not into session memory

**Symptom:** A follow-up item or decision only ever exists inside a chat or agent session transcript; weeks later nobody can reconstruct what was decided or why, because nothing was written to a place anyone would think to look.

**Rule:** The moment you defer an item or make a decision worth remembering, write it into a durable, checked-in location, such as a roadmap or backlog file in the repo, or a ticket, rather than leaving it in chat history or session notes. Do this even when no external tracker is set up yet; a plain file in the repo is enough.

**Why:** Chat and session history is not addressable by future work the way a checked-in file is, so anything left only there decays out of reach once the session that produced it is gone, and this recurred.

**Confidence:** High (One incident shows the practice working when followed, and a separate incident shows the cost of skipping it, which reinforces the rule from both directions.). **First seen:** 2026-07. **Applies to:** not version-specific. **Scope:** agent-agnostic.

### L-060 Describe a fixed bug's pattern in documentation, not the exact identifier that triggered it

**Symptom:** An explanatory doc about a fixed defect quotes the specific record ID, ticket number, or value involved as an illustrative example, and a later search for that exact value returns a false-positive hit from the doc itself.

**Rule:** When writing up a fixed defect for future readers, describe the general pattern of the mistake instead of embedding the exact identifier or value involved, so a later search for that value is not polluted by the explanation.

**Why:** Full-text search treats an explanatory mention of a value the same as a live occurrence of it, so embedding a literal identifier in documentation turns that documentation into a false-positive source for any future search on that identifier.

**Confidence:** Medium (Single observed instance.). **First seen:** 2026-07. **Applies to:** Any documentation or knowledge base that gets searched by exact string or ID match, regardless of host tool; not version-specific.. **Scope:** agent-agnostic.

### L-061 Separate mutable current state from append only history in knowledge entries

**Symptom:** Knowledge entries mix ongoing facts that can change, such as current status, with dated historical events in the same free form section, so old superseded claims linger unnoticed and contradict the current state.

**Rule:** Give each knowledge entry an explicit current state section that gets overwritten on every update, kept separate from an append only dated log section, and periodically lint the state section for dated language that means a historical claim leaked into it.

**Why:** When a status claim and a historical event share one unstructured section, updating the entry tends to add a new line instead of overwriting the old one, so a superseded claim keeps reading as current until something forces a full re-read.

**Confidence:** High (Structural fix implemented and measured against the existing corpus, not just theorized.). **First seen:** 2026-08. **Applies to:** not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs explain how to load memory files but say nothing about the internal structure that keeps a long lived memory file from accumulating silently stale claims; this is a format convention for the content itself.
**Related:** [Claude Code memory](https://code.claude.com/docs/en/memory)

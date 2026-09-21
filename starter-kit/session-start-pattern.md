# Session-start injection pattern

A "hook" here means a script the agent host runs automatically at a defined
point (session start, session end, before a context compaction) rather than
a script the agent chooses to run. This describes a pattern for a
SessionStart hook that hands a new session useful context automatically,
instead of the person re-explaining where things stand every time.

## Assemble context in priority order

Build the injected text as an ordered list of sections, most important
first, something like:

1. Today's date, written out in full. An agent that only sees relative
   dates from old files will get "yesterday" and "last week" wrong.
2. A short brief of work currently in progress, if one exists.
3. The tail end of the most recent daily log entries, if the setup keeps
   one.
4. A recency slice of a compiled knowledge index (see the link below), if
   one exists.

## Budget every section, and the whole thing

Give each section a character cap, and give the assembled result a total
cap. The reason for both: without a per-section cap, one section that
happens to be unusually long (a daily log from a long day, a brief that
grew past its usual size) can silently crowd out every section after it. A
total cap on top of that keeps the whole injection from growing without
bound even if every section stays under its own limit.

## Degrade gracefully

Any one of these sources might not exist yet, or might be empty, on a given
machine or a given day. Missing a source should mean that section is
skipped, not that the hook fails. A SessionStart hook that throws an error
because a log file does not exist yet is worse than one that silently skips
that section.

## Keep it fast and local

SessionStart hooks typically run under a tight timeout, on the order of
10 to 15 seconds. Keep the hook to local file reads: tailing log files,
reading an index, checking a date. Anything that calls out to a network
service risks blowing the timeout on a slow connection and delaying every
session start.

## Guard against re-entrancy

If anything in your setup launches a headless agent run from inside a hook
(for example, a scheduled pipeline that itself starts a session), that
headless run will also trigger SessionStart. Without a guard, this can
recurse. Set an environment variable before launching the headless run, and
have the hook check for that variable and exit immediately if it is set.

## Mirror the pattern across tools

This is not specific to one agent host. Gemini CLI has its own SessionStart
and SessionEnd hooks that can run the same kind of script. Codex does not
have hooks in the same sense, but it reads an AGENTS.md file at the start of
a session, so the equivalent there is keeping AGENTS.md itself current
rather than injecting fresh context through a script.

## What actually gets injected

The idea this pattern assumes is a compiled knowledge base: an LLM-maintained
personal knowledge index, built by periodically summarizing your own session
logs into durable notes, that lives separately from the raw transcripts.
What a SessionStart hook injects is a slice of that compiled index, never the
raw transcripts themselves. Raw logs are the input to compilation, not
something you want a new session reading cold.

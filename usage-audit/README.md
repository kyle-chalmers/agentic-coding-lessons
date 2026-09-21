# How I measured my own usage

## Why measure

I did not set out to write a usage audit. I set out to answer a narrower
question: why does one week feel tight against usage limits (the amount of
work you can ask an agent to do in a given window) while another week does
not, and why does a session sometimes stall for reasons that have nothing to
do with the actual task. The two real constraints on running a coding agent
day to day are usage limits and context, meaning the token budget available
to the model inside a single conversation, which shrinks as skills, memory
files, and MCP servers (background services that add tools to a session) get
loaded into every turn. My intuition about where that budget went turned out
to be wrong more often than it was right. The only way I found to know for
sure was to measure it directly, so I ran every measurement tool I had
against my own history and read what came back instead of guessing.

## The tools

`/insights` renders an HTML report of how you actually work: recurring
friction, what is going well, and concrete suggestions pulled from real
sessions rather than from a survey you fill out about yourself. It analyzes
up to 200 sessions it has not looked at before and writes its output under
`~/.claude/usage-data/`, so old runs stay around to compare against.

`/doctor` is an interactive setup checkup. It compares everything loaded
into every session (skills, plugins, MCP servers) against how often you
actually use each one, flags hooks (scripts the agent host runs
automatically around an action, such as after every file edit) that run
slowly, and checks your installed version.

`claude doctor` is a separate, narrower command that only checks the CLI
installation itself: version, update channel, basic health. It says nothing
about your skills, plugins, or how you actually work.

`/skill-doctor` reports, per skill, how much it costs in context on every
single turn versus how often you actually invoked it over the last seven
days. It also runs headless, meaning you can call it non-interactively with
a `-p` flag and pipe the output somewhere, so it can feed a scheduled job
instead of needing you at the keyboard.

`/usage` and `/context` give you live numbers: how close you are to a usage
limit right now, and how full the current conversation's context window is
right now. Neither is historical. Both are a snapshot of this exact moment,
not a trend.

Last, I run a homegrown monthly audit outside all of the above, because none
of the built-in tools give you a month-over-month trend on their own. It
classifies interactive sessions, meaning ones where I was actually typing,
as opposed to headless sessions kicked off by a scheduled job, into a
handful of repeated patterns, then counts, per distinct session rather than
per message, how often a skill built for that pattern actually fired.
Before counting anything, it collapses templated prompts, meaning the same
boilerplate message issued automatically by a script, so a nightly job
sending the same text thirty times does not get counted as thirty
conversations with a person behind them.

## This run

- /insights: run and summarized
- /doctor: run and summarized
- claude doctor: run (clean)
- /skill-doctor: run and summarized

## What I found

- Interactive session volume fell by roughly a third across the most recent
  month I compared, as headless, scheduled jobs took over work that used to
  happen in a live back-and-forth. That is a change in the shape of my
  usage, not just a drop in it.
- The single best-adopted skill, by a wide margin, is the one that ships a
  branch end to end: stage, commit, open a pull request, merge it. It is the
  clearest evidence I have that a skill earns its keep once it is trusted
  enough to reach for by habit.
- A skill I built specifically to turn a tracker or chat link into a
  verified, drafted answer fires in only a low single-digit share of the
  sessions shaped exactly for that job, and it has held at that low share
  two months running. I built the thing, I hit that exact shape of task
  constantly, and I still mostly do the work by hand instead. A gap that
  does not close on its own after two audits needs a direct look at why, not
  a third audit.
- Roughly a quarter of my interactive sessions contain me answering a
  clarifying question the agent asked up front, despite a standing
  instruction to proceed without stopping to ask unless the situation
  genuinely calls for it. A rule written into a memory file is not the same
  thing as a rule the agent reliably follows without reinforcement.
- The median interactive session is two or three messages, while a handful
  run to dozens of messages in a row instead of handing off to a fresh
  session before context gets unwieldy.
- I switch models in the middle of a session often enough for it to show up
  as its own pattern in the data, which reads less like a considered choice
  and more like compensating turn by turn for cost or capability instead of
  deciding up front.
- Two skills sat at zero invocations across two consecutive monthly
  windows. One of the two is built to be rare on purpose, since it is only
  meant to fire when the agent is visibly stuck, so zero uses there is fine.
  The other has no such excuse and is a genuine retirement candidate.
- The subagent (a smaller, separately invoked agent instance) I use for
  read-only reconnaissance, meaning it can look things up and report back
  but cannot edit anything, is the single most heavily used custom artifact
  I have, ahead of every skill. Handing off "go find out X and report back"
  instead of doing it myself in the main conversation pays off constantly.
- Calls to a shell outnumber file edits by about five to one across the
  window. Most of a session is spent looking and checking, not writing.
- A handful of sessions in the window died at a usage limit before producing
  any usable output at all, which is a pure loss: the exploration happened
  and the result never landed.
- More than one long session lost real time to an external reviewer process
  that hung waiting on input it was never going to receive.
- A recurring shape of "the work is actually done but I cannot ship it" is
  not the work itself, it is the last mile: an authentication prompt, a
  stale CLI, a permissions mismatch surfacing only once everything else is
  finished.

## What I changed, and what each tool is for

The interactive `/doctor` run found real, previously invisible waste sitting
in every single session's context: several thousand tokens spent on synced
skill listings I had never invoked once, a plugin's MCP server that failed
its authentication check every session without ever surfacing that fact to
me, two connectors doing the same job, and an advisory lint hook (a script
that runs after every edit and prints warnings without blocking anything)
that was taking multiple seconds per edit. It also flagged that my own
auto-memory index, the file that carries context forward between sessions,
was the single largest file loaded automatically on every session start.

I turned off the unused skill listings, disabled the plugin whose MCP
server kept failing authentication (its job was already covered by a
connector that works), turned off the duplicate connectors and a few unused
ones, and left the slow hook as a flagged finding to fix separately rather
than changing it in the same pass. `claude doctor` came back clean on the CLI itself: a
native install, a handful of patch versions behind, auto-update disabled by
an environment variable on purpose rather than by accident, updated on the
spot. Every change from the cleanup pass is reversible; none of it deleted
anything.

What each tool is good at, and what it is not: `/insights` is the only one
that reads the actual shape of a conversation, what kind of work it was,
what went wrong, what worked well, but it samples a subset of sessions, so
it is a trend line, not a full count. `/doctor` and `/skill-doctor` are
precise about cost and adoption but tell you nothing about whether the
underlying work went well. `claude doctor` only tells you the CLI itself is
healthy, nothing about how you use it. `/usage` and `/context` are only ever
a snapshot of right now. None of them, alone, gives you a trend across
months without somewhere to store past runs and a way to diff against them,
which is the gap my homegrown monthly audit exists to fill.

## Running this yourself

To reproduce this on your own setup, run the tools in this order: start with
`/insights` for the qualitative picture of how you actually work session to
session, then `/doctor` for the interactive cleanup pass over everything
loaded into every session, then `claude doctor` as a quick sanity check that
the CLI itself is healthy, then `/skill-doctor` (headless with `-p` if you
want it scriptable) for the per-skill cost and adoption numbers. Check
`/usage` and `/context` whenever you want the live picture rather than a
historical one. If you want a trend instead of a single point in time, save
each run's output somewhere durable and write a small script of your own
that classifies your interactive sessions into the patterns you actually see
yourself repeating, counted per session rather than per message, and diff
each month against the last.

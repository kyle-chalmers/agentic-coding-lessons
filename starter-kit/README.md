# Starter kit

A small set of portable config files for working with a coding agent. I
built these for my own use across a few different projects and I am
sharing them here in case they save someone else the setup time. None of
it is specific to any one codebase; it is all working-style and plumbing.

## What is in here

| File | What it does |
|---|---|
| `AGENTS.md` | Tool-neutral working-style rules: when to keep going, when to stop and ask, what "done" means, how to delegate. |
| `CLAUDE.md` | A one-line stub that points Claude Code at `AGENTS.md`, so the rules live in one place. |
| `GEMINI.md` | The same stub pattern for Gemini CLI, using its `@./AGENTS.md` import form. |
| `agents/scout.md` | A subagent definition for Claude Code: read-only reconnaissance on a cheaper model. Read-only by instruction; drop Bash from its tool list if you need that enforced. |
| `hooks/post-edit-lint.sh` | A hook, meaning a script the agent host runs automatically, that lints a file right after it is written or edited and prints findings without blocking. |
| `settings.hooks.example.json` | The settings.json snippet that wires the lint hook into Claude Code. |
| `memory-conventions.md` | The pattern I use for durable, cross-session memory files, and the rule for keeping them from going stale. |
| `session-start-pattern.md` | The pattern for injecting useful context automatically at the start of a session. |

## Install

### Claude Code

1. Copy `AGENTS.md` and `CLAUDE.md` into the root of a repository you work
   in, or into `~/.claude/` if you want the rules to apply everywhere. Edit
   `AGENTS.md` first (see below) before you rely on it.
2. Copy `agents/scout.md` to `~/.claude/agents/scout.md` to make the
   `scout` subagent available.
3. Copy `hooks/post-edit-lint.sh` to `~/.claude/hooks/post-edit-lint.sh`
   and make it executable: `chmod +x ~/.claude/hooks/post-edit-lint.sh`.
4. Merge the contents of `settings.hooks.example.json` into your
   `~/.claude/settings.json` under its `hooks` key. If you already have
   other hooks configured, add this entry alongside them rather than
   replacing the file. The session-start, pre-compaction, and session-end
   hooks described in `session-start-pattern.md` are a pattern, not shipped
   scripts; wire them only once you have written your own.

### Codex

Codex reads `AGENTS.md` natively, so copying that file into a repository
root is enough to get the working-style rules. Codex has its own hook events
(check its hooks documentation for the current names), so the session-start
pattern applies there too once adapted; the subagent definition, the lint
hook script, and the settings snippet here are Claude Code specific.

### Gemini CLI

Copy `GEMINI.md` next to `AGENTS.md`. Gemini CLI also supports SessionStart
and SessionEnd hooks, so the pattern in `session-start-pattern.md` applies
there too, though the hook itself would need to be adapted to Gemini CLI's
own hook format rather than copied as-is.

## What is Claude Code only

`agents/scout.md`, `hooks/post-edit-lint.sh`, and
`settings.hooks.example.json` are Claude Code specific: subagent
definitions with this frontmatter and this hook wiring are a Claude Code
feature. `AGENTS.md`, `memory-conventions.md`, and `session-start-pattern.md`
are written to be useful regardless of which agent host you use.

## What to edit first

Do not use these files unedited. At minimum:

- The stop-and-ask list in `AGENTS.md`: the specific things that should
  block on your approval will differ by project and by how much you trust
  the agent with that repository.
- The voice guide pointer in `AGENTS.md`: it assumes a voice or style guide
  might exist somewhere in your setup. If you have one, point to it; if you
  do not, drop that line.
- The linters wired into `hooks/post-edit-lint.sh`: it currently covers
  Python (ruff), SQL (sqlfluff), and shell scripts (shellcheck). Add or
  remove languages to match what you actually write, and each one is a
  no-op if its linter binary is not installed, so there is no harm in
  leaving one wired up that you do not currently use.

# Changelog

All notable changes to this repo. The format follows Keep a Changelog; versions follow semantic versioning.

## [Unreleased]

## [0.1.0] - 2026-09-21

### Added
- Initial lesson batch: 151 verified lessons across 16 themes (10 about using coding agents, 6 general engineering), rendered from `lessons/lessons.json`.
- Starter kit: tool-neutral `AGENTS.md` with Claude Code and Gemini CLI stubs, a read-only reconnaissance subagent, an advisory post-edit lint hook and its settings wiring, and writeups of the memory-conventions and session-start injection patterns.
- Usage chapter: how the usage was measured with `/insights`, `/doctor`, `claude doctor`, `/skill-doctor`, `/usage`, `/context`, and a homegrown monthly audit.
- Build tooling: JSON Schema, canonical hashing, deterministic renderer, link checker, structural leak scanner, and the `verify.sh` gate that CI runs.
- `SOURCES.md`, `CONTRIBUTING.md`, `ROADMAP.md`.

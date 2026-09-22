# Skills & Plugin Management

**Scope:** Installing, validating, and maintaining skills and plugins so what is configured matches what is loaded and running.

A plugin being committed to config, listed by an installer, or claimed by an update UI is not the same as it being installed and active, and I have been burned by that gap more than once. These lessons are how I verify a skill or plugin does what its configuration says.

Lessons in this file: 8

- [L-083 A plugin cannot declare its own install scope, the consuming project's config has to](#l-083-a-plugin-cannot-declare-its-own-install-scope-the-consuming-projects-config-has-to)
- [L-084 A git-source plugin install can silently pull an unreleased tip, not a tagged release](#l-084-a-git-source-plugin-install-can-silently-pull-an-unreleased-tip-not-a-tagged-release)
- [L-086 Committing a plugin's enablement config is not the same as the plugin being installed](#l-086-committing-a-plugins-enablement-config-is-not-the-same-as-the-plugin-being-installed)
- [L-087 Layer org-specific rules onto a shared plugin with a committed overlay file, not a fork](#l-087-layer-org-specific-rules-onto-a-shared-plugin-with-a-committed-overlay-file-not-a-fork)
- [L-088 Quote a frontmatter value that starts with a square bracket, or the file can lose its metadata](#l-088-quote-a-frontmatter-value-that-starts-with-a-square-bracket-or-the-file-can-lose-its-metadata)
- [L-089 Never duplicate a plugin's auto-loaded hook manifest entry](#l-089-never-duplicate-a-plugins-auto-loaded-hook-manifest-entry)
- [L-090 Port a useful skill to every coding agent you actually use, not just the one you built it in](#l-090-port-a-useful-skill-to-every-coding-agent-you-actually-use-not-just-the-one-you-built-it-in)
- [L-091 Query the target system's live config before customizing a generic template](#l-091-query-the-target-systems-live-config-before-customizing-a-generic-template)

---

### L-083 A plugin cannot declare its own install scope, the consuming project's config has to

**Symptom:** There is no manifest field for a plugin or extension to force itself into project-wide versus user-wide install scope. Installers that do expose a scope flag default to the wrong one, so teammates who clone the repo silently do not get the plugin and its hooks stay inert.

**Rule:** Do not look for a way to make a plugin dictate its own install scope. Check the platform's actual settings hierarchy, user versus project versus local config, and set scope there explicitly, usually by committing a project-level enablement file with any scope flag pinned to project, so a fresh clone resolves it without a manual reinstall.

**Why:** Plugin scope is decided by whichever settings layer the host reads, not by anything the plugin itself declares, so only a committed project-level config reliably reaches every clone.

**Confidence:** High (Confirmed directly on one real install where the scope flag defaulted wrong.). **First seen:** 2026-07. **Applies to:** Claude Code plugins and settings, not version-specific. **Scope:** claude-code-primary.
**Beyond the docs:** The docs describe the settings hierarchy but not that plugin installers can silently default to the wrong scope, leaving hooks inert until a project-level file pins it explicitly.
**Related:** [Claude Code plugins docs](https://code.claude.com/docs/en/plugins), [Claude Code settings docs](https://code.claude.com/docs/en/settings)

### L-084 A git-source plugin install can silently pull an unreleased tip, not a tagged release

**Symptom:** A plugin or dependency installed from a raw git source turns out to already include commits from the default branch that have not been through a tagged release, so what you have installed is ahead of, or different from, what a version number would suggest.

**Rule:** When a plugin or dependency installs from a git repository rather than a package registry, check whether the install mechanism tracks a specific release tag or just the default branch tip. If it tracks the tip, treat every install as pulling unvetted, unreleased changes, and pin to a commit or tag when you need reproducibility.

**Why:** A marketplace or package manager that installs straight from a git source can point at the default branch instead of a release tag, so an install labeled as the latest version silently carries commits that have not gone through any formal release.

**Confidence:** Medium (Single discovery; not yet verified across other git-source installs.). **First seen:** 2026-08. **Applies to:** Claude Code plugin marketplaces installed from a git source. **Scope:** claude-code-specific. **Last verified:** 2026-09.
**Beyond the docs:** The docs describe how to install and manage plugins but not that a git-backed marketplace source can resolve to a moving branch tip instead of a fixed release, so installs are not automatically reproducible.
**Related:** [Plugins](https://code.claude.com/docs/en/plugins)

### L-086 Committing a plugin's enablement config is not the same as the plugin being installed

**Symptom:** Onboarding instructions tell a new user to commit or pull a config file that registers a shared plugin or skill, and the user treats that step as finished setup, but the tool is still not actually installed or active until a separate install/activation step runs.

**Rule:** When you write onboarding steps for a shared plugin, skill, or tool config, split 'this file registers the tool' from 'this step installs and activates the tool' into two explicit, separately verifiable steps, and have the user confirm the tool actually runs before calling onboarding done.

**Why:** A config file that registers a tool only makes it available to be installed, so treating that commit as the finish line skips the separate activation step and leaves the tool silently absent.

**Confidence:** High (Directly root-caused as a contributing factor to a real onboarding failure.). **First seen:** 2026-09. **Applies to:** Claude Code plugin and skill onboarding where enablement is committed as config, not version-specific. **Scope:** claude-code-primary.
**Beyond the docs:** The docs already describe install as a distinct step after a plugin is registered, but they do not cover the specific failure mode where a team treats a committed enablement file as finished onboarding for a teammate who has not run any install or activation step at all.
**Related:** [Plugins](https://code.claude.com/docs/en/plugins)

### L-087 Layer org-specific rules onto a shared plugin with a committed overlay file, not a fork

**Symptom:** A team wants to add org-specific context to a shared skill or plugin, and the only option that seems available is copying and editing its source, which then drifts from upstream.

**Rule:** Give a shared tool an optional, committed overlay file it reads for local context, instead of forking its logic, so the base tool keeps receiving upstream fixes while local knowledge stays reviewable in version control.

**Why:** Forking a shared tool's source to add local context permanently cuts that copy off from upstream fixes, while a committed overlay file the tool reads at run time keeps the two concerns separate so both stay maintainable.

**Confidence:** High (shipped and reused across multiple modules of the same effort). **First seen:** 2026-09. **Applies to:** any shared skill or plugin that can read an external overlay or config file; not version-specific. **Scope:** claude-code-primary.
**Beyond the docs:** The docs explain how to author a plugin or skill but not the overlay-file convention for keeping org-specific customizations out of a fork of the tool itself.
**Related:** [Plugins](https://code.claude.com/docs/en/plugins), [Skills](https://code.claude.com/docs/en/skills)

### L-088 Quote a frontmatter value that starts with a square bracket, or the file can lose its metadata

**Symptom:** A skill or command's metadata field, such as an argument hint, silently loads as empty at install time with no visible error, because its YAML value looked like plain text but was not valid YAML.

**Rule:** When a frontmatter field's natural-language value starts with an opening square bracket, quote the whole value as a string. Unquoted, YAML reads it as a flow sequence, the trailing words make the document invalid, and a loader that swallows the parse error drops the field or the whole file's metadata without telling you.

**Why:** YAML treats a leading unquoted bracket as the start of a flow-sequence node, so the trailing words make the document invalid, and a frontmatter loader that catches the parse error instead of surfacing it leaves the file with no metadata at all.

**Confidence:** High (Confirmed root cause and fix, plus a regression test that reproduces it.). **First seen:** 2026-06. **Applies to:** any tool that loads YAML frontmatter and tolerates parse errors, including Claude Code skill and command files. **Scope:** agent-agnostic. **Last verified:** 2026-09.
**Beyond the docs:** The docs describe the frontmatter fields but do not warn that an unquoted value starting with a bracket makes the document invalid, or that the loader then drops the file's metadata rather than reporting an error.
**Related:** [Skills](https://code.claude.com/docs/en/skills)

### L-089 Never duplicate a plugin's auto-loaded hook manifest entry

**Symptom:** A plugin fails to load entirely, with a duplicate-file error, even though the hook code itself is correct.

**Rule:** When a plugin framework auto-loads a hooks file by convention, do not also declare that same path in the plugin manifest; reserve the manifest's hooks key for files the convention does not already pick up.

**Why:** A manifest that re-declares a path already picked up by convention creates two registrations for one file, and the framework refuses to load the whole plugin rather than pick one.

**Confidence:** High (Reproduced, root-caused, and fixed in a released version.). **First seen:** 2026-07. **Applies to:** Claude Code >=2.1 plugins with an auto-loaded hooks/hooks.json. **Scope:** claude-code-specific. **Last verified:** 2026-09.
**Beyond the docs:** The docs describe the manifest hooks key and the auto-load convention separately but do not warn that declaring both for the same file fails the entire plugin instead of just being redundant.
**Related:** [Hooks](https://code.claude.com/docs/en/hooks), [Plugins](https://code.claude.com/docs/en/plugins)

### L-090 Port a useful skill to every coding agent you actually use, not just the one you built it in

**Symptom:** A reusable skill or instruction pack gets installed for one coding agent and then sits unused by the other agents on the same machine, even though its content is generic and would work anywhere.

**Rule:** When you adopt a new reusable skill or prompt pack, check whether each coding agent you actually use has an equivalent skills or instructions directory, install it to all of them, and note which agents lack that mechanism so you can revisit later.

**Why:** A skill installed into only one agent's configuration directory is invisible to every other agent, because each agent discovers skills from its own directory and none of them scan a sibling agent's config.

**Confidence:** Medium (single documented instance, but it covers a concrete completed action across two of three agents). **First seen:** 2026-06. **Applies to:** not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs describe how Claude Code discovers and loads skills from its own directory; they say nothing about a workflow for keeping the same skill available across multiple coding agents installed on one machine.
**Related:** [Skills](https://code.claude.com/docs/en/skills)

### L-091 Query the target system's live config before customizing a generic template

**Symptom:** A generic workflow template or skill built for one destination system is pointed at a different one, and creation fails with a cryptic error because a required field or an exact format was left generic instead of matching what that destination actually enforces.

**Rule:** Before adapting a reusable template or skill to a new destination, query that destination's live configuration for its required fields and enforced formats instead of guessing from the generic version, and hard-code any hard, non-optional rule you find directly into the template rather than leaving it as a placeholder.

**Why:** Two destination systems built from the same generic template can require nearly opposite sets of mandatory fields and formats, so a template that stays generic will validate against neither one in particular and only reveals the mismatch as a failure at creation time.

**Confidence:** Medium (Observed in one session against two different destination targets, including a hard failure that only cleared once the constraint was hard-coded.). **First seen:** 2026-09. **Applies to:** any reusable workflow template or skill adapted to a new destination system, not version-specific. **Scope:** agent-agnostic.
**Beyond the docs:** The docs cover how to author a skill in general terms; they do not walk through querying a specific destination's live constraints before adapting a template to it, which is the step that avoided a creation failure here.
**Related:** [Claude Code skills](https://code.claude.com/docs/en/skills)

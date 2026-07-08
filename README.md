# Freedom OS Onboarding

A public bootstrap Agent Skill for new way2freedom team members.

This repository is intentionally small and public. New members install this skill first, then ask Codex or Hermes to use it to set up their local Freedom OS workspace.

## Quick start

Default path for new members who already have Codex installed and logged in:

```bash
npx skills add way2freedom/freedom-os-onboarding -a codex
```

If both Codex and Hermes Agent are installed, install to both:

```bash
npx skills add way2freedom/freedom-os-onboarding -a codex -a hermes-agent
```

After installing, open Codex and say:

```text
Use the freedom-os-onboarding skill to install todo-dashboard.
Detect my available agents automatically. If Git or GitHub access is missing, guide me step by step.
```

## What this skill does

It guides an agent through:

1. Detecting local agents: Codex and/or Hermes Agent.
2. Checking Git, Node, Corepack, and pnpm.
3. Configuring Git identity if missing.
4. Setting up GitHub access with `gh`, SSH, or HTTPS credentials.
5. Cloning `way2freedom/skills` into `~/Code/github.com/way2freedom/skills`.
6. Installing requested thin skills into available agents.
7. Preparing project runtime, for example `projects/todo-dashboard`.
8. Registering MCP servers for Codex and/or Hermes.
9. Verifying installation with real local commands.

## Repository layout

```text
SKILL.md                     # bootstrap skill entrypoint
references/
  todo-dashboard.md          # todo-dashboard install flow
  github-access.md           # GitHub auth guide
  troubleshooting.md         # common setup issues
scripts/
  detect-agents.sh           # prints npx-skills agent flags
  install-team-skill.sh      # installs a skill to detected agents
  bootstrap-todo-dashboard.sh # prepares todo-dashboard runtime and MCP
```

## Safety

- Scripts do not ask for or store tokens.
- GitHub credentials are handled by `gh`, SSH, or Git credential helpers.
- MCP registration is explicit and uses local CLI commands.
- Project runtime setup happens only after the team repository is cloned locally.

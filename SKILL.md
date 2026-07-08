---
name: freedom-os-onboarding
description: "Bootstrap a new way2freedom team member into Freedom OS from Codex or Hermes: Git/GitHub setup, repo clone, thin skill install, project runtime setup, and MCP registration."
version: 0.1.0
type: pure-skill
agents:
  - codex
  - hermes-agent
capabilities:
  - onboarding
  - git-setup
  - github-auth
  - skill-install
  - mcp-registration
---

# Freedom OS Onboarding

Use this skill when a new team member needs to set up Freedom OS on a fresh machine.

Default assumption: the user has Codex installed and logged in. If Hermes Agent is also installed, support it too. If both are available, install team skills and MCPs for both. If only one is available, install for that one.

## Core rule

Do not assume `npx skills add` makes a TypeScript project usable. Skill installation only installs the thin Agent Skill instructions. Project runtime still needs dependency install, setup, build, verification, and MCP registration.

## Standard local paths

Use this default team path unless the user asks otherwise:

```text
~/Code/github.com/way2freedom/skills
```

## Detection flow

Run:

```bash
command -v codex >/dev/null && echo codex=present || echo codex=missing
command -v hermes >/dev/null && echo hermes=present || echo hermes=missing
git --version || true
node --version || true
corepack --version || true
pnpm --version || true
gh auth status || true
```

Agent mapping for `npx skills`:

```text
codex command  -> -a codex
hermes command -> -a hermes-agent
```

You may use:

```bash
./scripts/detect-agents.sh
```

from this skill directory if the script is available after installation.

## Install flow

1. Check local agents.
2. Check/install Git.
3. Check Git identity:

```bash
git config --global user.name || true
git config --global user.email || true
```

If missing, ask the user for name/email before setting them.

4. Check GitHub access. Prefer `gh auth status`; otherwise use SSH test:

```bash
ssh -T git@github.com
```

If neither works, guide the user through `gh auth login` or SSH key creation. Never ask the user to paste a token into chat.

5. Clone or update team repo:

```bash
mkdir -p ~/Code/github.com/way2freedom
cd ~/Code/github.com/way2freedom
if [ ! -d skills/.git ]; then
  git clone git@github.com:way2freedom/skills.git
fi
cd skills
git checkout v3
git pull --ff-only
```

6. Install the requested team thin skill to detected agents. For todo-dashboard:

```bash
npx skills add ./skills/todo-dashboard $(~/Code/github.com/way2freedom/freedom-os-onboarding/scripts/detect-agents.sh)
```

If the script path is not available, build flags manually:

```bash
# Codex only
npx skills add ./skills/todo-dashboard -a codex

# Codex + Hermes
npx skills add ./skills/todo-dashboard -a codex -a hermes-agent
```

7. Prepare project runtime if needed. For todo-dashboard, follow `references/todo-dashboard.md`.

8. Verify with real commands and summarize exact results.

## When installing todo-dashboard

Follow:

```text
references/todo-dashboard.md
```

Important distinctions:

```text
skills/todo-dashboard   = thin Agent Skill
services/todo-dashboard = thin MCP registration docs
projects/todo-dashboard = actual TypeScript project/runtime
```

## Safety boundaries

- Do not hardcode GitHub tokens, Feishu tokens, OpenAI keys, profile names, local IPs, or personal account identifiers.
- Do not commit or push in the team repo unless the user explicitly asks.
- Prefer preview/dry-run for MCP registration when available.
- Ask before running commands that need sudo, install OS packages, overwrite config files, or change GitHub credentials.

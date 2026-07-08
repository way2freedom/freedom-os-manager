#!/usr/bin/env bash
set -euo pipefail

repo_root="${FREEDOM_OS_REPO:-$HOME/Code/github.com/way2freedom/skills}"
repo_parent=$(dirname "$repo_root")

if ! command -v git >/dev/null 2>&1; then
  echo "git is required. Install Git first, then rerun." >&2
  exit 1
fi

mkdir -p "$repo_parent"
if [ ! -d "$repo_root/.git" ]; then
  git clone git@github.com:way2freedom/skills.git "$repo_root"
fi

cd "$repo_root"
git checkout v3
git pull --ff-only

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
"$script_dir/install-team-skill.sh" ./skills/todo-dashboard

cd projects/todo-dashboard
corepack enable
pnpm install
pnpm setup
pnpm check
pnpm build
pnpm test
pnpm run doctor

if command -v codex >/dev/null 2>&1; then
  codex mcp add todo-dashboard -- pnpm --dir "$PWD" mcp:start || {
    echo "Codex MCP registration failed. Preview config with: pnpm mcp:install --agent codex --mode prod" >&2
    exit 1
  }
  codex mcp list
fi

if command -v hermes >/dev/null 2>&1; then
  echo "Hermes detected. Preview Hermes MCP registration with:"
  echo "  cd $PWD && pnpm mcp:install --agent hermes --mode prod --profile default"
fi

#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
freedom_os_root="${FREEDOM_OS_ROOT:-/Users/winston/Code/github.com/way2freedom/freedom-os}"

cd "$repo_root"

echo "== Freedom OS Manager Registry =="
PYTHONPATH=src python3 -m freedom_os_manager.cli \
  --repo-root "$freedom_os_root" \
  capabilities check-installed || true
echo
PYTHONPATH=src python3 -m freedom_os_manager.cli capabilities list
echo

echo "== Local Agent Skills =="
if [ -d "$HOME/.agents/skills" ]; then
  find "$HOME/.agents/skills" -maxdepth 2 -name SKILL.md -print \
    | sed "s#^$HOME/.agents/skills/##; s#/SKILL.md\$##" \
    | sort
else
  echo "not found: $HOME/.agents/skills"
fi
echo

echo "== Codex MCP =="
if command -v codex >/dev/null 2>&1; then
  codex mcp list
else
  echo "codex command not found"
fi
echo

echo "== Hermes Skills =="
if command -v hermes >/dev/null 2>&1; then
  hermes skills list
else
  echo "hermes command not found"
fi
echo

echo "== Hermes MCP =="
if command -v hermes >/dev/null 2>&1; then
  hermes mcp list
else
  echo "hermes command not found"
fi

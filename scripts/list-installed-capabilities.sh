#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
freedom_os_root="${FREEDOM_OS_ROOT:-/Users/winston/Code/github.com/way2freedom/freedom-os}"

cd "$repo_root"

PYTHONPATH=src python3 -m freedom_os_manager.cli \
  --repo-root "$freedom_os_root" \
  capabilities list-installed "$@"

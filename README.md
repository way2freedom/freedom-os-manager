# Freedom OS Launcher

中文文档见：[README.zh-CN.md](README.zh-CN.md)。

Freedom OS Launcher is a small bootstrap repo. It only does two things:

1. prepare the local environment
2. clone or update the `way2freedom/freedom-os` main repository

It is not the place for ongoing capability management, MCP registration, or project runtime work. Those tasks live in the main `way2freedom/freedom-os` repository after the bootstrap step.

## Quick start

Install the launcher skill from GitHub:

```bash
npx skills add way2freedom/freedom-os-manager --skill freedom-os-launcher -a codex
```

If both Codex and Hermes Agent are installed, target both:

```bash
npx skills add way2freedom/freedom-os-manager --skill freedom-os-launcher -a codex -a hermes-agent
```

Then ask Codex:

```text
Use the Freedom OS Launcher to prepare my environment and clone the way2freedom/freedom-os repository.
Detect my available agents automatically. If Git or GitHub access is missing, guide me step by step.
```

## What it covers

- local Git, GitHub, Node, Corepack, and pnpm checks
- Git identity and GitHub auth setup when needed
- clone or update of `~/Code/github.com/way2freedom/freedom-os`
- handoff to the main repository for the actual Freedom OS workflows

## What it does not cover

- installing arbitrary capabilities
- registering MCPs as a primary responsibility
- project build, test, or runtime setup beyond the bootstrap handoff

## Repository layout

```text
README.md                  English launcher guide
README.zh-CN.md            Chinese launcher guide
src/freedom_os_manager/    Small local helper runtime kept for installed-state inspection
skills/freedom-os-manager/ Launcher skill package
```

## Local helper

This repository still ships a small local capability inventory helper for maintainers. It is separate from the launcher flow and exists only to inspect local installed-state data when needed.

```bash
PYTHONPATH=src python3 -m freedom_os_manager.cli capabilities list-installed
PYTHONPATH=src python3 -m freedom_os_manager.cli capabilities list-installed --json
./scripts/list-installed-capabilities.sh --json
```


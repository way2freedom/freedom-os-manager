# Freedom OS 启动器

英文文档见：[README.md](README.md)。

Freedom OS 启动器是一个很小的引导仓库，只负责两件事：

1. 先把本机环境准备好
2. 再 clone 或更新 `way2freedom/freedom-os` 主仓库

它不是持续做能力管理、MCP 注册或项目运行时工作的地方。真正的后续工作都在主仓库里完成。

## 快速开始

从 GitHub 安装启动器 skill：

```bash
npx skills add way2freedom/freedom-os-manager --skill freedom-os-launcher -a codex
```

如果本机同时安装了 Codex 和 Hermes Agent：

```bash
npx skills add way2freedom/freedom-os-manager --skill freedom-os-launcher -a codex -a hermes-agent
```

安装后可以直接让 Codex 执行：

```text
使用 Freedom OS 启动器帮我准备本机环境，并 clone way2freedom/freedom-os 仓库。
自动检测我可用的 Agent。如果缺少 Git 或 GitHub 权限，请一步步引导我完成。
```

## 覆盖内容

- 本机 Git、GitHub、Node、Corepack、pnpm 检查
- Git 身份和 GitHub 认证的缺失补齐
- clone 或更新 `~/Code/github.com/way2freedom/freedom-os`
- 把用户交接到主仓库里的实际工作流

## 不覆盖的内容

- 作为主职责去安装任意能力
- 作为主职责去注册 MCP
- 启动器之外的项目构建、测试或运行时准备

## 仓库结构

```text
README.md                  英文启动器说明
README.zh-CN.md            中文启动器说明
src/freedom_os_manager/    用于已安装状态检查的小型本机辅助运行时
skills/freedom-os-manager/ 启动器 skill 包
```

## 本机辅助工具

这个仓库仍然保留一个给维护者看的轻量能力清单工具，和启动器职责分开。它只用于查看本机已安装状态。

```bash
PYTHONPATH=src python3 -m freedom_os_manager.cli capabilities list-installed
PYTHONPATH=src python3 -m freedom_os_manager.cli capabilities list-installed --json
./scripts/list-installed-capabilities.sh --json
```


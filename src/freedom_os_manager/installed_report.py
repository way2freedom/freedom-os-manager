from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from typing import Any

from .installed import DEFAULT_LOCAL_SKILL_ROOT, compare_installed_registry


def render_installed_report(
    capabilities: dict[str, dict[str, Any]],
    *,
    local_skill_root: Path = DEFAULT_LOCAL_SKILL_ROOT,
    known_mcp_names: set[str] | None = None,
) -> str:
    report = build_installed_report(capabilities, local_skill_root=local_skill_root, known_mcp_names=known_mcp_names)
    lines: list[str] = []
    diff = report["registry_check"]
    lines.append("== Registry Check ==")
    lines.append(f"Compared installed skills in {diff['local_skill_root']}")
    lines.append(f"matching={diff['counts']['matching']}")
    append_names(lines, "missing_in_registry", diff["missing_in_registry"])
    append_names(lines, "stale_in_registry", diff["stale_in_registry"])
    append_names(lines, "drifted_installs", diff["drifted_installs"])
    lines.append("")
    lines.append("== Installed Capabilities By Platform ==")
    lines.extend(render_platform_table(report))
    return "\n".join(lines) + "\n"


def render_installed_report_json(
    capabilities: dict[str, dict[str, Any]],
    *,
    local_skill_root: Path = DEFAULT_LOCAL_SKILL_ROOT,
    known_mcp_names: set[str] | None = None,
) -> str:
    report = build_installed_report(capabilities, local_skill_root=local_skill_root, known_mcp_names=known_mcp_names)
    return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def append_names(lines: list[str], label: str, names: list[str]) -> None:
    lines.append(f"{label}={len(names)}")
    for name in names:
        lines.append(f"- {name}")


def build_installed_report(
    capabilities: dict[str, dict[str, Any]],
    *,
    local_skill_root: Path = DEFAULT_LOCAL_SKILL_ROOT,
    known_mcp_names: set[str] | None = None,
) -> dict[str, Any]:
    diff = compare_installed_registry(local_skill_root, capabilities, known_mcp_names)
    local_skills = {path.parent.name for path in local_skill_root.glob("*/SKILL.md")}
    codex_mcp = parse_codex_mcp(run(["codex", "mcp", "list"]))
    hermes_skills = parse_hermes_skills(run(["hermes", "skills", "list"]))
    hermes_mcp = parse_hermes_mcp(run(["hermes", "mcp", "list"]))

    rows: list[dict[str, Any]] = []
    lark_names: list[str] = []
    for name, record in sorted(capabilities.items()):
        if name.startswith("lark-"):
            lark_names.append(name)
            continue
        prepared = project_prepared(record)
        rows.append(
            {
                "name": name,
                "type": record.get("type", "unknown"),
                "codex": platform_info(skill=name in local_skills, mcp=name in codex_mcp, runtime=prepared),
                "hermes": platform_info(skill=name in hermes_skills or name in local_skills, mcp=name in hermes_mcp, runtime=prepared),
                "sync": sync_status(name, record, local_skill_root),
                "description": read_description(record),
            }
        )

    lark_group = None
    if lark_names:
        codex_count = sum(1 for name in lark_names if name in local_skills)
        hermes_count = sum(1 for name in lark_names if name in hermes_skills or name in local_skills)
        lark_group = {
            "name": "lark-*",
            "type": "pure-skill",
            "count": len(lark_names),
            "names": lark_names,
            "codex": {"skill_count": codex_count, "status": f"skill x{codex_count}" if codex_count else "-"},
            "hermes": {"skill_count": hermes_count, "status": f"skill x{hermes_count}" if hermes_count else "-"},
            "sync": "n/a",
            "description": "Lark / Feishu local workflow skills",
        }

    extra_codex_mcp = sorted(codex_mcp - set(capabilities))
    extra_hermes_mcp = sorted(hermes_mcp - set(capabilities))
    external_mcp = [
        {
            "name": name,
            "type": "external",
            "codex": platform_info(skill=False, mcp=name in extra_codex_mcp),
            "hermes": platform_info(skill=False, mcp=name in extra_hermes_mcp),
            "sync": "n/a",
            "description": "external MCP",
        }
        for name in sorted(set(extra_codex_mcp) | set(extra_hermes_mcp))
    ]
    return {
        "registry_check": {
            "local_skill_root": str(local_skill_root),
            "counts": {key: len(value) for key, value in diff.items()},
            "matching": diff["matching"],
            "missing_in_registry": diff["missing_in_registry"],
            "stale_in_registry": diff["stale_in_registry"],
            "drifted_installs": diff["drifted_installs"],
        },
        "capabilities": rows,
        "lark_group": lark_group,
        "external_mcp": external_mcp,
    }


def render_platform_table(report: dict[str, Any]) -> list[str]:
    lines = ["{:<30} {:<16} {:<16} {:<16} {:<8} {}".format("CAPABILITY", "TYPE", "CODEX", "HERMES", "SYNC", "DESCRIPTION")]
    for row in report["capabilities"]:
        lines.append(
            "{:<30} {:<16} {:<16} {:<16} {:<8} {}".format(
                row["name"][:30],
                row["type"][:16],
                row["codex"]["status"],
                row["hermes"]["status"],
                row["sync"],
                shorten(row["description"]),
            )
        )

    lark_group = report["lark_group"]
    if lark_group:
        lines.append(
            "{:<30} {:<16} {:<16} {:<16} {:<8} {}".format(
                f"lark-* ({lark_group['count']})",
                lark_group["type"],
                lark_group["codex"]["status"],
                lark_group["hermes"]["status"],
                lark_group["sync"],
                lark_group["description"],
            )
        )
        lines.append("  " + ", ".join(lark_group["names"]))

    if report["external_mcp"]:
        lines.append("")
        lines.append("== Other Registered MCP ==")
        lines.append("{:<30} {:<16} {:<16} {:<16} {:<8} {}".format("NAME", "TYPE", "CODEX", "HERMES", "SYNC", "DESCRIPTION"))
        for row in report["external_mcp"]:
            lines.append(
                "{:<30} {:<16} {:<16} {:<16} {:<8} {}".format(
                    row["name"][:30],
                    row["type"],
                    row["codex"]["status"],
                    row["hermes"]["status"],
                    row["sync"],
                    row["description"],
                )
            )
    return lines


def platform_info(*, skill: bool, mcp: bool, runtime: bool = False) -> dict[str, Any]:
    return {"skill": skill, "mcp": mcp, "runtime": runtime, "status": platform_status(skill, mcp, runtime)}


def run(command: list[str]) -> str:
    if shutil.which(command[0]) is None:
        return ""
    result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=15)
    if result.returncode != 0:
        return ""
    return result.stdout


def parse_codex_mcp(output: str) -> set[str]:
    names: set[str] = set()
    for line in output.splitlines():
        if "WARNING:" in line or not line.strip() or line.lstrip().startswith("Name "):
            continue
        parts = line.split()
        if len(parts) >= 4 and parts[-2] == "enabled":
            names.add(parts[0])
    return names


def parse_hermes_skills(output: str) -> set[str]:
    names: set[str] = set()
    for line in output.splitlines():
        if "│" not in line or "Name" in line:
            continue
        cols = [col.strip() for col in line.split("│")[1:-1]]
        if len(cols) >= 5 and cols[2] == "local" and cols[4] == "enabled":
            names.add(cols[0])
    return names


def parse_hermes_mcp(output: str) -> set[str]:
    names: set[str] = set()
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("MCP Servers", "Name", "─")):
            continue
        parts = stripped.split()
        if len(parts) >= 4 and parts[-1] == "enabled":
            names.add(parts[0])
    return names


def platform_status(skill: bool, mcp: bool, runtime: bool = False) -> str:
    labels = []
    if skill:
        labels.append("skill")
    if mcp:
        labels.append("mcp")
    if runtime:
        labels.append("runtime")
    return "+".join(labels) if labels else "-"


def project_path(record: dict[str, Any]) -> Path | None:
    project = record.get("paths", {}).get("project")
    install_dir = record.get("paths", {}).get("install_dir")
    if not project:
        return None
    path = Path(project)
    if not path.is_absolute() and install_dir:
        path = Path(install_dir) / path
    return path


def project_prepared(record: dict[str, Any]) -> bool:
    if not record.get("runtime", {}).get("prepared"):
        return False
    path = project_path(record)
    return bool(path and path.is_dir())


def read_description(record: dict[str, Any]) -> str:
    skill = record.get("paths", {}).get("skill")
    install_dir = record.get("paths", {}).get("install_dir")
    if not skill:
        path = project_path(record)
        service_json = path / "service.json" if path else None
        if service_json and service_json.exists():
            try:
                value = json.loads(service_json.read_text(encoding="utf-8")).get("description")
            except json.JSONDecodeError:
                value = None
            if value:
                return " ".join(str(value).split())
        pyproject = path / "pyproject.toml" if path else None
        if pyproject and pyproject.exists():
            value = read_pyproject_description(pyproject)
            if value:
                return " ".join(str(value).split())
        return ""
    path = Path(skill)
    if not path.is_absolute() and install_dir:
        path = Path(install_dir) / skill
    skill_md = path / "SKILL.md"
    if not skill_md.exists():
        return ""
    in_frontmatter = False
    lines = skill_md.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            break
        if in_frontmatter and stripped.startswith("description:"):
            value = stripped.split(":", 1)[1].strip().strip("\"'")
            if value in {">", "|"}:
                value = read_indented_frontmatter_value(lines[index + 1 :])
            return " ".join(value.split())
    return ""


def read_indented_frontmatter_value(lines: list[str]) -> str:
    values: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == "---" or (line and not line[0].isspace() and ":" in line):
            break
        if stripped:
            values.append(stripped)
    return " ".join(values)


def read_pyproject_description(path: Path) -> str | None:
    in_project = False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "[project]":
            in_project = True
            continue
        if in_project and stripped.startswith("["):
            break
        if in_project and stripped.startswith("description"):
            _, value = stripped.split("=", 1)
            return value.strip().strip("\"'")
    return None


def shorten(text: str, width: int = 48) -> str:
    if len(text) <= width:
        return text
    return text[: max(0, width - 1)] + "..."


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_skill_file(record: dict[str, Any]) -> Path | None:
    skill = record.get("paths", {}).get("skill")
    install_dir = record.get("paths", {}).get("install_dir")
    if not skill:
        return None
    path = Path(skill)
    if not path.is_absolute() and install_dir:
        path = Path(install_dir) / path
    skill_md = path / "SKILL.md"
    return skill_md if skill_md.exists() else None


def sync_status(name: str, record: dict[str, Any], local_skill_root: Path) -> str:
    source = source_skill_file(record)
    installed = local_skill_root / name / "SKILL.md"
    if source is None or not installed.exists():
        return "n/a"
    return "ok" if file_hash(source) == file_hash(installed) else "drift"

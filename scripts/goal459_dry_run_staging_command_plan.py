#!/usr/bin/env python3
"""Generate dry-run git staging commands from the Goal 458 stage plan."""

from __future__ import annotations

import argparse
import json
import shlex
from collections import defaultdict
from pathlib import Path
from typing import Any


GROUP_ORDER = [
    "runtime_source",
    "test_source",
    "example_source",
    "validation_script",
    "release_facing_doc",
    "goal_doc",
    "review_handoff",
    "goal_report_or_review",
    "linux_validation_log",
    "consensus_record",
]


def _shell_join(paths: list[str]) -> str:
    return "git add -- " + " ".join(shlex.quote(path) for path in paths)


def build_command_plan(stage_plan: dict[str, Any]) -> dict[str, Any]:
    entries = stage_plan["entries"]
    include_entries = [entry for entry in entries if entry["decision"] == "include"]
    defer_entries = [entry for entry in entries if entry["decision"] == "defer"]
    exclude_entries = [entry for entry in entries if entry["decision"] == "exclude"]

    grouped: dict[str, list[str]] = defaultdict(list)
    for entry in include_entries:
        grouped[entry["category"]].append(entry["path"])

    command_groups = []
    for category in GROUP_ORDER:
        paths = sorted(grouped.pop(category, []))
        if paths:
            command_groups.append(
                {
                    "category": category,
                    "path_count": len(paths),
                    "paths": paths,
                    "command": _shell_join(paths),
                }
            )
    for category in sorted(grouped):
        paths = sorted(grouped[category])
        command_groups.append(
            {
                "category": category,
                "path_count": len(paths),
                "paths": paths,
                "command": _shell_join(paths),
            }
        )

    include_paths = {entry["path"] for entry in include_entries}
    defer_paths = {entry["path"] for entry in defer_entries}
    exclude_paths = {entry["path"] for entry in exclude_entries}
    overlaps = {
        "include_defer": sorted(include_paths & defer_paths),
        "include_exclude": sorted(include_paths & exclude_paths),
        "defer_exclude": sorted(defer_paths & exclude_paths),
    }

    return {
        "goal": 459,
        "source_goal": 458,
        "repo_root": stage_plan["repo_root"],
        "source_valid": stage_plan["valid"],
        "include_count": len(include_entries),
        "defer_count": len(defer_entries),
        "exclude_count": len(exclude_entries),
        "command_group_count": len(command_groups),
        "command_groups": command_groups,
        "deferred_paths": sorted(defer_paths),
        "excluded_paths": sorted(exclude_paths),
        "overlaps": overlaps,
        "staging_performed": False,
        "release_authorization": False,
        "valid": (
            stage_plan["valid"]
            and len(include_entries) > 0
            and not overlaps["include_defer"]
            and not overlaps["include_exclude"]
            and not overlaps["defer_exclude"]
            and not stage_plan["staging_performed"]
            and not stage_plan["release_authorization"]
        ),
    }


def write_markdown(path: Path, plan: dict[str, Any], json_path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Goal 459: v0.7 Dry-Run Staging Command Plan",
        "",
        "Date: 2026-04-16",
        "Author: Codex",
        "Status: Generated, pending external review",
        "",
        "## Verdict",
        "",
        "This is a dry-run command plan. It performs no staging, commit, tag, push, merge, or release action.",
        "",
        "## Generated Artifact",
        "",
        f"- JSON command plan: `{json_path}`",
        "",
        "## Summary",
        "",
        f"- Source Goal 458 valid: `{plan['source_valid']}`",
        f"- Include paths: `{plan['include_count']}`",
        f"- Deferred paths: `{plan['defer_count']}`",
        f"- Excluded paths: `{plan['exclude_count']}`",
        f"- Command groups: `{plan['command_group_count']}`",
        f"- Staging performed: `{plan['staging_performed']}`",
        f"- Release authorization: `{plan['release_authorization']}`",
        f"- Valid: `{plan['valid']}`",
        "",
        "## Command Groups",
        "",
    ]
    for group in plan["command_groups"]:
        lines.append(f"### `{group['category']}`")
        lines.append("")
        lines.append(f"Paths: `{group['path_count']}`")
        lines.append("")
        lines.append("```bash")
        lines.append(group["command"])
        lines.append("```")
        lines.append("")

    lines.extend(["## Deferred By Goal 457", ""])
    lines.extend(f"- `{path}`" for path in plan["deferred_paths"])
    lines.extend(["", "## Excluded By Default", ""])
    lines.extend(f"- `{path}`" for path in plan["excluded_paths"])
    lines.extend(
        [
            "",
            "## Closure Boundary",
            "",
            "- Do not run these commands until the user explicitly approves staging.",
            "- Do not include deferred v0.6 audit-history files in the v0.7 DB staging pass by default.",
            "- Do not stage `rtdsl_current.tar.gz`.",
            "- Do not commit, tag, push, merge, or release.",
            "",
        ]
    )
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage-plan", required=True)
    parser.add_argument("--json-out", required=True)
    parser.add_argument("--md-out", required=True)
    args = parser.parse_args()

    stage_plan_path = Path(args.stage_plan).resolve()
    json_path = Path(args.json_out).resolve()
    md_path = Path(args.md_out).resolve()

    stage_plan = json.loads(stage_plan_path.read_text())
    plan = build_command_plan(stage_plan)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    write_markdown(md_path, plan, json_path)
    print(json.dumps({key: plan[key] for key in plan if key != "command_groups"}, indent=2, sort_keys=True))
    return 0 if plan["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

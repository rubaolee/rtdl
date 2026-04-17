#!/usr/bin/env python3
"""Generate a post-Goal481 dry-run staging command plan."""

from __future__ import annotations

import json
import shlex
import subprocess
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_EXCLUDES = {"rtdsl_current.tar.gz"}
SELF_ARTIFACT_PREFIXES = (
    "docs/goal_482_",
    "docs/handoff/GOAL482_",
    "docs/reports/goal482_",
    "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal482-",
    "scripts/goal482_",
)

RELEASE_DOCS = {
    "README.md",
    "docs/README.md",
    "docs/features/README.md",
    "docs/features/db_workloads/README.md",
    "docs/quick_tutorial.md",
    "docs/tutorials/db_workloads.md",
    "docs/release_facing_examples.md",
    "docs/release_reports/v0_7/audit_report.md",
    "docs/release_reports/v0_7/release_statement.md",
    "docs/release_reports/v0_7/support_matrix.md",
    "docs/release_reports/v0_7/tag_preparation.md",
    "docs/history/goals/v0_7_goal_sequence_2026-04-15.md",
}

GROUP_ORDER = [
    "build_config",
    "runtime_source",
    "test_source",
    "example_source",
    "validation_script",
    "release_facing_doc",
    "feature_doc",
    "goal_doc",
    "review_handoff",
    "goal_report_or_review",
    "external_report_evidence",
    "linux_validation_log",
    "consensus_record",
    "other_doc",
]


@dataclass(frozen=True)
class Entry:
    status: str
    path: str
    decision: str
    category: str
    rationale: str


def _git_status() -> list[tuple[str, str]]:
    proc = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    rows: list[tuple[str, str]] = []
    for line in proc.stdout.splitlines():
        if not line:
            continue
        status = line[:2]
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        rows.append((status, path))
    return rows


def _classify(path: str) -> tuple[str, str, str]:
    if path in ARCHIVE_EXCLUDES:
        return "exclude", "archive_artifact", "Archive artifact excluded from the v0.7 staging plan."
    if path == "Makefile":
        return "include", "build_config", "Build configuration and backend build targets."
    if path.startswith("src/"):
        return "include", "runtime_source", "Runtime or native source for the v0.7 package."
    if path.startswith("tests/"):
        return "include", "test_source", "Automated validation source for the v0.7 package."
    if path.startswith("examples/"):
        return "include", "example_source", "Public example or example index."
    if path.startswith("scripts/"):
        return "include", "validation_script", "Validation, audit, or performance script."
    if path in RELEASE_DOCS:
        return "include", "release_facing_doc", "Release-facing documentation."
    if path.startswith("docs/features/") or path.startswith("docs/tutorials/"):
        return "include", "feature_doc", "Feature or tutorial documentation."
    if path.startswith("docs/goal_"):
        return "include", "goal_doc", "Goal definition and acceptance criteria."
    if path.startswith("docs/handoff/"):
        return "include", "review_handoff", "External-review handoff record."
    if path.startswith("docs/reports/goal"):
        return "include", "goal_report_or_review", "Goal report, review, status, JSON evidence, or generated evidence."
    if path.startswith("docs/reports/linux_"):
        return "include", "linux_validation_log", "Linux validation log."
    if path.startswith("docs/reports/rtdl_") or path.startswith("docs/reports/test_"):
        return "include", "external_report_evidence", "Preserved external tester report or imported external test evidence."
    if path.startswith("docs/reports/external_"):
        return "include", "external_report_evidence", "Preserved external review or release-check evidence."
    if path.startswith("history/ad_hoc_reviews/"):
        return "include", "consensus_record", "Codex consensus record."
    if path.startswith("docs/"):
        return "include", "other_doc", "Documentation or evidence path included in the staging plan."
    return "manual_review", "uncategorized_path", "Path is outside known v0.7 package categories."


def _shell_join(paths: list[str]) -> str:
    return "git add -- " + " ".join(shlex.quote(path) for path in paths)


def build_plan() -> dict[str, Any]:
    entries: list[Entry] = []
    ignored_self_artifacts: list[str] = []
    for status, path in _git_status():
        if path.startswith(SELF_ARTIFACT_PREFIXES):
            ignored_self_artifacts.append(path)
            continue
        decision, category, rationale = _classify(path)
        entries.append(Entry(status, path, decision, category, rationale))

    include_entries = [entry for entry in entries if entry.decision == "include"]
    exclude_entries = [entry for entry in entries if entry.decision == "exclude"]
    manual_review_entries = [entry for entry in entries if entry.decision == "manual_review"]

    grouped: dict[str, list[str]] = defaultdict(list)
    for entry in include_entries:
        grouped[entry.category].append(entry.path)

    command_groups = []
    for category in GROUP_ORDER:
        paths = sorted(grouped.pop(category, []))
        if paths:
            command_groups.append({"category": category, "path_count": len(paths), "paths": paths, "command": _shell_join(paths)})
    for category in sorted(grouped):
        paths = sorted(grouped[category])
        command_groups.append({"category": category, "path_count": len(paths), "paths": paths, "command": _shell_join(paths)})

    include_paths = {entry.path for entry in include_entries}
    exclude_paths = {entry.path for entry in exclude_entries}
    manual_paths = {entry.path for entry in manual_review_entries}
    overlaps = {
        "include_exclude": sorted(include_paths & exclude_paths),
        "include_manual_review": sorted(include_paths & manual_paths),
        "exclude_manual_review": sorted(exclude_paths & manual_paths),
    }
    decision_counts = Counter(entry.decision for entry in entries)
    category_counts = Counter(entry.category for entry in entries)
    valid = (
        bool(include_entries)
        and sorted(exclude_paths) == sorted(ARCHIVE_EXCLUDES)
        and not manual_review_entries
        and all(not values for values in overlaps.values())
    )
    return {
        "goal": 482,
        "repo_root": str(ROOT),
        "source": "git status --porcelain=v1 --untracked-files=all",
        "entry_count": len(entries),
        "ignored_self_artifact_count": len(ignored_self_artifacts),
        "ignored_self_artifacts": sorted(ignored_self_artifacts),
        "include_count": len(include_entries),
        "exclude_count": len(exclude_entries),
        "manual_review_count": len(manual_review_entries),
        "decision_counts": dict(sorted(decision_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "excluded_paths": sorted(exclude_paths),
        "manual_review_paths": sorted(manual_paths),
        "overlaps": overlaps,
        "command_group_count": len(command_groups),
        "command_groups": command_groups,
        "staging_performed": False,
        "release_authorization": False,
        "valid": valid,
        "entries": [asdict(entry) for entry in entries],
    }


def write_markdown(path: Path, plan: dict[str, Any], json_path: Path) -> None:
    lines = [
        "# Goal 482: v0.7 Post-Goal481 Dry-Run Staging Plan",
        "",
        "Date: 2026-04-16",
        "Author: Codex",
        "Status: Generated dry-run command plan",
        "",
        "## Generated Artifact",
        "",
        f"- JSON command plan: `{json_path}`",
        "",
        "## Summary",
        "",
        f"- Entries: `{plan['entry_count']}`",
        f"- Ignored Goal482 self-artifacts: `{plan['ignored_self_artifact_count']}`",
        f"- Include paths: `{plan['include_count']}`",
        f"- Excluded paths: `{plan['exclude_count']}`",
        f"- Manual review paths: `{plan['manual_review_count']}`",
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
    lines.extend(["## Excluded By Default", ""])
    lines.extend(f"- `{path}`" for path in plan["excluded_paths"])
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is a dry-run staging command plan only. It does not stage, commit, tag, push, merge, or release.",
            "Do not run these commands unless the user explicitly approves staging.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    plan = build_plan()
    json_path = ROOT / "docs/reports/goal482_post_goal481_dry_run_staging_plan_2026-04-16.json"
    md_path = ROOT / "docs/reports/goal482_post_goal481_dry_run_staging_plan_generated_2026-04-16.md"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(md_path, plan, json_path)
    print(
        json.dumps(
            {
                "output": str(json_path),
                "md": str(md_path),
                "entry_count": plan["entry_count"],
                "include_count": plan["include_count"],
                "exclude_count": plan["exclude_count"],
                "manual_review_count": plan["manual_review_count"],
                "command_group_count": plan["command_group_count"],
                "valid": plan["valid"],
            },
            sort_keys=True,
        )
    )
    return 0 if plan["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

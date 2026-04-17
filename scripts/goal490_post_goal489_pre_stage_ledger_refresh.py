#!/usr/bin/env python3
"""Refresh the v0.7 pre-stage ledger after Goal489."""

from __future__ import annotations

import csv
import json
import re
import shlex
import subprocess
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_EXCLUDES = {"rtdsl_current.tar.gz"}

RELEASE_DOCS = {
    "README.md",
    "docs/README.md",
    "docs/features/README.md",
    "docs/features/db_workloads/README.md",
    "docs/quick_tutorial.md",
    "docs/tutorials/README.md",
    "docs/tutorials/db_workloads.md",
    "docs/release_facing_examples.md",
    "docs/release_reports/v0_7/README.md",
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
    "current_goal_doc",
    "archived_goal_doc",
    "history_sequence_doc",
    "review_handoff",
    "goal_report_or_review",
    "external_report_evidence",
    "linux_validation_log",
    "consensus_record",
    "history_chronicle",
    "other_doc",
]


@dataclass(frozen=True)
class LedgerEntry:
    status: str
    path: str
    decision: str
    category: str
    rationale: str


def _run(command: list[str]) -> dict[str, Any]:
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return {
        "command": command,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "valid": proc.returncode == 0,
    }


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
        return "exclude", "archive_artifact", "Archive artifact excluded from the v0.7 source/doc/evidence package."
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
    if path.startswith("docs/history/goals/archive/"):
        return "include", "archived_goal_doc", "Archived historical goal documentation."
    if path.startswith("docs/history/goals/"):
        return "include", "history_sequence_doc", "Version goal-sequence or goal-history documentation."
    if path.startswith("docs/goal_"):
        match = re.match(r"docs/goal_(\d+)", path)
        if match and int(match.group(1)) <= 431:
            return "include", "archived_goal_doc", "Root historical goal removal paired with archived goal documentation."
        return "include", "current_goal_doc", "Current v0.7 goal definition and acceptance criteria."
    if path.startswith("docs/handoff/"):
        return "include", "review_handoff", "External-review handoff record."
    if path.startswith("docs/reports/goal"):
        return "include", "goal_report_or_review", "Goal report, review, status, JSON evidence, or generated evidence."
    if path.startswith("docs/reports/linux_"):
        return "include", "linux_validation_log", "Linux validation log."
    if path.startswith("docs/reports/rtdl_") or path.startswith("docs/reports/test_"):
        return "include", "external_report_evidence", "Preserved external tester report or imported external test evidence."
    if path.startswith("docs/reports/external_") or path.startswith("docs/reports/comprehensive_history_"):
        return "include", "external_report_evidence", "Preserved external review or release-check evidence."
    if path.startswith("history/ad_hoc_reviews/"):
        return "include", "consensus_record", "Codex consensus record."
    if path in {"history/history.db", "history/revision_dashboard.html", "history/revision_dashboard.md"}:
        return "include", "history_chronicle", "Root history database or dashboard."
    if path.startswith("history/revisions/"):
        return "include", "history_chronicle", "Registered revision-round chronicle artifact."
    if path.startswith("docs/"):
        return "include", "other_doc", "Documentation or evidence path included in the advisory package."
    return "manual_review", "uncategorized_path", "Path is outside known v0.7 package categories."


def _shell_join(paths: list[str]) -> str:
    return "git add -- " + " ".join(shlex.quote(path) for path in paths)


def build_ledger() -> dict[str, Any]:
    entries = [LedgerEntry(status, path, *_classify(path)) for status, path in _git_status()]
    include_entries = [entry for entry in entries if entry.decision == "include"]
    excluded_entries = [entry for entry in entries if entry.decision == "exclude"]
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
    exclude_paths = {entry.path for entry in excluded_entries}
    manual_paths = {entry.path for entry in manual_review_entries}
    overlaps = {
        "include_exclude": sorted(include_paths & exclude_paths),
        "include_manual_review": sorted(include_paths & manual_paths),
        "exclude_manual_review": sorted(exclude_paths & manual_paths),
    }
    diff_check = _run(["git", "diff", "--check"])
    decision_counts = Counter(entry.decision for entry in entries)
    category_counts = Counter(entry.category for entry in entries)
    valid = (
        bool(include_entries)
        and sorted(exclude_paths) == sorted(ARCHIVE_EXCLUDES)
        and not manual_review_entries
        and all(not values for values in overlaps.values())
        and diff_check["valid"]
    )
    return {
        "goal": 490,
        "repo_root": str(ROOT),
        "source": "git status --porcelain=v1 --untracked-files=all",
        "entry_count": len(entries),
        "include_count": len(include_entries),
        "exclude_count": len(excluded_entries),
        "manual_review_count": len(manual_review_entries),
        "decision_counts": dict(sorted(decision_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "excluded_paths": sorted(exclude_paths),
        "manual_review_paths": sorted(manual_paths),
        "overlaps": overlaps,
        "command_group_count": len(command_groups),
        "command_groups": command_groups,
        "diff_check": diff_check,
        "staging_performed": False,
        "commit_performed": False,
        "tag_performed": False,
        "push_performed": False,
        "merge_performed": False,
        "release_authorization": False,
        "valid": valid,
        "entries": [asdict(entry) for entry in entries],
    }


def write_csv(path: Path, entries: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["status", "path", "decision", "category", "rationale"])
        writer.writeheader()
        writer.writerows(entries)


def write_markdown(path: Path, ledger: dict[str, Any], json_path: Path, csv_path: Path) -> None:
    lines = [
        "# Goal 490: v0.7 Post-Goal489 Pre-Stage Ledger Refresh",
        "",
        "Date: 2026-04-16",
        "Author: Codex",
        "Status: Generated advisory hold ledger and dry-run staging plan",
        "",
        "## Generated Artifacts",
        "",
        f"- JSON ledger: `{json_path}`",
        f"- CSV ledger: `{csv_path}`",
        "",
        "## Summary",
        "",
        f"- Entries: `{ledger['entry_count']}`",
        f"- Include paths: `{ledger['include_count']}`",
        f"- Excluded paths: `{ledger['exclude_count']}`",
        f"- Manual review paths: `{ledger['manual_review_count']}`",
        f"- Command groups: `{ledger['command_group_count']}`",
        f"- `git diff --check` valid: `{ledger['diff_check']['valid']}`",
        f"- Staging performed: `{ledger['staging_performed']}`",
        f"- Release authorization: `{ledger['release_authorization']}`",
        f"- Valid: `{ledger['valid']}`",
        "",
        "## Category Counts",
        "",
    ]
    lines.extend(f"- `{key}`: `{value}`" for key, value in ledger["category_counts"].items())
    lines.extend(["", "## Command Groups", ""])
    for group in ledger["command_groups"]:
        lines.append(f"### `{group['category']}`")
        lines.append("")
        lines.append(f"Paths: `{group['path_count']}`")
        lines.append("")
        lines.append("```bash")
        lines.append(group["command"])
        lines.append("```")
        lines.append("")
    lines.extend(["## Excluded By Default", ""])
    lines.extend(f"- `{path}`" for path in ledger["excluded_paths"])
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is an advisory hold ledger and dry-run staging command plan only.",
            "It does not stage, commit, tag, push, merge, or release.",
            "Do not run generated `git add` command strings unless the user explicitly approves staging.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ledger = build_ledger()
    json_path = ROOT / "docs/reports/goal490_post_goal489_pre_stage_ledger_refresh_2026-04-16.json"
    csv_path = ROOT / "docs/reports/goal490_post_goal489_pre_stage_ledger_refresh_2026-04-16.csv"
    md_path = ROOT / "docs/reports/goal490_post_goal489_pre_stage_ledger_refresh_generated_2026-04-16.md"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(csv_path, ledger["entries"])
    write_markdown(md_path, ledger, json_path, csv_path)
    print(
        json.dumps(
            {
                "output": str(json_path),
                "csv": str(csv_path),
                "md": str(md_path),
                "entry_count": ledger["entry_count"],
                "include_count": ledger["include_count"],
                "exclude_count": ledger["exclude_count"],
                "manual_review_count": ledger["manual_review_count"],
                "command_group_count": ledger["command_group_count"],
                "diff_valid": ledger["diff_check"]["valid"],
                "valid": ledger["valid"],
            },
            sort_keys=True,
        )
    )
    return 0 if ledger["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

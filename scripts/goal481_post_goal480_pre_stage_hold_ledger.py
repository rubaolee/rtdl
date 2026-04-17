#!/usr/bin/env python3
"""Generate the post-Goal480 advisory pre-stage hold ledger."""

from __future__ import annotations

import csv
import json
import shlex
import subprocess
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RETIRED_NON_RELEASE_GOALS = {476}
CLOSED_GOALS = [goal for goal in [*range(432, 439), *range(440, 481)] if goal not in RETIRED_NON_RELEASE_GOALS]
OPEN_GOALS = [439]
ARCHIVE_EXCLUDES = {"rtdsl_current.tar.gz"}
SELF_ARTIFACT_PREFIXES = (
    "docs/goal_481_",
    "docs/handoff/GOAL481_",
    "docs/reports/goal481_",
    "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal481-",
    "scripts/goal481_",
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
class LedgerEntry:
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
        return "include", "other_doc", "Documentation or evidence path included in the advisory package."
    return "manual_review", "uncategorized_path", "Path is outside known v0.7 package categories."


def _find_one(pattern: str) -> list[str]:
    return sorted(str(path.relative_to(ROOT)) for path in ROOT.glob(pattern))


def _closed_goal_coverage() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for goal in CLOSED_GOALS:
        goal_doc = _find_one(f"docs/goal_{goal}_*.md")
        primary_reports = [
            path
            for path in _find_one(f"docs/reports/goal{goal}_*.md")
            if "external_review" not in path
            and "gemini_review" not in path
            and "review_status" not in path
            and "gemini_attempt" not in path
            and "invalid_attempt" not in path
        ]
        external_reviews = [
            path
            for path in _find_one(f"docs/reports/goal{goal}_external_review*.md")
            if "attempt" not in path and "status" not in path
        ]
        gemini_reviews = [
            path
            for path in _find_one(f"docs/reports/goal{goal}_gemini_review*.md")
            if "flash" not in path and "attempt" not in path
        ]
        handoffs = _find_one(f"docs/handoff/GOAL{goal}_*.md")
        consensus = _find_one(f"history/ad_hoc_reviews/*goal{goal}*.md")
        has_external = bool(external_reviews or gemini_reviews)
        rows.append(
            {
                "goal": goal,
                "goal_doc": goal_doc,
                "primary_reports": primary_reports,
                "external_reviews": external_reviews,
                "gemini_reviews": gemini_reviews,
                "handoffs": handoffs,
                "consensus": consensus,
                "valid": bool(goal_doc and primary_reports and has_external and handoffs and consensus),
            }
        )
    return rows


def _open_goal_coverage() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for goal in OPEN_GOALS:
        rows.append(
            {
                "goal": goal,
                "goal_doc": _find_one(f"docs/goal_{goal}_*.md"),
                "primary_reports": _find_one(f"docs/reports/goal{goal}_*.md"),
                "handoffs": _find_one(f"docs/handoff/GOAL{goal}_*.md"),
                "consensus": _find_one(f"history/ad_hoc_reviews/*goal{goal}*.md"),
                "expected_state": "open_external_tester_intake_ledger",
            }
        )
    return rows


def _shell_join(paths: list[str]) -> str:
    return "git add -- " + " ".join(shlex.quote(path) for path in paths)


def build_ledger() -> dict[str, Any]:
    entries = []
    ignored_self_artifacts = []
    for status, path in _git_status():
        if path.startswith(SELF_ARTIFACT_PREFIXES):
            ignored_self_artifacts.append(path)
            continue
        decision, category, rationale = _classify(path)
        entries.append(LedgerEntry(status, path, decision, category, rationale))

    include_entries = [entry for entry in entries if entry.decision == "include"]
    manual_review_entries = [entry for entry in entries if entry.decision == "manual_review"]
    excluded_entries = [entry for entry in entries if entry.decision == "exclude"]
    closed_coverage = _closed_goal_coverage()
    open_coverage = _open_goal_coverage()
    missing_closed = [row for row in closed_coverage if not row["valid"]]
    goal439 = open_coverage[0]
    goal439_valid_open = bool(goal439["goal_doc"] and goal439["primary_reports"] and goal439["handoffs"])

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

    decision_counts = Counter(entry.decision for entry in entries)
    category_counts = Counter(entry.category for entry in entries)
    valid = (
        bool(entries)
        and sorted(entry.path for entry in excluded_entries) == sorted(ARCHIVE_EXCLUDES)
        and not manual_review_entries
        and not missing_closed
        and goal439_valid_open
    )
    return {
        "goal": 481,
        "repo_root": str(ROOT),
        "entry_count": len(entries),
        "ignored_self_artifact_count": len(ignored_self_artifacts),
        "ignored_self_artifacts": sorted(ignored_self_artifacts),
        "include_count": len(include_entries),
        "exclude_count": len(excluded_entries),
        "manual_review_count": len(manual_review_entries),
        "decision_counts": dict(sorted(decision_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "manual_review_paths": [entry.path for entry in manual_review_entries],
        "excluded_paths": sorted(entry.path for entry in excluded_entries),
        "closed_goal_coverage": closed_coverage,
        "closed_goal_missing": missing_closed,
        "open_goal_coverage": open_coverage,
        "goal439_valid_open": goal439_valid_open,
        "command_group_count": len(command_groups),
        "command_groups": command_groups,
        "staging_performed": False,
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
        "# Goal 481: v0.7 Post-Goal480 Pre-Stage Hold Ledger",
        "",
        "Date: 2026-04-16",
        "Author: Codex",
        "Status: Generated advisory hold ledger",
        "",
        "## Generated Artifacts",
        "",
        f"- JSON ledger: `{json_path}`",
        f"- CSV ledger: `{csv_path}`",
        "",
        "## Summary",
        "",
        f"- Entries: `{ledger['entry_count']}`",
        f"- Ignored Goal481 self-artifacts: `{ledger['ignored_self_artifact_count']}`",
        f"- Include: `{ledger['include_count']}`",
        f"- Exclude: `{ledger['exclude_count']}`",
        f"- Manual review: `{ledger['manual_review_count']}`",
        f"- Missing closed-goal evidence rows: `{len(ledger['closed_goal_missing'])}`",
        f"- Goal439 valid open state: `{ledger['goal439_valid_open']}`",
        f"- Command groups: `{ledger['command_group_count']}`",
        f"- Staging performed: `{ledger['staging_performed']}`",
        f"- Release authorization: `{ledger['release_authorization']}`",
        f"- Valid: `{ledger['valid']}`",
        "",
        "## Excluded By Default",
        "",
    ]
    lines.extend(f"- `{path}`" for path in ledger["excluded_paths"])
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is an advisory hold ledger only. It does not stage, commit, tag, push, merge, or release.",
            "Do not run generated `git add` command strings unless the user explicitly approves staging.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ledger = build_ledger()
    json_path = ROOT / "docs/reports/goal481_post_goal480_pre_stage_hold_ledger_2026-04-16.json"
    csv_path = ROOT / "docs/reports/goal481_post_goal480_pre_stage_hold_ledger_2026-04-16.csv"
    md_path = ROOT / "docs/reports/goal481_post_goal480_pre_stage_hold_ledger_generated_2026-04-16.md"
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
                "closed_goal_missing": len(ledger["closed_goal_missing"]),
                "valid": ledger["valid"],
            },
            sort_keys=True,
        )
    )
    return 0 if ledger["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

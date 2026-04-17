#!/usr/bin/env python3
"""Build and validate the v0.7 DB pre-stage plan."""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any


CLOSED_GOALS = [*range(432, 439), *range(440, 465)]
OPEN_GOALS = [439]

ARCHIVE_EXCLUDES = {
    "rtdsl_current.tar.gz",
}

DEFER_BY_GOAL457 = {
    "docs/reports/external_independent_release_check_review_2026-04-15.md",
    "docs/reports/rtdl_v0_6_comprehensive_test_report_dev_handoff.md",
    "docs/reports/rtdl_v0_6_windows_audit_report_2026-04-16.md",
}

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


def _git_status(root: Path) -> list[dict[str, str]]:
    proc = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=root,
        check=True,
        text=True,
        capture_output=True,
    )
    entries: list[dict[str, str]] = []
    for line in proc.stdout.splitlines():
        status = line[:2]
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        entries.append({"status": status, "path": path})
    return entries


def _category(path: str) -> str:
    if path in RELEASE_DOCS:
        return "release_facing_doc"
    if path.startswith("src/"):
        return "runtime_source"
    if path.startswith("tests/"):
        return "test_source"
    if path.startswith("examples/"):
        return "example_source"
    if path.startswith("scripts/"):
        return "validation_script"
    if path.startswith("docs/goal_"):
        return "goal_doc"
    if path.startswith("docs/handoff/"):
        return "review_handoff"
    if path.startswith("docs/reports/goal"):
        return "goal_report_or_review"
    if path.startswith("docs/reports/linux_"):
        return "linux_validation_log"
    if path.startswith("history/ad_hoc_reviews/"):
        return "consensus_record"
    if path.startswith("docs/"):
        return "other_doc"
    return "other"


def _find_one(root: Path, pattern: str) -> list[str]:
    return sorted(str(path.relative_to(root)) for path in root.glob(pattern))


def _closed_goal_coverage(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for goal in CLOSED_GOALS:
        goal_doc = _find_one(root, f"docs/goal_{goal}_*.md")
        primary_reports = [
            path
            for path in _find_one(root, f"docs/reports/goal{goal}_*.md")
            if "external_review" not in path
            and "review_status" not in path
            and "gemini_attempt" not in path
        ]
        external_reviews = [
            path
            for path in _find_one(root, f"docs/reports/goal{goal}_external_review*.md")
            if "attempt" not in path and "status" not in path
        ]
        handoffs = _find_one(root, f"docs/handoff/GOAL{goal}_*.md")
        consensus = _find_one(root, f"history/ad_hoc_reviews/*goal{goal}*.md")
        rows.append(
            {
                "goal": goal,
                "goal_doc": goal_doc,
                "primary_reports": primary_reports,
                "external_reviews": external_reviews,
                "handoffs": handoffs,
                "consensus": consensus,
                "valid": bool(goal_doc and primary_reports and external_reviews and handoffs and consensus),
            }
        )
    return rows


def _open_goal_coverage(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for goal in OPEN_GOALS:
        rows.append(
            {
                "goal": goal,
                "goal_doc": _find_one(root, f"docs/goal_{goal}_*.md"),
                "primary_reports": _find_one(root, f"docs/reports/goal{goal}_*.md"),
                "handoffs": _find_one(root, f"docs/handoff/GOAL{goal}_*.md"),
                "consensus": _find_one(root, f"history/ad_hoc_reviews/*goal{goal}*.md"),
                "expected_state": "open_intake_gate_not_closed",
            }
        )
    return rows


def build_plan(root: Path) -> dict[str, Any]:
    entries = _git_status(root)
    plan_entries: list[dict[str, str]] = []
    for entry in entries:
        path = entry["path"]
        category = _category(path)
        if path in ARCHIVE_EXCLUDES:
            decision = "exclude"
            rationale = "Archive artifact excluded from source/doc staging by default."
        elif path in DEFER_BY_GOAL457:
            decision = "defer"
            rationale = "Goal 457 classifies this as v0.6 audit history, deferred from v0.7 DB staging by default."
        else:
            decision = "include"
            rationale = "Included in the current v0.7 DB source, validation, documentation, or evidence package."
        plan_entries.append({**entry, "decision": decision, "category": category, "rationale": rationale})

    closed_coverage = _closed_goal_coverage(root)
    open_coverage = _open_goal_coverage(root)
    decision_counts = Counter(entry["decision"] for entry in plan_entries)
    category_counts = Counter(entry["category"] for entry in plan_entries)
    unknown_includes = [
        entry
        for entry in plan_entries
        if entry["decision"] == "include" and entry["category"] in {"other", "other_doc"}
    ]
    deferred_paths = [entry["path"] for entry in plan_entries if entry["decision"] == "defer"]
    excluded_paths = [entry["path"] for entry in plan_entries if entry["decision"] == "exclude"]
    missing_closed = [row for row in closed_coverage if not row["valid"]]
    goal439 = open_coverage[0]
    goal439_valid_open = bool(goal439["goal_doc"] and goal439["primary_reports"] and goal439["handoffs"] and not goal439["consensus"])

    valid = (
        decision_counts["include"] > 0
        and sorted(excluded_paths) == sorted(ARCHIVE_EXCLUDES)
        and sorted(deferred_paths) == sorted(DEFER_BY_GOAL457)
        and not unknown_includes
        and not missing_closed
        and goal439_valid_open
    )
    return {
        "goal": 458,
        "repo_root": str(root),
        "entry_count": len(plan_entries),
        "decision_counts": dict(sorted(decision_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "include_count": decision_counts["include"],
        "defer_count": decision_counts["defer"],
        "exclude_count": decision_counts["exclude"],
        "deferred_paths": deferred_paths,
        "excluded_paths": excluded_paths,
        "unknown_includes": unknown_includes,
        "closed_goal_coverage": closed_coverage,
        "closed_goal_missing": missing_closed,
        "open_goal_coverage": open_coverage,
        "goal439_valid_open": goal439_valid_open,
        "staging_performed": False,
        "release_authorization": False,
        "valid": valid,
        "entries": plan_entries,
    }


def write_markdown(path: Path, plan: dict[str, Any], json_path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Goal 458: v0.7 Pre-Stage Validation Gate",
        "",
        "Date: 2026-04-16",
        "Author: Codex",
        "Status: Generated, pending external review",
        "",
        "## Verdict",
        "",
        "The pre-stage plan is valid if the JSON field `valid` is true. This gate performs no staging, commit, tag, push, merge, or release action.",
        "",
        "## Generated Artifact",
        "",
        f"- JSON stage plan: `{json_path}`",
        "",
        "## Summary",
        "",
        f"- Entries: `{plan['entry_count']}`",
        f"- Include: `{plan['include_count']}`",
        f"- Defer: `{plan['defer_count']}`",
        f"- Exclude: `{plan['exclude_count']}`",
        f"- Valid: `{plan['valid']}`",
        f"- Staging performed: `{plan['staging_performed']}`",
        f"- Release authorization: `{plan['release_authorization']}`",
        "",
        "## Excluded By Default",
        "",
    ]
    lines.extend(f"- `{path}`" for path in plan["excluded_paths"])
    lines.extend(["", "## Deferred By Goal 457", ""])
    lines.extend(f"- `{path}`" for path in plan["deferred_paths"])
    lines.extend(["", "## Closed Goal Coverage", ""])
    lines.append(f"- Closed goals checked: `{len(plan['closed_goal_coverage'])}`")
    lines.append(f"- Missing closed-goal evidence rows: `{len(plan['closed_goal_missing'])}`")
    lines.extend(["", "## Open Goal 439", ""])
    lines.append("- Goal 439 is intentionally open as external-tester intake infrastructure.")
    lines.append(f"- Goal 439 valid open state: `{plan['goal439_valid_open']}`")
    lines.extend(["", "## Unknown Include Paths", ""])
    if plan["unknown_includes"]:
        lines.extend(f"- `{entry['path']}` ({entry['category']})" for entry in plan["unknown_includes"])
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Closure Boundary",
            "",
            "- This stage plan is advisory.",
            "- Do not stage until the user explicitly approves.",
            "- Do not merge to main.",
            "- Do not tag or release.",
            "",
        ]
    )
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json-out", required=True)
    parser.add_argument("--md-out", required=True)
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    json_path = Path(args.json_out).resolve()
    md_path = Path(args.md_out).resolve()
    plan = build_plan(root)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    write_markdown(md_path, plan, json_path)
    print(json.dumps({key: plan[key] for key in plan if key != "entries"}, indent=2, sort_keys=True))
    return 0 if plan["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

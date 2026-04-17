#!/usr/bin/env python3
"""Generate an advisory pre-stage ledger for the v0.7 DB worktree."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class LedgerEntry:
    status: str
    path: str
    decision: str
    category: str
    rationale: str


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

MANUAL_REVIEW_DOCS = {
    "docs/reports/external_independent_release_check_review_2026-04-15.md",
    "docs/reports/rtdl_v0_6_comprehensive_test_report_dev_handoff.md",
    "docs/reports/rtdl_v0_6_windows_audit_report_2026-04-16.md",
}

INVALID_REVIEW_HISTORY = {
    "docs/reports/goal445_external_review_gemini_attempt_invalid_2026-04-16.md",
    "docs/reports/goal449_external_review_gemini_attempt_invalid_2026-04-16.md",
    "docs/reports/goal452_external_review_gemini_attempt_overbroad_2026-04-16.md",
}


def _git_status(root: Path) -> list[tuple[str, str]]:
    proc = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=root,
        check=True,
        text=True,
        capture_output=True,
    )
    entries: list[tuple[str, str]] = []
    for line in proc.stdout.splitlines():
        if not line:
            continue
        status = line[:2]
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        entries.append((status, path))
    return entries


def _classify(path: str) -> tuple[str, str, str]:
    if path == "rtdsl_current.tar.gz":
        return (
            "exclude",
            "archive_artifact",
            "Archive artifact is not source, tests, scripts, docs, or consensus evidence.",
        )

    if path in MANUAL_REVIEW_DOCS:
        return (
            "manual_review",
            "legacy_or_external_report",
            "Report is outside the v0.7 DB source package core; inspect before staging.",
        )

    if path in INVALID_REVIEW_HISTORY:
        return (
            "include",
            "invalid_review_history",
            "Preserve as review-history evidence only; do not count as consensus.",
        )

    if path == "docs/reports/goal431_external_review_2026-04-15.md":
        return (
            "include",
            "prior_v0_7_gate_evidence",
            "Prior v0.7 gate evidence remains part of the release trail.",
        )

    if path.startswith("src/"):
        return (
            "include",
            "runtime_source",
            "Runtime/native source change in the v0.7 DB implementation package.",
        )

    if path.startswith("tests/"):
        return (
            "include",
            "test_source",
            "Automated validation source for the v0.7 DB implementation package.",
        )

    if path.startswith("examples/"):
        return (
            "include",
            "example_source",
            "Release-facing example or examples index for the v0.7 DB package.",
        )

    if path.startswith("scripts/"):
        return (
            "include",
            "validation_script",
            "Validation, audit, or performance script for the v0.7 DB package.",
        )

    if path in RELEASE_DOCS:
        return (
            "include",
            "release_facing_doc",
            "Release-facing documentation updated for the current v0.7 evidence boundary.",
        )

    if path.startswith("docs/goal_"):
        return (
            "include",
            "goal_doc",
            "Goal definition and acceptance criteria belong in the evidence trail.",
        )

    if path.startswith("docs/handoff/"):
        return (
            "include",
            "review_handoff",
            "External-review request trail belongs in the evidence package.",
        )

    if path.startswith("docs/reports/goal"):
        return (
            "include",
            "goal_report_or_review",
            "Goal report, review, JSON evidence, or status record belongs in the evidence package.",
        )

    if path.startswith("docs/reports/linux_"):
        return (
            "include",
            "linux_validation_log",
            "Linux correctness or performance log belongs in the evidence package.",
        )

    if path.startswith("history/ad_hoc_reviews/"):
        return (
            "include",
            "consensus_record",
            "Codex consensus record belongs in the evidence package.",
        )

    if path.startswith("docs/"):
        return (
            "manual_review",
            "uncategorized_doc",
            "Documentation path is changed but not covered by the explicit v0.7 package rules.",
        )

    return (
        "manual_review",
        "uncategorized_path",
        "Changed path is not covered by the explicit v0.7 package rules.",
    )


def build_ledger(root: Path) -> dict[str, object]:
    entries: list[LedgerEntry] = []
    for status, path in _git_status(root):
        decision, category, rationale = _classify(path)
        entries.append(
            LedgerEntry(
                status=status,
                path=path,
                decision=decision,
                category=category,
                rationale=rationale,
            )
        )

    decision_counts = Counter(entry.decision for entry in entries)
    category_counts = Counter(entry.category for entry in entries)
    top_level_counts = Counter(entry.path.split("/", 1)[0] for entry in entries)
    manual_review_paths = [entry.path for entry in entries if entry.decision == "manual_review"]
    excluded_paths = [entry.path for entry in entries if entry.decision == "exclude"]

    return {
        "goal": 456,
        "repo_root": str(root),
        "entry_count": len(entries),
        "decision_counts": dict(sorted(decision_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "top_level_counts": dict(sorted(top_level_counts.items())),
        "manual_review_paths": manual_review_paths,
        "excluded_paths": excluded_paths,
        "release_authorization": False,
        "staging_performed": False,
        "valid": (
            len(entries) > 0
            and excluded_paths == ["rtdsl_current.tar.gz"]
            and not any(entry.decision == "manual_review" and entry.path == "rtdsl_current.tar.gz" for entry in entries)
            and not any(entry.decision == "exclude" and entry.path != "rtdsl_current.tar.gz" for entry in entries)
        ),
        "entries": [asdict(entry) for entry in entries],
    }


def write_csv(path: Path, entries: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["status", "path", "decision", "category", "rationale"],
        )
        writer.writeheader()
        writer.writerows(entries)


def write_markdown(path: Path, ledger: dict[str, object], json_path: Path, csv_path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    manual_paths = ledger["manual_review_paths"]
    excluded_paths = ledger["excluded_paths"]
    lines = [
        "# Goal 456: v0.7 Pre-Stage Filelist Ledger",
        "",
        "Date: 2026-04-16",
        "Author: Codex",
        "Status: Generated advisory ledger",
        "",
        "## Verdict",
        "",
        "This is an advisory pre-stage ledger. It performs no staging, commit, tag, push, merge, or release action.",
        "",
        "## Generated Artifacts",
        "",
        f"- JSON ledger: `{json_path}`",
        f"- CSV ledger: `{csv_path}`",
        "",
        "## Summary",
        "",
        f"- Entries: `{ledger['entry_count']}`",
        f"- Decisions: `{json.dumps(ledger['decision_counts'], sort_keys=True)}`",
        f"- Top-level counts: `{json.dumps(ledger['top_level_counts'], sort_keys=True)}`",
        f"- Release authorization: `{ledger['release_authorization']}`",
        f"- Staging performed: `{ledger['staging_performed']}`",
        f"- Valid ledger shape: `{ledger['valid']}`",
        "",
        "## Excluded By Default",
        "",
    ]
    if excluded_paths:
        lines.extend(f"- `{path}`" for path in excluded_paths)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Manual Review Before Staging",
            "",
        ]
    )
    if manual_paths:
        lines.extend(f"- `{path}`" for path in manual_paths)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Closure Conditions",
            "",
            "- Goal 456 must receive 2-AI consensus before closure.",
            "- The ledger does not authorize staging.",
            "- `rtdsl_current.tar.gz` remains excluded by default.",
            "- Manual-review paths require explicit inspection before any future staging action.",
            "",
        ]
    )
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json-out", required=True)
    parser.add_argument("--csv-out", required=True)
    parser.add_argument("--md-out", required=True)
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    ledger = build_ledger(root)
    json_path = Path(args.json_out).resolve()
    csv_path = Path(args.csv_out).resolve()
    md_path = Path(args.md_out).resolve()

    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n")
    write_csv(csv_path, ledger["entries"])
    write_markdown(md_path, ledger, json_path, csv_path)
    print(json.dumps({key: ledger[key] for key in ledger if key != "entries"}, indent=2, sort_keys=True))
    return 0 if ledger["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

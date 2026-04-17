#!/usr/bin/env python3
"""Generate the post-Goal483 v0.7 release-hold audit."""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RETIRED_NON_RELEASE_GOALS = {476}
CLOSED_GOALS = [goal for goal in [*range(432, 439), *range(440, 484)] if goal not in RETIRED_NON_RELEASE_GOALS]
OPEN_GOALS = [439]
ARCHIVE_EXCLUDES = {"rtdsl_current.tar.gz"}
SELF_ARTIFACT_PREFIXES = (
    "docs/goal_484_",
    "docs/handoff/GOAL484_",
    "docs/reports/goal484_",
    "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal484-",
    "scripts/goal484_",
)

RELEASE_DOCS = {
    "docs/release_reports/v0_7/audit_report.md": [
        "Goal 482",
        "Goal 483",
        "not release authorization",
        "not yet tagged",
    ],
    "docs/release_reports/v0_7/release_statement.md": [
        "Goal 482",
        "Goal 483",
        "not staging or release authorization",
        "not yet the new tagged mainline release",
    ],
    "docs/release_reports/v0_7/support_matrix.md": [
        "Goal 482",
        "Goal 483",
        "does not authorize staging",
        "PostgreSQL",
    ],
    "docs/release_reports/v0_7/tag_preparation.md": [
        "Do not tag `v0.7` yet",
        "Goal 482",
        "Goal 483",
        "Hold Condition",
    ],
}


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
    if path.startswith("docs/release_reports/") or path in {"README.md", "docs/README.md", "docs/quick_tutorial.md", "docs/release_facing_examples.md"}:
        return "include", "release_facing_doc", "Release-facing documentation."
    if path.startswith("docs/features/") or path.startswith("docs/tutorials/"):
        return "include", "feature_doc", "Feature or tutorial documentation."
    if path.startswith("docs/goal_"):
        return "include", "goal_doc", "Goal definition and acceptance criteria."
    if path.startswith("docs/handoff/"):
        return "include", "review_handoff", "External-review handoff record."
    if path.startswith("docs/reports/goal"):
        return "include", "goal_report_or_review", "Goal report, review, status, JSON evidence, or generated evidence."
    if path.startswith("docs/reports/rtdl_") or path.startswith("docs/reports/test_") or path.startswith("docs/reports/external_"):
        return "include", "external_report_evidence", "Preserved external tester, review, or release-check evidence."
    if path.startswith("history/ad_hoc_reviews/"):
        return "include", "consensus_record", "Codex consensus record."
    if path.startswith("docs/"):
        return "include", "other_doc", "Documentation or evidence path included in the package."
    return "manual_review", "uncategorized_path", "Path is outside known v0.7 package categories."


def _find(pattern: str) -> list[str]:
    return sorted(str(path.relative_to(ROOT)) for path in ROOT.glob(pattern))


def _closed_goal_coverage() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for goal in CLOSED_GOALS:
        goal_doc = _find(f"docs/goal_{goal}_*.md")
        primary_reports = [
            path
            for path in _find(f"docs/reports/goal{goal}_*.md")
            if "external_review" not in path
            and "gemini_review" not in path
            and "review_status" not in path
            and "gemini_attempt" not in path
            and "invalid_attempt" not in path
        ]
        external_reviews = [
            path
            for path in _find(f"docs/reports/goal{goal}_external_review*.md")
            if "attempt" not in path and "status" not in path
        ]
        gemini_reviews = [
            path
            for path in _find(f"docs/reports/goal{goal}_gemini_review*.md")
            if "flash" not in path and "attempt" not in path
        ]
        handoffs = _find(f"docs/handoff/GOAL{goal}_*.md")
        consensus = _find(f"history/ad_hoc_reviews/*goal{goal}*.md")
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
                "goal_doc": _find(f"docs/goal_{goal}_*.md"),
                "primary_reports": _find(f"docs/reports/goal{goal}_*.md"),
                "handoffs": _find(f"docs/handoff/GOAL{goal}_*.md"),
                "expected_state": "open_external_tester_intake_ledger",
            }
        )
    return rows


def _release_doc_checks() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rel_path, tokens in RELEASE_DOCS.items():
        full_path = ROOT / rel_path
        text = full_path.read_text(encoding="utf-8") if full_path.exists() else ""
        missing = [token for token in tokens if token not in text]
        rows.append({"path": rel_path, "exists": full_path.exists(), "missing_tokens": missing, "valid": full_path.exists() and not missing})
    return rows


def _run_check(command: list[str]) -> dict[str, Any]:
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return {
        "command": command,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "valid": proc.returncode == 0,
    }


def build_audit() -> dict[str, Any]:
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
    closed_coverage = _closed_goal_coverage()
    open_coverage = _open_goal_coverage()
    missing_closed = [row for row in closed_coverage if not row["valid"]]
    release_doc_checks = _release_doc_checks()
    audit_checks = [
        _run_check(["python3", "scripts/goal479_release_candidate_audit.py"]),
        _run_check(["python3", "scripts/goal470_pre_release_doc_audit.py"]),
        _run_check(["python3", "scripts/goal473_post_goal472_release_evidence_audit.py"]),
    ]

    decision_counts = Counter(entry.decision for entry in entries)
    category_counts = Counter(entry.category for entry in entries)
    goal439 = open_coverage[0]
    goal439_valid_open = bool(goal439["goal_doc"] and goal439["primary_reports"] and goal439["handoffs"])
    valid = (
        bool(entries)
        and sorted(entry.path for entry in exclude_entries) == sorted(ARCHIVE_EXCLUDES)
        and not manual_review_entries
        and not missing_closed
        and goal439_valid_open
        and all(row["valid"] for row in release_doc_checks)
        and all(row["valid"] for row in audit_checks)
    )
    return {
        "goal": 484,
        "repo_root": str(ROOT),
        "entry_count": len(entries),
        "ignored_self_artifact_count": len(ignored_self_artifacts),
        "ignored_self_artifacts": sorted(ignored_self_artifacts),
        "include_count": len(include_entries),
        "exclude_count": len(exclude_entries),
        "manual_review_count": len(manual_review_entries),
        "decision_counts": dict(sorted(decision_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "excluded_paths": sorted(entry.path for entry in exclude_entries),
        "manual_review_paths": sorted(entry.path for entry in manual_review_entries),
        "closed_goal_coverage": closed_coverage,
        "closed_goal_missing": missing_closed,
        "open_goal_coverage": open_coverage,
        "goal439_valid_open": goal439_valid_open,
        "release_doc_checks": release_doc_checks,
        "audit_checks": audit_checks,
        "staging_performed": False,
        "release_authorization": False,
        "valid": valid,
        "entries": [asdict(entry) for entry in entries],
    }


def write_markdown(path: Path, audit: dict[str, Any], json_path: Path) -> None:
    lines = [
        "# Goal 484: v0.7 Post-Goal483 Release Hold Audit",
        "",
        "Date: 2026-04-16",
        "Author: Codex",
        "Status: Generated release-hold audit",
        "",
        "## Generated Artifact",
        "",
        f"- JSON audit: `{json_path}`",
        "",
        "## Summary",
        "",
        f"- Entries: `{audit['entry_count']}`",
        f"- Ignored Goal484 self-artifacts: `{audit['ignored_self_artifact_count']}`",
        f"- Include paths: `{audit['include_count']}`",
        f"- Excluded paths: `{audit['exclude_count']}`",
        f"- Manual review paths: `{audit['manual_review_count']}`",
        f"- Missing closed-goal evidence rows: `{len(audit['closed_goal_missing'])}`",
        f"- Goal439 valid open state: `{audit['goal439_valid_open']}`",
        f"- Release docs valid: `{all(row['valid'] for row in audit['release_doc_checks'])}`",
        f"- Audit scripts valid: `{all(row['valid'] for row in audit['audit_checks'])}`",
        f"- Staging performed: `{audit['staging_performed']}`",
        f"- Release authorization: `{audit['release_authorization']}`",
        f"- Valid: `{audit['valid']}`",
        "",
        "## Excluded By Default",
        "",
    ]
    lines.extend(f"- `{path}`" for path in audit["excluded_paths"])
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is a release-hold audit only. It does not stage, commit, tag, push, merge, or release.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    audit = build_audit()
    json_path = ROOT / "docs/reports/goal484_post_goal483_release_hold_audit_2026-04-16.json"
    md_path = ROOT / "docs/reports/goal484_post_goal483_release_hold_audit_generated_2026-04-16.md"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(md_path, audit, json_path)
    print(
        json.dumps(
            {
                "output": str(json_path),
                "md": str(md_path),
                "entry_count": audit["entry_count"],
                "include_count": audit["include_count"],
                "exclude_count": audit["exclude_count"],
                "manual_review_count": audit["manual_review_count"],
                "closed_goal_missing": len(audit["closed_goal_missing"]),
                "release_docs_valid": all(row["valid"] for row in audit["release_doc_checks"]),
                "audit_scripts_valid": all(row["valid"] for row in audit["audit_checks"]),
                "valid": audit["valid"],
            },
            sort_keys=True,
        )
    )
    return 0 if audit["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

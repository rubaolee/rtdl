#!/usr/bin/env python3
"""Audit v0.7 release-candidate evidence after Goal 478."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/goal_477_v0_7_broad_unittest_discovery_repair.md",
    "docs/goal_478_v0_7_release_reports_refresh_after_goal477.md",
    "docs/reports/goal477_v0_7_broad_unittest_discovery_repair_2026-04-16.md",
    "docs/reports/goal478_v0_7_release_reports_refresh_after_goal477_2026-04-16.md",
    "docs/reports/goal477_external_review_2026-04-16.md",
    "docs/reports/goal478_external_review_2026-04-16.md",
    "docs/reports/goal477_gemini_review_2026-04-16.md",
    "docs/reports/goal478_gemini_review_2026-04-16.md",
    "docs/reports/goal477_gemini_flash_review_2026-04-16.md",
    "docs/reports/goal478_gemini_flash_review_2026-04-16.md",
    "docs/reports/goal477_goal478_gemini_flash_invalid_attempt_2026-04-16.md",
    "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal477-v0_7-broad-unittest-discovery-repair.md",
    "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal478-v0_7-release-reports-refresh-after-goal477.md",
    "docs/release_reports/v0_7/audit_report.md",
    "docs/release_reports/v0_7/release_statement.md",
    "docs/release_reports/v0_7/support_matrix.md",
    "docs/release_reports/v0_7/tag_preparation.md",
    "docs/history/goals/v0_7_goal_sequence_2026-04-15.md",
)

VALID_AUDIT_JSONS = (
    "docs/reports/goal470_pre_release_doc_audit_2026-04-16.json",
    "docs/reports/goal473_post_goal472_release_evidence_audit_2026-04-16.json",
    "docs/reports/goal475_external_input_manifest_2026-04-16.json",
)

NO_RELEASE_TOKENS = (
    "not release authorization",
    "Status: hold",
    "Do not tag",
    "Do not tag `v0.7` yet",
)


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def _json(rel: str) -> dict[str, Any]:
    return json.loads(_read(rel))


def _contains_all(rel: str, tokens: tuple[str, ...]) -> list[str]:
    text = _read(rel)
    return [token for token in tokens if token not in text]


def build_audit() -> dict[str, Any]:
    missing_files = [rel for rel in REQUIRED_FILES if not (ROOT / rel).is_file()]

    review_checks = []
    for goal in (477, 478):
        claude = f"docs/reports/goal{goal}_external_review_2026-04-16.md"
        gemini = f"docs/reports/goal{goal}_gemini_review_2026-04-16.md"
        codex = (
            "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal477-v0_7-broad-unittest-discovery-repair.md"
            if goal == 477
            else "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal478-v0_7-release-reports-refresh-after-goal477.md"
        )
        review_checks.append(
            {
                "goal": goal,
                "claude_accept": "Verdict: **ACCEPT**" in _read(claude) if (ROOT / claude).is_file() else False,
                "gemini_accept": "Verdict: **ACCEPT**" in _read(gemini) if (ROOT / gemini).is_file() else False,
                "codex_accept": "Verdict: ACCEPT" in _read(codex) if (ROOT / codex).is_file() else False,
            }
        )

    invalid_flash_checks = []
    for rel in (
        "docs/reports/goal477_gemini_flash_review_2026-04-16.md",
        "docs/reports/goal478_gemini_flash_review_2026-04-16.md",
    ):
        text = _read(rel) if (ROOT / rel).is_file() else ""
        invalid_flash_checks.append(
            {
                "path": rel,
                "marked_invalid": "INVALID GEMINI FLASH ATTEMPT" in text and "DO NOT COUNT AS CONSENSUS" in text,
                "no_raw_accept_line": "\nACCEPT\n" not in f"\n{text}\n",
            }
        )

    release_report_checks = {
        "tag_preparation_hold": "Status: hold" in _read("docs/release_reports/v0_7/tag_preparation.md"),
        "tag_preparation_no_tag": "Do not tag `v0.7` yet" in _read("docs/release_reports/v0_7/tag_preparation.md"),
        "audit_not_release_authorization": "not release authorization" in _read("docs/release_reports/v0_7/audit_report.md"),
        "support_not_release_authorization": "not release authorization" in _read("docs/release_reports/v0_7/support_matrix.md"),
        "release_statement_not_tagged": "not yet the new tagged mainline release" in _read("docs/release_reports/v0_7/release_statement.md"),
    }

    active_paths = (
        "docs/history/goals/v0_7_goal_sequence_2026-04-15.md",
        "docs/release_reports/v0_7/audit_report.md",
        "docs/release_reports/v0_7/release_statement.md",
        "docs/release_reports/v0_7/support_matrix.md",
        "docs/release_reports/v0_7/tag_preparation.md",
        "docs/goal_477_v0_7_broad_unittest_discovery_repair.md",
        "docs/goal_478_v0_7_release_reports_refresh_after_goal477.md",
    )
    stale_line_count_refs = []
    for rel in active_paths:
        text = _read(rel)
        for token in ("Goal 476", "Goal476", "goal476", "line-count", "line count", "Line Count"):
            if token in text:
                stale_line_count_refs.append({"path": rel, "token": token})

    audit_json_checks = []
    for rel in VALID_AUDIT_JSONS:
        payload = _json(rel) if (ROOT / rel).is_file() else {}
        audit_json_checks.append({"path": rel, "valid": payload.get("valid") is True})

    valid = (
        not missing_files
        and all(row["claude_accept"] and row["gemini_accept"] and row["codex_accept"] for row in review_checks)
        and all(row["marked_invalid"] and row["no_raw_accept_line"] for row in invalid_flash_checks)
        and all(release_report_checks.values())
        and not stale_line_count_refs
        and all(row["valid"] for row in audit_json_checks)
    )

    return {
        "goal": 479,
        "repo_root": str(ROOT),
        "missing_files": missing_files,
        "review_checks": review_checks,
        "invalid_flash_checks": invalid_flash_checks,
        "release_report_checks": release_report_checks,
        "stale_line_count_refs": stale_line_count_refs,
        "audit_json_checks": audit_json_checks,
        "staging_performed": False,
        "release_authorization": False,
        "valid": valid,
    }


def write_markdown(path: Path, audit: dict[str, Any], json_path: Path) -> None:
    lines = [
        "# Goal 479: v0.7 Release-Candidate Audit After Goal478",
        "",
        "Date: 2026-04-16",
        "Author: Codex",
        "Status: Generated release-candidate audit",
        "",
        "## Generated Artifact",
        "",
        f"- JSON audit: `{json_path}`",
        "",
        "## Result",
        "",
        f"- Valid: `{audit['valid']}`",
        f"- Missing required files: `{len(audit['missing_files'])}`",
        f"- Stale active retired-metrics refs: `{len(audit['stale_line_count_refs'])}`",
        f"- Staging performed: `{audit['staging_performed']}`",
        f"- Release authorization: `{audit['release_authorization']}`",
        "",
        "## Review Evidence",
        "",
    ]
    for row in audit["review_checks"]:
        lines.append(
            f"- Goal {row['goal']}: Codex `{row['codex_accept']}`, Claude `{row['claude_accept']}`, Gemini `{row['gemini_accept']}`"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "Goal479 is an audit artifact only. It does not stage, commit, tag, push, merge, or release.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    audit = build_audit()
    json_path = ROOT / "docs/reports/goal479_release_candidate_audit_after_goal478_2026-04-16.json"
    md_path = ROOT / "docs/reports/goal479_release_candidate_audit_after_goal478_generated_2026-04-16.md"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(md_path, audit, json_path)
    print(
        json.dumps(
            {
                "output": str(json_path),
                "md": str(md_path),
                "missing_files": len(audit["missing_files"]),
                "stale_line_count_refs": len(audit["stale_line_count_refs"]),
                "valid": audit["valid"],
            },
            sort_keys=True,
        )
    )
    return 0 if audit["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Audit v0.7 release-hold state after Goal490."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

GOAL490_JSON = ROOT / "docs/reports/goal490_post_goal489_pre_stage_ledger_refresh_2026-04-16.json"
REQUIRED_FILES = [
    "docs/goal_490_v0_7_post_goal489_pre_stage_ledger_refresh.md",
    "docs/reports/goal490_v0_7_post_goal489_pre_stage_ledger_refresh_2026-04-16.md",
    "docs/reports/goal490_post_goal489_pre_stage_ledger_refresh_2026-04-16.json",
    "docs/reports/goal490_post_goal489_pre_stage_ledger_refresh_generated_2026-04-16.md",
    "docs/reports/goal490_external_review_2026-04-16.md",
    "docs/reports/goal490_gemini_review_2026-04-16.md",
    "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal490-v0_7-post-goal489-pre-stage-ledger-refresh.md",
]
PUBLIC_DOCS = [
    "README.md",
    "docs/README.md",
    "docs/tutorials/db_workloads.md",
    "docs/release_facing_examples.md",
    "docs/release_reports/v0_7/audit_report.md",
    "docs/release_reports/v0_7/release_statement.md",
    "docs/release_reports/v0_7/support_matrix.md",
    "docs/release_reports/v0_7/tag_preparation.md",
]
REQUIRED_DOC_TOKENS = {
    "README.md": ["Goal 490", "release-held through Goal 490"],
    "docs/README.md": ["Goal 490", "held after Goal 490"],
    "docs/tutorials/db_workloads.md": ["Goal 490", "current release-hold/pre-stage ledger checkpoint"],
    "docs/release_facing_examples.md": ["Goal 490", "current pre-stage ledger checkpoint"],
    "docs/release_reports/v0_7/audit_report.md": ["Goal490 post-Goal489", "Goal 490 refreshed"],
    "docs/release_reports/v0_7/release_statement.md": ["Goal 490 post-Goal489", "Goal 490 is not staging or release authorization"],
    "docs/release_reports/v0_7/support_matrix.md": ["Goal 490 post-Goal489", "does not authorize staging"],
    "docs/release_reports/v0_7/tag_preparation.md": ["Goal 490 pre-stage ledger refresh", "Do not tag `v0.7` yet"],
}
STALE_PUBLIC_PATTERNS = [
    "release-held through Goal 487",
    "held after Goal 487",
    "Goal 487 is the current release-hold stability checkpoint",
]


def _run(command: list[str]) -> dict[str, Any]:
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return {
        "command": command,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "valid": proc.returncode == 0,
    }


def _run_json_script(script: str) -> dict[str, Any]:
    result = _run(["python3", script])
    parsed: dict[str, Any] | None = None
    if result["stdout"]:
        last_line = result["stdout"].splitlines()[-1]
        try:
            parsed = json.loads(last_line)
        except json.JSONDecodeError:
            parsed = None
    return {**result, "parsed": parsed, "valid": result["valid"] and bool(parsed and parsed.get("valid") is True)}


def _goal490_json_check() -> dict[str, Any]:
    if not GOAL490_JSON.exists():
        return {"exists": False, "valid": False}
    data = json.loads(GOAL490_JSON.read_text(encoding="utf-8"))
    return {
        "exists": True,
        "entry_count": data.get("entry_count"),
        "include_count": data.get("include_count"),
        "exclude_count": data.get("exclude_count"),
        "manual_review_count": data.get("manual_review_count"),
        "excluded_paths": data.get("excluded_paths"),
        "staging_performed": data.get("staging_performed"),
        "release_authorization": data.get("release_authorization"),
        "valid": data.get("valid") is True
        and data.get("manual_review_count") == 0
        and data.get("excluded_paths") == ["rtdsl_current.tar.gz"]
        and data.get("staging_performed") is False
        and data.get("release_authorization") is False,
    }


def _file_checks() -> list[dict[str, Any]]:
    rows = []
    for rel in REQUIRED_FILES:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        rows.append(
            {
                "path": rel,
                "exists": path.exists(),
                "contains_accept": "ACCEPT" in text or "Verdict: ACCEPT" in text,
                "valid": path.exists(),
            }
        )
    return rows


def _review_checks() -> dict[str, Any]:
    claude = (ROOT / "docs/reports/goal490_external_review_2026-04-16.md").read_text(encoding="utf-8")
    gemini = (ROOT / "docs/reports/goal490_gemini_review_2026-04-16.md").read_text(encoding="utf-8")
    consensus = (ROOT / "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal490-v0_7-post-goal489-pre-stage-ledger-refresh.md").read_text(encoding="utf-8")
    return {
        "claude_accept": "ACCEPT" in claude,
        "gemini_accept": "ACCEPT" in gemini,
        "codex_accept": "Verdict: ACCEPT" in consensus,
        "valid": "ACCEPT" in claude and "ACCEPT" in gemini and "Verdict: ACCEPT" in consensus,
    }


def _doc_checks() -> list[dict[str, Any]]:
    rows = []
    for rel in PUBLIC_DOCS:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        missing = [token for token in REQUIRED_DOC_TOKENS.get(rel, []) if token not in text]
        stale = [pattern for pattern in STALE_PUBLIC_PATTERNS if pattern in text]
        rows.append(
            {
                "path": rel,
                "exists": path.exists(),
                "missing_tokens": missing,
                "stale_patterns": stale,
                "valid": path.exists() and not missing and not stale,
            }
        )
    return rows


def _staged_check() -> dict[str, Any]:
    result = _run(["git", "diff", "--cached", "--name-only"])
    staged = [line for line in result["stdout"].splitlines() if line]
    return {**result, "staged_paths": staged, "valid": result["valid"] and not staged}


def build_audit() -> dict[str, Any]:
    file_checks = _file_checks()
    doc_checks = _doc_checks()
    checks = {
        "goal488": _run_json_script("scripts/goal488_front_tutorial_example_doc_consistency_audit.py"),
        "goal489": _run_json_script("scripts/goal489_history_synchronization_audit.py"),
        "goal490": _run_json_script("scripts/goal490_post_goal489_pre_stage_ledger_refresh.py"),
    }
    goal490_json = _goal490_json_check()
    review_checks = _review_checks()
    diff_check = _run(["git", "diff", "--check"])
    staged_check = _staged_check()
    valid = (
        all(row["valid"] for row in file_checks)
        and all(row["valid"] for row in doc_checks)
        and all(row["valid"] for row in checks.values())
        and goal490_json["valid"]
        and review_checks["valid"]
        and diff_check["valid"]
        and staged_check["valid"]
    )
    return {
        "goal": 491,
        "repo_root": str(ROOT),
        "file_checks": file_checks,
        "invalid_file_checks": [row for row in file_checks if not row["valid"]],
        "doc_checks": doc_checks,
        "invalid_doc_checks": [row for row in doc_checks if not row["valid"]],
        "script_checks": checks,
        "goal490_json_check": goal490_json,
        "review_checks": review_checks,
        "diff_check": diff_check,
        "staged_check": staged_check,
        "staging_performed": False,
        "commit_performed": False,
        "tag_performed": False,
        "push_performed": False,
        "merge_performed": False,
        "release_authorization": False,
        "valid": valid,
    }


def write_markdown(path: Path, audit: dict[str, Any], json_path: Path) -> None:
    lines = [
        "# Goal 491: v0.7 Post-Goal490 Release-Hold Audit",
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
        f"- Required files missing/invalid: `{len(audit['invalid_file_checks'])}`",
        f"- Public docs invalid: `{len(audit['invalid_doc_checks'])}`",
        f"- Goal488 audit valid: `{audit['script_checks']['goal488']['valid']}`",
        f"- Goal489 audit valid: `{audit['script_checks']['goal489']['valid']}`",
        f"- Goal490 ledger valid: `{audit['script_checks']['goal490']['valid']}`",
        f"- Goal490 reviews valid: `{audit['review_checks']['valid']}`",
        f"- `git diff --check` valid: `{audit['diff_check']['valid']}`",
        f"- Staged paths: `{len(audit['staged_check']['staged_paths'])}`",
        f"- Staging performed: `{audit['staging_performed']}`",
        f"- Release authorization: `{audit['release_authorization']}`",
        f"- Valid: `{audit['valid']}`",
        "",
        "## Boundary",
        "",
        "This is a release-hold audit only. It does not stage, commit, tag, push, merge, or release.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    audit = build_audit()
    json_path = ROOT / "docs/reports/goal491_post_goal490_release_hold_audit_2026-04-16.json"
    md_path = ROOT / "docs/reports/goal491_post_goal490_release_hold_audit_generated_2026-04-16.md"
    json_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(md_path, audit, json_path)
    print(
        json.dumps(
            {
                "output": str(json_path),
                "md": str(md_path),
                "invalid_file_checks": len(audit["invalid_file_checks"]),
                "invalid_doc_checks": len(audit["invalid_doc_checks"]),
                "staged_paths": len(audit["staged_check"]["staged_paths"]),
                "diff_valid": audit["diff_check"]["valid"],
                "valid": audit["valid"],
            },
            sort_keys=True,
        )
    )
    return 0 if audit["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Audit front-page, tutorial, example, and v0.7 release-doc consistency."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    "README.md",
    "docs/README.md",
    "docs/quick_tutorial.md",
    "docs/tutorials/README.md",
    "docs/tutorials/db_workloads.md",
    "docs/release_facing_examples.md",
    "examples/README.md",
    "docs/release_reports/v0_7/README.md",
    "docs/release_reports/v0_7/release_statement.md",
    "docs/release_reports/v0_7/support_matrix.md",
    "docs/release_reports/v0_7/audit_report.md",
    "docs/release_reports/v0_7/tag_preparation.md",
]
REQUIRED_TOKENS = {
    "README.md": [
        "current released version: `v0.6.1`",
        "bounded `v0.7` RT DB work",
        "rtdl_v0_7_db_app_demo.py",
        "rtdl_v0_7_db_kernel_app_demo.py",
        "Goal 490",
        "RTDL is not a DBMS",
    ],
    "docs/README.md": [
        "Current v0.7 Goal Sequence",
        "app-level and kernel-form v0.7 DB demos",
        "Goal 490",
    ],
    "docs/quick_tutorial.md": [
        "rtdl_v0_7_db_app_demo.py",
        "rtdl_v0_7_db_kernel_app_demo.py",
        "not a DBMS",
    ],
    "docs/tutorials/README.md": [
        "Database Workloads",
        "conjunctive_scan",
        "grouped_count",
        "grouped_sum",
    ],
    "docs/tutorials/db_workloads.md": [
        "prepare_embree_db_dataset",
        "transfer=\"columnar\"",
        "rtdl_v0_7_db_app_demo.py",
        "rtdl_v0_7_db_kernel_app_demo.py",
        "Goal 490",
    ],
    "docs/release_facing_examples.md": [
        "rtdl_v0_7_db_app_demo.py",
        "rtdl_v0_7_db_kernel_app_demo.py",
        "Goal 490",
    ],
    "examples/README.md": [
        "rtdl_v0_7_db_app_demo.py",
        "rtdl_v0_7_db_kernel_app_demo.py",
        "PostgreSQL remains a Linux correctness/performance anchor",
    ],
    "docs/release_reports/v0_7/release_statement.md": ["Goal 486", "Goal 487", "not staging or release authorization"],
    "docs/release_reports/v0_7/support_matrix.md": ["Goal 486", "Goal 487", "does not authorize staging"],
    "docs/release_reports/v0_7/audit_report.md": ["Goal 486", "Goal 487", "not staging or release authorization"],
    "docs/release_reports/v0_7/tag_preparation.md": ["Goal 486", "Goal 487", "Do not tag `v0.7` yet"],
}
STALE_CURRENT_PATTERNS = [
    "Goal 483 is the current",
    "Goal 483 as the current",
    "Goal483 release-report refresh after Goal482 with Claude and Gemini review",
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


def _doc_checks() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rel in DOCS:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        missing = [token for token in REQUIRED_TOKENS.get(rel, []) if token not in text]
        stale = [token for token in STALE_CURRENT_PATTERNS if token in text]
        rows.append(
            {
                "path": rel,
                "exists": path.exists(),
                "missing_tokens": missing,
                "stale_current_patterns": stale,
                "valid": path.exists() and not missing and not stale,
            }
        )
    return rows


def _example_command_checks() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    command_re = re.compile(r"python(?:3)?\\s+(examples/[A-Za-z0-9_./\\\\-]+\\.py)")
    for rel in DOCS:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for match in command_re.finditer(text):
            raw = match.group(1).replace("\\\\", "/")
            exists = (ROOT / raw).exists()
            rows.append({"doc": rel, "example": raw, "exists": exists, "valid": exists})
    return rows


def build_audit() -> dict[str, Any]:
    doc_checks = _doc_checks()
    command_checks = _example_command_checks()
    diff_check = _run(["git", "diff", "--check"])
    valid = (
        all(row["valid"] for row in doc_checks)
        and all(row["valid"] for row in command_checks)
        and diff_check["valid"]
    )
    return {
        "goal": 488,
        "repo_root": str(ROOT),
        "doc_checks": doc_checks,
        "example_command_checks": command_checks,
        "invalid_doc_checks": [row for row in doc_checks if not row["valid"]],
        "invalid_example_commands": [row for row in command_checks if not row["valid"]],
        "diff_check": diff_check,
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
        "# Goal 488: v0.7 Front/Tutorial/Example/Doc Consistency Audit",
        "",
        "Date: 2026-04-16",
        "Author: Codex",
        "Status: Generated consistency audit",
        "",
        "## Generated Artifact",
        "",
        f"- JSON audit: `{json_path}`",
        "",
        "## Summary",
        "",
        f"- Docs checked: `{len(audit['doc_checks'])}`",
        f"- Invalid doc checks: `{len(audit['invalid_doc_checks'])}`",
        f"- Example commands checked: `{len(audit['example_command_checks'])}`",
        f"- Invalid example commands: `{len(audit['invalid_example_commands'])}`",
        f"- `git diff --check` valid: `{audit['diff_check']['valid']}`",
        f"- Staging performed: `{audit['staging_performed']}`",
        f"- Release authorization: `{audit['release_authorization']}`",
        f"- Valid: `{audit['valid']}`",
        "",
        "## Boundary",
        "",
        "This is a documentation consistency audit only. It does not stage, commit, tag, push, merge, or release.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    audit = build_audit()
    json_path = ROOT / "docs/reports/goal488_front_tutorial_example_doc_consistency_audit_2026-04-16.json"
    md_path = ROOT / "docs/reports/goal488_front_tutorial_example_doc_consistency_audit_generated_2026-04-16.md"
    json_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(md_path, audit, json_path)
    print(
        json.dumps(
            {
                "output": str(json_path),
                "md": str(md_path),
                "invalid_doc_checks": len(audit["invalid_doc_checks"]),
                "invalid_example_commands": len(audit["invalid_example_commands"]),
                "diff_valid": audit["diff_check"]["valid"],
                "valid": audit["valid"],
            },
            sort_keys=True,
        )
    )
    return 0 if audit["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

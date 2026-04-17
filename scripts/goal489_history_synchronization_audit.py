#!/usr/bin/env python3
"""Audit current-branch history synchronization."""

from __future__ import annotations

import json
import re
import sqlite3
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "history/history.db"
REQUIRED_SLUGS = [
    "2026-04-09-v0-2-v0-3-closure",
    "2026-04-12-v0-4-closure",
    "2026-04-14-v0-5-closure",
    "2026-04-15-v0-6-closure",
    "2026-04-16-v0-7-current-hold",
]
SEQUENCE_FILES = [
    "docs/history/goals/v0_1_goal_sequence_2026-04-16.md",
    "docs/history/goals/v0_2_goal_sequence_2026-04-16.md",
    "docs/history/goals/v0_3_goal_sequence_2026-04-16.md",
    "docs/history/goals/v0_4_goal_sequence_2026-04-16.md",
    "docs/history/goals/v0_5_final_goal_sequence_2026-04-16.md",
    "docs/history/goals/v0_6_goal_sequence_2026-04-14.md",
    "docs/history/goals/v0_7_goal_sequence_2026-04-15.md",
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


def _root_goal_numbers() -> list[int]:
    nums: list[int] = []
    for path in (ROOT / "docs").glob("goal_*.md"):
        match = re.match(r"goal_(\d+)", path.name)
        if match:
            nums.append(int(match.group(1)))
    return sorted(nums)


def _db_check() -> dict[str, Any]:
    con = sqlite3.connect(DB)
    try:
        count = con.execute("select count(*) from revision_rounds").fetchone()[0]
        rows = con.execute("select slug from revision_rounds").fetchall()
        slugs = {row[0] for row in rows}
    finally:
        con.close()
    missing = [slug for slug in REQUIRED_SLUGS if slug not in slugs]
    return {"round_count": count, "missing_slugs": missing, "valid": not missing and count >= 65}


def build_audit() -> dict[str, Any]:
    root_nums = _root_goal_numbers()
    archive_count = len(list((ROOT / "docs/history/goals/archive").glob("goal_*.md")))
    sequence_checks = [
        {"path": rel, "exists": (ROOT / rel).exists(), "valid": (ROOT / rel).exists()}
        for rel in SEQUENCE_FILES
    ]
    report_path = ROOT / "docs/reports/comprehensive_history_synchronization_report_2026-04-16.md"
    dashboard_md = ROOT / "history/revision_dashboard.md"
    dashboard_html = ROOT / "history/revision_dashboard.html"
    db_check = _db_check()
    diff_check = _run(["git", "diff", "--check"])
    root_goal_valid = bool(root_nums) and min(root_nums) >= 432 and max(root_nums) >= 489
    dashboard_text = dashboard_md.read_text(encoding="utf-8") if dashboard_md.exists() else ""
    html_text = dashboard_html.read_text(encoding="utf-8") if dashboard_html.exists() else ""
    dashboard_valid = "2026-04-16-v0-7-current-hold" in dashboard_text and "2026-04-16-v0-7-current-hold" in html_text
    valid = (
        report_path.exists()
        and archive_count >= 352
        and root_goal_valid
        and all(row["valid"] for row in sequence_checks)
        and db_check["valid"]
        and dashboard_valid
        and diff_check["valid"]
    )
    return {
        "goal": 489,
        "repo_root": str(ROOT),
        "external_report_exists": report_path.exists(),
        "root_goal_count": len(root_nums),
        "root_goal_min": min(root_nums) if root_nums else None,
        "root_goal_max": max(root_nums) if root_nums else None,
        "root_goal_valid": root_goal_valid,
        "archive_goal_count": archive_count,
        "sequence_checks": sequence_checks,
        "db_check": db_check,
        "dashboard_valid": dashboard_valid,
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
        "# Goal 489: v0.7 History Synchronization Audit",
        "",
        "Date: 2026-04-16",
        "Author: Codex",
        "Status: Generated history synchronization audit",
        "",
        "## Generated Artifact",
        "",
        f"- JSON audit: `{json_path}`",
        "",
        "## Summary",
        "",
        f"- External report preserved: `{audit['external_report_exists']}`",
        f"- Root goal count: `{audit['root_goal_count']}`",
        f"- Root goal min/max: `{audit['root_goal_min']}` / `{audit['root_goal_max']}`",
        f"- Root goal range valid: `{audit['root_goal_valid']}`",
        f"- Archived historical goal files: `{audit['archive_goal_count']}`",
        f"- Revision DB valid: `{audit['db_check']['valid']}`",
        f"- Revision rounds: `{audit['db_check']['round_count']}`",
        f"- Dashboard valid: `{audit['dashboard_valid']}`",
        f"- `git diff --check` valid: `{audit['diff_check']['valid']}`",
        f"- Staging performed: `{audit['staging_performed']}`",
        f"- Release authorization: `{audit['release_authorization']}`",
        f"- Valid: `{audit['valid']}`",
        "",
        "## Boundary",
        "",
        "This is a history synchronization audit only. It does not stage, commit, tag, push, merge, or release.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    audit = build_audit()
    json_path = ROOT / "docs/reports/goal489_history_synchronization_audit_2026-04-16.json"
    md_path = ROOT / "docs/reports/goal489_history_synchronization_audit_generated_2026-04-16.md"
    json_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(md_path, audit, json_path)
    print(
        json.dumps(
            {
                "output": str(json_path),
                "md": str(md_path),
                "root_goal_count": audit["root_goal_count"],
                "archive_goal_count": audit["archive_goal_count"],
                "db_valid": audit["db_check"]["valid"],
                "dashboard_valid": audit["dashboard_valid"],
                "diff_valid": audit["diff_check"]["valid"],
                "valid": audit["valid"],
            },
            sort_keys=True,
        )
    )
    return 0 if audit["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

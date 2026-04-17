#!/usr/bin/env python3
"""Verify release-hold stability after Goal486."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HOME_GIT = Path("/Users/rl2025/.git")
HOME_GIT_BACKUP = Path("/Users/rl2025/.git.home-backup-2026-04-16")
MIN_FREE_BYTES = 5 * 1024 * 1024 * 1024


REQUIRED_FILES = {
    "goal486_report": {
        "path": ROOT / "docs/reports/goal486_v0_7_post_disk_cleanup_artifact_integrity_audit_2026-04-16.md",
        "required_text": "Status: Accepted",
    },
    "goal486_json": {
        "path": ROOT / "docs/reports/goal486_post_disk_cleanup_artifact_integrity_audit_2026-04-16.json",
        "required_text": '"valid": true',
    },
    "goal486_codex": {
        "path": ROOT / "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal486-v0_7-post-disk-cleanup-artifact-integrity-audit.md",
        "required_text": "Verdict: ACCEPT",
    },
    "goal486_claude": {
        "path": ROOT / "docs/reports/goal486_external_review_2026-04-16.md",
        "required_text": "ACCEPT",
    },
    "goal486_gemini": {
        "path": ROOT / "docs/reports/goal486_gemini_review_2026-04-16.md",
        "required_text": "ACCEPT",
    },
}


def _run(command: list[str], cwd: Path = ROOT) -> dict[str, Any]:
    proc = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    return {
        "command": command,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "valid": proc.returncode == 0,
    }


def _file_checks() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for label, spec in REQUIRED_FILES.items():
        path = spec["path"]
        required_text = spec["required_text"]
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        checks.append(
            {
                "label": label,
                "path": str(path),
                "exists": path.exists(),
                "size": path.stat().st_size if path.exists() else 0,
                "required_text": required_text,
                "has_required_text": required_text in text,
                "valid": path.exists() and path.stat().st_size > 0 and required_text in text,
            }
        )
    return checks


def _process_check() -> dict[str, Any]:
    proc = _run(["ps", "-axo", "pid=,command="])
    offenders = []
    for line in proc["stdout"].splitlines():
        if "git add" in line or "git ls-files" in line:
            if "goal487_post_goal486_release_hold_stability_audit.py" not in line:
                offenders.append(line.strip())
    return {
        "process_scan": proc,
        "offenders": offenders,
        "valid": proc["valid"] and not offenders,
    }


def _disk_check() -> dict[str, Any]:
    usage = shutil.disk_usage("/Users/rl2025")
    return {
        "total_bytes": usage.total,
        "used_bytes": usage.used,
        "free_bytes": usage.free,
        "min_free_bytes": MIN_FREE_BYTES,
        "valid": usage.free >= MIN_FREE_BYTES,
    }


def build_audit() -> dict[str, Any]:
    file_checks = _file_checks()
    goal486 = _run(["python3", "scripts/goal486_post_disk_cleanup_artifact_integrity_audit.py"])
    diff = _run(["git", "diff", "--check"])
    process = _process_check()
    disk = _disk_check()
    home_git = {
        "home_git_path": str(HOME_GIT),
        "home_git_exists": HOME_GIT.exists(),
        "backup_path": str(HOME_GIT_BACKUP),
        "backup_exists": HOME_GIT_BACKUP.exists(),
        "valid": not HOME_GIT.exists() and HOME_GIT_BACKUP.exists(),
    }
    valid = (
        all(row["valid"] for row in file_checks)
        and goal486["valid"]
        and diff["valid"]
        and process["valid"]
        and disk["valid"]
        and home_git["valid"]
    )
    return {
        "goal": 487,
        "repo_root": str(ROOT),
        "file_checks": file_checks,
        "goal486_check": goal486,
        "diff_check": diff,
        "process_check": process,
        "disk_check": disk,
        "home_git_check": home_git,
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
        "# Goal 487: v0.7 Post-Goal486 Release-Hold Stability Audit",
        "",
        "Date: 2026-04-16",
        "Author: Codex",
        "Status: Generated release-hold stability audit",
        "",
        "## Generated Artifact",
        "",
        f"- JSON audit: `{json_path}`",
        "",
        "## Summary",
        "",
        f"- Goal486 audit valid: `{audit['goal486_check']['valid']}`",
        f"- Required Goal486 review files valid: `{all(row['valid'] for row in audit['file_checks'])}`",
        f"- Home Git disabled with backup: `{audit['home_git_check']['valid']}`",
        f"- Runaway home Git process absent: `{audit['process_check']['valid']}`",
        f"- Disk threshold valid: `{audit['disk_check']['valid']}`",
        f"- `git diff --check` valid: `{audit['diff_check']['valid']}`",
        f"- Staging performed: `{audit['staging_performed']}`",
        f"- Commit performed: `{audit['commit_performed']}`",
        f"- Tag performed: `{audit['tag_performed']}`",
        f"- Push performed: `{audit['push_performed']}`",
        f"- Merge performed: `{audit['merge_performed']}`",
        f"- Release authorization: `{audit['release_authorization']}`",
        f"- Valid: `{audit['valid']}`",
        "",
        "## Boundary",
        "",
        "This is a non-mutating release-hold stability audit only. It does not stage, commit, tag, push, merge, or release.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    audit = build_audit()
    json_path = ROOT / "docs/reports/goal487_post_goal486_release_hold_stability_audit_2026-04-16.json"
    md_path = ROOT / "docs/reports/goal487_post_goal486_release_hold_stability_audit_generated_2026-04-16.md"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(md_path, audit, json_path)
    print(
        json.dumps(
            {
                "output": str(json_path),
                "md": str(md_path),
                "goal486_valid": audit["goal486_check"]["valid"],
                "home_git_valid": audit["home_git_check"]["valid"],
                "process_valid": audit["process_check"]["valid"],
                "disk_valid": audit["disk_check"]["valid"],
                "diff_valid": audit["diff_check"]["valid"],
                "valid": audit["valid"],
            },
            sort_keys=True,
        )
    )
    return 0 if audit["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

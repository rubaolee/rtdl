#!/usr/bin/env python3
"""Verify report-artifact integrity after disk cleanup."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HOME_GIT = Path("/Users/rl2025/.git")
HOME_GIT_BACKUP = Path("/Users/rl2025/.git.home-backup-2026-04-16")
HOME_GIT_OBJECTS = HOME_GIT / "objects"
MIN_FREE_BYTES = 5 * 1024 * 1024 * 1024


def _json_checks() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for path in sorted((ROOT / "docs/reports").glob("*.json")):
        rel = str(path.relative_to(ROOT))
        try:
            json.loads(path.read_text(encoding="utf-8"))
            checks.append({"path": rel, "size": path.stat().st_size, "valid": True, "error": ""})
        except Exception as exc:  # noqa: BLE001 - report exact parse failure.
            checks.append({"path": rel, "size": path.stat().st_size if path.exists() else 0, "valid": False, "error": str(exc)})
    return checks


def _text_checks() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for suffix in ("*.md", "*.txt", "*.csv"):
        for path in sorted((ROOT / "docs/reports").glob(suffix)):
            rel = str(path.relative_to(ROOT))
            size = path.stat().st_size
            checks.append({"path": rel, "size": size, "valid": size > 0})
    return checks


def _run(command: list[str], cwd: Path = ROOT) -> dict[str, Any]:
    proc = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    return {
        "command": command,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "valid": proc.returncode == 0,
    }


def _home_git_garbage_check() -> dict[str, Any]:
    if not HOME_GIT.exists():
        return {
            "mode": "home_git_disabled",
            "home_git_path": str(HOME_GIT),
            "backup_path": str(HOME_GIT_BACKUP),
            "backup_exists": HOME_GIT_BACKUP.exists(),
            "count_objects": None,
            "tmp_file_count": 0,
            "tmp_files": [],
            "zero_garbage": True,
            "valid": HOME_GIT_BACKUP.exists(),
        }
    count = _run(["git", "-C", "/Users/rl2025", "count-objects", "-vH"], cwd=Path("/Users/rl2025"))
    tmp_files = sorted(str(path) for path in HOME_GIT_OBJECTS.glob("**/tmp_*")) if HOME_GIT_OBJECTS.exists() else []
    stdout = count["stdout"]
    zero_garbage = "garbage: 0" in stdout and "size-garbage: 0 bytes" in stdout
    return {
        "count_objects": count,
        "tmp_file_count": len(tmp_files),
        "tmp_files": tmp_files,
        "zero_garbage": zero_garbage,
        "valid": count["valid"] and zero_garbage and not tmp_files,
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
    json_checks = _json_checks()
    text_checks = _text_checks()
    goal484_check = _run(["python3", "scripts/goal484_post_goal483_release_hold_audit.py"])
    git_garbage_check = _home_git_garbage_check()
    disk_check = _disk_check()
    diff_check = _run(["git", "diff", "--check"])
    invalid_json = [row for row in json_checks if not row["valid"]]
    invalid_text = [row for row in text_checks if not row["valid"]]
    valid = (
        not invalid_json
        and not invalid_text
        and goal484_check["valid"]
        and git_garbage_check["valid"]
        and disk_check["valid"]
        and diff_check["valid"]
    )
    return {
        "goal": 486,
        "repo_root": str(ROOT),
        "json_artifact_count": len(json_checks),
        "invalid_json_artifacts": invalid_json,
        "text_artifact_count": len(text_checks),
        "invalid_text_artifacts": invalid_text,
        "goal484_check": goal484_check,
        "home_git_garbage_check": git_garbage_check,
        "disk_check": disk_check,
        "diff_check": diff_check,
        "staging_performed": False,
        "release_authorization": False,
        "valid": valid,
        "json_checks": json_checks,
        "text_checks": text_checks,
    }


def write_markdown(path: Path, audit: dict[str, Any], json_path: Path) -> None:
    lines = [
        "# Goal 486: v0.7 Post-Disk-Cleanup Artifact Integrity Audit",
        "",
        "Date: 2026-04-16",
        "Author: Codex",
        "Status: Generated artifact-integrity audit",
        "",
        "## Generated Artifact",
        "",
        f"- JSON audit: `{json_path}`",
        "",
        "## Summary",
        "",
        f"- JSON artifacts checked: `{audit['json_artifact_count']}`",
        f"- Invalid JSON artifacts: `{len(audit['invalid_json_artifacts'])}`",
        f"- Text artifacts checked: `{audit['text_artifact_count']}`",
        f"- Invalid text artifacts: `{len(audit['invalid_text_artifacts'])}`",
        f"- Goal484 audit valid: `{audit['goal484_check']['valid']}`",
        f"- Home Git garbage check valid: `{audit['home_git_garbage_check']['valid']}`",
        f"- Remaining Git temp files: `{audit['home_git_garbage_check']['tmp_file_count']}`",
        f"- Free disk bytes: `{audit['disk_check']['free_bytes']}`",
        f"- Disk threshold valid: `{audit['disk_check']['valid']}`",
        f"- `git diff --check` valid: `{audit['diff_check']['valid']}`",
        f"- Staging performed: `{audit['staging_performed']}`",
        f"- Release authorization: `{audit['release_authorization']}`",
        f"- Valid: `{audit['valid']}`",
        "",
        "## Boundary",
        "",
        "This is a post-disk-cleanup artifact-integrity audit only. It does not stage, commit, tag, push, merge, or release.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    audit = build_audit()
    json_path = ROOT / "docs/reports/goal486_post_disk_cleanup_artifact_integrity_audit_2026-04-16.json"
    md_path = ROOT / "docs/reports/goal486_post_disk_cleanup_artifact_integrity_audit_generated_2026-04-16.md"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(md_path, audit, json_path)
    print(
        json.dumps(
            {
                "output": str(json_path),
                "md": str(md_path),
                "json_artifact_count": audit["json_artifact_count"],
                "invalid_json_artifacts": len(audit["invalid_json_artifacts"]),
                "text_artifact_count": audit["text_artifact_count"],
                "invalid_text_artifacts": len(audit["invalid_text_artifacts"]),
                "goal484_valid": audit["goal484_check"]["valid"],
                "home_git_garbage_valid": audit["home_git_garbage_check"]["valid"],
                "disk_valid": audit["disk_check"]["valid"],
                "valid": audit["valid"],
            },
            sort_keys=True,
        )
    )
    return 0 if audit["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

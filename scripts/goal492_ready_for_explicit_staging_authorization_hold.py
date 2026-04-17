#!/usr/bin/env python3
"""Verify v0.7 is ready for explicit staging authorization while still held."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


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
        try:
            parsed = json.loads(result["stdout"].splitlines()[-1])
        except json.JSONDecodeError:
            parsed = None
    return {**result, "parsed": parsed, "valid": result["valid"] and bool(parsed and parsed.get("valid") is True)}


def _contains(path: str, token: str) -> bool:
    full = ROOT / path
    return full.exists() and token in full.read_text(encoding="utf-8")


def _staged_check() -> dict[str, Any]:
    result = _run(["git", "diff", "--cached", "--name-only"])
    staged = [line for line in result["stdout"].splitlines() if line]
    return {**result, "staged_paths": staged, "valid": result["valid"] and not staged}


def build_audit() -> dict[str, Any]:
    goal491_script = _run_json_script("scripts/goal491_post_goal490_release_hold_audit.py")
    goal490_script = _run_json_script("scripts/goal490_post_goal489_pre_stage_ledger_refresh.py")
    diff_check = _run(["git", "diff", "--check"])
    staged_check = _staged_check()
    review_checks = {
        "codex_accept": _contains(
            "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal491-v0_7-post-goal490-release-hold-audit.md",
            "Verdict: ACCEPT",
        ),
        "claude_accept": _contains("docs/reports/goal491_external_review_2026-04-16.md", "ACCEPT"),
        "gemini_accept": _contains("docs/reports/goal491_gemini_review_2026-04-16.md", "ACCEPT"),
    }
    review_checks["valid"] = all(review_checks.values())
    goal490_parsed = goal490_script.get("parsed") or {}
    valid = (
        goal491_script["valid"]
        and goal490_script["valid"]
        and goal490_parsed.get("manual_review_count") == 0
        and goal490_parsed.get("exclude_count") == 1
        and goal490_parsed.get("valid") is True
        and review_checks["valid"]
        and diff_check["valid"]
        and staged_check["valid"]
    )
    return {
        "goal": 492,
        "repo_root": str(ROOT),
        "goal491_script": goal491_script,
        "goal490_script": goal490_script,
        "review_checks": review_checks,
        "diff_check": diff_check,
        "staged_check": staged_check,
        "next_mutating_step_requires_explicit_named_user_instruction": True,
        "staging_performed": False,
        "commit_performed": False,
        "tag_performed": False,
        "push_performed": False,
        "merge_performed": False,
        "release_authorization": False,
        "valid": valid,
    }


def write_markdown(path: Path, audit: dict[str, Any], json_path: Path) -> None:
    goal490 = audit["goal490_script"].get("parsed") or {}
    lines = [
        "# Goal 492: v0.7 Ready For Explicit Staging Authorization Hold",
        "",
        "Date: 2026-04-16",
        "Author: Codex",
        "Status: Generated final hold audit",
        "",
        "## Generated Artifact",
        "",
        f"- JSON audit: `{json_path}`",
        "",
        "## Summary",
        "",
        f"- Goal491 audit valid: `{audit['goal491_script']['valid']}`",
        f"- Goal490 current ledger valid: `{audit['goal490_script']['valid']}`",
        f"- Current ledger entries: `{goal490.get('entry_count')}`",
        f"- Current ledger include paths: `{goal490.get('include_count')}`",
        f"- Current ledger exclude paths: `{goal490.get('exclude_count')}`",
        f"- Current ledger manual-review paths: `{goal490.get('manual_review_count')}`",
        f"- Goal491 Codex/Claude/Gemini acceptance valid: `{audit['review_checks']['valid']}`",
        f"- `git diff --check` valid: `{audit['diff_check']['valid']}`",
        f"- Staged paths: `{len(audit['staged_check']['staged_paths'])}`",
        f"- Staging performed: `{audit['staging_performed']}`",
        f"- Release authorization: `{audit['release_authorization']}`",
        f"- Valid: `{audit['valid']}`",
        "",
        "## Next Mutating Step",
        "",
        "The next mutating step requires an explicit user instruction that names",
        "the requested git action, such as staging, committing, tagging, pushing,",
        "merging, or releasing.",
        "",
        "## Boundary",
        "",
        "This is a readiness hold only. It does not stage, commit, tag, push, merge, or release.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    audit = build_audit()
    json_path = ROOT / "docs/reports/goal492_ready_for_explicit_staging_authorization_hold_2026-04-16.json"
    md_path = ROOT / "docs/reports/goal492_ready_for_explicit_staging_authorization_hold_generated_2026-04-16.md"
    json_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(md_path, audit, json_path)
    print(
        json.dumps(
            {
                "output": str(json_path),
                "md": str(md_path),
                "goal491_valid": audit["goal491_script"]["valid"],
                "goal490_valid": audit["goal490_script"]["valid"],
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

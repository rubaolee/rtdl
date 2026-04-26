#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-26"
GOAL = "Goal1024 final public surface audit after history repair"

REQUIRED_FILES = (
    "README.md",
    "docs/README.md",
    "docs/current_main_support_matrix.md",
    "docs/application_catalog.md",
    "docs/app_engine_support_matrix.md",
    "docs/release_facing_examples.md",
    "docs/rtdl_feature_guide.md",
    "docs/v1_0_rtx_app_status.md",
    "history/COMPLETE_HISTORY.md",
    "history/revision_dashboard.md",
    "docs/reports/goal1020_public_docs_rtx_boundary_audit_2026-04-26.md",
    "docs/reports/goal1022_history_release_drift_audit_2026-04-26.md",
    "docs/reports/goal1023_two_ai_consensus_2026-04-26.md",
)

REQUIRED_PHRASES: dict[str, tuple[str, ...]] = {
    "README.md": (
        "current released version is `v0.9.6`",
        "not automatic public speedup claims",
        "robot_collision_screening / prepared_pose_flags",
        "larger RTX repeats stayed below the 100 ms",
    ),
    "docs/README.md": (
        "current released version is `v0.9.6`",
        "v0.9.6 Release Package",
        "v1.0 RTX App Status",
    ),
    "docs/current_main_support_matrix.md": (
        "Current public release: `v0.9.6`",
        "released `v0.9.6` tag",
    ),
    "docs/application_catalog.md": (
        "is not by itself a NVIDIA RT-core claim",
        "rtdsl.rtx_public_wording_matrix()",
        "remains blocked for public RTX speedup wording",
    ),
    "docs/app_engine_support_matrix.md": (
        "The machine-readable source of truth is `rtdsl.rtx_public_wording_matrix()`",
        "public_wording_blocked",
        "blocked_for_public_speedup_wording",
    ),
    "docs/release_facing_examples.md": (
        "`--backend optix` is a backend-selection flag, not an automatic NVIDIA RT-core",
        "These commands are bounded sub-paths, not broad speedup claims",
        "100 ms",
    ),
    "docs/rtdl_feature_guide.md": (
        "`--backend optix` is not enough for a public",
        "rtdsl.rtx_public_wording_matrix()",
        "100 ms public-review timing floor",
    ),
    "docs/v1_0_rtx_app_status.md": (
        "not release authorization and not a public speedup claim",
        "blocked_for_public_speedup_wording",
        "rtdsl.rtx_public_wording_matrix()",
    ),
    "history/COMPLETE_HISTORY.md": (
        "v0.9.6",
        "Goal1023",
        "Goal684",
        "Historical records are not rewritten",
    ),
    "history/revision_dashboard.md": (
        "v0.9.6",
        "Goal1023",
        "Goal684",
        "2026-04-26-goal1023-v0_9_6-history-catchup",
    ),
}

RECORDED_CHECKS = (
    {
        "name": "full_unittest_discovery",
        "command": "PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py' -v",
        "result": "OK",
        "tests": 1969,
        "skipped": 196,
    },
    {
        "name": "public_entry_smoke",
        "command": "PYTHONPATH=src:. python3 scripts/goal497_public_entry_smoke_check.py --json-out /tmp/goal497_next.json",
        "result": "valid true",
    },
    {
        "name": "focused_public_surface_suite",
        "command": (
            "PYTHONPATH=src:. python3 -m unittest "
            "tests.goal515_public_command_truth_audit_test "
            "tests.goal512_public_doc_smoke_audit_test "
            "tests.goal687_app_engine_support_matrix_test "
            "tests.goal938_public_rtx_wording_sync_test "
            "tests.goal1011_rtx_public_wording_matrix_test "
            "tests.goal1020_public_docs_rtx_boundary_audit_test -v"
        ),
        "result": "OK",
        "tests": 20,
    },
    {
        "name": "history_repair_suite",
        "command": (
            "PYTHONPATH=src:. python3 -m unittest "
            "tests.goal1017_recent_goal_consensus_audit_test "
            "tests.goal1022_history_release_drift_audit_test "
            "tests.goal1023_v0_9_6_history_catchup_test -v"
        ),
        "result": "OK",
        "tests": 7,
    },
)


def build_audit() -> dict[str, Any]:
    file_rows: list[dict[str, Any]] = []
    for rel_path in REQUIRED_FILES:
        path = ROOT / rel_path
        file_rows.append({"path": rel_path, "exists": path.exists()})

    phrase_rows: list[dict[str, Any]] = []
    for rel_path, phrases in REQUIRED_PHRASES.items():
        path = ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        missing = [phrase for phrase in phrases if phrase not in text]
        phrase_rows.append(
            {
                "path": rel_path,
                "required_phrase_count": len(phrases),
                "missing_phrases": missing,
                "status": "ok" if path.exists() and not missing else "missing_required_phrase",
            }
        )

    missing_files = [row for row in file_rows if not row["exists"]]
    failing_phrase_rows = [row for row in phrase_rows if row["status"] != "ok"]
    return {
        "goal": GOAL,
        "date": DATE,
        "file_count": len(file_rows),
        "missing_file_count": len(missing_files),
        "phrase_doc_count": len(phrase_rows),
        "failing_phrase_doc_count": len(failing_phrase_rows),
        "file_rows": file_rows,
        "phrase_rows": phrase_rows,
        "recorded_checks": list(RECORDED_CHECKS),
        "public_speedup_claim_authorized_count": 0,
        "valid": not missing_files and not failing_phrase_rows,
        "boundary": (
            "This final public-surface audit checks that release-facing docs, "
            "history indexes, app matrix wording, and RTX claim boundaries are aligned "
            "after Goal1023. It does not tag, release, or authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1024 Final Public Surface Audit",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- valid: `{payload['valid']}`",
        f"- files checked: `{payload['file_count']}`",
        f"- missing files: `{payload['missing_file_count']}`",
        f"- phrase docs checked: `{payload['phrase_doc_count']}`",
        f"- failing phrase docs: `{payload['failing_phrase_doc_count']}`",
        f"- public speedup claims authorized here: `{payload['public_speedup_claim_authorized_count']}`",
        "",
        "## Recorded Checks",
        "",
        "| Check | Result | Tests |",
        "|---|---|---:|",
    ]
    for row in payload["recorded_checks"]:
        lines.append(f"| `{row['name']}` | `{row['result']}` | `{row.get('tests', '')}` |")

    lines.extend(["", "## Phrase Rows", "", "| Doc | Status | Missing phrases |", "|---|---|---:|"])
    for row in payload["phrase_rows"]:
        lines.append(f"| `{row['path']}` | `{row['status']}` | {len(row['missing_phrases'])} |")

    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit final public surface after history repair.")
    parser.add_argument("--output-json", default="docs/reports/goal1024_final_public_surface_audit_2026-04-26.json")
    parser.add_argument("--output-md", default="docs/reports/goal1024_final_public_surface_audit_2026-04-26.md")
    args = parser.parse_args()

    payload = build_audit()
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    output_md.write_text(markdown + "\n", encoding="utf-8")
    print(markdown)
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

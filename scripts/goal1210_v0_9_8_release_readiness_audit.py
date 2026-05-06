#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-01"
GOAL = "Goal1210 v0.9.8 release-readiness audit after Goal1209"

REQUIRED_GOAL_FILES: dict[str, tuple[str, ...]] = {
    "Goal1204": (
        "docs/reports/goal1204_repaired_rtx_pod_packet_2026-05-01.md",
        "docs/reports/goal1204_gemini_repaired_rtx_pod_packet_review_2026-05-01.md",
        "docs/reports/goal1204_two_ai_consensus_2026-05-01.md",
    ),
    "Goal1205": (
        "docs/reports/goal1205_repaired_rtx_pod_intake_2026-05-01.md",
        "docs/reports/goal1205_gemini_repaired_rtx_pod_intake_fix_review_2026-05-01.md",
        "docs/reports/goal1205_two_ai_consensus_2026-05-01.md",
    ),
    "Goal1206": (
        "docs/reports/goal1206_repaired_rtx_recovery_merge_intake_2026-05-01.md",
        "docs/reports/goal1206_gemini_live_pod_merged_evidence_review_2026-05-01.md",
        "docs/reports/goal1206_two_ai_consensus_2026-05-01.md",
    ),
    "Goal1207": (
        "docs/reports/goal1207_linux_embree_prefix_env_fix_2026-05-01.md",
        "docs/reports/goal1207_gemini_linux_embree_prefix_fix_review_2026-05-01.md",
        "docs/reports/goal1207_two_ai_consensus_2026-05-01.md",
    ),
    "Goal1208": (
        "docs/reports/goal1208_public_wording_decision_after_goal1206_2026-05-01.md",
        "docs/reports/goal1208_claude_public_wording_decision_review_2026-05-01.md",
        "docs/reports/goal1208_two_ai_consensus_2026-05-01.md",
    ),
    "Goal1209": (
        "docs/reports/goal1209_public_status_sync_after_goal1208_2026-05-01.md",
        "docs/reports/goal1209_claude_public_status_sync_review_2026-05-01.md",
        "docs/reports/goal1209_two_ai_consensus_2026-05-01.md",
    ),
}

CURRENT_PUBLIC_SURFACE_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "README.md": (
        "The current released version is `v1.0`",
        "Reviewed rows are bounded public sub-path wording",
        "not automatic public speedup claims",
        "v1.0 RTX App Status",
    ),
    "docs/app_engine_support_matrix.md": (
        "Current reviewed public wording rows after Goal1263: `13`",
        "Goal1208 adds exactly one reviewed public wording row",
        "Default app behavior, full GIS/routing, row output, Python orchestration",
    ),
    "docs/application_catalog.md": (
        "road_hazard_screening / prepared_native_compact_summary_40k",
        "Goal1208 authorizes",
        "only the bounded road-hazard prepared native",
        "whole-app road-hazard speedup",
        "remain outside the claim",
    ),
    "docs/release_facing_examples.md": (
        "road_hazard_screening / prepared_native_compact_summary_40k",
        "Goal1208 authorizes only the bounded",
        "road-hazard prepared native compact-summary wording",
        "These commands are bounded sub-paths, not broad speedup claims",
    ),
    "docs/rtdl_feature_guide.md": (
        "road_hazard_screening / prepared_native_compact_summary_40k",
        "Goal1208 authorizes only the bounded",
        "road-hazard prepared native compact-summary wording",
        "whole-app road-hazard speedup remain",
        "outside the claim",
    ),
    "docs/v1_0_rtx_app_status.md": (
        "reviewed public RTX sub-path wording rows: `13`",
        "road_hazard_screening / prepared_native_compact_summary_40k",
        "Goal1208 adds exactly one reviewed public wording row",
        "Goal1224 resolves graph and Hausdorff; Goal1263 promotes bounded polygon-pair wording",
        "Graph remains blocked",
        "broad or whole-app public speedup claim authorized: `False`",
    ),
    "src/rtdsl/app_support_matrix.py": (
        "PUBLIC_WORDING_REVIEWED",
        "RTDL's prepared native road-hazard RTX sub-path measured 0.230652 s",
        "Goal1208",
        "whole-app road-hazard speedup",
    ),
}

PUBLIC_SURFACE_FORBIDDEN: tuple[str, ...] = (
    "Goal1208 authorizes full GIS",
    "Goal1208 authorizes whole-app",
    "database_analytics / public speedup",
    "polygon_set_jaccard / public speedup",
    "reviewed public RTX sub-path wording rows: `10`",
    "Current reviewed public wording rows after Goal1126",
)

RECORDED_CHECKS: tuple[dict[str, Any], ...] = (
    {
        "name": "goal1209_public_surface_suite",
        "command": (
            "PYTHONPATH=src:. python3 -m unittest "
            "tests.goal1011_rtx_public_wording_matrix_test "
            "tests.goal947_v1_rtx_app_status_page_test "
            "tests.goal1010_public_rtx_readme_wording_test "
            "tests.goal938_public_rtx_wording_sync_test "
            "tests.goal1179_public_docs_goal1177_boundary_audit_test "
            "tests.goal1180_current_release_readiness_window_audit_test "
            "tests.goal1185_goal1184_public_status_sync_audit_test "
            "tests.goal1186_current_release_readiness_after_goal1185_audit_test -v"
        ),
        "result": "OK",
        "tests": 35,
    },
    {
        "name": "goal1209_focused_matrix_docs_suite",
        "command": (
            "PYTHONPATH=src:. python3 -m unittest "
            "tests.goal1011_rtx_public_wording_matrix_test "
            "tests.goal947_v1_rtx_app_status_page_test "
            "tests.goal1010_public_rtx_readme_wording_test -v"
        ),
        "result": "OK",
        "tests": 18,
    },
)


def _check_path(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    return {"path": rel_path, "exists": path.exists()}


def _check_phrases(rel_path: str, phrases: tuple[str, ...]) -> dict[str, Any]:
    path = ROOT / rel_path
    exists = path.exists()
    text = path.read_text(encoding="utf-8") if exists else ""
    missing = [phrase for phrase in phrases if phrase not in text]
    forbidden = [phrase for phrase in PUBLIC_SURFACE_FORBIDDEN if phrase in text]
    return {
        "path": rel_path,
        "exists": exists,
        "missing_phrases": missing,
        "forbidden_phrases": forbidden,
        "status": "ok" if exists and not missing and not forbidden else "surface_failure",
    }


def build_audit() -> dict[str, Any]:
    goal_rows: list[dict[str, Any]] = []
    for goal, files in REQUIRED_GOAL_FILES.items():
        file_rows = [_check_path(path) for path in files]
        missing = [row["path"] for row in file_rows if not row["exists"]]
        goal_rows.append(
            {
                "goal": goal,
                "files": file_rows,
                "missing_files": missing,
                "status": "ok" if not missing else "missing_goal_closure_file",
            }
        )

    surface_rows = [
        _check_phrases(path, phrases)
        for path, phrases in CURRENT_PUBLIC_SURFACE_REQUIREMENTS.items()
    ]
    failing_goals = [row for row in goal_rows if row["status"] != "ok"]
    failing_surface = [row for row in surface_rows if row["status"] != "ok"]
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": not failing_goals and not failing_surface,
        "goal_count": len(goal_rows),
        "failing_goal_count": len(failing_goals),
        "surface_doc_count": len(surface_rows),
        "failing_surface_doc_count": len(failing_surface),
        "goal_rows": goal_rows,
        "surface_rows": surface_rows,
        "recorded_checks": list(RECORDED_CHECKS),
        "public_wording_row_count_expected": 13,
        "new_public_wording_rows": ["road_hazard_screening / prepared_native_compact_summary_40k"],
        "blocked_public_speedup_wording": ["graph_analytics"],
        "boundary": (
            "Goal1210 is a historical release-readiness evidence audit after Goal1209, "
            "now run against the current post-Goal1263 public surface. It confirms "
            "Goal1204-Goal1209 have external-AI consensus trails, road-hazard wording "
            "remains bounded, and the current docs use the 13-row Goal1263 wording "
            "state with graph still blocked and without tagging or releasing v0.9.8."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1210 v0.9.8 Release-Readiness Audit",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- valid: `{payload['valid']}`",
        f"- audited goals: `{payload['goal_count']}`",
        f"- goals missing closure files: `{payload['failing_goal_count']}`",
        f"- public surface docs checked: `{payload['surface_doc_count']}`",
        f"- public surface failures: `{payload['failing_surface_doc_count']}`",
        f"- expected reviewed public wording rows: `{payload['public_wording_row_count_expected']}`",
        f"- new public wording row: `{payload['new_public_wording_rows'][0]}`",
        "- graph public speedup wording: `blocked`",
        "",
        "## Goal Closure Rows",
        "",
        "| Goal | Status | Missing files |",
        "| --- | --- | ---: |",
    ]
    for row in payload["goal_rows"]:
        lines.append(
            f"| `{row['goal']}` | `{row['status']}` | `{len(row['missing_files'])}` |"
        )

    lines.extend(
        [
            "",
            "## Public Surface Rows",
            "",
            "| Path | Status | Missing | Forbidden |",
            "| --- | --- | ---: | ---: |",
        ]
    )
    for row in payload["surface_rows"]:
        lines.append(
            f"| `{row['path']}` | `{row['status']}` | "
            f"`{len(row['missing_phrases'])}` | `{len(row['forbidden_phrases'])}` |"
        )

    lines.extend(["", "## Recorded Checks", "", "| Check | Result | Tests |", "| --- | --- | ---: |"])
    for check in payload["recorded_checks"]:
        lines.append(f"| `{check['name']}` | `{check['result']}` | `{check['tests']}` |")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit v0.9.8 release readiness after Goal1209.")
    parser.add_argument("--output-json", default="docs/reports/goal1210_v0_9_8_release_readiness_audit_2026-05-01.json")
    parser.add_argument("--output-md", default="docs/reports/goal1210_v0_9_8_release_readiness_audit_2026-05-01.md")
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

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1109 v1 RTX readiness status after Goal1121 current-source RTX intake"


def build_status() -> dict[str, Any]:
    rows = [
        {
            "app": "facility_knn_assignment",
            "path_name": "coverage_threshold_prepared_recentered",
            "status": "engineering_review_ready_needs_public_wording_review",
            "latest_evidence": [
                "docs/reports/goal1116_current_source_rtx_rerun_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json",
                "docs/reports/goal1101_current_contract_non_optix_baselines/facility_recentered_2_5m_cpu_oracle_baseline.json",
                "docs/reports/goal1101_current_contract_non_optix_baselines/facility_recentered_2_5m_embree_baseline.json",
                "docs/reports/goal1121_current_source_rtx_rerun_intake_with_robot_64m_2026-04-29.json",
                "docs/reports/goal1121_two_ai_consensus_2026-04-29.md",
            ],
            "engineering_ratio_summary": "87.24x vs CPU oracle; 289.05x vs Embree using query-phase medians",
            "next_action": (
                "Run a public wording review against the Goal1121 current-source artifact before any README/front-page claim."
            ),
            "public_speedup_claim_authorized": False,
        },
        {
            "app": "robot_collision_screening",
            "path_name": "prepared_pose_flags",
            "status": "engineering_review_ready_needs_public_wording_review",
            "latest_evidence": [
                "docs/reports/goal1090_robot_embree_local_runbook_2026-04-29.json",
                "docs/reports/goal1091_robot_pose_offset_smoke_intake_2026-04-29.json",
                "docs/reports/goal1085_robot_chunked_embree_baseline/validation_chunk_0.json",
                "docs/reports/goal1085_robot_chunked_embree_baseline/timing_chunk_*.json",
                "docs/reports/goal1086_robot_chunked_embree_baseline_intake_2026-04-29.json",
                "docs/reports/goal1114_two_ai_consensus_2026-04-29.md",
                "docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_validation.json",
                "docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_64m_timing_goal1121.json",
                "docs/reports/goal1121_current_source_rtx_rerun_intake_with_robot_64m_2026-04-29.json",
                "docs/reports/goal1121_two_ai_consensus_2026-04-29.md",
            ],
            "engineering_ratio_summary": (
                "Robot same-source RTX evidence complete: 4096-pose correctness passed; 64M-pose timing crossed "
                "the 100 ms floor at 0.178698s median query. Same-scale public ratio still requires wording review."
            ),
            "next_action": (
                "Run a public wording review that decides whether the 64M RTX timing can be compared to the 36M "
                "chunked Embree native-any-hit baseline, and document any normalization limits."
            ),
            "public_speedup_claim_authorized": False,
        },
        {
            "app": "barnes_hut_force_app",
            "path_name": "node_coverage_prepared_rich",
            "status": "engineering_review_ready_needs_public_wording_review",
            "latest_evidence": [
                "docs/reports/goal1116_current_source_rtx_rerun_packet/barnes_hut_depth8_4096_validation.json",
                "docs/reports/goal1116_current_source_rtx_rerun_packet/barnes_hut_depth8_20m_timing.json",
                "docs/reports/goal1101_current_contract_non_optix_baselines/barnes_hut_depth8_20m_embree_timing_baseline.json",
                "docs/reports/goal1121_current_source_rtx_rerun_intake_with_robot_64m_2026-04-29.json",
                "docs/reports/goal1121_two_ai_consensus_2026-04-29.md",
            ],
            "engineering_ratio_summary": "222.19x vs Embree using query-phase medians",
            "next_action": (
                "Run a public wording review against the Goal1121 current-source validation and 20M timing artifacts "
                "before any README/front-page claim."
            ),
            "public_speedup_claim_authorized": False,
        },
    ]
    summary = {
        "row_count": len(rows),
        "engineering_comparison_ready_count": sum(
            row["status"].startswith("engineering_review_ready") for row in rows
        ),
        "non_cloud_ready_count": sum("ready_for_non_cloud" in row["status"] for row in rows),
        "blocked_count": sum("blocked" in row["status"] for row in rows),
        "public_speedup_claim_authorized_count": sum(
            1 for row in rows if row["public_speedup_claim_authorized"]
        ),
    }
    valid = (
        len(rows) == 3
        and summary["engineering_comparison_ready_count"] == 3
        and summary["non_cloud_ready_count"] == 0
        and summary["blocked_count"] == 0
        and summary["public_speedup_claim_authorized_count"] == 0
    )
    return {
        "goal": GOAL,
        "date": DATE,
        "supersedes": "docs/reports/goal1109_v1_rtx_readiness_status_after_baselines_2026-04-29.json",
        "rows": rows,
        "summary": summary,
        "valid": valid,
        "boundary": (
            "Goal1109 refreshes v1 RTX readiness after Goal1121 current-source RTX intake. It does not run cloud, "
            "does not authorize release, does not change public wording, and does not authorize public RTX speedup claims. "
            "Facility, Robot, and Barnes-Hut have engineering review evidence only; public wording review remains required."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1109 V1 RTX Readiness Status After Goal1121 Current-Source RTX Intake",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        f"Supersedes: `{payload['supersedes']}`",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in payload["summary"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| App | Path | Status | Engineering ratio summary | Next action | Claim authorized |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in payload["rows"]:
        ratio = "" if row["engineering_ratio_summary"] is None else row["engineering_ratio_summary"]
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{row['status']}` | "
            f"{ratio} | {row['next_action']} | `{row['public_speedup_claim_authorized']}` |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh v1 RTX readiness after baseline comparison.")
    parser.add_argument(
        "--output-json",
        default="docs/reports/goal1109_v1_rtx_readiness_status_after_baselines_2026-04-29.json",
    )
    parser.add_argument(
        "--output-md",
        default="docs/reports/goal1109_v1_rtx_readiness_status_after_baselines_2026-04-29.md",
    )
    args = parser.parse_args()
    payload = build_status()
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / args.output_md).write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], **payload["summary"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

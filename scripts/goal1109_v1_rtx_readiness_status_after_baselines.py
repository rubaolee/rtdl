#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1109 v1 RTX readiness status after baseline comparison"


def build_status() -> dict[str, Any]:
    rows = [
        {
            "app": "facility_knn_assignment",
            "path_name": "coverage_threshold_prepared_recentered",
            "status": "engineering_comparison_ready_needs_same_source_rtx_rerun_and_public_wording_review",
            "latest_evidence": [
                "docs/reports/goal1084_facility_recentered_rtx_pod_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json",
                "docs/reports/goal1101_current_contract_non_optix_baselines/facility_recentered_2_5m_cpu_oracle_baseline.json",
                "docs/reports/goal1101_current_contract_non_optix_baselines/facility_recentered_2_5m_embree_baseline.json",
                "docs/reports/goal1108_current_rtx_vs_baseline_comparison_2026-04-29.json",
                "docs/reports/goal1108_two_ai_consensus_2026-04-29.md",
            ],
            "engineering_ratio_summary": "66.61x vs CPU oracle; 220.70x vs Embree",
            "next_action": (
                "On next RTX pod, rerun the facility RTX artifact from the current source revision, "
                "then perform public wording review before any README/front-page claim."
            ),
            "public_speedup_claim_authorized": False,
        },
        {
            "app": "robot_collision_screening",
            "path_name": "prepared_pose_flags",
            "status": "engineering_comparison_ready_needs_same_source_rtx_rerun_and_public_wording_review",
            "latest_evidence": [
                "docs/reports/goal1090_robot_embree_local_runbook_2026-04-29.json",
                "docs/reports/goal1091_robot_pose_offset_smoke_intake_2026-04-29.json",
                "docs/reports/goal1085_robot_chunked_embree_baseline/validation_chunk_0.json",
                "docs/reports/goal1085_robot_chunked_embree_baseline/timing_chunk_*.json",
                "docs/reports/goal1086_robot_chunked_embree_baseline_intake_2026-04-29.json",
                "docs/reports/goal1114_two_ai_consensus_2026-04-29.md",
            ],
            "engineering_ratio_summary": (
                "Robot non-OptiX baseline complete: 36M poses, Embree native any-hit sum 92.25s; "
                "ratio intentionally withheld until same-source RTX rerun"
            ),
            "next_action": (
                "On next RTX pod, rerun the Robot prepared pose-flags RTX timing from the current source "
                "revision at a scale comparable to the 36M-pose Embree baseline, then perform public wording review."
            ),
            "public_speedup_claim_authorized": False,
        },
        {
            "app": "barnes_hut_force_app",
            "path_name": "node_coverage_prepared_rich",
            "status": "engineering_comparison_ready_needs_same_source_rtx_rerun_and_public_wording_review",
            "latest_evidence": [
                "docs/reports/goal1093_barnes_hut_20m_contract/barnes_hut_depth8_4096_validation.json",
                "docs/reports/goal1093_barnes_hut_20m_contract/barnes_hut_depth8_20m_timing.json",
                "docs/reports/goal1101_current_contract_non_optix_baselines/barnes_hut_depth8_20m_embree_timing_baseline.json",
                "docs/reports/goal1108_current_rtx_vs_baseline_comparison_2026-04-29.json",
                "docs/reports/goal1108_two_ai_consensus_2026-04-29.md",
            ],
            "engineering_ratio_summary": "231.82x vs Embree",
            "next_action": (
                "On next RTX pod, rerun the Barnes-Hut validation and 20M timing artifacts from the current "
                "source revision, then perform public wording review before any README/front-page claim."
            ),
            "public_speedup_claim_authorized": False,
        },
    ]
    summary = {
        "row_count": len(rows),
        "engineering_comparison_ready_count": sum(
            row["status"].startswith("engineering_comparison_ready") for row in rows
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
        "supersedes": "docs/reports/goal1099_post_pod_readiness_status_refresh_2026-04-29.json",
        "rows": rows,
        "summary": summary,
        "valid": valid,
        "boundary": (
            "Goal1109 refreshes v1 RTX readiness after same-contract baseline comparison. It does not run cloud, "
            "does not authorize release, does not change public wording, and does not authorize public RTX speedup claims. "
            "Facility, Robot, and Barnes-Hut have engineering comparison evidence only; same-source RTX reruns and public wording review remain required."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1109 V1 RTX Readiness Status After Baseline Comparison",
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

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1099 post-pod RTX readiness status refresh"


def build_status() -> dict[str, Any]:
    rows = [
        {
            "app": "facility_knn_assignment",
            "path_name": "coverage_threshold_prepared_recentered",
            "status": "rtx_pod_evidence_intaked_needs_same_semantics_baseline_and_public_wording_review",
            "latest_evidence": [
                "docs/reports/goal1083_facility_recentered_2_5m_cpu_oracle.json",
                "docs/reports/goal1084_facility_recentered_rtx_pod_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json",
                "docs/reports/goal1096_current_rtx_pod_artifact_intake_2026-04-29.json",
                "docs/reports/goal1098_two_ai_consensus_2026-04-29.md",
            ],
            "next_action": (
                "Run or identify a same-semantics baseline for the same recentered facility contract, "
                "then perform a public wording review before any README/front-page speedup claim."
            ),
            "public_speedup_claim_authorized": False,
        },
        {
            "app": "robot_collision_screening",
            "path_name": "prepared_pose_flags",
            "status": "ready_for_non_cloud_chunked_embree_baseline_execution",
            "latest_evidence": [
                "docs/reports/goal1090_robot_embree_local_runbook_2026-04-29.json",
                "docs/reports/goal1091_robot_pose_offset_smoke_intake_2026-04-29.json",
            ],
            "next_action": (
                "Use Goal1090 to run the Goal1085 resumable 180-chunk Embree baseline on Linux/Windows, "
                "then run Goal1086 intake and 2+ AI review."
            ),
            "public_speedup_claim_authorized": False,
        },
        {
            "app": "barnes_hut_force_app",
            "path_name": "node_coverage_prepared_rich",
            "status": "rtx_pod_evidence_intaked_needs_same_semantics_baseline_and_public_wording_review",
            "latest_evidence": [
                "docs/reports/goal1093_barnes_hut_20m_contract/barnes_hut_depth8_4096_validation.json",
                "docs/reports/goal1093_barnes_hut_20m_contract/barnes_hut_depth8_20m_timing.json",
                "docs/reports/goal1096_current_rtx_pod_artifact_intake_2026-04-29.json",
                "docs/reports/goal1098_two_ai_consensus_2026-04-29.md",
            ],
            "next_action": (
                "Run or identify a same-semantics baseline for the Barnes-Hut node-coverage contract, "
                "then perform a public wording review before any README/front-page speedup claim."
            ),
            "public_speedup_claim_authorized": False,
        },
    ]
    summary = {
        "row_count": len(rows),
        "pod_ready_count": sum("ready_for_next_rtx_pod" in row["status"] for row in rows),
        "evidence_intaked_count": sum("rtx_pod_evidence_intaked" in row["status"] for row in rows),
        "non_cloud_ready_count": sum("ready_for_non_cloud" in row["status"] for row in rows),
        "blocked_count": sum("blocked" in row["status"] for row in rows),
        "public_speedup_claim_authorized_count": sum(
            1 for row in rows if row["public_speedup_claim_authorized"]
        ),
    }
    valid = (
        len(rows) == 3
        and summary["pod_ready_count"] == 0
        and summary["evidence_intaked_count"] == 2
        and summary["non_cloud_ready_count"] == 1
        and summary["blocked_count"] == 0
        and summary["public_speedup_claim_authorized_count"] == 0
    )
    return {
        "goal": GOAL,
        "date": DATE,
        "supersedes": "docs/reports/goal1094_v1_rtx_readiness_status_refresh_2026-04-29.json",
        "rows": rows,
        "summary": summary,
        "valid": valid,
        "boundary": (
            "Goal1099 refreshes readiness after the RTX A5000 pod evidence intake. It does not run cloud, "
            "does not authorize release, does not change public wording, and does not authorize public RTX "
            "speedup claims. Same-semantics baselines and public wording review remain required."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1099 Post-Pod RTX Readiness Status Refresh",
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
            "| App | Path | Status | Next action | Claim authorized |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in payload["rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{row['status']}` | "
            f"{row['next_action']} | `{row['public_speedup_claim_authorized']}` |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh v1 RTX readiness status after Goal1098 pod intake.")
    parser.add_argument(
        "--output-json",
        default="docs/reports/goal1099_post_pod_readiness_status_refresh_2026-04-29.json",
    )
    parser.add_argument(
        "--output-md",
        default="docs/reports/goal1099_post_pod_readiness_status_refresh_2026-04-29.md",
    )
    args = parser.parse_args()
    payload = build_status()
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / args.output_md).write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], **payload["summary"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1092 v1 RTX readiness status refresh"


def build_status() -> dict[str, Any]:
    rows = [
        {
            "app": "facility_knn_assignment",
            "path_name": "coverage_threshold_prepared_recentered",
            "status": "ready_for_next_rtx_pod_validation",
            "latest_evidence": [
                "docs/reports/goal1083_facility_recentered_2_5m_cpu_oracle.json",
                "docs/reports/goal1084_facility_recentered_rtx_pod_packet_2026-04-29.json",
            ],
            "next_action": "Run Goal1084 on the next RTX pod without --skip-validation, then write artifact intake and 2+ AI review.",
            "public_speedup_claim_authorized": False,
        },
        {
            "app": "robot_collision_screening",
            "path_name": "prepared_pose_flags",
            "status": "ready_for_non_cloud_chunked_embree_baseline_execution",
            "latest_evidence": [
                "docs/reports/goal1090_robot_embree_local_runbook_2026-04-29.json",
                "docs/reports/goal1091_robot_embree_pose_offset_smoke_2026-04-29.json",
                "docs/reports/goal1091_robot_pose_offset_smoke_intake_2026-04-29.json",
            ],
            "next_action": "Use Goal1090 to run the Goal1085 resumable 180-chunk Embree baseline on Linux/Windows, then run Goal1086 intake and 2+ AI review.",
            "public_speedup_claim_authorized": False,
        },
        {
            "app": "barnes_hut_force_app",
            "path_name": "node_coverage_prepared_rich",
            "status": "blocked_pending_contract_supersession",
            "latest_evidence": [
                "docs/reports/goal1079_barnes_hut_rich_scale_up_probe/barnes_hut_rich_node_coverage_20m_timing.json",
                "docs/reports/goal1079_two_ai_consensus_2026-04-29.md",
            ],
            "next_action": "Define and review a 20M validation/intake contract before spending more cloud time or changing public wording.",
            "public_speedup_claim_authorized": False,
        },
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "supersedes": "docs/reports/goal1088_v1_rtx_readiness_status_audit_2026-04-29.json",
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "facility_ready_for_pod": rows[0]["status"] == "ready_for_next_rtx_pod_validation",
            "robot_ready_for_non_cloud_baseline": rows[1]["status"]
            == "ready_for_non_cloud_chunked_embree_baseline_execution",
            "barnes_hut_blocked": rows[2]["status"] == "blocked_pending_contract_supersession",
            "public_speedup_claim_authorized_count": sum(
                1 for row in rows if row["public_speedup_claim_authorized"]
            ),
        },
        "valid": (
            len(rows) == 3
            and not any(row["public_speedup_claim_authorized"] for row in rows)
            and rows[0]["status"] == "ready_for_next_rtx_pod_validation"
            and rows[1]["status"] == "ready_for_non_cloud_chunked_embree_baseline_execution"
            and rows[2]["status"] == "blocked_pending_contract_supersession"
        ),
        "boundary": (
            "Goal1092 refreshes readiness status only. It does not run cloud, does not run the heavy robot baseline, "
            "does not authorize release, does not change public wording, and does not authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1092 v1 RTX Readiness Status Refresh",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        f"Supersedes: `{payload['supersedes']}`",
        "",
        payload["boundary"],
        "",
        "## Rows",
        "",
        "| App | Path | Status | Next action | Claim authorized |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{row['status']}` | "
            f"{row['next_action']} | `{row['public_speedup_claim_authorized']}` |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh current v1 RTX readiness status.")
    parser.add_argument("--output-json", default="docs/reports/goal1092_v1_rtx_readiness_status_refresh_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1092_v1_rtx_readiness_status_refresh_2026-04-29.md")
    args = parser.parse_args()
    payload = build_status()
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / args.output_md).write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], **payload["summary"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

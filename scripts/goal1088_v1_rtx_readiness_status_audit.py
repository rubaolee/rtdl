#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1088 v1 RTX readiness status audit"


def build_audit() -> dict[str, Any]:
    rows = [
        {
            "app": "facility_knn_assignment",
            "path_name": "coverage_threshold_prepared_recentered",
            "current_status": "pending_next_rtx_pod_validation",
            "ready_artifact": "docs/reports/goal1084_facility_recentered_rtx_pod_packet_2026-04-29.json",
            "next_action": "Run Goal1084 via scripts/goal1084_facility_recentered_rtx_pod_packet_runner.sh on the next RTX pod without --skip-validation, then write intake/review.",
            "public_speedup_claim_authorized": False,
            "reason": "Original global-coordinate facility 2.5M row is blocked by Goal1082; Goal1083/1084 provide the precision-safe replacement candidate.",
        },
        {
            "app": "robot_collision_screening",
            "path_name": "prepared_pose_flags",
            "current_status": "pending_non_cloud_embree_baseline_execution",
            "ready_artifact": "docs/reports/goal1085_robot_chunked_embree_baseline_packet_2026-04-29.json",
            "next_action": "Run the resumable Goal1085 chunked Embree baseline on a strong non-cloud host, then run Goal1086 intake.",
            "public_speedup_claim_authorized": False,
            "reason": "RTX timing/validation evidence exists, but Goal1080 blocked public wording because the non-OptiX baseline scale did not match.",
        },
        {
            "app": "barnes_hut_force_app",
            "path_name": "node_coverage_prepared_rich",
            "current_status": "pending_contract_supersession",
            "ready_artifact": "docs/reports/goal1079_barnes_hut_rich_scale_up_probe/barnes_hut_rich_node_coverage_20m_timing.json",
            "next_action": "Define and review a 20M validation/intake contract and decide how Python input/packing overhead belongs in the comparison boundary.",
            "public_speedup_claim_authorized": False,
            "reason": "The reviewed Goal1076 1M row failed the timing floor; the 20M row is timing-only engineering evidence.",
        },
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "public_speedup_claim_authorized_count": sum(
                1 for row in rows if row["public_speedup_claim_authorized"]
            ),
            "pending_next_rtx_pod_validation_count": sum(
                1 for row in rows if row["current_status"] == "pending_next_rtx_pod_validation"
            ),
            "pending_non_cloud_baseline_count": sum(
                1 for row in rows if row["current_status"] == "pending_non_cloud_embree_baseline_execution"
            ),
            "pending_contract_supersession_count": sum(
                1 for row in rows if row["current_status"] == "pending_contract_supersession"
            ),
        },
        "valid": (
            len(rows) == 3
            and not any(row["public_speedup_claim_authorized"] for row in rows)
            and {row["app"] for row in rows}
            == {"facility_knn_assignment", "robot_collision_screening", "barnes_hut_force_app"}
        ),
        "boundary": (
            "Goal1088 is a status audit only. It does not run cloud or local heavy baselines, does not authorize release, "
            "does not change public wording, and does not authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1088 v1 RTX Readiness Status Audit",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
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
            f"| `{row['app']}` | `{row['path_name']}` | `{row['current_status']}` | "
            f"{row['next_action']} | `{row['public_speedup_claim_authorized']}` |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Write current v1 RTX readiness status audit.")
    parser.add_argument("--output-json", default="docs/reports/goal1088_v1_rtx_readiness_status_audit_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1088_v1_rtx_readiness_status_audit_2026-04-29.md")
    args = parser.parse_args()
    payload = build_audit()
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / args.output_md).write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], **payload["summary"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

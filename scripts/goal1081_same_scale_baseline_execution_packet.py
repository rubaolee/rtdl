#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1081 same-scale baseline execution packet"


def _command(*parts: str) -> list[str]:
    return list(parts)


def build_packet() -> dict[str, Any]:
    rows = [
        {
            "app": "facility_knn_assignment",
            "path_name": "coverage_threshold_prepared",
            "baseline_kind": "cpu_oracle_same_scale",
            "public_speedup_claim_authorized": False,
            "required_before_public_wording": True,
            "target_rtx_artifact": "docs/reports/goal1072_post_scale_up_rtx_pod_batch/facility_coverage_threshold_2_5m_timing.json",
            "scale": {"copies": 2_500_000, "query_count": 10_000_000, "iterations": 1},
            "expected_output_json": "docs/reports/goal1081_same_scale_baselines/facility_coverage_threshold_2_5m_cpu_oracle.json",
            "recommended_host": "local_or_linux",
            "purpose": (
                "Measure same-scale CPU oracle for the facility RTX timing row before any public speedup wording review."
            ),
            "command": _command(
                "PYTHONPATH=src:.",
                "python3",
                "scripts/goal887_prepared_decision_phase_profiler.py",
                "--scenario",
                "facility_service_coverage",
                "--mode",
                "dry-run",
                "--copies",
                "2500000",
                "--iterations",
                "1",
                "--radius",
                "1.0",
                "--output-json",
                "docs/reports/goal1081_same_scale_baselines/facility_coverage_threshold_2_5m_cpu_oracle.json",
            ),
        },
        {
            "app": "robot_collision_screening",
            "path_name": "prepared_pose_flags",
            "baseline_kind": "embree_same_scale",
            "public_speedup_claim_authorized": False,
            "required_before_public_wording": True,
            "target_rtx_artifact": "docs/reports/goal1072_post_scale_up_rtx_pod_batch/robot_prepared_pose_flags_36m_timing.json",
            "scale": {"pose_count": 36_000_000, "obstacle_count": 4096, "iterations": 3, "worker_count": 8},
            "expected_output_json": "docs/reports/goal1081_same_scale_baselines/robot_prepared_pose_flags_36m_embree_baseline.json",
            "recommended_host": "linux_or_windows_high_memory",
            "purpose": "Measure same-scale Embree pose-count baseline for the Goal1079 robot RTX timing row.",
            "command": _command(
                "PYTHONPATH=src:.",
                "python3",
                "scripts/goal839_robot_pose_count_baseline.py",
                "--backend",
                "embree",
                "--pose-count",
                "36000000",
                "--obstacle-count",
                "4096",
                "--iterations",
                "3",
                "--worker-count",
                "8",
                "--output-json",
                "docs/reports/goal1081_same_scale_baselines/robot_prepared_pose_flags_36m_embree_baseline.json",
            ),
        },
        {
            "app": "barnes_hut_force_app",
            "path_name": "node_coverage_prepared_rich",
            "baseline_kind": "future_contract",
            "public_speedup_claim_authorized": False,
            "required_before_public_wording": True,
            "target_rtx_artifact": "docs/reports/goal1079_barnes_hut_rich_scale_up_probe/barnes_hut_rich_node_coverage_20m_timing.json",
            "scale": {"body_count": 20_000_000, "node_count": 65_536, "iterations": 5},
            "expected_output_json": None,
            "recommended_host": "not_ready",
            "purpose": (
                "Do not collect public-wording baseline yet. First define a reviewed 20M validation/intake "
                "contract and decide whether the huge Python input/packing overhead should be part of the claim boundary."
            ),
            "command": [],
        },
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "source_artifacts": [
            "docs/reports/goal1080_post_pod_public_wording_readiness_audit_2026-04-29.json",
            "docs/reports/goal1079_rtx_pod_batch_result_2026-04-29.md",
        ],
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "executable_row_count": sum(1 for row in rows if row["command"]),
            "not_ready_row_count": sum(1 for row in rows if not row["command"]),
            "public_speedup_claim_authorized_count": sum(
                1 for row in rows if row["public_speedup_claim_authorized"]
            ),
        },
        "valid": (
            len(rows) == 3
            and sum(1 for row in rows if row["command"]) == 2
            and not any(row["public_speedup_claim_authorized"] for row in rows)
            and all(row["required_before_public_wording"] for row in rows)
            and rows[0]["scale"]["copies"] == 2_500_000
            and rows[1]["scale"]["pose_count"] == 36_000_000
            and rows[1]["scale"]["obstacle_count"] == 4096
            and rows[2]["recommended_host"] == "not_ready"
        ),
        "boundary": (
            "Goal1081 prepares same-scale baseline commands only. It does not run them, does not change public wording, "
            "does not authorize release, and does not authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1081 Same-Scale Baseline Execution Packet",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        payload["boundary"],
        "",
        "## Rows",
        "",
        "| App | Path | Baseline | Host | Output | Command |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        command = " ".join(row["command"]) if row["command"] else "not ready: contract redesign required"
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{row['baseline_kind']}` | "
            f"`{row['recommended_host']}` | `{row['expected_output_json']}` | `{command}` |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build same-scale baseline execution packet.")
    parser.add_argument("--output-json", default="docs/reports/goal1081_same_scale_baseline_execution_packet_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1081_same_scale_baseline_execution_packet_2026-04-29.md")
    args = parser.parse_args()
    payload = build_packet()
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / args.output_md).write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], **payload["summary"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

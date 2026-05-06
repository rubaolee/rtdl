#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt


DATE = "2026-04-29"
GOAL = "Goal1080 post-pod public wording readiness audit"
GOAL1073 = ROOT / "docs/reports/goal1073_goal1072_artifact_intake_after_pod_2026-04-29.json"
GOAL1078 = ROOT / "docs/reports/goal1078_goal1076_artifact_intake_after_pod_2026-04-29.json"
GOAL1079_BARNES = ROOT / "docs/reports/goal1079_barnes_hut_rich_scale_up_probe/barnes_hut_rich_node_coverage_20m_timing.json"
FACILITY_BASELINE = ROOT / "docs/reports/goal835_baseline_facility_knn_assignment_coverage_threshold_prepared_cpu_oracle_same_semantics_2026-04-23.json"
ROBOT_BASELINE = ROOT / "docs/reports/goal835_baseline_robot_collision_screening_prepared_pose_flags_embree_anyhit_pose_count_or_equivalent_compact_summary_2026-04-23.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_report_artifact(path: str) -> Path:
    raw = Path(path)
    if raw.exists():
        return raw
    parts = raw.parts
    for index in range(len(parts) - 1):
        if parts[index] == "docs" and parts[index + 1] == "reports":
            relocated = ROOT.joinpath(*parts[index:])
            if relocated.exists():
                return relocated
    return raw


def _row_by(intake: dict[str, Any], app: str, phase: str) -> dict[str, Any]:
    for row in intake["rows"]:
        if row["app"] == app and row["phase"] == phase:
            return row
    raise KeyError((app, phase))


def _artifact(path: str) -> dict[str, Any]:
    return _load(_resolve_report_artifact(path))


def _facility_row(goal1073: dict[str, Any]) -> dict[str, Any]:
    timing = _row_by(goal1073, "facility_knn_assignment", "large_timing_repeat")
    validation = _row_by(goal1073, "facility_knn_assignment", "correctness_validation")
    artifact = _artifact(timing["artifact_path"])
    baseline = _load(FACILITY_BASELINE)
    scale = {
        "rtx_copies": artifact["parameters"]["copies"],
        "rtx_query_count": artifact["scenario"]["result"]["query_count"],
        "baseline_copies": baseline["benchmark_scale"]["copies"],
        "baseline_customer_count": baseline["summary"]["customer_count"],
    }
    scale_match = scale["rtx_copies"] == scale["baseline_copies"]
    return {
        "app": "facility_knn_assignment",
        "path_name": "coverage_threshold_prepared",
        "post_pod_status": goal1073["overall_status"],
        "validation_status": validation["review_status"],
        "timing_status": timing["review_status"],
        "rtx_phase_sec": timing["rtx_phase_sec"],
        "baseline_name": baseline["baseline_name"],
        "baseline_phase_sec": baseline["phase_seconds"]["native_query"],
        "scale": scale,
        "same_scale_baseline_available": scale_match,
        "current_public_wording_status": rt.rtx_public_wording_status("facility_knn_assignment").status,
        "decision": "needs_same_scale_baseline_review",
        "reason": (
            "Goal1079 cleared validation and the 100 ms RTX timing floor, but the available same-semantics "
            "baseline is at 20k copies while the new RTX timing row is at 2.5M copies. Do not compute or "
            "publish a speedup ratio from mismatched scales."
        ),
        "public_speedup_claim_authorized": False,
    }


def _robot_row(goal1073: dict[str, Any]) -> dict[str, Any]:
    timing = _row_by(goal1073, "robot_collision_screening", "large_timing_repeat")
    validation = _row_by(goal1073, "robot_collision_screening", "correctness_validation")
    artifact = _artifact(timing["artifact_path"])
    baseline = _load(ROBOT_BASELINE)
    scale = {
        "rtx_pose_count": artifact["pose_count"],
        "rtx_obstacle_count": artifact["obstacle_count"],
        "baseline_pose_count": baseline["benchmark_scale"]["pose_count"],
        "baseline_obstacle_count": baseline["benchmark_scale"]["obstacle_count"],
    }
    scale_match = (
        scale["rtx_pose_count"] == scale["baseline_pose_count"]
        and scale["rtx_obstacle_count"] == scale["baseline_obstacle_count"]
    )
    return {
        "app": "robot_collision_screening",
        "path_name": "prepared_pose_flags",
        "post_pod_status": goal1073["overall_status"],
        "validation_status": validation["review_status"],
        "timing_status": timing["review_status"],
        "rtx_phase_sec": timing["rtx_phase_sec"],
        "baseline_name": baseline["baseline_name"],
        "baseline_phase_sec": baseline["phase_seconds"]["native_anyhit_query"],
        "scale": scale,
        "same_scale_baseline_available": scale_match,
        "current_public_wording_status": rt.rtx_public_wording_status("robot_collision_screening").status,
        "decision": "needs_same_scale_baseline_review",
        "reason": (
            "Goal1079 cleared validation and barely cleared the 100 ms RTX timing floor, but the available "
            "Embree baseline is at 200k poses / 1,024 obstacles while the new RTX timing row is at 36M poses "
            "/ 4,096 obstacles. Do not compute or publish a speedup ratio from mismatched scales."
        ),
        "public_speedup_claim_authorized": False,
    }


def _barnes_row(goal1078: dict[str, Any]) -> dict[str, Any]:
    artifact = _load(GOAL1079_BARNES)
    timing = _row_by(goal1078, "barnes_hut_force_app", "large_timing_repeat")
    return {
        "app": "barnes_hut_force_app",
        "path_name": "node_coverage_prepared_rich",
        "post_pod_status": goal1078["overall_status"],
        "validation_status": _row_by(goal1078, "barnes_hut_force_app", "correctness_validation")["review_status"],
        "timing_status": timing["review_status"],
        "rtx_phase_sec_1m": timing["rtx_phase_sec"],
        "rtx_phase_sec_20m_probe": artifact["scenario"]["timings_sec"]["optix_query_sec"]["median_sec"],
        "scale": {
            "intake_body_count": 1_000_000,
            "probe_body_count": artifact["parameters"]["body_count"],
            "probe_node_count": artifact["scenario"]["result"]["node_count"],
        },
        "same_scale_baseline_available": False,
        "current_public_wording_status": rt.rtx_public_wording_status("barnes_hut_force_app").status,
        "decision": "needs_reviewed_20m_validation_and_baseline",
        "reason": (
            "The reviewed Goal1076 1M timing row failed the 100 ms floor. The Goal1079 20M probe passed the "
            "floor, but it is timing-only engineering evidence and needs a matching reviewed validation/intake "
            "contract plus same-scale baseline before public wording review."
        ),
        "public_speedup_claim_authorized": False,
    }


def build_audit() -> dict[str, Any]:
    goal1073 = _load(GOAL1073)
    goal1078 = _load(GOAL1078)
    rows = [_facility_row(goal1073), _robot_row(goal1073), _barnes_row(goal1078)]
    decision_counts: dict[str, int] = {}
    for row in rows:
        decision_counts[row["decision"]] = decision_counts.get(row["decision"], 0) + 1
    return {
        "goal": GOAL,
        "date": DATE,
        "source_artifacts": [
            str(GOAL1073.relative_to(ROOT)),
            str(GOAL1078.relative_to(ROOT)),
            str(GOAL1079_BARNES.relative_to(ROOT)),
            str(FACILITY_BASELINE.relative_to(ROOT)),
            str(ROBOT_BASELINE.relative_to(ROOT)),
        ],
        "rows": rows,
        "decision_counts": decision_counts,
        "public_speedup_claim_authorized_count": 0,
        "valid": (
            decision_counts == {
                "needs_same_scale_baseline_review": 2,
                "needs_reviewed_20m_validation_and_baseline": 1,
            }
            and all(row["public_speedup_claim_authorized"] is False for row in rows)
        ),
        "boundary": (
            "Goal1080 audits post-pod wording readiness only. It does not change public wording, "
            "does not authorize release, and does not authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1080 Post-Pod Public Wording Readiness Audit",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- rows audited: `{len(payload['rows'])}`",
        f"- decision counts: `{payload['decision_counts']}`",
        f"- public speedup claims authorized: `{payload['public_speedup_claim_authorized_count']}`",
        "",
        "## Rows",
        "",
        "| App | Path | RTX phase | Decision | Reason |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in payload["rows"]:
        phase = row.get("rtx_phase_sec", row.get("rtx_phase_sec_20m_probe"))
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{float(phase):.6f}` | "
            f"`{row['decision']}` | {row['reason']} |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit post-pod public wording readiness.")
    parser.add_argument("--output-json", default="docs/reports/goal1080_post_pod_public_wording_readiness_audit_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1080_post_pod_public_wording_readiness_audit_2026-04-29.md")
    args = parser.parse_args()
    payload = build_audit()
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / args.output_md).write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "decision_counts": payload["decision_counts"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

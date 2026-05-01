#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1126 robot normalized public RTX wording review"

RTX_64M = ROOT / "docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_64m_timing_goal1142.json"
RTX_VALIDATION = ROOT / "docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_validation.json"
RTX_INTAKE = ROOT / "docs/reports/goal1142_current_source_rtx_rerun_intake_with_robot_64m_2026-04-29.json"
EMBREE_36M = ROOT / "docs/reports/goal1086_robot_chunked_embree_baseline_intake_2026-04-29.json"
GOAL1123 = ROOT / "docs/reports/goal1123_public_wording_review_after_goal1121_2026-04-29.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _nested(data: dict[str, Any], keys: tuple[str, ...]) -> Any:
    cur: Any = data
    for key in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def build_packet() -> dict[str, Any]:
    rtx = _load(RTX_64M)
    validation = _load(RTX_VALIDATION)
    intake = _load(RTX_INTAKE)
    embree = _load(EMBREE_36M)
    goal1123 = _load(GOAL1123)

    rtx_pose_count = int(rtx["pose_count"])
    rtx_obstacle_count = int(rtx["obstacle_count"])
    rtx_query_sec = float(_nested(rtx, ("phases", "prepared_pose_flags_warm_query_sec", "median_sec")))
    rtx_per_pose_sec = rtx_query_sec / rtx_pose_count

    embree_pose_count = int(_nested(embree, ("observed", "timing_total_pose_count")))
    embree_expected_pose_count = int(_nested(embree, ("expected", "total_pose_count")))
    embree_obstacle_count = int(_nested(embree, ("expected", "obstacle_count")))
    embree_anyhit_sum_sec = float(_nested(embree, ("phase_seconds", "native_anyhit_sum_sec")))
    embree_per_pose_sec = embree_anyhit_sum_sec / embree_pose_count

    normalized_ratio = embree_per_pose_sec / rtx_per_pose_sec
    same_obstacle_count = rtx_obstacle_count == embree_obstacle_count
    same_result_contract = (
        rtx.get("result_mode") == "pose_count"
        and _nested(rtx, ("cloud_claim_contract", "result_mode")) == "pose_count"
    )
    validation_ok = (
        validation.get("validated") is True
        and validation.get("matches_oracle") is True
        and validation.get("mode") == "optix"
        and validation.get("result_mode") == "pose_flags"
    )
    intake_ok = intake.get("valid") is True and intake.get("summary", {}).get("same_source_commit") is True
    embree_ok = (
        embree.get("valid") is True
        and embree.get("status") == "complete"
        and embree_pose_count == embree_expected_pose_count
        and embree.get("contract_mode") == "split_validation_and_timing"
    )

    candidate_public_wording = (
        "RTDL's prepared robot collision pose-count RTX query sub-path measured "
        f"{rtx_query_sec:.6f} s for 64M poses and {normalized_ratio:.2f}x per-pose throughput "
        "versus the reviewed 36M chunked Embree any-hit baseline."
    )
    boundary = (
        "This is normalized per-pose wording, not a same-total-work wall-time claim. It covers only "
        "the prepared ray/triangle any-hit pose-count query sub-path. Full robot kinematics, scene "
        "construction, ray packing, witness-row output, continuous collision detection, Python input "
        "construction, and whole-app planning speedup are outside the wording."
    )
    return {
        "goal": GOAL,
        "date": DATE,
        "sources": [
            str(RTX_64M.relative_to(ROOT)),
            str(RTX_VALIDATION.relative_to(ROOT)),
            str(RTX_INTAKE.relative_to(ROOT)),
            str(EMBREE_36M.relative_to(ROOT)),
            str(GOAL1123.relative_to(ROOT)),
        ],
        "decision_under_review": "accept_explicit_normalized_baseline_review",
        "current_goal1123_robot_decision": [
            row for row in goal1123["rows"]
            if row["app"] == "robot_collision_screening"
        ][0]["decision"],
        "rtx": {
            "pose_count": rtx_pose_count,
            "obstacle_count": rtx_obstacle_count,
            "source_commit": rtx.get("source_commit"),
            "median_query_sec": rtx_query_sec,
            "per_pose_sec": rtx_per_pose_sec,
            "matches_oracle": rtx.get("matches_oracle"),
            "timing_validation_mode": "skip_validation_large_timing_repeat",
        },
        "embree": {
            "pose_count": embree_pose_count,
            "obstacle_count": embree_obstacle_count,
            "native_anyhit_sum_sec": embree_anyhit_sum_sec,
            "per_pose_sec": embree_per_pose_sec,
            "contract_mode": embree.get("contract_mode"),
        },
        "checks": {
            "same_obstacle_count": same_obstacle_count,
            "same_result_contract": same_result_contract,
            "separate_current_source_validation_ok": validation_ok,
            "current_source_intake_ok": intake_ok,
            "embree_chunked_baseline_ok": embree_ok,
            "pose_counts_differ": rtx_pose_count != embree_pose_count,
            "wording_explicitly_normalized": True,
        },
        "normalized_ratio_embree_per_pose_over_rtx_per_pose": normalized_ratio,
        "candidate_public_wording": candidate_public_wording,
        "boundary": boundary,
        "valid": (
            same_obstacle_count
            and same_result_contract
            and validation_ok
            and intake_ok
            and embree_ok
            and rtx_query_sec >= 0.100
            and normalized_ratio > 1.0
        ),
        "public_speedup_claim_authorized": False,
        "reviewer_questions": [
            "Is the normalized per-pose comparison acceptable despite 64M RTX versus 36M Embree total pose counts?",
            "Is the wording narrow enough to avoid same-total-work, whole-app, or robot-planning claims?",
            "If accepted, should a follow-up update only robot_collision_screening in rtdsl.rtx_public_wording_matrix() and public docs?",
        ],
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1126 Robot Normalized Public RTX Wording Review",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{payload['valid']}`",
        "",
        "Goal1126 is a review packet only. It does not edit public wording, authorize release, start cloud resources, or by itself authorize a public speedup claim.",
        "",
        "## Decision Under Review",
        "",
        f"`{payload['decision_under_review']}`",
        "",
        f"Current Goal1123 robot decision: `{payload['current_goal1123_robot_decision']}`",
        "",
        "## Evidence",
        "",
        "| Engine | Pose count | Obstacle count | Phase seconds | Per-pose seconds |",
        "| --- | ---: | ---: | ---: | ---: |",
        f"| RTX/OptiX | `{payload['rtx']['pose_count']}` | `{payload['rtx']['obstacle_count']}` | `{payload['rtx']['median_query_sec']:.6f}` | `{payload['rtx']['per_pose_sec']:.12f}` |",
        f"| Embree | `{payload['embree']['pose_count']}` | `{payload['embree']['obstacle_count']}` | `{payload['embree']['native_anyhit_sum_sec']:.6f}` | `{payload['embree']['per_pose_sec']:.12f}` |",
        "",
        f"Normalized per-pose ratio, Embree over RTX: `{payload['normalized_ratio_embree_per_pose_over_rtx_per_pose']:.2f}x`.",
        "",
        "## Checks",
        "",
    ]
    for key, value in payload["checks"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Candidate Public Wording",
            "",
            payload["candidate_public_wording"],
            "",
            f"Boundary: {payload['boundary']}",
            "",
            "## Reviewer Questions",
            "",
        ]
    )
    for question in payload["reviewer_questions"]:
        lines.append(f"- {question}")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Goal1126 robot normalized public RTX wording review packet.")
    parser.add_argument("--output-json", default="docs/reports/goal1126_robot_normalized_public_wording_review_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1126_robot_normalized_public_wording_review_2026-04-29.md")
    args = parser.parse_args(argv)
    payload = build_packet()
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / args.output_md).write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "ratio": payload["normalized_ratio_embree_per_pose_over_rtx_per_pose"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

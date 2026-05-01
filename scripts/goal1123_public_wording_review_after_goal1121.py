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
GOAL = "Goal1123 public RTX wording review after Goal1142"

INTAKE = ROOT / "docs" / "reports" / "goal1142_current_source_rtx_rerun_intake_with_robot_64m_2026-04-29.json"
FACILITY_CPU = ROOT / "docs" / "reports" / "goal1101_current_contract_non_optix_baselines" / "facility_recentered_2_5m_cpu_oracle_baseline.json"
FACILITY_EMBREE = ROOT / "docs" / "reports" / "goal1101_current_contract_non_optix_baselines" / "facility_recentered_2_5m_embree_baseline.json"
BARNES_EMBREE = ROOT / "docs" / "reports" / "goal1101_current_contract_non_optix_baselines" / "barnes_hut_depth8_20m_embree_timing_baseline.json"
ROBOT_EMBREE = ROOT / "docs" / "reports" / "goal1086_robot_chunked_embree_baseline_intake_2026-04-29.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _nested(data: dict[str, Any], keys: tuple[str, ...]) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _fmt_sec(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.6f}"


def _fmt_ratio(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2f}x"


def _intake_row(intake: dict[str, Any], app: str, phase: str) -> dict[str, Any]:
    for row in intake["rows"]:
        if row["app"] == app and row["phase"] == phase:
            return row
    raise KeyError(f"missing intake row for {app} / {phase}")


def _native_query_median(path: Path) -> float:
    data = _load(path)
    value = _nested(data, ("scenario", "timings_sec", "native_query_sec", "median_sec"))
    if not isinstance(value, (int, float)):
        raise ValueError(f"{path} has no native_query_sec median")
    return float(value)


def _robot_embree_total_native_sec(path: Path) -> float:
    data = _load(path)
    value = _nested(data, ("phase_seconds", "native_anyhit_sum_sec"))
    if not isinstance(value, (int, float)):
        raise ValueError(f"{path} has no robot native_anyhit_sum_sec")
    return float(value)


def build_packet() -> dict[str, Any]:
    intake = _load(INTAKE)
    facility_rtx = float(_intake_row(intake, "facility_knn_assignment", "same_scale_validation_and_timing")["median_query_sec"])
    robot_rtx = float(_intake_row(intake, "robot_collision_screening", "large_timing_repeat")["median_query_sec"])
    barnes_rtx = float(_intake_row(intake, "barnes_hut_force_app", "large_timing_repeat")["median_query_sec"])

    facility_cpu = _native_query_median(FACILITY_CPU)
    facility_embree = _native_query_median(FACILITY_EMBREE)
    barnes_embree = _native_query_median(BARNES_EMBREE)
    robot_embree = _robot_embree_total_native_sec(ROBOT_EMBREE)

    facility_ratio_cpu = facility_cpu / facility_rtx
    facility_ratio_embree = facility_embree / facility_rtx
    barnes_ratio_embree = barnes_embree / barnes_rtx
    robot_normalized_embree_per_pose = robot_embree / 36_000_000
    robot_normalized_rtx_per_pose = robot_rtx / 64_000_000
    robot_normalized_ratio = robot_normalized_embree_per_pose / robot_normalized_rtx_per_pose

    rows = [
        {
            "app": "facility_knn_assignment",
            "path_name": "coverage_threshold_prepared_recentered",
            "decision": "candidate_public_wording_reviewed",
            "status_to_apply": "public_wording_reviewed",
            "rtx_median_query_sec": facility_rtx,
            "baseline": "fastest same-contract non-OptiX baseline is CPU oracle",
            "fastest_baseline_ratio": facility_ratio_cpu,
            "secondary_baseline_ratio": facility_ratio_embree,
            "candidate_public_wording": (
                "RTDL's prepared facility coverage-threshold RTX query sub-path measured "
                f"{_fmt_sec(facility_rtx)} s and {_fmt_ratio(facility_ratio_cpu)} versus the "
                "reviewed same-contract CPU oracle baseline."
            ),
            "boundary": (
                "Only the prepared recentered coverage-threshold query decision is covered; "
                "ranked nearest-facility assignment, KNN fallback output, facility-location "
                "optimization, Python-side setup, and whole-app speedup are outside this wording."
            ),
        },
        {
            "app": "robot_collision_screening",
            "path_name": "prepared_pose_flags",
            "decision": "keep_public_wording_blocked_pending_same_scale_baseline",
            "status_to_apply": "public_wording_blocked",
            "rtx_median_query_sec": robot_rtx,
            "baseline": "RTX 64M timing crosses floor, but the available Embree aggregate is 36M chunked work",
            "fastest_baseline_ratio": None,
            "diagnostic_normalized_ratio_not_public": robot_normalized_ratio,
            "candidate_public_wording": "No public RTX speedup wording is authorized for robot_collision_screening yet.",
            "boundary": (
                "The prepared ray/triangle any-hit pose-flag path is real RT-core work and now "
                "has timing-floor evidence, but public ratio wording remains blocked until a "
                "same-scale or explicitly normalized baseline review is accepted."
            ),
        },
        {
            "app": "barnes_hut_force_app",
            "path_name": "node_coverage_prepared_rich",
            "decision": "candidate_public_wording_reviewed",
            "status_to_apply": "public_wording_reviewed",
            "rtx_median_query_sec": barnes_rtx,
            "baseline": "same-contract chunked Embree node-coverage baseline",
            "fastest_baseline_ratio": barnes_ratio_embree,
            "secondary_baseline_ratio": None,
            "candidate_public_wording": (
                "RTDL's prepared Barnes-Hut node-coverage RTX query sub-path measured "
                f"{_fmt_sec(barnes_rtx)} s and {_fmt_ratio(barnes_ratio_embree)} versus the "
                "reviewed same-contract Embree node-coverage baseline."
            ),
            "boundary": (
                "Only the prepared depth-8 node-coverage threshold traversal is covered; "
                "Barnes-Hut opening-rule evaluation, candidate-row output, force-vector "
                "reduction, N-body simulation, and whole-app speedup are outside this wording."
            ),
        },
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "sources": [
            str(INTAKE.relative_to(ROOT)),
            str(FACILITY_CPU.relative_to(ROOT)),
            str(FACILITY_EMBREE.relative_to(ROOT)),
            str(BARNES_EMBREE.relative_to(ROOT)),
            str(ROBOT_EMBREE.relative_to(ROOT)),
        ],
        "current_public_wording_source": "rtdsl.rtx_public_wording_matrix()",
        "candidate_reviewed_count": 2,
        "blocked_count": 1,
        "public_speedup_claim_authorized": False,
        "rows": rows,
        "boundary": (
            "Goal1123 is a public-wording review packet after Goal1142 same-source RTX evidence. It proposes "
            "narrow wording for two prepared RTX query sub-paths, keeps robot speedup wording "
            "blocked, and does not itself edit public docs or authorize release."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1123 Public RTX Wording Review After Goal1142",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- candidate reviewed rows proposed: `{payload['candidate_reviewed_count']}`",
        f"- blocked rows retained: `{payload['blocked_count']}`",
        f"- public speedup claim authorized by this packet: `{str(payload['public_speedup_claim_authorized']).lower()}`",
        "",
        "## Decisions",
        "",
        "| App | Path | Decision | RTX median query | Ratio |",
        "| --- | --- | --- | ---: | ---: |",
    ]
    for row in payload["rows"]:
        ratio = row.get("fastest_baseline_ratio")
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{row['decision']}` | "
            f"`{_fmt_sec(row['rtx_median_query_sec'])}` | `{_fmt_ratio(ratio)}` |"
        )
    lines.extend(["", "## Candidate Public Wording", ""])
    for row in payload["rows"]:
        lines.extend(
            [
                f"### {row['app']} / {row['path_name']}",
                "",
                row["candidate_public_wording"],
                "",
                f"Boundary: {row['boundary']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Reviewer Questions",
            "",
            "- Are the facility and Barnes-Hut wording lines narrow enough to avoid whole-app or default-mode claims?",
            "- Is robot correctly kept blocked despite timing-floor evidence because the public ratio still needs same-scale or accepted normalized baseline review?",
            "- Are the evidence sources sufficient to update `rtdsl.rtx_public_wording_matrix()` and user-facing docs in a follow-up goal?",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Goal1123 public RTX wording review packet.")
    parser.add_argument("--output-json", default="docs/reports/goal1123_public_wording_review_after_goal1121_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1123_public_wording_review_after_goal1121_2026-04-29.md")
    args = parser.parse_args()
    payload = build_packet()
    Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    Path(args.output_md).write_text(markdown + "\n", encoding="utf-8")
    print(json.dumps({"valid": True, "candidate_reviewed_count": 2, "blocked_count": 1}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-26"
GOAL = "Goal1008 large-repeat RTX artifact intake"
SOURCE = ROOT / "docs" / "reports" / "goal1006_public_rtx_claim_wording_gate_2026-04-26.json"
ARTIFACT_ROOT = (
    ROOT
    / "docs"
    / "reports"
    / "cloud_2026_04_26"
    / "goal1007_large_repeats_a5000"
    / "docs"
    / "reports"
)
MIN_PHASE_SEC_FOR_PUBLIC_REVIEW = 0.10


TARGET_ARTIFACTS: tuple[dict[str, Any], ...] = (
    {
        "app": "robot_collision_screening",
        "path_name": "prepared_pose_flags",
        "phase_key": "phases.prepared_pose_flags_warm_query_sec.median_sec",
        "artifact_files": (
            "goal1007_robot_pose_flags_large_rtx.json",
            "goal1007_robot_pose_flags_dense_obstacles_large_rtx.json",
        ),
    },
    {
        "app": "outlier_detection",
        "path_name": "prepared_fixed_radius_density_summary",
        "phase_key": "results[outlier_detection].prepared_optix_warm_query_sec.median_sec",
        "artifact_files": (
            "goal1007_outlier_dbscan_large_rtx.json",
            "goal1007_outlier_dbscan_x3_large_rtx.json",
            "goal1007_outlier_dbscan_x35_large_rtx.json",
        ),
    },
    {
        "app": "dbscan_clustering",
        "path_name": "prepared_fixed_radius_core_flags",
        "phase_key": "results[dbscan_clustering].prepared_optix_warm_query_sec.median_sec",
        "artifact_files": (
            "goal1007_outlier_dbscan_large_rtx.json",
            "goal1007_outlier_dbscan_x3_large_rtx.json",
            "goal1007_outlier_dbscan_x35_large_rtx.json",
        ),
    },
    {
        "app": "facility_knn_assignment",
        "path_name": "coverage_threshold_prepared",
        "phase_key": "scenario.timings_sec.optix_query_sec.median_sec",
        "artifact_files": (
            "goal1007_facility_service_coverage_large_rtx.json",
            "goal1007_facility_service_coverage_x3_large_rtx.json",
            "goal1007_facility_service_coverage_x4_large_rtx.json",
        ),
    },
    {
        "app": "segment_polygon_hitcount",
        "path_name": "segment_polygon_hitcount_native_experimental",
        "phase_key": "timings_sec.optix_query_sec.median_sec",
        "artifact_files": ("goal1007_segment_polygon_hitcount_large_rtx.json",),
    },
    {
        "app": "segment_polygon_anyhit_rows",
        "path_name": "segment_polygon_anyhit_rows_prepared_bounded_gate",
        "phase_key": "timings_sec.optix_query_sec.median_sec",
        "artifact_files": ("goal1007_segment_polygon_anyhit_rows_large_rtx.json",),
    },
    {
        "app": "ann_candidate_search",
        "path_name": "candidate_threshold_prepared",
        "phase_key": "scenario.timings_sec.optix_query_sec.median_sec",
        "artifact_files": (
            "goal1007_ann_candidate_coverage_large_rtx.json",
            "goal1007_ann_candidate_coverage_x3_large_rtx.json",
            "goal1007_ann_candidate_coverage_x4_large_rtx.json",
        ),
    },
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _median(value: Any) -> float | None:
    if isinstance(value, dict):
        value = value.get("median_sec")
    if isinstance(value, (int, float)) and value > 0:
        return float(value)
    return None


def _result_for_app(payload: dict[str, Any], app: str) -> dict[str, Any] | None:
    results = payload.get("results")
    if isinstance(results, list):
        for row in results:
            if isinstance(row, dict) and row.get("app") == app:
                return row
    return None


def _extract_phase(payload: dict[str, Any], app: str) -> tuple[str, float | None]:
    phases = payload.get("phases")
    if isinstance(phases, dict) and "prepared_pose_flags_warm_query_sec" in phases:
        return (
            "phases.prepared_pose_flags_warm_query_sec.median_sec",
            _median(phases.get("prepared_pose_flags_warm_query_sec")),
        )

    app_result = _result_for_app(payload, app)
    if isinstance(app_result, dict) and "prepared_optix_warm_query_sec" in app_result:
        return (
            f"results[{app}].prepared_optix_warm_query_sec.median_sec",
            _median(app_result.get("prepared_optix_warm_query_sec")),
        )

    scenario = payload.get("scenario")
    if isinstance(scenario, dict):
        timings = scenario.get("timings_sec")
        if isinstance(timings, dict) and "optix_query_sec" in timings:
            return (
                "scenario.timings_sec.optix_query_sec.median_sec",
                _median(timings.get("optix_query_sec")),
            )

    timings = payload.get("timings_sec")
    if isinstance(timings, dict) and "optix_query_sec" in timings:
        return "timings_sec.optix_query_sec.median_sec", _median(timings.get("optix_query_sec"))

    return "unavailable", None


def _source_rows(source: Path) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (row["app"], row["path_name"]): row
        for row in _load_json(source)["rows"]
    }


def _best_artifact(target: dict[str, Any], artifact_root: Path) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for filename in target["artifact_files"]:
        path = artifact_root / filename
        if not path.exists():
            candidates.append(
                {
                    "artifact_file": filename,
                    "exists": False,
                    "rtx_phase_key": "missing",
                    "rtx_phase_sec": None,
                }
            )
            continue
        payload = _load_json(path)
        phase_key, phase_sec = _extract_phase(payload, target["app"])
        candidates.append(
            {
                "artifact_file": filename,
                "exists": True,
                "rtx_phase_key": phase_key,
                "rtx_phase_sec": phase_sec,
            }
        )
    valid = [row for row in candidates if isinstance(row["rtx_phase_sec"], float)]
    chosen = max(valid, key=lambda row: row["rtx_phase_sec"]) if valid else candidates[0]
    return {"chosen": chosen, "candidates": candidates}


def build_intake(source: Path = SOURCE, artifact_root: Path = ARTIFACT_ROOT) -> dict[str, Any]:
    source_by_key = _source_rows(source)
    rows: list[dict[str, Any]] = []
    for target in TARGET_ARTIFACTS:
        key = (target["app"], target["path_name"])
        source_row = source_by_key[key]
        artifact = _best_artifact(target, artifact_root)
        phase = artifact["chosen"]["rtx_phase_sec"]
        floor_cleared = isinstance(phase, float) and phase >= MIN_PHASE_SEC_FOR_PUBLIC_REVIEW
        rows.append(
            {
                "app": target["app"],
                "path_name": target["path_name"],
                "goal1006_status": source_row["public_wording_status"],
                "goal1006_ratio": source_row.get("fastest_ratio_baseline_over_rtx"),
                "goal1006_fastest_baseline": source_row.get("fastest_baseline"),
                "chosen_artifact": artifact["chosen"]["artifact_file"],
                "rtx_phase_key": artifact["chosen"]["rtx_phase_key"],
                "rtx_phase_sec": phase,
                "all_artifact_phases": artifact["candidates"],
                "large_repeat_status": (
                    "timing_floor_cleared_for_separate_2ai_public_wording_review"
                    if floor_cleared
                    else "still_below_public_review_timing_floor"
                ),
                "public_speedup_claim_authorized": False,
                "reason": (
                    "Large-repeat RTX median query phase is at least 100 ms. This repairs the "
                    "Goal1006 short-phase concern only; public wording still needs separate 2-AI review "
                    "and must remain query-phase scoped."
                    if floor_cleared
                    else "Large-repeat RTX median query phase is still below 100 ms, so this row remains held."
                ),
            }
        )

    counts: dict[str, int] = {}
    for row in rows:
        status = row["large_repeat_status"]
        counts[status] = counts.get(status, 0) + 1

    return {
        "goal": GOAL,
        "date": DATE,
        "source": str(source.relative_to(ROOT)),
        "artifact_root": str(artifact_root.relative_to(ROOT)),
        "row_count": len(rows),
        "status_counts": counts,
        "timing_floor_cleared_count": counts.get(
            "timing_floor_cleared_for_separate_2ai_public_wording_review", 0
        ),
        "still_held_count": counts.get("still_below_public_review_timing_floor", 0),
        "public_speedup_claim_authorized_count": 0,
        "min_phase_sec_for_public_review": MIN_PHASE_SEC_FOR_PUBLIC_REVIEW,
        "rows": rows,
        "boundary": (
            "Goal1008 is an artifact-intake gate for Goal1007 RTX A5000 larger repeats. "
            "It can clear the 100 ms timing-floor concern for separate public-wording review, "
            "but it does not authorize any public speedup claim."
        ),
    }


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    if value is None:
        return ""
    return str(value)


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1008 Large-Repeat RTX Artifact Intake",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- rows audited: `{payload['row_count']}`",
        f"- timing-floor-cleared rows: `{payload['timing_floor_cleared_count']}`",
        f"- still-held rows: `{payload['still_held_count']}`",
        f"- public speedup claims authorized here: `{payload['public_speedup_claim_authorized_count']}`",
        f"- minimum phase duration for public-wording review: `{payload['min_phase_sec_for_public_review']}` s",
        f"- status counts: `{payload['status_counts']}`",
        "",
        "## Decisions",
        "",
        "| App | Path | Chosen artifact | RTX phase (s) | Goal1006 ratio | Status |",
        "|---|---|---|---:|---:|---|",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{row['chosen_artifact']}` | "
            f"{_fmt(row['rtx_phase_sec'])} | {_fmt(row['goal1006_ratio'])} | "
            f"`{row['large_repeat_status']}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- A cleared timing floor means the row is eligible for separate 2-AI public-wording review.",
            "- It does not authorize front-page or release-note speedup wording by itself.",
            "- The wording remains limited to prepared RTX query/native sub-paths, not whole-app speedups.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Intake Goal1007 larger-scale RTX repeat artifacts.")
    parser.add_argument("--source", default=str(SOURCE))
    parser.add_argument("--artifact-root", default=str(ARTIFACT_ROOT))
    parser.add_argument("--output-json", default="docs/reports/goal1008_large_repeat_artifact_intake_2026-04-26.json")
    parser.add_argument("--output-md", default="docs/reports/goal1008_large_repeat_artifact_intake_2026-04-26.md")
    args = parser.parse_args()
    payload = build_intake(Path(args.source), Path(args.artifact_root))
    Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = to_markdown(payload)
    Path(args.output_md).write_text(md + "\n", encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

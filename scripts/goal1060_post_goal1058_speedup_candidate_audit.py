#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from scripts.goal1005_post_a5000_speedup_candidate_audit import (
    _baseline_index,
    _classify,
    _rtx_phase_seconds,
)
from scripts.goal978_rtx_speedup_claim_candidate_audit import _baseline_rows


DATE = "2026-04-28"
GOAL = "Goal1060 post-Goal1058 speedup candidate audit"
DEFAULT_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal1052_post_goal1048_cloud_batch"

ARTIFACT_ROWS = [
    ("facility_knn_assignment", "coverage_threshold_prepared", "coverage_threshold_prepared.json"),
    ("robot_collision_screening", "prepared_pose_flags", "prepared_pose_flags.json"),
    ("database_analytics", "prepared_db_session_sales_risk", "prepared_db_session_sales_risk.json"),
    ("database_analytics", "prepared_db_session_regional_dashboard", "prepared_db_session_regional_dashboard.json"),
    ("graph_analytics", "graph_visibility_edges_gate", "graph_visibility_edges_gate.json"),
    ("event_hotspot_screening", "prepared_count_summary", "prepared_count_summary.json"),
    ("road_hazard_screening", "road_hazard_native_summary_gate", "road_hazard_native_summary_gate.json"),
    (
        "polygon_pair_overlap_area_rows",
        "polygon_pair_overlap_optix_native_assisted_phase_gate",
        "polygon_pair_overlap_optix_native_assisted_phase_gate.json",
    ),
    (
        "polygon_set_jaccard",
        "polygon_set_jaccard_optix_native_assisted_phase_gate",
        "polygon_set_jaccard_optix_native_assisted_phase_gate.json",
    ),
    ("hausdorff_distance", "directed_threshold_prepared", "directed_threshold_prepared.json"),
    ("barnes_hut_force_app", "node_coverage_prepared", "node_coverage_prepared.json"),
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_ok(app: str, artifact: dict[str, Any]) -> tuple[bool, str]:
    if app == "facility_knn_assignment":
        result = (artifact.get("scenario") or {}).get("result") or {}
        return result.get("matches_oracle") is True, "facility oracle parity"
    if app == "robot_collision_screening":
        return (
            artifact.get("validated") is True and artifact.get("matches_oracle") is True,
            "robot validation and oracle parity",
        )
    if app == "database_analytics":
        results = artifact.get("results") or []
        return bool(results) and all(row.get("status") == "ok" for row in results), "DB compact-summary status ok"
    if app == "graph_analytics":
        return artifact.get("status") == "pass" and artifact.get("strict_pass") is True, "graph strict pass"
    if app == "event_hotspot_screening":
        scenario = artifact.get("scenario") or {}
        timings = scenario.get("timings_sec") or {}
        return scenario.get("mode") == "optix" and timings.get("optix_query", 0) > 0, "event OptiX count-summary artifact"
    if app in {"road_hazard_screening", "polygon_pair_overlap_area_rows", "polygon_set_jaccard"}:
        return artifact.get("status") == "pass", "native-assisted gate pass"
    if app in {"hausdorff_distance", "barnes_hut_force_app"}:
        result = (artifact.get("scenario") or {}).get("result") or {}
        return result.get("matches_oracle") is True, "prepared decision oracle parity"
    return False, "unknown artifact contract"


def build_audit(artifact_dir: Path = DEFAULT_ARTIFACT_DIR) -> dict[str, Any]:
    baseline_by_key = _baseline_index()
    rows: list[dict[str, Any]] = []

    for app, path_name, file_name in ARTIFACT_ROWS:
        artifact_path = artifact_dir / file_name
        artifact = _load(artifact_path)
        artifact_ok, artifact_reason = _artifact_ok(app, artifact)
        rtx_phase_key, rtx_sec = _rtx_phase_seconds(app, path_name, artifact)
        baseline_row = baseline_by_key[(app, path_name)]
        baselines = _baseline_rows(baseline_row)
        decision = _classify(
            rtx_sec,
            bool(baseline_row.get("baseline_complete_for_speedup_review")),
            "ok" if artifact_ok else "blocked",
            baselines,
        )
        public_wording = rt.rtx_public_wording_status(app)
        rows.append(
            {
                "app": app,
                "path_name": path_name,
                "artifact": str(artifact_path.relative_to(ROOT)),
                "artifact_ok": artifact_ok,
                "artifact_reason": artifact_reason,
                "rtx_phase_key": rtx_phase_key,
                "rtx_native_or_query_phase_sec": rtx_sec,
                "baseline_status": baseline_row.get("baseline_status"),
                "baseline_complete_for_speedup_review": baseline_row.get(
                    "baseline_complete_for_speedup_review"
                ),
                "recommendation": decision["recommendation"],
                "reason": decision["reason"],
                "fastest_baseline": decision["fastest_baseline"],
                "fastest_baseline_sec": decision["fastest_baseline_sec"],
                "fastest_ratio_baseline_over_rtx": decision["fastest_ratio_baseline_over_rtx"],
                "warnings": decision["warnings"],
                "current_public_wording_status": public_wording.status,
                "current_public_wording_boundary": public_wording.boundary,
                "public_speedup_claim_authorized": False,
                "timed_non_optix_baselines": [
                    item for item in baselines if item["phase_sec"] is not None
                ],
                "untimed_non_optix_baselines": [
                    item for item in baselines if item["phase_sec"] is None
                ],
            }
        )

    counts: dict[str, int] = {}
    for row in rows:
        recommendation = str(row["recommendation"])
        counts[recommendation] = counts.get(recommendation, 0) + 1
    return {
        "goal": GOAL,
        "date": DATE,
        "artifact_dir": str(artifact_dir.relative_to(ROOT)),
        "row_count": len(rows),
        "recommendation_counts": counts,
        "candidate_count": counts.get("candidate_for_separate_2ai_public_claim_review", 0),
        "public_speedup_claim_authorized_count": 0,
        "rows": rows,
        "valid": len(rows) == len(ARTIFACT_ROWS) and all(row["artifact_ok"] for row in rows),
        "boundary": (
            "Goal1060 compares accepted Goal1058 RTX A5000 artifact phases against existing "
            "same-semantics baselines. It does not authorize public speedup wording; candidate "
            "rows still require separate 2-AI public wording review."
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
        "# Goal1060 Post-Goal1058 Speedup Candidate Audit",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- valid: `{payload['valid']}`",
        f"- rows audited: `{payload['row_count']}`",
        f"- candidate rows for later 2-AI public wording review: `{payload['candidate_count']}`",
        f"- public speedup claims authorized here: `{payload['public_speedup_claim_authorized_count']}`",
        f"- recommendation counts: `{payload['recommendation_counts']}`",
        "",
        "## Decisions",
        "",
        "| App | Path | RTX phase key | RTX phase (s) | Fastest baseline | Ratio | Recommendation | Current public wording |",
        "| --- | --- | --- | ---: | --- | ---: | --- | --- |",
    ]
    for row in payload["rows"]:
        baseline = ""
        if row["fastest_baseline"]:
            baseline = f"`{row['fastest_baseline']}` {_fmt(row['fastest_baseline_sec'])}"
        lines.append(
            "| "
            f"`{row['app']}` | "
            f"`{row['path_name']}` | "
            f"`{row['rtx_phase_key']}` | "
            f"{_fmt(row['rtx_native_or_query_phase_sec'])} | "
            f"{baseline} | "
            f"{_fmt(row['fastest_ratio_baseline_over_rtx'])} | "
            f"`{row['recommendation']}` | "
            f"`{row['current_public_wording_status']}` |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Goal1058 RTX artifacts against baselines.")
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument(
        "--output-json",
        default="docs/reports/goal1060_post_goal1058_speedup_candidate_audit_2026-04-28.json",
    )
    parser.add_argument(
        "--output-md",
        default="docs/reports/goal1060_post_goal1058_speedup_candidate_audit_2026-04-28.md",
    )
    args = parser.parse_args()
    payload = build_audit(args.artifact_dir)
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps({"json": str(output_json), "md": str(output_md), "valid": payload["valid"]}))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

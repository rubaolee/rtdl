#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-26"


def _cmd(*parts: str) -> list[str]:
    return ["python3", *parts]


ENTRIES: list[dict[str, Any]] = [
    {
        "app": "robot_collision_screening",
        "rtx_path": "prepared_pose_flags",
        "local_status": "baseline_partial",
        "reason": "CPU and Embree app paths exist, but exact prepared-pose semantics need phase extraction.",
        "commands": [
            _cmd("examples/rtdl_robot_collision_screening_app.py", "--backend", "cpu", "--output-mode", "pose_flags", "--pose-count", "200000", "--obstacle-count", "1024"),
            _cmd("examples/rtdl_robot_collision_screening_app.py", "--backend", "embree", "--output-mode", "pose_flags", "--pose-count", "200000", "--obstacle-count", "1024"),
        ],
    },
    {
        "app": "outlier_detection",
        "rtx_path": "prepared_fixed_radius_density_summary",
        "local_status": "baseline_ready",
        "reason": "CPU, Embree prepared threshold, and real SciPy cKDTree threshold-count paths are exposed; SciPy remains an optional dependency and is available locally through the project venv used by Goal1034+.",
        "commands": [
            _cmd("examples/rtdl_outlier_detection_app.py", "--backend", "cpu", "--copies", "20000", "--output-mode", "density_count"),
            _cmd("examples/rtdl_outlier_detection_app.py", "--backend", "embree", "--copies", "20000", "--output-mode", "density_count", "--embree-summary-mode", "rt_count_threshold_prepared"),
            _cmd("examples/rtdl_outlier_detection_app.py", "--backend", "scipy", "--copies", "20000", "--output-mode", "density_count"),
        ],
    },
    {
        "app": "dbscan_clustering",
        "rtx_path": "prepared_fixed_radius_core_flags",
        "local_status": "baseline_ready",
        "reason": "CPU, Embree prepared core-count, and real SciPy cKDTree threshold-count paths are exposed; SciPy remains an optional dependency and is available locally through the project venv used by Goal1034+.",
        "commands": [
            _cmd("examples/rtdl_dbscan_clustering_app.py", "--backend", "cpu", "--copies", "20000", "--output-mode", "core_count"),
            _cmd("examples/rtdl_dbscan_clustering_app.py", "--backend", "embree", "--copies", "20000", "--output-mode", "core_count", "--embree-summary-mode", "rt_core_flags_prepared"),
            _cmd("examples/rtdl_dbscan_clustering_app.py", "--backend", "scipy", "--copies", "20000", "--output-mode", "core_count"),
        ],
    },
    {
        "app": "database_analytics:sales_risk",
        "rtx_path": "prepared_db_session_sales_risk",
        "local_status": "baseline_partial",
        "reason": "CPU and Embree compact summaries are local; PostgreSQL indexed baseline is Linux/PostgreSQL-gated.",
        "commands": [
            _cmd("scripts/goal756_db_prepared_session_perf.py", "--backend", "cpu", "--scenario", "sales_risk", "--copies", "20000", "--iterations", "10", "--output-mode", "compact_summary", "--strict"),
            _cmd("scripts/goal756_db_prepared_session_perf.py", "--backend", "embree", "--scenario", "sales_risk", "--copies", "20000", "--iterations", "10", "--output-mode", "compact_summary", "--strict"),
        ],
    },
    {
        "app": "database_analytics:regional_dashboard",
        "rtx_path": "prepared_db_session_regional_dashboard",
        "local_status": "baseline_partial",
        "reason": "CPU and Embree compact summaries are local; PostgreSQL indexed baseline is Linux/PostgreSQL-gated.",
        "commands": [
            _cmd("scripts/goal756_db_prepared_session_perf.py", "--backend", "cpu", "--scenario", "regional_dashboard", "--copies", "20000", "--iterations", "10", "--output-mode", "compact_summary", "--strict"),
            _cmd("scripts/goal756_db_prepared_session_perf.py", "--backend", "embree", "--scenario", "regional_dashboard", "--copies", "20000", "--iterations", "10", "--output-mode", "compact_summary", "--strict"),
        ],
    },
    {
        "app": "service_coverage_gaps",
        "rtx_path": "prepared_gap_summary",
        "local_status": "baseline_ready",
        "reason": "CPU, Embree summary, and SciPy paths are exposed by the app CLI; SciPy remains an optional dependency and is available locally through the project venv used by Goal1034+.",
        "commands": [
            _cmd("examples/rtdl_service_coverage_gaps.py", "--backend", "cpu", "--copies", "20000"),
            _cmd("examples/rtdl_service_coverage_gaps.py", "--backend", "embree", "--copies", "20000", "--embree-summary-mode", "gap_summary"),
            _cmd("examples/rtdl_service_coverage_gaps.py", "--backend", "scipy", "--copies", "20000"),
        ],
    },
    {
        "app": "event_hotspot_screening",
        "rtx_path": "prepared_count_summary",
        "local_status": "baseline_ready",
        "reason": "CPU, Embree summary, and SciPy paths are exposed by the app CLI; SciPy remains an optional dependency and is available locally through the project venv used by Goal1034+.",
        "commands": [
            _cmd("examples/rtdl_event_hotspot_screening.py", "--backend", "cpu", "--copies", "20000"),
            _cmd("examples/rtdl_event_hotspot_screening.py", "--backend", "embree", "--copies", "20000", "--embree-summary-mode", "count_summary"),
            _cmd("examples/rtdl_event_hotspot_screening.py", "--backend", "scipy", "--copies", "20000"),
        ],
    },
    {
        "app": "facility_knn_assignment",
        "rtx_path": "coverage_threshold_prepared",
        "local_status": "baseline_partial",
        "reason": "CPU/Embree/SciPy app paths exist, but coverage-threshold phase parity needs a dedicated extractor.",
        "commands": [
            _cmd("examples/rtdl_facility_knn_assignment.py", "--backend", "cpu", "--copies", "20000", "--output-mode", "summary"),
            _cmd("examples/rtdl_facility_knn_assignment.py", "--backend", "embree", "--copies", "20000", "--output-mode", "summary"),
            _cmd("examples/rtdl_facility_knn_assignment.py", "--backend", "scipy", "--copies", "20000", "--output-mode", "summary"),
        ],
    },
    {
        "app": "road_hazard_screening",
        "rtx_path": "road_hazard_native_summary_gate",
        "local_status": "baseline_partial",
        "reason": "CPU and Embree compact summaries are local; PostGIS same-semantics baseline is Linux/PostGIS-gated.",
        "commands": [
            _cmd("examples/rtdl_road_hazard_screening.py", "--backend", "cpu", "--copies", "20000", "--output-mode", "summary"),
            _cmd("examples/rtdl_road_hazard_screening.py", "--backend", "embree", "--copies", "20000", "--output-mode", "summary"),
        ],
    },
    {
        "app": "segment_polygon_hitcount",
        "rtx_path": "segment_polygon_hitcount_native_experimental",
        "local_status": "baseline_partial",
        "reason": "CPU and Embree hit-count paths are local; PostGIS same-semantics baseline is Linux/PostGIS-gated.",
        "commands": [
            _cmd("examples/rtdl_segment_polygon_hitcount.py", "--backend", "cpu", "--copies", "256"),
            _cmd("examples/rtdl_segment_polygon_hitcount.py", "--backend", "embree", "--copies", "256"),
        ],
    },
    {
        "app": "segment_polygon_anyhit_rows",
        "rtx_path": "segment_polygon_anyhit_rows_prepared_bounded_gate",
        "local_status": "baseline_partial",
        "reason": "CPU and Embree compact outputs are local; bounded pair-row capacity and PostGIS parity need Linux review.",
        "commands": [
            _cmd("examples/rtdl_segment_polygon_anyhit_rows.py", "--backend", "cpu", "--copies", "256", "--output-mode", "rows", "--output-capacity", "4096"),
            _cmd("examples/rtdl_segment_polygon_anyhit_rows.py", "--backend", "embree", "--copies", "256", "--output-mode", "rows", "--output-capacity", "4096"),
        ],
    },
    {
        "app": "graph_analytics",
        "rtx_path": "graph_visibility_edges_gate",
        "local_status": "baseline_partial",
        "reason": "CPU and Embree graph paths are local when GEOS/native oracle dependencies are present; visibility/BFS/triangle claims must stay separated.",
        "commands": [
            _cmd("examples/rtdl_graph_analytics_app.py", "--backend", "cpu", "--scenario", "visibility_edges", "--copies", "20000", "--output-mode", "summary"),
            _cmd("examples/rtdl_graph_analytics_app.py", "--backend", "embree", "--scenario", "visibility_edges", "--copies", "20000", "--output-mode", "summary"),
            _cmd("examples/rtdl_graph_analytics_app.py", "--backend", "embree", "--scenario", "bfs", "--copies", "20000", "--output-mode", "summary"),
            _cmd("examples/rtdl_graph_analytics_app.py", "--backend", "embree", "--scenario", "triangle_count", "--copies", "20000", "--output-mode", "summary"),
        ],
    },
    {
        "app": "hausdorff_distance",
        "rtx_path": "directed_threshold_prepared",
        "local_status": "baseline_partial",
        "reason": "CPU and Embree exact summaries exist, but threshold-decision parity needs dedicated extraction.",
        "commands": [
            _cmd("examples/rtdl_hausdorff_distance_app.py", "--backend", "cpu", "--copies", "20000", "--embree-result-mode", "directed_summary"),
            _cmd("examples/rtdl_hausdorff_distance_app.py", "--backend", "embree", "--copies", "20000", "--embree-result-mode", "directed_summary"),
        ],
    },
    {
        "app": "ann_candidate_search",
        "rtx_path": "candidate_threshold_prepared",
        "local_status": "baseline_partial",
        "reason": "CPU/Embree/SciPy app summaries exist, but candidate-threshold parity needs dedicated extraction.",
        "commands": [
            _cmd("examples/rtdl_ann_candidate_app.py", "--backend", "cpu", "--copies", "20000", "--output-mode", "quality_summary"),
            _cmd("examples/rtdl_ann_candidate_app.py", "--backend", "embree", "--copies", "20000", "--output-mode", "quality_summary"),
            _cmd("examples/rtdl_ann_candidate_app.py", "--backend", "scipy", "--copies", "20000", "--output-mode", "quality_summary"),
        ],
    },
    {
        "app": "barnes_hut_force_app",
        "rtx_path": "node_coverage_prepared",
        "local_status": "baseline_partial",
        "reason": "CPU/Embree candidate summaries exist, but node-coverage threshold parity needs dedicated extraction.",
        "commands": [
            _cmd("examples/rtdl_barnes_hut_force_app.py", "--backend", "cpu", "--body-count", "200000", "--output-mode", "candidate_summary"),
            _cmd("examples/rtdl_barnes_hut_force_app.py", "--backend", "embree", "--body-count", "200000", "--output-mode", "candidate_summary"),
        ],
    },
    {
        "app": "polygon_pair_overlap_area_rows",
        "rtx_path": "polygon_pair_overlap_optix_native_assisted_phase_gate",
        "local_status": "baseline_partial",
        "reason": "CPU and Embree summary paths are local; PostGIS same-semantics unit-cell baseline is Linux/PostGIS-gated.",
        "commands": [
            _cmd("examples/rtdl_polygon_pair_overlap_area_rows.py", "--backend", "cpu", "--copies", "20000", "--output-mode", "summary"),
            _cmd("examples/rtdl_polygon_pair_overlap_area_rows.py", "--backend", "embree", "--copies", "20000", "--output-mode", "summary"),
        ],
    },
    {
        "app": "polygon_set_jaccard",
        "rtx_path": "polygon_set_jaccard_optix_native_assisted_phase_gate",
        "local_status": "baseline_partial",
        "reason": "CPU and Embree paths are local; PostGIS same-semantics unit-cell baseline is Linux/PostGIS-gated.",
        "commands": [
            _cmd("examples/rtdl_polygon_set_jaccard.py", "--backend", "cpu", "--copies", "20000"),
            _cmd("examples/rtdl_polygon_set_jaccard.py", "--backend", "embree", "--copies", "20000"),
        ],
    },
]


def build_manifest() -> dict[str, Any]:
    counts: dict[str, int] = {}
    for entry in ENTRIES:
        counts[entry["local_status"]] = counts.get(entry["local_status"], 0) + 1
    return {
        "goal": "Goal1030 local RTX baseline manifest",
        "date": DATE,
        "entry_count": len(ENTRIES),
        "status_counts": counts,
        "entries": ENTRIES,
        "boundary": (
            "This is a local baseline command manifest. It does not execute benchmarks, "
            "does not authorize speedup claims, and does not replace same-semantics review."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1030 Local RTX Baseline Manifest",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- entries: `{payload['entry_count']}`",
        f"- status_counts: `{payload['status_counts']}`",
        "",
        "## Matrix",
        "",
        "| App | RTX Path | Local Status | Command Count | Reason |",
        "|---|---|---|---:|---|",
    ]
    for entry in payload["entries"]:
        lines.append(
            f"| `{entry['app']}` | `{entry['rtx_path']}` | `{entry['local_status']}` | "
            f"{len(entry['commands'])} | {entry['reason']} |"
        )
    lines.extend(["", "## Commands", ""])
    for entry in payload["entries"]:
        lines.append(f"### `{entry['app']}`")
        lines.append("")
        for command in entry["commands"]:
            lines.append("```bash")
            lines.append("PYTHONPATH=src:. " + " ".join(command))
            lines.append("```")
            lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Write the Goal1030 local baseline command manifest.")
    parser.add_argument("--output-json", default="docs/reports/goal1030_local_baseline_manifest_2026-04-26.json")
    parser.add_argument("--output-md", default="docs/reports/goal1030_local_baseline_manifest_2026-04-26.md")
    args = parser.parse_args()
    payload = build_manifest()
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    (ROOT / args.output_md).write_text(markdown + "\n", encoding="utf-8")
    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

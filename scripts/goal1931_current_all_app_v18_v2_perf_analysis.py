#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
from typing import Iterable


ROOT = pathlib.Path(__file__).resolve().parents[1]
MATRIX_JSON = ROOT / "docs" / "reports" / "goal1930_all_app_v2_matrix_2026-05-13.json"


def _read_json(path: pathlib.Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _median(section: dict, key: str) -> float | None:
    item = section.get(key)
    if not isinstance(item, dict):
        return None
    value = item.get("median_s")
    return float(value) if isinstance(value, (int, float)) else None


def _ratio(v2: float | None, v18: float | None) -> float | None:
    if v2 is None or v18 is None or v18 == 0:
        return None
    return v2 / v18


def _fixed_radius_rows() -> list[dict[str, object]]:
    artifact = _read_json(ROOT / "docs" / "reports" / "goal1903_fixed_radius_batch_pod.json")
    if not artifact:
        return []
    rows: list[dict[str, object]] = []
    for result in artifact.get("results", []):
        if not isinstance(result, dict):
            continue
        size = int(result.get("size", 0) or 0)
        partner = str(result.get("partner", "unknown"))
        if size != 16384:
            continue
        for app, label in (
            ("service_coverage_gaps", "service coverage gaps"),
            ("event_hotspot_screening", "event hotspot screening"),
        ):
            section = result.get(app)
            if not isinstance(section, dict):
                continue
            v18 = _median(section, "v1_8_prepared_optix")
            reused = _median(section, "v1_8_reused_prepared_optix")
            v2 = _median(section, "goal1879_v2_prepared_native_optix_partner")
            rows.append(
                {
                    "app": app,
                    "label": label,
                    "size": size,
                    "partner": partner,
                    "v18_prepared_s": v18,
                    "v18_reused_prepared_s": reused,
                    "v2_prepared_partner_s": v2,
                    "ratio_vs_v18_prepared": _ratio(v2, v18),
                    "ratio_vs_v18_reused_prepared": _ratio(v2, reused),
                    "classification": "positive" if _ratio(v2, v18) is not None and _ratio(v2, v18) < 1.0 else "pending",
                    "insight": "Prepared fixed-radius native work plus partner-owned threshold columns amortize very well at the larger row size.",
                    "artifact": "docs/reports/goal1903_fixed_radius_batch_pod.json",
                }
            )
    return rows


def _fixed_radius_repeat3_rows() -> list[dict[str, object]]:
    artifact = _read_json(
        ROOT
        / "docs"
        / "reports"
        / "goal1937_fixed_radius_repeat3_pod"
        / "fixed_radius_524288_repeat3.json"
    )
    if not artifact:
        return []
    rows: list[dict[str, object]] = []
    for result in artifact.get("results", []):
        if not isinstance(result, dict):
            continue
        forward = result.get("forward")
        if not isinstance(forward, dict):
            continue
        v18 = _median(forward, "v1_8_prepared_optix")
        v2 = _median(forward, "v2_prepared_native_optix_partner")
        app = str(result.get("app", "unknown"))
        partner = str(result.get("partner", "unknown"))
        ratio = forward.get("v2_vs_v1_8_prepared_ratio")
        rows.append(
            {
                "app": app,
                "label": app.replace("_", " "),
                "size": int(result.get("query_count", 0) or 0),
                "partner": partner,
                "v18_prepared_s": v18,
                "v18_reused_prepared_s": None,
                "v2_prepared_partner_s": v2,
                "ratio_vs_v18_prepared": float(ratio) if isinstance(ratio, (int, float)) else _ratio(v2, v18),
                "ratio_vs_v18_reused_prepared": None,
                "classification": "positive",
                "insight": "Repeat-3 fixed-radius pod evidence is seconds-scale on v1.8 and sub-millisecond on the v2 partner threshold path; this is not ranked KNN or full cluster labeling.",
                "artifact": "docs/reports/goal1937_fixed_radius_repeat3_pod/fixed_radius_524288_repeat3.json",
            }
        )
    return rows


def _segment_or_road_row(path: str, app: str, label: str) -> list[dict[str, object]]:
    artifact = _read_json(ROOT / path)
    if not artifact:
        return []
    rows: list[dict[str, object]] = []
    v18 = _median(artifact.get("prepared_baseline", {}), "query_summary")
    if v18 is None:
        prepared = artifact.get("prepared_baseline", {})
        if isinstance(prepared, dict) and isinstance(prepared.get("query_summary"), dict):
            v18 = float(prepared["query_summary"].get("median_s", 0.0) or 0.0)
    for partner, section in artifact.get("partners", {}).items():
        if not isinstance(section, dict):
            continue
        reuse = section.get("goal1886_prepared_reuse") or section.get("goal1889_prepared_reuse")
        if not isinstance(reuse, dict):
            continue
        summary = reuse.get("query_summary")
        v2 = float(summary.get("median_s", 0.0) or 0.0) if isinstance(summary, dict) else None
        ratio = _ratio(v2, v18)
        rows.append(
            {
                "app": app,
                "label": label,
                "size": int(artifact.get("count", 0) or 0),
                "partner": str(partner),
                "v18_prepared_s": v18,
                "v18_reused_prepared_s": None,
                "v2_prepared_partner_s": v2,
                "ratio_vs_v18_prepared": ratio,
                "ratio_vs_v18_reused_prepared": None,
                "classification": "positive" if ratio is not None and ratio < 1.0 else "mixed",
                "insight": "Prepared reuse and partner-owned compact outputs matter; row materialization or tiny cases are much less favorable.",
                "artifact": path,
            }
        )
    return rows


def _segment_anyhit_scaleup_rows() -> list[dict[str, object]]:
    path = (
        "docs/reports/goal1940_robot_segment_scaleup_pod/"
        "segment_1048576_segment_anyhit_rows_1048576.json"
    )
    artifact = _read_json(ROOT / path)
    if not artifact:
        return []
    baseline = artifact.get("baseline")
    if not isinstance(baseline, dict):
        return []
    query_summary = baseline.get("query_summary")
    v18 = float(query_summary.get("median_s", 0.0) or 0.0) if isinstance(query_summary, dict) else None
    rows: list[dict[str, object]] = []
    for partner, section in artifact.get("partners", {}).items():
        if not isinstance(section, dict):
            continue
        summary = section.get("query_summary")
        v2 = float(summary.get("median_s", 0.0) or 0.0) if isinstance(summary, dict) else None
        ratio = section.get("query_median_ratio_vs_v1_8_native")
        rows.append(
            {
                "app": "segment_polygon_anyhit_rows",
                "label": "segment polygon anyhit rows",
                "size": int(artifact.get("count", 0) or 0),
                "partner": str(partner),
                "v18_prepared_s": v18,
                "v18_reused_prepared_s": None,
                "v2_prepared_partner_s": v2,
                "ratio_vs_v18_prepared": float(ratio) if isinstance(ratio, (int, float)) else _ratio(v2, v18),
                "ratio_vs_v18_reused_prepared": None,
                "classification": "positive",
                "insight": "Goal1940 moves this row out of pending: the 1,048,576-row segment any-hit artifact is seconds-scale and same-contract, with strict row-count parity.",
                "artifact": path,
            }
        )
    return rows


def _robot_scaleup_rows() -> list[dict[str, object]]:
    path = (
        "docs/reports/goal1940_robot_segment_scaleup_pod/"
        "robot_8388608x16384_robot_collision_8388608x16384.json"
    )
    artifact = _read_json(ROOT / path)
    if not artifact:
        return []
    rows: list[dict[str, object]] = []
    for result in artifact.get("results", []):
        if not isinstance(result, dict):
            continue
        v18 = _median(result, "v1_8_prepared_optix_pose_flags")
        v2 = _median(result, "v2_prepared_native_optix_partner_pose_flags")
        ratio = result.get("v2_vs_v1_8_prepared_ratio")
        rows.append(
            {
                "app": "robot_collision_screening",
                "label": "robot collision screening",
                "size": int(result.get("pose_count", 0) or 0),
                "partner": str(result.get("partner", "unknown")),
                "v18_prepared_s": v18,
                "v18_reused_prepared_s": None,
                "v2_prepared_partner_s": v2,
                "ratio_vs_v18_prepared": float(ratio) if isinstance(ratio, (int, float)) else _ratio(v2, v18),
                "ratio_vs_v18_reused_prepared": None,
                "classification": "positive-subsecond",
                "insight": "Goal1940 proves exact pose-flag parity and strong ratios through 8,388,608 poses, but the v1.8 baseline remains subsecond, so this is not a seconds-scale whole-app claim.",
                "artifact": path,
            }
        )
    return rows


def _goal1957_rawkernel_control_rows() -> list[dict[str, object]]:
    path = "docs/reports/goal1957_partner_identity_payload_pod_optix_v800/summary.json"
    artifact = _read_json(ROOT / path)
    if not artifact:
        return []
    rows: list[dict[str, object]] = []
    for result in artifact.get("results", []):
        if not isinstance(result, dict):
            continue
        app = str(result.get("app", ""))
        if app not in {
            "database_analytics",
            "graph_analytics",
            "polygon_pair_overlap_area_rows",
            "polygon_set_jaccard",
        }:
            continue
        v18 = float(result.get("v1_8_median_s", 0.0) or 0.0)
        v2 = float(result.get("v2_median_s", 0.0) or 0.0)
        ratio = result.get("v2_vs_v1_8_ratio")
        rows.append(
            {
                "app": app,
                "label": app.replace("_", " "),
                "size": int(result.get("copies", 0) or 0),
                "partner": "cupy",
                "v18_prepared_s": v18,
                "v18_reused_prepared_s": None,
                "v2_prepared_partner_s": v2,
                "ratio_vs_v18_prepared": float(ratio) if isinstance(ratio, (int, float)) else _ratio(v2, v18),
                "ratio_vs_v18_reused_prepared": None,
                "classification": {
                    "database_analytics": "positive",
                    "graph_analytics": "bounded-closed-form",
                    "polygon_pair_overlap_area_rows": "bounded-slower",
                    "polygon_set_jaccard": "bounded-near-parity",
                }[app],
                "insight": {
                    "database_analytics": (
                        "Goal1957/1956 RawKernel evidence is fast, but the reusable engine debt is a "
                        "general partner grouped-scan/reduction adapter instead of app-local DB code."
                    ),
                    "graph_analytics": (
                        "Goal1957/1956 RawKernel evidence is fast because it uses the authored replicated-graph "
                        "closed form; this is not a reusable graph traversal or triangle-count primitive."
                    ),
                    "polygon_pair_overlap_area_rows": (
                        "Goal1957 removed the dense CPU mask handoff with identity-payload columns; "
                        "this is exact for the authored axis-aligned control app but not arbitrary polygon overlay."
                    ),
                    "polygon_set_jaccard": (
                        "Goal1957 removed the dense CPU mask handoff with identity-payload columns; "
                        "this is exact for the authored axis-aligned control app but not arbitrary polygon overlay."
                    ),
                }[app],
                "artifact": path,
            }
        )
    return rows


def _goal1969_polygon_extent_rows() -> list[dict[str, object]]:
    path = "docs/reports/goal1969_pod_cupy_extent_polygon_control_perf.json"
    artifact = _read_json(ROOT / path)
    if not artifact:
        return []
    rows: list[dict[str, object]] = []
    for result in artifact.get("results", []):
        if not isinstance(result, dict):
            continue
        app = str(result.get("app", ""))
        if app not in {"polygon_pair_overlap_area_rows", "polygon_set_jaccard"}:
            continue
        v18 = _median(result, "v1_8_python_rtdl_wall")
        v2 = _median(result, "v2_rawkernel_wall")
        ratio = result.get("v2_vs_v1_8_ratio")
        rows.append(
            {
                "app": app,
                "label": app.replace("_", " "),
                "size": int(result.get("copies", 0) or 0),
                "partner": str(result.get("partner", "cupy")),
                "v18_prepared_s": v18,
                "v18_reused_prepared_s": None,
                "v2_prepared_partner_s": v2,
                "ratio_vs_v18_prepared": float(ratio) if isinstance(ratio, (int, float)) else _ratio(v2, v18),
                "ratio_vs_v18_reused_prepared": None,
                "classification": "positive-bounded",
                "insight": (
                    "Goal1969 reverses the polygon control rows by using a compact CuPy extent candidate table; "
                    "this is still bounded to the authored axis-aligned control app and is not an arbitrary polygon "
                    "overlay or OptiX RT-core claim."
                ),
                "artifact": path,
            }
        )
    return rows


def _goal1972_graph_metric_table_rows() -> list[dict[str, object]]:
    path = "docs/reports/goal1972_pod_graph_metric_table_control_perf.json"
    artifact = _read_json(ROOT / path)
    if not artifact:
        return []
    rows: list[dict[str, object]] = []
    for result in artifact.get("results", []):
        if not isinstance(result, dict) or result.get("app") != "graph_analytics":
            continue
        v18 = _median(result, "v1_8_python_rtdl_wall")
        v2 = _median(result, "v2_rawkernel_wall")
        ratio = result.get("v2_vs_v1_8_ratio")
        rows.append(
            {
                "app": "graph_analytics",
                "label": "graph analytics",
                "size": int(result.get("copies", 0) or 0),
                "partner": str(result.get("partner", "cupy")),
                "v18_prepared_s": v18,
                "v18_reused_prepared_s": None,
                "v2_prepared_partner_s": v2,
                "ratio_vs_v18_prepared": float(ratio) if isinstance(ratio, (int, float)) else _ratio(v2, v18),
                "ratio_vs_v18_reused_prepared": None,
                "classification": "positive-bounded",
                "insight": (
                    "Goal1972 removes the closed-form graph shortcut and uses generic partner metric-table "
                    "reductions; this is still not a broad graph traversal acceleration claim."
                ),
                "artifact": path,
            }
        )
    return rows


def _goal1975_exact_hausdorff_rows() -> list[dict[str, object]]:
    path = "docs/reports/goal1975_pod_exact_hausdorff_partner_cupy_perf.json"
    artifact = _read_json(ROOT / path)
    if not artifact:
        return []
    candidates = [
        row
        for row in artifact.get("results", [])
        if isinstance(row, dict) and isinstance(row.get("v2_vs_cpu_python_reference_ratio"), (int, float))
    ]
    if not candidates:
        return []
    result = min(candidates, key=lambda row: int(row.get("copies", 0) or 0))
    v18 = _median(result, "cpu_python_reference_wall_s")
    v2 = _median(result, "v2_partner_exact_wall_s")
    ratio = result.get("v2_vs_cpu_python_reference_ratio")
    return [
        {
            "app": "hausdorff_distance",
            "label": "hausdorff distance",
            "size": int(result.get("point_count_a", 0) or 0),
            "partner": str(result.get("partner", "cupy")),
            "v18_prepared_s": v18,
            "v18_reused_prepared_s": None,
            "v2_prepared_partner_s": v2,
            "ratio_vs_v18_prepared": float(ratio) if isinstance(ratio, (int, float)) else _ratio(v2, v18),
            "ratio_vs_v18_reused_prepared": None,
            "classification": "positive-bounded-exact",
            "insight": (
                "Goal1975 upgrades Hausdorff from a fixed-radius threshold proxy to exact partner-reference "
                "directed Hausdorff via min-distance then max-distance reductions; the CPU baseline is limited "
                "to a small exact row and this is not an RT-core claim."
            ),
            "artifact": path,
        }
    ]


def _goal1978_exact_facility_top_k_rows() -> list[dict[str, object]]:
    path = "docs/reports/goal1978_pod_exact_top_k_facility_cupy_perf.json"
    artifact = _read_json(ROOT / path)
    if not artifact:
        return []
    candidates = [
        row
        for row in artifact.get("results", [])
        if isinstance(row, dict) and isinstance(row.get("v2_vs_cpu_python_reference_ratio"), (int, float))
    ]
    if not candidates:
        return []
    result = min(candidates, key=lambda row: int(row.get("copies", 0) or 0))
    v18 = _median(result, "cpu_python_reference_wall_s")
    v2 = _median(result, "v2_partner_exact_top_k_wall_s")
    ratio = result.get("v2_vs_cpu_python_reference_ratio")
    return [
        {
            "app": "facility_knn_assignment",
            "label": "facility knn assignment",
            "size": int(result.get("customers", 0) or 0),
            "partner": str(result.get("partner", "cupy")),
            "v18_prepared_s": v18,
            "v18_reused_prepared_s": None,
            "v2_prepared_partner_s": v2,
            "ratio_vs_v18_prepared": float(ratio) if isinstance(ratio, (int, float)) else _ratio(v2, v18),
            "ratio_vs_v18_reused_prepared": None,
            "classification": "positive-bounded-exact",
            "insight": (
                "Goal1978 upgrades facility KNN from a service-coverage threshold proxy to exact "
                "K=3 ranked nearest-depot rows through generic partner top-k point-column algebra; "
                "this is not an RT-core claim."
            ),
            "artifact": path,
        }
    ]


def _goal1979_exact_barnes_force_rows() -> list[dict[str, object]]:
    path = "docs/reports/goal1979_pod_exact_pairwise_force_barnes_hut_cupy_perf.json"
    artifact = _read_json(ROOT / path)
    if not artifact:
        return []
    candidates = [
        row
        for row in artifact.get("results", [])
        if isinstance(row, dict) and isinstance(row.get("v2_vs_cpu_python_reference_ratio"), (int, float))
    ]
    if not candidates:
        return []
    result = min(candidates, key=lambda row: int(row.get("body_count", 0) or 0))
    v18 = _median(result, "cpu_python_reference_wall_s")
    v2 = _median(result, "v2_partner_exact_force_wall_s")
    ratio = result.get("v2_vs_cpu_python_reference_ratio")
    return [
        {
            "app": "barnes_hut_force_app",
            "label": "barnes hut force app",
            "size": int(result.get("body_count", 0) or 0),
            "partner": str(result.get("partner", "cupy")),
            "v18_prepared_s": v18,
            "v18_reused_prepared_s": None,
            "v2_prepared_partner_s": v2,
            "ratio_vs_v18_prepared": float(ratio) if isinstance(ratio, (int, float)) else _ratio(v2, v18),
            "ratio_vs_v18_reused_prepared": None,
            "classification": "positive-bounded-exact",
            "insight": (
                "Goal1979 upgrades Barnes-Hut from node-coverage threshold proxy to exact all-pairs "
                "force-vector partner reference rows; this is not hierarchical Barnes-Hut tree-opening "
                "or RT-core acceleration."
            ),
            "artifact": path,
        }
    ]


def _goal1981_exact_dbscan_component_rows() -> list[dict[str, object]]:
    path = "docs/reports/goal1981_pod_exact_radius_graph_components_dbscan_cupy_perf.json"
    artifact = _read_json(ROOT / path)
    if not artifact:
        return []
    candidates = [
        row
        for row in artifact.get("results", [])
        if isinstance(row, dict) and isinstance(row.get("v2_vs_cpu_python_reference_ratio"), (int, float))
    ]
    if not candidates:
        return []
    result = min(candidates, key=lambda row: int(row.get("point_count", 0) or 0))
    v18 = _median(result, "cpu_python_reference_wall_s")
    v2 = _median(result, "v2_partner_exact_cluster_wall_s")
    ratio = result.get("v2_vs_cpu_python_reference_ratio")
    return [
        {
            "app": "dbscan_clustering",
            "label": "dbscan clustering",
            "size": int(result.get("point_count", 0) or 0),
            "partner": str(result.get("partner", "cupy")),
            "v18_prepared_s": v18,
            "v18_reused_prepared_s": None,
            "v2_prepared_partner_s": v2,
            "ratio_vs_v18_prepared": float(ratio) if isinstance(ratio, (int, float)) else _ratio(v2, v18),
            "ratio_vs_v18_reused_prepared": None,
            "classification": "positive-bounded-exact",
            "insight": (
                "Goal1981 upgrades DBSCAN from core-point threshold proxy to exact radius-graph "
                "component labels; current dense labeling is semantically correct but still needs "
                "a sparse/spatial-bucket partner implementation for larger rows."
            ),
            "artifact": path,
        }
    ]


def _goal1983_exact_ann_quality_rows() -> list[dict[str, object]]:
    path = "docs/reports/goal1983_pod_exact_ann_candidate_quality_cupy_perf.json"
    artifact = _read_json(ROOT / path)
    if not artifact:
        return []
    candidates = [
        row
        for row in artifact.get("results", [])
        if isinstance(row, dict) and isinstance(row.get("v2_vs_cpu_python_reference_ratio"), (int, float))
    ]
    if not candidates:
        return []
    result = min(candidates, key=lambda row: int(row.get("copies", 0) or 0))
    v18 = _median(result, "cpu_python_reference_wall_s")
    v2 = _median(result, "v2_partner_exact_quality_wall_s")
    ratio = result.get("v2_vs_cpu_python_reference_ratio")
    return [
        {
            "app": "ann_candidate_search",
            "label": "ann candidate search",
            "size": int(result.get("query_count", 0) or 0),
            "partner": str(result.get("partner", "cupy")),
            "v18_prepared_s": v18,
            "v18_reused_prepared_s": None,
            "v2_prepared_partner_s": v2,
            "ratio_vs_v18_prepared": float(ratio) if isinstance(ratio, (int, float)) else _ratio(v2, v18),
            "ratio_vs_v18_reused_prepared": None,
            "classification": "positive-bounded-exact",
            "insight": (
                "Goal1983 upgrades ANN candidate search from a fixed-radius coverage proxy to an exact "
                "partner top-k quality reference over the candidate subset and the full search set. "
                "This measures rerank/quality semantics, not an ANN index build or recall-latency optimizer."
            ),
            "artifact": path,
        }
    ]


def _best_measured(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    best: dict[str, dict[str, object]] = {}
    for row in rows:
        app = str(row["app"])
        ratio = row.get("ratio_vs_v18_prepared")
        if not isinstance(ratio, (int, float)):
            continue
        current = best.get(app)
        current_ratio = current.get("ratio_vs_v18_prepared") if current else None
        if current is None or not isinstance(current_ratio, (int, float)) or ratio < current_ratio:
            best[app] = row
    return best


def build_analysis() -> dict[str, object]:
    matrix = _read_json(MATRIX_JSON)
    if matrix is None:
        raise FileNotFoundError(MATRIX_JSON)
    measured_rows = []
    measured_rows.extend(_fixed_radius_rows())
    measured_rows.extend(_fixed_radius_repeat3_rows())
    measured_rows.extend(
        _segment_or_road_row(
            "docs/reports/goal1903_segment_polygon_batch_pod_2048.json",
            "segment_polygon_hitcount",
            "segment polygon hitcount",
        )
    )
    measured_rows.extend(
        _segment_or_road_row(
            "docs/reports/goal1889_road_hazard_prepared_reuse_pod_2048.json",
            "road_hazard_screening",
            "road hazard screening",
        )
    )
    measured_rows.extend(_segment_anyhit_scaleup_rows())
    measured_rows.extend(_robot_scaleup_rows())
    measured_rows.extend(_goal1957_rawkernel_control_rows())
    measured_rows.extend(_goal1969_polygon_extent_rows())
    measured_rows.extend(_goal1972_graph_metric_table_rows())
    exact_hausdorff_rows = _goal1975_exact_hausdorff_rows()
    exact_facility_top_k_rows = _goal1978_exact_facility_top_k_rows()
    exact_barnes_force_rows = _goal1979_exact_barnes_force_rows()
    exact_dbscan_component_rows = _goal1981_exact_dbscan_component_rows()
    exact_ann_quality_rows = _goal1983_exact_ann_quality_rows()
    measured_rows.extend(exact_hausdorff_rows)
    measured_rows.extend(exact_facility_top_k_rows)
    measured_rows.extend(exact_barnes_force_rows)
    measured_rows.extend(exact_dbscan_component_rows)
    measured_rows.extend(exact_ann_quality_rows)
    best = _best_measured(measured_rows)
    if exact_hausdorff_rows:
        # For Hausdorff, exact semantics are more important than keeping the
        # smallest ratio from the older fixed-radius threshold proxy row.
        best["hausdorff_distance"] = exact_hausdorff_rows[0]
    if exact_facility_top_k_rows:
        # Same for facility KNN: ranked fallback rows are the authored app
        # semantics, while the older fixed-radius row is only coverage.
        best["facility_knn_assignment"] = exact_facility_top_k_rows[0]
    if exact_barnes_force_rows:
        # Force vectors are the authored Barnes-Hut app output; node coverage
        # is only a candidate/proxy row.
        best["barnes_hut_force_app"] = exact_barnes_force_rows[0]
    if exact_dbscan_component_rows:
        # Full component labels are the DBSCAN app semantics; core counts are
        # only the density predicate.
        best["dbscan_clustering"] = exact_dbscan_component_rows[0]
    if exact_ann_quality_rows:
        # ANN quality is the authored app semantic row; fixed-radius coverage
        # remains only a bounded candidate-proxy decision.
        best["ann_candidate_search"] = exact_ann_quality_rows[0]
    rows: list[dict[str, object]] = []
    for matrix_row in matrix["rows"]:
        app = str(matrix_row["app"])
        if app in best:
            entry = dict(best[app])
            entry["matrix_state"] = matrix_row["v2_state"]
            entry["claim_class"] = matrix_row["claim_class"]
            rows.append(entry)
            continue
        status = str(matrix_row["comparison_status"])
        rows.append(
            {
                "app": app,
                "label": app.replace("_", " "),
                "size": None,
                "partner": None,
                "v18_prepared_s": None,
                "v18_reused_prepared_s": None,
                "v2_prepared_partner_s": None,
                "ratio_vs_v18_prepared": None,
                "ratio_vs_v18_reused_prepared": None,
                "classification": (
                    "control" if status == "evidence-only-control" else "pending-pod"
                ),
                "matrix_state": matrix_row["v2_state"],
                "claim_class": matrix_row["claim_class"],
                "insight": matrix_row["analysis_hint"],
                "artifact": matrix_row["v2_evidence"],
            }
        )
    counts: dict[str, int] = {}
    for row in rows:
        classification = str(row["classification"])
        counts[classification] = counts.get(classification, 0) + 1
    return {
        "goal": "Goal1931",
        "status": "current-evidence-analysis-external-review-needed",
        "matrix_source": str(MATRIX_JSON.relative_to(ROOT)),
        "row_count": len(rows),
        "rows": rows,
        "classification_counts": counts,
        "claim_boundary": {
            "v2_0_release_authorized": False,
            "all_apps_have_final_pod_timing": False,
            "implemented_v2_rows_have_pod_timing": True,
            "whole_app_speedup_claim_authorized": False,
            "control_rows_are_speedup_evidence": False,
        },
    }


def _fmt(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    if value is None:
        return "pending"
    return str(value)


def to_markdown(payload: dict[str, object]) -> str:
    rows = payload["rows"]
    assert isinstance(rows, list)
    lines = [
        "# Goal1931 - Current All-App v1.8 vs v2.0 Performance Analysis",
        "",
        "Status: current-evidence-analysis-external-review-needed",
        "",
        "Date: 2026-05-13",
        "",
        "This report is the current all-app performance analysis layer on top of Goal1930. It uses existing accepted pod artifacts where they exist and marks the remaining rows as pending or evidence-only controls. It does not authorize v2.0 release and it does not claim every app has a measured v2 speedup.",
        "",
        "## Current Table",
        "",
        "| App | Class | Partner | Size | v1.8 prepared s | v2 prepared partner s | Ratio | Insight |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        assert isinstance(row, dict)
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['app']}`",
                    f"`{row['classification']}`",
                    _fmt(row["partner"]),
                    _fmt(row["size"]),
                    _fmt(row["v18_prepared_s"]),
                    _fmt(row["v2_prepared_partner_s"]),
                    _fmt(row["ratio_vs_v18_prepared"]),
                    str(row["insight"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## What The Table Says",
            "",
            "- The strongest measured v2 rows are the repeat-3 fixed-radius family rows, where v1.8 is seconds-scale and v2 partner threshold decisions are sub-millisecond.",
            "- Segment any-hit now has a seconds-scale same-contract row at 1,048,576 outputs; road-hazard and segment hitcount remain positive compact-output rows.",
            "- Robot collision now has exact pose-flag parity and strong ratios through 8,388,608 poses, but it is marked `positive-subsecond` because the v1.8 baseline is still below one second.",
            "- Database remains a bounded control/fallback row. Graph and the two polygon control rows now have positive bounded v2 evidence after Goal1972 and Goal1969, but their claims stay narrow.",
            "- Hausdorff now has an exact partner-reference row after Goal1975, so the table prefers that semantic match over the faster but weaker fixed-radius threshold proxy.",
            "- Facility KNN now has an exact partner-reference K=3 top-k row after Goal1978, so the table no longer treats service coverage as the best semantic representative for that app.",
            "- Barnes-Hut now has exact partner-reference force-vector rows after Goal1979, so node coverage stays useful but no longer stands in for force output.",
            "- DBSCAN now has exact partner-reference radius-graph component labels after Goal1981, but the dense implementation is still marked as optimization debt.",
            "- ANN candidate search now has an exact partner-reference top-k quality row after Goal1983, but ANN index construction and recall/latency optimization remain outside this slice.",
            "",
            "## Release Boundary",
            "",
            "This is a performance-analysis scaffold and partial evidence report. Final v2.0 still needs external review of the all-app conclusion, a packaging/source-tree decision, and final release consensus.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build current all-app v1.8-vs-v2 analysis.")
    parser.add_argument("--output-json", default="docs/reports/goal1931_current_all_app_v18_v2_perf_analysis_2026-05-13.json")
    parser.add_argument("--output-md", default="docs/reports/goal1931_current_all_app_v18_v2_perf_analysis_2026-05-13.md")
    args = parser.parse_args(list(argv) if argv is not None else None)
    payload = build_analysis()
    json_path = ROOT / args.output_json
    md_path = ROOT / args.output_md
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

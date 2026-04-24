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


GOAL = "Goal759 RTX cloud benchmark manifest"
DATE = "2026-04-22"


def _entry(
    *,
    app: str,
    app_path: str,
    path_name: str,
    command: list[str],
    scale: dict[str, Any],
    claim_scope: str,
    non_claim: str,
    preconditions: list[str],
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    perf = rt.optix_app_performance_support(app)
    readiness = rt.optix_app_benchmark_readiness(app)
    return {
        "app": app,
        "app_path": app_path,
        "path_name": path_name,
        "command": command,
        "scale": scale,
        "optix_performance_class": perf.performance_class,
        "optix_performance_note": perf.note,
        "benchmark_readiness": readiness.status,
        "readiness_next_goal": readiness.next_goal,
        "benchmark_contract": readiness.benchmark_contract,
        "readiness_blocker": readiness.blocker,
        "allowed_claim_today": readiness.allowed_claim,
        "claim_scope": claim_scope,
        "non_claim": non_claim,
        "baseline_review_contract": _baseline_review_contract(app, path_name),
        "preconditions": preconditions,
        "env": dict(env or {}),
    }


def _deferred_entry(
    *,
    app: str,
    app_path: str,
    path_name: str,
    command: list[str],
    env: dict[str, str],
    reason_deferred: str,
    activation_gate: str,
    claim_scope: str,
    non_claim: str,
) -> dict[str, Any]:
    perf = rt.optix_app_performance_support(app)
    readiness = rt.optix_app_benchmark_readiness(app)
    return {
        "app": app,
        "app_path": app_path,
        "path_name": path_name,
        "command": command,
        "env": dict(env),
        "optix_performance_class": perf.performance_class,
        "optix_performance_note": perf.note,
        "benchmark_readiness": readiness.status,
        "reason_deferred": reason_deferred,
        "activation_gate": activation_gate,
        "claim_scope": claim_scope,
        "non_claim": non_claim,
        "baseline_review_contract": _baseline_review_contract(app, path_name),
    }


def _baseline_review_contract(app: str, path_name: str) -> dict[str, Any]:
    common = {
        "status": "required_before_public_speedup_claim",
        "minimum_repeated_runs": 3,
        "requires_correctness_parity": True,
        "requires_phase_separation": True,
        "forbidden_comparison": (
            "Do not compare a scalar/prepared RTX sub-path against a whole-app, "
            "row-output, validation-included, or different-result-mode baseline."
        ),
    }
    if app == "database_analytics":
        return {
            **common,
            "comparable_metric_scope": "compact_summary prepared DB query result for the same scenario/copies/iterations",
            "required_baselines": [
                "cpu_oracle_compact_summary",
                "embree_compact_summary",
                "postgresql_same_semantics_on_linux_when_available",
            ],
            "required_phases": [
                "input_pack_or_table_build",
                "backend_prepare",
                "native_query",
                "copyback_or_materialization",
                "python_summary_postprocess",
            ],
            "claim_limit": "prepared DB sub-path only; not a DBMS or SQL-engine speedup claim",
        }
    if app in {"outlier_detection", "dbscan_clustering"}:
        return {
            **common,
            "comparable_metric_scope": "prepared fixed-radius scalar threshold-count/core-count result with identical radius, threshold, fixture, and copies",
            "required_baselines": [
                "cpu_scalar_threshold_count_oracle",
                "embree_scalar_or_summary_path",
                "scipy_or_reference_neighbor_baseline_when_used_in_app_report",
            ],
            "required_phases": [
                "point_pack",
                "backend_prepare",
                "native_threshold_query",
                "scalar_copyback",
                "python_postprocess",
            ],
            "claim_limit": (
                "outlier threshold-count or DBSCAN core-count summary only; "
                "not row-returning neighbors or full DBSCAN cluster expansion"
            ),
        }
    if app == "robot_collision_screening":
        return {
            **common,
            "comparable_metric_scope": "prepared scalar colliding-pose count for the same poses, edges, obstacles, and iteration policy",
            "required_baselines": [
                "cpu_oracle_pose_count",
                "embree_anyhit_pose_count_or_equivalent_compact_summary",
            ],
            "required_phases": [
                "pose_and_obstacle_generation",
                "ray_pack",
                "backend_scene_prepare",
                "pose_index_prepare",
                "native_anyhit_query",
                "scalar_copyback",
                "oracle_validation_separate",
            ],
            "claim_limit": "scalar pose-count collision screening only; not full robot planning, kinematics, CCD, or witness-row output",
        }
    if app == "graph_analytics":
        return {
            **common,
            "comparable_metric_scope": (
                "strict graph visibility-edge, native BFS graph-ray, and native "
                "triangle-count graph-ray row-digest results for the same copies semantics"
            ),
            "required_baselines": [
                "cpu_python_reference_visibility_edges",
                "cpu_python_reference_bfs",
                "cpu_python_reference_triangle_count",
                "optix_visibility_anyhit",
                "optix_native_graph_ray_bfs",
                "optix_native_graph_ray_triangle_count",
                "embree_graph_ray_bfs_and_triangle_when_available",
            ],
            "required_phases": [
                "records",
                "row_digest",
                "strict_pass",
                "strict_failures",
                "status",
            ],
            "claim_limit": (
                "bounded graph RT sub-paths only: visibility any-hit plus BFS/triangle "
                "candidate generation; not shortest-path, graph database, distributed "
                "graph analytics, or whole-app graph-system acceleration"
            ),
        }
    if app in {"service_coverage_gaps", "event_hotspot_screening"}:
        return {
            **common,
            "comparable_metric_scope": "prepared compact fixed-radius summary for the same generated households/events/facilities and radius",
            "required_baselines": [
                "cpu_oracle_summary",
                "embree_summary_path",
                "scipy_baseline_when_available",
            ],
            "required_phases": [
                "input_build",
                "optix_prepare",
                "optix_query",
                "python_postprocess",
            ],
            "claim_limit": "prepared compact summary only; not nearest-row or whole-app speedup",
        }
    if app in {"road_hazard_screening", "segment_polygon_hitcount"}:
        if app == "road_hazard_screening":
            comparable = "strict road-hazard native OptiX summary result on the same copies/output-mode semantics"
            claim_limit = "experimental native road-hazard summary gate only; not default public app behavior or full GIS/routing speedup"
        else:
            comparable = "strict segment/polygon hit-count result on the same dataset and output count semantics"
            claim_limit = "experimental native hit-count gate only; not pair-row any-hit or road-hazard whole-app speedup"
        return {
            **common,
            "comparable_metric_scope": comparable,
            "required_baselines": [
                "cpu_python_reference",
                "optix_host_indexed",
                "postgis_when_available",
            ],
            "required_phases": [
                "records",
                "strict_pass",
                "strict_failures",
                "status",
            ],
            "claim_limit": claim_limit,
        }
    if app == "segment_polygon_anyhit_rows":
        return {
            **common,
            "comparable_metric_scope": "strict bounded segment/polygon pair-row result on the same dataset and output capacity",
            "required_baselines": [
                "cpu_python_reference",
                "optix_native_bounded_pair_rows",
                "postgis_when_available_for_same_pair_semantics",
            ],
            "required_phases": [
                "records",
                "row_digest",
                "emitted_count",
                "copied_count",
                "overflowed",
                "strict_pass",
                "strict_failures",
                "status",
            ],
            "claim_limit": (
                "experimental native bounded pair-row gate only; not default public app behavior "
                "and not unbounded row-volume performance"
            ),
        }
    if app in {"polygon_pair_overlap_area_rows", "polygon_set_jaccard"}:
        is_pair = app == "polygon_pair_overlap_area_rows"
        return {
            **common,
            "comparable_metric_scope": (
                "native-assisted OptiX LSI/PIP candidate-discovery phase plus CPU exact area refinement"
                if is_pair
                else "native-assisted OptiX LSI/PIP candidate-discovery phase plus CPU exact Jaccard refinement"
            ),
            "required_baselines": [
                "cpu_python_reference",
                "embree_native_assisted_candidate_discovery",
                "postgis_when_available_for_same_unit_cell_contract",
            ],
            "required_phases": [
                "input_build_sec",
                "cpu_reference_sec",
                "optix_candidate_discovery_sec",
                "cpu_exact_refinement_sec",
                "parity_vs_cpu",
                "rt_core_candidate_discovery_active",
            ],
            "claim_limit": (
                "native-assisted candidate-discovery path only; exact area/Jaccard refinement remains CPU/Python"
            ),
        }
    return {
        **common,
        "comparable_metric_scope": f"same app/path semantics for {app}:{path_name}",
        "required_baselines": [
            "cpu_oracle_same_semantics",
            "best_available_non_optix_backend_same_semantics",
        ],
        "required_phases": [
            "input_build",
            "backend_prepare",
            "native_query",
            "materialization_or_copyback",
            "postprocess",
        ],
        "claim_limit": "bounded sub-path only",
    }


def build_manifest() -> dict[str, Any]:
    python = "python3"
    return {
        "goal": GOAL,
        "date": DATE,
        "repo": str(ROOT),
        "purpose": (
            "Machine-readable contract for the next paid NVIDIA RTX cloud run. "
            "This manifest selects app paths worth timing and records what each "
            "result is allowed to claim."
        ),
        "global_preconditions": [
            "Run on RTX-class NVIDIA hardware with RT cores, not GTX 1070.",
            "Build the OptiX backend from the checked-out commit before timing.",
            "Record GPU model, driver, CUDA, OptiX SDK, commit hash, and command output.",
            "Keep validation/postprocess timing separate from native traversal where the profiler exposes it.",
        ],
        "entries": [
            _entry(
                app="database_analytics",
                app_path="examples/rtdl_database_analytics_app.py",
                path_name="prepared_db_session_sales_risk",
                command=[
                    python,
                    "scripts/goal756_db_prepared_session_perf.py",
                    "--backend",
                    "optix",
                    "--scenario",
                    "sales_risk",
                    "--copies",
                    "20000",
                    "--iterations",
                    "10",
                    "--output-mode",
                    "compact_summary",
                    "--strict",
                    "--output-json",
                    "docs/reports/goal759_db_sales_risk_rtx.json",
                ],
                scale={"copies": 20000, "iterations": 10},
                claim_scope="prepared OptiX DB session behavior and Python/interface cost split",
                non_claim="not a SQL engine claim and not a broad RTX RT-core app speedup claim",
                preconditions=["OptiX DB backend must be available.", "Use prepared-session profiler, not only one-shot CLI timing."],
            ),
            _entry(
                app="database_analytics",
                app_path="examples/rtdl_database_analytics_app.py",
                path_name="prepared_db_session_regional_dashboard",
                command=[
                    python,
                    "scripts/goal756_db_prepared_session_perf.py",
                    "--backend",
                    "optix",
                    "--scenario",
                    "regional_dashboard",
                    "--copies",
                    "20000",
                    "--iterations",
                    "10",
                    "--output-mode",
                    "compact_summary",
                    "--strict",
                    "--output-json",
                    "docs/reports/goal759_db_regional_dashboard_rtx.json",
                ],
                scale={"copies": 20000, "iterations": 10},
                claim_scope="prepared OptiX DB session behavior and Python/interface cost split",
                non_claim="not a SQL engine claim and not a broad RTX RT-core app speedup claim",
                preconditions=["OptiX DB backend must be available.", "Use prepared-session profiler, not only one-shot CLI timing."],
            ),
            _entry(
                app="outlier_detection",
                app_path="examples/rtdl_outlier_detection_app.py",
                path_name="prepared_fixed_radius_density_summary",
                command=[
                    python,
                    "scripts/goal757_optix_fixed_radius_prepared_perf.py",
                    "--copies",
                    "20000",
                    "--iterations",
                    "10",
                    "--result-mode",
                    "threshold_count",
                    "--skip-validation",
                    "--output-json",
                    "docs/reports/goal759_outlier_dbscan_fixed_radius_rtx.json",
                ],
                scale={"copies": 20000, "iterations": 10},
                claim_scope="prepared fixed-radius threshold summary traversal only",
                non_claim="not a KNN, Hausdorff, ANN, Barnes-Hut, anomaly-detection-system, or whole-app RTX speedup claim",
                preconditions=[
                    "OptiX fixed-radius prepared symbols must be exported.",
                    "Interpret only the outlier section of the combined Goal757 profiler for this entry.",
                ],
            ),
            _entry(
                app="dbscan_clustering",
                app_path="examples/rtdl_dbscan_clustering_app.py",
                path_name="prepared_fixed_radius_core_flags",
                command=[
                    python,
                    "scripts/goal757_optix_fixed_radius_prepared_perf.py",
                    "--copies",
                    "20000",
                    "--iterations",
                    "10",
                    "--result-mode",
                    "threshold_count",
                    "--skip-validation",
                    "--output-json",
                    "docs/reports/goal759_outlier_dbscan_fixed_radius_rtx.json",
                ],
                scale={"copies": 20000, "iterations": 10},
                claim_scope="prepared fixed-radius core-flag traversal only",
                non_claim="not a full DBSCAN clustering, KNN, Hausdorff, ANN, Barnes-Hut, or whole-app RTX speedup claim",
                preconditions=[
                    "OptiX fixed-radius prepared symbols must be exported.",
                    "Interpret only the DBSCAN section of the combined Goal757 profiler for this entry.",
                    "Report Python cluster expansion separately when measuring full DBSCAN.",
                ],
            ),
            _entry(
                app="robot_collision_screening",
                app_path="examples/rtdl_robot_collision_screening_app.py",
                path_name="prepared_pose_flags",
                command=[
                    python,
                    "scripts/goal760_optix_robot_pose_flags_phase_profiler.py",
                    "--mode",
                    "optix",
                    "--pose-count",
                    "200000",
                    "--obstacle-count",
                    "1024",
                    "--iterations",
                    "10",
                    "--input-mode",
                    "packed_arrays",
                    "--result-mode",
                    "pose_count",
                    "--skip-validation",
                    "--output-json",
                    "docs/reports/goal759_robot_pose_flags_phase_rtx.json",
                ],
                scale={"pose_count": 200000, "obstacle_count": 1024, "iterations": 3},
                claim_scope="prepared OptiX ray/triangle any-hit pose-flag summary",
                non_claim="not continuous collision detection, full robot kinematics, or mesh-engine replacement",
                preconditions=[
                    "OptiX ray/triangle any-hit prepared symbols must be exported.",
                    "Use the phase profiler rather than raw app CLI timing for final claim review.",
                    "Cloud performance timing must use --skip-validation after Goal763 focused correctness passes.",
                    "Use packed_arrays input mode to avoid per-ray Python object construction in large cloud timing.",
                    "Use pose_count result mode for scalar native summary timing after pose-flag correctness is established.",
                ],
            ),
        ],
        "excluded_apps": {
            "graph_analytics": "deferred graph gate must pass for visibility any-hit plus explicit native BFS/triangle graph-ray mode before any graph RT-core claim",
            "road_hazard_screening": "current default OptiX app path is host-indexed fallback; deferred native gate must pass before any promotion",
            "segment_polygon_hitcount": "current default OptiX app path is host-indexed fallback",
            "segment_polygon_anyhit_rows": "current default OptiX app path is host-indexed fallback; native bounded pair-row path is deferred behind Goal873 strict RTX gate",
            "polygon_pair_overlap_area_rows": "native-assisted OptiX candidate discovery exists, but exact area refinement is CPU/Python-owned and lacks phase-clean RTX artifact",
            "polygon_set_jaccard": "native-assisted OptiX candidate discovery exists, but exact Jaccard refinement is CPU/Python-owned and lacks phase-clean RTX artifact",
            "apple_rt_demo": "Apple-specific, not an NVIDIA RTX cloud app",
            "hiprt_ray_triangle_hitcount": "HIPRT-specific, not an OptiX app benchmark",
        },
        "deferred_entries": [
            _deferred_entry(
                app="graph_analytics",
                app_path="examples/rtdl_graph_analytics_app.py",
                path_name="graph_visibility_edges_gate",
                command=[
                    python,
                    "scripts/goal889_graph_visibility_optix_gate.py",
                    "--copies",
                    "20000",
                    "--output-mode",
                    "summary",
                    "--strict",
                    "--output-json",
                    "docs/reports/goal889_graph_visibility_optix_gate_rtx.json",
                ],
                env={},
                reason_deferred=(
                    "Goal889/905 packages bounded graph RT sub-paths: visibility maps "
                    "candidate graph edges to RTDL visibility rows and OptiX any-hit "
                    "traversal, while BFS and triangle-count use explicit native "
                    "OptiX graph-ray mode for candidate generation."
                ),
                activation_gate=(
                    "Promote only after strict mode passes on RTX hardware for "
                    "visibility, native BFS graph-ray, and native triangle graph-ray; "
                    "higher-level graph-system exclusions must remain explicit and "
                    "independent review must accept the artifact."
                ),
                claim_scope=(
                    "OptiX ray/triangle any-hit traversal for graph visibility-edge "
                    "filtering plus native OptiX graph-ray traversal candidate "
                    "generation for BFS and triangle-count"
                ),
                non_claim=(
                    "not shortest-path, graph database, distributed graph analytics, "
                    "or whole-app graph-system acceleration; BFS visited/frontier "
                    "bookkeeping and triangle set-intersection remain outside RT traversal"
                ),
            ),
            _deferred_entry(
                app="service_coverage_gaps",
                app_path="examples/rtdl_service_coverage_gaps.py",
                path_name="prepared_gap_summary",
                command=[
                    python,
                    "scripts/goal811_spatial_optix_summary_phase_profiler.py",
                    "--scenario",
                    "service_coverage_gaps",
                    "--mode",
                    "optix",
                    "--copies",
                    "20000",
                    "--output-json",
                    "docs/reports/goal811_service_coverage_rtx.json",
                ],
                env={},
                reason_deferred=(
                    "Goal810 exposes an OptiX prepared gap-summary path, and Goal811 "
                    "adds a phase profiler. It remains deferred until RTX timing and "
                    "review prove preparation/query/postprocess behavior."
                ),
                activation_gate=(
                    "Promote only after Goal811 optix mode runs on RTX hardware, phase "
                    "outputs are reviewed, and the app readiness matrix is updated."
                ),
                claim_scope="prepared OptiX fixed-radius threshold traversal for coverage-gap summaries",
                non_claim="not a whole-app service coverage speedup claim and not a nearest-clinic row-output claim",
            ),
            _deferred_entry(
                app="event_hotspot_screening",
                app_path="examples/rtdl_event_hotspot_screening.py",
                path_name="prepared_count_summary",
                command=[
                    python,
                    "scripts/goal811_spatial_optix_summary_phase_profiler.py",
                    "--scenario",
                    "event_hotspot_screening",
                    "--mode",
                    "optix",
                    "--copies",
                    "20000",
                    "--output-json",
                    "docs/reports/goal811_event_hotspot_rtx.json",
                ],
                env={},
                reason_deferred=(
                    "Goal810 exposes an OptiX prepared count-summary path, and Goal811 "
                    "adds a phase profiler. It remains deferred until RTX timing and "
                    "review prove preparation/query/postprocess behavior."
                ),
                activation_gate=(
                    "Promote only after Goal811 optix mode runs on RTX hardware, phase "
                    "outputs are reviewed, and the app readiness matrix is updated."
                ),
                claim_scope="prepared OptiX fixed-radius count traversal for hotspot summaries",
                non_claim="not a whole-app hotspot-screening speedup claim and not a neighbor-row output claim",
            ),
            _deferred_entry(
                app="road_hazard_screening",
                app_path="examples/rtdl_road_hazard_screening.py",
                path_name="road_hazard_native_summary_gate",
                command=[
                    python,
                    "scripts/goal888_road_hazard_native_optix_gate.py",
                    "--copies",
                    "20000",
                    "--output-mode",
                    "summary",
                    "--strict",
                    "--output-json",
                    "docs/reports/goal888_road_hazard_native_optix_gate_rtx.json",
                ],
                env={},
                reason_deferred=(
                    "Goal888 packages the road-hazard app around the explicit native "
                    "segment/polygon OptiX mode and compact summary output. It remains "
                    "deferred until strict RTX validation proves parity."
                ),
                activation_gate=(
                    "Promote only after Goal888 strict mode passes on RTX hardware, "
                    "the default host-indexed path remains clearly separated, and "
                    "independent review accepts the artifact."
                ),
                claim_scope="native OptiX segment/polygon traversal for compact road-hazard summaries",
                non_claim="not default public road-hazard behavior and not a full GIS/routing speedup claim",
            ),
            _deferred_entry(
                app="segment_polygon_hitcount",
                app_path="examples/rtdl_segment_polygon_hitcount.py",
                path_name="segment_polygon_hitcount_native_experimental",
                command=[
                    python,
                    "scripts/goal807_segment_polygon_optix_mode_gate.py",
                    "--dataset",
                    "derived/br_county_subset_segment_polygon_tiled_x256",
                    "--strict",
                    "--output-json",
                    "docs/reports/goal807_segment_polygon_optix_mode_gate_rtx.json",
                ],
                env={},
                reason_deferred=(
                    "Native OptiX hit-count exists behind an explicit app mode, but "
                    "historical Goal120 evidence showed no performance win and the "
                    "default public app path remains host-indexed. Goal807 now provides "
                    "the required focused native-vs-host-indexed gate, but the gate has "
                    "not passed on RTX hardware yet."
                ),
                activation_gate=(
                    "Promote only after Goal807 strict mode passes on RTX hardware, "
                    "PostGIS parity is recorded where PostGIS is available, and the "
                    "app readiness matrix is updated after independent review."
                ),
                claim_scope="experimental native custom-AABB segment/polygon hit-count traversal",
                non_claim="not default public app behavior and not a row-returning any-hit claim",
            ),
            _deferred_entry(
                app="hausdorff_distance",
                app_path="examples/rtdl_hausdorff_distance_app.py",
                path_name="directed_threshold_prepared",
                command=[
                    python,
                    "scripts/goal887_prepared_decision_phase_profiler.py",
                    "--scenario",
                    "hausdorff_threshold",
                    "--mode",
                    "optix",
                    "--copies",
                    "20000",
                    "--iterations",
                    "10",
                    "--radius",
                    "0.4",
                    "--skip-validation",
                    "--output-json",
                    "docs/reports/goal887_hausdorff_threshold_rtx.json",
                ],
                env={},
                reason_deferred=(
                    "Goal879 exposes a prepared OptiX threshold-decision sub-path, "
                    "but a phase profiler and same-semantics RTX artifact are still required."
                ),
                activation_gate=(
                    "Promote only after a Goal879 RTX artifact separates prepare/query/postprocess "
                    "and is reviewed against same-semantics threshold baselines."
                ),
                claim_scope="prepared OptiX fixed-radius threshold traversal for Hausdorff <= radius decisions",
                non_claim="not an exact Hausdorff distance, KNN-row, or nearest-neighbor ranking speedup claim",
            ),
            _deferred_entry(
                app="ann_candidate_search",
                app_path="examples/rtdl_ann_candidate_app.py",
                path_name="candidate_threshold_prepared",
                command=[
                    python,
                    "scripts/goal887_prepared_decision_phase_profiler.py",
                    "--scenario",
                    "ann_candidate_coverage",
                    "--mode",
                    "optix",
                    "--copies",
                    "20000",
                    "--iterations",
                    "10",
                    "--radius",
                    "0.2",
                    "--skip-validation",
                    "--output-json",
                    "docs/reports/goal887_ann_candidate_coverage_rtx.json",
                ],
                env={},
                reason_deferred=(
                    "Goal880 exposes a prepared OptiX candidate-coverage decision sub-path, "
                    "but a phase profiler and same-semantics RTX artifact are still required."
                ),
                activation_gate=(
                    "Promote only after a Goal880 RTX artifact separates prepare/query/postprocess "
                    "and is reviewed against same-semantics threshold baselines."
                ),
                claim_scope="prepared OptiX fixed-radius threshold traversal for ANN candidate-coverage decisions",
                non_claim="not a full ANN index, nearest-neighbor ranking, FAISS/HNSW/IVF/PQ, or recall-optimizer claim",
            ),
            _deferred_entry(
                app="facility_knn_assignment",
                app_path="examples/rtdl_facility_knn_assignment.py",
                path_name="coverage_threshold_prepared",
                command=[
                    python,
                    "scripts/goal887_prepared_decision_phase_profiler.py",
                    "--scenario",
                    "facility_service_coverage",
                    "--mode",
                    "optix",
                    "--copies",
                    "20000",
                    "--iterations",
                    "10",
                    "--radius",
                    "1.0",
                    "--skip-validation",
                    "--output-json",
                    "docs/reports/goal887_facility_service_coverage_rtx.json",
                ],
                env={},
                reason_deferred=(
                    "Goal881 exposes a prepared OptiX service-coverage decision sub-path, "
                    "but a phase profiler and same-semantics RTX artifact are still required."
                ),
                activation_gate=(
                    "Promote only after a Goal881 RTX artifact separates prepare/query/postprocess "
                    "and is reviewed against same-semantics threshold baselines."
                ),
                claim_scope="prepared OptiX fixed-radius threshold traversal for facility service-coverage decisions",
                non_claim="not a ranked nearest-depot, KNN fallback-assignment, or facility-location optimizer claim",
            ),
            _deferred_entry(
                app="barnes_hut_force_app",
                app_path="examples/rtdl_barnes_hut_force_app.py",
                path_name="node_coverage_prepared",
                command=[
                    python,
                    "scripts/goal887_prepared_decision_phase_profiler.py",
                    "--scenario",
                    "barnes_hut_node_coverage",
                    "--mode",
                    "optix",
                    "--body-count",
                    "200000",
                    "--iterations",
                    "10",
                    "--radius",
                    "10.0",
                    "--skip-validation",
                    "--output-json",
                    "docs/reports/goal887_barnes_hut_node_coverage_rtx.json",
                ],
                env={},
                reason_deferred=(
                    "Goal882 exposes a prepared OptiX node-coverage decision sub-path, "
                    "but a phase profiler and same-semantics RTX artifact are still required."
                ),
                activation_gate=(
                    "Promote only after a Goal882 RTX artifact separates prepare/query/postprocess "
                    "and is reviewed against same-semantics threshold baselines."
                ),
                claim_scope="prepared OptiX fixed-radius threshold traversal for Barnes-Hut node-coverage decisions",
                non_claim="not a Barnes-Hut opening-rule, force-vector reduction, or N-body solver speedup claim",
            ),
            _deferred_entry(
                app="segment_polygon_anyhit_rows",
                app_path="examples/rtdl_segment_polygon_anyhit_rows.py",
                path_name="segment_polygon_anyhit_rows_native_bounded_gate",
                command=[
                    python,
                    "scripts/goal873_native_pair_row_optix_gate.py",
                    "--dataset",
                    "authored_segment_polygon_minimal",
                    "--output-capacity",
                    "1024",
                    "--strict",
                    "--output-json",
                    "docs/reports/goal873_native_pair_row_optix_gate_rtx_strict.json",
                ],
                env={},
                reason_deferred=(
                    "Goal872 implements a native bounded device-side pair-row emitter, and Goal873 "
                    "adds the strict gate. The public rows path remains host-indexed until a real "
                    "RTX strict artifact proves CPU row-digest parity and no output overflow."
                ),
                activation_gate=(
                    "Promote only after Goal873 strict mode passes on RTX hardware, row digest "
                    "matches CPU reference, overflow is zero, and independent review accepts the artifact."
                ),
                claim_scope="experimental native bounded custom-AABB segment/polygon pair-row traversal",
                non_claim="not default public app behavior and not an unbounded pair-row performance claim",
            ),
            _deferred_entry(
                app="polygon_pair_overlap_area_rows",
                app_path="examples/rtdl_polygon_pair_overlap_area_rows.py",
                path_name="polygon_pair_overlap_optix_native_assisted_phase_gate",
                command=[
                    python,
                    "scripts/goal877_polygon_overlap_optix_phase_profiler.py",
                    "--app",
                    "pair_overlap",
                    "--mode",
                    "optix",
                    "--copies",
                    "20000",
                    "--output-json",
                    "docs/reports/goal877_pair_overlap_phase_rtx.json",
                ],
                env={},
                reason_deferred=(
                    "Goal876 exposes OptiX native-assisted candidate discovery, and Goal877 "
                    "adds phase separation. It remains deferred until a real RTX artifact proves "
                    "candidate-discovery timing, CPU refinement timing, and parity."
                ),
                activation_gate=(
                    "Promote only after Goal877 optix mode passes on RTX hardware, phases are reviewed, "
                    "and top-level claims stay limited to candidate discovery."
                ),
                claim_scope="OptiX native-assisted LSI/PIP candidate discovery for bounded polygon-pair overlap",
                non_claim="not a fully native polygon-area kernel and not a full app RTX speedup claim",
            ),
            _deferred_entry(
                app="polygon_set_jaccard",
                app_path="examples/rtdl_polygon_set_jaccard.py",
                path_name="polygon_set_jaccard_optix_native_assisted_phase_gate",
                command=[
                    python,
                    "scripts/goal877_polygon_overlap_optix_phase_profiler.py",
                    "--app",
                    "jaccard",
                    "--mode",
                    "optix",
                    "--copies",
                    "20000",
                    "--output-json",
                    "docs/reports/goal877_jaccard_phase_rtx.json",
                ],
                env={},
                reason_deferred=(
                    "Goal876 exposes OptiX native-assisted candidate discovery, and Goal877 "
                    "adds phase separation. It remains deferred until a real RTX artifact proves "
                    "candidate-discovery timing, CPU refinement timing, and parity."
                ),
                activation_gate=(
                    "Promote only after Goal877 optix mode passes on RTX hardware, phases are reviewed, "
                    "and top-level claims stay limited to candidate discovery."
                ),
                claim_scope="OptiX native-assisted LSI/PIP candidate discovery for bounded polygon-set Jaccard",
                non_claim="not a fully native Jaccard kernel and not a full app RTX speedup claim",
            ),
        ],
        "boundary": (
            "The manifest is a benchmark contract only. It does not authorize RTX speedup claims; "
            "claims require successful cloud runs, phase-clean evidence, and independent review."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit the Goal759 RTX cloud benchmark manifest.")
    parser.add_argument("--output-json")
    args = parser.parse_args(argv)
    payload = build_manifest()
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output_json:
        Path(args.output_json).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

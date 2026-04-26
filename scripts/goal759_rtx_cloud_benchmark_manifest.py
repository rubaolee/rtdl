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
            comparable = "prepared road-hazard native OptiX summary result on the same copies and priority-threshold semantics"
            claim_limit = "experimental prepared road-hazard summary gate only; not default public app behavior or full GIS/routing speedup"
        else:
            comparable = "prepared segment/polygon hit-count result on the same dataset and output count semantics"
            claim_limit = "experimental prepared hit-count gate only; not pair-row any-hit or road-hazard whole-app speedup"
        return {
            **common,
            "comparable_metric_scope": comparable,
            "required_baselines": [
                "cpu_python_reference",
                "embree_same_semantics",
                "postgis_when_available",
            ],
            "required_phases": [
                "input_build_sec",
                "optix_prepare_sec",
                "optix_query_sec",
                "python_postprocess_sec",
                "validation_sec",
                "optix_close_sec",
            ],
            "claim_limit": claim_limit,
        }
    if app == "segment_polygon_anyhit_rows":
        return {
            **common,
            "comparable_metric_scope": "strict bounded segment/polygon pair-row result on the same dataset and output capacity",
            "required_baselines": [
                "cpu_python_reference",
                "optix_prepared_bounded_pair_rows",
                "postgis_when_available_for_same_pair_semantics",
            ],
            "required_phases": [
                "input_build_sec",
                "cpu_reference_total_sec",
                "optix_prepare_sec",
                "optix_query_sec",
                "python_postprocess_sec",
                "validation_sec",
                "optix_close_sec",
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
                "native-assisted OptiX LSI/PIP candidate-discovery phase plus native C++ exact area continuation"
                if is_pair
                else "native-assisted OptiX LSI/PIP candidate-discovery phase plus native C++ exact Jaccard continuation"
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
                "native_exact_continuation_sec",
                "parity_vs_cpu",
                "rt_core_candidate_discovery_active",
            ],
            "claim_limit": (
                "native-assisted candidate-discovery plus native exact continuation path only; "
                "no full app RTX speedup claim without same-semantics review"
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
                claim_scope="prepared fixed-radius scalar threshold-count traversal only",
                non_claim=(
                    "not per-point outlier labels, row-output neighbors, KNN, Hausdorff, ANN, "
                    "Barnes-Hut, anomaly-detection-system, or whole-app RTX speedup claim"
                ),
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
                claim_scope="prepared fixed-radius scalar core-count traversal only",
                non_claim=(
                    "not per-point core flags, not a full DBSCAN clustering, KNN, Hausdorff, ANN, "
                    "Barnes-Hut, or whole-app RTX speedup claim"
                ),
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
            _entry(
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
                scale={"copies": 20000},
                claim_scope="prepared OptiX fixed-radius threshold traversal for coverage-gap summaries",
                non_claim="not a whole-app service coverage speedup claim and not a nearest-clinic row-output claim",
                preconditions=[
                    "Use the prepared gap-summary profiler, not row output or nearest-clinic output.",
                    "Interpret with the Goal917 same-scale CPU/Embree baseline review.",
                    "Do not start a pod only for this app; rerun only in a consolidated regression batch.",
                ],
            ),
            _entry(
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
                scale={"copies": 20000},
                claim_scope="prepared OptiX fixed-radius count traversal for hotspot summaries",
                non_claim="not a whole-app hotspot-screening speedup claim and not a neighbor-row output claim",
                preconditions=[
                    "Use the prepared count-summary profiler, not neighbor-row output.",
                    "Interpret with the Goal917 RTX artifact and Goal919 same-scale Embree baseline review.",
                    "Do not start a pod only for this app; rerun only in a consolidated regression batch.",
                ],
            ),
            _entry(
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
                scale={"copies": 20000, "iterations": 10},
                claim_scope="prepared OptiX fixed-radius threshold traversal for facility service-coverage decisions",
                non_claim="not a ranked nearest-depot, KNN fallback-assignment, or facility-location optimizer claim",
                preconditions=[
                    "Use the prepared coverage-threshold profiler, not KNN ranking output.",
                    "Interpret with the Goal887 RTX artifact and Goal920 same-scale CPU oracle baseline.",
                    "Do not start a pod only for this app; rerun only in a consolidated regression batch.",
                ],
            ),
        ],
        "excluded_apps": {
            "graph_analytics": "Goal929 passed the bounded graph gate; keep in deferred_entries only for consolidated regression reruns, not because it lacks an RTX artifact",
            "road_hazard_screening": "Goal929 proved native correctness, but native timing was slower than CPU; hold for native-kernel tuning before speedup claims",
            "segment_polygon_hitcount": "Goal929 proved native correctness, but native timing was slower than host-indexed/CPU paths; hold for native-kernel tuning",
            "segment_polygon_anyhit_rows": "Goal929 proved small bounded native pair-row correctness; hold for scalable row-output performance evidence",
            "polygon_pair_overlap_area_rows": "Goal929 passed native-assisted OptiX candidate discovery; keep in deferred_entries only for consolidated regression reruns",
            "polygon_set_jaccard": "Goal929 passed native-assisted OptiX candidate discovery at chunk-copies=20; larger chunks remain diagnostic failures",
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
                    "--validation-mode",
                    "analytic_summary",
                    "--chunk-copies",
                    "0",
                    "--strict",
                    "--output-json",
                    "docs/reports/goal889_graph_visibility_optix_gate_rtx.json",
                ],
                env={},
                reason_deferred=(
                    "Goal929 passed this bounded graph gate on RTX 3090. Keep the command "
                    "available for consolidated regression reruns: visibility maps "
                    "candidate graph edges to a prepared OptiX any-hit count summary, "
                    "while BFS and triangle-count use explicit native "
                    "OptiX graph-ray mode for candidate generation."
                ),
                activation_gate=(
                    "Regression artifact must pass strict mode on RTX hardware for "
                    "visibility, native BFS graph-ray, and native triangle graph-ray; "
                    "higher-level graph-system exclusions must remain explicit and "
                    "independent review must accept the artifact."
                ),
                claim_scope=(
                    "OptiX prepared ray/triangle any-hit count for graph visibility-edge "
                    "summary filtering plus native OptiX graph-ray traversal candidate "
                    "generation for BFS and triangle-count"
                ),
                non_claim=(
                    "not shortest-path, graph database, distributed graph analytics, "
                    "or whole-app graph-system acceleration; BFS visited/frontier "
                    "bookkeeping and triangle set-intersection remain outside RT traversal"
                ),
            ),
            _deferred_entry(
                app="road_hazard_screening",
                app_path="examples/rtdl_road_hazard_screening.py",
                path_name="road_hazard_native_summary_gate",
                command=[
                    python,
                    "scripts/goal933_prepared_segment_polygon_optix_profiler.py",
                    "--scenario",
                    "road_hazard_prepared_summary",
                    "--copies",
                    "20000",
                    "--iterations",
                    "5",
                    "--mode",
                    "run",
                    "--output-json",
                    "docs/reports/goal933_road_hazard_prepared_summary_rtx.json",
                ],
                env={},
                reason_deferred=(
                    "Goal929 proved strict native road-hazard parity on RTX 3090, but "
                    "native timing was slower than CPU. Goal933 now measures a prepared "
                    "polygon-BVH path so warm query time is separated from setup."
                ),
                activation_gate=(
                    "Re-enter claim review only after native-kernel tuning shows competitive "
                    "timing while the default host-indexed path remains clearly separated."
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
                    "scripts/goal933_prepared_segment_polygon_optix_profiler.py",
                    "--scenario",
                    "segment_polygon_hitcount_prepared",
                    "--copies",
                    "256",
                    "--iterations",
                    "5",
                    "--mode",
                    "run",
                    "--output-json",
                    "docs/reports/goal933_segment_polygon_hitcount_prepared_rtx.json",
                ],
                env={},
                reason_deferred=(
                    "Native OptiX hit-count exists behind an explicit app mode, but "
                    "Goal929 showed the native RTX path is slower than host-indexed and "
                    "CPU at the tested scale. Goal933 now measures a prepared polygon-BVH "
                    "path so warm query time is separated from setup."
                ),
                activation_gate=(
                    "Re-enter claim review only after native-kernel tuning shows competitive "
                    "timing, PostGIS parity is recorded where available, and independent "
                    "review accepts the artifact."
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
                path_name="segment_polygon_anyhit_rows_prepared_bounded_gate",
                command=[
                    python,
                    "scripts/goal934_prepared_segment_polygon_pair_rows_optix_profiler.py",
                    "--copies",
                    "256",
                    "--iterations",
                    "5",
                    "--output-capacity",
                    "4096",
                    "--mode",
                    "run",
                    "--output-json",
                    "docs/reports/goal934_segment_polygon_anyhit_rows_prepared_bounded_rtx.json",
                ],
                env={},
                reason_deferred=(
                    "Goal929 proved CPU row-digest parity and zero overflow for a small bounded "
                    "native pair-row gate. Goal934 now measures a prepared polygon-BVH pair-row "
                    "path on a larger tiled dataset so warm query time is separated from setup."
                ),
                activation_gate=(
                    "Re-enter claim review only after larger RTX row-output evidence remains overflow-free, "
                    "matches CPU reference, separates prepare/query/postprocess phases, and independent "
                    "review accepts the artifact."
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
                    "--output-mode",
                    "summary",
                    "--validation-mode",
                    "analytic_summary",
                    "--chunk-copies",
                    "100",
                    "--output-json",
                    "docs/reports/goal877_pair_overlap_phase_rtx.json",
                ],
                env={},
                reason_deferred=(
                    "Goal929 proved phase-separated RTX candidate-discovery timing, exact continuation "
                    "timing, and parity for this native-assisted polygon overlap sub-path. Keep "
                    "this command for consolidated regression reruns."
                ),
                activation_gate=(
                    "Regression artifacts must keep phases separated and top-level claims limited "
                    "to candidate discovery."
                ),
                claim_scope="OptiX native-assisted LSI/PIP candidate discovery for bounded polygon-pair overlap",
                non_claim="not a monolithic GPU polygon-area kernel and not a full app RTX speedup claim",
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
                    "--output-mode",
                    "summary",
                    "--validation-mode",
                    "analytic_summary",
                    "--chunk-copies",
                    "20",
                    "--output-json",
                    "docs/reports/goal877_jaccard_phase_rtx.json",
                ],
                env={},
                reason_deferred=(
                    "Goal929 proved phase-separated RTX candidate-discovery timing, exact continuation "
                    "timing, and parity for this native-assisted Jaccard sub-path at chunk-copies=20. "
                    "Keep this command for consolidated regression reruns."
                ),
                activation_gate=(
                    "Regression artifacts must keep chunk-copies=20 unless larger chunks are fixed, "
                    "phases separated, and top-level claims limited to candidate discovery."
                ),
                claim_scope="OptiX native-assisted LSI/PIP candidate discovery for bounded polygon-set Jaccard",
                non_claim="not a monolithic GPU Jaccard kernel and not a full app RTX speedup claim",
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

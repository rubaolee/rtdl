from __future__ import annotations

from typing import Any


ACTIVE_V1_5_BACKENDS = ("embree", "optix")
FROZEN_BEFORE_V2_1_BACKENDS = ("vulkan", "hiprt", "apple_rt")
V1_5_STABLE_GENERIC_PRIMITIVES = (
    "ANY_HIT",
    "FIXED_RADIUS_COUNT_THRESHOLD_2D",
    "DB_COMPACT_SUMMARY",
    "POLYGON_PAIR_EXACT_AREA_SUMMARY",
)
V1_5_EXPERIMENTAL_GENERIC_PRIMITIVES = ("COLLECT_K_BOUNDED",)
V1_5_STABLE_SUMMARY_PRIMITIVES = (
    "COUNT_HITS",
    "REDUCE_FLOAT(MIN)",
    "REDUCE_FLOAT(MAX)",
    "REDUCE_FLOAT(SUM)",
    "REDUCE_INT(COUNT)",
    "REDUCE_INT(SUM)",
)


def v1_5_generic_migration_inventory() -> tuple[dict[str, Any], ...]:
    """Return the current internal v1.5 app-to-generic-primitive migration map."""
    return (
        {
            "goal": "Goal1297",
            "app": "graph_analytics",
            "subpath": "visibility_edges_reusable_batches",
            "status": "pod_verified_generic",
            "generic_primitive": "ANY_HIT",
            "summary_primitive": "COUNT_HITS",
            "backend_scope": ("optix",),
            "remaining_app_specific_work": (),
            "public_wording_authorized": False,
            "boundary": "visibility any-hit count only; graph BFS, triangle counting, and graph-system analytics remain outside scope",
        },
        {
            "goal": "Goal1299",
            "app": "service_coverage_gaps",
            "subpath": "gap_summary_prepared",
            "status": "pod_verified_generic",
            "generic_primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
            "summary_primitive": "REDUCE_INT(COUNT)",
            "backend_scope": ACTIVE_V1_5_BACKENDS,
            "remaining_app_specific_work": (),
            "public_wording_authorized": False,
            "boundary": "coverage gap threshold-decision path only",
        },
        {
            "goal": "Goal1299",
            "app": "event_hotspot_screening",
            "subpath": "count_summary_prepared",
            "status": "pod_verified_generic",
            "generic_primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
            "summary_primitive": "REDUCE_INT(COUNT)",
            "backend_scope": ACTIVE_V1_5_BACKENDS,
            "remaining_app_specific_work": (),
            "public_wording_authorized": False,
            "boundary": "fixed-radius hotspot threshold-count path only",
        },
        {
            "goal": "Goal1300",
            "app": "ann_candidate_search",
            "subpath": "candidate_threshold_prepared",
            "status": "pod_verified_generic",
            "generic_primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
            "summary_primitive": "REDUCE_INT(COUNT)",
            "backend_scope": ("optix",),
            "remaining_app_specific_work": ("ann_indexing", "nearest_neighbor_ranking"),
            "public_wording_authorized": False,
            "boundary": "candidate threshold-decision path only",
        },
        {
            "goal": "Goal1300",
            "app": "facility_knn_assignment",
            "subpath": "coverage_threshold_prepared",
            "status": "pod_verified_generic",
            "generic_primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
            "summary_primitive": "REDUCE_INT(COUNT)",
            "backend_scope": ("optix",),
            "remaining_app_specific_work": ("ranked_knn_assignment",),
            "public_wording_authorized": False,
            "boundary": "facility service-coverage threshold-decision path only",
        },
        {
            "goal": "Goal1301",
            "app": "outlier_detection",
            "subpath": "density_count",
            "status": "pod_verified_generic",
            "generic_primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
            "summary_primitive": "REDUCE_INT(COUNT)",
            "backend_scope": ACTIVE_V1_5_BACKENDS,
            "remaining_app_specific_work": ("neighbor_row_materialization", "broad_outlier_analytics"),
            "public_wording_authorized": False,
            "boundary": "fixed-radius density threshold count only",
        },
        {
            "goal": "Goal1301",
            "app": "dbscan_clustering",
            "subpath": "core_count",
            "status": "pod_verified_generic",
            "generic_primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
            "summary_primitive": "REDUCE_INT(COUNT)",
            "backend_scope": ACTIVE_V1_5_BACKENDS,
            "remaining_app_specific_work": ("cluster_expansion", "connected_components"),
            "public_wording_authorized": False,
            "boundary": "fixed-radius DBSCAN core predicate count only",
        },
        {
            "goal": "Goal1302",
            "app": "barnes_hut_force_app",
            "subpath": "node_coverage_prepared",
            "status": "pod_verified_generic",
            "generic_primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
            "summary_primitive": "REDUCE_INT(COUNT)",
            "backend_scope": ("optix",),
            "remaining_app_specific_work": ("opening_rule", "force_vector_reduction"),
            "public_wording_authorized": False,
            "boundary": "node-coverage threshold-decision path only",
        },
        {
            "goal": "Goal1302",
            "app": "hausdorff_distance",
            "subpath": "directed_threshold_prepared",
            "status": "pod_verified_generic",
            "generic_primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
            "summary_primitive": "REDUCE_INT(COUNT)",
            "backend_scope": ("optix",),
            "remaining_app_specific_work": ("exact_distance", "nearest_neighbor_rows"),
            "public_wording_authorized": False,
            "boundary": "Hausdorff threshold-decision path only",
        },
        {
            "goal": "Goal1303",
            "app": "robot_collision_screening",
            "subpath": "prepared_count",
            "status": "pod_verified_generic",
            "generic_primitive": "ANY_HIT",
            "summary_primitive": "COUNT_HITS",
            "backend_scope": ("optix",),
            "remaining_app_specific_work": ("prepared_pose_flags", "grouped_pose_flag_reduction"),
            "public_wording_authorized": False,
            "boundary": "scalar hit-edge count only",
        },
        {
            "goal": "Goal1306",
            "app": "robot_collision_screening",
            "subpath": "prepared_pose_flags",
            "status": "pod_verified_generic",
            "generic_primitive": "ANY_HIT",
            "summary_primitive": "REDUCE_INT(COUNT)",
            "backend_scope": ("optix",),
            "remaining_app_specific_work": (),
            "public_wording_authorized": False,
            "boundary": "pose-level grouped count-to-boolean output only; no whole-app collision planning claim",
        },
        {
            "goal": "Goal1307",
            "app": "database_analytics",
            "subpath": "sales_risk_compact_summary",
            "status": "pod_verified_generic",
            "generic_primitive": "DB_COMPACT_SUMMARY",
            "summary_primitive": "REDUCE_INT(COUNT), REDUCE_INT(SUM)",
            "backend_scope": ACTIVE_V1_5_BACKENDS,
            "remaining_app_specific_work": (),
            "public_wording_authorized": False,
            "boundary": "sales-risk compact summary only; no SQL, DBMS, query planner, index, join, transaction, or row-output claim",
        },
        {
            "goal": "Goal1309",
            "app": "polygon_pair_overlap_area_rows",
            "subpath": "candidate_discovery_and_exact_area",
            "status": "pod_verified_generic",
            "generic_primitive": "POLYGON_PAIR_EXACT_AREA_SUMMARY",
            "summary_primitive": "REDUCE_FLOAT(SUM)",
            "backend_scope": ACTIVE_V1_5_BACKENDS,
            "remaining_app_specific_work": (),
            "public_wording_authorized": False,
            "boundary": "candidate discovery plus exact integer-grid area summary only; no generic overlay, broad GIS, or public speedup wording",
        },
        {
            "goal": "Goal1322",
            "app": "polygon_set_jaccard",
            "subpath": "chunked_candidate_scoring",
            "status": "pod_verified_generic",
            "generic_primitive": "COLLECT_K_BOUNDED",
            "summary_primitive": "REDUCE_FLOAT(SUM)",
            "backend_scope": ACTIVE_V1_5_BACKENDS,
            "remaining_app_specific_work": (),
            "public_wording_authorized": False,
            "boundary": "diagnostic native candidate-plus-backend-neutral area-summary pipeline; native bounded collection is pod-validated with no silent truncation; backend-neutral score reduction is pod-validated; OptiX remains slower than Embree; no public speedup wording; no fused GPU Jaccard kernel claim",
        },
    )


def v1_5_generic_migration_blockers() -> tuple[str, ...]:
    return (
        "app-level continuations remain outside v1.5 generic subpath scope where inventory rows name remaining_app_specific_work",
        "whole-app speedup wording remains blocked for graph, DB, polygon, ranking, clustering, SQL-style materialization, exact-distance rows, and force-vector reductions",
        "public NVIDIA wording remains blocked until exact-subpath evidence receives 3-AI consensus",
    )


def validate_v1_5_generic_migration_inventory() -> tuple[dict[str, Any], ...]:
    inventory = v1_5_generic_migration_inventory()
    _validate_v1_5_generic_migration_inventory_rows(inventory)
    return inventory


def _split_summary_primitives(value: Any) -> tuple[str, ...]:
    return tuple(part.strip() for part in str(value).split(",") if part.strip())


def _validate_v1_5_generic_migration_inventory_rows(inventory: tuple[dict[str, Any], ...]) -> None:
    valid_statuses = {
        "pod_verified_generic",
        "local_generic_pending_pod",
        "deferred_app_specific",
        "diagnostic_blocked",
    }
    valid_backend_scope = set(ACTIVE_V1_5_BACKENDS)
    valid_generic_primitives = set(V1_5_STABLE_GENERIC_PRIMITIVES) | set(
        V1_5_EXPERIMENTAL_GENERIC_PRIMITIVES
    )
    valid_summary_primitives = set(V1_5_STABLE_SUMMARY_PRIMITIVES)
    for row in inventory:
        for field in (
            "goal",
            "app",
            "subpath",
            "status",
            "generic_primitive",
            "summary_primitive",
            "backend_scope",
            "remaining_app_specific_work",
            "public_wording_authorized",
            "boundary",
        ):
            if field not in row:
                raise ValueError(f"missing v1.5 migration inventory field: {field}")
        if row["status"] not in valid_statuses:
            raise ValueError(f"invalid v1.5 migration status: {row['status']}")
        if row["generic_primitive"] not in valid_generic_primitives:
            raise ValueError(f"invalid v1.5 generic primitive: {row['generic_primitive']}")
        summary_primitives = _split_summary_primitives(row["summary_primitive"])
        if not summary_primitives:
            raise ValueError("summary_primitive must not be empty")
        invalid_summaries = [
            primitive for primitive in summary_primitives if primitive not in valid_summary_primitives
        ]
        if invalid_summaries:
            raise ValueError(
                f"invalid v1.5 summary primitive: {', '.join(invalid_summaries)}"
            )
        backend_scope = tuple(row["backend_scope"])
        if not backend_scope:
            raise ValueError("backend_scope must not be empty")
        if any(backend not in valid_backend_scope for backend in backend_scope):
            raise ValueError(f"invalid active v1.5 backend scope: {backend_scope}")
        if row["public_wording_authorized"]:
            raise ValueError("v1.5 migration inventory must not authorize public wording")

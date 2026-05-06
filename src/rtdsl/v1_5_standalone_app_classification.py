from __future__ import annotations

from typing import Any

from .app_support_matrix import public_apps


V1_5_STANDALONE_APP_CLASSIFICATIONS = (
    "fully_generic",
    "wrapper_backed",
    "scalar_only",
    "collection_dependent",
    "frozen",
    "demo_only",
)


def v1_5_standalone_app_classification_matrix() -> dict[str, dict[str, Any]]:
    """Return app-level standalone-v1.5 classification after Goal1397."""
    return {
        "database_analytics": {
            "classification": "wrapper_backed",
            "standalone_included": True,
            "generic_surface": "DB_COMPACT_SUMMARY + REDUCE_INT(COUNT|SUM)",
            "remaining_scope": ("SQL_DBMS_behavior", "row_materialization", "query_planner"),
            "release_boundary": "compact summary only; SQL/DBMS behavior remains outside standalone v1.5",
        },
        "graph_analytics": {
            "classification": "scalar_only",
            "standalone_included": True,
            "generic_surface": "ANY_HIT + COUNT_HITS",
            "remaining_scope": ("BFS_frontier_control", "triangle_set_intersection"),
            "release_boundary": "visibility any-hit/count only; graph-system analytics remain outside standalone v1.5",
        },
        "apple_rt_demo": {
            "classification": "demo_only",
            "standalone_included": False,
            "generic_surface": "none",
            "remaining_scope": ("apple_rt_frozen_before_v2_1",),
            "release_boundary": "Apple RT is a preserved demo/proof surface outside active standalone v1.5 scope",
        },
        "service_coverage_gaps": {
            "classification": "fully_generic",
            "standalone_included": True,
            "generic_surface": "FIXED_RADIUS_COUNT_THRESHOLD_2D + REDUCE_INT(COUNT)",
            "remaining_scope": (),
            "release_boundary": "fixed-radius gap summary only; no whole service-optimization claim",
        },
        "event_hotspot_screening": {
            "classification": "fully_generic",
            "standalone_included": True,
            "generic_surface": "FIXED_RADIUS_COUNT_THRESHOLD_2D + REDUCE_INT(COUNT)",
            "remaining_scope": (),
            "release_boundary": "fixed-radius hotspot count summary only; no whole hotspot analytics claim",
        },
        "facility_knn_assignment": {
            "classification": "scalar_only",
            "standalone_included": True,
            "generic_surface": "FIXED_RADIUS_COUNT_THRESHOLD_2D + REDUCE_INT(COUNT)",
            "remaining_scope": ("ranked_knn_assignment",),
            "release_boundary": "coverage-threshold decision only; ranked KNN remains outside standalone v1.5",
        },
        "road_hazard_screening": {
            "classification": "wrapper_backed",
            "standalone_included": True,
            "generic_surface": "segment/polygon compact count summary wrapper",
            "remaining_scope": ("GIS_routing", "row_output", "default_app_behavior"),
            "release_boundary": "compact hazard summary only; full GIS/routing remains outside standalone v1.5",
        },
        "segment_polygon_hitcount": {
            "classification": "wrapper_backed",
            "standalone_included": True,
            "generic_surface": "segment/polygon hit-count summary wrapper",
            "remaining_scope": ("pair_row_output",),
            "release_boundary": "compact hit-count summary only; pair-row output remains outside this class",
        },
        "segment_polygon_anyhit_rows": {
            "classification": "collection_dependent",
            "standalone_included": False,
            "generic_surface": "COLLECT_K_BOUNDED candidate rows",
            "remaining_scope": ("bounded_collection_resolution", "overflow_contract_evidence"),
            "release_boundary": "row-returning app is excluded unless COLLECT_K_BOUNDED promotion gates pass",
        },
        "polygon_pair_overlap_area_rows": {
            "classification": "wrapper_backed",
            "standalone_included": True,
            "generic_surface": "POLYGON_PAIR_EXACT_AREA_SUMMARY + REDUCE_FLOAT(SUM)",
            "remaining_scope": ("general_polygon_overlay",),
            "release_boundary": "candidate discovery plus exact-area summary only; broad overlay remains outside",
        },
        "polygon_set_jaccard": {
            "classification": "collection_dependent",
            "standalone_included": False,
            "generic_surface": "COLLECT_K_BOUNDED + REDUCE_FLOAT(SUM)",
            "remaining_scope": ("bounded_collection_resolution", "positive_speedup_evidence"),
            "release_boundary": "excluded unless COLLECT_K_BOUNDED promotion gates pass; no positive speedup claim",
        },
        "hausdorff_distance": {
            "classification": "scalar_only",
            "standalone_included": True,
            "generic_surface": "FIXED_RADIUS_COUNT_THRESHOLD_2D + REDUCE_INT(COUNT)",
            "remaining_scope": ("exact_distance", "nearest_neighbor_rows"),
            "release_boundary": "threshold decision only; exact Hausdorff rows remain outside standalone v1.5",
        },
        "ann_candidate_search": {
            "classification": "scalar_only",
            "standalone_included": True,
            "generic_surface": "FIXED_RADIUS_COUNT_THRESHOLD_2D + REDUCE_INT(COUNT)",
            "remaining_scope": ("ann_indexing", "nearest_neighbor_ranking"),
            "release_boundary": "candidate coverage decision only; full ANN ranking/indexing remains outside",
        },
        "outlier_detection": {
            "classification": "scalar_only",
            "standalone_included": True,
            "generic_surface": "FIXED_RADIUS_COUNT_THRESHOLD_2D + REDUCE_INT(COUNT)",
            "remaining_scope": ("neighbor_row_materialization", "per_point_labels"),
            "release_boundary": "density count summary only; row labels remain outside standalone v1.5",
        },
        "dbscan_clustering": {
            "classification": "scalar_only",
            "standalone_included": True,
            "generic_surface": "FIXED_RADIUS_COUNT_THRESHOLD_2D + REDUCE_INT(COUNT)",
            "remaining_scope": ("cluster_expansion", "connected_components"),
            "release_boundary": "core-count summary only; cluster expansion remains outside standalone v1.5",
        },
        "robot_collision_screening": {
            "classification": "wrapper_backed",
            "standalone_included": True,
            "generic_surface": "ANY_HIT + COUNT_HITS + REDUCE_INT(COUNT)",
            "remaining_scope": ("robot_kinematics", "witness_rows", "continuous_collision_detection"),
            "release_boundary": "prepared count/pose-flag summaries only; full robot planning remains outside",
        },
        "barnes_hut_force_app": {
            "classification": "scalar_only",
            "standalone_included": True,
            "generic_surface": "FIXED_RADIUS_COUNT_THRESHOLD_2D + REDUCE_INT(COUNT)",
            "remaining_scope": ("opening_rule", "force_vector_reduction"),
            "release_boundary": "node-coverage decision only; force-vector reduction remains outside",
        },
        "hiprt_ray_triangle_hitcount": {
            "classification": "frozen",
            "standalone_included": False,
            "generic_surface": "none",
            "remaining_scope": ("hiprt_frozen_before_v2_1",),
            "release_boundary": "HIPRT demo is frozen before v2.1 and excluded from standalone v1.5",
        },
    }


def validate_v1_5_standalone_app_classification_matrix() -> dict[str, dict[str, Any]]:
    matrix = v1_5_standalone_app_classification_matrix()
    expected_apps = set(public_apps())
    if set(matrix) != expected_apps:
        missing = sorted(expected_apps - set(matrix))
        extra = sorted(set(matrix) - expected_apps)
        raise ValueError(f"v1.5 standalone app classification mismatch: missing={missing}, extra={extra}")
    for app, row in matrix.items():
        for field in (
            "classification",
            "standalone_included",
            "generic_surface",
            "remaining_scope",
            "release_boundary",
        ):
            if field not in row:
                raise ValueError(f"missing v1.5 standalone app classification field: {app}.{field}")
        if row["classification"] not in V1_5_STANDALONE_APP_CLASSIFICATIONS:
            raise ValueError(f"invalid v1.5 standalone app classification: {app}")
        if not isinstance(row["standalone_included"], bool):
            raise ValueError(f"standalone_included must be boolean for {app}")
        if not row["generic_surface"]:
            raise ValueError(f"generic_surface must be non-empty for {app}")
        remaining_scope = tuple(row["remaining_scope"])
        boundary = str(row["release_boundary"])
        if row["classification"] in {"frozen", "demo_only"} and row["standalone_included"]:
            raise ValueError(f"frozen/demo app cannot be included in standalone v1.5: {app}")
        if row["classification"] == "collection_dependent" and row["standalone_included"]:
            raise ValueError(f"collection-dependent app cannot be included before collect-k resolution: {app}")
        if row["classification"] == "fully_generic" and remaining_scope:
            raise ValueError(f"fully generic app must not carry remaining scope: {app}")
        if remaining_scope and "outside" not in boundary and "excluded" not in boundary:
            raise ValueError(f"release boundary must constrain remaining scope for {app}")
        if row["classification"] == "collection_dependent" and "COLLECT_K_BOUNDED" not in row["generic_surface"]:
            raise ValueError(f"collection-dependent app must name COLLECT_K_BOUNDED: {app}")
    return matrix

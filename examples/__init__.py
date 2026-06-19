"""RTDL example package.

Current public examples live under ``examples.current``.  This package keeps a
small lazy compatibility map for older imports such as
``from examples import rtdl_hello_world`` while keeping the GitHub directory
view clean and versioned.
"""

from __future__ import annotations

import importlib
from types import ModuleType

_ALIASES = {
    "rtdl_hello_world": "examples.current.getting_started.rtdl_hello_world",
    "rtdl_hello_world_backends": "examples.current.getting_started.rtdl_hello_world_backends",
    "rtdl_feature_quickstart_cookbook": "examples.current.getting_started.rtdl_feature_quickstart_cookbook",
    "rtdl_prepared_measurement_demo": "examples.current.getting_started.rtdl_prepared_measurement_demo",
    "rtdl_primitive_discovery_workflow": "examples.current.getting_started.rtdl_primitive_discovery_workflow",
    "rtdl_partner_anyhit": "examples.current.partners.rtdl_partner_anyhit",
    "rtdl_control_apps_cupy_rawkernel": "examples.current.partners.rtdl_control_apps_cupy_rawkernel",
    "rtdl_hausdorff_user_cpp_continuation": "examples.current.partners.rtdl_hausdorff_user_cpp_continuation",
    "rtdl_ray_triangle_any_hit": "examples.current.features.ray_queries.rtdl_ray_triangle_any_hit",
    "rtdl_visibility_rows": "examples.current.features.ray_queries.rtdl_visibility_rows",
    "rtdl_reduce_rows": "examples.current.features.ray_queries.rtdl_reduce_rows",
    "rtdl_fixed_radius_neighbors": "examples.current.features.neighbors.rtdl_fixed_radius_neighbors",
    "rtdl_knn_rows": "examples.current.features.neighbors.rtdl_knn_rows",
    "rtdl_db_conjunctive_scan": "examples.current.features.database.rtdl_db_conjunctive_scan",
    "rtdl_db_grouped_count": "examples.current.features.database.rtdl_db_grouped_count",
    "rtdl_db_grouped_sum": "examples.current.features.database.rtdl_db_grouped_sum",
    "rtdl_graph_bfs": "examples.current.features.graph.rtdl_graph_bfs",
    "rtdl_graph_triangle_count": "examples.current.features.graph.rtdl_graph_triangle_count",
    "rtdl_segment_polygon_hitcount": "examples.current.features.spatial.rtdl_segment_polygon_hitcount",
    "rtdl_segment_polygon_anyhit_rows": "examples.current.features.spatial.rtdl_segment_polygon_anyhit_rows",
    "rtdl_polygon_pair_overlap_area_rows": "examples.current.features.spatial.rtdl_polygon_pair_overlap_area_rows",
    "rtdl_polygon_set_jaccard": "examples.current.features.spatial.rtdl_polygon_set_jaccard",
    "rtdl_database_analytics_app": "examples.current.apps.analytics.rtdl_database_analytics_app",
    "rtdl_graph_analytics_app": "examples.current.apps.analytics.rtdl_graph_analytics_app",
    "rtdl_service_coverage_gaps": "examples.current.apps.geospatial.rtdl_service_coverage_gaps",
    "rtdl_event_hotspot_screening": "examples.current.apps.geospatial.rtdl_event_hotspot_screening",
    "rtdl_facility_knn_assignment": "examples.current.apps.geospatial.rtdl_facility_knn_assignment",
    "rtdl_road_hazard_screening": "examples.current.apps.geospatial.rtdl_road_hazard_screening",
    "rtdl_sales_risk_screening": "examples.current.apps.geospatial.rtdl_sales_risk_screening",
    "rtdl_ann_candidate_app": "examples.current.apps.ml.rtdl_ann_candidate_app",
    "rtdl_outlier_detection_app": "examples.current.apps.ml.rtdl_outlier_detection_app",
    "rtdl_dbscan_clustering_app": "examples.current.apps.ml.rtdl_dbscan_clustering_app",
    "rtdl_robot_collision_screening_app": "examples.current.apps.robotics.rtdl_robot_collision_screening_app",
    "rtdl_barnes_hut_force_app": "examples.current.apps.simulation.rtdl_barnes_hut_force_app",
    "rtdl_continuous_frechet_distance_app": "examples.current.apps.trajectory.rtdl_continuous_frechet_distance_app",
    "rtdl_hausdorff_distance_app": "examples.current.research_benchmarks.hausdorff_xhd.rtdl_hausdorff_distance_app",
    "rtdl_hausdorff_v2_function": "examples.current.research_benchmarks.hausdorff_xhd.rtdl_hausdorff_v2_function",
    "rtdl_hausdorff_v2_language_lab": "examples.current.research_benchmarks.hausdorff_xhd.rtdl_hausdorff_v2_language_lab",
    "rtdl_hausdorff_v2_user_benchmark": "examples.current.research_benchmarks.hausdorff_xhd.rtdl_hausdorff_v2_user_benchmark",
    "rtdl_rayjoin_v2_spatial_join_app": "examples.current.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app",
    "rtdl_apple_rt_demo_app": "examples.legacy_or_backend_proofs.rtdl_apple_rt_demo_app",
    "rtdl_hiprt_ray_triangle_hitcount": "examples.legacy_or_backend_proofs.rtdl_hiprt_ray_triangle_hitcount",
}


def __getattr__(name: str) -> ModuleType:
    if name in _ALIASES:
        return importlib.import_module(_ALIASES[name])
    raise AttributeError(name)


__all__ = sorted(_ALIASES)

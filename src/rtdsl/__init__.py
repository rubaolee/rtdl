from __future__ import annotations
from .api import bounded_knn_rows
from .api import bfs_discover
from .api import compile_kernel
from .api import contains
from .api import conjunctive_scan
from .api import emit
from .api import fixed_radius_neighbors
from .api import grouped_count
from .api import grouped_sum
from .api import input
from .api import kernel
from .api import knn_rows
from .api import overlay_compose
from .api import point_nearest_segment
from .api import point_in_polygon
from .api import polygon_pair_overlap_area_rows
from .api import polygon_set_jaccard
from .api import ray_triangle_any_hit
from .api import ray_triangle_hit_count
from .api import ray_triangle_closest_hit
from .api import refine
from .api import segment_intersection
from .api import segment_polygon_anyhit_rows
from .api import segment_polygon_hitcount
from .api import triangle_match
from .api import traverse
from .adaptive_runtime import ADAPTIVE_BACKEND_NAME
from .adaptive_runtime import ADAPTIVE_COMPAT_MODE
from .adaptive_runtime import ADAPTIVE_NATIVE_RAY_HITCOUNT_3D_MODE
from .adaptive_runtime import adaptive_available
from .adaptive_runtime import adaptive_predicate_mode
from .adaptive_runtime import adaptive_support_matrix
from .adaptive_runtime import adaptive_version
from .adaptive_runtime import prepare_adaptive
from .adaptive_runtime import PreparedAdaptiveExecution
from .adaptive_runtime import run_adaptive
from .baseline_contracts import BASELINE_FLOAT_ABS_TOL
from .baseline_contracts import BASELINE_FLOAT_REL_TOL
from .baseline_contracts import BASELINE_PRECISION_MODE
from .baseline_contracts import BASELINE_WORKLOAD_ORDER
from .baseline_contracts import BASELINE_WORKLOADS
from .baseline_contracts import compare_baseline_rows
from .baseline_contracts import InputContract
from .baseline_contracts import validate_compiled_kernel_against_baseline
from .baseline_contracts import WorkloadContract
from .codegen import generate_optix_project
from .datasets import arcgis_pages_to_cdb
from .datasets import build_arcgis_geojson_query_url
from .datasets import build_arcgis_query_url
from .datasets import build_arcgis_layer_url
from .datasets import chains_to_polygons
from .datasets import chains_to_polygon_refs
from .datasets import chains_to_probe_points
from .datasets import chains_to_segments
from .datasets import CdbChain
from .datasets import CdbDataset
from .datasets import CdbPoint
from .datasets import download_rayjoin_sample
from .datasets import count_arcgis_loaded_pages
from .datasets import load_arcgis_feature_pages
from .datasets import load_cdb
from .datasets import load_natural_earth_populated_places_geojson
from .datasets import load_overpass_elements
from .datasets import overpass_elements_stats
from .datasets import overpass_elements_to_cdb
from .datasets import OverpassElementStats
from .datasets import parse_cdb_text
from .datasets import RayJoinBoundedPlan
from .datasets import RayJoinFeatureServiceLayer
from .datasets import rayjoin_bounded_plans
from .datasets import rayjoin_feature_service_layers
from .datasets import RayJoinPublicAsset
from .datasets import rayjoin_public_assets
from .datasets import slice_cdb_dataset
from .datasets import write_cdb
from .embree_runtime import embree_version
from .engine_feature_matrix import assert_engine_feature_supported
from .engine_feature_matrix import engine_feature_support
from .engine_feature_matrix import engine_feature_support_matrix
from .engine_feature_matrix import ENGINE_SUPPORT_STATUSES
from .engine_feature_matrix import public_engine_features
from .engine_feature_matrix import RTDL_ENGINES
from .app_support_matrix import app_engine_support
from .app_support_matrix import (
    OPTIX_APP_PERFORMANCE_CLASSES,
    app_engine_support_matrix,
    optix_app_performance_matrix,
    optix_app_performance_support,
)
from .app_support_matrix import APP_ENGINES
from .app_support_matrix import APP_SUPPORT_STATUSES
from .app_support_matrix import public_apps
from .apple_rt_runtime import apple_rt_context_probe
from .apple_rt_runtime import apple_rt_compute_u32_add
from .apple_rt_runtime import apple_rt_predicate_mode
from .apple_rt_runtime import apple_rt_support_matrix
from .apple_rt_runtime import apple_rt_version
from .apple_rt_runtime import AppleRtRay2DBuffer
from .apple_rt_runtime import AppleRtRowView
from .apple_rt_runtime import bfs_discover_apple_rt
from .apple_rt_runtime import conjunctive_scan_apple_rt
from .apple_rt_runtime import fixed_radius_neighbors_2d_apple_rt
from .apple_rt_runtime import fixed_radius_neighbors_3d_apple_rt
from .apple_rt_runtime import grouped_count_apple_rt
from .apple_rt_runtime import grouped_sum_apple_rt
from .apple_rt_runtime import overlay_compose_apple_rt
from .apple_rt_runtime import PreparedAppleRtRayTriangleAnyHit2D
from .apple_rt_runtime import PreparedAppleRtRayTriangleClosestHit3D
from .apple_rt_runtime import point_in_polygon_full_matrix_apple_rt
from .apple_rt_runtime import point_in_polygon_positive_hits_apple_rt
from .apple_rt_runtime import point_nearest_segment_apple_rt
from .apple_rt_runtime import polygon_pair_overlap_area_rows_apple_rt
from .apple_rt_runtime import polygon_set_jaccard_apple_rt
from .apple_rt_runtime import prepare_apple_rt_ray_triangle_any_hit_2d
from .apple_rt_runtime import prepare_apple_rt_ray_triangle_closest_hit
from .apple_rt_runtime import prepare_apple_rt_rays_2d
from .apple_rt_runtime import ray_triangle_any_hit_apple_rt
from .apple_rt_runtime import ray_triangle_closest_hit_apple_rt
from .apple_rt_runtime import ray_triangle_hit_count_apple_rt
from .apple_rt_runtime import run_apple_rt
from .apple_rt_runtime import segment_intersection_apple_rt
from .apple_rt_runtime import segment_polygon_anyhit_rows_apple_rt
from .apple_rt_runtime import segment_polygon_hitcount_apple_rt
from .apple_rt_runtime import triangle_match_apple_rt
from .external_baselines import build_postgis_fixed_radius_neighbors_sql
from .external_baselines import build_postgis_fixed_radius_neighbors_3d_sql
from .external_baselines import build_postgis_bounded_knn_rows_3d_sql
from .external_baselines import build_postgis_knn_rows_sql
from .external_baselines import build_postgis_knn_rows_3d_sql
from .external_baselines import connect_postgis
from .external_baselines import postgis_available
from .external_baselines import run_postgis_fixed_radius_neighbors
from .external_baselines import run_postgis_fixed_radius_neighbors_3d
from .external_baselines import run_postgis_bounded_knn_rows_3d
from .external_baselines import run_postgis_knn_rows
from .external_baselines import run_postgis_knn_rows_3d
from .external_baselines import run_scipy_fixed_radius_neighbors
from .external_baselines import run_scipy_knn_rows
from .external_baselines import scipy_available
from .optix_runtime import optix_version
from .optix_runtime import fixed_radius_count_threshold_2d_optix
from .optix_runtime import OptixRay2DBuffer
from .optix_runtime import OptixRowView
from .optix_runtime import prepare_optix
from .optix_runtime import prepare_optix_db_dataset
from .optix_runtime import prepare_optix_ray_triangle_any_hit_2d
from .optix_runtime import prepare_optix_rays_2d
from .optix_runtime import PreparedOptixDbDataset
from .optix_runtime import PreparedOptixExecution
from .optix_runtime import PreparedOptixKernel
from .optix_runtime import PreparedOptixRayTriangleAnyHit2D
from .optix_runtime import run_optix
from .reduction_runtime import reduce_rows
from .hiprt_runtime import fixed_radius_neighbors_2d_hiprt
from .hiprt_runtime import fixed_radius_neighbors_3d_hiprt
from .hiprt_runtime import bfs_expand_hiprt
from .hiprt_runtime import conjunctive_scan_hiprt
from .hiprt_runtime import grouped_count_hiprt
from .hiprt_runtime import grouped_sum_hiprt
from .hiprt_runtime import hiprt_context_probe
from .hiprt_runtime import hiprt_version
from .hiprt_runtime import knn_rows_2d_hiprt
from .hiprt_runtime import overlay_compose_hiprt
from .hiprt_runtime import prepare_hiprt_db_table
from .hiprt_runtime import prepare_hiprt_ray_triangle_any_hit_2d
from .hiprt_runtime import prepare_hiprt_ray_triangle_hit_count
from .hiprt_runtime import prepare_hiprt_fixed_radius_neighbors_3d
from .hiprt_runtime import prepare_hiprt_graph_csr
from .hiprt_runtime import prepare_hiprt
from .hiprt_runtime import PreparedHiprtDbKernel
from .hiprt_runtime import PreparedHiprtDbTable
from .hiprt_runtime import PreparedHiprtFixedRadiusNeighbors3D
from .hiprt_runtime import PreparedHiprtFixedRadiusKernel
from .hiprt_runtime import PreparedHiprtGraphCSR
from .hiprt_runtime import PreparedHiprtGraphKernel
from .hiprt_runtime import PreparedHiprtKernel
from .hiprt_runtime import PreparedHiprtRayTriangleAnyHit2D
from .hiprt_runtime import PreparedHiprtRayTriangleHitCount3D
from .hiprt_runtime import ray_triangle_any_hit_hiprt
from .hiprt_runtime import ray_triangle_hit_count_hiprt
from .hiprt_runtime import run_hiprt
from .hiprt_runtime import segment_polygon_anyhit_rows_hiprt
from .hiprt_runtime import segment_polygon_hitcount_hiprt
from .hiprt_runtime import triangle_match_hiprt
from .vulkan_runtime import vulkan_version
from .vulkan_runtime import VulkanRowView
from .vulkan_runtime import prepare_vulkan
from .vulkan_runtime import prepare_vulkan_db_dataset
from .vulkan_runtime import prepare_vulkan_ray_triangle_any_hit_2d
from .vulkan_runtime import PreparedVulkanDbDataset
from .vulkan_runtime import PreparedVulkanExecution
from .vulkan_runtime import PreparedVulkanKernel
from .vulkan_runtime import PreparedVulkanRayTriangleAnyHit2D
from .vulkan_runtime import run_vulkan
from .embree_runtime import EmbreeRowView
from .embree_runtime import pack_points
from .embree_runtime import pack_polygons
from .embree_runtime import pack_rays
from .embree_runtime import pack_segments
from .embree_runtime import pack_triangles
from .embree_runtime import PackedPoints
from .embree_runtime import PackedPolygons
from .embree_runtime import PackedRays
from .embree_runtime import PackedSegments
from .embree_runtime import PackedTriangles
from .embree_runtime import prepare_embree
from .embree_runtime import prepare_embree_db_dataset
from .embree_runtime import PreparedEmbreeDbDataset
from .embree_runtime import PreparedEmbreeExecution
from .embree_runtime import PreparedEmbreeKernel
from .embree_runtime import run_embree
from .evaluation_matrix import evaluation_entries
from .evaluation_matrix import EMBREE_EVALUATION_MATRIX
from .generate_only import generate_python_program
from .generate_only import generate_handoff_bundle
from .generate_only import GenerateOnlyRequest
from .generate_only import render_python_program
from .goal23_reproduction import generate_goal23_artifacts
from .goal23_reproduction import run_goal23_reproduction
from .goal112_segment_polygon_perf import render_goal112_markdown
from .goal112_segment_polygon_perf import run_goal112_segment_polygon_perf
from .goal112_segment_polygon_perf import write_goal112_artifacts
from .goal114_segment_polygon_postgis import render_goal114_markdown
from .goal114_segment_polygon_postgis import run_goal114_segment_polygon_postgis_validation
from .goal114_segment_polygon_postgis import segment_polygon_large_dataset_name
from .goal114_segment_polygon_postgis import write_goal114_artifacts
from .goal116_segment_polygon_backend_audit import render_goal116_markdown
from .goal116_segment_polygon_backend_audit import run_goal116_segment_polygon_backend_audit
from .goal116_segment_polygon_backend_audit import write_goal116_artifacts
from .goal118_segment_polygon_linux_large_perf import render_goal118_markdown
from .goal118_segment_polygon_linux_large_perf import run_goal118_segment_polygon_linux_large_perf
from .goal118_segment_polygon_linux_large_perf import write_goal118_artifacts
from .goal128_segment_polygon_anyhit_postgis import render_goal128_linux_markdown
from .goal128_segment_polygon_anyhit_postgis import render_goal128_postgis_markdown
from .goal128_segment_polygon_anyhit_postgis import run_goal128_segment_polygon_anyhit_linux_large_perf
from .goal128_segment_polygon_anyhit_postgis import run_goal128_segment_polygon_anyhit_postgis_validation
from .goal128_segment_polygon_anyhit_postgis import write_goal128_linux_artifacts
from .goal128_segment_polygon_anyhit_postgis import write_goal128_postgis_artifacts
from .goal138_polygon_overlap_postgis import render_goal138_markdown
from .goal138_polygon_overlap_postgis import run_goal138_polygon_overlap_postgis_validation
from .goal138_polygon_overlap_postgis import run_postgis_polygon_pair_overlap_area_rows
from .goal138_polygon_overlap_postgis import write_goal138_artifacts
from .goal139_pathology_data import describe_download_boundary
from .goal139_pathology_data import direct_download_allowed
from .goal139_pathology_data import download_nuinsseg_zip
from .goal139_pathology_data import load_monuseg_xml_annotations
from .goal139_pathology_data import monuseg_drive_file_id
from .goal139_pathology_data import parse_monuseg_xml_annotations
from .goal139_pathology_data import public_pathology_datasets
from .goal139_pathology_data import render_goal139_markdown
from .goal139_pathology_data import write_goal139_artifacts
from .goal139_pathology_data import write_public_pathology_manifest
from .goal140_polygon_set_jaccard_postgis import render_goal140_markdown
from .goal140_polygon_set_jaccard_postgis import run_goal140_polygon_set_jaccard_postgis_validation
from .goal140_polygon_set_jaccard_postgis import run_postgis_polygon_set_jaccard
from .goal140_polygon_set_jaccard_postgis import write_goal140_artifacts
from .goal141_public_jaccard_audit import build_goal141_public_case
from .goal141_public_jaccard_audit import download_monuseg_training_zip
from .goal141_public_jaccard_audit import list_monuseg_training_xml_names
from .goal141_public_jaccard_audit import load_monuseg_training_xml_annotations
from .goal141_public_jaccard_audit import monuseg_polygons_to_unit_square_polygons
from .goal141_public_jaccard_audit import MONUSEG_DEFAULT_XML
from .goal141_public_jaccard_audit import render_goal141_markdown
from .goal141_public_jaccard_audit import run_goal141_public_jaccard_audit
from .goal141_public_jaccard_audit import run_postgis_polygon_set_jaccard_for_case
from .goal141_public_jaccard_audit import tile_polygon_set
from .goal141_public_jaccard_audit import write_goal141_artifacts
from .goal146_jaccard_linux_stress import render_goal146_markdown
from .goal146_jaccard_linux_stress import run_goal146_jaccard_linux_stress
from .goal146_jaccard_linux_stress import write_goal146_artifacts
from .ir import CandidateSet
from .ir import CompiledKernel
from .ir import EmitOp
from .ir import GeometryInput
from .ir import LaunchParam
from .ir import OutputRecord
from .ir import PayloadRegister
from .ir import Predicate
from .ir import RayJoinPlan
from .ir import RTExecutionPlan
from .ir import RefineOp
from .lowering import lower_to_execution_plan
from .lowering import lower_to_rayjoin
from .oracle_runtime import oracle_version
from .plan_schema import load_plan_schema
from .plan_schema import schema_path
from .plan_schema import validate_plan_dict
from .paper_reproduction import paper_targets
from .paper_reproduction import dataset_families
from .paper_reproduction import local_profiles
from .paper_reproduction import PaperTarget
from .paper_reproduction import RAYJOIN_PAPER_TARGETS
from .rtnn_baselines import rtnn_baseline_decisions
from .rtnn_baselines import rtnn_baseline_libraries
from .rtnn_baselines import RtnnBaselineDecision
from .rtnn_baselines import RtnnBaselineLibrary
from .rtnn_cunsearch import cunsearch_adapter_config
from .rtnn_cunsearch import cunsearch_available
from .rtnn_cunsearch import load_cunsearch_fixed_radius_response
from .rtnn_cunsearch import plan_cunsearch_fixed_radius_neighbors
from .rtnn_cunsearch import resolve_cunsearch_binary
from .rtnn_cunsearch import write_cunsearch_fixed_radius_request
from .rtnn_cunsearch import CuNSearchAdapterConfig
from .rtnn_cunsearch import CuNSearchFixedRadiusResult
from .rtnn_cunsearch import CuNSearchInvocationPlan
from .rtnn_cunsearch_live import resolve_cunsearch_build_config
from .rtnn_cunsearch_live import run_cunsearch_fixed_radius_request_live
from .rtnn_cunsearch_live import compile_cunsearch_fixed_radius_request_driver
from .rtnn_cunsearch_live import execute_compiled_cunsearch_fixed_radius_driver
from .rtnn_cunsearch_live import CuNSearchBuildConfig
from .rtnn_comparison import compare_bounded_fixed_radius_from_packages
from .rtnn_comparison import compare_bounded_fixed_radius_live_cunsearch
from .rtnn_comparison import RtnnBoundedComparisonResult
from .rtnn_duplicate_audit import assess_cunsearch_duplicate_point_guard
from .rtnn_duplicate_audit import CuNSearchDuplicatePointGuardResult
from .rtnn_duplicate_audit import ExactCrossPackageMatch
from .rtnn_duplicate_audit import find_exact_cross_package_matches
from .rtnn_perf_audit import FixedRadiusMismatchSummary
from .rtnn_perf_audit import summarize_fixed_radius_mismatch
from .rtnn_kitti import discover_kitti_velodyne_frames
from .rtnn_kitti import kitti_source_config
from .rtnn_kitti import load_kitti_bounded_points_from_manifest
from .rtnn_kitti import load_kitti_bounded_point_package
from .rtnn_kitti import resolve_kitti_source_root
from .rtnn_kitti import select_kitti_bounded_frames
from .rtnn_kitti import write_kitti_bounded_package_manifest
from .rtnn_kitti import write_kitti_bounded_point_package
from .rtnn_kitti import KittiBoundedPointPackage
from .rtnn_kitti import KittiFrameRecord
from .rtnn_kitti import KittiSourceConfig
from .rtnn_kitti_ready import inspect_kitti_linux_source_root
from .rtnn_kitti_ready import write_kitti_linux_ready_report
from .rtnn_kitti_ready import KittiLinuxReadyReport
from .rtnn_kitti_selector import find_duplicate_free_kitti_pair
from .rtnn_kitti_selector import KittiDuplicateFreePair
from .rtnn_manifests import rtnn_bounded_dataset_manifests
from .rtnn_manifests import write_rtnn_bounded_dataset_manifest
from .rtnn_manifests import RtnnBoundedDatasetManifest
from .rtnn_matrix import rtnn_reproduction_matrix
from .rtnn_matrix import RtnnMatrixEntry
from .rtnn_reproduction import rtnn_dataset_families
from .rtnn_reproduction import rtnn_experiment_targets
from .rtnn_reproduction import rtnn_local_profiles
from .rtnn_reproduction import RtnnDatasetFamily
from .rtnn_reproduction import RtnnExperimentTarget
from .rtnn_reproduction import RtnnLocalProfile
from .reference import bounded_knn_rows_cpu
from .reference import fixed_radius_neighbors_cpu
from .reference import knn_rows_cpu
from .reference import lsi_cpu
from .reference import overlay_compose_cpu
from .reference import point_nearest_segment_cpu
from .reference import pip_cpu
from .reference import Point
from .reference import Point3D
from .reference import Polygon
from .reference import polygon_pair_overlap_area_rows_cpu
from .reference import polygon_set_jaccard_cpu
from .reference import Ray2D
from .reference import Ray3D
from .reference import ray_triangle_hit_count_cpu
from .reference import ray_triangle_any_hit_cpu
from .reference import ray_triangle_closest_hit_cpu
from .reference import Segment
from .reference import segment_polygon_anyhit_rows_cpu
from .reference import segment_polygon_hitcount_cpu
from .reference import Triangle
from .reference import Triangle3D
from .reference import visibility_ray_pairs
from .reference import visibility_rows_cpu
from .reference import visibility_rows_from_any_hit
from .visibility_runtime import visibility_rows
from .graph_reference import bfs_expand_cpu
from .db_reference import conjunctive_scan_cpu
from .db_reference import grouped_count_cpu
from .db_reference import grouped_sum_cpu
from .db_reference import GroupedAggregateQuery
from .db_reference import normalize_denorm_table
from .db_reference import normalize_grouped_query
from .db_reference import normalize_predicate_bundle
from .db_reference import PredicateBundle
from .db_reference import PredicateClause
from .graph_reference import csr_graph
from .graph_reference import CSRGraph
from .graph_postgresql import build_postgresql_bfs_expand_sql
from .graph_postgresql import build_postgresql_triangle_probe_sql
from .graph_postgresql import connect_postgresql
from .graph_postgresql import postgresql_available
from .graph_postgresql import prepare_postgresql_bfs_inputs
from .graph_postgresql import prepare_postgresql_graph_tables
from .graph_postgresql import prepare_postgresql_triangle_inputs
from .graph_postgresql import query_postgresql_bfs_expand
from .graph_postgresql import query_postgresql_triangle_probe
from .graph_postgresql import run_postgresql_bfs_expand
from .graph_postgresql import run_postgresql_triangle_probe
from .db_postgresql import build_postgresql_conjunctive_scan_sql
from .db_postgresql import build_postgresql_grouped_count_sql
from .db_postgresql import build_postgresql_grouped_sum_sql
from .db_postgresql import FakePostgresqlConnection
from .db_postgresql import prepare_postgresql_denorm_table
from .db_postgresql import query_postgresql_conjunctive_scan
from .db_postgresql import query_postgresql_grouped_count
from .db_postgresql import query_postgresql_grouped_sum
from .db_postgresql import run_postgresql_conjunctive_scan
from .db_postgresql import run_postgresql_grouped_count
from .db_postgresql import run_postgresql_grouped_sum
from .graph_datasets import graph_dataset_candidates
from .graph_datasets import graph_dataset_spec
from .graph_datasets import GraphDatasetSpec
from .graph_datasets import load_snap_edge_list_graph
from .graph_datasets import load_snap_simple_undirected_graph
from .graph_reference import EdgeSeed
from .graph_reference import FrontierVertex
from .graph_reference import triangle_probe_cpu
from .graph_reference import validate_csr_graph
from .section_5_6_scalability import generate_section_5_6_artifacts
from .section_5_6_scalability import generate_synthetic_polygons
from .section_5_6_scalability import polygon_probe_points
from .section_5_6_scalability import polygons_to_segments
from .section_5_6_scalability import run_section_5_6
from .section_5_6_scalability import ScalabilityConfig
from .runtime import run_cpu
from .runtime import run_cpu_python_reference
from .layout_types import f32
from .layout_types import DenormTable
from .layout_types import DenormTableLayout
from .layout_types import EdgeSet
from .layout_types import EdgeSetLayout
from .layout_types import field
from .layout_types import GraphCSR
from .layout_types import GraphCSRLayout
from .layout_types import GeometryType
from .layout_types import GroupedQuery
from .layout_types import GroupedQueryLayout
from .layout_types import layout
from .layout_types import Layout
from .layout_types import Points
from .layout_types import Point2DLayout
from .layout_types import Point3DLayout
from .layout_types import Points3D
from .layout_types import Polygons
from .layout_types import Polygon2DLayout
from .layout_types import Rays
from .layout_types import Ray2DLayout
from .layout_types import Ray3DLayout
from .layout_types import Rays3D
from .layout_types import Segment2DLayout
from .layout_types import Segments
from .layout_types import Triangle2DLayout
from .layout_types import Triangles
from .layout_types import Triangle3DLayout
from .layout_types import Triangles3D
from .layout_types import u32
from .layout_types import PredicateSet
from .layout_types import PredicateSetLayout
from .layout_types import VertexFrontier
from .layout_types import VertexFrontierLayout
from .layout_types import VertexSet
from .layout_types import VertexSetLayout


def infer_workload(kernel_fn_or_compiled):
    from .baseline_runner import infer_workload as _infer_workload

    return _infer_workload(kernel_fn_or_compiled)


def representative_dataset_names(workload: str):
    from .baseline_runner import representative_dataset_names as _representative_dataset_names

    return _representative_dataset_names(workload)


def run_baseline_case(kernel_fn_or_compiled, dataset: str, backend: str = "both", *, postgis_dsn: str | None = None):
    from .baseline_runner import run_baseline_case as _run_baseline_case

    return _run_baseline_case(kernel_fn_or_compiled, dataset, backend=backend, postgis_dsn=postgis_dsn)


def run_baseline_benchmark(*, workloads, backends, iterations: int, warmup: int):
    from .baseline_benchmark import run_benchmark as _run_benchmark

    return _run_benchmark(
        workloads=workloads,
        backends=backends,
        iterations=iterations,
        warmup=warmup,
    )


def write_baseline_benchmark_json(payload, output_path):
    from .baseline_benchmark import write_benchmark_json as _write_benchmark_json

    return _write_benchmark_json(payload, output_path)


def summarize_baseline_benchmark(payload):
    from .baseline_summary import summarize_benchmark as _summarize_benchmark

    return _summarize_benchmark(payload)


def generate_embree_evaluation_artifacts(*, workloads=None, iterations: int = 5, warmup: int = 1, output_dir=None):
    from .evaluation_report import generate_evaluation_artifacts as _generate_evaluation_artifacts

    return _generate_evaluation_artifacts(
        workloads=workloads,
        iterations=iterations,
        warmup=warmup,
        output_dir=output_dir,
    )

__all__ = [
    "CdbChain",
    "CdbDataset",
    "CdbPoint",
    "BASELINE_FLOAT_ABS_TOL",
    "BASELINE_FLOAT_REL_TOL",
    "EMBREE_EVALUATION_MATRIX",
    "BASELINE_PRECISION_MODE",
    "BASELINE_WORKLOAD_ORDER",
    "BASELINE_WORKLOADS",
    "bounded_knn_rows",
    "bounded_knn_rows_cpu",
    "bfs_discover",
    "bfs_discover_apple_rt",
    "bfs_expand_cpu",
    "CandidateSet",
    "CompiledKernel",
    "contains",
    "conjunctive_scan",
    "conjunctive_scan_apple_rt",
    "conjunctive_scan_hiprt",
    "conjunctive_scan_cpu",
    "csr_graph",
    "CSRGraph",
    "DenormTable",
    "DenormTableLayout",
    "EdgeSeed",
    "EdgeSet",
    "EdgeSetLayout",
    "EmitOp",
    "FrontierVertex",
    "GraphCSR",
    "GraphCSRLayout",
    "GraphDatasetSpec",
    "GeometryInput",
    "GeometryType",
    "GenerateOnlyRequest",
    "GroupedAggregateQuery",
    "GroupedQuery",
    "GroupedQueryLayout",
    "grouped_count",
    "grouped_count_cpu",
    "grouped_count_apple_rt",
    "grouped_count_hiprt",
    "grouped_sum",
    "grouped_sum_cpu",
    "grouped_sum_apple_rt",
    "grouped_sum_hiprt",
    "hiprt_context_probe",
    "hiprt_version",
    "InputContract",
    "LaunchParam",
    "Layout",
    "overlay_compose",
    "overlay_compose_hiprt",
    "oracle_version",
    "point_nearest_segment",
    "polygon_pair_overlap_area_rows",
    "polygon_set_jaccard",
    "prepare_hiprt",
    "prepare_hiprt_db_table",
    "prepare_hiprt_fixed_radius_neighbors_3d",
    "prepare_hiprt_graph_csr",
    "prepare_hiprt_ray_triangle_hit_count",
    "PreparedHiprtDbKernel",
    "PreparedHiprtDbTable",
    "PreparedHiprtFixedRadiusKernel",
    "PreparedHiprtFixedRadiusNeighbors3D",
    "PreparedHiprtGraphCSR",
    "PreparedHiprtGraphKernel",
    "PreparedHiprtKernel",
    "OutputRecord",
    "OverpassElementStats",
    "PaperTarget",
    "PackedPoints",
    "PackedPolygons",
    "PackedRays",
    "PackedSegments",
    "PackedTriangles",
    "PayloadRegister",
    "Points",
    "Point2DLayout",
    "Point3DLayout",
    "Polygons",
    "Polygon2DLayout",
    "point_in_polygon",
    "point_in_polygon_positive_hits_apple_rt",
    "Predicate",
    "PredicateBundle",
    "PredicateClause",
    "PredicateSet",
    "PredicateSetLayout",
    "Rays",
    "Ray2D",
    "Ray2DLayout",
    "Ray3D",
    "Ray3DLayout",
    "Rays3D",
    "RayJoinPlan",
    "RTExecutionPlan",
    "RayJoinBoundedPlan",
    "RayJoinFeatureServiceLayer",
    "RayJoinPublicAsset",
    "RefineOp",
    "Segment2DLayout",
    "Segments",
    "triangle_match",
    "triangle_probe_cpu",
    "Triangles",
    "Triangle",
    "Triangle2DLayout",
    "Triangle3D",
    "Triangle3DLayout",
    "Triangles3D",
    "validate_csr_graph",
    "visibility_rows_cpu",
    "visibility_rows",
    "visibility_ray_pairs",
    "visibility_rows_from_any_hit",
    "VertexFrontier",
    "VertexFrontierLayout",
    "VertexSet",
    "VertexSetLayout",
    "compile_kernel",
    "dataset_families",
    "compare_baseline_rows",
    "evaluation_entries",
    "infer_workload",
    "arcgis_pages_to_cdb",
    "ADAPTIVE_BACKEND_NAME",
    "ADAPTIVE_COMPAT_MODE",
    "ADAPTIVE_NATIVE_RAY_HITCOUNT_3D_MODE",
    "adaptive_available",
    "adaptive_predicate_mode",
    "adaptive_support_matrix",
    "adaptive_version",
    "assert_engine_feature_supported",
    "build_arcgis_geojson_query_url",
    "build_arcgis_query_url",
    "build_arcgis_layer_url",
    "chains_to_polygons",
    "chains_to_polygon_refs",
    "chains_to_probe_points",
    "chains_to_segments",
    "count_arcgis_loaded_pages",
    "download_rayjoin_sample",
    "build_postgis_fixed_radius_neighbors_sql",
    "build_postgis_fixed_radius_neighbors_3d_sql",
    "build_postgis_bounded_knn_rows_3d_sql",
    "build_postgis_knn_rows_sql",
    "build_postgis_knn_rows_3d_sql",
    "build_postgresql_conjunctive_scan_sql",
    "build_postgresql_grouped_count_sql",
    "build_postgresql_grouped_sum_sql",
    "connect_postgis",
    "connect_postgresql",
    "FakePostgresqlConnection",
    "bfs_expand_hiprt",
    "fixed_radius_neighbors_2d_hiprt",
    "fixed_radius_neighbors_2d_apple_rt",
    "fixed_radius_neighbors_3d_apple_rt",
    "fixed_radius_neighbors_3d_hiprt",
    "fixed_radius_neighbors_cpu",
    "knn_rows_cpu",
    "EmbreeRowView",
    "embree_version",
    "OptixRowView",
    "optix_version",
    "OptixRay2DBuffer",
    "prepare_optix",
    "prepare_optix_db_dataset",
    "prepare_optix_ray_triangle_any_hit_2d",
    "prepare_optix_rays_2d",
    "PreparedOptixDbDataset",
    "PreparedOptixExecution",
    "PreparedOptixKernel",
    "PreparedOptixRayTriangleAnyHit2D",
    "run_optix",
    "triangle_match_apple_rt",
    "triangle_match_hiprt",
    "VulkanRowView",
    "vulkan_version",
    "prepare_vulkan",
    "prepare_vulkan_db_dataset",
    "prepare_vulkan_ray_triangle_any_hit_2d",
    "PreparedVulkanDbDataset",
    "PreparedVulkanExecution",
    "PreparedVulkanKernel",
    "PreparedVulkanRayTriangleAnyHit2D",
    "run_vulkan",
    "emit",
    "f32",
    "field",
    "generate_section_5_6_artifacts",
    "render_goal118_markdown",
    "render_goal128_linux_markdown",
    "render_goal128_postgis_markdown",
    "render_goal138_markdown",
    "render_goal139_markdown",
    "render_goal140_markdown",
    "render_goal141_markdown",
    "run_goal118_segment_polygon_linux_large_perf",
    "run_goal128_segment_polygon_anyhit_linux_large_perf",
    "run_goal128_segment_polygon_anyhit_postgis_validation",
    "run_goal138_polygon_overlap_postgis_validation",
    "run_goal140_polygon_set_jaccard_postgis_validation",
    "run_goal141_public_jaccard_audit",
    "run_hiprt",
    "run_postgis_polygon_pair_overlap_area_rows",
    "run_postgis_polygon_set_jaccard",
    "run_postgis_polygon_set_jaccard_for_case",
    "write_goal118_artifacts",
    "write_goal128_linux_artifacts",
    "write_goal128_postgis_artifacts",
    "write_goal138_artifacts",
    "write_goal139_artifacts",
    "write_goal140_artifacts",
    "write_goal141_artifacts",
    "write_public_pathology_manifest",
    "generate_synthetic_polygons",
    "generate_optix_project",
    "generate_goal23_artifacts",
    "generate_embree_evaluation_artifacts",
    "render_goal112_markdown",
    "render_goal114_markdown",
    "render_goal116_markdown",
    "run_goal112_segment_polygon_perf",
    "run_goal114_segment_polygon_postgis_validation",
    "run_goal116_segment_polygon_backend_audit",
    "generate_handoff_bundle",
    "generate_python_program",
    "graph_dataset_candidates",
    "graph_dataset_spec",
    "render_python_program",
    "input",
    "kernel",
    "knn_rows",
    "knn_rows_2d_hiprt",
    "layout",
    "load_arcgis_feature_pages",
    "load_cdb",
    "load_natural_earth_populated_places_geojson",
    "load_snap_edge_list_graph",
    "load_snap_simple_undirected_graph",
    "load_overpass_elements",
    "local_profiles",
    "overpass_elements_stats",
    "overpass_elements_to_cdb",
    "paper_targets",
    "pack_points",
    "pack_polygons",
    "pack_rays",
    "pack_segments",
    "pack_triangles",
    "lower_to_execution_plan",
    "lower_to_rayjoin",
    "load_plan_schema",
    "lsi_cpu",
    "overlay_compose_apple_rt",
    "overlay_compose_cpu",
    "parse_cdb_text",
    "postgis_available",
    "postgresql_available",
    "pip_cpu",
    "Point",
    "point_in_polygon_full_matrix_apple_rt",
    "point_nearest_segment_cpu",
    "point_nearest_segment_apple_rt",
    "polygon_probe_points",
    "Polygon",
    "polygon_pair_overlap_area_rows_apple_rt",
    "polygon_pair_overlap_area_rows_cpu",
    "polygon_set_jaccard_apple_rt",
    "polygon_set_jaccard_cpu",
    "polygons_to_segments",
    "MONUSEG_DEFAULT_XML",
    "monuseg_polygons_to_unit_square_polygons",
    "list_monuseg_training_xml_names",
    "load_monuseg_training_xml_annotations",
    "download_monuseg_training_zip",
    "build_goal141_public_case",
    "prepare_embree",
    "prepare_adaptive",
    "apple_rt_context_probe",
    "apple_rt_compute_u32_add",
    "apple_rt_predicate_mode",
    "apple_rt_support_matrix",
    "apple_rt_version",
    "AppleRtRay2DBuffer",
    "AppleRtRowView",
    "PreparedAppleRtRayTriangleAnyHit2D",
    "PreparedAppleRtRayTriangleClosestHit3D",
    "prepare_apple_rt_ray_triangle_any_hit_2d",
    "prepare_apple_rt_ray_triangle_closest_hit",
    "prepare_apple_rt_rays_2d",
    "prepare_embree_db_dataset",
    "prepare_postgresql_denorm_table",
    "PreparedEmbreeDbDataset",
    "PreparedEmbreeExecution",
    "PreparedEmbreeKernel",
    "PreparedAdaptiveExecution",
    "public_pathology_datasets",
    "public_engine_features",
    "ray_triangle_any_hit",
    "ray_triangle_hit_count",
    "ray_triangle_closest_hit",
    "ray_triangle_any_hit_cpu",
    "ray_triangle_any_hit_apple_rt",
    "ray_triangle_any_hit_hiprt",
    "ray_triangle_hit_count_cpu",
    "ray_triangle_closest_hit_cpu",
    "ray_triangle_closest_hit_apple_rt",
    "ray_triangle_hit_count_apple_rt",
    "ray_triangle_hit_count_hiprt",
    "PreparedHiprtRayTriangleHitCount3D",
    "PreparedHiprtRayTriangleAnyHit2D",
    "prepare_hiprt_ray_triangle_any_hit_2d",
    "RAYJOIN_PAPER_TARGETS",
    "rayjoin_bounded_plans",
    "rayjoin_feature_service_layers",
    "rayjoin_public_assets",
    "representative_dataset_names",
    "refine",
    "reduce_rows",
    "RTDL_ENGINES",
    "APP_ENGINES",
    "ENGINE_SUPPORT_STATUSES",
    "APP_SUPPORT_STATUSES",
    "engine_feature_support",
    "engine_feature_support_matrix",
    "app_engine_support",
    "app_engine_support_matrix",
    "optix_app_performance_matrix",
    "optix_app_performance_support",
    "OPTIX_APP_PERFORMANCE_CLASSES",
    "public_apps",
    "run_baseline_benchmark",
    "run_baseline_case",
    "run_adaptive",
    "run_embree",
    "run_apple_rt",
    "run_goal23_reproduction",
    "run_cpu",
    "run_cpu_python_reference",
    "compile_cunsearch_fixed_radius_request_driver",
    "CuNSearchDuplicatePointGuardResult",
    "execute_compiled_cunsearch_fixed_radius_driver",
    "ExactCrossPackageMatch",
    "assess_cunsearch_duplicate_point_guard",
    "FixedRadiusMismatchSummary",
    "find_exact_cross_package_matches",
    "find_duplicate_free_kitti_pair",
    "KittiDuplicateFreePair",
    "run_postgis_fixed_radius_neighbors",
    "run_postgis_fixed_radius_neighbors_3d",
    "run_postgis_bounded_knn_rows_3d",
    "run_postgis_knn_rows",
    "run_postgis_knn_rows_3d",
    "query_postgresql_bfs_expand",
    "query_postgresql_conjunctive_scan",
    "query_postgresql_grouped_count",
    "query_postgresql_grouped_sum",
    "query_postgresql_triangle_probe",
    "run_postgresql_bfs_expand",
    "run_postgresql_conjunctive_scan",
    "run_postgresql_grouped_count",
    "run_postgresql_grouped_sum",
    "run_postgresql_triangle_probe",
    "run_scipy_fixed_radius_neighbors",
    "run_scipy_knn_rows",
    "run_section_5_6",
    "ScalabilityConfig",
    "schema_path",
    "scipy_available",
    "segment_intersection",
    "segment_intersection_apple_rt",
    "segment_polygon_anyhit_rows_apple_rt",
    "segment_polygon_hitcount_apple_rt",
    "segment_polygon_anyhit_rows",
    "segment_polygon_hitcount",
    "segment_polygon_anyhit_rows_hiprt",
    "segment_polygon_hitcount_hiprt",
    "segment_polygon_large_dataset_name",
    "Segment",
    "segment_polygon_hitcount_cpu",
    "segment_polygon_anyhit_rows_cpu",
    "parse_monuseg_xml_annotations",
    "load_monuseg_xml_annotations",
    "download_nuinsseg_zip",
    "direct_download_allowed",
    "describe_download_boundary",
    "monuseg_drive_file_id",
    "tile_polygon_set",
    "summarize_baseline_benchmark",
    "summarize_fixed_radius_mismatch",
    "slice_cdb_dataset",
    "traverse",
    "write_cdb",
    "u32",
    "validate_compiled_kernel_against_baseline",
    "validate_plan_dict",
    "write_baseline_benchmark_json",
    "write_goal112_artifacts",
    "write_goal114_artifacts",
    "write_goal116_artifacts",
    "WorkloadContract",
]

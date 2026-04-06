from .api import compile_kernel
from .api import contains
from .api import emit
from .api import input
from .api import kernel
from .api import overlay_compose
from .api import point_nearest_segment
from .api import point_in_polygon
from .api import ray_triangle_hit_count
from .api import refine
from .api import segment_intersection
from .api import segment_polygon_anyhit_rows
from .api import segment_polygon_hitcount
from .api import traverse
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
from .optix_runtime import optix_version
from .optix_runtime import OptixRowView
from .optix_runtime import prepare_optix
from .optix_runtime import PreparedOptixExecution
from .optix_runtime import PreparedOptixKernel
from .optix_runtime import run_optix
from .vulkan_runtime import vulkan_version
from .vulkan_runtime import VulkanRowView
from .vulkan_runtime import prepare_vulkan
from .vulkan_runtime import PreparedVulkanExecution
from .vulkan_runtime import PreparedVulkanKernel
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
from .reference import lsi_cpu
from .reference import overlay_compose_cpu
from .reference import point_nearest_segment_cpu
from .reference import pip_cpu
from .reference import Point
from .reference import Polygon
from .reference import Ray2D
from .reference import ray_triangle_hit_count_cpu
from .reference import Segment
from .reference import segment_polygon_anyhit_rows_cpu
from .reference import segment_polygon_hitcount_cpu
from .reference import Triangle
from .section_5_6_scalability import generate_section_5_6_artifacts
from .section_5_6_scalability import generate_synthetic_polygons
from .section_5_6_scalability import polygon_probe_points
from .section_5_6_scalability import polygons_to_segments
from .section_5_6_scalability import run_section_5_6
from .section_5_6_scalability import ScalabilityConfig
from .runtime import run_cpu
from .runtime import run_cpu_python_reference
from .types import f32
from .types import field
from .types import GeometryType
from .types import layout
from .types import Layout
from .types import Points
from .types import Point2DLayout
from .types import Polygons
from .types import Polygon2DLayout
from .types import Rays
from .types import Ray2DLayout
from .types import Segment2DLayout
from .types import Segments
from .types import Triangle2DLayout
from .types import Triangles
from .types import u32


def infer_workload(kernel_fn_or_compiled):
    from .baseline_runner import infer_workload as _infer_workload

    return _infer_workload(kernel_fn_or_compiled)


def representative_dataset_names(workload: str):
    from .baseline_runner import representative_dataset_names as _representative_dataset_names

    return _representative_dataset_names(workload)


def run_baseline_case(kernel_fn_or_compiled, dataset: str, backend: str = "both"):
    from .baseline_runner import run_baseline_case as _run_baseline_case

    return _run_baseline_case(kernel_fn_or_compiled, dataset, backend=backend)


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
    "CandidateSet",
    "CompiledKernel",
    "contains",
    "EmitOp",
    "GeometryInput",
    "GeometryType",
    "GenerateOnlyRequest",
    "InputContract",
    "LaunchParam",
    "Layout",
    "overlay_compose",
    "oracle_version",
    "point_nearest_segment",
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
    "Polygons",
    "Polygon2DLayout",
    "point_in_polygon",
    "Predicate",
    "Rays",
    "Ray2D",
    "Ray2DLayout",
    "RayJoinPlan",
    "RTExecutionPlan",
    "RayJoinBoundedPlan",
    "RayJoinFeatureServiceLayer",
    "RayJoinPublicAsset",
    "RefineOp",
    "Segment2DLayout",
    "Segments",
    "Triangles",
    "Triangle",
    "Triangle2DLayout",
    "compile_kernel",
    "dataset_families",
    "compare_baseline_rows",
    "evaluation_entries",
    "infer_workload",
    "arcgis_pages_to_cdb",
    "build_arcgis_geojson_query_url",
    "build_arcgis_query_url",
    "build_arcgis_layer_url",
    "chains_to_polygons",
    "chains_to_polygon_refs",
    "chains_to_probe_points",
    "chains_to_segments",
    "count_arcgis_loaded_pages",
    "download_rayjoin_sample",
    "EmbreeRowView",
    "embree_version",
    "OptixRowView",
    "optix_version",
    "prepare_optix",
    "PreparedOptixExecution",
    "PreparedOptixKernel",
    "run_optix",
    "VulkanRowView",
    "vulkan_version",
    "prepare_vulkan",
    "PreparedVulkanExecution",
    "PreparedVulkanKernel",
    "run_vulkan",
    "emit",
    "f32",
    "field",
    "generate_section_5_6_artifacts",
    "render_goal118_markdown",
    "run_goal118_segment_polygon_linux_large_perf",
    "write_goal118_artifacts",
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
    "render_python_program",
    "input",
    "kernel",
    "layout",
    "load_arcgis_feature_pages",
    "load_cdb",
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
    "overlay_compose_cpu",
    "parse_cdb_text",
    "pip_cpu",
    "Point",
    "point_nearest_segment_cpu",
    "polygon_probe_points",
    "Polygon",
    "polygons_to_segments",
    "prepare_embree",
    "PreparedEmbreeExecution",
    "PreparedEmbreeKernel",
    "ray_triangle_hit_count",
    "ray_triangle_hit_count_cpu",
    "RAYJOIN_PAPER_TARGETS",
    "rayjoin_bounded_plans",
    "rayjoin_feature_service_layers",
    "rayjoin_public_assets",
    "representative_dataset_names",
    "refine",
    "run_baseline_benchmark",
    "run_baseline_case",
    "run_embree",
    "run_goal23_reproduction",
    "run_cpu",
    "run_cpu_python_reference",
    "run_section_5_6",
    "ScalabilityConfig",
    "schema_path",
    "segment_intersection",
    "segment_polygon_anyhit_rows",
    "segment_polygon_hitcount",
    "segment_polygon_large_dataset_name",
    "Segment",
    "segment_polygon_hitcount_cpu",
    "segment_polygon_anyhit_rows_cpu",
    "summarize_baseline_benchmark",
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

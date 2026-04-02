from .api import compile_kernel
from .api import emit
from .api import input
from .api import kernel
from .api import overlay_compose
from .api import point_nearest_segment
from .api import point_in_polygon
from .api import ray_triangle_hit_count
from .api import refine
from .api import segment_intersection
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
from .goal23_reproduction import generate_goal23_artifacts
from .goal23_reproduction import run_goal23_reproduction
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
from .reference import segment_polygon_hitcount_cpu
from .reference import Triangle
from .section_5_6_scalability import generate_section_5_6_artifacts
from .section_5_6_scalability import generate_synthetic_polygons
from .section_5_6_scalability import polygon_probe_points
from .section_5_6_scalability import polygons_to_segments
from .section_5_6_scalability import run_section_5_6
from .section_5_6_scalability import ScalabilityConfig
from .runtime import run_cpu
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
    "EmitOp",
    "GeometryInput",
    "GeometryType",
    "InputContract",
    "LaunchParam",
    "Layout",
    "overlay_compose",
    "point_nearest_segment",
    "OutputRecord",
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
    "emit",
    "f32",
    "field",
    "generate_section_5_6_artifacts",
    "generate_synthetic_polygons",
    "generate_optix_project",
    "generate_goal23_artifacts",
    "generate_embree_evaluation_artifacts",
    "input",
    "kernel",
    "layout",
    "load_arcgis_feature_pages",
    "load_cdb",
    "local_profiles",
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
    "run_section_5_6",
    "ScalabilityConfig",
    "schema_path",
    "segment_intersection",
    "segment_polygon_hitcount",
    "Segment",
    "segment_polygon_hitcount_cpu",
    "summarize_baseline_benchmark",
    "slice_cdb_dataset",
    "traverse",
    "write_cdb",
    "u32",
    "validate_compiled_kernel_against_baseline",
    "validate_plan_dict",
    "write_baseline_benchmark_json",
    "WorkloadContract",
]

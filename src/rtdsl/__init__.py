from .api import compile_kernel
from .api import emit
from .api import input
from .api import kernel
from .api import overlay_compose
from .api import point_in_polygon
from .api import ray_triangle_hit_count
from .api import refine
from .api import segment_intersection
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
from .datasets import chains_to_polygon_refs
from .datasets import chains_to_probe_points
from .datasets import chains_to_segments
from .datasets import CdbChain
from .datasets import CdbDataset
from .datasets import CdbPoint
from .datasets import download_rayjoin_sample
from .datasets import load_cdb
from .datasets import parse_cdb_text
from .embree_runtime import embree_version
from .embree_runtime import run_embree
from .ir import CandidateSet
from .ir import CompiledKernel
from .ir import EmitOp
from .ir import GeometryInput
from .ir import LaunchParam
from .ir import OutputRecord
from .ir import PayloadRegister
from .ir import Predicate
from .ir import RayJoinPlan
from .ir import RefineOp
from .lowering import lower_to_rayjoin
from .plan_schema import load_plan_schema
from .plan_schema import schema_path
from .plan_schema import validate_plan_dict
from .reference import lsi_cpu
from .reference import overlay_compose_cpu
from .reference import pip_cpu
from .reference import Point
from .reference import Polygon
from .reference import Ray2D
from .reference import ray_triangle_hit_count_cpu
from .reference import Segment
from .reference import Triangle
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

__all__ = [
    "CdbChain",
    "CdbDataset",
    "CdbPoint",
    "BASELINE_FLOAT_ABS_TOL",
    "BASELINE_FLOAT_REL_TOL",
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
    "OutputRecord",
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
    "RefineOp",
    "Segment2DLayout",
    "Segments",
    "Triangles",
    "Triangle",
    "Triangle2DLayout",
    "compile_kernel",
    "compare_baseline_rows",
    "infer_workload",
    "chains_to_polygon_refs",
    "chains_to_probe_points",
    "chains_to_segments",
    "download_rayjoin_sample",
    "embree_version",
    "emit",
    "f32",
    "field",
    "generate_optix_project",
    "input",
    "kernel",
    "layout",
    "load_cdb",
    "lower_to_rayjoin",
    "load_plan_schema",
    "lsi_cpu",
    "overlay_compose_cpu",
    "parse_cdb_text",
    "pip_cpu",
    "Point",
    "Polygon",
    "ray_triangle_hit_count",
    "ray_triangle_hit_count_cpu",
    "representative_dataset_names",
    "refine",
    "run_baseline_benchmark",
    "run_baseline_case",
    "run_embree",
    "run_cpu",
    "schema_path",
    "segment_intersection",
    "Segment",
    "summarize_baseline_benchmark",
    "traverse",
    "u32",
    "validate_compiled_kernel_against_baseline",
    "validate_plan_dict",
    "write_baseline_benchmark_json",
    "WorkloadContract",
]

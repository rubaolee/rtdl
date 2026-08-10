#!/usr/bin/env python3
"""Author-compatible X-HD RTDL application entrypoint.

This app-owned wrapper accepts the author's key ``hd_exec`` flags and writes a
JSON payload with an ``HDResult`` field plus ``Running`` timing metadata.  It
does not make RTDL core understand X-HD, file formats, or paper datasets.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Iterable


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import run_xhd_cell_mbr_frontier_route_gate as cell_mbr_gate
import build_xhd_goal5359_cell_mbr_author_like_queue_route as author_queue_route
import run_xhd_rtdl_route_gate as public_route_gate
import xhd_memory_accounting
from xhd_input_loader import load_points_matrix
from xhd_input_loader import lift_point_matrix_2d_to_3d_zero_z
from xhd_input_loader import normalize_point_matrix_to_author_float32_unit_box
from xhd_input_loader import normalize_point_matrix_to_author_unit_box
from xhd_input_loader import point_matrix_to_rows
from xhd_input_loader import translate_point_matrix_to_min_bound


ROUTE_LABELS = (
    "auto",
    "public-columnar",
    "cell-mbr-fast-scalar",
    "cell-mbr-exact-witness",
    "cell-mbr-author-queue-diagnostic",
)
AUTHOR_VARIANTS = ("eb", "nn", "itk", "clover", "rt")
AUTHOR_RT_OPTION_SPECS = {
    "fast_build_bvh": {
        "author_flag": "fast_build_bvh",
        "type": "bool",
        "author_default": False,
        "meaning": "Prefer fast-build BVH in author RT mode.",
    },
    "rebuild_bvh": {
        "author_flag": "rebuild_bvh",
        "type": "bool",
        "author_default": False,
        "meaning": "Rebuild BVH on each author RT radius iteration instead of updating.",
    },
    "eb": {
        "author_flag": "eb",
        "type": "bool",
        "author_default": True,
        "meaning": "Use early-break optimization in author RT mode.",
    },
    "prune": {
        "author_flag": "prune",
        "type": "bool",
        "author_default": True,
        "meaning": "Use upper/lower-bound pruning in author RT mode.",
    },
    "lb": {
        "author_flag": "lb",
        "type": "int",
        "author_default": 256,
        "meaning": "Author load-balance threshold; 0 disables load balance.",
    },
    "n_points_cell": {
        "author_flag": "n_points_cell",
        "type": "int",
        "author_default": 15,
        "meaning": "Expected points per cell used for author grid/radius setup.",
    },
    "tune_grid": {
        "author_flag": "tune_grid",
        "type": "bool",
        "author_default": False,
        "meaning": "Author brute-force grid-size tuning mode.",
    },
    "tune_radius": {
        "author_flag": "tune_radius",
        "type": "choice",
        "choices": ("adaptive", "double", "add"),
        "author_default": "adaptive",
        "meaning": "Author radius growth policy between RT iterations.",
    },
}


class UnsupportedAuthorRtOptionsError(ValueError):
    """Raised when an explicit author RT option has no evidenced RTDL mapping."""

    def __init__(self, surface: dict[str, object]):
        self.surface = surface
        explicit = ", ".join(surface.get("explicit_author_rt_options", []))
        super().__init__(f"unsupported explicit author RT option(s): {explicit}")


def _parse_author_bool(value: str | bool | None, *, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError(f"expected boolean text, got: {value!r}")


def _parse_optional_author_bool(value: str | bool | None) -> bool | None:
    if value is None:
        return None
    return _parse_author_bool(value, default=False)


def _author_trace_has_nonterminal_radius_transition(path: str | None) -> bool:
    if not path:
        return False
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        iterations = payload["Running"]["Repeats"][0]["Iterations"]
    except Exception:
        return False
    if not isinstance(iterations, list) or len(iterations) < 2:
        return False
    return any(int(row.get("NumOutputPoints", 0)) > 0 for row in iterations if isinstance(row, dict))


def _supported_explicit_author_rt_options(args: argparse.Namespace, *, route_label: str) -> dict[str, dict[str, object]]:
    supported: dict[str, dict[str, object]] = {}
    if (
        route_label == "cell-mbr-author-queue-diagnostic"
        and getattr(args, "author_rt_tune_radius", None) == "adaptive"
        and _author_trace_has_nonterminal_radius_transition(getattr(args, "author_trace_json", None))
    ):
        supported["tune_radius"] = {
            "mapped_to_rtdl_control": "radius_growth_step(mode=adaptive)",
            "current_rtdl_support_status": (
                "supported_internal_cell_mbr_author_queue_diagnostic_nonterminal_trace"
            ),
            "support_scope": (
                "Internal diagnostic route only; requires --author-trace-json with "
                "a nonterminal author radius trace. This is not author RT-core "
                "algorithm parity, Figure 8 reproduction, or a performance claim."
            ),
        }
    return supported


def _author_rt_option_surface(args: argparse.Namespace, *, route_label: str) -> dict[str, object]:
    options: dict[str, object] = {}
    explicit_options: list[str] = []
    supported_options = _supported_explicit_author_rt_options(args, route_label=route_label)
    unsupported_options: list[str] = []
    for name, spec in AUTHOR_RT_OPTION_SPECS.items():
        raw_value = getattr(args, f"author_rt_{name}", None)
        explicit = raw_value is not None
        value = spec["author_default"] if not explicit else raw_value
        if explicit:
            explicit_options.append(name)
        support = supported_options.get(name) if explicit else None
        if explicit and support is None:
            unsupported_options.append(name)
        options[name] = {
            "author_flag": spec["author_flag"],
            "type": spec["type"],
            "author_default": spec["author_default"],
            "effective_value": value,
            "explicitly_requested": explicit,
            "meaning": spec["meaning"],
            "mapped_to_rtdl_control": None if support is None else support["mapped_to_rtdl_control"],
            "current_rtdl_support_status": (
                str(support["current_rtdl_support_status"])
                if support is not None
                else (
                    "unsupported_explicit_author_rt_option_fail_closed"
                    if explicit
                    else "author_default_recorded_not_algorithm_parity"
                )
            ),
            "support_scope": None if support is None else support["support_scope"],
            "author_semantics_equivalence_claimed": False,
        }
    status = (
        "unsupported_explicit_author_rt_options"
        if unsupported_options
        else "explicit_author_rt_options_supported_for_internal_diagnostic_route"
        if explicit_options
        else "no_explicit_author_rt_options__author_defaults_recorded_only"
    )
    return {
        "schema": "rtdl.paper_reproduction.xhd.author_rt_option_surface.v1",
        "status": status,
        "selected_route_label": route_label,
        "selected_variant": str(args.variant),
        "explicit_author_rt_options": explicit_options,
        "supported_explicit_author_rt_options": list(supported_options.keys()),
        "unsupported_explicit_author_rt_options": unsupported_options,
        "all_explicit_author_rt_options_supported": (
            None if not explicit_options else bool(not unsupported_options)
        ),
        "options": options,
        "boundary": (
            "These are author RT option-surface records. Omitted defaults are recorded "
            "for audit only. Explicit author RT options fail closed unless this "
            "surface records an evidenced narrow RTDL mapping for the selected route."
        ),
        "claim_boundary": {
            "author_rt_option_surface_complete_claimed": False,
            "author_rt_core_algorithm_equivalence_claimed": False,
            "performance_parity_claimed": False,
        },
    }


def _raise_if_unsupported_author_rt_options(surface: dict[str, object]) -> None:
    if surface.get("unsupported_explicit_author_rt_options", surface["explicit_author_rt_options"]):
        raise UnsupportedAuthorRtOptionsError(surface)


def _unsupported_author_rt_options_payload(
    args: argparse.Namespace, *, route_label: str, surface: dict[str, object]
) -> dict[str, object]:
    return {
        "HDResult": None,
        "Running": {
            "Algorithm": f"RTDL-{route_label}",
            "AvgTime": None,
            "TimeSemantics": "No route was executed because explicit author RT options failed closed.",
            "Repeats": [],
        },
        "RTDL": {
            "schema": "rtdl.paper_reproduction.xhd.rtdl_hd_exec_compatible.fail_closed.v1",
            "paper_app": "x-hd-paper",
            "status": "unsupported_author_rt_options_fail_closed",
            "entrypoint_contract": "author_hd_exec_key_flags_plus_rtdl_route_extension",
            "input1": str(args.input1),
            "input2": str(args.input2),
            "n_dims": int(args.n_dims),
            "input_type": str(args.input_type),
            "variant": str(args.variant),
            "execution": str(args.execution),
            "route_label": route_label,
            "author_rt_option_surface": surface,
            "claim_boundary": {
                "full_xhd_paper_reproduction_claim_authorized": False,
                "author_rt_core_algorithm_equivalence_claim_authorized": False,
                "author_rt_option_surface_complete_claimed": False,
                "author_variant_algorithm_equivalence_claimed": False,
                "performance_claim_authorized": False,
                "author_performance_parity_claimed": False,
                "exact_paper_dataset_identity_claimed": False,
            },
            "boundary": (
                "Explicit author RT options were supplied, but this RTDL app has not "
                "yet mapped those options to evidenced generic RTDL behavior. The run "
                "failed closed before loading inputs or computing a value."
            ),
        },
    }


def _select_route_label(*, requested: str, n_dims: int, execution: str) -> str:
    if requested != "auto":
        return requested
    if n_dims == 2 or execution == "cpu":
        return "public-columnar"
    return "cell-mbr-exact-witness"


def _variant_support_status(variant: str) -> dict[str, object]:
    if variant == "rt":
        return {
            "requested_author_variant": variant,
            "status": "xhd_rt_value_route",
            "hdresult_value_supported": True,
            "author_variant_algorithm_equivalence_claimed": False,
            "performance_parity_claimed": False,
            "description": (
                "The requested author variant is rt, the X-HD paper algorithm. "
                "RTDL computes the same directed HDResult contract through an "
                "explicit RTDL route label, but does not claim author RT-core "
                "kernel or performance equivalence."
            ),
        }
    return {
        "requested_author_variant": variant,
        "status": "author_variant_value_compatible_route_only",
        "hdresult_value_supported": True,
        "author_variant_algorithm_equivalence_claimed": False,
        "performance_parity_claimed": False,
        "description": (
            "The requested author variant is accepted for hd_exec-compatible "
            "value output. RTDL computes the directed HDResult via the selected "
            "generic RTDL route; it does not reproduce the author's variant-"
            "specific algorithm, timing denominator, or performance behavior."
        ),
    }


def _load_preprocessed_rows(args: argparse.Namespace) -> list[tuple[list[tuple[float, ...]], float, list[str]]]:
    load_start = time.perf_counter()
    points_a = load_points_matrix(Path(args.input1), n_dims=args.n_dims, input_type=args.input_type)
    points_b = load_points_matrix(Path(args.input2), n_dims=args.n_dims, input_type=args.input_type)
    preprocessing: list[str] = []
    if args.normalize_each_input_to_author_unit_box:
        if args.author_float32_normalization:
            points_a = normalize_point_matrix_to_author_float32_unit_box(points_a, copy=False)
            points_b = normalize_point_matrix_to_author_float32_unit_box(points_b, copy=False)
            preprocessing.append("normalize_each_input_to_author_float32_unit_box")
        else:
            points_a = normalize_point_matrix_to_author_unit_box(points_a, copy=False)
            points_b = normalize_point_matrix_to_author_unit_box(points_b, copy=False)
            preprocessing.append("normalize_each_input_to_author_unit_box")
    if args.translate_each_input_to_min_bound:
        points_a = translate_point_matrix_to_min_bound(points_a, copy=False)
        points_b = translate_point_matrix_to_min_bound(points_b, copy=False)
        preprocessing.append("translate_each_input_to_min_bound")
    load_sec = time.perf_counter() - load_start
    return [(point_matrix_to_rows(points_a), point_matrix_to_rows(points_b), load_sec, preprocessing)]


def _load_preprocessed_matrices(args: argparse.Namespace) -> tuple[object, object, float, list[str]]:
    load_start = time.perf_counter()
    points_a = load_points_matrix(Path(args.input1), n_dims=args.n_dims, input_type=args.input_type)
    points_b = load_points_matrix(Path(args.input2), n_dims=args.n_dims, input_type=args.input_type)
    preprocessing: list[str] = []
    if args.n_dims == 2:
        if not bool(getattr(args, "lift_2d_to_3d_zero_z", False)):
            raise ValueError("cell-mbr-author-queue-diagnostic requires --lift-2d-to-3d-zero-z for 2-D inputs")
        points_a = lift_point_matrix_2d_to_3d_zero_z(points_a, copy=False)
        points_b = lift_point_matrix_2d_to_3d_zero_z(points_b, copy=False)
        preprocessing.append("lift_2d_to_3d_zero_z_for_cell_mbr")
    if args.normalize_each_input_to_author_unit_box:
        if args.author_float32_normalization:
            points_a = normalize_point_matrix_to_author_float32_unit_box(points_a, copy=False)
            points_b = normalize_point_matrix_to_author_float32_unit_box(points_b, copy=False)
            preprocessing.append("normalize_each_input_to_author_float32_unit_box")
        else:
            points_a = normalize_point_matrix_to_author_unit_box(points_a, copy=False)
            points_b = normalize_point_matrix_to_author_unit_box(points_b, copy=False)
            preprocessing.append("normalize_each_input_to_author_unit_box")
    if args.translate_each_input_to_min_bound:
        points_a = translate_point_matrix_to_min_bound(points_a, copy=False)
        points_b = translate_point_matrix_to_min_bound(points_b, copy=False)
        preprocessing.append("translate_each_input_to_min_bound")
    load_sec = time.perf_counter() - load_start
    return points_a, points_b, load_sec, preprocessing


def _run_public_columnar_directed(args: argparse.Namespace) -> dict[str, object]:
    rows_a, rows_b, load_sec, preprocessing = _load_preprocessed_rows(args)[0]
    route_start = time.perf_counter()
    if args.n_dims == 2:
        source = public_route_gate._as_rtdl_points(rows_a)
        target = public_route_gate._as_rtdl_points(rows_b)
        directed = public_route_gate._run_numpy_columns_directed(source, target, label="a_to_b")
        route_name = "rtdl_public_columnar_directed_2d"
    elif args.n_dims == 3:
        source = public_route_gate._as_rtdl_points_3d(rows_a)
        target = public_route_gate._as_rtdl_points_3d(rows_b)
        directed = public_route_gate._run_numpy_columns_3d_directed(source, target, label="a_to_b")
        route_name = "rtdl_public_columnar_directed_3d"
    else:
        raise ValueError("RTDL hd_exec-compatible entrypoint supports only n_dims 2 or 3")
    route_sec = time.perf_counter() - route_start
    return {
        "route_label": "public-columnar",
        "route": route_name,
        "hd_result": float(directed["distance"]),
        "directed_a_to_b": directed,
        "run_phases": {
            "load_input_sec": load_sec,
            "rtdl_route_sec": route_sec,
            "total_sec": load_sec + route_sec,
        },
        "reference_preprocessing": preprocessing,
        "point_count_a": len(rows_a),
        "point_count_b": len(rows_b),
        "route_contract": (
            "RTDL public columnar directed Hausdorff route built from generic "
            "point-column, pairwise distance, nearest-witness, and max-nearest "
            "operators. This is not the author X-HD RT-core implementation."
        ),
        "witness_contract": "directed_input1_to_input2_witness_exact_for_public_columnar_reference",
        "per_source_witness_exact": True,
    }


def _cell_mbr_namespace(args: argparse.Namespace, *, route_label: str) -> SimpleNamespace:
    lift_2d_to_3d_zero_z = bool(getattr(args, "lift_2d_to_3d_zero_z", False))
    if args.n_dims not in {2, 3}:
        raise ValueError(f"{route_label} supports only 2-D or 3-D inputs")
    if args.n_dims == 2 and not lift_2d_to_3d_zero_z:
        raise ValueError(
            f"{route_label} requires --lift-2d-to-3d-zero-z for 2-D inputs; "
            "the default 2-D route remains public-columnar"
        )
    if args.execution != "gpu":
        raise ValueError(f"{route_label} requires -execution gpu")
    if route_label == "cell-mbr-fast-scalar":
        initial_state = "local-grid-cell"
        local_grid_seed_executor = "native_cuda"
        grid_branch_bound_seed_executor = "auto"
        frontier_inline_nearest = True
        global_bound_early_break = True
        skip_frontier_if_exact_seed = False
    elif route_label == "cell-mbr-exact-witness":
        initial_state = "grid-branch-bound"
        local_grid_seed_executor = "auto"
        grid_branch_bound_seed_executor = "native_cuda"
        frontier_inline_nearest = False
        global_bound_early_break = False
        skip_frontier_if_exact_seed = True
    else:
        raise ValueError(f"unsupported cell-MBR route label: {route_label}")
    return SimpleNamespace(
        input1=args.input1,
        input2=args.input2,
        n_dims=args.n_dims,
        input_type=args.input_type,
        lift_2d_to_3d_zero_z=lift_2d_to_3d_zero_z,
        normalize_each_input_to_author_unit_box=args.normalize_each_input_to_author_unit_box,
        author_float32_normalization=args.author_float32_normalization,
        translate_each_input_to_min_bound=args.translate_each_input_to_min_bound,
        backend="optix",
        grid_shape=args.grid_shape,
        radius=None,
        max_inline_points=args.max_inline_points,
        initial_state=initial_state,
        seed_cell_budget=args.seed_cell_budget,
        frontier_nearest_executor="auto",
        local_grid_seed_executor=local_grid_seed_executor,
        grid_branch_bound_seed_executor=grid_branch_bound_seed_executor,
        frontier_row_order="sorted",
        cell_order="native",
        grid_cell_point_order="point-id",
        grid_cell_builder="native_cuda",
        frontier_inline_nearest=frontier_inline_nearest,
        skip_frontier_if_exact_seed=skip_frontier_if_exact_seed,
        global_bound_early_break=global_bound_early_break,
        collect_inline_stats=False,
        collect_frontier_native_phase_timings=False,
        emit_radius_trace_metadata=bool(getattr(args, "emit_radius_trace_metadata", False)),
        frontier_row_capacity=None,
        direction_mode="directed-a-to-b",
        validation_mode="none",
        author_json=None,
        summary="",
        tolerance=args.tolerance,
    )


def _run_cell_mbr_directed(args: argparse.Namespace, *, route_label: str) -> dict[str, object]:
    summary = cell_mbr_gate.build_summary(_cell_mbr_namespace(args, route_label=route_label))
    directed = summary["rtdl_route"]["directed_a_to_b"]
    return {
        "route_label": route_label,
        "route": summary["rtdl_route"]["route"],
        "hd_result": float(directed["distance"]),
        "directed_a_to_b": directed,
        "run_phases": summary["run_phases"],
        "reference_preprocessing": summary["reference_preprocessing"],
        "point_count_a": summary["point_count_a"],
        "point_count_b": summary["point_count_b"],
        "route_contract": summary["rtdl_route"]["route_contract"],
        "witness_contract": (
            "directed_input1_to_input2_witness_may_be_approximate_for_fast_scalar"
            if route_label == "cell-mbr-fast-scalar"
            else "directed_input1_to_input2_per_source_witness_exact_seed_route"
        ),
        "per_source_witness_exact": bool(directed.get("per_source_witness_exact", False)),
        "radius_trace_metadata": summary.get("radius_trace_metadata"),
        "cell_mbr_summary": summary,
    }


def run_loaded_cell_mbr_exact_witness(
    source_points,
    target_points,
    *,
    grid_shape: tuple[int, int, int] = (32, 32, 32),
    max_inline_points: int = 512,
) -> dict[str, object]:
    """Run the locked Goal5263 V2 route on already prepared point matrices.

    Callers own PLY parsing, per-input translation, and input hashing.  The
    returned registered interval therefore matches Goal5632's
    ``loaded_translated_points_to_directed_exact_witness`` contract exactly.
    This remains an app-owned V2.x route and does not reproduce the author's
    RT-core algorithm.
    """

    parsed_grid_shape = tuple(int(value) for value in grid_shape)
    if len(parsed_grid_shape) != 3 or any(value <= 0 for value in parsed_grid_shape):
        raise ValueError("grid_shape must contain three positive integers")
    if int(max_inline_points) <= 0:
        raise ValueError("max_inline_points must be positive")
    registered_primary_start = time.perf_counter()
    directed = cell_mbr_gate._directed_cell_mbr_route(  # app-owned route helper
        source_points,
        target_points,
        label="a_to_b",
        backend="optix",
        grid_shape=parsed_grid_shape,
        radius=None,
        fallback_radius=cell_mbr_gate._full_cover_radius(source_points, target_points),
        max_inline_points=int(max_inline_points),
        initial_state="grid-branch-bound",
        seed_cell_budget=4,
        local_grid_seed_executor="auto",
        grid_branch_bound_seed_executor="native_cuda",
        frontier_nearest_executor="auto",
        frontier_row_order="sorted",
        frontier_inline_nearest=False,
        cell_order="native",
        grid_cell_point_order="point-id",
        grid_cell_builder="native_cuda",
        skip_frontier_if_exact_seed=True,
        global_bound_early_break=False,
        collect_inline_stats=False,
        collect_frontier_native_phase_timings=False,
        frontier_row_capacity=None,
    )
    registered_primary_elapsed_seconds = time.perf_counter() - registered_primary_start
    if not bool(directed.get("per_source_witness_exact", False)):
        raise RuntimeError("loaded Goal5263 route lost its exact-witness contract")
    return {
        "schema": "rtdl.paper_reproduction.xhd.loaded_cell_mbr_exact_witness.v1",
        "status": "loaded_goal5263_cell_mbr_exact_witness_completed",
        "route_label": "cell-mbr-exact-witness",
        "directed_a_to_b": directed,
        "registered_primary_timing": {
            "contract_id": "loaded_translated_points_to_directed_exact_witness",
            "elapsed_seconds": registered_primary_elapsed_seconds,
            "input_loading_included": False,
            "input_translation_included": False,
            "correctness_comparator_included": False,
        },
        "claim_boundary": {
            "v2x_route": True,
            "author_rt_core_algorithm_equivalence_claimed": False,
            "runtime_claimed": False,
        },
    }


def _run_cell_mbr_author_queue_diagnostic(args: argparse.Namespace) -> dict[str, object]:
    author_trace_json = getattr(args, "author_trace_json", None)
    if not author_trace_json:
        raise ValueError("cell-mbr-author-queue-diagnostic requires --author-trace-json")
    supported_author_options = _supported_explicit_author_rt_options(
        args,
        route_label="cell-mbr-author-queue-diagnostic",
    )
    tune_radius_support = supported_author_options.get("tune_radius")
    author_payload = json.loads(Path(author_trace_json).read_text(encoding="utf-8"))
    points_a, points_b, load_sec, preprocessing = _load_preprocessed_matrices(args)
    route_start = time.perf_counter()
    queue_route = author_queue_route._run_queue_route(
        source_points=points_a,
        target_points=points_b,
        author_payload=author_payload,
        backend="numpy",
        max_inline_points=int(args.max_inline_points),
    )
    route_sec = time.perf_counter() - route_start
    queue_rows = list(queue_route["queue_rows"])
    hd_result = 0.0 if not queue_rows else float(queue_rows[-1]["CMax2"]) ** 0.5
    return {
        "route_label": "cell-mbr-author-queue-diagnostic",
        "route": "rtdl_cell_mbr_author_like_queue_diagnostic_numpy_3d",
        "hd_result": hd_result,
        "directed_a_to_b": {
            "distance": hd_result,
            "queue_rows": queue_rows,
            "route_iterations": queue_route["route_iterations"],
        },
        "run_phases": {
            "load_input_sec": load_sec,
            "rtdl_route_sec": route_sec,
            "total_sec": load_sec + route_sec,
        },
        "reference_preprocessing": preprocessing,
        "point_count_a": int(len(points_a)),
        "point_count_b": int(len(points_b)),
        "route_contract": (
            "App-owned bounded diagnostic route that emits author-like radius "
            "queue rows from the generic cell-MBR route and emitted nearest "
            "columns. This is not the author RT-core implementation."
        ),
        "witness_contract": "directed_input1_to_input2_author_like_queue_trace_bounded_diagnostic",
        "per_source_witness_exact": True,
        "author_like_queue_iterations": queue_rows,
        "author_trace_json": str(author_trace_json),
        "radius_trace_metadata": {
            "schema": "rtdl.paper_reproduction.xhd.author_like_queue_trace.v1",
            "status": "author_like_queue_trace_available_from_cell_mbr_diagnostic_route",
            "route_iteration_model": queue_route["route_iteration_model"],
            "uses_radius_growth_step": bool(queue_route.get("uses_radius_growth_step", False)),
            "author_queue_semantics_aligned_for_bounded_trace": True,
            "author_tune_radius_supported": tune_radius_support is not None,
            "author_tune_radius_support_scope": None
            if tune_radius_support is None
            else tune_radius_support["support_scope"],
            "directions": [
                {
                    "label": "a_to_b",
                    "iterations": queue_rows,
                }
            ],
            "claim_boundary": {
                "author_tune_radius_route_mapping_claimed": False,
                "author_rt_core_algorithm_equivalence_claimed": False,
                "figure8_reproduction_claimed": False,
                "performance_claimed": False,
                "full_xhd_paper_reproduction_claimed": False,
            },
        },
    }


def _unsupported_memory_accounting_payload(payload: dict[str, object], *, reason: str) -> dict[str, object]:
    rtdl = payload["RTDL"]
    return {
        "schema": "rtdl.paper_reproduction.xhd.rtdl_memory_accounting.v1",
        "status": "memory_accounting_unavailable_for_selected_route",
        "reason": reason,
        "route_label": rtdl.get("route_label"),
        "point_count_a": int(rtdl.get("point_count_a", 0)),
        "point_count_b": int(rtdl.get("point_count_b", 0)),
        "author_mapped_fields": {
            "BVH": xhd_memory_accounting.memory_field_json(
                status="unavailable_selected_route_does_not_expose_author_memory_field",
                bytes_value=None,
                method="No compatible acceleration-structure memory metadata for this route.",
            ),
            "Grid": xhd_memory_accounting.memory_field_json(
                status="unavailable_selected_route_does_not_expose_author_memory_field",
                bytes_value=None,
                method="No generic grid-cell memory metadata for this route.",
            ),
            "MBRs B": xhd_memory_accounting.memory_field_json(
                status="unavailable_selected_route_does_not_expose_author_memory_field",
                bytes_value=None,
                method="No cell-MBR memory metadata for this route.",
            ),
            "WL": xhd_memory_accounting.memory_field_json(
                status="unavailable_selected_route_does_not_expose_author_memory_field",
                bytes_value=None,
                method="No frontier worklist capacity metadata for this route.",
            ),
            "WL Heavy Peak": xhd_memory_accounting.memory_field_json(
                status="unavailable_selected_route_does_not_expose_author_memory_field",
                bytes_value=None,
                method="No author-like heavy worklist peak metadata for this route.",
            ),
        },
        "rtdl_only_fields": {},
        "estimated_author_mapped_bytes_excluding_unavailable": 0,
        "estimated_author_mapped_mb_excluding_unavailable": 0.0,
        "estimated_total_accounted_bytes_excluding_unavailable": 0,
        "estimated_total_accounted_mb_excluding_unavailable": 0.0,
        "claim_boundary": {
            "figure11_reproduced": False,
            "author_memory_parity_claimed": False,
            "exact_gpu_allocator_measurement_claimed": False,
            "performance_ratio_claimed": False,
        },
    }


def _attach_memory_accounting_if_requested(
    payload: dict[str, object], *, include_memory_accounting: bool
) -> None:
    if not include_memory_accounting:
        return
    route_label = payload["RTDL"].get("route_label")
    if route_label in {"cell-mbr-fast-scalar", "cell-mbr-exact-witness"}:
        accounting = xhd_memory_accounting.rtdl_memory_accounting_from_hd_exec_payload(payload)
        status = "status_bearing_rtdl_memory_accounting_attached"
    else:
        accounting = _unsupported_memory_accounting_payload(
            payload,
            reason=(
                "The selected route is a public-columnar reference route and does not expose "
                "the grid/frontier metadata needed for Figure 11-style RTDL accounting."
            ),
        )
        status = "memory_accounting_unavailable_for_selected_route"

    memory_payload = {
        "Schema": "rtdl.paper_reproduction.xhd.rtdl_memory_accounting.running_repeat.v1",
        "Status": status,
        "Semantics": (
            "RTDL status-bearing memory accounting for the selected route. This is not "
            "the author's Figure 11 Memory schema, not exact GPU allocator telemetry, "
            "and not an author memory parity claim."
        ),
        "Accounting": accounting,
    }
    payload["RTDL"]["memory_accounting"] = accounting
    payload["RTDL"]["claim_boundary"]["figure11_reproduction_claimed"] = False
    payload["RTDL"]["claim_boundary"]["author_memory_parity_claimed"] = False
    payload["RTDL"]["claim_boundary"]["exact_gpu_allocator_measurement_claimed"] = False
    payload["Running"]["MemorySemantics"] = memory_payload["Semantics"]
    payload["Running"]["Repeats"][0]["Memory"] = memory_payload


def run_rtdl_hd_exec(args: argparse.Namespace) -> dict[str, object]:
    if args.input_type == "image":
        raise ValueError("RTDL X-HD paper app does not yet support -input_type image")
    route_label = _select_route_label(
        requested=args.rtdl_route,
        n_dims=args.n_dims,
        execution=args.execution,
    )
    author_rt_options = _author_rt_option_surface(args, route_label=route_label)
    _raise_if_unsupported_author_rt_options(author_rt_options)
    total_start = time.perf_counter()
    if route_label == "public-columnar":
        route = _run_public_columnar_directed(args)
    elif route_label == "cell-mbr-author-queue-diagnostic":
        route = _run_cell_mbr_author_queue_diagnostic(args)
    else:
        route = _run_cell_mbr_directed(args, route_label=route_label)
    total_sec = time.perf_counter() - total_start
    route_sec = float(route["run_phases"]["rtdl_route_sec"])
    route_ms = route_sec * 1000.0
    payload = {
        "HDResult": float(route["hd_result"]),
        "Running": {
            "Algorithm": f"RTDL-{route_label}",
            "AvgTime": route_ms,
            "TimeSemantics": (
                "RTDL route wall time in milliseconds for the selected route label; "
                "not author internal Running.AvgTime parity"
            ),
            "Repeats": [
                {
                    "Algorithm": f"RTDL-{route_label}",
                    "ReportedTime": route_ms,
                    "TimeSemantics": (
                        "RTDL route wall time in milliseconds for the selected route label; "
                        "not author internal ReportedTime parity"
                    ),
                    "Iterations": [
                        {
                            "RouteTime": route_ms,
                            "TotalWallTime": total_sec * 1000.0,
                            "TimeSemantics": "RTDL route and entrypoint wall time in milliseconds",
                        }
                    ],
                }
            ],
        },
        "RTDL": {
            "schema": "rtdl.paper_reproduction.xhd.rtdl_hd_exec_compatible.v1",
            "paper_app": "x-hd-paper",
            "entrypoint_contract": "author_hd_exec_key_flags_plus_rtdl_route_extension",
            "input1": str(args.input1),
            "input2": str(args.input2),
            "n_dims": int(args.n_dims),
            "input_type": str(args.input_type),
            "variant": str(args.variant),
            "variant_support": _variant_support_status(str(args.variant)),
            "author_rt_option_surface": author_rt_options,
            "execution": str(args.execution),
            "route_label": route_label,
            "route": route,
            "hd_result_semantics": "directed_input1_to_input2",
            "reference_preprocessing": route["reference_preprocessing"],
            "point_count_a": int(route["point_count_a"]),
            "point_count_b": int(route["point_count_b"]),
            "run_phases": {**route["run_phases"], "entrypoint_total_sec": total_sec},
            "running_avg_time_semantics": (
                "Running.AvgTime is populated for author-shaped JSON compatibility, "
                "but it is RTDL route wall time for the selected route label. It must "
                "not be compared to author internal Running.AvgTime without an explicit "
                "phase-boundary review."
            ),
            "claim_boundary": {
                "full_xhd_paper_reproduction_claim_authorized": False,
                "author_rt_core_algorithm_equivalence_claim_authorized": False,
                "author_rt_option_surface_complete_claimed": False,
                "author_variant_algorithm_equivalence_claimed": False,
                "performance_claim_authorized": False,
                "author_performance_parity_claimed": False,
                "exact_paper_dataset_identity_claimed": False,
            },
            "boundary": (
                "Author-compatible RTDL X-HD app entrypoint. The CLI mirrors the "
                "author hd_exec key flags and writes HDResult/Running JSON, but "
                "the computation is an RTDL route label selected by --rtdl-route. "
                "Non-rt author variants are accepted as value-compatible HDResult "
                "requests only; their author-specific algorithms and performance "
                "denominators are not reproduced. "
                "This is not a claim of full paper reproduction, author RT-core "
                "algorithm equivalence, or performance parity."
            ),
        },
    }
    if route.get("radius_trace_metadata") is not None:
        payload["RTDL"]["radius_trace_metadata"] = route["radius_trace_metadata"]
        payload["Running"]["Repeats"][0]["RTDLRadiusTrace"] = route["radius_trace_metadata"]
    if route.get("author_like_queue_iterations") is not None:
        payload["Running"]["Repeats"][0]["Iterations"] = route["author_like_queue_iterations"]
        payload["Running"]["Repeats"][0]["IterationSemantics"] = (
            "RTDL author-like radius queue rows emitted by the selected diagnostic route; "
            "not author internal timing parity"
        )
    _attach_memory_accounting_if_requested(
        payload,
        include_memory_accounting=bool(getattr(args, "include_memory_accounting", False)),
    )
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the RTDL X-HD app with author hd_exec-compatible flags.")
    parser.add_argument("-input1", "--input1", required=True)
    parser.add_argument("-input2", "--input2", required=True)
    parser.add_argument("-n_dims", "--n-dims", dest="n_dims", type=int, default=3)
    parser.add_argument("-input_type", "--input-type", dest="input_type", default="ply", choices=("image", "wkt", "ply", "off"))
    parser.add_argument("-variant", "--variant", default="rt", choices=AUTHOR_VARIANTS)
    parser.add_argument("-execution", "--execution", default="gpu", choices=("cpu", "gpu"))
    parser.add_argument("-json", "--json", dest="json_path", required=True)
    parser.add_argument("-overwrite", "--overwrite", default="true")
    parser.add_argument("-check", "--check", default="false")
    parser.add_argument("--rtdl-route", default="auto", choices=ROUTE_LABELS)
    parser.add_argument("--grid-shape", default="4,4,4")
    parser.add_argument("--max-inline-points", type=int, default=64)
    parser.add_argument(
        "--emit-radius-trace-metadata",
        action="store_true",
        help=(
            "Emit app-owned internal radius trace metadata for cell-MBR RTDL routes. "
            "Explicit tune_radius remains fail-closed except for the internal "
            "cell-mbr-author-queue-diagnostic adaptive trace gate."
        ),
    )
    parser.add_argument(
        "--author-trace-json",
        help=(
            "Internal diagnostic input for cell-mbr-author-queue-diagnostic. "
            "Provides author InitRadius/GridResolution/HDUpperBound trace fields; "
            "required for the narrow internal adaptive -tune_radius mapping; "
            "not author RT-core parity or Figure 8 reproduction."
        ),
    )
    parser.add_argument("--seed-cell-budget", type=int, default=4)
    parser.add_argument(
        "-fast_build_bvh",
        "--fast-build-bvh",
        "--fast_build_bvh",
        dest="author_rt_fast_build_bvh",
        nargs="?",
        const="true",
        type=_parse_optional_author_bool,
        default=None,
        help="Author RT flag accepted for audit and fail-closed until semantics are implemented.",
    )
    parser.add_argument(
        "-rebuild_bvh",
        "--rebuild-bvh",
        "--rebuild_bvh",
        dest="author_rt_rebuild_bvh",
        nargs="?",
        const="true",
        type=_parse_optional_author_bool,
        default=None,
        help="Author RT flag accepted for audit and fail-closed until semantics are implemented.",
    )
    parser.add_argument(
        "-eb",
        "--eb",
        dest="author_rt_eb",
        nargs="?",
        const="true",
        type=_parse_optional_author_bool,
        default=None,
        help="Author RT early-break flag accepted for audit and fail-closed until semantics are implemented.",
    )
    parser.add_argument(
        "-prune",
        "--prune",
        dest="author_rt_prune",
        nargs="?",
        const="true",
        type=_parse_optional_author_bool,
        default=None,
        help="Author RT prune flag accepted for audit and fail-closed until semantics are implemented.",
    )
    parser.add_argument(
        "-lb",
        "--lb",
        dest="author_rt_lb",
        type=int,
        default=None,
        help="Author RT load-balance threshold accepted for audit and fail-closed until semantics are implemented.",
    )
    parser.add_argument(
        "-n_points_cell",
        "--n-points-cell",
        "--n_points_cell",
        dest="author_rt_n_points_cell",
        type=int,
        default=None,
        help="Author RT grid/radius setup flag accepted for audit and fail-closed until semantics are implemented.",
    )
    parser.add_argument(
        "-tune_grid",
        "--tune-grid",
        "--tune_grid",
        dest="author_rt_tune_grid",
        nargs="?",
        const="true",
        type=_parse_optional_author_bool,
        default=None,
        help="Author RT grid-tuning flag accepted for audit and fail-closed until semantics are implemented.",
    )
    parser.add_argument(
        "-tune_radius",
        "--tune-radius",
        "--tune_radius",
        dest="author_rt_tune_radius",
        choices=("adaptive", "double", "add"),
        default=None,
        help=(
            "Author RT radius tuning mode. Only adaptive is narrowly mapped for "
            "the internal cell-mbr-author-queue-diagnostic route with a "
            "nonterminal author trace; all other cases fail closed."
        ),
    )
    parser.add_argument(
        "--lift-2d-to-3d-zero-z",
        action="store_true",
        help=(
            "Explicitly embed 2-D input coordinates as (x,y,0) before using a "
            "cell-MBR route. The default 2-D route remains public-columnar."
        ),
    )
    parser.add_argument("--normalize-each-input-to-author-unit-box", action="store_true")
    parser.add_argument("--author-float32-normalization", action="store_true")
    parser.add_argument("--translate-each-input-to-min-bound", action="store_true")
    parser.add_argument(
        "--include-memory-accounting",
        action="store_true",
        help=(
            "Attach RTDL status-bearing memory accounting under Running.Repeats[0].Memory "
            "and RTDL.memory_accounting. This is not the author's Figure 11 Memory schema."
        ),
    )
    parser.add_argument("--tolerance", type=float, default=1e-6)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    out = Path(args.json_path)
    overwrite = _parse_author_bool(args.overwrite, default=True)
    _ = _parse_author_bool(args.check, default=False)
    if out.exists() and not overwrite:
        raise FileExistsError(f"{out} already exists; pass -overwrite=true to replace it")
    route_label = _select_route_label(
        requested=args.rtdl_route,
        n_dims=args.n_dims,
        execution=args.execution,
    )
    try:
        payload = run_rtdl_hd_exec(args)
        exit_code = 0
    except UnsupportedAuthorRtOptionsError as exc:
        payload = _unsupported_author_rt_options_payload(args, route_label=route_label, surface=exc.surface)
        exit_code = 2
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

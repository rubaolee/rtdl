from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Iterable

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from rtdsl.reference import Point
from rtdsl.reference import Point3D

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from run_xhd_author_json_gate import exact_hausdorff, load_author_hd_result
from xhd_input_loader import load_points
from xhd_input_loader import translate_points_to_min_bound


def _as_rtdl_points(points: list[tuple[float, ...]]) -> tuple[Point, ...]:
    return tuple(Point(id=index, x=float(point[0]), y=float(point[1])) for index, point in enumerate(points))


def _as_rtdl_points_3d(points: list[tuple[float, ...]]) -> tuple[Point3D, ...]:
    return tuple(
        Point3D(id=index, x=float(point[0]), y=float(point[1]), z=float(point[2]))
        for index, point in enumerate(points)
    )


def _run_numpy_columns_directed(source: tuple[Point, ...], target: tuple[Point, ...], *, label: str) -> dict[str, object]:
    source_columns = rt.point_rows_to_numpy_columns(source)
    target_columns = rt.point_rows_to_numpy_columns(target)
    result = rt.directed_hausdorff_2d_numpy_columns(
        source_columns,
        target_columns,
        return_metadata=True,
    )
    metadata = result["metadata"]
    return {
        "label": label,
        "distance": float(metadata["distance"]),
        "source_id": int(metadata["source_id"]),
        "target_id": int(metadata["target_id"]),
        "row_count": int(metadata["source_count"]),
        "partner_reference_contract": metadata["partner_reference_contract"],
        "native_engine_row_contract": metadata["native_engine_row_contract"],
        "direct_device_handoff_authorized": bool(metadata["direct_device_handoff_authorized"]),
        "rt_core_speedup_claim_authorized": bool(metadata["rt_core_speedup_claim_authorized"]),
        "whole_app_speedup_claim_authorized": bool(metadata["whole_app_speedup_claim_authorized"]),
    }


def _run_numpy_columns_3d_directed(
    source: tuple[Point3D, ...],
    target: tuple[Point3D, ...],
    *,
    label: str,
) -> dict[str, object]:
    source_columns = rt.point_rows_to_numpy_columns_3d(source)
    target_columns = rt.point_rows_to_numpy_columns_3d(target)
    result = rt.directed_hausdorff_3d_numpy_columns(
        source_columns,
        target_columns,
        return_metadata=True,
    )
    metadata = result["metadata"]
    return {
        "label": label,
        "distance": float(metadata["distance"]),
        "source_id": int(metadata["source_id"]),
        "target_id": int(metadata["target_id"]),
        "row_count": int(metadata["source_count"]),
        "partner_reference_contract": metadata["partner_reference_contract"],
        "native_engine_row_contract": metadata["native_engine_row_contract"],
        "direct_device_handoff_authorized": bool(metadata["direct_device_handoff_authorized"]),
        "rt_core_speedup_claim_authorized": bool(metadata["rt_core_speedup_claim_authorized"]),
        "whole_app_speedup_claim_authorized": bool(metadata["whole_app_speedup_claim_authorized"]),
    }


def run_rtdl_hausdorff(points_a: list[tuple[float, ...]], points_b: list[tuple[float, ...]], *, n_dims: int) -> dict[str, object]:
    if n_dims == 2:
        return run_rtdl_hausdorff_2d(points_a, points_b)
    if n_dims == 3:
        return run_rtdl_hausdorff_3d(points_a, points_b)
    raise ValueError("RTDL route gate supports only public 2D and 3D Hausdorff APIs")


def run_rtdl_hausdorff_2d(points_a: list[tuple[float, ...]], points_b: list[tuple[float, ...]]) -> dict[str, object]:
    rows_a = _as_rtdl_points(points_a)
    rows_b = _as_rtdl_points(points_b)
    directed_ab = _run_numpy_columns_directed(rows_a, rows_b, label="a_to_b")
    directed_ba = _run_numpy_columns_directed(rows_b, rows_a, label="b_to_a")
    hausdorff = max(float(directed_ab["distance"]), float(directed_ba["distance"]))
    return {
        "route": "rtdl_numpy_columns_2d",
        "directed_a_to_b": directed_ab,
        "directed_b_to_a": directed_ba,
        "hausdorff": hausdorff,
        "route_contract": (
            "RTDL public 2D columnar Hausdorff route using point_rows_to_numpy_columns "
            "and directed_hausdorff_2d_numpy_columns. This is a generic RTDL route, "
            "not the author X-HD RT-core implementation and not a performance claim."
        ),
    }


def run_rtdl_hausdorff_3d(points_a: list[tuple[float, ...]], points_b: list[tuple[float, ...]]) -> dict[str, object]:
    rows_a = _as_rtdl_points_3d(points_a)
    rows_b = _as_rtdl_points_3d(points_b)
    directed_ab = _run_numpy_columns_3d_directed(rows_a, rows_b, label="a_to_b")
    directed_ba = _run_numpy_columns_3d_directed(rows_b, rows_a, label="b_to_a")
    hausdorff = max(float(directed_ab["distance"]), float(directed_ba["distance"]))
    return {
        "route": "rtdl_numpy_columns_3d",
        "directed_a_to_b": directed_ab,
        "directed_b_to_a": directed_ba,
        "hausdorff": hausdorff,
        "route_contract": (
            "RTDL public 3D columnar Hausdorff route using point_rows_to_numpy_columns_3d "
            "and directed_hausdorff_3d_numpy_columns. This is a generic RTDL route, "
            "not the author X-HD RT-core implementation and not a performance claim."
        ),
    }


def build_summary(args: argparse.Namespace) -> dict[str, object]:
    if args.n_dims not in {2, 3}:
        raise ValueError("RTDL route gate supports only public 2D and 3D Hausdorff APIs")

    total_start = time.perf_counter()
    input1 = Path(args.input1)
    input2 = Path(args.input2)
    load_start = time.perf_counter()
    points_a = load_points(input1, n_dims=args.n_dims, input_type=args.input_type)
    points_b = load_points(input2, n_dims=args.n_dims, input_type=args.input_type)
    preprocessing: list[str] = []
    if args.translate_each_input_to_min_bound:
        points_a = translate_points_to_min_bound(points_a)
        points_b = translate_points_to_min_bound(points_b)
        preprocessing.append("translate_each_input_to_min_bound")
    load_sec = time.perf_counter() - load_start
    exact_start = time.perf_counter()
    exact = exact_hausdorff(points_a, points_b)
    exact_sec = time.perf_counter() - exact_start
    route_start = time.perf_counter()
    rtdl_route = run_rtdl_hausdorff(points_a, points_b, n_dims=args.n_dims)
    route_sec = time.perf_counter() - route_start

    rtdl_exact_diff = abs(float(rtdl_route["hausdorff"]) - float(exact["hausdorff"]))
    rtdl_matches_exact_reference = bool(rtdl_exact_diff <= args.tolerance)

    # The author's `hd_exec -variant=rt` reports directed input1 -> input2
    # Hausdorff.  Keep the symmetric max as a route diagnostic, but compare the
    # author HDResult to the directed A -> B route value.
    author_reference_key = "directed_a_to_b"
    author_comparison_distance = float(rtdl_route[author_reference_key]["distance"])

    author_json = Path(args.author_json) if args.author_json else None
    author_load_start = time.perf_counter()
    author_hd = load_author_hd_result(author_json) if author_json is not None and author_json.exists() else None
    author_json_load_sec = time.perf_counter() - author_load_start
    author_abs_diff = None if author_hd is None else abs(float(author_hd) - author_comparison_distance)
    author_matched = None if author_abs_diff is None else bool(author_abs_diff <= args.tolerance)
    matched = None if author_matched is None else bool(author_matched and rtdl_matches_exact_reference)
    total_sec = time.perf_counter() - total_start

    return {
        "schema": "rtdl.paper_reproduction.xhd.rtdl_route_gate.v1",
        "paper_app": "x-hd-paper",
        "input1": str(input1),
        "input2": str(input2),
        "n_dims": args.n_dims,
        "input_type": args.input_type,
        "point_count_a": len(points_a),
        "point_count_b": len(points_b),
        "reference_preprocessing": preprocessing,
        "rtdl_route": rtdl_route,
        "exact_reference": exact,
        "rtdl_exact_abs_diff": rtdl_exact_diff,
        "rtdl_matches_exact_reference": rtdl_matches_exact_reference,
        "author_comparison_reference": author_reference_key,
        "author_comparison_distance": author_comparison_distance,
        "author_json": None if author_json is None else str(author_json),
        "author_hd_result": author_hd,
        "author_abs_diff": author_abs_diff,
        "tolerance": args.tolerance,
        "matched": matched,
        "run_phases": {
            "load_input_sec": load_sec,
            "exact_reference_sec": exact_sec,
            "rtdl_route_sec": route_sec,
            "author_json_load_sec": author_json_load_sec,
            "total_sec": total_sec,
        },
        "boundary": (
            "Bounded same-input RTDL route gate. This compares a generic RTDL 2D "
            "or 3D columnar Hausdorff route against an existing author HDResult JSON and "
            "a deterministic exact reference for the same bounded WKT or ASCII PLY "
            "fixture. It is not "
            "full X-HD paper reproduction, not the author RT-core algorithm, and "
            "not a performance claim."
        ),
        "paper_reproduction_claim_authorized": False,
        "performance_claim_authorized": False,
        "author_performance_parity_claimed": False,
        "existing_hausdorff_xhd_benchmark_reclassified_as_paper_reproduction": False,
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a bounded X-HD RTDL route gate against author JSON.")
    parser.add_argument("--input1", required=True)
    parser.add_argument("--input2", required=True)
    parser.add_argument("--n-dims", type=int, default=2)
    parser.add_argument("--input-type", default="wkt", choices=("wkt", "ply"))
    parser.add_argument(
        "--translate-each-input-to-min-bound",
        action="store_true",
        help=(
            "Translate each input point set independently so its coordinate-wise "
            "minimum is zero before computing the RTDL/reference comparator. "
            "This models the author PLY loader's reported MBR convention."
        ),
    )
    parser.add_argument("--author-json")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--tolerance", type=float, default=1e-6)
    args = parser.parse_args(list(argv) if argv is not None else None)

    summary = build_summary(args)
    out = Path(args.summary)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if summary["matched"] is not False else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run the Goal5305 bounded County-ZCTA RTDL route gate.

This is an app-owned paper-reproduction runner. It connects the X-HD WKT
front door to an existing generic RTDL partner 2-D max-nearest primitive. It
does not add a geo or X-HD primitive to RTDL core.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Iterable


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import rtdsl as rt
from rtdsl.reference import Point

from run_xhd_author_json_gate import load_author_hd_result
from xhd_input_loader import load_points_matrix


def _point_rows_from_matrix(matrix) -> tuple[Point, ...]:
    return tuple(
        Point(id=index, x=float(row[0]), y=float(row[1]))
        for index, row in enumerate(matrix)
    )


def run_goal5305_gate(args: argparse.Namespace) -> dict[str, object]:
    if int(args.n_dims) != 2:
        raise ValueError("Goal5305 County-ZCTA WKT gate currently supports n_dims=2 only")
    if str(args.input_type).lower() != "wkt":
        raise ValueError("Goal5305 County-ZCTA gate expects input_type=wkt")

    total_start = time.perf_counter()
    load_start = time.perf_counter()
    matrix_a = load_points_matrix(Path(args.input1), n_dims=2, input_type="wkt")
    matrix_b = load_points_matrix(Path(args.input2), n_dims=2, input_type="wkt")
    load_sec = time.perf_counter() - load_start

    column_start = time.perf_counter()
    partner = str(args.partner)
    source_columns = rt.point_rows_to_partner_columns(_point_rows_from_matrix(matrix_a), partner=partner)
    target_columns = rt.point_rows_to_partner_columns(_point_rows_from_matrix(matrix_b), partner=partner)
    column_sec = time.perf_counter() - column_start

    route_start = time.perf_counter()
    result = rt.directed_max_of_nearest_distance_2d_partner_columns(
        source_columns,
        target_columns,
        partner=partner,
        numba_strategy="block_nearest_rows",
        numba_block_size=int(args.numba_block_size),
        triton_strategy=str(args.triton_strategy),
        triton_candidate_block_size=int(args.triton_candidate_block_size),
        materialize_nearest_distances=False,
        return_metadata=True,
    )
    route_sec = time.perf_counter() - route_start
    metadata = result["metadata"]
    author_hd = load_author_hd_result(Path(args.author_json)) if args.author_json else None
    distance = float(metadata["distance"])
    author_abs_diff = None if author_hd is None else abs(float(author_hd) - distance)
    matched = None if author_abs_diff is None else bool(author_abs_diff <= float(args.tolerance))
    total_sec = time.perf_counter() - total_start

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5305.county_zcta_rtdl_partner_gate.v2",
        "goal": "Goal5305",
        "status": (
            "rtdl_partner_route_attempted__level_b_bounded_geo_only"
            if matched is None or matched
            else "rtdl_partner_route_mismatch__level_b_bounded_geo_only"
        ),
        "input": {
            "input1": str(args.input1),
            "input2": str(args.input2),
            "input_type": "wkt",
            "n_dims": 2,
            "point_count_a": int(matrix_a.shape[0]),
            "point_count_b": int(matrix_b.shape[0]),
        },
        "author": {
            "author_json": None if args.author_json is None else str(args.author_json),
            "HDResult": author_hd,
            "comparison_reference": "directed_input1_to_input2",
            "tolerance": float(args.tolerance),
            "abs_diff": author_abs_diff,
            "matched": matched,
        },
        "rtdl": {
            "HDResult": distance,
            "source_id": int(metadata["source_id"]),
            "target_id": int(metadata["target_id"]),
            "distance_sq": float(metadata["distance_sq"]),
            "route": "directed_max_of_nearest_distance_2d_partner_columns",
            "partner": partner,
            "numba_strategy": metadata.get("numba_strategy"),
            "numba_block_size": metadata.get("numba_block_size"),
            "numba_score_row_operation": metadata.get("numba_score_row_operation"),
            "numba_score_row_count": metadata.get("numba_score_row_count"),
            "numba_logical_pair_count": metadata.get("numba_logical_pair_count"),
            "triton_strategy": metadata.get("v2_5_triton_strategy"),
            "triton_candidate_block_size": metadata.get("triton_candidate_block_size"),
            "triton_candidate_tile_count": metadata.get("triton_candidate_tile_count"),
            "triton_tile_witness_row_count": metadata.get("triton_tile_witness_row_count"),
            "score_rows_generated_on_partner_device": metadata.get("score_rows_generated_on_partner_device"),
            "host_score_row_materialization_used": metadata.get("host_score_row_materialization_used"),
            "nearest_distance_column_materialized": metadata.get("nearest_distance_column_materialized"),
            "per_source_witness_exact": True,
            "native_engine_row_contract": metadata["native_engine_row_contract"],
            "partner_reference_contract": metadata["partner_reference_contract"],
            "rt_core_speedup_claim_authorized": bool(metadata["rt_core_speedup_claim_authorized"]),
            "whole_app_speedup_claim_authorized": bool(metadata["whole_app_speedup_claim_authorized"]),
        },
        "run_phases": {
            "load_input_sec": load_sec,
            "partner_column_upload_sec": column_sec,
            "rtdl_route_sec": route_sec,
            "total_sec": total_sec,
            "numba_pairwise_elapsed_seconds": metadata.get("numba_pairwise_elapsed_seconds"),
            "numba_grouped_argmin_elapsed_seconds": metadata.get("numba_grouped_argmin_elapsed_seconds"),
            "numba_grouped_argmax_elapsed_seconds": metadata.get("numba_grouped_argmax_elapsed_seconds"),
            "triton_dense_point_nearest_elapsed_seconds": metadata.get(
                "triton_dense_point_nearest_elapsed_seconds"
            ),
            "triton_grouped_argmax_elapsed_seconds": metadata.get("triton_grouped_argmax_elapsed_seconds"),
        },
        "claim_boundary": {
            "level_b_bounded_geo_correctness_claimed": bool(matched),
            "exact_paper_dataset_reproduction_claimed": False,
            "geo_figure5_reproduction_claimed": False,
            "author_rt_core_algorithm_equivalence_claimed": False,
            "author_performance_parity_claimed": False,
            "performance_ratio_claimed": False,
            "full_paper_reproduction_claimed": False,
        },
        "boundary": (
            "This bounded gate compares the RTDL generic partner 2-D "
            "directed max-nearest route with the Goal5304 author HDResult on "
            "the same WKT fixture. It is not the author X-HD RT-core algorithm, "
            "not exact paper input recovery, not Figure 5 reproduction, and not "
            "a performance-ratio denominator."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Goal5305 X-HD County-ZCTA RTDL partner gate.")
    parser.add_argument("--input1", required=True)
    parser.add_argument("--input2", required=True)
    parser.add_argument("--author-json")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--input-type", default="wkt", choices=("wkt",))
    parser.add_argument("--n-dims", type=int, default=2)
    parser.add_argument("--partner", default="numba", choices=("numba", "triton", "torch", "cupy"))
    parser.add_argument("--numba-block-size", type=int, default=256, choices=(32, 64, 128, 256))
    parser.add_argument(
        "--triton-strategy",
        default="dense_point_nearest_tiled",
        choices=("generic_score_rows", "dense_point_nearest", "dense_point_nearest_tiled"),
    )
    parser.add_argument("--triton-candidate-block-size", type=int, default=256)
    parser.add_argument("--tolerance", type=float, default=1e-5)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    payload = run_goal5305_gate(args)
    out = Path(args.summary)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    matched = payload["author"]["matched"]
    return 0 if matched is None or bool(matched) else 1


if __name__ == "__main__":
    raise SystemExit(main())

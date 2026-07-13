from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import rtdsl as rt

from run_xhd_cell_mbr_frontier_route_gate import _columns_3d
from xhd_input_loader import load_points, translate_points_to_min_bound


def _direction_summary(
    source_points: list[tuple[float, ...]],
    target_points: list[tuple[float, ...]],
    *,
    label: str,
    grid_shape: tuple[int, int, int],
    max_inline_points: int,
    sort_rows: bool,
) -> dict[str, object]:
    source_columns = _columns_3d(source_points)
    target_columns = _columns_3d(target_points)
    grid = rt.point_grid_cell_mbrs_numpy_columns(
        target_columns,
        coordinate_fields=("x", "y", "z"),
        grid_shape=grid_shape,
        return_metadata=True,
    )
    seed = rt.seed_nearest_witness_from_nearest_cell_mbr_numpy_columns(
        source_columns,
        target_columns,
        grid["cell_columns"],
        coordinate_fields=("x", "y", "z"),
        executor="numba_parallel",
        return_metadata=True,
    )
    radius = float(np.max(seed["columns"]["nearest_distances"])) + 1.0e-12
    frontier = rt.cell_mbr_nearest_frontier_native_3d_optix_columns(
        source_columns,
        grid["cell_columns"],
        radius=radius,
        current_best_distances=seed["columns"]["nearest_distances"],
        current_best_item_ids=seed["columns"]["nearest_item_ids"],
        max_inline_points=max_inline_points,
        emit_pruned_rows=False,
        sort_rows=sort_rows,
        return_split_frontiers=False,
        return_metadata=True,
    )
    columns = frontier["row_table"]["columns"]
    kinds = np.asarray(columns["frontier_kind_codes"], dtype=np.int64)
    point_counts = np.asarray(columns["point_counts"], dtype=np.int64)
    by_kind: dict[str, object] = {}
    for name, code in rt.CELL_MBR_FRONTIER_KIND_CODES.items():
        mask = kinds == int(code)
        by_kind[name] = {
            "rows": int(np.count_nonzero(mask)),
            "candidate_points": int(point_counts[mask].sum()) if np.any(mask) else 0,
            "max_point_count": int(point_counts[mask].max()) if np.any(mask) else 0,
        }
    return {
        "label": label,
        "source_point_count": len(source_points),
        "target_point_count": len(target_points),
        "grid_cell_count": int(grid["metadata"]["cell_count"]),
        "seed_candidate_distance_evaluations": int(seed["metadata"]["candidate_distance_evaluations"]),
        "frontier_row_count": int(frontier["metadata"]["row_count"]),
        "frontier_row_order": frontier["metadata"]["frontier_row_order"],
        "native_generic_symbol": frontier["metadata"]["native_generic_symbol"],
        "radius": radius,
        "by_kind": by_kind,
    }


def _parse_grid_shape(value: str) -> tuple[int, int, int]:
    parts = tuple(int(item) for item in value.lower().replace("x", ",").split(",") if item.strip())
    if len(parts) != 3:
        raise ValueError("--grid-shape must contain three dimensions")
    return parts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Probe X-HD cell-MBR frontier row kind distribution.")
    parser.add_argument("--input1", required=True)
    parser.add_argument("--input2", required=True)
    parser.add_argument("--input-type", default="ply", choices=("ply", "wkt"))
    parser.add_argument("--grid-shape", default="8,8,8")
    parser.add_argument("--max-inline-points", type=int, default=64)
    parser.add_argument("--frontier-row-order", default="native", choices=("sorted", "native"))
    parser.add_argument("--summary", required=True)
    args = parser.parse_args(argv)

    points_a = translate_points_to_min_bound(load_points(Path(args.input1), n_dims=3, input_type=args.input_type))
    points_b = translate_points_to_min_bound(load_points(Path(args.input2), n_dims=3, input_type=args.input_type))
    grid_shape = _parse_grid_shape(args.grid_shape)
    sort_rows = args.frontier_row_order == "sorted"
    summary = {
        "schema": "rtdl.paper_reproduction.xhd.frontier_kind_distribution_probe.v1",
        "paper_app": "x-hd-paper",
        "input1": str(args.input1),
        "input2": str(args.input2),
        "grid_shape": grid_shape,
        "max_inline_points": int(args.max_inline_points),
        "frontier_row_order": args.frontier_row_order,
        "directions": [
            _direction_summary(
                points_a,
                points_b,
                label="a_to_b",
                grid_shape=grid_shape,
                max_inline_points=args.max_inline_points,
                sort_rows=sort_rows,
            ),
            _direction_summary(
                points_b,
                points_a,
                label="b_to_a",
                grid_shape=grid_shape,
                max_inline_points=args.max_inline_points,
                sort_rows=sort_rows,
            ),
        ],
        "boundary": (
            "Diagnostic frontier kind distribution for the representative X-HD "
            "route. This is not a correctness gate, performance claim, or full "
            "paper reproduction claim."
        ),
        "paper_reproduction_claim_authorized": False,
        "performance_claim_authorized": False,
    }
    out = Path(args.summary)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

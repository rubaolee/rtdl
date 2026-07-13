from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))


def _fixture_3d():
    import rtdsl as rt

    target_points = {
        "ids": [10, 11, 12, 13, 14],
        "x": [0.0, 1.0, 10.0, 12.0, 12.5],
        "y": [0.0, 1.0, 0.0, 0.0, 0.0],
        "z": [0.0, 0.0, 0.0, 2.0, 2.0],
    }
    query_points = {
        "ids": [100, 101, 102],
        "x": [0.5, 5.0, 11.0],
        "y": [0.0, 0.0, 0.0],
        "z": [0.0, 0.0, 1.0],
    }
    grid = rt.point_grid_cell_mbrs_numpy_columns(
        target_points,
        coordinate_fields=("x", "y", "z"),
        grid_shape=(2, 1, 1),
    )
    return query_points, grid["cell_columns"]


def _columns_to_json(columns):
    return {name: values.tolist() for name, values in columns.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default=str(ROOT / "Paper-reproduction-apps/x-hd-paper/results/native_3d_cell_mbr_frontier_gate_pod_optix.json"),
    )
    args = parser.parse_args()

    import numpy as np
    import rtdsl as rt

    query_points, cell_columns = _fixture_3d()
    route_kwargs = {
        "radius": 20.0,
        "current_best_distances": [1.0, 4.5, float("inf")],
        "current_best_item_ids": [10, 11, -1],
        "max_inline_points": 2,
    }
    native = rt.cell_mbr_nearest_frontier_native_3d_optix_columns(
        query_points,
        cell_columns,
        **route_kwargs,
        return_metadata=True,
    )
    oracle = rt.cell_mbr_nearest_frontier_numpy_columns(
        query_points,
        cell_columns,
        coordinate_fields=("x", "y", "z"),
        **route_kwargs,
    )

    mismatches = []
    for name, expected in oracle["row_table"]["columns"].items():
        actual = native["row_table"]["columns"][name]
        if actual.dtype.kind == "f":
            if not np.allclose(actual, expected, rtol=0.0, atol=1.0e-9):
                mismatches.append(name)
        elif actual.tolist() != expected.tolist():
            mismatches.append(name)

    matched = not mismatches
    summary = {
        "schema": "rtdl.paper_reproduction.xhd.native_3d_cell_mbr_frontier_gate.v1",
        "status": "native_3d_cell_mbr_frontier_gate_completed" if matched else "mismatch",
        "fixture": "goal5148_synthetic_3d_cell_mbr_frontier",
        "matched": matched,
        "mismatched_columns": mismatches,
        "native_metadata": native["metadata"],
        "native_columns": _columns_to_json(native["row_table"]["columns"]),
        "oracle_columns": _columns_to_json(oracle["row_table"]["columns"]),
        "claim_boundary": {
            "generic_native_symbol": "rtdl_optix_collect_cell_mbr_nearest_frontier_3d",
            "app_semantics": "none",
            "full_native_abi_backend_complete": False,
            "xhd_performance_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
        },
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if matched else 1


if __name__ == "__main__":
    raise SystemExit(main())

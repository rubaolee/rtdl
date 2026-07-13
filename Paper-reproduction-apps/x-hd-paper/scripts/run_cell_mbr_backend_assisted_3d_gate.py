from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time


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
    return query_points, grid


def _columns_as_lists(table):
    return {name: values.tolist() for name, values in table["columns"].items()}


def run_gate(*, backend: str) -> dict[str, object]:
    import rtdsl as rt

    query_points, grid = _fixture_3d()
    started = time.perf_counter()
    assisted = rt.cell_mbr_nearest_frontier_aabb_membership_3d_numpy_columns(
        query_points,
        grid["cell_columns"],
        radius=20.0,
        current_best_distances=[1.0, 4.5, float("inf")],
        current_best_item_ids=[10, 11, -1],
        max_inline_points=2,
        backend=backend,
        return_metadata=True,
    )
    elapsed_sec = time.perf_counter() - started
    oracle = rt.cell_mbr_nearest_frontier_numpy_columns(
        query_points,
        grid["cell_columns"],
        coordinate_fields=("x", "y", "z"),
        radius=20.0,
        current_best_distances=[1.0, 4.5, float("inf")],
        current_best_item_ids=[10, 11, -1],
        max_inline_points=2,
    )
    assisted_columns = _columns_as_lists(assisted["row_table"])
    oracle_columns = _columns_as_lists(oracle["row_table"])
    matched = assisted_columns == oracle_columns
    return {
        "schema": "rtdl.paper_reproduction.xhd.backend_assisted_3d_cell_mbr_gate.v1",
        "goal": "Goal5147",
        "fixture": "goal5147_synthetic_3d_cell_mbr_frontier",
        "backend": backend,
        "status": "backend_assisted_3d_cell_mbr_gate_completed" if matched else "mismatch",
        "matched": matched,
        "elapsed_sec": elapsed_sec,
        "assisted_columns": assisted_columns,
        "oracle_columns": oracle_columns,
        "metadata": assisted["metadata"],
        "claim_boundary": {
            "generic_3d_backend_assisted_frontdoor": True,
            "complete_native_goal5140_backend_claim": False,
            "paper_reproduction_claim": False,
            "xhd_performance_claim": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=("cpu", "optix"), default="cpu")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    summary = run_gate(backend=args.backend)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

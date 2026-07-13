from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))


def _fixture() -> tuple[dict[str, list[float] | list[int]], dict[str, Any], dict[str, Any]]:
    import rtdsl as rt

    facility_points = {
        "ids": [10, 11, 12, 13, 14],
        "x": [0.0, 1.0, 10.0, 12.0, 12.5],
        "y": [0.0, 1.0, 0.0, 0.0, 0.0],
    }
    demand_points = {
        "ids": [100, 101, 102],
        "x": [0.5, 5.0, 11.0],
        "y": [0.0, 0.0, 0.0],
    }
    grid = rt.point_grid_cell_mbrs_numpy_columns(
        facility_points,
        coordinate_fields=("x", "y"),
        grid_shape=(2, 1),
    )
    candidates = rt.radius_cell_mbr_candidate_rows_numpy_columns(
        demand_points,
        grid["cell_columns"],
        coordinate_fields=("x", "y"),
        radius=20.0,
    )
    reference_frontier = rt.nearest_state_frontier_from_cell_candidates_numpy_columns(
        candidates["columns"],
        grid["cell_columns"],
        query_point_ids=demand_points["ids"],
        current_best_distances=[1.0, 4.5, float("inf")],
        current_best_item_ids=[10, 11, -1],
        max_inline_points=2,
    )
    reference_table = rt.cell_mbr_frontiers_to_row_table_numpy_columns(
        reference_frontier,
        return_metadata=True,
    )
    return demand_points, grid, reference_table


def _columns_as_lists(table: dict[str, Any]) -> dict[str, list[Any]]:
    return {name: column.tolist() for name, column in table["columns"].items()}


def _build_success_summary(args: argparse.Namespace) -> dict[str, Any]:
    import rtdsl as rt

    demand_points, grid, reference_table = _fixture()
    start = time.perf_counter()
    assisted = rt.cell_mbr_nearest_frontier_aabb_membership_2d_numpy_columns(
        demand_points,
        grid["cell_columns"],
        radius=20.0,
        current_best_distances=[1.0, 4.5, float("inf")],
        current_best_item_ids=[10, 11, -1],
        max_inline_points=2,
        backend=args.backend,
        return_metadata=True,
    )
    elapsed = time.perf_counter() - start
    reference_columns = _columns_as_lists(reference_table)
    assisted_columns = _columns_as_lists(assisted["row_table"])
    matched = reference_columns == assisted_columns
    return {
        "schema": "rtdl.paper_reproduction.xhd.cell_mbr_backend_assisted_gate.v1",
        "goal": "Goal5144",
        "status": "cell_mbr_backend_assisted_gate_completed",
        "backend": args.backend,
        "matched": bool(matched),
        "elapsed_sec": elapsed,
        "fixture": "goal5142_synthetic_2d_cell_mbr_frontier",
        "reference_contract": reference_table["metadata"]["contract"],
        "assisted_contract": assisted["metadata"]["contract"],
        "native_abi_contract": assisted["metadata"]["native_abi_contract"],
        "broadphase_contract": assisted["metadata"]["broadphase_contract"],
        "broadphase_native_symbol": assisted["metadata"]["broadphase_native_symbol"],
        "row_count": assisted["metadata"]["row_count"],
        "broadphase_row_count": assisted["metadata"]["broadphase_row_count"],
        "exact_candidate_row_count": assisted["metadata"]["exact_candidate_row_count"],
        "reference_columns": reference_columns,
        "assisted_columns": assisted_columns,
        "claim_boundary": {
            "xhd_performance_claim": False,
            "native_goal5140_backend_claim": False,
            "paper_reproduction_claim": False,
            "backend_assisted_correctness_gate": True,
        },
    }


def build_summary(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    try:
        return _build_success_summary(args), 0
    except Exception as exc:  # noqa: BLE001 - gate records fail-closed details.
        summary = {
            "schema": "rtdl.paper_reproduction.xhd.cell_mbr_backend_assisted_gate.v1",
            "goal": "Goal5144",
            "status": "cell_mbr_backend_assisted_gate_failed",
            "backend": args.backend,
            "matched": None,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "claim_boundary": {
                "xhd_performance_claim": False,
                "native_goal5140_backend_claim": False,
                "paper_reproduction_claim": False,
                "backend_assisted_correctness_gate": False,
            },
        }
        return summary, 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the generic cell-MBR backend-assisted frontier gate."
    )
    parser.add_argument("--backend", choices=("cpu", "embree", "optix"), required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args(argv)

    summary, code = build_summary(args)
    out = Path(args.summary)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())

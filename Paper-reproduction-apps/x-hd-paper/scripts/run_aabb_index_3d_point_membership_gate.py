from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))


def _fixture() -> tuple[tuple[tuple[int, float, float, float, float, float, float], ...], tuple[tuple[int, float, float, float], ...]]:
    boxes = (
        (10, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0),
        (11, 0.5, 0.5, 0.5, 2.0, 2.0, 2.0),
        (12, -2.0, -2.0, -2.0, -1.0, -1.0, -1.0),
    )
    points = (
        (100, 0.25, 0.25, 0.25),
        (101, 0.75, 0.75, 0.75),
        (102, 1.5, 1.5, 1.5),
        (103, -1.5, -1.5, -1.5),
        (104, 9.0, 9.0, 9.0),
    )
    return boxes, points


def _expected_rows(
    boxes: tuple[tuple[int, float, float, float, float, float, float], ...],
    points: tuple[tuple[int, float, float, float], ...],
) -> list[list[int]]:
    rows: list[list[int]] = []
    for point_id, x, y, z in points:
        for box_id, min_x, min_y, min_z, max_x, max_y, max_z in boxes:
            if min_x <= x <= max_x and min_y <= y <= max_y and min_z <= z <= max_z:
                rows.append([int(point_id), int(box_id)])
    rows.sort()
    return rows


def build_summary(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    boxes, points = _fixture()
    expected_rows = _expected_rows(boxes, points)
    try:
        import rtdsl as rt

        start = time.perf_counter()
        native = rt.collect_aabb_point_membership_pair_rows_3d_optix(
            boxes,
            points,
            row_capacity=args.row_capacity,
        )
        elapsed = time.perf_counter() - start
        observed_rows = [list(row) for row in native["candidate_id_rows"]]
        matched = observed_rows == expected_rows
        return {
            "schema": "rtdl.paper_reproduction.xhd.aabb_index_3d_point_membership_gate.v1",
            "goal": "Goal5146",
            "status": "aabb_index_3d_point_membership_gate_completed",
            "matched": bool(matched),
            "elapsed_sec": elapsed,
            "fixture": "goal5146_synthetic_3d_aabb_point_membership",
            "backend": native["backend"],
            "primitive": native["primitive"],
            "contract": native["contract"],
            "native_generic_symbol": native["native_generic_symbol"],
            "row_schema": list(native["row_schema"]),
            "row_capacity": int(native["row_capacity"]),
            "valid_count": int(native["valid_count"]),
            "expected_rows": expected_rows,
            "observed_rows": observed_rows,
            "claim_boundary": {
                "xhd_performance_claim": False,
                "native_goal5140_backend_claim": False,
                "paper_reproduction_claim": False,
                "generic_3d_aabb_point_membership_gate": True,
            },
        }, (0 if matched else 1)
    except Exception as exc:  # noqa: BLE001 - gate records fail-closed details.
        return {
            "schema": "rtdl.paper_reproduction.xhd.aabb_index_3d_point_membership_gate.v1",
            "goal": "Goal5146",
            "status": "aabb_index_3d_point_membership_gate_failed",
            "matched": None,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "expected_rows": expected_rows,
            "claim_boundary": {
                "xhd_performance_claim": False,
                "native_goal5140_backend_claim": False,
                "paper_reproduction_claim": False,
                "generic_3d_aabb_point_membership_gate": False,
            },
        }, 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the generic OptiX 3-D AABB point-membership row gate."
    )
    parser.add_argument("--summary", required=True)
    parser.add_argument("--row-capacity", type=int, default=16)
    args = parser.parse_args(argv)

    summary, code = build_summary(args)
    out = Path(args.summary)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())

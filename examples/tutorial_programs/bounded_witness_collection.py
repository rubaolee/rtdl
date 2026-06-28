from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl as rt
import rtdsl.v4 as rtdl_v4
from rtdsl.reference import Segment


@rt.kernel(backend="rtdl", precision="float_approx")
def segment_witness_rows_kernel():
    left_segments = rt.input("left_segments", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    right_segments = rt.input("right_segments", rt.Segments, layout=rt.Segment2DLayout, role="build")
    candidates = rt.traverse(left_segments, right_segments, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(hits, fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"])


def make_case() -> dict[str, tuple[Segment, ...]]:
    return {
        "left_segments": (
            Segment(id=1, x0=0.0, y0=0.0, x1=4.0, y1=4.0),
            Segment(id=2, x0=0.0, y0=3.0, x1=4.0, y1=3.0),
        ),
        "right_segments": (
            Segment(id=100, x0=0.0, y0=4.0, x1=4.0, y1=0.0),
            Segment(id=101, x0=2.0, y0=0.0, x1=2.0, y1=4.0),
            Segment(id=102, x0=3.0, y0=0.0, x1=3.0, y1=4.0),
        ),
    }


def _bounded_collect(
    candidate_rows: tuple[dict[str, float | int], ...],
    *,
    capacity: int,
) -> dict[str, object]:
    collected_rows = []
    validation_rows = []
    for pair_id in sorted({int(row["pair_id"]) for row in candidate_rows}):
        rows = [row for row in candidate_rows if int(row["pair_id"]) == pair_id]
        rows.sort(key=lambda row: (-float(row["depth"]), int(row["witness_id"])))
        kept = rows[:capacity]
        overflowed = len(rows) > capacity
        collected_rows.extend({**row, "slot": slot} for slot, row in enumerate(kept))
        validation_rows.append(
            {
                "pair_id": pair_id,
                "candidate_count": len(rows),
                "kept_count": len(kept),
                "capacity": capacity,
                "overflowed": overflowed,
            }
        )
    return {
        "capacity": capacity,
        "collected_rows": tuple(collected_rows),
        "validation_rows": tuple(validation_rows),
    }


def _witness_rows_from_kernel_rows(rows: tuple[dict[str, float | int], ...]) -> tuple[dict[str, float | int], ...]:
    witnesses = []
    for row in rows:
        pair_id = int(row["left_id"])
        witness_id = int(row["right_id"])
        # In a real contact workload this score would come from contact depth.
        # Here it is deterministic teaching data derived from the witness id.
        depth = 0.01 * (witness_id - 99)
        witnesses.append(
            {
                "pair_id": pair_id,
                "witness_id": witness_id,
                "depth": round(depth, 4),
                "x": round(float(row["intersection_point_x"]), 4),
                "y": round(float(row["intersection_point_y"]), 4),
            }
        )
    return tuple(witnesses)


def run_kernel_mode() -> dict[str, object]:
    case = make_case()
    compiled = rt.compile_kernel(segment_witness_rows_kernel)
    rows = tuple(rt.run_cpu_python_reference(segment_witness_rows_kernel, **case))
    witness_rows = _witness_rows_from_kernel_rows(rows)
    bounded = _bounded_collect(witness_rows, capacity=2)
    return {
        "mode": "kernel_plus_continuation",
        "status": "ok",
        "teaches": (
            "RTDL kernel emits witness rows; bounded collection keeps K witnesses "
            "per app-owned pair and reports overflow"
        ),
        "kernel_summary": compiled.format(),
        "candidate_witness_rows": witness_rows,
        **bounded,
    }


def run_visible_flow() -> dict[str, object]:
    candidate_rows = (
        {"pair_id": 1, "witness_id": 100, "depth": 0.05},
        {"pair_id": 1, "witness_id": 101, "depth": 0.08},
        {"pair_id": 1, "witness_id": 102, "depth": 0.02},
        {"pair_id": 2, "witness_id": 200, "depth": 0.03},
    )
    bounded = _bounded_collect(candidate_rows, capacity=2)
    return {
        "mode": "visible_python_flow",
        "status": "ok",
        "concept": "manual bounded collection over witness rows",
        "manual_data_flow": "candidate witness rows -> sort by score -> keep K rows per pair -> overflow validation",
        "candidate_rows": candidate_rows,
        **bounded,
    }


def run_v4_mode() -> dict[str, object]:
    plan = rtdl_v4.plan_operator_request_v4("closest_hit_argmin", partner="torch")
    return {
        "mode": "v4",
        "status": "ok",
        "teaches": "V4 operator/runtime mapping for closest-witness grouped argmin",
        "operator": "closest_hit_argmin",
        "partner": "torch",
        "plan_status": plan.status,
        "surface": plan.api_surface,
        "generic_primitive": plan.generic_primitive,
        "relationship_to_kernel": (
            "The kernel produces witness rows. Bounded collection and grouped "
            "argmin consume those rows. V4 exposes a measured grouped-argmin "
            "surface for recognized closest-witness patterns."
        ),
    }


def run_both_modes() -> dict[str, object]:
    kernel = run_kernel_mode()
    v4 = run_v4_mode()
    return {
        "status": "ok",
        "concept": "bounded witness collection is a continuation over emitted witness rows",
        "kernel_mode": kernel,
        "visible_flow": run_visible_flow(),
        "v4_mode": v4,
        "same_semantics": {
            "relation": "candidate_witness_rows_to_bounded_witness_rows",
            "kernel_output_field": "candidate_witness_rows",
            "continuation_output_field": "collected_rows",
            "v4_execution_target": v4["surface"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="RTDL bounded-witness tutorial")
    parser.add_argument("--mode", choices=("kernel", "v4", "both", "visible"), default="both")
    args = parser.parse_args()
    if args.mode == "kernel":
        payload = run_kernel_mode()
    elif args.mode == "v4":
        payload = run_v4_mode()
    elif args.mode == "visible":
        payload = run_visible_flow()
    else:
        payload = run_both_modes()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

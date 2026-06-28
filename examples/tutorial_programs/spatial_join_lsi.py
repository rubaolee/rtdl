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
def line_segment_intersection_kernel():
    left_segments = rt.input("left_segments", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    right_segments = rt.input("right_segments", rt.Segments, layout=rt.Segment2DLayout, role="build")
    candidates = rt.traverse(left_segments, right_segments, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(hits, fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"])


def make_case() -> dict[str, tuple[Segment, ...]]:
    return {
        "left_segments": (
            Segment(id=100, x0=0.0, y0=0.0, x1=4.0, y1=4.0),
            Segment(id=101, x0=0.0, y0=3.0, x1=4.0, y1=3.0),
            Segment(id=102, x0=0.0, y0=5.0, x1=4.0, y1=5.0),
        ),
        "right_segments": (
            Segment(id=200, x0=0.0, y0=4.0, x1=4.0, y1=0.0),
            Segment(id=201, x0=2.0, y0=0.0, x1=2.0, y1=4.0),
            Segment(id=202, x0=5.0, y0=5.0, x1=6.0, y1=6.0),
        ),
    }


def _bounds(segment: Segment) -> dict[str, float | int]:
    return {
        "segment_id": int(segment.id),
        "min_x": min(float(segment.x0), float(segment.x1)),
        "min_y": min(float(segment.y0), float(segment.y1)),
        "max_x": max(float(segment.x0), float(segment.x1)),
        "max_y": max(float(segment.y0), float(segment.y1)),
    }


def _overlaps(left: dict[str, float | int], right: dict[str, float | int]) -> bool:
    return not (
        float(left["max_x"]) < float(right["min_x"])
        or float(right["max_x"]) < float(left["min_x"])
        or float(left["max_y"]) < float(right["min_y"])
        or float(right["max_y"]) < float(left["min_y"])
    )


def _orientation(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _segments_cross(left: Segment, right: Segment) -> bool:
    a0 = (float(left.x0), float(left.y0))
    a1 = (float(left.x1), float(left.y1))
    b0 = (float(right.x0), float(right.y0))
    b1 = (float(right.x1), float(right.y1))
    left0 = _orientation(a0, a1, b0)
    left1 = _orientation(a0, a1, b1)
    right0 = _orientation(b0, b1, a0)
    right1 = _orientation(b0, b1, a1)
    return left0 * left1 <= 0.0 and right0 * right1 <= 0.0


def run_kernel_mode() -> dict[str, object]:
    case = make_case()
    compiled = rt.compile_kernel(line_segment_intersection_kernel)
    rows = tuple(rt.run_cpu_python_reference(line_segment_intersection_kernel, **case))
    return {
        "mode": "kernel",
        "status": "ok",
        "teaches": (
            "RTDL kernel: input left/right segments, traverse candidate pairs, "
            "refine(segment_intersection), emit intersection witness rows"
        ),
        "kernel_summary": compiled.format(),
        "left_segments": tuple(segment.__dict__ for segment in case["left_segments"]),
        "right_segments": tuple(segment.__dict__ for segment in case["right_segments"]),
        "exact_intersection_rows": tuple(
            {
                "left_id": int(row["left_id"]),
                "right_id": int(row["right_id"]),
                "intersection_point_x": round(float(row["intersection_point_x"]), 4),
                "intersection_point_y": round(float(row["intersection_point_y"]), 4),
            }
            for row in rows
        ),
    }


def run_visible_flow() -> dict[str, object]:
    case = make_case()
    left_segments = case["left_segments"]
    right_segments = case["right_segments"]
    left_bounds = tuple(_bounds(segment) for segment in left_segments)
    right_bounds = tuple(_bounds(segment) for segment in right_segments)
    broadphase_rows = []
    exact_rows = []
    for left_segment, left_box in zip(left_segments, left_bounds):
        for right_segment, right_box in zip(right_segments, right_bounds):
            if not _overlaps(left_box, right_box):
                continue
            row = {"left_id": int(left_segment.id), "right_id": int(right_segment.id)}
            broadphase_rows.append(row)
            if _segments_cross(left_segment, right_segment):
                exact_rows.append({**row, "intersects": True})

    return {
        "mode": "visible_python_flow",
        "status": "ok",
        "concept": "manual mirror of spatial join: AABB broadphase candidate pairs plus exact LSI refinement",
        "manual_data_flow": (
            "segments -> AABB bounds -> candidate pair rows -> exact line-segment intersection rows"
        ),
        "left_bounds": left_bounds,
        "right_bounds": right_bounds,
        "broadphase_candidate_pairs": tuple(broadphase_rows),
        "exact_intersection_pairs": tuple(exact_rows),
    }


def run_v4_mode() -> dict[str, object]:
    plan = rtdl_v4.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")
    return {
        "mode": "v4",
        "status": "ok",
        "teaches": (
            "V4 operator/runtime mapping for broadphase spatial-join candidate "
            "generation; exact LSI remains the RTDL kernel predicate above"
        ),
        "operator": "aabb_index_query",
        "partner": "rtdl_native",
        "plan_status": plan.status,
        "surface": plan.api_surface,
        "generic_primitive": plan.generic_primitive,
        "relationship_to_kernel": (
            "The kernel teaches the language relation: segment pairs refined by "
            "segment_intersection. The V4 AABB route is the prepared broadphase "
            "surface used to produce candidate pairs for that relation."
        ),
    }


def run_both_modes() -> dict[str, object]:
    kernel = run_kernel_mode()
    v4 = run_v4_mode()
    return {
        "status": "ok",
        "concept": (
            "line-segment spatial join is first an RTDL kernel relation; V4 then "
            "maps candidate generation to a prepared operator surface"
        ),
        "kernel_mode": kernel,
        "visible_flow": run_visible_flow(),
        "v4_mode": v4,
        "same_semantics": {
            "relation": "segment_pair_intersection_rows",
            "kernel_output_field": "exact_intersection_rows",
            "v4_execution_target": v4["surface"],
            "v4_scope": "broadphase candidate generation plus prepared routing",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="RTDL line-segment spatial-join tutorial")
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

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def _bounds(segment: dict[str, float | int]) -> dict[str, float | int]:
    return {
        "segment_id": int(segment["id"]),
        "min_x": min(float(segment["x0"]), float(segment["x1"])),
        "min_y": min(float(segment["y0"]), float(segment["y1"])),
        "max_x": max(float(segment["x0"]), float(segment["x1"])),
        "max_y": max(float(segment["y0"]), float(segment["y1"])),
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


def _segments_cross(left: dict[str, float | int], right: dict[str, float | int]) -> bool:
    a0 = (float(left["x0"]), float(left["y0"]))
    a1 = (float(left["x1"]), float(left["y1"]))
    b0 = (float(right["x0"]), float(right["y0"]))
    b1 = (float(right["x1"]), float(right["y1"]))
    left0 = _orientation(a0, a1, b0)
    left1 = _orientation(a0, a1, b1)
    right0 = _orientation(b0, b1, a0)
    right1 = _orientation(b0, b1, a1)
    return left0 * left1 <= 0.0 and right0 * right1 <= 0.0


def main() -> int:
    left_segments = (
        {"id": 100, "x0": 0.0, "y0": 0.0, "x1": 4.0, "y1": 4.0},
        {"id": 101, "x0": 0.0, "y0": 3.0, "x1": 4.0, "y1": 3.0},
        {"id": 102, "x0": 0.0, "y0": 5.0, "x1": 4.0, "y1": 5.0},
    )
    right_segments = (
        {"id": 200, "x0": 0.0, "y0": 4.0, "x1": 4.0, "y1": 0.0},
        {"id": 201, "x0": 2.0, "y0": 0.0, "x1": 2.0, "y1": 4.0},
        {"id": 202, "x0": 5.0, "y0": 5.0, "x1": 6.0, "y1": 6.0},
    )

    left_bounds = tuple(_bounds(segment) for segment in left_segments)
    right_bounds = tuple(_bounds(segment) for segment in right_segments)
    broadphase_rows = []
    exact_rows = []
    for left_segment, left_box in zip(left_segments, left_bounds):
        for right_segment, right_box in zip(right_segments, right_bounds):
            if not _overlaps(left_box, right_box):
                continue
            row = {"left_id": int(left_segment["id"]), "right_id": int(right_segment["id"])}
            broadphase_rows.append(row)
            if _segments_cross(left_segment, right_segment):
                exact_rows.append({**row, "intersects": True})

    plan = rtdl_v4.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")
    payload = {
        "status": "ok",
        "concept": "spatial join is broadphase pair generation plus exact refinement; RTDL accelerates the candidate relation, app logic owns the final predicate",
        "manual_data_flow": (
            "segments -> AABB bounds -> candidate pair rows -> exact line-segment intersection rows"
        ),
        "left_bounds": left_bounds,
        "right_bounds": right_bounds,
        "broadphase_candidate_pairs": tuple(broadphase_rows),
        "exact_intersection_pairs": tuple(exact_rows),
        "v4_surface": {
            "operator": "aabb_index_query",
            "partner": "rtdl_native",
            "status": plan.status,
            "surface": plan.api_surface,
            "generic_primitive": plan.generic_primitive,
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

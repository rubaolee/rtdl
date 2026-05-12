from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from rtdsl.reference import Point, Polygon, Segment


@rt.kernel(backend="rtdl", precision="float_approx")
def frechet_cell_broadphase_kernel():
    curve_segments = rt.input("curve_segments", rt.Segments, role="probe")
    segment_tubes = rt.input("segment_tubes", rt.Polygons, role="build")
    candidates = rt.traverse(curve_segments, segment_tubes, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_polygon_anyhit_rows())
    return rt.emit(hits, fields=["segment_id", "polygon_id"])


Interval = tuple[float, float] | None


def make_authored_curves(copies: int = 1) -> dict[str, tuple[Point, ...]]:
    if copies < 1:
        raise ValueError("copies must be at least 1")

    base_p = (
        Point(id=1, x=0.0, y=0.0),
        Point(id=2, x=1.0, y=0.0),
        Point(id=3, x=2.0, y=0.5),
        Point(id=4, x=3.0, y=0.5),
    )
    base_q = (
        Point(id=101, x=0.0, y=0.2),
        Point(id=102, x=1.0, y=0.1),
        Point(id=103, x=2.0, y=0.7),
        Point(id=104, x=3.0, y=0.6),
    )

    curve_p: list[Point] = []
    curve_q: list[Point] = []
    for copy_index in range(copies):
        x_offset = 4.0 * copy_index
        id_offset = 1000 * copy_index
        for point in base_p:
            curve_p.append(Point(id=point.id + id_offset, x=point.x + x_offset, y=point.y))
        for point in base_q:
            curve_q.append(Point(id=point.id + id_offset, x=point.x + x_offset, y=point.y))
    return {"curve_p": tuple(curve_p), "curve_q": tuple(curve_q)}


def _segments_from_curve(curve: tuple[Point, ...]) -> tuple[Segment, ...]:
    return tuple(
        Segment(id=index + 1, x0=a.x, y0=a.y, x1=b.x, y1=b.y)
        for index, (a, b) in enumerate(zip(curve, curve[1:]))
    )


def _expanded_segment_boxes(segments: tuple[Segment, ...], radius: float) -> tuple[Polygon, ...]:
    pad = max(float(radius), 1.0e-12)
    boxes = []
    for index, segment in enumerate(segments):
        min_x = min(segment.x0, segment.x1) - pad
        max_x = max(segment.x0, segment.x1) + pad
        min_y = min(segment.y0, segment.y1) - pad
        max_y = max(segment.y0, segment.y1) + pad
        boxes.append(
            Polygon(
                id=index + 1,
                vertices=((min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)),
            )
        )
    return tuple(boxes)


def _run_broadphase_rows(
    backend: str,
    curve_segments: tuple[Segment, ...],
    segment_tubes: tuple[Polygon, ...],
    *,
    require_rt_core: bool,
    output_capacity: int,
) -> tuple[dict[str, object], ...]:
    if require_rt_core and backend != "optix":
        raise ValueError("--require-rt-core is only meaningful with --backend optix")
    if require_rt_core:
        return rt.segment_polygon_anyhit_rows_native_bounded_optix(
            curve_segments,
            segment_tubes,
            output_capacity=output_capacity,
        )
    if backend == "cpu_python_reference":
        return rt.run_cpu_python_reference(
            frechet_cell_broadphase_kernel,
            curve_segments=curve_segments,
            segment_tubes=segment_tubes,
        )
    if backend == "cpu":
        return rt.run_cpu(
            frechet_cell_broadphase_kernel,
            curve_segments=curve_segments,
            segment_tubes=segment_tubes,
        )
    if backend == "embree":
        return rt.run_embree(
            frechet_cell_broadphase_kernel,
            curve_segments=curve_segments,
            segment_tubes=segment_tubes,
        )
    if backend == "optix":
        return rt.run_optix(
            frechet_cell_broadphase_kernel,
            curve_segments=curve_segments,
            segment_tubes=segment_tubes,
        )
    if backend == "vulkan":
        return rt.run_vulkan(
            frechet_cell_broadphase_kernel,
            curve_segments=curve_segments,
            segment_tubes=segment_tubes,
        )
    raise ValueError(f"unsupported backend `{backend}`")


def _candidate_cells_from_rows(rows: Iterable[dict[str, object]]) -> frozenset[tuple[int, int]]:
    return frozenset((int(row["segment_id"]) - 1, int(row["polygon_id"]) - 1) for row in rows)


def _clip_interval(interval: Interval, start: float) -> Interval:
    if interval is None:
        return None
    lo, hi = interval
    lo = max(lo, start)
    if lo > hi + 1.0e-12:
        return None
    return (lo, hi)


def _contains(interval: Interval, value: float) -> bool:
    return interval is not None and interval[0] <= value <= interval[1]


def _union_single_interval(a: Interval, b: Interval) -> Interval:
    if a is None:
        return b
    if b is None:
        return a
    return (min(a[0], b[0]), max(a[1], b[1]))


def _point_segment_free_interval(a: Point, b: Point, p: Point, radius: float) -> Interval:
    vx = b.x - a.x
    vy = b.y - a.y
    wx = a.x - p.x
    wy = a.y - p.y
    qa = vx * vx + vy * vy
    qb = 2.0 * (vx * wx + vy * wy)
    qc = wx * wx + wy * wy - radius * radius
    if qa == 0.0:
        return (0.0, 1.0) if qc <= 1.0e-12 else None
    disc = qb * qb - 4.0 * qa * qc
    if disc < -1.0e-12:
        return None
    disc = max(0.0, disc)
    root = math.sqrt(disc)
    lo = (-qb - root) / (2.0 * qa)
    hi = (-qb + root) / (2.0 * qa)
    lo = max(0.0, lo)
    hi = min(1.0, hi)
    if lo > hi + 1.0e-12:
        return None
    return (lo, hi)


def _distance(a: Point, b: Point) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def continuous_frechet_decision(
    curve_p: tuple[Point, ...],
    curve_q: tuple[Point, ...],
    radius: float,
    *,
    candidate_cells: frozenset[tuple[int, int]] | None = None,
) -> bool:
    if len(curve_p) < 2 or len(curve_q) < 2:
        raise ValueError("continuous Frechet distance requires two curves with at least two points each")
    if radius < 0.0:
        return False
    if _distance(curve_p[0], curve_q[0]) > radius + 1.0e-12:
        return False
    if _distance(curve_p[-1], curve_q[-1]) > radius + 1.0e-12:
        return False

    p_count = len(curve_p) - 1
    q_count = len(curve_q) - 1
    reach_top: list[list[Interval]] = [[None for _ in range(q_count)] for _ in range(p_count)]
    reach_right: list[list[Interval]] = [[None for _ in range(q_count)] for _ in range(p_count)]

    for i in range(p_count):
        for j in range(q_count):
            if candidate_cells is not None and (i, j) not in candidate_cells:
                continue

            p0, p1 = curve_p[i], curve_p[i + 1]
            q0, q1 = curve_q[j], curve_q[j + 1]
            bottom_free = _point_segment_free_interval(p0, p1, q0, radius)
            top_free = _point_segment_free_interval(p0, p1, q1, radius)
            left_free = _point_segment_free_interval(q0, q1, p0, radius)
            right_free = _point_segment_free_interval(q0, q1, p1, radius)

            if j > 0:
                bottom_reach = reach_top[i][j - 1]
            elif i == 0:
                bottom_reach = _clip_interval(bottom_free, 0.0) if _contains(bottom_free, 0.0) else None
            elif _contains(reach_right[i - 1][j], 0.0):
                bottom_reach = _clip_interval(bottom_free, 0.0)
            else:
                bottom_reach = None

            if i > 0:
                left_reach = reach_right[i - 1][j]
            elif j == 0:
                left_reach = _clip_interval(left_free, 0.0) if _contains(left_free, 0.0) else None
            elif _contains(reach_top[i][j - 1], 0.0):
                left_reach = _clip_interval(left_free, 0.0)
            else:
                left_reach = None

            top_from_bottom = _clip_interval(top_free, bottom_reach[0]) if bottom_reach is not None else None
            top_from_left = top_free if left_reach is not None else None
            right_from_bottom = right_free if bottom_reach is not None else None
            right_from_left = _clip_interval(right_free, left_reach[0]) if left_reach is not None else None
            reach_top[i][j] = _union_single_interval(top_from_bottom, top_from_left)
            reach_right[i][j] = _union_single_interval(right_from_bottom, right_from_left)

    return _contains(reach_top[p_count - 1][q_count - 1], 1.0) or _contains(
        reach_right[p_count - 1][q_count - 1],
        1.0,
    )


def _upper_bound(curve_p: tuple[Point, ...], curve_q: tuple[Point, ...]) -> float:
    return max(_distance(a, b) for a in curve_p for b in curve_q) + 1.0


def continuous_frechet_distance_estimate(
    curve_p: tuple[Point, ...],
    curve_q: tuple[Point, ...],
    *,
    iterations: int,
    candidate_provider,
) -> dict[str, object]:
    lo = 0.0
    hi = _upper_bound(curve_p, curve_q)
    candidate_cell_count = None
    broadphase_row_count = None
    for _ in range(iterations):
        mid = (lo + hi) * 0.5
        candidate_cells, row_count = candidate_provider(mid)
        candidate_cell_count = len(candidate_cells) if candidate_cells is not None else None
        broadphase_row_count = row_count
        if continuous_frechet_decision(curve_p, curve_q, mid, candidate_cells=candidate_cells):
            hi = mid
        else:
            lo = mid
    return {
        "distance_estimate": hi,
        "lower_bound": lo,
        "upper_bound": hi,
        "iterations": iterations,
        "last_candidate_cell_count": candidate_cell_count,
        "last_broadphase_row_count": broadphase_row_count,
    }


def run_app(
    backend: str = "cpu_python_reference",
    *,
    copies: int = 1,
    candidate_mode: str = "all_cells",
    iterations: int = 24,
    decision_radius: float | None = None,
    require_rt_core: bool = False,
    output_capacity: int = 1_000_000,
) -> dict[str, object]:
    if candidate_mode not in {"all_cells", "rtdl_broadphase"}:
        raise ValueError("candidate_mode must be 'all_cells' or 'rtdl_broadphase'")
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    case = make_authored_curves(copies=copies)
    curve_p = case["curve_p"]
    curve_q = case["curve_q"]
    p_segments = _segments_from_curve(curve_p)
    q_segments = _segments_from_curve(curve_q)
    all_cells = frozenset((i, j) for i in range(len(p_segments)) for j in range(len(q_segments)))
    phases: dict[str, float] = {}

    def candidate_provider(radius: float):
        if candidate_mode == "all_cells":
            return None, None
        broadphase_start = time.perf_counter()
        rows = _run_broadphase_rows(
            backend,
            p_segments,
            _expanded_segment_boxes(q_segments, radius),
            require_rt_core=require_rt_core,
            output_capacity=output_capacity,
        )
        phases["last_rtdl_broadphase_sec"] = time.perf_counter() - broadphase_start
        cells = _candidate_cells_from_rows(rows)
        # The start and end cells are required by the continuous Frechet boundary condition.
        cells = frozenset(set(cells) | {(0, 0), (len(p_segments) - 1, len(q_segments) - 1)})
        return cells, len(rows)

    distance_start = time.perf_counter()
    estimate = continuous_frechet_distance_estimate(
        curve_p,
        curve_q,
        iterations=iterations,
        candidate_provider=candidate_provider,
    )
    phases["distance_search_sec"] = time.perf_counter() - distance_start
    oracle_start = time.perf_counter()
    oracle = continuous_frechet_distance_estimate(
        curve_p,
        curve_q,
        iterations=iterations,
        candidate_provider=lambda radius: (None, None),
    )
    phases["oracle_search_sec"] = time.perf_counter() - oracle_start
    decision = None
    if decision_radius is not None:
        cells, row_count = candidate_provider(decision_radius)
        decision = {
            "radius": decision_radius,
            "within_radius": continuous_frechet_decision(curve_p, curve_q, decision_radius, candidate_cells=cells),
            "candidate_cell_count": len(cells) if cells is not None else len(all_cells),
            "broadphase_row_count": row_count,
        }

    return {
        "app": "continuous_frechet_distance",
        "backend": backend,
        "candidate_mode": candidate_mode,
        "copies": copies,
        "curve_p_point_count": len(curve_p),
        "curve_q_point_count": len(curve_q),
        "free_space_cell_count": len(all_cells),
        "distance_estimate": estimate["distance_estimate"],
        "oracle_distance_estimate": oracle["distance_estimate"],
        "matches_oracle": math.isclose(
            float(estimate["distance_estimate"]),
            float(oracle["distance_estimate"]),
            rel_tol=1.0e-5,
            abs_tol=1.0e-5,
        ),
        "decision": decision,
        "rtdl_role": (
            "RTDL is used as a generic segment-vs-expanded-shape broadphase over "
            "free-space cells. Python owns the continuous Frechet free-space "
            "reachability algorithm and distance search."
        ),
        "rt_core_accelerated": bool(backend == "optix" and candidate_mode == "rtdl_broadphase" and require_rt_core),
        "nvidia_rt_core_path": (
            "--backend optix --candidate-mode rtdl_broadphase --require-rt-core "
            "uses the bounded native OptiX segment/shape pair-row emitter for the "
            "cell broadphase when librtdl_optix is available."
        ),
        "claim_boundary": (
            "This is a v1.8 Python+RTDL learner app. It demonstrates how a new "
            "continuous Frechet application can route RT-shaped broadphase work "
            "through RTDL/OptiX, but it is not a universal speedup claim and the "
            "exact free-space dynamic program remains Python-owned."
        ),
        "run_phases": phases,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Continuous Frechet distance as a Python+RTDL learner app with optional RTDL broadphase.",
    )
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"),
        default="cpu_python_reference",
    )
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument("--iterations", type=int, default=24)
    parser.add_argument("--decision-radius", type=float, default=None)
    parser.add_argument(
        "--candidate-mode",
        choices=("all_cells", "rtdl_broadphase"),
        default="all_cells",
    )
    parser.add_argument(
        "--require-rt-core",
        action="store_true",
        help="Fail unless the Frechet cell broadphase uses the explicit native OptiX pair-row path.",
    )
    parser.add_argument("--output-capacity", type=int, default=1_000_000)
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_app(
                args.backend,
                copies=args.copies,
                candidate_mode=args.candidate_mode,
                iterations=args.iterations,
                decision_radius=args.decision_radius,
                require_rt_core=args.require_rt_core,
                output_capacity=args.output_capacity,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

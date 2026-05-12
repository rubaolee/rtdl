from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
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

CPP_CONTINUATION_SOURCE = r"""
#include <algorithm>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iostream>
#include <optional>
#include <utility>
#include <vector>

struct Point {
    double x;
    double y;
};

using Interval = std::optional<std::pair<double, double>>;

static double distance(Point a, Point b) {
    return std::hypot(a.x - b.x, a.y - b.y);
}

static Interval clip_interval(Interval interval, double start) {
    if (!interval) return std::nullopt;
    auto [lo, hi] = *interval;
    lo = std::max(lo, start);
    if (lo > hi + 1.0e-12) return std::nullopt;
    return std::make_pair(lo, hi);
}

static bool contains(Interval interval, double value) {
    return interval && interval->first <= value && value <= interval->second;
}

static Interval union_single_interval(Interval a, Interval b) {
    if (!a) return b;
    if (!b) return a;
    return std::make_pair(std::min(a->first, b->first), std::max(a->second, b->second));
}

static Interval point_segment_free_interval(Point a, Point b, Point p, double radius) {
    const double vx = b.x - a.x;
    const double vy = b.y - a.y;
    const double wx = a.x - p.x;
    const double wy = a.y - p.y;
    const double qa = vx * vx + vy * vy;
    const double qb = 2.0 * (vx * wx + vy * wy);
    const double qc = wx * wx + wy * wy - radius * radius;
    if (qa == 0.0) {
        return qc <= 1.0e-12 ? Interval(std::make_pair(0.0, 1.0)) : std::nullopt;
    }
    double disc = qb * qb - 4.0 * qa * qc;
    if (disc < -1.0e-12) return std::nullopt;
    disc = std::max(0.0, disc);
    const double root = std::sqrt(disc);
    double lo = (-qb - root) / (2.0 * qa);
    double hi = (-qb + root) / (2.0 * qa);
    lo = std::max(0.0, lo);
    hi = std::min(1.0, hi);
    if (lo > hi + 1.0e-12) return std::nullopt;
    return std::make_pair(lo, hi);
}

static bool decision(const std::vector<Point>& p, const std::vector<Point>& q, double radius) {
    if (p.size() < 2 || q.size() < 2) return false;
    if (radius < 0.0) return false;
    if (distance(p.front(), q.front()) > radius + 1.0e-12) return false;
    if (distance(p.back(), q.back()) > radius + 1.0e-12) return false;

    const size_t p_count = p.size() - 1;
    const size_t q_count = q.size() - 1;
    std::vector<Interval> reach_top(p_count * q_count);
    std::vector<Interval> reach_right(p_count * q_count);
    auto cell = [q_count](std::vector<Interval>& values, size_t i, size_t j) -> Interval& {
        return values[i * q_count + j];
    };

    for (size_t i = 0; i < p_count; ++i) {
        for (size_t j = 0; j < q_count; ++j) {
            const Point p0 = p[i];
            const Point p1 = p[i + 1];
            const Point q0 = q[j];
            const Point q1 = q[j + 1];
            const Interval bottom_free = point_segment_free_interval(p0, p1, q0, radius);
            const Interval top_free = point_segment_free_interval(p0, p1, q1, radius);
            const Interval left_free = point_segment_free_interval(q0, q1, p0, radius);
            const Interval right_free = point_segment_free_interval(q0, q1, p1, radius);

            Interval bottom_reach;
            Interval left_reach;
            if (j > 0) {
                bottom_reach = cell(reach_top, i, j - 1);
            } else if (i == 0) {
                bottom_reach = contains(bottom_free, 0.0) ? clip_interval(bottom_free, 0.0) : Interval{};
            } else if (contains(cell(reach_right, i - 1, j), 0.0)) {
                bottom_reach = clip_interval(bottom_free, 0.0);
            }

            if (i > 0) {
                left_reach = cell(reach_right, i - 1, j);
            } else if (j == 0) {
                left_reach = contains(left_free, 0.0) ? clip_interval(left_free, 0.0) : Interval{};
            } else if (contains(cell(reach_top, i, j - 1), 0.0)) {
                left_reach = clip_interval(left_free, 0.0);
            }

            const Interval top_from_bottom = bottom_reach ? clip_interval(top_free, bottom_reach->first) : Interval{};
            const Interval top_from_left = left_reach ? top_free : Interval{};
            const Interval right_from_bottom = bottom_reach ? right_free : Interval{};
            const Interval right_from_left = left_reach ? clip_interval(right_free, left_reach->first) : Interval{};
            cell(reach_top, i, j) = union_single_interval(top_from_bottom, top_from_left);
            cell(reach_right, i, j) = union_single_interval(right_from_bottom, right_from_left);
        }
    }
    return contains(cell(reach_top, p_count - 1, q_count - 1), 1.0) ||
           contains(cell(reach_right, p_count - 1, q_count - 1), 1.0);
}

static double upper_bound(const std::vector<Point>& p, const std::vector<Point>& q) {
    double result = 0.0;
    for (const Point& a : p) {
        for (const Point& b : q) {
            result = std::max(result, distance(a, b));
        }
    }
    return result + 1.0;
}

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "usage: rtdl_frechet_cpp_continuation curves.txt iterations\n";
        return 2;
    }
    std::ifstream input(argv[1]);
    const int iterations = std::stoi(argv[2]);
    size_t p_size = 0;
    size_t q_size = 0;
    input >> p_size >> q_size;
    std::vector<Point> p(p_size);
    std::vector<Point> q(q_size);
    for (Point& point : p) input >> point.x >> point.y;
    for (Point& point : q) input >> point.x >> point.y;

    const auto start = std::chrono::steady_clock::now();
    double lo = 0.0;
    double hi = upper_bound(p, q);
    for (int step = 0; step < iterations; ++step) {
        const double mid = (lo + hi) * 0.5;
        if (decision(p, q, mid)) {
            hi = mid;
        } else {
            lo = mid;
        }
    }
    const auto stop = std::chrono::steady_clock::now();
    const double sec = std::chrono::duration<double>(stop - start).count();
    std::cout << "{\"distance_estimate\":" << hi
              << ",\"lower_bound\":" << lo
              << ",\"upper_bound\":" << hi
              << ",\"wall_sec\":" << sec
              << "}\n";
    return 0;
}
"""


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
    tubes = []
    for index, segment in enumerate(segments):
        dx = segment.x1 - segment.x0
        dy = segment.y1 - segment.y0
        length = math.hypot(dx, dy)
        if length <= 1.0e-12:
            vertices = (
                (segment.x0 - pad, segment.y0 - pad),
                (segment.x0 + pad, segment.y0 - pad),
                (segment.x0 + pad, segment.y0 + pad),
                (segment.x0 - pad, segment.y0 + pad),
            )
        else:
            ux = dx / length
            uy = dy / length
            nx = -uy
            ny = ux
            sx = segment.x0 - ux * pad
            sy = segment.y0 - uy * pad
            ex = segment.x1 + ux * pad
            ey = segment.y1 + uy * pad
            vertices = (
                (sx + nx * pad, sy + ny * pad),
                (ex + nx * pad, ey + ny * pad),
                (ex - nx * pad, ey - ny * pad),
                (sx - nx * pad, sy - ny * pad),
            )
        tubes.append(
            Polygon(
                id=index + 1,
                vertices=vertices,
            )
        )
    return tuple(tubes)


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


def _expand_candidate_cells(
    cells: frozenset[tuple[int, int]],
    *,
    p_count: int,
    q_count: int,
    radius: int,
) -> frozenset[tuple[int, int]]:
    if radius <= 0:
        return cells
    expanded: set[tuple[int, int]] = set()
    for i, j in cells:
        for di in range(-radius, radius + 1):
            ni = i + di
            if ni < 0 or ni >= p_count:
                continue
            for dj in range(-radius, radius + 1):
                nj = j + dj
                if 0 <= nj < q_count:
                    expanded.add((ni, nj))
    return frozenset(expanded)


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


def _cpp_continuation_cache_dir() -> Path:
    root = Path(os.environ.get("RTDL_FRECHET_CPP_CACHE", ROOT / "build" / "frechet_cpp"))
    root.mkdir(parents=True, exist_ok=True)
    return root


def _build_cpp_continuation() -> Path:
    cache = _cpp_continuation_cache_dir()
    digest = hashlib.sha256(CPP_CONTINUATION_SOURCE.encode("utf-8")).hexdigest()[:16]
    suffix = ".exe" if sys.platform.startswith("win") else ""
    exe = cache / f"rtdl_frechet_cpp_continuation_{digest}{suffix}"
    if exe.exists():
        return exe
    source = cache / f"rtdl_frechet_cpp_continuation_{digest}.cpp"
    source.write_text(CPP_CONTINUATION_SOURCE, encoding="utf-8")
    compiler = os.environ.get("CXX", "g++")
    completed = subprocess.run(
        [compiler, "-O3", "-std=c++17", str(source), "-o", str(exe)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "failed to build the C++ Frechet continuation with "
            f"{compiler}: {completed.stderr.strip()}"
        )
    return exe


def _write_cpp_curve_file(curve_p: tuple[Point, ...], curve_q: tuple[Point, ...]) -> Path:
    cache = _cpp_continuation_cache_dir()
    digest = hashlib.sha256(
        json.dumps(
            {
                "p": [(point.x, point.y) for point in curve_p],
                "q": [(point.x, point.y) for point in curve_q],
            },
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()[:16]
    path = cache / f"curves_{digest}.txt"
    with path.open("w", encoding="utf-8") as fh:
        fh.write(f"{len(curve_p)} {len(curve_q)}\n")
        for point in curve_p:
            fh.write(f"{point.x:.17g} {point.y:.17g}\n")
        for point in curve_q:
            fh.write(f"{point.x:.17g} {point.y:.17g}\n")
    return path


def continuous_frechet_distance_estimate_cpp(
    curve_p: tuple[Point, ...],
    curve_q: tuple[Point, ...],
    *,
    iterations: int,
) -> dict[str, object]:
    exe = _build_cpp_continuation()
    curve_file = _write_cpp_curve_file(curve_p, curve_q)
    start = time.perf_counter()
    completed = subprocess.run(
        [str(exe), str(curve_file), str(iterations)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    outer_wall = time.perf_counter() - start
    payload = json.loads(completed.stdout)
    payload["iterations"] = iterations
    payload["outer_wall_sec"] = outer_wall
    payload["continuation"] = "cpp_all_cells"
    return payload


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


def run_curves_app(
    curve_p: tuple[Point, ...],
    curve_q: tuple[Point, ...],
    backend: str = "cpu_python_reference",
    *,
    copies: int | None = None,
    candidate_mode: str = "all_cells",
    continuation: str = "python",
    iterations: int = 24,
    decision_radius: float | None = None,
    require_rt_core: bool = False,
    output_capacity: int = 1_000_000,
    min_prune_ratio: float = 0.25,
    verify_oracle: bool = True,
    candidate_expansion: int = 1,
) -> dict[str, object]:
    if len(curve_p) < 2 or len(curve_q) < 2:
        raise ValueError("continuous Frechet distance requires two curves with at least two points each")
    if candidate_mode not in {"all_cells", "rtdl_broadphase"}:
        raise ValueError("candidate_mode must be 'all_cells' or 'rtdl_broadphase'")
    if continuation not in {"python", "cpp"}:
        raise ValueError("continuation must be 'python' or 'cpp'")
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    if not 0.0 <= min_prune_ratio <= 1.0:
        raise ValueError("min_prune_ratio must be between 0 and 1")
    p_segments = _segments_from_curve(curve_p)
    q_segments = _segments_from_curve(curve_q)
    all_cells = frozenset((i, j) for i in range(len(p_segments)) for j in range(len(q_segments)))
    phases: dict[str, float] = {}

    broadphase_stats: dict[str, object] = {
        "used_as_filter": False,
        "fallback_reason": None,
        "last_candidate_cell_count": None,
        "last_broadphase_row_count": None,
        "last_raw_candidate_cell_count": None,
        "last_prune_ratio": None,
        "candidate_expansion": candidate_expansion,
    }

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
        raw_cells = _candidate_cells_from_rows(rows)
        # The start and end cells are required by the continuous Frechet boundary condition.
        cells = frozenset(set(raw_cells) | {(0, 0), (len(p_segments) - 1, len(q_segments) - 1)})
        cells = _expand_candidate_cells(
            cells,
            p_count=len(p_segments),
            q_count=len(q_segments),
            radius=candidate_expansion,
        )
        prune_ratio = 1.0 - (len(cells) / max(1, len(all_cells)))
        broadphase_stats["last_candidate_cell_count"] = len(cells)
        broadphase_stats["last_raw_candidate_cell_count"] = len(raw_cells)
        broadphase_stats["last_broadphase_row_count"] = len(rows)
        broadphase_stats["last_prune_ratio"] = prune_ratio
        if prune_ratio < min_prune_ratio:
            broadphase_stats["fallback_reason"] = (
                "RTDL broadphase was not selective enough for safe candidate filtering; "
                "using all free-space cells for the Frechet continuation."
            )
            return None, len(rows)
        broadphase_stats["used_as_filter"] = True
        broadphase_stats["fallback_reason"] = None
        return cells, len(rows)

    distance_start = time.perf_counter()
    if continuation == "cpp":
        if candidate_mode == "rtdl_broadphase":
            _, row_count = candidate_provider(_upper_bound(curve_p, curve_q))
            broadphase_stats["warmup_broadphase_row_count"] = row_count
        estimate = continuous_frechet_distance_estimate_cpp(
            curve_p,
            curve_q,
            iterations=iterations,
        )
    else:
        estimate = continuous_frechet_distance_estimate(
            curve_p,
            curve_q,
            iterations=iterations,
            candidate_provider=candidate_provider,
        )
    phases["distance_search_sec"] = time.perf_counter() - distance_start
    oracle = None
    if verify_oracle:
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
            "candidate_filter_used": cells is not None,
        }

    return {
        "app": "continuous_frechet_distance",
        "backend": backend,
        "candidate_mode": candidate_mode,
        "continuation": continuation,
        "copies": copies,
        "curve_p_point_count": len(curve_p),
        "curve_q_point_count": len(curve_q),
        "free_space_cell_count": len(all_cells),
        "distance_estimate": estimate["distance_estimate"],
        "oracle_distance_estimate": oracle["distance_estimate"] if oracle is not None else None,
        "matches_oracle": (
            math.isclose(
                float(estimate["distance_estimate"]),
                float(oracle["distance_estimate"]),
                rel_tol=1.0e-5,
                abs_tol=1.0e-5,
            )
            if oracle is not None
            else None
        ),
        "oracle_verified": oracle is not None,
        "decision": decision,
        "rtdl_role": (
            "RTDL is used as a generic segment-vs-expanded-shape broadphase over "
            "free-space cells. The continuous Frechet free-space reachability "
            "algorithm and distance search stay outside the app-agnostic RTDL "
            "engine, in either Python or the optional learner-owned C++ continuation."
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
            "exact free-space dynamic program remains outside the app-agnostic "
            "native engine."
        ),
        "broadphase_stats": broadphase_stats,
        "run_phases": phases,
    }


def run_app(
    backend: str = "cpu_python_reference",
    *,
    copies: int = 1,
    candidate_mode: str = "all_cells",
    continuation: str = "python",
    iterations: int = 24,
    decision_radius: float | None = None,
    require_rt_core: bool = False,
    output_capacity: int = 1_000_000,
    min_prune_ratio: float = 0.25,
    verify_oracle: bool = True,
    candidate_expansion: int = 1,
) -> dict[str, object]:
    if candidate_mode not in {"all_cells", "rtdl_broadphase"}:
        raise ValueError("candidate_mode must be 'all_cells' or 'rtdl_broadphase'")
    if continuation not in {"python", "cpp"}:
        raise ValueError("continuation must be 'python' or 'cpp'")
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    if not 0.0 <= min_prune_ratio <= 1.0:
        raise ValueError("min_prune_ratio must be between 0 and 1")
    case = make_authored_curves(copies=copies)
    return run_curves_app(
        case["curve_p"],
        case["curve_q"],
        backend,
        copies=copies,
        candidate_mode=candidate_mode,
        continuation=continuation,
        iterations=iterations,
        decision_radius=decision_radius,
        require_rt_core=require_rt_core,
        output_capacity=output_capacity,
        min_prune_ratio=min_prune_ratio,
        verify_oracle=verify_oracle,
        candidate_expansion=candidate_expansion,
    )


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
        "--continuation",
        choices=("python", "cpp"),
        default="python",
        help="Run the Frechet continuation in Python or a learner-owned compiled C++ helper.",
    )
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
    parser.add_argument(
        "--min-prune-ratio",
        type=float,
        default=0.25,
        help="Use RTDL candidates as a Frechet filter only when they prune at least this fraction of cells.",
    )
    parser.add_argument(
        "--candidate-expansion",
        type=int,
        default=1,
        help="Expand RTDL candidate cells by this Chebyshev neighborhood radius before Frechet filtering.",
    )
    parser.add_argument(
        "--no-oracle",
        action="store_true",
        help="Skip the Python all-cells oracle pass for performance-oriented runs.",
    )
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_app(
                args.backend,
                copies=args.copies,
                candidate_mode=args.candidate_mode,
                continuation=args.continuation,
                iterations=args.iterations,
                decision_radius=args.decision_radius,
                require_rt_core=args.require_rt_core,
                output_capacity=args.output_capacity,
                min_prune_ratio=args.min_prune_ratio,
                verify_oracle=not args.no_oracle,
                candidate_expansion=args.candidate_expansion,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

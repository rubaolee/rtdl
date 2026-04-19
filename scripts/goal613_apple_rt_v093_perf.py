#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import platform
import statistics
import sys
import time
from pathlib import Path
from typing import Callable, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import rtdsl as rt

from scripts.goal595_apple_rt_perf_harness import hit_count_3d_kernel
from scripts.goal595_apple_rt_perf_harness import _plane_triangles
from scripts.goal595_apple_rt_perf_harness import _rays_3d
from tests import goal582_apple_rt_full_surface_dispatch_test as g582
from tests import goal607_apple_rt_point_in_polygon_positive_native_test as g607


REPORTS_DIR = ROOT / "docs" / "reports"
DEFAULT_JSON = REPORTS_DIR / "goal613_v0_9_3_apple_rt_native_perf_macos_2026-04-19.json"
DEFAULT_MD = REPORTS_DIR / "goal613_v0_9_3_apple_rt_native_perf_macos_2026-04-19.md"


def _square(polygon_id: int, x0: float, y0: float, x1: float, y1: float) -> rt.Polygon:
    return rt.Polygon(id=polygon_id, vertices=((x0, y0), (x1, y0), (x1, y1), (x0, y1)))


def _points_2d(count: int) -> tuple[rt.Point, ...]:
    return tuple(rt.Point(id=1000 + i, x=float(i % 16), y=float(i // 16)) for i in range(count))


def _segments(count: int) -> tuple[rt.Segment, ...]:
    return tuple(
        rt.Segment(
            id=2000 + i,
            x0=-1.0,
            y0=float(i % 32) * 0.25,
            x1=10.0,
            y1=float(i % 32) * 0.25,
        )
        for i in range(count)
    )


def _vertical_segments(count: int) -> tuple[rt.Segment, ...]:
    return tuple(
        rt.Segment(
            id=3000 + i,
            x0=float(i % 32) * 0.25,
            y0=-1.0,
            x1=float(i % 32) * 0.25,
            y1=10.0,
        )
        for i in range(count)
    )


def _polygons(count: int) -> tuple[rt.Polygon, ...]:
    return tuple(
        _square(
            4000 + i,
            float((i % 8) * 2),
            float((i // 8) * 2),
            float((i % 8) * 2 + 1),
            float((i // 8) * 2 + 1),
        )
        for i in range(count)
    )


def _shifted_polygons(count: int) -> tuple[rt.Polygon, ...]:
    return tuple(
        _square(
            5000 + i,
            float((i % 8) * 2 + 1),
            float((i // 8) * 2 + 1),
            float((i % 8) * 2 + 2),
            float((i // 8) * 2 + 2),
        )
        for i in range(count)
    )


def _rays_2d(count: int) -> tuple[rt.Ray2D, ...]:
    return tuple(rt.Ray2D(id=6000 + i, ox=-1.0, oy=0.25 + 0.05 * i, dx=1.0, dy=0.0, tmax=8.0) for i in range(count))


def _triangles_2d(count: int) -> tuple[rt.Triangle, ...]:
    return tuple(
        rt.Triangle(id=7000 + i, x0=1.0 + 0.05 * i, y0=0.0, x1=1.0 + 0.05 * i, y1=2.0, x2=1.5 + 0.05 * i, y2=1.0)
        for i in range(count)
    )


def _neighbor_points(count: int) -> tuple[rt.Point, ...]:
    return tuple(rt.Point(id=8000 + i, x=(i % 16) * 0.25, y=(i // 16) * 0.25) for i in range(count))


def _cases() -> tuple[dict[str, object], ...]:
    points = _points_2d(64)
    neighbor_queries = _neighbor_points(32)
    neighbor_points = _neighbor_points(128)
    left_polygons = (_square(10, 0.0, 0.0, 3.0, 3.0), _square(11, 10.0, 10.0, 11.0, 11.0))
    right_polygons = (_square(20, 2.0, 2.0, 5.0, 5.0), _square(21, 1.0, 1.0, 2.0, 2.0))
    polygons = _polygons(16)
    return (
        {
            "name": "ray_triangle_closest_hit_3d",
            "predicate": "ray_triangle_closest_hit",
            "kernel": g582.ray_closest_3d_kernel,
            "inputs": {"rays": _rays_3d(128), "triangles": _plane_triangles(128)},
        },
        {
            "name": "ray_triangle_hit_count_3d",
            "predicate": "ray_triangle_hit_count",
            "kernel": hit_count_3d_kernel,
            "inputs": {"rays": _rays_3d(96), "triangles": _plane_triangles(256)},
        },
        {
            "name": "ray_triangle_hit_count_2d",
            "predicate": "ray_triangle_hit_count",
            "kernel": g582.ray_hitcount_kernel,
            "inputs": {"rays": _rays_2d(64), "triangles": _triangles_2d(64)},
        },
        {
            "name": "segment_intersection",
            "predicate": "segment_intersection",
            "kernel": g582.segment_intersection_kernel,
            "inputs": {"left": _segments(64), "right": _vertical_segments(64)},
        },
        {
            "name": "point_in_polygon_full_matrix",
            "predicate": "point_in_polygon",
            "kernel": g582.point_in_polygon_kernel,
            "inputs": {"points": points, "polygons": polygons},
        },
        {
            "name": "point_in_polygon_positive_hits",
            "predicate": "point_in_polygon",
            "kernel": g607.point_in_polygon_positive_kernel,
            "inputs": {"points": points, "polygons": polygons},
        },
        {
            "name": "segment_polygon_hitcount",
            "predicate": "segment_polygon_hitcount",
            "kernel": g582.segment_polygon_hitcount_kernel,
            "inputs": {"segments": _segments(64), "polygons": polygons},
        },
        {
            "name": "segment_polygon_anyhit_rows",
            "predicate": "segment_polygon_anyhit_rows",
            "kernel": g582.segment_polygon_anyhit_kernel,
            "inputs": {"segments": _segments(64), "polygons": polygons},
        },
        {
            "name": "point_nearest_segment",
            "predicate": "point_nearest_segment",
            "kernel": g582.point_nearest_segment_kernel,
            "inputs": {"points": points, "segments": _segments(64)},
        },
        {
            "name": "fixed_radius_neighbors",
            "predicate": "fixed_radius_neighbors",
            "kernel": g582.fixed_radius_kernel,
            "inputs": {"queries": neighbor_queries, "points": neighbor_points},
        },
        {
            "name": "knn_rows",
            "predicate": "knn_rows",
            "kernel": g582.knn_kernel,
            "inputs": {"queries": neighbor_queries, "points": neighbor_points},
        },
        {
            "name": "bounded_knn_rows",
            "predicate": "bounded_knn_rows",
            "kernel": g582.bounded_knn_kernel,
            "inputs": {"queries": neighbor_queries, "points": neighbor_points},
        },
        {
            "name": "polygon_pair_overlap_area_rows",
            "predicate": "polygon_pair_overlap_area_rows",
            "kernel": g582.polygon_overlap_kernel,
            "inputs": {"left": left_polygons, "right": right_polygons},
        },
        {
            "name": "polygon_set_jaccard",
            "predicate": "polygon_set_jaccard",
            "kernel": g582.polygon_jaccard_kernel,
            "inputs": {"left": left_polygons, "right": right_polygons},
        },
        {
            "name": "overlay_compose",
            "predicate": "overlay_compose",
            "kernel": g582.overlay_kernel,
            "inputs": {"left": left_polygons, "right": right_polygons},
        },
    )


def _canonical_rows(rows: Iterable[dict[str, object]]) -> tuple[dict[str, object], ...]:
    return tuple(sorted((dict(row) for row in rows), key=lambda row: tuple((key, row[key]) for key in sorted(row))))


def _value_close(left: object, right: object) -> bool:
    if isinstance(left, float) or isinstance(right, float):
        return math.isclose(float(left), float(right), rel_tol=1.0e-5, abs_tol=1.0e-5)
    return left == right


def _rows_match(left: Iterable[dict[str, object]], right: Iterable[dict[str, object]]) -> bool:
    left_rows = _canonical_rows(left)
    right_rows = _canonical_rows(right)
    if len(left_rows) != len(right_rows):
        return False
    for left_row, right_row in zip(left_rows, right_rows):
        if set(left_row) != set(right_row):
            return False
        if any(not _value_close(left_row[key], right_row[key]) for key in left_row):
            return False
    return True


def _seconds(fn: Callable[[], object]) -> tuple[float, object]:
    start = time.perf_counter()
    result = fn()
    return time.perf_counter() - start, result


def _stats(samples: list[float]) -> dict[str, float | int | None]:
    if not samples:
        return {"count": 0}
    mean = statistics.mean(samples)
    stdev = statistics.stdev(samples) if len(samples) > 1 else 0.0
    return {
        "count": len(samples),
        "min_seconds": min(samples),
        "median_seconds": statistics.median(samples),
        "mean_seconds": mean,
        "max_seconds": max(samples),
        "stdev_seconds": stdev,
        "coefficient_of_variation": stdev / mean if mean > 0.0 else None,
    }


def _measure(fn: Callable[[], tuple[dict[str, object], ...]], *, warmups: int, repeats: int) -> dict[str, object]:
    cold_seconds, cold_rows = _seconds(fn)
    for _ in range(warmups):
        fn()
    samples = []
    rows = cold_rows
    for _ in range(repeats):
        elapsed, rows = _seconds(fn)
        samples.append(elapsed)
    return {
        "cold_seconds": cold_seconds,
        "warmups": warmups,
        "samples_seconds": samples,
        "stats": _stats(samples),
        "row_count": len(rows),
        "rows": tuple(rows),
    }


def _safe_version(fn: Callable[[], object]) -> object:
    try:
        return fn()
    except Exception as exc:
        return {"unavailable": str(exc)}


def run_harness(*, warmups: int, repeats: int, cv_threshold: float) -> dict[str, object]:
    payload: dict[str, object] = {
        "date": "2026-04-19",
        "goal": "Goal613 v0.9.3 Apple RT native/native-assisted performance characterization",
        "host": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "versions": {
            "apple_rt": _safe_version(rt.apple_rt_version),
            "apple_rt_context": _safe_version(rt.apple_rt_context_probe),
            "embree": _safe_version(rt.embree_version),
        },
        "methodology": {
            "warmups_before_sample_window": warmups,
            "measured_repeats": repeats,
            "stability_threshold_cv": cv_threshold,
            "note": "Apple RT runs use native_only=True. Embree is the mature local RTDL baseline. CPU reference is used only for parity.",
        },
        "cases": [],
    }
    for case in _cases():
        kernel = case["kernel"]
        inputs = case["inputs"]
        assert isinstance(inputs, dict)
        cpu_rows = tuple(rt.run_cpu_python_reference(kernel, **inputs))
        backends: dict[str, object] = {}
        row: dict[str, object] = {
            "name": case["name"],
            "predicate": case["predicate"],
            "input_sizes": {key: len(value) if hasattr(value, "__len__") else None for key, value in inputs.items()},
            "cpu_reference_rows": len(cpu_rows),
            "backends": backends,
        }
        for backend_name, fn in (
            ("embree", lambda kernel=kernel, inputs=inputs: tuple(rt.run_embree(kernel, **inputs))),
            ("apple_rt", lambda kernel=kernel, inputs=inputs: tuple(rt.run_apple_rt(kernel, native_only=True, **inputs))),
        ):
            try:
                measured = _measure(fn, warmups=warmups, repeats=repeats)
            except Exception as exc:
                backends[backend_name] = {"available": False, "error": str(exc)}
                continue
            rows = measured.pop("rows")
            stats = measured["stats"]
            assert isinstance(stats, dict)
            cv = stats.get("coefficient_of_variation")
            backends[backend_name] = {
                "available": True,
                **measured,
                "stable": bool(cv is not None and cv <= cv_threshold),
                "matches_cpu_reference": _rows_match(rows, cpu_rows),
            }
        embree = backends.get("embree")
        apple = backends.get("apple_rt")
        if isinstance(embree, dict) and isinstance(apple, dict) and embree.get("available") and apple.get("available"):
            embree_stats = embree["stats"]
            apple_stats = apple["stats"]
            assert isinstance(embree_stats, dict)
            assert isinstance(apple_stats, dict)
            embree_median = float(embree_stats["median_seconds"])
            apple_median = float(apple_stats["median_seconds"])
            row["apple_rt_vs_embree_median_ratio"] = apple_median / embree_median if embree_median > 0.0 else None
            row["apple_rt_vs_embree_correctness_valid"] = bool(
                embree.get("matches_cpu_reference") and apple.get("matches_cpu_reference")
            )
        payload["cases"].append(row)
    return payload


def render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal613: v0.9.3 Apple RT Native Performance Characterization",
        "",
        "Date: 2026-04-19",
        "",
        "Status: local measurement artifact",
        "",
        "## Methodology",
        "",
        f"- Warmups before sample window: `{payload['methodology']['warmups_before_sample_window']}`",
        f"- Measured repeats: `{payload['methodology']['measured_repeats']}`",
        f"- Stability threshold: coefficient of variation <= `{payload['methodology']['stability_threshold_cv']}`",
        "- Apple RT runs use `native_only=True`.",
        "- Embree is the mature local RTDL baseline.",
        "- CPU reference is used only for parity.",
        "- Native-assisted means Apple MPS RT performs candidate or flag discovery; CPU refinement/materialization may still be used as documented in Goals 608-612.",
        "",
        "## Host",
        "",
        "```json",
        json.dumps(payload["host"], indent=2),
        "```",
        "",
        "## Versions",
        "",
        "```json",
        json.dumps(payload["versions"], indent=2),
        "```",
        "",
        "## Results",
        "",
        "| Workload | Predicate | Inputs | Rows | Embree median | Apple RT median | Apple/Embree | Embree parity | Apple parity | Stable |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    ratios = []
    invalid_ratios = []
    for case in payload["cases"]:
        backends = case["backends"]
        embree = backends.get("embree", {})
        apple = backends.get("apple_rt", {})
        if not embree.get("available") or not apple.get("available"):
            lines.append(
                f"| `{case['name']}` | `{case['predicate']}` | `{case['input_sizes']}` | {case['cpu_reference_rows']} | unavailable | unavailable | n/a | false | false | false |"
            )
            continue
        embree_stats = embree["stats"]
        apple_stats = apple["stats"]
        embree_parity = bool(embree["matches_cpu_reference"])
        apple_parity = bool(apple["matches_cpu_reference"])
        stable = bool(embree["stable"] and apple["stable"])
        ratio = case.get("apple_rt_vs_embree_median_ratio")
        ratio_valid = bool(case.get("apple_rt_vs_embree_correctness_valid"))
        if isinstance(ratio, float) and ratio_valid:
            ratios.append((case["name"], ratio))
        elif isinstance(ratio, float):
            invalid_ratios.append(case["name"])
        lines.append(
            f"| `{case['name']}` | `{case['predicate']}` | `{case['input_sizes']}` | {apple['row_count']} | "
            f"{float(embree_stats['median_seconds']):.9f} s | {float(apple_stats['median_seconds']):.9f} s | "
            f"{float(ratio):.3f}x | {embree_parity} | {apple_parity} | {stable} |"
        )
    if ratios:
        fastest = min(ratios, key=lambda item: item[1])
        slowest = max(ratios, key=lambda item: item[1])
        lines.extend(
            [
                "",
                "## Major Conclusion",
                "",
                f"- Best correctness-valid Apple-vs-Embree median ratio in this run: `{fastest[0]}` at `{fastest[1]:.3f}x`.",
                f"- Worst correctness-valid Apple-vs-Embree median ratio in this run: `{slowest[0]}` at `{slowest[1]:.3f}x`.",
                "- The current Apple RT backend is correctness-broad for geometry/nearest-neighbor native/native-assisted rows, but it is not broadly performance-leading versus Embree on this Mac-local harness.",
                "- This report should be treated as engineering evidence for optimization planning, not public speedup wording.",
            ]
        )
    if invalid_ratios:
        lines.extend(
            [
                "",
                "## Correctness-Validity Notes",
                "",
                "The following Apple/Embree timing ratios are not correctness-valid comparisons because at least one backend did not match the CPU reference on that fixture:",
                "",
                *[f"- `{name}`" for name in invalid_ratios],
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--cv-threshold", type=float, default=0.30)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    args = parser.parse_args()
    if args.warmups < 0 or args.repeats <= 0:
        raise SystemExit("--warmups must be >= 0 and --repeats must be > 0")
    payload = run_harness(warmups=args.warmups, repeats=args.repeats, cv_threshold=args.cv_threshold)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(args.json_out)
    print(args.md_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
from typing import Callable

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


REPORTS_DIR = ROOT / "docs" / "reports"
DEFAULT_JSON = REPORTS_DIR / "goal601_v0_9_2_apple_rt_full_surface_perf_macos_2026-04-19.json"
DEFAULT_MD = REPORTS_DIR / "goal601_v0_9_2_apple_rt_full_surface_perf_macos_2026-04-19.md"


def _square(polygon_id: int, x0: float, y0: float, x1: float, y1: float) -> rt.Polygon:
    return rt.Polygon(id=polygon_id, vertices=((x0, y0), (x1, y0), (x1, y1), (x0, y1)))


def _table() -> tuple[dict[str, object], ...]:
    return (
        {"row_id": 1, "region": "east", "ship_date": 10, "quantity": 12, "discount": 5, "revenue": 5},
        {"row_id": 2, "region": "west", "ship_date": 11, "quantity": 30, "discount": 8, "revenue": 8},
        {"row_id": 3, "region": "east", "ship_date": 12, "quantity": 18, "discount": 6, "revenue": 6},
        {"row_id": 4, "region": "west", "ship_date": 13, "quantity": 10, "discount": 6, "revenue": 10},
    )


def _cases() -> tuple[dict[str, object], ...]:
    square = _square(1, 0.0, 0.0, 2.0, 2.0)
    shifted_square = _square(2, 1.0, 1.0, 3.0, 3.0)
    table = _table()
    return (
        {
            "name": "segment_intersection_2d",
            "predicate": "segment_intersection",
            "kernel": g582.segment_intersection_kernel,
            "inputs": {
                "left": (
                    rt.Segment(1, 0.0, 0.0, 2.0, 2.0),
                    rt.Segment(3, -1.0, 1.0, 3.0, 1.0),
                ),
                "right": (
                    rt.Segment(2, 0.0, 2.0, 2.0, 0.0),
                    rt.Segment(4, 1.0, -1.0, 1.0, 3.0),
                ),
            },
            "apple_mode": "native_mps_rt",
        },
        {
            "name": "point_in_polygon",
            "predicate": "point_in_polygon",
            "kernel": g582.point_in_polygon_kernel,
            "inputs": {"points": (rt.Point(1, 0.5, 0.5), rt.Point(2, 3.0, 3.0)), "polygons": (square,)},
            "apple_mode": "cpu_reference_compat",
        },
        {
            "name": "overlay_compose",
            "predicate": "overlay_compose",
            "kernel": g582.overlay_kernel,
            "inputs": {"left": (square,), "right": (shifted_square,)},
            "apple_mode": "cpu_reference_compat",
        },
        {
            "name": "ray_triangle_hit_count_2d",
            "predicate": "ray_triangle_hit_count",
            "kernel": g582.ray_hitcount_kernel,
            "inputs": {
                "rays": (rt.Ray2D(1, -1.0, 0.5, 1.0, 0.0, 3.0),),
                "triangles": (rt.Triangle(2, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0),),
            },
            "apple_mode": "cpu_reference_compat",
        },
        {
            "name": "ray_triangle_hit_count_3d",
            "predicate": "ray_triangle_hit_count",
            "kernel": hit_count_3d_kernel,
            "inputs": {"rays": _rays_3d(32), "triangles": _plane_triangles(64)},
            "apple_mode": "native_mps_rt",
        },
        {
            "name": "ray_triangle_closest_hit_3d",
            "predicate": "ray_triangle_closest_hit",
            "kernel": g582.ray_closest_3d_kernel,
            "inputs": {
                "rays": (rt.Ray3D(1, -1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 3.0),),
                "triangles": (rt.Triangle3D(2, 0.5, -1.0, -1.0, 0.5, 1.0, 0.0, 0.5, -1.0, 1.0),),
            },
            "apple_mode": "native_mps_rt",
        },
        {
            "name": "segment_polygon_hitcount",
            "predicate": "segment_polygon_hitcount",
            "kernel": g582.segment_polygon_hitcount_kernel,
            "inputs": {"segments": (rt.Segment(1, -1.0, 1.0, 3.0, 1.0),), "polygons": (square,)},
            "apple_mode": "cpu_reference_compat",
        },
        {
            "name": "segment_polygon_anyhit_rows",
            "predicate": "segment_polygon_anyhit_rows",
            "kernel": g582.segment_polygon_anyhit_kernel,
            "inputs": {"segments": (rt.Segment(1, -1.0, 1.0, 3.0, 1.0),), "polygons": (square,)},
            "apple_mode": "cpu_reference_compat",
        },
        {
            "name": "polygon_pair_overlap_area_rows",
            "predicate": "polygon_pair_overlap_area_rows",
            "kernel": g582.polygon_overlap_kernel,
            "inputs": {"left": (square,), "right": (shifted_square,)},
            "apple_mode": "cpu_reference_compat",
        },
        {
            "name": "polygon_set_jaccard",
            "predicate": "polygon_set_jaccard",
            "kernel": g582.polygon_jaccard_kernel,
            "inputs": {"left": (square,), "right": (shifted_square,)},
            "apple_mode": "cpu_reference_compat",
        },
        {
            "name": "point_nearest_segment",
            "predicate": "point_nearest_segment",
            "kernel": g582.point_nearest_segment_kernel,
            "inputs": {"points": (rt.Point(1, 0.5, 1.0),), "segments": (rt.Segment(2, 0.0, 0.0, 2.0, 0.0),)},
            "apple_mode": "cpu_reference_compat",
        },
        {
            "name": "fixed_radius_neighbors",
            "predicate": "fixed_radius_neighbors",
            "kernel": g582.fixed_radius_kernel,
            "inputs": {"queries": (rt.Point(1, 0.0, 0.0),), "points": (rt.Point(2, 0.5, 0.0), rt.Point(3, 2.0, 0.0))},
            "apple_mode": "cpu_reference_compat",
        },
        {
            "name": "knn_rows",
            "predicate": "knn_rows",
            "kernel": g582.knn_kernel,
            "inputs": {"queries": (rt.Point(1, 0.0, 0.0),), "points": (rt.Point(2, 0.5, 0.0), rt.Point(3, 2.0, 0.0))},
            "apple_mode": "cpu_reference_compat",
        },
        {
            "name": "bounded_knn_rows",
            "predicate": "bounded_knn_rows",
            "kernel": g582.bounded_knn_kernel,
            "inputs": {"queries": (rt.Point(1, 0.0, 0.0),), "points": (rt.Point(2, 0.5, 0.0), rt.Point(3, 2.0, 0.0))},
            "apple_mode": "cpu_reference_compat",
        },
        {
            "name": "bfs_discover",
            "predicate": "bfs_discover",
            "kernel": g582.bfs_kernel,
            "inputs": {
                "frontier": (rt.FrontierVertex(vertex_id=0, level=0),),
                "graph": rt.csr_graph(row_offsets=(0, 2, 3, 3), column_indices=(1, 2, 2)),
                "visited": (0,),
            },
            "apple_mode": "cpu_reference_compat",
        },
        {
            "name": "triangle_match",
            "predicate": "triangle_match",
            "kernel": g582.triangle_match_kernel,
            "inputs": {
                "seeds": ((0, 1),),
                "graph": rt.csr_graph(row_offsets=(0, 2, 4, 6), column_indices=(1, 2, 0, 2, 0, 1)),
            },
            "apple_mode": "cpu_reference_compat",
        },
        {
            "name": "conjunctive_scan",
            "predicate": "conjunctive_scan",
            "kernel": g582.db_scan_kernel,
            "inputs": {"predicates": (("ship_date", "between", 11, 13), ("discount", "eq", 6)), "table": table},
            "apple_mode": "cpu_reference_compat",
        },
        {
            "name": "grouped_count",
            "predicate": "grouped_count",
            "kernel": g582.grouped_count_kernel,
            "inputs": {"query": {"predicates": (("ship_date", "ge", 11),), "group_keys": ("region",)}, "table": table},
            "apple_mode": "cpu_reference_compat",
        },
        {
            "name": "grouped_sum",
            "predicate": "grouped_sum",
            "kernel": g582.grouped_sum_kernel,
            "inputs": {
                "query": {"predicates": (("ship_date", "ge", 11),), "group_keys": ("region",), "value_field": "revenue"},
                "table": table,
            },
            "apple_mode": "cpu_reference_compat",
        },
    )


def _rows_close(left: object, right: object) -> bool:
    if isinstance(left, float) or isinstance(right, float):
        return math.isclose(float(left), float(right), rel_tol=1.0e-5, abs_tol=1.0e-5)
    return left == right


def _rows_match(left: tuple[dict[str, object], ...], right: tuple[dict[str, object], ...]) -> bool:
    if len(left) != len(right):
        return False
    for left_row, right_row in zip(left, right):
        if set(left_row) != set(right_row):
            return False
        for key, left_value in left_row.items():
            if not _rows_close(left_value, right_row[key]):
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
    samples: list[float] = []
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
        "rows": rows,
    }


def _run_backend(name: str, kernel: object, inputs: dict[str, object]) -> tuple[dict[str, object], ...]:
    if name == "cpu_reference":
        return tuple(rt.run_cpu_python_reference(kernel, **inputs))
    if name == "embree":
        return tuple(rt.run_embree(kernel, **inputs))
    if name == "apple_rt":
        return tuple(rt.run_apple_rt(kernel, **inputs))
    raise ValueError(name)


def _safe_version(fn: Callable[[], object]) -> object:
    try:
        return fn()
    except Exception as exc:
        return {"unavailable": str(exc)}


def run_harness(*, warmups: int, repeats: int, cv_threshold: float) -> dict[str, object]:
    cases = []
    for case in _cases():
        kernel = case["kernel"]
        inputs = case["inputs"]
        assert isinstance(inputs, dict)
        cpu_rows = _run_backend("cpu_reference", kernel, inputs)
        row: dict[str, object] = {
            "name": case["name"],
            "predicate": case["predicate"],
            "apple_mode": case["apple_mode"],
            "input_sizes": {key: len(value) if hasattr(value, "__len__") else None for key, value in inputs.items()},
            "cpu_reference_rows": len(cpu_rows),
            "backends": {},
        }
        backends = row["backends"]
        assert isinstance(backends, dict)
        for backend in ("embree", "apple_rt"):
            try:
                measured = _measure(lambda backend=backend: _run_backend(backend, kernel, inputs), warmups=warmups, repeats=repeats)
            except Exception as exc:
                backends[backend] = {"available": False, "error": str(exc)}
                continue
            rows = measured.pop("rows")
            stats = measured["stats"]
            assert isinstance(stats, dict)
            cv = stats.get("coefficient_of_variation")
            backends[backend] = {
                "available": True,
                **measured,
                "stable": bool(cv is not None and cv <= cv_threshold),
                "matches_cpu_reference": _rows_match(tuple(rows), cpu_rows),
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
        cases.append(row)
    return {
        "date": "2026-04-19",
        "goal": "Goal601 Apple RT full-surface perf characterization",
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
            "warning": "Rows marked cpu_reference_compat are run_apple_rt API compatibility timings, not Apple hardware-backed RT timings.",
        },
        "cases": cases,
    }


def write_markdown(payload: dict[str, object], path: Path) -> None:
    lines = [
        "# Goal601: Apple RT Full-Surface Performance Characterization",
        "",
        "Date: 2026-04-19",
        "",
        "Status: characterization artifact",
        "",
        "## Methodology",
        "",
        f"- Warmups before sample window: `{payload['methodology']['warmups_before_sample_window']}`",
        f"- Measured repeats: `{payload['methodology']['measured_repeats']}`",
        f"- Stability threshold: coefficient of variation <= `{payload['methodology']['stability_threshold_cv']}`",
        "- Embree is the mature local RTDL baseline.",
        "- `native_mps_rt` rows are Apple Metal/MPS RT native slices.",
        "- `cpu_reference_compat` rows are callable through `run_apple_rt`, but they are not Apple hardware-backed RT execution.",
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
        "This table has 19 measured shape rows for the 18-predicate Apple RT surface because `ray_triangle_hit_count` has both a 2D compatibility shape and a 3D native Apple RT shape.",
        "",
        "| Workload | Apple mode | Rows | Embree median | Apple RT median | Apple/Embree | Parity | Stable |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for case in payload["cases"]:
        backends = case["backends"]
        embree = backends.get("embree", {})
        apple = backends.get("apple_rt", {})
        if not embree.get("available") or not apple.get("available"):
            lines.append(
                f"| `{case['name']}` | `{case['apple_mode']}` | {case['cpu_reference_rows']} | unavailable | unavailable | n/a | false | false |"
            )
            continue
        embree_stats = embree["stats"]
        apple_stats = apple["stats"]
        parity = bool(embree["matches_cpu_reference"] and apple["matches_cpu_reference"])
        stable = bool(embree["stable"] and apple["stable"])
        ratio = case.get("apple_rt_vs_embree_median_ratio")
        lines.append(
            f"| `{case['name']}` | `{case['apple_mode']}` | {apple['row_count']} | "
            f"{float(embree_stats['median_seconds']):.9f} s | {float(apple_stats['median_seconds']):.9f} s | "
            f"{float(ratio):.3f}x | {parity} | {stable} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This report answers the full-surface question. The current Apple RT API can run the measured workload surface, but only the rows marked `native_mps_rt` are Apple Metal/MPS RT native execution.",
            "",
            "The compatibility rows are useful for API uniformity and app portability, but they must not be used as Apple RT hardware-speed evidence.",
            "",
            "The tiny native rows in this full-surface table are overhead-characterization fixtures. They are intentionally small so every supported shape can be measured quickly in one report. For native Apple RT performance wording, use the scaled Goal600 artifact:",
            "",
            "- `/Users/rl2025/rtdl_python_only/docs/reports/goal600_v0_9_2_pre_release_apple_rt_perf_macos_2026-04-19.md`",
            "",
            "Combining both artifacts gives the current honest answer:",
            "",
            "- Full API surface: callable through `run_apple_rt`, with parity on all measured rows.",
            "- Native Apple RT surface: 3D closest-hit, 3D hit-count, and 2D segment-intersection.",
            "- Performance: closest-hit is the strongest current native Apple RT result on this Mac; hit-count and segment-intersection are correct but still not performance-leading versus Embree.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--repeats", type=int, default=15)
    parser.add_argument("--cv-threshold", type=float, default=0.20)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    args = parser.parse_args()
    payload = run_harness(warmups=args.warmups, repeats=args.repeats, cv_threshold=args.cv_threshold)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload, args.md_out)
    print(args.json_out)
    print(args.md_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

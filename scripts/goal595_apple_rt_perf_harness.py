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


REPORTS_DIR = ROOT / "docs" / "reports"
DEFAULT_JSON = REPORTS_DIR / "goal595_apple_rt_repeatable_perf_macos_2026-04-19.json"
DEFAULT_MD = REPORTS_DIR / "goal595_apple_rt_repeatable_perf_macos_2026-04-19.md"


@rt.kernel(backend="rtdl", precision="float_approx")
def closest_hit_3d_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray3DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_closest_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "triangle_id", "t"])


@rt.kernel(backend="rtdl", precision="float_approx")
def hit_count_3d_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray3DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def segment_intersection_kernel():
    left = rt.input("left", rt.Segments, role="probe")
    right = rt.input("right", rt.Segments, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(hits, fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"])


def _plane_triangles(count: int) -> tuple[rt.Triangle3D, ...]:
    return tuple(
        rt.Triangle3D(
            id=1000 + index,
            x0=1.0 + 0.002 * index,
            y0=-2.0,
            z0=-2.0,
            x1=1.0 + 0.002 * index,
            y1=2.0,
            z1=0.0,
            x2=1.0 + 0.002 * index,
            y2=-2.0,
            z2=2.0,
        )
        for index in range(count)
    )


def _rays_3d(count: int) -> tuple[rt.Ray3D, ...]:
    return tuple(
        rt.Ray3D(
            id=2000 + index,
            ox=0.0,
            oy=((index % 17) - 8) * 0.02,
            oz=((index % 11) - 5) * 0.02,
            dx=1.0,
            dy=0.0,
            dz=0.0,
            tmax=8.0,
        )
        for index in range(count)
    )


def _left_segments(count: int) -> tuple[rt.Segment, ...]:
    return tuple(
        rt.Segment(
            id=3000 + index,
            x0=-1.0,
            y0=-1.0 + 2.0 * (index + 0.5) / count,
            x1=1.0,
            y1=-1.0 + 2.0 * (index + 0.5) / count,
        )
        for index in range(count)
    )


def _right_segments(count: int) -> tuple[rt.Segment, ...]:
    return tuple(
        rt.Segment(
            id=4000 + index,
            x0=-1.0 + 2.0 * (index + 0.5) / count,
            y0=-1.0,
            x1=-1.0 + 2.0 * (index + 0.5) / count,
            y1=1.0,
        )
        for index in range(count)
    )


def _rows_match(workload: str, left: Iterable[dict[str, object]], right: Iterable[dict[str, object]]) -> bool:
    left_rows = tuple(left)
    right_rows = tuple(right)
    if len(left_rows) != len(right_rows):
        return False
    if workload == "ray_triangle_closest_hit_3d":
        for a, b in zip(left_rows, right_rows):
            if int(a["ray_id"]) != int(b["ray_id"]) or int(a["triangle_id"]) != int(b["triangle_id"]):
                return False
            if not math.isclose(float(a["t"]), float(b["t"]), rel_tol=1.0e-5, abs_tol=1.0e-5):
                return False
        return True
    if workload == "segment_intersection_2d":
        for a, b in zip(left_rows, right_rows):
            if int(a["left_id"]) != int(b["left_id"]) or int(a["right_id"]) != int(b["right_id"]):
                return False
            if not math.isclose(
                float(a["intersection_point_x"]),
                float(b["intersection_point_x"]),
                rel_tol=1.0e-6,
                abs_tol=1.0e-6,
            ):
                return False
            if not math.isclose(
                float(a["intersection_point_y"]),
                float(b["intersection_point_y"]),
                rel_tol=1.0e-6,
                abs_tol=1.0e-6,
            ):
                return False
        return True
    return left_rows == right_rows


def _seconds(fn: Callable[[], object]) -> tuple[float, object]:
    start = time.perf_counter()
    result = fn()
    return time.perf_counter() - start, result


def _stats(samples: tuple[float, ...]) -> dict[str, float | int | None]:
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
        "coefficient_of_variation": (stdev / mean) if mean > 0.0 else None,
    }


def _measure(fn: Callable[[], object], *, warmups: int, repeats: int, cv_threshold: float) -> dict[str, object]:
    cold_seconds, cold_result = _seconds(fn)
    for _ in range(warmups):
        fn()
    samples = []
    last_result = cold_result
    for _ in range(repeats):
        seconds, last_result = _seconds(fn)
        samples.append(seconds)
    stats = _stats(tuple(samples))
    cv = stats.get("coefficient_of_variation")
    return {
        "cold_seconds": cold_seconds,
        "warmups": warmups,
        "samples_seconds": samples,
        "stats": stats,
        "stable": bool(cv is not None and cv <= cv_threshold),
        "stability_threshold_cv": cv_threshold,
        "last_result": tuple(last_result),
    }


def _safe_version(fn: Callable[[], object]) -> object:
    try:
        return fn()
    except Exception as exc:
        return {"unavailable": str(exc)}


def _backend_functions(workload: str, inputs: dict[str, object]) -> dict[str, Callable[[], tuple[dict[str, object], ...]]]:
    if workload == "ray_triangle_closest_hit_3d":
        return {
            "cpu_reference": lambda: tuple(rt.ray_triangle_closest_hit_cpu(inputs["rays"], inputs["triangles"])),
            "embree": lambda: tuple(rt.run_embree(closest_hit_3d_kernel, **inputs)),
            "apple_rt": lambda: tuple(rt.run_apple_rt(closest_hit_3d_kernel, native_only=True, **inputs)),
        }
    if workload == "ray_triangle_hit_count_3d":
        return {
            "cpu_reference": lambda: tuple(rt.ray_triangle_hit_count_cpu(inputs["rays"], inputs["triangles"])),
            "embree": lambda: tuple(rt.run_embree(hit_count_3d_kernel, **inputs)),
            "apple_rt": lambda: tuple(rt.run_apple_rt(hit_count_3d_kernel, native_only=True, **inputs)),
        }
    if workload == "segment_intersection_2d":
        return {
            "cpu_reference": lambda: tuple(rt.run_cpu_python_reference(segment_intersection_kernel, **inputs)),
            "embree": lambda: tuple(rt.run_embree(segment_intersection_kernel, **inputs)),
            "apple_rt": lambda: tuple(rt.run_apple_rt(segment_intersection_kernel, native_only=True, **inputs)),
        }
    raise ValueError(workload)


def _case_inputs() -> dict[str, dict[str, object]]:
    return {
        "ray_triangle_closest_hit_3d": {
            "rays": _rays_3d(256),
            "triangles": _plane_triangles(256),
        },
        "ray_triangle_hit_count_3d": {
            "rays": _rays_3d(128),
            "triangles": _plane_triangles(512),
        },
        "segment_intersection_2d": {
            "left": _left_segments(128),
            "right": _right_segments(128),
        },
    }


def run_harness(*, warmups: int, repeats: int, cv_threshold: float) -> dict[str, object]:
    payload: dict[str, object] = {
        "date": "2026-04-19",
        "goal": "Goal595 v0.9.2 Apple RT repeatable performance harness",
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
            "cold_seconds": "first measured call in this process before harness warmups",
            "statistics": "min/median/mean/max/stdev/coefficient_of_variation over measured repeats",
            "note": "CPU reference is for parity and scale context; Embree is the current mature RTDL local backend baseline.",
        },
        "cases": [],
        "unstable_results": [],
    }

    for workload, inputs in _case_inputs().items():
        backends = _backend_functions(workload, inputs)
        cpu_rows = backends["cpu_reference"]()
        case_payload: dict[str, object] = {
            "workload": workload,
            "input_sizes": {name: len(value) for name, value in inputs.items()},
            "cpu_reference_rows": len(cpu_rows),
            "backend_results": {},
        }
        backend_results = case_payload["backend_results"]
        assert isinstance(backend_results, dict)
        for backend_name in ("embree", "apple_rt"):
            measured = _measure(backends[backend_name], warmups=warmups, repeats=repeats, cv_threshold=cv_threshold)
            last_result = measured.pop("last_result")
            stats = measured["stats"]
            assert isinstance(stats, dict)
            backend_results[backend_name] = {
                **measured,
                "row_count": len(last_result),
                "matches_cpu_reference": _rows_match(workload, cpu_rows, last_result),
            }
            if not backend_results[backend_name]["stable"]:
                payload["unstable_results"].append(
                    {
                        "workload": workload,
                        "backend": backend_name,
                        "coefficient_of_variation": stats.get("coefficient_of_variation"),
                        "threshold": cv_threshold,
                    }
                )
        embree_median = backend_results["embree"]["stats"]["median_seconds"]
        apple_median = backend_results["apple_rt"]["stats"]["median_seconds"]
        if isinstance(embree_median, float) and isinstance(apple_median, float) and embree_median > 0.0:
            case_payload["apple_rt_vs_embree_median_ratio"] = apple_median / embree_median
        payload["cases"].append(case_payload)
    return payload


def render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal595: Apple RT Repeatable Performance Harness",
        "",
        f"Date: {payload['date']}",
        "",
        "Status: local measurement artifact",
        "",
        "## Methodology",
        "",
        "- Cold time is the first measured backend call in this process before harness warmups.",
        f"- Warmups before sample window: `{payload['methodology']['warmups_before_sample_window']}`.",
        f"- Measured repeats: `{payload['methodology']['measured_repeats']}`.",
        f"- Stability threshold: coefficient of variation <= `{payload['methodology']['stability_threshold_cv']}`.",
        "- Reported statistics are min, median, mean, max, standard deviation, and coefficient of variation over the measured repeat window.",
        "- CPU reference is used for parity; Embree is the mature RTDL local backend baseline.",
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
        "| Workload | Input sizes | Rows | Embree median | Apple RT median | Apple/Embree | Parity | Stability |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for case in payload["cases"]:
        backends = case["backend_results"]
        embree = backends["embree"]
        apple = backends["apple_rt"]
        parity = bool(embree["matches_cpu_reference"]) and bool(apple["matches_cpu_reference"])
        stability = bool(embree["stable"]) and bool(apple["stable"])
        ratio = case.get("apple_rt_vs_embree_median_ratio")
        ratio_text = f"{ratio:.3f}x" if isinstance(ratio, float) else "n/a"
        lines.append(
            "| "
            f"`{case['workload']}` | "
            f"`{case['input_sizes']}` | "
            f"{case['cpu_reference_rows']} | "
            f"{embree['stats']['median_seconds']:.9f} s | "
            f"{apple['stats']['median_seconds']:.9f} s | "
            f"{ratio_text} | "
            f"{parity} | "
            f"{stability} |"
        )
    unstable = payload.get("unstable_results", [])
    if unstable:
        lines.extend(["", "## Stability Warnings", "", "```json", json.dumps(unstable, indent=2), "```"])
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This harness is the v0.9.2 baseline gate. It is not a final performance claim.",
            "If any backend/workload cell is marked unstable, its median is evidence for engineering triage only and must not be used as public speedup wording.",
            "The next Apple RT optimization goals should compare against this artifact and only update public wording after repeatable parity and timing evidence exists.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--cv-threshold", type=float, default=0.15)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    args = parser.parse_args()
    if args.warmups < 0 or args.repeats <= 0:
        raise SystemExit("--warmups must be >= 0 and --repeats must be > 0")
    if args.cv_threshold <= 0.0:
        raise SystemExit("--cv-threshold must be > 0")
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

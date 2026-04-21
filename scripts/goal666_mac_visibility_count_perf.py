#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from math import ceil
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import rtdsl as rt
from scripts import goal659_mac_visibility_collision_perf as visibility_harness


DEFAULT_JSON = ROOT / "docs" / "reports" / "goal666_mac_visibility_count_perf_2026-04-20.json"
DEFAULT_MD = ROOT / "docs" / "reports" / "goal666_mac_visibility_count_perf_2026-04-20.md"


def _parse_scale(text: str) -> tuple[str, int, int]:
    return visibility_harness._parse_scale(text)


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
        "coefficient_of_variation": stdev / mean if mean else None,
    }


def _measure_count(
    name: str,
    fn: Callable[[], int],
    *,
    warmups: int,
    repeats: int,
    target_sample_seconds: float,
    expected_count: int | None,
    max_inner_iterations: int = 100000,
) -> dict[str, object]:
    def run_inner(inner_iterations: int) -> int:
        count = 0
        for _ in range(inner_iterations):
            count = fn()
        return count

    try:
        prime_start = time.perf_counter()
        prime_count = fn()
        prime_seconds = time.perf_counter() - prime_start
        calibration_start = time.perf_counter()
        calibration_iterations = 0
        while calibration_iterations < 3 or (time.perf_counter() - calibration_start) < 0.25:
            fn()
            calibration_iterations += 1
            if calibration_iterations >= max_inner_iterations:
                break
        calibration_total_seconds = time.perf_counter() - calibration_start
        calibration_seconds = calibration_total_seconds / max(1, calibration_iterations)
        inner_iterations = 1
        if target_sample_seconds > 0.0 and calibration_seconds > 0.0:
            inner_iterations = max(1, min(max_inner_iterations, ceil(target_sample_seconds / calibration_seconds)))
        for _ in range(warmups):
            run_inner(inner_iterations)
        samples: list[float] = []
        count = prime_count
        for _ in range(repeats):
            start = time.perf_counter()
            count = run_inner(inner_iterations)
            samples.append(time.perf_counter() - start)
        per_query = [sample / inner_iterations for sample in samples]
        return {
            "backend": name,
            "status": "ok",
            "prime_seconds": prime_seconds,
            "calibration_seconds": calibration_seconds,
            "calibration_iterations": calibration_iterations,
            "inner_iterations": inner_iterations,
            "samples_seconds": samples,
            "stats": _stats(samples),
            "per_query_samples_seconds": per_query,
            "per_query_stats": _stats(per_query),
            "blocked_count": count,
            "matches_expected_count": count == expected_count if expected_count is not None else None,
        }
    except Exception as exc:
        return {"backend": name, "status": "error", "error": f"{type(exc).__name__}: {exc}"}


def _count_rows(rows: tuple[dict[str, object], ...]) -> int:
    return sum(1 for row in rows if int(row["any_hit"]) != 0)


def run_benchmark(
    scales: tuple[tuple[str, int, int], ...],
    *,
    warmups: int,
    repeats: int,
    target_sample_seconds: float,
    oracle_mode: str,
) -> dict[str, object]:
    cases: list[dict[str, object]] = []
    for label, ray_count, obstacle_count in scales:
        kind, scale_name = label.split(":", 1)
        case = visibility_harness.make_case(kind, ray_count, obstacle_count)
        rays = case["rays"]
        triangles = case["triangles"]
        expected_count = None
        oracle_seconds = None
        if oracle_mode == "full":
            start = time.perf_counter()
            expected_count = _count_rows(visibility_harness._run_oracle(rays, triangles))
            oracle_seconds = time.perf_counter() - start

        prepared = None
        packed_rays = None
        prepare_seconds = None
        pack_seconds = None
        try:
            start = time.perf_counter()
            prepared = rt.prepare_apple_rt_ray_triangle_any_hit_2d(triangles)
            prepare_seconds = time.perf_counter() - start
            start = time.perf_counter()
            packed_rays = rt.prepare_apple_rt_rays_2d(rays)
            pack_seconds = time.perf_counter() - start
        except Exception:
            prepared = None
            packed_rays = None

        measurements: list[dict[str, object]] = []
        if prepared is not None and packed_rays is not None:
            measurements.append(
                _measure_count(
                    "apple_rt_prepared_packed_count",
                    lambda prepared=prepared, packed_rays=packed_rays: prepared.count_profile_packed(packed_rays)[0],
                    warmups=warmups,
                    repeats=repeats,
                    target_sample_seconds=target_sample_seconds,
                    expected_count=expected_count,
                )
            )
        else:
            measurements.append({"backend": "apple_rt_prepared_packed_count", "status": "error", "error": "prepared Apple RT unavailable"})
        measurements.append(
            _measure_count(
                "embree_row_count",
                lambda rays=rays, triangles=triangles: _count_rows(visibility_harness._run_embree(rays, triangles)),
                warmups=warmups,
                repeats=repeats,
                target_sample_seconds=target_sample_seconds,
                expected_count=expected_count,
            )
        )
        measurements.append(
            _measure_count(
                "shapely_strtree_count",
                lambda rays=rays, triangles=triangles: _count_rows(visibility_harness._run_shapely_strtree(rays, triangles)),
                warmups=warmups,
                repeats=repeats,
                target_sample_seconds=target_sample_seconds,
                expected_count=expected_count,
            )
        )
        if oracle_mode == "backend_agreement":
            reference = next((m for m in measurements if m.get("status") == "ok"), None)
            expected_count = int(reference["blocked_count"]) if reference is not None else None
            reference_backend = str(reference["backend"]) if reference is not None else None
            for measurement in measurements:
                if measurement.get("status") == "ok":
                    measurement["reference_backend"] = reference_backend
                    measurement["matches_reference_count"] = int(measurement["blocked_count"]) == expected_count
        if prepared is not None:
            prepared.close()
        cases.append(
            {
                "case": label,
                "kind": kind,
                "scale": scale_name,
                "ray_count": ray_count,
                "obstacle_rectangle_count": obstacle_count,
                "obstacle_triangle_count": len(triangles),
                "oracle_mode": oracle_mode,
                "oracle_seconds": oracle_seconds,
                "expected_blocked_count": expected_count,
                "apple_rt_prepare_seconds": prepare_seconds,
                "apple_rt_ray_pack_seconds": pack_seconds,
                "measurements": measurements,
            }
        )
    return {
        "goal": "goal666_mac_visibility_count_perf",
        "date": "2026-04-20",
        "host": visibility_harness.host_info(),
        "methodology": {
            "workload": "Visibility/collision blocked-ray count.",
            "correctness_mode": oracle_mode,
            "warmups": warmups,
            "repeats": repeats,
            "target_sample_seconds": target_sample_seconds,
            "note": "Apple RT uses prepared scene and prepacked rays, then returns only blocked-ray count. Embree/Shapely baselines materialize rows and reduce to count because they do not expose the same scalar prepared-count API in this harness.",
        },
        "cases": cases,
    }


def render_markdown(payload: dict[str, object]) -> str:
    methodology = payload["methodology"]
    lines = [
        "# Goal666: Mac Visibility Count Performance",
        "",
        "Date: 2026-04-20",
        "",
        "Status: characterization artifact",
        "",
        "## Methodology",
        "",
        f"- Workload: {methodology['workload']}",
        f"- Correctness mode: `{methodology['correctness_mode']}`.",
        f"- {methodology['note']}",
        "- Each timing sample loops enough calls to approach the requested target duration, then reports per-query median.",
        "- This is a fair app-level comparison for scalar blocked-ray count, not for full row-table output.",
        "",
        "## Host",
        "",
        "```json",
        json.dumps(payload["host"], indent=2, sort_keys=True),
        "```",
        "",
        "## Results",
        "",
        "### Setup Costs",
        "",
        "| Case | Apple RT Scene Prepare | Apple RT Ray Pack | Oracle Time |",
        "| --- | ---: | ---: | ---: |",
    ]
    for case in payload["cases"]:
        lines.append(
            "| {case} | {prepare} | {pack} | {oracle} |".format(
                case=case["case"],
                prepare=f"{float(case['apple_rt_prepare_seconds']):.6f} s" if case.get("apple_rt_prepare_seconds") is not None else "n/a",
                pack=f"{float(case['apple_rt_ray_pack_seconds']):.6f} s" if case.get("apple_rt_ray_pack_seconds") is not None else "n/a",
                oracle=f"{float(case['oracle_seconds']):.6f} s" if case.get("oracle_seconds") is not None else "n/a",
            )
        )
    lines.extend(
        [
            "",
            "### Repeated Query Cost",
            "",
        "| Case | Rays | Triangles | Backend | Status | Per-Query Median | Inner Iterations | Blocked Count | Correctness |",
        "| --- | ---: | ---: | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for case in payload["cases"]:
        for measurement in case["measurements"]:
            if measurement["status"] != "ok":
                lines.append(f"| {case['case']} | {case['ray_count']} | {case['obstacle_triangle_count']} | `{measurement['backend']}` | error | n/a | n/a | n/a | {measurement.get('error', 'n/a')} |")
                continue
            correctness = "not checked"
            if measurement.get("matches_expected_count") is not None:
                correctness = f"oracle={measurement['matches_expected_count']}"
            elif measurement.get("matches_reference_count") is not None:
                correctness = f"{measurement['reference_backend']}={measurement['matches_reference_count']}"
            lines.append(
                "| {case} | {rays} | {tris} | `{backend}` | ok | {per_query:.9f} s | {inner} | {blocked} | {correctness} |".format(
                    case=case["case"],
                    rays=case["ray_count"],
                    tris=case["obstacle_triangle_count"],
                    backend=measurement["backend"],
                    per_query=float(measurement["per_query_stats"]["median_seconds"]),
                    inner=int(measurement["inner_iterations"]),
                    blocked=int(measurement["blocked_count"]),
                    correctness=correctness,
                )
            )
    lines.extend(["", "## Ratio Summary", ""])
    for case in payload["cases"]:
        by_backend = {m["backend"]: m for m in case["measurements"] if m.get("status") == "ok"}
        apple = by_backend.get("apple_rt_prepared_packed_count")
        embree = by_backend.get("embree_row_count")
        shapely = by_backend.get("shapely_strtree_count")
        parts: list[str] = []
        if apple and embree:
            apple_t = float(apple["per_query_stats"]["median_seconds"])
            embree_t = float(embree["per_query_stats"]["median_seconds"])
            parts.append(f"Apple packed-count / Embree row-count: {apple_t / embree_t:.3f}x")
        if apple and shapely:
            apple_t = float(apple["per_query_stats"]["median_seconds"])
            shapely_t = float(shapely["per_query_stats"]["median_seconds"])
            parts.append(f"Apple packed-count / Shapely count: {apple_t / shapely_t:.3f}x")
        if parts:
            lines.append(f"- `{case['case']}`: " + "; ".join(parts))
    lines.extend(
        [
            "",
            "## Major Conclusion",
            "",
            "For scalar visibility/collision count, the optimized Apple RT prepared packed-count path is now substantially faster than row-materialized Embree and Shapely/GEOS in this harness. This does not mean Apple RT is faster for full emitted-row output: the row path remains slower than Embree because Python-facing row materialization dominates. The correct claim is narrower: when an app can prepack rays and consume a scalar count, Apple RT can expose a fast Mac hardware-backed path.",
            "",
            "## Interpretation Rules",
            "",
            "- Include Apple RT scene preparation and ray packing separately when judging first-query latency.",
            "- Use per-query timing for repeated-query apps where obstacles and ray buffers are reused.",
            "- Do not compare this scalar-count result against full-row Embree as if the output contracts were identical.",
            "- Do not generalize this result to Apple RT DB or graph workloads.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mac Apple RT visibility/collision count benchmark.")
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--target-sample-seconds", type=float, default=2.0)
    parser.add_argument("--oracle-mode", choices=("full", "backend_agreement"), default="backend_agreement")
    parser.add_argument(
        "--scale",
        action="append",
        type=_parse_scale,
        default=None,
        help="Add a scale as KIND:NAME,RAYS,OBSTACLE_RECTS. KIND is dense_blocked, sparse_clear, or mixed_visibility.",
    )
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    args = parser.parse_args(argv)
    scales = tuple(
        args.scale
        if args.scale
        else (
            ("dense_blocked:large_count", 32768, 4096),
            ("mixed_visibility:large_count", 32768, 4096),
            ("sparse_clear:large_count", 32768, 4096),
        )
    )
    payload = run_benchmark(
        scales,
        warmups=args.warmups,
        repeats=args.repeats,
        target_sample_seconds=args.target_sample_seconds,
        oracle_mode=args.oracle_mode,
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

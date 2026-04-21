#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import rtdsl as rt
from scripts import goal659_mac_visibility_collision_perf as visibility_harness


DEFAULT_JSON = ROOT / "docs" / "reports" / "goal665_apple_rt_prepared_profile_2026-04-20.json"
DEFAULT_MD = ROOT / "docs" / "reports" / "goal665_apple_rt_prepared_profile_2026-04-20.md"


def _parse_scale(text: str) -> tuple[str, int, int]:
    return visibility_harness._parse_scale(text)


def _stats(values: list[float]) -> dict[str, float | int]:
    if not values:
        return {"count": 0}
    mean = statistics.mean(values)
    return {
        "count": len(values),
        "min": min(values),
        "median": statistics.median(values),
        "mean": mean,
        "max": max(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
    }


def _profile_case(label: str, ray_count: int, obstacle_count: int, repeats: int) -> dict[str, object]:
    kind, scale_name = label.split(":", 1)
    case = visibility_harness.make_case(kind, ray_count, obstacle_count)
    rays = case["rays"]
    triangles = case["triangles"]
    packed_rays = rt.prepare_apple_rt_rays_2d(rays)
    prepare_start = time.perf_counter()
    prepared = rt.prepare_apple_rt_ray_triangle_any_hit_2d(triangles)
    prepare_seconds = time.perf_counter() - prepare_start
    profile_rows: list[dict[str, float | int]] = []
    count_profile_rows: list[dict[str, float | int]] = []
    packed_count_profile_rows: list[dict[str, float | int]] = []
    python_wall_seconds: list[float] = []
    count_python_wall_seconds: list[float] = []
    packed_count_python_wall_seconds: list[float] = []
    try:
        for _ in range(repeats):
            start = time.perf_counter()
            rows_view, profile = prepared.run_profile(rays)
            rows = tuple(rows_view)
            rows_view.close()
            python_wall_seconds.append(time.perf_counter() - start)
            profile = dict(profile)
            profile["blocked_count"] = sum(1 for row in rows if int(row["any_hit"]) != 0)
            profile_rows.append(profile)
            start = time.perf_counter()
            hit_count, count_profile = prepared.count_profile(rays)
            count_python_wall_seconds.append(time.perf_counter() - start)
            count_profile = dict(count_profile)
            count_profile["blocked_count"] = hit_count
            count_profile_rows.append(count_profile)
            start = time.perf_counter()
            packed_hit_count, packed_count_profile = prepared.count_profile_packed(packed_rays)
            packed_count_python_wall_seconds.append(time.perf_counter() - start)
            packed_count_profile = dict(packed_count_profile)
            packed_count_profile["blocked_count"] = packed_hit_count
            packed_count_profile_rows.append(packed_count_profile)
    finally:
        prepared.close()
    timing_keys = (
        "total_seconds",
        "buffer_seconds",
        "ray_pack_seconds",
        "dispatch_wait_seconds",
        "result_scan_seconds",
        "output_seconds",
    )
    aggregate: dict[str, object] = {key: _stats([float(row[key]) for row in profile_rows]) for key in timing_keys}
    aggregate["python_wall_seconds"] = _stats(python_wall_seconds)
    count_aggregate: dict[str, object] = {key: _stats([float(row[key]) for row in count_profile_rows]) for key in timing_keys}
    count_aggregate["python_wall_seconds"] = _stats(count_python_wall_seconds)
    packed_count_aggregate: dict[str, object] = {key: _stats([float(row[key]) for row in packed_count_profile_rows]) for key in timing_keys}
    packed_count_aggregate["python_wall_seconds"] = _stats(packed_count_python_wall_seconds)
    median_total = float(aggregate["total_seconds"]["median"])
    fractions = {
        key: (float(aggregate[key]["median"]) / median_total if median_total > 0.0 else None)
        for key in timing_keys
        if key != "total_seconds"
    }
    return {
        "case": label,
        "kind": kind,
        "scale": scale_name,
        "ray_count": ray_count,
        "obstacle_rectangle_count": obstacle_count,
        "obstacle_triangle_count": len(triangles),
        "prepare_seconds": prepare_seconds,
        "repeats": repeats,
        "aggregate": aggregate,
        "count_aggregate": count_aggregate,
        "packed_count_aggregate": packed_count_aggregate,
        "median_fraction_of_native_total": fractions,
        "last_profile": profile_rows[-1] if profile_rows else None,
        "last_count_profile": count_profile_rows[-1] if count_profile_rows else None,
        "last_packed_count_profile": packed_count_profile_rows[-1] if packed_count_profile_rows else None,
    }


def render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal665: Apple RT Prepared Any-Hit Native Profile",
        "",
        "Date: 2026-04-20",
        "",
        "Status: characterization artifact",
        "",
        "## Methodology",
        "",
        "- Uses the native `rtdl_apple_rt_profile_prepared_ray_anyhit_2d` entry point.",
        "- Reports native section timings inside the Apple RT prepared 2D any-hit call.",
        "- Python wall time is included to estimate wrapper/materialization overhead outside native timing.",
        "- This is profiling evidence, not a new performance-win claim.",
        "",
        "## Results",
        "",
        "### Row Materialization Path",
        "",
        "| Case | Rays | Triangles | Prepare | Native Total | Python Wall | Buffer | Ray Pack | Dispatch/Wait | Result Scan | Output |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for case in payload["cases"]:
        aggregate = case["aggregate"]
        lines.append(
            "| {case} | {rays} | {tris} | {prepare:.6f} s | {total:.6f} s | {wall:.6f} s | {buffer:.6f} s | {pack:.6f} s | {dispatch:.6f} s | {scan:.6f} s | {output:.6f} s |".format(
                case=case["case"],
                rays=case["ray_count"],
                tris=case["obstacle_triangle_count"],
                prepare=float(case["prepare_seconds"]),
                total=float(aggregate["total_seconds"]["median"]),
                wall=float(aggregate["python_wall_seconds"]["median"]),
                buffer=float(aggregate["buffer_seconds"]["median"]),
                pack=float(aggregate["ray_pack_seconds"]["median"]),
                dispatch=float(aggregate["dispatch_wait_seconds"]["median"]),
                scan=float(aggregate["result_scan_seconds"]["median"]),
                output=float(aggregate["output_seconds"]["median"]),
            )
        )
    lines.extend(
        [
            "",
            "### Count-Only App Path",
            "",
            "| Case | Rays | Triangles | Native Total | Python Wall | Buffer | Ray Pack | Dispatch/Wait | Result Scan | Output |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for case in payload["cases"]:
        aggregate = case["count_aggregate"]
        lines.append(
            "| {case} | {rays} | {tris} | {total:.6f} s | {wall:.6f} s | {buffer:.6f} s | {pack:.6f} s | {dispatch:.6f} s | {scan:.6f} s | {output:.6f} s |".format(
                case=case["case"],
                rays=case["ray_count"],
                tris=case["obstacle_triangle_count"],
                total=float(aggregate["total_seconds"]["median"]),
                wall=float(aggregate["python_wall_seconds"]["median"]),
                buffer=float(aggregate["buffer_seconds"]["median"]),
                pack=float(aggregate["ray_pack_seconds"]["median"]),
                dispatch=float(aggregate["dispatch_wait_seconds"]["median"]),
                scan=float(aggregate["result_scan_seconds"]["median"]),
                output=float(aggregate["output_seconds"]["median"]),
            )
        )
    lines.extend(
        [
            "",
            "### Packed-Ray Count-Only App Path",
            "",
            "| Case | Rays | Triangles | Native Total | Python Wall | Buffer | Ray Pack | Dispatch/Wait | Result Scan | Output |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for case in payload["cases"]:
        aggregate = case["packed_count_aggregate"]
        lines.append(
            "| {case} | {rays} | {tris} | {total:.6f} s | {wall:.6f} s | {buffer:.6f} s | {pack:.6f} s | {dispatch:.6f} s | {scan:.6f} s | {output:.6f} s |".format(
                case=case["case"],
                rays=case["ray_count"],
                tris=case["obstacle_triangle_count"],
                total=float(aggregate["total_seconds"]["median"]),
                wall=float(aggregate["python_wall_seconds"]["median"]),
                buffer=float(aggregate["buffer_seconds"]["median"]),
                pack=float(aggregate["ray_pack_seconds"]["median"]),
                dispatch=float(aggregate["dispatch_wait_seconds"]["median"]),
                scan=float(aggregate["result_scan_seconds"]["median"]),
                output=float(aggregate["output_seconds"]["median"]),
            )
        )
    lines.extend(["", "## Fraction Of Native Total", ""])
    for case in payload["cases"]:
        fractions = case["median_fraction_of_native_total"]
        parts = [
            f"buffer={fractions['buffer_seconds']:.1%}",
            f"ray_pack={fractions['ray_pack_seconds']:.1%}",
            f"dispatch_wait={fractions['dispatch_wait_seconds']:.1%}",
            f"result_scan={fractions['result_scan_seconds']:.1%}",
            f"output={fractions['output_seconds']:.1%}",
        ]
        lines.append(f"- `{case['case']}`: " + ", ".join(parts))
    lines.extend(
        [
            "",
            "## Major Conclusion",
            "",
            "Native Apple RT traversal is not the dominant cost in the Python-facing row path. The native profiled sections are sub-millisecond to low-millisecond, while Python wall time is much larger because row dictionary materialization and repeated Python-side input packing are outside the useful RT work. The count-only path plus prepacked rays removes those two dominant costs for scalar visibility/collision apps: on the measured large cases, Python wall time falls from tens of milliseconds to sub-millisecond. The remaining boundary is output contract: this optimized path returns a scalar blocked-ray count, not the full emitted row table.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Profile native Apple RT prepared 2D any-hit sections.")
    parser.add_argument("--scale", action="append", type=_parse_scale, default=None)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    args = parser.parse_args(argv)
    scales = tuple(
        args.scale
        if args.scale
        else (
            ("dense_blocked:small_profile", 8192, 1024),
            ("dense_blocked:large_profile", 32768, 4096),
            ("sparse_clear:large_profile", 32768, 4096),
        )
    )
    payload = {
        "goal": "goal665_apple_rt_prepared_profile",
        "date": "2026-04-20",
        "cases": [_profile_case(label, rays, obstacles, args.repeats) for label, rays, obstacles in scales],
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

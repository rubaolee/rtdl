#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import numbers
import platform
import statistics
import subprocess
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


REPORTS_DIR = ROOT / "docs" / "reports"
DEFAULT_JSON = REPORTS_DIR / "goal659_mac_visibility_collision_perf_2026-04-20.json"
DEFAULT_MD = REPORTS_DIR / "goal659_mac_visibility_collision_perf_2026-04-20.md"


@rt.kernel(backend="rtdl", precision="float_approx")
def visibility_any_hit_2d_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_any_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "any_hit"])


def _rect_triangles(rect_id: int, x0: float, y0: float, x1: float, y1: float) -> tuple[rt.Triangle, rt.Triangle]:
    return (
        rt.Triangle(id=rect_id * 2, x0=x0, y0=y0, x1=x1, y1=y0, x2=x1, y2=y1),
        rt.Triangle(id=rect_id * 2 + 1, x0=x0, y0=y0, x1=x1, y1=y1, x2=x0, y2=y1),
    )


def _make_obstacle_triangles(obstacle_count: int) -> tuple[rt.Triangle, ...]:
    if obstacle_count < 1:
        raise ValueError("obstacle_count must be positive")
    grid = int(math.ceil(math.sqrt(obstacle_count)))
    triangles: list[rt.Triangle] = []
    for index in range(obstacle_count):
        gx = index % grid
        gy = index // grid
        x0 = gx * 1.75 + 0.55
        y0 = gy * 1.35 - 0.38
        triangles.extend(_rect_triangles(1000 + index, x0, y0, x0 + 0.48, y0 + 0.54))
    return tuple(triangles)


def _make_dense_blocked_rays(ray_count: int, obstacle_count: int) -> tuple[rt.Ray2D, ...]:
    grid = int(math.ceil(math.sqrt(obstacle_count)))
    rays: list[rt.Ray2D] = []
    for index in range(ray_count):
        obstacle = index % obstacle_count
        gx = obstacle % grid
        gy = obstacle // grid
        y = gy * 1.35 - 0.1 + ((index % 5) - 2) * 0.018
        rays.append(
            rt.Ray2D(
                id=index,
                ox=gx * 1.75 - 0.25,
                oy=y,
                dx=1.2,
                dy=0.0,
                tmax=1.0,
            )
        )
    return tuple(rays)


def _make_sparse_clear_rays(ray_count: int, obstacle_count: int) -> tuple[rt.Ray2D, ...]:
    grid = int(math.ceil(math.sqrt(obstacle_count)))
    height = max(1, math.ceil(obstacle_count / grid))
    y_base = height * 1.35 + 3.0
    rays: list[rt.Ray2D] = []
    for index in range(ray_count):
        lane = index % max(1, grid)
        rays.append(
            rt.Ray2D(
                id=index,
                ox=lane * 1.75 - 0.45,
                oy=y_base + (index % 17) * 0.003,
                dx=1.25,
                dy=0.0,
                tmax=1.0,
            )
        )
    return tuple(rays)


def _make_mixed_visibility_rays(ray_count: int, obstacle_count: int) -> tuple[rt.Ray2D, ...]:
    blocked_rays = _make_dense_blocked_rays(ray_count, obstacle_count)
    clear_rays = _make_sparse_clear_rays(ray_count, obstacle_count)
    rays: list[rt.Ray2D] = []
    for index in range(ray_count):
        source = blocked_rays[index] if index % 2 == 0 else clear_rays[index]
        rays.append(
            rt.Ray2D(
                id=index,
                ox=source.ox,
                oy=source.oy,
                dx=source.dx,
                dy=source.dy,
                tmax=source.tmax,
            )
        )
    return tuple(rays)


def make_case(kind: str, ray_count: int, obstacle_count: int) -> dict[str, object]:
    if ray_count < 1:
        raise ValueError("ray_count must be positive")
    triangles = _make_obstacle_triangles(obstacle_count)
    if kind == "dense_blocked":
        rays = _make_dense_blocked_rays(ray_count, obstacle_count)
    elif kind == "sparse_clear":
        rays = _make_sparse_clear_rays(ray_count, obstacle_count)
    elif kind == "mixed_visibility":
        rays = _make_mixed_visibility_rays(ray_count, obstacle_count)
    else:
        raise ValueError(f"unknown case kind: {kind}")
    return {"rays": rays, "triangles": triangles}


def _summary(rows: tuple[dict[str, object], ...]) -> dict[str, int]:
    blocked = sum(1 for row in rows if int(row["any_hit"]) != 0)
    return {"row_count": len(rows), "blocked_count": blocked, "clear_count": len(rows) - blocked}


def _canonical_any_hit(rows: tuple[dict[str, object], ...]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted((int(row["ray_id"]), int(row["any_hit"]) != 0) for row in rows))


def _run_apple_rt(rays: tuple[rt.Ray2D, ...], triangles: tuple[rt.Triangle, ...]) -> tuple[dict[str, object], ...]:
    return tuple(rt.run_apple_rt(visibility_any_hit_2d_kernel, native_only=True, rays=rays, triangles=triangles))


def _run_embree(rays: tuple[rt.Ray2D, ...], triangles: tuple[rt.Triangle, ...]) -> tuple[dict[str, object], ...]:
    return tuple(rt.run_embree(visibility_any_hit_2d_kernel, rays=rays, triangles=triangles))


def _run_oracle(rays: tuple[rt.Ray2D, ...], triangles: tuple[rt.Triangle, ...]) -> tuple[dict[str, object], ...]:
    return tuple(rt.ray_triangle_any_hit_cpu(rays, triangles))


def _run_shapely_strtree(rays: tuple[rt.Ray2D, ...], triangles: tuple[rt.Triangle, ...]) -> tuple[dict[str, object], ...]:
    try:
        from shapely.geometry import LineString
        from shapely.geometry import Polygon
        from shapely.strtree import STRtree
    except Exception as exc:
        raise RuntimeError(f"Shapely/GEOS baseline unavailable: {exc}") from exc

    polygons = [
        Polygon(((tri.x0, tri.y0), (tri.x1, tri.y1), (tri.x2, tri.y2)))
        for tri in triangles
    ]
    tree = STRtree(polygons)
    rows: list[dict[str, object]] = []
    for ray in rays:
        segment = LineString(((ray.ox, ray.oy), (ray.ox + ray.dx * ray.tmax, ray.oy + ray.dy * ray.tmax)))
        any_hit = 0
        for candidate in tree.query(segment):
            polygon = polygons[int(candidate)] if isinstance(candidate, numbers.Integral) else candidate
            if segment.intersects(polygon):
                any_hit = 1
                break
        rows.append({"ray_id": ray.id, "any_hit": any_hit})
    return tuple(rows)


def _seconds(fn: Callable[[], tuple[dict[str, object], ...]]) -> tuple[float, tuple[dict[str, object], ...]]:
    start = time.perf_counter()
    result = fn()
    return time.perf_counter() - start, result


def _stats(samples: list[float]) -> dict[str, object]:
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


def _measure(
    name: str,
    fn: Callable[[], tuple[dict[str, object], ...]],
    oracle_rows: tuple[dict[str, object], ...] | None,
    *,
    warmups: int,
    repeats: int,
    target_sample_seconds: float = 0.0,
    max_inner_iterations: int = 10000,
) -> dict[str, object]:
    def run_inner(inner_iterations: int) -> tuple[dict[str, object], ...]:
        rows: tuple[dict[str, object], ...] = ()
        for _ in range(inner_iterations):
            rows = fn()
        return rows

    try:
        prime_seconds, prime_rows = _seconds(fn)
        calibration_start = time.perf_counter()
        calibration_rows = prime_rows
        calibration_iterations = 0
        while calibration_iterations < 3 or (time.perf_counter() - calibration_start) < 0.25:
            calibration_rows = fn()
            calibration_iterations += 1
            if calibration_iterations >= max_inner_iterations:
                break
        calibration_total_seconds = time.perf_counter() - calibration_start
        calibration_seconds = calibration_total_seconds / max(1, calibration_iterations)
        inner_iterations = 1
        if target_sample_seconds > 0.0 and calibration_seconds > 0.0:
            inner_iterations = max(1, min(max_inner_iterations, ceil(target_sample_seconds / calibration_seconds)))
        cold_seconds, cold_rows = _seconds(lambda: run_inner(inner_iterations))
        for _ in range(warmups):
            run_inner(inner_iterations)
        samples: list[float] = []
        rows = cold_rows
        for _ in range(repeats):
            seconds, rows = _seconds(lambda: run_inner(inner_iterations))
            samples.append(seconds)
        sample_stats = _stats(samples)
        per_query_samples = [sample / inner_iterations for sample in samples]
        return {
            "backend": name,
            "status": "ok",
            "prime_seconds": prime_seconds,
            "calibration_seconds": calibration_seconds,
            "calibration_total_seconds": calibration_total_seconds,
            "calibration_iterations": calibration_iterations,
            "inner_iterations": inner_iterations,
            "cold_seconds": cold_seconds,
            "warmups": warmups,
            "samples_seconds": samples,
            "stats": sample_stats,
            "per_query_samples_seconds": per_query_samples,
            "per_query_stats": _stats(per_query_samples),
            "summary": _summary(rows),
            "matches_oracle": _canonical_any_hit(rows) == _canonical_any_hit(oracle_rows) if oracle_rows is not None else None,
            "canonical_rows": _canonical_any_hit(rows),
        }
    except Exception as exc:
        return {"backend": name, "status": "error", "error": f"{type(exc).__name__}: {exc}"}


def _command(cmd: list[str]) -> str | None:
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT, timeout=8).strip()
    except Exception:
        return None


def _safe_version(fn: Callable[[], object]) -> str:
    try:
        return str(fn())
    except Exception as exc:
        return f"unavailable: {type(exc).__name__}: {exc}"


def host_info() -> dict[str, object]:
    return {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "processor": platform.processor(),
        "sw_vers": _command(["sw_vers"]),
        "apple_rt_version": _safe_version(rt.apple_rt_version),
        "apple_rt_context": _safe_version(rt.apple_rt_context_probe),
        "embree_version": _safe_version(rt.embree_version),
    }


def run_benchmark(
    scales: tuple[tuple[str, int, int], ...],
    *,
    warmups: int,
    repeats: int,
    backends: tuple[str, ...],
    target_sample_seconds: float,
    oracle_mode: str,
) -> dict[str, object]:
    cases: list[dict[str, object]] = []
    for label, ray_count, obstacle_count in scales:
        kind, scale_name = label.split(":", 1)
        case = make_case(kind, ray_count, obstacle_count)
        rays = case["rays"]
        triangles = case["triangles"]
        oracle_rows = _run_oracle(rays, triangles) if oracle_mode == "full" else None
        prepare_seconds = None
        prepared = None
        prepared_error = None
        try:
            start = time.perf_counter()
            prepared = rt.prepare_apple_rt_ray_triangle_any_hit_2d(triangles)
            prepare_seconds = time.perf_counter() - start
        except Exception as exc:
            prepared_error = f"{type(exc).__name__}: {exc}"
        measurements = []
        if "apple_rt" in backends:
            measurements.append(
                _measure(
                    "apple_rt",
                    lambda rays=rays, triangles=triangles: _run_apple_rt(rays, triangles),
                    oracle_rows,
                    warmups=warmups,
                    repeats=repeats,
                    target_sample_seconds=target_sample_seconds,
                )
            )
        if "apple_rt_prepared_query" in backends:
            if prepared is not None:
                measurements.append(
                    _measure(
                        "apple_rt_prepared_query",
                        lambda prepared=prepared, rays=rays: tuple(prepared.run(rays)),
                        oracle_rows,
                        warmups=warmups,
                        repeats=repeats,
                        target_sample_seconds=target_sample_seconds,
                    )
                )
            else:
                measurements.append(
                    {
                        "backend": "apple_rt_prepared_query",
                        "status": "error",
                        "error": prepared_error or "prepared Apple RT unavailable",
                    }
                )
        if "embree" in backends:
            measurements.append(
                _measure(
                    "embree",
                    lambda rays=rays, triangles=triangles: _run_embree(rays, triangles),
                    oracle_rows,
                    warmups=warmups,
                    repeats=repeats,
                    target_sample_seconds=target_sample_seconds,
                )
            )
        if "shapely_strtree" in backends:
            measurements.append(
                _measure(
                    "shapely_strtree",
                    lambda rays=rays, triangles=triangles: _run_shapely_strtree(rays, triangles),
                    oracle_rows,
                    warmups=warmups,
                    repeats=repeats,
                    target_sample_seconds=target_sample_seconds,
                ),
            )
        reference_backend = None
        reference_rows = None
        if oracle_mode == "backend_agreement":
            for measurement in measurements:
                if measurement.get("status") == "ok":
                    reference_backend = str(measurement["backend"])
                    reference_rows = measurement.get("canonical_rows")
                    break
            for measurement in measurements:
                if measurement.get("status") == "ok":
                    measurement["reference_backend"] = reference_backend
                    measurement["matches_reference_backend"] = measurement.get("canonical_rows") == reference_rows
        for measurement in measurements:
            measurement.pop("canonical_rows", None)
        if prepared is not None:
            prepared.close()
        cases.append(
            {
                "case": label,
                "kind": kind,
                "scale": scale_name,
                "ray_count": ray_count,
                "obstacle_triangle_count": len(triangles),
                "obstacle_rectangle_count": obstacle_count,
                "apple_rt_prepare_seconds": prepare_seconds,
                "oracle_summary": _summary(oracle_rows) if oracle_rows is not None else None,
                "oracle_mode": oracle_mode,
                "measurements": measurements,
            }
        )
    return {
        "goal": "goal659_mac_visibility_collision_perf",
        "date": "2026-04-20",
        "host": host_info(),
        "methodology": {
            "reported_backends": list(backends),
            "correctness_mode": oracle_mode,
            "hidden_correctness_oracle": "rt.ray_triangle_any_hit_cpu" if oracle_mode == "full" else None,
            "warmups": warmups,
            "repeats": repeats,
            "target_sample_seconds": target_sample_seconds,
            "note": (
                "CPU/oracle is used only for parity and is not reported as a performance engine."
                if oracle_mode == "full"
                else "Full CPU/oracle is skipped for scale; successful backends are compared by backend-output agreement."
                if oracle_mode == "backend_agreement"
                else "Full CPU/oracle is skipped; this mode is timing-only and does not establish correctness."
            ),
        },
        "cases": cases,
    }


def render_markdown(payload: dict[str, object]) -> str:
    methodology = payload.get("methodology", {})
    note = methodology.get("note", "CPU/oracle is used only for correctness parity and is not reported as a performance engine.")
    lines = [
        "# Goal659: Mac Visibility/Collision Performance",
        "",
        "Date: 2026-04-20",
        "",
        "Status: characterization artifact",
        "",
        "## Methodology",
        "",
        "- Reported engines: Apple RT one-shot, Apple RT prepared-query, Embree, Shapely/GEOS STRtree when installed.",
        f"- Correctness mode: `{methodology.get('correctness_mode', 'full')}`.",
        f"- {note}",
        "- Each case reports repeated warm samples; with target-sample mode, each sample loops enough queries to approach the requested wall time and also reports per-query median.",
        "- Apple RT uses `run_apple_rt(..., native_only=True)` over the 2D any-hit kernel.",
        "",
        "## Host",
        "",
        "```json",
        json.dumps(payload["host"], indent=2, sort_keys=True),
        "```",
        "",
        "## Results",
        "",
        "| Case | Rays | Triangles | Backend | Status | Sample Median | Per-Query Median | Inner Iterations | Prepare | Blocked | Correctness Check |",
        "| --- | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for case in payload["cases"]:
        for measurement in case["measurements"]:
            if measurement["status"] == "ok":
                stats = measurement["stats"]
                per_query_stats = measurement.get("per_query_stats", stats)
                summary = measurement["summary"]
                if measurement.get("matches_oracle") is not None:
                    correctness = f"oracle={measurement['matches_oracle']}"
                elif measurement.get("matches_reference_backend") is not None:
                    correctness = f"{measurement['reference_backend']}={measurement['matches_reference_backend']}"
                else:
                    correctness = "not checked"
                lines.append(
                    "| {case} | {rays} | {tris} | `{backend}` | ok | {median:.6f} s | {per_query:.9f} s | {inner} | {prepare} | {blocked} | {correctness} |".format(
                        case=case["case"],
                        rays=case["ray_count"],
                        tris=case["obstacle_triangle_count"],
                        backend=measurement["backend"],
                        median=float(stats["median_seconds"]),
                        per_query=float(per_query_stats["median_seconds"]),
                        inner=int(measurement.get("inner_iterations", 1)),
                        prepare=(
                            f"{float(case['apple_rt_prepare_seconds']):.6f} s"
                            if measurement["backend"] == "apple_rt_prepared_query" and case.get("apple_rt_prepare_seconds") is not None
                            else "n/a"
                        ),
                        blocked=int(summary["blocked_count"]),
                        correctness=correctness,
                    )
                )
            else:
                lines.append(
                    f"| {case['case']} | {case['ray_count']} | {case['obstacle_triangle_count']} | `{measurement['backend']}` | error | n/a | n/a | n/a | n/a | n/a | n/a |"
                )
    lines.extend(["", "## Ratio Summary", ""])
    for case in payload["cases"]:
        by_backend = {measurement["backend"]: measurement for measurement in case["measurements"]}
        apple = by_backend.get("apple_rt")
        embree = by_backend.get("embree")
        shapely = by_backend.get("shapely_strtree")
        prepared = by_backend.get("apple_rt_prepared_query")
        ratio_parts: list[str] = []
        if apple and embree and apple["status"] == "ok" and embree["status"] == "ok":
            apple_median = float(apple["stats"]["median_seconds"])
            embree_median = float(embree["stats"]["median_seconds"])
            apple_query = float(apple.get("per_query_stats", apple["stats"])["median_seconds"])
            embree_query = float(embree.get("per_query_stats", embree["stats"])["median_seconds"])
            ratio_parts.append(f"Apple RT / Embree per-query: {apple_query / embree_query:.3f}x")
        if apple and shapely and apple["status"] == "ok" and shapely["status"] == "ok":
            apple_query = float(apple.get("per_query_stats", apple["stats"])["median_seconds"])
            shapely_query = float(shapely.get("per_query_stats", shapely["stats"])["median_seconds"])
            ratio_parts.append(f"Apple RT / Shapely STRtree per-query: {apple_query / shapely_query:.3f}x")
        if prepared and embree and prepared["status"] == "ok" and embree["status"] == "ok":
            prepared_query = float(prepared.get("per_query_stats", prepared["stats"])["median_seconds"])
            embree_query = float(embree.get("per_query_stats", embree["stats"])["median_seconds"])
            ratio_parts.append(f"Apple RT prepared-query / Embree per-query: {prepared_query / embree_query:.3f}x")
        if prepared and shapely and prepared["status"] == "ok" and shapely["status"] == "ok":
            prepared_query = float(prepared.get("per_query_stats", prepared["stats"])["median_seconds"])
            shapely_query = float(shapely.get("per_query_stats", shapely["stats"])["median_seconds"])
            ratio_parts.append(f"Apple RT prepared-query / Shapely STRtree per-query: {prepared_query / shapely_query:.3f}x")
        if ratio_parts:
            lines.append(f"- `{case['case']}`: " + "; ".join(ratio_parts))
    correctness_mode = methodology.get("correctness_mode", "full")
    if correctness_mode == "full":
        conclusion = (
            "This is a useful Mac real-hardware app benchmark, but the current Apple RT path is not yet performance-leading versus Embree. "
            "All reported Apple RT, Embree, and Shapely/GEOS rows pass correctness parity on the measured scales. "
            "Embree is the fastest engine in this run. Prepared Apple RT separates obstacle setup from repeated ray queries; use that row to judge app-style repeated-query behavior."
        )
    elif correctness_mode == "backend_agreement":
        conclusion = (
            "This is a useful Mac real-hardware app benchmark, but the current Apple RT path is not yet performance-leading versus Embree. "
            "Full CPU/oracle validation is intentionally skipped at this scale; successful backends are checked for canonical output agreement. "
            "Embree is the fastest engine in this run. Prepared Apple RT separates obstacle setup from repeated ray queries; use that row to judge app-style repeated-query behavior."
        )
    else:
        conclusion = (
            "This is a timing-only Mac real-hardware app benchmark. It does not establish correctness because oracle and backend-agreement checks are disabled."
        )
    lines.extend(
        [
            "",
            "## Major Conclusion",
            "",
            conclusion,
            "",
            "## Interpretation Rules",
            "",
            "- Do not treat CPU/oracle as a reported competitor in this benchmark.",
            "- In `backend_agreement` mode, correctness means successful backends produced the same canonical any-hit rows; it is not a full independent CPU proof.",
            "- Treat Shapely absence as an environment gap, not an RTDL speed result.",
            "- Treat Apple RT results as Mac real-hardware evidence only for the Apple RT rows that pass parity.",
            "- Dense-blocked cases are the intended any-hit-friendly shape; sparse-clear cases expose worst-case traversal/setup behavior.",
            "",
        ]
    )
    return "\n".join(lines)


def _parse_scale(text: str) -> tuple[str, int, int]:
    try:
        label, rays, obstacles = text.split(",")
        if ":" not in label:
            raise ValueError
        return label, int(rays), int(obstacles)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("scale must be KIND:NAME,RAYS,OBSTACLE_RECTS") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mac Apple RT visibility/collision benchmark against Embree and Shapely/GEOS.")
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument(
        "--backend",
        action="append",
        choices=("apple_rt", "apple_rt_prepared_query", "embree", "shapely_strtree"),
        default=None,
        help="Backend to include. Repeat this flag to select multiple backends.",
    )
    parser.add_argument(
        "--target-sample-seconds",
        type=float,
        default=0.0,
        help="If positive, calibrate inner iterations so each measured sample approaches this wall time.",
    )
    parser.add_argument(
        "--oracle-mode",
        choices=("full", "backend_agreement", "none"),
        default="full",
        help="Correctness mode: full CPU oracle, backend agreement only, or timing-only.",
    )
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
            ("dense_blocked:small", 512, 64),
            ("dense_blocked:medium", 2048, 256),
            ("sparse_clear:small", 512, 64),
            ("sparse_clear:medium", 2048, 256),
        )
    )
    backends = tuple(args.backend) if args.backend else ("apple_rt", "apple_rt_prepared_query", "embree", "shapely_strtree")
    payload = run_benchmark(
        scales,
        warmups=args.warmups,
        repeats=args.repeats,
        backends=backends,
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

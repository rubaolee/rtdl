from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples import rtdl_apple_rt_closest_hit


SCENARIOS = ("closest_hit", "visibility_count", "all")


def run_closest_hit() -> dict[str, Any]:
    rays, triangles = rtdl_apple_rt_closest_hit.make_scene()
    cpu_rows = rt.run_cpu_python_reference(
        rtdl_apple_rt_closest_hit.apple_rt_closest_hit_kernel,
        rays=rays,
        triangles=triangles,
    )
    result: dict[str, Any] = {
        "scenario": "closest_hit",
        "scope": "3D Ray3D/Triangle3D closest-hit through Apple Metal/MPS when available",
        "cpu_python_reference": rtdl_apple_rt_closest_hit._rows(cpu_rows),
    }
    try:
        result["apple_rt_probe"] = rt.apple_rt_context_probe()
        apple_rows = rt.run_apple_rt(
            rtdl_apple_rt_closest_hit.apple_rt_closest_hit_kernel,
            rays=rays,
            triangles=triangles,
        )
        result["apple_rt_available"] = True
        result["run_apple_rt"] = rtdl_apple_rt_closest_hit._rows(apple_rows)
        result["parity"] = rtdl_apple_rt_closest_hit._same_rows_approx(apple_rows, cpu_rows)
    except (FileNotFoundError, OSError, RuntimeError, NotImplementedError, ValueError) as exc:
        result["apple_rt_available"] = False
        result["apple_rt_error"] = str(exc).splitlines()[0]
    return result


def run_visibility_count() -> dict[str, Any]:
    triangles = (
        rt.Triangle(id=0, x0=1.0, y0=-0.5, x1=1.8, y1=-0.5, x2=1.8, y2=0.5),
        rt.Triangle(id=1, x0=1.0, y0=-0.5, x1=1.8, y1=0.5, x2=1.0, y2=0.5),
        rt.Triangle(id=2, x0=1.0, y0=2.0, x1=1.8, y1=2.0, x2=1.8, y2=2.8),
        rt.Triangle(id=3, x0=1.0, y0=2.0, x1=1.8, y1=2.8, x2=1.0, y2=2.8),
    )
    rays = (
        rt.Ray2D(id=0, ox=0.0, oy=0.0, dx=3.0, dy=0.0, tmax=1.0),
        rt.Ray2D(id=1, ox=0.0, oy=2.4, dx=3.0, dy=0.0, tmax=1.0),
        rt.Ray2D(id=2, ox=0.0, oy=4.0, dx=3.0, dy=0.0, tmax=1.0),
        rt.Ray2D(id=3, ox=0.0, oy=-2.0, dx=3.0, dy=0.0, tmax=1.0),
    )
    result: dict[str, Any] = {
        "scenario": "visibility_count",
        "scope": "prepared/prepacked Apple RT 2D scalar visibility-count path",
        "input": {"ray_count": len(rays), "triangle_count": len(triangles)},
    }
    try:
        packed_rays = rt.prepare_apple_rt_rays_2d(rays)
        with rt.prepare_apple_rt_ray_triangle_any_hit_2d(triangles) as prepared:
            blocked_count, profile = prepared.count_profile_packed(packed_rays)
        result.update(
            {
                "status": "ok",
                "output": {
                    "blocked_ray_count": blocked_count,
                    "clear_ray_count": len(rays) - blocked_count,
                },
                "profile": {
                    "native_total_seconds": profile["total_seconds"],
                    "dispatch_wait_seconds": profile["dispatch_wait_seconds"],
                    "hit_count": profile["hit_count"],
                },
            }
        )
    except Exception as exc:
        result.update({"status": "skipped", "reason": f"Apple RT unavailable: {exc}"})
    return result


def run_app(scenario: str = "all") -> dict[str, Any]:
    if scenario not in SCENARIOS:
        raise ValueError(f"unsupported scenario: {scenario}")

    sections: dict[str, Any] = {}
    if scenario in {"closest_hit", "all"}:
        sections["closest_hit"] = run_closest_hit()
    if scenario in {"visibility_count", "all"}:
        sections["visibility_count"] = run_visibility_count()
    return {
        "app": "apple_rt_demo",
        "scenario": scenario,
        "sections": sections,
        "unifies": [
            "examples/rtdl_apple_rt_closest_hit.py",
            "examples/rtdl_apple_rt_visibility_count.py",
        ],
        "honesty_boundary": "Unified Apple RT demo; hardware-backed support depends on macOS Apple Silicon and a rebuilt librtdl_apple_rt, and this is not a broad Apple speedup claim.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Unified Apple RT demo app.")
    parser.add_argument(
        "--scenario",
        default="all",
        choices=SCENARIOS,
        help="Run one Apple RT demo scenario or the complete unified app.",
    )
    args = parser.parse_args(argv)
    print(json.dumps(run_app(args.scenario), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

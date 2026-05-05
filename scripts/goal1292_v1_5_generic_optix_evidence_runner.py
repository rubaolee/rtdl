#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


GOAL = "Goal1292 v1.5 generic OptiX evidence runner"


def _git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "unknown"


def _make_ray_triangle_case(copies: int) -> tuple[tuple[rt.Ray2D, ...], tuple[rt.Triangle, ...]]:
    if copies <= 0:
        raise ValueError("copies must be positive")
    rays: list[rt.Ray2D] = []
    triangles: list[rt.Triangle] = []
    for copy_index in range(copies):
        y_offset = float(copy_index * 4)
        ray_id = copy_index * 2
        triangle_id = copy_index
        rays.append(rt.Ray2D(id=ray_id, ox=0.0, oy=y_offset + 0.25, dx=2.0, dy=0.0, tmax=1.0))
        rays.append(rt.Ray2D(id=ray_id + 1, ox=0.0, oy=y_offset + 2.0, dx=2.0, dy=0.0, tmax=1.0))
        triangles.append(
            rt.Triangle(
                id=triangle_id,
                x0=1.0,
                y0=y_offset,
                x1=1.0,
                y1=y_offset + 1.0,
                x2=1.2,
                y2=y_offset + 0.5,
            )
        )
    return tuple(rays), tuple(triangles)


def _run_direct_backend(
    backend: str,
    rays: tuple[rt.Ray2D, ...],
    triangles: tuple[rt.Triangle, ...],
) -> dict[str, Any]:
    start = time.perf_counter()
    try:
        result = rt.run_generic_ray_triangle_any_hit_count(
            rays,
            triangles,
            backend=backend,
            include_rows=True,
        )
    except Exception as exc:  # pragma: no cover - depends on host backend availability.
        return {
            "backend": backend,
            "status": "failed",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "elapsed_sec": time.perf_counter() - start,
        }
    return {
        "backend": backend,
        "status": "ok",
        "elapsed_sec": time.perf_counter() - start,
        "row_count": int(result["row_count"]),
        "hit_count": int(result["hit_count"]),
        "rows": list(result.get("rows", ())),
        "claim_boundary": result["claim_boundary"],
    }


def _run_prepared_optix(
    rays: tuple[rt.Ray2D, ...],
    triangles: tuple[rt.Triangle, ...],
    query_repeats: int,
) -> dict[str, Any]:
    start = time.perf_counter()
    try:
        result = rt.run_generic_prepared_ray_triangle_any_hit_count(
            triangles=triangles,
            rays=rays,
            backend="optix",
            query_repeats=query_repeats,
        )
    except Exception as exc:  # pragma: no cover - depends on host backend availability.
        return {
            "backend": "optix",
            "status": "failed",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "elapsed_sec": time.perf_counter() - start,
            "query_repeats": query_repeats,
        }
    return {
        "backend": "optix",
        "status": "ok",
        "elapsed_sec": time.perf_counter() - start,
        "query_repeats": int(result["query_repeats"]),
        "hit_count": int(result["hit_count"]),
        "run_phases": result["run_phases"],
        "claim_boundary": result["claim_boundary"],
    }


def _parity(cpu: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    if cpu.get("status") != "ok" or candidate.get("status") != "ok":
        return {"status": "not_comparable"}
    return {
        "status": "ok" if cpu.get("rows") == candidate.get("rows") else "mismatch",
        "hit_count_matches": cpu.get("hit_count") == candidate.get("hit_count"),
        "rows_match": cpu.get("rows") == candidate.get("rows"),
    }


def build_payload(
    *,
    copies: int,
    backends: tuple[str, ...],
    query_repeats: int,
    skip_prepared: bool,
) -> dict[str, Any]:
    rays, triangles = _make_ray_triangle_case(copies)
    direct = {backend: _run_direct_backend(backend, rays, triangles) for backend in backends}
    if "cpu" not in direct:
        direct["cpu"] = _run_direct_backend("cpu", rays, triangles)

    prepared = None if skip_prepared else _run_prepared_optix(rays, triangles, query_repeats)
    parity = {
        backend: _parity(direct["cpu"], result)
        for backend, result in direct.items()
        if backend != "cpu"
    }
    if prepared is not None and prepared.get("status") == "ok" and direct["cpu"].get("status") == "ok":
        parity["optix_prepared_count"] = {
            "status": "ok" if prepared["hit_count"] == direct["cpu"]["hit_count"] else "mismatch",
            "hit_count_matches": prepared["hit_count"] == direct["cpu"]["hit_count"],
        }

    return {
        "goal": GOAL,
        "source_commit": _git_head(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "fixture": {
            "copies": copies,
            "ray_count": len(rays),
            "triangle_count": len(triangles),
            "expected_hit_count": copies,
        },
        "active_backends": ["embree", "optix"],
        "frozen_backends_before_v2_1": ["vulkan", "hiprt", "apple_rt"],
        "direct_anyhit_count": direct,
        "prepared_optix_anyhit_count": prepared,
        "parity": parity,
        "public_wording_authorized": False,
        "boundary": (
            "v1.5 internal generic raw ray/triangle ANY_HIT plus COUNT_HITS evidence only; "
            "no public speedup wording, app-class claim, or Vulkan/HIPRT/Apple RT work is authorized."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run v1.5 generic OptiX primitive evidence.")
    parser.add_argument("--copies", type=int, default=1000)
    parser.add_argument("--query-repeats", type=int, default=100)
    parser.add_argument("--backend", action="append", choices=("cpu", "embree", "optix"))
    parser.add_argument("--skip-prepared", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    backends = tuple(args.backend or ("cpu", "embree", "optix"))
    payload = build_payload(
        copies=args.copies,
        backends=backends,
        query_repeats=args.query_repeats,
        skip_prepared=args.skip_prepared,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

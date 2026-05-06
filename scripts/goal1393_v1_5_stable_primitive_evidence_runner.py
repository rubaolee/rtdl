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


GOAL = "Goal1393 v1.5 stable primitive evidence runner"
STABLE_PRIMITIVES = (
    "ANY_HIT",
    "COUNT_HITS",
    "REDUCE_FLOAT(MIN)",
    "REDUCE_FLOAT(MAX)",
    "REDUCE_FLOAT(SUM)",
    "REDUCE_INT(COUNT)",
    "REDUCE_INT(SUM)",
)


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


def _command_output(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.stdout.strip()


def _timed(callable_obj, *, repeats: int = 1) -> tuple[Any, list[float]]:
    timings: list[float] = []
    result = None
    for _ in range(repeats):
        start = time.perf_counter()
        result = callable_obj()
        timings.append(time.perf_counter() - start)
    return result, timings


def _timing_summary(timings: list[float]) -> dict[str, Any]:
    if not timings:
        return {"repeats": 0}
    ordered = sorted(timings)
    return {
        "repeats": len(timings),
        "first_sec": timings[0],
        "min_sec": ordered[0],
        "median_sec": ordered[len(ordered) // 2],
        "max_sec": ordered[-1],
        "total_sec": sum(timings),
    }


def _make_ray_triangle_case(copies: int) -> tuple[tuple[rt.Ray2D, ...], tuple[rt.Triangle, ...]]:
    if copies <= 0:
        raise ValueError("copies must be positive")
    rays: list[rt.Ray2D] = []
    triangles: list[rt.Triangle] = []
    for copy_index in range(copies):
        y_offset = float(copy_index * 4)
        ray_id = copy_index * 2
        rays.append(rt.Ray2D(id=ray_id, ox=0.0, oy=y_offset + 0.25, dx=2.0, dy=0.0, tmax=1.0))
        rays.append(rt.Ray2D(id=ray_id + 1, ox=0.0, oy=y_offset + 2.0, dx=2.0, dy=0.0, tmax=1.0))
        triangles.append(
            rt.Triangle(
                id=copy_index,
                x0=1.0,
                y0=y_offset,
                x1=1.0,
                y1=y_offset + 1.0,
                x2=1.2,
                y2=y_offset + 0.5,
            )
        )
    return tuple(rays), tuple(triangles)


def _row_digest(rows: Any) -> dict[str, Any]:
    normalized = tuple(dict(row) for row in rows)
    encoded = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return {
        "row_count": len(normalized),
        "json_length": len(encoded),
        "rows": normalized if len(normalized) <= 16 else normalized[:8] + normalized[-8:],
    }


def _scalar_reduction_evidence(repeats: int) -> dict[str, Any]:
    rows = (
        {"any_hit": 1, "payload": 3, "score": 4.0},
        {"any_hit": 0, "payload": -1, "score": 2.5},
        {"any_hit": True, "payload": 5, "score": 8.25},
        {"any_hit": 1, "payload": 4, "score": -0.75},
    )
    cases = (
        ("COUNT_HITS", None, 3),
        ("REDUCE_INT(COUNT)", None, 4),
        ("REDUCE_INT(SUM)", "payload", 11),
        ("REDUCE_FLOAT(MIN)", "score", -0.75),
        ("REDUCE_FLOAT(MAX)", "score", 8.25),
        ("REDUCE_FLOAT(SUM)", "score", 14.0),
    )
    evidence: dict[str, Any] = {}
    for primitive, value_field, expected in cases:
        def run_case():
            return rt.run_generic_scalar_reduction(
                rows,
                summary_primitive=primitive,
                value_field=value_field,
            )

        result, timings = _timed(run_case, repeats=repeats)
        evidence[primitive] = {
            "status": "ok" if result["result"] == expected else "mismatch",
            "expected": expected,
            "result": result,
            "timing": _timing_summary(timings),
        }
    return evidence


def _run_anyhit_backend(
    backend: str,
    rays: tuple[rt.Ray2D, ...],
    triangles: tuple[rt.Triangle, ...],
    repeats: int,
) -> dict[str, Any]:
    def run_case():
        return rt.run_generic_ray_triangle_any_hit_count(
            rays,
            triangles,
            backend=backend,
            include_rows=True,
        )

    try:
        result, timings = _timed(run_case, repeats=repeats)
    except Exception as exc:  # pragma: no cover - backend availability is host-specific.
        return {
            "backend": backend,
            "status": "failed",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
    return {
        "backend": backend,
        "status": "ok",
        "primitive": result["primitive"],
        "summary_primitive": result["summary_primitive"],
        "row_count": int(result["row_count"]),
        "hit_count": int(result["hit_count"]),
        "rows": _row_digest(result["rows"]),
        "scalar_reduction": result["scalar_reduction"],
        "timing": _timing_summary(timings),
        "claim_boundary": result["claim_boundary"],
    }


def _prepared_optix_anyhit_count(
    rays: tuple[rt.Ray2D, ...],
    triangles: tuple[rt.Triangle, ...],
    query_repeats: int,
    *,
    skip: bool,
) -> dict[str, Any] | None:
    if skip:
        return None
    try:
        result = rt.run_generic_prepared_ray_triangle_any_hit_count(
            triangles=triangles,
            rays=rays,
            backend="optix",
            query_repeats=query_repeats,
        )
    except Exception as exc:  # pragma: no cover - backend availability is host-specific.
        return {
            "backend": "optix",
            "status": "failed",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "query_repeats": query_repeats,
        }
    return {
        "backend": "optix",
        "status": "ok",
        "primitive": result["primitive"],
        "summary_primitive": result["summary_primitive"],
        "hit_count": int(result["hit_count"]),
        "query_repeats": int(result["query_repeats"]),
        "run_phases": result["run_phases"],
        "claim_boundary": result["claim_boundary"],
    }


def _parity(cpu: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    if cpu.get("status") != "ok" or candidate.get("status") != "ok":
        return {"status": "not_comparable"}
    return {
        "status": "ok" if cpu["hit_count"] == candidate["hit_count"] else "mismatch",
        "hit_count_matches": cpu["hit_count"] == candidate["hit_count"],
        "row_count_matches": cpu["row_count"] == candidate["row_count"],
    }


def build_payload(
    *,
    copies: int,
    direct_repeats: int,
    scalar_repeats: int,
    prepared_query_repeats: int,
    backends: tuple[str, ...],
    skip_prepared: bool,
) -> dict[str, Any]:
    rays, triangles = _make_ray_triangle_case(copies)
    direct = {
        backend: _run_anyhit_backend(backend, rays, triangles, direct_repeats)
        for backend in backends
    }
    if "cpu" not in direct:
        direct["cpu"] = _run_anyhit_backend("cpu", rays, triangles, direct_repeats)
    prepared = _prepared_optix_anyhit_count(
        rays,
        triangles,
        prepared_query_repeats,
        skip=skip_prepared,
    )
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
        "tool_versions": {
            "git": _command_output(["git", "--version"]),
            "python": _command_output([sys.executable, "--version"]),
        },
        "stable_primitives": STABLE_PRIMITIVES,
        "active_backends": ["embree", "optix"],
        "frozen_backends_before_v2_1": ["vulkan", "hiprt", "apple_rt"],
        "fixture": {
            "copies": copies,
            "ray_count": len(rays),
            "triangle_count": len(triangles),
            "expected_hit_count": copies,
        },
        "scalar_reductions": _scalar_reduction_evidence(scalar_repeats),
        "direct_anyhit_count": direct,
        "prepared_optix_anyhit_count": prepared,
        "parity": parity,
        "public_wording_authorized": False,
        "boundary": (
            "Internal v1.5 exact-subpath evidence for stable generic primitives only; "
            "no public v1.5 release wording, whole-app speedup wording, broad NVIDIA claim, "
            "package/install claim, or COLLECT_K_BOUNDED stable promotion is authorized by this artifact."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run v1.5 stable primitive evidence.")
    parser.add_argument("--copies", type=int, default=256)
    parser.add_argument("--direct-repeats", type=int, default=5)
    parser.add_argument("--scalar-repeats", type=int, default=100)
    parser.add_argument("--prepared-query-repeats", type=int, default=100)
    parser.add_argument("--backend", action="append", choices=("cpu", "embree", "optix"))
    parser.add_argument("--skip-prepared", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    payload = build_payload(
        copies=args.copies,
        direct_repeats=args.direct_repeats,
        scalar_repeats=args.scalar_repeats,
        prepared_query_repeats=args.prepared_query_repeats,
        backends=tuple(args.backend or ("cpu", "embree", "optix")),
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

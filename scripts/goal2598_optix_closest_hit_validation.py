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

from examples.v2_0.learner_apps.gpu_rmq import rtdl_gpu_rmq_learner_app as gpu_rmq
from rtdsl.generic_primitives import run_generic_ray_triangle_closest_hit
from rtdsl.reference import Ray3D
from rtdsl.reference import Triangle3D
from rtdsl.reference import ray_triangle_closest_hit_cpu


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def _closest_hit_fixture() -> tuple[tuple[Ray3D, ...], tuple[Triangle3D, ...]]:
    triangles = (
        Triangle3D(10, 5.0, 0.0, 0.0, 5.0, 1.0, 0.0, 5.0, 0.0, 1.0),
        Triangle3D(20, 2.0, 0.0, 0.0, 2.0, 1.0, 0.0, 2.0, 0.0, 1.0),
        Triangle3D(30, 4.0, 2.0, 2.0, 4.0, 3.0, 2.0, 4.0, 2.0, 3.0),
    )
    rays = (
        Ray3D(1, 0.0, 0.25, 0.25, 1.0, 0.0, 0.0, 10.0),
        Ray3D(2, 0.0, 2.25, 2.25, 1.0, 0.0, 0.0, 10.0),
        Ray3D(3, 0.0, 4.00, 4.00, 1.0, 0.0, 0.0, 10.0),
        Ray3D(4, 3.0, 0.25, 0.25, 1.0, 0.0, 0.0, 1.0),
    )
    return rays, triangles


def _rows_match(
    expected: tuple[dict[str, float | int], ...],
    actual: tuple[dict[str, float | int], ...],
    *,
    tolerance: float,
) -> bool:
    if len(expected) != len(actual):
        return False
    expected_by_ray = {int(row["ray_id"]): row for row in expected}
    actual_by_ray = {int(row["ray_id"]): row for row in actual}
    if set(expected_by_ray) != set(actual_by_ray):
        return False
    for ray_id, expected_row in expected_by_ray.items():
        actual_row = actual_by_ray[ray_id]
        if int(expected_row["triangle_id"]) != int(actual_row["triangle_id"]):
            return False
        if abs(float(expected_row["t"]) - float(actual_row["t"])) > tolerance:
            return False
    return True


def run_closest_hit_check(backend: str, tolerance: float) -> dict[str, Any]:
    rays, triangles = _closest_hit_fixture()
    expected = ray_triangle_closest_hit_cpu(rays, triangles)
    start = time.perf_counter()
    actual = run_generic_ray_triangle_closest_hit(rays, triangles, backend=backend)
    elapsed = time.perf_counter() - start
    return {
        "backend": backend,
        "fixture": "goal2598_no_tie_ray_triangle_3d",
        "expected_rows": expected,
        "actual_rows": actual,
        "matches_cpu_reference": _rows_match(expected, actual, tolerance=tolerance),
        "elapsed_sec": elapsed,
        "tolerance": tolerance,
    }


def run_gpu_rmq_check(args: argparse.Namespace) -> dict[str, Any]:
    return gpu_rmq.run_app(
        "paper_rt_lowering_reference",
        dataset=args.dataset,
        value_count=args.value_count,
        query_count=args.query_count,
        seed=args.seed,
        max_width=args.max_width,
        block_size=args.block_size,
        sample=False,
        rt_backend=args.backend,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate generic OptiX 3-D closest-hit wiring.")
    parser.add_argument("--backend", choices=("cpu", "embree", "optix"), default="optix")
    parser.add_argument("--tolerance", type=float, default=1.0e-4)
    parser.add_argument("--skip-gpu-rmq", action="store_true")
    parser.add_argument("--dataset", default="repeated")
    parser.add_argument("--value-count", type=int, default=4096)
    parser.add_argument("--query-count", type=int, default=1024)
    parser.add_argument("--max-width", type=int, default=256)
    parser.add_argument("--block-size", type=int, default=64)
    parser.add_argument("--seed", type=int, default=123)
    args = parser.parse_args(argv)

    payload: dict[str, Any] = {
        "script": "goal2598_optix_closest_hit_validation",
        "git_commit": _git_commit(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "backend": args.backend,
        "closest_hit": run_closest_hit_check(args.backend, args.tolerance),
        "claim_boundary": {
            "source_wired": True,
            "optix_ready_requires_pod_validation": True,
            "this_run_is_optix_validation": args.backend == "optix",
            "public_speedup_claim_authorized": False,
        },
    }
    if not args.skip_gpu_rmq:
        payload["gpu_rmq"] = run_gpu_rmq_check(args)
    payload["overall_matches_cpu_reference"] = bool(
        payload["closest_hit"]["matches_cpu_reference"]
        and (
            args.skip_gpu_rmq
            or payload.get("gpu_rmq", {}).get("matches_cpu_reference", False)
        )
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["overall_matches_cpu_reference"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

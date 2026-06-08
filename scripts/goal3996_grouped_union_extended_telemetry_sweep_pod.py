#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import platform
import statistics
import subprocess
import sys
import time
from typing import Any

import rtdsl as rt
from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    make_rt_dbscan_points,
)


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=_repo_root(),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return ""


def _nvidia_smi() -> str:
    try:
        return subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return ""


def _sync(cp: Any) -> None:
    cp.cuda.Stream.null.synchronize()


def _timed(cp: Any, fn) -> tuple[float, Any]:
    _sync(cp)
    start = time.perf_counter()
    result = fn()
    _sync(cp)
    return time.perf_counter() - start, result


def _median(values: list[float]) -> float:
    return float(statistics.median(values)) if values else 0.0


def _run_variant(
    prepared: Any,
    *,
    same_root_culling: bool,
    direct_side_effect: bool,
    repeats: int,
) -> dict[str, Any]:
    cp = prepared.cupy
    samples: list[dict[str, Any]] = []
    for repeat in range(repeats):
        parent = cp.arange(prepared.point_count, dtype=cp.int32)
        telemetry = cp.zeros((8,), dtype=cp.uint64)
        elapsed_sec, result = _timed(
            cp,
            lambda: prepared.prepared_native.apply_device_grouped_union_all_self(
                radius=prepared.radius,
                parent_out=parent,
                telemetry_out=telemetry,
                same_root_culling=same_root_culling,
                direct_side_effect=direct_side_effect,
            ),
        )
        samples.append(
            {
                "repeat": repeat,
                "elapsed_sec": elapsed_sec,
                "native_elapsed_sec": float(result["metadata"].get("native_elapsed_sec", 0.0)),
                "metadata": result["metadata"],
                "telemetry": [int(value) for value in telemetry.get().tolist()],
            }
        )
    elapsed = [float(sample["elapsed_sec"]) for sample in samples]
    native = [float(sample["native_elapsed_sec"]) for sample in samples]
    telemetry_ref = samples[-1]["telemetry"] if samples else [0] * 8
    return {
        "same_root_culling": same_root_culling,
        "direct_side_effect": direct_side_effect,
        "repeats": repeats,
        "median_elapsed_sec": _median(elapsed),
        "median_native_elapsed_sec": _median(native),
        "last_telemetry": telemetry_ref,
        "last_metadata": samples[-1]["metadata"] if samples else {},
        "samples": samples,
    }


def _run_point_count(
    *,
    point_count: int,
    radius: float,
    seed: int,
    repeats: int,
    profile: str,
) -> dict[str, Any]:
    points = make_rt_dbscan_points(profile, point_count=point_count, seed=seed)
    with rt.prepare_optix_cupy_radius_graph_grouped_stream_continuation_3d(
        points,
        radius=radius,
        partner="cupy",
    ) as prepared:
        cp = prepared.cupy
        warm_parent = cp.arange(prepared.point_count, dtype=cp.int32)
        _timed(
            cp,
            lambda: prepared.prepared_native.apply_device_grouped_union_all_self(
                radius=prepared.radius,
                parent_out=warm_parent,
                same_root_culling=True,
                direct_side_effect=False,
            ),
        )
        variants = []
        for same_root_culling, direct_side_effect in (
            (True, False),
            (False, False),
            (True, True),
            (False, True),
        ):
            label = (
                f"same_root_{'on' if same_root_culling else 'off'}_"
                f"direct_{'on' if direct_side_effect else 'off'}"
            )
            print(
                f"[goal3996] point_count={point_count} variant={label} repeats={repeats}",
                flush=True,
            )
            variant = _run_variant(
                prepared,
                same_root_culling=same_root_culling,
                direct_side_effect=direct_side_effect,
                repeats=repeats,
            )
            variant["label"] = label
            variants.append(variant)
    return {
        "point_count": point_count,
        "radius": radius,
        "seed": seed,
        "profile": profile,
        "variants": variants,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Goal3996 grouped-union extended telemetry mode sweep."
    )
    parser.add_argument("--point-counts", default="4096,16384,65536")
    parser.add_argument("--radius", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=20260608)
    parser.add_argument("--profile", default="clustered3d")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("docs/reports/goal3996_grouped_union_extended_telemetry_sweep_pod.json"),
    )
    args = parser.parse_args()

    point_counts = [int(part) for part in args.point_counts.split(",") if part.strip()]
    if not point_counts:
        raise ValueError("--point-counts must contain at least one count")
    if args.repeats <= 0:
        raise ValueError("--repeats must be positive")

    started = time.perf_counter()
    rows = []
    for point_count in point_counts:
        print(f"[goal3996] start point_count={point_count}", flush=True)
        rows.append(
            _run_point_count(
                point_count=point_count,
                radius=args.radius,
                seed=args.seed,
                repeats=args.repeats,
                profile=args.profile,
            )
        )
        print(f"[goal3996] done point_count={point_count}", flush=True)

    payload = {
        "goal": "Goal3996",
        "status": "pass",
        "source_commit": _git_head(),
        "host": platform.node(),
        "platform": platform.platform(),
        "gpu": _nvidia_smi(),
        "elapsed_sec": time.perf_counter() - started,
        "point_counts": point_counts,
        "radius": args.radius,
        "profile": args.profile,
        "repeats": args.repeats,
        "rows": rows,
        "claim_boundary": {
            "performance_claim_authorized": False,
            "release_authorized": False,
            "telemetry_is_diagnostic": True,
            "dbscan_native_abi_added": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[goal3996] failed: {exc}", file=sys.stderr, flush=True)
        raise

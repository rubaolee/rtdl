#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    _load_rayjoin_case,
)


def _median(values: list[float]) -> float | None:
    return float(statistics.median(values)) if values else None


def _repo_state() -> dict[str, object]:
    def run(args: list[str]) -> str:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()

    try:
        commit = run(["git", "rev-parse", "HEAD"])
    except Exception:
        commit = "unknown"
    try:
        status = run(["git", "status", "--short"])
    except Exception:
        status = ""
    return {
        "commit": commit,
        "source_dirty": [line for line in status.splitlines() if line.strip()],
    }


def _timed_call(fn) -> tuple[int, float, dict[str, object] | None]:
    start = time.perf_counter()
    count = int(fn())
    elapsed = time.perf_counter() - start
    return count, elapsed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare exact and fast device-filtered prepared closed-shape membership counts."
    )
    parser.add_argument(
        "--dataset",
        default="/root/rtdl_goal3151/data/rayjoin_public_cdb/br_county_start0_count512.cdb",
        help="PIP CDB dataset path.",
    )
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--repeat", type=int, default=9)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    print(f"[goal3252] loading dataset: {args.dataset}", flush=True)
    case = _load_rayjoin_case("pip", args.dataset)
    points = tuple(case.inputs["points"])
    shapes = tuple(case.inputs["polygons"])
    print(f"[goal3252] loaded points={len(points)} shapes={len(shapes)}", flush=True)

    from rtdsl.optix_runtime import pack_points
    from rtdsl.optix_runtime import pack_polygons
    from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

    phase_sec: dict[str, float] = {}
    start = time.perf_counter()
    packed_points = pack_points(records=points, dimension=2)
    phase_sec["pack_points_sec"] = time.perf_counter() - start

    start = time.perf_counter()
    packed_shapes = pack_polygons(records=shapes)
    phase_sec["pack_shapes_sec"] = time.perf_counter() - start

    print("[goal3252] preparing closed-shape scene", flush=True)
    start = time.perf_counter()
    prepared = prepare_point_closed_shape_membership_2d_optix(packed_shapes)
    phase_sec["prepare_sec"] = time.perf_counter() - start

    exact_samples: list[float] = []
    exact_counts: list[int] = []
    exact_phases: list[dict[str, object] | None] = []
    device_samples: list[float] = []
    device_counts: list[int] = []
    device_phases: list[dict[str, object] | None] = []
    try:
        for index in range(args.warmup):
            exact = prepared.count(packed_points)
            device = prepared.count_device_filtered(packed_points)
            print(
                f"[goal3252] warmup {index + 1}/{args.warmup}: exact={exact} device_filtered={device}",
                flush=True,
            )

        for index in range(args.repeat):
            start = time.perf_counter()
            exact = int(prepared.count(packed_points))
            exact_elapsed = time.perf_counter() - start
            exact_phase = prepared.last_phase_timings()

            start = time.perf_counter()
            device = int(prepared.count_device_filtered(packed_points))
            device_elapsed = time.perf_counter() - start
            device_phase = prepared.last_phase_timings()

            exact_counts.append(exact)
            exact_samples.append(exact_elapsed)
            exact_phases.append(exact_phase)
            device_counts.append(device)
            device_samples.append(device_elapsed)
            device_phases.append(device_phase)
            print(
                f"[goal3252] repeat {index + 1}/{args.repeat}: "
                f"exact={exact} {exact_elapsed * 1000.0:.6f} ms; "
                f"device_filtered={device} {device_elapsed * 1000.0:.6f} ms",
                flush=True,
            )
    finally:
        prepared.close()

    exact_median = _median(exact_samples)
    device_median = _median(device_samples)
    payload = {
        "goal": 3252,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repo_state": _repo_state(),
        "dataset": args.dataset,
        "inputs": {
            "point_count": len(points),
            "shape_count": len(shapes),
        },
        "phase_sec": phase_sec,
        "exact_count": {
            "counts": exact_counts,
            "median_sec": exact_median,
            "phase_samples": exact_phases,
        },
        "device_filtered_count": {
            "counts": device_counts,
            "median_sec": device_median,
            "phase_samples": device_phases,
        },
        "comparison": {
            "all_counts_match": exact_counts == device_counts,
            "speedup_over_exact_count": (
                (exact_median / device_median) if exact_median and device_median else None
            ),
            "device_filtered_is_exact_authority": False,
            "requires_exact_oracle_validation_per_workload": True,
        },
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "rayjoin_paper_reproduction_claim_authorized": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3252] wrote {args.output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

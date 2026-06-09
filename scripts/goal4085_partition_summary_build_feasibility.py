from __future__ import annotations

import argparse
import json
import pathlib
import platform
import statistics
import subprocess
import time
from typing import Any

import rtdsl as rt
from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    make_rt_dbscan_points,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal4085_partition_summary_build_feasibility_pod.json"
PROFILE_RADII = {
    "clustered3d": 0.055,
    "road3d": 0.030,
    "ngsim_dense": 0.012,
}


def _source_commit() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


def _nvidia_smi() -> str:
    try:
        return subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return ""


def _summary(values: list[float]) -> dict[str, float]:
    return {
        "min_sec": min(values),
        "median_sec": statistics.median(values),
        "mean_sec": statistics.fmean(values),
        "max_sec": max(values),
    }


def _status_counts(metadata: dict[str, Any]) -> dict[str, int]:
    raw = metadata.get("status_counts")
    return {str(key): int(value) for key, value in dict(raw or {}).items()}


def _run_profile(
    *,
    profile: str,
    point_count: int,
    seed: int,
    cell_factor: float,
    pair_enumeration: str,
    repeat: int,
    warmup: int,
) -> dict[str, Any]:
    import cupy

    radius = PROFILE_RADII[profile]
    points = make_rt_dbscan_points(profile, point_count=point_count, seed=seed)
    samples: list[dict[str, Any]] = []
    total_runs = warmup + repeat
    for run_index in range(total_runs):
        measured = run_index >= warmup
        label = "MEASURE" if measured else "WARMUP"
        print(
            f"PROFILE_{label} {profile} point_count={point_count} run={run_index}",
            flush=True,
        )
        cupy.cuda.Stream.null.synchronize()
        start = time.perf_counter()
        result = rt.build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
            points,
            radius=radius,
            cell_factor=cell_factor,
            pair_enumeration=pair_enumeration,
        )
        cupy.cuda.Stream.null.synchronize()
        elapsed = time.perf_counter() - start
        metadata = dict(result["metadata"])
        digest = {
            "run_index": run_index,
            "measured": measured,
            "partition_summary_build_sec": elapsed,
            "status": metadata.get("reference"),
            "partition_count": int(metadata["partition_count"]),
            "pair_count": int(metadata["pair_count"]),
            "visible_pair_count": int(metadata["visible_pair_count"]),
            "pair_capacity": int(metadata["pair_capacity"]),
            "pair_capacity_source": metadata.get("pair_capacity_source"),
            "pair_enumeration": metadata.get("pair_enumeration"),
            "overflow": bool(metadata["overflow"]),
            "complete_candidate_coverage": bool(metadata["complete_candidate_coverage"]),
            "status_counts": _status_counts(metadata),
            "device_pair_enumeration_used": bool(metadata.get("device_pair_enumeration_used")),
            "device_pair_count_probe_used": bool(metadata.get("device_pair_count_probe_used")),
            "release_authorized": bool(metadata.get("release_authorized")),
            "public_speedup_claim_authorized": bool(metadata.get("public_speedup_claim_authorized")),
            "rt_core_speedup_claim_authorized": bool(metadata.get("rt_core_speedup_claim_authorized")),
            "whole_app_speedup_claim_authorized": bool(metadata.get("whole_app_speedup_claim_authorized")),
            "true_zero_copy_claim_authorized": bool(metadata.get("true_zero_copy_claim_authorized")),
            "native_abi_added": bool(metadata.get("native_abi_added")),
        }
        print(
            "PROFILE_SAMPLE "
            + json.dumps(
                {
                    "profile": profile,
                    "run_index": run_index,
                    "measured": measured,
                    "partition_summary_build_sec": elapsed,
                    "partition_count": digest["partition_count"],
                    "pair_count": digest["pair_count"],
                    "pair_capacity": digest["pair_capacity"],
                    "status_counts": digest["status_counts"],
                },
                sort_keys=True,
            ),
            flush=True,
        )
        samples.append(digest)
    measured_samples = [sample for sample in samples if sample["measured"]]
    build_times = [float(sample["partition_summary_build_sec"]) for sample in measured_samples]
    if not build_times:
        raise ValueError("repeat must produce at least one measured sample")
    reference = measured_samples[-1]
    return {
        "profile": profile,
        "point_count": point_count,
        "radius": radius,
        "cell_factor": cell_factor,
        "pair_enumeration": pair_enumeration,
        "repeat": repeat,
        "warmup": warmup,
        "partition_summary_build_sec": _summary(build_times),
        "partition_count": reference["partition_count"],
        "pair_count": reference["pair_count"],
        "visible_pair_count": reference["visible_pair_count"],
        "pair_capacity": reference["pair_capacity"],
        "pair_capacity_source": reference["pair_capacity_source"],
        "overflow": reference["overflow"],
        "complete_candidate_coverage": reference["complete_candidate_coverage"],
        "status_counts": reference["status_counts"],
        "device_pair_enumeration_used": reference["device_pair_enumeration_used"],
        "device_pair_count_probe_used": reference["device_pair_count_probe_used"],
        "samples": samples,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "native_abi_added": False,
    }


def run(
    *,
    output: pathlib.Path,
    profiles: tuple[str, ...],
    point_count: int,
    seed: int,
    cell_factor: float,
    pair_enumeration: str,
    repeat: int,
    warmup: int,
) -> dict[str, Any]:
    rows = [
        _run_profile(
            profile=profile,
            point_count=point_count,
            seed=seed,
            cell_factor=cell_factor,
            pair_enumeration=pair_enumeration,
            repeat=repeat,
            warmup=warmup,
        )
        for profile in profiles
    ]
    payload = {
        "goal": "Goal4085",
        "schema": "rtdl.goal4085.partition_summary_build_feasibility.v1",
        "source_commit": _source_commit(),
        "host": platform.node(),
        "platform": platform.platform(),
        "gpu": _nvidia_smi(),
        "profiles": profiles,
        "point_count": point_count,
        "seed": seed,
        "cell_factor": cell_factor,
        "pair_enumeration": pair_enumeration,
        "repeat": repeat,
        "warmup": warmup,
        "rows": rows,
        "claim_boundary": (
            "Internal partition-summary build feasibility evidence only. It does not promote "
            "partition_convergence_hybrid, authorize release, public speedup, broad RT-core, "
            "whole-app, paper-reproduction, hidden-dispatch, automatic partner selection, "
            "app-specific engine logic, native ABI addition, or true-zero-copy claims."
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "native_abi_added": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--profiles", default="clustered3d,road3d,ngsim_dense")
    parser.add_argument("--point-count", type=int, default=65536)
    parser.add_argument("--seed", type=int, default=20260519)
    parser.add_argument("--cell-factor", type=float, default=0.125)
    parser.add_argument("--pair-enumeration", default="device_count_then_emit")
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--warmup", type=int, default=1)
    args = parser.parse_args()
    profiles = tuple(part.strip() for part in args.profiles.split(",") if part.strip())
    unknown = tuple(profile for profile in profiles if profile not in PROFILE_RADII)
    if unknown:
        raise ValueError(f"unknown profiles: {unknown}")
    payload = run(
        output=args.output,
        profiles=profiles,
        point_count=args.point_count,
        seed=args.seed,
        cell_factor=args.cell_factor,
        pair_enumeration=args.pair_enumeration,
        repeat=args.repeat,
        warmup=args.warmup,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

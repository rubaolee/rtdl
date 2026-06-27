from __future__ import annotations

import argparse
import json
import math
import pathlib
import platform
import statistics
import subprocess
import time
from typing import Any

import rtdsl as rt
from examples.benchmark_apps.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    make_rt_dbscan_points,
)
from scripts.goal4085_partition_summary_build_feasibility import PROFILE_RADII


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal4087_prepared_partition_summary_reuse_threshold_pod.json"

CURRENT_RECOMMENDED_REFERENCE_SEC = {
    "clustered3d": 0.093321,
    "road3d": 0.036245,
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
    if not values:
        return {"min_sec": math.nan, "median_sec": math.nan, "mean_sec": math.nan, "max_sec": math.nan}
    return {
        "min_sec": min(values),
        "median_sec": statistics.median(values),
        "mean_sec": statistics.fmean(values),
        "max_sec": max(values),
    }


def _status_counts(metadata: dict[str, Any]) -> dict[str, int]:
    return {str(key): int(value) for key, value in dict(metadata.get("status_counts") or {}).items()}


def _break_even_runs(*, prepare_sec: float, replay_sec: float, reference_sec: float | None) -> float | None:
    if reference_sec is None or replay_sec >= reference_sec:
        return None
    return prepare_sec / max(reference_sec - replay_sec, 1.0e-12)


def _run_profile(
    *,
    profile: str,
    point_count: int,
    seed: int,
    cell_factor: float,
    pair_enumeration: str,
    signature_runs: int,
    warmup: int,
) -> dict[str, Any]:
    import cupy

    radius = PROFILE_RADII[profile]
    points = make_rt_dbscan_points(profile, point_count=point_count, seed=seed)
    print(
        f"PROFILE_PREPARE_START {profile} point_count={point_count} radius={radius} cell_factor={cell_factor}",
        flush=True,
    )
    cupy.cuda.Stream.null.synchronize()
    prepare_start = time.perf_counter()
    prepared = rt.prepare_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
        points,
        radius=radius,
        cell_factor=cell_factor,
        pair_enumeration=pair_enumeration,
        validate_summary_same_contract=False,
    )
    cupy.cuda.Stream.null.synchronize()
    prepare_sec = time.perf_counter() - prepare_start
    prepared_metadata = prepared.to_metadata()
    print(
        "PROFILE_PREPARE_DONE "
        + json.dumps(
            {
                "profile": profile,
                "prepare_sec": prepare_sec,
                "partition_count": prepared_metadata["partition_summary_digest"]["partition_count"],
                "pair_count": prepared_metadata["partition_summary_digest"]["pair_count"],
                "status_counts": prepared_metadata["partition_summary_digest"]["status_counts"],
            },
            sort_keys=True,
        ),
        flush=True,
    )

    replay_samples: list[dict[str, Any]] = []
    total_runs = warmup + signature_runs
    expected_signature: list[int] | None = None
    for run_index in range(total_runs):
        measured = run_index >= warmup
        label = "MEASURE" if measured else "WARMUP"
        print(f"PROFILE_SIGNATURE_{label}_START {profile} run={run_index}", flush=True)
        cupy.cuda.Stream.null.synchronize()
        start = time.perf_counter()
        result = rt.run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_preview_3d(
            prepared,
            validate_summary_same_contract=False,
        )
        cupy.cuda.Stream.null.synchronize()
        elapsed = time.perf_counter() - start
        metadata = dict(result["metadata"])
        signature = [int(value) for value in result["columns"]["component_size_signature"]]
        if expected_signature is None:
            expected_signature = signature
        elif signature != expected_signature:
            raise RuntimeError(f"component signature mismatch for {profile}")
        sample = {
            "run_index": run_index,
            "measured": measured,
            "component_signature_sec": elapsed,
            "status": metadata.get("status"),
            "prepared_partition_summary_reused": bool(metadata.get("prepared_partition_summary_reused")),
            "partition_summary_reused": bool(metadata.get("partition_summary_reused")),
            "component_count": int(metadata.get("component_count", 0)),
            "ambiguous_partition_pairs": int(metadata.get("ambiguous_partition_pairs", 0)),
            "device_ambiguous_union_used": bool(metadata.get("device_ambiguous_union_used")),
            "release_authorized": bool(metadata.get("release_authorized", False)),
            "public_speedup_claim_authorized": bool(metadata.get("public_speedup_claim_authorized", False)),
            "rt_core_speedup_claim_authorized": bool(metadata.get("rt_core_speedup_claim_authorized", False)),
            "whole_app_speedup_claim_authorized": bool(metadata.get("whole_app_speedup_claim_authorized", False)),
            "true_zero_copy_claim_authorized": bool(metadata.get("true_zero_copy_claim_authorized", False)),
        }
        if sample["status"] != "accept":
            raise RuntimeError(f"prepared signature rejected for {profile}: {metadata}")
        replay_samples.append(sample)
        print(
            "PROFILE_SIGNATURE_DONE "
            + json.dumps(
                {
                    "profile": profile,
                    "run_index": run_index,
                    "measured": measured,
                    "component_signature_sec": elapsed,
                    "component_count": sample["component_count"],
                },
                sort_keys=True,
            ),
            flush=True,
        )

    measured_samples = [sample for sample in replay_samples if sample["measured"]]
    replay_times = [float(sample["component_signature_sec"]) for sample in measured_samples]
    replay_summary = _summary(replay_times)
    reference_sec = CURRENT_RECOMMENDED_REFERENCE_SEC.get(profile)
    replay_median = replay_summary["median_sec"]
    break_even = _break_even_runs(
        prepare_sec=prepare_sec,
        replay_sec=replay_median,
        reference_sec=reference_sec,
    )
    amortized = {
        "signature_runs": int(signature_runs),
        "prepared_total_sec": prepare_sec + replay_median * signature_runs,
        "prepared_amortized_per_run_sec": (prepare_sec + replay_median * signature_runs) / max(signature_runs, 1),
        "current_recommended_total_sec_reference": (
            reference_sec * signature_runs if reference_sec is not None else None
        ),
        "speedup_vs_current_reference_for_n_runs": (
            (reference_sec * signature_runs) / (prepare_sec + replay_median * signature_runs)
            if reference_sec is not None
            else None
        ),
        "break_even_runs_reference": break_even,
    }
    return {
        "profile": profile,
        "point_count": point_count,
        "radius": radius,
        "cell_factor": cell_factor,
        "pair_enumeration": pair_enumeration,
        "prepare_sec": prepare_sec,
        "prepared_metadata": prepared_metadata,
        "prepared_status_counts": _status_counts(prepared.partition_summary["metadata"]),
        "component_signature_match": True,
        "component_signature_replay_sec": replay_summary,
        "replay_samples": replay_samples,
        "current_recommended_reference_sec": reference_sec,
        "amortized": amortized,
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
    signature_runs: int,
    warmup: int,
) -> dict[str, Any]:
    rows = [
        _run_profile(
            profile=profile,
            point_count=point_count,
            seed=seed,
            cell_factor=cell_factor,
            pair_enumeration=pair_enumeration,
            signature_runs=signature_runs,
            warmup=warmup,
        )
        for profile in profiles
    ]
    payload = {
        "goal": "Goal4087",
        "schema": "rtdl.goal4087.prepared_partition_summary_reuse_threshold.v1",
        "source_commit": _source_commit(),
        "host": platform.node(),
        "platform": platform.platform(),
        "gpu": _nvidia_smi(),
        "profiles": profiles,
        "point_count": int(point_count),
        "seed": int(seed),
        "cell_factor": float(cell_factor),
        "pair_enumeration": pair_enumeration,
        "signature_runs": int(signature_runs),
        "warmup": int(warmup),
        "current_recommended_reference_source": "Goal4074 recommended_unblocked median rows",
        "rows": rows,
        "claim_boundary": (
            "Internal prepared partition-summary reuse threshold evidence only. It does not promote "
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
    parser.add_argument("--profiles", default="clustered3d,road3d")
    parser.add_argument("--point-count", type=int, default=65536)
    parser.add_argument("--seed", type=int, default=20260519)
    parser.add_argument("--cell-factor", type=float, default=0.125)
    parser.add_argument("--pair-enumeration", default="device_count_then_emit")
    parser.add_argument("--signature-runs", type=int, default=5)
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
        signature_runs=args.signature_runs,
        warmup=args.warmup,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

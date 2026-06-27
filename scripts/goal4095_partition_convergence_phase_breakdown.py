from __future__ import annotations

import argparse
import json
import pathlib
import platform
import statistics
import subprocess
import time
from contextlib import contextmanager
from typing import Any, Iterator

import rtdsl as rt
import rtdsl.v2_8_fixed_radius_graph_component_front_door as frontdoor
from examples.benchmark_apps.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    make_rt_dbscan_points,
)
from scripts.goal4085_partition_summary_build_feasibility import PROFILE_RADII


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal4095_partition_convergence_phase_breakdown_pod.json"


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


def _sum_events(events: list[dict[str, Any]], label: str) -> float:
    return sum(float(event["elapsed_sec"]) for event in events if event["label"] == label)


@contextmanager
def _timed_partition_pair_status(cupy, events: list[dict[str, Any]]) -> Iterator[None]:
    original = frontdoor._cupy_partition_pair_status_device_bounded_offsets

    def wrapper(*args, **kwargs):
        pair_capacity = int(kwargs.get("pair_capacity", 0))
        emit_status_filter = str(kwargs.get("emit_status_filter", "all"))
        label = "pair_status_count_probe" if pair_capacity == 1 else "pair_status_emit"
        cupy.cuda.Stream.null.synchronize()
        start = time.perf_counter()
        result = original(*args, **kwargs)
        cupy.cuda.Stream.null.synchronize()
        elapsed = time.perf_counter() - start
        events.append(
            {
                "label": label,
                "pair_capacity": pair_capacity,
                "emit_status_filter": emit_status_filter,
                "elapsed_sec": elapsed,
            }
        )
        return result

    frontdoor._cupy_partition_pair_status_device_bounded_offsets = wrapper
    try:
        yield
    finally:
        frontdoor._cupy_partition_pair_status_device_bounded_offsets = original


@contextmanager
def _timed_partition_union(cupy, events: list[dict[str, Any]]) -> Iterator[None]:
    original_safe_full = frontdoor._cupy_union_safe_full_partition_pairs
    original_ambiguous = frontdoor._cupy_union_partition_pairs_with_ambiguous_points

    def safe_full_wrapper(*args, **kwargs):
        cupy.cuda.Stream.null.synchronize()
        start = time.perf_counter()
        result = original_safe_full(*args, **kwargs)
        cupy.cuda.Stream.null.synchronize()
        events.append({"label": "safe_full_partition_union", "elapsed_sec": time.perf_counter() - start})
        return result

    def ambiguous_wrapper(*args, **kwargs):
        cupy.cuda.Stream.null.synchronize()
        start = time.perf_counter()
        result = original_ambiguous(*args, **kwargs)
        cupy.cuda.Stream.null.synchronize()
        events.append({"label": "ambiguous_partition_point_union", "elapsed_sec": time.perf_counter() - start})
        return result

    frontdoor._cupy_union_safe_full_partition_pairs = safe_full_wrapper
    frontdoor._cupy_union_partition_pairs_with_ambiguous_points = ambiguous_wrapper
    try:
        yield
    finally:
        frontdoor._cupy_union_safe_full_partition_pairs = original_safe_full
        frontdoor._cupy_union_partition_pairs_with_ambiguous_points = original_ambiguous


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
    for run_index in range(warmup + repeat):
        measured = run_index >= warmup
        label = "MEASURE" if measured else "WARMUP"
        print(
            f"PROFILE_PHASE_{label}_START {profile} point_count={point_count} run={run_index}",
            flush=True,
        )

        pair_events: list[dict[str, Any]] = []
        cupy.cuda.Stream.null.synchronize()
        build_start = time.perf_counter()
        with _timed_partition_pair_status(cupy, pair_events):
            summary = rt.build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
                points,
                radius=radius,
                cell_factor=cell_factor,
                pair_enumeration=pair_enumeration,
            )
        cupy.cuda.Stream.null.synchronize()
        build_total_sec = time.perf_counter() - build_start

        union_events: list[dict[str, Any]] = []
        cupy.cuda.Stream.null.synchronize()
        signature_start = time.perf_counter()
        with _timed_partition_union(cupy, union_events):
            signature = rt.build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d(
                points,
                radius=radius,
                cell_factor=cell_factor,
                partition_summary=summary,
                validate_summary_same_contract=False,
                validate_against_component_labels=False,
            )
        cupy.cuda.Stream.null.synchronize()
        signature_total_sec = time.perf_counter() - signature_start

        count_probe_sec = _sum_events(pair_events, "pair_status_count_probe")
        emit_sec = _sum_events(pair_events, "pair_status_emit")
        safe_full_sec = _sum_events(union_events, "safe_full_partition_union")
        ambiguous_sec = _sum_events(union_events, "ambiguous_partition_point_union")
        build_uninstrumented_sec = max(0.0, build_total_sec - count_probe_sec - emit_sec)
        signature_uninstrumented_sec = max(0.0, signature_total_sec - safe_full_sec - ambiguous_sec)
        metadata = dict(summary["metadata"])
        sig_metadata = dict(signature["metadata"])
        sample = {
            "run_index": run_index,
            "measured": measured,
            "build_total_sec": build_total_sec,
            "pair_status_count_probe_sec": count_probe_sec,
            "pair_status_emit_sec": emit_sec,
            "build_uninstrumented_sec": build_uninstrumented_sec,
            "signature_total_sec": signature_total_sec,
            "safe_full_partition_union_sec": safe_full_sec,
            "ambiguous_partition_point_union_sec": ambiguous_sec,
            "signature_uninstrumented_sec": signature_uninstrumented_sec,
            "partition_count": int(metadata["partition_count"]),
            "pair_count": int(metadata["pair_count"]),
            "pair_enumeration": metadata["pair_enumeration"],
            "pair_stream_filter": metadata.get("pair_stream_filter", "all_partition_pairs"),
            "safe_skip_pairs_elided": bool(metadata.get("safe_skip_pairs_elided", False)),
            "status_counts": dict(metadata["status_counts"]),
            "component_count": int(sig_metadata["component_count"]),
            "ambiguous_point_comparisons": int(sig_metadata["ambiguous_point_comparisons"]),
            "ambiguous_positive_edges": int(sig_metadata["ambiguous_positive_edges"]),
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "native_abi_added": False,
        }
        samples.append(sample)
        print(
            "PROFILE_PHASE_SAMPLE "
            + json.dumps(
                {
                    "profile": profile,
                    "run_index": run_index,
                    "measured": measured,
                    "build_total_sec": build_total_sec,
                    "pair_status_count_probe_sec": count_probe_sec,
                    "pair_status_emit_sec": emit_sec,
                    "signature_total_sec": signature_total_sec,
                    "ambiguous_partition_point_union_sec": ambiguous_sec,
                    "pair_count": int(metadata["pair_count"]),
                    "component_count": int(sig_metadata["component_count"]),
                },
                sort_keys=True,
            ),
            flush=True,
        )
    measured_samples = [sample for sample in samples if sample["measured"]]
    if not measured_samples:
        raise ValueError("repeat must produce at least one measured sample")
    phase_keys = (
        "build_total_sec",
        "pair_status_count_probe_sec",
        "pair_status_emit_sec",
        "build_uninstrumented_sec",
        "signature_total_sec",
        "safe_full_partition_union_sec",
        "ambiguous_partition_point_union_sec",
        "signature_uninstrumented_sec",
    )
    phase_summary = {
        key: _summary([float(sample[key]) for sample in measured_samples])
        for key in phase_keys
    }
    reference = measured_samples[-1]
    return {
        "profile": profile,
        "point_count": int(point_count),
        "radius": float(radius),
        "cell_factor": float(cell_factor),
        "pair_enumeration": pair_enumeration,
        "partition_count": reference["partition_count"],
        "pair_count": reference["pair_count"],
        "pair_stream_filter": reference["pair_stream_filter"],
        "safe_skip_pairs_elided": reference["safe_skip_pairs_elided"],
        "status_counts": reference["status_counts"],
        "component_count": reference["component_count"],
        "phase_summary": phase_summary,
        "samples": samples,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
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
        "goal": "Goal4095",
        "schema": "rtdl.goal4095.partition_convergence_phase_breakdown.v1",
        "source_commit": _source_commit(),
        "host": platform.node(),
        "platform": platform.platform(),
        "gpu": _nvidia_smi(),
        "profiles": profiles,
        "point_count": int(point_count),
        "seed": int(seed),
        "cell_factor": float(cell_factor),
        "pair_enumeration": pair_enumeration,
        "repeat": int(repeat),
        "warmup": int(warmup),
        "rows": rows,
        "claim_boundary": (
            "Internal RT-DBSCAN partition-convergence phase-breakdown evidence only. It does not "
            "promote partition_convergence_hybrid, authorize release, public speedup, broad RT-core, "
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
    parser.add_argument("--pair-enumeration", default="device_count_then_emit_non_skip")
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

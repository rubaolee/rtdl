from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import subprocess
from typing import Any

from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    run_rt_dbscan_benchmark,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal4074_rt_dbscan_grouped_stream_bottleneck_refresh_pod.json"

PROFILES = (
    ("clustered3d_65536", "clustered3d", 65536),
    ("road3d_65536", "road3d", 65536),
)

VARIANTS = (
    (
        "recommended_unblocked",
        "optix_rt_core_grouped_stream_numba_column_signature_3d",
        {},
    ),
    (
        "direct_side_effect",
        "optix_rt_core_grouped_stream_numba_column_signature_3d",
        {"grouped_union_direct_side_effect": True},
    ),
    (
        "blocked_32768",
        "optix_rt_core_grouped_stream_blocked_numba_column_signature_3d",
        {"grouped_union_query_block_size": 32768},
    ),
    (
        "no_same_root_culling",
        "optix_rt_core_grouped_stream_numba_column_signature_3d",
        {"grouped_union_same_root_culling": False},
    ),
)


def _source_commit() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


def _phase(metadata: dict[str, Any], *names: str) -> dict[str, Any]:
    value: Any = metadata
    for name in names:
        if not isinstance(value, dict):
            return {}
        value = value.get(name)
    return value if isinstance(value, dict) else {}


def _component_size_signature(signature: dict[str, Any]) -> list[int]:
    if "component_sizes" in signature:
        return sorted(int(value) for value in signature["component_sizes"])
    cluster_sizes = signature.get("cluster_sizes")
    if isinstance(cluster_sizes, dict):
        return sorted(int(value) for value in cluster_sizes.values())
    raise ValueError(f"unsupported signature shape: {signature!r}")


def _median(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot summarize empty timing list")
    return float(statistics.median(values))


def _run_variant(
    *,
    profile: str,
    dataset: str,
    point_count: int,
    variant: str,
    mode: str,
    extra: dict[str, Any],
    repeat: int,
    warmup: int,
) -> dict[str, Any]:
    print("BOTTLENECK_START", profile, variant, mode, json.dumps(extra, sort_keys=True), flush=True)
    payload = run_rt_dbscan_benchmark(
        mode=mode,
        dataset=dataset,
        point_count=point_count,
        radius=None,
        min_neighbors=None,
        seed=20260519,
        partner="cupy",
        include_rows=False,
        validate=False,
        repeat=repeat,
        warmup=warmup,
        **extra,
    )
    metadata = payload["metadata"]
    timing = _phase(metadata, "benchmark_timing_breakdown")
    host_timing = _phase(timing, "host_observed_sec")
    derived = _phase(timing, "derived_sec")
    native = _phase(metadata, "native_grouped_stream_metadata")
    count_metadata = _phase(metadata, "count_metadata")
    count_native = _phase(count_metadata, "native_metadata")
    row = {
        "profile": profile,
        "dataset": dataset,
        "point_count": int(point_count),
        "variant": variant,
        "mode": mode,
        "elapsed_sec": float(payload["elapsed_sec"]),
        "signature": payload["signature"],
        "component_size_signature": _component_size_signature(payload["signature"]),
        "path": metadata.get("path"),
        "partner": metadata.get("partner"),
        "rt_core_accelerated": bool(metadata.get("rt_core_accelerated", False)),
        "column_signature_strategy": metadata.get("column_signature_strategy"),
        "all_core_flags_true": bool(metadata.get("all_core_flags_true", False)),
        "core_flag_cache_reused": bool(metadata.get("core_flag_cache_reused", False)),
        "prepared_grouped_stream_reused": bool(metadata.get("prepared_grouped_stream_reused", False)),
        "grouped_union_query_blocked_candidate": bool(metadata.get("grouped_union_query_blocked_candidate", False)),
        "grouped_union_query_block_size": metadata.get("grouped_union_query_block_size"),
        "grouped_union_query_block_count": metadata.get("grouped_union_query_block_count"),
        "grouped_union_same_root_culling_enabled": metadata.get("grouped_union_same_root_culling_enabled"),
        "grouped_union_direct_side_effect_enabled": metadata.get("grouped_union_direct_side_effect_enabled"),
        "host_observed_sec": host_timing,
        "derived_sec": derived,
        "native_symbol": native.get("native_symbol"),
        "native_execution_path": native.get("native_execution_path"),
        "native_elapsed_sec": native.get("native_elapsed_sec"),
        "count_native_elapsed_sec": count_native.get("native_elapsed_sec"),
        "prepared_query_repeat_protocol": metadata.get("prepared_query_repeat_protocol"),
        "release_authorized": bool(metadata.get("release_authorized", False)),
        "public_speedup_claim_authorized": bool(metadata.get("public_speedup_claim_authorized", False)),
        "rt_core_speedup_claim_authorized": bool(metadata.get("rt_core_speedup_claim_authorized", False)),
        "whole_app_speedup_claim_authorized": bool(metadata.get("whole_app_speedup_claim_authorized", False)),
        "true_zero_copy_claim_authorized": bool(metadata.get("true_zero_copy_claim_authorized", False)),
    }
    print("BOTTLENECK_DONE", json.dumps({
        "profile": profile,
        "variant": variant,
        "elapsed_sec": row["elapsed_sec"],
        "native_elapsed_sec": row["native_elapsed_sec"],
        "count_native_elapsed_sec": row["count_native_elapsed_sec"],
        "component_size_signature": row["component_size_signature"],
    }, sort_keys=True), flush=True)
    return row


def run(output: pathlib.Path, repeat: int, warmup: int) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for profile, dataset, point_count in PROFILES:
        profile_rows = [
            _run_variant(
                profile=profile,
                dataset=dataset,
                point_count=point_count,
                variant=variant,
                mode=mode,
                extra=dict(extra),
                repeat=repeat,
                warmup=warmup,
            )
            for variant, mode, extra in VARIANTS
        ]
        reference = profile_rows[0]["component_size_signature"]
        reference_elapsed = float(profile_rows[0]["elapsed_sec"])
        for row in profile_rows:
            row["same_component_size_signature_as_recommended"] = row["component_size_signature"] == reference
            row["time_ratio_over_recommended"] = float(row["elapsed_sec"]) / max(reference_elapsed, 1.0e-12)
        rows.extend(profile_rows)

    recommended_rows = [row for row in rows if row["variant"] == "recommended_unblocked"]
    payload = {
        "goal": "Goal4074",
        "schema": "rtdl.goal4074.rt_dbscan_grouped_stream_bottleneck_refresh.v1",
        "source_commit": _source_commit(),
        "repeat": int(repeat),
        "warmup": int(warmup),
        "profiles": [profile for profile, _, _ in PROFILES],
        "variants": [variant for variant, _, _ in VARIANTS],
        "recommended_elapsed_sec_median": _median([float(row["elapsed_sec"]) for row in recommended_rows]),
        "claim_boundary": (
            "Internal RT-DBSCAN grouped-stream bottleneck telemetry. It does not authorize release, "
            "paper, public speedup, broad RT-core, whole-app, hidden-dispatch, automatic partner "
            "selection, app-specific engine logic, native ABI addition, or true-zero-copy claims."
        ),
        "release_authorized": False,
        "paper_speedup_claim_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "native_abi_added": False,
        "rows": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--repeat", type=int, default=6)
    parser.add_argument("--warmup", type=int, default=2)
    args = parser.parse_args()
    payload = run(args.output, args.repeat, args.warmup)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

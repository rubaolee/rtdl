#!/usr/bin/env python3
"""Fair timing probe for fixed-radius boundary-assignment policies.

This is a benchmark-app probe, not a promoted RTDL route. It compares the
default one-pass grouped-stream policy with the explicit two-pass
lowest-component-root preview under the same prepared-handle contract.
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import time
from pathlib import Path
from typing import Iterable

import rtdsl as rt
from examples.v2_0.research_benchmarks.rt_dbscan import rtdl_rt_dbscan_benchmark_app as app


POLICIES = ("single_pass_candidate_root_rebased", "lowest_component_root_two_pass")
SCHEMA = "rtdl.goal4201.rt_dbscan_boundary_policy_fair_timing.v1"
DEFAULT_OUTPUT = (
    Path("docs")
    / "reports"
    / "goal4201_rt_dbscan_boundary_policy_fair_timing_pod.json"
)

PRESETS: dict[str, dict[str, object]] = {
    "clustered3d_16k": {
        "dataset": "clustered3d",
        "point_count": 16_384,
        "radius": 0.035,
        "component_threshold": 16,
    },
    "clustered3d_64k": {
        "dataset": "clustered3d",
        "point_count": 65_536,
        "radius": 0.035,
        "component_threshold": 16,
    },
    "road3d_64k": {
        "dataset": "road3d",
        "point_count": 65_536,
        "radius": 0.01,
        "component_threshold": 16,
    },
    "ngsim_dense_64k": {
        "dataset": "ngsim_dense",
        "point_count": 65_536,
        "radius": 0.012,
        "component_threshold": 16,
    },
}


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:  # pragma: no cover - only for non-git ad hoc runs.
        return "unknown"


def _maybe_sync() -> None:
    try:
        from numba import cuda

        cuda.synchronize()
    except Exception:
        return


def _median(values: Iterable[float]) -> float | None:
    values = list(values)
    if not values:
        return None
    return float(statistics.median(values))


def _run_signature(prepared, component_threshold: int) -> tuple[dict[str, object], dict[str, object]]:
    out = rt.fixed_radius_graph_component_size_signature_3d_v2_8(
        prepared,
        component_threshold=component_threshold,
        return_metadata=True,
    )
    cols = out["columns"]
    meta = out["metadata"]
    label_counts = cols["label_counts"].copy_to_host()
    nonzero_sizes = sorted(int(x) for x in label_counts if int(x) > 0)
    signature = {
        "flag_true_count": int(cols["flag_true_count"].copy_to_host()[0]),
        "negative_label_count": int(cols["negative_label_count"].copy_to_host()[0]),
        "component_count": len(nonzero_sizes),
        "largest_component_size": max(nonzero_sizes) if nonzero_sizes else 0,
        "label_count_signature_head": nonzero_sizes[:16],
        "label_count_signature_tail": nonzero_sizes[-16:],
    }
    return signature, meta


def run_case(
    *,
    dataset: str,
    point_count: int,
    radius: float,
    component_threshold: int,
    repeat: int,
    warmup: int,
    seed: int,
) -> dict[str, object]:
    points = app.make_rt_dbscan_points(dataset, point_count=point_count, seed=seed)
    prepared_by_policy = {}
    prepare_elapsed_by_policy = {}
    for policy in POLICIES:
        start = time.perf_counter()
        prepared_by_policy[policy] = rt.prepare_v2_8_fixed_radius_graph_component_continuation_3d(
            points,
            radius=radius,
            component_threshold=component_threshold,
            backend="optix",
            partner="numba",
            strategy="grouped_stream",
            boundary_assignment_policy=policy,
        )
        _maybe_sync()
        prepare_elapsed_by_policy[policy] = time.perf_counter() - start

    try:
        warmup_signatures: dict[str, dict[str, object]] = {}
        policy_metadata: dict[str, dict[str, object]] = {}
        for _ in range(warmup):
            for policy in POLICIES:
                signature, meta = _run_signature(prepared_by_policy[policy], component_threshold)
                warmup_signatures[policy] = signature
                policy_metadata[policy] = meta
                _maybe_sync()

        timings = {policy: [] for policy in POLICIES}
        signatures = {policy: None for policy in POLICIES}
        for index in range(repeat):
            order = POLICIES if index % 2 == 0 else tuple(reversed(POLICIES))
            for policy in order:
                _maybe_sync()
                start = time.perf_counter()
                signature, meta = _run_signature(prepared_by_policy[policy], component_threshold)
                _maybe_sync()
                elapsed = time.perf_counter() - start
                timings[policy].append(elapsed)
                signatures[policy] = signature
                policy_metadata[policy] = meta

        policies = {}
        for policy in POLICIES:
            metadata = policy_metadata.get(policy, {})
            native_meta = metadata.get("native_grouped_stream_metadata", {}) or {}
            policies[policy] = {
                "prepare_elapsed_sec": prepare_elapsed_by_policy[policy],
                "run_elapsed_sec": timings[policy],
                "run_median_sec": _median(timings[policy]),
                "run_min_sec": min(timings[policy]) if timings[policy] else None,
                "run_max_sec": max(timings[policy]) if timings[policy] else None,
                "signature": signatures[policy] or warmup_signatures.get(policy),
                "metadata_boundary_assignment_policy": metadata.get("boundary_assignment_policy"),
                "native_boundary_assignment_policy": native_meta.get("boundary_assignment_policy"),
                "native_boundary_assignment_pass_count": native_meta.get("boundary_assignment_pass_count"),
                "native_symbol": native_meta.get("native_symbol"),
                "public_speedup_claim_authorized": metadata.get("public_speedup_claim_authorized"),
                "true_zero_copy_claim_authorized": metadata.get("true_zero_copy_claim_authorized"),
            }

        default_signature = policies["single_pass_candidate_root_rebased"]["signature"]
        two_pass_signature = policies["lowest_component_root_two_pass"]["signature"]
        default_median = policies["single_pass_candidate_root_rebased"]["run_median_sec"]
        two_pass_median = policies["lowest_component_root_two_pass"]["run_median_sec"]
        return {
            "dataset": dataset,
            "point_count": point_count,
            "radius": radius,
            "component_threshold": component_threshold,
            "seed": seed,
            "repeat": repeat,
            "warmup": warmup,
            "policies": policies,
            "same_counts_only_signature": default_signature == two_pass_signature,
            "two_pass_vs_default_median_ratio": (
                (two_pass_median / default_median)
                if default_median and two_pass_median
                else None
            ),
            "route_promotion_authorized": False,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        }
    finally:
        for prepared in prepared_by_policy.values():
            prepared.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", action="append", choices=sorted(PRESETS), help="Named benchmark preset")
    parser.add_argument("--dataset", choices=("clustered3d", "road3d", "ngsim_dense"))
    parser.add_argument("--point-count", type=int)
    parser.add_argument("--radius", type=float)
    parser.add_argument("--component-threshold", type=int, default=16)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20260519)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--list-presets", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.list_presets:
        print(json.dumps(PRESETS, indent=2, sort_keys=True))
        return

    cases: list[dict[str, object]] = []
    for preset in args.preset or ():
        cases.append(dict(PRESETS[preset]))
    if args.dataset:
        if args.point_count is None or args.radius is None:
            raise SystemExit("--dataset requires --point-count and --radius")
        cases.append(
            {
                "dataset": args.dataset,
                "point_count": args.point_count,
                "radius": args.radius,
                "component_threshold": args.component_threshold,
            }
        )
    if not cases:
        cases.append(dict(PRESETS["clustered3d_16k"]))

    payload = {
        "schema": SCHEMA,
        "commit": _git_commit(),
        "cases": [],
        "claim_boundary": {
            "release_authorized": False,
            "route_promotion_authorized": False,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        },
    }
    for case in cases:
        print(
            f"[goal4201] running {case['dataset']} n={case['point_count']} radius={case['radius']}",
            flush=True,
        )
        payload["cases"].append(
            run_case(
                dataset=str(case["dataset"]),
                point_count=int(case["point_count"]),
                radius=float(case["radius"]),
                component_threshold=int(case["component_threshold"]),
                repeat=args.repeat,
                warmup=args.warmup,
                seed=args.seed,
            )
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import time
from typing import Any

from examples.current.research_benchmarks.rt_dbscan import rtdl_rt_dbscan_benchmark_app as app


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal4190_rt_dbscan_counts_only_mixed_route_probe_pod.json"


ROUTES = (
    {
        "label": "current_grouped_stream_numba",
        "mode": app.RT_DBSCAN_GROUPED_STREAM_NUMBA_APP_MODE,
        "partner": "numba",
        "direct_status_convergence_mode": "until_stable",
        "border_assignment_policy": "one_predicate_true_neighbor_candidate_per_predicate_false_item_captured_during_rt_pass",
        "semantic_scope": "policy_bound_component_sizes_and_counts_only_reference",
    },
    {
        "label": "predicate_direct_status_until_stable",
        "mode": app.RT_DBSCAN_PREDICATE_DIRECT_STATUS_APP_MODE,
        "partner": "cupy",
        "direct_status_convergence_mode": "until_stable",
        "border_assignment_policy": "lowest_predicate_true_point_id_within_radius",
        "semantic_scope": "counts_only_candidate_component_sizes_policy_bound_to_explicit_lowest_id_policy",
    },
    {
        "label": "predicate_direct_status_single_pass_candidate",
        "mode": app.RT_DBSCAN_PREDICATE_DIRECT_STATUS_APP_MODE,
        "partner": "cupy",
        "direct_status_convergence_mode": "single_pass_candidate",
        "border_assignment_policy": "lowest_predicate_true_point_id_within_radius",
        "semantic_scope": "counts_only_candidate_single_pass_not_promoted",
    },
)


def _source_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def _gpu_summary() -> str:
    try:
        return subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            text=True,
            timeout=15,
        ).strip()
    except Exception as exc:  # pragma: no cover - hardware dependent.
        return f"unavailable: {exc}"


def _policy_signatures(signature: dict[str, Any], *, border_assignment_policy: str) -> dict[str, Any]:
    return {
        "policy_bound_component_sizes": app.policy_aware_rt_dbscan_semantic_signature(
            signature,
            border_assignment_policy=border_assignment_policy,
            component_size_contract="policy_bound_component_sizes",
        ),
        "core_noise_assigned_counts_only": app.policy_aware_rt_dbscan_semantic_signature(
            signature,
            border_assignment_policy="border_tie_break_not_semantic",
            component_size_contract="core_noise_assigned_counts_only",
        ),
    }


def _run_route(
    *,
    route: dict[str, Any],
    dataset: str,
    point_count: int,
    radius: float,
    min_neighbors: int,
    partition_cell_factor: float,
    repeat: int,
    warmup: int,
    seed: int,
) -> dict[str, Any]:
    print(
        "GOAL4190_ROUTE_START",
        json.dumps(
            {
                "label": route["label"],
                "mode": route["mode"],
                "dataset": dataset,
                "point_count": point_count,
                "radius": radius,
                "min_neighbors": min_neighbors,
                "repeat": repeat,
                "warmup": warmup,
                "direct_status_convergence_mode": route["direct_status_convergence_mode"],
            },
            sort_keys=True,
        ),
        flush=True,
    )
    wall_start = time.perf_counter()
    payload = app.run_rt_dbscan_benchmark(
        mode=str(route["mode"]),
        dataset=dataset,
        point_count=point_count,
        radius=radius,
        min_neighbors=min_neighbors,
        seed=seed,
        partner=str(route["partner"]),
        include_rows=False,
        validate=False,
        partition_cell_factor=partition_cell_factor,
        direct_status_convergence_mode=str(route["direct_status_convergence_mode"]),
        repeat=repeat,
        warmup=warmup,
    )
    wall_sec = time.perf_counter() - wall_start
    metadata = dict(payload["metadata"])
    policy_signatures = _policy_signatures(
        payload["signature"],
        border_assignment_policy=str(route["border_assignment_policy"]),
    )
    row = {
        "label": route["label"],
        "mode": payload["mode"],
        "partner": route["partner"],
        "elapsed_sec": float(payload["elapsed_sec"]),
        "wall_sec": float(wall_sec),
        "signature": payload["signature"],
        "policy_signatures": policy_signatures,
        "metadata": metadata,
        "path": metadata.get("path"),
        "native_engine_summary_contract": metadata.get("native_engine_summary_contract"),
        "native_execution_path": metadata.get("native_execution_path"),
        "rt_core_accelerated": bool(metadata.get("rt_core_accelerated", False)),
        "direct_status_convergence_mode": route["direct_status_convergence_mode"],
        "border_assignment_policy": route["border_assignment_policy"],
        "semantic_scope": route["semantic_scope"],
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "route_promotion_authorized": False,
    }
    print(
        "GOAL4190_ROUTE_DONE",
        json.dumps(
            {
                "label": row["label"],
                "elapsed_sec": row["elapsed_sec"],
                "wall_sec": row["wall_sec"],
                "signature": row["signature"],
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return row


def run(
    *,
    output: pathlib.Path,
    dataset: str,
    point_count: int,
    warmup_point_count: int,
    radius: float,
    min_neighbors: int,
    partition_cell_factor: float,
    repeat: int,
    warmup: int,
    seed: int,
) -> dict[str, Any]:
    print("GOAL4190_PROBE_START", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), flush=True)
    warmup_rows = [
        _run_route(
            route=route,
            dataset=dataset,
            point_count=warmup_point_count,
            radius=radius,
            min_neighbors=min_neighbors,
            partition_cell_factor=partition_cell_factor,
            repeat=1,
            warmup=0,
            seed=seed,
        )
        for route in ROUTES
    ]
    rows = [
        _run_route(
            route=route,
            dataset=dataset,
            point_count=point_count,
            radius=radius,
            min_neighbors=min_neighbors,
            partition_cell_factor=partition_cell_factor,
            repeat=repeat,
            warmup=warmup,
            seed=seed,
        )
        for route in ROUTES
    ]
    reference = rows[0]
    reference_policy = reference["policy_signatures"]
    reference_elapsed = float(reference["elapsed_sec"])
    for row in rows:
        row["same_policy_bound_component_sizes_as_reference"] = (
            row["policy_signatures"]["policy_bound_component_sizes"]
            == reference_policy["policy_bound_component_sizes"]
        )
        row["same_counts_only_as_reference"] = (
            row["policy_signatures"]["core_noise_assigned_counts_only"]
            == reference_policy["core_noise_assigned_counts_only"]
        )
        row["speedup_vs_grouped_elapsed"] = reference_elapsed / max(float(row["elapsed_sec"]), 1.0e-12)
    payload = {
        "goal": "Goal4190",
        "schema": "rtdl.goal4190.rt_dbscan_counts_only_mixed_route_probe.v1",
        "purpose": (
            "Measure explicit mixed-predicate RT-DBSCAN route choices under a policy-aware "
            "semantic contract. Predicate direct-status may be meaningful for counts-only "
            "semantics, but component-size distribution still requires an explicit border policy."
        ),
        "source_commit": _source_commit(),
        "gpu": _gpu_summary(),
        "dataset": dataset,
        "point_count": int(point_count),
        "warmup_point_count": int(warmup_point_count),
        "radius": float(radius),
        "min_neighbors": int(min_neighbors),
        "partition_cell_factor": float(partition_cell_factor),
        "repeat": int(repeat),
        "warmup": int(warmup),
        "seed": int(seed),
        "semantic_contracts": (
            "policy_bound_component_sizes",
            "core_noise_assigned_counts_only",
        ),
        "route_promotion_authorized": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_rt_core_speedup_claim_authorized": False,
        "whole_app_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "native_abi_added": False,
        "claim_boundary": (
            "Internal explicit-route evidence only. Counts-only semantic matches do not promote "
            "predicate direct-status as the default mixed-predicate route and do not claim "
            "component-size equivalence."
        ),
        "warmup_rows": warmup_rows,
        "rows": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print("GOAL4190_PROBE_DONE", json.dumps({"output": str(output), "rows": len(rows)}, sort_keys=True), flush=True)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dataset", default="road3d", choices=tuple(app.DEFAULT_DATASET_CONFIG))
    parser.add_argument("--point-count", type=int, default=262_144)
    parser.add_argument("--warmup-point-count", type=int, default=4096)
    parser.add_argument("--radius", type=float, default=0.003)
    parser.add_argument("--min-neighbors", type=int, default=16)
    parser.add_argument("--partition-cell-factor", type=float, default=0.25)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--warmup", type=int, default=0)
    parser.add_argument("--seed", type=int, default=20260519)
    args = parser.parse_args()
    payload = run(
        output=args.output,
        dataset=args.dataset,
        point_count=args.point_count,
        warmup_point_count=args.warmup_point_count,
        radius=args.radius,
        min_neighbors=args.min_neighbors,
        partition_cell_factor=args.partition_cell_factor,
        repeat=args.repeat,
        warmup=args.warmup,
        seed=args.seed,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

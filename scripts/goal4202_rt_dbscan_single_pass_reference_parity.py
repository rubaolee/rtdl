#!/usr/bin/env python3
"""Compare RTDL fixed-radius grouped-stream policies to the Goal4194 reference."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path

import rtdsl as rt
from examples.current.research_benchmarks.rt_dbscan import rtdl_rt_dbscan_benchmark_app as app


SCHEMA = "rtdl.goal4202.rt_dbscan_single_pass_reference_parity.v1"
DEFAULT_OUTPUT = (
    Path("docs")
    / "reports"
    / "goal4202_rt_dbscan_single_pass_reference_parity_pod.json"
)
POLICIES = ("single_pass_candidate_root_rebased", "lowest_component_root_two_pass")
PRESETS: dict[str, dict[str, object]] = {
    "adversarial_root_shadow_1d": {
        "dataset": "adversarial_root_shadow_1d",
        "point_count": 5,
        "radius": 1.01,
        "component_threshold": 3,
    },
    "tiny": {
        "dataset": "tiny",
        "point_count": 9,
        "radius": 0.13,
        "component_threshold": 3,
    },
    "clustered3d_512": {
        "dataset": "clustered3d",
        "point_count": 512,
        "radius": 0.035,
        "component_threshold": 16,
    },
    "road3d_1024": {
        "dataset": "road3d",
        "point_count": 1024,
        "radius": 0.02,
        "component_threshold": 16,
    },
    "ngsim_dense_1024": {
        "dataset": "ngsim_dense",
        "point_count": 1024,
        "radius": 0.012,
        "component_threshold": 16,
    },
}


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:  # pragma: no cover
        return "unknown"


def _candidate_pairs(points, radius: float) -> list[tuple[int, int]]:
    radius_sq = radius * radius
    pairs: list[tuple[int, int]] = []
    coords = [(float(p.x), float(p.y), float(p.z)) for p in points]
    for left in range(len(coords)):
        lx, ly, lz = coords[left]
        for right in range(left + 1, len(coords)):
            rx, ry, rz = coords[right]
            dx = lx - rx
            dy = ly - ry
            dz = lz - rz
            if dx * dx + dy * dy + dz * dz <= radius_sq:
                pairs.append((left, right))
    return pairs


def _make_points(dataset: str, *, point_count: int, seed: int):
    if dataset == "adversarial_root_shadow_1d":
        if point_count != 5:
            raise ValueError("adversarial_root_shadow_1d uses exactly 5 points")
        # Four predicate-true candidates form a chain whose final root is point 0.
        # The fifth point is a predicate-false boundary item near the high-index
        # end of the chain, so a one-pass traversal must rebase its observed
        # candidate through final roots to match the reference contract.
        coords = (0.0, 0.45, 0.90, 1.35, 2.35)
        return tuple(rt.Point3D(id=index + 1, x=x, y=0.0, z=0.0) for index, x in enumerate(coords))
    return app.make_rt_dbscan_points(dataset, point_count=point_count, seed=seed)


def _run_policy(points, *, radius: float, component_threshold: int, policy: str) -> dict[str, object]:
    with rt.prepare_v2_8_fixed_radius_graph_component_continuation_3d(
        points,
        radius=radius,
        component_threshold=component_threshold,
        backend="optix",
        partner="numba",
        strategy="grouped_stream",
        boundary_assignment_policy=policy,
    ) as prepared:
        out = rt.fixed_radius_graph_component_labels_3d_v2_8(
            prepared,
            component_threshold=component_threshold,
            return_metadata=True,
        )
        columns = out["columns"]
        labels_host = [int(value) for value in columns["component_labels"].copy_to_host()]
        zero_based_labels = tuple((label - 1) if label > 0 else -1 for label in labels_host)
        core_flags = tuple(bool(int(value)) for value in columns["is_core"].copy_to_host())
        neighbor_counts = tuple(int(value) for value in columns["neighbor_counts"].copy_to_host())
        metadata = out["metadata"]
        native_meta = metadata.get("native_grouped_stream_metadata", {}) or {}
        return {
            "component_labels": zero_based_labels,
            "predicate_flags": core_flags,
            "neighbor_counts_head": neighbor_counts[:16],
            "native_boundary_assignment_policy": native_meta.get("boundary_assignment_policy"),
            "native_boundary_assignment_pass_count": native_meta.get("boundary_assignment_pass_count"),
            "native_symbol": native_meta.get("native_symbol"),
            "metadata": {
                "public_speedup_claim_authorized": metadata.get("public_speedup_claim_authorized"),
                "true_zero_copy_claim_authorized": metadata.get("true_zero_copy_claim_authorized"),
                "rt_core_accelerated": metadata.get("rt_core_accelerated"),
            },
        }


def run_case(case: dict[str, object], *, seed: int) -> dict[str, object]:
    dataset = str(case["dataset"])
    point_count = int(case["point_count"])
    radius = float(case["radius"])
    component_threshold = int(case["component_threshold"])
    points = _make_points(dataset, point_count=point_count, seed=seed)
    pairs = _candidate_pairs(points, radius)
    policy_results = {
        policy: _run_policy(points, radius=radius, component_threshold=component_threshold, policy=policy)
        for policy in POLICIES
    }
    predicate_flags = policy_results["single_pass_candidate_root_rebased"]["predicate_flags"]
    reference = rt.predicate_aware_boundary_union_reference(
        point_count=point_count,
        candidate_pairs=pairs,
        predicate_flags=predicate_flags,
        boundary_assignment_policy="lowest_component_root",
    )
    reference_labels = tuple(int(value) for value in reference["component_labels"])
    policies = {}
    for policy, result in policy_results.items():
        labels = tuple(result["component_labels"])
        policies[policy] = {
            "matches_reference_labels": labels == reference_labels,
            "mismatch_count": sum(1 for left, right in zip(labels, reference_labels) if left != right),
            "native_boundary_assignment_policy": result["native_boundary_assignment_policy"],
            "native_boundary_assignment_pass_count": result["native_boundary_assignment_pass_count"],
            "native_symbol": result["native_symbol"],
            "metadata": result["metadata"],
        }
    default_labels = policy_results["single_pass_candidate_root_rebased"]["component_labels"]
    two_pass_labels = policy_results["lowest_component_root_two_pass"]["component_labels"]
    return {
        "dataset": dataset,
        "point_count": point_count,
        "radius": radius,
        "component_threshold": component_threshold,
        "candidate_pair_count": len(pairs),
        "predicate_true_count": int(reference["predicate_true_count"]),
        "reference_component_count": int(reference["component_count"]),
        "reference_component_sizes": tuple(int(value) for value in reference["component_sizes"]),
        "policies": policies,
        "default_matches_two_pass_labels": tuple(default_labels) == tuple(two_pass_labels),
        "all_policies_match_reference": all(row["matches_reference_labels"] for row in policies.values()),
        "route_promotion_authorized": False,
        "public_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", action="append", choices=sorted(PRESETS))
    parser.add_argument("--seed", type=int, default=20260519)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--list-presets", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.list_presets:
        print(json.dumps(PRESETS, indent=2, sort_keys=True))
        return
    presets = args.preset or list(PRESETS)
    payload = {
        "schema": SCHEMA,
        "commit": _git_commit(),
        "cases": [],
        "claim_boundary": {
            "route_promotion_authorized": False,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
    }
    for preset in presets:
        print(f"[goal4202] running {preset}", flush=True)
        payload["cases"].append(run_case(PRESETS[preset], seed=args.seed))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

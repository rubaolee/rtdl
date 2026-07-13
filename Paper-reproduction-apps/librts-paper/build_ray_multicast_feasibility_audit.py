from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt


APP_DIR = Path(__file__).resolve().parent
SOURCE_MANIFEST = (
    APP_DIR / "data" / "author_source" / "goal5468_ray_multicast_source_manifest.json"
)
DEFAULT_OUTPUT = (
    APP_DIR / "results" / "librts_goal5468_5469_ray_multicast_feasibility.json"
)


def build_payload() -> dict[str, object]:
    source = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    reference_plan = rt.partitioned_traversal_fanout_plan(
        primitive_ids=range(16),
        ray_ids=range(100, 104),
        partition_count=4,
    )
    sampled_selectivity = rt.estimate_partitioned_traversal_selectivity(
        sampled_hit_count=64,
        sampled_ray_count=8,
        sampled_primitive_count=64,
    )
    cost_model = rt.select_partitioned_traversal_fanout(
        ray_count=4096,
        primitive_count=100000,
        selectivity=sampled_selectivity,
        intersection_cost_weight=0.8,
    )
    return {
        "schema": "rtdl.paper_reproduction.librts.ray_multicast_feasibility.v2",
        "status": (
            "generic_contract_and_non_librts_consumer_complete__"
            "native_optix_pod_spike_authorized__review_pending"
        ),
        "goals": [5468, 5469],
        "author_source_manifest": source,
        "existing_rtdl_assets": [
            "generic prepared OptiX AABB index",
            "prepared box-query GAS",
            "two-pass range-intersection count and pair-row output",
            "prepared multi-operation query execution on independent streams",
            "generic sorted and duplicate-free query/indexed id pair rows"
        ],
        "missing_native_capabilities": [
            "partition-id encoding into disjoint traversal layers",
            "per-ray partition fanout in a two-dimensional OptiX launch",
            "partition-id payload filtering in the intersection program",
            "per-ray intersection-load telemetry",
            "native sampled-selectivity fanout selection"
        ],
        "historical_non_equivalences": [
            "query batching does not partition one traversal workload",
            "multiple CUDA streams do not bound intersections handled by one ray",
            "prepared query replay does not create disjoint traversal layers",
            "status worklists and deferred queues are dynamic scheduling, not static layer fanout"
        ],
        "generic_reference_contract": {
            "fanout": reference_plan,
            "sampled_selectivity": sampled_selectivity,
            "cost_model": cost_model,
            "native_backend": False,
            "runtime_speedup_claimed": False
        },
        "genericity_gate": {
            "generic_capability_produced": True,
            "capability": "partitioned traversal fanout plan and configurable cost selector",
            "requires_app_identity_in_core": False,
            "non_app_consumer": "contact-manifold broad-phase scheduling test",
            "non_app_consumer_complete": True,
            "falsifiable_static_metric": (
                "max primitives assigned to one partition must fall from N to ceil(N/k)"
            ),
            "falsifiable_pod_metric": (
                "exact pair rows must match baseline and candidate end-to-end time must beat k=1"
            ),
            "kill_gate": "pass_for_bounded_native_spike"
        },
        "next_pod_gate": {
            "authorized": True,
            "scope": "generic OptiX partitioned range-intersection spike only",
            "required_controls": [
                "same prepared boxes and query boxes",
                "k=1 baseline",
                "at least two power-of-two k candidates",
                "exact canonical pair-row equality",
                "per-partition and maximum per-ray hit telemetry",
                "fresh and prepared timings reported separately",
                "contact-manifold non-app smoke"
            ],
            "stop_conditions": [
                "pair-row mismatch",
                "host-side partition traversal in measured body",
                "no same-POD end-to-end win over k=1 on a skewed workload",
                "app identity required by native ABI"
            ]
        },
        "claim_boundary": {
            "native_backend_implemented": False,
            "runtime_speedup_measured": False,
            "author_equivalence_claimed": False,
            "figure9_reproduced": False,
            "full_paper_reproduction_claimed": False,
            "embree_in_scope": False
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

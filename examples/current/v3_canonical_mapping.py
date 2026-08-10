"""Inspect one V3 canonical semantic-to-physical mapping without executing it."""

from __future__ import annotations

from rtdsl.canonical_physical_resolution import (
    resolve_canonical_standalone_provider_for_contract,
)


def main() -> None:
    receipt = resolve_canonical_standalone_provider_for_contract(
        statement_stable_id="metric_knn.filter_refine_linf_3d.v1",
        backend_contract_id="nvidia.optix_traversal.v1",
        action_identity={"tutorial_contract": "exact_linf_knn"},
        output_contract={"kind": "exact_ordered_u32_topk"},
        work_domain={"dimensions": 3, "metric": "linf"},
        input_bytes=4096,
        output_bytes=512,
        prepared_bytes=8192,
        logical_cardinality_bound=128,
        pair_cardinality_bound=16_384,
        logical_item_bytes_bound=32,
        pair_item_bytes_bound=8,
        target_identity={"platform": "tutorial-static", "backend": "optix"},
        available_providers=("optix",),
        memory_limit_bytes=1 << 30,
    )

    print(f"status: {receipt['status']}")
    print(f"statement: {receipt['statement']['stable_id']}")
    print(f"backend: {receipt['backend_contract']['stable_id']}")
    print(f"provider: {receipt['provider_candidate_stable_id']}")
    print(f"cost input used: {receipt['cost_or_latency_order_used']}")
    print(f"candidate executed: {receipt['candidate_executed']}")
    print(
        "behavioral receipt still required: "
        f"{receipt['behavioral_traversal_receipt_still_required']}"
    )


if __name__ == "__main__":
    main()

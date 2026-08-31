"""Non-paper consumer of the V4 bounded hierarchy-frontier contract.

This executable example answers a practical question: for every monitoring
station, how many exact peers or accepted remote coverage cells contribute
under a fixed size/distance policy?  It uses the same compiler-owned true-
OptiX physical family as the aggregate-force paper lane but selects the closed
``aggregate_count`` reducer instead of inverse-square force.
"""

from __future__ import annotations

import hashlib

from rtdsl.v4_hierarchy_frontier import (
    HierarchyFrontierSchema,
    HierarchyReducer,
    compile_hierarchy_frontier,
    execute_hierarchy_frontier,
    hierarchy_content_sha256,
)


def run(spec):
    hierarchy = spec.prepared_hierarchy.hierarchy
    schema = HierarchyFrontierSchema(
        producer_contract_sha256=hashlib.sha256(
            b"hierarchical_spatial_coverage_count_v1").hexdigest(),
        hierarchy_sha256=hierarchy_content_sha256(spec),
        reducer=HierarchyReducer.AGGREGATE_COUNT,
        maximum_output_rows=hierarchy.point_count,
        maximum_visits_per_source=hierarchy.node_count * 2 + 1,
    )
    compiled = compile_hierarchy_frontier(spec, schema)
    return execute_hierarchy_frontier(compiled, spec)


__all__ = ("run",)

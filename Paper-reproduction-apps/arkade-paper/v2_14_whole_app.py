"""Arkade V2-direct true-OptiX backport lane.

This lane is application-directed: the caller chooses FR or MT and directly
drives the generic physical metric-kNN executor.  It does not use canonical
resolution, DEFAULT, a compiler planner, or an application-named native symbol.
"""

from __future__ import annotations

from arkade_contract import ArkadeAlgorithm, FrozenArkadeView, independent_oracle
from v2_direct_metric_knn import prepare_v2_direct


def run_v2_direct(
    *,
    algorithm: ArkadeAlgorithm,
    view: FrozenArkadeView,
    data_points,
    query_points,
    data_ids,
    query_ids,
    candidate_provider=None,
) -> dict[str, object]:
    if candidate_provider is not None:
        # Explicit test/reference mode.  It remains independent of the V3
        # compiler module and is never used for a true-OptiX claim.
        result = independent_oracle(
            algorithm,
            data_points,
            query_points,
            k=view.k,
            data_ids=data_ids,
        )
        return {
            **result,
            "query_ids": query_ids.copy(),
            "metadata": {
                "contract": "rtdl.arkade_v2_direct_cpu_model.v1",
                "method": "v2_direct_true_optix_backport",
                "application_selected_paper_algorithm": algorithm.value,
                "default_selected_between_paper_algorithms": False,
                "compiler_or_canonical_resolution_used": False,
                "stock_v2_14_claimed": False,
                "cpu_reference_model_used": True,
                "completed_round_count": 0,
                "native_refit_count": 0,
                "unbounded_candidate_relation_materialized": True,
            },
        }
    with prepare_v2_direct(
        algorithm=algorithm,
        view=view,
        data_points=data_points,
        data_ids=data_ids,
    ) as prepared:
        return prepared.execute(query_points, query_ids=query_ids)


__all__ = ["prepare_v2_direct", "run_v2_direct"]

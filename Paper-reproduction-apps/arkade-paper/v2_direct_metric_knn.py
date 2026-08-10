"""Independent legacy direct adapter for Arkade's prepared OptiX search.

This module deliberately does not import :mod:`rtdsl.metric_knn`.  V2 owns
the paper-algorithm preprocessing and calls the generic native ABI through
the direct physical owner.  V3 reaches the same native family through its
semantic statement, canonical resolution, and compiler-owned prepared plan.
"""

from __future__ import annotations

import math

import numpy as np

from arkade_contract import ArkadeAlgorithm, FrozenArkadeView
from rtdsl.direct_optix_physical import prepare_direct_optix_metric_knn_3d


_METRIC_KIND = {
    ArkadeAlgorithm.FR_LINF: "l_infinity_filter_refine",
    ArkadeAlgorithm.MT_COSINE: "cosine_monotone_transform",
}


def _points(values, *, count: int, name: str) -> np.ndarray:
    result = np.ascontiguousarray(values, dtype=np.float32)
    if result.shape != (count, 3) or not bool(np.all(np.isfinite(result))):
        raise ValueError(f"{name} must be a finite ({count},3) binary32 matrix")
    return result


def _ids(values, *, count: int, name: str) -> np.ndarray:
    result = np.asarray(values)
    if result.shape != (count,) or not bool(np.all(np.isfinite(result))):
        raise ValueError(f"{name} must be a finite ({count},) vector")
    as_i64 = np.ascontiguousarray(result, dtype=np.int64)
    if bool(np.any(as_i64 < 0)) or bool(np.any(as_i64 > (1 << 32) - 1)):
        raise ValueError(f"{name} must fit U32")
    if int(np.unique(as_i64).size) != count:
        raise ValueError(f"{name} must be unique")
    return as_i64.astype(np.uint32, copy=False)


def _normalize(values: np.ndarray, *, name: str) -> np.ndarray:
    semantic = values.astype(np.float64)
    norms = np.linalg.norm(semantic, axis=1)
    if not bool(np.all(np.isfinite(norms))) or bool(np.any(norms == 0.0)):
        raise ValueError(f"{name} contains a zero or invalid vector")
    return np.ascontiguousarray(semantic / norms[:, None], dtype=np.float32)


def _packed(values: np.ndarray, ids: np.ndarray) -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "id": int(item_id),
            "x": float(point[0]),
            "y": float(point[1]),
            "z": float(point[2]),
        }
        for item_id, point in zip(ids, values, strict=True)
    )


class PreparedArkadeV2Direct:
    """Application-directed V2 owner; no V3 compiler or registry is imported."""

    def __init__(
        self,
        *,
        algorithm: ArkadeAlgorithm,
        view: FrozenArkadeView,
        data_points,
        data_ids,
    ) -> None:
        if not isinstance(algorithm, ArkadeAlgorithm):
            raise TypeError("algorithm must be ArkadeAlgorithm")
        data = _points(data_points, count=view.data_count, name="data_points")
        item_ids = _ids(data_ids, count=view.data_count, name="data_ids")
        if algorithm is ArkadeAlgorithm.MT_COSINE:
            data = _normalize(data, name="data_points")
        self._algorithm = algorithm
        self._view = view
        self._owner = prepare_direct_optix_metric_knn_3d(
            _packed(data, item_ids),
            initial_geometric_radius=view.initial_radius,
        )
        self._closed = False

    def execute(self, query_points, *, query_ids) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared Arkade V2-direct owner is closed")
        view = self._view
        queries = _points(
            query_points, count=view.query_count, name="query_points"
        )
        source_ids = _ids(query_ids, count=view.query_count, name="query_ids")
        if self._algorithm is ArkadeAlgorithm.MT_COSINE:
            queries = _normalize(queries, name="query_points")
        native = self._owner.run(
            _packed(queries, source_ids),
            metric_kind=_METRIC_KIND[self._algorithm],
            k=view.k,
            maximum_rounds=32,
        )
        rows = tuple(native["rows"])
        if len(rows) != view.query_count * view.k:
            raise RuntimeError("V2-direct native result has the wrong cardinality")
        ordered_ids = np.empty((view.query_count, view.k), dtype=np.uint32)
        ordered_distances = np.empty((view.query_count, view.k), dtype=np.float64)
        for position, query_id_raw in enumerate(source_ids):
            selected = rows[position * view.k : (position + 1) * view.k]
            if any(int(row[0]) != int(query_id_raw) for row in selected):
                raise RuntimeError("V2-direct native result escaped query order")
            ids = [int(row[1]) for row in selected]
            distances = [float(row[2]) for row in selected]
            if len(set(ids)) != view.k or not all(
                math.isfinite(value) and value >= 0.0 for value in distances
            ):
                raise RuntimeError("V2-direct native result violated exact output contract")
            ordered_ids[position, :] = ids
            ordered_distances[position, :] = distances
        direct_metadata = dict(native["metadata"])
        return {
            "query_ids": source_ids.copy(),
            "ordered_item_ids": ordered_ids,
            "ordered_metric_distances": ordered_distances,
            "metadata": {
                "contract": "rtdl.arkade_v2_direct_prepared_metric_knn.v1",
                "method": "v2_direct_true_optix_backport",
                "application_selected_paper_algorithm": self._algorithm.value,
                "default_selected_between_paper_algorithms": False,
                "compiler_or_canonical_resolution_used": False,
                "stock_v2_14_claimed": False,
                "physical_family": direct_metadata["physical_family"],
                "native_generic_symbol": direct_metadata["native_symbol"],
                "completed_round_count": direct_metadata[
                    "completed_round_count"
                ],
                "native_refit_count": direct_metadata["native_refit_count"],
                "persistent_gas": True,
                "device_metric_filter": True,
                "device_topk": True,
                "unbounded_candidate_relation_materialized": False,
                "direct_physical_metadata": direct_metadata,
            },
        }

    def close(self) -> None:
        if self._closed:
            return
        self._owner.close()
        self._closed = True

    def __enter__(self) -> "PreparedArkadeV2Direct":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def prepare_v2_direct(
    *,
    algorithm: ArkadeAlgorithm,
    view: FrozenArkadeView,
    data_points,
    data_ids,
) -> PreparedArkadeV2Direct:
    return PreparedArkadeV2Direct(
        algorithm=algorithm,
        view=view,
        data_points=data_points,
        data_ids=data_ids,
    )


__all__ = ["PreparedArkadeV2Direct", "prepare_v2_direct"]

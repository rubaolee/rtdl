from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

try:
    import numpy as np
except ModuleNotFoundError:
    class _MissingNumpy:
        def __getattr__(self, name: str):
            raise ModuleNotFoundError(
                "numpy is required for RTDL partner continuation helpers; "
                "use a Python environment with project dependencies installed"
            )

    np = _MissingNumpy()


@dataclass(frozen=True)
class PartnerCandidateRows:
    """Backend-neutral candidate row schema for v2 partner continuations."""

    query_ids: np.ndarray
    primitive_ids: np.ndarray
    values: np.ndarray | None = None
    witness_ids: np.ndarray | None = None

    def normalized(self) -> "PartnerCandidateRows":
        query_ids = np.asarray(self.query_ids, dtype=np.int64)
        primitive_ids = np.asarray(self.primitive_ids, dtype=np.int64)
        if query_ids.shape != primitive_ids.shape:
            raise ValueError("query_ids and primitive_ids must have the same shape")
        values = None if self.values is None else np.asarray(self.values, dtype=np.float64)
        witness_ids = None if self.witness_ids is None else np.asarray(self.witness_ids, dtype=np.int64)
        if values is not None and values.shape != query_ids.shape:
            raise ValueError("values must have the same shape as query_ids")
        if witness_ids is not None and witness_ids.shape != query_ids.shape:
            raise ValueError("witness_ids must have the same shape as query_ids")
        return PartnerCandidateRows(
            query_ids=query_ids,
            primitive_ids=primitive_ids,
            values=values,
            witness_ids=witness_ids,
        )


def _as_i64(values, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=np.int64)
    if array.ndim != 1:
        raise ValueError(f"{name} must be a 1-D array")
    return array


def _as_f64(values, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1:
        raise ValueError(f"{name} must be a 1-D array")
    return array


def _validate_group_count(group_count: int) -> int:
    group_count = int(group_count)
    if group_count < 0:
        raise ValueError("group_count must be non-negative")
    return group_count


def numpy_segmented_count(keys, group_count: int) -> np.ndarray:
    """Count rows per integer key with deterministic NumPy semantics."""

    keys = _as_i64(keys, "keys")
    group_count = _validate_group_count(group_count)
    if keys.size == 0:
        return np.zeros(group_count, dtype=np.int64)
    if np.any(keys < 0) or np.any(keys >= group_count):
        raise ValueError("keys must be in [0, group_count)")
    return np.bincount(keys, minlength=group_count).astype(np.int64, copy=False)


def numpy_segmented_sum(keys, values, group_count: int) -> np.ndarray:
    """Sum values per integer key with deterministic NumPy semantics."""

    keys = _as_i64(keys, "keys")
    values = _as_f64(values, "values")
    group_count = _validate_group_count(group_count)
    if keys.shape != values.shape:
        raise ValueError("keys and values must have the same shape")
    if keys.size == 0:
        return np.zeros(group_count, dtype=np.float64)
    if np.any(keys < 0) or np.any(keys >= group_count):
        raise ValueError("keys must be in [0, group_count)")
    return np.bincount(keys, weights=values, minlength=group_count).astype(np.float64, copy=False)


def numpy_segmented_minmax(keys, values, group_count: int, *, reduce: str) -> np.ndarray:
    """Compute per-key min or max values."""

    if reduce not in {"min", "max"}:
        raise ValueError("reduce must be 'min' or 'max'")
    keys = _as_i64(keys, "keys")
    values = _as_f64(values, "values")
    group_count = _validate_group_count(group_count)
    if keys.shape != values.shape:
        raise ValueError("keys and values must have the same shape")
    initial = np.inf if reduce == "min" else -np.inf
    out = np.full(group_count, initial, dtype=np.float64)
    if keys.size == 0:
        return out
    if np.any(keys < 0) or np.any(keys >= group_count):
        raise ValueError("keys must be in [0, group_count)")
    reducer = np.minimum.at if reduce == "min" else np.maximum.at
    reducer(out, keys, values)
    return out


def numpy_group_topk(
    group_ids,
    item_ids,
    scores,
    *,
    group_count: int,
    k: int,
    largest: bool = False,
) -> dict[str, np.ndarray]:
    """Return deterministic top-k rows per group.

    Tie-break is `score` then `item_id`, ascending for nearest/smallest scores
    and descending score then ascending item id for largest scores.
    """

    group_ids = _as_i64(group_ids, "group_ids")
    item_ids = _as_i64(item_ids, "item_ids")
    scores = _as_f64(scores, "scores")
    group_count = _validate_group_count(group_count)
    k = int(k)
    if k <= 0:
        raise ValueError("k must be positive")
    if not (group_ids.shape == item_ids.shape == scores.shape):
        raise ValueError("group_ids, item_ids, and scores must have the same shape")
    if group_ids.size and (np.any(group_ids < 0) or np.any(group_ids >= group_count)):
        raise ValueError("group_ids must be in [0, group_count)")

    out_group_ids: list[int] = []
    out_item_ids: list[int] = []
    out_scores: list[float] = []
    out_ranks: list[int] = []
    for group in range(group_count):
        mask = group_ids == group
        if not np.any(mask):
            continue
        group_item_ids = item_ids[mask]
        group_scores = scores[mask]
        primary = -group_scores if largest else group_scores
        order = np.lexsort((group_item_ids, primary))[:k]
        for rank, index in enumerate(order, start=1):
            out_group_ids.append(group)
            out_item_ids.append(int(group_item_ids[index]))
            out_scores.append(float(group_scores[index]))
            out_ranks.append(rank)
    return {
        "group_ids": np.asarray(out_group_ids, dtype=np.int64),
        "item_ids": np.asarray(out_item_ids, dtype=np.int64),
        "scores": np.asarray(out_scores, dtype=np.float64),
        "rank": np.asarray(out_ranks, dtype=np.int64),
    }


def numpy_group_argmin_then_global_argmax_with_witness(
    group_ids,
    item_ids,
    values,
    *,
    group_count: int,
) -> dict[str, object]:
    """Compute per-group argmin, then global argmax over those minima."""

    top1 = numpy_group_topk(
        group_ids,
        item_ids,
        values,
        group_count=group_count,
        k=1,
        largest=False,
    )
    if top1["group_ids"].size != group_count:
        missing = sorted(set(range(group_count)) - set(int(v) for v in top1["group_ids"]))
        raise ValueError(f"every group must have at least one candidate; missing groups: {missing}")
    order = np.lexsort((top1["item_ids"], top1["group_ids"], -top1["scores"]))
    winner = int(order[0])
    return {
        "group_id": int(top1["group_ids"][winner]),
        "item_id": int(top1["item_ids"][winner]),
        "value": float(top1["scores"][winner]),
        "per_group_argmin": top1,
        "contract": "generic_group_argmin_then_global_argmax_with_witness",
    }


def point_rows_to_numpy_columns(points) -> dict[str, np.ndarray]:
    rows = tuple(points)
    return {
        "ids": np.asarray([int(point.id) for point in rows], dtype=np.int64),
        "x": np.asarray([float(point.x) for point in rows], dtype=np.float64),
        "y": np.asarray([float(point.y) for point in rows], dtype=np.float64),
    }


def directed_hausdorff_2d_numpy_columns(
    source_point_columns: Mapping[str, object],
    target_point_columns: Mapping[str, object],
    *,
    return_metadata: bool = False,
):
    """Exact directed Hausdorff using generic NumPy partner primitives."""

    source_ids = _as_i64(source_point_columns["ids"], "source ids")
    target_ids = _as_i64(target_point_columns["ids"], "target ids")
    sx = _as_f64(source_point_columns["x"], "source x")
    sy = _as_f64(source_point_columns["y"], "source y")
    tx = _as_f64(target_point_columns["x"], "target x")
    ty = _as_f64(target_point_columns["y"], "target y")
    if not (source_ids.shape == sx.shape == sy.shape):
        raise ValueError("source ids/x/y must have the same shape")
    if not (target_ids.shape == tx.shape == ty.shape):
        raise ValueError("target ids/x/y must have the same shape")
    if source_ids.size == 0 or target_ids.size == 0:
        raise ValueError("directed Hausdorff requires non-empty source and target columns")

    dx = sx.reshape(-1, 1) - tx.reshape(1, -1)
    dy = sy.reshape(-1, 1) - ty.reshape(1, -1)
    distances = np.sqrt(dx * dx + dy * dy)
    group_ids = np.repeat(np.arange(source_ids.size, dtype=np.int64), target_ids.size)
    item_ids = np.tile(target_ids, source_ids.size)
    values = distances.reshape(-1)
    witness = numpy_group_argmin_then_global_argmax_with_witness(
        group_ids,
        item_ids,
        values,
        group_count=int(source_ids.size),
    )
    source_index = int(witness["group_id"])
    nearest = witness["per_group_argmin"]
    columns = {
        "source_ids": source_ids,
        "nearest_target_ids": nearest["item_ids"].astype(np.int64, copy=False),
        "nearest_distances": nearest["scores"].astype(np.float64, copy=False),
    }
    metadata = {
        "adapter": "directed_hausdorff_2d_numpy_columns",
        "partner": "numpy",
        "input_contract": "caller_supplied_partner_host_point_columns",
        "partner_reference_contract": "generic_group_argmin_then_global_argmax_with_witness",
        "native_engine_row_contract": "not_called_partner_reference_only",
        "source_count": int(source_ids.size),
        "target_count": int(target_ids.size),
        "source_id": int(source_ids[source_index]),
        "target_id": int(witness["item_id"]),
        "distance": float(witness["value"]),
        "app_distance_materialization": "partner_numpy_exact_min_then_max_distance_with_witness",
        "direct_device_handoff_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "v2_0_release_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def cupy_group_topk(
    group_ids,
    item_ids,
    scores,
    *,
    group_count: int,
    k: int,
    largest: bool = False,
) -> dict[str, object]:
    """CuPy counterpart of `numpy_group_topk` for pod/device validation."""

    import cupy

    group_ids = cupy.asarray(group_ids, dtype=cupy.int64)
    item_ids = cupy.asarray(item_ids, dtype=cupy.int64)
    scores = cupy.asarray(scores, dtype=cupy.float64)
    group_count = _validate_group_count(group_count)
    k = int(k)
    if k <= 0:
        raise ValueError("k must be positive")
    if not (group_ids.shape == item_ids.shape == scores.shape):
        raise ValueError("group_ids, item_ids, and scores must have the same shape")
    if int(group_ids.size) and bool(cupy.any((group_ids < 0) | (group_ids >= group_count)).item()):
        raise ValueError("group_ids must be in [0, group_count)")

    out_group_ids = []
    out_item_ids = []
    out_scores = []
    out_ranks = []
    for group in range(group_count):
        positions = cupy.where(group_ids == group)[0]
        if int(positions.size) == 0:
            continue
        group_item_ids = item_ids[positions]
        group_scores = scores[positions]
        primary = -group_scores if largest else group_scores
        item_order = cupy.argsort(group_item_ids, kind="stable")
        primary_order = cupy.argsort(primary[item_order], kind="stable")
        order = item_order[primary_order][:k]
        count = int(order.size)
        out_group_ids.append(cupy.full((count,), group, dtype=cupy.int64))
        out_item_ids.append(group_item_ids[order])
        out_scores.append(group_scores[order])
        out_ranks.append(cupy.arange(1, count + 1, dtype=cupy.int64))

    if not out_group_ids:
        return {
            "group_ids": cupy.asarray([], dtype=cupy.int64),
            "item_ids": cupy.asarray([], dtype=cupy.int64),
            "scores": cupy.asarray([], dtype=cupy.float64),
            "rank": cupy.asarray([], dtype=cupy.int64),
        }
    return {
        "group_ids": cupy.concatenate(out_group_ids),
        "item_ids": cupy.concatenate(out_item_ids),
        "scores": cupy.concatenate(out_scores),
        "rank": cupy.concatenate(out_ranks),
    }


def cupy_group_argmin_then_global_argmax_with_witness(
    group_ids,
    item_ids,
    values,
    *,
    group_count: int,
) -> dict[str, object]:
    """CuPy per-group argmin followed by global argmax with witness ids."""

    import cupy

    top1 = cupy_group_topk(
        group_ids,
        item_ids,
        values,
        group_count=group_count,
        k=1,
        largest=False,
    )
    if int(top1["group_ids"].size) != int(group_count):
        present = set(int(value) for value in cupy.asnumpy(top1["group_ids"]).tolist())
        missing = sorted(set(range(int(group_count))) - present)
        raise ValueError(f"every group must have at least one candidate; missing groups: {missing}")
    item_order = cupy.argsort(top1["item_ids"], kind="stable")
    group_order = item_order[cupy.argsort(top1["group_ids"][item_order], kind="stable")]
    score_order = group_order[cupy.argsort((-top1["scores"])[group_order], kind="stable")]
    winner = int(score_order[0].item())
    return {
        "group_id": int(top1["group_ids"][winner].item()),
        "item_id": int(top1["item_ids"][winner].item()),
        "value": float(top1["scores"][winner].item()),
        "per_group_argmin": top1,
        "contract": "generic_group_argmin_then_global_argmax_with_witness",
    }


def directed_hausdorff_2d_cupy_columns(
    source_point_columns: Mapping[str, object],
    target_point_columns: Mapping[str, object],
    *,
    return_metadata: bool = False,
):
    """Exact directed Hausdorff using generic CuPy partner primitives."""

    import cupy

    source_ids = cupy.asarray(source_point_columns["ids"], dtype=cupy.int64)
    target_ids = cupy.asarray(target_point_columns["ids"], dtype=cupy.int64)
    sx = cupy.asarray(source_point_columns["x"], dtype=cupy.float64)
    sy = cupy.asarray(source_point_columns["y"], dtype=cupy.float64)
    tx = cupy.asarray(target_point_columns["x"], dtype=cupy.float64)
    ty = cupy.asarray(target_point_columns["y"], dtype=cupy.float64)
    if not (source_ids.shape == sx.shape == sy.shape):
        raise ValueError("source ids/x/y must have the same shape")
    if not (target_ids.shape == tx.shape == ty.shape):
        raise ValueError("target ids/x/y must have the same shape")
    if int(source_ids.size) == 0 or int(target_ids.size) == 0:
        raise ValueError("directed Hausdorff requires non-empty source and target columns")

    dx = sx.reshape(-1, 1) - tx.reshape(1, -1)
    dy = sy.reshape(-1, 1) - ty.reshape(1, -1)
    distances = cupy.sqrt(dx * dx + dy * dy)
    group_ids = cupy.repeat(cupy.arange(int(source_ids.size), dtype=cupy.int64), int(target_ids.size))
    item_ids = cupy.tile(target_ids, int(source_ids.size))
    values = distances.reshape(-1)
    witness = cupy_group_argmin_then_global_argmax_with_witness(
        group_ids,
        item_ids,
        values,
        group_count=int(source_ids.size),
    )
    nearest = witness["per_group_argmin"]
    source_index = int(witness["group_id"])
    columns = {
        "source_ids": source_ids,
        "nearest_target_ids": nearest["item_ids"].astype(cupy.int64, copy=False),
        "nearest_distances": nearest["scores"].astype(cupy.float64, copy=False),
    }
    metadata = {
        "adapter": "directed_hausdorff_2d_cupy_columns",
        "partner": "cupy",
        "input_contract": "caller_supplied_partner_device_point_columns",
        "partner_reference_contract": "generic_group_argmin_then_global_argmax_with_witness",
        "native_engine_row_contract": "not_called_partner_reference_only",
        "source_count": int(source_ids.size),
        "target_count": int(target_ids.size),
        "source_id": int(source_ids[source_index].item()),
        "target_id": int(witness["item_id"]),
        "distance": float(witness["value"]),
        "app_distance_materialization": "partner_cupy_exact_min_then_max_distance_with_witness",
        "direct_device_handoff_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "v2_0_release_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }
    cupy.cuda.runtime.deviceSynchronize()
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns

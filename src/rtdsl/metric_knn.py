"""App-neutral exact 3-D metric kNN over a prepared true-OptiX traversal.

The module deliberately separates three authorities:

* the application chooses one semantic metric algorithm;
* canonical resolution binds that statement to this one generic physical
  composition;
* the behavioral traversal receipt remains the authority that OptiX actually
  executed.

No application, publication, dataset or benchmark identity participates in
dispatch.  The native physical family owns a persistent refittable GAS and
performs conservative traversal, exact metric filtering and deterministic
bounded top-k on device.  It never materializes the unbounded candidate-pair
relation in Python or on the host.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
from typing import Callable, Mapping, Sequence


METRIC_KNN_EXECUTION_CONTRACT = "rtdl.prepared_metric_knn_3d_optix.v2"
METRIC_KNN_LINF_STATEMENT = "metric_knn.filter_refine_linf_3d.v1"
METRIC_KNN_COSINE_STATEMENT = "metric_knn.monotone_cosine_3d.v1"
METRIC_KNN_EUCLIDEAN_STATEMENT = "metric_knn.filter_refine_euclidean_3d.v1"


class MetricKnnError(RuntimeError):
    """Fail-closed metric-kNN compilation or execution error."""


class MetricKnn3DKind(str, Enum):
    EUCLIDEAN_FILTER_REFINE = "euclidean_filter_refine"
    L_INFINITY_FILTER_REFINE = "l_infinity_filter_refine"
    COSINE_MONOTONE_TRANSFORM = "cosine_monotone_transform"


_STATEMENT_BY_METRIC = {
    MetricKnn3DKind.EUCLIDEAN_FILTER_REFINE: METRIC_KNN_EUCLIDEAN_STATEMENT,
    MetricKnn3DKind.L_INFINITY_FILTER_REFINE: METRIC_KNN_LINF_STATEMENT,
    MetricKnn3DKind.COSINE_MONOTONE_TRANSFORM: METRIC_KNN_COSINE_STATEMENT,
}


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _positive_finite(value: object, *, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be positive and finite")
    return result


@dataclass(frozen=True)
class MetricKnn3DSpec:
    """Complete, resource-bounded semantic contract for one 3-D metric kNN."""

    metric: MetricKnn3DKind
    data_count: int
    query_count: int
    k: int
    initial_geometric_radius: float
    maximum_rounds: int
    maximum_candidate_rows: int

    def __post_init__(self) -> None:
        if not isinstance(self.metric, MetricKnn3DKind):
            raise TypeError("metric must be MetricKnn3DKind")
        for name, value in (
            ("data_count", self.data_count),
            ("query_count", self.query_count),
            ("k", self.k),
            ("maximum_rounds", self.maximum_rounds),
            ("maximum_candidate_rows", self.maximum_candidate_rows),
        ):
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"{name} must be an integer")
        if self.data_count <= 0 or self.data_count > (1 << 32) - 1:
            raise ValueError("data_count must fit positive U32")
        if self.query_count <= 0 or self.query_count > (1 << 32) - 1:
            raise ValueError("query_count must fit positive U32")
        if self.k <= 0 or self.k > min(64, self.data_count):
            raise ValueError("k must be in [1,min(64,data_count)]")
        if self.maximum_rounds <= 0 or self.maximum_rounds > 64:
            raise ValueError("maximum_rounds must be in [1,64]")
        if self.maximum_candidate_rows <= 0:
            raise ValueError("maximum_candidate_rows must be positive")
        if self.maximum_candidate_rows > self.data_count * self.query_count:
            raise ValueError("maximum_candidate_rows exceeds the complete pair domain")
        _positive_finite(
            self.initial_geometric_radius,
            name="initial_geometric_radius",
        )

    @property
    def statement_stable_id(self) -> str:
        return _STATEMENT_BY_METRIC[self.metric]

    def as_dict(self) -> dict[str, object]:
        cosine = self.metric is MetricKnn3DKind.COSINE_MONOTONE_TRANSFORM
        return {
            "metric": self.metric.value,
            "statement_stable_id": self.statement_stable_id,
            "data_count": self.data_count,
            "query_count": self.query_count,
            "k": self.k,
            "initial_geometric_radius": float(self.initial_geometric_radius),
            "maximum_rounds": self.maximum_rounds,
            "maximum_candidate_rows": self.maximum_candidate_rows,
            "radius_boundary": "closed",
            "output_order": ["canonical_binary32_metric_key", "item_id"],
            "input_domain": (
                "finite_nonzero_binary32_vectors_3d"
                if cosine
                else "finite_binary32_points_3d"
            ),
            "metric_transform": (
                "host_verified_unit_normalization_then_l2_squared_binary32"
                if cosine
                else "identity"
            ),
            "input_domain_checked_before_native_prepare_and_launch": True,
            "opaque_callback_allowed": False,
        }

    @property
    def semantic_digest(self) -> str:
        return _digest(self.as_dict())


CandidateProvider = Callable[..., Mapping[str, object]]


def _validated_f32_points(points, *, expected_count: int, name: str):
    import numpy as np

    original = np.asarray(points)
    if original.shape != (expected_count, 3):
        raise ValueError(f"{name} must have shape ({expected_count},3)")
    as_f32 = np.ascontiguousarray(original, dtype=np.float32)
    if not bool(np.all(np.isfinite(as_f32))):
        raise ValueError(f"{name} must contain finite binary32 coordinates")
    return np.ascontiguousarray(as_f32, dtype=np.float64)


def _validated_ids(ids, *, expected_count: int, name: str):
    import numpy as np

    if ids is None:
        return np.arange(expected_count, dtype=np.uint32)
    values = np.asarray(ids)
    if values.shape != (expected_count,):
        raise ValueError(f"{name} must have shape ({expected_count},)")
    if not bool(np.all(np.isfinite(values))):
        raise ValueError(f"{name} must be finite")
    as_i64 = np.ascontiguousarray(values, dtype=np.int64)
    if bool(np.any(as_i64 < 0)) or bool(np.any(as_i64 > (1 << 32) - 1)):
        raise ValueError(f"{name} must fit U32")
    if int(np.unique(as_i64).size) != expected_count:
        raise ValueError(f"{name} must be unique")
    return as_i64.astype(np.uint32, copy=False)


def _normalize_nonzero_rows(points, *, name: str):
    import numpy as np

    norms = np.linalg.norm(points, axis=1)
    if not bool(np.all(np.isfinite(norms))) or bool(np.any(norms == 0.0)):
        raise ValueError(f"{name} contains a zero or invalid vector")
    normalized = points / norms[:, None]
    if not bool(np.all(np.isfinite(normalized))):
        raise ValueError(f"{name} normalization produced invalid coordinates")
    # The native OptiX family consumes float32 points.  Freeze that rounding at
    # the semantic boundary so CPU models and device execution share one
    # transformed coordinate domain.
    return np.ascontiguousarray(normalized, dtype=np.float32).astype(
        np.float64, copy=False
    )


def _prepare_metric_space(metric: MetricKnn3DKind, data, queries):
    if metric in (
        MetricKnn3DKind.EUCLIDEAN_FILTER_REFINE,
        MetricKnn3DKind.L_INFINITY_FILTER_REFINE,
    ):
        return data, queries
    if metric is MetricKnn3DKind.COSINE_MONOTONE_TRANSFORM:
        return (
            _normalize_nonzero_rows(data, name="data_points"),
            _normalize_nonzero_rows(queries, name="query_points"),
        )
    raise AssertionError(metric)


def _prepare_metric_data(metric: MetricKnn3DKind, data):
    if metric is MetricKnn3DKind.COSINE_MONOTONE_TRANSFORM:
        return _normalize_nonzero_rows(data, name="data_points")
    if metric in (
        MetricKnn3DKind.EUCLIDEAN_FILTER_REFINE,
        MetricKnn3DKind.L_INFINITY_FILTER_REFINE,
    ):
        return data
    raise AssertionError(metric)


def _prepare_metric_queries(metric: MetricKnn3DKind, queries):
    if metric is MetricKnn3DKind.COSINE_MONOTONE_TRANSFORM:
        return _normalize_nonzero_rows(queries, name="query_points")
    if metric in (
        MetricKnn3DKind.EUCLIDEAN_FILTER_REFINE,
        MetricKnn3DKind.L_INFINITY_FILTER_REFINE,
    ):
        return queries
    raise AssertionError(metric)


def _metric_distance(metric: MetricKnn3DKind, query, item) -> float:
    import numpy as np

    query_f32 = np.asarray(query, dtype=np.float32)
    item_f32 = np.asarray(item, dtype=np.float32)
    if metric is MetricKnn3DKind.EUCLIDEAN_FILTER_REFINE:
        return float(np.float32(np.linalg.norm(query_f32 - item_f32)))
    if metric is MetricKnn3DKind.L_INFINITY_FILTER_REFINE:
        return float(np.float32(np.max(np.abs(query_f32 - item_f32))))
    if metric is MetricKnn3DKind.COSINE_MONOTONE_TRANSFORM:
        # The MT paper reduction ranks normalized rows by transformed L2.  Use
        # its squared key with explicit binary32 rounding; do not substitute a
        # separately rounded cosine dot product at the physical boundary.
        delta = item_f32 - query_f32
        xy = np.float32(
            np.float32(delta[0] * delta[0])
            + np.float32(delta[1] * delta[1])
        )
        return float(np.float32(xy + np.float32(delta[2] * delta[2])))
    raise AssertionError(metric)


def _inside_exact_geometric_radius(
    metric: MetricKnn3DKind,
    query,
    item,
    radius: float,
) -> bool:
    import numpy as np

    delta = np.asarray(query, dtype=np.float32) - np.asarray(
        item, dtype=np.float32
    )
    radius_f32 = np.float32(radius)
    if metric is MetricKnn3DKind.EUCLIDEAN_FILTER_REFINE:
        return float(np.dot(delta, delta)) <= float(radius_f32 * radius_f32)
    if metric is MetricKnn3DKind.L_INFINITY_FILTER_REFINE:
        return float(np.max(np.abs(delta))) <= float(radius_f32)
    if metric is MetricKnn3DKind.COSINE_MONOTONE_TRANSFORM:
        return float(np.dot(delta, delta)) <= float(radius_f32 * radius_f32)
    raise AssertionError(metric)


def cpu_aabb_candidate_provider_3d(
    *,
    data_points,
    query_points,
    data_ids,
    query_ids,
    geometric_radius: float,
    row_capacity: int,
) -> dict[str, object]:
    """Exact CPU model of the generic inclusive AABB candidate producer."""

    rows: list[tuple[int, int]] = []
    for query_id, query in zip(query_ids, query_points, strict=True):
        for item_id, item in zip(data_ids, data_points, strict=True):
            if all(abs(float(query[axis] - item[axis])) <= geometric_radius for axis in range(3)):
                rows.append((int(query_id), int(item_id)))
                if len(rows) > row_capacity:
                    raise RuntimeError(
                        "metric kNN candidate rows overflowed capacity; failure_mode=fail_closed_overflow"
                    )
    return {
        "candidate_id_rows": tuple(rows),
        "complete_candidate_coverage": True,
        "overflowed": False,
        "backend": "cpu_reference",
        "native_generic_symbol": None,
        "behavioral_traversal_receipt_required": False,
    }


def optix_aabb_candidate_provider_3d(
    *,
    data_points,
    query_points,
    data_ids,
    query_ids,
    geometric_radius: float,
    row_capacity: int,
) -> dict[str, object]:
    """Drive the pre-existing app-neutral true-OptiX 3-D AABB producer."""

    from .optix_runtime import collect_aabb_point_membership_pair_rows_3d_optix

    boxes = tuple(
        (
            int(item_id),
            float(point[0] - geometric_radius),
            float(point[1] - geometric_radius),
            float(point[2] - geometric_radius),
            float(point[0] + geometric_radius),
            float(point[1] + geometric_radius),
            float(point[2] + geometric_radius),
        )
        for item_id, point in zip(data_ids, data_points, strict=True)
    )
    points = tuple(
        (int(query_id), float(point[0]), float(point[1]), float(point[2]))
        for query_id, point in zip(query_ids, query_points, strict=True)
    )
    result = collect_aabb_point_membership_pair_rows_3d_optix(
        boxes,
        points,
        row_capacity=row_capacity,
    )
    if result.get("backend") != "optix":
        raise MetricKnnError("canonical metric kNN provider did not use OptiX")
    body = dict(result)
    body["behavioral_traversal_receipt_required"] = True
    return body


def _packed_point_rows(points, ids) -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "id": int(item_id),
            "x": float(point[0]),
            "y": float(point[1]),
            "z": float(point[2]),
        }
        for item_id, point in zip(ids, points, strict=True)
    )


class PreparedMetricKnnPhysical3D:
    """Prepared app-neutral metric-kNN owner with persistent refittable GAS."""

    def __init__(
        self,
        spec: MetricKnn3DSpec,
        data_points,
        *,
        data_ids=None,
        expected_native_library_identity=None,
        expected_native_library_ref=None,
        _native_library_loader=None,
    ) -> None:
        from .direct_optix_physical import prepare_direct_optix_metric_knn_3d

        if not isinstance(spec, MetricKnn3DSpec):
            raise TypeError("spec must be MetricKnn3DSpec")
        data = _validated_f32_points(
            data_points, expected_count=spec.data_count, name="data_points"
        )
        item_ids = _validated_ids(
            data_ids, expected_count=spec.data_count, name="data_ids"
        )
        # Data-space conversion is preparation work.  Never repeat this O(N)
        # pass in execute(): the physical algorithm keeps the target set and
        # its refittable GAS resident while queries/radii change.
        metric_data = _prepare_metric_data(spec.metric, data)
        self._spec = spec
        self._metric_data = metric_data
        self._item_ids = item_ids
        self._closed = False
        self._owner = prepare_direct_optix_metric_knn_3d(
            _packed_point_rows(metric_data, item_ids),
            initial_geometric_radius=spec.initial_geometric_radius,
            expected_native_library_identity=expected_native_library_identity,
            expected_native_library_ref=expected_native_library_ref,
            _native_library_loader=_native_library_loader,
        )

    def execute(
        self,
        query_points,
        *,
        query_ids=None,
    ) -> dict[str, object]:
        import numpy as np

        if self._closed:
            raise RuntimeError("prepared metric-kNN physical owner is closed")
        spec = self._spec
        queries = _validated_f32_points(
            query_points,
            expected_count=spec.query_count,
            name="query_points",
        )
        source_ids = _validated_ids(
            query_ids, expected_count=spec.query_count, name="query_ids"
        )
        metric_queries = _prepare_metric_queries(spec.metric, queries)
        direct = self._owner.run(
            _packed_point_rows(metric_queries, source_ids),
            metric_kind=spec.metric.value,
            k=spec.k,
            maximum_rounds=spec.maximum_rounds,
        )
        rows = tuple(direct["rows"])
        expected_count = spec.query_count * spec.k
        if len(rows) != expected_count:
            raise MetricKnnError(
                "prepared native metric-kNN result did not contain query_count*k rows"
            )
        ordered_ids = np.empty((spec.query_count, spec.k), dtype=np.uint32)
        ordered_distances = np.empty(
            (spec.query_count, spec.k), dtype=np.float64
        )
        for query_position, query_id_raw in enumerate(source_ids):
            query_id = int(query_id_raw)
            base = query_position * spec.k
            selected = rows[base : base + spec.k]
            if any(int(row[0]) != query_id for row in selected):
                raise MetricKnnError(
                    "prepared native metric-kNN query order escaped the input order"
                )
            neighbor_ids = [int(row[1]) for row in selected]
            distances = [float(row[2]) for row in selected]
            if len(set(neighbor_ids)) != spec.k:
                raise MetricKnnError(
                    "prepared native metric-kNN returned duplicate neighbor ids"
                )
            if not all(math.isfinite(value) and value >= 0.0 for value in distances):
                raise MetricKnnError(
                    "prepared native metric-kNN returned invalid distances"
                )
            ordered_ids[query_position, :] = neighbor_ids
            ordered_distances[query_position, :] = distances
        direct_metadata = dict(direct["metadata"])
        return {
            "query_ids": source_ids.copy(),
            "ordered_item_ids": ordered_ids,
            "ordered_metric_distances": ordered_distances,
            "metadata": {
                "contract": METRIC_KNN_EXECUTION_CONTRACT,
                "metric": spec.metric.value,
                "statement_stable_id": spec.statement_stable_id,
                "semantic_digest": spec.semantic_digest,
                "data_count": spec.data_count,
                "query_count": spec.query_count,
                "k": spec.k,
                "completed_round_count": direct_metadata[
                    "completed_round_count"
                ],
                "final_geometric_radius": direct_metadata[
                    "final_geometric_radius"
                ],
                "native_refit_count": direct_metadata["native_refit_count"],
                "native_generic_symbol": direct_metadata["native_symbol"],
                "physical_family": direct_metadata["physical_family"],
                "persistent_gas": True,
                "device_metric_filter": True,
                "device_topk": True,
                "unbounded_candidate_relation_materialized": False,
                "radius_boundary": "closed",
                "deterministic_output_order": [
                    "canonical_binary32_metric_key",
                    "item_id",
                ],
                "cosine_physical_ranking_key": (
                    "normalized_l2_squared_binary32"
                    if spec.metric is MetricKnn3DKind.COSINE_MONOTONE_TRANSFORM
                    else None
                ),
                "opaque_callback_used": False,
                "application_or_publication_identity_used_for_dispatch": False,
                "compiler_or_canonical_resolution_used": False,
                "behavioral_traversal_receipt_required": True,
                "direct_physical_metadata": direct_metadata,
            },
        }

    def close(self) -> None:
        if self._closed:
            return
        self._owner.close()
        self._closed = True

    def __enter__(self) -> "PreparedMetricKnnPhysical3D":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def prepare_metric_knn_physical_3d(
    spec: MetricKnn3DSpec,
    data_points,
    *,
    data_ids=None,
    expected_native_library_identity=None,
    expected_native_library_ref=None,
    _native_library_loader=None,
) -> PreparedMetricKnnPhysical3D:
    return PreparedMetricKnnPhysical3D(
        spec,
        data_points,
        data_ids=data_ids,
        expected_native_library_identity=expected_native_library_identity,
        expected_native_library_ref=expected_native_library_ref,
        _native_library_loader=_native_library_loader,
    )


def execute_metric_knn_physical_3d(
    spec: MetricKnn3DSpec,
    data_points,
    query_points,
    *,
    data_ids=None,
    query_ids=None,
    candidate_provider: CandidateProvider = optix_aabb_candidate_provider_3d,
) -> dict[str, object]:
    """Execute the common physical composition without compiler authority.

    V2-direct callers intentionally use this entrypoint.  V3 callers use a
    compiled program below, which adds canonical semantic/provider authority
    before reaching the same physical executor.
    """

    import numpy as np

    if not isinstance(spec, MetricKnn3DSpec):
        raise TypeError("spec must be MetricKnn3DSpec")
    if candidate_provider is optix_aabb_candidate_provider_3d:
        with prepare_metric_knn_physical_3d(
            spec,
            data_points,
            data_ids=data_ids,
        ) as prepared:
            return prepared.execute(query_points, query_ids=query_ids)
    data = _validated_f32_points(
        data_points,
        expected_count=spec.data_count,
        name="data_points",
    )
    queries = _validated_f32_points(
        query_points,
        expected_count=spec.query_count,
        name="query_points",
    )
    item_ids = _validated_ids(data_ids, expected_count=spec.data_count, name="data_ids")
    source_ids = _validated_ids(
        query_ids,
        expected_count=spec.query_count,
        name="query_ids",
    )
    metric_data, metric_queries = _prepare_metric_space(spec.metric, data, queries)
    item_position = {int(item_id): index for index, item_id in enumerate(item_ids)}
    query_position = {int(query_id): index for index, query_id in enumerate(source_ids)}
    radius = float(spec.initial_geometric_radius)
    round_receipts: list[dict[str, object]] = []

    for round_index in range(spec.maximum_rounds):
        if not math.isfinite(radius) or radius <= 0.0:
            raise MetricKnnError("metric kNN radius escaped the positive finite contract")
        produced = candidate_provider(
            data_points=metric_data,
            query_points=metric_queries,
            data_ids=item_ids,
            query_ids=source_ids,
            geometric_radius=radius,
            row_capacity=spec.maximum_candidate_rows,
        )
        if produced.get("complete_candidate_coverage") is not True:
            raise MetricKnnError("candidate provider did not prove complete coverage")
        if produced.get("overflowed") not in (False, None):
            raise MetricKnnError("candidate provider overflowed")
        rows = tuple(produced.get("candidate_id_rows", ()))
        if len(rows) > spec.maximum_candidate_rows:
            raise MetricKnnError("candidate provider exceeded the declared row capacity")
        if len(set(rows)) != len(rows):
            raise MetricKnnError("candidate provider returned duplicate identity rows")

        selected: dict[int, list[tuple[float, int]]] = {
            int(query_id): [] for query_id in source_ids
        }
        for raw_query_id, raw_item_id in rows:
            query_id = int(raw_query_id)
            item_id = int(raw_item_id)
            if query_id not in query_position or item_id not in item_position:
                raise MetricKnnError("candidate identity escaped the frozen input domains")
            query = metric_queries[query_position[query_id]]
            item = metric_data[item_position[item_id]]
            if not _inside_exact_geometric_radius(spec.metric, query, item, radius):
                continue
            distance = _metric_distance(spec.metric, query, item)
            if not math.isfinite(distance):
                raise MetricKnnError("exact metric evaluation produced a nonfinite value")
            selected[query_id].append((distance, item_id))

        exact_counts = {query_id: len(values) for query_id, values in selected.items()}
        complete = all(count >= spec.k for count in exact_counts.values())
        round_receipts.append(
            {
                "round_index": round_index,
                "geometric_radius": radius,
                "broadphase_candidate_rows": len(rows),
                "minimum_exact_candidate_count": min(exact_counts.values()),
                "maximum_exact_candidate_count": max(exact_counts.values()),
                "all_queries_have_k": complete,
                "provider_backend": produced.get("backend"),
                "native_generic_symbol": produced.get("native_generic_symbol"),
                "behavioral_traversal_receipt_required": bool(
                    produced.get("behavioral_traversal_receipt_required", False)
                ),
            }
        )
        if complete:
            ordered_ids = np.empty((spec.query_count, spec.k), dtype=np.uint32)
            ordered_distances = np.empty((spec.query_count, spec.k), dtype=np.float64)
            for position, query_id_raw in enumerate(source_ids):
                query_id = int(query_id_raw)
                values = sorted(selected[query_id], key=lambda value: (value[0], value[1]))
                top = values[: spec.k]
                ordered_distances[position, :] = [value[0] for value in top]
                ordered_ids[position, :] = [value[1] for value in top]
            return {
                "query_ids": source_ids.copy(),
                "ordered_item_ids": ordered_ids,
                "ordered_metric_distances": ordered_distances,
                "metadata": {
                    "contract": METRIC_KNN_EXECUTION_CONTRACT,
                    "metric": spec.metric.value,
                    "statement_stable_id": spec.statement_stable_id,
                    "semantic_digest": spec.semantic_digest,
                    "data_count": spec.data_count,
                    "query_count": spec.query_count,
                    "k": spec.k,
                    "completed_round_count": round_index + 1,
                    "final_geometric_radius": radius,
                    "round_receipts": tuple(round_receipts),
                    "candidate_provider_complete": True,
                    "radius_boundary": "closed",
                    "deterministic_output_order": [
                        "canonical_binary32_metric_key",
                        "item_id",
                    ],
                    "opaque_callback_used": False,
                    "application_or_publication_identity_used_for_dispatch": False,
                    "compiler_or_canonical_resolution_used": False,
                },
            }
        radius *= 2.0

    raise MetricKnnError(
        "metric kNN completion exhausted maximum_rounds before every query had k candidates"
    )


@dataclass(frozen=True)
class CompiledMetricKnn3D:
    spec: MetricKnn3DSpec
    canonical_resolution: Mapping[str, object]
    production_authority: Mapping[str, object]

    def _decorate_result(self, result: Mapping[str, object]) -> dict[str, object]:
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "compiler_or_canonical_resolution_used": True,
                "canonical_resolution_receipt_sha256": self.canonical_resolution[
                    "receipt_sha256"
                ],
                "canonical_production_authority_sha256": self.production_authority[
                    "authority_receipt_sha256"
                ],
                "canonical_provider_stable_id": self.canonical_resolution[
                    "provider_candidate_stable_id"
                ],
                "behavioral_traversal_claimed_by_static_resolution": False,
            }
        )
        body = dict(result)
        body["metadata"] = metadata
        return body

    def execute(
        self,
        data_points,
        query_points,
        *,
        data_ids=None,
        query_ids=None,
    ) -> dict[str, object]:
        result = execute_metric_knn_physical_3d(
            self.spec,
            data_points,
            query_points,
            data_ids=data_ids,
            query_ids=query_ids,
            candidate_provider=optix_aabb_candidate_provider_3d,
        )
        return self._decorate_result(result)

    def execute_reference_for_functional_validation(
        self,
        data_points,
        query_points,
        *,
        data_ids=None,
        query_ids=None,
    ) -> dict[str, object]:
        """Run the explicit CPU model without changing production selection.

        This is intentionally not an arbitrary provider hook.  The compiled
        production front door above has exactly one canonical OptiX physical
        plan; tests may request this named reference model only.
        """

        result = execute_metric_knn_physical_3d(
            self.spec,
            data_points,
            query_points,
            data_ids=data_ids,
            query_ids=query_ids,
            candidate_provider=cpu_aabb_candidate_provider_3d,
        )
        body = self._decorate_result(result)
        metadata = dict(body["metadata"])
        metadata["functional_reference_model_used"] = True
        metadata["production_physical_plan_executed"] = False
        body["metadata"] = metadata
        return body

    def prepare(
        self,
        data_points,
        *,
        data_ids=None,
        expected_native_library_identity=None,
        expected_native_library_ref=None,
        _native_library_loader=None,
    ) -> "PreparedCompiledMetricKnn3D":
        physical = prepare_metric_knn_physical_3d(
            self.spec,
            data_points,
            data_ids=data_ids,
            expected_native_library_identity=expected_native_library_identity,
            expected_native_library_ref=expected_native_library_ref,
            _native_library_loader=_native_library_loader,
        )
        return PreparedCompiledMetricKnn3D(self, physical)


class PreparedCompiledMetricKnn3D:
    """Prepared V3 owner retaining canonical compiler authority."""

    def __init__(
        self,
        program: CompiledMetricKnn3D,
        physical: PreparedMetricKnnPhysical3D,
    ) -> None:
        self._program = program
        self._physical = physical
        self._closed = False

    def execute(self, query_points, *, query_ids=None) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared compiled metric-kNN owner is closed")
        return self._program._decorate_result(
            self._physical.execute(query_points, query_ids=query_ids)
        )

    def close(self) -> None:
        if self._closed:
            return
        self._physical.close()
        self._closed = True

    def __enter__(self) -> "PreparedCompiledMetricKnn3D":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def compile_metric_knn_3d(
    spec: MetricKnn3DSpec,
    *,
    target_identity: Mapping[str, object],
    memory_limit_bytes: int,
) -> CompiledMetricKnn3D:
    """Resolve one metric statement to one canonical generic OptiX provider."""

    from .canonical_physical_resolution import (
        bind_canonical_provider_to_direct_provider,
        resolve_canonical_standalone_provider_for_contract,
    )

    if not isinstance(spec, MetricKnn3DSpec):
        raise TypeError("spec must be MetricKnn3DSpec")
    if not isinstance(memory_limit_bytes, int) or memory_limit_bytes <= 0:
        raise ValueError("memory_limit_bytes must be a positive integer")
    resolution = resolve_canonical_standalone_provider_for_contract(
        statement_stable_id=spec.statement_stable_id,
        backend_contract_id="nvidia.optix_traversal.v1",
        action_identity={
            "semantic_digest": spec.semantic_digest,
            "metric": spec.metric.value,
        },
        output_contract={
            "kind": "ordered_metric_knn_rows_3d.v1",
            "k": spec.k,
            "order": ["canonical_binary32_metric_key", "item_id"],
        },
        work_domain={
            "data_count": spec.data_count,
            "query_count": spec.query_count,
            "maximum_candidate_rows": spec.maximum_candidate_rows,
            "maximum_rounds": spec.maximum_rounds,
        },
        input_bytes=(spec.data_count + spec.query_count) * 3 * 4,
        output_bytes=spec.query_count * spec.k * (4 + 8),
        prepared_bytes=spec.data_count * (4 + 6 * 8),
        logical_cardinality_bound=spec.query_count * spec.k,
        pair_cardinality_bound=spec.maximum_candidate_rows,
        logical_item_bytes_bound=12,
        pair_item_bytes_bound=8,
        target_identity=dict(target_identity),
        available_providers=("optix",),
        memory_limit_bytes=memory_limit_bytes,
    )
    provider_id = str(resolution["provider_candidate_stable_id"])
    execution_contract_sha256 = _digest(
        {
            "contract": METRIC_KNN_EXECUTION_CONTRACT,
            "statement_stable_id": spec.statement_stable_id,
            "semantic_digest": spec.semantic_digest,
            "provider_candidate_stable_id": provider_id,
        }
    )
    authority = bind_canonical_provider_to_direct_provider(
        resolution,
        direct_provider_stable_id=provider_id,
        direct_execution_contract_sha256=execution_contract_sha256,
    )
    return CompiledMetricKnn3D(
        spec=spec,
        canonical_resolution=resolution,
        production_authority=authority,
    )


__all__ = [
    "CompiledMetricKnn3D",
    "PreparedCompiledMetricKnn3D",
    "PreparedMetricKnnPhysical3D",
    "METRIC_KNN_COSINE_STATEMENT",
    "METRIC_KNN_EUCLIDEAN_STATEMENT",
    "METRIC_KNN_EXECUTION_CONTRACT",
    "METRIC_KNN_LINF_STATEMENT",
    "MetricKnn3DKind",
    "MetricKnn3DSpec",
    "MetricKnnError",
    "compile_metric_knn_3d",
    "cpu_aabb_candidate_provider_3d",
    "execute_metric_knn_physical_3d",
    "optix_aabb_candidate_provider_3d",
    "prepare_metric_knn_physical_3d",
]

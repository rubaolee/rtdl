from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from .aabb_columns import Aabb2DColumns


AABB_INDEX_2D_OPERATIONS = ("point_contains", "range_contains", "range_intersects")
_COMPILER_AABB_INDEX_2D_OPERATIONS = AABB_INDEX_2D_OPERATIONS + (
    "point_contains_rows",
    "range_intersection_rows",
)
_PRODUCTION_AABB_SEMANTIC_KIND = "prepared_aabb_index_queries_2d.v1"
_PRODUCTION_AABB_CONTRACT_CLASS = "bounded_count_or_pair_rows"
_PRODUCTION_AABB_TEMPLATE = "prepared_optix_aabb_index_query_2d"
EXPANDED_AABB_POINT_MEMBERSHIP_2D_PRIMITIVE = "EXPANDED_AABB_POINT_MEMBERSHIP_2D"
EXPANDED_AABB_POINT_MEMBERSHIP_2D_CONTRACT = "generic_expanded_aabb_point_membership_rows_2d_v1"
EXPANDED_AABB_POINT_MEMBERSHIP_2D_ROW_SCHEMA = ("source_id", "box_id", "metadata_flags")
EXPANDED_AABB_POINT_MEMBERSHIP_METADATA_FLAGS_NONE = 0
AABB_INDEX_2D_CONTRACT = {
    "primitive": "AABB_INDEX_QUERY_2D",
    "behavior": "prepared 2-D axis-aligned bounding-box index with exact predicate refinement",
    "operations": {
        "point_contains": "indexed_box_contains_query_point",
        "point_contains_rows": "emit_query_point_indexed_box_membership_pairs",
        "range_contains": "indexed_box_contains_query_box",
        "range_intersects": "indexed_box_intersects_query_box",
        "range_intersection_rows": "emit_query_box_indexed_box_intersection_pairs",
    },
    "indexed_box_validity": (
        "OptiX range_intersects paths reject indexed boxes that are "
        "not strict after numeric packing (min_x < max_x and min_y < max_y); "
        "point_contains and range_contains retain their inclusive exact predicates "
        "after numeric packing and do not inherit the intersection-only validity guard"
    ),
    "backend_status": {
        "cpu": "reference_uniform_grid_counts_and_intersection_pair_rows",
        "embree": "native_prepared_aabb_collision_counts_with_columnar_fallback",
        "optix": "native_count_point_contains_range_contains_range_intersects_point_contains_rows_and_range_intersection_rows",
        "hiprt": "native_count_point_contains_range_contains_range_intersects",
    },
    "app_boundary": "app-name-free primitive; LibRTS, spatial joins, and collision broadphases may lower to it",
}


@dataclass(frozen=True)
class Point2DLike:
    x: float
    y: float


@dataclass(frozen=True)
class Aabb2D:
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    def __post_init__(self) -> None:
        if self.max_x < self.min_x or self.max_y < self.min_y:
            raise ValueError(f"invalid AABB bounds: {self}")

    def contains_point(self, point: Point2DLike) -> bool:
        return self.min_x <= point.x <= self.max_x and self.min_y <= point.y <= self.max_y

    def contains_box(self, other: "Aabb2D") -> bool:
        return (
            self.min_x <= other.min_x
            and self.min_y <= other.min_y
            and self.max_x >= other.max_x
            and self.max_y >= other.max_y
        )

    def intersects_box(self, other: "Aabb2D") -> bool:
        return (
            other.min_x <= self.max_x
            and other.max_x >= self.min_x
            and other.min_y <= self.max_y
            and other.max_y >= self.min_y
        )


@dataclass(frozen=True)
class _IdentifiedAabb2D:
    id: int
    min_x: float
    min_y: float
    max_x: float
    max_y: float


@dataclass(frozen=True)
class _IdentifiedPoint2D:
    id: int
    x: float
    y: float


class ExpandedAabbPointMembershipOverflowError(RuntimeError):
    """Raised when bounded point/AABB membership row output would overflow."""


@dataclass(frozen=True)
class AabbIndex2D:
    """Prepared CPU reference index for app-name-free 2-D AABB queries."""

    boxes: tuple[Aabb2D, ...]
    resolution: int
    bounds: tuple[float, float, float, float]
    cells: dict[tuple[int, int], tuple[int, ...]]
    candidate_entries: int
    backend: str = "cpu"

    def point_candidates(self, point: Any) -> tuple[int, ...]:
        normalized = _normalize_point2d(point)
        return self.cells.get(_cell_for_point(normalized, self.bounds, self.resolution), ())

    def box_candidates(self, box: Any) -> tuple[int, ...]:
        normalized = _normalize_aabb2d(box)
        candidates: set[int] = set()
        for cell in _cells_for_box(normalized, self.bounds, self.resolution):
            candidates.update(self.cells.get(cell, ()))
        return tuple(sorted(candidates))

    def point_membership_rows(
        self,
        point_queries: Iterable[Any],
        query_ids: tuple[int, ...],
        *,
        indexed_ids: tuple[int, ...],
    ) -> tuple[tuple[int, int], ...]:
        points = tuple(_normalize_point2d(point) for point in point_queries)
        if len(query_ids) != len(points):
            raise ValueError("query_ids length must match point_queries length")
        rows: set[tuple[int, int]] = set()
        for query_index, point in enumerate(points):
            query_id = int(query_ids[query_index])
            for indexed_index in self.point_candidates(point):
                if self.boxes[indexed_index].contains_point(point):
                    rows.add((query_id, int(indexed_ids[indexed_index])))
        return tuple(sorted(rows))

    def count(
        self,
        *,
        point_queries: Iterable[Any] = (),
        box_queries: Iterable[Any] = (),
        operation: str = "all",
    ) -> dict[str, Any]:
        operations = AABB_INDEX_2D_OPERATIONS if operation == "all" else (operation,)
        _validate_operations(operations)
        points = tuple(_normalize_point2d(point) for point in point_queries)
        query_boxes = tuple(_normalize_aabb2d(box) for box in box_queries)
        counts: dict[str, int] = {}
        candidate_checks: dict[str, int] = {}

        query_start = time.perf_counter()
        for name in operations:
            count = 0
            checks = 0
            if name == "point_contains":
                for point in points:
                    candidates = self.point_candidates(point)
                    checks += len(candidates)
                    count += sum(1 for box_id in candidates if self.boxes[box_id].contains_point(point))
            elif name == "range_contains":
                for query_box in query_boxes:
                    candidates = self.box_candidates(query_box)
                    checks += len(candidates)
                    count += sum(1 for box_id in candidates if self.boxes[box_id].contains_box(query_box))
            elif name == "range_intersects":
                for query_box in query_boxes:
                    candidates = self.box_candidates(query_box)
                    checks += len(candidates)
                    count += sum(1 for box_id in candidates if self.boxes[box_id].intersects_box(query_box))
            counts[name] = count
            candidate_checks[name] = checks
        query_sec = time.perf_counter() - query_start

        return {
            "primitive": AABB_INDEX_2D_CONTRACT["primitive"],
            "contract": "generic_prepared_aabb_index_query_2d",
            "backend": self.backend,
            "prepared": True,
            "operation": operation,
            "counts": counts,
            "candidate_checks": candidate_checks,
            "query_counts": {
                "point_queries": len(points),
                "box_queries": len(query_boxes),
            },
            "index": {
                "resolution": self.resolution,
                "bounds": list(self.bounds),
                "occupied_cells": len(self.cells),
                "candidate_entries": self.candidate_entries,
            },
            "run_phases": {
                "query_aabb_index_2d_sec": query_sec,
            },
            "rt_core_accelerated": False,
            "native_engine_customization": False,
            "claim_boundary": (
                "Generic CPU reference AABB_INDEX_QUERY_2D only; not LibRTS-specific, "
                "not native Embree/OptiX execution, and not public speedup wording."
            ),
        }


@dataclass(frozen=True)
class OptixAabbIndex2D:
    """Prepared OptiX AABB index for supported native count queries."""

    boxes: tuple[Aabb2D, ...]
    prepared: Any
    row_ids: tuple[int, ...]
    backend: str = "optix"

    def refit(
        self,
        boxes: Iterable[Any],
        *,
        row_ids: tuple[int, ...],
    ) -> dict[str, object]:
        normalized_boxes = tuple(_normalize_aabb2d(box) for box in boxes)
        if tuple(int(value) for value in row_ids) != self.row_ids:
            raise ValueError("OptiX AABB refit requires unchanged stable row_ids")
        if len(normalized_boxes) != len(self.boxes):
            raise ValueError("OptiX AABB refit requires unchanged box_count")
        records = tuple(
            _IdentifiedAabb2D(
                int(self.row_ids[index]),
                box.min_x,
                box.min_y,
                box.max_x,
                box.max_y,
            )
            for index, box in enumerate(normalized_boxes)
        )
        result = self.prepared.refit(records)
        object.__setattr__(self, "boxes", normalized_boxes)
        return result

    def refit_updates(self, updates: Iterable[tuple[int, Any]]) -> dict[str, object]:
        normalized_updates = tuple(
            (int(row_id), _normalize_aabb2d(box)) for row_id, box in updates
        )
        row_to_slot = {row_id: slot for slot, row_id in enumerate(self.row_ids)}
        missing = sorted(row_id for row_id, _ in normalized_updates if row_id not in row_to_slot)
        if missing:
            raise KeyError(f"OptiX AABB refit update ids are not active: {missing}")
        slots = tuple(row_to_slot[row_id] for row_id, _ in normalized_updates)
        records = tuple(
            _IdentifiedAabb2D(row_id, box.min_x, box.min_y, box.max_x, box.max_y)
            for row_id, box in normalized_updates
        )
        result = self.prepared.refit_slots(slots, records)
        candidate_boxes = list(self.boxes)
        for slot, (_, box) in zip(slots, normalized_updates):
            candidate_boxes[slot] = box
        object.__setattr__(self, "boxes", tuple(candidate_boxes))
        return result

    def count(
        self,
        *,
        point_queries: Iterable[Any] = (),
        box_queries: Iterable[Any] = (),
        operation: str = "all",
    ) -> dict[str, Any]:
        operations = _normalize_requested_operations(operation)
        _validate_optix_operations(operations)
        points = tuple(_normalize_point2d(point) for point in point_queries)
        query_boxes = tuple(_normalize_aabb2d(box) for box in box_queries)

        counts: dict[str, int] = {}
        query_start = time.perf_counter()
        for name in operations:
            if name == "point_contains":
                counts[name] = int(self.prepared.count(point_queries=points, operation=name))
            elif name in {"range_contains", "range_intersects"}:
                counts[name] = int(self.prepared.count(box_queries=query_boxes, operation=name))
        query_sec = time.perf_counter() - query_start

        return {
            "primitive": AABB_INDEX_2D_CONTRACT["primitive"],
            "contract": "generic_prepared_aabb_index_query_2d",
            "backend": self.backend,
            "prepared": True,
            "operation": operation,
            "counts": counts,
            "candidate_checks": None,
            "query_counts": {
                "point_queries": len(points),
                "box_queries": len(query_boxes),
            },
            "index": {
                "indexed_boxes": len(self.boxes),
                "native_index": "optix_custom_aabb_gas",
            },
            "run_phases": {
                "query_aabb_index_2d_sec": query_sec,
            },
            "rt_core_accelerated": True,
            "native_engine_customization": False,
            "claim_boundary": (
                "Generic OptiX AABB_INDEX_QUERY_2D count-only subpath for point_contains, "
                "range_contains, and range_intersects; row output is exposed through "
                "aabb_intersection_pair_rows_2d. Not LibRTS-specific."
            ),
        }

    def intersection_rows(
        self,
        query_boxes: Iterable[Any],
        query_ids: tuple[int, ...],
        *,
        row_capacity: int | None = None,
    ) -> tuple[tuple[int, int], ...]:
        if row_capacity is None:
            raise ValueError("OptiX prepared AABB row output requires explicit row_capacity")
        normalized_query_boxes = tuple(_normalize_aabb2d(box) for box in query_boxes)
        if len(query_ids) != len(normalized_query_boxes):
            raise ValueError("query_ids length must match query_boxes length")
        _validate_u32_ids(query_ids, label="query_ids")
        query_records = tuple(
            _IdentifiedAabb2D(
                int(query_ids[index]),
                box.min_x,
                box.min_y,
                box.max_x,
                box.max_y,
            )
            for index, box in enumerate(normalized_query_boxes)
        )
        native = self.prepared.collect_range_intersection_rows(
            query_records,
            row_capacity=int(row_capacity),
        )
        return tuple(
            sorted((int(query_id), int(indexed_id)) for query_id, indexed_id in native["candidate_id_rows"])
        )

    def point_membership_rows(
        self,
        point_queries: Iterable[Any],
        query_ids: tuple[int, ...],
        *,
        row_capacity: int,
    ) -> tuple[tuple[int, int], ...]:
        points = tuple(_normalize_point2d(point) for point in point_queries)
        if len(query_ids) != len(points):
            raise ValueError("query_ids length must match point_queries length")
        _validate_u32_ids(query_ids, label="query_ids")
        point_records = tuple(
            _IdentifiedPoint2D(
                int(query_ids[index]),
                point.x,
                point.y,
            )
            for index, point in enumerate(points)
        )
        native = self.prepared.collect_point_contains_rows(
            point_records,
            row_capacity=int(row_capacity),
        )
        return tuple(
            sorted((int(query_id), int(indexed_id)) for query_id, indexed_id in native["candidate_id_rows"])
        )

    def close(self) -> None:
        close = getattr(self.prepared, "close", None)
        if callable(close):
            close()


@dataclass(frozen=True)
class HiprtAabbIndex2D:
    """Prepared HIPRT AABB index for supported native count queries."""

    boxes: tuple[Aabb2D, ...]
    prepared: Any
    row_ids: tuple[int, ...]
    backend: str = "hiprt"

    def count(
        self,
        *,
        point_queries: Iterable[Any] = (),
        box_queries: Iterable[Any] = (),
        operation: str = "all",
    ) -> dict[str, Any]:
        operations = _normalize_requested_operations(operation)
        points = tuple(_normalize_point2d(point) for point in point_queries)
        query_boxes = tuple(_normalize_aabb2d(box) for box in box_queries)

        counts: dict[str, int] = {}
        query_start = time.perf_counter()
        for name in operations:
            if name == "point_contains":
                counts[name] = int(self.prepared.count(point_queries=points, operation=name))
            elif name in {"range_contains", "range_intersects"}:
                counts[name] = int(self.prepared.count(box_queries=query_boxes, operation=name))
        query_sec = time.perf_counter() - query_start

        return {
            "primitive": AABB_INDEX_2D_CONTRACT["primitive"],
            "contract": "generic_prepared_aabb_index_query_2d",
            "backend": self.backend,
            "prepared": True,
            "operation": operation,
            "counts": counts,
            "candidate_checks": None,
            "query_counts": {
                "point_queries": len(points),
                "box_queries": len(query_boxes),
            },
            "index": {
                "indexed_boxes": len(self.boxes),
                "native_index": "hiprt_custom_aabb_geometry",
            },
            "run_phases": {
                "query_aabb_index_2d_sec": query_sec,
            },
            "rt_core_accelerated": True,
            "native_engine_customization": False,
            "claim_boundary": (
                "Generic HIPRT AABB_INDEX_QUERY_2D count-only subpath for point_contains, "
                "range_contains, and range_intersects. Evidence may be CUDA/Orochi HIPRT on NVIDIA "
                "until separately validated on AMD hardware; not LibRTS-specific."
            ),
        }

    def close(self) -> None:
        close = getattr(self.prepared, "close", None)
        if callable(close):
            close()


@dataclass(frozen=True)
class EmbreeAabbIndex2D:
    """Prepared Embree AABB query path with native collision traversal when available."""

    boxes: tuple[Aabb2D, ...]
    prepared: Any
    row_ids: tuple[int, ...]
    backend: str = "embree"

    def count(
        self,
        *,
        point_queries: Iterable[Any] = (),
        box_queries: Iterable[Any] = (),
        operation: str = "all",
    ) -> dict[str, Any]:
        operations = _normalize_requested_operations(operation)
        points = tuple(_normalize_point2d(point) for point in point_queries)
        query_boxes = tuple(_normalize_aabb2d(box) for box in box_queries)
        counts: dict[str, int] = {}

        query_start = time.perf_counter()
        native_prepared = bool(getattr(self.prepared, "native_aabb_index", False))
        if native_prepared:
            for name in operations:
                if name == "point_contains":
                    counts[name] = self.prepared.count(point_queries=points, operation=name)
                else:
                    counts[name] = self.prepared.count(box_queries=query_boxes, operation=name)
        else:
            for name in operations:
                count = 0
                if name == "point_contains":
                    for point in points:
                        count += self.prepared.conjunctive_scan_count(_point_contains_clauses(point))
                elif name == "range_contains":
                    for query_box in query_boxes:
                        count += self.prepared.conjunctive_scan_count(_range_contains_clauses(query_box))
                elif name == "range_intersects":
                    for query_box in query_boxes:
                        count += self.prepared.conjunctive_scan_count(_range_intersects_clauses(query_box))
                counts[name] = count
        query_sec = time.perf_counter() - query_start

        return {
            "primitive": AABB_INDEX_2D_CONTRACT["primitive"],
            "contract": "generic_prepared_aabb_index_query_2d",
            "backend": self.backend,
            "prepared": True,
            "operation": operation,
            "counts": counts,
            "candidate_checks": None,
            "query_counts": {
                "point_queries": len(points),
                "box_queries": len(query_boxes),
            },
            "index": {
                "indexed_boxes": len(self.boxes),
                "native_index": (
                    "embree_native_aabb_collision_index"
                    if native_prepared
                    else "embree_generic_columnar_payload"
                ),
                "primary_fields": [] if native_prepared else ["min_x", "min_y", "max_x"],
            },
            "run_phases": {
                "query_aabb_index_2d_sec": query_sec,
            },
            "rt_core_accelerated": False,
            "native_engine_customization": False,
            "claim_boundary": (
                "Generic Embree AABB_INDEX_QUERY_2D count subpath using native "
                "prepared AABB collision traversal when available, with a columnar "
                "fallback for older libraries; not LibRTS-specific and not NVIDIA "
                "RT-core accelerated."
            ),
        }

    def intersection_rows(
        self,
        query_boxes: Iterable[Any],
        query_ids: tuple[int, ...],
    ) -> tuple[tuple[int, int], ...]:
        normalized_query_boxes = tuple(_normalize_aabb2d(box) for box in query_boxes)
        if len(query_ids) != len(normalized_query_boxes):
            raise ValueError("query_ids length must match query_boxes length")
        if bool(getattr(self.prepared, "native_aabb_index", False)):
            _validate_u32_ids(query_ids, label="query_ids")
            query_records = tuple(
                _IdentifiedAabb2D(
                    int(query_ids[index]),
                    box.min_x,
                    box.min_y,
                    box.max_x,
                    box.max_y,
                )
                for index, box in enumerate(normalized_query_boxes)
            )
            native = self.prepared.collect_range_intersection_rows(query_records)
            return tuple(
                sorted((int(query_id), int(indexed_id)) for query_id, indexed_id in native["candidate_id_rows"])
            )
        rows: set[tuple[int, int]] = set()
        for query_index, query_box in enumerate(normalized_query_boxes):
            query_id = int(query_ids[query_index])
            matches = self.prepared.conjunctive_scan(_range_intersects_clauses(query_box))
            rows.update((query_id, int(row["row_id"])) for row in matches)
        return tuple(sorted(rows))

    def point_membership_rows(
        self,
        point_queries: Iterable[Any],
        query_ids: tuple[int, ...],
    ) -> tuple[tuple[int, int], ...]:
        points = tuple(_normalize_point2d(point) for point in point_queries)
        if len(query_ids) != len(points):
            raise ValueError("query_ids length must match point_queries length")
        rows: set[tuple[int, int]] = set()
        for query_index, point in enumerate(points):
            query_id = int(query_ids[query_index])
            matches = self.prepared.conjunctive_scan(_point_contains_clauses(point))
            rows.update((query_id, int(row["row_id"])) for row in matches)
        return tuple(sorted(rows))

    def close(self) -> None:
        close = getattr(self.prepared, "close", None)
        if callable(close):
            close()


def prepare_aabb_index_2d(
    indexed_boxes: Iterable[Any],
    *,
    point_queries: Iterable[Any] = (),
    box_queries: Iterable[Any] = (),
    indexed_ids: Iterable[int] | None = None,
    resolution: int = 32,
    backend: str = "cpu",
    allow_native_update: bool = False,
) -> AabbIndex2D | OptixAabbIndex2D | HiprtAabbIndex2D | EmbreeAabbIndex2D:
    """Prepare an app-name-free 2-D AABB index for point/box query predicates."""

    normalized_backend = _validate_backend(backend)
    box_tuple = tuple(_normalize_aabb2d(box) for box in indexed_boxes)
    point_tuple = tuple(_normalize_point2d(point) for point in point_queries)
    query_box_tuple = tuple(_normalize_aabb2d(box) for box in box_queries)
    if resolution < 1:
        raise ValueError("resolution must be positive")
    if not box_tuple:
        raise ValueError("AABB index requires at least one indexed box")
    indexed_id_tuple = (
        tuple(int(value) for value in indexed_ids)
        if indexed_ids is not None
        else tuple(range(len(box_tuple)))
    )
    if len(indexed_id_tuple) != len(box_tuple):
        raise ValueError("indexed_ids length must match indexed_boxes length")

    if normalized_backend == "optix":
        from .optix_runtime import prepare_optix_aabb_index_2d

        _validate_u32_ids(indexed_id_tuple, label="indexed_ids")
        identified_records = tuple(
            _IdentifiedAabb2D(
                int(indexed_id_tuple[index]),
                box.min_x,
                box.min_y,
                box.max_x,
                box.max_y,
            )
            for index, box in enumerate(box_tuple)
        )
        return OptixAabbIndex2D(
            boxes=box_tuple,
            prepared=prepare_optix_aabb_index_2d(
                identified_records,
                allow_update=bool(allow_native_update),
            ),
            row_ids=indexed_id_tuple,
        )

    if allow_native_update:
        raise ValueError("allow_native_update is supported only by the OptiX backend")

    if normalized_backend == "hiprt":
        from .hiprt_runtime import prepare_hiprt_aabb_index_2d

        _validate_u32_ids(indexed_id_tuple, label="indexed_ids")
        identified_records = tuple(
            _IdentifiedAabb2D(
                int(indexed_id_tuple[index]),
                box.min_x,
                box.min_y,
                box.max_x,
                box.max_y,
            )
            for index, box in enumerate(box_tuple)
        )
        return HiprtAabbIndex2D(
            boxes=box_tuple,
            prepared=prepare_hiprt_aabb_index_2d(identified_records),
            row_ids=indexed_id_tuple,
        )

    if normalized_backend == "embree":
        return _prepare_embree_aabb_index_2d(
            box_tuple,
            row_ids=indexed_id_tuple,
        )

    bounds = _compute_bounds(box_tuple, point_tuple, query_box_tuple)
    mutable_cells: dict[tuple[int, int], list[int]] = {}
    candidate_entries = 0
    for box_id, box in enumerate(box_tuple):
        for cell in _cells_for_box(box, bounds, resolution):
            mutable_cells.setdefault(cell, []).append(box_id)
            candidate_entries += 1

    return AabbIndex2D(
        boxes=box_tuple,
        resolution=resolution,
        bounds=bounds,
        cells={cell: tuple(box_ids) for cell, box_ids in mutable_cells.items()},
        candidate_entries=candidate_entries,
        backend=normalized_backend,
    )


def prepare_aabb_index_2d_columns(
    columns: Aabb2DColumns | Mapping[str, object],
    *,
    point_queries: Iterable[Any] = (),
    box_queries: Iterable[Any] = (),
    indexed_ids: Iterable[int] | None = None,
    resolution: int = 32,
    backend: str = "cpu",
    allow_native_update: bool = False,
) -> AabbIndex2D | OptixAabbIndex2D | HiprtAabbIndex2D | EmbreeAabbIndex2D:
    """Prepare a generic 2-D AABB index from validated host columns.

    The OptiX path preserves the columns through native packing and avoids
    constructing one Python Aabb2D/_IdentifiedAabb2D object per indexed row.
    CPU and other backends retain the existing row-shaped reference path.
    """
    columnar = (
        columns
        if isinstance(columns, Aabb2DColumns)
        else Aabb2DColumns.from_mapping(columns, indexed_ids=indexed_ids)
    )
    normalized_backend = _validate_backend(backend)
    if normalized_backend != "optix":
        return prepare_aabb_index_2d(
            tuple(columnar),
            point_queries=point_queries,
            box_queries=box_queries,
            indexed_ids=columnar.ids,
            resolution=resolution,
            backend=normalized_backend,
            allow_native_update=allow_native_update,
        )
    if len(columnar) == 0:
        raise ValueError("AABB index requires at least one indexed box")
    from .optix_runtime import prepare_optix_aabb_index_2d

    return OptixAabbIndex2D(
        boxes=columnar,
        prepared=prepare_optix_aabb_index_2d(
            columnar,
            allow_update=bool(allow_native_update),
        ),
        row_ids=columnar.ids,
    )


@dataclass
class CompilerPreparedAabbIndex2D:
    """Compiler-selected prepared AABB owner without an application backend knob."""

    owner: Any
    target_profile: Any
    requested_operations: tuple[str, ...]
    selected_backend: str
    fallback_rejections: tuple[tuple[str, str], ...]
    production_plan: Mapping[str, object]
    production_binding: Mapping[str, object]
    canonical_resolution: Mapping[str, object] | None
    canonical_production_authority: Mapping[str, object] | None
    max_query_count: int
    max_output_rows: int
    closed: bool = False

    def count(self, **kwargs) -> dict[str, Any]:
        if self.closed:
            raise RuntimeError("compiler-prepared AABB owner is closed")
        return self.owner.count(**kwargs)

    def intersection_rows(self, *args, **kwargs):
        if self.closed:
            raise RuntimeError("compiler-prepared AABB owner is closed")
        method = getattr(self.owner, "intersection_rows", None)
        if not callable(method):
            raise RuntimeError("compiler-selected AABB owner cannot emit intersection rows")
        return method(*args, **kwargs)

    def point_membership_rows(self, *args, **kwargs):
        if self.closed:
            raise RuntimeError("compiler-prepared AABB owner is closed")
        method = getattr(self.owner, "point_membership_rows", None)
        if not callable(method):
            raise RuntimeError("compiler-selected AABB owner cannot emit point-membership rows")
        return method(*args, **kwargs)

    def close(self) -> None:
        if self.closed:
            return
        try:
            close = getattr(self.owner, "close", None)
            if callable(close):
                close()
        finally:
            self.closed = True

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": "rtdl.compiler_prepared_aabb_index_2d.private_candidate.v1",
            "target_profile": self.target_profile.to_metadata(),
            "requested_operations": list(self.requested_operations),
            "selected_backend": self.selected_backend,
            "fallback_rejections": [
                {"backend": backend, "reason": reason}
                for backend, reason in self.fallback_rejections
            ],
            "production_default_plan": dict(self.production_plan),
            "production_default_binding": dict(self.production_binding),
            "canonical_resolution": (
                dict(self.canonical_resolution)
                if self.canonical_resolution is not None
                else None
            ),
            "canonical_production_authority": (
                dict(self.canonical_production_authority)
                if self.canonical_production_authority is not None
                else None
            ),
            "max_query_count": self.max_query_count,
            "max_output_rows": self.max_output_rows,
            "fixed_priority_legal_order": None,
            "compiler_owned": True,
            "application_selected_backend": False,
            "closed": self.closed,
            "runtime_speedup_claimed": False,
        }

    def __enter__(self):
        if self.closed:
            raise RuntimeError("compiler-prepared AABB owner is closed")
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")
    ).hexdigest()


def _compile_aabb_index_production_default(
    *,
    indexed_count: int,
    operations: tuple[str, ...],
    max_query_count: int,
    max_output_rows: int,
    semantic_statement_stable_id: str | None = None,
    backend_contract_id: str | None = None,
) -> tuple[
    object,
    dict[str, object],
    dict[str, object],
    str,
    Mapping[str, object] | None,
    Mapping[str, object] | None,
]:
    """Select and bind the generic prepared-AABB query implementation.

    This compiler front door accepts only semantic/resource facts.  It never
    receives an application, dataset, candidate, backend, template, or
    program override.  Counts stream a bounded scalar result; row-producing
    operations are bounded by the caller-declared fail-closed row capacity.
    """

    for field, value in (
        ("indexed_count", indexed_count),
        ("max_query_count", max_query_count),
        ("max_output_rows", max_output_rows),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{field} must be a nonnegative integer")
    if indexed_count == 0:
        raise ValueError("prepared AABB DEFAULT requires at least one indexed box")
    if max_query_count == 0:
        raise ValueError("prepared AABB DEFAULT requires a positive max_query_count")
    if not operations or any(
        operation not in _COMPILER_AABB_INDEX_2D_OPERATIONS
        for operation in operations
    ):
        raise ValueError("prepared AABB DEFAULT operation set is invalid")
    row_operations = {
        "point_contains_rows",
        "range_intersection_rows",
    }.intersection(operations)
    if row_operations and max_output_rows == 0:
        raise ValueError("row-producing prepared AABB DEFAULT requires max_output_rows")
    if not row_operations and max_output_rows != 0:
        raise ValueError("count-only prepared AABB DEFAULT cannot declare row output")
    pair_count = indexed_count * max_query_count
    if pair_count >= 1 << 64:
        raise ValueError("prepared AABB DEFAULT pair bound exceeds uint64")

    from .action_api import detect_action_target_profile
    from .default_physical_selection import current_registry_snapshot
    from .production_default_integration import (
        bind_default_plan_to_lowering,
        compile_production_default_plan,
        make_production_action_descriptor,
        make_production_target_descriptor,
    )

    target = detect_action_target_profile(cpu_reference_available=False)
    if not target.optix_available or target.device_memory_limit_bytes is None:
        raise RuntimeError("NO_LEGAL_CANDIDATE: prepared AABB true-OptiX target unavailable")
    providers = ["optix"]
    action_contract = {
        "schema": "rtdl.production.prepared_aabb_index_query_2d.v1",
        "semantic_kind": _PRODUCTION_AABB_SEMANTIC_KIND,
        "contract_class": _PRODUCTION_AABB_CONTRACT_CLASS,
        "operations": list(operations),
        "inclusive_exact_predicates": True,
        "bounded_output": True,
    }
    output_bytes = (
        max_output_rows * 16 if row_operations else max(8, len(operations) * 8)
    )
    action = make_production_action_descriptor(
        semantic_kind=_PRODUCTION_AABB_SEMANTIC_KIND,
        action_contract_class=_PRODUCTION_AABB_CONTRACT_CLASS,
        action_semantic_digest=_canonical_sha256(action_contract),
        output_contract={
            "operations": list(operations),
            "row_order": "canonical_query_then_indexed_id",
            "overflow": "fail_closed",
            "output_bytes": output_bytes,
        },
        work_domain={
            "indexed_count": indexed_count,
            "max_query_count": max_query_count,
            "max_output_rows": max_output_rows,
            "pair_interaction_bound": pair_count,
        },
        input_bytes=indexed_count * 40 + max_query_count * 40,
        output_bytes=output_bytes,
        prepared_bytes=indexed_count * 40,
        logical_cardinality_bound=max(indexed_count, max_query_count),
        pair_cardinality_bound=pair_count,
        logical_item_bytes_bound=40,
        pair_item_bytes_bound=16,
    )
    target_descriptor = make_production_target_descriptor(
        target_identity={
            "target_profile": target.to_metadata(),
            "semantic_kind": _PRODUCTION_AABB_SEMANTIC_KIND,
            "mandatory_nvidia_rt": True,
        },
        available_providers=providers,
        memory_limit_bytes=int(target.device_memory_limit_bytes),
        mandatory_nvidia_rt=True,
    )
    if (semantic_statement_stable_id is None) != (backend_contract_id is None):
        raise ValueError(
            "canonical semantic statement and backend contract are required together"
        )
    canonical_resolution = None
    canonical_authority = None
    if semantic_statement_stable_id is not None:
        from .canonical_physical_resolution import (
            CanonicalPhysicalResolutionError,
            registered_backend_contract,
            registered_semantic_statement,
            resolve_canonical_provider,
        )

        statement = registered_semantic_statement(semantic_statement_stable_id)
        backend_contract = registered_backend_contract(backend_contract_id)
        canonical_resolution = resolve_canonical_provider(
            statement_stable_id=statement.stable_id,
            expected_statement_sha256=statement.digest,
            backend_contract_id=backend_contract.stable_id,
            expected_backend_contract_sha256=backend_contract.digest,
            action=action,
            target=target_descriptor,
        )
        if canonical_resolution.get("status") != "RESOLVED":
            raise CanonicalPhysicalResolutionError(
                str(canonical_resolution.get("error_code", "FAIL_CLOSED")),
                str(canonical_resolution.get("error_detail", "")),
            )
    plan = compile_production_default_plan(
        action,
        target_descriptor,
        mandatory_nvidia_rt=True,
        repository_root=Path(__file__).resolve().parents[2],
    )
    winner = str(plan["selected_candidate_stable_id"])
    declaration = next(
        row
        for row in current_registry_snapshot().declarations
        if row.stable_id == winner
    )
    if declaration.backend != "optix" or declaration.template != _PRODUCTION_AABB_TEMPLATE:
        raise RuntimeError("prepared AABB DEFAULT selected an unsupported physical route")
    binding = bind_default_plan_to_lowering(
        plan,
        actual_backend=declaration.backend,
        actual_template=declaration.template,
        repository_root=Path(__file__).resolve().parents[2],
    )
    if canonical_resolution is not None:
        from .canonical_physical_resolution import (
            bind_canonical_provider_to_materialized_plan,
        )

        canonical_authority = bind_canonical_provider_to_materialized_plan(
            canonical_resolution,
            materialized_provider_stable_id=winner,
            materialized_plan_sha256=plan["production_plan_sha256"],
            materialized_binding_sha256=binding["binding_sha256"],
        )
    return (
        target,
        plan,
        binding,
        declaration.backend,
        canonical_resolution,
        canonical_authority,
    )


def prepare_compiler_aabb_index_2d_columns(
    columns: Aabb2DColumns | Mapping[str, object],
    *,
    operations: Iterable[str],
    indexed_ids: Iterable[int] | None = None,
    resolution: int = 32,
    max_query_count: int,
    max_output_rows: int = 0,
    semantic_statement_stable_id: str | None = None,
    backend_contract_id: str | None = None,
) -> CompilerPreparedAabbIndex2D:
    """Select through production DEFAULT and prepare one generic AABB owner."""

    requested = tuple(dict.fromkeys(str(value) for value in operations))
    if not requested:
        raise ValueError("at least one AABB operation is required")
    columnar = (
        columns
        if isinstance(columns, Aabb2DColumns)
        else Aabb2DColumns.from_mapping(columns, indexed_ids=indexed_ids)
    )
    target, plan, binding, backend, canonical_resolution, canonical_authority = (
        _compile_aabb_index_production_default(
        indexed_count=len(columnar),
        operations=requested,
        max_query_count=max_query_count,
        max_output_rows=max_output_rows,
        semantic_statement_stable_id=semantic_statement_stable_id,
        backend_contract_id=backend_contract_id,
        )
    )
    owner = prepare_aabb_index_2d_columns(
        columnar,
        indexed_ids=columnar.ids,
        resolution=resolution,
        backend=backend,
    )
    return CompilerPreparedAabbIndex2D(
        owner=owner,
        target_profile=target,
        requested_operations=requested,
        selected_backend=backend,
        fallback_rejections=(),
        production_plan=plan,
        production_binding=binding,
        canonical_resolution=canonical_resolution,
        canonical_production_authority=canonical_authority,
        max_query_count=max_query_count,
        max_output_rows=max_output_rows,
    )


def compiler_expanded_aabb_point_membership_rows_2d(
    indexed_boxes: Iterable[Any],
    source_points: Iterable[Any],
    **kwargs,
) -> dict[str, Any]:
    """Compiler-owned placement for generic expanded-AABB membership rows."""

    if "backend" in kwargs:
        raise ValueError("compiler expanded-AABB front door does not accept a backend")
    indexed = tuple(indexed_boxes)
    sources = tuple(source_points)
    row_capacity = kwargs.get("row_capacity")
    resolved_capacity = (
        len(indexed) * len(sources)
        if row_capacity is None
        else int(row_capacity)
    )
    target, plan, binding, backend, canonical_resolution, canonical_authority = (
        _compile_aabb_index_production_default(
        indexed_count=len(indexed),
        operations=("point_contains_rows",),
        max_query_count=len(sources),
        max_output_rows=resolved_capacity,
        )
    )
    result = expanded_aabb_point_membership_rows_2d(
        indexed,
        sources,
        backend=backend,
        **kwargs,
    )
    return {
        **result,
        "compiler_plan": {
            "contract": "rtdl.compiler_expanded_aabb_membership_plan.production_default.v2",
            "target_profile": target.to_metadata(),
            "selected_backend": backend,
            "fallback_rejections": [],
            "production_default_plan": plan,
            "production_default_binding": binding,
            "canonical_resolution": canonical_resolution,
            "canonical_production_authority": canonical_authority,
            "fixed_priority_legal_order": None,
            "compiler_owned": True,
            "application_selected_backend": False,
            "runtime_speedup_claimed": False,
        },
    }


def query_aabb_index_2d(
    indexed_boxes: Iterable[Any],
    *,
    point_queries: Iterable[Any] = (),
    box_queries: Iterable[Any] = (),
    operation: str = "all",
    resolution: int = 32,
    backend: str = "cpu",
) -> dict[str, Any]:
    """Prepare and query a 2-D AABB index in one call."""

    normalized_backend = _validate_backend(backend)
    operations = _normalize_requested_operations(operation)
    if normalized_backend == "optix":
        _validate_optix_operations(operations)
    prepared = prepare_aabb_index_2d(
        indexed_boxes,
        point_queries=point_queries,
        box_queries=box_queries,
        resolution=resolution,
        backend=normalized_backend,
    )
    try:
        return prepared.count(point_queries=point_queries, box_queries=box_queries, operation=operation)
    finally:
        if isinstance(prepared, (EmbreeAabbIndex2D, OptixAabbIndex2D, HiprtAabbIndex2D)):
            prepared.close()


def aabb_intersection_pair_rows_2d(
    indexed_boxes: Iterable[Any],
    query_boxes: Iterable[Any],
    *,
    indexed_ids: Iterable[int] | None = None,
    query_ids: Iterable[int] | None = None,
    resolution: int = 32,
    backend: str = "cpu",
    row_capacity: int | None = None,
) -> dict[str, Any]:
    """Emit generic 2-D AABB intersection candidate-pair rows.

    The row contract is intentionally geometry-generic: each output row is
    ``(query_id, indexed_id)`` when a query AABB intersects an indexed AABB.
    Downstream apps may refine those broadphase rows with app-owned predicates.
    For the OptiX backend, ``row_capacity`` is required and must accommodate
    the raw pre-deduplication bidirectional-pass hit count, which can be up to
    twice the final unique pair count.
    """

    normalized_backend = _validate_backend(backend)
    indexed_tuple = tuple(_normalize_aabb2d(box) for box in indexed_boxes)
    query_tuple = tuple(_normalize_aabb2d(box) for box in query_boxes)
    if not query_tuple:
        raise ValueError("AABB intersection pair rows require at least one query box")
    indexed_id_tuple = (
        tuple(int(value) for value in indexed_ids)
        if indexed_ids is not None
        else tuple(range(len(indexed_tuple)))
    )
    query_id_tuple = (
        tuple(int(value) for value in query_ids)
        if query_ids is not None
        else tuple(range(len(query_tuple)))
    )
    if len(indexed_id_tuple) != len(indexed_tuple):
        raise ValueError("indexed_ids length must match indexed_boxes length")
    if len(query_id_tuple) != len(query_tuple):
        raise ValueError("query_ids length must match query_boxes length")

    all_pairs_count = len(indexed_tuple) * len(query_tuple)
    if normalized_backend == "optix":
        if row_capacity is None:
            raise ValueError("OptiX AABB row output requires explicit row_capacity")
        resolved_row_capacity = int(row_capacity)
        if resolved_row_capacity < 0:
            raise ValueError("row_capacity must be non-negative")
        _validate_u32_ids(indexed_id_tuple, label="indexed_ids")
        _validate_u32_ids(query_id_tuple, label="query_ids")
        indexed_records = tuple(
            _IdentifiedAabb2D(
                int(indexed_id_tuple[index]),
                box.min_x,
                box.min_y,
                box.max_x,
                box.max_y,
            )
            for index, box in enumerate(indexed_tuple)
        )
        query_records = tuple(
            _IdentifiedAabb2D(
                int(query_id_tuple[index]),
                box.min_x,
                box.min_y,
                box.max_x,
                box.max_y,
            )
            for index, box in enumerate(query_tuple)
        )

        from .optix_runtime import collect_aabb_intersection_pair_rows_2d_optix

        row_start = time.perf_counter()
        native = collect_aabb_intersection_pair_rows_2d_optix(
            indexed_records,
            query_records,
            row_capacity=resolved_row_capacity,
        )
        row_query_sec = time.perf_counter() - row_start
        rows = tuple(sorted((int(query_id), int(indexed_id)) for query_id, indexed_id in native["candidate_id_rows"]))

        return {
            "primitive": AABB_INDEX_2D_CONTRACT["primitive"],
            "contract": "generic_aabb_intersection_pair_rows_2d",
            "backend": normalized_backend,
            "prepared": True,
            "operation": "range_intersection_rows",
            "row_schema": ("query_id", "indexed_id"),
            "candidate_id_rows": rows,
            "valid_count": len(rows),
            "indexed_box_count": len(indexed_tuple),
            "query_box_count": len(query_tuple),
            "candidate_checks": None,
            "all_pairs_count": all_pairs_count,
            "candidate_checks_avoided": None,
            "pruning_ratio": None,
            "row_capacity": resolved_row_capacity,
            "complete_candidate_coverage": bool(native["complete_candidate_coverage"]),
            "index": {
                "indexed_boxes": len(indexed_tuple),
                "native_index": "optix_custom_aabb_gas",
            },
            "run_phases": {
                "prepare_and_emit_aabb_intersection_pair_rows_2d_sec": row_query_sec,
            },
            "rt_core_accelerated": True,
            "native_engine_customization": False,
            "native_generic_symbol": native["native_generic_symbol"],
            "claim_boundary": (
                "Generic OptiX AABB_INDEX_QUERY_2D broadphase row output only; exact app "
                "semantics and final witness interpretation remain outside the engine."
            ),
        }

    if normalized_backend == "embree":
        _validate_u32_ids(indexed_id_tuple, label="indexed_ids")
        _validate_u32_ids(query_id_tuple, label="query_ids")
        prepare_start = time.perf_counter()
        prepared_embree = _prepare_embree_aabb_index_2d(
            indexed_tuple,
            row_ids=indexed_id_tuple,
        )
        prepare_sec = time.perf_counter() - prepare_start
        row_start = time.perf_counter()
        try:
            rows = prepared_embree.intersection_rows(query_tuple, query_id_tuple)
        finally:
            prepared_embree.close()
        row_query_sec = time.perf_counter() - row_start

        return {
            "primitive": AABB_INDEX_2D_CONTRACT["primitive"],
            "contract": "generic_aabb_intersection_pair_rows_2d",
            "backend": normalized_backend,
            "prepared": True,
            "operation": "range_intersection_rows",
            "row_schema": ("query_id", "indexed_id"),
            "candidate_id_rows": rows,
            "valid_count": len(rows),
            "indexed_box_count": len(indexed_tuple),
            "query_box_count": len(query_tuple),
            "candidate_checks": None,
            "all_pairs_count": all_pairs_count,
            "candidate_checks_avoided": None,
            "pruning_ratio": None,
            "complete_candidate_coverage": True,
            "index": {
                "indexed_boxes": len(indexed_tuple),
                "native_index": (
                    "embree_native_aabb_collision_index"
                    if bool(getattr(prepared_embree.prepared, "native_aabb_index", False))
                    else "embree_generic_columnar_payload"
                ),
                "primary_fields": (
                    []
                    if bool(getattr(prepared_embree.prepared, "native_aabb_index", False))
                    else ["min_x", "min_y", "max_x"]
                ),
            },
            "run_phases": {
                "prepare_aabb_index_2d_sec": prepare_sec,
                "emit_aabb_intersection_pair_rows_2d_sec": row_query_sec,
            },
            "rt_core_accelerated": False,
            "native_engine_customization": False,
            "native_generic_symbol": (
                "rtdl_embree_collect_prepared_aabb_index_2d_range_intersection_rows"
                if bool(getattr(prepared_embree.prepared, "native_aabb_index", False))
                else "rtdl_embree_columnar_payload_multi_predicate_scan"
            ),
            "claim_boundary": (
                "Generic Embree AABB_INDEX_QUERY_2D broadphase row output lowered to "
                "the app-agnostic prepared AABB collision primitive when available, "
                "with a columnar conjunctive-scan fallback; exact app "
                "semantics and final witness interpretation remain outside the engine."
            ),
        }

    prepare_start = time.perf_counter()
    prepared = prepare_aabb_index_2d(
        indexed_tuple,
        box_queries=query_tuple,
        resolution=resolution,
        backend=normalized_backend,
    )
    prepare_sec = time.perf_counter() - prepare_start
    if not isinstance(prepared, AabbIndex2D):
        raise TypeError("CPU AABB row output expected AabbIndex2D")

    row_start = time.perf_counter()
    rows: set[tuple[int, int]] = set()
    candidate_checks = 0
    for query_index, query_box in enumerate(query_tuple):
        candidates = prepared.box_candidates(query_box)
        candidate_checks += len(candidates)
        query_id = query_id_tuple[query_index]
        for indexed_index in candidates:
            indexed_box = prepared.boxes[indexed_index]
            if indexed_box.intersects_box(query_box):
                rows.add((query_id, indexed_id_tuple[indexed_index]))
    row_query_sec = time.perf_counter() - row_start

    return {
        "primitive": AABB_INDEX_2D_CONTRACT["primitive"],
        "contract": "generic_aabb_intersection_pair_rows_2d",
        "backend": normalized_backend,
        "prepared": True,
        "operation": "range_intersection_rows",
        "row_schema": ("query_id", "indexed_id"),
        "candidate_id_rows": tuple(sorted(rows)),
        "valid_count": len(rows),
        "indexed_box_count": len(indexed_tuple),
        "query_box_count": len(query_tuple),
        "candidate_checks": candidate_checks,
        "all_pairs_count": all_pairs_count,
        "candidate_checks_avoided": max(0, all_pairs_count - candidate_checks),
        "pruning_ratio": (
            0.0
            if all_pairs_count == 0
            else max(0.0, 1.0 - (candidate_checks / float(all_pairs_count)))
        ),
        "complete_candidate_coverage": True,
        "index": {
            "resolution": prepared.resolution,
            "bounds": list(prepared.bounds),
            "occupied_cells": len(prepared.cells),
            "candidate_entries": prepared.candidate_entries,
        },
        "run_phases": {
            "prepare_aabb_index_2d_sec": prepare_sec,
            "emit_aabb_intersection_pair_rows_2d_sec": row_query_sec,
        },
        "rt_core_accelerated": False,
        "native_engine_customization": False,
        "claim_boundary": (
            "Generic CPU AABB_INDEX_QUERY_2D broadphase row output only; exact app "
            "semantics and final witness interpretation remain outside the engine. "
            "OptiX row output follows the same app-agnostic row contract when the native "
            "backend symbol is available."
        ),
    }


def expanded_aabb_point_membership_rows_2d(
    indexed_boxes: Iterable[Any],
    source_points: Iterable[Any],
    *,
    expansions: float | Iterable[float] = 0.0,
    indexed_ids: Iterable[int] | None = None,
    source_ids: Iterable[int] | None = None,
    max_rows_per_source: int | None = None,
    row_capacity: int | None = None,
    resolution: int = 32,
    backend: str = "cpu",
) -> dict[str, Any]:
    """Emit generic bounded rows for points inside expanded 2-D AABBs.

    The primitive is intentionally app-agnostic: indexed boxes may represent
    tree nodes, spatial cells, broadphase bins, or any other caller-owned box
    table. The engine only emits ``(source_id, box_id, metadata_flags)`` rows.
    """

    normalized_backend = _validate_backend(backend)
    box_tuple = tuple(_normalize_aabb2d(box) for box in indexed_boxes)
    point_tuple = tuple(_normalize_point2d(point) for point in source_points)
    if not box_tuple:
        raise ValueError("EXPANDED_AABB_POINT_MEMBERSHIP_2D requires at least one indexed box")
    indexed_id_tuple = (
        tuple(int(value) for value in indexed_ids)
        if indexed_ids is not None
        else tuple(range(len(box_tuple)))
    )
    source_id_tuple = (
        tuple(int(value) for value in source_ids)
        if source_ids is not None
        else tuple(range(len(point_tuple)))
    )
    if len(indexed_id_tuple) != len(box_tuple):
        raise ValueError("indexed_ids length must match indexed_boxes length")
    if len(source_id_tuple) != len(point_tuple):
        raise ValueError("source_ids length must match source_points length")
    _validate_unique_ids(indexed_id_tuple, label="indexed_ids")
    _validate_unique_ids(source_id_tuple, label="source_ids")
    expansion_tuple = _normalize_expansions(expansions, len(box_tuple))
    expanded_boxes = tuple(
        _expand_aabb2d(box, expansion_tuple[index])
        for index, box in enumerate(box_tuple)
    )
    resolved_row_capacity = (
        len(box_tuple) * len(point_tuple)
        if row_capacity is None
        else int(row_capacity)
    )
    if resolved_row_capacity < 0:
        raise ValueError("row_capacity must be non-negative")
    if max_rows_per_source is not None and int(max_rows_per_source) < 0:
        raise ValueError("max_rows_per_source must be non-negative when provided")
    resolved_max_rows_per_source = (
        None if max_rows_per_source is None else int(max_rows_per_source)
    )

    query_start = time.perf_counter()
    if normalized_backend == "optix":
        _validate_u32_ids(indexed_id_tuple, label="indexed_ids")
        _validate_u32_ids(source_id_tuple, label="source_ids")
        indexed_records = tuple(
            _IdentifiedAabb2D(
                int(indexed_id_tuple[index]),
                box.min_x,
                box.min_y,
                box.max_x,
                box.max_y,
            )
            for index, box in enumerate(expanded_boxes)
        )
        point_records = tuple(
            _IdentifiedPoint2D(
                int(source_id_tuple[index]),
                point.x,
                point.y,
            )
            for index, point in enumerate(point_tuple)
        )
        from .optix_runtime import collect_aabb_point_membership_pair_rows_2d_optix

        try:
            native = collect_aabb_point_membership_pair_rows_2d_optix(
                indexed_records,
                point_records,
                row_capacity=resolved_row_capacity,
            )
        except RuntimeError as exc:
            if "failure_mode=fail_closed_overflow" in str(exc):
                raise ExpandedAabbPointMembershipOverflowError(
                    "EXPANDED_AABB_POINT_MEMBERSHIP_2D OptiX row output overflowed; "
                    "failure_mode=fail_closed_overflow; partial_result_returned=False"
                ) from exc
            raise
        pair_rows = tuple(
            sorted((int(source_id), int(box_id)) for source_id, box_id in native["candidate_id_rows"])
        )
        native_symbol = native["native_generic_symbol"]
        rt_core_accelerated = True
        native_index = "optix_custom_aabb_gas"
    elif normalized_backend == "embree":
        _validate_u32_ids(indexed_id_tuple, label="indexed_ids")
        _validate_u32_ids(source_id_tuple, label="source_ids")
        prepared_embree = _prepare_embree_aabb_index_2d(
            expanded_boxes,
            row_ids=indexed_id_tuple,
        )
        try:
            pair_rows = prepared_embree.point_membership_rows(point_tuple, source_id_tuple)
        finally:
            prepared_embree.close()
        native_symbol = "rtdl_embree_columnar_payload_multi_predicate_scan"
        rt_core_accelerated = False
        native_index = "embree_generic_columnar_payload"
    else:
        prepared_cpu = prepare_aabb_index_2d(
            expanded_boxes,
            point_queries=point_tuple,
            indexed_ids=indexed_id_tuple,
            resolution=resolution,
            backend="cpu",
        )
        if not isinstance(prepared_cpu, AabbIndex2D):
            raise TypeError("CPU point membership row output expected AabbIndex2D")
        pair_rows = prepared_cpu.point_membership_rows(
            point_tuple,
            source_id_tuple,
            indexed_ids=indexed_id_tuple,
        )
        native_symbol = None
        rt_core_accelerated = False
        native_index = "cpu_uniform_grid_reference"
    query_sec = time.perf_counter() - query_start

    grouped: dict[int, list[tuple[int, int, int]]] = {source_id: [] for source_id in source_id_tuple}
    for source_id, box_id in pair_rows:
        grouped.setdefault(source_id, []).append(
            (source_id, box_id, EXPANDED_AABB_POINT_MEMBERSHIP_METADATA_FLAGS_NONE)
        )
    frontier_rows: list[tuple[int, int, int]] = []
    row_offsets = [0]
    for source_id in source_id_tuple:
        rows_for_source = sorted(grouped.get(source_id, ()))
        if (
            resolved_max_rows_per_source is not None
            and len(rows_for_source) > resolved_max_rows_per_source
        ):
            raise ExpandedAabbPointMembershipOverflowError(
                "EXPANDED_AABB_POINT_MEMBERSHIP_2D per-source capacity overflowed; "
                f"source_id={source_id}; attempted {len(rows_for_source)}; "
                "failure_mode=fail_closed_overflow; partial_result_returned=False"
            )
        frontier_rows.extend(rows_for_source)
        row_offsets.append(len(frontier_rows))
    if len(frontier_rows) > resolved_row_capacity:
        raise ExpandedAabbPointMembershipOverflowError(
            "EXPANDED_AABB_POINT_MEMBERSHIP_2D total row capacity overflowed; "
            f"attempted {len(frontier_rows)}; capacity {resolved_row_capacity}; "
            "failure_mode=fail_closed_overflow; partial_result_returned=False"
        )

    return {
        "primitive": EXPANDED_AABB_POINT_MEMBERSHIP_2D_PRIMITIVE,
        "contract": EXPANDED_AABB_POINT_MEMBERSHIP_2D_CONTRACT,
        "backend": normalized_backend,
        "operation": "point_contains_rows",
        "row_schema": EXPANDED_AABB_POINT_MEMBERSHIP_2D_ROW_SCHEMA,
        "candidate_id_rows": tuple(frontier_rows),
        "source_ids": source_id_tuple,
        "row_offsets": tuple(row_offsets),
        "valid_count": len(frontier_rows),
        "indexed_box_count": len(box_tuple),
        "source_count": len(point_tuple),
        "row_capacity": resolved_row_capacity,
        "max_rows_per_source": resolved_max_rows_per_source,
        "overflowed": False,
        "complete_candidate_coverage": True,
        "expansion_policy": "per_box_symmetric_axis_expansion",
        "run_phases": {
            "emit_expanded_aabb_point_membership_rows_2d_sec": query_sec,
        },
        "rt_core_accelerated": rt_core_accelerated,
        "native_engine_customization": False,
        "native_generic_symbol": native_symbol,
        "index": {
            "indexed_boxes": len(box_tuple),
            "native_index": native_index,
        },
        "claim_boundary": (
            "Generic expanded-AABB point-membership row output only. The engine "
            "sees points, expanded boxes, ids, row offsets, and fail-closed "
            "capacity; app interpretation remains outside the engine."
        ),
    }


def _validate_u32_ids(ids: tuple[int, ...], *, label: str) -> None:
    max_u32 = (1 << 32) - 1
    for value in ids:
        if value < 0 or value > max_u32:
            raise ValueError(f"{label} values must fit uint32 for OptiX AABB row output")


def _validate_unique_ids(ids: tuple[int, ...], *, label: str) -> None:
    if len(set(ids)) != len(ids):
        raise ValueError(f"{label} values must be unique for row-offset output")


def _normalize_expansions(expansions: float | Iterable[float], count: int) -> tuple[float, ...]:
    if isinstance(expansions, (int, float)):
        values = (float(expansions),) * count
    else:
        values = tuple(float(value) for value in expansions)
        if len(values) != count:
            raise ValueError("expansions length must match indexed_boxes length")
    for value in values:
        if value < 0.0 or not math.isfinite(value):
            raise ValueError("expansions must be finite non-negative values")
    return values


def _expand_aabb2d(box: Aabb2D, expansion: float) -> Aabb2D:
    return Aabb2D(
        box.min_x - expansion,
        box.min_y - expansion,
        box.max_x + expansion,
        box.max_y + expansion,
    )


def _validate_backend(backend: str) -> str:
    normalized = backend.lower().replace("-", "_")
    if normalized in {"python", "cpu_python_reference"}:
        normalized = "cpu"
    if normalized in {"nvidia_rt", "cuda_optix"}:
        normalized = "optix"
    if normalized in {"amd_hiprt", "hiprt_cuda_orochi"}:
        normalized = "hiprt"
    if normalized not in {"cpu", "embree", "optix", "hiprt"}:
        raise ValueError(
            "generic AABB_INDEX_QUERY_2D supports backend='cpu', backend='embree', backend='optix', or backend='hiprt'"
        )
    return normalized


def _prepare_embree_aabb_index_2d(
    boxes: tuple[Aabb2D, ...],
    *,
    row_ids: tuple[int, ...],
) -> EmbreeAabbIndex2D:
    from .embree_runtime import embree_aabb_index_2d_available
    from .embree_runtime import prepare_embree_aabb_index_2d
    from .embree_runtime import prepare_embree_columnar_record_set

    if len(row_ids) != len(boxes):
        raise ValueError("row_ids length must match indexed_boxes length")
    _validate_u32_ids(row_ids, label="row_ids")
    identified_boxes = tuple(
        _IdentifiedAabb2D(row_ids[index], box.min_x, box.min_y, box.max_x, box.max_y)
        for index, box in enumerate(boxes)
    )
    if embree_aabb_index_2d_available():
        return EmbreeAabbIndex2D(
            boxes=boxes,
            prepared=prepare_embree_aabb_index_2d(identified_boxes),
            row_ids=row_ids,
        )
    record_set = {
        "row_ids": row_ids,
        "columns": {
            "min_x": tuple(box.min_x for box in boxes),
            "min_y": tuple(box.min_y for box in boxes),
            "max_x": tuple(box.max_x for box in boxes),
            "max_y": tuple(box.max_y for box in boxes),
        },
    }
    prepared = prepare_embree_columnar_record_set(
        record_set,
        primary_fields=("min_x", "min_y", "max_x"),
    )
    return EmbreeAabbIndex2D(boxes=boxes, prepared=prepared, row_ids=row_ids)


def _point_contains_clauses(point: Point2DLike) -> tuple[tuple[str, str, float], ...]:
    return (
        ("min_x", "le", point.x),
        ("min_y", "le", point.y),
        ("max_x", "ge", point.x),
        ("max_y", "ge", point.y),
    )


def _range_contains_clauses(box: Aabb2D) -> tuple[tuple[str, str, float], ...]:
    return (
        ("min_x", "le", box.min_x),
        ("min_y", "le", box.min_y),
        ("max_x", "ge", box.max_x),
        ("max_y", "ge", box.max_y),
    )


def _range_intersects_clauses(box: Aabb2D) -> tuple[tuple[str, str, float], ...]:
    return (
        ("min_x", "le", box.max_x),
        ("min_y", "le", box.max_y),
        ("max_x", "ge", box.min_x),
        ("max_y", "ge", box.min_y),
    )


def _normalize_requested_operations(operation: str) -> tuple[str, ...]:
    operations = AABB_INDEX_2D_OPERATIONS if operation == "all" else (operation,)
    _validate_operations(operations)
    return operations


def _validate_operations(operations: Iterable[str]) -> None:
    unsupported = tuple(operation for operation in operations if operation not in AABB_INDEX_2D_OPERATIONS)
    if unsupported:
        raise ValueError(f"unsupported AABB index operation(s): {', '.join(unsupported)}")


def _validate_optix_operations(operations: Iterable[str]) -> None:
    unsupported = tuple(operation for operation in operations if operation not in AABB_INDEX_2D_OPERATIONS)
    if unsupported:
        raise ValueError(
            "OptiX AABB_INDEX_QUERY_2D unsupported native operation(s): "
            f"{', '.join(unsupported)}"
        )


def _normalize_point2d(point: Any) -> Point2DLike:
    try:
        return Point2DLike(float(point.x), float(point.y))
    except AttributeError:
        try:
            if len(point) >= 2:
                return Point2DLike(float(point[0]), float(point[1]))
        except TypeError:
            pass
    raise TypeError("AABB_INDEX_QUERY_2D requires point-like inputs with x/y attributes or 2-tuples")


def _normalize_aabb2d(box: Any) -> Aabb2D:
    if isinstance(box, Aabb2D):
        return box
    try:
        return Aabb2D(
            min_x=float(box.min_x),
            min_y=float(box.min_y),
            max_x=float(box.max_x),
            max_y=float(box.max_y),
        )
    except AttributeError:
        try:
            if len(box) >= 4:
                return Aabb2D(float(box[0]), float(box[1]), float(box[2]), float(box[3]))
        except TypeError:
            pass
    raise TypeError("AABB_INDEX_QUERY_2D requires boxes with min_x/min_y/max_x/max_y or 4-tuples")


def _compute_bounds(
    boxes: tuple[Aabb2D, ...],
    point_queries: tuple[Point2DLike, ...],
    box_queries: tuple[Aabb2D, ...],
) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    for box in (*boxes, *box_queries):
        xs.extend((box.min_x, box.max_x))
        ys.extend((box.min_y, box.max_y))
    for point in point_queries:
        xs.append(point.x)
        ys.append(point.y)
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    if max_x == min_x:
        min_x -= 0.5
        max_x += 0.5
    if max_y == min_y:
        min_y -= 0.5
        max_y += 0.5
    return (min_x, min_y, max_x, max_y)


def _cell_for_point(
    point: Point2DLike,
    bounds: tuple[float, float, float, float],
    resolution: int,
) -> tuple[int, int]:
    return (
        _axis_cell(point.x, bounds[0], bounds[2], resolution),
        _axis_cell(point.y, bounds[1], bounds[3], resolution),
    )


def _cells_for_box(
    box: Aabb2D,
    bounds: tuple[float, float, float, float],
    resolution: int,
) -> tuple[tuple[int, int], ...]:
    x0, x1 = _axis_cell_range(box.min_x, box.max_x, bounds[0], bounds[2], resolution)
    y0, y1 = _axis_cell_range(box.min_y, box.max_y, bounds[1], bounds[3], resolution)
    return tuple((ix, iy) for ix in range(x0, x1 + 1) for iy in range(y0, y1 + 1))


def _axis_cell(value: float, min_value: float, max_value: float, resolution: int) -> int:
    span = max_value - min_value
    raw = math.floor(((value - min_value) / span) * resolution)
    return min(resolution - 1, max(0, raw))


def _axis_cell_range(
    min_value: float,
    max_value: float,
    global_min: float,
    global_max: float,
    resolution: int,
) -> tuple[int, int]:
    return (
        _axis_cell(min_value, global_min, global_max, resolution),
        _axis_cell(max_value, global_min, global_max, resolution),
    )

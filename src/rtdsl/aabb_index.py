from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any, Iterable


AABB_INDEX_2D_OPERATIONS = ("point_contains", "range_contains", "range_intersects")
AABB_INDEX_2D_CONTRACT = {
    "primitive": "AABB_INDEX_QUERY_2D",
    "behavior": "prepared 2-D axis-aligned bounding-box index with exact predicate refinement",
    "operations": {
        "point_contains": "indexed_box_contains_query_point",
        "range_contains": "indexed_box_contains_query_box",
        "range_intersects": "indexed_box_intersects_query_box",
        "range_intersection_rows": "emit_query_box_indexed_box_intersection_pairs",
    },
    "backend_status": {
        "cpu": "reference_uniform_grid_counts_and_intersection_pair_rows",
        "embree": "not_implemented",
        "optix": "native_count_point_contains_range_contains_range_intersects_and_range_intersection_rows",
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
    backend: str = "optix"

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


def prepare_aabb_index_2d(
    indexed_boxes: Iterable[Any],
    *,
    point_queries: Iterable[Any] = (),
    box_queries: Iterable[Any] = (),
    resolution: int = 32,
    backend: str = "cpu",
) -> AabbIndex2D | OptixAabbIndex2D:
    """Prepare an app-name-free 2-D AABB index for point/box query predicates."""

    normalized_backend = _validate_backend(backend)
    box_tuple = tuple(_normalize_aabb2d(box) for box in indexed_boxes)
    point_tuple = tuple(_normalize_point2d(point) for point in point_queries)
    query_box_tuple = tuple(_normalize_aabb2d(box) for box in box_queries)
    if resolution < 1:
        raise ValueError("resolution must be positive")
    if not box_tuple:
        raise ValueError("AABB index requires at least one indexed box")

    if normalized_backend == "optix":
        from .optix_runtime import prepare_optix_aabb_index_2d

        return OptixAabbIndex2D(
            boxes=box_tuple,
            prepared=prepare_optix_aabb_index_2d(box_tuple),
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
    return prepared.count(point_queries=point_queries, box_queries=box_queries, operation=operation)


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


def _validate_u32_ids(ids: tuple[int, ...], *, label: str) -> None:
    max_u32 = (1 << 32) - 1
    for value in ids:
        if value < 0 or value > max_u32:
            raise ValueError(f"{label} values must fit uint32 for OptiX AABB row output")


def _validate_backend(backend: str) -> str:
    normalized = backend.lower().replace("-", "_")
    if normalized in {"python", "cpu_python_reference"}:
        normalized = "cpu"
    if normalized in {"nvidia_rt", "cuda_optix"}:
        normalized = "optix"
    if normalized not in {"cpu", "optix"}:
        raise ValueError("generic AABB_INDEX_QUERY_2D supports backend='cpu' or backend='optix'")
    return normalized


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

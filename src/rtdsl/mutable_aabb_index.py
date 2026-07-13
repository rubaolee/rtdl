from __future__ import annotations

from typing import Any, Iterable

from .aabb_index import (
    AABB_INDEX_2D_OPERATIONS,
    AabbIndex2D,
    OptixAabbIndex2D,
    _normalize_aabb2d,
    _normalize_point2d,
    prepare_aabb_index_2d,
)


MUTABLE_AABB_INDEX_2D_CONTRACT = {
    "primitive": "MUTABLE_AABB_INDEX_2D",
    "execution_model": "native_fixed_cardinality_refit_or_atomic_snapshot_rebuild",
    "id_contract": "stable_explicit_or_monotonic_auto_ids",
    "supported_backends": ("cpu", "optix"),
    "native_incremental_update": True,
    "native_incremental_insert_delete": False,
    "app_semantics": "none",
}


class MutableAabbIndex2D:
    """Revisioned 2-D AABB index with atomic snapshot-rebuild mutations."""

    def __init__(
        self,
        indexed_boxes: Iterable[Any] = (),
        *,
        indexed_ids: Iterable[int] | None = None,
        backend: str = "cpu",
        resolution: int = 32,
    ):
        normalized_backend = str(backend).strip().lower().replace("-", "_")
        if normalized_backend not in MUTABLE_AABB_INDEX_2D_CONTRACT["supported_backends"]:
            raise ValueError("mutable AABB index backend must be cpu or optix")
        if int(resolution) < 1:
            raise ValueError("resolution must be positive")
        boxes = tuple(_normalize_aabb2d(box) for box in indexed_boxes)
        ids = tuple(range(len(boxes))) if indexed_ids is None else tuple(int(value) for value in indexed_ids)
        if len(ids) != len(boxes):
            raise ValueError("indexed_ids length must match indexed_boxes length")
        self._validate_unique_nonnegative_ids(ids, label="indexed_ids")
        self.backend = normalized_backend
        self.resolution = int(resolution)
        self._records = dict(zip(ids, boxes))
        self._used_ids = set(ids)
        self._next_id = max(ids, default=-1) + 1
        self._revision = 0
        self._closed = False
        self._prepared = self._prepare_snapshot(self._records)
        self._last_mutation_execution_model = "initial_snapshot_prepare"

    @staticmethod
    def _validate_unique_nonnegative_ids(ids: tuple[int, ...], *, label: str) -> None:
        if any(value < 0 for value in ids):
            raise ValueError(f"{label} must contain non-negative integers")
        if len(set(ids)) != len(ids):
            raise ValueError(f"{label} must not contain duplicates")

    def _require_open(self) -> None:
        if self._closed:
            raise RuntimeError("mutable AABB index is closed")

    def _prepare_snapshot(self, records: dict[int, Any]):
        if not records:
            return None
        ordered = tuple(sorted(records.items()))
        return prepare_aabb_index_2d(
            tuple(box for _, box in ordered),
            indexed_ids=tuple(row_id for row_id, _ in ordered),
            resolution=self.resolution,
            backend=self.backend,
            allow_native_update=self.backend == "optix",
        )

    @staticmethod
    def _close_prepared(prepared: Any) -> None:
        close = getattr(prepared, "close", None)
        if callable(close):
            close()

    @property
    def revision(self) -> int:
        return self._revision

    @property
    def active_count(self) -> int:
        return len(self._records)

    @property
    def active_ids(self) -> tuple[int, ...]:
        return tuple(sorted(self._records))

    def metadata(self) -> dict[str, object]:
        return {
            "contract": "generic_mutable_aabb_index_2d_v1",
            "primitive": MUTABLE_AABB_INDEX_2D_CONTRACT["primitive"],
            "backend": self.backend,
            "execution_model": MUTABLE_AABB_INDEX_2D_CONTRACT["execution_model"],
            "native_incremental_update": self.backend == "optix",
            "native_incremental_insert_delete": False,
            "last_mutation_execution_model": self._last_mutation_execution_model,
            "revision": self._revision,
            "active_count": len(self._records),
            "active_ids": list(self.active_ids),
            "closed": self._closed,
            "app_semantics": "none",
        }

    def apply_mutations(
        self,
        *,
        insert_boxes: Iterable[Any] = (),
        insert_ids: Iterable[int] | None = None,
        updates: Iterable[tuple[int, Any]] = (),
        delete_ids: Iterable[int] = (),
        clear: bool = False,
    ) -> dict[str, object]:
        self._require_open()
        normalized_inserts = tuple(_normalize_aabb2d(box) for box in insert_boxes)
        normalized_updates = tuple((int(row_id), _normalize_aabb2d(box)) for row_id, box in updates)
        normalized_deletes = tuple(int(row_id) for row_id in delete_ids)
        update_ids = tuple(row_id for row_id, _ in normalized_updates)
        self._validate_unique_nonnegative_ids(update_ids, label="update ids")
        self._validate_unique_nonnegative_ids(normalized_deletes, label="delete_ids")
        if clear and (normalized_updates or normalized_deletes):
            raise ValueError("clear cannot be combined with updates or deletes")
        if set(update_ids) & set(normalized_deletes):
            raise ValueError("the same id cannot be updated and deleted in one batch")

        candidate_records = {} if clear else dict(self._records)
        candidate_used_ids = set() if clear else set(self._used_ids)
        candidate_next_id = 0 if clear else self._next_id

        missing_updates = sorted(set(update_ids) - set(candidate_records))
        missing_deletes = sorted(set(normalized_deletes) - set(candidate_records))
        if missing_updates:
            raise KeyError(f"update ids are not active: {missing_updates}")
        if missing_deletes:
            raise KeyError(f"delete ids are not active: {missing_deletes}")

        for row_id in normalized_deletes:
            del candidate_records[row_id]
        for row_id, box in normalized_updates:
            candidate_records[row_id] = box

        if insert_ids is None:
            resolved_insert_ids: list[int] = []
            for _ in normalized_inserts:
                while candidate_next_id in candidate_used_ids:
                    candidate_next_id += 1
                resolved_insert_ids.append(candidate_next_id)
                candidate_used_ids.add(candidate_next_id)
                candidate_next_id += 1
            normalized_insert_ids = tuple(resolved_insert_ids)
        else:
            normalized_insert_ids = tuple(int(value) for value in insert_ids)
            if len(normalized_insert_ids) != len(normalized_inserts):
                raise ValueError("insert_ids length must match insert_boxes length")
            self._validate_unique_nonnegative_ids(normalized_insert_ids, label="insert_ids")
            reused = sorted(set(normalized_insert_ids) & candidate_used_ids)
            if reused:
                raise ValueError(f"insert ids were already used in this lifecycle: {reused}")
            candidate_used_ids.update(normalized_insert_ids)
            candidate_next_id = max(candidate_next_id, max(normalized_insert_ids, default=-1) + 1)

        for row_id, box in zip(normalized_insert_ids, normalized_inserts):
            candidate_records[row_id] = box

        changed = bool(clear or normalized_inserts or normalized_updates or normalized_deletes)
        if not changed:
            return {
                **self.metadata(),
                "applied": False,
                "revision_before": self._revision,
                "revision_after": self._revision,
                "inserted_ids": [],
                "updated_ids": [],
                "deleted_ids": [],
                "cleared": False,
            }

        revision_before = self._revision
        ordered_candidate = tuple(sorted(candidate_records.items()))
        use_native_refit = bool(
            self.backend == "optix"
            and normalized_updates
            and not clear
            and not normalized_inserts
            and not normalized_deletes
            and isinstance(self._prepared, OptixAabbIndex2D)
        )
        if use_native_refit:
            self._prepared.refit_updates(normalized_updates)
            mutation_execution_model = "native_sparse_slot_refit_with_rollback"
        else:
            new_prepared = self._prepare_snapshot(candidate_records)
            old_prepared = self._prepared
            self._prepared = new_prepared
            self._close_prepared(old_prepared)
            mutation_execution_model = "atomic_snapshot_rebuild"
        self._records = candidate_records
        self._used_ids = candidate_used_ids
        self._next_id = candidate_next_id
        self._revision += 1
        self._last_mutation_execution_model = mutation_execution_model
        return {
            **self.metadata(),
            "applied": True,
            "revision_before": revision_before,
            "revision_after": self._revision,
            "inserted_ids": list(normalized_insert_ids),
            "updated_ids": list(update_ids),
            "deleted_ids": list(normalized_deletes),
            "cleared": bool(clear),
            "mutation_execution_model": mutation_execution_model,
        }

    def insert(self, boxes: Iterable[Any], *, ids: Iterable[int] | None = None) -> dict[str, object]:
        return self.apply_mutations(insert_boxes=boxes, insert_ids=ids)

    def update(self, updates: Iterable[tuple[int, Any]]) -> dict[str, object]:
        return self.apply_mutations(updates=updates)

    def delete(self, ids: Iterable[int]) -> dict[str, object]:
        return self.apply_mutations(delete_ids=ids)

    def clear(self) -> dict[str, object]:
        return self.apply_mutations(clear=True)

    def count(
        self,
        *,
        point_queries: Iterable[Any] = (),
        box_queries: Iterable[Any] = (),
        operation: str = "all",
    ) -> dict[str, object]:
        self._require_open()
        if self._prepared is None:
            operations = AABB_INDEX_2D_OPERATIONS if operation == "all" else (operation,)
            if any(name not in AABB_INDEX_2D_OPERATIONS for name in operations):
                raise ValueError(f"unsupported AABB index operation: {operation}")
            return {
                "primitive": "MUTABLE_AABB_INDEX_2D",
                "contract": "generic_mutable_aabb_index_2d_v1",
                "backend": self.backend,
                "counts": {name: 0 for name in operations},
                "rt_core_accelerated": False,
                "native_engine_customization": False,
                "mutable_state": self.metadata(),
            }
        payload = self._prepared.count(
            point_queries=point_queries,
            box_queries=box_queries,
            operation=operation,
        )
        return {**payload, "mutable_state": self.metadata()}

    def point_membership_rows(
        self,
        point_queries: Iterable[Any],
        *,
        query_ids: Iterable[int] | None = None,
        row_capacity: int | None = None,
    ) -> tuple[tuple[int, int], ...]:
        self._require_open()
        points = tuple(_normalize_point2d(point) for point in point_queries)
        ids = tuple(range(len(points))) if query_ids is None else tuple(int(value) for value in query_ids)
        if len(ids) != len(points):
            raise ValueError("query_ids length must match point_queries length")
        if self._prepared is None:
            return ()
        if isinstance(self._prepared, AabbIndex2D):
            return self._prepared.point_membership_rows(points, ids, indexed_ids=self.active_ids)
        if not isinstance(self._prepared, OptixAabbIndex2D):
            raise TypeError("unsupported mutable AABB prepared backend")
        if row_capacity is None:
            raise ValueError("OptiX mutable point rows require explicit row_capacity")
        return self._prepared.point_membership_rows(points, ids, row_capacity=int(row_capacity))

    def intersection_rows(
        self,
        query_boxes: Iterable[Any],
        *,
        query_ids: Iterable[int] | None = None,
        row_capacity: int | None = None,
    ) -> tuple[tuple[int, int], ...]:
        self._require_open()
        boxes = tuple(_normalize_aabb2d(box) for box in query_boxes)
        ids = tuple(range(len(boxes))) if query_ids is None else tuple(int(value) for value in query_ids)
        if len(ids) != len(boxes):
            raise ValueError("query_ids length must match query_boxes length")
        if self._prepared is None:
            return ()
        if isinstance(self._prepared, AabbIndex2D):
            rows: set[tuple[int, int]] = set()
            for query_index, query_box in enumerate(boxes):
                for indexed_index in self._prepared.box_candidates(query_box):
                    if self._prepared.boxes[indexed_index].intersects_box(query_box):
                        rows.add((ids[query_index], self.active_ids[indexed_index]))
            return tuple(sorted(rows))
        if not isinstance(self._prepared, OptixAabbIndex2D):
            raise TypeError("unsupported mutable AABB prepared backend")
        if row_capacity is None:
            raise ValueError("OptiX mutable intersection rows require explicit row_capacity")
        return self._prepared.intersection_rows(boxes, ids, row_capacity=int(row_capacity))

    def close(self) -> None:
        if self._closed:
            return
        self._close_prepared(self._prepared)
        self._prepared = None
        self._closed = True

    def __enter__(self) -> "MutableAabbIndex2D":
        self._require_open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def prepare_mutable_aabb_index_2d(
    indexed_boxes: Iterable[Any] = (),
    *,
    indexed_ids: Iterable[int] | None = None,
    backend: str = "cpu",
    resolution: int = 32,
) -> MutableAabbIndex2D:
    return MutableAabbIndex2D(
        indexed_boxes,
        indexed_ids=indexed_ids,
        backend=backend,
        resolution=resolution,
    )

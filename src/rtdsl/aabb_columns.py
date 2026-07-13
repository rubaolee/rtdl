"""Generic host column contract for 2-D AABB inputs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np


@dataclass(frozen=True)
class Aabb2DColumns:
    """Validated host columns for generic 2-D AABB preparation.

    The columns are intentionally app-neutral. Backends may use the arrays
    directly for packing, while iteration remains available for CPU/reference
    callers that need row-shaped values.
    """

    ids: np.ndarray
    min_x: np.ndarray
    min_y: np.ndarray
    max_x: np.ndarray
    max_y: np.ndarray

    def __post_init__(self) -> None:
        raw_ids = np.asarray(self.ids)
        if raw_ids.ndim != 1:
            raise ValueError("Aabb2DColumns.ids must be one-dimensional")
        if not np.issubdtype(raw_ids.dtype, np.integer):
            raise TypeError("Aabb2DColumns.ids must contain integers")
        if np.any(raw_ids < 0) or np.any(raw_ids > np.iinfo(np.uint32).max):
            raise ValueError("Aabb2DColumns.ids must fit uint32")
        normalized = {
            "ids": raw_ids.astype(np.uint32, copy=False),
            "min_x": np.asarray(self.min_x, dtype=np.float64),
            "min_y": np.asarray(self.min_y, dtype=np.float64),
            "max_x": np.asarray(self.max_x, dtype=np.float64),
            "max_y": np.asarray(self.max_y, dtype=np.float64),
        }
        count = normalized["ids"].size
        for name, values in normalized.items():
            if values.ndim != 1:
                raise ValueError(f"Aabb2DColumns.{name} must be one-dimensional")
            if values.size != count:
                raise ValueError("Aabb2DColumns columns must have equal lengths")
        for name in ("min_x", "min_y", "max_x", "max_y"):
            if not np.all(np.isfinite(normalized[name])):
                raise ValueError(f"Aabb2DColumns.{name} must contain finite values")
        if np.any(normalized["max_x"] < normalized["min_x"]):
            raise ValueError("Aabb2DColumns max_x must be >= min_x")
        if np.any(normalized["max_y"] < normalized["min_y"]):
            raise ValueError("Aabb2DColumns max_y must be >= min_y")
        for name, values in normalized.items():
            object.__setattr__(self, name, np.ascontiguousarray(values))

    @classmethod
    def from_mapping(
        cls,
        columns: Mapping[str, object],
        *,
        indexed_ids: object | None = None,
    ) -> "Aabb2DColumns":
        required = ("min_x", "min_y", "max_x", "max_y")
        missing = [name for name in required if name not in columns]
        if missing:
            raise ValueError(f"Aabb2DColumns missing required columns: {', '.join(missing)}")
        min_x = np.asarray(columns["min_x"], dtype=np.float64)
        ids = (
            np.arange(min_x.size, dtype=np.uint32)
            if indexed_ids is None and "id" not in columns
            else np.asarray(
                columns.get("id") if indexed_ids is None else indexed_ids,
            )
        )
        return cls(
            ids=ids,
            min_x=min_x,
            min_y=np.asarray(columns["min_y"], dtype=np.float64),
            max_x=np.asarray(columns["max_x"], dtype=np.float64),
            max_y=np.asarray(columns["max_y"], dtype=np.float64),
        )

    def __len__(self) -> int:
        return int(self.ids.size)

    def __iter__(self):
        return iter(
            zip(
                self.min_x.tolist(),
                self.min_y.tolist(),
                self.max_x.tolist(),
                self.max_y.tolist(),
            )
        )

    def as_mapping(self) -> dict[str, np.ndarray]:
        return {
            "id": self.ids,
            "min_x": self.min_x,
            "min_y": self.min_y,
            "max_x": self.max_x,
            "max_y": self.max_y,
        }

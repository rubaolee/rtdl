from __future__ import annotations

from dataclasses import dataclass
from typing import Any


GEOMETRY_RELATION_BOUNDS_OVERLAP_AREA_CUPY_VERSION = (
    "rtdl.v2_8.geometry_relation.bounds_overlap_area_cupy.v1"
)


@dataclass(frozen=True)
class ShapePairBoundsOverlapAreaCupyResult:
    row_areas: object
    group_keys: object | None
    group_area_sums: object | None
    metadata: dict[str, Any]

    def to_metadata(self) -> dict[str, Any]:
        return dict(self.metadata)


def shape_pair_relation_bounds_overlap_area_cupy(
    relation_columns,
    *,
    group_by: str | None = "left",
) -> ShapePairBoundsOverlapAreaCupyResult:
    """Compute bounds-overlap areas for active shape-pair relation rows.

    This consumes generic relation id/ordinal columns plus generic shape-pair
    geometry payload columns. It intentionally computes axis-aligned bounds
    overlap area, not exact polygon overlay area.
    """
    if group_by not in (None, "left", "right"):
        raise ValueError("group_by must be None, 'left', or 'right'")
    if getattr(relation_columns, "overflow", False):
        raise RuntimeError("cannot consume an overflowed shape-pair relation stream")

    import cupy as cp  # type: ignore

    ids = relation_columns.as_cupy_columns()
    ordinals = relation_columns.as_cupy_ordinal_columns()
    geometry = relation_columns.as_cupy_geometry_payload_columns()

    left_ordinal = ordinals["left_ordinal"].astype(cp.int64, copy=False)
    right_ordinal = ordinals["right_ordinal"].astype(cp.int64, copy=False)
    left_bounds = geometry["left_bounds"][left_ordinal]
    right_bounds = geometry["right_bounds"][right_ordinal]

    overlap_min_x = cp.maximum(left_bounds[:, 0], right_bounds[:, 0])
    overlap_min_y = cp.maximum(left_bounds[:, 1], right_bounds[:, 1])
    overlap_max_x = cp.minimum(left_bounds[:, 2], right_bounds[:, 2])
    overlap_max_y = cp.minimum(left_bounds[:, 3], right_bounds[:, 3])
    widths = cp.maximum(cp.asarray(0.0, dtype=cp.float32), overlap_max_x - overlap_min_x)
    heights = cp.maximum(cp.asarray(0.0, dtype=cp.float32), overlap_max_y - overlap_min_y)
    row_areas = (widths * heights).astype(cp.float64)

    group_keys = None
    group_area_sums = None
    if group_by is not None:
        source_keys = ids["left_id"] if group_by == "left" else ids["right_id"]
        group_keys = cp.unique(source_keys)
        inverse = cp.searchsorted(group_keys, source_keys)
        group_area_sums = cp.zeros((int(group_keys.size),), dtype=cp.float64)
        cp.add.at(group_area_sums, inverse, row_areas)

    metadata = {
        "schema": GEOMETRY_RELATION_BOUNDS_OVERLAP_AREA_CUPY_VERSION,
        "operation": "shape_pair_bounds_overlap_area",
        "partner": "cupy",
        "input_contract": "shape_pair_relation_flags_with_ordinals_and_geometry_payload",
        "row_count": int(getattr(relation_columns, "row_count")),
        "group_by": group_by,
        "area_semantics": "axis_aligned_bounds_overlap_area_upper_bound",
        "exact_polygon_overlay_area": False,
        "requires_relation_ordinals": True,
        "requires_geometry_payload_columns": True,
        "app_specific_engine_logic_allowed": False,
        "automatic_partner_selection_allowed": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "full_overlay_area_claim_authorized": False,
    }
    return ShapePairBoundsOverlapAreaCupyResult(
        row_areas=row_areas,
        group_keys=group_keys,
        group_area_sums=group_area_sums,
        metadata=metadata,
    )

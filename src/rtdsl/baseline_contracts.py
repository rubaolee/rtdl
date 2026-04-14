from __future__ import annotations
from dataclasses import dataclass
from math import isclose
from typing import Optional, List, Dict, Union, Tuple

from .ir import CompiledKernel

BASELINE_WORKLOAD_ORDER = (
    "lsi",
    "pip",
    "overlay",
    "ray_tri_hitcount",
    "segment_polygon_hitcount",
    "segment_polygon_anyhit_rows",
    "point_nearest_segment",
    "fixed_radius_neighbors",
    "knn_rows",
)
BASELINE_PRECISION_MODE = "float_approx"
BASELINE_FLOAT_ABS_TOL = 1e-6
BASELINE_FLOAT_REL_TOL = 1e-6


@dataclass(frozen=True)
class InputContract:
    name: str
    geometry: str
    role: str
    layout_name: str
    layout_fields: tuple[str, ...]
    logical_record_fields: tuple[str, ...]


@dataclass(frozen=True)
class WorkloadContract:
    workload: str
    backend: str
    precision: str
    predicate: str
    accel: str
    inputs: tuple[InputContract, ...]
    emit_fields: tuple[str, ...]
    comparison_mode: str
    representative_datasets: tuple[str, ...]
    notes: str


BASELINE_WORKLOADS: dict[str, WorkloadContract] = {
    "lsi": WorkloadContract(
        workload="lsi",
        backend="rtdl",
        precision=BASELINE_PRECISION_MODE,
        predicate="segment_intersection",
        accel="bvh",
        inputs=(
            InputContract(
                name="left",
                geometry="segments",
                role="probe",
                layout_name="Segment2D",
                layout_fields=("x0", "y0", "x1", "y1", "id"),
                logical_record_fields=("id", "x0", "y0", "x1", "y1"),
            ),
            InputContract(
                name="right",
                geometry="segments",
                role="build",
                layout_name="Segment2D",
                layout_fields=("x0", "y0", "x1", "y1", "id"),
                logical_record_fields=("id", "x0", "y0", "x1", "y1"),
            ),
        ),
        emit_fields=("left_id", "right_id", "intersection_point_x", "intersection_point_y"),
        comparison_mode="exact_ids_and_flags_plus_float_tolerance",
        representative_datasets=(
            "authored_lsi_minimal",
            "tests/fixtures/rayjoin/br_county_subset.cdb",
        ),
        notes="Current local backend lowers this workload to native_loop for exact-source parity; float outputs use epsilon comparison for cross-backend checks.",
    ),
    "pip": WorkloadContract(
        workload="pip",
        backend="rtdl",
        precision=BASELINE_PRECISION_MODE,
        predicate="point_in_polygon",
        accel="bvh",
        inputs=(
            InputContract(
                name="points",
                geometry="points",
                role="probe",
                layout_name="Point2D",
                layout_fields=("x", "y", "id"),
                logical_record_fields=("id", "x", "y"),
            ),
            InputContract(
                name="polygons",
                geometry="polygons",
                role="build",
                layout_name="Polygon2DRef",
                layout_fields=("vertex_offset", "vertex_count", "id"),
                logical_record_fields=("id", "vertices"),
            ),
        ),
        emit_fields=("point_id", "polygon_id", "contains"),
        comparison_mode="exact",
        representative_datasets=(
            "authored_pip_minimal",
            "tests/fixtures/rayjoin/br_county_subset.cdb",
        ),
        notes="Logical polygon inputs are expressed as inline vertices even though lowering uses Polygon2DRef layouts.",
    ),
    "overlay": WorkloadContract(
        workload="overlay",
        backend="rtdl",
        precision=BASELINE_PRECISION_MODE,
        predicate="overlay_compose",
        accel="bvh",
        inputs=(
            InputContract(
                name="left",
                geometry="polygons",
                role="probe",
                layout_name="Polygon2DRef",
                layout_fields=("vertex_offset", "vertex_count", "id"),
                logical_record_fields=("id", "vertices"),
            ),
            InputContract(
                name="right",
                geometry="polygons",
                role="build",
                layout_name="Polygon2DRef",
                layout_fields=("vertex_offset", "vertex_count", "id"),
                logical_record_fields=("id", "vertices"),
            ),
        ),
        emit_fields=("left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"),
        comparison_mode="exact",
        representative_datasets=(
            "authored_overlay_minimal",
            "tests/fixtures/rayjoin/br_county_subset.cdb + tests/fixtures/rayjoin/br_soil_subset.cdb",
        ),
        notes="Overlay is treated as compositional seed generation in the current baseline.",
    ),
    "ray_tri_hitcount": WorkloadContract(
        workload="ray_tri_hitcount",
        backend="rtdl",
        precision=BASELINE_PRECISION_MODE,
        predicate="ray_triangle_hit_count",
        accel="bvh",
        inputs=(
            InputContract(
                name="rays",
                geometry="rays",
                role="probe",
                layout_name="Ray2D",
                layout_fields=("ox", "oy", "dx", "dy", "tmax", "id"),
                logical_record_fields=("id", "ox", "oy", "dx", "dy", "tmax"),
            ),
            InputContract(
                name="triangles",
                geometry="triangles",
                role="build",
                layout_name="Triangle2D",
                layout_fields=("x0", "y0", "x1", "y1", "x2", "y2", "id"),
                logical_record_fields=("id", "x0", "y0", "x1", "y1", "x2", "y2"),
            ),
        ),
        emit_fields=("ray_id", "hit_count"),
        comparison_mode="exact",
        representative_datasets=(
            "authored_ray_tri_minimal",
            "examples/reference/rtdl_ray_tri_hitcount.py synthetic random generators",
        ),
        notes="Finite 2D rays against triangles with one hit-count record per ray.",
    ),
    "segment_polygon_hitcount": WorkloadContract(
        workload="segment_polygon_hitcount",
        backend="rtdl",
        precision=BASELINE_PRECISION_MODE,
        predicate="segment_polygon_hitcount",
        accel="bvh",
        inputs=(
            InputContract(
                name="segments",
                geometry="segments",
                role="probe",
                layout_name="Segment2D",
                layout_fields=("x0", "y0", "x1", "y1", "id"),
                logical_record_fields=("id", "x0", "y0", "x1", "y1"),
            ),
            InputContract(
                name="polygons",
                geometry="polygons",
                role="build",
                layout_name="Polygon2DRef",
                layout_fields=("vertex_offset", "vertex_count", "id"),
                logical_record_fields=("id", "vertices"),
            ),
        ),
        emit_fields=("segment_id", "hit_count"),
        comparison_mode="exact",
        representative_datasets=(
            "authored_segment_polygon_minimal",
            "tests/fixtures/rayjoin/br_county_subset.cdb",
            "derived/br_county_subset_segment_polygon_tiled_x4",
        ),
        notes="Current local backend lowers this workload to native_loop even though the DSL traverse stays bvh-shaped.",
    ),
    "segment_polygon_anyhit_rows": WorkloadContract(
        workload="segment_polygon_anyhit_rows",
        backend="rtdl",
        precision=BASELINE_PRECISION_MODE,
        predicate="segment_polygon_anyhit_rows",
        accel="bvh",
        inputs=(
            InputContract(
                name="segments",
                geometry="segments",
                role="probe",
                layout_name="Segment2D",
                layout_fields=("x0", "y0", "x1", "y1", "id"),
                logical_record_fields=("id", "x0", "y0", "x1", "y1"),
            ),
            InputContract(
                name="polygons",
                geometry="polygons",
                role="build",
                layout_name="Polygon2DRef",
                layout_fields=("vertex_offset", "vertex_count", "id"),
                logical_record_fields=("id", "vertices"),
            ),
        ),
        emit_fields=("segment_id", "polygon_id"),
        comparison_mode="exact",
        representative_datasets=(
            "authored_segment_polygon_minimal",
            "tests/fixtures/rayjoin/br_county_subset.cdb",
            "derived/br_county_subset_segment_polygon_tiled_x4",
        ),
        notes="Row-materializing segment/polygon any-hit join over the same segment/polygon geometric core as hitcount.",
    ),
    "point_nearest_segment": WorkloadContract(
        workload="point_nearest_segment",
        backend="rtdl",
        precision=BASELINE_PRECISION_MODE,
        predicate="point_nearest_segment",
        accel="bvh",
        inputs=(
            InputContract(
                name="points",
                geometry="points",
                role="probe",
                layout_name="Point2D",
                layout_fields=("x", "y", "id"),
                logical_record_fields=("id", "x", "y"),
            ),
            InputContract(
                name="segments",
                geometry="segments",
                role="build",
                layout_name="Segment2D",
                layout_fields=("x0", "y0", "x1", "y1", "id"),
                logical_record_fields=("id", "x0", "y0", "x1", "y1"),
            ),
        ),
        emit_fields=("point_id", "segment_id", "distance"),
        comparison_mode="exact_ids_and_flags_plus_float_tolerance",
        representative_datasets=(
            "authored_point_nearest_segment_minimal",
            "tests/fixtures/rayjoin/br_county_subset.cdb",
        ),
        notes="Current local backend lowers this workload to native_loop even though the DSL traverse stays bvh-shaped.",
    ),
    "fixed_radius_neighbors": WorkloadContract(
        workload="fixed_radius_neighbors",
        backend="rtdl",
        precision=BASELINE_PRECISION_MODE,
        predicate="fixed_radius_neighbors",
        accel="bvh",
        inputs=(
            InputContract(
                name="query_points",
                geometry="points",
                role="probe",
                layout_name="Point2D",
                layout_fields=("x", "y", "id"),
                logical_record_fields=("id", "x", "y"),
            ),
            InputContract(
                name="search_points",
                geometry="points",
                role="build",
                layout_name="Point2D",
                layout_fields=("x", "y", "id"),
                logical_record_fields=("id", "x", "y"),
            ),
        ),
        emit_fields=("query_id", "neighbor_id", "distance"),
        comparison_mode="exact_ids_and_flags_plus_float_tolerance",
        representative_datasets=(
            "authored_fixed_radius_neighbors_minimal",
            "tests/fixtures/rayjoin/br_county_subset.cdb",
            "tests/fixtures/public/natural_earth_populated_places_sample.geojson",
        ),
        notes="Current closure includes Python truth path, native CPU/oracle support, and Embree support; external baseline and later NN-family extensions land in later goals.",
    ),
    "knn_rows": WorkloadContract(
        workload="knn_rows",
        backend="rtdl",
        precision=BASELINE_PRECISION_MODE,
        predicate="knn_rows",
        accel="bvh",
        inputs=(
            InputContract(
                name="query_points",
                geometry="points",
                role="probe",
                layout_name="Point2D",
                layout_fields=("x", "y", "id"),
                logical_record_fields=("id", "x", "y"),
            ),
            InputContract(
                name="search_points",
                geometry="points",
                role="build",
                layout_name="Point2D",
                layout_fields=("x", "y", "id"),
                logical_record_fields=("id", "x", "y"),
            ),
        ),
        emit_fields=("query_id", "neighbor_id", "distance", "neighbor_rank"),
        comparison_mode="exact_ids_and_flags_plus_float_tolerance",
        representative_datasets=(
            "authored_knn_rows_minimal",
            "tests/fixtures/rayjoin/br_county_subset.cdb",
            "tests/fixtures/public/natural_earth_populated_places_sample.geojson",
        ),
        notes="Current closure includes Python truth path only; native/backend and external baseline support land in later goals.",
    ),
}


def validate_compiled_kernel_against_baseline(
    compiled: CompiledKernel,
    workload: str,
) -> None:
    contract = BASELINE_WORKLOADS[workload]
    if compiled.backend != contract.backend:
        raise ValueError(
            f"baseline workload `{workload}` requires backend `{contract.backend}`, "
            f"got `{compiled.backend}`"
        )
    if compiled.precision != contract.precision:
        raise ValueError(
            f"baseline workload `{workload}` requires precision `{contract.precision}`, "
            f"got `{compiled.precision}`"
        )
    if compiled.candidates is None or compiled.refine_op is None or compiled.emit_op is None:
        raise ValueError(f"baseline workload `{workload}` requires traverse/refine/emit")
    if compiled.candidates.accel != contract.accel:
        raise ValueError(
            f"baseline workload `{workload}` requires accel `{contract.accel}`, "
            f"got `{compiled.candidates.accel}`"
        )
    if compiled.refine_op.predicate.name != contract.predicate:
        raise ValueError(
            f"baseline workload `{workload}` requires predicate `{contract.predicate}`, "
            f"got `{compiled.refine_op.predicate.name}`"
        )
    if compiled.emit_op.fields != contract.emit_fields:
        raise ValueError(
            f"baseline workload `{workload}` requires emit fields {contract.emit_fields!r}, "
            f"got {compiled.emit_op.fields!r}"
        )

    actual_inputs = {item.name: item for item in compiled.inputs}
    expected_names = {item.name for item in contract.inputs}
    if set(actual_inputs) != expected_names:
        raise ValueError(
            f"baseline workload `{workload}` requires inputs {sorted(expected_names)!r}, "
            f"got {sorted(actual_inputs)!r}"
        )

    for expected in contract.inputs:
        item = actual_inputs[expected.name]
        if item.geometry.name != expected.geometry:
            raise ValueError(
                f"input `{expected.name}` requires geometry `{expected.geometry}`, "
                f"got `{item.geometry.name}`"
            )
        if item.role != expected.role:
            raise ValueError(
                f"input `{expected.name}` requires role `{expected.role}`, got `{item.role}`"
            )
        if item.layout.name != expected.layout_name:
            raise ValueError(
                f"input `{expected.name}` requires layout `{expected.layout_name}`, "
                f"got `{item.layout.name}`"
            )
        if item.layout.field_names() != expected.layout_fields:
            raise ValueError(
                f"input `{expected.name}` requires layout fields {expected.layout_fields!r}, "
                f"got {item.layout.field_names()!r}"
            )


def compare_baseline_rows(
    workload: str,
    cpu_rows: tuple[dict[str, object], ...],
    embree_rows: tuple[dict[str, object], ...],
    *,
    abs_tol: Optional[float] = None,
    rel_tol: Optional[float] = None,
) -> bool:
    contract = BASELINE_WORKLOADS[workload]
    actual_abs_tol = abs_tol if abs_tol is not None else BASELINE_FLOAT_ABS_TOL
    actual_rel_tol = rel_tol if rel_tol is not None else BASELINE_FLOAT_REL_TOL
    cpu_sorted = tuple(sorted(cpu_rows, key=_row_sort_key))
    embree_sorted = tuple(sorted(embree_rows, key=_row_sort_key))
    if len(cpu_sorted) != len(embree_sorted):
        return False
    for cpu_row, embree_row in zip(cpu_sorted, embree_sorted):
        if set(cpu_row) != set(embree_row):
            return False
        for field in cpu_row:
            left = cpu_row[field]
            right = embree_row[field]
            if contract.comparison_mode == "exact":
                if left != right:
                    return False
                continue
            if isinstance(left, float) or isinstance(right, float):
                if not isclose(
                    float(left),
                    float(right),
                    rel_tol=actual_rel_tol,
                    abs_tol=actual_abs_tol,
                ):
                    return False
            elif left != right:
                return False
    return True


def _row_sort_key(row: dict[str, object]) -> tuple[tuple[str, object], ...]:
    normalized = []
    for key, value in sorted(row.items()):
        if isinstance(value, float):
            normalized.append((key, round(value, 9)))
        else:
            normalized.append((key, value))
    return tuple(normalized)

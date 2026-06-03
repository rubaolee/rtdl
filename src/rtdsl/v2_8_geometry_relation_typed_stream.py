from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .v2_8_typed_result_stream import V28TypedResultStreamContract
from .v2_8_typed_result_stream import make_typed_result_stream_contract
from .v2_8_typed_result_stream import typed_result_column
from .v2_8_typed_result_stream import typed_result_status_columns


V2_8_GEOMETRY_RELATION_TYPED_PRODUCER_VERSION = (
    "rtdl.v2_8.geometry_relation_typed_producer.v1"
)
V2_8_GEOMETRY_RELATION_TYPED_PRODUCER_STATUS = (
    "host_row_view_metadata_no_device_resident_relation_rows_yet"
)
V2_8_GEOMETRY_RELATION_TYPED_PRODUCER_CLAIM_BOUNDARY = (
    "v2.8 geometry-relation typed producer metadata records generic row schemas "
    "for prepared geometry outputs. It does not authorize release, public "
    "speedup wording, RT-core speedup wording, true-zero-copy wording, hidden "
    "dispatch, hidden partner selection, paper reproduction claims, or "
    "app-specific native-engine behavior."
)


@dataclass(frozen=True)
class V28GeometryRelationColumnSpec:
    name: str
    role: str
    dtype: str


@dataclass(frozen=True)
class V28GeometryRelationSchema:
    schema_id: str
    producer_primitive: str
    columns: tuple[V28GeometryRelationColumnSpec, ...]
    output_residency: str = "host_materialized_row_view"


V2_8_GEOMETRY_RELATION_SCHEMAS: dict[tuple[str, ...], V28GeometryRelationSchema] = {
    ("point_id", "shape_id", "membership"): V28GeometryRelationSchema(
        schema_id="point_closed_shape_membership_2d_rows",
        producer_primitive="point_closed_shape_membership_2d",
        columns=(
            V28GeometryRelationColumnSpec("point_id", "group_key", "int64"),
            V28GeometryRelationColumnSpec("shape_id", "item_id", "int64"),
            V28GeometryRelationColumnSpec("membership", "mask", "uint32"),
        ),
    ),
    ("left_id", "right_id", "intersection_point_x", "intersection_point_y"): V28GeometryRelationSchema(
        schema_id="segment_pair_intersection_2d_rows",
        producer_primitive="segment_pair_intersection_2d",
        columns=(
            V28GeometryRelationColumnSpec("left_id", "group_key", "int64"),
            V28GeometryRelationColumnSpec("right_id", "item_id", "int64"),
            V28GeometryRelationColumnSpec("intersection_point_x", "witness", "float64"),
            V28GeometryRelationColumnSpec("intersection_point_y", "witness", "float64"),
        ),
    ),
    ("left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"): V28GeometryRelationSchema(
        schema_id="shape_pair_relation_flags_2d_rows",
        producer_primitive="shape_pair_relation_flags_2d",
        columns=(
            V28GeometryRelationColumnSpec("left_polygon_id", "group_key", "int64"),
            V28GeometryRelationColumnSpec("right_polygon_id", "item_id", "int64"),
            V28GeometryRelationColumnSpec("requires_lsi", "mask", "uint32"),
            V28GeometryRelationColumnSpec("requires_pip", "mask", "uint32"),
        ),
    ),
}


def _normalize_field_names(field_names: Iterable[str]) -> tuple[str, ...]:
    return tuple(str(field) for field in field_names)


def geometry_relation_schema_for_fields(
    field_names: Iterable[str],
) -> V28GeometryRelationSchema:
    fields = _normalize_field_names(field_names)
    try:
        return V2_8_GEOMETRY_RELATION_SCHEMAS[fields]
    except KeyError as exc:
        raise ValueError(f"unsupported v2.8 geometry relation row schema: {fields}") from exc


def make_v2_8_geometry_relation_typed_stream_contract(
    field_names: Iterable[str],
    row_count: int,
    *,
    stream_id: str | None = None,
    producer_primitive: str | None = None,
    device_type: str = "cpu",
    device_id: int = 0,
    source_protocol: str = "optix_host_row_view",
    data_ptrs: dict[str, int] | None = None,
) -> V28TypedResultStreamContract:
    schema = geometry_relation_schema_for_fields(field_names)
    count = int(row_count)
    if count < 0:
        raise ValueError("row_count must be non-negative")
    ptrs = {str(key): int(value) for key, value in dict(data_ptrs or {}).items()}
    columns = tuple(
        typed_result_column(
            spec.name,
            spec.role,
            spec.dtype,
            (count,),
            device_type=str(device_type),
            device_id=int(device_id),
            data_ptr=ptrs.get(spec.name),
            source_protocol=str(source_protocol),
            capacity_elements=count,
        )
        for spec in schema.columns
    )
    return make_typed_result_stream_contract(
        stream_id=stream_id or schema.schema_id,
        stream_kind="candidate_stream",
        producer_primitive=producer_primitive or schema.producer_primitive,
        columns=columns,
        status_columns=typed_result_status_columns(
            device_type=str(device_type),
            device_id=int(device_id),
            source_protocol=str(source_protocol),
        ),
        ordering="stable_row_order",
        page_capacity=max(1, count),
    )


def make_v2_8_geometry_relation_typed_producer_metadata(
    field_names: Iterable[str],
    row_count: int,
    *,
    source_protocol: str = "optix_host_row_view",
    output_residency: str | None = None,
    native_symbol: str | None = None,
) -> dict[str, Any]:
    schema = geometry_relation_schema_for_fields(field_names)
    return {
        "version": V2_8_GEOMETRY_RELATION_TYPED_PRODUCER_VERSION,
        "status": V2_8_GEOMETRY_RELATION_TYPED_PRODUCER_STATUS,
        "schema_id": schema.schema_id,
        "producer_primitive": schema.producer_primitive,
        "row_count": int(row_count),
        "column_names": tuple(spec.name for spec in schema.columns),
        "source_protocol": str(source_protocol),
        "producer_output_residency": output_residency or schema.output_residency,
        "native_symbol": native_symbol,
        "native_typed_producer_metadata_present": True,
        "device_resident_output_stream_proven": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "claim_boundary": V2_8_GEOMETRY_RELATION_TYPED_PRODUCER_CLAIM_BOUNDARY,
    }


def geometry_relation_typed_stream_metadata_for_row_view(
    *,
    field_names: Iterable[str],
    row_count: int,
    source_protocol: str = "optix_host_row_view",
    native_symbol: str | None = None,
) -> dict[str, Any]:
    typed_stream = make_v2_8_geometry_relation_typed_stream_contract(
        field_names,
        row_count,
        source_protocol=source_protocol,
    ).to_metadata()
    producer_metadata = make_v2_8_geometry_relation_typed_producer_metadata(
        field_names,
        row_count,
        source_protocol=source_protocol,
        native_symbol=native_symbol,
    )
    return {
        "typed_result_stream": typed_stream,
        "v2_8_typed_producer_metadata": producer_metadata,
    }


__all__ = [
    "V28GeometryRelationColumnSpec",
    "V28GeometryRelationSchema",
    "V2_8_GEOMETRY_RELATION_SCHEMAS",
    "V2_8_GEOMETRY_RELATION_TYPED_PRODUCER_CLAIM_BOUNDARY",
    "V2_8_GEOMETRY_RELATION_TYPED_PRODUCER_STATUS",
    "V2_8_GEOMETRY_RELATION_TYPED_PRODUCER_VERSION",
    "geometry_relation_schema_for_fields",
    "geometry_relation_typed_stream_metadata_for_row_view",
    "make_v2_8_geometry_relation_typed_producer_metadata",
    "make_v2_8_geometry_relation_typed_stream_contract",
]

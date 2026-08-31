from __future__ import annotations

from typing import Any, Mapping

from .v2_8_typed_result_stream import V28TypedResultStreamContract
from .v2_8_typed_result_stream import make_typed_result_stream_contract
from .v2_8_typed_result_stream import typed_result_column
from .v2_8_typed_result_stream import typed_result_status_columns


V2_8_POINT_GROUP_NEAREST_WITNESS_TYPED_PRODUCER_VERSION = (
    "rtdl.v2_8.point_group_nearest_witness_typed_producer.v1"
)
V2_8_POINT_GROUP_NEAREST_WITNESS_TYPED_PRODUCER_PRIMITIVE = "point_group_nearest_witness_2d"
V2_8_POINT_GROUP_NEAREST_WITNESS_COLUMNS = ("query_id", "neighbor_id", "distance")
V2_8_POINT_GROUP_NEAREST_WITNESS_CLAIM_BOUNDARY = (
    "This is generic typed producer metadata for point/group nearest-witness "
    "columns. It can record partner-owned CUDA output columns without host row "
    "materialization, but it does not authorize a release, public speedup "
    "wording, broad RT-core wording, true-zero-copy wording, hidden dispatch, "
    "hidden partner selection, or app-specific native-engine behavior."
)


def make_v2_8_point_group_nearest_witness_typed_stream_contract(
    row_count: int,
    *,
    stream_id: str = "point_group_nearest_witness_2d",
    device_type: str = "cuda",
    device_id: int = 0,
    source_protocol: str = "partner_owned_cuda_output_columns",
    data_ptrs: Mapping[str, int] | None = None,
) -> V28TypedResultStreamContract:
    """Describe one nearest-witness row per query as a v2.8 typed stream."""

    count = int(row_count)
    if count < 0:
        raise ValueError("row_count must be non-negative")
    ptrs = {str(key): int(value) for key, value in dict(data_ptrs or {}).items()}
    data_columns = (
        typed_result_column(
            "query_id",
            "group_key",
            "uint32",
            (count,),
            device_type=str(device_type),
            device_id=int(device_id),
            data_ptr=ptrs.get("query_id"),
            access_mode="write",
            source_protocol=str(source_protocol),
            capacity_elements=count,
        ),
        typed_result_column(
            "neighbor_id",
            "witness",
            "uint32",
            (count,),
            device_type=str(device_type),
            device_id=int(device_id),
            data_ptr=ptrs.get("neighbor_id"),
            access_mode="write",
            source_protocol=str(source_protocol),
            capacity_elements=count,
        ),
        typed_result_column(
            "distance",
            "score",
            "float64",
            (count,),
            device_type=str(device_type),
            device_id=int(device_id),
            data_ptr=ptrs.get("distance"),
            access_mode="write",
            source_protocol=str(source_protocol),
            capacity_elements=count,
        ),
    )
    return make_typed_result_stream_contract(
        stream_id=str(stream_id),
        stream_kind="candidate_stream",
        producer_primitive=V2_8_POINT_GROUP_NEAREST_WITNESS_TYPED_PRODUCER_PRIMITIVE,
        columns=data_columns,
        status_columns=typed_result_status_columns(
            device_type="cpu",
            source_protocol="metadata_status_columns_no_device_status_buffer",
        ),
        ordering="stable_row_order",
        page_capacity=max(1, count),
    )


def make_v2_8_point_group_nearest_witness_typed_producer_metadata(
    typed_stream: V28TypedResultStreamContract | Mapping[str, Any],
    *,
    backend: str,
    native_symbol: str,
    native_execution_path: str,
    query_count: int,
    search_count: int,
    group_count: int,
    radius: float,
    transfer_mode: str,
    source_protocols: tuple[str, ...] = (),
    source_devices: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Build claim-bounded metadata for the generic nearest-witness producer."""

    stream_metadata = (
        typed_stream.to_metadata()
        if isinstance(typed_stream, V28TypedResultStreamContract)
        else dict(typed_stream)
    )
    device_resident_data_columns = sum(
        1
        for column in stream_metadata.get("columns", ())
        if column.get("device_resident") is True
    )
    output_columns_proven = (
        device_resident_data_columns == len(V2_8_POINT_GROUP_NEAREST_WITNESS_COLUMNS)
        and str(backend) in {"optix", "hiprt"}
        and int(query_count) > 0
    )
    return {
        "version": V2_8_POINT_GROUP_NEAREST_WITNESS_TYPED_PRODUCER_VERSION,
        "producer_primitive": V2_8_POINT_GROUP_NEAREST_WITNESS_TYPED_PRODUCER_PRIMITIVE,
        "backend": str(backend),
        "native_symbol": str(native_symbol),
        "native_execution_path": str(native_execution_path),
        "row_count": int(query_count),
        "query_count": int(query_count),
        "search_count": int(search_count),
        "group_count": int(group_count),
        "radius": float(radius),
        "column_names": V2_8_POINT_GROUP_NEAREST_WITNESS_COLUMNS,
        "output_column_count": len(V2_8_POINT_GROUP_NEAREST_WITNESS_COLUMNS),
        "device_resident_output_columns_proven": bool(output_columns_proven),
        "producer_output_residency": (
            "partner_owned_cuda_output_columns"
            if output_columns_proven
            else "metadata_only_or_empty_output_columns"
        ),
        "device_resident_output_stream_proven": bool(output_columns_proven),
        "host_row_materialization_used": False,
        "transfer_mode": str(transfer_mode),
        "source_protocols": tuple(str(value) for value in source_protocols),
        "source_devices": tuple(str(value) for value in source_devices),
        "native_typed_producer_metadata_present": True,
        "end_to_end_true_zero_copy_proven": False,
        "release_authorized": False,
        "v2_8_release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "claim_boundary": V2_8_POINT_GROUP_NEAREST_WITNESS_CLAIM_BOUNDARY,
    }


__all__ = [
    "V2_8_POINT_GROUP_NEAREST_WITNESS_CLAIM_BOUNDARY",
    "V2_8_POINT_GROUP_NEAREST_WITNESS_COLUMNS",
    "V2_8_POINT_GROUP_NEAREST_WITNESS_TYPED_PRODUCER_PRIMITIVE",
    "V2_8_POINT_GROUP_NEAREST_WITNESS_TYPED_PRODUCER_VERSION",
    "make_v2_8_point_group_nearest_witness_typed_producer_metadata",
    "make_v2_8_point_group_nearest_witness_typed_stream_contract",
]

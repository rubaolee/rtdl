from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .hit_stream_handoff import RtdlHitStreamColumnHandoff
from .hit_stream_handoff import RtdlRawCudaColumn
from .v2_6_neutral_partner_handoff import V2_6_NEUTRAL_PARTNER_HANDOFF_VERSION
from .v2_6_neutral_partner_handoff import plan_v2_6_neutral_partner_handoff


DEVICE_COLUMN_ROW_BUFFER_CONTRACT_VERSION = "rtdl.device_column_row_buffer.v2_14_2.layer1"
DEVICE_COLUMN_ROW_BUFFER_API_MATURITY = "experimental_reuse_adapter_no_release_claim"
DEVICE_COLUMN_BUFFER_CONTRACT_VERSION = "rtdl.device_column_buffer.v2_14_4.public.v1"
DEVICE_COLUMN_BUFFER_API_MATURITY = "public_contract_device_columnar_prepared_pipeline"
DEVICE_COLUMN_ROW_BUFFER_SOURCE_MODES = (
    "native_device_columns",
    "host_rows_to_columns_bridge",
    "reference_columns",
)
DEVICE_COLUMN_ROW_BUFFER_STREAM_ORDERING_STATES = (
    "not_proven",
    "same_stream",
    "producer_event_waited_by_consumer",
    "host_synchronized_before_consumer",
)
DEVICE_COLUMN_ROW_BUFFER_CLAIM_BOUNDARY = (
    "This row-buffer adapter reuses the v2.5/v2.6 device-column and neutral "
    "partner handoff contracts. It validates named primitive-output columns for "
    "explicit CuPy/Numba continuation planning. It does not execute the partner "
    "continuation, authorize true-zero-copy wording, authorize speedup wording, "
    "or promote any app-specific output schema into RTDL core."
)
DEVICE_COLUMN_BUFFER_CLAIM_BOUNDARY = (
    "Public v2.14.4 device-column buffer contract.  It exposes typed primitive "
    "output columns, lifetime metadata, stream-ordering metadata, and verified "
    "host-materialization status.  It does not authorize speedup, whole-app, "
    "or true-zero-copy wording, and it does not encode app-specific schemas."
)
DEVICE_COLUMN_BUFFER_OWNER_LIFETIME_STATES = (
    "borrowed",
    "owned_close_on_buffer_close",
    "no_close_required",
)


@dataclass(frozen=True)
class RtdlDeviceColumnRowBuffer:
    """Generic named-column carrier between RTDL primitive output and partners.

    This is intentionally narrower than a memory manager.  It records row-buffer
    shape, source residency, stream-ordering status, and the original producer,
    then delegates partner validation to the existing v2.6 neutral handoff path.
    """

    columns: Mapping[str, Any]
    row_count: int
    producer: str
    source_mode: str = "native_device_columns"
    materializes_host_rows_for_bridge: bool = False
    phase_timing_seconds: Mapping[str, float] | None = None
    owner: Any = None
    producer_consumer_stream_ordering: str = "not_proven"
    native_device_column_output_proven_on_hardware: bool = False

    def __post_init__(self) -> None:
        columns = dict(self.columns)
        if not columns:
            raise ValueError("device-column row buffer requires at least one named column")
        if not str(self.producer):
            raise ValueError("device-column row buffer requires a producer")
        if self.source_mode not in DEVICE_COLUMN_ROW_BUFFER_SOURCE_MODES:
            raise ValueError("unsupported device-column row-buffer source mode")
        if self.producer_consumer_stream_ordering not in DEVICE_COLUMN_ROW_BUFFER_STREAM_ORDERING_STATES:
            raise ValueError("unsupported device-column row-buffer stream ordering state")
        row_count = int(self.row_count)
        if row_count < 0:
            raise ValueError("device-column row buffer row_count must be non-negative")
        for raw_name, column in columns.items():
            name = str(raw_name)
            if not name:
                raise ValueError("device-column row buffer column names must be non-empty")
            length = _column_length(column)
            if length != row_count:
                raise ValueError(f"{name} length must match row_count")
        if self.materializes_host_rows_for_bridge and self.source_mode == "native_device_columns":
            raise ValueError("native_device_columns cannot materialize host rows before handoff")
        object.__setattr__(self, "columns", columns)
        object.__setattr__(self, "row_count", row_count)
        if self.phase_timing_seconds is None:
            object.__setattr__(self, "phase_timing_seconds", {})
        else:
            object.__setattr__(self, "phase_timing_seconds", dict(self.phase_timing_seconds))

    @property
    def column_count(self) -> int:
        return len(self.columns)

    @property
    def device_resident_candidate(self) -> bool:
        return (
            self.source_mode == "native_device_columns"
            and not self.materializes_host_rows_for_bridge
            and all(_has_direct_device_interface(column) for column in self.columns.values())
        )

    def to_metadata(self) -> dict[str, Any]:
        return {
            "contract_version": DEVICE_COLUMN_ROW_BUFFER_CONTRACT_VERSION,
            "api_maturity": DEVICE_COLUMN_ROW_BUFFER_API_MATURITY,
            "row_count": int(self.row_count),
            "column_count": self.column_count,
            "columns": tuple(self.columns.keys()),
            "producer": self.producer,
            "source_mode": self.source_mode,
            "materializes_host_rows_for_bridge": bool(self.materializes_host_rows_for_bridge),
            "host_rows_materialized_before_partner_handoff": bool(self.materializes_host_rows_for_bridge),
            "device_resident_candidate": self.device_resident_candidate,
            "native_device_column_output_proven_on_hardware": bool(
                self.native_device_column_output_proven_on_hardware
            ),
            "producer_consumer_stream_ordering": self.producer_consumer_stream_ordering,
            "stream_synchronization_proven": self.producer_consumer_stream_ordering != "not_proven",
            "phase_timing_seconds": dict(self.phase_timing_seconds or {}),
            "column_records": tuple(
                _column_record(name, column)
                for name, column in self.columns.items()
            ),
            "reuses_v2_5_device_column_contract": True,
            "neutral_partner_handoff_version": V2_6_NEUTRAL_PARTNER_HANDOFF_VERSION,
            "engine_boundary": "generic_app_agnostic_primitive_output_columns",
            "app_specific_schema_allowed": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "claim_boundary": DEVICE_COLUMN_ROW_BUFFER_CLAIM_BOUNDARY,
        }


@dataclass
class DeviceColumnBuffer:
    """Public v2.14.4 wrapper for typed primitive-output device columns."""

    row_buffer: RtdlDeviceColumnRowBuffer
    owner_lifetime: str = "borrowed"
    _closed: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.row_buffer, RtdlDeviceColumnRowBuffer):
            raise ValueError("DeviceColumnBuffer requires an RtdlDeviceColumnRowBuffer substrate")
        if self.owner_lifetime not in DEVICE_COLUMN_BUFFER_OWNER_LIFETIME_STATES:
            raise ValueError("unsupported DeviceColumnBuffer owner_lifetime")

    def __enter__(self) -> "DeviceColumnBuffer":
        if self._closed:
            raise ValueError("cannot enter a closed DeviceColumnBuffer")
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    @classmethod
    def from_row_buffer(
        cls,
        row_buffer: RtdlDeviceColumnRowBuffer,
        *,
        owner_lifetime: str = "borrowed",
    ) -> "DeviceColumnBuffer":
        return cls(row_buffer=row_buffer, owner_lifetime=owner_lifetime)

    @property
    def columns(self) -> Mapping[str, Any]:
        return self.row_buffer.columns

    @property
    def row_count(self) -> int:
        return self.row_buffer.row_count

    @property
    def column_count(self) -> int:
        return self.row_buffer.column_count

    @property
    def producer(self) -> str:
        return self.row_buffer.producer

    @property
    def source_mode(self) -> str:
        return self.row_buffer.source_mode

    @property
    def materializes_host_rows_for_bridge(self) -> bool:
        return self.row_buffer.materializes_host_rows_for_bridge

    @property
    def producer_consumer_stream_ordering(self) -> str:
        return self.row_buffer.producer_consumer_stream_ordering

    @property
    def device_resident_candidate(self) -> bool:
        return self.row_buffer.device_resident_candidate

    @property
    def closed(self) -> bool:
        return bool(self._closed)

    def close(self) -> None:
        if self._closed:
            return
        owner = self.row_buffer.owner
        if self.owner_lifetime == "owned_close_on_buffer_close" and callable(getattr(owner, "close", None)):
            owner.close()
        self._closed = True

    def to_metadata(self) -> dict[str, Any]:
        substrate = self.row_buffer.to_metadata()
        return {
            "contract_version": DEVICE_COLUMN_BUFFER_CONTRACT_VERSION,
            "api_maturity": DEVICE_COLUMN_BUFFER_API_MATURITY,
            "substrate_contract_version": substrate["contract_version"],
            "row_count": int(self.row_count),
            "column_count": int(self.column_count),
            "columns": tuple(self.columns.keys()),
            "producer": self.producer,
            "source_mode": self.source_mode,
            "materializes_host_rows_for_bridge": bool(self.materializes_host_rows_for_bridge),
            "host_rows_materialized_before_partner_handoff": bool(
                self.materializes_host_rows_for_bridge
            ),
            "device_resident_candidate": bool(self.device_resident_candidate),
            "native_device_column_output_proven_on_hardware": bool(
                substrate["native_device_column_output_proven_on_hardware"]
            ),
            "producer_consumer_stream_ordering": self.producer_consumer_stream_ordering,
            "stream_synchronization_proven": self.producer_consumer_stream_ordering != "not_proven",
            "owner_lifetime": self.owner_lifetime,
            "closed": bool(self.closed),
            "column_records": substrate["column_records"],
            "phase_timing_seconds": substrate["phase_timing_seconds"],
            "app_specific_schema_allowed": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "residency_self_declared": False,
            "claim_boundary": DEVICE_COLUMN_BUFFER_CLAIM_BOUNDARY,
        }

    def plan_partner_handoff(
        self,
        *,
        partner: str,
        consumer: str | None = None,
        access_modes: Mapping[str, str] | None = None,
        require_device_resident: bool = True,
    ) -> dict[str, Any]:
        packet = plan_device_column_row_buffer_partner_handoff(
            self.row_buffer,
            partner=partner,
            consumer=consumer,
            access_modes=access_modes,
            require_device_resident=require_device_resident,
        )
        packet["public_device_column_buffer"] = self.to_metadata()
        return packet

    def prepare_partner_handoff(
        self,
        *,
        partner: str,
        consumer: str | None = None,
        access_modes: Mapping[str, str] | None = None,
        require_device_resident: bool = True,
    ) -> dict[str, Any]:
        packet = self.plan_partner_handoff(
            partner=partner,
            consumer=consumer,
            access_modes=access_modes,
            require_device_resident=require_device_resident,
        )
        if packet["status"] != "accept":
            raise ValueError("; ".join(str(error) for error in packet["errors"]))
        return packet


def describe_device_column_buffer_contract() -> dict[str, Any]:
    return {
        "contract_version": DEVICE_COLUMN_BUFFER_CONTRACT_VERSION,
        "api_maturity": DEVICE_COLUMN_BUFFER_API_MATURITY,
        "substrate_contract_version": DEVICE_COLUMN_ROW_BUFFER_CONTRACT_VERSION,
        "source_modes": DEVICE_COLUMN_ROW_BUFFER_SOURCE_MODES,
        "stream_ordering_states": DEVICE_COLUMN_ROW_BUFFER_STREAM_ORDERING_STATES,
        "owner_lifetime_states": DEVICE_COLUMN_BUFFER_OWNER_LIFETIME_STATES,
        "device_residency_derived_from_metadata": True,
        "self_declared_residency_allowed": False,
        "app_specific_schema_allowed": False,
        "true_zero_copy_claim_authorized": False,
        "public_speedup_claim_authorized": False,
        "claim_boundary": DEVICE_COLUMN_BUFFER_CLAIM_BOUNDARY,
    }


def device_column_buffer(
    columns: Mapping[str, Any],
    *,
    row_count: int | None = None,
    producer: str,
    source_mode: str = "native_device_columns",
    materializes_host_rows_for_bridge: bool = False,
    phase_timing_seconds: Mapping[str, float] | None = None,
    owner: Any = None,
    owner_lifetime: str = "borrowed",
    producer_consumer_stream_ordering: str = "not_proven",
    native_device_column_output_proven_on_hardware: bool = False,
) -> DeviceColumnBuffer:
    row_buffer = prepare_device_column_row_buffer(
        columns,
        row_count=row_count,
        producer=producer,
        source_mode=source_mode,
        materializes_host_rows_for_bridge=materializes_host_rows_for_bridge,
        phase_timing_seconds=phase_timing_seconds,
        owner=owner,
        producer_consumer_stream_ordering=producer_consumer_stream_ordering,
        native_device_column_output_proven_on_hardware=native_device_column_output_proven_on_hardware,
    )
    return DeviceColumnBuffer.from_row_buffer(row_buffer, owner_lifetime=owner_lifetime)


def device_column_buffer_from_row_buffer(
    row_buffer: RtdlDeviceColumnRowBuffer,
    *,
    owner_lifetime: str = "borrowed",
) -> DeviceColumnBuffer:
    return DeviceColumnBuffer.from_row_buffer(row_buffer, owner_lifetime=owner_lifetime)


def describe_device_column_row_buffer_contract() -> dict[str, Any]:
    return {
        "contract_version": DEVICE_COLUMN_ROW_BUFFER_CONTRACT_VERSION,
        "api_maturity": DEVICE_COLUMN_ROW_BUFFER_API_MATURITY,
        "source_modes": DEVICE_COLUMN_ROW_BUFFER_SOURCE_MODES,
        "supported_partner_handoff": ("cupy", "numba"),
        "reuses_v2_5_hit_stream_device_columns": True,
        "reuses_v2_6_neutral_partner_handoff": True,
        "torch_carrier_required": False,
        "app_specific_schema_allowed": False,
        "true_zero_copy_claim_authorized": False,
        "public_speedup_claim_authorized": False,
        "claim_boundary": DEVICE_COLUMN_ROW_BUFFER_CLAIM_BOUNDARY,
    }


def prepare_device_column_row_buffer(
    columns: Mapping[str, Any],
    *,
    row_count: int | None = None,
    producer: str,
    source_mode: str = "native_device_columns",
    materializes_host_rows_for_bridge: bool = False,
    phase_timing_seconds: Mapping[str, float] | None = None,
    owner: Any = None,
    producer_consumer_stream_ordering: str = "not_proven",
    native_device_column_output_proven_on_hardware: bool = False,
) -> RtdlDeviceColumnRowBuffer:
    resolved_columns = dict(columns)
    if row_count is None:
        if not resolved_columns:
            raise ValueError("row_count is required when no columns are provided")
        first = next(iter(resolved_columns.values()))
        row_count = _column_length(first)
    return RtdlDeviceColumnRowBuffer(
        columns=resolved_columns,
        row_count=int(row_count),
        producer=producer,
        source_mode=source_mode,
        materializes_host_rows_for_bridge=bool(materializes_host_rows_for_bridge),
        phase_timing_seconds=phase_timing_seconds,
        owner=owner,
        producer_consumer_stream_ordering=producer_consumer_stream_ordering,
        native_device_column_output_proven_on_hardware=bool(native_device_column_output_proven_on_hardware),
    )


def device_column_row_buffer_from_hit_stream_handoff(
    hit_stream_columns: RtdlHitStreamColumnHandoff,
    *,
    producer: str | None = None,
) -> RtdlDeviceColumnRowBuffer:
    resolved_producer = (
        f"{hit_stream_columns.backend}_ray_triangle_hit_stream"
        if producer is None
        else str(producer)
    )
    return prepare_device_column_row_buffer(
        {
            "ray_ids": hit_stream_columns.ray_ids,
            "primitive_ids": hit_stream_columns.primitive_ids,
        },
        row_count=hit_stream_columns.row_count,
        producer=resolved_producer,
        source_mode=hit_stream_columns.source_mode,
        materializes_host_rows_for_bridge=hit_stream_columns.materializes_host_rows_for_bridge,
        phase_timing_seconds=hit_stream_columns.phase_timing_seconds,
        owner=hit_stream_columns,
        producer_consumer_stream_ordering=hit_stream_columns.producer_consumer_stream_ordering,
        native_device_column_output_proven_on_hardware=(
            hit_stream_columns.native_device_column_output_proven_on_hardware
        ),
    )


def device_column_row_buffer_from_native_pair_columns(
    pair_columns: Any,
    *,
    producer: str | None = None,
) -> RtdlDeviceColumnRowBuffer:
    """Adapt a native ``left_id/right_id`` pair-column producer to Layer 1.

    The first supported producer is the OptiX segment-pair candidate device
    column route.  The adapter intentionally carries only the generic pair-id
    columns; relation-status or app-specific side channels must be surfaced by a
    separate, explicitly typed producer before they can enter this carrier.
    """

    field_names = tuple(getattr(pair_columns, "field_names", ("left_id", "right_id")))
    if len(field_names) != 2:
        raise ValueError("native pair-column output must expose exactly two field names")
    row_count = int(getattr(pair_columns, "row_count"))
    device_id = int(getattr(pair_columns, "device_ordinal", 0))
    left_ptr = int(getattr(pair_columns, "left_ids_device_ptr"))
    right_ptr = int(getattr(pair_columns, "right_ids_device_ptr"))
    native_symbol = str(getattr(pair_columns, "native_symbol", "native_pair_columns"))
    traversal_seconds = getattr(pair_columns, "traversal_seconds", None)
    phase_timing_seconds = {}
    if traversal_seconds is not None:
        phase_timing_seconds["rt_traversal"] = float(traversal_seconds)
    resolved_producer = producer or native_symbol
    return prepare_device_column_row_buffer(
        {
            str(field_names[0]): RtdlRawCudaColumn(
                str(field_names[0]),
                "int64",
                left_ptr,
                row_count,
                device_id=device_id,
                owner=pair_columns,
            ),
            str(field_names[1]): RtdlRawCudaColumn(
                str(field_names[1]),
                "int64",
                right_ptr,
                row_count,
                device_id=device_id,
                owner=pair_columns,
            ),
        },
        row_count=row_count,
        producer=resolved_producer,
        source_mode="native_device_columns",
        materializes_host_rows_for_bridge=False,
        phase_timing_seconds=phase_timing_seconds,
        owner=pair_columns,
        producer_consumer_stream_ordering="host_synchronized_before_consumer",
        native_device_column_output_proven_on_hardware=bool(
            getattr(pair_columns, "device_resident", False)
        ),
    )


def device_column_row_buffer_from_point_location_id_columns(
    id_columns: Any,
    *,
    producer: str | None = None,
) -> RtdlDeviceColumnRowBuffer:
    """Adapt a directed point-location id-column producer to Layer 1.

    The carrier is deliberately just the produced id vector (`face_id` or
    `segment_id`).  It does not encode output chains, domain semantics, or an
    app-specific output schema.
    """

    field_name = str(getattr(id_columns, "field_name", "id"))
    if field_name not in {"face_id", "segment_id"}:
        raise ValueError("point-location id columns must expose face_id or segment_id")
    row_count = int(getattr(id_columns, "row_count"))
    device_id = int(getattr(id_columns, "device_ordinal", 0))
    ids_ptr = int(getattr(id_columns, "ids_device_ptr"))
    dtype = str(getattr(id_columns, "dtype", "uint32"))
    native_symbol = str(getattr(id_columns, "native_symbol", "directed_point_location_id_columns"))
    traversal_seconds = getattr(id_columns, "traversal_seconds", None)
    phase_timing_seconds = {}
    if traversal_seconds is not None:
        phase_timing_seconds["rt_traversal"] = float(traversal_seconds)
    resolved_producer = producer or native_symbol
    return prepare_device_column_row_buffer(
        {
            field_name: RtdlRawCudaColumn(
                field_name,
                dtype,
                ids_ptr,
                row_count,
                device_id=device_id,
                owner=id_columns,
            ),
        },
        row_count=row_count,
        producer=resolved_producer,
        source_mode="native_device_columns",
        materializes_host_rows_for_bridge=False,
        phase_timing_seconds=phase_timing_seconds,
        owner=id_columns,
        producer_consumer_stream_ordering="host_synchronized_before_consumer",
        native_device_column_output_proven_on_hardware=bool(
            getattr(id_columns, "device_resident", False)
        ),
    )


def plan_device_column_row_buffer_partner_handoff(
    row_buffer: RtdlDeviceColumnRowBuffer,
    *,
    partner: str,
    consumer: str | None = None,
    access_modes: Mapping[str, str] | None = None,
    require_device_resident: bool = True,
) -> dict[str, Any]:
    errors: list[str] = []
    if require_device_resident and row_buffer.materializes_host_rows_for_bridge:
        errors.append("host-materialized row buffers cannot satisfy device-resident partner handoff")
    neutral_packet = plan_v2_6_neutral_partner_handoff(
        row_buffer.columns,
        partner=partner,
        producer=row_buffer.producer,
        consumer=consumer,
        access_modes=access_modes,
        require_device_resident=require_device_resident,
    )
    errors.extend(str(error) for error in neutral_packet.get("errors", ()))
    status = "accept" if not errors and neutral_packet.get("status") == "accept" else "reject"
    row_metadata = row_buffer.to_metadata()
    return {
        "contract_version": DEVICE_COLUMN_ROW_BUFFER_CONTRACT_VERSION,
        "row_buffer": row_metadata,
        "neutral_handoff": neutral_packet,
        "status": status,
        "selected_partner": neutral_packet.get("selected_partner"),
        "row_count": int(row_buffer.row_count),
        "column_count": row_buffer.column_count,
        "all_columns_device_resident": bool(neutral_packet.get("all_columns_device_resident")),
        "device_resident_candidate": row_buffer.device_resident_candidate,
        "materializes_host_rows_for_bridge": bool(row_buffer.materializes_host_rows_for_bridge),
        "torch_conversion_used": False,
        "torch_carrier_used": False,
        "silent_cross_partner_torch_coercion_allowed": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "errors": tuple(errors),
        "claim_boundary": DEVICE_COLUMN_ROW_BUFFER_CLAIM_BOUNDARY,
    }


def prepare_device_column_row_buffer_partner_handoff(
    row_buffer: RtdlDeviceColumnRowBuffer,
    *,
    partner: str,
    consumer: str | None = None,
    access_modes: Mapping[str, str] | None = None,
    require_device_resident: bool = True,
) -> dict[str, Any]:
    packet = plan_device_column_row_buffer_partner_handoff(
        row_buffer,
        partner=partner,
        consumer=consumer,
        access_modes=access_modes,
        require_device_resident=require_device_resident,
    )
    if packet["status"] != "accept":
        raise ValueError("; ".join(str(error) for error in packet["errors"]))
    return packet


def _column_length(column: Any) -> int:
    shape = getattr(column, "shape", None)
    if shape is not None:
        if len(shape) == 0:
            raise ValueError("device-column row-buffer columns must be one-dimensional")
        return int(shape[0])
    return len(column)


def _column_record(name: str, column: Any) -> dict[str, Any]:
    return {
        "name": str(name),
        "length": _column_length(column),
        "source_protocol": _source_protocol(column),
        "device_resident_candidate": _has_direct_device_interface(column),
        "has_cuda_array_interface": isinstance(getattr(column, "__cuda_array_interface__", None), Mapping),
        "has_dlpack": callable(getattr(column, "__dlpack__", None)),
    }


def _source_protocol(column: Any) -> str:
    module = type(column).__module__.split(".", 1)[0]
    if module in {"torch", "cupy", "numpy", "numba"}:
        return module
    if callable(getattr(column, "__dlpack__", None)) and callable(getattr(column, "__dlpack_device__", None)):
        return "dlpack"
    if isinstance(getattr(column, "__cuda_array_interface__", None), Mapping):
        return "cuda_array_interface"
    if isinstance(getattr(column, "__array_interface__", None), Mapping):
        return "array_interface"
    return "python"


def _has_direct_device_interface(column: Any) -> bool:
    cuda_interface = getattr(column, "__cuda_array_interface__", None)
    if isinstance(cuda_interface, Mapping):
        data = cuda_interface.get("data")
        if isinstance(data, tuple) and data and int(data[0]) > 0:
            return True
    return callable(getattr(column, "__dlpack__", None)) and callable(getattr(column, "__dlpack_device__", None))

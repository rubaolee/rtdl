from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Mapping, Sequence

from .generic_primitives import GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_PRIMITIVE
from .generic_primitives import GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_ROW_SCHEMA
from .neutral_buffer_seam import V2_5_NEUTRAL_BUFFER_SEAM_VERSION
from .neutral_buffer_seam import neutral_buffer_descriptor_from_rtdl_buffer
from .partner_protocol import RtdlBufferDescriptor
from .partner_protocol import V2_4_PHASES
from .v2_5_partner_support_matrix import plan_v2_5_partner_support


GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION = "rtdl.rt_hit_stream_handoff.v2.5"
GENERIC_HIT_STREAM_HANDOFF_API_MATURITY = "experimental_host_bridge_contract"
GENERIC_DEVICE_RESIDENT_HIT_STREAM_COLUMNS = ("ray_ids:int64", "primitive_ids:int64")
GENERIC_TYPED_PRIMITIVE_PAYLOAD_COLUMNS = ("primitive_group_ids:int64", "primitive_values:float64")
GENERIC_HIT_STREAM_HANDOFF_SOURCE_MODES = (
    "native_device_columns",
    "host_rows_to_columns_bridge",
    "reference_columns",
)
GENERIC_TYPED_PAYLOAD_GROUP_ID_VALIDATION_MODES = (
    "host_scan",
    "caller_asserted",
    "deferred_device_check",
)
GENERIC_HIT_STREAM_HANDOFF_PHASES = (
    "rt_traversal",
    "hit_stream_column_handoff",
    "typed_payload_gather",
    "partner_continuation",
    "host_materialization",
)


@dataclass(frozen=True)
class RtdlHitStreamColumnHandoff:
    ray_ids: Any
    primitive_ids: Any
    row_count: int
    capacity: int
    overflow: bool
    backend: str
    source_mode: str
    phase_timing_seconds: Mapping[str, float]
    native_symbol: str | None = None
    materializes_host_rows_for_bridge: bool = False
    native_device_column_output_proven_on_hardware: bool = False
    owner: Any = None

    def __post_init__(self) -> None:
        row_count = int(self.row_count)
        capacity = int(self.capacity)
        if row_count < 0:
            raise ValueError("hit-stream row_count must be non-negative")
        if capacity < 0:
            raise ValueError("hit-stream capacity must be non-negative")
        if _column_length(self.ray_ids) != row_count:
            raise ValueError("ray_ids length must match row_count")
        if _column_length(self.primitive_ids) != row_count:
            raise ValueError("primitive_ids length must match row_count")
        if self.overflow and row_count != 0:
            raise ValueError("overflowed hit-stream handoffs must be fail-closed with row_count=0")
        if self.source_mode not in GENERIC_HIT_STREAM_HANDOFF_SOURCE_MODES:
            raise ValueError("unsupported hit-stream column source mode")
        _validate_int64_column(self.ray_ids, "ray_ids")
        _validate_int64_column(self.primitive_ids, "primitive_ids")
        if self.native_device_column_output_proven_on_hardware:
            if self.source_mode != "native_device_columns":
                raise ValueError("hardware-proven native device columns require source_mode=native_device_columns")
            if self.materializes_host_rows_for_bridge:
                raise ValueError("hardware-proven native device columns must not materialize host rows first")
            if self.device_type != "cuda":
                raise ValueError("hardware-proven native device columns currently require CUDA-resident columns")

    @property
    def device_type(self) -> str:
        return _device_info(self.primitive_ids)[0]

    @property
    def device_id(self) -> int:
        return _device_info(self.primitive_ids)[1]

    @property
    def source_protocol(self) -> str:
        return _source_protocol(self.primitive_ids)

    @property
    def device_resident(self) -> bool:
        return self.device_type == "cuda" and not self.materializes_host_rows_for_bridge

    @property
    def removes_host_materialization_bottleneck(self) -> bool:
        return (
            self.source_mode == "native_device_columns"
            and self.device_resident
            and not self.materializes_host_rows_for_bridge
            and bool(self.native_device_column_output_proven_on_hardware)
        )

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract_version": GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION,
            "api_maturity": GENERIC_HIT_STREAM_HANDOFF_API_MATURITY,
            "columns": GENERIC_DEVICE_RESIDENT_HIT_STREAM_COLUMNS,
            "backend": self.backend,
            "row_count": int(self.row_count),
            "capacity": int(self.capacity),
            "overflow": bool(self.overflow),
            "fail_closed_overflow": True,
            "source_mode": self.source_mode,
            "device": f"{self.device_type}:{self.device_id}",
            "source_protocol": self.source_protocol,
            "native_symbol": self.native_symbol,
            "device_resident": self.device_resident,
            "materializes_host_rows_for_bridge": bool(self.materializes_host_rows_for_bridge),
            "host_hit_rows_materialized_before_handoff": bool(self.materializes_host_rows_for_bridge),
            "removes_host_materialization_bottleneck": self.removes_host_materialization_bottleneck,
            "native_device_column_output_proven_on_hardware": bool(
                self.native_device_column_output_proven_on_hardware
            ),
            "device_resident_but_unproven_native_output": (
                self.source_mode == "native_device_columns"
                and self.device_resident
                and not bool(self.native_device_column_output_proven_on_hardware)
            ),
            "ownership_lifetime_model": (
                "native_owner_state_machine_required_before_promotion"
                if self.source_mode == "native_device_columns"
                else "caller_retained_python_reference"
            ),
            "true_zero_copy_authorized": False,
            "public_speedup_claim_authorized": False,
            "neutral_buffer_seam_contract_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
            "neutral_buffer_seams": (
                _neutral_buffer_seam_metadata(
                    "ray_ids",
                    self.ray_ids,
                    "int64",
                    producer=self.source_mode,
                    consumer="typed_payload_gather",
                    access_mode="read",
                    native_producer=self.source_mode == "native_device_columns",
                    host_materialized_before_handoff=bool(self.materializes_host_rows_for_bridge),
                ),
                _neutral_buffer_seam_metadata(
                    "primitive_ids",
                    self.primitive_ids,
                    "int64",
                    producer=self.source_mode,
                    consumer="typed_payload_gather",
                    access_mode="read",
                    native_producer=self.source_mode == "native_device_columns",
                    host_materialized_before_handoff=bool(self.materializes_host_rows_for_bridge),
                ),
            ),
            "column_descriptors": (
                _buffer_descriptor("ray_ids", self.ray_ids, "int64", access_mode="read").to_metadata(),
                _buffer_descriptor("primitive_ids", self.primitive_ids, "int64", access_mode="read").to_metadata(),
            ),
            "phase_timing_seconds": dict(self.phase_timing_seconds),
        }


@dataclass(frozen=True)
class RtdlTypedPrimitivePayloadColumns:
    primitive_group_ids: Any
    primitive_values: Any
    primitive_count: int
    group_count: int
    source_mode: str
    group_id_bounds_validation: str = "host_scan"
    default_primitive_values_used: bool = False
    owner: Any = None

    def __post_init__(self) -> None:
        primitive_count = int(self.primitive_count)
        group_count = int(self.group_count)
        if primitive_count < 0:
            raise ValueError("primitive_count must be non-negative")
        if group_count < 0:
            raise ValueError("group_count must be non-negative")
        if _column_length(self.primitive_group_ids) != primitive_count:
            raise ValueError("primitive_group_ids length must match primitive_count")
        if _column_length(self.primitive_values) != primitive_count:
            raise ValueError("primitive_values length must match primitive_count")
        if self.group_id_bounds_validation not in GENERIC_TYPED_PAYLOAD_GROUP_ID_VALIDATION_MODES:
            raise ValueError("unsupported primitive group-id validation mode")
        _validate_int64_column(self.primitive_group_ids, "primitive_group_ids")
        _validate_float64_column(self.primitive_values, "primitive_values")
        if self.group_id_bounds_validation == "host_scan":
            group_ids = _column_to_host_ints(self.primitive_group_ids)
            if any(group_id < 0 or group_id >= group_count for group_id in group_ids):
                raise ValueError("primitive group ids must be in [0, group_count)")

    @property
    def device_type(self) -> str:
        return _device_info(self.primitive_group_ids)[0]

    @property
    def device_id(self) -> int:
        return _device_info(self.primitive_group_ids)[1]

    @property
    def source_protocol(self) -> str:
        return _source_protocol(self.primitive_group_ids)

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract_version": GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION,
            "api_maturity": GENERIC_HIT_STREAM_HANDOFF_API_MATURITY,
            "columns": GENERIC_TYPED_PRIMITIVE_PAYLOAD_COLUMNS,
            "primitive_count": int(self.primitive_count),
            "group_count": int(self.group_count),
            "source_mode": self.source_mode,
            "group_id_bounds_validation": self.group_id_bounds_validation,
            "group_id_bounds_validated": self.group_id_bounds_validation == "host_scan",
            "group_id_bounds_caller_asserted": self.group_id_bounds_validation == "caller_asserted",
            "group_id_bounds_asserted_not_verified": self.group_id_bounds_validation == "caller_asserted",
            "host_scan_for_group_id_validation": self.group_id_bounds_validation == "host_scan",
            "device_group_id_validation_pending": self.group_id_bounds_validation == "deferred_device_check",
            "default_primitive_values_used": bool(self.default_primitive_values_used),
            "device": f"{self.device_type}:{self.device_id}",
            "source_protocol": self.source_protocol,
            "app_specific_semantics_allowed": False,
            "neutral_buffer_seam_contract_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
            "neutral_buffer_seams": (
                _neutral_buffer_seam_metadata(
                    "primitive_group_ids",
                    self.primitive_group_ids,
                    "int64",
                    producer=self.source_mode,
                    consumer="typed_payload_gather",
                    access_mode="read",
                ),
                _neutral_buffer_seam_metadata(
                    "primitive_values",
                    self.primitive_values,
                    "float64",
                    producer=self.source_mode,
                    consumer="typed_payload_gather",
                    access_mode="read",
                ),
            ),
            "column_descriptors": (
                _buffer_descriptor("primitive_group_ids", self.primitive_group_ids, "int64", access_mode="read").to_metadata(),
                _buffer_descriptor("primitive_values", self.primitive_values, "float64", access_mode="read").to_metadata(),
            ),
        }


def describe_generic_device_resident_hit_stream_handoff_3d() -> dict[str, object]:
    return {
        "contract_version": GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION,
        "api_maturity": GENERIC_HIT_STREAM_HANDOFF_API_MATURITY,
        "hit_stream_primitive": GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_PRIMITIVE,
        "hit_stream_columns": GENERIC_DEVICE_RESIDENT_HIT_STREAM_COLUMNS,
        "typed_primitive_payload_columns": GENERIC_TYPED_PRIMITIVE_PAYLOAD_COLUMNS,
        "row_count_metadata": ("row_count:uint64", "capacity:uint64"),
        "overflow_policy": "fail_closed_bounded_columns",
        "ownership": "producer_retains_until_partner_continuation_finishes",
        "allowed_source_modes": GENERIC_HIT_STREAM_HANDOFF_SOURCE_MODES,
        "typed_payload_group_id_validation_modes": GENERIC_TYPED_PAYLOAD_GROUP_ID_VALIDATION_MODES,
        "phase_timing_required": GENERIC_HIT_STREAM_HANDOFF_PHASES,
        "v2_4_phase_timing_basis": V2_4_PHASES,
        "native_engine_app_specific_vocab_allowed": False,
        "triton_replaces_rt_traversal": False,
        "goal2685_host_bridge_only": True,
        "native_device_column_output_proven_on_hardware": False,
        "removes_host_materialization_bottleneck": False,
        "true_zero_copy_claim_authorized": False,
        "public_speedup_claim_authorized": False,
        "claim_boundary": (
            "Goal2685 defines an experimental typed-column handoff contract for RT-produced "
            "ray/primitive hit streams. The current implementation is a host-row bridge only; "
            "native device-column output, a lifetime/ownership state machine, and pod timings "
            "are required before any zero-copy, removed-bottleneck, or speedup claim."
        ),
    }


def prepare_generic_hit_stream_columns_from_rows(
    hit_stream: Mapping[str, Any],
    *,
    prefer_torch_cuda: bool = False,
    require_torch_cuda: bool = False,
) -> RtdlHitStreamColumnHandoff:
    if hit_stream.get("primitive") != GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_PRIMITIVE:
        raise ValueError("expected a generic ray/triangle hit-stream result")
    if tuple(hit_stream.get("row_schema", ())) != GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_ROW_SCHEMA:
        raise ValueError("unexpected generic hit-stream row schema")
    if bool(hit_stream.get("overflow", False)):
        raise ValueError("cannot prepare columns from an overflowed hit stream; failure mode is fail-closed")

    started = perf_counter()
    rows = tuple(hit_stream.get("rows", ()))
    ray_values = tuple(int(row["ray_id"]) for row in rows)
    primitive_values = tuple(int(row["primitive_id"]) for row in rows)
    ray_ids = _maybe_torch_column(ray_values, dtype="int64", prefer_cuda=prefer_torch_cuda, require_cuda=require_torch_cuda)
    primitive_ids = _maybe_torch_column(
        primitive_values,
        dtype="int64",
        prefer_cuda=prefer_torch_cuda,
        require_cuda=require_torch_cuda,
    )
    elapsed = perf_counter() - started
    timings = dict(hit_stream.get("phase_timing_seconds", {}))
    timings["hit_stream_column_handoff"] = elapsed
    return RtdlHitStreamColumnHandoff(
        ray_ids=ray_ids,
        primitive_ids=primitive_ids,
        row_count=len(rows),
        capacity=int(hit_stream.get("max_rows", len(rows))),
        overflow=False,
        backend=str(hit_stream.get("backend", "unknown")),
        source_mode="host_rows_to_columns_bridge",
        phase_timing_seconds=timings,
        native_symbol=hit_stream.get("native_symbol"),
        materializes_host_rows_for_bridge=True,
        owner=hit_stream,
    )


def prepare_generic_device_resident_hit_stream_columns(
    *,
    ray_ids: Any,
    primitive_ids: Any,
    row_count: int | None = None,
    capacity: int | None = None,
    overflow: bool = False,
    backend: str = "optix",
    phase_timing_seconds: Mapping[str, float] | None = None,
    native_symbol: str | None = None,
    native_device_column_output_proven_on_hardware: bool = False,
    owner: Any = None,
) -> RtdlHitStreamColumnHandoff:
    resolved_count = _column_length(primitive_ids) if row_count is None else int(row_count)
    return RtdlHitStreamColumnHandoff(
        ray_ids=ray_ids,
        primitive_ids=primitive_ids,
        row_count=resolved_count,
        capacity=resolved_count if capacity is None else int(capacity),
        overflow=bool(overflow),
        backend=backend,
        source_mode="native_device_columns",
        phase_timing_seconds={} if phase_timing_seconds is None else dict(phase_timing_seconds),
        native_symbol=native_symbol,
        materializes_host_rows_for_bridge=False,
        native_device_column_output_proven_on_hardware=bool(native_device_column_output_proven_on_hardware),
        owner=owner,
    )


def prepare_generic_typed_primitive_payload_columns(
    primitive_group_ids: Sequence[int] | Any,
    primitive_values: Sequence[float] | Any | None = None,
    *,
    primitive_count: int | None = None,
    group_count: int | None = None,
    prefer_torch_cuda: bool = False,
    require_torch_cuda: bool = False,
    device_like: Any = None,
    group_id_bounds_validation: str | None = None,
) -> RtdlTypedPrimitivePayloadColumns:
    if group_id_bounds_validation is None:
        group_id_bounds_validation = "host_scan"
    if group_id_bounds_validation not in GENERIC_TYPED_PAYLOAD_GROUP_ID_VALIDATION_MODES:
        raise ValueError("unsupported primitive group-id validation mode")
    if primitive_count is None:
        primitive_count = _column_length(primitive_group_ids)
    default_primitive_values_used = primitive_values is None
    if primitive_values is None:
        primitive_values = tuple(1.0 for _ in range(int(primitive_count)))
    if group_count is None:
        if group_id_bounds_validation != "host_scan":
            raise ValueError("group_count must be provided when primitive group ids are not host-scanned")
        group_count = max(_column_to_host_ints(primitive_group_ids), default=-1) + 1
    use_cuda = prefer_torch_cuda or _device_info(device_like)[0] == "cuda"
    group_ids = _maybe_torch_column(
        primitive_group_ids,
        dtype="int64",
        prefer_cuda=use_cuda,
        require_cuda=require_torch_cuda,
        device_like=device_like,
    )
    values = _maybe_torch_column(
        primitive_values,
        dtype="float64",
        prefer_cuda=use_cuda,
        require_cuda=require_torch_cuda,
        device_like=device_like,
    )
    return RtdlTypedPrimitivePayloadColumns(
        primitive_group_ids=group_ids,
        primitive_values=values,
        primitive_count=int(primitive_count),
        group_count=int(group_count),
        source_mode="typed_payload_columns",
        group_id_bounds_validation=group_id_bounds_validation,
        default_primitive_values_used=default_primitive_values_used,
        owner=(primitive_group_ids, primitive_values),
    )


def gather_typed_payload_columns_for_hit_stream(
    hit_stream_columns: RtdlHitStreamColumnHandoff,
    payload_columns: RtdlTypedPrimitivePayloadColumns,
) -> tuple[dict[str, Any], dict[str, object]]:
    if hit_stream_columns.overflow:
        raise ValueError("cannot gather continuation inputs from an overflowed hit stream")
    started = perf_counter()
    _validate_primitive_ids_in_payload_range(
        hit_stream_columns.primitive_ids,
        payload_columns.primitive_count,
    )
    if _is_torch_tensor(hit_stream_columns.primitive_ids) or _is_torch_tensor(payload_columns.primitive_group_ids):
        import torch

        primitive_ids = _torch_as(hit_stream_columns.primitive_ids, dtype=torch.int64, device_like=payload_columns.primitive_group_ids)
        group_ids = _torch_as(payload_columns.primitive_group_ids, dtype=torch.int64, device_like=primitive_ids)[primitive_ids]
        values = _torch_as(payload_columns.primitive_values, dtype=torch.float64, device_like=primitive_ids)[primitive_ids]
        gather_mode = "torch_index_select"
        continuation_inputs = {
            "group_ids": group_ids,
            "values": values,
            "group_count": int(payload_columns.group_count),
        }
    else:
        primitive_ids = _column_to_host_ints(hit_stream_columns.primitive_ids)
        group_source = tuple(int(value) for value in payload_columns.primitive_group_ids)
        value_source = tuple(float(value) for value in payload_columns.primitive_values)
        continuation_inputs = {
            "group_ids": tuple(group_source[index] for index in primitive_ids),
            "values": tuple(value_source[index] for index in primitive_ids),
            "group_count": int(payload_columns.group_count),
        }
        gather_mode = "python_reference_columns"
    elapsed = perf_counter() - started
    metadata = {
        "contract_version": GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION,
        "gather_mode": gather_mode,
        "hit_stream_columns": hit_stream_columns.to_metadata(),
        "typed_primitive_payload_columns": payload_columns.to_metadata(),
        "row_count": int(hit_stream_columns.row_count),
        "group_count": int(payload_columns.group_count),
        "typed_payload_gather_sec": elapsed,
        "primitive_id_bounds_checked": True,
        "python_rebuilt_primitive_row_table": False,
        "materializes_host_rows_for_bridge": bool(hit_stream_columns.materializes_host_rows_for_bridge),
        "host_hit_rows_materialized_before_handoff": bool(hit_stream_columns.materializes_host_rows_for_bridge),
        "native_device_hit_stream_columns_ready": hit_stream_columns.source_mode == "native_device_columns",
        "removes_host_materialization_bottleneck": hit_stream_columns.removes_host_materialization_bottleneck,
        "neutral_buffer_seam_contract_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
        "neutral_buffer_handoff_summary": _neutral_buffer_handoff_summary(
            hit_stream_columns,
            payload_columns,
        ),
        "true_zero_copy_authorized": False,
        "public_speedup_claim_authorized": False,
    }
    return continuation_inputs, metadata


def plan_v2_5_hit_stream_partner_continuation(
    hit_stream_columns: RtdlHitStreamColumnHandoff,
    payload_columns: RtdlTypedPrimitivePayloadColumns,
    *,
    operation: str,
    partner: str,
) -> dict[str, object]:
    """Plan a v2.5 continuation over hit-stream/payload columns.

    This is a planning surface only. It combines the neutral buffer handoff
    metadata with the declared partner support matrix so apps can fail closed
    before they run an unsupported partner or silently pay for a copy.
    """

    support = plan_v2_5_partner_support(operation, partner)
    summary = _neutral_buffer_handoff_summary(hit_stream_columns, payload_columns)
    hit_metadata = hit_stream_columns.to_metadata()
    payload_metadata = payload_columns.to_metadata()
    seams = (
        *hit_metadata["neutral_buffer_seams"],
        *payload_metadata["neutral_buffer_seams"],
    )
    current_inputs_device_ready = all(
        seam["device_resident"] and seam["transfer_status"] != "host_stage"
        for seam in seams
    )
    requires_cuda = bool(support["requires_cuda"])
    requirements_satisfied = bool(support["supported"]) and (
        current_inputs_device_ready if requires_cuda else True
    )
    fail_closed = not bool(support["supported"])
    return {
        "contract_version": GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION,
        "neutral_buffer_seam_contract_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
        "operation": str(operation),
        "requested_partner": str(partner),
        "selected_partner": support["partner"],
        "support_cell": support,
        "neutral_buffer_handoff_summary": summary,
        "current_inputs_device_ready": current_inputs_device_ready,
        "current_inputs_satisfy_device_requirements": requirements_satisfied,
        "copy_or_host_stage_required": bool(summary["any_host_stage"]) or (
            requires_cuda and not current_inputs_device_ready
        ),
        "fail_closed": fail_closed,
        "execution_allowed_without_copy": requirements_satisfied and not summary["any_host_stage"],
        "pod_validation_required": bool(support["requires_sm70_plus"]),
        "true_zero_copy_authorized": False,
        "public_speedup_claim_authorized": False,
        "runtime_action": _partner_plan_runtime_action(
            support,
            current_inputs_device_ready=current_inputs_device_ready,
            any_host_stage=bool(summary["any_host_stage"]),
        ),
        "claim_boundary": (
            "This is a plan/explain record only. It does not execute the "
            "partner continuation, prove zero-copy, or authorize speedup claims."
        ),
    }


def _validate_primitive_ids_in_payload_range(primitive_ids: Any, primitive_count: int) -> None:
    primitive_count = int(primitive_count)
    if primitive_count < 0:
        raise ValueError("primitive_count must be non-negative")
    if _column_length(primitive_ids) == 0:
        return
    if _is_torch_tensor(primitive_ids):
        import torch

        ids = primitive_ids.to(dtype=torch.int64)
        if bool(((ids < 0) | (ids >= primitive_count)).any().detach().cpu().item()):
            raise ValueError("primitive ids must be in [0, primitive_count)")
        return
    ids = _column_to_host_ints(primitive_ids)
    if any(primitive_id < 0 or primitive_id >= primitive_count for primitive_id in ids):
        raise ValueError("primitive ids must be in [0, primitive_count)")


def _column_length(column: Any) -> int:
    if column is None:
        return 0
    shape = getattr(column, "shape", None)
    if shape is not None:
        if len(shape) == 0:
            raise ValueError("hit-stream handoff columns must be one-dimensional")
        return int(shape[0])
    return len(column)


def _column_to_host_ints(column: Any) -> tuple[int, ...]:
    if column is None:
        return ()
    if _is_torch_tensor(column):
        return tuple(int(value) for value in column.detach().cpu().tolist())
    tolist = getattr(column, "tolist", None)
    if callable(tolist):
        return tuple(int(value) for value in tolist())
    return tuple(int(value) for value in column)


def _validate_int64_column(column: Any, name: str) -> None:
    dtype = _dtype_name(column)
    if dtype is not None and dtype not in {"int64", "long"}:
        raise ValueError(f"{name} must be int64")


def _validate_float64_column(column: Any, name: str) -> None:
    dtype = _dtype_name(column)
    if dtype is not None and dtype not in {"float64", "double"}:
        raise ValueError(f"{name} must be float64")


def _dtype_name(column: Any) -> str | None:
    dtype = getattr(column, "dtype", None)
    if dtype is None:
        return None
    text = str(dtype).lower()
    if "." in text:
        text = text.rsplit(".", 1)[-1]
    return text


def _device_info(column: Any) -> tuple[str, int]:
    if column is None:
        return "cpu", 0
    device = getattr(column, "device", None)
    if device is not None:
        device_type = getattr(device, "type", None)
        device_index = getattr(device, "index", None)
        if device_type is not None:
            return str(device_type), 0 if device_index is None else int(device_index)
        text = str(device)
        if text.startswith("cuda"):
            _, _, index = text.partition(":")
            return "cuda", int(index) if index else 0
    cuda_interface = getattr(column, "__cuda_array_interface__", None)
    if isinstance(cuda_interface, Mapping):
        return "cuda", 0
    return "cpu", 0


def _source_protocol(column: Any) -> str:
    if column is None:
        return "python"
    module = type(column).__module__.split(".", 1)[0]
    if module in {"torch", "cupy", "numpy"}:
        return module
    if hasattr(column, "__cuda_array_interface__"):
        return "cuda_array_interface"
    return "python"


def _data_ptr(column: Any) -> int | None:
    data_ptr = getattr(column, "data_ptr", None)
    if callable(data_ptr):
        return int(data_ptr())
    data = getattr(column, "data", None)
    ptr = getattr(data, "ptr", None)
    if ptr is not None:
        return int(ptr)
    cuda_interface = getattr(column, "__cuda_array_interface__", None)
    if isinstance(cuda_interface, Mapping):
        pointer = cuda_interface.get("data", (None,))[0]
        return None if pointer is None else int(pointer)
    return None


def _buffer_descriptor(name: str, column: Any, dtype: str, *, access_mode: str) -> RtdlBufferDescriptor:
    device_type, device_id = _device_info(column)
    return RtdlBufferDescriptor(
        name=name,
        dtype=dtype,
        shape=(_column_length(column),),
        device_type=device_type,
        device_id=device_id,
        data_ptr=_data_ptr(column),
        access_mode=access_mode,
        source_protocol=_source_protocol(column),
        lifetime="caller_retained",
        mutability="immutable",
        capacity_elements=_column_length(column),
        owner=column,
    )


def _neutral_buffer_seam_metadata(
    name: str,
    column: Any,
    dtype: str,
    *,
    producer: str,
    consumer: str,
    access_mode: str,
    native_producer: bool = False,
    host_materialized_before_handoff: bool = False,
) -> dict[str, Any]:
    lifetime_state = "native_owned_pending_state_machine" if native_producer else "caller_retained"
    transfer_status = "host_stage" if host_materialized_before_handoff else None
    descriptor = neutral_buffer_descriptor_from_rtdl_buffer(
        _buffer_descriptor(name, column, dtype, access_mode=access_mode),
        producer=producer,
        consumer=consumer,
        lifetime_state=lifetime_state,
        native_producer=native_producer,
        transfer_status=transfer_status,
        host_materialized_before_handoff=host_materialized_before_handoff,
    )
    return descriptor.to_metadata()


def _neutral_buffer_handoff_summary(
    hit_stream_columns: RtdlHitStreamColumnHandoff,
    payload_columns: RtdlTypedPrimitivePayloadColumns,
) -> dict[str, object]:
    hit_metadata = hit_stream_columns.to_metadata()
    payload_metadata = payload_columns.to_metadata()
    hit_statuses = tuple(
        seam["transfer_status"] for seam in hit_metadata["neutral_buffer_seams"]
    )
    payload_statuses = tuple(
        seam["transfer_status"] for seam in payload_metadata["neutral_buffer_seams"]
    )
    return {
        "contract_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
        "hit_stream_transfer_statuses": hit_statuses,
        "payload_transfer_statuses": payload_statuses,
        "any_zero_copy_claim_authorized": any(
            seam["zero_copy_claim_authorized"]
            for seam in (
                *hit_metadata["neutral_buffer_seams"],
                *payload_metadata["neutral_buffer_seams"],
            )
        ),
        "any_host_stage": any(
            seam["host_materialized_before_handoff"]
            or seam["transfer_status"] == "host_stage"
            for seam in (
                *hit_metadata["neutral_buffer_seams"],
                *payload_metadata["neutral_buffer_seams"],
            )
        ),
        "claim_boundary": (
            "Current hit-stream continuation metadata is neutral-buffer-aware, "
            "but native OptiX device-column output and zero-copy evidence remain unproven."
        ),
    }


def _partner_plan_runtime_action(
    support: dict[str, Any],
    *,
    current_inputs_device_ready: bool,
    any_host_stage: bool,
) -> str:
    if not bool(support["supported"]):
        return "fail_closed_unsupported_partner_operation"
    if any_host_stage:
        return "host_stage_or_copy_must_be_explicit"
    if bool(support["requires_cuda"]) and not current_inputs_device_ready:
        return "requires_device_resident_columns_or_explicit_copy"
    if bool(support["requires_sm70_plus"]):
        return "requires_sm70_pod_validation_before_performance_claim"
    return "plan_available"


def _is_torch_tensor(value: Any) -> bool:
    return type(value).__module__.split(".", 1)[0] == "torch"


def _maybe_torch_column(
    values: Any,
    *,
    dtype: str,
    prefer_cuda: bool,
    require_cuda: bool,
    device_like: Any = None,
) -> Any:
    if _is_torch_tensor(values):
        import torch

        target_dtype = torch.int64 if dtype == "int64" else torch.float64
        target_device = getattr(device_like, "device", values.device)
        return values.to(device=target_device, dtype=target_dtype)
    if prefer_cuda or require_cuda or _device_info(device_like)[0] == "cuda":
        import torch

        if require_cuda and not torch.cuda.is_available():
            raise RuntimeError("Torch CUDA is required for native device hit-stream handoff validation")
        if torch.cuda.is_available():
            device = getattr(device_like, "device", torch.device("cuda:0"))
            target_dtype = torch.int64 if dtype == "int64" else torch.float64
            return torch.as_tensor(values, dtype=target_dtype, device=device)
    if dtype == "int64":
        return tuple(int(value) for value in values)
    return tuple(float(value) for value in values)


def _torch_as(value: Any, *, dtype: Any, device_like: Any) -> Any:
    import torch

    device = getattr(device_like, "device", None)
    if _is_torch_tensor(value):
        return value.to(dtype=dtype, device=device)
    return torch.as_tensor(value, dtype=dtype, device=device)

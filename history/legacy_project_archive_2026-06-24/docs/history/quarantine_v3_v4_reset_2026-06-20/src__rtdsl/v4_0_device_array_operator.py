from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from . import partner as _partner
from .partner_adapters import (
    allocate_fixed_radius_count_threshold_2d_partner_device_output_columns as _allocate_outputs,
)
from .partner_adapters import (
    fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns as _run_prepared,
)
from .optix_runtime import (
    prepare_optix_fixed_radius_count_threshold_2d_device_search_columns_on_stream as _prepare_scene_on_stream,
)
from .partner_adapters import (
    prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene as _prepare_scene,
)


V4_0_PRODUCT_SCOPE = "python_gpu_rt_core_operator"
V4_0_M1_ROUTE_ID = "fixed_radius_count_threshold_2d"
V4_0_M1_NATIVE_BACKEND = "optix"
V4_0_M1_OPERATOR_STATUS = "m1_route_frozen_m2_device_array_intake"
V4_0_M1_CALLER_STREAM_STATUS = "caller_stream_supported_synchronous"
V4_0_M1_CROSS_STREAM_STATUS = "fixed_radius_m1_prepare_ready_event_wait_supported_synchronous"
V4_0_M1_SUPPORTED_INPUT_PROTOCOLS = ("cuda_array_interface", "cupy")
V4_0_M1_EVIDENCE_BACKED_FRAMEWORKS = ("cupy", "numba", "pytorch")
V4_0_M1_EXPERIMENTAL_INPUT_PROTOCOLS = ("dlpack_bridge_wrapper", "legacy_dlpack_capsule")
V4_0_M1_TARGET_INPUT_PROTOCOLS = ("cuda_array_interface", "dlpack")
V4_0_M1_TARGET_FRAMEWORKS = ("cupy", "numba", "pytorch", "jax")
V4_0_M1_BLOCKED_INPUT_PROTOCOLS_WITHOUT_FULL_ROUTE_EVIDENCE = ("full_dlpack_capsule",)
V4_0_M1_BLOCKED_FRAMEWORKS_WITHOUT_ROUTE_EVIDENCE = ("jax",)

_POINT_COLUMNS = ("ids", "x", "y")
_OUTPUT_COLUMNS = ("query_ids", "neighbor_counts", "threshold_flags")
_POINT_DTYPES = {
    "ids": {"uint32"},
    "x": {"float64", "double"},
    "y": {"float64", "double"},
}
_OUTPUT_DTYPES = {
    "query_ids": {"uint32"},
    "neighbor_counts": {"uint32"},
    "threshold_flags": {"uint32"},
}


@dataclass(frozen=True)
class V4DeviceColumnDescriptor:
    """Borrowed CUDA column metadata for the V4 Python operator front door."""

    name: str
    data_ptr: int
    dtype: str
    shape: tuple[int, ...]
    strides: tuple[int, ...] | None
    device_type: str
    device_id: int
    access_mode: str
    source_protocol: str
    producer_stream_handle: int
    owner: Any = field(repr=False, compare=False)

    @property
    def device(self) -> str:
        return f"{self.device_type}:{self.device_id}"

    def to_metadata(self) -> dict[str, object]:
        return {
            "name": self.name,
            "data_ptr": int(self.data_ptr),
            "dtype": self.dtype,
            "shape": self.shape,
            "strides": self.strides,
            "device": self.device,
            "access_mode": self.access_mode,
            "source_protocol": self.source_protocol,
            "producer_stream_handle": int(self.producer_stream_handle),
        }


@dataclass(frozen=True)
class V4FixedRadiusCountThreshold2DPlan:
    route_id: str
    backend: str
    query_count: int
    search_count: int
    device: str
    caller_stream_handle: int
    prepare_stream_handle: int
    search_columns: dict[str, V4DeviceColumnDescriptor]
    query_columns: dict[str, V4DeviceColumnDescriptor]
    output_columns: dict[str, V4DeviceColumnDescriptor] | None = None

    def to_metadata(self) -> dict[str, object]:
        descriptors = {f"search.{k}": v.to_metadata() for k, v in self.search_columns.items()}
        descriptors.update({f"query.{k}": v.to_metadata() for k, v in self.query_columns.items()})
        if self.output_columns is not None:
            descriptors.update({f"output.{k}": v.to_metadata() for k, v in self.output_columns.items()})
        source_protocols = tuple(sorted({d["source_protocol"] for d in descriptors.values()}))
        return {
            "scope": V4_0_PRODUCT_SCOPE,
            "route_id": self.route_id,
            "backend": self.backend,
            "query": "fixed_radius_count_threshold_2d",
            "dimension": 2,
            "query_count": int(self.query_count),
            "search_count": int(self.search_count),
            "device": self.device,
            "caller_stream_handle": int(self.caller_stream_handle),
            "prepare_stream_handle": int(self.prepare_stream_handle),
            "caller_stream_native_propagation_ready": True,
            "native_prepare_stream_propagation_ready": True,
            "caller_stream_status": V4_0_M1_CALLER_STREAM_STATUS,
            "cross_stream_event_wait_ready": True,
            "cross_stream_prepare_query_policy": (
                "fixed_radius_m1_prepare_ready_event_wait_when_prepare_and_query_streams_differ"
            ),
            "cross_stream_event_wait_scope": "fixed_radius_m1_prepare_query_only",
            "prepare_query_streams_differ": bool(
                self.caller_stream_handle
                and self.prepare_stream_handle
                and self.caller_stream_handle != self.prepare_stream_handle
            ),
            "native_prepare_ready_event_wait_required": bool(
                self.caller_stream_handle and self.caller_stream_handle != self.prepare_stream_handle
            ),
            "input_contract": "caller_owned_cuda_point_columns",
            "output_contract": (
                "caller_owned_cuda_output_columns"
                if self.output_columns is not None
                else "partner_allocated_cuda_output_columns"
            ),
            "materializes_neighbor_rows": False,
            "source_protocols": source_protocols,
            "borrowed_device_pointers": {name: int(meta["data_ptr"]) for name, meta in descriptors.items()},
            "descriptors": descriptors,
        }


def describe_v4_fixed_radius_count_threshold_2d_route() -> dict[str, object]:
    """Return the frozen first V4.0 product route and its current gates."""
    return {
        "scope": V4_0_PRODUCT_SCOPE,
        "status": V4_0_M1_OPERATOR_STATUS,
        "route_id": V4_0_M1_ROUTE_ID,
        "backend": V4_0_M1_NATIVE_BACKEND,
        "primitive": "point2d",
        "query": "fixed_radius_count_threshold",
        "input_columns": _POINT_COLUMNS,
        "output_columns": _OUTPUT_COLUMNS,
        "output_shape": "fixed one row per query, no variable neighbor rows",
        "supported_input_protocols": V4_0_M1_SUPPORTED_INPUT_PROTOCOLS,
        "evidence_backed_frameworks": V4_0_M1_EVIDENCE_BACKED_FRAMEWORKS,
        "experimental_input_protocols": V4_0_M1_EXPERIMENTAL_INPUT_PROTOCOLS,
        "target_input_protocols": V4_0_M1_TARGET_INPUT_PROTOCOLS,
        "target_frameworks": V4_0_M1_TARGET_FRAMEWORKS,
        "blocked_input_protocols_without_full_route_evidence": (
            V4_0_M1_BLOCKED_INPUT_PROTOCOLS_WITHOUT_FULL_ROUTE_EVIDENCE
        ),
        "blocked_frameworks_without_route_evidence": V4_0_M1_BLOCKED_FRAMEWORKS_WITHOUT_ROUTE_EVIDENCE,
        "requires_cuda_device_arrays": True,
        "requires_borrowed_device_pointers": True,
        "requires_caller_owned_outputs_for_exact_zero_copy_claim": True,
        "native_stream_propagation_ready": True,
        "native_prepare_stream_propagation_ready": True,
        "caller_stream_status": V4_0_M1_CALLER_STREAM_STATUS,
        "cross_stream_event_wait_ready": True,
        "cross_stream_status": V4_0_M1_CROSS_STREAM_STATUS,
        "cross_stream_prepare_query_policy": (
            "fixed_radius_m1_prepare_ready_event_wait_when_prepare_and_query_streams_differ"
        ),
        "cross_stream_event_wait_scope": "fixed_radius_m1_prepare_query_only",
        "native_async_ready": False,
        "public_speedup_claim_authorized": False,
        "v4_true_zero_copy_claim_authorized": False,
        "blocked_generalizations": (
            "variable_length_neighbor_rows",
            "all_fixed_radius_routes",
            "ray_triangle_any_hit",
            "non_python_hosts",
            "stable_sdk",
            "full_pytorch_partner_surface",
            "dlpack_route_support",
            "general_cross_stream_event_wait",
            "full_external_stream_ownership",
        ),
    }


def _dtype_token(dtype: object) -> str:
    token = str(dtype).lower()
    if "." in token:
        token = token.rsplit(".", 1)[-1]
    return token


def _dtype_itemsize(dtype_token: str) -> int:
    if dtype_token in {"uint32", "int32", "float32", "float"}:
        return 4
    if dtype_token in {"uint64", "int64", "float64", "double"}:
        return 8
    raise ValueError(f"unsupported dtype for V4 column stride validation: {dtype_token!r}")


def _is_contiguous_column(strides: tuple[int, ...] | None, *, itemsize: int) -> bool:
    return strides in (None, (1,), (itemsize,))


def _producer_stream_handle(obj: Any) -> int:
    cuda_array = getattr(obj, "__cuda_array_interface__", None)
    if not isinstance(cuda_array, dict):
        return 0
    stream = cuda_array.get("stream", 0)
    if stream in (None, 0):
        return 0
    if hasattr(stream, "value"):
        stream = stream.value
    return int(stream)


def _caller_stream_handle(stream: Any) -> int:
    if stream is None:
        return 0
    value = getattr(stream, "ptr", None)
    if value is None:
        value = getattr(stream, "cuda_stream", None)
    if value is None:
        value = getattr(stream, "handle", None)
    if value is None:
        value = stream
    if hasattr(value, "value"):
        value = value.value
    return int(value)


def _require_supported_caller_stream(stream: Any) -> int:
    return _caller_stream_handle(stream)


def _prepare_ready_event_wait_required(caller_stream: int, prepare_stream: int) -> bool:
    return bool(caller_stream and caller_stream != prepare_stream)


def _uses_v4_dlpack_capsule_path(obj: Any) -> bool:
    return _partner._uses_dlpack_capsule_only_path(obj)


def _extract_descriptor(
    name: str,
    obj: Any,
    *,
    access: str,
    dlpack_stream: int | None = None,
) -> V4DeviceColumnDescriptor:
    if _uses_v4_dlpack_capsule_path(obj):
        handoff = _partner.prepare_dlpack_device_pointer_handoff(
            obj,
            access=access,
            stream=dlpack_stream,
        )
    else:
        handoff = _partner.prepare_direct_device_pointer_handoff(obj, access=access)
    return V4DeviceColumnDescriptor(
        name=name,
        data_ptr=int(handoff.data_ptr),
        dtype=_dtype_token(handoff.dtype),
        shape=tuple(int(dim) for dim in handoff.shape),
        strides=None if handoff.strides is None else tuple(int(stride) for stride in handoff.strides),
        device_type=handoff.device_type,
        device_id=int(handoff.device_id),
        access_mode=handoff.access_mode,
        source_protocol=handoff.source_protocol,
        producer_stream_handle=_producer_stream_handle(obj),
        owner=getattr(getattr(handoff, "descriptor", None), "owner", obj),
    )


def _require_columns(
    columns: Mapping[str, Any],
    required: tuple[str, ...],
    *,
    label: str,
) -> None:
    missing = [name for name in required if name not in columns]
    unexpected = [name for name in columns if name not in required]
    if missing:
        raise ValueError(f"missing V4 {label} columns: {', '.join(missing)}")
    if unexpected:
        raise ValueError(f"unexpected V4 {label} columns: {', '.join(unexpected)}")


def _validate_column_group(
    columns: Mapping[str, Any],
    required: tuple[str, ...],
    dtypes: Mapping[str, set[str]],
    *,
    label: str,
    access: str,
    expected_count: int | None = None,
    expected_device: str | None = None,
    dlpack_stream: int | None = None,
) -> dict[str, V4DeviceColumnDescriptor]:
    _require_columns(columns, required, label=label)
    descriptors: dict[str, V4DeviceColumnDescriptor] = {}
    group_count = expected_count
    group_device = expected_device
    for name in required:
        descriptor = _extract_descriptor(
            f"{label}.{name}",
            columns[name],
            access=access,
            dlpack_stream=dlpack_stream,
        )
        allowed = dtypes[name]
        if descriptor.dtype not in allowed:
            allowed_text = ", ".join(sorted(allowed))
            raise ValueError(f"V4 {label} column {name!r} must use dtype {allowed_text}")
        if len(descriptor.shape) != 1:
            raise ValueError(f"V4 {label} column {name!r} must be one-dimensional")
        if not _is_contiguous_column(
            descriptor.strides,
            itemsize=_dtype_itemsize(descriptor.dtype),
        ):
            raise ValueError(f"V4 {label} column {name!r} must be contiguous")
        count = int(descriptor.shape[0])
        if group_count is None:
            group_count = count
        elif count != group_count:
            raise ValueError(f"V4 {label} columns must have matching lengths")
        if group_device is None:
            group_device = descriptor.device
        elif descriptor.device != group_device:
            raise ValueError(f"V4 {label} columns must live on the same CUDA device")
        descriptors[name] = descriptor
    return descriptors


def plan_v4_fixed_radius_count_threshold_2d(
    query_point_columns: Mapping[str, Any],
    search_point_columns: Mapping[str, Any],
    *,
    output_columns: Mapping[str, Any] | None = None,
    stream: Any = None,
    prepare_stream: Any = None,
) -> V4FixedRadiusCountThreshold2DPlan:
    """Validate the frozen V4.0 M1 device-column route without executing it."""
    caller_stream = _require_supported_caller_stream(stream)
    prepare_stream_handle = (
        _require_supported_caller_stream(prepare_stream)
        if prepare_stream is not None
        else caller_stream
    )
    search_descriptors = _validate_column_group(
        search_point_columns,
        _POINT_COLUMNS,
        _POINT_DTYPES,
        label="search",
        access="read",
        dlpack_stream=prepare_stream_handle,
    )
    search_count = int(search_descriptors["ids"].shape[0])
    device = search_descriptors["ids"].device
    query_descriptors = _validate_column_group(
        query_point_columns,
        _POINT_COLUMNS,
        _POINT_DTYPES,
        label="query",
        access="read",
        expected_device=device,
        dlpack_stream=caller_stream,
    )
    query_count = int(query_descriptors["ids"].shape[0])
    output_descriptors = None
    if output_columns is not None:
        output_descriptors = _validate_column_group(
            output_columns,
            _OUTPUT_COLUMNS,
            _OUTPUT_DTYPES,
            label="output",
            access="write",
            expected_count=query_count,
            expected_device=device,
            dlpack_stream=caller_stream,
        )
    return V4FixedRadiusCountThreshold2DPlan(
        route_id=V4_0_M1_ROUTE_ID,
        backend=V4_0_M1_NATIVE_BACKEND,
        query_count=query_count,
        search_count=search_count,
        device=device,
        caller_stream_handle=caller_stream,
        prepare_stream_handle=prepare_stream_handle,
        search_columns=search_descriptors,
        query_columns=query_descriptors,
        output_columns=output_descriptors,
    )


class V4FixedRadiusCountThreshold2D:
    """Frozen first V4 Python device-array operator route."""

    def __init__(
        self,
        search_point_columns: Mapping[str, Any],
        *,
        max_radius: float,
        partner: str = "cupy",
        stream: Any = None,
    ) -> None:
        max_radius = float(max_radius)
        if max_radius < 0:
            raise ValueError("max_radius must be non-negative")
        self.prepare_stream_handle = _require_supported_caller_stream(stream)
        self.search_point_columns = dict(search_point_columns)
        self.partner = str(partner)
        self.max_radius = max_radius
        self.route = describe_v4_fixed_radius_count_threshold_2d_route()
        search_descriptors = _validate_column_group(
            self.search_point_columns,
            _POINT_COLUMNS,
            _POINT_DTYPES,
            label="search",
            access="read",
            dlpack_stream=self.prepare_stream_handle,
        )
        self.search_count = int(search_descriptors["ids"].shape[0])
        self.device = search_descriptors["ids"].device
        self.search_descriptors = search_descriptors
        if self.prepare_stream_handle:
            self._prepared = _prepare_scene_on_stream(
                self.search_point_columns,
                max_radius=max_radius,
                cuda_stream_ptr=self.prepare_stream_handle,
            )
        else:
            self._prepared = _prepare_scene(
                self.search_point_columns,
                max_radius=max_radius,
                partner=self.partner,
            )
        self._closed = False

    def run(
        self,
        query_point_columns: Mapping[str, Any],
        *,
        radius: float,
        threshold: int = 1,
        output_columns: Mapping[str, Any] | None = None,
        stream: Any = None,
        return_metadata: bool = False,
    ):
        if self._closed:
            raise RuntimeError("V4 fixed-radius operator is closed")
        radius = float(radius)
        threshold = int(threshold)
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if radius > self.max_radius:
            raise ValueError("radius must be less than or equal to prepared max_radius")
        if threshold < 0:
            raise ValueError("threshold must be non-negative")

        if output_columns is None:
            query_descriptors = _validate_column_group(
                query_point_columns,
                _POINT_COLUMNS,
                _POINT_DTYPES,
                label="query",
                access="read",
                expected_device=self.device,
                dlpack_stream=_caller_stream_handle(stream),
            )
            output_columns = _allocate_outputs(
                int(query_descriptors["ids"].shape[0]),
                partner=self.partner,
            )

        plan = plan_v4_fixed_radius_count_threshold_2d(
            query_point_columns,
            self.search_point_columns,
            output_columns=output_columns,
            stream=stream,
            prepare_stream=self.prepare_stream_handle,
        )
        if plan.caller_stream_handle:
            on_stream = getattr(self._prepared, "write_device_count_threshold_columns_on_stream", None)
            if not callable(on_stream):
                raise RuntimeError(
                    "prepared OptiX fixed-radius handle does not expose the V4 caller-stream route; "
                    "rebuild the OptiX runtime from current main"
                )
            native_metadata_result = on_stream(
                dict(query_point_columns),
                radius=radius,
                threshold=threshold,
                query_ids_out=output_columns["query_ids"],
                neighbor_counts_out=output_columns["neighbor_counts"],
                threshold_flags_out=output_columns["threshold_flags"],
                cuda_stream_ptr=plan.caller_stream_handle,
            )
            native_result = {
                "columns": dict(output_columns),
                "metadata": {
                    "adapter": "v4_fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns_on_stream",
                    "partner": self.partner,
                    "native_metadata": native_metadata_result["metadata"],
                    "true_zero_copy_authorized": bool(
                        native_metadata_result["metadata"].get("true_zero_copy_authorized", False)
                    ),
                },
            }
        else:
            native_result = _run_prepared(
                self._prepared,
                dict(query_point_columns),
                radius=radius,
                threshold=threshold,
                partner=self.partner,
                output_columns=dict(output_columns),
                return_metadata=True,
            )
        metadata = dict(native_result["metadata"])
        native_metadata = dict(metadata.get("native_metadata", {}))
        metadata.update(
            {
                "scope": V4_0_PRODUCT_SCOPE,
                "v4_route_id": V4_0_M1_ROUTE_ID,
                "v4_operator_status": V4_0_M1_OPERATOR_STATUS,
                "v4_backend": V4_0_M1_NATIVE_BACKEND,
                "v4_plan": plan.to_metadata(),
                "caller_stream_handle": int(plan.caller_stream_handle),
                "prepare_stream_handle": int(self.prepare_stream_handle),
                "caller_stream_native_propagation_ready": True,
                "native_prepare_stream_propagation_ready": True,
                "caller_stream_status": V4_0_M1_CALLER_STREAM_STATUS,
                "cross_stream_event_wait_ready": True,
                "cross_stream_status": V4_0_M1_CROSS_STREAM_STATUS,
                "cross_stream_event_wait_scope": "fixed_radius_m1_prepare_query_only",
                "prepare_query_streams_differ": bool(
                    plan.caller_stream_handle
                    and plan.prepare_stream_handle
                    and plan.caller_stream_handle != plan.prepare_stream_handle
                ),
                "native_prepare_ready_event_wait_required": _prepare_ready_event_wait_required(
                    plan.caller_stream_handle,
                    plan.prepare_stream_handle,
                ),
                "native_prepare_ready_event_wait_ready": bool(
                    native_metadata.get("native_prepare_ready_event_wait_ready", True)
                ),
                "native_prepare_ready_event_wait_used": bool(
                    native_metadata.get("native_prepare_ready_event_wait_used", False)
                ),
                "native_prepare_ready_event_recorded": bool(
                    native_metadata.get("native_prepare_ready_event_recorded", False)
                ),
                "native_synchronized_before_return": bool(
                    native_metadata.get("native_synchronized_before_return", plan.caller_stream_handle == 0)
                ),
                "native_async_ready": bool(native_metadata.get("native_async_ready", False)),
                "native_true_zero_copy_authorized": bool(
                    native_metadata.get("true_zero_copy_authorized", metadata.get("true_zero_copy_authorized", False))
                ),
                "named_cuda_columns_no_host_stage_authorized": bool(
                    native_metadata.get("named_cuda_columns_no_host_stage_authorized", False)
                ),
                "named_cuda_columns_no_host_stage_ready": bool(
                    native_metadata.get("named_cuda_columns_no_host_stage_ready", False)
                ),
                "native_call_device_pointer_echo": dict(native_metadata.get("native_call_device_pointer_echo", {})),
                "native_call_device_pointer_echo_complete": bool(
                    native_metadata.get("native_call_device_pointer_echo_complete", False)
                ),
                "v4_true_zero_copy_claim_authorized": False,
                "v4_true_zero_copy_claim_blocker": (
                    "public_true_zero_copy_wording_blocked_by_internal_device_staging_and_sync_contract"
                ),
                "internal_device_staging_disclosed": True,
                "internal_device_staging_scope": "device-resident AABB/BVH staging may occur inside the native route",
                "public_speedup_claim_authorized": False,
                "materializes_neighbor_rows": False,
            }
        )
        result = {"columns": native_result["columns"], "metadata": metadata}
        if return_metadata:
            return result
        return result["columns"]

    def close(self) -> None:
        if self._closed:
            return
        close = getattr(self._prepared, "close", None)
        if callable(close):
            close()
        self._closed = True

    def __enter__(self) -> "V4FixedRadiusCountThreshold2D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def prepare_v4_fixed_radius_count_threshold_2d(
    search_point_columns: Mapping[str, Any],
    *,
    max_radius: float,
    partner: str = "cupy",
    stream: Any = None,
) -> V4FixedRadiusCountThreshold2D:
    return V4FixedRadiusCountThreshold2D(
        search_point_columns,
        max_radius=max_radius,
        partner=partner,
        stream=stream,
    )


def run_v4_fixed_radius_count_threshold_2d(
    query_point_columns: Mapping[str, Any],
    search_point_columns: Mapping[str, Any],
    *,
    radius: float,
    threshold: int = 1,
    partner: str = "cupy",
    output_columns: Mapping[str, Any] | None = None,
    stream: Any = None,
    return_metadata: bool = False,
):
    with prepare_v4_fixed_radius_count_threshold_2d(
        search_point_columns,
        max_radius=radius,
        partner=partner,
        stream=stream,
    ) as operator:
        return operator.run(
            query_point_columns,
            radius=radius,
            threshold=threshold,
            output_columns=output_columns,
            stream=stream,
            return_metadata=return_metadata,
        )

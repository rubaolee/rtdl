from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
import math
import secrets
import time
from types import MappingProxyType
from typing import Any, Iterator, Mapping, NoReturn, Sequence

from .action_interpreter import ReductionRelation
from .action_numba_continuation import (
    ActionPlacementError,
    PreparedGroupedI64x2DeviceWorkspace,
    compile_numba_grouped_i64x2_count_sum,
    validate_numba_grouped_i64x2_order_indexed_binding_shape,
)


try:  # pragma: no cover - availability depends on the runtime image.
    from numba import njit  # type: ignore

    _NUMBA_HOST_SCAN_AVAILABLE = True
except Exception:  # pragma: no cover
    njit = None
    _NUMBA_HOST_SCAN_AVAILABLE = False


if _NUMBA_HOST_SCAN_AVAILABLE:

    @njit(cache=True)
    def _aggregate_sorted_i64x2_numba(
        key0,
        key1,
        values,
        out0,
        out1,
        out_counts,
        out_sums,
        require_nonnegative,
    ):
        """Single-pass checked scan equivalent to the established host reducer."""

        count = key0.shape[0]
        if count == 0:
            return 0, 0
        maximum = (1 << 63) - 1
        minimum = -(1 << 63)
        output_count = 0
        current0 = key0[0]
        current1 = key1[0]
        current_count = 0
        current_sum = 0
        for index in range(count):
            value0 = key0[index]
            value1 = key1[index]
            if value0 < current0 or (value0 == current0 and value1 < current1):
                return 0, 1
            if value0 != current0 or value1 != current1:
                out0[output_count] = current0
                out1[output_count] = current1
                out_counts[output_count] = current_count
                out_sums[output_count] = current_sum
                output_count += 1
                current0 = value0
                current1 = value1
                current_count = 0
                current_sum = 0
            scalar = values[index]
            if require_nonnegative and scalar < 0:
                return 0, 3
            if (scalar > 0 and current_sum > maximum - scalar) or (
                scalar < 0 and current_sum < minimum - scalar
            ):
                return 0, 2
            current_count += 1
            current_sum += scalar
        out0[output_count] = current0
        out1[output_count] = current1
        out_counts[output_count] = current_count
        out_sums[output_count] = current_sum
        return output_count + 1, 0

    @njit(cache=True)
    def _aggregate_order_indexed_i64x2_numba(
        key0,
        key1,
        values,
        order,
        out0,
        out1,
        out_counts,
        out_sums,
        require_nonnegative,
    ):
        """Checked grouped scan through a compiler-created lexicographic order."""

        count = order.shape[0]
        if count == 0:
            return 0, 0
        maximum = (1 << 63) - 1
        minimum = -(1 << 63)
        first = order[0]
        if first < 0 or first >= key0.shape[0]:
            return 0, 4
        output_count = 0
        current0 = key0[first]
        current1 = key1[first]
        current_count = 0
        current_sum = 0
        for position in range(count):
            index = order[position]
            if index < 0 or index >= key0.shape[0]:
                return 0, 4
            value0 = key0[index]
            value1 = key1[index]
            if value0 < current0 or (value0 == current0 and value1 < current1):
                return 0, 1
            if value0 != current0 or value1 != current1:
                out0[output_count] = current0
                out1[output_count] = current1
                out_counts[output_count] = current_count
                out_sums[output_count] = current_sum
                output_count += 1
                current0 = value0
                current1 = value1
                current_count = 0
                current_sum = 0
            scalar = values[index]
            if require_nonnegative and scalar < 0:
                return 0, 3
            if (scalar > 0 and current_sum > maximum - scalar) or (
                scalar < 0 and current_sum < minimum - scalar
            ):
                return 0, 2
            current_count += 1
            current_sum += scalar
        out0[output_count] = current0
        out1[output_count] = current1
        out_counts[output_count] = current_count
        out_sums[output_count] = current_sum
        return output_count + 1, 0


ACTION_HOST_CONTINUATION_VERSION = "rtdl.action_host_continuation.private_candidate.v1"
_HOST_GROUPED_PREPARED_RESOURCE_SECRET = secrets.token_bytes(32)
_PRODUCER_OWNED_DEVICE_BATCH_SECRET = secrets.token_bytes(32)


@dataclass(frozen=True)
class HostGroupedI64x2CountSumProgram:
    """Closed host lowering for the same grouped COUNT+signed-SUM Action shape."""

    spec: object
    event_fields: tuple[str, ...]
    key_fields: tuple[str, str]
    sum_field: str
    count_reduction_name: str
    sum_reduction_name: str
    delivery_proof_reference: str
    parameter_fields: tuple[str, ...] = ()
    placement_contract: str = "verified_action_ir_sorted_host_i64x2_count_sum_v1"

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract_version": ACTION_HOST_CONTINUATION_VERSION,
            "semantic_digest": self.spec.semantic_digest,
            "event_fields": list(self.event_fields),
            "key_fields": list(self.key_fields),
            "sum_field": self.sum_field,
            "count_reduction_name": self.count_reduction_name,
            "sum_reduction_name": self.sum_reduction_name,
            "parameter_fields": list(self.parameter_fields),
            "placement_contract": self.placement_contract,
            "delivery_proof_reference": self.delivery_proof_reference,
            "delivery_proof_discharged_by_placement": True,
            "action_name_used_for_dispatch": False,
            "application_selected_backend": False,
            "user_host_callback_accepted": False,
            "supported_effect_subset": ["keyed_reduce"],
            "key_schema": ["i64", "i64"],
            "reduction_schema": ["count_u64", "sum_i64"],
            "source_order_contract": "arbitrary_typed_i64_columns",
            "physical_input_order": "compiler_owned_lexicographic_i64x2_then_logical_key",
            "semantic_output_projection": "canonical_key_order",
            "signed_overflow_policy": "fail_closed",
            "unsupported_effects_fail_closed": True,
        }


@dataclass(frozen=True)
class HostGroupedI64x2MaterializedBatch:
    columns: Mapping[str, object]
    row_count: int
    source_residency: str
    device_to_host_copy_used: bool
    compiler_generated_logical_key: bool
    ordering_fields: tuple[str, ...]
    content_digest: str | None
    binding_kind: str
    sum_field_nonnegative_validation_deferred_to_checked_scan: bool
    phase_timing_seconds: Mapping[str, float]

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": "rtdl.host_grouped_i64x2_materialized_batch.private_candidate.v1",
            "row_count": self.row_count,
            "source_residency": self.source_residency,
            "device_to_host_copy_used": self.device_to_host_copy_used,
            "compiler_generated_logical_key": self.compiler_generated_logical_key,
            "ordering_fields": list(self.ordering_fields),
            "content_digest": self.content_digest,
            "binding_kind": self.binding_kind,
            "sum_field_nonnegative_validation_deferred_to_checked_scan": (
                self.sum_field_nonnegative_validation_deferred_to_checked_scan
            ),
            "phase_timing_seconds": dict(self.phase_timing_seconds),
            "full_typed_payload_and_order_bound": True,
            "host_payload_content_rehashed_for_persistent_identity": (
                self.content_digest is not None
            ),
            "duplicate_logical_keys_rejected": True,
            "caller_owned_device_columns_retained": False,
            "download_result_reowned_by_compiler": True,
            "python_event_rows_materialized": False,
        }


def _device_array_identity(array: object) -> dict[str, object]:
    interface = getattr(array, "__cuda_array_interface__", None)
    if not isinstance(interface, Mapping):
        _fail(
            "cuda_array_interface_required",
            "producer_owned_batch.storage",
            type(array).__name__,
        )
    data = interface.get("data")
    shape = interface.get("shape")
    typestr = interface.get("typestr")
    if (
        not isinstance(data, tuple)
        or len(data) < 1
        or not isinstance(data[0], int)
        or not isinstance(shape, tuple)
        or len(shape) != 1
        or not isinstance(typestr, str)
    ):
        _fail(
            "cuda_array_interface_invalid",
            "producer_owned_batch.storage",
            repr(interface),
        )
    return {
        "object_id": id(array),
        "device_pointer": int(data[0]),
        "shape": [int(value) for value in shape],
        "strides": (
            None
            if interface.get("strides") is None
            else [int(value) for value in interface["strides"]]
        ),
        "typestr": typestr,
        "readonly": bool(data[1]) if len(data) > 1 else False,
    }


class CompilerOwnedUnorderedI64x2DeviceBatch:
    """One closed producer-write lease followed by one synchronous consumption.

    The prepared compiler owner allocates every device column before the
    producer runs.  The producer can write only during the ``writable`` state;
    completion synchronizes and seals counts/capacity before a single prepared
    host or device query may consume the batch.  Completion always detaches
    the consumer-visible snapshot from producer-retained write references.
    """

    __slots__ = (
        "_batch_ordinal",
        "_capacity",
        "_completed_group_count",
        "_completed_group_length_device",
        "_completed_group_length_host",
        "_completed_label_a_device",
        "_completed_label_a_host",
        "_completed_label_b_device",
        "_completed_label_b_host",
        "_completed_point_row_count",
        "_completed_skipped_group_count",
        "_completion_device_to_device_seconds",
        "_completion_device_to_host_seconds",
        "_completion_residency",
        "_counters_device",
        "_group_length_device",
        "_label_a_device",
        "_label_b_device",
        "_overflow_device",
        "_owner_identity_digest",
        "_producer_workspace_allocation_seconds",
        "_private_workspace",
        "_private_workspace_metadata",
        "_workspace_generation_digest",
        "_seal",
        "_state",
        "_storage_identity_digest",
    )

    def __init__(
        self,
        *,
        owner_identity_digest: str,
        batch_ordinal: int,
        capacity: int,
        group_length_device: object,
        label_a_device: object,
        label_b_device: object,
        counters_device: object,
        overflow_device: object,
        completion_residency: str = "host",
        producer_workspace_allocation_seconds: float = 0.0,
        private_workspace: PreparedGroupedI64x2DeviceWorkspace | None = None,
    ) -> None:
        if (
            not isinstance(owner_identity_digest, str)
            or len(owner_identity_digest) != 64
            or not isinstance(batch_ordinal, int)
            or isinstance(batch_ordinal, bool)
            or batch_ordinal < 0
            or not isinstance(capacity, int)
            or isinstance(capacity, bool)
            or capacity < 0
            or completion_residency not in {"host", "device"}
            or not isinstance(producer_workspace_allocation_seconds, (int, float))
            or isinstance(producer_workspace_allocation_seconds, bool)
            or not math.isfinite(float(producer_workspace_allocation_seconds))
            or float(producer_workspace_allocation_seconds) < 0.0
        ):
            _fail(
                "producer_owned_identity_invalid",
                "producer_owned_batch",
                "owner digest, ordinal, or capacity is invalid",
            )
        self._owner_identity_digest = owner_identity_digest
        self._batch_ordinal = batch_ordinal
        self._capacity = capacity
        self._group_length_device = group_length_device
        self._label_a_device = label_a_device
        self._label_b_device = label_b_device
        self._counters_device = counters_device
        self._overflow_device = overflow_device
        self._completion_residency = completion_residency
        self._producer_workspace_allocation_seconds = float(
            producer_workspace_allocation_seconds
        )
        if (
            private_workspace is not None
            and type(private_workspace) is not PreparedGroupedI64x2DeviceWorkspace
        ):
            _fail(
                "producer_owned_private_workspace_invalid",
                "producer_owned_batch.private_workspace",
                type(private_workspace).__name__,
            )
        self._private_workspace = private_workspace
        self._private_workspace_metadata: dict[str, object] | None = None
        self._workspace_generation_digest: str | None = None
        identities = {
            "group_length": _device_array_identity(group_length_device),
            "label_a": _device_array_identity(label_a_device),
            "label_b": _device_array_identity(label_b_device),
            "counters": _device_array_identity(counters_device),
            "overflow": _device_array_identity(overflow_device),
        }
        self._storage_identity_digest = hashlib.sha256(
            json.dumps(
                identities,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        self._completed_group_count: int | None = None
        self._completed_group_length_device = None
        self._completed_group_length_host = None
        self._completed_label_a_device = None
        self._completed_label_a_host = None
        self._completed_label_b_device = None
        self._completed_label_b_host = None
        self._completed_point_row_count: int | None = None
        self._completed_skipped_group_count: int | None = None
        self._completion_device_to_device_seconds: float | None = None
        self._completion_device_to_host_seconds: float | None = None
        self._state = "writable"
        self._seal = self._issue_seal()

    def _seal_payload(self) -> bytes:
        completed_host_columns = (
            None
            if self._completed_group_length_host is None
            or self._completed_label_a_host is None
            or self._completed_label_b_host is None
            else {
                name: {
                    "object_id": id(array),
                    "shape": [int(value) for value in array.shape],
                    "dtype": str(array.dtype),
                    "writeable": bool(array.flags.writeable),
                }
                for name, array in (
                    ("group_length", self._completed_group_length_host),
                    ("label_a", self._completed_label_a_host),
                    ("label_b", self._completed_label_b_host),
                )
            }
        )
        completed_device_columns = (
            None
            if self._completed_group_length_device is None
            or self._completed_label_a_device is None
            or self._completed_label_b_device is None
            else {
                name: _device_array_identity(array)
                for name, array in (
                    ("group_length", self._completed_group_length_device),
                    ("label_a", self._completed_label_a_device),
                    ("label_b", self._completed_label_b_device),
                )
            }
        )
        payload = {
            "contract": "rtdl.compiler_owned_unordered_i64x2_device_batch.v1",
            "owner_identity_digest": self._owner_identity_digest,
            "batch_ordinal": self._batch_ordinal,
            "capacity": self._capacity,
            "completion_residency": self._completion_residency,
            "producer_workspace_allocation_seconds": (
                self._producer_workspace_allocation_seconds
            ),
            "private_workspace_metadata": self._private_workspace_metadata,
            "workspace_generation_digest": self._workspace_generation_digest,
            "private_workspace_attached": self._private_workspace is not None,
            "storage_identity_digest": self._storage_identity_digest,
            "completed_group_count": self._completed_group_count,
            "completed_device_columns": completed_device_columns,
            "completed_host_columns": completed_host_columns,
            "completed_point_row_count": self._completed_point_row_count,
            "completed_skipped_group_count": self._completed_skipped_group_count,
            "completion_device_to_device_seconds": self._completion_device_to_device_seconds,
            "completion_device_to_host_seconds": self._completion_device_to_host_seconds,
            "state": self._state,
        }
        return json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    def _issue_seal(self) -> str:
        return hmac.new(
            _PRODUCER_OWNED_DEVICE_BATCH_SECRET,
            self._seal_payload(),
            hashlib.sha256,
        ).hexdigest()

    def _validate_integrity(self) -> None:
        completed_host_columns = (
            self._completed_group_length_host,
            self._completed_label_a_host,
            self._completed_label_b_host,
        )
        completed_device_columns = (
            self._completed_group_length_device,
            self._completed_label_a_device,
            self._completed_label_b_device,
        )
        no_completed_snapshot = (
            all(column is None for column in completed_host_columns)
            and all(column is None for column in completed_device_columns)
            and self._completed_group_count is None
            and self._completion_device_to_host_seconds is None
            and self._completion_device_to_device_seconds is None
        )
        cleared_consumed_snapshot = (
            self._state == "consumed"
            and all(column is None for column in completed_host_columns)
            and all(column is None for column in completed_device_columns)
            and isinstance(self._completed_group_count, int)
            and self._completed_group_count >= 0
            and (
                (
                    self._completion_residency == "host"
                    and isinstance(
                        self._completion_device_to_host_seconds,
                        float,
                    )
                    and self._completion_device_to_host_seconds >= 0.0
                    and self._completion_device_to_device_seconds is None
                )
                or (
                    self._completion_residency == "device"
                    and isinstance(
                        self._completion_device_to_device_seconds,
                        float,
                    )
                    and self._completion_device_to_device_seconds >= 0.0
                    and self._completion_device_to_host_seconds is None
                )
            )
        )
        completed_host_columns_valid = (
            no_completed_snapshot
            if self._state in {"writable", "invalidated"}
            else cleared_consumed_snapshot
            if self._state == "consumed"
            else (
                self._completion_residency == "host"
                and isinstance(self._completed_group_count, int)
                and self._completed_group_count >= 0
                and all(column is None for column in completed_device_columns)
                and all(
                    getattr(column, "ndim", None) == 1
                    and str(getattr(column, "dtype", "")) == "int64"
                    and int(column.shape[0]) == self._completed_group_count
                    and not bool(column.flags.writeable)
                    for column in completed_host_columns
                )
                and isinstance(self._completion_device_to_host_seconds, float)
                and math.isfinite(self._completion_device_to_host_seconds)
                and self._completion_device_to_host_seconds >= 0.0
                and self._completion_device_to_device_seconds is None
            )
        )
        completed_device_columns_valid = (
            no_completed_snapshot
            if self._state in {"writable", "invalidated"}
            else cleared_consumed_snapshot
            if self._state == "consumed"
            else (
                self._completion_residency == "device"
                and isinstance(self._completed_group_count, int)
                and self._completed_group_count >= 0
                and all(column is None for column in completed_host_columns)
                and all(
                    _device_array_identity(column)["shape"]
                    == [self._completed_group_count]
                    and _device_array_identity(column)["typestr"]
                    in {"<i8", "|i8", "=i8"}
                    for column in completed_device_columns
                )
                and isinstance(self._completion_device_to_device_seconds, float)
                and math.isfinite(self._completion_device_to_device_seconds)
                and self._completion_device_to_device_seconds >= 0.0
                and self._completion_device_to_host_seconds is None
            )
        )
        if (
            type(self) is not CompilerOwnedUnorderedI64x2DeviceBatch
            or not isinstance(self._seal, str)
            or not hmac.compare_digest(self._seal, self._issue_seal())
            or self._state not in {"writable", "completed", "consumed", "invalidated"}
            or (
                self._completion_residency == "host"
                and not completed_host_columns_valid
            )
            or (
                self._completion_residency == "device"
                and not completed_device_columns_valid
            )
            or any(
                _device_array_identity(array)["shape"][0] < required
                for array, required in (
                    (self._group_length_device, self._capacity),
                    (self._label_a_device, self._capacity),
                    (self._label_b_device, self._capacity),
                    (self._counters_device, 3),
                    (self._overflow_device, 1),
                )
            )
        ):
            _fail(
                "producer_owned_batch_seal_invalid",
                "producer_owned_batch",
                "device storage identity or lifecycle state changed",
            )

    def _refresh_seal(self) -> None:
        self._seal = self._issue_seal()

    def _require_writable(self) -> None:
        self._validate_integrity()
        if self._state != "writable":
            _fail(
                "producer_owned_batch_not_writable",
                "producer_owned_batch.state",
                self._state,
            )

    @property
    def group_length_device(self):
        self._require_writable()
        return self._group_length_device

    @property
    def label_a_device(self):
        self._require_writable()
        return self._label_a_device

    @property
    def label_b_device(self):
        self._require_writable()
        return self._label_b_device

    @property
    def counters_device(self):
        self._require_writable()
        return self._counters_device

    @property
    def overflow_device(self):
        self._require_writable()
        return self._overflow_device

    @property
    def capacity(self) -> int:
        self._validate_integrity()
        return self._capacity

    def complete_production(self) -> dict[str, int]:
        self._require_writable()
        try:
            from numba import cuda  # type: ignore
            import numpy as np

            cuda.synchronize()
            counters = np.asarray(
                self._counters_device.copy_to_host(),
                dtype=np.int64,
            )
            overflow = np.asarray(
                self._overflow_device.copy_to_host(),
                dtype=np.int64,
            )
        except Exception as exc:  # pragma: no cover - hardware/runtime specific.
            self._state = "invalidated"
            self._refresh_seal()
            _fail(
                "producer_owned_batch_completion_failed",
                "producer_owned_batch",
                str(exc),
            )
        if counters.shape != (3,) or overflow.shape != (1,):
            self._state = "invalidated"
            self._refresh_seal()
            _fail(
                "producer_owned_batch_counter_shape_invalid",
                "producer_owned_batch",
                f"counters={counters.shape}; overflow={overflow.shape}",
            )
        group_count = int(counters[0])
        point_row_count = int(counters[1])
        skipped_group_count = int(counters[2])
        if (
            int(overflow[0]) != 0
            or group_count < 0
            or group_count > self._capacity
            or point_row_count < 0
            or skipped_group_count < 0
        ):
            self._state = "invalidated"
            self._refresh_seal()
            _fail(
                "producer_owned_batch_overflow_or_count_invalid",
                "producer_owned_batch",
                (
                    f"capacity={self._capacity}; groups={group_count}; "
                    f"point_rows={point_row_count}; skipped={skipped_group_count}; "
                    f"overflow={int(overflow[0])}"
                ),
            )
        transfer_started = time.perf_counter()
        try:
            import numpy as np

            if self._completion_residency == "host":
                completed_group_length_host = _readonly_compiler_owned_numpy_1d(
                    np.asarray(
                        self._group_length_device[:group_count].copy_to_host(),
                        dtype=np.int64,
                    )
                )
                completed_label_a_host = _readonly_compiler_owned_numpy_1d(
                    np.asarray(
                        self._label_a_device[:group_count].copy_to_host(),
                        dtype=np.int64,
                    )
                )
                completed_label_b_host = _readonly_compiler_owned_numpy_1d(
                    np.asarray(
                        self._label_b_device[:group_count].copy_to_host(),
                        dtype=np.int64,
                    )
                )
                self._completion_device_to_host_seconds = float(
                    time.perf_counter() - transfer_started
                )
                self._completed_group_length_host = completed_group_length_host
                self._completed_label_a_host = completed_label_a_host
                self._completed_label_b_host = completed_label_b_host
            else:
                if self._private_workspace is None:
                    completed_group_length_device = cuda.device_array(
                        group_count, dtype=np.int64
                    )
                    completed_label_a_device = cuda.device_array(
                        group_count, dtype=np.int64
                    )
                    completed_label_b_device = cuda.device_array(
                        group_count, dtype=np.int64
                    )
                    completed_group_length_device.copy_to_device(
                        self._group_length_device[:group_count]
                    )
                    completed_label_a_device.copy_to_device(
                        self._label_a_device[:group_count]
                    )
                    completed_label_b_device.copy_to_device(
                        self._label_b_device[:group_count]
                    )
                    cuda.synchronize()
                    self._completion_device_to_device_seconds = float(
                        time.perf_counter() - transfer_started
                    )
                else:
                    snapshot, workspace_metadata = (
                        self._private_workspace.capture_completion_snapshot(
                            owner_identity_digest=self._owner_identity_digest,
                            query_ordinal=self._batch_ordinal,
                            row_count=group_count,
                            key0_source=self._label_a_device,
                            key1_source=self._label_b_device,
                            value_source=self._group_length_device,
                        )
                    )
                    completed_label_a_device = snapshot["key0"]
                    completed_label_b_device = snapshot["key1"]
                    completed_group_length_device = snapshot["value"]
                    self._private_workspace_metadata = dict(
                        workspace_metadata
                    )
                    self._workspace_generation_digest = str(
                        workspace_metadata["workspace_generation_digest"]
                    )
                    self._completion_device_to_device_seconds = float(
                        workspace_metadata[
                            "completion_device_to_device_seconds"
                        ]
                    )
                self._completed_group_length_device = completed_group_length_device
                self._completed_label_a_device = completed_label_a_device
                self._completed_label_b_device = completed_label_b_device
        except Exception as exc:  # pragma: no cover - hardware/runtime specific.
            private_workspace = self._private_workspace
            if private_workspace is not None:
                private_workspace.abort_query(
                    owner_identity_digest=self._owner_identity_digest,
                    query_ordinal=self._batch_ordinal,
                )
            self._completed_group_length_device = None
            self._completed_label_a_device = None
            self._completed_label_b_device = None
            self._completed_group_length_host = None
            self._completed_label_a_host = None
            self._completed_label_b_host = None
            self._completion_device_to_device_seconds = None
            self._completion_device_to_host_seconds = None
            self._private_workspace = None
            self._state = "invalidated"
            self._refresh_seal()
            _fail(
                "producer_owned_batch_payload_snapshot_failed",
                "producer_owned_batch",
                str(exc),
            )
        self._completed_group_count = group_count
        self._completed_point_row_count = point_row_count
        self._completed_skipped_group_count = skipped_group_count
        self._state = "completed"
        self._refresh_seal()
        return {
            "group_count": group_count,
            "point_row_count": point_row_count,
            "skipped_group_count": skipped_group_count,
        }

    def carrier_view(self) -> dict[str, object]:
        self._validate_integrity()
        if self._state != "completed":
            _fail(
                "producer_owned_batch_not_completed",
                "producer_owned_batch.state",
                self._state,
            )
        return {
            "group_length_device": self._group_length_device,
            "label_a_device": self._label_a_device,
            "label_b_device": self._label_b_device,
            "group_count": int(self._completed_group_count or 0),
            "point_row_count": int(self._completed_point_row_count or 0),
            "skipped_group_count": int(self._completed_skipped_group_count or 0),
            "padded_group_count": self._capacity,
            "_compiler_owned_unordered_i64x2_batch": self,
        }

    def _consume(
        self,
        *,
        owner_identity_digest: str,
        batch_ordinal: int,
    ) -> tuple[dict[str, object], dict[str, object]]:
        self._validate_integrity()
        if (
            self._state != "completed"
            or owner_identity_digest != self._owner_identity_digest
            or batch_ordinal != self._batch_ordinal
        ):
            _fail(
                "producer_owned_batch_owner_or_ordinal_mismatch",
                "producer_owned_batch",
                (
                    f"state={self._state}; expected_ordinal={self._batch_ordinal}; "
                    f"actual_ordinal={batch_ordinal}"
                ),
            )
        row_count = int(self._completed_group_count or 0)
        columns = {
            "label_a": self._completed_label_a_host,
            "label_b": self._completed_label_b_host,
            "group_length": self._completed_group_length_host,
        }
        receipt = self.to_metadata()
        self._completed_group_length_host = None
        self._completed_label_a_host = None
        self._completed_label_b_host = None
        self._state = "consumed"
        self._refresh_seal()
        receipt["state"] = "consumed"
        return columns, receipt

    def _consume_device_snapshot(
        self,
        *,
        owner_identity_digest: str,
        batch_ordinal: int,
    ) -> tuple[dict[str, object], dict[str, object]]:
        """Transfer one sealed private device snapshot to the device reducer."""

        self._validate_integrity()
        if (
            self._completion_residency != "device"
            or self._state != "completed"
            or owner_identity_digest != self._owner_identity_digest
            or batch_ordinal != self._batch_ordinal
        ):
            _fail(
                "producer_owned_batch_owner_or_ordinal_mismatch",
                "producer_owned_batch",
                (
                    f"residency={self._completion_residency}; state={self._state}; "
                    f"expected_ordinal={self._batch_ordinal}; actual_ordinal={batch_ordinal}"
                ),
            )
        columns = {
            "label_a": self._completed_label_a_device,
            "label_b": self._completed_label_b_device,
            "group_length": self._completed_group_length_device,
        }
        receipt = self.to_metadata()
        self._completed_group_length_device = None
        self._completed_label_a_device = None
        self._completed_label_b_device = None
        self._private_workspace = None
        self._state = "consumed"
        self._refresh_seal()
        receipt["state"] = "consumed"
        return columns, receipt

    def invalidate(self) -> None:
        self._validate_integrity()
        if self._state != "consumed":
            private_workspace = self._private_workspace
            if private_workspace is not None:
                private_workspace.abort_query(
                    owner_identity_digest=self._owner_identity_digest,
                    query_ordinal=self._batch_ordinal,
                )
            self._completed_group_length_device = None
            self._completed_label_a_device = None
            self._completed_label_b_device = None
            self._completed_group_length_host = None
            self._completed_label_a_host = None
            self._completed_label_b_host = None
            self._completed_group_count = None
            self._completed_point_row_count = None
            self._completed_skipped_group_count = None
            self._completion_device_to_device_seconds = None
            self._completion_device_to_host_seconds = None
            self._private_workspace = None
            self._state = "invalidated"
            self._refresh_seal()

    def _owner_reference_matches(
        self,
        *,
        owner_identity_digest: str,
        batch_ordinal: int,
    ) -> bool:
        self._validate_integrity()
        return (
            owner_identity_digest == self._owner_identity_digest
            and batch_ordinal == self._batch_ordinal
        )

    def to_metadata(self) -> dict[str, object]:
        self._validate_integrity()
        return {
            "contract": "rtdl.compiler_owned_unordered_i64x2_device_batch.v1",
            "owner_identity_digest": self._owner_identity_digest,
            "batch_ordinal": self._batch_ordinal,
            "capacity": self._capacity,
            "completion_residency": self._completion_residency,
            "storage_identity_digest": self._storage_identity_digest,
            "group_count": self._completed_group_count,
            "point_row_count": self._completed_point_row_count,
            "skipped_group_count": self._completed_skipped_group_count,
            "completion_device_to_device_seconds": (
                self._completion_device_to_device_seconds
            ),
            "completion_device_to_host_seconds": (
                self._completion_device_to_host_seconds
            ),
            "producer_workspace_allocation_seconds": (
                self._producer_workspace_allocation_seconds
            ),
            "private_workspace_metadata": (
                None
                if self._private_workspace_metadata is None
                else dict(self._private_workspace_metadata)
            ),
            "workspace_generation_digest": self._workspace_generation_digest,
            "prepared_private_workspace_used": (
                self._private_workspace_metadata is not None
            ),
            "consumer_reads_completion_host_snapshot": (
                self._completion_residency == "host"
            ),
            "consumer_reads_completion_device_snapshot": (
                self._completion_residency == "device"
            ),
            "device_storage_post_completion_mutation_can_affect_consumer": False,
            "state": self._state,
            "compiler_allocated_before_producer": True,
            "exactly_once_delivery_contract": True,
            "single_consumption": True,
            "raw_device_pointer_exposed_in_metadata": False,
        }


@dataclass(frozen=True)
class HostGroupedI64x2QueryResult:
    payload: tuple[ReductionRelation, ...]
    query_ordinal: int
    timing_regime: str
    elapsed_seconds: float
    prepared_identity_digest: str
    backend_owner_generation: int
    event_batch_certificate: Mapping[str, object]
    phase_timing_seconds: Mapping[str, float]

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": "rtdl.host_grouped_i64x2_query_result.private_candidate.v1",
            "query_ordinal": self.query_ordinal,
            "timing_regime": self.timing_regime,
            "elapsed_seconds": self.elapsed_seconds,
            "prepared_identity_digest": self.prepared_identity_digest,
            "backend_owner_generation": self.backend_owner_generation,
            "event_batch_certificate": dict(self.event_batch_certificate),
            "phase_timing_seconds": dict(self.phase_timing_seconds),
            "runtime_speedup_claimed": False,
        }


class HostI64x2ReductionRows(Sequence[tuple[tuple[int, int], int]]):
    """Immutable row view over compiler-owned canonical reduction columns.

    ``ReductionRelation`` historically stores Python tuple rows.  Building two
    complete key/value tuple trees for COUNT and SUM only to have an app join
    them again is unnecessary.  This view preserves the public sequence
    behavior while keeping the generic host physical result columnar until a
    consumer actually iterates it.
    """

    __slots__ = ("_key0", "_key1", "_values")

    def __init__(self, key0, key1, values) -> None:
        self._key0 = _immutable_numpy_1d(key0)
        self._key1 = _immutable_numpy_1d(key1)
        self._values = _immutable_numpy_1d(values)

    @classmethod
    def _from_compiler_owned(cls, key0, key1, values):
        """Wrap detached compiler arrays while preserving shared key identity."""

        instance = cls.__new__(cls)
        instance._key0 = key0
        instance._key1 = key1
        instance._values = values
        for value in (key0, key1, values):
            if value.flags.writeable:
                raise ValueError("compiler-owned reduction columns must be immutable")
        return instance

    def __len__(self) -> int:
        return int(self._values.shape[0])

    def __iter__(self) -> Iterator[tuple[tuple[int, int], int]]:
        for index in range(len(self)):
            yield (
                (int(self._key0[index]), int(self._key1[index])),
                int(self._values[index]),
            )

    def __getitem__(self, index):
        if isinstance(index, slice):
            return tuple(self[position] for position in range(*index.indices(len(self))))
        position = int(index)
        if position < 0:
            position += len(self)
        if position < 0 or position >= len(self):
            raise IndexError(index)
        return (
            (int(self._key0[position]), int(self._key1[position])),
            int(self._values[position]),
        )

    def to_i64x2_columns(self):
        """Expose read-only owned columns to a compatible generic consumer."""

        return self._key0, self._key1, self._values


class AlignedI64x2CountSumProjection:
    """Validated columnar projection over aligned COUNT and SUM relations.

    The checked host and device reducers already return canonical immutable
    columns.  Consumers that need both complete rows and a ranked prefix should
    not repeatedly index NumPy scalars or sort Python dictionaries.  This
    app-neutral view converts each column to Python integers once and computes
    ranked indices against the existing immutable columns.
    """

    __slots__ = ("_key_fields", "_key0", "_key1", "_counts", "_sums")

    def __init__(
        self,
        *,
        key_fields: tuple[str, str],
        key0,
        key1,
        counts,
        sums,
    ) -> None:
        import numpy as np

        arrays = tuple(np.asarray(value) for value in (key0, key1, counts, sums))
        if (
            len(key_fields) != 2
            or any(array.ndim != 1 for array in arrays)
            or len({int(array.shape[0]) for array in arrays}) != 1
            or arrays[0].dtype != np.dtype(np.int64)
            or arrays[1].dtype != np.dtype(np.int64)
            or arrays[2].dtype not in {np.dtype(np.int64), np.dtype(np.uint64)}
            or arrays[3].dtype != np.dtype(np.int64)
            or any(array.flags.writeable for array in arrays)
        ):
            raise ValueError(
                "aligned i64x2 count/sum projection requires immutable "
                "one-dimensional canonical integer columns"
            )
        if arrays[0].shape[0] > 1:
            descending = (arrays[0][1:] < arrays[0][:-1]) | (
                (arrays[0][1:] == arrays[0][:-1])
                & (arrays[1][1:] < arrays[1][:-1])
            )
            if bool(np.any(descending)):
                raise ValueError(
                    "aligned i64x2 count/sum projection keys are not canonical"
                )
        self._key_fields = key_fields
        self._key0, self._key1, self._counts, self._sums = arrays

    @property
    def row_count(self) -> int:
        return int(self._counts.shape[0])

    def to_python_columns(
        self,
    ) -> tuple[list[int], list[int], list[int], list[int]]:
        """Detach the four canonical columns to Python integers exactly once."""

        return (
            self._key0.tolist(),
            self._key1.tolist(),
            self._counts.tolist(),
            self._sums.tolist(),
        )

    def top_indices_by_sum(self, limit: int) -> tuple[int, ...]:
        """Return SUM-descending, key-ascending indices without row objects."""

        import numpy as np

        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 0:
            raise ValueError("top index limit must be a nonnegative integer")
        if limit == 0 or self.row_count == 0:
            return ()
        # Map signed int64 order to uint64, then invert it so an ascending
        # lexsort implements exact signed-descending order without overflowing
        # INT64_MIN.  key0/key1 remain ascending tie breakers.
        signed_order = np.bitwise_xor(
            self._sums.view(np.uint64),
            np.uint64(1 << 63),
        )
        descending_sum = np.bitwise_not(signed_order)
        order = np.lexsort((self._key1, self._key0, descending_sum))
        return tuple(int(index) for index in order[: min(limit, self.row_count)])

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": "rtdl.aligned_i64x2_count_sum_projection.v1",
            "key_fields": list(self._key_fields),
            "row_count": self.row_count,
            "canonical_key_order_validated": True,
            "python_scalar_conversion_count_per_column": 1,
            "python_row_sort_used_for_ranked_prefix": False,
            "application_or_publication_identity_used": False,
        }


def aligned_i64x2_count_sum_projection(
    reductions: Sequence[ReductionRelation],
    *,
    count_reduction_name: str,
    sum_reduction_name: str,
) -> AlignedI64x2CountSumProjection:
    """Bind two canonical relations to one generic aligned columnar view."""

    by_name = {relation.name: relation for relation in reductions}
    if (
        len(by_name) != len(reductions)
        or count_reduction_name not in by_name
        or sum_reduction_name not in by_name
    ):
        raise ValueError("count/sum projection reduction names are incomplete")
    count_relation = by_name[count_reduction_name]
    sum_relation = by_name[sum_reduction_name]
    count_columns = getattr(count_relation.rows, "to_i64x2_columns", None)
    sum_columns = getattr(sum_relation.rows, "to_i64x2_columns", None)
    if not callable(count_columns) or not callable(sum_columns):
        raise TypeError("count/sum projection requires columnar reduction rows")
    count_key0, count_key1, counts = count_columns()
    sum_key0, sum_key1, sums = sum_columns()
    if (
        count_relation.key_fields != sum_relation.key_fields
        or len(count_relation.key_fields) != 2
        or count_key0 is not sum_key0
        or count_key1 is not sum_key1
    ):
        raise ValueError("count/sum projection relations do not share exact keys")
    return AlignedI64x2CountSumProjection(
        key_fields=(
            str(count_relation.key_fields[0]),
            str(count_relation.key_fields[1]),
        ),
        key0=count_key0,
        key1=count_key1,
        counts=counts,
        sums=sums,
    )


def _immutable_numpy_1d(values):
    """Detach into a bytes-backed ndarray whose write flag cannot be restored."""

    import numpy as np

    contiguous = np.ascontiguousarray(values)
    if contiguous.ndim != 1:
        raise ValueError("immutable reduction column must be one-dimensional")
    payload = contiguous.tobytes(order="C")
    return np.frombuffer(payload, dtype=contiguous.dtype, count=contiguous.size)


def _readonly_compiler_owned_numpy_1d(values):
    """Make a compiler-created D2H ndarray/view read-only without another copy.

    Numba may represent a fresh ``DeviceNDArray`` slice download as a
    C-contiguous one-dimensional view whose base is the fresh host allocation;
    ``flags.owndata`` is therefore not an ownership certificate.  This helper
    is valid only at the compiler-owned D2H creation site.  The view and its
    base never escape the prepared query, while the original producer retains
    only the unrelated device allocation.
    """

    import numpy as np

    array = np.asarray(values)
    if array.ndim != 1 or not array.flags.c_contiguous:
        raise ValueError(
            "compiler-created D2H column must be contiguous and one-dimensional"
        )
    array.setflags(write=False)
    return array


def compile_host_grouped_i64x2_count_sum(
    spec,
    *,
    discharged_delivery_proofs: frozenset[str] = frozenset(),
) -> HostGroupedI64x2CountSumProgram:
    """Lower the generic grouped shape after the shared strict shape verifier."""

    # The existing device lowerer owns the authoritative closed-shape verifier.
    # Reusing it keeps both physical templates locked to one exact Action subset;
    # no Numba kernel or device runtime is constructed by this call.
    checked = compile_numba_grouped_i64x2_count_sum(
        spec,
        discharged_delivery_proofs=discharged_delivery_proofs,
    )
    validate_numba_grouped_i64x2_order_indexed_binding_shape(checked)
    logical_keys = tuple(checked.spec.logical_event.key_fields)
    if len(logical_keys) != 1:
        _fail(
            "generated_host_logical_key_unsupported",
            "logical_event.key_fields",
            repr(logical_keys),
        )
    return HostGroupedI64x2CountSumProgram(
        spec=checked.spec,
        event_fields=checked.event_fields,
        key_fields=checked.key_fields,
        sum_field=checked.sum_field,
        count_reduction_name=checked.count_reduction_name,
        sum_reduction_name=checked.sum_reduction_name,
        delivery_proof_reference=checked.delivery_proof_reference,
        parameter_fields=checked.parameter_fields,
    )


def _validate_canonical_host_grouped_i64x2_count_sum_program(
    program: HostGroupedI64x2CountSumProgram,
) -> HostGroupedI64x2CountSumProgram:
    """Recompile every executable role before a public program is trusted."""

    if type(program) is not HostGroupedI64x2CountSumProgram:
        _fail("host_grouped_program_required", "program", type(program).__name__)
    canonical = compile_host_grouped_i64x2_count_sum(
        program.spec,
        discharged_delivery_proofs=frozenset({program.delivery_proof_reference}),
    )
    if program != canonical:
        _fail(
            "host_grouped_program_role_binding_invalid",
            "program",
            "compiler-issued executable roles differ from canonical Action lowering",
        )
    return canonical


def materialize_sorted_host_grouped_i64x2_batch(
    program: HostGroupedI64x2CountSumProgram,
    source_columns: Mapping[str, object],
    *,
    max_row_count: int,
) -> HostGroupedI64x2MaterializedBatch:
    """Own one typed batch on host and establish its exact canonical order."""

    canonical = _validate_canonical_host_grouped_i64x2_count_sum_program(program)
    return _materialize_sorted_host_grouped_i64x2_batch(
        canonical,
        source_columns,
        max_row_count=max_row_count,
        persistent_content_digest_required=True,
    )


def _materialize_sorted_host_grouped_i64x2_batch(
    program: HostGroupedI64x2CountSumProgram,
    source_columns: Mapping[str, object],
    *,
    max_row_count: int,
    persistent_content_digest_required: bool,
) -> HostGroupedI64x2MaterializedBatch:
    """Internal owner materialization; the consumed path never exposes aliases."""

    import numpy as np

    materialize_started = time.perf_counter()
    transfer_seconds = 0.0
    validation_seconds = 0.0

    if type(program) is not HostGroupedI64x2CountSumProgram:
        _fail("host_grouped_program_required", "program", type(program).__name__)
    if not isinstance(source_columns, Mapping):
        _fail("event_columns_mapping_required", "source_columns", type(source_columns).__name__)
    if (
        not isinstance(max_row_count, int)
        or isinstance(max_row_count, bool)
        or max_row_count < 0
    ):
        _fail("invalid_prepared_event_batch_capacity", "max_row_count", repr(max_row_count))

    logical_keys = tuple(program.spec.logical_event.key_fields)
    if len(logical_keys) != 1:
        _fail(
            "generated_host_logical_key_unsupported",
            "logical_event.key_fields",
            repr(logical_keys),
        )
    logical_key = logical_keys[0]
    expected = set(program.event_fields)
    accepted_without_generated_key = expected - {logical_key}
    supplied = set(source_columns)
    if supplied not in (expected, accepted_without_generated_key):
        _fail(
            "event_column_schema_mismatch",
            "source_columns",
            f"expected {sorted(expected)!r} or {sorted(accepted_without_generated_key)!r}",
        )

    arrays: dict[str, object] = {}
    arrays_from_device_inputs: dict[str, bool] = {}
    row_count: int | None = None
    device_copy_used = False
    for field in program.spec.event_type.fields:
        if field.name == logical_key and field.name not in source_columns:
            continue
        value = source_columns[field.name]
        is_device = bool(
            hasattr(value, "copy_to_host")
            or hasattr(value, "__cuda_array_interface__")
        )
        transfer_started = time.perf_counter()
        if hasattr(value, "copy_to_host"):
            host = value.copy_to_host()
        elif hasattr(value, "__cuda_array_interface__"):
            try:
                from numba import cuda  # type: ignore

                host = cuda.as_cuda_array(value).copy_to_host()
            except Exception as exc:  # pragma: no cover - hardware/runtime specific.
                _fail(
                    "device_column_download_failed",
                    f"source_columns.{field.name}",
                    str(exc),
                )
        else:
            host = np.asarray(value)
        transfer_seconds += time.perf_counter() - transfer_started
        validation_started = time.perf_counter()
        device_copy_used = device_copy_used or is_device
        array = np.asarray(host)
        if array.ndim != 1 or array.dtype != np.dtype(np.int64):
            _fail(
                "event_column_layout_mismatch",
                f"source_columns.{field.name}",
                "expected contiguous 1-D int64",
            )
        count = int(array.shape[0])
        if row_count is None:
            row_count = count
        elif row_count != count:
            _fail(
                "event_column_length_mismatch",
                f"source_columns.{field.name}",
                str(count),
            )
        # Establish compiler ownership before any value validation.  A real
        # Numba ``copy_to_host`` currently returns a fresh ndarray, but the
        # accepted device-column protocol is structural and must not trust an
        # arbitrary provider's returned object to be detached.  The explicit
        # copy also closes the same validation/sort TOCTOU for host columns.
        owned = np.array(array, dtype=np.int64, order="C", copy=True)
        defer_sum_nonnegative = bool(
            not persistent_content_digest_required
            and field.name == program.sum_field
            and field.nonnegative
        )
        if field.nonnegative and not defer_sum_nonnegative and bool(np.any(owned < 0)):
            _fail(
                "nonnegative_field_violation",
                f"source_columns.{field.name}",
                field.name,
            )
        arrays[field.name] = owned
        arrays_from_device_inputs[field.name] = is_device
        validation_seconds += time.perf_counter() - validation_started

    resolved_count = row_count or 0
    if resolved_count > max_row_count:
        _fail(
            "prepared_event_batch_capacity_exceeded",
            "source_columns",
            f"rows={resolved_count}; capacity={max_row_count}",
        )
    generated = logical_key not in arrays
    if not generated and resolved_count > 1:
        logical = np.asarray(arrays[logical_key])
        if int(np.unique(logical).shape[0]) != resolved_count:
            _fail(
                "duplicate_logical_event_key",
                f"source_columns.{logical_key}",
                "logical event key values must be globally unique",
            )

    digest_started = time.perf_counter()
    content_digest = None
    if persistent_content_digest_required:
        digest = hashlib.sha256(b"rtdl.host_grouped_i64x2_batch.v2\x00")
        for name in program.event_fields:
            digest.update(name.encode("utf-8"))
            digest.update(b"\x00")
            digest.update(str(resolved_count).encode("ascii"))
            digest.update(b"\x00")
            if generated and name == logical_key:
                # The logical key is exactly iota(source_row_count).  Binding that
                # closed generator and count is equivalent to hashing an O(N)
                # materialized array but avoids an allocation and memory pass.
                digest.update(b"compiler_generated_iota_i64.v1\x00")
            else:
                array = np.asarray(arrays[name])
                little_endian = array.astype("<i8", copy=False)
                digest.update(memoryview(little_endian).cast("B"))
        content_digest = digest.hexdigest()
    digest_seconds = time.perf_counter() - digest_started

    ordering_fields = (*program.key_fields, logical_key)
    sort_started = time.perf_counter()
    if resolved_count > 1:
        if generated:
            # np.lexsort is stable, so source order is the implicit iota
            # tiebreaker for equal i64x2 keys.  This is the exact established
            # V2 generic reducer order without materializing the iota column.
            order = np.lexsort(
                (
                    np.asarray(arrays[program.key_fields[1]]),
                    np.asarray(arrays[program.key_fields[0]]),
                )
            )
        else:
            order = np.lexsort(
                tuple(np.asarray(arrays[name]) for name in reversed(ordering_fields))
            )
        arrays = {
            name: np.ascontiguousarray(np.asarray(values)[order])
            for name, values in arrays.items()
        }
    else:
        arrays = {
            name: np.ascontiguousarray(values)
            for name, values in arrays.items()
        }
    # Persistent batches may outlive this call and therefore retain the
    # irreversible bytes-backed ownership boundary.  The prepared consumed
    # path is synchronous and its freshly detached, sorted columns are never
    # exposed; making those arrays read-only avoids serializing the complete
    # batch into bytes only to scan it immediately.
    immutable_wrapper = (
        _immutable_numpy_1d
        if persistent_content_digest_required
        else _readonly_compiler_owned_numpy_1d
    )
    arrays = MappingProxyType(
        {name: immutable_wrapper(values) for name, values in arrays.items()}
    )
    sort_seconds = time.perf_counter() - sort_started

    all_source_columns_device = bool(arrays_from_device_inputs) and all(
        arrays_from_device_inputs.values()
    )
    return HostGroupedI64x2MaterializedBatch(
        columns=arrays,
        row_count=resolved_count,
        source_residency=(
            "device"
            if all_source_columns_device
            else ("mixed_host_device" if device_copy_used else "host")
        ),
        device_to_host_copy_used=device_copy_used,
        compiler_generated_logical_key=generated,
        ordering_fields=ordering_fields,
        content_digest=content_digest,
        binding_kind=(
            "persistent_full_content_sha256"
            if persistent_content_digest_required
            else (
                "synchronous_consumed_compiler_owned_device_download_columns"
                if all_source_columns_device
                else "synchronous_copied_caller_owned_host_columns"
            )
        ),
        sum_field_nonnegative_validation_deferred_to_checked_scan=bool(
            not persistent_content_digest_required
            and program.spec.event_type.field(program.sum_field).nonnegative
        ),
        phase_timing_seconds={
            "device_to_host_or_host_view_seconds": float(transfer_seconds),
            "layout_ownership_and_value_validation_seconds": float(validation_seconds),
            "persistent_content_digest_seconds": float(digest_seconds),
            "canonical_sort_and_permute_seconds": float(sort_seconds),
            "materialize_total_seconds": float(time.perf_counter() - materialize_started),
        },
    )


def execute_sorted_host_grouped_i64x2_count_sum(
    program: HostGroupedI64x2CountSumProgram,
    event_columns: Mapping[str, object],
) -> tuple[ReductionRelation, ...]:
    """Execute a compiler-owned sorted scan with fail-closed signed overflow."""

    canonical = _validate_canonical_host_grouped_i64x2_count_sum_program(program)
    return _execute_sorted_host_grouped_i64x2_count_sum(canonical, event_columns)


def _execute_sorted_host_grouped_i64x2_count_sum(
    program: HostGroupedI64x2CountSumProgram,
    event_columns: Mapping[str, object],
) -> tuple[ReductionRelation, ...]:
    """Hot execution for a program canonicalized by the prepared owner."""

    import numpy as np

    expected = set(program.event_fields)
    logical_keys = tuple(program.spec.logical_event.key_fields)
    implicit_logical = expected - set(logical_keys)
    if set(event_columns) not in (expected, implicit_logical):
        _fail("event_column_schema_mismatch", "event_columns", repr(sorted(event_columns)))
    arrays = {name: np.asarray(value) for name, value in event_columns.items()}
    row_counts = {int(array.shape[0]) for array in arrays.values() if array.ndim == 1}
    if (
        any(array.ndim != 1 or array.dtype != np.dtype(np.int64) for array in arrays.values())
        or len(row_counts) != 1
    ):
        _fail(
            "event_column_layout_mismatch",
            "event_columns",
            "expected equal-length contiguous 1-D int64 columns",
        )
    row_count = next(iter(row_counts), 0)
    key0 = np.ascontiguousarray(arrays[program.key_fields[0]])
    key1 = np.ascontiguousarray(arrays[program.key_fields[1]])
    values = np.ascontiguousarray(arrays[program.sum_field])
    out0 = np.empty(row_count, dtype=np.int64)
    out1 = np.empty(row_count, dtype=np.int64)
    out_counts = np.empty(row_count, dtype=np.uint64)
    out_sums = np.empty(row_count, dtype=np.int64)
    count, error = _aggregate_sorted_i64x2_dispatch(
        key0,
        key1,
        values,
        out0,
        out1,
        out_counts,
        out_sums,
        sum_field_nonnegative=bool(
            program.spec.event_type.field(program.sum_field).nonnegative
        ),
    )
    if error == 1:
        _fail(
            "group_key_order_certificate_violated",
            "event_columns.key_order",
            "i64x2 keys are not lexicographically nondecreasing",
        )
    if error == 2:
        _fail("signed_reduction_overflow", "event_columns.sum", "signed i64 sum overflowed")
    if error == 3:
        _fail(
            "nonnegative_field_violation",
            f"event_columns.{program.sum_field}",
            program.sum_field,
        )
    if error:
        _fail("unknown_host_reduction_error", "event_columns", str(error))
    keys0 = _immutable_numpy_1d(out0[:count])
    keys1 = _immutable_numpy_1d(out1[:count])
    counts = _immutable_numpy_1d(out_counts[:count])
    sums = _immutable_numpy_1d(out_sums[:count])
    by_name = {
        program.count_reduction_name: ReductionRelation(
            program.count_reduction_name,
            program.key_fields,
            HostI64x2ReductionRows._from_compiler_owned(keys0, keys1, counts),
        ),
        program.sum_reduction_name: ReductionRelation(
            program.sum_reduction_name,
            program.key_fields,
            HostI64x2ReductionRows._from_compiler_owned(keys0, keys1, sums),
        ),
    }
    return tuple(by_name[reduction.name] for reduction in program.spec.reductions)


def _execute_order_indexed_host_grouped_i64x2_count_sum(
    program: HostGroupedI64x2CountSumProgram,
    event_columns: Mapping[str, object],
    order,
) -> tuple[ReductionRelation, ...]:
    """Consume detached host columns through compiler-created key order."""

    import numpy as np

    expected = set(program.event_fields)
    logical_keys = tuple(program.spec.logical_event.key_fields)
    implicit_logical = expected - set(logical_keys)
    if set(event_columns) not in (expected, implicit_logical):
        _fail("event_column_schema_mismatch", "event_columns", repr(sorted(event_columns)))
    arrays = {name: np.asarray(value) for name, value in event_columns.items()}
    row_counts = {int(array.shape[0]) for array in arrays.values() if array.ndim == 1}
    if (
        any(array.ndim != 1 or array.dtype != np.dtype(np.int64) for array in arrays.values())
        or len(row_counts) != 1
    ):
        _fail(
            "event_column_layout_mismatch",
            "event_columns",
            "expected equal-length contiguous 1-D int64 columns",
        )
    row_count = next(iter(row_counts), 0)
    order_array = np.ascontiguousarray(order, dtype=np.int64)
    if order_array.ndim != 1 or int(order_array.shape[0]) != row_count:
        _fail(
            "event_order_shape_mismatch",
            "order",
            f"rows={row_count}; order_shape={order_array.shape}",
        )
    if row_count:
        if (
            int(order_array.min()) != 0
            or int(order_array.max()) != row_count - 1
            or int(np.unique(order_array).shape[0]) != row_count
        ):
            _fail(
                "event_order_not_a_permutation",
                "order",
                "compiler order must contain every source row exactly once",
            )
    key0 = np.ascontiguousarray(arrays[program.key_fields[0]])
    key1 = np.ascontiguousarray(arrays[program.key_fields[1]])
    values = np.ascontiguousarray(arrays[program.sum_field])
    out0 = np.empty(row_count, dtype=np.int64)
    out1 = np.empty(row_count, dtype=np.int64)
    out_counts = np.empty(row_count, dtype=np.uint64)
    out_sums = np.empty(row_count, dtype=np.int64)
    count, error = _aggregate_order_indexed_i64x2_dispatch(
        key0,
        key1,
        values,
        order_array,
        out0,
        out1,
        out_counts,
        out_sums,
        sum_field_nonnegative=bool(
            program.spec.event_type.field(program.sum_field).nonnegative
        ),
    )
    if error == 1:
        _fail(
            "group_key_order_certificate_violated",
            "event_columns.key_order",
            "order-indexed i64x2 keys are not lexicographically nondecreasing",
        )
    if error == 2:
        _fail("signed_reduction_overflow", "event_columns.sum", "signed i64 sum overflowed")
    if error == 3:
        _fail(
            "nonnegative_field_violation",
            f"event_columns.{program.sum_field}",
            program.sum_field,
        )
    if error == 4:
        _fail("event_order_index_out_of_range", "order", "order index is out of range")
    if error:
        _fail("unknown_host_reduction_error", "event_columns", str(error))
    keys0 = _immutable_numpy_1d(out0[:count])
    keys1 = _immutable_numpy_1d(out1[:count])
    counts = _immutable_numpy_1d(out_counts[:count])
    sums = _immutable_numpy_1d(out_sums[:count])
    by_name = {
        program.count_reduction_name: ReductionRelation(
            program.count_reduction_name,
            program.key_fields,
            HostI64x2ReductionRows._from_compiler_owned(keys0, keys1, counts),
        ),
        program.sum_reduction_name: ReductionRelation(
            program.sum_reduction_name,
            program.key_fields,
            HostI64x2ReductionRows._from_compiler_owned(keys0, keys1, sums),
        ),
    }
    return tuple(by_name[reduction.name] for reduction in program.spec.reductions)


class PreparedHostGroupedI64x2CountSumExecution:
    """Prepared host physical route for bounded variable typed-column batches."""

    __slots__ = (
        "_active_producer_batch",
        "_closed",
        "_eager_specialization_count",
        "_eager_specialization_seconds",
        "_identity_digest",
        "_identity_payload_bytes",
        "_last_batch_metadata",
        "_max_event_rows",
        "_program",
        "_query_elapsed_seconds",
        "_resource_seal",
    )

    def __init__(self, planned, *, max_event_rows: int) -> None:
        from .action_api import validate_planned_lowered_action

        validate_planned_lowered_action(planned)
        lowered = planned.lowered
        if (
            lowered.backend != "host"
            or lowered.template_kind != "sorted_host_i64x2_count_sum"
            or type(lowered.program) is not HostGroupedI64x2CountSumProgram
        ):
            _fail("host_grouped_plan_required", "planned.lowered", lowered.template_kind)
        canonical_program = _validate_canonical_host_grouped_i64x2_count_sum_program(
            lowered.program
        )
        eager_specialization_started = time.perf_counter()
        eager_specialization_count = 0
        if _NUMBA_HOST_SCAN_AVAILABLE:
            import numpy as np

            empty_i64 = np.empty(0, dtype=np.int64)
            empty_u64 = np.empty(0, dtype=np.uint64)
            compiled_count, compiled_error = _aggregate_sorted_i64x2_numba(
                empty_i64,
                empty_i64,
                empty_i64,
                empty_i64,
                empty_i64,
                empty_u64,
                empty_i64,
                bool(canonical_program.spec.event_type.field(canonical_program.sum_field).nonnegative),
            )
            if int(compiled_count) != 0 or int(compiled_error) != 0:
                _fail(
                    "host_grouped_eager_specialization_failed",
                    "prepared",
                    f"count={compiled_count}; error={compiled_error}",
                )
            indexed_count, indexed_error = _aggregate_order_indexed_i64x2_numba(
                empty_i64,
                empty_i64,
                empty_i64,
                empty_i64,
                empty_i64,
                empty_i64,
                empty_u64,
                empty_i64,
                bool(
                    canonical_program.spec.event_type.field(
                        canonical_program.sum_field
                    ).nonnegative
                ),
            )
            if int(indexed_count) != 0 or int(indexed_error) != 0:
                _fail(
                    "host_grouped_order_indexed_eager_specialization_failed",
                    "prepared",
                    f"count={indexed_count}; error={indexed_error}",
                )
            eager_specialization_count = 1
        self._eager_specialization_seconds = float(
            time.perf_counter() - eager_specialization_started
        )
        self._eager_specialization_count = eager_specialization_count
        if (
            not isinstance(max_event_rows, int)
            or isinstance(max_event_rows, bool)
            or max_event_rows < 0
        ):
            _fail("invalid_prepared_event_batch_capacity", "max_event_rows", repr(max_event_rows))
        certificate = lowered.event_column_certificate
        if certificate is None or certificate.row_count > max_event_rows:
            _fail(
                "prepared_event_batch_capacity_too_small",
                "max_event_rows",
                repr(max_event_rows),
            )
        identity_payload = {
            "contract": "rtdl.host_grouped_i64x2_prepared_identity.private_candidate.v1",
            "semantic_digest": lowered.compiled.spec.semantic_digest,
            "source_digest": lowered.compiled.source_digest,
            "producer_binding_digest": lowered.producer_binding_digest,
            "target_profile": planned.target_profile.to_metadata(),
            "plan": planned.plan.to_dict(),
            "template": lowered.program.to_metadata(),
            "max_event_rows": max_event_rows,
        }
        self._identity_payload_bytes = json.dumps(
            identity_payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self._identity_digest = hashlib.sha256(
            self._identity_payload_bytes
        ).hexdigest()
        # Query execution is detached from the caller-retained plan object. The
        # full plan and canonical role validation happened once above; only this
        # compiler-reconstructed immutable program participates in hot queries.
        self._program = canonical_program
        self._max_event_rows = max_event_rows
        self._query_elapsed_seconds: list[float] = []
        self._last_batch_metadata: Mapping[str, object] | None = None
        self._active_producer_batch: (
            CompilerOwnedUnorderedI64x2DeviceBatch | None
        ) = None
        self._closed = False
        self._resource_seal = self._issue_resource_seal()

    def _resource_seal_payload(self) -> bytes:
        payload = {
            "contract": "rtdl.host_grouped_i64x2_prepared_resource_seal.v1",
            "owner_type": type(self).__name__,
            "program_type": type(self._program).__name__,
            "program_object_id": id(self._program),
            "program_metadata": self._program.to_metadata(),
            "identity_payload_sha256": hashlib.sha256(
                self._identity_payload_bytes
            ).hexdigest(),
            "identity_digest": self._identity_digest,
            "max_event_rows": self._max_event_rows,
            "eager_specialization_seconds": self._eager_specialization_seconds,
            "eager_specialization_count": self._eager_specialization_count,
            "query_elapsed_seconds": list(self._query_elapsed_seconds),
            "last_batch_metadata": (
                None
                if self._last_batch_metadata is None
                else dict(self._last_batch_metadata)
            ),
            "active_producer_batch": (
                None
                if self._active_producer_batch is None
                else {
                    "object_id": id(self._active_producer_batch),
                    "owner_and_ordinal_match": (
                        self._active_producer_batch._owner_reference_matches(
                            owner_identity_digest=self._identity_digest,
                            batch_ordinal=len(self._query_elapsed_seconds),
                        )
                    ),
                }
            ),
            "closed": self._closed,
        }
        return json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    def _issue_resource_seal(self) -> str:
        return hmac.new(
            _HOST_GROUPED_PREPARED_RESOURCE_SECRET,
            self._resource_seal_payload(),
            hashlib.sha256,
        ).hexdigest()

    def _validate_integrity(self) -> None:
        if type(self) is not PreparedHostGroupedI64x2CountSumExecution:
            _fail("host_grouped_prepared_owner_required", "prepared", type(self).__name__)
        if type(self._program) is not HostGroupedI64x2CountSumProgram:
            _fail(
                "host_grouped_prepared_program_substituted",
                "prepared.program",
                type(self._program).__name__,
            )
        if (
            not isinstance(self._identity_payload_bytes, bytes)
            or not isinstance(self._identity_digest, str)
            or hashlib.sha256(self._identity_payload_bytes).hexdigest()
            != self._identity_digest
            or not isinstance(self._max_event_rows, int)
            or isinstance(self._max_event_rows, bool)
            or self._max_event_rows < 0
            or not isinstance(self._eager_specialization_count, int)
            or isinstance(self._eager_specialization_count, bool)
            or self._eager_specialization_count not in {0, 1}
            or not isinstance(self._eager_specialization_seconds, float)
            or not math.isfinite(self._eager_specialization_seconds)
            or self._eager_specialization_seconds < 0.0
            or type(self._query_elapsed_seconds) is not list
            or any(
                not isinstance(value, float)
                or not math.isfinite(value)
                or value < 0.0
                for value in self._query_elapsed_seconds
            )
            or (
                self._last_batch_metadata is not None
                and type(self._last_batch_metadata) is not MappingProxyType
            )
            or (
                self._active_producer_batch is not None
                and (
                    type(self._active_producer_batch)
                    is not CompilerOwnedUnorderedI64x2DeviceBatch
                    or not self._active_producer_batch._owner_reference_matches(
                        owner_identity_digest=self._identity_digest,
                        batch_ordinal=len(self._query_elapsed_seconds),
                    )
                )
            )
            or type(self._closed) is not bool
            or not isinstance(self._resource_seal, str)
            or not hmac.compare_digest(
                self._resource_seal,
                self._issue_resource_seal(),
            )
        ):
            _fail(
                "host_grouped_prepared_resource_seal_invalid",
                "prepared",
                "prepared host resource identity or lifecycle state changed",
            )

    def _refresh_resource_seal(self) -> None:
        self._resource_seal = self._issue_resource_seal()

    @property
    def closed(self) -> bool:
        self._validate_integrity()
        return self._closed

    def begin_producer_owned_device_batch(
        self,
        *,
        capacity: int,
    ) -> CompilerOwnedUnorderedI64x2DeviceBatch:
        """Allocate one compiler-owned producer output batch."""

        self._validate_integrity()
        if self._closed:
            _fail("prepared_execution_closed", "prepared", "prepared host execution is closed")
        if self._active_producer_batch is not None:
            _fail(
                "producer_owned_batch_already_active",
                "prepared",
                "one producer batch must be consumed before another begins",
            )
        if (
            not isinstance(capacity, int)
            or isinstance(capacity, bool)
            or capacity < 0
            or capacity > self._max_event_rows
        ):
            _fail(
                "producer_owned_batch_capacity_invalid",
                "capacity",
                f"capacity={capacity}; max_event_rows={self._max_event_rows}",
            )
        try:
            from numba import cuda  # type: ignore
            import numpy as np

            allocated_capacity = max(1, capacity)
            batch = CompilerOwnedUnorderedI64x2DeviceBatch(
                owner_identity_digest=self._identity_digest,
                batch_ordinal=len(self._query_elapsed_seconds),
                capacity=capacity,
                group_length_device=cuda.device_array(
                    allocated_capacity,
                    dtype=np.int64,
                ),
                label_a_device=cuda.device_array(
                    allocated_capacity,
                    dtype=np.int64,
                ),
                label_b_device=cuda.device_array(
                    allocated_capacity,
                    dtype=np.int64,
                ),
                counters_device=cuda.to_device(np.zeros(3, dtype=np.int64)),
                overflow_device=cuda.to_device(np.zeros(1, dtype=np.int64)),
            )
        except ActionPlacementError:
            raise
        except Exception as exc:  # pragma: no cover - hardware/runtime specific.
            _fail(
                "producer_owned_batch_allocation_failed",
                "prepared",
                str(exc),
            )
        self._active_producer_batch = batch
        self._refresh_resource_seal()
        return batch

    def execute_producer_owned_device_batch(
        self,
        batch: CompilerOwnedUnorderedI64x2DeviceBatch,
        *,
        extents,
        parameters,
    ):
        """Consume one completed producer-owned batch without payload permutation."""

        self._validate_integrity()
        if self._closed:
            _fail("prepared_execution_closed", "prepared", "prepared host execution is closed")
        if extents or parameters:
            _fail(
                "prepared_query_contract_mismatch",
                "extents_or_parameters",
                "grouped host reduction accepts empty extents and parameters",
            )
        ordinal = len(self._query_elapsed_seconds)
        if (
            type(batch) is not CompilerOwnedUnorderedI64x2DeviceBatch
            or batch is not self._active_producer_batch
        ):
            _fail(
                "producer_owned_batch_substitution",
                "batch",
                "batch is not the active compiler-owned producer allocation",
            )
        started = time.perf_counter()
        try:
            host_snapshot_columns, producer_receipt = batch._consume(
                owner_identity_digest=self._identity_digest,
                batch_ordinal=ordinal,
            )
            import numpy as np

            host_columns = {
                name: np.asarray(column)
                for name, column in host_snapshot_columns.items()
            }
            transfer_seconds = float(
                producer_receipt["completion_device_to_host_seconds"]
            )
            row_counts = {
                int(array.shape[0])
                for array in host_columns.values()
                if array.ndim == 1
            }
            if (
                any(
                    array.ndim != 1 or array.dtype != np.dtype(np.int64)
                    for array in host_columns.values()
                )
                or len(row_counts) != 1
            ):
                _fail(
                    "producer_owned_host_column_layout_mismatch",
                    "batch",
                    "expected equal-length 1-D int64 D2H results",
                )
            row_count = next(iter(row_counts), 0)
            order_started = time.perf_counter()
            order = np.ascontiguousarray(
                np.lexsort(
                    (
                        host_columns[self._program.key_fields[1]],
                        host_columns[self._program.key_fields[0]],
                    )
                ),
                dtype=np.int64,
            )
            order_seconds = time.perf_counter() - order_started
            aggregate_started = time.perf_counter()
            payload = _execute_order_indexed_host_grouped_i64x2_count_sum(
                self._program,
                host_columns,
                order,
            )
            aggregate_seconds = time.perf_counter() - aggregate_started
        except BaseException:
            batch.invalidate()
            self._active_producer_batch = None
            self._closed = True
            self._refresh_resource_seal()
            raise
        elapsed = time.perf_counter() - started
        self._query_elapsed_seconds.append(float(elapsed))
        batch_metadata = {
            **producer_receipt,
            "contract": "rtdl.producer_owned_order_indexed_host_batch.v1",
            "row_count": row_count,
            "source_residency": "device",
            "device_to_host_copy_used": True,
            "compiler_generated_logical_key": True,
            "ordering_fields": [
                *self._program.key_fields,
                *self._program.spec.logical_event.key_fields,
            ],
            "binding_kind": "compiler_preallocated_single_consume_device_batch",
            "full_typed_payload_and_order_bound": True,
            "duplicate_logical_keys_rejected": True,
            "caller_owned_device_columns_retained": False,
            "download_result_reowned_by_compiler": False,
            "download_result_owned_by_compiler_at_creation": True,
            "consumer_reads_completion_host_snapshot": True,
            "device_storage_post_completion_mutation_can_affect_consumer": False,
            "python_event_rows_materialized": False,
            "sorted_payload_permutation_used": False,
            "order_indexed_checked_scan_used": True,
            "phase_timing_seconds": {
                "device_to_host_or_host_view_seconds": float(transfer_seconds),
                "layout_ownership_and_value_validation_seconds": 0.0,
                "persistent_content_digest_seconds": 0.0,
                "canonical_order_index_seconds": float(order_seconds),
                "sorted_payload_permutation_seconds": 0.0,
                "materialize_total_seconds": float(
                    transfer_seconds + order_seconds
                ),
            },
        }
        self._last_batch_metadata = MappingProxyType(batch_metadata)
        self._active_producer_batch = None
        self._refresh_resource_seal()
        return HostGroupedI64x2QueryResult(
            payload=payload,
            query_ordinal=ordinal,
            timing_regime="first_query" if ordinal == 0 else "repeated_query",
            elapsed_seconds=float(elapsed),
            prepared_identity_digest=self._identity_digest,
            backend_owner_generation=0,
            event_batch_certificate=batch_metadata,
            phase_timing_seconds={
                "plan_integrity_validation_seconds": 0.0,
                **dict(batch_metadata["phase_timing_seconds"]),
                "checked_grouped_scan_seconds": float(aggregate_seconds),
            },
        )

    def execute_columns(self, event_columns, *, extents, parameters):
        return self._execute(event_columns, extents=extents, parameters=parameters)

    def execute_device_columns(self, event_columns, *, extents, parameters):
        return self._execute(event_columns, extents=extents, parameters=parameters)

    def _execute(self, event_columns, *, extents, parameters):
        self._validate_integrity()
        if self._closed:
            _fail("prepared_execution_closed", "prepared", "prepared host execution is closed")
        if self._active_producer_batch is not None:
            _fail(
                "producer_owned_batch_still_active",
                "prepared",
                "active producer batch must be consumed or invalidated first",
            )
        if extents or parameters:
            _fail(
                "prepared_query_contract_mismatch",
                "extents_or_parameters",
                "grouped host reduction accepts empty extents and parameters",
            )
        started = time.perf_counter()
        batch = _materialize_sorted_host_grouped_i64x2_batch(
            self._program,
            event_columns,
            max_row_count=self._max_event_rows,
            persistent_content_digest_required=False,
        )
        aggregate_started = time.perf_counter()
        payload = _execute_sorted_host_grouped_i64x2_count_sum(
            self._program,
            batch.columns,
        )
        aggregate_seconds = time.perf_counter() - aggregate_started
        elapsed = time.perf_counter() - started
        ordinal = len(self._query_elapsed_seconds)
        self._query_elapsed_seconds.append(float(elapsed))
        self._last_batch_metadata = MappingProxyType(batch.to_metadata())
        self._refresh_resource_seal()
        return HostGroupedI64x2QueryResult(
            payload=payload,
            query_ordinal=ordinal,
            timing_regime="first_query" if ordinal == 0 else "repeated_query",
            elapsed_seconds=float(elapsed),
            prepared_identity_digest=self._identity_digest,
            backend_owner_generation=0,
            event_batch_certificate=batch.to_metadata(),
            phase_timing_seconds={
                "plan_integrity_validation_seconds": 0.0,
                **dict(batch.phase_timing_seconds),
                "checked_grouped_scan_seconds": float(aggregate_seconds),
            },
        )

    def timing_metadata(self) -> dict[str, object]:
        self._validate_integrity()
        return {
            "contract": "rtdl.host_grouped_i64x2_prepared_timing.private_candidate.v1",
            "prepare_seconds": self._eager_specialization_seconds,
            "eager_specialization_seconds": self._eager_specialization_seconds,
            "eager_specialization_count": self._eager_specialization_count,
            "first_query_seconds": (
                self._query_elapsed_seconds[0] if self._query_elapsed_seconds else None
            ),
            "repeated_query_seconds": list(self._query_elapsed_seconds[1:]),
            "query_count": len(self._query_elapsed_seconds),
            "runtime_speedup_claimed": False,
        }

    def to_metadata(self) -> dict[str, object]:
        self._validate_integrity()
        return {
            "contract": "rtdl.host_grouped_i64x2_prepared_execution.private_candidate.v1",
            "identity": {
                "identity_digest": self._identity_digest,
                "identity_payload_sha256": hashlib.sha256(
                    self._identity_payload_bytes
                ).hexdigest(),
                "identity_payload": json.loads(
                    self._identity_payload_bytes.decode("utf-8")
                ),
                "selected_backend": "host",
                "selected_placement": "host_continuation",
                "selected_template": "sorted_host_i64x2_count_sum",
                "event_batch_row_count_mode": "bounded_variable",
                "max_event_rows": self._max_event_rows,
            },
            "event_batch_lifecycle": {
                "row_count_mode": "bounded_variable",
                "max_event_rows": self._max_event_rows,
                "column_rebind_count": len(self._query_elapsed_seconds),
                "schema_reverified_per_batch": True,
                "ordering_reverified_per_batch": True,
                "duplicate_logical_keys_rejected_per_batch": True,
                "capacity_reverified_per_batch": True,
                "producer_owned_device_batch_supported": True,
                "order_indexed_host_consumption_supported": True,
                "compiler_authored": True,
            },
            "backend_runtime_lifecycle": {
                "contract": "rtdl.sorted_host_i64x2_scan_lifecycle.private_candidate.v1",
                "compiler_owned": True,
                "query_count": len(self._query_elapsed_seconds),
                "gpu_kernel_launch_count": 0,
                "compiler_owned_eager_host_specialization_count": (
                    self._eager_specialization_count
                ),
                "compiler_owned_eager_host_specialization_seconds": (
                    self._eager_specialization_seconds
                ),
                "device_to_host_copy_is_explicit": True,
                "producer_owned_single_consume_batches": True,
                "sorted_payload_permutation_required": False,
            },
            # Keep the sealed owner private.  Public metadata must be a plain
            # JSON-serializable copy; exposing MappingProxyType here broke the
            # fresh-process evidence writer after an otherwise valid run.
            "last_event_batch_certificate": (
                json.loads(
                    json.dumps(
                        dict(self._last_batch_metadata),
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                )
                if self._last_batch_metadata is not None
                else None
            ),
            "timing": self.timing_metadata(),
            "closed": self._closed,
            "application_selected_backend": False,
            "raw_callback_accepted": False,
            "runtime_speedup_claimed": False,
        }

    def close(self) -> None:
        self._validate_integrity()
        if not self._closed:
            if self._active_producer_batch is not None:
                self._active_producer_batch.invalidate()
                self._active_producer_batch = None
            self._closed = True
            self._refresh_resource_seal()


def prepare_host_grouped_i64x2_count_sum_execution(
    planned,
    *,
    max_event_rows: int,
) -> PreparedHostGroupedI64x2CountSumExecution:
    return PreparedHostGroupedI64x2CountSumExecution(
        planned,
        max_event_rows=max_event_rows,
    )


def _aggregate_sorted_i64x2_dispatch(
    key0,
    key1,
    values,
    out0,
    out1,
    out_counts,
    out_sums,
    *,
    sum_field_nonnegative: bool,
):
    import numpy as np

    count = int(key0.shape[0])
    if count == 0:
        return 0, 0
    if _NUMBA_HOST_SCAN_AVAILABLE:
        # This is the same generic sorted i64x2 scan shape used by the strongest
        # established host reducer, with the Action contract's order and signed
        # overflow checks fused into that one pass.  The cached specialization
        # is shared by every application using this physical template.
        return _aggregate_sorted_i64x2_numba(
            key0,
            key1,
            values,
            out0,
            out1,
            out_counts,
            out_sums,
            bool(sum_field_nonnegative),
        )
    if sum_field_nonnegative and bool(np.any(values < 0)):
        return 0, 3
    descending = (key0[1:] < key0[:-1]) | (
        (key0[1:] == key0[:-1]) & (key1[1:] < key1[:-1])
    )
    if bool(np.any(descending)):
        return 0, 1
    starts = np.concatenate(
        (
            np.asarray([0], dtype=np.int64),
            np.flatnonzero((key0[1:] != key0[:-1]) | (key1[1:] != key1[:-1]))
            + 1,
        )
    )
    ends = np.concatenate((starts[1:], np.asarray([count], dtype=np.int64)))
    group_counts = ends - starts
    maxima = np.maximum.reduceat(values, starts)
    maximum = (1 << 63) - 1
    minimum = -(1 << 63)
    # This bound proves that no prefix in a group can overflow, so the fast
    # int64 reduce is exact. Only the rare unproved group takes the scalar
    # arbitrary-precision path; ordinary nonnegative count/sum workloads stay
    # entirely vectorized and incur no JIT startup.
    if sum_field_nonnegative:
        # Every prefix is bounded by the complete nonnegative group.  Integer
        # division gives a sufficient overflow proof without object arrays.
        safe = maxima <= (maximum // group_counts)
    else:
        minima = np.minimum.reduceat(values, starts)
        lower_bounds = minima.astype(object) * group_counts.astype(object)
        upper_bounds = maxima.astype(object) * group_counts.astype(object)
        safe = (lower_bounds >= minimum) & (upper_bounds <= maximum)
    sums = np.empty(starts.shape[0], dtype=np.int64)
    if bool(np.all(safe)):
        sums[:] = np.add.reduceat(values, starts, dtype=np.int64)
    else:
        fast = np.flatnonzero(safe)
        if fast.size:
            reduced = np.add.reduceat(values, starts, dtype=np.int64)
            sums[fast] = reduced[fast]
        for group in np.flatnonzero(~safe):
            running = 0
            for value in values[int(starts[group]) : int(ends[group])]:
                scalar = int(value)
                if (scalar > 0 and running > maximum - scalar) or (
                    scalar < 0 and running < minimum - scalar
                ):
                    return 0, 2
                running += scalar
            sums[group] = running
    output_count = int(starts.shape[0])
    out0[:output_count] = key0[starts]
    out1[:output_count] = key1[starts]
    out_counts[:output_count] = group_counts.astype(np.uint64, copy=False)
    out_sums[:output_count] = sums
    return output_count, 0


def _aggregate_order_indexed_i64x2_dispatch(
    key0,
    key1,
    values,
    order,
    out0,
    out1,
    out_counts,
    out_sums,
    *,
    sum_field_nonnegative: bool,
):
    if _NUMBA_HOST_SCAN_AVAILABLE:
        return _aggregate_order_indexed_i64x2_numba(
            key0,
            key1,
            values,
            order,
            out0,
            out1,
            out_counts,
            out_sums,
            bool(sum_field_nonnegative),
        )
    # The generic fallback preserves semantics even when the optimized
    # order-indexed Numba scan is unavailable.
    return _aggregate_sorted_i64x2_dispatch(
        key0[order],
        key1[order],
        values[order],
        out0,
        out1,
        out_counts,
        out_sums,
        sum_field_nonnegative=sum_field_nonnegative,
    )


def _fail(code: str, path: str, message: str) -> NoReturn:
    # The host template participates in the same closed Action placement error
    # surface as the device template, so compiler preflight remains uniform.
    from .action_numba_continuation import ActionPlacementIssue

    raise ActionPlacementError(ActionPlacementIssue(code, path, message))


__all__ = (
    "ACTION_HOST_CONTINUATION_VERSION",
    "HostGroupedI64x2CountSumProgram",
    "HostGroupedI64x2MaterializedBatch",
    "HostGroupedI64x2QueryResult",
    "HostI64x2ReductionRows",
    "AlignedI64x2CountSumProjection",
    "CompilerOwnedUnorderedI64x2DeviceBatch",
    "aligned_i64x2_count_sum_projection",
    "PreparedHostGroupedI64x2CountSumExecution",
    "compile_host_grouped_i64x2_count_sum",
    "execute_sorted_host_grouped_i64x2_count_sum",
    "materialize_sorted_host_grouped_i64x2_batch",
    "prepare_host_grouped_i64x2_count_sum_execution",
)

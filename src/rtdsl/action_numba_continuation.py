from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import hmac
import json
import math
import secrets
import time
from types import MappingProxyType
from typing import Mapping, NoReturn

from .action_interpreter import EmittedRelation, ReductionRelation, StateRelation, _finalize_emit
from .action_ir import (
    ActionBlock,
    ActionEmitSpec,
    ActionOp,
    ActionScalarKind,
    ActionScalarType,
    ActionSpec,
    ActionStateSpec,
    ActionStaticLoop,
    DeliveryEnforcement,
    ExtentKind,
    PhysicalDelivery,
    ReductionOperator,
    StateScope,
    TerminationProofKind,
    evaluate_capacity,
    verify_action_spec,
)
from .action_native_ordering import (
    GroupedI64x2NativeOrderContext,
    GroupedI64x2NativeOrderProbe,
)


ACTION_NUMBA_CONTINUATION_VERSION = "rtdl.action_numba_continuation.v1"
_SUPPORTED_OPCODES = {
    "load_event",
    "load_param",
    "const",
    "compare",
    "bool_and",
    "bool_or",
    "bool_not",
    "add",
    "sub",
    "mul",
    "min",
    "max",
    "select",
    "cast",
    "filter",
    "emit",
    "accept",
    "ignore",
}
_KERNEL_CACHE: dict[str, object] = {}
_CERTIFIED_QUERY_MIN_KERNELS: tuple[object, object] | None = None
_CERTIFIED_QUERY_MIN_GLOBAL_MAX_KERNELS: tuple[object, object] | None = None
_GROUPED_I64X2_COUNT_SUM_KERNEL: object | None = None
_GROUPED_I64X2_COUNT_SUM_KERNEL_CONSTRUCT_COUNT = 0
_GROUPED_I64X2_COUNT_SUM_KERNEL_LOOKUP_COUNT = 0
_GROUPED_I64X2_COUNT_SUM_KERNEL_LAUNCH_COUNT = 0
_GROUPED_I64X2_ORDER_INDEXED_COUNT_SUM_KERNEL: object | None = None
_GROUPED_I64X2_ORDER_INDEXED_COUNT_SUM_KERNEL_CONSTRUCT_COUNT = 0
_GROUPED_I64X2_ORDER_INDEXED_COUNT_SUM_KERNEL_LOOKUP_COUNT = 0
_GROUPED_I64X2_ORDER_INDEXED_COUNT_SUM_KERNEL_LAUNCH_COUNT = 0
_DEVICE_COLUMN_CERTIFICATE_KERNELS: tuple[object, object, object] | None = None
_GROUPED_DEVICE_BATCH_SEAL_KEY = secrets.token_bytes(32)
_GROUPED_DEVICE_RESULT_SEAL_KEY = secrets.token_bytes(32)
_GROUPED_DEVICE_EAGER_WRAPPER_SEAL_KEY = secrets.token_bytes(32)
_GROUPED_DEVICE_WORKSPACE_SEAL_KEY = secrets.token_bytes(32)

CERTIFIED_QUERY_MIN_ORDERING = "query-grouped-canonical-f32-candidate-order-v1"


@dataclass(frozen=True)
class ActionPlacementIssue:
    code: str
    path: str
    message: str


class ActionPlacementError(ValueError):
    def __init__(self, issue: ActionPlacementIssue) -> None:
        self.issue = issue
        super().__init__(f"Action placement failed: {issue.code}@{issue.path}: {issue.message}")


@dataclass(frozen=True)
class NumbaActionProgram:
    spec: ActionSpec
    kernel_source: str
    kernel_code_digest: str
    event_fields: tuple[str, ...]
    parameter_fields: tuple[str, ...]
    emit: ActionEmitSpec
    delivery_proof_reference: str
    placement_contract: str = "verified_action_ir_filter_bounded_emit_proven_single_v1"

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract_version": ACTION_NUMBA_CONTINUATION_VERSION,
            "semantic_digest": self.spec.semantic_digest,
            "event_fields": list(self.event_fields),
            "parameter_fields": list(self.parameter_fields),
            "kernel_code_digest": self.kernel_code_digest,
            "placement_contract": self.placement_contract,
            "delivery_proof_reference": self.delivery_proof_reference,
            "delivery_proof_discharged_by_placement": True,
            "action_name_used_for_dispatch": False,
            "user_numba_kernel_accepted": False,
            "supported_effect_subset": ["filter", "bounded_emit"],
            "unsupported_effects_fail_closed": True,
            "physical_output_order": "atomic_append_unspecified",
            "semantic_output_projection": self.emit.order_kind.value,
        }


@dataclass
class PreparedNumbaActionColumns:
    program: NumbaActionProgram
    event_columns: dict[str, object]
    parameters: dict[str, object]
    row_count: int
    owns_event_columns: bool
    host_to_device_copy_used: bool
    active_results: int = 0
    closed: bool = False

    def to_metadata(self) -> dict[str, object]:
        return self.program.to_metadata() | {
            "row_count": self.row_count,
            "input_columns_device_resident": True,
            "host_to_device_copy_used": self.host_to_device_copy_used,
            "owns_event_columns": self.owns_event_columns,
            "materializes_host_rows_for_bridge": False,
            "lifetime_owner_required_through_synchronize": True,
            "active_results": self.active_results,
            "closed": self.closed,
        }

    def close(self) -> None:
        if self.active_results:
            _fail(
                "input_owner_still_in_use",
                "prepared.active_results",
                "close device results before closing prepared input columns",
            )
        self.event_columns.clear()
        self.parameters.clear()
        self.closed = True


@dataclass
class NumbaActionDeviceResult:
    program: NumbaActionProgram
    output_columns: dict[str, object]
    output_count: object
    error_flag: object
    capacity: int
    input_owner: PreparedNumbaActionColumns
    synchronized: bool = False
    host_projection_used: bool = False
    closed: bool = False

    def synchronize(self) -> None:
        self._require_open()
        cuda, _ = _import_numba_stack()
        cuda.synchronize()
        self.synchronized = True

    def to_host_relation(self) -> EmittedRelation:
        self._require_open()
        if not self.synchronized:
            self.synchronize()
        error = int(self.error_flag.copy_to_host()[0])
        if error == 1:
            _fail("nonfinite_runtime_value", "device.error_flag", "NaN or infinity rejected")
        if error == 2:
            _fail("emit_capacity_exceeded", "device.error_flag", "bounded emit overflowed")
        if error == 3:
            _fail("nonnegative_field_violation", "device.error_flag", "negative runtime field rejected")
        if error:
            _fail("unknown_device_error", "device.error_flag", str(error))
        count = int(self.output_count.copy_to_host()[0])
        if count > self.capacity:
            _fail("emit_capacity_exceeded", "device.output_count", str(count))
        host_columns = {
            field.name: self.output_columns[field.name].copy_to_host()[:count]
            for field in self.program.emit.record_type.fields
        }
        rows = [
            tuple(_python_scalar(host_columns[field.name][index]) for field in self.program.emit.record_type.fields)
            for index in range(count)
        ]
        self.host_projection_used = True
        return _finalize_emit(self.program.emit, rows)

    def to_metadata(self) -> dict[str, object]:
        return self.input_owner.to_metadata() | {
            "output_columns_device_resident": True,
            "device_output_owner_live": not self.closed,
            "capacity": self.capacity,
            "synchronized": self.synchronized,
            "host_projection_used": self.host_projection_used,
            "host_projection_is_explicit_diagnostic_or_consumer_boundary": True,
        }

    def close(self) -> None:
        if self.closed:
            return
        if not self.synchronized:
            self.synchronize()
        self.output_columns.clear()
        self.output_count = None
        self.error_flag = None
        self.input_owner.active_results -= 1
        self.closed = True

    def _require_open(self) -> None:
        if self.closed:
            _fail("device_result_closed", "result", "device result owner has been closed")
        if self.input_owner.closed:
            _fail("input_owner_closed", "input_owner", "input columns closed before completion")


@dataclass(frozen=True)
class NumbaGroupedI64x2CountSumProgram:
    spec: ActionSpec
    event_fields: tuple[str, ...]
    key_fields: tuple[str, str]
    sum_field: str
    count_reduction_name: str
    sum_reduction_name: str
    delivery_proof_reference: str
    parameter_fields: tuple[str, ...] = ()
    placement_contract: str = "verified_action_ir_grouped_i64x2_count_sum_v1"

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract_version": ACTION_NUMBA_CONTINUATION_VERSION,
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
            "user_numba_kernel_accepted": False,
            "supported_effect_subset": ["keyed_reduce"],
            "key_schema": ["i64", "i64"],
            "reduction_schema": ["count_u64", "sum_i64"],
            "input_order_contract": (
                "lexicographic_nondecreasing_i64x2_or_compiler_owned_order_indices"
            ),
            "input_order_verified_on_device": True,
            "order_indexed_grouped_reduction_supported": True,
            "physical_output_order": "atomic_group_append_unspecified",
            "semantic_output_projection": "canonical_key_order",
            "signed_overflow_policy": "fail_closed",
            "unsupported_effects_fail_closed": True,
        }


def _device_resource_token(value) -> tuple[object, ...]:
    interface = getattr(value, "__cuda_array_interface__", {})
    pointer = interface.get("data", (None,))[0] if isinstance(interface, Mapping) else None
    return (
        id(value),
        type(value).__module__,
        type(value).__qualname__,
        tuple(int(item) for item in getattr(value, "shape", ())),
        str(getattr(value, "dtype", None)),
        int(pointer) if pointer is not None else None,
    )


def _freeze_certificate_metadata(value):
    if isinstance(value, Mapping):
        frozen = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("device certificate metadata keys must be strings")
            frozen[key] = _freeze_certificate_metadata(item)
        return MappingProxyType(frozen)
    if isinstance(value, (tuple, list)):
        return tuple(_freeze_certificate_metadata(item) for item in value)
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    raise TypeError(
        "device certificate metadata must contain only JSON-compatible values"
    )


def _plain_certificate_metadata(value):
    if isinstance(value, Mapping):
        return {
            key: _plain_certificate_metadata(item)
            for key, item in value.items()
        }
    if isinstance(value, tuple):
        return [_plain_certificate_metadata(item) for item in value]
    return value


def _certificate_metadata_digest(value) -> str | None:
    if value is None:
        return None
    encoded = json.dumps(
        _plain_certificate_metadata(value),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class PreparedGroupedI64x2DeviceWorkspace:
    """Prepared-lifetime owner for compiler-private grouped device resources.

    Producer-visible arrays are deliberately excluded. Only the detached
    completion snapshot, native-order workspace, checked-reducer workspace,
    and their fixed status words live across query generations.
    """

    def __init__(self, *, owner_identity_digest: str, max_row_count: int) -> None:
        if (
            not isinstance(owner_identity_digest, str)
            or len(owner_identity_digest) != 64
            or any(
                character not in "0123456789abcdef"
                for character in owner_identity_digest
            )
            or not isinstance(max_row_count, int)
            or isinstance(max_row_count, bool)
            or max_row_count < 0
        ):
            _fail(
                "prepared_private_workspace_identity_invalid",
                "private_workspace",
                "owner digest or maximum row count is invalid",
            )
        self._owner_identity_digest = owner_identity_digest
        self._max_row_count = max_row_count
        self._capacity = 0
        self._allocation_generation = 0
        self._active_ordinal: int | None = None
        self._active_generation_digest: str | None = None
        self._active_row_count: int | None = None
        self._active_prepared = None
        self._active_result = None
        self._active_snapshot_views: tuple[object, object, object] | None = None
        self._active_order_view = None
        self._active_output_views: tuple[object, ...] | None = None
        self._snapshot_key0 = None
        self._snapshot_key1 = None
        self._snapshot_value = None
        self._order = None
        self._sort_key0 = None
        self._sort_key1 = None
        self._zero_distance = None
        self._output_key0 = None
        self._output_key1 = None
        self._output_counts = None
        self._output_sums = None
        self._output_count = None
        self._error_flag = None
        self._permutation_seen = None
        self._host_zero_i64 = None
        self._host_zero_i32 = None
        self._closed = False
        self._physical_identity_digest = self._compute_physical_identity_digest()

    @property
    def active_generation_digest(self) -> str:
        self._require_active()
        assert self._active_generation_digest is not None
        return self._active_generation_digest

    @property
    def capacity(self) -> int:
        return self._capacity

    def begin_query(
        self,
        *,
        owner_identity_digest: str,
        query_ordinal: int,
    ) -> None:
        if self._closed:
            _fail(
                "prepared_private_workspace_closed",
                "private_workspace",
                "workspace is closed",
            )
        if (
            owner_identity_digest != self._owner_identity_digest
            or not isinstance(query_ordinal, int)
            or isinstance(query_ordinal, bool)
            or query_ordinal < 0
        ):
            _fail(
                "prepared_private_workspace_owner_or_ordinal_mismatch",
                "private_workspace",
                f"query_ordinal={query_ordinal!r}",
            )
        if self._active_ordinal is not None:
            _fail(
                "prepared_private_workspace_generation_active",
                "private_workspace",
                f"active_ordinal={self._active_ordinal}",
            )
        self._active_ordinal = query_ordinal
        self._active_row_count = None
        self._active_generation_digest = self._issue_generation_digest(
            query_ordinal=query_ordinal,
            row_count=None,
        )

    def capture_completion_snapshot(
        self,
        *,
        owner_identity_digest: str,
        query_ordinal: int,
        row_count: int,
        key0_source,
        key1_source,
        value_source,
    ) -> tuple[dict[str, object], dict[str, object]]:
        self._require_generation(
            owner_identity_digest=owner_identity_digest,
            query_ordinal=query_ordinal,
        )
        if (
            not isinstance(row_count, int)
            or isinstance(row_count, bool)
            or row_count < 0
            or row_count > self._max_row_count
        ):
            _fail(
                "prepared_private_workspace_row_count_invalid",
                "private_workspace.row_count",
                f"rows={row_count}; max={self._max_row_count}",
            )
        allocation = self._ensure_capacity(row_count)
        copy_started = time.perf_counter()
        try:
            assert self._snapshot_key0 is not None
            assert self._snapshot_key1 is not None
            assert self._snapshot_value is not None
            key0_view = self._snapshot_key0[:row_count]
            key1_view = self._snapshot_key1[:row_count]
            value_view = self._snapshot_value[:row_count]
            key0_view.copy_to_device(key0_source[:row_count])
            key1_view.copy_to_device(key1_source[:row_count])
            value_view.copy_to_device(value_source[:row_count])
            cuda, _ = _import_numba_stack()
            cuda.synchronize()
        except Exception as exc:
            self.abort_query(
                owner_identity_digest=owner_identity_digest,
                query_ordinal=query_ordinal,
            )
            _fail(
                "prepared_private_workspace_snapshot_failed",
                "private_workspace.snapshot",
                str(exc),
            )
        copy_seconds = time.perf_counter() - copy_started
        self._active_row_count = row_count
        self._active_snapshot_views = (key0_view, key1_view, value_view)
        self._active_generation_digest = self._issue_generation_digest(
            query_ordinal=query_ordinal,
            row_count=row_count,
        )
        metadata = {
            "contract": (
                "rtdl.prepared_grouped_i64x2_private_workspace_generation.v1"
            ),
            "query_ordinal": query_ordinal,
            "row_count": row_count,
            "workspace_capacity": self._capacity,
            "workspace_allocation_generation": self._allocation_generation,
            "workspace_generation_digest": self._active_generation_digest,
            "workspace_reused_without_growth": not bool(allocation["grew"]),
            "workspace_grew_in_registered_query": bool(allocation["grew"]),
            "snapshot_workspace_allocation_seconds": float(
                allocation["snapshot_seconds"]
            ),
            "order_workspace_allocation_seconds": float(
                allocation["order_seconds"]
            ),
            "reducer_workspace_allocation_seconds": float(
                allocation["reducer_seconds"]
            ),
            "total_private_workspace_allocation_seconds": float(
                allocation["total_seconds"]
            ),
            "completion_device_to_device_seconds": float(copy_seconds),
            "producer_visible_storage_reused": False,
            "compiler_private_storage_reused": not bool(allocation["grew"]),
            "allocation_charged_to_registered_query": True,
        }
        return {
            "key0": key0_view,
            "key1": key1_view,
            "value": value_view,
        }, metadata

    def capture_canonical_host_snapshot(
        self,
        *,
        owner_identity_digest: str,
        query_ordinal: int,
        row_count: int,
        key0_source,
        key1_source,
        value_source,
    ) -> tuple[dict[str, object], dict[str, object]]:
        """Copy a compiler-verified canonical host batch into reusable storage.

        Unlike ``capture_completion_snapshot``, this boundary is host-to-device
        and does not claim producer-device lease revocation.  The three copied
        columns are the only columns read by the checked grouped reducer; the
        logical event column is validated before this method is called and is
        not redundantly transferred to the device.
        """

        self._require_generation(
            owner_identity_digest=owner_identity_digest,
            query_ordinal=query_ordinal,
        )
        if (
            not isinstance(row_count, int)
            or isinstance(row_count, bool)
            or row_count < 0
            or row_count > self._max_row_count
        ):
            _fail(
                "prepared_private_workspace_row_count_invalid",
                "private_workspace.row_count",
                f"rows={row_count}; max={self._max_row_count}",
            )
        allocation = self._ensure_capacity(row_count)
        copy_started = time.perf_counter()
        try:
            assert self._snapshot_key0 is not None
            assert self._snapshot_key1 is not None
            assert self._snapshot_value is not None
            key0_view = self._snapshot_key0[:row_count]
            key1_view = self._snapshot_key1[:row_count]
            value_view = self._snapshot_value[:row_count]
            key0_view.copy_to_device(key0_source[:row_count])
            key1_view.copy_to_device(key1_source[:row_count])
            value_view.copy_to_device(value_source[:row_count])
            cuda, _ = _import_numba_stack()
            cuda.synchronize()
        except Exception as exc:
            self.abort_query(
                owner_identity_digest=owner_identity_digest,
                query_ordinal=query_ordinal,
            )
            _fail(
                "prepared_private_workspace_host_snapshot_failed",
                "private_workspace.snapshot",
                str(exc),
            )
        copy_seconds = time.perf_counter() - copy_started
        self._active_row_count = row_count
        self._active_snapshot_views = (key0_view, key1_view, value_view)
        self._active_order_view = None
        self._active_generation_digest = self._issue_generation_digest(
            query_ordinal=query_ordinal,
            row_count=row_count,
        )
        metadata = {
            "contract": (
                "rtdl.prepared_grouped_i64x2_canonical_host_workspace_generation.v1"
            ),
            "query_ordinal": query_ordinal,
            "row_count": row_count,
            "workspace_capacity": self._capacity,
            "workspace_allocation_generation": self._allocation_generation,
            "workspace_generation_digest": self._active_generation_digest,
            "workspace_reused_without_growth": not bool(allocation["grew"]),
            "workspace_grew_in_registered_query": bool(allocation["grew"]),
            "total_private_workspace_allocation_seconds": float(
                allocation["total_seconds"]),
            "canonical_host_to_device_seconds": float(copy_seconds),
            "host_to_device_copy_used": True,
            "device_to_device_copy_used": False,
            "producer_visible_storage_reused": False,
            "compiler_private_storage_reused": not bool(allocation["grew"]),
            "allocation_charged_to_registered_query": True,
        }
        return {
            "key0": key0_view,
            "key1": key1_view,
            "value": value_view,
        }, metadata

    def order_resources(
        self,
        *,
        generation_digest: str,
        row_count: int,
    ) -> tuple[object, object, object, object]:
        self._require_bound_generation(generation_digest, row_count)
        assert self._order is not None
        assert self._sort_key0 is not None
        assert self._sort_key1 is not None
        assert self._zero_distance is not None
        order = self._order[:row_count]
        sort_key0 = self._sort_key0[:row_count]
        sort_key1 = self._sort_key1[:row_count]
        zero_distance = self._zero_distance[:row_count]
        self._active_order_view = order
        return order, sort_key0, sort_key1, zero_distance

    def reducer_resources(
        self,
        *,
        generation_digest: str,
        row_count: int,
    ) -> tuple[tuple[object, ...], float]:
        self._require_bound_generation(generation_digest, row_count)
        if self._active_result is not None:
            _fail(
                "prepared_private_workspace_result_active",
                "private_workspace",
                "close the current result before another reducer launch",
            )
        assert self._output_key0 is not None
        assert self._output_key1 is not None
        assert self._output_counts is not None
        assert self._output_sums is not None
        assert self._output_count is not None
        assert self._error_flag is not None
        assert self._permutation_seen is not None
        assert self._host_zero_i64 is not None
        assert self._host_zero_i32 is not None
        reset_started = time.perf_counter()
        self._output_count.copy_to_device(self._host_zero_i64[:1])
        self._error_flag.copy_to_device(self._host_zero_i32[:1])
        permutation = self._permutation_seen[:row_count]
        if row_count:
            permutation.copy_to_device(self._host_zero_i32[:row_count])
        reset_seconds = time.perf_counter() - reset_started
        resources = (
            self._output_key0[:row_count],
            self._output_key1[:row_count],
            self._output_counts[:row_count],
            self._output_sums[:row_count],
            self._output_count,
            self._error_flag,
            permutation,
        )
        self._active_output_views = resources
        return resources, float(reset_seconds)

    def register_prepared(self, prepared, *, generation_digest: str) -> None:
        self._require_bound_generation(generation_digest, prepared.row_count)
        if self._active_prepared is not None:
            _fail(
                "prepared_private_workspace_prepared_active",
                "private_workspace",
                "one prepared binding already owns this generation",
            )
        snapshot = self._active_snapshot_views
        if (
            snapshot is None
            or prepared._event_columns.get(prepared.program.key_fields[0])
            is not snapshot[0]
            or prepared._event_columns.get(prepared.program.key_fields[1])
            is not snapshot[1]
            or prepared._event_columns.get(prepared.program.sum_field)
            is not snapshot[2]
            or prepared._order_indices is not self._active_order_view
        ):
            _fail(
                "prepared_private_workspace_binding_substituted",
                "private_workspace.prepared",
                "prepared columns or order view differ from the active generation",
            )
        self._active_prepared = prepared

    def validate_prepared(self, prepared, *, generation_digest: str) -> None:
        self._require_bound_generation(generation_digest, prepared._row_count)
        if prepared is not self._active_prepared:
            _fail(
                "prepared_private_workspace_binding_substituted",
                "private_workspace.prepared",
                "prepared owner differs from the active generation",
            )
        if (
            prepared._program is not prepared._sealed_program_ref
            or prepared._event_columns is not prepared._sealed_event_columns_ref
            or prepared._order_indices is not self._active_order_view
            or any(
                prepared._event_columns.get(name) is not value
                for name, value in prepared._sealed_event_column_refs
            )
        ):
            _fail(
                "prepared_private_workspace_binding_changed",
                "private_workspace.prepared",
                "active generation resource references changed",
            )

    def release_prepared(self, prepared, *, generation_digest: str) -> None:
        self.validate_prepared(prepared, generation_digest=generation_digest)
        if self._active_result is not None:
            _fail(
                "prepared_private_workspace_result_active",
                "private_workspace",
                "close the active result before releasing prepared inputs",
            )
        self._active_prepared = None

    def register_result(self, result, *, generation_digest: str) -> None:
        self._require_bound_generation(generation_digest, result._capacity)
        if (
            self._active_prepared is None
            or self._active_result is not None
            or self._active_output_views is None
        ):
            _fail(
                "prepared_private_workspace_result_registration_invalid",
                "private_workspace.result",
                "prepared owner or output workspace is not uniquely active",
            )
        expected = self._active_output_views
        actual = (
            result._key0,
            result._key1,
            result._counts,
            result._sums,
            result._output_count,
            result._error_flag,
            result._permutation_seen,
        )
        if any(current is not sealed for current, sealed in zip(actual, expected)):
            _fail(
                "prepared_private_workspace_result_substituted",
                "private_workspace.result",
                "result arrays differ from the active generation",
            )
        self._active_result = result

    def validate_result(self, result, *, generation_digest: str) -> None:
        self._require_bound_generation(generation_digest, result._capacity)
        if (
            result is not self._active_result
            or result._input_owner is not self._active_prepared
            or self._active_output_views is None
        ):
            _fail(
                "prepared_private_workspace_result_substituted",
                "private_workspace.result",
                "result owner differs from the active generation",
            )
        actual = (
            result._key0,
            result._key1,
            result._counts,
            result._sums,
            result._output_count,
            result._error_flag,
            result._permutation_seen,
        )
        if any(
            current is not sealed
            for current, sealed in zip(actual, self._active_output_views)
        ):
            _fail(
                "prepared_private_workspace_result_binding_changed",
                "private_workspace.result",
                "result resource references changed",
            )

    def release_result(self, result, *, generation_digest: str) -> None:
        self.validate_result(result, generation_digest=generation_digest)
        self._active_result = None
        self._active_output_views = None

    def finish_query(
        self,
        *,
        owner_identity_digest: str,
        query_ordinal: int,
        generation_digest: str,
    ) -> None:
        self._require_generation(
            owner_identity_digest=owner_identity_digest,
            query_ordinal=query_ordinal,
        )
        if generation_digest != self._active_generation_digest:
            _fail(
                "prepared_private_workspace_generation_mismatch",
                "private_workspace.generation_digest",
                generation_digest,
            )
        if self._active_prepared is not None or self._active_result is not None:
            _fail(
                "prepared_private_workspace_resources_still_active",
                "private_workspace",
                "prepared or result resource survived query close",
            )
        self._active_snapshot_views = None
        self._active_order_view = None
        self._active_output_views = None
        self._active_row_count = None
        self._active_generation_digest = None
        self._active_ordinal = None

    def abort_query(
        self,
        *,
        owner_identity_digest: str,
        query_ordinal: int,
    ) -> None:
        if self._active_ordinal is None:
            return
        self._require_generation(
            owner_identity_digest=owner_identity_digest,
            query_ordinal=query_ordinal,
        )
        self._active_prepared = None
        self._active_result = None
        self._active_snapshot_views = None
        self._active_order_view = None
        self._active_output_views = None
        self._active_row_count = None
        self._active_generation_digest = None
        self._active_ordinal = None

    def close(self) -> None:
        if self._closed:
            return
        if self._active_ordinal is not None:
            _fail(
                "prepared_private_workspace_generation_active",
                "private_workspace",
                f"active_ordinal={self._active_ordinal}",
            )
        for name in (
            "_snapshot_key0",
            "_snapshot_key1",
            "_snapshot_value",
            "_order",
            "_sort_key0",
            "_sort_key1",
            "_zero_distance",
            "_output_key0",
            "_output_key1",
            "_output_counts",
            "_output_sums",
            "_output_count",
            "_error_flag",
            "_permutation_seen",
            "_host_zero_i64",
            "_host_zero_i32",
        ):
            setattr(self, name, None)
        self._capacity = 0
        self._closed = True
        self._physical_identity_digest = self._compute_physical_identity_digest()

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": "rtdl.prepared_grouped_i64x2_private_workspace.v1",
            "owner_identity_digest": self._owner_identity_digest,
            "max_row_count": self._max_row_count,
            "capacity": self._capacity,
            "allocation_generation": self._allocation_generation,
            "physical_identity_digest": self._physical_identity_digest,
            "active_query_ordinal": self._active_ordinal,
            "active_generation_digest": self._active_generation_digest,
            "producer_visible_storage_reused": False,
            "compiler_private_storage_reusable": True,
            "closed": self._closed,
        }

    def _ensure_capacity(self, row_count: int) -> dict[str, object]:
        required = max(1, row_count)
        if self._capacity >= required:
            return {
                "grew": False,
                "snapshot_seconds": 0.0,
                "order_seconds": 0.0,
                "reducer_seconds": 0.0,
                "total_seconds": 0.0,
            }
        if required > max(1, self._max_row_count):
            _fail(
                "prepared_private_workspace_capacity_exceeded",
                "private_workspace.capacity",
                f"required={required}; max={self._max_row_count}",
            )
        cuda, np = _import_numba_stack()
        total_started = time.perf_counter()
        snapshot_started = time.perf_counter()
        snapshot_key0 = cuda.device_array(required, dtype=np.int64)
        snapshot_key1 = cuda.device_array(required, dtype=np.int64)
        snapshot_value = cuda.device_array(required, dtype=np.int64)
        snapshot_seconds = time.perf_counter() - snapshot_started
        order_started = time.perf_counter()
        order = cuda.device_array(required, dtype=np.int64)
        sort_key0 = cuda.device_array(required, dtype=np.int64)
        sort_key1 = cuda.device_array(required, dtype=np.int64)
        zero_distance = cuda.device_array(required, dtype=np.float64)
        order_seconds = time.perf_counter() - order_started
        reducer_started = time.perf_counter()
        output_key0 = cuda.device_array(required, dtype=np.int64)
        output_key1 = cuda.device_array(required, dtype=np.int64)
        output_counts = cuda.device_array(required, dtype=np.uint64)
        output_sums = cuda.device_array(required, dtype=np.int64)
        output_count = cuda.device_array(1, dtype=np.int64)
        error_flag = cuda.device_array(1, dtype=np.int32)
        permutation_seen = cuda.device_array(required, dtype=np.int32)
        host_zero_i64 = np.zeros(1, dtype=np.int64)
        host_zero_i32 = np.zeros(required, dtype=np.int32)
        reducer_seconds = time.perf_counter() - reducer_started
        self._snapshot_key0 = snapshot_key0
        self._snapshot_key1 = snapshot_key1
        self._snapshot_value = snapshot_value
        self._order = order
        self._sort_key0 = sort_key0
        self._sort_key1 = sort_key1
        self._zero_distance = zero_distance
        self._output_key0 = output_key0
        self._output_key1 = output_key1
        self._output_counts = output_counts
        self._output_sums = output_sums
        self._output_count = output_count
        self._error_flag = error_flag
        self._permutation_seen = permutation_seen
        self._host_zero_i64 = host_zero_i64
        self._host_zero_i32 = host_zero_i32
        self._capacity = required
        self._allocation_generation += 1
        self._physical_identity_digest = self._compute_physical_identity_digest()
        return {
            "grew": True,
            "snapshot_seconds": float(snapshot_seconds),
            "order_seconds": float(order_seconds),
            "reducer_seconds": float(reducer_seconds),
            "total_seconds": float(time.perf_counter() - total_started),
        }

    def _compute_physical_identity_digest(self) -> str:
        resources = (
            self._snapshot_key0,
            self._snapshot_key1,
            self._snapshot_value,
            self._order,
            self._sort_key0,
            self._sort_key1,
            self._zero_distance,
            self._output_key0,
            self._output_key1,
            self._output_counts,
            self._output_sums,
            self._output_count,
            self._error_flag,
            self._permutation_seen,
        )
        payload = (
            "rtdl.prepared_grouped_i64x2_private_workspace.physical.v1",
            self._owner_identity_digest,
            self._max_row_count,
            self._capacity,
            self._allocation_generation,
            tuple(
                None if value is None else _device_resource_token(value)
                for value in resources
            ),
        )
        return hashlib.sha256(repr(payload).encode("utf-8")).hexdigest()

    def _issue_generation_digest(
        self,
        *,
        query_ordinal: int,
        row_count: int | None,
    ) -> str:
        payload = repr(
            (
                "rtdl.prepared_grouped_i64x2_private_workspace.generation.v1",
                self._owner_identity_digest,
                query_ordinal,
                row_count,
                self._capacity,
                self._allocation_generation,
                self._physical_identity_digest,
            )
        ).encode("utf-8")
        return hmac.new(
            _GROUPED_DEVICE_WORKSPACE_SEAL_KEY,
            payload,
            hashlib.sha256,
        ).hexdigest()

    def _require_active(self) -> None:
        if (
            self._closed
            or self._active_ordinal is None
            or self._active_generation_digest is None
        ):
            _fail(
                "prepared_private_workspace_generation_inactive",
                "private_workspace",
                "no active query generation",
            )

    def _require_generation(
        self,
        *,
        owner_identity_digest: str,
        query_ordinal: int,
    ) -> None:
        self._require_active()
        if (
            owner_identity_digest != self._owner_identity_digest
            or query_ordinal != self._active_ordinal
        ):
            _fail(
                "prepared_private_workspace_owner_or_ordinal_mismatch",
                "private_workspace",
                (
                    f"expected={self._owner_identity_digest}:{self._active_ordinal}; "
                    f"actual={owner_identity_digest}:{query_ordinal}"
                ),
            )

    def _require_bound_generation(
        self,
        generation_digest: str,
        row_count: int,
    ) -> None:
        self._require_active()
        if (
            generation_digest != self._active_generation_digest
            or row_count != self._active_row_count
        ):
            _fail(
                "prepared_private_workspace_generation_mismatch",
                "private_workspace",
                (
                    f"expected_digest={self._active_generation_digest}; "
                    f"actual_digest={generation_digest}; "
                    f"expected_rows={self._active_row_count}; actual_rows={row_count}"
                ),
            )


class PreparedNumbaGroupedI64x2CountSumColumns:
    """Opaque compiler-owned input resources for one checked grouped batch."""

    def __init__(
        self,
        *,
        program: NumbaGroupedI64x2CountSumProgram,
        event_columns: Mapping[str, object],
        row_count: int,
        owns_event_columns: bool,
        host_to_device_copy_used: bool,
        device_to_device_copy_used: bool = False,
        device_certificate_metadata: Mapping[str, object] | None = None,
        order_indices: object | None = None,
        private_workspace: PreparedGroupedI64x2DeviceWorkspace | None = None,
        workspace_generation_digest: str | None = None,
    ) -> None:
        raw_columns = dict(event_columns)
        self._program = program
        self._event_columns = MappingProxyType(raw_columns)
        self._row_count = int(row_count)
        self._owns_event_columns = bool(owns_event_columns)
        self._host_to_device_copy_used = bool(host_to_device_copy_used)
        self._device_to_device_copy_used = bool(device_to_device_copy_used)
        self._device_certificate_metadata = (
            _freeze_certificate_metadata(dict(device_certificate_metadata))
            if device_certificate_metadata is not None
            else None
        )
        self._order_indices = order_indices
        self._private_workspace = private_workspace
        self._workspace_generation_digest = workspace_generation_digest
        self._active_result_ids: set[int] = set()
        self._closed = False
        self._sealed_program_ref = program
        self._sealed_event_columns_ref = self._event_columns
        self._sealed_event_column_refs = tuple(
            (name, raw_columns[name]) for name in sorted(raw_columns)
        )
        self._sealed_order_indices_ref = order_indices
        self._compiler_seal = self._expected_compiler_seal()
        if private_workspace is not None:
            if (
                type(private_workspace) is not PreparedGroupedI64x2DeviceWorkspace
                or not isinstance(workspace_generation_digest, str)
            ):
                _fail(
                    "prepared_private_workspace_binding_invalid",
                    "prepared.private_workspace",
                    type(private_workspace).__name__,
                )
            private_workspace.register_prepared(
                self,
                generation_digest=workspace_generation_digest,
            )

    @property
    def program(self) -> NumbaGroupedI64x2CountSumProgram:
        return self._program

    @property
    def row_count(self) -> int:
        return self._row_count

    @property
    def owns_event_columns(self) -> bool:
        return self._owns_event_columns

    @property
    def host_to_device_copy_used(self) -> bool:
        return self._host_to_device_copy_used

    @property
    def device_to_device_copy_used(self) -> bool:
        return self._device_to_device_copy_used

    @property
    def device_certificate_metadata(self) -> Mapping[str, object] | None:
        return self._device_certificate_metadata

    @property
    def active_results(self) -> int:
        return len(self._active_result_ids)

    @property
    def closed(self) -> bool:
        return self._closed

    def _column(self, name: str):
        self.validate_integrity()
        return self._event_columns[name]

    def _execution_order_indices(self):
        self.validate_integrity()
        return self._order_indices

    def _register_result(self, result) -> None:
        self.validate_integrity()
        token = id(result)
        if token in self._active_result_ids:
            _fail("duplicate_device_result_registration", "result", str(token))
        self._active_result_ids.add(token)

    def _release_result(self, result) -> None:
        self.validate_integrity()
        token = id(result)
        if token not in self._active_result_ids:
            _fail("unowned_device_result_release", "result", str(token))
        self._active_result_ids.remove(token)

    def _seal_payload(self) -> bytes:
        return repr(
            (
                "rtdl.numba_grouped_i64x2_prepared_batch.seal.v2",
                id(self._program),
                type(self._program).__module__,
                type(self._program).__qualname__,
                self._program.spec.semantic_digest,
                id(self._event_columns),
                tuple(
                    (name, _device_resource_token(value))
                    for name, value in sorted(self._event_columns.items())
                ),
                self._row_count,
                self._owns_event_columns,
                self._host_to_device_copy_used,
                self._device_to_device_copy_used,
                (
                    _device_resource_token(self._order_indices)
                    if self._order_indices is not None
                    else None
                ),
                _certificate_metadata_digest(self._device_certificate_metadata),
            )
        ).encode("utf-8")

    def _expected_compiler_seal(self) -> str:
        return hmac.new(
            _GROUPED_DEVICE_BATCH_SEAL_KEY,
            self._seal_payload(),
            hashlib.sha256,
        ).hexdigest()

    def validate_integrity(self) -> None:
        if type(self) is not PreparedNumbaGroupedI64x2CountSumColumns:
            _fail("prepared_columns_exact_type_required", "prepared", type(self).__name__)
        if self._closed:
            _fail("prepared_columns_closed", "prepared", "prepared input owner has been closed")
        if (
            self._program is not self._sealed_program_ref
            or self._event_columns is not self._sealed_event_columns_ref
            or any(
                self._event_columns.get(name) is not value
                for name, value in self._sealed_event_column_refs
            )
            or self._order_indices is not self._sealed_order_indices_ref
        ):
            _fail(
                "prepared_columns_resource_binding_changed",
                "prepared",
                "program, columns, or order-index owner changed after compiler preparation",
            )
        if self._private_workspace is not None:
            self._private_workspace.validate_prepared(
                self,
                generation_digest=str(self._workspace_generation_digest),
            )
            return
        if self._device_to_device_copy_used and self._order_indices is None:
            _fail(
                "prepared_order_indexed_mode_stripped",
                "prepared.order_indices",
                "device-resident binding requires the checked order-indexed kernel",
            )
        if not hmac.compare_digest(
            self._compiler_seal,
            self._expected_compiler_seal(),
        ):
            _fail(
                "prepared_columns_compiler_seal_invalid",
                "prepared._compiler_seal",
                "prepared grouped batch identity or certificate changed after issuance",
            )

    def to_metadata(self) -> dict[str, object]:
        if not self._closed:
            self.validate_integrity()
        return self._program.to_metadata() | {
            "row_count": self._row_count,
            "input_columns_device_resident": True,
            "host_to_device_copy_used": self._host_to_device_copy_used,
            "device_to_device_copy_used": self._device_to_device_copy_used,
            "order_indexed_execution": self._order_indices is not None,
            "permutation_validation_fused_into_checked_reduction": (
                self._order_indices is not None
            ),
            "owns_event_columns": self._owns_event_columns,
            "compiler_owned_device_resources_are_opaque": True,
            "materializes_host_rows_for_bridge": False,
            "lifetime_owner_required_through_synchronize": True,
            "active_results": len(self._active_result_ids),
            "closed": self._closed,
            "device_column_certificate": (
                _plain_certificate_metadata(self._device_certificate_metadata)
                if self._device_certificate_metadata is not None
                else None
            ),
            "device_column_certificate_canonical_digest": (
                _certificate_metadata_digest(self._device_certificate_metadata)
            ),
        }

    def close(self) -> None:
        if self._closed:
            return
        self.validate_integrity()
        if self._active_result_ids:
            _fail(
                "input_owner_still_in_use",
                "prepared.active_results",
                "close device results before closing prepared input columns",
            )
        if self._private_workspace is not None:
            self._private_workspace.release_prepared(
                self,
                generation_digest=str(self._workspace_generation_digest),
            )
        self._event_columns = MappingProxyType({})
        self._order_indices = None
        self._sealed_program_ref = None
        self._sealed_event_columns_ref = None
        self._sealed_event_column_refs = ()
        self._sealed_order_indices_ref = None
        self._private_workspace = None
        self._workspace_generation_digest = None
        self._closed = True


class NumbaGroupedI64x2CountSumDeviceResult:
    """Opaque, sealed owner for checked grouped device outputs."""

    def __init__(
        self,
        *,
        program: NumbaGroupedI64x2CountSumProgram,
        key0,
        key1,
        counts,
        sums,
        output_count,
        error_flag,
        permutation_seen,
        capacity: int,
        input_owner: PreparedNumbaGroupedI64x2CountSumColumns,
        observation_timing_seconds: Mapping[str, object] | None = None,
        private_workspace: PreparedGroupedI64x2DeviceWorkspace | None = None,
        workspace_generation_digest: str | None = None,
    ) -> None:
        input_owner.validate_integrity()
        self._program = program
        self._key0 = key0
        self._key1 = key1
        self._counts = counts
        self._sums = sums
        self._output_count = output_count
        self._error_flag = error_flag
        self._permutation_seen = permutation_seen
        self._capacity = int(capacity)
        self._input_owner = input_owner
        self._private_workspace = private_workspace
        self._workspace_generation_digest = workspace_generation_digest
        self._observation_timing_seconds = (
            _freeze_certificate_metadata(dict(observation_timing_seconds))
            if observation_timing_seconds is not None
            else None
        )
        self._synchronized = False
        self._host_projection_used = False
        self._closed = False
        self._sealed_resource_refs = (
            program,
            key0,
            key1,
            counts,
            sums,
            output_count,
            error_flag,
            permutation_seen,
            input_owner,
        )
        self._compiler_seal = self._expected_compiler_seal()
        if private_workspace is not None:
            if (
                type(private_workspace) is not PreparedGroupedI64x2DeviceWorkspace
                or not isinstance(workspace_generation_digest, str)
                or input_owner._private_workspace is not private_workspace
            ):
                _fail(
                    "prepared_private_workspace_result_binding_invalid",
                    "result.private_workspace",
                    type(private_workspace).__name__,
                )
            private_workspace.register_result(
                self,
                generation_digest=workspace_generation_digest,
            )

    @property
    def synchronized(self) -> bool:
        return self._synchronized

    @property
    def host_projection_used(self) -> bool:
        return self._host_projection_used

    @property
    def closed(self) -> bool:
        return self._closed

    def _seal_payload(self) -> bytes:
        return repr(
            (
                "rtdl.numba_grouped_i64x2_device_result.seal.v1",
                id(self._program),
                self._program.spec.semantic_digest,
                _device_resource_token(self._key0),
                _device_resource_token(self._key1),
                _device_resource_token(self._counts),
                _device_resource_token(self._sums),
                _device_resource_token(self._output_count),
                _device_resource_token(self._error_flag),
                (
                    _device_resource_token(self._permutation_seen)
                    if self._permutation_seen is not None
                    else None
                ),
                self._capacity,
                id(self._input_owner),
                self._input_owner._compiler_seal,
                _certificate_metadata_digest(
                    self._observation_timing_seconds
                ),
            )
        ).encode("utf-8")

    def _expected_compiler_seal(self) -> str:
        return hmac.new(
            _GROUPED_DEVICE_RESULT_SEAL_KEY,
            self._seal_payload(),
            hashlib.sha256,
        ).hexdigest()

    def _validate_integrity(self) -> None:
        if type(self) is not NumbaGroupedI64x2CountSumDeviceResult:
            _fail("device_result_exact_type_required", "result", type(self).__name__)
        if self._closed:
            _fail("device_result_closed", "result", "device result owner has been closed")
        if self._private_workspace is not None:
            self._private_workspace.validate_result(
                self,
                generation_digest=str(self._workspace_generation_digest),
            )
            return
        self._input_owner.validate_integrity()
        current_resources = (
            self._program,
            self._key0,
            self._key1,
            self._counts,
            self._sums,
            self._output_count,
            self._error_flag,
            self._permutation_seen,
            self._input_owner,
        )
        if any(
            current is not sealed
            for current, sealed in zip(current_resources, self._sealed_resource_refs)
        ):
            _fail(
                "device_result_resource_binding_changed",
                "result",
                "program, output resources, validation resources, or input owner changed",
            )
        if not hmac.compare_digest(
            self._compiler_seal,
            self._expected_compiler_seal(),
        ):
            _fail(
                "device_result_compiler_seal_invalid",
                "result._compiler_seal",
                "grouped device result identity changed after issuance",
            )

    def synchronize(self) -> None:
        self._require_open()
        cuda, _ = _import_numba_stack()
        cuda.synchronize()
        self._synchronized = True

    def to_host_reductions(self) -> tuple[ReductionRelation, ...]:
        self._require_open()
        if not self._synchronized:
            self.synchronize()
        error = int(self._error_flag.copy_to_host()[0])
        if error == 1:
            _fail(
                "group_key_order_certificate_violated",
                "device.key_order",
                "i64x2 keys are not lexicographically nondecreasing",
            )
        if error == 2:
            _fail("signed_reduction_overflow", "device.sum", "signed i64 sum overflowed")
        if error == 3:
            _fail(
                "device_order_index_out_of_range",
                "device.order_indices",
                "compiler-owned order index escaped the input batch",
            )
        if error == 4:
            _fail(
                "device_order_not_a_permutation",
                "device.order_indices",
                "compiler-owned order contains a duplicate source row",
            )
        if error == 5:
            _fail(
                "nonnegative_field_violation",
                f"device.{self._program.key_fields[0]}",
                self._program.key_fields[0],
            )
        if error == 6:
            _fail(
                "nonnegative_field_violation",
                f"device.{self._program.key_fields[1]}",
                self._program.key_fields[1],
            )
        if error == 7:
            _fail(
                "nonnegative_field_violation",
                f"device.{self._program.sum_field}",
                self._program.sum_field,
            )
        if error:
            _fail("unknown_device_error", "device.error_flag", str(error))
        count = int(self._output_count.copy_to_host()[0])
        if count < 0 or count > self._capacity:
            _fail("group_capacity_exceeded", "device.output_count", str(count))
        keys0 = self._key0[:count].copy_to_host()
        keys1 = self._key1[:count].copy_to_host()
        counts = self._counts[:count].copy_to_host()
        sums = self._sums[:count].copy_to_host()
        if count > 1:
            _, np = _import_numba_stack()
            order = np.lexsort((keys1, keys0))
            keys0 = np.ascontiguousarray(keys0[order])
            keys1 = np.ascontiguousarray(keys1[order])
            counts = np.ascontiguousarray(counts[order])
            sums = np.ascontiguousarray(sums[order])
        from .action_host_continuation import (
            HostI64x2ReductionRows,
            _immutable_numpy_1d,
        )

        keys0 = _immutable_numpy_1d(keys0)
        keys1 = _immutable_numpy_1d(keys1)
        counts = _immutable_numpy_1d(counts)
        sums = _immutable_numpy_1d(sums)

        by_name = {
            self._program.count_reduction_name: ReductionRelation(
                self._program.count_reduction_name,
                self._program.key_fields,
                HostI64x2ReductionRows._from_compiler_owned(keys0, keys1, counts),
            ),
            self._program.sum_reduction_name: ReductionRelation(
                self._program.sum_reduction_name,
                self._program.key_fields,
                HostI64x2ReductionRows._from_compiler_owned(keys0, keys1, sums),
            ),
        }
        self._host_projection_used = True
        return tuple(by_name[reduction.name] for reduction in self._program.spec.reductions)

    def to_metadata(self) -> dict[str, object]:
        self._require_open()
        return self._input_owner.to_metadata() | {
            "output_columns_device_resident": True,
            "device_output_owner_live": not self._closed,
            "capacity": self._capacity,
            "synchronized": self._synchronized,
            "host_projection_used": self._host_projection_used,
            "host_projection_is_explicit_diagnostic_or_consumer_boundary": True,
            "host_group_sort_used_for_semantic_projection": self._host_projection_used,
            "compiler_owned_device_output_resources_are_opaque": True,
            "device_result_compiler_sealed": True,
            "observation_timing_seconds": (
                _plain_certificate_metadata(
                    self._observation_timing_seconds
                )
                if self._observation_timing_seconds is not None
                else None
            ),
        }

    def close(self) -> None:
        if self._closed:
            return
        self._validate_integrity()
        if not self._synchronized:
            self.synchronize()
        self._input_owner._release_result(self)
        if self._private_workspace is not None:
            self._private_workspace.release_result(
                self,
                generation_digest=str(self._workspace_generation_digest),
            )
        self._closed = True
        self._key0 = None
        self._key1 = None
        self._counts = None
        self._sums = None
        self._output_count = None
        self._error_flag = None
        self._permutation_seen = None
        self._private_workspace = None
        self._workspace_generation_digest = None

    def _require_open(self) -> None:
        self._validate_integrity()


class EagerSpecializedGroupedI64x2PreparedExecution:
    """Transparent prepared owner with explicit setup specialization evidence."""

    __slots__ = (
        "_prepared",
        "_prepared_identity_digest",
        "_prepared_object_id",
        "_seal",
        "_specialization",
    )

    def __init__(self, prepared, specialization: Mapping[str, object]) -> None:
        from .action_prepared import PreparedActionExecution

        if type(prepared) is not PreparedActionExecution:
            _fail(
                "grouped_eager_prepared_owner_required",
                "prepared",
                type(prepared).__name__,
            )
        canonical_specialization = self._validate_specialization(specialization)
        metadata = prepared.to_metadata()
        identity = metadata.get("identity")
        if (
            not isinstance(identity, Mapping)
            or identity.get("selected_backend") != "numba"
            or identity.get("selected_placement") != "device_continuation"
            or identity.get("selected_template") != "grouped_i64x2_count_sum"
            or not isinstance(identity.get("identity_digest"), str)
            or len(str(identity["identity_digest"])) != 64
            or metadata.get("application_selected_backend") is not False
        ):
            _fail(
                "grouped_eager_prepared_identity_invalid",
                "prepared.identity",
                "expected compiler-owned grouped numba prepared identity",
            )
        self._prepared = prepared
        self._prepared_object_id = id(prepared)
        self._prepared_identity_digest = str(identity["identity_digest"])
        self._specialization = MappingProxyType(canonical_specialization)
        self._seal = self._issue_seal()

    @staticmethod
    def _validate_specialization(
        specialization: Mapping[str, object],
    ) -> dict[str, object]:
        if type(specialization) is not dict:
            _fail(
                "grouped_eager_specialization_mapping_required",
                "specialization",
                type(specialization).__name__,
            )
        value = dict(specialization)
        row_count = value.get("synthetic_row_count")
        expected_keys = {
            "contract",
            "elapsed_seconds",
            "synthetic_row_count",
            "complete_physical_route_executed",
            "registered_query_count",
            "kernel_launch_delta",
            "runtime_speedup_claimed",
        }
        if row_count == 0:
            expected_keys.add("reason")
        elapsed = value.get("elapsed_seconds")
        kernel_delta = value.get("kernel_launch_delta")
        if (
            set(value) != expected_keys
            or value.get("contract")
            != "rtdl.grouped_i64x2_eager_device_specialization.v1"
            or type(row_count) is not int
            or row_count not in {0, 1}
            or type(elapsed) is not float
            or not math.isfinite(elapsed)
            or elapsed < 0.0
            or type(kernel_delta) is not int
            or kernel_delta < 0
            or type(value.get("registered_query_count")) is not int
            or value.get("registered_query_count") != 0
            or value.get("runtime_speedup_claimed") is not False
            or (
                row_count == 1
                and (
                    value.get("complete_physical_route_executed") is not True
                    or kernel_delta < 1
                )
            )
            or (
                row_count == 0
                and (
                    value.get("complete_physical_route_executed") is not False
                    or elapsed != 0.0
                    or kernel_delta != 0
                    or value.get("reason") != "zero_capacity"
                )
            )
        ):
            _fail(
                "grouped_eager_specialization_invalid",
                "specialization",
                "specialization facts are not compiler-canonical",
            )
        return value

    def _seal_payload(self) -> bytes:
        return json.dumps(
            {
                "contract": "rtdl.grouped_i64x2_eager_wrapper_seal.v1",
                "prepared_object_id": self._prepared_object_id,
                "prepared_identity_digest": self._prepared_identity_digest,
                "specialization": dict(self._specialization),
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    def _issue_seal(self) -> str:
        return hmac.new(
            _GROUPED_DEVICE_EAGER_WRAPPER_SEAL_KEY,
            self._seal_payload(),
            hashlib.sha256,
        ).hexdigest()

    def _validate_integrity(self) -> None:
        from .action_prepared import PreparedActionExecution

        if (
            type(self) is not EagerSpecializedGroupedI64x2PreparedExecution
            or type(self._prepared) is not PreparedActionExecution
            or id(self._prepared) != self._prepared_object_id
            or type(self._specialization) is not MappingProxyType
            or not isinstance(self._prepared_identity_digest, str)
            or not isinstance(self._seal, str)
        ):
            _fail(
                "grouped_eager_wrapper_binding_invalid",
                "prepared",
                "wrapper type, owner object, or immutable specialization changed",
            )
        self._validate_specialization(dict(self._specialization))
        metadata = self._prepared.to_metadata()
        identity = metadata.get("identity")
        if (
            not isinstance(identity, Mapping)
            or identity.get("identity_digest") != self._prepared_identity_digest
            or identity.get("selected_backend") != "numba"
            or identity.get("selected_placement") != "device_continuation"
            or identity.get("selected_template") != "grouped_i64x2_count_sum"
            or metadata.get("application_selected_backend") is not False
            or not hmac.compare_digest(self._seal, self._issue_seal())
        ):
            _fail(
                "grouped_eager_wrapper_seal_invalid",
                "prepared",
                "prepared identity or eager specialization differs from issuance",
            )

    @property
    def closed(self) -> bool:
        self._validate_integrity()
        return bool(self._prepared.closed)

    def execute_columns(self, *args, **kwargs):
        self._validate_integrity()
        return self._prepared.execute_columns(*args, **kwargs)

    def execute_device_columns(self, *args, **kwargs):
        self._validate_integrity()
        return self._prepared.execute_device_columns(*args, **kwargs)

    def begin_producer_owned_device_batch(self, *args, **kwargs):
        self._validate_integrity()
        return self._prepared.begin_producer_owned_device_batch(*args, **kwargs)

    def execute_producer_owned_device_batch(self, *args, **kwargs):
        self._validate_integrity()
        return self._prepared.execute_producer_owned_device_batch(*args, **kwargs)

    def to_metadata(self) -> dict[str, object]:
        self._validate_integrity()
        metadata = dict(self._prepared.to_metadata())
        metadata["compiler_owned_eager_device_specialization"] = dict(
            self._specialization
        )
        timing = dict(metadata.get("timing", {}))
        timing["eager_specialization_seconds"] = float(
            self._specialization.get("elapsed_seconds", 0.0)
        )
        timing["eager_specialization_registered_query_count"] = 0
        metadata["timing"] = timing
        return metadata

    def close(self) -> None:
        self._validate_integrity()
        self._prepared.close()
        if self._prepared.closed is not True:
            _fail(
                "grouped_eager_prepared_close_incomplete",
                "prepared",
                "underlying prepared owner did not close",
            )


@dataclass(frozen=True)
class NumbaCertifiedQueryMinProgram:
    spec: ActionSpec
    query_field: str
    candidate_field: str
    distance_field: str
    distance_state: ActionStateSpec
    candidate_state: ActionStateSpec
    delivery_proof_reference: str
    termination_proof_name: str
    termination_certificate: str
    ordering_certificate: str = CERTIFIED_QUERY_MIN_ORDERING
    placement_contract: str = "verified_action_ir_certified_query_min_state_v1"

    def to_metadata(self) -> dict[str, object]:
        distance_kind = self.distance_state.value_type.kind.value
        return {
            "contract_version": ACTION_NUMBA_CONTINUATION_VERSION,
            "semantic_digest": self.spec.semantic_digest,
            "placement_contract": self.placement_contract,
            "delivery_proof_reference": self.delivery_proof_reference,
            "termination_proof_name": self.termination_proof_name,
            "termination_certificate": self.termination_certificate,
            "ordering_certificate": self.ordering_certificate,
            "delivery_proof_discharged_by_placement": True,
            "termination_proof_discharged_by_placement": True,
            "ordering_verified_on_device_before_state_write": True,
            "action_name_used_for_dispatch": False,
            "user_numba_kernel_accepted": False,
            "supported_effect_subset": ["filter", "state_update", "certified_traversal_control"],
            "state_scope": "per_query",
            "state_update": f"lexicographic_min_canonical_{distance_kind}_then_candidate_id",
            "distance_value_type": distance_kind,
            "per_source_witness_exact": True,
            "unbounded_event_rows_downloaded": False,
            "unsupported_effects_fail_closed": True,
        }


@dataclass
class PreparedNumbaCertifiedQueryMinColumns:
    program: NumbaCertifiedQueryMinProgram
    event_columns: dict[str, object]
    query_count: int
    owns_event_columns: bool
    host_to_device_copy_used: bool
    active_results: int = 0
    closed: bool = False

    def to_metadata(self) -> dict[str, object]:
        return self.program.to_metadata() | {
            "row_count": self.row_count,
            "query_count": self.query_count,
            "input_columns_device_resident": True,
            "host_to_device_copy_used": self.host_to_device_copy_used,
            "owns_event_columns": self.owns_event_columns,
            "materializes_host_rows_for_bridge": False,
            "lifetime_owner_required_through_synchronize": True,
            "active_results": self.active_results,
            "closed": self.closed,
        }

    @property
    def row_count(self) -> int:
        if not self.event_columns:
            return 0
        return int(next(iter(self.event_columns.values())).shape[0])

    def close(self) -> None:
        if self.active_results:
            _fail(
                "input_owner_still_in_use",
                "prepared.active_results",
                "close device results before closing prepared input columns",
            )
        self.event_columns.clear()
        self.closed = True


@dataclass
class NumbaCertifiedQueryMinDeviceResult:
    program: NumbaCertifiedQueryMinProgram
    best_distances: object
    best_candidates: object
    present: object
    error_flag: object
    input_owner: PreparedNumbaCertifiedQueryMinColumns
    synchronized: bool = False
    host_projection_used: bool = False
    closed: bool = False

    def synchronize(self) -> None:
        self._require_open()
        cuda, _ = _import_numba_stack()
        cuda.synchronize()
        self.synchronized = True

    def to_host_states(self) -> tuple[StateRelation, StateRelation]:
        self._require_open()
        if not self.synchronized:
            self.synchronize()
        error = int(self.error_flag.copy_to_host()[0])
        error_messages = {
            1: ("nan_runtime_value", "distance contains NaN"),
            2: ("query_extent_exceeded", "query id is outside query_count"),
            3: ("query_order_certificate_violated", "query ids are not grouped in ascending order"),
            4: ("distance_order_certificate_violated", "distance is not nondecreasing within a query"),
            5: ("candidate_order_certificate_violated", "candidate ids do not strictly order equal-distance ties"),
        }
        if error:
            code, message = error_messages.get(error, ("unknown_device_error", str(error)))
            _fail(code, "device.ordering_validation", message)
        present = self.present.copy_to_host()
        distances = self.best_distances.copy_to_host()
        candidates = self.best_candidates.copy_to_host()
        distance_rows = tuple(
            ((query_id,), _python_scalar(distances[query_id]))
            for query_id in range(self.input_owner.query_count)
            if int(present[query_id]) != 0
        )
        candidate_rows = tuple(
            ((query_id,), _python_scalar(candidates[query_id]))
            for query_id in range(self.input_owner.query_count)
            if int(present[query_id]) != 0
        )
        self.host_projection_used = True
        by_name = {
            self.program.distance_state.name: StateRelation(
                self.program.distance_state.name,
                self.program.distance_state.scope,
                self.program.distance_state.key_fields,
                distance_rows,
            ),
            self.program.candidate_state.name: StateRelation(
                self.program.candidate_state.name,
                self.program.candidate_state.scope,
                self.program.candidate_state.key_fields,
                candidate_rows,
            ),
        }
        return tuple(by_name[state.name] for state in self.program.spec.states)  # type: ignore[return-value]

    def to_metadata(self) -> dict[str, object]:
        return self.input_owner.to_metadata() | {
            "output_state_columns_device_resident": True,
            "device_output_owner_live": not self.closed,
            "synchronized": self.synchronized,
            "host_projection_used": self.host_projection_used,
            "host_projection_is_explicit_diagnostic_or_consumer_boundary": True,
        }

    def close(self) -> None:
        if self.closed:
            return
        if not self.synchronized:
            self.synchronize()
        self.best_distances = None
        self.best_candidates = None
        self.present = None
        self.error_flag = None
        self.input_owner.active_results -= 1
        self.closed = True

    def _require_open(self) -> None:
        if self.closed:
            _fail("device_result_closed", "result", "device result owner has been closed")
        if self.input_owner.closed:
            _fail("input_owner_closed", "input_owner", "input columns closed before completion")


@dataclass
class NumbaCertifiedQueryMinGlobalMaxDeviceResult:
    source_ids: object
    candidate_ids: object
    distances: object
    row_indices: object
    valid_count: object
    status: object
    input_metadata: dict[str, object]
    reducer_metadata: dict[str, object]
    host_projection_used: bool = False
    closed: bool = False

    def to_host_witness(self) -> dict[str, object]:
        if self.closed:
            _fail("device_result_closed", "result", "global-max result has been closed")
        status = int(self.status.copy_to_host()[0])
        error_messages = {
            1: ("nan_runtime_value", "distance contains NaN"),
            2: ("query_extent_exceeded", "query id is outside query_count"),
            3: ("query_order_certificate_violated", "query ids are not grouped in ascending order"),
            4: ("distance_order_certificate_violated", "distance is not nondecreasing within a query"),
            5: ("candidate_order_certificate_violated", "candidate ids do not strictly order equal-distance ties"),
        }
        if status:
            code, message = error_messages.get(status, ("unknown_device_error", str(status)))
            _fail(code, "device.ordering_validation", message)
        valid_count = int(self.valid_count.copy_to_host()[0])
        if valid_count <= 0:
            _fail("no_present_query_state", "device.valid_count", "no query produced a finite minimum")
        self.host_projection_used = True
        return {
            "source_index": int(self.row_indices.copy_to_host()[0]),
            "source_id": int(self.source_ids.copy_to_host()[0]),
            "item_id": int(self.candidate_ids.copy_to_host()[0]),
            "value": float(self.distances.copy_to_host()[0]),
        }

    def to_metadata(self) -> dict[str, object]:
        return dict(self.input_metadata) | {
            "composition_contract": "certified_query_min_state_to_global_max_witness_v1",
            "input_state_columns_device_resident": True,
            "full_state_host_projection_used": False,
            "bounded_output_rows": 1,
            "bounded_witness_host_projection_used": self.host_projection_used,
            "host_valid_count_materialization_before_reduction_used": False,
            "reducer_host_row_materialization_used": bool(
                self.reducer_metadata["host_row_materialization_used"]
            ),
            "reducer_host_valid_count_materialization_used": bool(
                self.reducer_metadata["host_valid_count_materialization_used"]
            ),
            "reducer_empty_validation_deferred_to_bounded_consumer": bool(
                self.reducer_metadata["empty_validation_deferred_to_bounded_consumer"]
            ),
            "device_output_owner_live": not self.closed,
        }

    def close(self) -> None:
        if self.closed:
            return
        self.source_ids = None
        self.candidate_ids = None
        self.distances = None
        self.row_indices = None
        self.valid_count = None
        self.status = None
        self.closed = True


def compile_numba_certified_query_min_state(
    spec: ActionSpec,
    *,
    discharged_delivery_proofs: frozenset[str] = frozenset(),
    discharged_termination_certificates: frozenset[str] = frozenset(),
    discharged_ordering_certificates: frozenset[str] = frozenset(),
) -> NumbaCertifiedQueryMinProgram:
    """Lower the closed certified-first-min Action shape without name dispatch."""

    verify_action_spec(spec)
    if spec.parameter_type.fields or spec.emits or spec.reductions:
        _fail(
            "certified_query_min_shape_required",
            "spec",
            "placement requires state-only input with no parameters, emits, or reductions",
        )
    if (
        spec.logical_event.physical_delivery is not PhysicalDelivery.PROVEN_SINGLE
        or spec.logical_event.enforcement is not DeliveryEnforcement.PROVEN_SINGLE
    ):
        _fail(
            "single_delivery_not_discharged",
            "logical_event",
            "certified query-min has no dedup stage and requires proven-single delivery",
        )
    delivery_proof = spec.logical_event.proof_reference
    if not delivery_proof or delivery_proof not in discharged_delivery_proofs:
        _fail(
            "delivery_proof_not_discharged",
            "logical_event.proof_reference",
            "the prepared producer's single-delivery proof must be discharged",
        )
    if len(spec.states) != 2:
        _fail("two_query_states_required", "states", "expected distance and candidate-id state")
    distance_states = [
        state
        for state in spec.states
        if isinstance(state.value_type, ActionScalarType)
        and state.value_type.kind in {ActionScalarKind.F32, ActionScalarKind.F64}
    ]
    candidate_states = [
        state
        for state in spec.states
        if isinstance(state.value_type, ActionScalarType)
        and state.value_type.kind is ActionScalarKind.U32
    ]
    if len(distance_states) != 1 or len(candidate_states) != 1:
        _fail(
            "query_min_state_types_required",
            "states",
            "expected exactly one F32/F64 distance state and one U32 candidate state",
        )
    distance_state = distance_states[0]
    candidate_state = candidate_states[0]
    if (
        distance_state.scope is not StateScope.PER_QUERY
        or candidate_state.scope is not StateScope.PER_QUERY
        or len(distance_state.key_fields) != 1
        or candidate_state.key_fields != distance_state.key_fields
    ):
        _fail("per_query_state_scope_required", "states", "states must share one per-query key")
    query_field = distance_state.key_fields[0]
    query_spec = spec.event_type.field(query_field)
    if (
        query_spec is None
        or not isinstance(query_spec.value_type, ActionScalarType)
        or query_spec.value_type.kind is not ActionScalarKind.U32
    ):
        _fail("u32_query_key_required", "states.key_fields", query_field)
    if not math.isinf(float(distance_state.initial_value.to_python())) or float(
        distance_state.initial_value.to_python()
    ) < 0:
        _fail("positive_infinity_distance_identity_required", "states", distance_state.name)
    if int(candidate_state.initial_value.to_python()) != (1 << 32) - 1:
        _fail("u32_max_candidate_identity_required", "states", candidate_state.name)
    if len(spec.termination_proofs) != 1:
        _fail("one_termination_proof_required", "termination_proofs", str(len(spec.termination_proofs)))
    proof = spec.termination_proofs[0]
    if (
        proof.kind is not TerminationProofKind.MONOTONE_BOUND
        or proof.state_name != distance_state.name
        or not proof.order_independent
        or not proof.unseen_cannot_improve
    ):
        _fail(
            "certified_monotone_termination_required",
            "termination_proofs[0]",
            "proof must certify the per-query distance state and unseen-cannot-improve",
        )
    if proof.certificate not in discharged_termination_certificates:
        _fail(
            "termination_certificate_not_discharged",
            "termination_proofs[0].certificate",
            proof.certificate,
        )
    if CERTIFIED_QUERY_MIN_ORDERING not in discharged_ordering_certificates:
        _fail(
            "ordering_certificate_not_discharged",
            "placement.ordering_certificate",
            CERTIFIED_QUERY_MIN_ORDERING,
        )
    if len(spec.blocks) != 1 or any(
        isinstance(statement, ActionStaticLoop) for statement in spec.blocks[0].operations
    ):
        _fail("single_straight_line_block_required", "blocks", "certified query-min is straight-line")
    operations = tuple(spec.blocks[0].operations)
    expected_opcodes = (
        "load_event",
        "load_event",
        "state_read",
        "compare",
        "filter",
        "state_write",
        "state_write",
        "terminate",
    )
    if tuple(op.opcode for op in operations) != expected_opcodes:
        _fail(
            "certified_query_min_operation_shape_required",
            "blocks[0]",
            str(tuple(op.opcode for op in operations)),
        )
    distance_load, candidate_load, state_read, compare, filter_op, distance_write, candidate_write, terminate = operations
    distance_field = str(distance_load.attribute("field"))
    candidate_field = str(candidate_load.attribute("field"))
    distance_spec = spec.event_type.field(distance_field)
    candidate_spec = spec.event_type.field(candidate_field)
    if (
        distance_spec is None
        or not isinstance(distance_spec.value_type, ActionScalarType)
        or distance_spec.value_type.kind is not distance_state.value_type.kind
        or candidate_spec is None
        or not isinstance(candidate_spec.value_type, ActionScalarType)
        or candidate_spec.value_type.kind is not ActionScalarKind.U32
    ):
        _fail(
            "query_min_event_types_required",
            "event_type",
            "expected distance type to match the floating state and a U32 candidate",
        )
    if tuple(field.name for field in spec.event_type.fields) != (
        query_field,
        candidate_field,
        distance_field,
    ):
        _fail(
            "closed_query_min_event_schema_required",
            "event_type",
            "expected query, candidate, distance only",
        )
    if spec.logical_event.key_fields != (query_field, candidate_field):
        _fail(
            "query_candidate_logical_key_required",
            "logical_event.key_fields",
            str(spec.logical_event.key_fields),
        )
    distance_value = distance_load.outputs[0].name
    candidate_value = candidate_load.outputs[0].name
    best_value = state_read.outputs[0].name
    improves_value = compare.outputs[0].name
    if (
        state_read.attribute("state") != distance_state.name
        or compare.attribute("predicate") != "lt"
        or compare.inputs != (distance_value, best_value)
        or filter_op.inputs != (improves_value,)
        or distance_write.attribute("state") != distance_state.name
        or distance_write.inputs != (distance_value,)
        or candidate_write.attribute("state") != candidate_state.name
        or candidate_write.inputs != (candidate_value,)
        or terminate.attribute("proof") != proof.name
    ):
        _fail(
            "certified_query_min_dataflow_required",
            "blocks[0]",
            "distance<best must guard paired distance/id writes followed by certified terminate",
        )
    return NumbaCertifiedQueryMinProgram(
        spec=spec,
        query_field=query_field,
        candidate_field=candidate_field,
        distance_field=distance_field,
        distance_state=distance_state,
        candidate_state=candidate_state,
        delivery_proof_reference=delivery_proof,
        termination_proof_name=proof.name,
        termination_certificate=proof.certificate,
    )


def prepare_numba_certified_query_min_columns(
    program: NumbaCertifiedQueryMinProgram,
    event_columns: Mapping[str, object],
    *,
    query_count: int,
) -> PreparedNumbaCertifiedQueryMinColumns:
    """Borrow or copy typed columns; ordering is validated by the execution preflight."""

    cuda, np = _import_numba_stack()
    if not isinstance(query_count, int) or isinstance(query_count, bool) or query_count < 0:
        _fail("invalid_query_count", "query_count", str(query_count))
    if query_count > (1 << 32):
        _fail("invalid_query_count", "query_count", "query_count exceeds the U32 key space")
    expected = {field.name for field in program.spec.event_type.fields}
    if set(event_columns) != expected:
        _fail("event_column_schema_mismatch", "event_columns", f"expected {sorted(expected)}")
    prepared: dict[str, object] = {}
    row_count: int | None = None
    copied = False
    all_owned = True
    for field in program.spec.event_type.fields:
        expected_dtype = _numpy_dtype(field.value_type, np)
        value = event_columns[field.name]
        if hasattr(value, "__cuda_array_interface__") or hasattr(value, "copy_to_host"):
            device = cuda.as_cuda_array(value) if not hasattr(value, "copy_to_host") else value
            all_owned = False
        else:
            host = np.asarray(value)
            if host.ndim != 1 or host.dtype != expected_dtype or not host.flags.c_contiguous:
                _fail(
                    "event_column_layout_mismatch",
                    f"event_columns.{field.name}",
                    f"expected contiguous 1-D {expected_dtype}",
                )
            device = cuda.to_device(host)
            copied = True
        if len(tuple(device.shape)) != 1 or device.dtype != expected_dtype:
            _fail("event_device_column_mismatch", f"event_columns.{field.name}", str(device.dtype))
        count = int(device.shape[0])
        if row_count is None:
            row_count = count
        elif row_count != count:
            _fail("event_column_length_mismatch", f"event_columns.{field.name}", str(count))
        prepared[field.name] = device
    return PreparedNumbaCertifiedQueryMinColumns(
        program=program,
        event_columns=prepared,
        query_count=query_count,
        owns_event_columns=all_owned,
        host_to_device_copy_used=copied,
    )


def execute_numba_certified_query_min_state(
    prepared: PreparedNumbaCertifiedQueryMinColumns,
    *,
    block_size: int = 128,
) -> NumbaCertifiedQueryMinDeviceResult:
    """Validate the certified order and materialize exact per-query min state on device."""

    if prepared.closed:
        _fail("prepared_columns_closed", "prepared", "prepared input owner is closed")
    if block_size <= 0:
        _fail("invalid_block_size", "block_size", str(block_size))
    cuda, np = _import_numba_stack()
    query_count = prepared.query_count
    distance_dtype = (
        np.float32
        if prepared.program.distance_state.value_type.kind is ActionScalarKind.F32
        else np.float64
    )
    best_distances = cuda.to_device(np.full(query_count, np.inf, dtype=distance_dtype))
    best_candidates = cuda.to_device(np.full(query_count, np.iinfo(np.uint32).max, dtype=np.uint32))
    present = cuda.to_device(np.zeros(query_count, dtype=np.uint8))
    error_flag = cuda.to_device(np.zeros(1, dtype=np.int32))
    validate_kernel, state_kernel = _compiled_certified_query_min_kernels(cuda)
    row_count = prepared.row_count
    if row_count:
        blocks = (row_count + block_size - 1) // block_size
        query_ids = prepared.event_columns[prepared.program.query_field]
        candidate_ids = prepared.event_columns[prepared.program.candidate_field]
        distances = prepared.event_columns[prepared.program.distance_field]
        validate_kernel[blocks, block_size](
            query_ids,
            candidate_ids,
            distances,
            error_flag,
            row_count,
            query_count,
        )
        state_kernel[blocks, block_size](
            query_ids,
            candidate_ids,
            distances,
            best_distances,
            best_candidates,
            present,
            error_flag,
            row_count,
        )
    prepared.active_results += 1
    return NumbaCertifiedQueryMinDeviceResult(
        program=prepared.program,
        best_distances=best_distances,
        best_candidates=best_candidates,
        present=present,
        error_flag=error_flag,
        input_owner=prepared,
    )


def reduce_numba_certified_query_min_global_max_witness(
    result: NumbaCertifiedQueryMinDeviceResult,
    *,
    block_size: int = 256,
) -> NumbaCertifiedQueryMinGlobalMaxDeviceResult:
    """Feed resident per-query minimum state into a resident global max reducer."""

    result._require_open()
    cuda, np = _import_numba_stack()
    query_count = result.input_owner.query_count
    if query_count <= 0:
        _fail("invalid_query_count", "result.input_owner.query_count", str(query_count))
    if block_size <= 0 or block_size > 256:
        _fail("invalid_block_size", "block_size", "expected a value in [1, 256]")
    source_ids = cuda.device_array((query_count,), dtype=np.uint32)
    distances_f64 = cuda.device_array((query_count,), dtype=np.float64)
    status = cuda.device_array((1,), dtype=np.int32)
    mark_sources, gather_candidate = _compiled_certified_query_min_global_max_kernels(cuda)
    blocks = (query_count + block_size - 1) // block_size
    mark_sources[blocks, block_size](
        result.present,
        result.error_flag,
        result.best_distances,
        source_ids,
        distances_f64,
        status,
        query_count,
        np.uint32((1 << 32) - 1),
    )

    from .numba_partner_continuation import run_numba_global_argmax_u32_f64

    reduced = run_numba_global_argmax_u32_f64(
        source_ids,
        distances_f64,
        block_size=block_size,
        defer_empty_validation=True,
    )
    outputs = reduced["outputs"]
    candidate_ids = cuda.device_array((1,), dtype=np.uint32)
    gather_candidate[1, 1](
        outputs["row_indices"],
        outputs["valid_count"],
        result.best_candidates,
        candidate_ids,
        np.uint32((1 << 32) - 1),
    )
    cuda.synchronize()
    result.synchronized = True
    return NumbaCertifiedQueryMinGlobalMaxDeviceResult(
        source_ids=outputs["item_ids"],
        candidate_ids=candidate_ids,
        distances=outputs["scores"],
        row_indices=outputs["row_indices"],
        valid_count=outputs["valid_count"],
        status=status,
        input_metadata=result.to_metadata(),
        reducer_metadata={
            "host_row_materialization_used": reduced["host_row_materialization_used"],
            "host_valid_count_materialization_used": reduced[
                "host_valid_count_materialization_used"
            ],
            "empty_validation_deferred_to_bounded_consumer": reduced[
                "empty_validation_deferred_to_bounded_consumer"
            ],
        },
    )


def compile_numba_grouped_i64x2_count_sum(
    spec: ActionSpec,
    *,
    discharged_delivery_proofs: frozenset[str] = frozenset(),
) -> NumbaGroupedI64x2CountSumProgram:
    """Lower the exact generic grouped-i64x2 COUNT plus signed-SUM shape."""

    verify_action_spec(spec)
    if spec.parameter_type.fields or spec.states or spec.emits or spec.termination_proofs:
        _fail(
            "grouped_i64x2_count_sum_shape_required",
            "spec",
            "placement accepts reductions only, with no parameters, state, emit, or termination",
        )
    if (
        spec.logical_event.physical_delivery is not PhysicalDelivery.PROVEN_SINGLE
        or spec.logical_event.enforcement is not DeliveryEnforcement.PROVEN_SINGLE
    ):
        _fail(
            "single_delivery_not_discharged",
            "logical_event",
            "grouped reduction requires compiler-verified single logical delivery",
        )
    proof_reference = spec.logical_event.proof_reference
    if not proof_reference or proof_reference not in discharged_delivery_proofs:
        _fail(
            "delivery_proof_not_discharged",
            "logical_event.proof_reference",
            "a placement-proven delivery certificate must be supplied",
        )
    if len(spec.blocks) != 1:
        _fail("single_block_required", "blocks", "grouped reduction requires one straight-line block")
    if len(spec.reductions) != 2:
        _fail(
            "count_and_sum_reductions_required",
            "reductions",
            "expected exactly one COUNT and one signed-I64 SUM",
        )
    count_reductions = [item for item in spec.reductions if item.operator is ReductionOperator.COUNT]
    sum_reductions = [item for item in spec.reductions if item.operator is ReductionOperator.SUM]
    if len(count_reductions) != 1 or len(sum_reductions) != 1:
        _fail(
            "count_and_sum_reductions_required",
            "reductions",
            "expected exactly one COUNT and one signed-I64 SUM",
        )
    count_reduction = count_reductions[0]
    sum_reduction = sum_reductions[0]
    if (
        not isinstance(count_reduction.value_type, ActionScalarType)
        or count_reduction.value_type.kind is not ActionScalarKind.U64
        or not isinstance(sum_reduction.value_type, ActionScalarType)
        or sum_reduction.value_type.kind is not ActionScalarKind.I64
    ):
        _fail(
            "count_u64_sum_i64_required",
            "reductions",
            "COUNT must use U64 and SUM must use I64",
        )
    if count_reduction.key_fields != sum_reduction.key_fields or len(sum_reduction.key_fields) != 2:
        _fail(
            "shared_i64x2_key_required",
            "reductions",
            "COUNT and SUM must share exactly two key fields",
        )
    key_fields = tuple(sum_reduction.key_fields)
    for index, key in enumerate(key_fields):
        field = spec.event_type.field(key)
        if (
            field is None
            or not isinstance(field.value_type, ActionScalarType)
            or field.value_type.kind is not ActionScalarKind.I64
        ):
            _fail("shared_i64x2_key_required", f"reductions.key_fields[{index}]", key)

    operations = spec.blocks[0].operations
    if len(operations) != 3 or any(isinstance(item, ActionStaticLoop) for item in operations):
        _fail(
            "load_then_count_sum_required",
            "blocks[0]",
            "expected one load_event and two reduce operations",
        )
    load_ops = [item for item in operations if item.opcode == "load_event"]
    reduce_ops = [item for item in operations if item.opcode == "reduce"]
    if len(load_ops) != 1 or len(reduce_ops) != 2 or len(load_ops[0].outputs) != 1:
        _fail(
            "load_then_count_sum_required",
            "blocks[0]",
            "expected one load_event and two reduce operations",
        )
    load_op = load_ops[0]
    loaded = load_op.outputs[0]
    sum_field = str(load_op.attribute("field"))
    field = spec.event_type.field(sum_field)
    if (
        field is None
        or not isinstance(field.value_type, ActionScalarType)
        or field.value_type.kind is not ActionScalarKind.I64
        or loaded.value_type != field.value_type
    ):
        _fail("signed_i64_sum_field_required", "blocks[0].load_event", sum_field)
    by_reduction = {str(item.attribute("reduction")): item for item in reduce_ops}
    count_op = by_reduction.get(count_reduction.name)
    sum_op = by_reduction.get(sum_reduction.name)
    if count_op is None or count_op.inputs or sum_op is None or sum_op.inputs != (loaded.name,):
        _fail(
            "load_then_count_sum_required",
            "blocks[0]",
            "COUNT must have no input and SUM must consume the loaded I64 value",
        )
    return NumbaGroupedI64x2CountSumProgram(
        spec=spec,
        event_fields=tuple(field.name for field in spec.event_type.fields),
        key_fields=(key_fields[0], key_fields[1]),
        sum_field=sum_field,
        count_reduction_name=count_reduction.name,
        sum_reduction_name=sum_reduction.name,
        delivery_proof_reference=proof_reference,
    )


def validate_numba_grouped_i64x2_order_indexed_binding_shape(
    program: NumbaGroupedI64x2CountSumProgram,
) -> str:
    """Validate the closed generated-key device-column binding shape.

    This verifier is deliberately pure: capability construction, lowering,
    and runtime preparation all use the same restrictions, so a template
    cannot be advertised as legal and then reject its producer shape later.
    """

    if type(program) is not NumbaGroupedI64x2CountSumProgram:
        _fail("grouped_i64x2_program_required", "program", type(program).__name__)
    logical_keys = tuple(program.spec.logical_event.key_fields)
    if len(logical_keys) != 1:
        _fail(
            "generated_device_logical_key_unsupported",
            "logical_event.key_fields",
            repr(logical_keys),
        )
    logical_key = logical_keys[0]
    logical_field = program.spec.event_type.field(logical_key)
    if (
        logical_field is None
        or not isinstance(logical_field.value_type, ActionScalarType)
        or logical_field.value_type.kind is not ActionScalarKind.I64
        or not logical_field.nonnegative
    ):
        _fail(
            "generated_device_logical_key_unsupported",
            "logical_event.key_fields[0]",
            logical_key,
        )
    required_source_fields = set(program.event_fields) - {logical_key}
    key0_name, key1_name = program.key_fields
    if required_source_fields != {key0_name, key1_name, program.sum_field}:
        _fail(
            "closed_grouped_device_schema_required",
            "event_type.fields",
            repr(sorted(required_source_fields)),
        )
    return logical_key


def compile_numba_order_indexed_grouped_i64x2_count_sum(
    spec: ActionSpec,
    *,
    discharged_delivery_proofs: frozenset[str] = frozenset(),
) -> NumbaGroupedI64x2CountSumProgram:
    """Compile only when the order-indexed device binding is executable."""

    program = compile_numba_grouped_i64x2_count_sum(
        spec,
        discharged_delivery_proofs=discharged_delivery_proofs,
    )
    validate_numba_grouped_i64x2_order_indexed_binding_shape(program)
    return program


def _validate_canonical_numba_grouped_i64x2_count_sum_program(
    program: NumbaGroupedI64x2CountSumProgram,
) -> NumbaGroupedI64x2CountSumProgram:
    """Recompile and detach all executable roles before physical ownership."""

    if type(program) is not NumbaGroupedI64x2CountSumProgram:
        _fail("grouped_i64x2_program_required", "program", type(program).__name__)
    canonical = compile_numba_grouped_i64x2_count_sum(
        program.spec,
        discharged_delivery_proofs=frozenset({program.delivery_proof_reference}),
    )
    if program != canonical:
        _fail(
            "grouped_i64x2_program_role_binding_invalid",
            "program",
            "compiler-issued executable roles differ from canonical Action lowering",
        )
    return canonical


def prepare_numba_grouped_i64x2_count_sum_columns(
    program: NumbaGroupedI64x2CountSumProgram,
    event_columns: Mapping[str, object],
) -> PreparedNumbaGroupedI64x2CountSumColumns:
    """Prepare or borrow exact event columns for the grouped reduction."""

    program = _validate_canonical_numba_grouped_i64x2_count_sum_program(program)
    cuda, np = _import_numba_stack()
    expected = set(program.event_fields)
    if set(event_columns) != expected:
        _fail("event_column_schema_mismatch", "event_columns", f"expected {sorted(expected)}")
    prepared: dict[str, object] = {}
    row_count: int | None = None
    copied = False
    all_owned = True
    for field in program.spec.event_type.fields:
        expected_dtype = _numpy_dtype(field.value_type, np)
        value = event_columns[field.name]
        if hasattr(value, "__cuda_array_interface__") or hasattr(value, "copy_to_host"):
            device = cuda.as_cuda_array(value) if not hasattr(value, "copy_to_host") else value
            all_owned = False
        else:
            host = np.asarray(value)
            if host.ndim != 1 or host.dtype != expected_dtype or not host.flags.c_contiguous:
                _fail(
                    "event_column_layout_mismatch",
                    f"event_columns.{field.name}",
                    f"expected contiguous 1-D {expected_dtype}",
                )
            if field.nonnegative and bool(np.any(host < 0)):
                _fail("nonnegative_field_violation", f"event_columns.{field.name}", field.name)
            device = cuda.to_device(host)
            copied = True
        if len(tuple(device.shape)) != 1 or device.dtype != expected_dtype:
            _fail("event_device_column_mismatch", f"event_columns.{field.name}", str(device.dtype))
        count = int(device.shape[0])
        if row_count is None:
            row_count = count
        elif row_count != count:
            _fail("event_column_length_mismatch", f"event_columns.{field.name}", str(count))
        prepared[field.name] = device
    return PreparedNumbaGroupedI64x2CountSumColumns(
        program=program,
        event_columns=prepared,
        row_count=row_count or 0,
        owns_event_columns=all_owned,
        host_to_device_copy_used=copied,
    )


def prepare_numba_grouped_i64x2_count_sum_canonical_host_workspace(
    program: NumbaGroupedI64x2CountSumProgram,
    event_columns: Mapping[str, object],
    *,
    private_workspace: PreparedGroupedI64x2DeviceWorkspace,
    owner_identity_digest: str,
    query_ordinal: int,
) -> tuple[PreparedNumbaGroupedI64x2CountSumColumns, Mapping[str, object]]:
    """Bind canonical compiler-owned host columns to one reusable workspace.

    The public host-column front door remains unchanged.  This private prepared
    route is only for callers that have already validated a sealed canonical
    batch and own the workspace for the complete prepared lifetime.
    """

    program = _validate_canonical_numba_grouped_i64x2_count_sum_program(program)
    return _prepare_numba_grouped_i64x2_count_sum_canonical_host_workspace_verified(
        program,
        event_columns,
        private_workspace=private_workspace,
        owner_identity_digest=owner_identity_digest,
        query_ordinal=query_ordinal,
    )


def _prepare_numba_grouped_i64x2_count_sum_canonical_host_workspace_verified(
    program: NumbaGroupedI64x2CountSumProgram,
    event_columns: Mapping[str, object],
    *,
    private_workspace: PreparedGroupedI64x2DeviceWorkspace,
    owner_identity_digest: str,
    query_ordinal: int,
) -> tuple[PreparedNumbaGroupedI64x2CountSumColumns, Mapping[str, object]]:
    """Private route for an enclosing compiler owner that sealed ``program``."""

    if type(program) is not NumbaGroupedI64x2CountSumProgram:
        _fail("grouped_i64x2_program_required", "program", type(program).__name__)
    if type(private_workspace) is not PreparedGroupedI64x2DeviceWorkspace:
        _fail(
            "prepared_private_workspace_binding_invalid",
            "private_workspace",
            type(private_workspace).__name__,
        )
    cuda, np = _import_numba_stack()
    del cuda
    expected = set(program.event_fields)
    if set(event_columns) != expected:
        _fail(
            "event_column_schema_mismatch",
            "event_columns",
            f"expected {sorted(expected)}",
        )
    host: dict[str, object] = {}
    row_count: int | None = None
    for field in program.spec.event_type.fields:
        expected_dtype = _numpy_dtype(field.value_type, np)
        value = np.asarray(event_columns[field.name])
        if (
            value.ndim != 1
            or value.dtype != expected_dtype
            or not value.flags.c_contiguous
        ):
            _fail(
                "event_column_layout_mismatch",
                f"event_columns.{field.name}",
                f"expected contiguous 1-D {expected_dtype}",
            )
        if field.nonnegative and bool(np.any(value < 0)):
            _fail(
                "nonnegative_field_violation",
                f"event_columns.{field.name}",
                field.name,
            )
        count = int(value.shape[0])
        if row_count is None:
            row_count = count
        elif row_count != count:
            _fail(
                "event_column_length_mismatch",
                f"event_columns.{field.name}",
                str(count),
            )
        host[field.name] = value
    resolved_count = row_count or 0
    private_workspace.begin_query(
        owner_identity_digest=owner_identity_digest,
        query_ordinal=query_ordinal,
    )
    try:
        captured, metadata = private_workspace.capture_canonical_host_snapshot(
            owner_identity_digest=owner_identity_digest,
            query_ordinal=query_ordinal,
            row_count=resolved_count,
            key0_source=host[program.key_fields[0]],
            key1_source=host[program.key_fields[1]],
            value_source=host[program.sum_field],
        )
        source = {
            program.key_fields[0]: captured["key0"],
            program.key_fields[1]: captured["key1"],
            program.sum_field: captured["value"],
        }
        generation_digest = str(metadata["workspace_generation_digest"])
        prepared = PreparedNumbaGroupedI64x2CountSumColumns(
            program=program,
            event_columns=source,
            row_count=resolved_count,
            owns_event_columns=True,
            host_to_device_copy_used=True,
            device_to_device_copy_used=False,
            device_certificate_metadata=metadata,
            order_indices=None,
            private_workspace=private_workspace,
            workspace_generation_digest=generation_digest,
        )
        return prepared, metadata
    except Exception:
        private_workspace.abort_query(
            owner_identity_digest=owner_identity_digest,
            query_ordinal=query_ordinal,
        )
        raise


def prepare_numba_grouped_i64x2_count_sum_device_columns(
    program: NumbaGroupedI64x2CountSumProgram,
    event_columns: Mapping[str, object],
    *,
    max_row_count: int,
    native_order_context: GroupedI64x2NativeOrderContext | None = None,
) -> PreparedNumbaGroupedI64x2CountSumColumns:
    """Own, sort, and certify one device-resident grouped-reduction batch.

    The logical single-delivery key is compiler-generated from the source-row
    permutation.  Source columns are copied device-to-device into private
    source-order allocations, and the checked reduction reads through a
    compiler-owned order permutation.  Later mutation of caller-owned buffers
    therefore cannot change the certified batch.  Only the fixed-size
    validation status crosses to the host.
    """

    program = _validate_canonical_numba_grouped_i64x2_count_sum_program(program)
    if not isinstance(max_row_count, int) or isinstance(max_row_count, bool) or max_row_count < 0:
        _fail("invalid_prepared_event_batch_capacity", "max_row_count", repr(max_row_count))
    logical_key = validate_numba_grouped_i64x2_order_indexed_binding_shape(program)
    required_source_fields = set(program.event_fields) - {logical_key}
    if set(event_columns) != required_source_fields:
        _fail(
            "event_device_column_schema_mismatch",
            "event_columns",
            f"expected {sorted(required_source_fields)}",
        )
    key0_name, key1_name = program.key_fields

    cuda, np = _import_numba_stack()
    source: dict[str, object] = {}
    row_count: int | None = None
    for name in (key0_name, key1_name, program.sum_field):
        value = event_columns[name]
        if not (
            hasattr(value, "__cuda_array_interface__")
            or hasattr(value, "copy_to_host")
        ):
            _fail(
                "device_resident_event_columns_required",
                f"event_columns.{name}",
                "host columns are not accepted by the device-resident binding",
            )
        device = cuda.as_cuda_array(value) if not hasattr(value, "copy_to_host") else value
        if len(tuple(device.shape)) != 1 or device.dtype != np.dtype(np.int64):
            _fail(
                "event_device_column_mismatch",
                f"event_columns.{name}",
                f"expected 1-D int64; got {getattr(device, 'dtype', None)}",
            )
        count = int(device.shape[0])
        if row_count is None:
            row_count = count
        elif row_count != count:
            _fail("event_column_length_mismatch", f"event_columns.{name}", str(count))
        # Establish private ownership once in source order.  The reduction will
        # later read these three columns through the compiler-owned order
        # permutation, avoiding a second four-column gather/materialization.
        owned_source = cuda.device_array(count, dtype=np.int64)
        owned_source.copy_to_device(device)
        source[name] = owned_source
    resolved_count = row_count or 0
    return _prepare_owned_numba_grouped_i64x2_count_sum_device_columns(
        program,
        source,
        row_count=resolved_count,
        max_row_count=max_row_count,
        native_order_context=native_order_context,
        ownership_origin="private_d2d_copy_from_caller_columns",
        completion_snapshot_device_to_device_copy_used=True,
    )


def prepare_numba_grouped_i64x2_count_sum_compiler_snapshot(
    program: NumbaGroupedI64x2CountSumProgram,
    event_columns: Mapping[str, object],
    *,
    max_row_count: int,
    native_order_context: GroupedI64x2NativeOrderContext | None = None,
    private_workspace: PreparedGroupedI64x2DeviceWorkspace | None = None,
    workspace_generation_digest: str | None = None,
) -> PreparedNumbaGroupedI64x2CountSumColumns:
    """Bind a detached compiler-owned device snapshot without copying it again.

    This entry is deliberately narrower than the ordinary device-column
    front door.  Its caller must already have revoked the producer write lease
    by taking the private D2D completion snapshot.  The existing native order
    and checked grouped reducer remain the only algorithms used here.
    """

    program = _validate_canonical_numba_grouped_i64x2_count_sum_program(program)
    if (
        not isinstance(max_row_count, int)
        or isinstance(max_row_count, bool)
        or max_row_count < 0
    ):
        _fail(
            "invalid_prepared_event_batch_capacity",
            "max_row_count",
            repr(max_row_count),
        )
    logical_key = validate_numba_grouped_i64x2_order_indexed_binding_shape(program)
    required_source_fields = set(program.event_fields) - {logical_key}
    if set(event_columns) != required_source_fields:
        _fail(
            "event_device_column_schema_mismatch",
            "event_columns",
            f"expected {sorted(required_source_fields)}",
        )
    cuda, np = _import_numba_stack()
    source: dict[str, object] = {}
    row_count: int | None = None
    for name in (*program.key_fields, program.sum_field):
        value = event_columns[name]
        if not (
            hasattr(value, "__cuda_array_interface__")
            or hasattr(value, "copy_to_host")
        ):
            _fail(
                "compiler_owned_device_snapshot_required",
                f"event_columns.{name}",
                "host columns are not accepted by the compiler snapshot binding",
            )
        device = (
            cuda.as_cuda_array(value)
            if not hasattr(value, "copy_to_host")
            else value
        )
        if len(tuple(device.shape)) != 1 or device.dtype != np.dtype(np.int64):
            _fail(
                "event_device_column_mismatch",
                f"event_columns.{name}",
                f"expected 1-D int64; got {getattr(device, 'dtype', None)}",
            )
        count = int(device.shape[0])
        if row_count is None:
            row_count = count
        elif row_count != count:
            _fail(
                "event_column_length_mismatch",
                f"event_columns.{name}",
                str(count),
            )
        source[name] = device
    return _prepare_owned_numba_grouped_i64x2_count_sum_device_columns(
        program,
        source,
        row_count=row_count or 0,
        max_row_count=max_row_count,
        native_order_context=native_order_context,
        ownership_origin="producer_completion_private_device_snapshot",
        completion_snapshot_device_to_device_copy_used=True,
        private_workspace=private_workspace,
        workspace_generation_digest=workspace_generation_digest,
    )


def _prepare_owned_numba_grouped_i64x2_count_sum_device_columns(
    program: NumbaGroupedI64x2CountSumProgram,
    source: Mapping[str, object],
    *,
    row_count: int,
    max_row_count: int,
    native_order_context: GroupedI64x2NativeOrderContext | None,
    ownership_origin: str,
    completion_snapshot_device_to_device_copy_used: bool,
    private_workspace: PreparedGroupedI64x2DeviceWorkspace | None = None,
    workspace_generation_digest: str | None = None,
) -> PreparedNumbaGroupedI64x2CountSumColumns:
    """Create the existing order-indexed reducer state from private columns."""

    resolved_count = row_count
    if resolved_count > max_row_count:
        _fail(
            "prepared_event_batch_capacity_exceeded",
            "event_columns",
            f"rows={resolved_count}; capacity={max_row_count}",
        )

    key0_name, key1_name = program.key_fields
    logical_key = validate_numba_grouped_i64x2_order_indexed_binding_shape(program)
    cuda, np = _import_numba_stack()
    if private_workspace is None:
        allocation_started = time.perf_counter()
        order = cuda.device_array(resolved_count, dtype=np.int64)
        sort_key0 = cuda.device_array(resolved_count, dtype=np.int64)
        sort_key1 = cuda.device_array(resolved_count, dtype=np.int64)
        zero_distance = cuda.device_array(resolved_count, dtype=np.float64)
        order_workspace_allocation_seconds = (
            time.perf_counter() - allocation_started
        )
    else:
        if (
            type(private_workspace) is not PreparedGroupedI64x2DeviceWorkspace
            or not isinstance(workspace_generation_digest, str)
        ):
            _fail(
                "prepared_private_workspace_binding_invalid",
                "private_workspace",
                type(private_workspace).__name__,
            )
        order, sort_key0, sort_key1, zero_distance = (
            private_workspace.order_resources(
                generation_digest=workspace_generation_digest,
                row_count=resolved_count,
            )
        )
        order_workspace_allocation_seconds = 0.0
    order_initialization_enqueue_seconds = 0.0
    native_order_seconds = 0.0
    if resolved_count:
        init_sort_columns, fill_f64, certify_gather = (
            _compiled_device_column_certificate_kernels(cuda)
        )
        threads = 256
        blocks = (resolved_count + threads - 1) // threads
        initialization_started = time.perf_counter()
        init_sort_columns[blocks, threads](
            source[key0_name],
            source[key1_name],
            order,
            sort_key0,
            sort_key1,
        )
        fill_f64[blocks, threads](zero_distance, 0.0)
        order_initialization_enqueue_seconds = (
            time.perf_counter() - initialization_started
        )
        context = native_order_context
        if context is None:
            _fail(
                "grouped_native_order_prerequisite_unavailable",
                "native_order_context",
                "compiler planning must bind the generic native ordering context",
            )
        if type(context) is not GroupedI64x2NativeOrderContext:
            _fail(
                "grouped_native_order_context_required",
                "native_order_context",
                type(context).__name__,
            )
        try:
            native_order_started = time.perf_counter()
            ordering = context.sort_i64_f64_i64_i64(
                sort_key0,
                zero_distance,
                sort_key1,
                order,
                row_count=resolved_count,
            )
            native_order_seconds = time.perf_counter() - native_order_started
        except (RuntimeError, TypeError, ValueError) as exc:
            _fail(
                "grouped_native_order_context_changed",
                "native_order_context",
                str(exc),
            )
    else:
        context = native_order_context
        ordering = None

    # Exact range, permutation, order, nonnegative, and signed-overflow checks
    # are fused into the one order-indexed reduction launch.  Result projection
    # reads the shared error word before exposing rows, so no unchecked payload
    # can escape while the standalone validation launch/synchronization vanish.
    pointer_payload = []
    for name in (key0_name, key1_name, program.sum_field):
        interface = getattr(source[name], "__cuda_array_interface__", {})
        pointer_payload.append((name, int(interface.get("data", (0,))[0])))
    order_interface = getattr(order, "__cuda_array_interface__", {})
    pointer_payload.append(
        ("compiler_order_indices", int(order_interface.get("data", (0,))[0]))
    )
    allocation_identity = hashlib.sha256(
        repr(
            (
                "rtdl.compiler_owned_device_event_columns.v1",
                program.spec.semantic_digest,
                resolved_count,
                tuple(pointer_payload),
                workspace_generation_digest,
            )
        ).encode("utf-8")
    ).hexdigest()
    certificate = {
        "contract": "rtdl.compiler_owned_device_event_column_batch.private_candidate.v1",
        "row_count": resolved_count,
        "schema_fields": list(program.event_fields),
        "logical_key_field": logical_key,
        "ordering_fields": [key0_name, key1_name, logical_key],
        "allocation_identity_digest": allocation_identity,
        "content_digest_claimed": False,
        "identity_basis": (
            f"{ownership_origin} plus live allocation identity"
        ),
        "device_to_device_copy_used": (
            completion_snapshot_device_to_device_copy_used
        ),
        "private_source_column_copy_count": 3,
        "private_source_columns_already_owned_at_reducer_prepare": (
            ownership_origin == "producer_completion_private_device_snapshot"
        ),
        "redundant_reducer_input_copy_avoided": (
            ownership_origin == "producer_completion_private_device_snapshot"
        ),
        "sorted_payload_gather_column_count": 0,
        "materialized_logical_key_column_count": 0,
        "physical_storage": "private_source_columns_plus_compiler_order_indices",
        "grouped_reduction_reads_through_order_indices": True,
        "device_to_host_payload_copy_used": False,
        "device_to_host_validation_status_words": 1,
        "source_order_permutation_verified_on_device": True,
        "duplicate_logical_keys_rejected_on_device": True,
        "lexicographic_order_verified_on_device": True,
        "validation_fused_into_checked_grouped_reduction": True,
        "standalone_validation_kernel_launch_count": 0,
        "standalone_validation_synchronization_count": 0,
        "caller_mutation_after_certificate_can_change_execution": False,
        "native_ordering_contract": (
            dict(ordering) if ordering is not None else None
        ),
        "observation_only_order_phase_timing_seconds": {
            "order_workspace_allocation_seconds": float(
                order_workspace_allocation_seconds
            ),
            "order_initialization_enqueue_seconds": float(
                order_initialization_enqueue_seconds
            ),
            "native_order_seconds": float(native_order_seconds),
            "explicit_synchronization_added_by_observation": False,
            "prepared_private_workspace_used": private_workspace is not None,
        },
        "prepared_private_workspace_used": private_workspace is not None,
        "workspace_generation_digest": workspace_generation_digest,
    }
    return PreparedNumbaGroupedI64x2CountSumColumns(
        program=program,
        event_columns=source,
        row_count=resolved_count,
        owns_event_columns=True,
        host_to_device_copy_used=False,
        device_to_device_copy_used=completion_snapshot_device_to_device_copy_used,
        device_certificate_metadata=certificate,
        order_indices=order,
        private_workspace=private_workspace,
        workspace_generation_digest=workspace_generation_digest,
    )


def execute_numba_grouped_i64x2_count_sum(
    prepared: PreparedNumbaGroupedI64x2CountSumColumns,
    *,
    block_size: int = 128,
) -> NumbaGroupedI64x2CountSumDeviceResult:
    """Reduce lexicographically grouped i64x2 rows on the device."""

    prepared.validate_integrity()
    if block_size <= 0 or block_size > 1024:
        _fail("invalid_block_size", "block_size", str(block_size))
    cuda, np = _import_numba_stack()
    capacity = prepared.row_count
    order_indices = prepared._execution_order_indices()
    private_workspace = prepared._private_workspace
    workspace_generation_digest = prepared._workspace_generation_digest
    reducer_workspace_reset_seconds = 0.0
    if private_workspace is None:
        allocation_started = time.perf_counter()
        key0 = cuda.device_array((capacity,), dtype=np.int64)
        key1 = cuda.device_array((capacity,), dtype=np.int64)
        counts = cuda.device_array((capacity,), dtype=np.uint64)
        sums = cuda.device_array((capacity,), dtype=np.int64)
        output_count = cuda.to_device(np.zeros(1, dtype=np.int64))
        error_flag = cuda.to_device(np.zeros(1, dtype=np.int32))
        permutation_seen = (
            cuda.to_device(np.zeros(prepared.row_count, dtype=np.int32))
            if order_indices is not None
            else None
        )
        reducer_workspace_allocation_seconds = (
            time.perf_counter() - allocation_started
        )
    else:
        (
            (
                key0,
                key1,
                counts,
                sums,
                output_count,
                error_flag,
                permutation_seen,
            ),
            reducer_workspace_reset_seconds,
        ) = private_workspace.reducer_resources(
            generation_digest=str(workspace_generation_digest),
            row_count=capacity,
        )
        reducer_workspace_allocation_seconds = 0.0
    reducer_kernel_enqueue_seconds = 0.0
    if prepared.row_count:
        global _GROUPED_I64X2_COUNT_SUM_KERNEL_LAUNCH_COUNT
        global _GROUPED_I64X2_ORDER_INDEXED_COUNT_SUM_KERNEL_LAUNCH_COUNT
        order_indexed = order_indices is not None
        kernel = (
            _compiled_grouped_i64x2_order_indexed_count_sum_kernel(cuda)
            if order_indexed
            else _compiled_grouped_i64x2_count_sum_kernel(cuda)
        )
        blocks = (prepared.row_count + block_size - 1) // block_size
        first_key, second_key = prepared.program.key_fields
        nonnegative_flags = (
            bool(prepared.program.spec.event_type.field(first_key).nonnegative),
            bool(prepared.program.spec.event_type.field(second_key).nonnegative),
            bool(
                prepared.program.spec.event_type.field(
                    prepared.program.sum_field
                ).nonnegative
            ),
        )
        arguments = (
            prepared._column(first_key),
            prepared._column(second_key),
            prepared._column(prepared.program.sum_field),
            *(
                (
                    order_indices,
                    permutation_seen,
                )
                if order_indexed
                else ()
            ),
            *nonnegative_flags,
            key0,
            key1,
            counts,
            sums,
            output_count,
            error_flag,
            prepared.row_count,
        )
        kernel_started = time.perf_counter()
        kernel[blocks, block_size](*arguments)
        reducer_kernel_enqueue_seconds = (
            time.perf_counter() - kernel_started
        )
        _GROUPED_I64X2_COUNT_SUM_KERNEL_LAUNCH_COUNT += 1
        if order_indexed:
            _GROUPED_I64X2_ORDER_INDEXED_COUNT_SUM_KERNEL_LAUNCH_COUNT += 1
    result = NumbaGroupedI64x2CountSumDeviceResult(
        program=prepared.program,
        key0=key0,
        key1=key1,
        counts=counts,
        sums=sums,
        output_count=output_count,
        error_flag=error_flag,
        permutation_seen=permutation_seen,
        capacity=capacity,
        input_owner=prepared,
        observation_timing_seconds={
            "reducer_workspace_allocation_seconds": float(
                reducer_workspace_allocation_seconds
            ),
            "reducer_kernel_enqueue_seconds": float(
                reducer_kernel_enqueue_seconds
            ),
            "reducer_workspace_reset_seconds": float(
                reducer_workspace_reset_seconds
            ),
            "prepared_private_workspace_used": private_workspace is not None,
            "explicit_synchronization_added_by_observation": False,
        },
        private_workspace=private_workspace,
        workspace_generation_digest=workspace_generation_digest,
    )
    prepared._register_result(result)
    return result


def eager_specialize_numba_grouped_i64x2_count_sum(
    program: NumbaGroupedI64x2CountSumProgram,
    *,
    native_order_context: GroupedI64x2NativeOrderContext | None = None,
) -> dict[str, object]:
    """Compile and execute the complete one-row device route during setup.

    This warms the device ordering certificate, checked grouped kernel, and
    host projection without charging the first registered query.  It is a
    compiler-owned setup action and is reported explicitly; it is not a hidden
    query or a runtime-speedup claim.
    """

    canonical = _validate_canonical_numba_grouped_i64x2_count_sum_program(program)
    cuda, np = _import_numba_stack()
    started = time.perf_counter()
    before = grouped_i64x2_count_sum_kernel_lifecycle_metadata()
    prepared = None
    result = None
    try:
        if native_order_context is None:
            # The canonical host-column route receives rows already ordered by
            # the verified compiler batch.  Warm that exact physical route;
            # do not invent a native ordering authority that the owner does
            # not possess.
            source = {
                name: np.asarray(
                    [1 if name == canonical.sum_field else 0],
                    dtype=np.int64,
                )
                for name in canonical.event_fields
            }
            prepared = prepare_numba_grouped_i64x2_count_sum_columns(
                canonical,
                source,
            )
        else:
            source = {
                canonical.key_fields[0]: cuda.to_device(
                    np.asarray([0], dtype=np.int64)),
                canonical.key_fields[1]: cuda.to_device(
                    np.asarray([0], dtype=np.int64)),
                canonical.sum_field: cuda.to_device(
                    np.asarray([1], dtype=np.int64)),
            }
            prepared = prepare_numba_grouped_i64x2_count_sum_device_columns(
                canonical,
                source,
                max_row_count=1,
                native_order_context=native_order_context,
            )
        result = execute_numba_grouped_i64x2_count_sum(prepared)
        reductions = result.to_host_reductions()
        by_name = {relation.name: tuple(relation.rows) for relation in reductions}
        if by_name != {
            canonical.count_reduction_name: (((0, 0), 1),),
            canonical.sum_reduction_name: (((0, 0), 1),),
        }:
            _fail(
                "grouped_i64x2_eager_specialization_result_invalid",
                "warmup.result",
                repr(by_name),
            )
        cuda.synchronize()
    finally:
        if result is not None:
            result.close()
        if prepared is not None:
            prepared.close()
    after = grouped_i64x2_count_sum_kernel_lifecycle_metadata()
    return {
        "contract": "rtdl.grouped_i64x2_eager_device_specialization.v1",
        "elapsed_seconds": float(time.perf_counter() - started),
        "synthetic_row_count": 1,
        "complete_physical_route_executed": True,
        "registered_query_count": 0,
        "kernel_launch_delta": int(after["kernel_launch_count"])
        - int(before["kernel_launch_count"]),
        "runtime_speedup_claimed": False,
    }


def compile_numba_action_continuation(
    spec: ActionSpec,
    *,
    discharged_delivery_proofs: frozenset[str] = frozenset(),
) -> NumbaActionProgram:
    """Lower the closed filter+emit Action IR subset without name dispatch."""

    verify_action_spec(spec)
    if spec.states or spec.reductions or spec.termination_proofs:
        _fail(
            "effect_subset_not_supported",
            "spec",
            "v1 Numba continuation supports filter+bounded-emit only; state/reduce/terminate require a later placement",
        )
    if (
        spec.logical_event.physical_delivery is not PhysicalDelivery.PROVEN_SINGLE
        or spec.logical_event.enforcement is not DeliveryEnforcement.PROVEN_SINGLE
    ):
        _fail(
            "single_delivery_not_discharged",
            "logical_event",
            "v1 continuation has no device dedup and therefore requires proven-single delivery",
        )
    proof_reference = spec.logical_event.proof_reference
    if not proof_reference or proof_reference not in discharged_delivery_proofs:
        _fail(
            "delivery_proof_not_discharged",
            "logical_event.proof_reference",
            "a placement-proven delivery certificate must be supplied; an IR string is not itself proof",
        )
    if len(spec.blocks) != 1:
        _fail("single_block_required", "blocks", "v1 continuation requires one straight-line block")
    if len(spec.emits) != 1:
        _fail("single_emit_required", "emits", "v1 continuation requires exactly one emit relation")
    if spec.emits[0].selection is not None:
        _fail(
            "bounded_selection_not_supported",
            "emits[0].selection",
            "v1 Numba continuation implements plain bounded emit, not per-scope bounded selection",
        )
    operations: list[ActionOp] = []
    for index, statement in enumerate(spec.blocks[0].operations):
        if isinstance(statement, ActionStaticLoop):
            _fail("static_loop_not_supported", f"blocks[0].operations[{index}]", "GPU v1 is straight-line")
        if statement.opcode not in _SUPPORTED_OPCODES:
            _fail(
                "opcode_not_supported_by_numba_placement",
                f"blocks[0].operations[{index}]",
                statement.opcode,
            )
        operations.append(statement)
    emit_count = sum(item.opcode == "emit" for item in operations)
    if emit_count != 1:
        _fail("one_emit_operation_required", "blocks[0]", f"found {emit_count}")
    source = _generate_kernel_source(spec, operations)
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    return NumbaActionProgram(
        spec=spec,
        kernel_source=source,
        kernel_code_digest=digest,
        event_fields=tuple(field.name for field in spec.event_type.fields),
        parameter_fields=tuple(field.name for field in spec.parameter_type.fields),
        emit=spec.emits[0],
        delivery_proof_reference=proof_reference,
    )


def prepare_numba_action_columns(
    program: NumbaActionProgram,
    event_columns: Mapping[str, object],
    parameters: Mapping[str, object],
) -> PreparedNumbaActionColumns:
    """Prepare or borrow RTDL-owned columns; never accepts user executable code."""

    cuda, np = _import_numba_stack()
    expected = set(program.event_fields)
    if set(event_columns) != expected:
        _fail("event_column_schema_mismatch", "event_columns", f"expected {sorted(expected)}")
    normalized_parameters = _normalize_parameters(program, parameters, np)
    prepared: dict[str, object] = {}
    row_count: int | None = None
    copied = False
    all_owned = True
    for field in program.spec.event_type.fields:
        expected_dtype = _numpy_dtype(field.value_type, np)
        value = event_columns[field.name]
        if hasattr(value, "__cuda_array_interface__") or hasattr(value, "copy_to_host"):
            device = cuda.as_cuda_array(value) if not hasattr(value, "copy_to_host") else value
            all_owned = False
        else:
            host = np.asarray(value)
            if host.ndim != 1 or host.dtype != expected_dtype or not host.flags.c_contiguous:
                _fail(
                    "event_column_layout_mismatch",
                    f"event_columns.{field.name}",
                    f"expected contiguous 1-D {expected_dtype}",
                )
            if field.nonnegative and bool(np.any(host < 0)):
                _fail("nonnegative_field_violation", f"event_columns.{field.name}", field.name)
            device = cuda.to_device(host)
            copied = True
        if len(tuple(device.shape)) != 1 or device.dtype != expected_dtype:
            _fail("event_device_column_mismatch", f"event_columns.{field.name}", str(device.dtype))
        count = int(device.shape[0])
        if row_count is None:
            row_count = count
        elif row_count != count:
            _fail("event_column_length_mismatch", f"event_columns.{field.name}", str(count))
        prepared[field.name] = device
    return PreparedNumbaActionColumns(
        program=program,
        event_columns=prepared,
        parameters=normalized_parameters,
        row_count=row_count or 0,
        owns_event_columns=all_owned,
        host_to_device_copy_used=copied,
    )


def execute_numba_action_continuation(
    prepared: PreparedNumbaActionColumns,
    *,
    extents: Mapping[ExtentKind | str, int],
    block_size: int = 128,
) -> NumbaActionDeviceResult:
    """Execute into device-resident output columns and return their lifetime owner."""

    if prepared.closed:
        _fail("prepared_columns_closed", "prepared", "prepared input owner is closed")
    cuda, np = _import_numba_stack()
    if block_size <= 0:
        _fail("invalid_block_size", "block_size", str(block_size))
    capacity_parameters = {
        name: int(value)
        for name, value in prepared.parameters.items()
        if isinstance(value, (int, np.integer)) and not isinstance(value, (bool, np.bool_))
    }
    try:
        capacity = evaluate_capacity(
            prepared.program.emit.capacity,
            extents=extents,
            parameters=capacity_parameters,
            allocator_limit=(1 << 63) - 1,
        )
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        _fail("capacity_evaluation_failed", "emit.capacity", str(exc))
    outputs = {
        field.name: cuda.device_array(capacity, dtype=_numpy_dtype(field.value_type, np))
        for field in prepared.program.emit.record_type.fields
    }
    output_count = cuda.to_device(np.zeros(1, dtype=np.int64))
    error_flag = cuda.to_device(np.zeros(1, dtype=np.int32))
    kernel = _compiled_kernel(prepared.program, cuda, np)
    arguments = [prepared.event_columns[name] for name in prepared.program.event_fields]
    arguments.extend(prepared.parameters[name] for name in prepared.program.parameter_fields)
    arguments.extend(outputs[field.name] for field in prepared.program.emit.record_type.fields)
    arguments.extend((output_count, error_flag, prepared.row_count, capacity))
    if prepared.row_count:
        blocks = (prepared.row_count + block_size - 1) // block_size
        kernel[blocks, block_size](*arguments)
    prepared.active_results += 1
    return NumbaActionDeviceResult(
        program=prepared.program,
        output_columns=outputs,
        output_count=output_count,
        error_flag=error_flag,
        capacity=capacity,
        input_owner=prepared,
    )


def _generate_kernel_source(spec: ActionSpec, operations: list[ActionOp]) -> str:
    event_fields = tuple(field.name for field in spec.event_type.fields)
    parameter_fields = tuple(field.name for field in spec.parameter_type.fields)
    emit = spec.emits[0]
    arguments = [f"event_{index}" for index in range(len(event_fields))]
    arguments += [f"param_{index}" for index in range(len(parameter_fields))]
    arguments += [f"output_{index}" for index in range(len(emit.record_type.fields))]
    arguments += ["output_count", "error_flag", "row_count", "capacity"]
    lines = [f"def _rtdl_action_kernel({', '.join(arguments)}):", "    row = cuda.grid(1)"]
    lines.append("    if row >= row_count:")
    lines.append("        return")
    event_index = {name: index for index, name in enumerate(event_fields)}
    event_specs = {field.name: field for field in spec.event_type.fields}
    param_index = {name: index for index, name in enumerate(parameter_fields)}
    value_types: dict[str, ActionScalarType] = {}
    for op in operations:
        opcode = op.opcode
        output_name = op.outputs[0].name if op.outputs else None
        if op.outputs:
            value_types[output_name] = op.outputs[0].value_type
        if opcode == "load_event":
            field_name = str(op.attribute("field"))
            lines.append(f"    {output_name} = event_{event_index[field_name]}[row]")
            if event_specs[field_name].nonnegative:
                lines.append(f"    if {output_name} < 0:")
                lines.append("        cuda.atomic.max(error_flag, 0, 3)")
                lines.append("        return")
            if op.outputs[0].value_type.is_float:
                lines.extend(_finite_guard(output_name))
        elif opcode == "load_param":
            field_name = str(op.attribute("field"))
            lines.append(f"    {output_name} = param_{param_index[field_name]}")
        elif opcode == "const":
            literal = op.attribute("literal")
            constructor = _kernel_scalar_constructor(op.outputs[0].value_type)
            lines.append(f"    {output_name} = {constructor}({literal.to_python()!r})")
        elif opcode == "compare":
            operator = {"eq": "==", "ne": "!=", "lt": "<", "le": "<=", "gt": ">", "ge": ">="}[
                str(op.attribute("predicate"))
            ]
            lines.append(f"    {output_name} = {op.inputs[0]} {operator} {op.inputs[1]}")
        elif opcode in {"bool_and", "bool_or"}:
            operator = "and" if opcode == "bool_and" else "or"
            lines.append(f"    {output_name} = {op.inputs[0]} {operator} {op.inputs[1]}")
        elif opcode == "bool_not":
            lines.append(f"    {output_name} = not {op.inputs[0]}")
        elif opcode in {"add", "sub", "mul"}:
            operator = {"add": "+", "sub": "-", "mul": "*"}[opcode]
            lines.append(f"    {output_name} = {op.inputs[0]} {operator} {op.inputs[1]}")
            if op.outputs[0].value_type.is_float:
                lines.extend(_finite_guard(output_name))
        elif opcode in {"min", "max"}:
            compare = "<=" if opcode == "min" else ">="
            lines.append(
                f"    {output_name} = {op.inputs[0]} if {op.inputs[0]} {compare} {op.inputs[1]} else {op.inputs[1]}"
            )
        elif opcode == "select":
            lines.append(f"    {output_name} = {op.inputs[1]} if {op.inputs[0]} else {op.inputs[2]}")
        elif opcode == "cast":
            constructor = _kernel_scalar_constructor(op.outputs[0].value_type)
            lines.append(f"    {output_name} = {constructor}({op.inputs[0]})")
        elif opcode == "filter":
            lines.append(f"    if not {op.inputs[0]}:")
            lines.append("        return")
        elif opcode == "emit":
            lines.append("    slot = cuda.atomic.add(output_count, 0, 1)")
            lines.append("    if slot >= capacity:")
            lines.append("        cuda.atomic.max(error_flag, 0, 2)")
            lines.append("        return")
            for index, value_name in enumerate(op.inputs):
                lines.append(f"    output_{index}[slot] = {value_name}")
        elif opcode == "ignore":
            lines.append("    return")
        elif opcode == "accept":
            lines.append("    pass")
        else:
            raise AssertionError(opcode)
    return "\n".join(lines) + "\n"


def _finite_guard(value_name: str) -> list[str]:
    return [
        f"    if not math.isfinite({value_name}):",
        "        cuda.atomic.max(error_flag, 0, 1)",
        "        return",
    ]


def _compiled_kernel(program: NumbaActionProgram, cuda, np):
    cached = _KERNEL_CACHE.get(program.kernel_code_digest)
    if cached is not None:
        return cached
    namespace = {"cuda": cuda, "math": math, "np": np}
    exec(compile(program.kernel_source, "<rtdl-action-kernel>", "exec"), namespace)
    kernel = cuda.jit(namespace["_rtdl_action_kernel"])
    _KERNEL_CACHE[program.kernel_code_digest] = kernel
    return kernel


def _compiled_device_column_certificate_kernels(cuda):
    global _DEVICE_COLUMN_CERTIFICATE_KERNELS
    if _DEVICE_COLUMN_CERTIFICATE_KERNELS is not None:
        return _DEVICE_COLUMN_CERTIFICATE_KERNELS

    @cuda.jit
    def init_sort_columns(source_key0, source_key1, order, sort_key0, sort_key1):
        index = cuda.grid(1)
        if index < order.shape[0]:
            order[index] = index
            sort_key0[index] = source_key0[index]
            sort_key1[index] = source_key1[index]

    @cuda.jit
    def fill_f64(values, value):
        index = cuda.grid(1)
        if index < values.shape[0]:
            values[index] = value

    @cuda.jit
    def certify_order(
        source_key0,
        source_key1,
        source_values,
        order,
        seen,
        error_flag,
        row_count,
    ):
        index = cuda.grid(1)
        if index >= row_count:
            return
        source_index = order[index]
        if source_index < 0 or source_index >= row_count:
            cuda.atomic.max(error_flag, 0, 1)
            return
        if cuda.atomic.cas(seen, source_index, 0, 1) != 0:
            cuda.atomic.max(error_flag, 0, 2)
            return
        key0 = source_key0[source_index]
        key1 = source_key1[source_index]
        value = source_values[source_index]
        if value < 0:
            cuda.atomic.max(error_flag, 0, 4)
            return
        if index > 0:
            previous_source = order[index - 1]
            if previous_source < 0 or previous_source >= row_count:
                cuda.atomic.max(error_flag, 0, 1)
                return
            previous0 = source_key0[previous_source]
            previous1 = source_key1[previous_source]
            if key0 < previous0 or (
                key0 == previous0
                and (
                    key1 < previous1
                    or (key1 == previous1 and source_index < previous_source)
                )
            ):
                cuda.atomic.max(error_flag, 0, 3)
                return
    _DEVICE_COLUMN_CERTIFICATE_KERNELS = (
        init_sort_columns,
        fill_f64,
        certify_order,
    )
    return _DEVICE_COLUMN_CERTIFICATE_KERNELS


def _compiled_certified_query_min_global_max_kernels(cuda):
    global _CERTIFIED_QUERY_MIN_GLOBAL_MAX_KERNELS
    if _CERTIFIED_QUERY_MIN_GLOBAL_MAX_KERNELS is not None:
        return _CERTIFIED_QUERY_MIN_GLOBAL_MAX_KERNELS

    @cuda.jit
    def mark_present_sources(present, error_flag, best_distances, source_ids, distances_f64, status, query_count, invalid_item_id):
        query_id = cuda.grid(1)
        if query_id == 0:
            status[0] = error_flag[0]
        if query_id < query_count:
            source_ids[query_id] = query_id if present[query_id] != 0 and error_flag[0] == 0 else invalid_item_id
            distances_f64[query_id] = best_distances[query_id]

    @cuda.jit
    def gather_winner_candidate(row_indices, valid_count, best_candidates, candidate_ids, invalid_item_id):
        if cuda.grid(1) == 0:
            candidate_ids[0] = (
                best_candidates[row_indices[0]] if valid_count[0] > 0 else invalid_item_id
            )

    _CERTIFIED_QUERY_MIN_GLOBAL_MAX_KERNELS = (mark_present_sources, gather_winner_candidate)
    return _CERTIFIED_QUERY_MIN_GLOBAL_MAX_KERNELS


def _compiled_grouped_i64x2_count_sum_kernel(cuda):
    global _GROUPED_I64X2_COUNT_SUM_KERNEL
    global _GROUPED_I64X2_COUNT_SUM_KERNEL_CONSTRUCT_COUNT
    global _GROUPED_I64X2_COUNT_SUM_KERNEL_LOOKUP_COUNT
    _GROUPED_I64X2_COUNT_SUM_KERNEL_LOOKUP_COUNT += 1
    if _GROUPED_I64X2_COUNT_SUM_KERNEL is not None:
        return _GROUPED_I64X2_COUNT_SUM_KERNEL

    max_i64 = (1 << 63) - 1
    min_i64 = -(1 << 63)

    @cuda.jit
    def grouped_i64x2_count_sum(
        input_key0,
        input_key1,
        input_values,
        require_nonnegative_key0,
        require_nonnegative_key1,
        require_nonnegative_value,
        output_key0,
        output_key1,
        output_counts,
        output_sums,
        output_count,
        error_flag,
        row_count,
    ):
        index = cuda.grid(1)
        if index >= row_count:
            return
        current0 = input_key0[index]
        current1 = input_key1[index]
        current_value = input_values[index]
        if require_nonnegative_key0 and current0 < 0:
            cuda.atomic.max(error_flag, 0, 5)
            return
        if require_nonnegative_key1 and current1 < 0:
            cuda.atomic.max(error_flag, 0, 6)
            return
        if require_nonnegative_value and current_value < 0:
            cuda.atomic.max(error_flag, 0, 7)
            return
        if index > 0:
            previous0 = input_key0[index - 1]
            previous1 = input_key1[index - 1]
            if current0 < previous0 or (current0 == previous0 and current1 < previous1):
                cuda.atomic.max(error_flag, 0, 1)
                return
            if current0 == previous0 and current1 == previous1:
                return

        total = 0
        count = 0
        cursor = index
        while cursor < row_count:
            key0 = input_key0[cursor]
            key1 = input_key1[cursor]
            if key0 != current0 or key1 != current1:
                break
            value = input_values[cursor]
            if (value > 0 and total > max_i64 - value) or (
                value < 0 and total < min_i64 - value
            ):
                cuda.atomic.max(error_flag, 0, 2)
                return
            total += value
            count += 1
            cursor += 1

        slot = cuda.atomic.add(output_count, 0, 1)
        output_key0[slot] = current0
        output_key1[slot] = current1
        output_counts[slot] = count
        output_sums[slot] = total

    _GROUPED_I64X2_COUNT_SUM_KERNEL = grouped_i64x2_count_sum
    _GROUPED_I64X2_COUNT_SUM_KERNEL_CONSTRUCT_COUNT += 1
    return _GROUPED_I64X2_COUNT_SUM_KERNEL


def _compiled_grouped_i64x2_order_indexed_count_sum_kernel(cuda):
    """Reduce private source columns directly through a certified permutation."""

    global _GROUPED_I64X2_ORDER_INDEXED_COUNT_SUM_KERNEL
    global _GROUPED_I64X2_ORDER_INDEXED_COUNT_SUM_KERNEL_CONSTRUCT_COUNT
    global _GROUPED_I64X2_ORDER_INDEXED_COUNT_SUM_KERNEL_LOOKUP_COUNT
    _GROUPED_I64X2_ORDER_INDEXED_COUNT_SUM_KERNEL_LOOKUP_COUNT += 1
    if _GROUPED_I64X2_ORDER_INDEXED_COUNT_SUM_KERNEL is not None:
        return _GROUPED_I64X2_ORDER_INDEXED_COUNT_SUM_KERNEL

    max_i64 = (1 << 63) - 1
    min_i64 = -(1 << 63)

    @cuda.jit
    def grouped_i64x2_order_indexed_count_sum(
        source_key0,
        source_key1,
        source_values,
        order_indices,
        permutation_seen,
        require_nonnegative_key0,
        require_nonnegative_key1,
        require_nonnegative_value,
        output_key0,
        output_key1,
        output_counts,
        output_sums,
        output_count,
        error_flag,
        row_count,
    ):
        index = cuda.grid(1)
        if index >= row_count:
            return
        source_index = order_indices[index]
        if source_index < 0 or source_index >= row_count:
            cuda.atomic.max(error_flag, 0, 3)
            return
        if cuda.atomic.cas(permutation_seen, source_index, 0, 1) != 0:
            cuda.atomic.max(error_flag, 0, 4)
            return
        source_value = source_values[source_index]
        current0 = source_key0[source_index]
        current1 = source_key1[source_index]
        if require_nonnegative_key0 and current0 < 0:
            cuda.atomic.max(error_flag, 0, 5)
            return
        if require_nonnegative_key1 and current1 < 0:
            cuda.atomic.max(error_flag, 0, 6)
            return
        if require_nonnegative_value and source_value < 0:
            cuda.atomic.max(error_flag, 0, 7)
            return
        if index > 0:
            previous_source = order_indices[index - 1]
            if previous_source < 0 or previous_source >= row_count:
                cuda.atomic.max(error_flag, 0, 3)
                return
            previous0 = source_key0[previous_source]
            previous1 = source_key1[previous_source]
            if current0 < previous0 or (current0 == previous0 and current1 < previous1):
                cuda.atomic.max(error_flag, 0, 1)
                return
            if current0 == previous0 and current1 == previous1:
                return

        total = 0
        count = 0
        cursor = index
        while cursor < row_count:
            ordered_source = order_indices[cursor]
            if ordered_source < 0 or ordered_source >= row_count:
                cuda.atomic.max(error_flag, 0, 3)
                return
            key0 = source_key0[ordered_source]
            key1 = source_key1[ordered_source]
            if key0 != current0 or key1 != current1:
                break
            value = source_values[ordered_source]
            if (value > 0 and total > max_i64 - value) or (
                value < 0 and total < min_i64 - value
            ):
                cuda.atomic.max(error_flag, 0, 2)
                return
            total += value
            count += 1
            cursor += 1

        slot = cuda.atomic.add(output_count, 0, 1)
        output_key0[slot] = current0
        output_key1[slot] = current1
        output_counts[slot] = count
        output_sums[slot] = total

    _GROUPED_I64X2_ORDER_INDEXED_COUNT_SUM_KERNEL = (
        grouped_i64x2_order_indexed_count_sum
    )
    _GROUPED_I64X2_ORDER_INDEXED_COUNT_SUM_KERNEL_CONSTRUCT_COUNT += 1
    return _GROUPED_I64X2_ORDER_INDEXED_COUNT_SUM_KERNEL


def grouped_i64x2_count_sum_kernel_lifecycle_metadata() -> dict[str, object]:
    """Describe compiler-owned dispatcher reuse without compiling or launching it."""

    kernel = _GROUPED_I64X2_COUNT_SUM_KERNEL
    overloads = getattr(kernel, "overloads", {}) if kernel is not None else {}
    compiled_signature_count = len(overloads) if hasattr(overloads, "__len__") else None
    order_kernel = _GROUPED_I64X2_ORDER_INDEXED_COUNT_SUM_KERNEL
    order_overloads = (
        getattr(order_kernel, "overloads", {}) if order_kernel is not None else {}
    )
    order_signature_count = (
        len(order_overloads) if hasattr(order_overloads, "__len__") else None
    )
    return {
        "contract": "rtdl.numba_grouped_i64x2_kernel_lifecycle.private_candidate.v1",
        "dispatcher_construct_count": _GROUPED_I64X2_COUNT_SUM_KERNEL_CONSTRUCT_COUNT,
        "dispatcher_lookup_count": _GROUPED_I64X2_COUNT_SUM_KERNEL_LOOKUP_COUNT,
        "kernel_launch_count": _GROUPED_I64X2_COUNT_SUM_KERNEL_LAUNCH_COUNT,
        "compiled_signature_count": compiled_signature_count,
        "order_indexed_dispatcher_construct_count": (
            _GROUPED_I64X2_ORDER_INDEXED_COUNT_SUM_KERNEL_CONSTRUCT_COUNT
        ),
        "order_indexed_dispatcher_lookup_count": (
            _GROUPED_I64X2_ORDER_INDEXED_COUNT_SUM_KERNEL_LOOKUP_COUNT
        ),
        "order_indexed_kernel_launch_count": (
            _GROUPED_I64X2_ORDER_INDEXED_COUNT_SUM_KERNEL_LAUNCH_COUNT
        ),
        "order_indexed_compiled_signature_count": order_signature_count,
        "row_count_participates_in_signature": False,
        "compiler_owned": True,
        "application_selected_kernel": False,
    }


def _compiled_certified_query_min_kernels(cuda):
    global _CERTIFIED_QUERY_MIN_KERNELS
    if _CERTIFIED_QUERY_MIN_KERNELS is not None:
        return _CERTIFIED_QUERY_MIN_KERNELS

    @cuda.jit
    def validate_order(query_ids, candidate_ids, distances, error_flag, row_count, query_count):
        row = cuda.grid(1)
        if row >= row_count:
            return
        query_id = query_ids[row]
        distance = distances[row]
        if distance != distance:
            cuda.atomic.max(error_flag, 0, 1)
            return
        if query_id >= query_count:
            cuda.atomic.max(error_flag, 0, 2)
            return
        if row == 0:
            return
        previous_query = query_ids[row - 1]
        if query_id < previous_query:
            cuda.atomic.max(error_flag, 0, 3)
            return
        if query_id != previous_query:
            return
        previous_distance = distances[row - 1]
        if distance < previous_distance:
            cuda.atomic.max(error_flag, 0, 4)
            return
        distances_equal = not (distance < previous_distance) and not (previous_distance < distance)
        if distances_equal and candidate_ids[row] <= candidate_ids[row - 1]:
            cuda.atomic.max(error_flag, 0, 5)

    @cuda.jit
    def write_first_state(
        query_ids,
        candidate_ids,
        distances,
        best_distances,
        best_candidates,
        present,
        error_flag,
        row_count,
    ):
        row = cuda.grid(1)
        if row >= row_count or error_flag[0] != 0:
            return
        if row > 0 and query_ids[row] == query_ids[row - 1]:
            return
        distance = distances[row]
        # This mirrors the IR's strict `distance < +inf` state guard.
        if distance < float("inf"):
            query_id = query_ids[row]
            best_distances[query_id] = distance
            best_candidates[query_id] = candidate_ids[row]
            present[query_id] = 1

    _CERTIFIED_QUERY_MIN_KERNELS = (validate_order, write_first_state)
    return _CERTIFIED_QUERY_MIN_KERNELS


def _normalize_parameters(program: NumbaActionProgram, values: Mapping[str, object], np):
    expected = set(program.parameter_fields)
    if set(values) != expected:
        _fail("parameter_schema_mismatch", "parameters", f"expected {sorted(expected)}")
    normalized: dict[str, object] = {}
    for field in program.spec.parameter_type.fields:
        scalar_type = field.value_type
        value = values[field.name]
        dtype = _numpy_dtype(scalar_type, np)
        if scalar_type.kind is ActionScalarKind.BOOL:
            if not isinstance(value, (bool, np.bool_)):
                _fail("parameter_type_mismatch", f"parameters.{field.name}", "bool required")
        elif scalar_type.is_integer:
            if not isinstance(value, (int, np.integer)) or isinstance(value, (bool, np.bool_)):
                _fail("parameter_type_mismatch", f"parameters.{field.name}", "integer required")
            limits = np.iinfo(dtype)
            if int(value) < int(limits.min) or int(value) > int(limits.max):
                _fail("parameter_type_mismatch", f"parameters.{field.name}", "integer out of range")
        elif scalar_type.is_float:
            if not isinstance(value, (int, float, np.integer, np.floating)) or isinstance(
                value, (bool, np.bool_)
            ):
                _fail("parameter_type_mismatch", f"parameters.{field.name}", "numeric required")
        try:
            scalar = dtype.type(value)
        except (TypeError, ValueError, OverflowError) as exc:
            _fail("parameter_type_mismatch", f"parameters.{field.name}", str(exc))
        python_value = _python_scalar(scalar)
        if field.nonnegative and python_value < 0:
            _fail("nonnegative_field_violation", f"parameters.{field.name}", field.name)
        if scalar_type.is_float:
            if math.isnan(float(python_value)) or (
                math.isinf(float(python_value)) and not program.spec.numeric_contract.allow_infinity
            ):
                _fail("nonfinite_parameter", f"parameters.{field.name}", str(python_value))
        normalized[field.name] = scalar
    return normalized


def _numpy_dtype(value_type: ActionScalarType, np):
    mapping = {
        ActionScalarKind.BOOL: np.dtype(np.bool_),
        ActionScalarKind.I32: np.dtype(np.int32),
        ActionScalarKind.I64: np.dtype(np.int64),
        ActionScalarKind.U32: np.dtype(np.uint32),
        ActionScalarKind.U64: np.dtype(np.uint64),
        ActionScalarKind.F32: np.dtype(np.float32),
        ActionScalarKind.F64: np.dtype(np.float64),
    }
    return mapping[value_type.kind]


def _kernel_scalar_constructor(value_type: ActionScalarType) -> str:
    return {
        ActionScalarKind.BOOL: "np.bool_",
        ActionScalarKind.I32: "np.int32",
        ActionScalarKind.I64: "np.int64",
        ActionScalarKind.U32: "np.uint32",
        ActionScalarKind.U64: "np.uint64",
        ActionScalarKind.F32: "np.float32",
        ActionScalarKind.F64: "np.float64",
    }[value_type.kind]


def _python_scalar(value):
    return value.item() if hasattr(value, "item") else value


def _import_numba_stack():
    try:
        import numpy as np

        try:
            import _numba_cuda_redirector  # noqa: F401
        except ImportError:
            pass
        from numba import cuda
    except ImportError as exc:
        raise ModuleNotFoundError("Numba Action continuation requires numpy, numba, and CUDA") from exc
    if not cuda.is_available():
        raise RuntimeError("Numba Action continuation requires an available CUDA runtime")
    return cuda, np


def _fail(code: str, path: str, message: str) -> NoReturn:
    raise ActionPlacementError(ActionPlacementIssue(code, path, message))

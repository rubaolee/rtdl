"""Partner-resident execution for the verified V4 triangle count family.

The application owns graph-to-geometry segmentation and the paper algorithm.
This module only binds already-resident CuPy columns to the same verified
built-in-triangle callback executable used by the host-array runtime.
"""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re

from .physical_execution_provenance import (
    CapturedTraversalObservation,
    OptixTraversalAuditSession,
)
from .v4_checked_u64_device_reduction import (
    CheckedU64WeightedReduction,
    checked_u64_downstream_operation_sha256,
    checked_u64_weighted_sum_device,
    checked_u64_weighted_sum_unfused_device,
)
from .v4_fusion_ablation import (
    FusionAblationPlan,
    FusionVariant,
    verify_fusion_ablation_plan,
)
from .v4_operation_evidence import (
    OperationTrace,
    preverify_operation_trace_authority,
)
from .v4_triangle_reduction import (
    MetadataDomain,
    ReducerAlgebra,
    compile_triangle_reduction_abi,
    compile_triangle_reduction_contract,
    verify_triangle_reduction_schema,
)
from .v4_triangle_reduction_optix_compiler import (
    consume_verified_triangle_reduction_executable,
)
from .v4_triangle_reduction_optix_runtime import _digest, _native_path


_U64_MAX = (1 << 64) - 1
_SHA256 = re.compile(r"[0-9a-f]{64}")
_FUSION_EXECUTION_TOKEN_ISSUER = object()
_TRIANGLE_KEYS = (
    "ids", "x0", "y0", "z0", "x1", "y1", "z1", "x2", "y2", "z2")
_RAY_KEYS = ("ids", "ox", "oy", "oz", "dx", "dy", "dz", "tmax")


class FusionExecutionTokenError(RuntimeError):
    """Stable fail-closed diagnostic for process-local execution tokens."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"V4 fusion execution token rejected: {code}: {message}")


def _token_fail(code: str, message: str) -> None:
    raise FusionExecutionTokenError(code, message)


def _token_u64(value: object, name: str, *, positive: bool = False) -> int:
    if type(value) is not int or value < 0 or value > _U64_MAX:
        _token_fail("token_integer", f"{name} must be an unsigned 64-bit integer")
    if positive and value == 0:
        _token_fail("token_integer", f"{name} must be positive")
    return value


def _token_sha(value: object, name: str) -> str:
    if type(value) is not str or _SHA256.fullmatch(value) is None:
        _token_fail("token_sha256", f"{name} must be a lowercase SHA-256")
    return value


class VerifiedFusionExecutionToken:
    """Opaque, single-use admission for one measured fusion segment.

    The owning executor performs all recursive plan, target, recipe and
    operation-contract validation before issuing this token.  Execution only
    checks fixed-size process/owner/identity/descriptor/count bindings.  The
    token is deliberately process-local and cannot be copied or serialized.
    """

    __slots__ = (
        "_owner_key", "_creator_pid", "_executor_identity", "_cupy_version",
        "_segment_ordinal", "_primitive_count", "_query_count",
        "_segment_descriptor_sha256", "_plan_input_sha256", "_plan",
        "_trace_authority", "_state",
    )

    def __init__(
        self,
        *,
        owner_key: object,
        creator_pid: int,
        executor_identity: tuple[object, ...],
        cupy_version: str,
        segment_ordinal: int,
        primitive_count: int,
        query_count: int,
        segment_descriptor_sha256: str,
        plan_input_sha256: str,
        plan: FusionAblationPlan,
        trace_authority: object,
        _issuer: object,
    ) -> None:
        if _issuer is not _FUSION_EXECUTION_TOKEN_ISSUER:
            raise TypeError("verified fusion execution token is opaque")
        self._owner_key = owner_key
        self._creator_pid = creator_pid
        self._executor_identity = executor_identity
        self._cupy_version = cupy_version
        self._segment_ordinal = segment_ordinal
        self._primitive_count = primitive_count
        self._query_count = query_count
        self._segment_descriptor_sha256 = segment_descriptor_sha256
        self._plan_input_sha256 = plan_input_sha256
        self._plan = plan
        self._trace_authority = trace_authority
        self._state = "fresh"

    @property
    def state(self) -> str:
        return self._state

    @property
    def plan_sha256(self) -> str:
        return self._plan.plan_sha256

    @property
    def segment_descriptor_sha256(self) -> str:
        return self._segment_descriptor_sha256

    @property
    def plan_input_sha256(self) -> str:
        return self._plan_input_sha256

    def __copy__(self):
        raise TypeError("verified fusion execution token is not copyable")

    def __deepcopy__(self, _memo):
        raise TypeError("verified fusion execution token is not copyable")

    def __reduce__(self):
        raise TypeError("verified fusion execution token is not serializable")

    def _consume(self) -> None:
        if self._state != "fresh":
            _token_fail("token_replay", f"token state is {self._state}")
        # Consumption precedes every remaining check.  A failed, cross-owner or
        # forked attempt cannot leave a reusable admission behind.
        self._state = "consumed"

    def _validate_entry(
        self, *,
        owner_key: object,
        creator_pid: int,
        executor_identity: tuple[object, ...],
        segment_ordinal: object,
        segment_descriptor_sha256: object,
        legacy_arguments_present: bool,
    ) -> tuple[FusionAblationPlan, object]:
        if self._state != "consumed":
            _token_fail("token_state", f"token state is {self._state}")
        if legacy_arguments_present:
            _token_fail("token_api_conflict", "token and legacy plan/nonce are exclusive")
        if self._owner_key is not owner_key:
            _token_fail("token_wrong_owner", "token belongs to another executor")
        if self._creator_pid != creator_pid:
            _token_fail("token_wrong_process", "token crossed a process boundary")
        if self._executor_identity != executor_identity:
            _token_fail("token_identity_drift", "executor live identity changed")
        if type(segment_ordinal) is not int \
                or self._segment_ordinal != segment_ordinal:
            _token_fail("token_segment_ordinal", "segment ordinal mismatch")
        if type(segment_descriptor_sha256) is not str \
                or self._segment_descriptor_sha256 != segment_descriptor_sha256:
            _token_fail("token_segment_descriptor", "segment descriptor mismatch")
        return self._plan, self._trace_authority

    def _check_live_cupy_and_counts(
        self,
        *,
        cupy_version: object,
        primitive_count: int,
        query_count: int,
    ) -> None:
        if self._cupy_version != cupy_version:
            _token_fail("token_identity_drift", "live CuPy identity changed")
        if type(primitive_count) is not int \
                or self._primitive_count != primitive_count:
            _token_fail("token_primitive_count", "primitive count mismatch")
        if type(query_count) is not int or self._query_count != query_count:
            _token_fail("token_query_count", "query count mismatch")


@dataclass(frozen=True, slots=True)
class UnsealedTriangleSegmentExecution:
    """Device-complete segment whose evidence is sealed after the timer.

    Native prepare/execute/destroy, the declared downstream reducer, all host
    synchronizations and native traversal-audit capture have completed before
    this object is returned.  Receipt dictionaries and SHA chains have not.
    A caller must either call :meth:`seal` outside the registered timer or
    abort the item; no unsealed item is serializable evidence.
    """

    reduced_output: int
    role_counters: tuple[int, ...]
    triangle_count: int
    query_count: int
    reduction: CheckedU64WeightedReduction | None
    fusion_ablation_plan: FusionAblationPlan | None
    operation_trace: OperationTrace | None
    traversal_observation: CapturedTraversalObservation
    authority_nonce: str
    contract_sha256: str
    abi_sha256: str
    composed_program_sha256: str
    native_library_sha256: str
    _state: str = "device_complete_unsealed"

    @property
    def state(self) -> str:
        return self._state

    def abort(self) -> None:
        if self._state == "device_complete_unsealed":
            if self.operation_trace is not None:
                self.operation_trace.abort()
            object.__setattr__(self, "_state", "aborted")

    def seal(self) -> dict[str, object]:
        """Seal traversal and operation receipts outside the device timer."""

        if self._state != "device_complete_unsealed":
            raise RuntimeError(f"triangle segment evidence state is {self._state}")
        try:
            output_sha = _digest(self.reduced_output)
            traversal = self.traversal_observation.build_receipt(
                semantic_digest=_digest({
                    "authority": self.authority_nonce,
                    "contract": self.contract_sha256,
                    "abi": self.abi_sha256,
                    "composed_ptx": self.composed_program_sha256,
                    "native": self.native_library_sha256,
                    "device_column_count": True,
                }),
                output_digest=output_sha,
                route_identity=(
                    "v4_builtin_triangle_callback_ir:"
                    "partner_resident_checked_count_v1"),
            )
            if traversal["physical_executor_classification"] \
                    != "optix_traversal_observed":
                raise RuntimeError(
                    "V4 device-column segment lacked bound traversal")
            operation_receipt = None
            if self.operation_trace is not None:
                operation_receipt = self.operation_trace.seal(
                    output_sha256=output_sha,
                    traversal_receipt_sha256=traversal["receipt_sha256"],
                ).to_dict()
            reduction_receipt = None
            if self.reduction is not None:
                if self.reduction.maximum_value_is_device_observed:
                    maximum_value_provenance = "device_observed"
                elif self.fusion_ablation_plan is not None \
                        and self.fusion_ablation_plan.variant \
                        is FusionVariant.FUSION_OFF:
                    maximum_value_provenance = (
                        "optix_producer_declared_primitive_bound"
                    )
                else:
                    raise RuntimeError(
                        "checked-U64 maximum-value provenance is unsupported"
                    )
                reduction_receipt = {
                    "schema": "rtdl.v4.checked_u64_weighted_reduction.receipt.v1",
                    "maximum_value": self.reduction.maximum_value,
                    "maximum_weight": self.reduction.maximum_weight,
                    "weight_sum": self.reduction.weight_sum,
                    "value_count": self.reduction.value_count,
                    "value_upper_bound": self.reduction.value_upper_bound,
                    "device_kernel_launch_count": (
                        self.reduction.device_kernel_launch_count),
                    "host_synchronization_count": (
                        self.reduction.host_synchronization_count),
                    "logical_reduction_count": (
                        self.reduction.logical_reduction_count),
                    "device_materialization_count": (
                        self.reduction.device_materialization_count),
                    "operation_counts_event_derived": (
                        self.reduction.operation_counts_event_derived),
                    "maximum_value_is_device_observed": (
                        self.reduction.maximum_value_is_device_observed),
                    "maximum_value_provenance": maximum_value_provenance,
                    "provisional_sum_trusted_only_after_bounds": True,
                }
            result = {
                "reduced_output": self.reduced_output,
                "role_counters": self.role_counters,
                "traversal_receipt": traversal,
                "output_sha256": output_sha,
                "native_library_sha256": self.native_library_sha256,
                "device_columns_preserved": True,
                "per_ray_host_materialized": False,
                "triangle_count": self.triangle_count,
                "query_count": self.query_count,
                "checked_u64_weighted_reduction": reduction_receipt,
                "fusion_ablation_plan_sha256": (
                    None if self.fusion_ablation_plan is None
                    else self.fusion_ablation_plan.plan_sha256),
                "operation_evidence_receipt": operation_receipt,
            }
        except BaseException:
            self.abort()
            raise
        object.__setattr__(self, "_state", "sealed")
        return result


def _configure(library):
    prepare = getattr(
        library,
        "rtdl_optix_v4_prepare_triangle_reduction_device_columns_count_v1",
        None,
    )
    execute = getattr(
        library,
        "rtdl_optix_v4_execute_prepared_triangle_reduction_device_columns_count_v1",
        None,
    )
    destroy = getattr(
        library, "rtdl_optix_v4_destroy_prepared_triangle_reduction_callback_v1",
        None,
    )
    if prepare is None or execute is None or destroy is None:
        raise RuntimeError("native library lacks V4 device-column triangle count ABI")
    prepare.argtypes = [
        ctypes.c_char_p,
        *([ctypes.c_void_p] * 9), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t,
    ]
    execute.argtypes = [
        ctypes.c_uint64,
        *([ctypes.c_void_p] * 7), ctypes.c_size_t, ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t,
    ]
    destroy.argtypes = [
        ctypes.c_uint64, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
    for symbol in (prepare, execute, destroy):
        symbol.restype = ctypes.c_int
    return prepare, execute, destroy


def _raise(status: int, error, label: str) -> None:
    if status:
        raise RuntimeError(
            error.value.decode("utf-8", errors="replace") or
            f"{label} failed with status {status}")


def _device_columns(cp, columns, keys, *, floating: frozenset[str]):
    if set(columns) != set(keys):
        raise ValueError(f"device columns must contain exactly {keys!r}")
    result = {}
    count = None
    device_id = None
    for key in keys:
        value = columns[key]
        if not isinstance(value, cp.ndarray):
            raise TypeError(f"{key} must be an existing CuPy array")
        expected = cp.float64 if key in floating else cp.uint32
        if value.dtype != expected or value.ndim != 1 or not value.flags.c_contiguous:
            raise TypeError(f"{key} must be contiguous one-dimensional {expected}")
        if count is None:
            count = int(value.size)
            device_id = int(value.device.id)
        elif int(value.size) != count or int(value.device.id) != device_id:
            raise ValueError("device columns must have one count and device")
        result[key] = value
    if not count:
        raise ValueError("device columns must be nonempty")
    ids = result["ids"]
    if not bool(cp.all(ids == cp.arange(count, dtype=cp.uint32)).item()):
        raise ValueError("device column IDs must be canonical launch order")
    return result, count, device_id


class VerifiedTriangleDeviceColumnCountExecutor:
    """One verified callback program reused across bounded device segments."""

    def __init__(
        self, *, authority, contract, abi, any_hit_proof_authority,
        executable, library=None, native_library_path=None,
    ):
        fresh = verify_triangle_reduction_schema(
            authority.callback, authority.schema, target=authority.target)
        if (
            fresh != authority or
            compile_triangle_reduction_abi(
                fresh, any_hit_proof_authority=any_hit_proof_authority) != abi or
            compile_triangle_reduction_contract(
                fresh, abi_sha256=abi.abi_sha256) != contract
        ):
            raise RuntimeError("triangle device-column authority/ABI/contract drift")
        if fresh.schema.reducer.algebra not in {
            ReducerAlgebra.CHECKED_U64_SUM,
            ReducerAlgebra.CHECKED_U64_PRODUCT_SUM,
        }:
            raise ValueError("device-column route accepts only checked U64 count reducers")
        primitive_channels = tuple(
            channel for channel in fresh.schema.metadata_channels
            if channel.domain is MetadataDomain.PRIMITIVE)
        if primitive_channels:
            raise ValueError("device-column count route rejects primitive metadata")
        query_channels = tuple(
            channel.semantic_id for channel in fresh.schema.metadata_channels
            if channel.domain is MetadataDomain.QUERY)
        expected_query = (
            () if fresh.schema.reducer.algebra is ReducerAlgebra.CHECKED_U64_SUM
            else ("query.weight",))
        if query_channels != expected_query:
            raise ValueError("device-column count route has an unexpected query schema")
        composed_ptx = consume_verified_triangle_reduction_executable(
            executable, fresh, contract, abi,
            any_hit_proof_authority=any_hit_proof_authority)
        if library is None:
            from . import optix_runtime
            library = optix_runtime._load_optix_library()
        native_path = _native_path(library, native_library_path)
        native_sha = hashlib.sha256(Path(native_path).read_bytes()).hexdigest()
        if native_sha != fresh.target.native_sha256:
            raise RuntimeError("executed native bytes do not match target authority")
        self._fresh = fresh
        self._contract = contract
        self._abi = abi
        self._library = library
        self._prepare, self._execute, self._destroy = _configure(library)
        self._composed_ptx = composed_ptx
        self._composed_ptx_sha = hashlib.sha256(composed_ptx.encode()).hexdigest()
        self._native_sha = native_sha
        self._closed = False
        self._fusion_execution_owner_key = object()

    @property
    def native_library_sha256(self) -> str:
        return self._native_sha

    @property
    def composed_program_sha256(self) -> str:
        return self._composed_ptx_sha

    @property
    def callback_ir_sha256(self) -> str:
        return self._fresh.callback.ir_sha256

    @property
    def callback_authority_nonce(self) -> str:
        return self._fresh.authority_nonce

    @property
    def contract_sha256(self) -> str:
        return self._contract.contract_sha256

    @property
    def abi_sha256(self) -> str:
        return self._abi.abi_sha256

    @property
    def target_identity_sha256(self) -> str:
        return self._fresh.target.target_sha256

    def _fusion_owner_key(self) -> object:
        # Test doubles and preserved legacy constructors may predate the token
        # field.  Lazy creation occurs only during pre-timer admission.
        if not hasattr(self, "_fusion_execution_owner_key"):
            self._fusion_execution_owner_key = object()
        return self._fusion_execution_owner_key

    def _fusion_executor_live_identity(self) -> tuple[object, ...]:
        """Return the fixed-size identity checked by a process-local token."""

        return (
            id(self),
            id(self._library),
            id(self._prepare),
            id(self._execute),
            id(self._destroy),
            self._fresh.callback.ir_sha256,
            self._fresh.authority_nonce,
            self._contract.contract_sha256,
            self._abi.abi_sha256,
            self._native_sha,
            self._composed_ptx_sha,
            self._fresh.target.target_sha256,
            self._fresh.schema.reducer.algebra,
            self._closed,
        )

    def _deep_verify_fusion_plan_for_runtime(
        self,
        fusion_ablation_plan: FusionAblationPlan,
        *,
        query_count: int,
        cupy_version: str,
    ) -> FusionAblationPlan:
        """Perform the recursive admission deliberately excluded from timing."""

        plan = verify_fusion_ablation_plan(fusion_ablation_plan)
        if self._fresh.schema.reducer.algebra \
                is not ReducerAlgebra.CHECKED_U64_PRODUCT_SUM:
            raise ValueError(
                "fusion ablation accepts only checked-U64 product-sum schemas")
        expected_downstream = checked_u64_downstream_operation_sha256(
            plan.variant.value,
            target_identity_sha256=self._fresh.target.target_sha256,
            cupy_version=cupy_version,
        )
        expected_identities = {
            "value_count": (plan.value_count, query_count),
            "callback_ir_sha256": (
                plan.callback_ir_sha256, self._fresh.callback.ir_sha256),
            "callback_authority_nonce": (
                plan.callback_authority_nonce, self._fresh.authority_nonce),
            "contract_sha256": (
                plan.contract_sha256, self._contract.contract_sha256),
            "abi_sha256": (plan.abi_sha256, self._abi.abi_sha256),
            "native_library_sha256": (
                plan.native_library_sha256, self._native_sha),
            "composed_program_sha256": (
                plan.composed_program_sha256, self._composed_ptx_sha),
            "target_identity_sha256": (
                plan.target_identity_sha256, self._fresh.target.target_sha256),
            "cupy_version": (plan.cupy_version, cupy_version),
            "downstream_operation_recipe_sha256": (
                plan.downstream_operation_recipe_sha256, expected_downstream),
        }
        mismatches = {
            name: {"plan": left, "runtime": right}
            for name, (left, right) in expected_identities.items()
            if left != right
        }
        if mismatches:
            raise RuntimeError(
                "fusion ablation plan/runtime identity mismatch: " +
                repr(mismatches))
        return plan

    def admit_fusion_execution_token(
        self,
        fusion_ablation_plan: FusionAblationPlan,
        *,
        operation_execution_nonce: str,
        segment_ordinal: int,
        primitive_count: int,
        query_count: int,
        segment_descriptor_sha256: str,
        plan_input_binding_sha256: str | None = None,
    ) -> VerifiedFusionExecutionToken:
        """Deep-verify and issue one single-use pre-timer segment admission.

        ``segment_descriptor_sha256`` binds the physical segment shape used at
        execution entry.  ``plan_input_binding_sha256`` independently binds a
        canonical input preimage (for example, source bytes plus descriptor and
        formal/prewarm role).  Omitting the latter preserves the legacy
        descriptor-as-input contract; new callers with a richer input identity
        must pass it explicitly.
        """

        if self._closed:
            raise RuntimeError("V4 device-column triangle executor is closed")
        ordinal = _token_u64(segment_ordinal, "segment_ordinal")
        primitives = _token_u64(
            primitive_count, "primitive_count", positive=True)
        queries = _token_u64(query_count, "query_count", positive=True)
        descriptor = _token_sha(
            segment_descriptor_sha256, "segment_descriptor_sha256")
        if plan_input_binding_sha256 is None:
            plan_input = descriptor
            mismatch_code = "token_segment_descriptor"
            mismatch_detail = "plan input identity differs from segment descriptor"
        else:
            plan_input = _token_sha(
                plan_input_binding_sha256, "plan_input_binding_sha256")
            mismatch_code = "token_plan_input_binding"
            mismatch_detail = "plan input identity differs from admitted input binding"

        import cupy as cp

        plan = self._deep_verify_fusion_plan_for_runtime(
            fusion_ablation_plan,
            query_count=queries,
            cupy_version=cp.__version__,
        )
        if plan.input_sha256 != plan_input:
            _token_fail(
                mismatch_code,
                mismatch_detail,
            )
        trace_authority = preverify_operation_trace_authority(
            plan.operation_contract(),
            execution_nonce=operation_execution_nonce,
            value_count=queries,
        )
        return VerifiedFusionExecutionToken(
            owner_key=self._fusion_owner_key(),
            creator_pid=os.getpid(),
            executor_identity=self._fusion_executor_live_identity(),
            cupy_version=cp.__version__,
            segment_ordinal=ordinal,
            primitive_count=primitives,
            query_count=queries,
            segment_descriptor_sha256=descriptor,
            plan_input_sha256=plan_input,
            plan=plan,
            trace_authority=trace_authority,
            _issuer=_FUSION_EXECUTION_TOKEN_ISSUER,
        )

    def execute_segment_unsealed(
        self, triangles, rays, *, ray_weights=None,
        fusion_ablation_plan: FusionAblationPlan | None = None,
        operation_execution_nonce: str | None = None,
        fusion_execution_token: VerifiedFusionExecutionToken | None = None,
        segment_ordinal: int | None = None,
        segment_descriptor_sha256: str | None = None,
    ) -> UnsealedTriangleSegmentExecution:
        """Execute one complete device segment without sealing evidence.

        This method is the registered-timer-safe phase.  It performs all
        required native and reducer work, captures and closes the native audit,
        completes the operation trace, and destroys the native token.  Output,
        traversal and operation receipt digests are deferred to ``seal()``.
        """

        admitted_plan = None
        admitted_trace_authority = None
        if fusion_execution_token is not None:
            if type(fusion_execution_token) is not VerifiedFusionExecutionToken:
                _token_fail("token_type", type(fusion_execution_token).__name__)
            fusion_execution_token._consume()
            admitted_plan, admitted_trace_authority = (
                fusion_execution_token._validate_entry(
                    owner_key=self._fusion_owner_key(),
                    creator_pid=os.getpid(),
                    executor_identity=self._fusion_executor_live_identity(),
                    segment_ordinal=segment_ordinal,
                    segment_descriptor_sha256=segment_descriptor_sha256,
                    legacy_arguments_present=(
                        fusion_ablation_plan is not None
                        or operation_execution_nonce is not None
                    ),
                )
            )
        elif segment_ordinal is not None or segment_descriptor_sha256 is not None:
            raise ValueError(
                "segment ordinal/descriptor require a fusion execution token")

        if self._closed:
            raise RuntimeError("V4 device-column triangle executor is closed")

        import cupy as cp

        triangles, triangle_count, triangle_device = _device_columns(
            cp, triangles, _TRIANGLE_KEYS,
            floating=frozenset(_TRIANGLE_KEYS) - {"ids"})
        rays, query_count, ray_device = _device_columns(
            cp, rays, _RAY_KEYS, floating=frozenset(_RAY_KEYS) - {"ids"})
        if fusion_execution_token is not None:
            fusion_execution_token._check_live_cupy_and_counts(
                cupy_version=cp.__version__,
                primitive_count=triangle_count,
                query_count=query_count,
            )
        if triangle_device != ray_device or triangle_device != int(cp.cuda.Device().id):
            raise ValueError("all V4 segment columns must belong to the current device")
        weighted = (
            self._fresh.schema.reducer.algebra
            is ReducerAlgebra.CHECKED_U64_PRODUCT_SUM)
        if weighted:
            if not isinstance(ray_weights, cp.ndarray) or \
                    ray_weights.dtype != cp.uint64 or ray_weights.ndim != 1 or \
                    not ray_weights.flags.c_contiguous or \
                    int(ray_weights.size) != query_count or \
                    int(ray_weights.device.id) != ray_device:
                raise TypeError("weighted count requires matching contiguous CuPy u64 weights")
        elif ray_weights is not None:
            raise ValueError("unweighted count must not carry ray weights")
        operation_trace = None
        if admitted_plan is not None:
            plan = admitted_plan
            fusion_ablation_plan = plan
            if not weighted:  # The fixed-size live-identity check should catch this first.
                _token_fail("token_identity_drift", "reducer algebra changed")
            operation_trace = OperationTrace.from_preverified_authority(
                admitted_trace_authority)
        elif fusion_ablation_plan is not None:
            if operation_execution_nonce is None:
                raise ValueError("fusion ablation requires an execution nonce")
            plan = self._deep_verify_fusion_plan_for_runtime(
                fusion_ablation_plan,
                query_count=query_count,
                cupy_version=cp.__version__,
            )
            fusion_ablation_plan = plan
            operation_trace = OperationTrace(
                plan.operation_contract(),
                execution_nonce=operation_execution_nonce,
                value_count=query_count,
            )
        elif operation_execution_nonce is not None:
            raise ValueError("operation nonce requires a fusion ablation plan")
        token = ctypes.c_uint64()
        error = ctypes.create_string_buffer(16384)
        _raise(int(self._prepare(
            self._composed_ptx.encode(),
            *[ctypes.c_void_p(int(triangles[key].data.ptr))
              for key in _TRIANGLE_KEYS[1:]],
            triangle_count, ctypes.byref(token), error, len(error))),
            error, "V4 device-column triangle prepare")
        if not token.value:
            raise RuntimeError("V4 device-column triangle prepare returned zero token")
        pending = None
        try:
            per_ray = cp.empty(query_count, dtype=cp.uint64)
            counters = (ctypes.c_uint64 * 7)()
            error = ctypes.create_string_buffer(16384)
            audit = OptixTraversalAuditSession.open(library=self._library)
            try:
                _raise(int(self._execute(
                    token.value,
                    *[ctypes.c_void_p(int(rays[key].data.ptr))
                      for key in _RAY_KEYS[1:]],
                    query_count, ctypes.c_void_p(int(per_ray.data.ptr)),
                    counters, error, len(error))),
                    error, "V4 device-column triangle execute")
                counter_rows = tuple(int(item) for item in counters)
                if counter_rows[1] != query_count or \
                        counter_rows[5] != query_count or \
                        counter_rows[6] != query_count or counter_rows[3] <= 0:
                    raise RuntimeError("V4 device-column callback lifecycle incomplete")
                reduction = None
                if weighted:
                    if fusion_ablation_plan is not None \
                            and fusion_ablation_plan.variant is FusionVariant.FUSION_OFF:
                        reduction = checked_u64_weighted_sum_unfused_device(
                            per_ray, ray_weights,
                            value_upper_bound=triangle_count,
                            operation_trace=operation_trace,
                        )
                    else:
                        reduction = checked_u64_weighted_sum_device(
                            per_ray, ray_weights,
                            value_upper_bound=triangle_count,
                            operation_trace=operation_trace,
                        )
                    reduced = reduction.value
                else:
                    if triangle_count > _U64_MAX // query_count:
                        raise OverflowError("hit-count U64 domain is unsafe")
                    reduced = int(cp.sum(per_ray, dtype=cp.uint64).item())
                if operation_trace is not None:
                    operation_trace.complete()
                observation = audit.capture(
                    expected_program_bundles=(
                        "v4_builtin_triangle_checked_reduction_composed",),
                )
            except Exception:
                audit.abort()
                if operation_trace is not None:
                    operation_trace.abort()
                raise
            if observation.physical_executor_classification \
                    != "optix_traversal_observed":
                if operation_trace is not None:
                    operation_trace.abort()
                raise RuntimeError("V4 device-column segment lacked bound traversal")
            pending = UnsealedTriangleSegmentExecution(
                reduced_output=reduced,
                role_counters=counter_rows,
                triangle_count=triangle_count,
                query_count=query_count,
                reduction=reduction,
                fusion_ablation_plan=fusion_ablation_plan,
                operation_trace=operation_trace,
                traversal_observation=observation,
                authority_nonce=(
                    self._fresh.authority_nonce
                    if fusion_ablation_plan is None
                    else fusion_ablation_plan.callback_authority_nonce
                ),
                contract_sha256=(
                    self._contract.contract_sha256
                    if fusion_ablation_plan is None
                    else fusion_ablation_plan.contract_sha256
                ),
                abi_sha256=(
                    self._abi.abi_sha256
                    if fusion_ablation_plan is None
                    else fusion_ablation_plan.abi_sha256
                ),
                composed_program_sha256=self._composed_ptx_sha,
                native_library_sha256=self._native_sha,
            )
            return pending
        finally:
            error = ctypes.create_string_buffer(16384)
            try:
                _raise(int(self._destroy(token.value, error, len(error))),
                       error, "V4 device-column triangle destroy")
            except BaseException:
                if pending is not None:
                    pending.abort()
                elif operation_trace is not None:
                    operation_trace.abort()
                raise

    def execute_segment(
        self, triangles, rays, *, ray_weights=None,
        fusion_ablation_plan: FusionAblationPlan | None = None,
        operation_execution_nonce: str | None = None,
        fusion_execution_token: VerifiedFusionExecutionToken | None = None,
        segment_ordinal: int | None = None,
        segment_descriptor_sha256: str | None = None,
    ) -> dict[str, object]:
        """Backward-compatible immediate execute-and-seal wrapper."""

        return self.execute_segment_unsealed(
            triangles,
            rays,
            ray_weights=ray_weights,
            fusion_ablation_plan=fusion_ablation_plan,
            operation_execution_nonce=operation_execution_nonce,
            fusion_execution_token=fusion_execution_token,
            segment_ordinal=segment_ordinal,
            segment_descriptor_sha256=segment_descriptor_sha256,
        ).seal()

    def close(self) -> None:
        """Close the reusable host-side executor authority.

        Segment-native tokens are destroyed by ``execute_segment`` itself, so
        this method owns no additional native destruction.  It still makes the
        prepared-owner lifecycle explicit and prevents use after owner close.
        """

        self._closed = True

    def __enter__(self):
        if self._closed:
            raise RuntimeError("V4 device-column triangle executor is closed")
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


__all__ = [
    "FusionExecutionTokenError",
    "UnsealedTriangleSegmentExecution",
    "VerifiedFusionExecutionToken",
    "VerifiedTriangleDeviceColumnCountExecutor",
]

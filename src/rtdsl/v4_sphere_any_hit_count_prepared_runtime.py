"""Prepared OptiX owner for Goal5838 built-in-sphere any-hit count."""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import threading
from dataclasses import dataclass

from .physical_execution_provenance import (
    OptixTraversalAuditSession,
    validate_traversal_receipt,
)
from .v4_callback_ir import CallbackRole
from .v4_sphere_any_hit_count_contract import (
    derive_sphere_any_hit_count_proof,
    verify_sphere_any_hit_count_abi,
    verify_sphere_any_hit_count_physical_schema,
)
from .v4_sphere_any_hit_count_optix_compiler import (
    consume_verified_sphere_any_hit_count_executable,
)
from .v4_sphere_physical_schema import (
    SPHERE_DISCRIMINANT_GUARD_UNIT_ROUNDOFFS,
    SPHERE_NONEXACT_TOI_ULP_BOUND,
    SPHERE_NUMERIC_POLICY,
    verify_motion_segments,
    verify_reference_sphere_contents,
)
from .v4_sphere_prepared_runtime import (
    _configure,
    _loaded_native_identity,
    _native_static_input_fingerprint,
    _query_commitment,
    _raise,
    _read_native_descriptor,
    _require_native_descriptor_transition,
    _require_native_execution_fingerprints,
    _require_native_failure_fingerprints,
    _require_native_target_binding,
    _require_traversal_provider_binding,
    _static_input_commitment,
    _Status,
)

OUTPUT_SCHEMA = "rtdl.v4.sphere_any_hit_count_output.v1"
ROUTE_IDENTITY = "v4_builtin_sphere_any_hit_count:four_role_composed_v1"
PROGRAM_BUNDLE = "v4_builtin_sphere_callback_ir_four_role_composed"


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")
    ).hexdigest()


def _fresh(authority, plan, abi):
    fresh = verify_sphere_any_hit_count_physical_schema(
        authority.callback, authority.schema, target=authority.target
    )
    if fresh != authority or plan != fresh.canonical_plan:
        raise RuntimeError("selected sphere authority/plan does not rederive")
    proof = derive_sphere_any_hit_count_proof(fresh.callback)
    if verify_sphere_any_hit_count_abi(abi, fresh, proof) != abi:
        raise RuntimeError("selected sphere ABI does not rederive")
    return fresh


def _field_mapping_commitment(authority) -> str:
    schema = authority.schema
    return _digest(
        {
            "schema": "rtdl.v4.sphere_any_hit_count_field_mapping.v1",
            "centers": schema.center_field_id,
            "radii": schema.radius_field_id,
            "provider_primitive_ids": schema.provider_primitive_id_field_id,
            "queries": schema.query_field_id,
            "outputs": schema.output_field_id,
            "status": schema.status_field_id,
        }
    )


def sphere_any_hit_count_output(counts) -> dict[str, object]:
    return {"schema": OUTPUT_SCHEMA, "counts": [int(item) for item in counts]}


@dataclass(frozen=True)
class V4SphereAnyHitCountResult:
    counts: tuple[int, ...]
    output: dict[str, object]
    raw_output_u32x3: tuple[tuple[int, int, int], ...]
    counters: tuple[int, ...]
    statuses: tuple[dict[str, int], ...]
    traversal_receipt: dict[str, object]
    output_sha256: str
    composed_ptx_sha256: str
    native_library_sha256: str
    physical_receipt: dict[str, object]


class PreparedSphereAnyHitCountOwner:
    def __init__(
        self,
        *,
        authority,
        plan,
        abi,
        executable,
        centers,
        radii,
        library=None,
        native_library_path=None,
    ) -> None:
        fresh = _fresh(authority, plan, abi)
        source_centers = tuple(centers)
        provider_ids = tuple(range(len(source_centers)))
        normalized = verify_reference_sphere_contents(
            source_centers, radii, provider_ids
        )
        self._centers, self._radii, self._provider_ids = normalized
        composed_ptx = consume_verified_sphere_any_hit_count_executable(
            executable, fresh, plan, abi
        )
        if library is None:
            from . import optix_runtime

            library = optix_runtime._load_optix_library()
        prepare, execute, describe, destroy = _configure(library)
        native_path, native_sha256 = _loaded_native_identity(
            library, native_library_path, symbol=prepare
        )
        if native_sha256 != fresh.target.native_sha256:
            raise RuntimeError(
                "executed native bytes do not match selected sphere target"
            )
        flat_centers = [value for row in self._centers for value in row]
        native_centers = (ctypes.c_float * len(flat_centers))(*flat_centers)
        native_radii = (ctypes.c_float * len(self._radii))(*self._radii)
        native_ids = (ctypes.c_uint32 * len(self._provider_ids))(
            *self._provider_ids
        )
        token = ctypes.c_uint64()
        error = ctypes.create_string_buffer(16384)
        _raise(
            int(
                prepare(
                    composed_ptx.encode("utf-8"),
                    native_centers,
                    native_radii,
                    native_ids,
                    len(self._centers),
                    ctypes.byref(token),
                    error,
                    len(error),
                )
            ),
            error,
            "selected sphere prepare",
        )
        if token.value == 0:
            raise RuntimeError("selected sphere prepare returned zero token")
        try:
            descriptor = _read_native_descriptor(describe, int(token.value))
            if descriptor["primitive_count"] != len(self._centers):
                raise RuntimeError("selected sphere primitive count differs")
            _require_native_target_binding(descriptor, fresh.target)
            if descriptor["static_input_fingerprint"] != (
                _native_static_input_fingerprint(
                    self._centers, self._radii, self._provider_ids
                )
            ):
                raise RuntimeError("selected sphere static content differs")
        except Exception as primary:
            cleanup_error = ctypes.create_string_buffer(16384)
            cleanup_status = int(
                destroy(int(token.value), cleanup_error, len(cleanup_error))
            )
            if cleanup_status:
                primary.add_note(
                    "selected sphere token cleanup also failed: "
                    + (
                        cleanup_error.value.decode(
                            "utf-8", errors="replace"
                        )
                        or str(cleanup_status)
                    )
                )
            raise
        self._token = int(token.value)
        self._fresh = fresh
        self._plan = plan
        self._abi = abi
        self._library = library
        self._execute = execute
        self._describe = describe
        self._destroy = destroy
        self._native_path = native_path
        self._native_sha256 = native_sha256
        self._ptx_sha256 = hashlib.sha256(
            composed_ptx.encode("utf-8")
        ).hexdigest()
        self._descriptor = descriptor
        self._pid = os.getpid()
        self._thread_id = threading.get_ident()
        self._active = threading.Lock()
        self._closed = False
        self._execution_count = 0
        self._last_failure_receipt = None
        self._physical_receipt = {
            "schema": "rtdl.v4.sphere_any_hit_count_physical_receipt.v1",
            "native_descriptor": descriptor,
            "build_input_type_name": "OPTIX_BUILD_INPUT_TYPE_SPHERES",
            "primitive_type_name": "OPTIX_PRIMITIVE_TYPE_SPHERE",
            "builtin_is_api_name": "optixBuiltinISModuleGet",
            "geometry_flags_name": (
                "OPTIX_GEOMETRY_FLAG_REQUIRE_SINGLE_ANYHIT_CALL"
            ),
            "continuation_name": "optixIgnoreIntersection",
            "result_semantics": "per_query_u64_intersected_primitive_count",
            "provider_private_primitive_ids": True,
            "metadata_channels": [],
            "native_library_sha256": native_sha256,
            "loaded_native_library_path": str(native_path),
            "composed_ptx_sha256": self._ptx_sha256,
            "authority_nonce": fresh.authority_nonce,
            "field_mapping_commitment_sha256": _field_mapping_commitment(fresh),
            "static_input_commitment_sha256": _static_input_commitment(
                self._centers, self._radii, self._provider_ids
            ),
            "status_before_output": True,
            "numeric_policy": SPHERE_NUMERIC_POLICY,
            "discriminant_guard_binary32_unit_roundoffs": (
                SPHERE_DISCRIMINANT_GUARD_UNIT_ROUNDOFFS
            ),
            "nonexact_toi_ulp_bound": SPHERE_NONEXACT_TOI_ULP_BOUND,
        }

    def _check(self) -> None:
        if self._closed:
            raise RuntimeError("prepared selected sphere owner is closed")
        if os.getpid() != self._pid:
            raise RuntimeError("prepared selected sphere owner changed process")
        if threading.get_ident() != self._thread_id:
            raise RuntimeError("prepared selected sphere owner changed thread")

    @property
    def lifecycle_receipt(self):
        self._check()
        return {
            "schema": "rtdl.v4.prepared_sphere_any_hit_count_owner.v1",
            "process_bound": True,
            "thread_bound": True,
            "nonserializable": True,
            "nonreentrant": True,
            "execution_count": self._execution_count,
            "native_library_sha256": self._native_sha256,
            "composed_ptx_sha256": self._ptx_sha256,
            "physical_receipt_sha256": _digest(self._physical_receipt),
        }

    @property
    def last_failure_receipt(self):
        self._check()
        return None if self._last_failure_receipt is None else json.loads(
            json.dumps(self._last_failure_receipt, sort_keys=True)
        )

    def __getstate__(self):
        raise RuntimeError("prepared selected sphere owner cannot be serialized")

    def execute(self, queries) -> V4SphereAnyHitCountResult:
        self._check()
        if not self._active.acquire(blocking=False):
            raise RuntimeError("prepared selected sphere owner is already executing")
        try:
            starts: list[tuple[object, ...]] = []
            ends: list[tuple[object, ...]] = []
            for index, query in enumerate(queries):
                try:
                    row = tuple(query)
                except TypeError as exc:
                    raise ValueError(f"query {index} must be (start,end)") from exc
                if len(row) != 2:
                    raise ValueError(f"query {index} must be (start,end)")
                starts.append(tuple(row[0]))
                ends.append(tuple(row[1]))
            normalized = verify_motion_segments(
                starts,
                ends,
                centers=self._centers,
                radii=self._radii,
            )
            start_flat = [value for row in normalized for value in row[:3]]
            end_flat = [value for row in normalized for value in row[3:]]
            query_count = len(normalized)
            native_starts = (ctypes.c_float * len(start_flat))(*start_flat)
            native_ends = (ctypes.c_float * len(end_flat))(*end_flat)
            output_0 = (ctypes.c_uint32 * query_count)()
            output_1 = (ctypes.c_uint32 * query_count)()
            output_2 = (ctypes.c_uint32 * query_count)()
            observed_primitive = (ctypes.c_uint32 * query_count)()
            observed_kind = (ctypes.c_uint32 * query_count)()
            observed_t = (ctypes.c_float * query_count)()
            statuses = (_Status * query_count)()
            counters = (ctypes.c_uint64 * len(CallbackRole))()
            error = ctypes.create_string_buffer(16384)
            audit = OptixTraversalAuditSession.open(library=self._library)
            try:
                native_status = int(
                    self._execute(
                        self._token,
                        native_starts,
                        native_ends,
                        query_count,
                        output_0,
                        output_1,
                        output_2,
                        observed_primitive,
                        observed_kind,
                        observed_t,
                        statuses,
                        counters,
                        error,
                        len(error),
                    )
                )
                status_rows = tuple(
                    {
                        name: int(getattr(item, name))
                        for name, _ in _Status._fields_
                    }
                    for item in statuses
                )
                counter_values = tuple(int(item) for item in counters)
                execution_descriptor = _read_native_descriptor(
                    self._describe, self._token
                )
                _require_native_descriptor_transition(
                    self._descriptor, execution_descriptor
                )
                _require_native_target_binding(
                    execution_descriptor, self._fresh.target
                )
                if native_status:
                    _require_native_failure_fingerprints(
                        execution_descriptor,
                        normalized=normalized,
                        statuses=status_rows,
                        counters=counter_values,
                    )
                    failure_digest = _digest(
                        {
                            "schema": "rtdl.v4.sphere_any_hit_count_failure.v1",
                            "statuses": status_rows,
                            "counters": counter_values,
                        }
                    )
                    failure_receipt = audit.finish(
                        semantic_digest=self._semantic_digest(
                            execution_descriptor, normalized
                        ),
                        output_digest=failure_digest,
                        route_identity=ROUTE_IDENTITY,
                        expected_program_bundles=(PROGRAM_BUNDLE,),
                    )
                    self._last_failure_receipt = {
                        "schema": (
                            "rtdl.v4.sphere_any_hit_count_failure_receipt.v1"
                        ),
                        "failure_digest": failure_digest,
                        "traversal_receipt": failure_receipt,
                    }
                    _raise(native_status, error, "selected sphere execute")
                if any(
                    row["first_error_claimed"] or row["error_code"]
                    for row in status_rows
                ):
                    raise RuntimeError("selected sphere returned device error")
                raw_outputs = tuple(
                    (
                        int(output_0[index]),
                        int(output_1[index]),
                        int(output_2[index]),
                    )
                    for index in range(query_count)
                )
                observed_primitive_values = tuple(
                    int(item) for item in observed_primitive
                )
                observed_kind_values = tuple(int(item) for item in observed_kind)
                observed_t_values = tuple(float(item) for item in observed_t)
                _require_native_execution_fingerprints(
                    execution_descriptor,
                    normalized=normalized,
                    outputs=raw_outputs,
                    observed_primitive=observed_primitive_values,
                    observed_kind=observed_kind_values,
                    observed_t=observed_t_values,
                    statuses=status_rows,
                    counters=counter_values,
                )
                if any(row[2] != 0 for row in raw_outputs):
                    raise RuntimeError("selected sphere reserved output is nonzero")
                if any(item != 0xFFFFFFFF for item in observed_primitive_values):
                    raise RuntimeError("selected sphere exposed unordered primitive data")
                if any(item != 0xFFFFFFFF for item in observed_kind_values):
                    raise RuntimeError("selected sphere exposed unordered hit-kind data")
                counts = tuple(
                    low | (high << 32) for low, high, _ in raw_outputs
                )
                if any(value > len(self._centers) for value in counts):
                    raise RuntimeError("selected sphere count exceeds primitive bound")
                self._verify_role_evidence(counts, status_rows, counter_values)
                output = sphere_any_hit_count_output(counts)
                output_sha256 = _digest(output)
                physical_receipt = dict(self._physical_receipt)
                physical_receipt.update(
                    {
                        "native_descriptor": execution_descriptor,
                        "query_commitment_sha256": _query_commitment(normalized),
                        "output_commitment_sha256": output_sha256,
                        "raw_output_commitment_sha256": _digest(raw_outputs),
                        "role_counters": list(counter_values),
                    }
                )
                receipt = audit.finish(
                    semantic_digest=self._semantic_digest(
                        execution_descriptor, normalized
                    ),
                    output_digest=output_sha256,
                    route_identity=ROUTE_IDENTITY,
                    expected_program_bundles=(PROGRAM_BUNDLE,),
                )
            except Exception:
                audit.abort()
                raise
            if receipt["physical_executor_classification"] != (
                "optix_traversal_observed"
            ):
                raise RuntimeError("selected sphere lacked bound OptiX traversal")
            _require_traversal_provider_binding(
                receipt,
                native_path=self._native_path,
                native_sha256=self._native_sha256,
            )
            validate_traversal_receipt(
                receipt,
                provider_library_sha256=self._native_sha256,
                route_identity=ROUTE_IDENTITY,
                output_digest=output_sha256,
                expected_program_bundles=(PROGRAM_BUNDLE,),
                expected_successful_launch_count=1,
                expected_raygen_invocation_count=query_count,
            )
            self._execution_count += 1
            return V4SphereAnyHitCountResult(
                counts=counts,
                output=output,
                raw_output_u32x3=raw_outputs,
                counters=counter_values,
                statuses=status_rows,
                traversal_receipt=receipt,
                output_sha256=output_sha256,
                composed_ptx_sha256=self._ptx_sha256,
                native_library_sha256=self._native_sha256,
                physical_receipt=physical_receipt,
            )
        finally:
            self._active.release()

    def _semantic_digest(self, descriptor, normalized) -> str:
        return _digest(
            {
                "authority": self._fresh.authority_nonce,
                "plan": self._plan.plan_sha256,
                "abi": self._abi.abi_sha256,
                "ptx": self._ptx_sha256,
                "native": self._native_sha256,
                "descriptor": descriptor,
                "query": _query_commitment(normalized),
            }
        )

    def _verify_role_evidence(self, counts, statuses, counters) -> None:
        role_index = {
            role: list(CallbackRole).index(role) for role in CallbackRole
        }
        query_count = len(counts)
        expected = {
            CallbackRole.MAKE_RAY: query_count,
            CallbackRole.ANY_HIT: sum(counts),
            CallbackRole.MISS: query_count,
            CallbackRole.FINALIZE: query_count,
        }
        for role in CallbackRole:
            observed = counters[role_index[role]]
            if observed != expected.get(role, 0):
                raise RuntimeError(
                    f"selected sphere {role.value} counter differs: {observed}"
                )
        base_mask = sum(
            1 << role_index[role]
            for role in (
                CallbackRole.MAKE_RAY,
                CallbackRole.MISS,
                CallbackRole.FINALIZE,
            )
        )
        any_hit_mask = 1 << role_index[CallbackRole.ANY_HIT]
        for index, (count, status) in enumerate(zip(counts, statuses)):
            expected_mask = base_mask | (any_hit_mask if count else 0)
            if (
                status["invocation_mask"] != expected_mask
                or status["launch_index"] != index
            ):
                raise RuntimeError(
                    f"selected sphere role mask differs at query {index}"
                )

    def close(self) -> None:
        if self._closed:
            return
        self._check()
        if not self._active.acquire(blocking=False):
            raise RuntimeError("cannot close selected sphere during execution")
        try:
            error = ctypes.create_string_buffer(16384)
            _raise(
                int(self._destroy(self._token, error, len(error))),
                error,
                "selected sphere destroy",
            )
            self._token = 0
            self._closed = True
        finally:
            self._active.release()

    def __enter__(self):
        self._check()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


__all__ = [
    "OUTPUT_SCHEMA",
    "PreparedSphereAnyHitCountOwner",
    "V4SphereAnyHitCountResult",
    "sphere_any_hit_count_output",
]

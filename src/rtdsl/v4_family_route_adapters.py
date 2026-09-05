"""Declarative family bindings for the current closed V4 OptiX routes.

Concrete geometry knowledge belongs here, outside the provider-neutral family
core.  Each binding derives a target-neutral family plan from already verified
Callback IR and then delegates target compilation and execution to the existing
closed provider implementation.
"""

from __future__ import annotations

import hashlib
import json
import struct
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .physical_execution_provenance import ValidatedCompactTraversalReceipt
from .v4_callback_abi import compile_callback_abi
from .v4_callback_lifecycle import (
    AnyHitProtocolProof,
    BoundedRelationProtocol,
    TriangleReductionMode,
    TriangleReductionProtocol,
    compile_protocol_program,
    standard_protocol_physical_plan,
)
from .v4_bounded_relation_prepared_runtime import (
    ValidatedBoundedRelationRows,
    validate_bound_relation_rows,
)
from .v4_family_schema import (
    CanonicalFamilyCompilationPlan,
    FamilySchemaV1,
    ProtocolInstanceV1,
    admit_family_schema,
    lower_canonical_compilation_plan,
)
from .v4_generic_family_lifecycle import (
    FAMILY_BEHAVIOR_SCHEMA_ARTIFACT_ID,
    FAMILY_CALLBACK_ABI_ARTIFACT_ID,
    FAMILY_CALLBACK_PROGRAM_ARTIFACT_ID,
    FamilyArtifactV1,
    FamilyExecutableIdentityV1,
    FamilyMaterializedHandleV1,
    FamilyPreparedHandleV1,
    FamilyProgramArtifactsV1,
    FamilyProviderDescriptorV1,
    FamilyProviderExecutionV1,
    FamilyProviderV1,
    VerifiedGenericFamilyProgram,
    bind_family_program_artifacts,
    compile_generic_family_program,
    derive_family_plan_requirements,
    expected_provider_projection,
)


_MODULE_PATH = Path(__file__).resolve()


@lru_cache(maxsize=4096)
def _is_canonical_sha256(value: str) -> bool:
    return len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")).hexdigest()


def _module_sha256() -> str:
    return hashlib.sha256(_MODULE_PATH.read_bytes()).hexdigest()


def _canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _program_artifacts(
    plan: CanonicalFamilyCompilationPlan,
    *,
    callback: object,
    abi: object,
    behavior: object,
) -> FamilyProgramArtifactsV1:
    callback_program = getattr(callback, "program")
    rows = (
        FamilyArtifactV1(
            FAMILY_CALLBACK_PROGRAM_ARTIFACT_ID,
            "rtdl.callback_program.canonical_json.v1",
            _canonical_json_bytes(getattr(callback_program, "to_dict")()),
        ),
        FamilyArtifactV1(
            "rtdl.callback.verification",
            "rtdl.callback_verification.canonical_json.v1",
            _canonical_json_bytes(getattr(callback, "to_dict")()),
        ),
        FamilyArtifactV1(
            FAMILY_CALLBACK_ABI_ARTIFACT_ID,
            "rtdl.callback_abi.canonical_json.v1",
            _canonical_json_bytes(getattr(abi, "to_dict")()),
        ),
        FamilyArtifactV1(
            FAMILY_BEHAVIOR_SCHEMA_ARTIFACT_ID,
            "rtdl.behavior_schema.canonical_json.v1",
            _canonical_json_bytes(getattr(behavior, "to_dict")()),
        ),
    )
    return bind_family_program_artifacts(plan, rows)


def _f32_bits(value: float) -> str:
    bits = struct.unpack("<I", struct.pack("<f", float(value)))[0]
    return f"f32:{bits:08x}"


def _provider_operator(
    *,
    step_id: str,
    operator_id: str,
    contract: Mapping[str, object],
    inputs: list[dict[str, str]],
    output_type: str,
    output_count_relation: str,
    algebra_properties: tuple[str, ...],
) -> dict[str, object]:
    return {
        "operator": "provider_operator",
        "step_id": step_id,
        "operator_id": operator_id,
        "operator_contract_sha256": _digest(contract),
        "inputs": inputs,
        "output_type": output_type,
        "output_count_relation": output_count_relation,
        "algebra_properties": list(algebra_properties),
        "commits_output": True,
    }


def _role(
    name: str,
    allowed: tuple[str, ...],
    required: tuple[str, ...] | None = None,
) -> dict[str, object]:
    return {
        "role": name,
        "cardinality": "exactly_one",
        "allowed_effects": list(allowed),
        "required_effects": list(allowed if required is None else required),
    }


def _buffer(
    buffer_id: str,
    ordinal: int,
    semantic: str,
    domain: str,
    value_type: str,
    access: str,
    count_relation: str,
    alignment_bytes: int,
) -> dict[str, object]:
    return {
        "buffer_id": buffer_id,
        "ordinal": ordinal,
        "semantic": semantic,
        "domain": domain,
        "value_type": value_type,
        "access": access,
        "count_relation": count_relation,
        "alignment_bytes": alignment_bytes,
        "contiguous": True,
        "residency": "device",
    }


def _continuation(prefix: str) -> dict[str, object]:
    return {
        "initial_state": f"{prefix}_prepared",
        "states": [
            {"state_id": f"{prefix}_prepared", "kind": "prepared"},
            {"state_id": f"{prefix}_launched", "kind": "launched"},
            {"state_id": f"{prefix}_ok", "kind": "status_ok"},
            {"state_id": f"{prefix}_failed", "kind": "status_failed"},
            {"state_id": f"{prefix}_committed", "kind": "committed"},
        ],
        "transitions": [
            {
                "from_state": f"{prefix}_prepared",
                "event": "launch",
                "to_state": f"{prefix}_launched",
            },
            {
                "from_state": f"{prefix}_launched",
                "event": "observe_status_ok",
                "to_state": f"{prefix}_ok",
            },
            {
                "from_state": f"{prefix}_launched",
                "event": "observe_status_failure",
                "to_state": f"{prefix}_failed",
            },
            {
                "from_state": f"{prefix}_ok",
                "event": "copy_output",
                "to_state": f"{prefix}_committed",
            },
        ],
        "terminal_states": [f"{prefix}_failed", f"{prefix}_committed"],
        "invariants": [
            "copy_output_requires_status_ok",
            "status_failure_forbids_output_copy",
        ],
    }


def _base_shape(
    *,
    prefix: str,
    parameters: list[dict[str, object]],
    primitive_kind: str,
    buffers: list[dict[str, object]],
    channels: list[dict[str, object]],
    views: list[dict[str, object]],
    events: list[dict[str, object]],
    roles: list[dict[str, object]],
    channel_bindings: list[dict[str, object]],
    result_pipeline: list[dict[str, object]],
    capabilities: tuple[str, ...],
    resources: Mapping[str, object],
) -> dict[str, object]:
    return {
        "schema": "rtdl.family_shape.v1",
        "parameters": parameters,
        "graph_nodes": [{
            "node_id": f"{prefix}_gas",
            "kind": "gas",
            "primitive_kind": primitive_kind,
            "ordinal": 0,
            "update_policy": "static",
            "sbt_record_stride": 1,
            "children": [],
        }],
        "buffers": buffers,
        "channels": channels,
        "views": views,
        "events": events,
        "callback": {"roles": roles},
        "physical": {
            "root": {"node_ref": f"{prefix}_gas"},
            "metadata_bindings": [],
            "channel_bindings": channel_bindings,
            "sbt": {
                "record_stride": 1,
                "record_count_relation": "primitive_count",
                "ray_type_count": 1,
            },
        },
        "result_pipeline": result_pipeline,
        "continuation": _continuation(prefix),
        "capabilities": list(capabilities),
        "identity_bind_set": [
            "actual_executable",
            "callback_ir",
            "native_library",
            "provider_projection",
        ],
        "resource_limits": dict(resources),
    }


def _bounded_shape(resources: Mapping[str, object]) -> dict[str, object]:
    prefix = "relation"
    row_event = f"{prefix}_row"
    capacity = f"{prefix}_capacity"
    operator_id = "rtdl.result.canonical_bounded_pair_collection.v1"
    contract = {
        "schema": "rtdl.provider_operator_contract.v1",
        "operator_id": operator_id,
        "input": "accepted_pair_events",
        "duplicate_policy": "keyed_identical_deduplicate",
        "order": "lexicographic",
        "capacity": "fail_closed_no_partial_result",
        "output": "u32_pair_rows",
    }
    channel = f"{prefix}_item_id"
    return _base_shape(
        prefix=prefix,
        parameters=[
            {"parameter_id": capacity, "type": "u32", "minimum": 1},
            {"parameter_id": f"{prefix}_threshold", "type": "f32_bits"},
        ],
        primitive_kind="custom_primitive",
        buffers=[
            _buffer(f"{prefix}_primitive_bounds", 0, "primitive.bounds",
                    "primitive", "aabb3f_bits", "read_only",
                    "primitive_count", 16),
            _buffer(f"{prefix}_primitive_ids", 1, "primitive.item_id",
                    "primitive", "u32", "read_only", "primitive_count", 4),
            _buffer(f"{prefix}_queries", 2, "query.bounds", "query",
                    "aabb3f_bits", "read_only", "query_count", 16),
            _buffer(f"{prefix}_output", 3, "result.canonical_pair",
                    "result", "u32x2", "write_only", "result_count", 8),
        ],
        channels=[{
            "channel_id": channel,
            "ordinal": 0,
            "semantic": "primitive.item_id",
            "value_type": "u32",
            "producer": {
                "kind": "verified_effect",
                "role": "intersection",
                "effect": "hit",
            },
            "ownership": "verified_intersection.attribute0",
            "consumers": [
                {"role": "any_hit", "argument_index": 0},
                {"role": "closest_hit", "argument_index": 0},
            ],
        }],
        views=[{
            "role": "any_hit",
            "argument_index": 0,
            "source": {"kind": "hit_channel", "channel_ref": channel},
        }],
        events=[{
            "event_id": row_event,
            "ordinal": 0,
            "value_type": "u32x2",
            "source": "verified_effect",
        }],
        roles=[
            _role("any_hit", ("accept_continue",)),
            _role("bounds", ("aabb",)),
            _role("closest_hit", ("payload",)),
            _role("finalize", ("output",)),
            _role("intersection", ("hit", "no_hit")),
            _role("make_ray", ("trace_request",)),
            _role("miss", ("payload",)),
        ],
        channel_bindings=[{
            "channel_ref": channel,
            "producer_role": "intersection",
        }],
        result_pipeline=[_provider_operator(
            step_id=f"{prefix}_commit",
            operator_id=operator_id,
            contract=contract,
            inputs=[
                {"kind": "event", "event_ref": row_event},
                {"kind": "parameter", "parameter_ref": capacity},
                {
                    "kind": "parameter",
                    "parameter_ref": f"{prefix}_threshold",
                },
            ],
            output_type="u32x2",
            output_count_relation="result_count",
            algebra_properties=("deterministic", "fail_closed", "idempotent"),
        )],
        capabilities=(
            "callback_ir",
            "custom_primitive_intersection",
            "fail_closed_status",
            "result_pair_collection",
        ),
        resources=resources,
    )


def _triangle_shape(resources: Mapping[str, object]) -> dict[str, object]:
    prefix = "triangle"
    event = f"{prefix}_per_ray_value"
    mode = f"{prefix}_reduction_mode"
    channel = f"{prefix}_primitive_index"
    operator_id = "rtdl.result.checked_u64_reduction.v1"
    contract = {
        "schema": "rtdl.provider_operator_contract.v1",
        "operator_id": operator_id,
        "modes": ["checked_u64_product_sum", "checked_u64_sum"],
        "overflow": "fail_closed",
        "output": "u64_scalar",
    }
    return _base_shape(
        prefix=prefix,
        parameters=[{
            "parameter_id": mode,
            "type": "namespaced_identifier",
        }],
        primitive_kind="builtin_triangle",
        buffers=[
            _buffer(f"{prefix}_vertices", 0, "primitive.vertex_position",
                    "primitive", "vec3f_bits", "read_only", "vertex_count", 16),
            _buffer(f"{prefix}_indices", 1, "primitive.vertex_indices",
                    "primitive", "u32x3", "read_only", "primitive_count", 4),
            _buffer(f"{prefix}_queries", 2, "query.ray", "query",
                    "ray3f_bits", "read_only", "query_count", 16),
            _buffer(f"{prefix}_weights", 3, "query.weight", "query",
                    "u64", "read_only", "query_count", 8),
            _buffer(f"{prefix}_output", 4, "result.checked_u64",
                    "result", "u64", "write_only", "scalar_count", 8),
        ],
        channels=[{
            "channel_id": channel,
            "ordinal": 0,
            "semantic": "primitive.index",
            "value_type": "u32",
            "producer": {
                "kind": "provider_builtin",
                "builtin": "primitive_index",
            },
            "ownership": "provider.builtin_primitive_index",
            "consumers": [{"role": "any_hit", "argument_index": 0}],
        }],
        views=[{
            "role": "any_hit",
            "argument_index": 0,
            "source": {"kind": "hit_channel", "channel_ref": channel},
        }],
        events=[{
            "event_id": event,
            "ordinal": 0,
            "value_type": "u64",
            "source": "ir_output",
        }],
        roles=[
            _role("any_hit", ("accept_continue",)),
            _role("finalize", ("output",)),
            _role("make_ray", ("trace_request",)),
            _role("miss", ("payload",)),
        ],
        channel_bindings=[{
            "channel_ref": channel,
            "provider_builtin": "primitive_index",
        }],
        result_pipeline=[_provider_operator(
            step_id=f"{prefix}_commit",
            operator_id=operator_id,
            contract=contract,
            inputs=[
                {"kind": "event", "event_ref": event},
                {"kind": "parameter", "parameter_ref": mode},
            ],
            output_type="u64",
            output_count_relation="scalar_count",
            algebra_properties=("commutative", "deterministic", "fail_closed"),
        )],
        capabilities=(
            "builtin_triangle_intersection",
            "callback_ir",
            "checked_u64_reduction",
            "fail_closed_status",
        ),
        resources=resources,
    )


def _owner_grouped_shape(resources: Mapping[str, object]) -> dict[str, object]:
    prefix = "grouped"
    event = f"{prefix}_primitive_event"
    owner_count = f"{prefix}_maximum_owner_count"
    channel = f"{prefix}_primitive_index"
    owner_buffer = f"{prefix}_owner_ids"
    operator_id = "rtdl.result.owner_indexed_bool_or.v1"
    contract = {
        "schema": "rtdl.provider_operator_contract.v1",
        "operator_id": operator_id,
        "event": "accepted_primitive_index",
        "lookup": "primitive_to_owner_u32",
        "operation": "atomic_or_u32_one",
        "duplicate_policy": "idempotent",
        "owner_bounds": "fail_closed_before_output",
    }
    return _base_shape(
        prefix=prefix,
        parameters=[{
            "parameter_id": owner_count,
            "type": "u32",
            "minimum": 1,
        }],
        primitive_kind="builtin_round_linear_curve",
        buffers=[
            _buffer(f"{prefix}_points", 0, "primitive.control_point",
                    "primitive", "vec3f_bits", "read_only", "vertex_count", 16),
            _buffer(f"{prefix}_widths", 1, "primitive.width",
                    "primitive", "f32_bits", "read_only", "vertex_count", 4),
            _buffer(f"{prefix}_indices", 2, "primitive.segment_index",
                    "primitive", "u32", "read_only", "primitive_count", 4),
            _buffer(owner_buffer, 3, "primitive.owner_id", "primitive",
                    "u32", "read_only", "primitive_count", 4),
            _buffer(f"{prefix}_queries", 4, "query.motion_segment", "query",
                    "ray3f_bits", "read_only", "query_count", 16),
            _buffer(f"{prefix}_output", 5, "result.owner_hit_bit", "result",
                    "u32", "write_only", "owner_count", 4),
        ],
        channels=[{
            "channel_id": channel,
            "ordinal": 0,
            "semantic": "primitive.index",
            "value_type": "u32",
            "producer": {
                "kind": "provider_builtin",
                "builtin": "primitive_index",
            },
            "ownership": "provider.builtin_primitive_index",
            "consumers": [{"role": "any_hit", "argument_index": 0}],
        }],
        views=[{
            "role": "any_hit",
            "argument_index": 0,
            "source": {"kind": "hit_channel", "channel_ref": channel},
        }],
        events=[{
            "event_id": event,
            "ordinal": 0,
            "value_type": "u32",
            "source": "provider_builtin",
            "provider_builtin": "accepted_primitive_index",
        }],
        roles=[
            _role("make_ray", ("trace_request",)),
            _role("any_hit", ("accept_continue",)),
            _role("miss", ("payload",)),
            _role("finalize", ("output",)),
        ],
        channel_bindings=[{
            "channel_ref": channel,
            "provider_builtin": "primitive_index",
        }],
        result_pipeline=[_provider_operator(
            step_id=f"{prefix}_commit",
            operator_id=operator_id,
            contract=contract,
            inputs=[
                {"kind": "event", "event_ref": event},
                {"kind": "buffer", "buffer_ref": owner_buffer},
                {"kind": "parameter", "parameter_ref": owner_count},
            ],
            output_type="u32",
            output_count_relation="owner_count",
            algebra_properties=("commutative", "fail_closed", "idempotent"),
        )],
        capabilities=(
            "builtin_round_linear_curve_intersection",
            "callback_ir",
            "fail_closed_status",
            "owner_indexed_bool_or",
        ),
        resources=resources,
    )


def _instance(
    schema: FamilySchemaV1,
    *,
    parameter_values: list[dict[str, object]],
    nominal_semantics: dict[str, str],
    callback,
    abi_sha256: str,
    authorities: list[dict[str, str]],
) -> ProtocolInstanceV1:
    return ProtocolInstanceV1({
        "schema": "rtdl.protocol_instance.v1",
        "family_shape_sha256": schema.family_shape_sha256,
        "parameter_values": parameter_values,
        "nominal_semantics": nominal_semantics,
        "callback_source_sha256": callback.program.source_sha256,
        "callback_ir_sha256": callback.ir_sha256,
        "effect_digest": callback.effect_digest,
        "abi_sha256": abi_sha256,
        "authorities": authorities,
    })


def _plan(
    schema: FamilySchemaV1,
    instance: ProtocolInstanceV1,
    *,
    behavior_schema_sha256: str,
    template_id: str,
) -> CanonicalFamilyCompilationPlan:
    return lower_canonical_compilation_plan(admit_family_schema(
        schema,
        instance,
        behavior_schema_sha256=behavior_schema_sha256,
        canonical_template_id=template_id,
    ))


class _PreparedBridge(FamilyPreparedHandleV1):
    def __init__(
        self,
        prepared: object,
        identity: FamilyExecutableIdentityV1,
        plan_sha256: str,
        output_adapter: Callable[[object], tuple[object, str, Mapping[str, object]]],
    ) -> None:
        self._prepared = prepared
        self._identity = identity
        self._identity_sha256 = identity.identity_sha256
        self._plan_sha256 = plan_sha256
        self._output_adapter = output_adapter

    @property
    def lifecycle_receipt(self) -> Mapping[str, object]:
        return getattr(self._prepared, "lifecycle_receipt")

    def execute(self, batch: object) -> FamilyProviderExecutionV1:
        result = getattr(self._prepared, "execute")(batch)
        output, output_sha256, receipt = self._output_adapter(result)
        if (
            type(output) is int
            and type(receipt) is ValidatedCompactTraversalReceipt
        ):
            envelope = _ValidatedScalarProviderExecution
        elif (
            type(output) is ValidatedBoundedRelationRows
            and type(receipt) is ValidatedCompactTraversalReceipt
        ):
            envelope = _ValidatedRelationProviderExecution
        else:
            envelope = FamilyProviderExecutionV1
        return envelope(
            self._plan_sha256,
            self._identity_sha256,
            "OK",
            0,
            output,
            output_sha256,
            receipt,
        )

    def close(self) -> None:
        getattr(self._prepared, "close")()


class _ValidatedScalarProviderExecution(FamilyProviderExecutionV1):
    """Bridge envelope for a scalar and factory-validated compact proof.

    The protocol lifecycle immediately below this bridge has already checked
    the output digest, native identity, route, program bundle, ray count, and
    native stamp.  Repeating a JSON round trip here adds no independent fact.
    External providers and every non-scalar/non-compact result continue through
    ``FamilyProviderExecutionV1.__post_init__`` unchanged.
    """

    def __post_init__(self) -> None:
        digests = (
            self.plan_sha256,
            self.executable_identity_sha256,
            self.output_sha256,
        )
        if any(
            type(value) is not str
            or not _is_canonical_sha256(value)
            for value in digests
        ):
            raise RuntimeError("validated scalar provider digest differs")
        if (
            self.status != "OK"
            or self.status_code != 0
            or type(self.output_document) is not int
            or type(self.traversal_receipt)
                is not ValidatedCompactTraversalReceipt
        ):
            raise RuntimeError("validated scalar provider envelope differs")


class _ValidatedRelationProviderExecution(FamilyProviderExecutionV1):
    """Bridge envelope for factory-validated immutable relation rows."""

    def __post_init__(self) -> None:
        digests = (
            self.plan_sha256,
            self.executable_identity_sha256,
            self.output_sha256,
        )
        if any(
            type(value) is not str or not _is_canonical_sha256(value)
            for value in digests
        ):
            raise RuntimeError("validated relation provider digest differs")
        if (
            self.status != "OK"
            or self.status_code != 0
            or type(self.output_document) is not ValidatedBoundedRelationRows
            or type(self.traversal_receipt)
                is not ValidatedCompactTraversalReceipt
        ):
            raise RuntimeError("validated relation provider envelope differs")
        validate_bound_relation_rows(
            self.output_document,
            output_sha256=self.output_sha256,
        )
        if (
            self.traversal_receipt._route_identity
                != "v4_callback_ir:custom_aabb_bounded_relation_v1"
            or self.traversal_receipt._output_digest != self.output_sha256
            or self.traversal_receipt._expected_successful_launch_count != 2
        ):
            raise RuntimeError("validated relation traversal binding differs")


class _MaterializedBridge(FamilyMaterializedHandleV1):
    def __init__(
        self,
        materialized: object,
        identity: FamilyExecutableIdentityV1,
        plan_sha256: str,
        output_adapter: Callable[[object], tuple[object, str, Mapping[str, object]]],
    ) -> None:
        self._materialized = materialized
        self._identity = identity
        self._plan_sha256 = plan_sha256
        self._output_adapter = output_adapter

    @property
    def identity(self) -> FamilyExecutableIdentityV1:
        return self._identity

    def prepare(self, static_input: object) -> FamilyPreparedHandleV1:
        prepared = getattr(self._materialized, "prepare")(static_input)
        return _PreparedBridge(
            prepared,
            self._identity,
            self._plan_sha256,
            self._output_adapter,
        )


def _stable_output(result: object) -> tuple[object, str, Mapping[str, object]]:
    return (
        getattr(result, "output"),
        getattr(result, "output_sha256"),
        getattr(result, "traversal_receipt"),
    )


def _owner_output(result: object) -> tuple[object, str, Mapping[str, object]]:
    from .v4_owner_grouped_any_hit import OWNER_GROUPED_ANY_HIT_OUTPUT_SCHEMA

    output = {
        "schema": OWNER_GROUPED_ANY_HIT_OUTPUT_SCHEMA,
        "owner_hit_bits": getattr(result, "owner_hit_bits"),
    }
    return (
        output,
        getattr(result, "output_sha256"),
        getattr(result, "traversal_receipt"),
    )


class _BoundOptixProvider(FamilyProviderV1):
    def __init__(
        self,
        plan: CanonicalFamilyCompilationPlan,
        artifacts: FamilyProgramArtifactsV1,
        *,
        provider_id: str,
        materializer: Callable[[object, object], object],
        output_adapter: Callable[[object], tuple[object, str, Mapping[str, object]]],
    ) -> None:
        self._plan_sha256 = plan.plan_sha256
        self._artifacts = artifacts
        self._implementation_sha256 = _module_sha256()
        self._materializer = materializer
        self._output_adapter = output_adapter
        requirements = derive_family_plan_requirements(plan)
        self._descriptor = FamilyProviderDescriptorV1(
            provider_id=provider_id,
            provider_version="v1",
            target_api="optix.v4",
            implementation_sha256=self._implementation_sha256,
            graph_kinds=requirements.graph_kinds,
            primitive_kinds=requirements.primitive_kinds,
            callback_roles=requirements.callback_roles,
            provider_builtins=requirements.provider_builtins,
            artifact_formats=artifacts.artifact_formats,
            operator_contracts=requirements.operator_contracts,
            capabilities=requirements.capabilities,
        )

    def _check_plan(self, plan: CanonicalFamilyCompilationPlan) -> None:
        if plan.plan_sha256 != self._plan_sha256:
            raise ValueError("provider is bound to a different family plan")
        if _module_sha256() != self._implementation_sha256:
            raise RuntimeError("provider implementation bytes changed after binding")

    def _check_artifacts(self, artifacts: FamilyProgramArtifactsV1) -> None:
        if artifacts != self._artifacts:
            raise ValueError("provider is bound to a different artifact bundle")

    @property
    def descriptor(self) -> FamilyProviderDescriptorV1:
        return self._descriptor

    def project(
        self,
        plan: CanonicalFamilyCompilationPlan,
        artifacts: FamilyProgramArtifactsV1,
    ):
        self._check_plan(plan)
        self._check_artifacts(artifacts)
        return expected_provider_projection(plan, self._descriptor, artifacts)

    def materialize(self, plan, projection, artifacts, *, target, toolchain):
        self._check_plan(plan)
        self._check_artifacts(artifacts)
        expected = expected_provider_projection(plan, self._descriptor, artifacts)
        if projection != expected:
            raise ValueError("provider projection differs from bound plan")
        materialized = self._materializer(target, toolchain)
        old_identity = getattr(materialized, "identity", None)
        if old_identity is not None:
            target_sha256 = old_identity.target_sha256
            executable_sha256 = old_identity.generated_executable_sha256
            provider_artifact_sha256 = old_identity.native_library_sha256
            generated_artifact_sha256 = old_identity.composed_ptx_sha256
        else:
            program = getattr(materialized, "program")
            executable = getattr(materialized, "executable")
            target_sha256 = program.target.profile.target_sha256
            executable_sha256 = executable.executable_sha256
            provider_artifact_sha256 = program.target.profile.native_sha256
            generated_artifact_sha256 = executable.composed.ptx_sha256
        identity = FamilyExecutableIdentityV1(
            self._descriptor.descriptor_sha256,
            projection.projection_sha256,
            plan.plan_sha256,
            target_sha256,
            executable_sha256,
            provider_artifact_sha256,
            generated_artifact_sha256,
        )
        return _MaterializedBridge(
            materialized,
            identity,
            plan.plan_sha256,
            self._output_adapter,
        )


@dataclass(frozen=True, slots=True)
class DeclarativeFamilyRouteV1:
    """One classified route bound to a canonical plan and exact provider."""

    classification: str
    plan: CanonicalFamilyCompilationPlan
    artifacts: FamilyProgramArtifactsV1
    provider: FamilyProviderV1

    def compile(self) -> VerifiedGenericFamilyProgram:
        return compile_generic_family_program(
            self.plan, self.provider, artifacts=self.artifacts
        )


def bounded_relation_family_route(
    protocol: BoundedRelationProtocol,
    any_hit_proof: AnyHitProtocolProof,
) -> DeclarativeFamilyRouteV1:
    if not isinstance(protocol, BoundedRelationProtocol):
        raise TypeError("BoundedRelationProtocol required")
    physical_plan = standard_protocol_physical_plan(protocol)
    legacy = compile_protocol_program(
        protocol,
        physical_plan=physical_plan,
        any_hit_proof=any_hit_proof,
    )
    proof = any_hit_proof.bind(legacy.callback)
    abi = compile_callback_abi(
        legacy.callback, any_hit_proof_authority=proof
    )
    from .v4_bounded_relation import (
        BoundedRelationEmissionSchema,
        RelationDuplicatePolicy,
    )
    from .v4_box_relation_callback import physical_schema

    physical = physical_schema(legacy.callback)
    behavior = BoundedRelationEmissionSchema(
        legacy.callback.ir_sha256,
        legacy.callback.effect_digest,
        physical.schema_sha256,
        protocol.capacity,
        minimum_overlap_f32=protocol.minimum_overlap_f32,
        duplicate_policy=RelationDuplicatePolicy.KEYED_IDENTICAL_DEDUP,
    )
    schema = FamilySchemaV1(_bounded_shape(
        legacy.callback.program.manifest.resources.to_dict()
    ))
    instance = _instance(
        schema,
        parameter_values=[
            {"parameter_ref": "p0", "value_type": "u32", "value": protocol.capacity},
            {
                "parameter_ref": "p1",
                "value_type": "f32_bits",
                "value": _f32_bits(protocol.minimum_overlap_f32),
            },
        ],
        nominal_semantics={
            "event": "result.accepted_pair",
            "output": "result.canonical_pair_rows",
        },
        callback=legacy.callback,
        abi_sha256=abi.abi_sha256,
        authorities=[
            {"authority_kind": "any_hit_proof", "authority_sha256": proof.proof_sha256},
            {"authority_kind": "physical_schema", "authority_sha256": physical.schema_sha256},
            {"authority_kind": "protocol", "authority_sha256": legacy.identity.protocol_sha256},
        ],
    )
    plan = _plan(
        schema,
        instance,
        behavior_schema_sha256=behavior.schema_sha256,
        template_id=physical_plan.template_id,
    )
    artifacts = _program_artifacts(
        plan, callback=legacy.callback, abi=abi, behavior=behavior
    )
    provider = _BoundOptixProvider(
        plan,
        artifacts,
        provider_id="rtdl.optix.bounded_pair_collection",
        materializer=lambda target, toolchain: legacy.materialize(
            target=target, toolchain=toolchain
        ),
        output_adapter=_stable_output,
    )
    return DeclarativeFamilyRouteV1(
        "stable_constructor", plan, artifacts, provider
    )


def _triangle_schema_and_abi(protocol, callback, proof):
    from .v4_triangle_reduction import (
        compile_triangle_reduction_abi,
        verify_triangle_reduction_schema,
    )
    from .v4_triangle_standard_library import (
        all_hit_count_schema,
        weighted_hit_count_schema,
    )
    from .v4_typed_physical_schema import ReferenceTargetProfile

    behavior = (
        weighted_hit_count_schema(callback)
        if protocol.mode is TriangleReductionMode.WEIGHTED_HIT_COUNT
        else all_hit_count_schema(callback)
    )
    neutral_profile = ReferenceTargetProfile(
        provider="optix",
        optix_sdk="0.0.0",
        compute_capability="0.0",
        native_sha256="0" * 64,
        supports_custom_aabb=False,
        supports_builtin_triangle=True,
    )
    authority = verify_triangle_reduction_schema(
        callback, behavior, target=neutral_profile
    )
    abi = compile_triangle_reduction_abi(
        authority, any_hit_proof_authority=proof
    )
    return behavior, abi


def triangle_reduction_family_route(
    protocol: TriangleReductionProtocol,
    any_hit_proof: AnyHitProtocolProof,
) -> DeclarativeFamilyRouteV1:
    if not isinstance(protocol, TriangleReductionProtocol):
        raise TypeError("TriangleReductionProtocol required")
    physical_plan = standard_protocol_physical_plan(protocol)
    legacy = compile_protocol_program(
        protocol,
        physical_plan=physical_plan,
        any_hit_proof=any_hit_proof,
    )
    proof = any_hit_proof.bind(legacy.callback)
    behavior, abi = _triangle_schema_and_abi(protocol, legacy.callback, proof)
    schema = FamilySchemaV1(_triangle_shape(
        legacy.callback.program.manifest.resources.to_dict()
    ))
    instance = _instance(
        schema,
        parameter_values=[{
            "parameter_ref": "p0",
            "value_type": "namespaced_identifier",
            "value": physical_plan.reducer_algebra,
        }],
        nominal_semantics={
            "event": "result.per_ray_u64",
            "output": "result.checked_u64_scalar",
        },
        callback=legacy.callback,
        abi_sha256=abi.abi_sha256,
        authorities=[
            {"authority_kind": "any_hit_proof", "authority_sha256": proof.proof_sha256},
            {"authority_kind": "protocol", "authority_sha256": legacy.identity.protocol_sha256},
            {"authority_kind": "reduction_schema", "authority_sha256": behavior.schema_sha256},
        ],
    )
    plan = _plan(
        schema,
        instance,
        behavior_schema_sha256=behavior.schema_sha256,
        template_id=physical_plan.template_id,
    )
    artifacts = _program_artifacts(
        plan, callback=legacy.callback, abi=abi, behavior=behavior
    )
    provider = _BoundOptixProvider(
        plan,
        artifacts,
        provider_id="rtdl.optix.checked_u64_reduction",
        materializer=lambda target, toolchain: legacy.materialize(
            target=target, toolchain=toolchain
        ),
        output_adapter=_stable_output,
    )
    return DeclarativeFamilyRouteV1(
        "stable_constructor", plan, artifacts, provider
    )


def curve_owner_grouped_any_hit_family_route() -> DeclarativeFamilyRouteV1:
    from .v4_curve_owner_grouped_any_hit_public import (
        curve_owner_grouped_any_hit_source,
    )
    from .v4_curve_owner_grouped_any_hit_standard_library import (
        CURVE_OWNER_GROUPED_ANY_HIT_SOURCE,
        compile_curve_owner_grouped_any_hit_callback,
    )
    from .v4_owner_grouped_any_hit import (
        OwnerGroupedAnyHitSchema,
        compile_owner_grouped_any_hit_abi,
        derive_owner_grouped_any_hit_proof,
        verify_owner_grouped_any_hit_schema,
    )

    callback = compile_curve_owner_grouped_any_hit_callback()
    behavior_schema = OwnerGroupedAnyHitSchema(
        callback.ir_sha256, callback.effect_digest
    )
    proof = derive_owner_grouped_any_hit_proof(callback)
    behavior = verify_owner_grouped_any_hit_schema(
        callback, behavior_schema, proof
    )
    abi = compile_owner_grouped_any_hit_abi(behavior)
    public_source_sha256 = hashlib.sha256(
        CURVE_OWNER_GROUPED_ANY_HIT_SOURCE.encode("utf-8")
    ).hexdigest()
    schema = FamilySchemaV1(_owner_grouped_shape(
        callback.program.manifest.resources.to_dict()
    ))
    instance = _instance(
        schema,
        parameter_values=[{
            "parameter_ref": "p0",
            "value_type": "u32",
            "value": behavior_schema.maximum_owner_count,
        }],
        nominal_semantics={
            "event": "primitive.accepted_index",
            "output": "result.owner_hit_bits",
        },
        callback=callback,
        abi_sha256=abi.abi_sha256,
        authorities=[
            {"authority_kind": "any_hit_proof", "authority_sha256": proof.proof_sha256},
            {"authority_kind": "behavior", "authority_sha256": behavior.authority_sha256},
            {"authority_kind": "behavior_schema", "authority_sha256": behavior_schema.schema_sha256},
            {"authority_kind": "public_source", "authority_sha256": public_source_sha256},
        ],
    )
    plan = _plan(
        schema,
        instance,
        behavior_schema_sha256=behavior_schema.schema_sha256,
        template_id="rtdl.builtin_curve.owner_indexed_bool_or.v1",
    )
    artifacts = _program_artifacts(
        plan, callback=callback, abi=abi, behavior=behavior_schema
    )

    def materialize(target, toolchain):
        source = curve_owner_grouped_any_hit_source()
        if source.source_sha256 != public_source_sha256:
            raise RuntimeError("owner-grouped callback source identity drift")
        program = source.compile(target=target)
        if program.authority.callback.ir_sha256 != callback.ir_sha256 \
                or program.authority.callback.effect_digest != callback.effect_digest \
                or program.abi.abi_sha256 != abi.abi_sha256:
            raise RuntimeError("owner-grouped verified identities drifted")
        return program.materialize(toolchain=toolchain)

    provider = _BoundOptixProvider(
        plan,
        artifacts,
        provider_id="rtdl.optix.owner_indexed_bool_or",
        materializer=materialize,
        output_adapter=_owner_output,
    )
    return DeclarativeFamilyRouteV1("closed_successor", plan, artifacts, provider)


__all__ = [
    "DeclarativeFamilyRouteV1",
    "bounded_relation_family_route",
    "curve_owner_grouped_any_hit_family_route",
    "triangle_reduction_family_route",
]

"""Selected Goal5838 built-in-sphere any-hit count contract.

This module is an extension outside the frozen generic family core.  It binds
one restricted Callback-IR topology to OptiX built-in spheres: every delivered
primitive hit increments a per-query U64 payload and continues traversal.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from . import v4_callback_abi as _abi
from .v4_callback_frontend import parse_callback_source
from .v4_callback_ir import (
    CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    HIT,
    ROLE_STAGE,
    AnyHitDeliveryContract,
    CallbackModuleManifest,
    CallbackProgramSpec,
    CallbackRole,
    GeometryAdmission,
    GeometryContract,
    LinkageMechanism,
    NumericContract,
    ResourceBudget,
    ScalarKind,
    TypeKind,
    VerifiedCallbackProgram,
    _verify_callback_program_with_role_contract,
)
from .v4_sphere_physical_schema import (
    BUILTIN_SPHERE_CONTRACT,
    SphereTargetProfile,
)

SPHERE_ANY_HIT_COUNT_TEMPLATE = "builtin_sphere_any_hit_count_u64_per_query_v1"
SPHERE_ANY_HIT_COUNT_SCHEMA_ID = (
    "https://rtdl.dev/schemas/v4-builtin-sphere-any-hit-count-v1.json"
)
SPHERE_ANY_HIT_COUNT_FIELD_IDS = (
    "sphere_centers",
    "sphere_radii",
    "provider_primitive_ids",
    "motion_segments",
    "per_query_counts",
    "device_status",
)


SPHERE_ANY_HIT_COUNT_SOURCE = r'''
@optix.payload
class CountPayload:
    count: u64

@optix.record
class MotionSegment:
    start: vec3f32
    end: vec3f32

@optix.output
class CountOutput:
    count: u64

@optix.program(payload=CountPayload, output=CountOutput, attributes=(), max_trace_depth=1, max_callable_depth=0)
class StaticSphereAnyHitCount:
    @optix.make_ray
    def make_ray(launch_id: u32, queries: ReadOnlyView[MotionSegment]) -> TraceRequest:
        query = queries[launch_id]
        direction = query.end - query.start
        initial = CountPayload(count=0)
        return optix.trace_request(origin=query.start, direction=direction, tmin=0.0, tmax=1.0, payload=initial)

    @optix.any_hit
    def any_hit(hit: Hit, payload: CountPayload) -> AnyHitEffect:
        updated = CountPayload(count=payload.count + 1)
        return optix.accept_continue(payload=updated)

    @optix.miss
    def miss(ray: Ray3f, payload: CountPayload) -> CountPayload:
        return optix.payload(payload=payload)

    @optix.finalize
    def finalize(payload: CountPayload) -> CountOutput:
        value = CountOutput(count=payload.count)
        return optix.output(value=value)
'''


class SphereAnyHitCountContractError(ValueError):
    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(
            f"V4 sphere any-hit count rejected: {code}@{path}: {message}"
        )


def _fail(code: str, path: str, message: str) -> None:
    raise SphereAnyHitCountContractError(code, path, message)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def sphere_any_hit_count_manifest() -> CallbackModuleManifest:
    return CallbackModuleManifest(
        name="static_sphere_any_hit_count",
        payload_record="CountPayload",
        output_record="CountOutput",
        attribute_types=(),
        constants=(),
        numeric=NumericContract(),
        resources=ResourceBudget(),
        geometry=GeometryContract(
            GeometryAdmission.OPTIX_BUILTIN_SEMANTICS,
            BUILTIN_SPHERE_CONTRACT,
            False,
        ),
        any_hit_delivery=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        selected_linkage=LinkageMechanism.TRUSTED_SINGLE_MODULE_COMPOSITION_V1,
        linkage_selection_reason=(
            "selected Goal5838 built-in-sphere per-query any-hit count"
        ),
    )


def verify_sphere_any_hit_count_callback_program(
    program: CallbackProgramSpec,
) -> VerifiedCallbackProgram:
    if program.schema_version != CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION:
        _fail(
            "callback_schema",
            "program.schema_version",
            CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
        )
    manifest = program.manifest
    if manifest.geometry.contract_name != BUILTIN_SPHERE_CONTRACT:
        _fail(
            "sphere_contract",
            "manifest.geometry.contract_name",
            BUILTIN_SPHERE_CONTRACT,
        )
    if manifest.attribute_types:
        _fail(
            "sphere_attributes",
            "manifest.attribute_types",
            "built-in sphere attributes are provider-owned",
        )
    if manifest.any_hit_delivery is not (
        AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL
    ):
        _fail(
            "delivery_contract",
            "manifest.any_hit_delivery",
            AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL.value,
        )
    verified = _verify_callback_program_with_role_contract(
        program,
        required_roles=frozenset(
            {
                CallbackRole.MAKE_RAY,
                CallbackRole.ANY_HIT,
                CallbackRole.MISS,
                CallbackRole.FINALIZE,
            }
        ),
        forbidden_roles=frozenset(
            {
                CallbackRole.BOUNDS,
                CallbackRole.INTERSECTION,
                CallbackRole.CLOSEST_HIT,
            }
        ),
        hit_value_type=HIT,
        allow_hit_read_only_views=False,
        allowed_geometry_admissions=frozenset(
            {GeometryAdmission.OPTIX_BUILTIN_SEMANTICS}
        ),
        expected_schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    )
    any_hit = verified.program.function_for_role(CallbackRole.ANY_HIT)
    if len(any_hit.arguments) != 2 or any_hit.arguments[0].value_type != HIT:
        _fail(
            "any_hit_signature",
            "any_hit.arguments",
            "exact Hit and payload arguments required",
        )
    payload_type = any_hit.arguments[1].value_type
    if (
        payload_type.kind is not TypeKind.RECORD
        or payload_type.name != manifest.payload_record
    ):
        _fail(
            "any_hit_signature",
            "any_hit.arguments[1]",
            "exact payload record required",
        )
    records = {record.name: record for record in program.records}
    for name in (manifest.payload_record, manifest.output_record):
        record = records[name]
        if len(record.fields) != 1:
            _fail("record_shape", name, "one U64 field required")
        field = record.fields[0]
        if (
            field.name != "count"
            or field.value_type.kind is not TypeKind.SCALAR
            or field.value_type.scalar is not ScalarKind.U64
        ):
            _fail("record_shape", name, "count: u64 required")
    return verified


def compile_sphere_any_hit_count_callback() -> VerifiedCallbackProgram:
    program = parse_callback_source(
        SPHERE_ANY_HIT_COUNT_SOURCE,
        sphere_any_hit_count_manifest(),
        schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    )
    return verify_sphere_any_hit_count_callback_program(program)


@dataclass(frozen=True, slots=True)
class SphereAnyHitCountPhysicalSchema:
    callback_ir_sha256: str
    effect_digest: str
    center_field_id: str = SPHERE_ANY_HIT_COUNT_FIELD_IDS[0]
    radius_field_id: str = SPHERE_ANY_HIT_COUNT_FIELD_IDS[1]
    provider_primitive_id_field_id: str = SPHERE_ANY_HIT_COUNT_FIELD_IDS[2]
    query_field_id: str = SPHERE_ANY_HIT_COUNT_FIELD_IDS[3]
    output_field_id: str = SPHERE_ANY_HIT_COUNT_FIELD_IDS[4]
    status_field_id: str = SPHERE_ANY_HIT_COUNT_FIELD_IDS[5]
    schema_id: str = SPHERE_ANY_HIT_COUNT_SCHEMA_ID
    schema_version: str = "v1"
    contract_name: str = BUILTIN_SPHERE_CONTRACT
    template_id: str = SPHERE_ANY_HIT_COUNT_TEMPLATE
    geometry_family: str = "builtin_sphere"
    gas_update_policy: str = "static"
    graph_depth: int = 1
    sbt_record_count: int = 1
    motion_blur: bool = False
    primitive_index_offset: int = 0
    geometry_flags: str = "require_single_anyhit_call"
    result_semantics: str = "per_query_u64_intersected_primitive_count"

    def semantic_dict(self) -> dict[str, object]:
        return {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
        } | {
            "buffers": {
                "centers": "primitive:vec3f32:read_only:primitive_count",
                "radii": "primitive:f32:read_only:primitive_count",
                "provider_primitive_ids": (
                    "provider_private:u32:read_only:primitive_count"
                ),
                "queries": (
                    "query:motion_segment_f32x6:read_only:query_count"
                ),
                "outputs": "output:u64:write_only:query_count",
                "status": "status:status_record:internal:query_count",
            },
            "metadata_channels": [],
            "hit_delivery": (
                "one_any_hit_invocation_per_intersected_primitive_then_continue"
            ),
        }

    @property
    def schema_sha256(self) -> str:
        return _digest(self.semantic_dict())


@dataclass(frozen=True, slots=True)
class SphereAnyHitCountCanonicalPlan:
    schema_sha256: str
    callback_ir_sha256: str
    effect_digest: str
    target_sha256: str
    authority_nonce: str
    template_id: str = SPHERE_ANY_HIT_COUNT_TEMPLATE
    executable: bool = False

    def semantic_dict(self) -> dict[str, object]:
        return {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
        }

    @property
    def plan_sha256(self) -> str:
        return _digest(self.semantic_dict())


@dataclass(frozen=True, slots=True)
class VerifiedSphereAnyHitCountAuthority:
    callback: VerifiedCallbackProgram
    schema: SphereAnyHitCountPhysicalSchema
    target: SphereTargetProfile
    canonical_plan: SphereAnyHitCountCanonicalPlan

    @property
    def authority_nonce(self) -> str:
        return self.canonical_plan.authority_nonce


def verify_sphere_any_hit_count_physical_schema(
    callback: VerifiedCallbackProgram,
    schema: SphereAnyHitCountPhysicalSchema,
    *,
    target: SphereTargetProfile,
) -> VerifiedSphereAnyHitCountAuthority:
    if type(schema) is not SphereAnyHitCountPhysicalSchema:
        _fail("schema_type", "schema", type(schema).__name__)
    if type(target) is not SphereTargetProfile:
        _fail("target_type", "target", type(target).__name__)
    fresh_target = SphereTargetProfile(
        provider=target.provider,
        optix_sdk=target.optix_sdk,
        compute_capability=target.compute_capability,
        native_sha256=target.native_sha256,
        supports_builtin_sphere=target.supports_builtin_sphere,
        max_graph_depth=target.max_graph_depth,
    )
    fresh = verify_sphere_any_hit_count_callback_program(callback.program)
    if fresh != callback:
        _fail(
            "callback_reverification",
            "callback",
            "Callback IR does not rederive exactly",
        )
    if (
        schema.callback_ir_sha256 != fresh.ir_sha256
        or schema.effect_digest != fresh.effect_digest
    ):
        _fail("callback_binding", "schema", "exact callback identity required")
    expected_fields = (
        schema.center_field_id,
        schema.radius_field_id,
        schema.provider_primitive_id_field_id,
        schema.query_field_id,
        schema.output_field_id,
        schema.status_field_id,
    )
    if expected_fields != SPHERE_ANY_HIT_COUNT_FIELD_IDS:
        _fail("field_identity", "schema", repr(expected_fields))
    expected_constants = {
        "schema_id": SPHERE_ANY_HIT_COUNT_SCHEMA_ID,
        "schema_version": "v1",
        "contract_name": BUILTIN_SPHERE_CONTRACT,
        "template_id": SPHERE_ANY_HIT_COUNT_TEMPLATE,
        "geometry_family": "builtin_sphere",
        "gas_update_policy": "static",
        "graph_depth": 1,
        "sbt_record_count": 1,
        "motion_blur": False,
        "primitive_index_offset": 0,
        "geometry_flags": "require_single_anyhit_call",
        "result_semantics": "per_query_u64_intersected_primitive_count",
    }
    for name, expected in expected_constants.items():
        if type(getattr(schema, name)) is not type(expected) or getattr(
            schema, name
        ) != expected:
            _fail("schema_identity", f"schema.{name}", repr(getattr(schema, name)))
    nonce = _digest(
        {
            "kind": "builtin_sphere_any_hit_count_physical_authority_v1",
            "callback": fresh.ir_sha256,
            "effect": fresh.effect_digest,
            "schema": schema.schema_sha256,
            "target": fresh_target.target_sha256,
        }
    )
    plan = SphereAnyHitCountCanonicalPlan(
        schema.schema_sha256,
        fresh.ir_sha256,
        fresh.effect_digest,
        fresh_target.target_sha256,
        nonce,
    )
    return VerifiedSphereAnyHitCountAuthority(
        fresh, schema, fresh_target, plan
    )


def derive_sphere_any_hit_count_proof(
    callback: VerifiedCallbackProgram,
) -> _abi.AnyHitProofAuthority:
    fresh = verify_sphere_any_hit_count_callback_program(callback.program)
    canonical = compile_sphere_any_hit_count_callback()
    if _canonical(fresh.to_dict()) != _canonical(canonical.to_dict()):
        _fail(
            "proof_normal_form",
            "callback",
            "callback is not the selected increment-by-one normal form",
        )
    payload = {
        "schema": "rtdl.v4.sphere_any_hit_count_order_proof.v1",
        "callback_ir_sha256": fresh.ir_sha256,
        "effect_digest": fresh.effect_digest,
        "delivery_contract": (
            AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL.value
        ),
        "recognized_normal_form": "payload.count := payload.count + 1",
        "event_multiplicity": (
            "provider_requires_single_anyhit_call_per_intersected_primitive"
        ),
        "continuation": "accept_every_hit_and_continue",
        "algebra": "commutative_associative_natural_count",
        "overflow_bound": "count_le_primitive_count_le_u32_max_lt_u64_max",
    }
    return _abi.AnyHitProofAuthority(
        callback_ir_sha256=fresh.ir_sha256,
        effect_digest=fresh.effect_digest,
        delivery_contract=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        proof_sha256=_digest(payload),
        proof_kind="external_machine_checked_order_independence_v1",
    )


def compile_sphere_any_hit_count_abi(
    authority: VerifiedSphereAnyHitCountAuthority,
    proof: _abi.AnyHitProofAuthority,
) -> _abi.CompiledCallbackAbi:
    fresh = verify_sphere_any_hit_count_physical_schema(
        authority.callback, authority.schema, target=authority.target
    )
    if fresh != authority:
        raise _abi.CallbackAbiError(
            "sphere_count_authority_reverification",
            "physical_schema_authority",
            "authority does not rederive exactly",
        )
    expected_proof = derive_sphere_any_hit_count_proof(fresh.callback)
    if proof != expected_proof:
        raise _abi.CallbackAbiError(
            "sphere_count_proof_reverification",
            "any_hit_proof",
            "proof does not rederive from the selected normal form",
        )
    proof_sha = _abi._verify_any_hit_authority(fresh.callback, proof)
    role_functions = {
        item.role: item
        for item in fresh.callback.program.functions
        if item.role is not None
    }
    records = {item.name: item for item in fresh.callback.program.records}
    roles = []
    for role in CallbackRole:
        function = role_functions.get(role)
        if function is None:
            continue
        inputs = [
            _abi.AbiField(
                "in.context.launch_index",
                "u64",
                "in",
                "launch_index",
                True,
            )
        ]
        for argument in function.arguments:
            inputs.extend(
                _abi._flatten_type(
                    argument.value_type,
                    f"in.{argument.name}",
                    direction="in",
                    records=records,
                    seen=set(),
                )
            )
        nonce = int(
            hashlib.sha256(
                (
                    f"{fresh.callback.ir_sha256}:"
                    f"{fresh.callback.effect_digest}:{role.value}"
                ).encode("ascii")
            ).hexdigest()[:8],
            16,
        )
        roles.append(
            _abi.RoleAbi(
                role=role,
                role_tag=_abi._ROLE_TAGS[role],
                stage_tag=_abi._STAGE_TAGS[ROLE_STAGE[role]],
                symbol=(
                    f"rtdl_v4_{role.value}_"
                    f"{fresh.callback.ir_sha256[:16]}"
                ),
                inputs=tuple(inputs),
                status=_abi._STATUS_FIELDS,
                effects=_abi._effect_variants(function, records),
                first_error_policy=_abi._FIRST_ERROR_POLICY,
                nonce_word=nonce,
            )
        )
    base = _abi.CompiledCallbackAbi(
        schema_id=_abi.CALLBACK_ABI_SCHEMA_ID,
        schema_version=_abi.CALLBACK_ABI_SCHEMA_VERSION,
        callback_ir_sha256=fresh.callback.ir_sha256,
        callback_effect_digest=fresh.callback.effect_digest,
        any_hit_proof_sha256=proof_sha,
        any_hit_proof_kind=proof.proof_kind,
        any_hit_delivery_contract=proof.delivery_contract.value,
        runtime_status_codes=_abi._RUNTIME_STATUS_CODES,
        roles=tuple(roles),
        abi_sha256="",
    )
    digest = hashlib.sha256(
        _abi._canonical_json(base.payload_without_digest())
    ).hexdigest()
    return _abi.CompiledCallbackAbi(
        **{**base.__dict__, "abi_sha256": digest}
    )


def verify_sphere_any_hit_count_abi(
    artifact: _abi.CompiledCallbackAbi,
    authority: VerifiedSphereAnyHitCountAuthority,
    proof: _abi.AnyHitProofAuthority,
) -> _abi.CompiledCallbackAbi:
    if type(artifact) is not _abi.CompiledCallbackAbi:
        raise _abi.CallbackAbiError(
            "sphere_count_abi_type", "abi", "CompiledCallbackAbi required"
        )
    expected = compile_sphere_any_hit_count_abi(authority, proof)
    if _abi._canonical_json(artifact.to_dict()) != _abi._canonical_json(
        expected.to_dict()
    ):
        raise _abi.CallbackAbiError(
            "sphere_count_abi_recompile_mismatch",
            "abi",
            "ABI differs from exact selected-topology recompilation",
        )
    return expected


@dataclass(frozen=True, slots=True)
class SphereAnyHitCountBehaviorSchema:
    callback_ir_sha256: str
    effect_digest: str
    physical_schema_sha256: str
    event_semantics: str = "intersected_primitive_once"
    continuation: str = "accept_every_hit_and_continue"
    result_operator: str = "rtdl.result.per_query_u64.v1"
    output_count_relation: str = "query_count"
    overflow: str = "impossible_under_u32_primitive_count_bound"

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "rtdl.behavior.sphere_any_hit_count.v1",
            **{
                name: getattr(self, name)
                for name in self.__dataclass_fields__
            },
        }

    @property
    def schema_sha256(self) -> str:
        return _digest(self.to_dict())


def build_sphere_any_hit_count_authority(
    target: SphereTargetProfile,
) -> tuple[
    VerifiedSphereAnyHitCountAuthority,
    _abi.AnyHitProofAuthority,
    _abi.CompiledCallbackAbi,
    SphereAnyHitCountBehaviorSchema,
]:
    callback = compile_sphere_any_hit_count_callback()
    schema = SphereAnyHitCountPhysicalSchema(
        callback.ir_sha256, callback.effect_digest
    )
    authority = verify_sphere_any_hit_count_physical_schema(
        callback, schema, target=target
    )
    proof = derive_sphere_any_hit_count_proof(callback)
    abi = compile_sphere_any_hit_count_abi(authority, proof)
    behavior = SphereAnyHitCountBehaviorSchema(
        callback.ir_sha256, callback.effect_digest, schema.schema_sha256
    )
    return authority, proof, abi, behavior


__all__ = [
    "SPHERE_ANY_HIT_COUNT_FIELD_IDS",
    "SPHERE_ANY_HIT_COUNT_SCHEMA_ID",
    "SPHERE_ANY_HIT_COUNT_SOURCE",
    "SPHERE_ANY_HIT_COUNT_TEMPLATE",
    "SphereAnyHitCountBehaviorSchema",
    "SphereAnyHitCountCanonicalPlan",
    "SphereAnyHitCountContractError",
    "SphereAnyHitCountPhysicalSchema",
    "VerifiedSphereAnyHitCountAuthority",
    "build_sphere_any_hit_count_authority",
    "compile_sphere_any_hit_count_abi",
    "compile_sphere_any_hit_count_callback",
    "derive_sphere_any_hit_count_proof",
    "sphere_any_hit_count_manifest",
    "verify_sphere_any_hit_count_abi",
    "verify_sphere_any_hit_count_callback_program",
    "verify_sphere_any_hit_count_physical_schema",
]

"""Closed standard-library source for curve owner-grouped any-hit."""

from __future__ import annotations

from .v4_callback_frontend import parse_callback_source
from .v4_callback_ir import (
    AnyHitDeliveryContract,
    CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    CallbackModuleManifest,
    GeometryAdmission,
    GeometryContract,
    LinkageMechanism,
    NumericContract,
    ResourceBudget,
)
from .v4_curve_owner_grouped_any_hit import (
    BuiltinCurveOwnerGroupedAnyHitPhysicalSchema,
    verify_callback_program_for_curve_owner_grouped_any_hit,
    verify_curve_owner_grouped_any_hit_physical_schema,
)
from .v4_curve_physical_schema import BUILTIN_CURVE_CONTRACT, CurveTargetProfile
from .v4_owner_grouped_any_hit import (
    OwnerGroupedAnyHitSchema,
    derive_owner_grouped_any_hit_proof,
    verify_owner_grouped_any_hit_schema,
)


CURVE_OWNER_GROUPED_ANY_HIT_SOURCE = r'''
@optix.payload
class GroupedAnyHitPayload:
    token: u32

@optix.record
class MotionSegment:
    start: vec3f32
    end: vec3f32

@optix.output
class GroupedAnyHitOutput:
    token: u32

@optix.program(payload=GroupedAnyHitPayload, output=GroupedAnyHitOutput, attributes=(), max_trace_depth=1, max_callable_depth=0)
class StaticRoundLinearCurveOwnerGroupedAnyHit:
    @optix.make_ray
    def make_ray(launch_id: u32, queries: ReadOnlyView[MotionSegment]) -> TraceRequest:
        query = queries[launch_id]
        initial = GroupedAnyHitPayload(token=ZERO_U32)
        direction = query.end - query.start
        return optix.trace_request(origin=query.start, direction=direction, tmin=ZERO_F32, tmax=ONE_F32, payload=initial)

    @optix.any_hit
    def any_hit(hit: Hit, payload: GroupedAnyHitPayload) -> AnyHitEffect:
        return optix.accept_continue(payload=payload)

    @optix.miss
    def miss(ray: Ray3f, payload: GroupedAnyHitPayload) -> GroupedAnyHitPayload:
        return optix.payload(payload=payload)

    @optix.finalize
    def finalize(payload: GroupedAnyHitPayload) -> GroupedAnyHitOutput:
        result = GroupedAnyHitOutput(token=payload.token)
        return optix.output(value=result)
'''


def curve_owner_grouped_any_hit_manifest() -> CallbackModuleManifest:
    from .v4_callback_ir import F32, U32, FrozenConstant

    return CallbackModuleManifest(
        name="static_round_linear_curve_owner_grouped_any_hit",
        payload_record="GroupedAnyHitPayload",
        output_record="GroupedAnyHitOutput",
        attribute_types=(),
        constants=(
            FrozenConstant("ZERO_U32", U32, 0),
            FrozenConstant("ZERO_F32", F32, 0.0),
            FrozenConstant("ONE_F32", F32, 1.0),
        ),
        numeric=NumericContract(),
        resources=ResourceBudget(),
        geometry=GeometryContract(
            GeometryAdmission.OPTIX_BUILTIN_SEMANTICS,
            BUILTIN_CURVE_CONTRACT,
            False,
        ),
        any_hit_delivery=AnyHitDeliveryContract.IDEMPOTENT_MONOTONE,
        selected_linkage=LinkageMechanism.TRUSTED_SINGLE_MODULE_COMPOSITION_V1,
        linkage_selection_reason=(
            "closed curve owner-grouped idempotent any-hit protocol"),
    )


def compile_curve_owner_grouped_any_hit_callback():
    spec = parse_callback_source(
        CURVE_OWNER_GROUPED_ANY_HIT_SOURCE,
        curve_owner_grouped_any_hit_manifest(),
        schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    )
    return verify_callback_program_for_curve_owner_grouped_any_hit(spec)


def build_curve_owner_grouped_any_hit_authority(
    target: CurveTargetProfile,
):
    callback = compile_curve_owner_grouped_any_hit_callback()
    behavior_schema = OwnerGroupedAnyHitSchema(
        callback.ir_sha256, callback.effect_digest)
    proof = derive_owner_grouped_any_hit_proof(callback)
    behavior = verify_owner_grouped_any_hit_schema(
        callback, behavior_schema, proof)
    physical_schema = BuiltinCurveOwnerGroupedAnyHitPhysicalSchema(
        callback.ir_sha256,
        callback.effect_digest,
        behavior_schema.schema_sha256,
    )
    authority = verify_curve_owner_grouped_any_hit_physical_schema(
        behavior, physical_schema, target=target)
    return authority, proof


__all__ = [
    "CURVE_OWNER_GROUPED_ANY_HIT_SOURCE",
    "build_curve_owner_grouped_any_hit_authority",
    "compile_curve_owner_grouped_any_hit_callback",
    "curve_owner_grouped_any_hit_manifest",
]

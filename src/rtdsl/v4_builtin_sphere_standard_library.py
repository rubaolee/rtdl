"""App-neutral Callback IR standard program for static built-in spheres."""

from __future__ import annotations

from .v4_callback_frontend import parse_callback_source
from .v4_callback_ir import (
    CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    F32,
    U32,
    CallbackModuleManifest,
    FrozenConstant,
    GeometryAdmission,
    GeometryContract,
    LinkageMechanism,
    NumericContract,
    ResourceBudget,
)
from .v4_sphere_physical_schema import (
    BUILTIN_SPHERE_CONTRACT,
    BuiltinSpherePhysicalSchema,
    SphereTargetProfile,
    verify_builtin_sphere_physical_schema,
    verify_callback_program_for_builtin_sphere,
)
from .v4_sphere_optix_wrapper_codegen import generate_trusted_optix_sphere_wrapper_v1
from .v4_sphere_callback_abi import compile_sphere_callback_abi


FIRST_CONTACT_SOURCE = r'''
@optix.payload
class FirstContactPayload:
    hit: u32
    toi: f32
    application_id: u32

@optix.record
class MotionSegment:
    start: vec3f32
    end: vec3f32

@optix.output
class FirstContactOutput:
    hit: u32
    toi: f32
    application_id: u32

@optix.program(payload=FirstContactPayload, output=FirstContactOutput, attributes=(), max_trace_depth=1, max_callable_depth=0)
class StaticSphereFirstContact:
    @optix.make_ray
    def make_ray(launch_id: u32, queries: ReadOnlyView[MotionSegment]) -> TraceRequest:
        query = queries[launch_id]
        direction = query.end - query.start
        initial = FirstContactPayload(hit=ZERO_U32, toi=ONE_F32, application_id=U32_MAX)
        return optix.trace_request(origin=query.start, direction=direction, tmin=ZERO_F32, tmax=ONE_F32, payload=initial)

    @optix.closest_hit
    def closest_hit(hit: Hit, payload: FirstContactPayload, application_ids: ReadOnlyView[u32]) -> FirstContactPayload:
        updated = FirstContactPayload(hit=ONE_U32, toi=hit.t, application_id=application_ids[ZERO_U32])
        return optix.payload(payload=updated)

    @optix.miss
    def miss(ray: Ray3f, payload: FirstContactPayload) -> FirstContactPayload:
        return optix.payload(payload=payload)

    @optix.finalize
    def finalize(payload: FirstContactPayload) -> FirstContactOutput:
        result = FirstContactOutput(hit=payload.hit, toi=payload.toi, application_id=payload.application_id)
        return optix.output(value=result)
'''


def first_contact_manifest() -> CallbackModuleManifest:
    return CallbackModuleManifest(
        name="static_sphere_first_contact",
        payload_record="FirstContactPayload",
        output_record="FirstContactOutput",
        attribute_types=(),
        constants=(
            FrozenConstant("ZERO_U32", U32, 0),
            FrozenConstant("ONE_U32", U32, 1),
            FrozenConstant("U32_MAX", U32, 0xFFFFFFFF),
            FrozenConstant("ZERO_F32", F32, 0.0),
            FrozenConstant("ONE_F32", F32, 1.0),
        ),
        numeric=NumericContract(),
        resources=ResourceBudget(),
        geometry=GeometryContract(
            GeometryAdmission.OPTIX_BUILTIN_SEMANTICS,
            BUILTIN_SPHERE_CONTRACT,
            False,
        ),
        any_hit_delivery=None,
        selected_linkage=LinkageMechanism.TRUSTED_SINGLE_MODULE_COMPOSITION_V1,
        linkage_selection_reason="static built-in-sphere first-contact protocol",
    )


def compile_first_contact_callback():
    spec = parse_callback_source(
        FIRST_CONTACT_SOURCE,
        first_contact_manifest(),
        schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    )
    return verify_callback_program_for_builtin_sphere(spec)


def build_first_contact_authority(
    target: SphereTargetProfile,
    *,
    center_field_id: str = "sphere_centers",
    radius_field_id: str = "sphere_radii",
    application_id_field_id: str = "application_ids",
    query_field_id: str = "motion_segments",
    output_field_id: str = "first_contacts",
    status_field_id: str = "device_status",
):
    callback = compile_first_contact_callback()
    schema = BuiltinSpherePhysicalSchema(
        callback.ir_sha256, callback.effect_digest,
        center_field_id, radius_field_id, application_id_field_id,
        query_field_id, output_field_id, status_field_id,
    )
    authority = verify_builtin_sphere_physical_schema(
        callback, schema, target=target)
    abi = compile_sphere_callback_abi(authority)
    wrapper = generate_trusted_optix_sphere_wrapper_v1(
        authority, authority.canonical_plan, abi)
    return authority, abi, wrapper


__all__ = [
    "FIRST_CONTACT_SOURCE", "build_first_contact_authority",
    "compile_first_contact_callback", "first_contact_manifest",
]

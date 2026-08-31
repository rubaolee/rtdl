"""Closed app-neutral callback/schema for prepared spatial candidates."""

from __future__ import annotations

from .v4_callback_frontend import compile_callback_source
from .v4_callback_ir import (
    AnyHitDeliveryContract, CallbackModuleManifest, CallbackRole,
    FrozenConstant, GeometryAdmission, GeometryContract, LinkageMechanism,
    NumericContract, ResourceBudget, U32,
)
from .v4_typed_physical_schema import (
    BufferAccess, BufferDomain, BufferFieldSchema, BufferSemantic,
    CountRelation, GasSchema, GasUpdatePolicy, GeometryFamily,
    HitChannelProducer, HitChannelSchema, HitChannelSemantic,
    PhysicalValueType, TypedPhysicalSchemaV1,
)

U32_MAX = 0xFFFFFFFF

SPATIAL_CANDIDATE_SOURCE = r'''
@optix.payload
class SpatialPayload:
    hit_count: u32
    minimum_id: u32
@optix.record
class SpatialPrimitive:
    lower: vec3f32
    upper: vec3f32
    item_id: u32
@optix.record
class SpatialQuery:
    lower: vec3f32
    upper: vec3f32
    diagonal_kind: u32
@optix.output
class SpatialOutput:
    hit_count: u32
    minimum_id: u32
@optix.program(payload=SpatialPayload, output=SpatialOutput, attributes=(u32,), max_trace_depth=1, max_callable_depth=0)
class SpatialCandidateProgram:
    @optix.bounds
    def bounds(primitive: SpatialPrimitive) -> Aabb3f:
        return optix.aabb(lower=primitive.lower, upper=primitive.upper)
    @optix.make_ray
    def make_ray(launch_id: u32, queries: ReadOnlyView[SpatialQuery]) -> TraceRequest:
        query = queries[launch_id]
        initial = SpatialPayload(hit_count=0, minimum_id=U32_MAX)
        return optix.trace_request(origin=query.lower, direction=vec3f32(1.0, 0.0, 0.0), tmin=0.0, tmax=query.upper.x, payload=initial)
    @optix.intersection
    def intersection(ray: Ray3f, primitive: SpatialPrimitive) -> IntersectionEffect:
        center = (primitive.lower + primitive.upper) * vec3f32(0.5, 0.5, 0.5)
        radius = (primitive.upper.x - primitive.lower.x) * 0.5
        offset = ray.origin - center
        b = optix.dot(offset, ray.direction)
        c = optix.dot(offset, offset) - radius * radius
        discriminant = b * b - c
        if discriminant >= 0.0:
            root = optix.sqrt(discriminant)
            near_t = -b - root
            far_t = -b + root
            selected_t = near_t if near_t >= ray.tmin else far_t
            if selected_t >= ray.tmin and selected_t <= ray.tmax:
                return optix.hit(t=selected_t, hit_kind=0, attributes=(primitive.item_id,))
            else:
                return optix.no_hit()
        else:
            return optix.no_hit()
    @optix.any_hit
    def any_hit(hit: Hit, payload: SpatialPayload) -> AnyHitEffect:
        updated = SpatialPayload(hit_count=payload.hit_count + 1, minimum_id=payload.minimum_id)
        return optix.accept_continue(payload=updated)
    @optix.closest_hit
    def closest_hit(hit: Hit, payload: SpatialPayload) -> SpatialPayload:
        return optix.payload(payload=payload)
    @optix.miss
    def miss(ray: Ray3f, payload: SpatialPayload) -> SpatialPayload:
        return optix.payload(payload=payload)
    @optix.finalize
    def finalize(payload: SpatialPayload) -> SpatialOutput:
        value = SpatialOutput(hit_count=payload.hit_count, minimum_id=payload.minimum_id)
        return optix.output(value=value)
'''


def manifest() -> CallbackModuleManifest:
    return CallbackModuleManifest(
        name="prepared_spatial_candidate_fragment",
        payload_record="SpatialPayload", output_record="SpatialOutput",
        attribute_types=(U32,),
        constants=(FrozenConstant("U32_MAX", U32, U32_MAX),),
        numeric=NumericContract(), resources=ResourceBudget(),
        geometry=GeometryContract(
            GeometryAdmission.TESTED_USER_GEOMETRY,
            "closed_sphere_candidate_geometry_v1", False),
        any_hit_delivery=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        selected_linkage=LinkageMechanism.TRUSTED_SINGLE_MODULE_COMPOSITION_V1,
        linkage_selection_reason="closed app-neutral prepared spatial target",
    )


def compile_callback():
    return compile_callback_source(SPATIAL_CANDIDATE_SOURCE, manifest())


def physical_schema(callback) -> TypedPhysicalSchemaV1:
    return TypedPhysicalSchemaV1(
        callback.ir_sha256, callback.effect_digest, GeometryFamily.CUSTOM_AABB,
        (BufferFieldSchema(
            "primitives", BufferSemantic.CUSTOM_PRIMITIVE_DATA,
            BufferDomain.PRIMITIVE, PhysicalValueType.OPAQUE_RECORD,
            BufferAccess.READ_ONLY, CountRelation.PRIMITIVE_COUNT, 16),),
        (HitChannelSchema(
            HitChannelSemantic.CUSTOM_HIT_KIND, PhysicalValueType.U32,
            HitChannelProducer.VERIFIED_INTERSECTION_EFFECT,
            (CallbackRole.ANY_HIT, CallbackRole.CLOSEST_HIT)),),
        (),
        GasSchema(
            GeometryFamily.CUSTOM_AABB,
            (BufferSemantic.CUSTOM_PRIMITIVE_DATA,),
            GasUpdatePolicy.DECLARED_REFIT, 1, 1),
    )


__all__ = ["SPATIAL_CANDIDATE_SOURCE", "compile_callback", "manifest", "physical_schema"]

"""App-neutral fixtures for Goal5760 bounded relation emission.

LibRTS and polygon-set Jaccard remain consumers; neither identity occurs in
the product schema/compiler/runtime.  The callback source expresses closed
box overlap while the trusted target owns the bounded relation emission.
"""

from __future__ import annotations

from rtdsl.v4_callback_ir import (
    AnyHitDeliveryContract,
    CallbackModuleManifest,
    FrozenConstant,
    GeometryAdmission,
    GeometryContract,
    LinkageMechanism,
    NumericContract,
    ResourceBudget,
    U32,
)
from rtdsl.v4_callback_frontend import compile_callback_source
from rtdsl.v4_typed_physical_schema import (
    BufferAccess,
    BufferDomain,
    BufferFieldSchema,
    BufferSemantic,
    CountRelation,
    GasSchema,
    GasUpdatePolicy,
    GeometryFamily,
    HitChannelProducer,
    HitChannelSchema,
    HitChannelSemantic,
    PhysicalValueType,
    TypedPhysicalSchemaV1,
)
from rtdsl.v4_callback_ir import CallbackRole


U32_MAX = 0xFFFFFFFF


BOX_RELATION_SOURCE = r'''
@optix.payload
class BoxPayload:
    hit_count: u32
    minimum_id: u32

@optix.record
class BoxPrimitive:
    lower: vec3f32
    upper: vec3f32
    item_id: u32

@optix.record
class BoxQuery:
    lower: vec3f32
    upper: vec3f32
    diagonal_kind: u32

@optix.output
class BoxOutput:
    hit_count: u32
    minimum_id: u32

@optix.program(
    payload=BoxPayload,
    output=BoxOutput,
    attributes=(u32,),
    max_trace_depth=1,
    max_callable_depth=0,
)
class BoxRelationProgram:
    @optix.bounds
    def bounds(primitive: BoxPrimitive) -> Aabb3f:
        return optix.aabb(lower=primitive.lower, upper=primitive.upper)

    @optix.make_ray
    def make_ray(launch_id: u32, queries: ReadOnlyView[BoxQuery]) -> TraceRequest:
        query = queries[launch_id]
        initial = BoxPayload(hit_count=0, minimum_id=U32_MAX)
        if query.diagonal_kind == 0:
            origin = vec3f32(query.upper.x, query.lower.y, 0.0)
            direction = vec3f32(query.lower.x - query.upper.x, query.upper.y - query.lower.y, 0.0)
            return optix.trace_request(origin=origin, direction=direction, tmin=0.0, tmax=1.0, payload=initial)
        else:
            origin = vec3f32(query.lower.x, query.lower.y, 1.0)
            direction = vec3f32(query.upper.x - query.lower.x, query.upper.y - query.lower.y, 0.0)
            return optix.trace_request(origin=origin, direction=direction, tmin=0.0, tmax=1.0, payload=initial)

    @optix.intersection
    def intersection(ray: Ray3f, primitive: BoxPrimitive) -> IntersectionEffect:
        source_x1 = ray.origin.x + ray.direction.x
        source_y1 = ray.origin.y + ray.direction.y
        source_min_x = source_x1 if source_x1 < ray.origin.x else ray.origin.x
        source_max_x = ray.origin.x if source_x1 < ray.origin.x else source_x1
        source_min_y = source_y1 if source_y1 < ray.origin.y else ray.origin.y
        source_max_y = ray.origin.y if source_y1 < ray.origin.y else source_y1
        overlap = primitive.lower.x <= source_max_x and primitive.upper.x >= source_min_x and primitive.lower.y <= source_max_y and primitive.upper.y >= source_min_y
        if overlap:
            return optix.hit(t=0.0, hit_kind=0, attributes=(primitive.item_id,))
        else:
            return optix.no_hit()

    @optix.any_hit
    def any_hit(hit: Hit, payload: BoxPayload) -> AnyHitEffect:
        updated_count = payload.hit_count + 1
        updated_id = hit.hit_kind if hit.hit_kind < payload.minimum_id else payload.minimum_id
        updated = BoxPayload(hit_count=updated_count, minimum_id=updated_id)
        return optix.accept_continue(payload=updated)

    @optix.closest_hit
    def closest_hit(hit: Hit, payload: BoxPayload) -> BoxPayload:
        return optix.payload(payload=payload)

    @optix.miss
    def miss(ray: Ray3f, payload: BoxPayload) -> BoxPayload:
        return optix.payload(payload=payload)

    @optix.finalize
    def finalize(payload: BoxPayload) -> BoxOutput:
        value = BoxOutput(hit_count=payload.hit_count, minimum_id=payload.minimum_id)
        return optix.output(value=value)
'''


def manifest() -> CallbackModuleManifest:
    return CallbackModuleManifest(
        name="bounded_relation_fragment",
        payload_record="BoxPayload",
        output_record="BoxOutput",
        attribute_types=(U32,),
        constants=(FrozenConstant("U32_MAX", U32, U32_MAX),),
        numeric=NumericContract(),
        resources=ResourceBudget(),
        geometry=GeometryContract(
            GeometryAdmission.TESTED_USER_GEOMETRY,
            "closed_box_overlap_geometry_v1", False),
        any_hit_delivery=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        selected_linkage=LinkageMechanism.TRUSTED_SINGLE_MODULE_COMPOSITION_V1,
        linkage_selection_reason=(
            "verified app-neutral custom-AABB relation target"),
    )


def compile_callback():
    return compile_callback_source(BOX_RELATION_SOURCE, manifest())


def physical_schema(callback) -> TypedPhysicalSchemaV1:
    return TypedPhysicalSchemaV1(
        callback.ir_sha256,
        callback.effect_digest,
        GeometryFamily.CUSTOM_AABB,
        (
            BufferFieldSchema(
                "primitives", BufferSemantic.CUSTOM_PRIMITIVE_DATA,
                BufferDomain.PRIMITIVE, PhysicalValueType.OPAQUE_RECORD,
                BufferAccess.READ_ONLY, CountRelation.PRIMITIVE_COUNT, 16),
        ),
        (
            HitChannelSchema(
                HitChannelSemantic.CUSTOM_HIT_KIND, PhysicalValueType.U32,
                HitChannelProducer.VERIFIED_INTERSECTION_EFFECT,
                (CallbackRole.ANY_HIT, CallbackRole.CLOSEST_HIT)),
        ),
        (),
        GasSchema(
            GeometryFamily.CUSTOM_AABB,
            (BufferSemantic.CUSTOM_PRIMITIVE_DATA,),
            GasUpdatePolicy.STATIC, 1, 1),
    )


def exact_relation(
    sources,
    indexed,
    *,
    minimum_overlap: float = 0.0,
):
    rows = []
    for source in sources:
        for item in indexed:
            dx = max(0.0, min(source[2], item[2]) - max(source[0], item[0]))
            dy = max(0.0, min(source[3], item[3]) - max(source[1], item[1]))
            closed_overlap = (
                item[0] <= source[2] and item[2] >= source[0]
                and item[1] <= source[3] and item[3] >= source[1]
            )
            if closed_overlap and dx * dy >= minimum_overlap:
                rows.append((int(source[4]), int(item[4])))
    return tuple(sorted(set(rows)))


def polygon_set_jaccard_candidate_boxes():
    """Derive the non-LibRTS lane from the real authored application case.

    This deliberately imports the existing application fixture rather than
    copying a convenient synthetic box set into the Goal5760 harness.  The
    M2 capability is only the broad-phase relation producer: the application's
    exact polygon-set Jaccard continuation remains outside this goal.
    """

    from examples.current.features.spatial.rtdl_polygon_set_jaccard import (
        make_authored_polygon_set_jaccard_case,
    )

    case = make_authored_polygon_set_jaccard_case(copies=1)

    def box(polygon):
        xs = tuple(float(vertex[0]) for vertex in polygon.vertices)
        ys = tuple(float(vertex[1]) for vertex in polygon.vertices)
        return (min(xs), min(ys), max(xs), max(ys), int(polygon.id))

    # The application names left as probe/source and right as build/indexed.
    sources = tuple(box(polygon) for polygon in case["left"])
    indexed = tuple(box(polygon) for polygon in case["right"])
    return indexed, sources


__all__ = [
    "BOX_RELATION_SOURCE", "compile_callback", "exact_relation", "manifest",
    "physical_schema", "polygon_set_jaccard_candidate_boxes",
]

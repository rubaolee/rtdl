"""Application-owned restricted callback for the selected particle locator.

The source is data, never executed as Python.  Goal5753 feeds it only to the
frozen V4 parser/verifier.  Passing that frontend does not grant physical
runtime authority; the frozen wrapper/runtime must independently admit the
geometry contract and ABI.
"""

from __future__ import annotations

import dataclasses

from rtdsl.v4_callback_ir import (
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


CALLBACK_SOURCE = r'''
@optix.payload
class CellPayload:
    best_t: f32
    cell_id: u32

@optix.record
class SharedFace:
    a: vec3f32
    b: vec3f32
    c: vec3f32
    front_cell: u32
    back_cell: u32
    face_id: u32

@optix.record
class ParticleQuery:
    position: vec3f32
    tmax: f32

@optix.output
class CellLocation:
    cell_id: u32
    face_id: u32

@optix.helper
def cross(left: vec3f32, right: vec3f32) -> vec3f32:
    return vec3f32(
        left.y * right.z - left.z * right.y,
        left.z * right.x - left.x * right.z,
        left.x * right.y - left.y * right.x,
    )

@optix.program(
    payload=CellPayload,
    output=CellLocation,
    attributes=(u32,),
    max_trace_depth=1,
    max_callable_depth=0,
)
class TetrahedralCellLocator:
    @optix.bounds
    def bounds(primitive: SharedFace) -> Aabb3f:
        lower = vec3f32(
            optix.min(primitive.a.x, optix.min(primitive.b.x, primitive.c.x)),
            optix.min(primitive.a.y, optix.min(primitive.b.y, primitive.c.y)),
            optix.min(primitive.a.z, optix.min(primitive.b.z, primitive.c.z)),
        )
        upper = vec3f32(
            optix.max(primitive.a.x, optix.max(primitive.b.x, primitive.c.x)),
            optix.max(primitive.a.y, optix.max(primitive.b.y, primitive.c.y)),
            optix.max(primitive.a.z, optix.max(primitive.b.z, primitive.c.z)),
        )
        return optix.aabb(lower=lower, upper=upper)

    @optix.make_ray
    def make_ray(launch_id: u32, queries: ReadOnlyView[ParticleQuery]) -> TraceRequest:
        query = queries[launch_id]
        initial = CellPayload(best_t=query.tmax, cell_id=U32_MAX)
        return optix.trace_request(
            origin=query.position,
            direction=vec3f32(1.0, RAY_EPSILON, RAY_EPSILON),
            tmin=0.0,
            tmax=query.tmax,
            payload=initial,
        )

    @optix.intersection
    def intersection(ray: Ray3f, primitive: SharedFace) -> IntersectionEffect:
        edge1 = primitive.b - primitive.a
        edge2 = primitive.c - primitive.a
        pvec = cross(ray.direction, edge2)
        determinant = optix.dot(edge1, pvec)
        if optix.abs(determinant) > DET_EPSILON:
            inverse = 1.0 / determinant
            tvec = ray.origin - primitive.a
            u = optix.dot(tvec, pvec) * inverse
            qvec = cross(tvec, edge1)
            v = optix.dot(ray.direction, qvec) * inverse
            t = optix.dot(edge2, qvec) * inverse
            if u >= 0.0 and v >= 0.0 and u + v <= 1.0 and t >= ray.tmin and t <= ray.tmax:
                cell_id = primitive.front_cell if determinant < 0.0 else primitive.back_cell
                return optix.hit(t=t, hit_kind=0, attributes=(cell_id,))
            else:
                return optix.no_hit()
        else:
            return optix.no_hit()

    @optix.closest_hit
    def closest_hit(hit: Hit, payload: CellPayload) -> CellPayload:
        updated = CellPayload(best_t=hit.t, cell_id=hit.hit_kind)
        return optix.payload(payload=updated)

    @optix.miss
    def miss(ray: Ray3f, payload: CellPayload) -> CellPayload:
        return optix.payload(payload=payload)

    @optix.finalize
    def finalize(payload: CellPayload) -> CellLocation:
        value = CellLocation(cell_id=payload.cell_id, face_id=U32_MAX)
        return optix.output(value=value)
'''


def manifest() -> CallbackModuleManifest:
    """Declare the selected application's semantics without minting authority."""

    return CallbackModuleManifest(
        name="tetrahedral_particle_cell_locator",
        payload_record="CellPayload",
        output_record="CellLocation",
        attribute_types=(U32,),
        constants=(
            FrozenConstant("U32_MAX", U32, 0xFFFFFFFF),
            FrozenConstant("RAY_EPSILON", F32, 1.0e-10),
            FrozenConstant("DET_EPSILON", F32, 1.0e-8),
        ),
        numeric=NumericContract(),
        resources=ResourceBudget(),
        geometry=GeometryContract(
            GeometryAdmission.TESTED_USER_GEOMETRY,
            "tetrahedral_shared_triangle_faces_v1",
            False,
        ),
        # The author cell-locator launch uses OPTIX_RAY_FLAG_DISABLE_ANYHIT.
        any_hit_delivery=None,
        selected_linkage=LinkageMechanism.TRUSTED_SINGLE_MODULE_COMPOSITION_V1,
        linkage_selection_reason="frozen Goal5752 production linkage",
    )


REQUIRED_PHYSICAL_CAPABILITIES = {
    "geometry_family": "built_in_triangle_gas",
    "primitive_columns": (
        "vertices_f32x3",
        "triangle_indices_u32x3",
        "front_cell_u32",
        "back_cell_u32",
        "face_id_u32",
    ),
    "hit_channels": ("primitive_index", "triangle_front_back_hit_kind"),
    "query_columns": ("position_f32x3", "direction_f32x3", "tmax_f32"),
    "output_columns": ("cell_id_u32", "face_id_u32", "status", "counters"),
}

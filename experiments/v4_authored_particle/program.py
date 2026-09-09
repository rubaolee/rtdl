"""Project-authored Particle callback for the public V4 source lifecycle.

The application requests one strict-interior face transition per ray and owns
the output semantics.  RTDL sees only the generic built-in-triangle u32x3
physical template; no Particle name or rule enters the engine.
"""

from __future__ import annotations

import numpy as np

from rtdsl import v4


U32_MAX = 0xFFFFFFFF
FRONT_HIT_KIND = 0xFE
BACK_HIT_KIND = 0xFF


FACE_FIRST_SOURCE = r'''
@optix.payload
class FaceFirstPayload:
    face_id: u32
    selected_cell: u32
    neighbor_cell: u32

@optix.record
class Query:
    origin: vec3f32
    direction: vec3f32
    tmax: f32

@optix.output
class FaceFirstOutput:
    face_id: u32
    selected_cell: u32
    neighbor_cell: u32

@optix.program(payload=FaceFirstPayload, output=FaceFirstOutput, attributes=(), max_trace_depth=1, max_callable_depth=0)
class ParticleFaceFirstTransition:
    @optix.make_ray
    def make_ray(launch_id: u32, queries: ReadOnlyView[Query]) -> TraceRequest:
        query = queries[launch_id]
        initial = FaceFirstPayload(face_id=U32_MAX, selected_cell=U32_MAX, neighbor_cell=U32_MAX)
        return optix.trace_request(origin=query.origin, direction=query.direction, tmin=0.0, tmax=query.tmax, payload=initial)

    @optix.closest_hit
    def closest_hit(hit: TriangleHit, payload: FaceFirstPayload, first_side: ReadOnlyView[u32], second_side: ReadOnlyView[u32]) -> FaceFirstPayload:
        is_front = hit.hit_kind == FRONT_HIT_KIND
        selected = first_side[hit.primitive_index] if is_front else second_side[hit.primitive_index]
        neighbor = second_side[hit.primitive_index] if is_front else first_side[hit.primitive_index]
        updated = FaceFirstPayload(face_id=hit.primitive_index, selected_cell=selected, neighbor_cell=neighbor)
        return optix.payload(payload=updated)

    @optix.miss
    def miss(ray: Ray3f, payload: FaceFirstPayload) -> FaceFirstPayload:
        return optix.payload(payload=payload)

    @optix.finalize
    def finalize(payload: FaceFirstPayload) -> FaceFirstOutput:
        result = FaceFirstOutput(face_id=payload.face_id, selected_cell=payload.selected_cell, neighbor_cell=payload.neighbor_cell)
        return optix.output(value=result)
'''


def face_first_manifest() -> v4.CallbackModuleManifest:
    return v4.CallbackModuleManifest(
        name="particle_face_first_transition",
        payload_record="FaceFirstPayload",
        output_record="FaceFirstOutput",
        attribute_types=(),
        constants=(
            v4.FrozenConstant("U32_MAX", v4.U32, U32_MAX),
            v4.FrozenConstant("FRONT_HIT_KIND", v4.U32, FRONT_HIT_KIND),
            v4.FrozenConstant("BACK_HIT_KIND", v4.U32, BACK_HIT_KIND),
        ),
        numeric=v4.NumericContract(),
        resources=v4.ResourceBudget(),
        geometry=v4.GeometryContract(
            v4.GeometryAdmission.OPTIX_BUILTIN_SEMANTICS,
            v4.BUILTIN_TRIANGLE_CONTRACT,
            False,
        ),
        any_hit_delivery=None,
        selected_linkage=v4.LinkageMechanism.TRUSTED_SINGLE_MODULE_COMPOSITION_V1,
        linkage_selection_reason=(
            "project-authored Particle face-first transition through the "
            "public built-in-triangle template"
        ),
    )


def build_face_first_physical_plan(
    verified_source: v4.VerifiedBuiltinTriangleCallbackSource,
    *,
    independent_cpu_oracle_sha256: str,
) -> v4.BuiltinTriangleCallbackPhysicalPlan:
    orientation = v4.BuiltinTriangleOrientationDeclaration(
        contract_name="particle_face_first_ccw_front_v1",
        independent_cpu_oracle_sha256=independent_cpu_oracle_sha256,
        winding_policy=v4.TriangleWindingPolicy.CCW_IS_FRONT,
        front_hit_kind=FRONT_HIT_KIND,
        back_hit_kind=BACK_HIT_KIND,
        callback_front_hit_kind_constant="FRONT_HIT_KIND",
        callback_back_hit_kind_constant="BACK_HIT_KIND",
        front_hit_selects=v4.AdjacencySide.FRONT,
        back_hit_selects=v4.AdjacencySide.BACK,
    )
    fields = v4.BuiltinTriangleU32x3FieldIds(
        vertex_positions="particle_vertices",
        triangle_indices="particle_faces",
        first_primitive_values="front_cells",
        second_primitive_values="back_cells",
        queries="particle_rays",
        outputs="face_first_transitions",
        status="device_status",
    )
    return v4.build_builtin_triangle_u32x3_physical_plan(
        verified_source,
        field_ids=fields,
        orientation=orientation,
        first_metadata_argument_index=2,
        second_metadata_argument_index=3,
        hit_selection_policy=v4.TriangleHitSelectionPolicy.PROVIDER_NATIVE_CLOSEST,
    )


def face_first_expected(adjacency_rows: object) -> np.ndarray:
    """Return `(face, selected, neighbor)` from independent app oracle rows."""

    rows = np.asarray(adjacency_rows)
    if rows.dtype != np.dtype(np.uint32) or rows.ndim != 2 or rows.shape[1] != 3:
        raise ValueError("Particle oracle must be an Nx3 uint32 array")
    result = np.ascontiguousarray(rows[:, (2, 0, 1)], dtype=np.uint32)
    result.setflags(write=False)
    return result


__all__ = [
    "BACK_HIT_KIND",
    "FACE_FIRST_SOURCE",
    "FRONT_HIT_KIND",
    "U32_MAX",
    "build_face_first_physical_plan",
    "face_first_expected",
    "face_first_manifest",
]

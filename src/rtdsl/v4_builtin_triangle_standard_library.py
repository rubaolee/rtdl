"""Closed V4 standard library for built-in-triangle adjacency queries.

The template is application-neutral: applications provide vertices, triangle
indices, two primitive-aligned adjacency columns, queries and provenance for
their orientation contract.  They cannot provide PTX or an opaque callback.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .v4_triangle_optix_compiler import VerifiedTriangleExecutable

from .v4_callback_abi import compile_callback_abi
from .v4_callback_frontend import parse_callback_source
from .v4_callback_ir import (
    CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    CallbackModuleManifest,
    CallbackRole,
    FrozenConstant,
    GeometryAdmission,
    GeometryContract,
    LinkageMechanism,
    NumericContract,
    ResourceBudget,
    U32,
)
from .v4_typed_physical_schema import (
    BUILTIN_TRIANGLE_CONTRACT,
    AdjacencySide,
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
    HitMetadataBinding,
    PhysicalValueType,
    ReferenceTargetProfile,
    TriangleOrientationAuthority,
    TriangleWindingPolicy,
    TypedPhysicalSchemaV1,
    default_reference_templates,
    lower_canonical_reference_plan,
    triangle_author_semantics_sha256,
    verify_callback_program_for_geometry,
    verify_typed_physical_schema,
)


FRONT_HIT_KIND = 0xFE
BACK_HIT_KIND = 0xFF

ADJACENCY_SOURCE = r'''
@optix.payload
class CellPayload:
    cell_id: u32
    neighbor_id: u32
    face_id: u32

@optix.record
class Query:
    origin: vec3f32
    direction: vec3f32
    tmax: f32

@optix.output
class CellOutput:
    cell_id: u32
    neighbor_id: u32
    face_id: u32

@optix.program(payload=CellPayload, output=CellOutput, attributes=(), max_trace_depth=1, max_callable_depth=0)
class TriangleAdjacencyLocator:
    @optix.make_ray
    def make_ray(launch_id: u32, queries: ReadOnlyView[Query]) -> TraceRequest:
        query = queries[launch_id]
        initial = CellPayload(cell_id=U32_MAX, neighbor_id=U32_MAX, face_id=U32_MAX)
        return optix.trace_request(origin=query.origin, direction=query.direction, tmin=0.0, tmax=query.tmax, payload=initial)

    @optix.closest_hit
    def closest_hit(hit: TriangleHit, payload: CellPayload, first_side: ReadOnlyView[u32], second_side: ReadOnlyView[u32]) -> CellPayload:
        is_front = hit.hit_kind == FRONT_HIT_KIND
        selected = first_side[hit.primitive_index] if is_front else second_side[hit.primitive_index]
        neighbor = second_side[hit.primitive_index] if is_front else first_side[hit.primitive_index]
        updated = CellPayload(cell_id=selected, neighbor_id=neighbor, face_id=hit.primitive_index)
        return optix.payload(payload=updated)

    @optix.miss
    def miss(ray: Ray3f, payload: CellPayload) -> CellPayload:
        return optix.payload(payload=payload)

    @optix.finalize
    def finalize(payload: CellPayload) -> CellOutput:
        result = CellOutput(cell_id=payload.cell_id, neighbor_id=payload.neighbor_id, face_id=payload.face_id)
        return optix.output(value=result)
'''


def compile_adjacency_callback():
    manifest = CallbackModuleManifest(
        name="triangle_adjacency_locator",
        payload_record="CellPayload",
        output_record="CellOutput",
        attribute_types=(),
        constants=(
            FrozenConstant("U32_MAX", U32, 0xFFFFFFFF),
            FrozenConstant("FRONT_HIT_KIND", U32, FRONT_HIT_KIND),
            FrozenConstant("BACK_HIT_KIND", U32, BACK_HIT_KIND),
        ),
        numeric=NumericContract(),
        resources=ResourceBudget(),
        geometry=GeometryContract(
            GeometryAdmission.OPTIX_BUILTIN_SEMANTICS,
            BUILTIN_TRIANGLE_CONTRACT,
            False,
        ),
        any_hit_delivery=None,
        selected_linkage=LinkageMechanism.TRUSTED_SINGLE_MODULE_COMPOSITION_V1,
        linkage_selection_reason="closed V4 built-in-triangle adjacency contract",
    )
    callback = parse_callback_source(
        ADJACENCY_SOURCE,
        manifest,
        schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    )
    return verify_callback_program_for_geometry(
        callback, GeometryFamily.BUILTIN_TRIANGLE)


def adjacency_schema(callback, *, orientation_authority_sha256: str):
    read_only = BufferAccess.READ_ONLY
    hit_roles = (CallbackRole.CLOSEST_HIT,)
    return TypedPhysicalSchemaV1(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        geometry_family=GeometryFamily.BUILTIN_TRIANGLE,
        buffers=(
            BufferFieldSchema("positions_xyz", BufferSemantic.VERTEX_POSITIONS, BufferDomain.VERTEX, PhysicalValueType.VEC3F32, read_only, CountRelation.VERTEX_COUNT, 16),
            BufferFieldSchema("connectivity_abc", BufferSemantic.TRIANGLE_INDICES, BufferDomain.PRIMITIVE, PhysicalValueType.VEC3U32, read_only, CountRelation.PRIMITIVE_COUNT, 16),
            BufferFieldSchema("side_alpha", BufferSemantic.PRIMITIVE_FRONT_VALUE, BufferDomain.PRIMITIVE, PhysicalValueType.U32, read_only, CountRelation.PRIMITIVE_COUNT),
            BufferFieldSchema("side_omega", BufferSemantic.PRIMITIVE_BACK_VALUE, BufferDomain.PRIMITIVE, PhysicalValueType.U32, read_only, CountRelation.PRIMITIVE_COUNT),
            BufferFieldSchema("queries", BufferSemantic.QUERY_INPUT, BufferDomain.QUERY, PhysicalValueType.OPAQUE_RECORD, read_only, CountRelation.QUERY_COUNT, 16),
            BufferFieldSchema("outputs", BufferSemantic.OUTPUT_VALUE, BufferDomain.OUTPUT, PhysicalValueType.OPAQUE_RECORD, BufferAccess.WRITE_ONLY, CountRelation.OUTPUT_COUNT_EQUALS_QUERY_COUNT, 16),
            BufferFieldSchema("status", BufferSemantic.STATUS, BufferDomain.LAUNCH_PARAM, PhysicalValueType.STATUS_RECORD, BufferAccess.INTERNAL_STATUS, CountRelation.SINGLETON, 16),
        ),
        hit_channels=(
            HitChannelSchema(HitChannelSemantic.PRIMITIVE_INDEX, PhysicalValueType.U32, HitChannelProducer.OPTIX_BUILTIN, hit_roles),
            HitChannelSchema(HitChannelSemantic.TRIANGLE_FRONT_BACK_HIT_KIND, PhysicalValueType.U32, HitChannelProducer.OPTIX_BUILTIN, hit_roles),
            HitChannelSchema(HitChannelSemantic.TRIANGLE_BARYCENTRICS, PhysicalValueType.VEC2F32, HitChannelProducer.OPTIX_BUILTIN, hit_roles),
            HitChannelSchema(HitChannelSemantic.PRIMITIVE_METADATA, PhysicalValueType.U32, HitChannelProducer.COMPILER_METADATA_LOOKUP, hit_roles),
        ),
        hit_metadata_bindings=(
            HitMetadataBinding(CallbackRole.CLOSEST_HIT, 2, BufferSemantic.PRIMITIVE_FRONT_VALUE),
            HitMetadataBinding(CallbackRole.CLOSEST_HIT, 3, BufferSemantic.PRIMITIVE_BACK_VALUE),
        ),
        gas=GasSchema(
            GeometryFamily.BUILTIN_TRIANGLE,
            (BufferSemantic.VERTEX_POSITIONS, BufferSemantic.TRIANGLE_INDICES),
            GasUpdatePolicy.STATIC,
            1,
            1,
        ),
        triangle_winding=TriangleWindingPolicy.CCW_IS_FRONT,
        triangle_orientation_authority_sha256=orientation_authority_sha256,
    )


def make_orientation_authority(
    callback,
    *,
    source_semantics_sha256: str,
    independent_oracle_sha256: str,
):
    return TriangleOrientationAuthority(
        contract_name="v4_triangle_adjacency_ccw_front_v1",
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        vertex_positions_semantic=BufferSemantic.VERTEX_POSITIONS,
        triangle_indices_semantic=BufferSemantic.TRIANGLE_INDICES,
        front_values_semantic=BufferSemantic.PRIMITIVE_FRONT_VALUE,
        back_values_semantic=BufferSemantic.PRIMITIVE_BACK_VALUE,
        winding_policy=TriangleWindingPolicy.CCW_IS_FRONT,
        front_hit_kind=FRONT_HIT_KIND,
        back_hit_kind=BACK_HIT_KIND,
        callback_front_hit_kind_constant="FRONT_HIT_KIND",
        callback_back_hit_kind_constant="BACK_HIT_KIND",
        front_hit_selects=AdjacencySide.FRONT,
        back_hit_selects=AdjacencySide.BACK,
        author_source_sha256=source_semantics_sha256,
        author_semantics_sha256=triangle_author_semantics_sha256(
            front_hit_kind=FRONT_HIT_KIND,
            back_hit_kind=BACK_HIT_KIND,
            front_hit_selects=AdjacencySide.FRONT,
            back_hit_selects=AdjacencySide.BACK,
        ),
        independent_cpu_oracle_sha256=independent_oracle_sha256,
    )


@dataclass(frozen=True)
class StandardBuiltinTriangleProgram:
    authority: object
    plan: object
    abi: object
    executable: VerifiedTriangleExecutable
    compiler_log: str


def compile_standard_builtin_triangle_program(
    target: ReferenceTargetProfile,
    *,
    source_semantics_sha256: str,
    independent_oracle_sha256: str,
    compute_capability: tuple[int, int],
    optix_include,
    cuda_include,
    expected_python_version: str,
    expected_numba_version: str,
    expected_numpy_version: str,
):
    from .v4_triangle_optix_compiler import compile_verified_triangle_executable

    callback = compile_adjacency_callback()
    orientation = make_orientation_authority(
        callback,
        source_semantics_sha256=source_semantics_sha256,
        independent_oracle_sha256=independent_oracle_sha256,
    )
    authority = verify_typed_physical_schema(
        callback,
        adjacency_schema(
            callback,
            orientation_authority_sha256=orientation.authority_sha256,
        ),
        target=target,
        orientation_authorities={orientation.authority_sha256: orientation},
    )
    plan = lower_canonical_reference_plan(
        authority, default_reference_templates())
    abi = compile_callback_abi(
        callback, physical_schema_authority=authority)
    executable, compiler_log = compile_verified_triangle_executable(
        authority,
        plan,
        abi,
        compute_capability=compute_capability,
        optix_include=optix_include,
        cuda_include=cuda_include,
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
        expected_numpy_version=expected_numpy_version,
    )
    return StandardBuiltinTriangleProgram(
        authority, plan, abi, executable, compiler_log)


__all__ = [
    "ADJACENCY_SOURCE",
    "BACK_HIT_KIND",
    "FRONT_HIT_KIND",
    "StandardBuiltinTriangleProgram",
    "adjacency_schema",
    "compile_adjacency_callback",
    "compile_standard_builtin_triangle_program",
    "make_orientation_authority",
]

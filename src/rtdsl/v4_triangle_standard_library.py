"""Closed, app-neutral V4 built-in-triangle callback/reducer templates.

Applications select a semantic template explicitly.  They do not provide PTX,
an OptiX callback pointer, or a reducer implementation.  Keeping these
templates in product source (rather than evaluation fixtures) allows real
application front doors to share the exact verified implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .v4_triangle_reduction_optix_compiler import (
        VerifiedTriangleReductionExecutable,
    )

from .v4_callback_abi import AnyHitProofAuthority
from .v4_callback_numba_codegen import FormalNumbaLeafCachePolicy
from .v4_callback_frontend import parse_callback_source
from .v4_callback_ir import (
    AnyHitDeliveryContract,
    CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    CallbackModuleManifest,
    CallbackRole,
    GeometryAdmission,
    GeometryContract,
    LinkageMechanism,
    NumericContract,
    ResourceBudget,
    ScalarKind,
)
from .v4_triangle_reduction import (
    CheckedReducerSpec,
    DuplicatePolicy,
    MetadataDomain,
    ReducerAlgebra,
    ReducerSource,
    ReducerSourceKind,
    TriangleMetadataBinding,
    TriangleMetadataChannel,
    TriangleReductionSchema,
    compile_triangle_reduction_abi,
    compile_triangle_reduction_contract,
    verify_triangle_reduction_schema,
)
from .v4_typed_physical_schema import (
    BUILTIN_TRIANGLE_CONTRACT,
    GeometryFamily,
    ReferenceTargetProfile,
    verify_callback_program_for_geometry,
)


COUNT_SOURCE = r'''
@optix.payload
class CountPayload:
    count: u64
@optix.record
class RayQuery:
    origin: vec3f32
    direction: vec3f32
    tmax: f32
@optix.output
class CountOutput:
    count: u64
@optix.program(payload=CountPayload, output=CountOutput, attributes=(), max_trace_depth=1, max_callable_depth=0)
class TrianglePerRayCount:
    @optix.make_ray
    def make_ray(launch_id: u32, queries: ReadOnlyView[RayQuery]) -> TraceRequest:
        query = queries[launch_id]
        initial = CountPayload(count=0)
        return optix.trace_request(origin=query.origin, direction=query.direction, tmin=0.0, tmax=query.tmax, payload=initial)
    @optix.any_hit
    def any_hit(hit: TriangleHit, payload: CountPayload) -> AnyHitEffect:
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

KEYED_SOURCE = r'''
@optix.payload
class EventPayload:
    accepted: u64
@optix.record
class RayQuery:
    origin: vec3f32
    direction: vec3f32
    tmax: f32
@optix.output
class EventOutput:
    accepted: u64
@optix.program(payload=EventPayload, output=EventOutput, attributes=(), max_trace_depth=1, max_callable_depth=0)
class KeyedTriangleEvents:
    @optix.make_ray
    def make_ray(launch_id: u32, queries: ReadOnlyView[RayQuery]) -> TraceRequest:
        query = queries[launch_id]
        initial = EventPayload(accepted=0)
        return optix.trace_request(origin=query.origin, direction=query.direction, tmin=0.0, tmax=query.tmax, payload=initial)
    @optix.any_hit
    def any_hit(hit: TriangleHit, payload: EventPayload, stable_ids: ReadOnlyView[u64], signed_values: ReadOnlyView[i64], include_flags: ReadOnlyView[u32]) -> AnyHitEffect:
        include = include_flags[hit.primitive_index]
        if include == 1:
            updated = EventPayload(accepted=payload.accepted + 1)
            return optix.accept_continue(payload=updated)
        else:
            return optix.ignore(payload=payload)
    @optix.miss
    def miss(ray: Ray3f, payload: EventPayload) -> EventPayload:
        return optix.payload(payload=payload)
    @optix.finalize
    def finalize(payload: EventPayload) -> EventOutput:
        value = EventOutput(accepted=payload.accepted)
        return optix.output(value=value)
'''


def _manifest(name: str, payload: str, output: str) -> CallbackModuleManifest:
    return CallbackModuleManifest(
        name=name,
        payload_record=payload,
        output_record=output,
        attribute_types=(),
        constants=(),
        numeric=NumericContract(),
        resources=ResourceBudget(),
        geometry=GeometryContract(
            GeometryAdmission.OPTIX_BUILTIN_SEMANTICS,
            BUILTIN_TRIANGLE_CONTRACT,
            False,
        ),
        any_hit_delivery=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        selected_linkage=LinkageMechanism.TRUSTED_SINGLE_MODULE_COMPOSITION_V1,
        linkage_selection_reason="closed V4 triangle reduction contract",
    )


def compile_count_callback():
    program = parse_callback_source(
        COUNT_SOURCE,
        _manifest("per_ray_count", "CountPayload", "CountOutput"),
        schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    )
    return verify_callback_program_for_geometry(
        program, GeometryFamily.BUILTIN_TRIANGLE)


def compile_keyed_callback():
    program = parse_callback_source(
        KEYED_SOURCE,
        _manifest("keyed_events", "EventPayload", "EventOutput"),
        schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    )
    return verify_callback_program_for_geometry(
        program, GeometryFamily.BUILTIN_TRIANGLE)


def _source(kind: ReducerSourceKind, *, semantic=None, field=None) -> ReducerSource:
    return ReducerSource(kind, semantic_id=semantic, output_field=field)


def keyed_i64_sum_schema(callback) -> TriangleReductionSchema:
    channels = (
        TriangleMetadataChannel(
            "primitive.stable_id", "stable_ids", ScalarKind.U64,
            MetadataDomain.PRIMITIVE, True),
        TriangleMetadataChannel(
            "primitive.signed_value", "signed_values", ScalarKind.I64,
            MetadataDomain.PRIMITIVE, True),
        TriangleMetadataChannel(
            "primitive.include", "include_flags", ScalarKind.U32,
            MetadataDomain.PRIMITIVE, True),
    )
    reducer = CheckedReducerSpec(
        ReducerAlgebra.CHECKED_KEYED_I64_SUM,
        (_source(ReducerSourceKind.LAUNCH_INDEX),),
        _source(ReducerSourceKind.METADATA,
                semantic="primitive.signed_value"),
        include_source=_source(
            ReducerSourceKind.METADATA, semantic="primitive.include"),
        event_identity_sources=(
            _source(ReducerSourceKind.METADATA,
                    semantic="primitive.stable_id"),
            _source(ReducerSourceKind.LAUNCH_INDEX),
        ),
        duplicate_policy=DuplicatePolicy.KEYED_IDENTICAL_DEDUP,
        output_capacity=4096,
    )
    return TriangleReductionSchema(
        callback.ir_sha256,
        callback.effect_digest,
        channels,
        (
            TriangleMetadataBinding(
                CallbackRole.ANY_HIT, 2, "primitive.stable_id"),
            TriangleMetadataBinding(
                CallbackRole.ANY_HIT, 3, "primitive.signed_value"),
            TriangleMetadataBinding(
                CallbackRole.ANY_HIT, 4, "primitive.include"),
        ),
        reducer,
    )


def all_hit_count_schema(callback) -> TriangleReductionSchema:
    reducer = CheckedReducerSpec(
        ReducerAlgebra.CHECKED_U64_SUM,
        (),
        _source(ReducerSourceKind.PER_RAY_OUTPUT, field="count"),
        output_capacity=1,
    )
    return TriangleReductionSchema(
        callback.ir_sha256, callback.effect_digest, (), (), reducer)


def weighted_hit_count_schema(callback) -> TriangleReductionSchema:
    channel = TriangleMetadataChannel(
        "query.weight", "query_weights", ScalarKind.U64,
        MetadataDomain.QUERY)
    reducer = CheckedReducerSpec(
        ReducerAlgebra.CHECKED_U64_PRODUCT_SUM,
        (),
        _source(ReducerSourceKind.PER_RAY_OUTPUT, field="count"),
        multiplicand_source=_source(
            ReducerSourceKind.METADATA, semantic="query.weight"),
        output_capacity=1,
    )
    return TriangleReductionSchema(
        callback.ir_sha256,
        callback.effect_digest,
        (channel,),
        (),
        reducer,
    )


@dataclass(frozen=True)
class StandardTriangleProgram:
    authority: object
    proof: AnyHitProofAuthority
    abi: object
    contract: object
    executable: VerifiedTriangleReductionExecutable
    compiler_log: str


def compile_standard_triangle_program(
    callback,
    schema: TriangleReductionSchema,
    target: ReferenceTargetProfile,
    proof: AnyHitProofAuthority,
    *,
    compute_capability: tuple[int, int],
    optix_include,
    cuda_include,
    expected_python_version: str,
    expected_numba_version: str,
    expected_numpy_version: str,
    formal_leaf_cache: FormalNumbaLeafCachePolicy | None = None,
) -> StandardTriangleProgram:
    """Compile one closed standard template without app identity dispatch."""

    from .v4_triangle_reduction_optix_compiler import (
        compile_verified_triangle_reduction_executable,
    )

    authority = verify_triangle_reduction_schema(callback, schema, target=target)
    abi = compile_triangle_reduction_abi(
        authority, any_hit_proof_authority=proof)
    contract = compile_triangle_reduction_contract(
        authority, abi_sha256=abi.abi_sha256)
    executable, compiler_log = compile_verified_triangle_reduction_executable(
        authority,
        contract,
        abi,
        any_hit_proof_authority=proof,
        compute_capability=compute_capability,
        optix_include=optix_include,
        cuda_include=cuda_include,
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
        expected_numpy_version=expected_numpy_version,
        formal_leaf_cache=formal_leaf_cache,
    )
    return StandardTriangleProgram(
        authority, proof, abi, contract, executable, compiler_log)


__all__ = [
    "COUNT_SOURCE",
    "KEYED_SOURCE",
    "all_hit_count_schema",
    "compile_standard_triangle_program",
    "compile_count_callback",
    "compile_keyed_callback",
    "keyed_i64_sum_schema",
    "StandardTriangleProgram",
    "weighted_hit_count_schema",
]

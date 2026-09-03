"""Trusted OptiX wrapper for Goal5838 built-in-sphere any-hit count."""

from __future__ import annotations

import hashlib

from .v4_callback_abi import CallbackAbiError, CompiledCallbackAbi
from .v4_callback_ir import CallbackRole, EffectKind, ScalarKind, TypeKind
from .v4_callback_optix_wrapper_codegen import (
    CallbackWrapperCodegenError,
    GeneratedOptixWrapper,
    _call_block,
    _effect_tag,
    _indent,
    _prototype,
)
from .v4_sphere_any_hit_count_contract import (
    SPHERE_ANY_HIT_COUNT_TEMPLATE,
    SphereAnyHitCountCanonicalPlan,
    VerifiedSphereAnyHitCountAuthority,
    derive_sphere_any_hit_count_proof,
    verify_sphere_any_hit_count_abi,
    verify_sphere_any_hit_count_physical_schema,
)


def _fail(code: str, detail: str) -> None:
    raise CallbackWrapperCodegenError(code, detail)


def _fresh(
    authority: VerifiedSphereAnyHitCountAuthority,
    plan: SphereAnyHitCountCanonicalPlan,
) -> VerifiedSphereAnyHitCountAuthority:
    if type(authority) is not VerifiedSphereAnyHitCountAuthority:
        _fail("sphere_count_authority", "live selected-topology authority required")
    fresh = verify_sphere_any_hit_count_physical_schema(
        authority.callback, authority.schema, target=authority.target
    )
    if fresh != authority or plan != fresh.canonical_plan:
        _fail("sphere_count_authority", "authority/plan does not rederive exactly")
    if plan.template_id != SPHERE_ANY_HIT_COUNT_TEMPLATE or plan.executable:
        _fail("sphere_count_plan", "exact non-executable canonical plan required")
    return fresh


def _single_u64_record(authority, record_name: str) -> None:
    record = next(
        (
            item
            for item in authority.callback.program.records
            if item.name == record_name
        ),
        None,
    )
    if record is None or len(record.fields) != 1:
        _fail("callback_record_shape", f"{record_name}: one field required")
    field = record.fields[0]
    if (
        field.name != "count"
        or field.value_type.kind is not TypeKind.SCALAR
        or field.value_type.scalar is not ScalarKind.U64
    ):
        _fail("callback_record_shape", f"{record_name}: count:u64 required")


def generate_trusted_optix_sphere_any_hit_count_wrapper_v1(
    authority: VerifiedSphereAnyHitCountAuthority,
    plan: SphereAnyHitCountCanonicalPlan,
    abi: CompiledCallbackAbi,
) -> GeneratedOptixWrapper:
    """Compose the selected four-role topology over OptiX built-in spheres."""

    fresh = _fresh(authority, plan)
    proof = derive_sphere_any_hit_count_proof(fresh.callback)
    try:
        canonical = verify_sphere_any_hit_count_abi(
            abi, fresh, proof
        )
    except CallbackAbiError as exc:
        raise CallbackWrapperCodegenError(
            "abi_admission", f"{exc.code}@{exc.path}: {exc.message}"
        ) from exc
    roles = {item.role: item for item in canonical.roles}
    required_roles = {
        CallbackRole.MAKE_RAY,
        CallbackRole.ANY_HIT,
        CallbackRole.MISS,
        CallbackRole.FINALIZE,
    }
    if set(roles) != required_roles:
        _fail(
            "role_set",
            repr(sorted(item.value for item in set(roles) ^ required_roles)),
        )
    program = fresh.callback.program
    _single_u64_record(fresh, program.manifest.payload_record)
    _single_u64_record(fresh, program.manifest.output_record)
    expected_inputs = {
        CallbackRole.MAKE_RAY: {
            "in.context.launch_index",
            "in.launch_id",
            "in.queries.columns.start.x",
            "in.queries.columns.start.y",
            "in.queries.columns.start.z",
            "in.queries.columns.end.x",
            "in.queries.columns.end.y",
            "in.queries.columns.end.z",
            "in.queries.length",
        },
        CallbackRole.ANY_HIT: {
            "in.context.launch_index",
            "in.hit.t",
            "in.hit.hit_kind",
            "in.payload.count",
        },
        CallbackRole.MISS: {
            "in.context.launch_index",
            "in.ray.origin.x",
            "in.ray.origin.y",
            "in.ray.origin.z",
            "in.ray.direction.x",
            "in.ray.direction.y",
            "in.ray.direction.z",
            "in.ray.tmin",
            "in.ray.tmax",
            "in.payload.count",
        },
        CallbackRole.FINALIZE: {
            "in.context.launch_index",
            "in.payload.count",
        },
    }
    for role, expected in expected_inputs.items():
        observed = {item.path for item in roles[role].inputs}
        if observed != expected:
            _fail(
                "template_input_shape",
                f"{role.value}:{sorted(observed ^ expected)}",
            )

    expected_effect_expression = "(" + " : ".join(
        f"expected_role == {roles[role].role_tag}u ? "
        f"{_effect_tag(roles[role], effect)}u"
        for role, effect in (
            (CallbackRole.MAKE_RAY, EffectKind.TRACE_REQUEST),
            (CallbackRole.ANY_HIT, EffectKind.ACCEPT_CONTINUE),
            (CallbackRole.MISS, EffectKind.PAYLOAD),
            (CallbackRole.FINALIZE, EffectKind.OUTPUT),
        )
    ) + " : 0u)"
    prototypes = "\n".join(
        _prototype(roles[role])
        for role in sorted(required_roles, key=lambda item: list(CallbackRole).index(item))
    )
    common = r'''
#include <optix_device.h>
struct V4SphereLaunchStatus {
    unsigned int first_error_claimed, error_code, stage, role;
    unsigned long long launch_index;
    unsigned int error_site, effect_tag, nonce_word, invocation_mask;
};
struct V4SphereParams {
    OptixTraversableHandle traversable;
    const float* query_sx; const float* query_sy; const float* query_sz;
    const float* query_ex; const float* query_ey; const float* query_ez;
    const unsigned int* application_ids;
    unsigned int primitive_count, query_count;
    unsigned int* output_0; unsigned int* output_1; unsigned int* output_2;
    unsigned int* observed_primitive_index; unsigned int* observed_hit_kind;
    float* observed_t;
    V4SphereLaunchStatus* status; unsigned long long* role_counters;
};
extern "C" { __constant__ V4SphereParams params; }
static __forceinline__ __device__ unsigned long long v4_join_u64(
        unsigned int low, unsigned int high) {
    return (static_cast<unsigned long long>(high) << 32) |
           static_cast<unsigned long long>(low);
}
static __forceinline__ __device__ unsigned int v4_u64_low(
        unsigned long long value) { return static_cast<unsigned int>(value); }
static __forceinline__ __device__ unsigned int v4_u64_high(
        unsigned long long value) { return static_cast<unsigned int>(value >> 32); }
static __forceinline__ __device__ void v4_sphere_first_error(
        unsigned int query, unsigned int code, unsigned int stage,
        unsigned int role, unsigned long long launch_index,
        unsigned int site, unsigned int effect, unsigned int nonce) {
    if (query >= params.query_count || code == 0u) return;
    V4SphereLaunchStatus* record = params.status + query;
    if (atomicCAS(&record->first_error_claimed, 0u, 1u) == 0u) {
        record->error_code = code; record->stage = stage; record->role = role;
        record->launch_index = launch_index; record->error_site = site;
        record->effect_tag = effect; record->nonce_word = nonce;
    }
}
static __forceinline__ __device__ bool v4_commit_leaf_status(
        unsigned int query, unsigned int ok, unsigned int error_code,
        unsigned int stage, unsigned int role, unsigned long long launch_index,
        unsigned int error_site, unsigned int effect_tag, unsigned int nonce,
        unsigned int invocation_mask, unsigned int first_error_claimed,
        unsigned int expected_stage, unsigned int expected_role,
        unsigned int expected_nonce) {
    const unsigned int expected_mask = 1u << (expected_role - 1u);
    const unsigned int expected_effect_tag = __RTDL_EXPECTED_EFFECT_TAG__;
    const bool valid = ok == 1u && error_code == 0u &&
        stage == expected_stage && role == expected_role &&
        launch_index == static_cast<unsigned long long>(query) &&
        error_site == 0u && nonce == expected_nonce &&
        invocation_mask == expected_mask && first_error_claimed == 0u &&
        expected_effect_tag != 0u && effect_tag == expected_effect_tag;
    if (!valid) {
        v4_sphere_first_error(query, error_code ? error_code : 0xffff3801u,
                              stage, role, launch_index, error_site,
                              effect_tag, nonce);
        return false;
    }
    atomicOr(&params.status[query].invocation_mask, invocation_mask);
    atomicAdd(params.role_counters + expected_role - 1u, 1ull);
    return true;
}
'''
    if common.count("__RTDL_EXPECTED_EFFECT_TAG__") != 1:
        raise AssertionError("effect-tag marker cardinality changed")
    common = common.replace(
        "__RTDL_EXPECTED_EFFECT_TAG__", expected_effect_expression
    )

    query = "query"
    make_ray, make_out = _call_block(
        roles[CallbackRole.MAKE_RAY],
        "mr",
        {
            "in.context.launch_index": query,
            "in.launch_id": query,
            "in.queries.columns.start.x": "params.query_sx",
            "in.queries.columns.start.y": "params.query_sy",
            "in.queries.columns.start.z": "params.query_sz",
            "in.queries.columns.end.x": "params.query_ex",
            "in.queries.columns.end.y": "params.query_ey",
            "in.queries.columns.end.z": "params.query_ez",
            "in.queries.length": "(unsigned long long)params.query_count",
        },
        query_expression=query,
        failure_statement="return;",
    )
    any_hit, any_out = _call_block(
        roles[CallbackRole.ANY_HIT],
        "ah",
        {
            "in.context.launch_index": query,
            "in.hit.t": "hit_t",
            "in.hit.hit_kind": "optixGetHitKind()",
            "in.payload.count": "v4_join_u64(optixGetPayload_0(), optixGetPayload_1())",
        },
        query_expression=query,
        failure_statement="optixTerminateRay(); return;",
    )
    miss, miss_out = _call_block(
        roles[CallbackRole.MISS],
        "ms",
        {
            "in.context.launch_index": query,
            "in.ray.origin.x": "origin.x",
            "in.ray.origin.y": "origin.y",
            "in.ray.origin.z": "origin.z",
            "in.ray.direction.x": "direction.x",
            "in.ray.direction.y": "direction.y",
            "in.ray.direction.z": "direction.z",
            "in.ray.tmin": "optixGetRayTmin()",
            "in.ray.tmax": "optixGetRayTmax()",
            "in.payload.count": "v4_join_u64(optixGetPayload_0(), optixGetPayload_1())",
        },
        query_expression=query,
        failure_statement="return;",
    )
    finalize, finalize_out = _call_block(
        roles[CallbackRole.FINALIZE],
        "fin",
        {
            "in.context.launch_index": query,
            "in.payload.count": "v4_join_u64(payload_0, payload_1)",
        },
        query_expression=query,
        failure_statement="return;",
    )

    raygen = f'''
extern "C" __global__ void __raygen__rtdl_v4_sphere() {{
    const unsigned int query = optixGetLaunchIndex().x;
    if (query >= params.query_count) return;
    params.status[query] = {{0u,0u,0u,0u,(unsigned long long)query,0u,0u,0u,0u}};
    params.observed_primitive_index[query] = 0xffffffffu;
    params.observed_hit_kind[query] = 0xffffffffu;
    params.observed_t[query] = __int_as_float(0x7fffffffu);
{_indent(make_ray, 4)}
    if ({make_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.MAKE_RAY], EffectKind.TRACE_REQUEST)}u) {{
        v4_sphere_first_error(query,0xffff3802u,0u,0u,query,0u,{make_out['out.effect_tag']},0u);
        return;
    }}
    unsigned long long initial_count = {make_out['out.trace_request.payload.count']};
    unsigned int payload_0 = v4_u64_low(initial_count);
    unsigned int payload_1 = v4_u64_high(initial_count);
    unsigned int payload_2 = 0u, payload_3 = 0u, payload_4 = 0u;
    unsigned int payload_5 = 0u, payload_6 = 0u, payload_7 = 0u;
    optixTrace(params.traversable,
        make_float3({make_out['out.trace_request.origin.x']},{make_out['out.trace_request.origin.y']},{make_out['out.trace_request.origin.z']}),
        make_float3({make_out['out.trace_request.direction.x']},{make_out['out.trace_request.direction.y']},{make_out['out.trace_request.direction.z']}),
        {make_out['out.trace_request.tmin']},{make_out['out.trace_request.tmax']},
        0.0f,OptixVisibilityMask(255),OPTIX_RAY_FLAG_DISABLE_CLOSESTHIT,
        0,1,0,payload_0,payload_1,payload_2,payload_3,
        payload_4,payload_5,payload_6,payload_7);
    if (params.status[query].first_error_claimed != 0u) return;
{_indent(finalize, 4)}
    if ({finalize_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.FINALIZE], EffectKind.OUTPUT)}u) {{
        v4_sphere_first_error(query,0xffff3803u,0u,0u,query,0u,{finalize_out['out.effect_tag']},0u);
        return;
    }}
    const unsigned long long result = {finalize_out['out.output.value.count']};
    params.output_0[query] = v4_u64_low(result);
    params.output_1[query] = v4_u64_high(result);
    params.output_2[query] = 0u;
}}
'''
    anyhit_program = f'''
extern "C" __global__ void __anyhit__rtdl_v4_sphere_canonical() {{
    const unsigned int query = optixGetLaunchIndex().x;
    const unsigned int primitive = optixGetPrimitiveIndex();
    if (query >= params.query_count || primitive >= params.primitive_count) {{
        v4_sphere_first_error(query,0xffff3804u,0u,0u,query,0u,0u,0u);
        optixTerminateRay();
        return;
    }}
    const float hit_t = optixGetRayTmax();
    if (!isfinite(hit_t) || hit_t < optixGetRayTmin()) {{
        v4_sphere_first_error(query,0xffff3805u,0u,0u,query,0u,0u,0u);
        optixTerminateRay();
        return;
    }}
{_indent(any_hit, 4)}
    if ({any_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.ANY_HIT], EffectKind.ACCEPT_CONTINUE)}u) {{
        v4_sphere_first_error(query,0xffff3806u,0u,0u,query,0u,{any_out['out.effect_tag']},0u);
        optixTerminateRay();
        return;
    }}
    const unsigned long long updated = {any_out['out.accept_continue.payload.count']};
    optixSetPayload_0(v4_u64_low(updated));
    optixSetPayload_1(v4_u64_high(updated));
    optixIgnoreIntersection();
}}
'''
    miss_program = f'''
extern "C" __global__ void __miss__rtdl_v4_sphere() {{
    const unsigned int query = optixGetLaunchIndex().x;
    if (query >= params.query_count) return;
    const float3 origin = optixGetWorldRayOrigin();
    const float3 direction = optixGetWorldRayDirection();
{_indent(miss, 4)}
    if ({miss_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.MISS], EffectKind.PAYLOAD)}u) {{
        v4_sphere_first_error(query,0xffff3807u,0u,0u,query,0u,{miss_out['out.effect_tag']},0u);
        return;
    }}
    const unsigned long long updated = {miss_out['out.payload.payload.count']};
    optixSetPayload_0(v4_u64_low(updated));
    optixSetPayload_1(v4_u64_high(updated));
}}
'''
    source = common + "\n" + prototypes + "\n" + raygen + anyhit_program + miss_program
    return GeneratedOptixWrapper(
        schema="rtdl.v4.generated_trusted_optix_sphere_any_hit_count_wrapper.v1",
        physical_template=SPHERE_ANY_HIT_COUNT_TEMPLATE,
        callback_ir_sha256=fresh.callback.ir_sha256,
        callback_abi_sha256=canonical.abi_sha256,
        source=source,
        source_sha256=hashlib.sha256(source.encode("utf-8")).hexdigest(),
        role_symbols=tuple(
            (role.value, roles[role].symbol)
            for role in sorted(
                required_roles, key=lambda item: list(CallbackRole).index(item)
            )
        ),
    )


__all__ = ["generate_trusted_optix_sphere_any_hit_count_wrapper_v1"]

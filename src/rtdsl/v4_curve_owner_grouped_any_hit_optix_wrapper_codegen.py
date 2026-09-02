"""Trusted OptiX wrapper for curve owner-grouped any-hit Boolean OR."""

from __future__ import annotations

import hashlib

from .v4_callback_abi import CompiledCallbackAbi
from .v4_callback_ir import CallbackRole, EffectKind
from .v4_callback_optix_wrapper_codegen import (
    CallbackWrapperCodegenError,
    GeneratedOptixWrapper,
    _call_block,
    _effect_tag,
    _indent,
    _prototype,
)
from .v4_curve_owner_grouped_any_hit import (
    CURVE_OWNER_GROUPED_PHYSICAL_TEMPLATE,
    VerifiedCurveOwnerGroupedAnyHitAuthority,
    verify_curve_owner_grouped_any_hit_physical_schema,
)
from .v4_owner_grouped_any_hit import verify_owner_grouped_any_hit_abi


def _fail(code: str, detail: str) -> None:
    raise CallbackWrapperCodegenError(code, detail)


def generate_trusted_optix_curve_owner_grouped_any_hit_wrapper_v1(
    authority: VerifiedCurveOwnerGroupedAnyHitAuthority,
    abi: CompiledCallbackAbi,
) -> GeneratedOptixWrapper:
    fresh = verify_curve_owner_grouped_any_hit_physical_schema(
        authority.behavior, authority.schema, target=authority.target)
    if fresh != authority or authority.canonical_plan.executable:
        _fail("authority_reverification", "live non-executable authority required")
    canonical = verify_owner_grouped_any_hit_abi(abi, fresh.behavior)
    roles = {item.role: item for item in canonical.roles}
    required = (
        CallbackRole.MAKE_RAY,
        CallbackRole.ANY_HIT,
        CallbackRole.MISS,
        CallbackRole.FINALIZE,
    )
    if set(roles) != set(required):
        _fail("role_set", repr(sorted(item.value for item in set(roles) ^ set(required))))
    any_hit_effects = roles[CallbackRole.ANY_HIT].effects
    if len(any_hit_effects) != 1 \
            or any_hit_effects[0].kind is not EffectKind.ACCEPT_CONTINUE:
        _fail("any_hit_effect", "exact pass-through accept_continue required")

    expected_inputs = {
        CallbackRole.MAKE_RAY: {
            "in.context.launch_index", "in.launch_id",
            "in.queries.columns.start.x", "in.queries.columns.start.y",
            "in.queries.columns.start.z", "in.queries.columns.end.x",
            "in.queries.columns.end.y", "in.queries.columns.end.z",
            "in.queries.length",
        },
        CallbackRole.ANY_HIT: {
            "in.context.launch_index", "in.hit.t", "in.hit.hit_kind",
            "in.payload.token",
        },
        CallbackRole.MISS: {
            "in.context.launch_index", "in.ray.origin.x", "in.ray.origin.y",
            "in.ray.origin.z", "in.ray.direction.x", "in.ray.direction.y",
            "in.ray.direction.z", "in.ray.tmin", "in.ray.tmax",
            "in.payload.token",
        },
        CallbackRole.FINALIZE: {
            "in.context.launch_index", "in.payload.token",
        },
    }
    for role, expected in expected_inputs.items():
        observed = {item.path for item in roles[role].inputs}
        if observed != expected:
            _fail("template_input_shape", f"{role.value}:{sorted(observed ^ expected)}")

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
    prototypes = "\n".join(_prototype(roles[role]) for role in required)
    common = r'''
#include <optix_device.h>
struct V4CurveOwnerGroupedStatus {
    unsigned int first_error_claimed, error_code, stage, role;
    unsigned long long launch_index;
    unsigned int error_site, effect_tag, nonce_word, invocation_mask;
};
struct V4CurveOwnerGroupedParams {
    OptixTraversableHandle traversable;
    const float* query_sx; const float* query_sy; const float* query_sz;
    const float* query_ex; const float* query_ey; const float* query_ez;
    const unsigned int* owner_ids;
    unsigned int primitive_count, query_count, owner_count;
    unsigned int* owner_hit_bits;
    unsigned int* query_completion_tokens;
    V4CurveOwnerGroupedStatus* status;
    unsigned long long* role_counters;
};
extern "C" { __constant__ V4CurveOwnerGroupedParams params; }
static __forceinline__ __device__ void v4_owner_grouped_first_error(
        unsigned int query, unsigned int code, unsigned int stage,
        unsigned int role, unsigned long long launch_index,
        unsigned int site, unsigned int effect, unsigned int nonce) {
    if (query >= params.query_count || code == 0u) return;
    V4CurveOwnerGroupedStatus* record = params.status + query;
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
    const unsigned int expected_effect_tag = __RTDL_EXPECTED_GROUPED_EFFECT_TAG__;
    const bool valid = ok == 1u && error_code == 0u &&
        stage == expected_stage && role == expected_role &&
        launch_index == (unsigned long long)query && error_site == 0u &&
        nonce == expected_nonce && invocation_mask == expected_mask &&
        first_error_claimed == 0u && expected_effect_tag != 0u &&
        effect_tag == expected_effect_tag;
    if (!valid) {
        v4_owner_grouped_first_error(
            query, error_code ? error_code : 0xffff6101u,
            stage, role, launch_index, error_site, effect_tag, nonce);
        return false;
    }
    atomicOr(&params.status[query].invocation_mask, invocation_mask);
    atomicAdd(params.role_counters + expected_role - 1u, 1ull);
    return true;
}
'''
    if common.count("__RTDL_EXPECTED_GROUPED_EFFECT_TAG__") != 1:
        raise AssertionError("owner-grouped effect marker cardinality changed")
    common = common.replace(
        "__RTDL_EXPECTED_GROUPED_EFFECT_TAG__", expected_effect_expression)

    q = "query"
    make_ray, make_ray_out = _call_block(
        roles[CallbackRole.MAKE_RAY], "mr", {
            "in.context.launch_index": q,
            "in.launch_id": q,
            "in.queries.columns.start.x": "params.query_sx",
            "in.queries.columns.start.y": "params.query_sy",
            "in.queries.columns.start.z": "params.query_sz",
            "in.queries.columns.end.x": "params.query_ex",
            "in.queries.columns.end.y": "params.query_ey",
            "in.queries.columns.end.z": "params.query_ez",
            "in.queries.length": "(unsigned long long)params.query_count",
        }, query_expression=q, failure_statement="return;")
    finalize, finalize_out = _call_block(
        roles[CallbackRole.FINALIZE], "fin", {
            "in.context.launch_index": q,
            "in.payload.token": "payload_token",
        }, query_expression=q, failure_statement="return;")
    raygen = f'''
extern "C" __global__ void __raygen__rtdl_v4_curve_owner_grouped() {{
    const unsigned int query = optixGetLaunchIndex().x;
    if (query >= params.query_count) return;
    params.status[query] = {{0u,0u,0u,0u,(unsigned long long)query,0u,0u,0u,0u}};
{_indent(make_ray, 4)}
    if ({make_ray_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.MAKE_RAY], EffectKind.TRACE_REQUEST)}u) {{
        v4_owner_grouped_first_error(query,0xffff6102u,0u,0u,query,0u,
                                     {make_ray_out['out.effect_tag']},0u); return;
    }}
    unsigned int payload_token = {make_ray_out['out.trace_request.payload.token']};
    const float ray_tmin = {make_ray_out['out.trace_request.tmin']};
    const float ray_tmax = {make_ray_out['out.trace_request.tmax']};
    optixTrace(params.traversable,
        make_float3({make_ray_out['out.trace_request.origin.x']},
                    {make_ray_out['out.trace_request.origin.y']},
                    {make_ray_out['out.trace_request.origin.z']}),
        make_float3({make_ray_out['out.trace_request.direction.x']},
                    {make_ray_out['out.trace_request.direction.y']},
                    {make_ray_out['out.trace_request.direction.z']}),
        ray_tmin, ray_tmax, 0.0f, OptixVisibilityMask(255),
        OPTIX_RAY_FLAG_DISABLE_CLOSESTHIT, 0, 1, 0, payload_token);
    if (params.status[query].first_error_claimed != 0u) return;
{_indent(finalize, 4)}
    if ({finalize_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.FINALIZE], EffectKind.OUTPUT)}u) {{
        v4_owner_grouped_first_error(query,0xffff6103u,0u,0u,query,0u,
                                     {finalize_out['out.effect_tag']},0u); return;
    }}
    params.query_completion_tokens[query] =
        {finalize_out['out.output.value.token']};
}}
'''

    any_hit, any_hit_out = _call_block(
        roles[CallbackRole.ANY_HIT], "ah", {
            "in.context.launch_index": q,
            "in.hit.t": "optixGetRayTmax()",
            "in.hit.hit_kind": "optixGetHitKind()",
            "in.payload.token": "payload_token",
        }, query_expression=q,
        failure_statement="optixTerminateRay(); return;")
    accept_tag = _effect_tag(
        roles[CallbackRole.ANY_HIT], EffectKind.ACCEPT_CONTINUE)
    anyhit_source = f'''
extern "C" __global__ void __anyhit__rtdl_v4_curve_owner_grouped() {{
    const unsigned int query = optixGetLaunchIndex().x;
    const unsigned int primitive = optixGetPrimitiveIndex();
    if (query >= params.query_count || primitive >= params.primitive_count) {{
        v4_owner_grouped_first_error(query,0xffff6104u,0u,0u,query,0u,0u,0u);
        optixTerminateRay(); return;
    }}
    unsigned int payload_token = optixGetPayload_0();
{_indent(any_hit, 4)}
    if ({any_hit_out['out.effect_tag']} != {accept_tag}u) {{
        v4_owner_grouped_first_error(query,0xffff6105u,0u,0u,query,0u,
                                     {any_hit_out['out.effect_tag']},0u);
        optixTerminateRay(); return;
    }}
    const unsigned int owner = params.owner_ids[primitive];
    if (owner >= params.owner_count) {{
        v4_owner_grouped_first_error(query,0xffff6106u,0u,0u,query,0u,
                                     {any_hit_out['out.effect_tag']},0u);
        optixTerminateRay(); return;
    }}
    atomicOr(params.owner_hit_bits + owner, 1u);
    payload_token = {any_hit_out['out.accept_continue.payload.token']};
    optixSetPayload_0(payload_token);
    optixIgnoreIntersection();
}}
'''

    miss, miss_out = _call_block(
        roles[CallbackRole.MISS], "ms", {
            "in.context.launch_index": q,
            "in.ray.origin.x": "optixGetWorldRayOrigin().x",
            "in.ray.origin.y": "optixGetWorldRayOrigin().y",
            "in.ray.origin.z": "optixGetWorldRayOrigin().z",
            "in.ray.direction.x": "optixGetWorldRayDirection().x",
            "in.ray.direction.y": "optixGetWorldRayDirection().y",
            "in.ray.direction.z": "optixGetWorldRayDirection().z",
            "in.ray.tmin": "optixGetRayTmin()",
            "in.ray.tmax": "optixGetRayTmax()",
            "in.payload.token": "payload_token",
        }, query_expression=q, failure_statement="return;")
    miss_source = f'''
extern "C" __global__ void __miss__rtdl_v4_curve_owner_grouped() {{
    const unsigned int query = optixGetLaunchIndex().x;
    unsigned int payload_token = optixGetPayload_0();
{_indent(miss, 4)}
    if ({miss_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.MISS], EffectKind.PAYLOAD)}u) {{
        v4_owner_grouped_first_error(query,0xffff6107u,0u,0u,query,0u,
                                     {miss_out['out.effect_tag']},0u); return;
    }}
    optixSetPayload_0({miss_out['out.payload.payload.token']});
}}
'''
    source = common + "\n" + prototypes + "\n" + raygen + anyhit_source + miss_source
    forbidden = ("collision", "trajectory", "robot", "pose", "raydb")
    if any(word in source.lower() for word in forbidden):
        raise AssertionError("application vocabulary entered owner-grouped wrapper")
    return GeneratedOptixWrapper(
        schema="rtdl.v4.generated_curve_owner_grouped_any_hit_wrapper.v1",
        physical_template=CURVE_OWNER_GROUPED_PHYSICAL_TEMPLATE,
        callback_ir_sha256=fresh.callback.ir_sha256,
        callback_abi_sha256=canonical.abi_sha256,
        source=source,
        source_sha256=hashlib.sha256(source.encode("utf-8")).hexdigest(),
        role_symbols=tuple((role.value, roles[role].symbol) for role in required),
        linked_role_symbols=True,
    )


__all__ = [
    "generate_trusted_optix_curve_owner_grouped_any_hit_wrapper_v1",
]

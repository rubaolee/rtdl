"""Trusted OptiX built-in-sphere wrapper for Goal5833 Callback IR."""

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
from .v4_sphere_physical_schema import (
    BUILTIN_SPHERE_TEMPLATE,
    SphereCanonicalPlan,
    VerifiedSpherePhysicalAuthority,
    verify_builtin_sphere_physical_schema,
)
from .v4_sphere_callback_abi import verify_sphere_callback_abi


def _fail(code: str, detail: str) -> None:
    raise CallbackWrapperCodegenError(code, detail)


def _fresh(authority, plan):
    if not isinstance(authority, VerifiedSpherePhysicalAuthority):
        _fail("sphere_authority", "live VerifiedSpherePhysicalAuthority required")
    fresh = verify_builtin_sphere_physical_schema(
        authority.callback, authority.schema, target=authority.target)
    if fresh != authority or plan != fresh.canonical_plan:
        _fail("sphere_authority", "authority/plan does not rederive exactly")
    if plan.template_id != BUILTIN_SPHERE_TEMPLATE or plan.executable:
        _fail("sphere_plan", "non-executable canonical sphere plan required")
    return fresh


def _record_fields(authority, record_name: str, expected_kinds):
    record = next(
        (item for item in authority.callback.program.records if item.name == record_name), None)
    if record is None or len(record.fields) != len(expected_kinds):
        _fail(
            "callback_record_shape",
            f"{record_name}: exactly {len(expected_kinds)} fields required",
        )
    observed = tuple((item.name, item.value_type) for item in record.fields)
    if any(value_type.kind is not TypeKind.SCALAR or value_type.scalar is not kind
           for (_, value_type), kind in zip(observed, expected_kinds)):
        _fail(
            "callback_record_shape",
            f"{record_name}: expected "
            f"{tuple(item.value for item in expected_kinds)!r}",
        )
    return observed


def _to_payload(value_type, expression: str) -> str:
    return f"__float_as_uint({expression})" if value_type.scalar is ScalarKind.F32 else expression


def _from_payload(index: int, value_type) -> str:
    return f"__uint_as_float(payload_{index})" if value_type.scalar is ScalarKind.F32 else f"payload_{index}"


def _generate_trusted_optix_first_contact_wrapper_v1(
    authority,
    plan,
    abi: CompiledCallbackAbi,
    *,
    fresh_validator,
    abi_validator,
    template_id: str,
    namespace: str,
    wrapper_schema: str,
    record_scalar_kinds=(ScalarKind.U32, ScalarKind.F32, ScalarKind.U32),
    physical_payload_slots: int = 3,
    physical_output_slots: int = 3,
) -> GeneratedOptixWrapper:
    """Generate the shared trusted first-contact wrapper after provider checks.

    Provider adapters remain responsible for rederiving their exact physical
    authority, canonical plan, and ABI before entering this helper.  The
    generated control flow is intentionally shared: OptiX owns primitive
    intersection, while the compiler-owned any-hit enumerator orders the
    platform-produced ``(t, primitive_index)`` events by application ID.
    """

    if namespace not in ("sphere", "curve"):
        _fail("wrapper_namespace", repr(namespace))
    fresh = fresh_validator(authority, plan)
    try:
        canonical = abi_validator(abi, fresh)
    except CallbackAbiError as exc:
        raise CallbackWrapperCodegenError(
            "abi_admission", f"{exc.code}@{exc.path}: {exc.message}") from exc
    roles = {item.role: item for item in canonical.roles}
    required_roles = {
        CallbackRole.MAKE_RAY, CallbackRole.CLOSEST_HIT,
        CallbackRole.MISS, CallbackRole.FINALIZE,
    }
    if set(roles) != required_roles:
        _fail("role_set", repr(sorted(item.value for item in set(roles) ^ required_roles)))
    program = fresh.callback.program
    if not record_scalar_kinds \
            or len(record_scalar_kinds) > physical_payload_slots \
            or len(record_scalar_kinds) > physical_output_slots \
            or physical_payload_slots != 3 or physical_output_slots != 3:
        _fail("physical_record_slots", "exact one-to-three fields over u32x3 required")
    payload_fields = _record_fields(
        fresh, program.manifest.payload_record, record_scalar_kinds)
    output_fields = _record_fields(
        fresh, program.manifest.output_record, record_scalar_kinds)
    closest = program.function_for_role(CallbackRole.CLOSEST_HIT)
    if len(closest.arguments) != 3:
        _fail("closest_hit_shape", "expected Hit, payload, and one application-id view")
    metadata_name = closest.arguments[2].name

    query_inputs = {
        "in.context.launch_index", "in.launch_id",
        "in.queries.columns.start.x", "in.queries.columns.start.y", "in.queries.columns.start.z",
        "in.queries.columns.end.x", "in.queries.columns.end.y", "in.queries.columns.end.z",
        "in.queries.length",
    }
    payload_paths = {f"in.payload.{name}" for name, _ in payload_fields}
    expected_inputs = {
        CallbackRole.MAKE_RAY: query_inputs,
        CallbackRole.CLOSEST_HIT: {
            "in.context.launch_index", "in.hit.t", "in.hit.hit_kind", *payload_paths,
            f"in.{metadata_name}.columns", f"in.{metadata_name}.length",
        },
        CallbackRole.MISS: {
            "in.context.launch_index", "in.ray.origin.x", "in.ray.origin.y",
            "in.ray.origin.z", "in.ray.direction.x", "in.ray.direction.y",
            "in.ray.direction.z", "in.ray.tmin", "in.ray.tmax", *payload_paths,
        },
        CallbackRole.FINALIZE: {"in.context.launch_index", *payload_paths},
    }
    for role, expected in expected_inputs.items():
        observed = {item.path for item in roles[role].inputs}
        if observed != expected:
            _fail("template_input_shape", f"{role.value}:{sorted(observed ^ expected)}")

    expected_effect_expression = "(" + " : ".join(
        f"expected_role == {roles[role].role_tag}u ? "
        f"{_effect_tag(roles[role], kind)}u"
        for role, kind in (
            (CallbackRole.MAKE_RAY, EffectKind.TRACE_REQUEST),
            (CallbackRole.CLOSEST_HIT, EffectKind.PAYLOAD),
            (CallbackRole.MISS, EffectKind.PAYLOAD),
            (CallbackRole.FINALIZE, EffectKind.OUTPUT),
        )
    ) + " : 0u)"

    prototypes = "\n".join(
        _prototype(roles[role])
        for role in sorted(required_roles, key=lambda item: list(CallbackRole).index(item)))
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
    const unsigned int expected_effect_tag = __RTDL_EXPECTED_SPHERE_EFFECT_TAG__;
    const bool valid = ok == 1u && error_code == 0u &&
        stage == expected_stage && role == expected_role &&
        launch_index == (unsigned long long)query && error_site == 0u &&
        nonce == expected_nonce && invocation_mask == expected_mask &&
        first_error_claimed == 0u && expected_effect_tag != 0u &&
        effect_tag == expected_effect_tag;
    if (!valid) {
        v4_sphere_first_error(query, error_code ? error_code : 0xffff3001u,
                              stage, role, launch_index, error_site, effect_tag, nonce);
        return false;
    }
    atomicOr(&params.status[query].invocation_mask, invocation_mask);
    atomicAdd(params.role_counters + expected_role - 1u, 1ull);
    return true;
}
'''
    if common.count("__RTDL_EXPECTED_SPHERE_EFFECT_TAG__") != 1:
        raise AssertionError("sphere status-effect marker cardinality changed")
    common = common.replace(
        "__RTDL_EXPECTED_SPHERE_EFFECT_TAG__", expected_effect_expression)
    q = "query"
    mr, mr_out = _call_block(roles[CallbackRole.MAKE_RAY], "mr", {
        "in.context.launch_index": q, "in.launch_id": q,
        "in.queries.columns.start.x": "params.query_sx",
        "in.queries.columns.start.y": "params.query_sy",
        "in.queries.columns.start.z": "params.query_sz",
        "in.queries.columns.end.x": "params.query_ex",
        "in.queries.columns.end.y": "params.query_ey",
        "in.queries.columns.end.z": "params.query_ez",
        "in.queries.length": "(unsigned long long)params.query_count",
    }, query_expression=q, failure_statement="return;")
    payload_init_values = [
        f"    unsigned int payload_{index} = "
        f"{_to_payload(value_type, mr_out[f'out.trace_request.payload.{name}'])};"
        for index, (name, value_type) in enumerate(payload_fields)]
    payload_init_values.extend(
        f"    unsigned int payload_{index} = 0u;"
        for index in range(len(payload_fields), physical_payload_slots))
    payload_init = "\n".join(payload_init_values)
    payload_args = ", ".join(
        f"payload_{index}" for index in range(physical_payload_slots))

    closest_inputs = {
        "in.context.launch_index": q, "in.hit.t": "selected_hit_t",
        "in.hit.hit_kind": "selected_hit_kind",
        f"in.{metadata_name}.columns": "params.application_ids + selected_primitive_index",
        f"in.{metadata_name}.length": "1ull",
    }
    miss_inputs = {
        "in.context.launch_index": q,
        "in.ray.origin.x": "__uint_as_float(ray_ox)",
        "in.ray.origin.y": "__uint_as_float(ray_oy)",
        "in.ray.origin.z": "__uint_as_float(ray_oz)",
        "in.ray.direction.x": "__uint_as_float(ray_dx)",
        "in.ray.direction.y": "__uint_as_float(ray_dy)",
        "in.ray.direction.z": "__uint_as_float(ray_dz)",
        # The miss role must observe the exact interval returned by make_ray.
        # A literal [0,1] here would make TraceRequest.tmin/tmax decorative even
        # if optixTrace itself were corrected below.
        "in.ray.tmin": "ray_tmin", "in.ray.tmax": "ray_tmax",
    }
    finalize_inputs = {"in.context.launch_index": q}
    for index, (name, value_type) in enumerate(payload_fields):
        expression = _from_payload(index, value_type)
        closest_inputs[f"in.payload.{name}"] = expression
        miss_inputs[f"in.payload.{name}"] = expression
        finalize_inputs[f"in.payload.{name}"] = expression
    ch, ch_out = _call_block(
        roles[CallbackRole.CLOSEST_HIT], "ch", closest_inputs,
        query_expression=q, failure_statement="return;")
    ms, ms_out = _call_block(
        roles[CallbackRole.MISS], "ms", miss_inputs,
        query_expression=q, failure_statement="return;")
    fin, fin_out = _call_block(
        roles[CallbackRole.FINALIZE], "fin", finalize_inputs,
        query_expression=q, failure_statement="return;")
    assign_ch = "\n".join(
        f"        payload_{index} = {_to_payload(value_type, ch_out[f'out.payload.payload.{name}'])};"
        for index, (name, value_type) in enumerate(payload_fields))
    assign_ms = "\n".join(
        f"        payload_{index} = {_to_payload(value_type, ms_out[f'out.payload.payload.{name}'])};"
        for index, (name, value_type) in enumerate(payload_fields))
    output_expr = [
        _to_payload(value_type, fin_out[f"out.output.value.{name}"])
        for name, value_type in output_fields]
    output_expr.extend(
        "0u" for _index in range(len(output_expr), physical_output_slots))
    output_assignments = "\n".join(
        f"    params.output_{index}[query]={expression};"
        for index, expression in enumerate(output_expr))

    raygen = f'''
extern "C" __global__ void __raygen__rtdl_v4_sphere() {{
    const unsigned int query = optixGetLaunchIndex().x;
    if (query >= params.query_count) return;
    params.status[query] = {{0u,0u,0u,0u,(unsigned long long)query,0u,0u,0u,0u}};
    params.observed_primitive_index[query]=0xffffffffu;
    params.observed_hit_kind[query]=0xffffffffu;
    params.observed_t[query]=__int_as_float(0x7fffffffu);
{_indent(mr, 4)}
    if ({mr_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.MAKE_RAY], EffectKind.TRACE_REQUEST)}u) {{
        v4_sphere_first_error(query,0xffff3002u,0u,0u,query,0u,{mr_out['out.effect_tag']},0u); return;
    }}
{payload_init}
    unsigned int ray_ox=__float_as_uint({mr_out['out.trace_request.origin.x']});
    unsigned int ray_oy=__float_as_uint({mr_out['out.trace_request.origin.y']});
    unsigned int ray_oz=__float_as_uint({mr_out['out.trace_request.origin.z']});
    unsigned int ray_dx=__float_as_uint({mr_out['out.trace_request.direction.x']});
    unsigned int ray_dy=__float_as_uint({mr_out['out.trace_request.direction.y']});
    unsigned int ray_dz=__float_as_uint({mr_out['out.trace_request.direction.z']});
    const float ray_tmin={mr_out['out.trace_request.tmin']};
    const float ray_tmax={mr_out['out.trace_request.tmax']};
    unsigned int best_t_bits=0x7f800000u, best_application_id=0xffffffffu;
    unsigned int best_primitive=0xffffffffu, best_hit_kind=0xffffffffu, best_found=0u;
    optixTrace(params.traversable,
        make_float3({mr_out['out.trace_request.origin.x']},{mr_out['out.trace_request.origin.y']},{mr_out['out.trace_request.origin.z']}),
        make_float3({mr_out['out.trace_request.direction.x']},{mr_out['out.trace_request.direction.y']},{mr_out['out.trace_request.direction.z']}),
        ray_tmin,ray_tmax,0.0f,OptixVisibilityMask(255),OPTIX_RAY_FLAG_NONE,
        0,1,0,{payload_args},best_t_bits,best_application_id,best_primitive,best_hit_kind,best_found);
    if (params.status[query].first_error_claimed != 0u) return;
    if (best_found == 1u) {{
        const float selected_hit_t=__uint_as_float(best_t_bits);
        const unsigned int selected_primitive_index=best_primitive;
        const unsigned int selected_hit_kind=best_hit_kind;
        if (!isfinite(selected_hit_t) || selected_hit_t<ray_tmin || selected_hit_t>ray_tmax ||
                selected_primitive_index>=params.primitive_count ||
                params.application_ids[selected_primitive_index]!=best_application_id) {{
            v4_sphere_first_error(query,0xffff3004u,0u,0u,query,0u,0u,0u); return;
        }}
        params.observed_primitive_index[query]=selected_primitive_index;
        params.observed_hit_kind[query]=selected_hit_kind;
        params.observed_t[query]=selected_hit_t;
{_indent(ch, 8)}
        if ({ch_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.CLOSEST_HIT], EffectKind.PAYLOAD)}u) {{
            v4_sphere_first_error(query,0xffff3005u,0u,0u,query,0u,{ch_out['out.effect_tag']},0u); return;
        }}
{assign_ch}
    }} else {{
{_indent(ms, 8)}
        if ({ms_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.MISS], EffectKind.PAYLOAD)}u) {{
            v4_sphere_first_error(query,0xffff3006u,0u,0u,query,0u,{ms_out['out.effect_tag']},0u); return;
        }}
{assign_ms}
    }}
{_indent(fin, 4)}
    if ({fin_out['out.effect_tag']} != {_effect_tag(roles[CallbackRole.FINALIZE], EffectKind.OUTPUT)}u) {{
        v4_sphere_first_error(query,0xffff3003u,0u,0u,query,0u,{fin_out['out.effect_tag']},0u); return;
    }}
{output_assignments}
}}
'''
    anyhit = r'''
extern "C" __global__ void __anyhit__rtdl_v4_sphere_canonical() {
    const unsigned int query=optixGetLaunchIndex().x;
    const unsigned int primitive=optixGetPrimitiveIndex();
    if (query>=params.query_count || primitive>=params.primitive_count) {
        v4_sphere_first_error(query,0xffff3004u,0u,0u,query,0u,0u,0u);
        optixTerminateRay(); return;
    }
    const float hit_t=optixGetRayTmax();
    const unsigned int application_id=params.application_ids[primitive];
    if (!isfinite(hit_t) || hit_t<optixGetRayTmin()) {
        v4_sphere_first_error(query,0xffff3007u,0u,0u,query,0u,0u,0u);
        optixTerminateRay(); return;
    }
    const float current_t=__uint_as_float(optixGetPayload_3());
    const unsigned int current_id=optixGetPayload_4();
    if (hit_t<current_t || (hit_t==current_t &&
            application_id<current_id)) {
        optixSetPayload_3(__float_as_uint(hit_t));
        optixSetPayload_4(application_id);
        optixSetPayload_5(primitive);
        optixSetPayload_6(optixGetHitKind());
        optixSetPayload_7(1u);
    }
    optixIgnoreIntersection();
}
extern "C" __global__ void __miss__rtdl_v4_sphere() {}
'''
    source = common + "\n" + prototypes + "\n" + raygen + anyhit
    if namespace == "curve":
        # Names are part of the physical executable identity.  Keep the
        # reviewed control flow byte-for-byte shared while making a curve
        # executable unable to bind the sphere native entry points.
        source = source.replace("V4Sphere", "V4Curve").replace(
            "v4_sphere", "v4_curve")
    return GeneratedOptixWrapper(
        schema=wrapper_schema,
        physical_template=template_id,
        callback_ir_sha256=fresh.callback.ir_sha256,
        callback_abi_sha256=canonical.abi_sha256,
        source=source,
        source_sha256=hashlib.sha256(source.encode("utf-8")).hexdigest(),
        role_symbols=tuple(
            (role.value, roles[role].symbol)
            for role in sorted(required_roles, key=lambda item: list(CallbackRole).index(item))),
    )


def generate_trusted_optix_sphere_wrapper_v1(
    authority: VerifiedSpherePhysicalAuthority,
    plan: SphereCanonicalPlan,
    abi: CompiledCallbackAbi,
) -> GeneratedOptixWrapper:
    return _generate_trusted_optix_first_contact_wrapper_v1(
        authority,
        plan,
        abi,
        fresh_validator=_fresh,
        abi_validator=verify_sphere_callback_abi,
        template_id=BUILTIN_SPHERE_TEMPLATE,
        namespace="sphere",
        wrapper_schema="rtdl.v4.generated_trusted_optix_sphere_wrapper.v1",
    )


__all__ = ["generate_trusted_optix_sphere_wrapper_v1"]

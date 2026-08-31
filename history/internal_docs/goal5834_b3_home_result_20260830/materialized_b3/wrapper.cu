
#include <optix_device.h>
struct V4CurveLaunchStatus {
    unsigned int first_error_claimed, error_code, stage, role;
    unsigned long long launch_index;
    unsigned int error_site, effect_tag, nonce_word, invocation_mask;
};
struct V4CurveParams {
    OptixTraversableHandle traversable;
    const float* query_sx; const float* query_sy; const float* query_sz;
    const float* query_ex; const float* query_ey; const float* query_ez;
    const unsigned int* application_ids;
    unsigned int primitive_count, query_count;
    unsigned int* output_0; unsigned int* output_1; unsigned int* output_2;
    unsigned int* observed_primitive_index; unsigned int* observed_hit_kind;
    float* observed_t;
    V4CurveLaunchStatus* status; unsigned long long* role_counters;
};
extern "C" { __constant__ V4CurveParams params; }
static __forceinline__ __device__ void v4_curve_first_error(
        unsigned int query, unsigned int code, unsigned int stage,
        unsigned int role, unsigned long long launch_index,
        unsigned int site, unsigned int effect, unsigned int nonce) {
    if (query >= params.query_count || code == 0u) return;
    V4CurveLaunchStatus* record = params.status + query;
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
    const unsigned int expected_effect_tag = (expected_role == 2u ? 2u : expected_role == 5u ? 8u : expected_role == 6u ? 8u : expected_role == 7u ? 9u : 0u);
    const bool valid = ok == 1u && error_code == 0u &&
        stage == expected_stage && role == expected_role &&
        launch_index == (unsigned long long)query && error_site == 0u &&
        nonce == expected_nonce && invocation_mask == expected_mask &&
        first_error_claimed == 0u && expected_effect_tag != 0u &&
        effect_tag == expected_effect_tag;
    if (!valid) {
        v4_curve_first_error(query, error_code ? error_code : 0xffff3001u,
                              stage, role, launch_index, error_site, effect_tag, nonce);
        return false;
    }
    atomicOr(&params.status[query].invocation_mask, invocation_mask);
    atomicAdd(params.role_counters + expected_role - 1u, 1ull);
    return true;
}

extern "C" __device__ unsigned long long rtdl_v4_make_ray_daf61a8371e76956(unsigned long long, unsigned int, const float*, const float*, const float*, const float*, const float*, const float*, unsigned long long, unsigned int*, unsigned int*, unsigned int*, unsigned int*, unsigned long long*, unsigned int*, unsigned int*, unsigned int*, unsigned int*, unsigned int*, unsigned int*, float*, float*, float*, float*, float*, float*, unsigned int*, float*, float*);
extern "C" __device__ unsigned long long rtdl_v4_closest_hit_daf61a8371e76956(unsigned long long, float, unsigned int, unsigned int, const unsigned int*, unsigned long long, unsigned int*, unsigned int*, unsigned int*, unsigned int*, unsigned long long*, unsigned int*, unsigned int*, unsigned int*, unsigned int*, unsigned int*, unsigned int*, unsigned int*);
extern "C" __device__ unsigned long long rtdl_v4_miss_daf61a8371e76956(unsigned long long, float, float, float, float, float, float, float, float, unsigned int, unsigned int*, unsigned int*, unsigned int*, unsigned int*, unsigned long long*, unsigned int*, unsigned int*, unsigned int*, unsigned int*, unsigned int*, unsigned int*, unsigned int*);
extern "C" __device__ unsigned long long rtdl_v4_finalize_daf61a8371e76956(unsigned long long, unsigned int, unsigned int*, unsigned int*, unsigned int*, unsigned int*, unsigned long long*, unsigned int*, unsigned int*, unsigned int*, unsigned int*, unsigned int*, unsigned int*, unsigned int*);

extern "C" __global__ void __raygen__rtdl_v4_curve() {
    const unsigned int query = optixGetLaunchIndex().x;
    if (query >= params.query_count) return;
    params.status[query] = {0u,0u,0u,0u,(unsigned long long)query,0u,0u,0u,0u};
    params.observed_primitive_index[query]=0xffffffffu;
    params.observed_hit_kind[query]=0xffffffffu;
    params.observed_t[query]=__int_as_float(0x7fffffffu);
    unsigned int mr_status_ok = 0;
    unsigned int mr_status_error_code = 0;
    unsigned int mr_status_stage = 0;
    unsigned int mr_status_role = 0;
    unsigned long long mr_status_launch_index = 0;
    unsigned int mr_status_error_site = 0;
    unsigned int mr_status_effect_tag = 0;
    unsigned int mr_status_nonce_word = 0;
    unsigned int mr_status_invocation_mask = 0;
    unsigned int mr_status_first_error_claimed = 0;
    unsigned int mr_out_effect_tag = 0;
    float mr_out_trace_request_direction_x = 0;
    float mr_out_trace_request_direction_y = 0;
    float mr_out_trace_request_direction_z = 0;
    float mr_out_trace_request_origin_x = 0;
    float mr_out_trace_request_origin_y = 0;
    float mr_out_trace_request_origin_z = 0;
    unsigned int mr_out_trace_request_payload_hit = 0;
    float mr_out_trace_request_tmax = 0;
    float mr_out_trace_request_tmin = 0;
    (void)rtdl_v4_make_ray_daf61a8371e76956(query, query, params.query_sx, params.query_sy, params.query_sz, params.query_ex, params.query_ey, params.query_ez, (unsigned long long)params.query_count, &mr_status_ok, &mr_status_error_code, &mr_status_stage, &mr_status_role, &mr_status_launch_index, &mr_status_error_site, &mr_status_effect_tag, &mr_status_nonce_word, &mr_status_invocation_mask, &mr_status_first_error_claimed, &mr_out_effect_tag, &mr_out_trace_request_direction_x, &mr_out_trace_request_direction_y, &mr_out_trace_request_direction_z, &mr_out_trace_request_origin_x, &mr_out_trace_request_origin_y, &mr_out_trace_request_origin_z, &mr_out_trace_request_payload_hit, &mr_out_trace_request_tmax, &mr_out_trace_request_tmin);
    if (!v4_commit_leaf_status(query, mr_status_ok, mr_status_error_code, mr_status_stage, mr_status_role, mr_status_launch_index, mr_status_error_site, mr_status_effect_tag, mr_status_nonce_word, mr_status_invocation_mask, mr_status_first_error_claimed, 2u, 2u, 40167612u)) { return; }
    if (mr_out_effect_tag != 2u) {
        v4_curve_first_error(query,0xffff3002u,0u,0u,query,0u,mr_out_effect_tag,0u); return;
    }
    unsigned int payload_0 = mr_out_trace_request_payload_hit;
    unsigned int payload_1 = 0u;
    unsigned int payload_2 = 0u;
    unsigned int ray_ox=__float_as_uint(mr_out_trace_request_origin_x);
    unsigned int ray_oy=__float_as_uint(mr_out_trace_request_origin_y);
    unsigned int ray_oz=__float_as_uint(mr_out_trace_request_origin_z);
    unsigned int ray_dx=__float_as_uint(mr_out_trace_request_direction_x);
    unsigned int ray_dy=__float_as_uint(mr_out_trace_request_direction_y);
    unsigned int ray_dz=__float_as_uint(mr_out_trace_request_direction_z);
    const float ray_tmin=mr_out_trace_request_tmin;
    const float ray_tmax=mr_out_trace_request_tmax;
    unsigned int best_t_bits=0x7f800000u, best_application_id=0xffffffffu;
    unsigned int best_primitive=0xffffffffu, best_hit_kind=0xffffffffu, best_found=0u;
    optixTrace(params.traversable,
        make_float3(mr_out_trace_request_origin_x,mr_out_trace_request_origin_y,mr_out_trace_request_origin_z),
        make_float3(mr_out_trace_request_direction_x,mr_out_trace_request_direction_y,mr_out_trace_request_direction_z),
        ray_tmin,ray_tmax,0.0f,OptixVisibilityMask(255),OPTIX_RAY_FLAG_NONE,
        0,1,0,payload_0, payload_1, payload_2,best_t_bits,best_application_id,best_primitive,best_hit_kind,best_found);
    if (params.status[query].first_error_claimed != 0u) return;
    if (best_found == 1u) {
        const float selected_hit_t=__uint_as_float(best_t_bits);
        const unsigned int selected_primitive_index=best_primitive;
        const unsigned int selected_hit_kind=best_hit_kind;
        if (!isfinite(selected_hit_t) || selected_hit_t<ray_tmin || selected_hit_t>ray_tmax ||
                selected_primitive_index>=params.primitive_count ||
                params.application_ids[selected_primitive_index]!=best_application_id) {
            v4_curve_first_error(query,0xffff3004u,0u,0u,query,0u,0u,0u); return;
        }
        params.observed_primitive_index[query]=selected_primitive_index;
        params.observed_hit_kind[query]=selected_hit_kind;
        params.observed_t[query]=selected_hit_t;
        unsigned int ch_status_ok = 0;
        unsigned int ch_status_error_code = 0;
        unsigned int ch_status_stage = 0;
        unsigned int ch_status_role = 0;
        unsigned long long ch_status_launch_index = 0;
        unsigned int ch_status_error_site = 0;
        unsigned int ch_status_effect_tag = 0;
        unsigned int ch_status_nonce_word = 0;
        unsigned int ch_status_invocation_mask = 0;
        unsigned int ch_status_first_error_claimed = 0;
        unsigned int ch_out_effect_tag = 0;
        unsigned int ch_out_payload_payload_hit = 0;
        (void)rtdl_v4_closest_hit_daf61a8371e76956(query, selected_hit_t, selected_hit_kind, payload_0, params.application_ids + selected_primitive_index, 1ull, &ch_status_ok, &ch_status_error_code, &ch_status_stage, &ch_status_role, &ch_status_launch_index, &ch_status_error_site, &ch_status_effect_tag, &ch_status_nonce_word, &ch_status_invocation_mask, &ch_status_first_error_claimed, &ch_out_effect_tag, &ch_out_payload_payload_hit);
        if (!v4_commit_leaf_status(query, ch_status_ok, ch_status_error_code, ch_status_stage, ch_status_role, ch_status_launch_index, ch_status_error_site, ch_status_effect_tag, ch_status_nonce_word, ch_status_invocation_mask, ch_status_first_error_claimed, 3u, 5u, 3829449019u)) { return; }
        if (ch_out_effect_tag != 8u) {
            v4_curve_first_error(query,0xffff3005u,0u,0u,query,0u,ch_out_effect_tag,0u); return;
        }
        payload_0 = ch_out_payload_payload_hit;
    } else {
        unsigned int ms_status_ok = 0;
        unsigned int ms_status_error_code = 0;
        unsigned int ms_status_stage = 0;
        unsigned int ms_status_role = 0;
        unsigned long long ms_status_launch_index = 0;
        unsigned int ms_status_error_site = 0;
        unsigned int ms_status_effect_tag = 0;
        unsigned int ms_status_nonce_word = 0;
        unsigned int ms_status_invocation_mask = 0;
        unsigned int ms_status_first_error_claimed = 0;
        unsigned int ms_out_effect_tag = 0;
        unsigned int ms_out_payload_payload_hit = 0;
        (void)rtdl_v4_miss_daf61a8371e76956(query, __uint_as_float(ray_ox), __uint_as_float(ray_oy), __uint_as_float(ray_oz), __uint_as_float(ray_dx), __uint_as_float(ray_dy), __uint_as_float(ray_dz), ray_tmin, ray_tmax, payload_0, &ms_status_ok, &ms_status_error_code, &ms_status_stage, &ms_status_role, &ms_status_launch_index, &ms_status_error_site, &ms_status_effect_tag, &ms_status_nonce_word, &ms_status_invocation_mask, &ms_status_first_error_claimed, &ms_out_effect_tag, &ms_out_payload_payload_hit);
        if (!v4_commit_leaf_status(query, ms_status_ok, ms_status_error_code, ms_status_stage, ms_status_role, ms_status_launch_index, ms_status_error_site, ms_status_effect_tag, ms_status_nonce_word, ms_status_invocation_mask, ms_status_first_error_claimed, 3u, 6u, 1281424282u)) { return; }
        if (ms_out_effect_tag != 8u) {
            v4_curve_first_error(query,0xffff3006u,0u,0u,query,0u,ms_out_effect_tag,0u); return;
        }
        payload_0 = ms_out_payload_payload_hit;
    }
    unsigned int fin_status_ok = 0;
    unsigned int fin_status_error_code = 0;
    unsigned int fin_status_stage = 0;
    unsigned int fin_status_role = 0;
    unsigned long long fin_status_launch_index = 0;
    unsigned int fin_status_error_site = 0;
    unsigned int fin_status_effect_tag = 0;
    unsigned int fin_status_nonce_word = 0;
    unsigned int fin_status_invocation_mask = 0;
    unsigned int fin_status_first_error_claimed = 0;
    unsigned int fin_out_effect_tag = 0;
    unsigned int fin_out_output_value_hit = 0;
    (void)rtdl_v4_finalize_daf61a8371e76956(query, payload_0, &fin_status_ok, &fin_status_error_code, &fin_status_stage, &fin_status_role, &fin_status_launch_index, &fin_status_error_site, &fin_status_effect_tag, &fin_status_nonce_word, &fin_status_invocation_mask, &fin_status_first_error_claimed, &fin_out_effect_tag, &fin_out_output_value_hit);
    if (!v4_commit_leaf_status(query, fin_status_ok, fin_status_error_code, fin_status_stage, fin_status_role, fin_status_launch_index, fin_status_error_site, fin_status_effect_tag, fin_status_nonce_word, fin_status_invocation_mask, fin_status_first_error_claimed, 2u, 7u, 4164633680u)) { return; }
    if (fin_out_effect_tag != 9u) {
        v4_curve_first_error(query,0xffff3003u,0u,0u,query,0u,fin_out_effect_tag,0u); return;
    }
    params.output_0[query]=fin_out_output_value_hit;
    params.output_1[query]=0u;
    params.output_2[query]=0u;
}

extern "C" __global__ void __anyhit__rtdl_v4_curve_canonical() {
    const unsigned int query=optixGetLaunchIndex().x;
    const unsigned int primitive=optixGetPrimitiveIndex();
    if (query>=params.query_count || primitive>=params.primitive_count) {
        v4_curve_first_error(query,0xffff3004u,0u,0u,query,0u,0u,0u);
        optixTerminateRay(); return;
    }
    const float hit_t=optixGetRayTmax();
    const unsigned int application_id=params.application_ids[primitive];
    if (!isfinite(hit_t) || hit_t<optixGetRayTmin()) {
        v4_curve_first_error(query,0xffff3007u,0u,0u,query,0u,0u,0u);
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
extern "C" __global__ void __miss__rtdl_v4_curve() {}

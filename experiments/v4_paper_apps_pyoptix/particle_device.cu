#include <optix_device.h>

struct RtdlParticleControl {
    unsigned int validated_row_count;
    unsigned int first_error;
    unsigned int error_code;
    unsigned int status;
};

struct RtdlParticleParams {
    OptixTraversableHandle traversable;
    const float* query_ox;
    const float* query_oy;
    const float* query_oz;
    const float* query_dx;
    const float* query_dy;
    const float* query_dz;
    const float* query_tmax;
    const unsigned int* front_values;
    const unsigned int* back_values;
    unsigned int primitive_count;
    unsigned int query_count;
    unsigned int* output_selected;
    unsigned int* output_neighbor;
    unsigned int* output_face;
    RtdlParticleControl* control;
};

extern "C" { __constant__ RtdlParticleParams params; }

enum RtdlParticleError : unsigned int {
    RTDL_PARTICLE_ERROR_MISS = 1u,
    RTDL_PARTICLE_ERROR_NON_STRICT_INTERIOR = 2u,
    RTDL_PARTICLE_ERROR_PRIMITIVE = 3u,
    RTDL_PARTICLE_ERROR_HIT_KIND = 4u,
    RTDL_PARTICLE_ERROR_OWNER = 5u
};

static __forceinline__ __device__ void rtdl_particle_first_error(
        unsigned int query, unsigned int code) {
    if (code == 0u) return;
    if (atomicCAS(&params.control->first_error, 0xffffffffu, query) ==
            0xffffffffu)
        params.control->error_code = code;
    atomicExch(&params.control->status, 1u);
}

extern "C" __global__ void __raygen__rtdl_particle_strict_interior() {
    const unsigned int query = optixGetLaunchIndex().x;
    if (query >= params.query_count) return;
    unsigned int primitive = 0xffffffffu;
    unsigned int front_face = 0xffffffffu;
    optixTrace(
        params.traversable,
        make_float3(params.query_ox[query], params.query_oy[query],
                    params.query_oz[query]),
        make_float3(params.query_dx[query], params.query_dy[query],
                    params.query_dz[query]),
        0.0f, params.query_tmax[query], 0.0f,
        OptixVisibilityMask(255), OPTIX_RAY_FLAG_DISABLE_ANYHIT,
        0u, 1u, 0u, primitive, front_face);
    if (primitive == 0xffffffffu) return;
    if (primitive >= params.primitive_count || front_face > 1u) {
        rtdl_particle_first_error(
            query, primitive >= params.primitive_count
                ? RTDL_PARTICLE_ERROR_PRIMITIVE
                : RTDL_PARTICLE_ERROR_HIT_KIND);
        return;
    }
    const unsigned int selected = front_face != 0u
        ? params.front_values[primitive] : params.back_values[primitive];
    const unsigned int neighbor = front_face != 0u
        ? params.back_values[primitive] : params.front_values[primitive];
    if (selected == 0xffffffffu) {
        rtdl_particle_first_error(query, RTDL_PARTICLE_ERROR_OWNER);
        return;
    }
    const unsigned int row = 3u * query;
    params.output_selected[row] = selected;
    params.output_neighbor[row] = neighbor;
    params.output_face[row] = primitive;
    atomicAdd(&params.control->validated_row_count, 1u);
}

extern "C" __global__ void __closesthit__rtdl_particle_strict_interior() {
    const unsigned int query = optixGetLaunchIndex().x;
    const unsigned int primitive = optixGetPrimitiveIndex();
    if (query >= params.query_count || primitive >= params.primitive_count) {
        rtdl_particle_first_error(query, RTDL_PARTICLE_ERROR_PRIMITIVE);
        return;
    }
    const float2 barycentrics = optixGetTriangleBarycentrics();
    const float barycentric_a = 1.0f - barycentrics.x - barycentrics.y;
    if (!isfinite(barycentrics.x) || !isfinite(barycentrics.y) ||
            !isfinite(barycentric_a) || barycentrics.x <= 0.0f ||
            barycentrics.y <= 0.0f || barycentric_a <= 0.0f) {
        rtdl_particle_first_error(
            query, RTDL_PARTICLE_ERROR_NON_STRICT_INTERIOR);
        return;
    }
    const unsigned int hit_kind = optixGetHitKind();
    if (hit_kind != OPTIX_HIT_KIND_TRIANGLE_FRONT_FACE &&
            hit_kind != OPTIX_HIT_KIND_TRIANGLE_BACK_FACE) {
        rtdl_particle_first_error(query, RTDL_PARTICLE_ERROR_HIT_KIND);
        return;
    }
    optixSetPayload_0(primitive);
    optixSetPayload_1(
        hit_kind == OPTIX_HIT_KIND_TRIANGLE_FRONT_FACE ? 1u : 0u);
}

extern "C" __global__ void __miss__rtdl_particle_strict_interior() {
    const unsigned int query = optixGetLaunchIndex().x;
    if (query < params.query_count)
        rtdl_particle_first_error(query, RTDL_PARTICLE_ERROR_MISS);
}

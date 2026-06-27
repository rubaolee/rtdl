#include <optix.h>
#include <optix_device.h>
#include <math.h>
#include <stdint.h>

struct Segment2D {
    float x0;
    float y0;
    float x1;
    float y1;
    uint32_t id;
};

struct IntersectionRecord {
    uint32_t left_id;
    uint32_t right_id;
    float intersection_point_x;
    float intersection_point_y;
};

struct LaunchParams {
    OptixTraversableHandle traversable;
    const Segment2D* right_segments;
    const Segment2D* left_segments;
    IntersectionRecord* output_records;
    uint32_t* output_count;
    uint32_t output_capacity;
    uint32_t probe_count;
};

extern "C" __constant__ LaunchParams params;

static __forceinline__ __device__ uint32_t rtdl_float_as_u32(float value) {
    return __float_as_uint(value);
}

static __forceinline__ __device__ float rtdl_u32_as_float(uint32_t value) {
    return __uint_as_float(value);
}

static __forceinline__ __device__ float rtdl_cross2(float2 a, float2 b) {
    return a.x * b.y - a.y * b.x;
}

static __forceinline__ __device__ bool rtdl_intersect_segments(
    const Segment2D& probe,
    const Segment2D& build,
    float* hit_t,
    float* ix,
    float* iy
) {
    const float2 p = make_float2(probe.x0, probe.y0);
    const float2 r = make_float2(probe.x1 - probe.x0, probe.y1 - probe.y0);
    const float2 q = make_float2(build.x0, build.y0);
    const float2 s = make_float2(build.x1 - build.x0, build.y1 - build.y0);
    const float2 qp = make_float2(q.x - p.x, q.y - p.y);
    const float denom = rtdl_cross2(r, s);

    if (fabsf(denom) < 1.0e-7f) {
        return false;
    }

    const float t = rtdl_cross2(qp, s) / denom;
    const float u = rtdl_cross2(qp, r) / denom;
    if (t < 0.0f || t > 1.0f || u < 0.0f || u > 1.0f) {
        return false;
    }

    *hit_t = t;
    *ix = p.x + t * r.x;
    *iy = p.y + t * r.y;
    return true;
}

static __forceinline__ __device__ void rtdl_pack_payload(uint32_t probe_index, uint32_t build_primitive_index, float hit_t, uint32_t hit_kind) {
    optixSetPayload_0(probe_index);
    optixSetPayload_1(build_primitive_index);
    optixSetPayload_2(rtdl_float_as_u32(hit_t));
    optixSetPayload_3(hit_kind);
}

static __forceinline__ __device__ void rtdl_store_record(uint32_t probe_id, uint32_t build_id, float ix, float iy) {
    const uint32_t slot = atomicAdd(params.output_count, 1U);
    if (slot >= params.output_capacity) {
        return;
    }
    IntersectionRecord record = {};
    record.left_id = probe_id;
    record.right_id = build_id;
    record.intersection_point_x = ix;
    record.intersection_point_y = iy;
    params.output_records[slot] = record;
}

extern "C" __global__ void __raygen__rtdl_probe() {
    const uint32_t probe_index = optixGetLaunchIndex().x;
    if (probe_index >= params.probe_count) {
        return;
    }

    const Segment2D probe = params.left_segments[probe_index];
    const float3 origin = make_float3(probe.x0, probe.y0, 0.0f);
    const float3 direction = make_float3(probe.x1 - probe.x0, probe.y1 - probe.y0, 0.0f);

    unsigned int p0 = probe_index;
    unsigned int p1 = 0u;
    unsigned int p2 = rtdl_float_as_u32(-1.0f);
    unsigned int p3 = 0u;

    optixTrace(
        params.traversable,
        origin,
        direction,
        0.0f,
        1.0f,
        0.0f,
        OptixVisibilityMask(255),
        OPTIX_RAY_FLAG_NONE,
        0,
        1,
        0,
        p0,
        p1,
        p2,
        p3
    );
}

extern "C" __global__ void __miss__rtdl_miss() {
    // Intentionally empty for the narrow segment-join path.
}

extern "C" __global__ void __closesthit__rtdl_refine() {
    const uint32_t probe_index = optixGetPayload_0();
    const uint32_t build_primitive_index = optixGetPayload_1();
    const float candidate_hit_t = rtdl_u32_as_float(optixGetPayload_2());
    const uint32_t hit_kind = optixGetPayload_3();
    (void)candidate_hit_t;
    (void)hit_kind;

    const Segment2D probe = params.left_segments[probe_index];
    const Segment2D build = params.right_segments[build_primitive_index];
    float refined_hit_t = 0.0f;
    float ix = 0.0f;
    float iy = 0.0f;

    if (!rtdl_intersect_segments(probe, build, &refined_hit_t, &ix, &iy)) {
        return;
    }

    rtdl_store_record(probe.id, build.id, ix, iy);
}

extern "C" __global__ void __intersection__rtdl_segments() {
    // p0 -> probe_index (u32)
    // p1 -> build_primitive_index (u32)
    // p2 -> hit_t_bits (f32_bits)
    // p3 -> hit_kind (u32)
    const uint32_t primitive_index = optixGetPrimitiveIndex();
    const Segment2D build = params.right_segments[primitive_index];
    const uint32_t probe_index = optixGetPayload_0();
    const Segment2D probe = params.left_segments[probe_index];
    float hit_t = 0.0f;
    float ix = 0.0f;
    float iy = 0.0f;

    if (!rtdl_intersect_segments(probe, build, &hit_t, &ix, &iy)) {
        return;
    }

    rtdl_pack_payload(probe_index, primitive_index, hit_t, 1u);
    optixReportIntersection(hit_t, 0u);
}

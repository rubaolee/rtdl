#include <optix.h>
#include <optix_device.h>
#include <math.h>
#include <stdint.h>

struct Triangle2D {
    float x0;
    float y0;
    float x1;
    float y1;
    float x2;
    float y2;
    uint32_t id;
};

struct Ray2D {
    float ox;
    float oy;
    float dx;
    float dy;
    float tmax;
    uint32_t id;
};

struct RayHitCountRecord {
    uint32_t ray_id;
    uint32_t hit_count;
};

struct LaunchParams {
    OptixTraversableHandle traversable;
    const Triangle2D* triangles;
    const Ray2D* rays;
    RayHitCountRecord* output_records;
    uint32_t* output_count;
    uint32_t output_capacity;
    uint32_t probe_count;
};

extern "C" __constant__ LaunchParams params;

static __forceinline__ __device__ float rtdl_cross2(float2 a, float2 b) {
    return a.x * b.y - a.y * b.x;
}

static __forceinline__ __device__ bool rtdl_segment_intersection(
    float2 p,
    float2 r,
    float2 q,
    float2 s
) {
    const float denom = rtdl_cross2(r, s);
    if (fabsf(denom) < 1.0e-7f) {
        return false;
    }
    const float2 qp = make_float2(q.x - p.x, q.y - p.y);
    const float t = rtdl_cross2(qp, s) / denom;
    const float u = rtdl_cross2(qp, r) / denom;
    return t >= 0.0f && t <= 1.0f && u >= 0.0f && u <= 1.0f;
}

static __forceinline__ __device__ bool rtdl_point_in_triangle(float2 p, const Triangle2D& tri) {
    const float2 a = make_float2(tri.x0, tri.y0);
    const float2 b = make_float2(tri.x1, tri.y1);
    const float2 c = make_float2(tri.x2, tri.y2);
    const float2 v0 = make_float2(c.x - a.x, c.y - a.y);
    const float2 v1 = make_float2(b.x - a.x, b.y - a.y);
    const float2 v2 = make_float2(p.x - a.x, p.y - a.y);

    const float dot00 = v0.x * v0.x + v0.y * v0.y;
    const float dot01 = v0.x * v1.x + v0.y * v1.y;
    const float dot02 = v0.x * v2.x + v0.y * v2.y;
    const float dot11 = v1.x * v1.x + v1.y * v1.y;
    const float dot12 = v1.x * v2.x + v1.y * v2.y;
    const float denom = dot00 * dot11 - dot01 * dot01;
    if (fabsf(denom) < 1.0e-7f) {
        return false;
    }
    const float inv = 1.0f / denom;
    const float u = (dot11 * dot02 - dot01 * dot12) * inv;
    const float v = (dot00 * dot12 - dot01 * dot02) * inv;
    return u >= 0.0f && v >= 0.0f && (u + v) <= 1.0f;
}

static __forceinline__ __device__ bool rtdl_ray_hits_triangle(
    const Ray2D& ray,
    const Triangle2D& tri
) {
    const float2 origin = make_float2(ray.ox, ray.oy);
    const float2 delta = make_float2(ray.dx * ray.tmax, ray.dy * ray.tmax);
    const float2 end = make_float2(origin.x + delta.x, origin.y + delta.y);

    if (rtdl_point_in_triangle(origin, tri) || rtdl_point_in_triangle(end, tri)) {
        return true;
    }

    const float2 a = make_float2(tri.x0, tri.y0);
    const float2 b = make_float2(tri.x1, tri.y1);
    const float2 c = make_float2(tri.x2, tri.y2);
    return rtdl_segment_intersection(origin, delta, a, make_float2(b.x - a.x, b.y - a.y))
        || rtdl_segment_intersection(origin, delta, b, make_float2(c.x - b.x, c.y - b.y))
        || rtdl_segment_intersection(origin, delta, c, make_float2(a.x - c.x, a.y - c.y));
}

static __forceinline__ __device__ void rtdl_store_record(uint32_t ray_id, uint32_t hit_count) {
    const uint32_t slot = atomicAdd(params.output_count, 1U);
    if (slot >= params.output_capacity) {
        return;
    }
    RayHitCountRecord record = {};
    record.ray_id = ray_id;
    record.hit_count = hit_count;
    params.output_records[slot] = record;
}

extern "C" __global__ void __raygen__rtdl_ray_hitcount() {
    const uint32_t ray_index = optixGetLaunchIndex().x;
    if (ray_index >= params.probe_count) {
        return;
    }

    const Ray2D probe = params.rays[ray_index];
    const float3 origin = make_float3(probe.ox, probe.oy, 0.0f);
    const float3 direction = make_float3(probe.dx, probe.dy, 0.0f);

    unsigned int p0 = ray_index;
    unsigned int p1 = 0u;
    unsigned int p2 = 0u;
    unsigned int p3 = 0u;

    optixTrace(
        params.traversable,
        origin,
        direction,
        0.0f,
        probe.tmax,
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

    rtdl_store_record(probe.id, p2);
}

extern "C" __global__ void __miss__rtdl_miss() {
    // Intentionally empty for the ray-triangle hit-count path.
}

extern "C" __global__ void __anyhit__rtdl_triangle_count() {
    const uint32_t hit_count = optixGetPayload_2() + 1u;
    optixSetPayload_2(hit_count);
    optixIgnoreIntersection();
}

extern "C" __global__ void __intersection__rtdl_triangles() {
    // p0 -> ray_index (u32)
    // p1 -> triangle_index (u32)
    // p2 -> hit_count (u32)
    // p3 -> hit_kind (u32)
    const uint32_t triangle_index = optixGetPrimitiveIndex();
    const Triangle2D tri = params.triangles[triangle_index];
    const uint32_t ray_index = optixGetPayload_0();
    const Ray2D ray = params.rays[ray_index];

    if (!rtdl_ray_hits_triangle(ray, tri)) {
        return;
    }

    optixSetPayload_1(triangle_index);
    optixSetPayload_3(1u);
    optixReportIntersection(0.0f, 0u);
}

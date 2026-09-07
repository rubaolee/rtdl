#include <optix.h>
#include <optix_device.h>

struct Ray {
    float ox, oy, oz;
    float dx, dy, dz;
    float tmax;
};

struct Params {
    OptixTraversableHandle traversable;
    const Ray* rays;
    const unsigned long long* weights;
    unsigned long long* weighted_sum;
    unsigned int* status;
    unsigned int query_count;
    float tmin;
    float tmax;
};

extern "C" { __constant__ Params params; }

static __forceinline__ __device__ unsigned long long payload_u64() {
    return static_cast<unsigned long long>(optixGetPayload_0()) |
        (static_cast<unsigned long long>(optixGetPayload_1()) << 32);
}

static __forceinline__ __device__ void set_payload_u64(
        unsigned long long value) {
    optixSetPayload_0(static_cast<unsigned int>(value));
    optixSetPayload_1(static_cast<unsigned int>(value >> 32));
}

extern "C" __global__ void __raygen__paper_triangle_count() {
    const unsigned int ray_index = optixGetLaunchIndex().x;
    if (ray_index >= params.query_count) {
        atomicExch(params.status, 1u);
        return;
    }
    const Ray ray = params.rays[ray_index];
    if (!(ray.tmax > params.tmin) || ray.tmax > params.tmax ||
            !isfinite(ray.tmax)) {
        atomicExch(params.status, 5u);
        return;
    }
    unsigned int lo = 0u;
    unsigned int hi = 0u;
    optixTrace(
        params.traversable,
        make_float3(ray.ox, ray.oy, ray.oz),
        make_float3(ray.dx, ray.dy, ray.dz),
        params.tmin, ray.tmax, 0.0f,
        OptixVisibilityMask(255), OPTIX_RAY_FLAG_NONE,
        0u, 1u, 0u, lo, hi);
    const unsigned long long count =
        static_cast<unsigned long long>(lo) |
        (static_cast<unsigned long long>(hi) << 32);
    const unsigned long long weight = params.weights[ray_index];
    if (weight != 0ull && count > (~0ull) / weight) {
        atomicExch(params.status, 2u);
        return;
    }
    const unsigned long long term = count * weight;
    const unsigned long long prior = atomicAdd(params.weighted_sum, term);
    if (prior > (~0ull) - term) atomicExch(params.status, 3u);
}

extern "C" __global__ void __anyhit__paper_triangle_count() {
    const unsigned long long before = payload_u64();
    if (before == ~0ull) {
        atomicExch(params.status, 4u);
        optixTerminateRay();
        return;
    }
    set_payload_u64(before + 1ull);
    optixIgnoreIntersection();
}

extern "C" __global__ void __miss__paper_triangle_count() {}

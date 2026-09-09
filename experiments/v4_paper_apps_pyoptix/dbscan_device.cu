// Application-specialized public-PyOptiX baseline for full RT-DBSCAN.
#include <optix.h>
#include <optix_device.h>

#if defined(__CUDACC_RTC__)
#define RTDL_OFFSETOF(T, member) ((unsigned long long)&(((T*)0)->member))
#else
#include <stddef.h>
#define RTDL_OFFSETOF(T, member) offsetof(T, member)
#endif

#define RTDL_INT_MAX 2147483647

struct Point {
    float x, y, z;
    unsigned int id;
};

struct Params {
    OptixTraversableHandle traversable;
    const Point* points;
    unsigned int* counts;
    unsigned char* core;
    int* parent;
    int* roots;
    int* border;
    unsigned int* status;
    unsigned int count, min_points, mode, reserved;
    float radius, trace_tmax;
};

static_assert(sizeof(Point) == 16, "point ABI");
static_assert(
    sizeof(Params) == 88 && RTDL_OFFSETOF(Params, count) == 64 &&
        RTDL_OFFSETOF(Params, radius) == 80,
    "params ABI");

extern "C" {
__constant__ Params params;
}

static __forceinline__ __device__ int root_of(int item) {
    const volatile int* parent = params.parent;
    for (unsigned int step = 0; step < params.count; ++step) {
        const int next = parent[item];
        if (next == item) {
            return item;
        }
        if (next < 0 || next >= item) {
            atomicCAS(params.status, 0u, 2u);
            return -1;
        }
        item = next;
    }
    atomicCAS(params.status, 0u, 2u);
    return -1;
}

static __forceinline__ __device__ void join_min_root(int a, int b) {
    for (;;) {
        a = root_of(a);
        b = root_of(b);
        if (a < 0 || b < 0 || a == b) {
            return;
        }
        const int high = a > b ? a : b;
        const int low = a > b ? b : a;
        // Failed CAS preserves the competing edge; recompute both roots.
        if (atomicCAS(params.parent + high, high, low) == high) {
            return;
        }
    }
}

extern "C" __global__ void __raygen__dbscan() {
    const unsigned int i = optixGetLaunchIndex().x;
    if (i >= params.count) {
        return;
    }
    // Mode 0: exact degree. Mode 1: core connectivity. Mode 2: border root.
    if ((params.mode == 1u && !params.core[i]) ||
        (params.mode == 2u && params.core[i])) {
        return;
    }
    const Point q = params.points[i];
    unsigned int p0 = i;
    unsigned int p1 = params.mode == 2u ? (unsigned int)RTDL_INT_MAX : 0u;
    optixTrace(
        params.traversable, make_float3(q.x, q.y, q.z), make_float3(1, 0, 0),
        0.0f, params.trace_tmax, 0.0f, OptixVisibilityMask(255),
        OPTIX_RAY_FLAG_NONE, 0, 1, 0, p0, p1);
    if (params.mode == 0u) {
        params.counts[i] = p1;
        params.core[i] = p1 >= params.min_points ? 1u : 0u;
    } else if (params.mode == 2u) {
        params.border[i] = (int)p1;
    }
}

extern "C" __global__ void __miss__dbscan() {}

extern "C" __global__ void __intersection__dbscan() {
    const unsigned int i = optixGetPayload_0();
    const unsigned int j = optixGetPrimitiveIndex();
    if (i >= params.count || j >= params.count) {
        atomicCAS(params.status, 0u, 1u);
        return;
    }
    if (params.mode == 1u && (j <= i || !params.core[j])) {
        return;
    }
    if (params.mode == 2u && !params.core[j]) {
        return;
    }
    const Point q = params.points[i];
    const Point target = params.points[j];
    const float dx = __fsub_rn(target.x, q.x);
    const float dy = __fsub_rn(target.y, q.y);
    const float dz = __fsub_rn(target.z, q.z);
    const float distance_sq = __fadd_rn(
        __fadd_rn(__fmul_rn(dx, dx), __fmul_rn(dy, dy)),
        __fmul_rn(dz, dz));
    if (distance_sq <= __fmul_rn(params.radius, params.radius)) {
        optixReportIntersection(params.radius, 0u);
    }
}

extern "C" __global__ void __anyhit__dbscan() {
    const unsigned int i = optixGetPayload_0();
    const unsigned int j = optixGetPrimitiveIndex();
    if (params.mode == 0u) {
        // Exact full degree, including self; no threshold cap.
        optixSetPayload_1(optixGetPayload_1() + 1u);
    } else if (params.mode == 1u) {
        join_min_root((int)i, (int)j);
    } else {
        // roots[] is immutable after the union and root-extraction stages.
        const int root = params.roots[j];
        if (root < 0 || (unsigned int)root >= params.count) {
            atomicCAS(params.status, 0u, 3u);
        } else if ((unsigned int)root < optixGetPayload_1()) {
            optixSetPayload_1((unsigned int)root);
        }
    }
    optixIgnoreIntersection();
}

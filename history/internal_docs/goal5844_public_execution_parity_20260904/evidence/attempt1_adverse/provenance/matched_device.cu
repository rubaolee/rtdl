#include <optix.h>
#include <optix_device.h>

struct Box {
    float lower_x, lower_y, lower_z;
    float upper_x, upper_y, upper_z;
    unsigned int item_id;
};

struct RelationRow {
    unsigned int source_id;
    unsigned int item_id;
};

struct Ray {
    float origin_x, origin_y, origin_z;
    float direction_x, direction_y, direction_z;
};

struct Params {
    OptixTraversableHandle traversable;
    const Box* boxes;
    const Box* queries;
    RelationRow* rows;
    unsigned int* row_count;
    unsigned int* overflow;
    unsigned int box_count;
    unsigned int query_count;
    unsigned int raw_row_capacity;
    unsigned int reverse_orientation;
    float minimum_overlap;
    float tmin;
    float tmax;
    unsigned int reserved0;
    const Ray* rays;
    const unsigned long long* weights;
    unsigned long long* per_ray;
    unsigned long long* weighted_sum;
    unsigned int* status;
};

extern "C" { __constant__ Params params; }

static __forceinline__ __device__ unsigned long long payload_u64() {
    return static_cast<unsigned long long>(optixGetPayload_0()) |
        (static_cast<unsigned long long>(optixGetPayload_1()) << 32);
}

static __forceinline__ __device__ void set_payload_u64(unsigned long long value) {
    optixSetPayload_0(static_cast<unsigned int>(value));
    optixSetPayload_1(static_cast<unsigned int>(value >> 32));
}

extern "C" __global__ void __raygen__goal5796_relation() {
    const unsigned int query_index = optixGetLaunchIndex().x;
    if (query_index >= params.query_count) return;
    const Box query = params.queries[query_index];
    float3 origin;
    float3 direction;
    if (params.reverse_orientation == 0u) {
        origin = make_float3(query.upper_x, query.lower_y, 0.0f);
        direction = make_float3(
            query.lower_x - query.upper_x,
            query.upper_y - query.lower_y,
            0.0f);
    } else {
        origin = make_float3(query.lower_x, query.lower_y, 0.0f);
        direction = make_float3(
            query.upper_x - query.lower_x,
            query.upper_y - query.lower_y,
            0.0f);
    }
    unsigned int p0 = 0u;
    unsigned int p1 = 0u;
    optixTrace(
        params.traversable, origin, direction, 0.0f, 1.0f, 0.0f,
        OptixVisibilityMask(255), OPTIX_RAY_FLAG_NONE,
        0u, 1u, 0u, p0, p1);
}

extern "C" __global__ void __intersection__goal5796_relation() {
    const unsigned int query_index = optixGetLaunchIndex().x;
    const unsigned int primitive_index = optixGetPrimitiveIndex();
    if (query_index >= params.query_count || primitive_index >= params.box_count) {
        atomicExch(params.status, 1u);
        return;
    }
    const Box query = params.queries[query_index];
    const Box item = params.boxes[primitive_index];
    const bool closed =
        item.lower_x <= query.upper_x && item.upper_x >= query.lower_x &&
        item.lower_y <= query.upper_y && item.upper_y >= query.lower_y;
    const float dx = fmaxf(0.0f,
        fminf(query.upper_x, item.upper_x) -
        fmaxf(query.lower_x, item.lower_x));
    const float dy = fmaxf(0.0f,
        fminf(query.upper_y, item.upper_y) -
        fmaxf(query.lower_y, item.lower_y));
    if (closed && dx * dy >= params.minimum_overlap) {
        optixReportIntersection(0.0f, 0u, item.item_id);
    }
}

extern "C" __global__ void __anyhit__goal5796_relation() {
    const unsigned int query_index = optixGetLaunchIndex().x;
    const unsigned int slot = atomicAdd(params.row_count, 1u);
    if (slot < params.raw_row_capacity) {
        RelationRow row;
        if (params.reverse_orientation == 0u) {
            row.source_id = params.queries[query_index].item_id;
            row.item_id = optixGetAttribute_0();
        } else {
            row.source_id = optixGetAttribute_0();
            row.item_id = params.queries[query_index].item_id;
        }
        params.rows[slot] = row;
    } else {
        atomicExch(params.overflow, 1u);
    }
    optixIgnoreIntersection();
}

extern "C" __global__ void __miss__goal5796_relation() {}

extern "C" __global__ void __raygen__goal5796_triangle() {
    const unsigned int ray_index = optixGetLaunchIndex().x;
    if (ray_index >= params.query_count) return;
    const Ray ray = params.rays[ray_index];
    unsigned int lo = 0u;
    unsigned int hi = 0u;
    optixTrace(
        params.traversable,
        make_float3(ray.origin_x, ray.origin_y, ray.origin_z),
        make_float3(ray.direction_x, ray.direction_y, ray.direction_z),
        params.tmin, params.tmax, 0.0f,
        OptixVisibilityMask(255), OPTIX_RAY_FLAG_NONE,
        0u, 1u, 0u, lo, hi);
    const unsigned long long count =
        static_cast<unsigned long long>(lo) |
        (static_cast<unsigned long long>(hi) << 32);
    params.per_ray[ray_index] = count;
    const unsigned long long weight = params.weights[ray_index];
    if (weight != 0ull && count > (~0ull) / weight) {
        atomicExch(params.status, 2u);
        return;
    }
    const unsigned long long term = count * weight;
    const unsigned long long prior = atomicAdd(params.weighted_sum, term);
    if (prior > (~0ull) - term) atomicExch(params.status, 3u);
}

extern "C" __global__ void __anyhit__goal5796_triangle() {
    const unsigned long long before = payload_u64();
    if (before == ~0ull) {
        atomicExch(params.status, 4u);
        optixTerminateRay();
        return;
    }
    set_payload_u64(before + 1ull);
    optixIgnoreIntersection();
}

extern "C" __global__ void __miss__goal5796_triangle() {}

#include <optix.h>
#include <optix_device.h>

struct Params {
    OptixTraversableHandle traversable;
    const float* indexed_min_x;
    const float* indexed_min_y;
    const float* indexed_max_x;
    const float* indexed_max_y;
    const float* query_min_x;
    const float* query_min_y;
    const float* query_max_x;
    const float* query_max_y;
    unsigned int* query_counts;
    unsigned int* status;
    unsigned int indexed_count;
    unsigned int query_count;
    unsigned int operation;
    unsigned int reserved;
};

extern "C" { __constant__ Params params; }

extern "C" __global__ void __raygen__paper_librts_count() {
    const unsigned int query_index = optixGetLaunchIndex().x;
    if (query_index >= params.query_count) {
        atomicExch(params.status, 1u);
        return;
    }
    const float x = 0.5f * (
        params.query_min_x[query_index] + params.query_max_x[query_index]);
    const float y = 0.5f * (
        params.query_min_y[query_index] + params.query_max_y[query_index]);
    unsigned int payload0 = query_index;
    unsigned int payload1 = 0u;
    optixTrace(
        params.traversable,
        make_float3(x, y, -1.0f),
        make_float3(0.0f, 0.0f, 1.0f),
        0.0f, 2.0f, 0.0f,
        OptixVisibilityMask(255), OPTIX_RAY_FLAG_NONE,
        0u, 1u, 0u, payload0, payload1);
}

extern "C" __global__ void __intersection__paper_librts_count() {
    const unsigned int primitive_index = optixGetPrimitiveIndex();
    const unsigned int query_index = optixGetPayload_0();
    if (primitive_index >= params.indexed_count || query_index >= params.query_count) {
        atomicExch(params.status, 2u);
        return;
    }
    const float imin_x = params.indexed_min_x[primitive_index];
    const float imin_y = params.indexed_min_y[primitive_index];
    const float imax_x = params.indexed_max_x[primitive_index];
    const float imax_y = params.indexed_max_y[primitive_index];
    bool accept = false;
    if (params.operation == 1u) {
        const float x = params.query_min_x[query_index];
        const float y = params.query_min_y[query_index];
        accept = imin_x <= x && x <= imax_x && imin_y <= y && y <= imax_y;
    } else if (params.operation == 2u) {
        accept =
            imin_x <= params.query_min_x[query_index] &&
            imin_y <= params.query_min_y[query_index] &&
            imax_x >= params.query_max_x[query_index] &&
            imax_y >= params.query_max_y[query_index];
    } else {
        atomicExch(params.status, 3u);
        return;
    }
    if (accept) atomicAdd(params.query_counts + query_index, 1u);
}

extern "C" __global__ void __miss__paper_librts_count() {}

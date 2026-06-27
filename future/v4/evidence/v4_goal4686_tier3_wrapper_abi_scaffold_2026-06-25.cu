#include <optix.h>
#include <optix_device.h>

extern "C" __device__ double rtdl_user_scalar_reduce(
    double hit_t,
    unsigned int primitive_id,
    double payload0,
    double state0);

extern "C" __device__ double __direct_callable__rtdl_tier3_scalar_reduce(
    double hit_t,
    unsigned int primitive_id,
    double payload0,
    double state0) {
    return rtdl_user_scalar_reduce(hit_t, primitive_id, payload0, state0);
}

struct RtdlTier3ProbeParams {
    double* output_state;
};

extern "C" {
__constant__ RtdlTier3ProbeParams params;
}

extern "C" __global__ void __raygen__rtdl_tier3_probe() {
    // Minimal semantic entry. Goal4687 decides whether this launches directly
    // or is replaced by a traversal shell that calls the direct callable.
    if (params.output_state != nullptr) {
        params.output_state[0] = __direct_callable__rtdl_tier3_scalar_reduce(1.0, 0u, 2.0, 3.0);
    }
}

extern "C" __global__ void __miss__rtdl_tier3_probe() {
}

extern "C" __global__ void __closesthit__rtdl_tier3_probe() {
}

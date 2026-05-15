#include <optix.h>
#include <optix_device.h>
#include <stdint.h>

struct Polygon2DRef {
    uint32_t vertex_offset;
    uint32_t vertex_count;
    uint32_t id;
};

struct OverlaySeedRecord {
    uint32_t left_polygon_id;
    uint32_t right_polygon_id;
    uint32_t requires_lsi;
    uint32_t requires_pip;
};

struct LaunchParams {
    OptixTraversableHandle traversable;
    const Polygon2DRef* right_polygons;
    const Polygon2DRef* left_polygons;
    OverlaySeedRecord* output_records;
    uint32_t* output_count;
    uint32_t output_capacity;
    uint32_t probe_count;
};

extern "C" __constant__ LaunchParams params;

static __forceinline__ __device__ void rtdl_store_record(uint32_t left_polygon_id, uint32_t right_polygon_id, uint32_t requires_lsi, uint32_t requires_pip) {
    const uint32_t slot = atomicAdd(params.output_count, 1U);
    if (slot >= params.output_capacity) {
        return;
    }
    OverlaySeedRecord record = {};
    record.left_polygon_id = left_polygon_id;
    record.right_polygon_id = right_polygon_id;
    record.requires_lsi = requires_lsi;
    record.requires_pip = requires_pip;
    params.output_records[slot] = record;
}

extern "C" __global__ void __raygen__rtdl_overlay_dispatch() {
    const uint32_t polygon_index = optixGetLaunchIndex().x;
    if (polygon_index >= params.probe_count) {
        return;
    }

    // Overlay composition is represented as a plan-level workload for now.
    // The runtime implementation will dispatch LSI and PIP subqueries from this seed stage.
}

extern "C" __global__ void __miss__rtdl_miss() {
    // Intentionally empty for the overlay path.
}

extern "C" __global__ void __closesthit__rtdl_overlay_compose() {
    // Overlay seed emission is deferred to a later runtime milestone.
    // This skeleton keeps the workload contract explicit in generated backend code.
}

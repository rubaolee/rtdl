#include <float.h>
#include <optix.h>
#include <optix_device.h>
#include <stdint.h>

struct Polygon2DRef {
    uint32_t vertex_offset;
    uint32_t vertex_count;
    uint32_t id;
};

struct Point2D {
    float x;
    float y;
    uint32_t id;
};

struct PointInPolygonRecord {
    uint32_t point_id;
    uint32_t polygon_id;
    uint32_t contains;
};

struct LaunchParams {
    OptixTraversableHandle traversable;
    const Polygon2DRef* polygons;
    const Point2D* points;
    PointInPolygonRecord* output_records;
    uint32_t* output_count;
    uint32_t output_capacity;
    uint32_t probe_count;
};

extern "C" __constant__ LaunchParams params;

static __forceinline__ __device__ void rtdl_store_record(uint32_t point_id, uint32_t polygon_id, uint32_t contains) {
    const uint32_t slot = atomicAdd(params.output_count, 1U);
    if (slot >= params.output_capacity) {
        return;
    }
    PointInPolygonRecord record = {};
    record.point_id = point_id;
    record.polygon_id = polygon_id;
    record.contains = contains;
    params.output_records[slot] = record;
}

extern "C" __global__ void __raygen__rtdl_pip_probe() {
    const uint32_t point_index = optixGetLaunchIndex().x;
    if (point_index >= params.probe_count) {
        return;
    }

    const Point2D probe = params.points[point_index];
    const float3 origin = make_float3(probe.x, probe.y, 0.0f);
    const float3 direction = make_float3(0.0f, 1.0f, 0.0f);

    unsigned int p0 = point_index;
    unsigned int p1 = 0u;
    unsigned int p2 = 0u;
    unsigned int p3 = 0u;

    optixTrace(
        params.traversable,
        origin,
        direction,
        0.0f,
        FLT_MAX,
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
    // Intentionally empty for the PIP path.
}

extern "C" __global__ void __closesthit__rtdl_pip_refine() {
    const uint32_t point_index = optixGetPayload_0();
    const uint32_t polygon_face_index = optixGetPayload_1();
    const uint32_t winding_hits = optixGetPayload_2();
    const Point2D point = params.points[point_index];
    const Polygon2DRef polygon = params.polygons[polygon_face_index];
    const uint32_t contains = winding_hits & 1u;

    // Current backend contract only materializes a workload-specific skeleton here.
    rtdl_store_record(point.id, polygon.id, contains);
}

extern "C" __global__ void __intersection__rtdl_polygon_refs() {
    // p0 -> point_index (u32)
    // p1 -> polygon_face_index (u32)
    // p2 -> winding_hits (u32)
    // p3 -> hit_kind (u32)
    // Polygon edge traversal and parity counting are deferred to a later runtime milestone.
    // This skeleton fixes the payload and launch contract for the PIP workload now.
}

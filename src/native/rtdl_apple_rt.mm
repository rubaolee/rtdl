#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <MetalPerformanceShaders/MetalPerformanceShaders.h>

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <new>
#include <string>
#include <vector>

#define RTDL_APPLE_RT_EXPORT __attribute__((visibility("default")))

namespace {

struct __attribute__((packed)) RtdlRay3D {
    uint32_t id;
    double ox;
    double oy;
    double oz;
    double dx;
    double dy;
    double dz;
    double tmax;
};

struct __attribute__((packed)) RtdlTriangle3D {
    uint32_t id;
    double x0;
    double y0;
    double z0;
    double x1;
    double y1;
    double z1;
    double x2;
    double y2;
    double z2;
};

struct RtdlSegment {
    uint32_t id;
    double x0;
    double y0;
    double x1;
    double y1;
};

struct RtdlLsiRow {
    uint32_t left_id;
    uint32_t right_id;
    double intersection_point_x;
    double intersection_point_y;
};

struct RtdlRayClosestHitRow {
    uint32_t ray_id;
    uint32_t triangle_id;
    double t;
};

struct RtdlRayHitCountRow {
    uint32_t ray_id;
    uint32_t hit_count;
};

struct AppleRtClosestHitPrepared {
    id<MTLDevice> device = nil;
    id<MTLCommandQueue> command_queue = nil;
    id<MTLBuffer> vertex_buffer = nil;
    MPSTriangleAccelerationStructure* accel = nil;
    MPSRayIntersector* intersector = nil;
    std::vector<uint32_t> triangle_ids;

    ~AppleRtClosestHitPrepared() {
        [intersector release];
        [accel release];
        [vertex_buffer release];
        [command_queue release];
        [device release];
    }
};

void set_message(char* error_out, size_t error_size, const std::string& message) {
    if (error_out == nullptr || error_size == 0) {
        return;
    }
    const size_t n = std::min(error_size - 1, message.size());
    std::memcpy(error_out, message.data(), n);
    error_out[n] = '\0';
}

float finite_tmax(double value) {
    if (!std::isfinite(value) || value < 0.0) {
        return std::numeric_limits<float>::infinity();
    }
    return static_cast<float>(value);
}

bool valid_ray(const RtdlRay3D& ray) {
    return std::isfinite(ray.ox) && std::isfinite(ray.oy) && std::isfinite(ray.oz) &&
           std::isfinite(ray.dx) && std::isfinite(ray.dy) && std::isfinite(ray.dz) &&
           (ray.dx != 0.0 || ray.dy != 0.0 || ray.dz != 0.0);
}

bool valid_segment_ray(const RtdlSegment& segment) {
    return std::isfinite(segment.x0) && std::isfinite(segment.y0) &&
           std::isfinite(segment.x1) && std::isfinite(segment.y1) &&
           (segment.x0 != segment.x1 || segment.y0 != segment.y1);
}

bool segment_intersection_point(const RtdlSegment& left, const RtdlSegment& right, double* ix, double* iy) {
    const double px = left.x0;
    const double py = left.y0;
    const double rx = left.x1 - left.x0;
    const double ry = left.y1 - left.y0;
    const double qx = right.x0;
    const double qy = right.y0;
    const double sx = right.x1 - right.x0;
    const double sy = right.y1 - right.y0;
    const double denom = rx * sy - ry * sx;
    if (std::abs(denom) < 1.0e-7) {
        return false;
    }
    const double qpx = qx - px;
    const double qpy = qy - py;
    const double t = (qpx * sy - qpy * sx) / denom;
    const double u = (qpx * ry - qpy * rx) / denom;
    if (t < 0.0 || t > 1.0 || u < 0.0 || u > 1.0) {
        return false;
    }
    *ix = px + t * rx;
    *iy = py + t * ry;
    return true;
}

int run_closest_hit_prepared(
    AppleRtClosestHitPrepared* prepared,
    const RtdlRay3D* rays,
    size_t ray_count,
    RtdlRayClosestHitRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    if (prepared == nullptr || rows_out == nullptr || row_count_out == nullptr) {
        set_message(error_out, error_size, "null handle or output passed to Apple RT prepared closest-hit run");
        return 1;
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if (ray_count > 0 && rays == nullptr) {
        set_message(error_out, error_size, "null rays passed to Apple RT prepared closest-hit run");
        return 1;
    }
    if (ray_count == 0 || prepared->triangle_ids.empty()) {
        return 0;
    }

    std::vector<MPSRayOriginMinDistanceDirectionMaxDistance> mps_rays(ray_count);
    for (size_t i = 0; i < ray_count; ++i) {
        if (!valid_ray(rays[i])) {
            mps_rays[i].origin = MPSPackedFloat3(INFINITY, INFINITY, INFINITY);
            mps_rays[i].minDistance = 0.0f;
            mps_rays[i].direction = MPSPackedFloat3(0.0f, 0.0f, 0.0f);
            mps_rays[i].maxDistance = -1.0f;
            continue;
        }
        mps_rays[i].origin = MPSPackedFloat3(static_cast<float>(rays[i].ox), static_cast<float>(rays[i].oy), static_cast<float>(rays[i].oz));
        mps_rays[i].minDistance = 0.0f;
        mps_rays[i].direction = MPSPackedFloat3(static_cast<float>(rays[i].dx), static_cast<float>(rays[i].dy), static_cast<float>(rays[i].dz));
        mps_rays[i].maxDistance = finite_tmax(rays[i].tmax);
    }

    id<MTLBuffer> ray_buffer = [prepared->device newBufferWithBytes:mps_rays.data()
                                                             length:mps_rays.size() * sizeof(MPSRayOriginMinDistanceDirectionMaxDistance)
                                                            options:MTLResourceStorageModeShared];
    if (ray_buffer == nil) {
        set_message(error_out, error_size, "Metal ray buffer creation failed");
        return 2;
    }

    id<MTLBuffer> intersection_buffer = [prepared->device newBufferWithLength:ray_count * sizeof(MPSIntersectionDistancePrimitiveIndex)
                                                                      options:MTLResourceStorageModeShared];
    if (intersection_buffer == nil) {
        [ray_buffer release];
        set_message(error_out, error_size, "Metal intersection buffer creation failed");
        return 3;
    }

    id<MTLCommandBuffer> command_buffer = [prepared->command_queue commandBuffer];
    if (command_buffer == nil) {
        [intersection_buffer release];
        [ray_buffer release];
        set_message(error_out, error_size, "Metal command buffer creation failed");
        return 4;
    }
    [prepared->intersector encodeIntersectionToCommandBuffer:command_buffer
                                            intersectionType:MPSIntersectionTypeNearest
                                                   rayBuffer:ray_buffer
                                             rayBufferOffset:0
                                          intersectionBuffer:intersection_buffer
                                    intersectionBufferOffset:0
                                                    rayCount:ray_count
                                       accelerationStructure:prepared->accel];
    [command_buffer commit];
    [command_buffer waitUntilCompleted];
    NSError* error = [command_buffer error];
    if (error != nil) {
        [intersection_buffer release];
        [ray_buffer release];
        set_message(error_out, error_size, [[error localizedDescription] UTF8String]);
        return 5;
    }

    const auto* gpu_intersections = static_cast<const MPSIntersectionDistancePrimitiveIndex*>([intersection_buffer contents]);
    std::vector<RtdlRayClosestHitRow> rows;
    rows.reserve(ray_count);
    for (size_t i = 0; i < ray_count; ++i) {
        const float distance = gpu_intersections[i].distance;
        const uint32_t primitive_index = gpu_intersections[i].primitiveIndex;
        if (distance < 0.0f || primitive_index >= prepared->triangle_ids.size()) {
            continue;
        }
        rows.push_back(RtdlRayClosestHitRow{
            rays[i].id,
            prepared->triangle_ids[primitive_index],
            static_cast<double>(distance),
        });
    }
    [intersection_buffer release];
    [ray_buffer release];
    if (rows.empty()) {
        return 0;
    }
    auto* out = static_cast<RtdlRayClosestHitRow*>(std::malloc(rows.size() * sizeof(RtdlRayClosestHitRow)));
    if (out == nullptr) {
        set_message(error_out, error_size, "out of memory allocating Apple RT prepared closest-hit rows");
        return 6;
    }
    std::memcpy(out, rows.data(), rows.size() * sizeof(RtdlRayClosestHitRow));
    *rows_out = out;
    *row_count_out = rows.size();
    return 0;
}

}  // namespace

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_get_version(int* major, int* minor, int* patch) {
    if (major == nullptr || minor == nullptr || patch == nullptr) {
        return 1;
    }
    *major = 0;
    *minor = 9;
    *patch = 2;
    return 0;
}

extern "C" RTDL_APPLE_RT_EXPORT void rtdl_apple_rt_free_rows(void* ptr) {
    std::free(ptr);
}

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_context_probe(char* error_out, size_t error_size) {
    @autoreleasepool {
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (device == nil) {
            set_message(error_out, error_size, "Metal default device is unavailable");
            return 2;
        }
        MPSRayIntersector* intersector = [[MPSRayIntersector alloc] initWithDevice:device];
        if (intersector == nil) {
            set_message(error_out, error_size, "MPSRayIntersector initialization failed");
            return 3;
        }
        set_message(error_out, error_size, [[device name] UTF8String]);
        return 0;
    }
}

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_run_ray_closest_hit_3d(
    const RtdlRay3D* rays,
    size_t ray_count,
    const RtdlTriangle3D* triangles,
    size_t triangle_count,
    RtdlRayClosestHitRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    if (rows_out == nullptr || row_count_out == nullptr) {
        set_message(error_out, error_size, "null output passed to rtdl_apple_rt_run_ray_closest_hit_3d");
        return 1;
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if ((ray_count > 0 && rays == nullptr) || (triangle_count > 0 && triangles == nullptr)) {
        set_message(error_out, error_size, "null input passed to rtdl_apple_rt_run_ray_closest_hit_3d");
        return 1;
    }
    if (ray_count == 0 || triangle_count == 0) {
        return 0;
    }

    @autoreleasepool {
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (device == nil) {
            set_message(error_out, error_size, "Metal default device is unavailable");
            return 2;
        }
        id<MTLCommandQueue> command_queue = [device newCommandQueue];
        if (command_queue == nil) {
            set_message(error_out, error_size, "Metal command queue creation failed");
            return 3;
        }

        std::vector<MPSPackedFloat3> vertices;
        vertices.reserve(triangle_count * 3);
        for (size_t i = 0; i < triangle_count; ++i) {
            const RtdlTriangle3D& tri = triangles[i];
            vertices.emplace_back(static_cast<float>(tri.x0), static_cast<float>(tri.y0), static_cast<float>(tri.z0));
            vertices.emplace_back(static_cast<float>(tri.x1), static_cast<float>(tri.y1), static_cast<float>(tri.z1));
            vertices.emplace_back(static_cast<float>(tri.x2), static_cast<float>(tri.y2), static_cast<float>(tri.z2));
        }

        id<MTLBuffer> vertex_buffer = [device newBufferWithBytes:vertices.data()
                                                          length:vertices.size() * sizeof(MPSPackedFloat3)
                                                         options:MTLResourceStorageModeShared];
        if (vertex_buffer == nil) {
            set_message(error_out, error_size, "Metal vertex buffer creation failed");
            return 4;
        }

        MPSTriangleAccelerationStructure* accel = [[MPSTriangleAccelerationStructure alloc] initWithDevice:device];
        if (accel == nil) {
            set_message(error_out, error_size, "MPSTriangleAccelerationStructure initialization failed");
            return 5;
        }
        accel.vertexBuffer = vertex_buffer;
        accel.vertexStride = sizeof(MPSPackedFloat3);
        accel.triangleCount = triangle_count;
        [accel rebuild];

        std::vector<MPSRayOriginMinDistanceDirectionMaxDistance> mps_rays(ray_count);
        for (size_t i = 0; i < ray_count; ++i) {
            if (!valid_ray(rays[i])) {
                mps_rays[i].origin = MPSPackedFloat3(INFINITY, INFINITY, INFINITY);
                mps_rays[i].minDistance = 0.0f;
                mps_rays[i].direction = MPSPackedFloat3(0.0f, 0.0f, 0.0f);
                mps_rays[i].maxDistance = -1.0f;
                continue;
            }
            mps_rays[i].origin = MPSPackedFloat3(static_cast<float>(rays[i].ox), static_cast<float>(rays[i].oy), static_cast<float>(rays[i].oz));
            mps_rays[i].minDistance = 0.0f;
            mps_rays[i].direction = MPSPackedFloat3(static_cast<float>(rays[i].dx), static_cast<float>(rays[i].dy), static_cast<float>(rays[i].dz));
            mps_rays[i].maxDistance = finite_tmax(rays[i].tmax);
        }

        id<MTLBuffer> ray_buffer = [device newBufferWithBytes:mps_rays.data()
                                                       length:mps_rays.size() * sizeof(MPSRayOriginMinDistanceDirectionMaxDistance)
                                                      options:MTLResourceStorageModeShared];
        if (ray_buffer == nil) {
            set_message(error_out, error_size, "Metal ray buffer creation failed");
            return 6;
        }

        std::vector<MPSIntersectionDistancePrimitiveIndex> intersections(ray_count);
        id<MTLBuffer> intersection_buffer = [device newBufferWithBytes:intersections.data()
                                                                length:intersections.size() * sizeof(MPSIntersectionDistancePrimitiveIndex)
                                                               options:MTLResourceStorageModeShared];
        if (intersection_buffer == nil) {
            set_message(error_out, error_size, "Metal intersection buffer creation failed");
            return 7;
        }

        MPSRayIntersector* intersector = [[MPSRayIntersector alloc] initWithDevice:device];
        if (intersector == nil) {
            set_message(error_out, error_size, "MPSRayIntersector initialization failed");
            return 8;
        }
        intersector.cullMode = MTLCullModeNone;
        intersector.rayDataType = MPSRayDataTypeOriginMinDistanceDirectionMaxDistance;
        intersector.intersectionDataType = MPSIntersectionDataTypeDistancePrimitiveIndex;
        intersector.rayStride = sizeof(MPSRayOriginMinDistanceDirectionMaxDistance);
        intersector.intersectionStride = sizeof(MPSIntersectionDistancePrimitiveIndex);

        id<MTLCommandBuffer> command_buffer = [command_queue commandBuffer];
        if (command_buffer == nil) {
            set_message(error_out, error_size, "Metal command buffer creation failed");
            return 9;
        }
        [intersector encodeIntersectionToCommandBuffer:command_buffer
                                      intersectionType:MPSIntersectionTypeNearest
                                             rayBuffer:ray_buffer
                                       rayBufferOffset:0
                                    intersectionBuffer:intersection_buffer
                              intersectionBufferOffset:0
                                              rayCount:ray_count
                                 accelerationStructure:accel];
        [command_buffer commit];
        [command_buffer waitUntilCompleted];
        NSError* error = [command_buffer error];
        if (error != nil) {
            set_message(error_out, error_size, [[error localizedDescription] UTF8String]);
            return 10;
        }

        const auto* gpu_intersections = static_cast<const MPSIntersectionDistancePrimitiveIndex*>([intersection_buffer contents]);
        std::vector<RtdlRayClosestHitRow> rows;
        rows.reserve(ray_count);
        for (size_t i = 0; i < ray_count; ++i) {
            const float distance = gpu_intersections[i].distance;
            const uint32_t primitive_index = gpu_intersections[i].primitiveIndex;
            if (distance < 0.0f || primitive_index >= triangle_count) {
                continue;
            }
            rows.push_back(RtdlRayClosestHitRow{
                rays[i].id,
                triangles[primitive_index].id,
                static_cast<double>(distance),
            });
        }
        if (rows.empty()) {
            return 0;
        }
        auto* out = static_cast<RtdlRayClosestHitRow*>(std::malloc(rows.size() * sizeof(RtdlRayClosestHitRow)));
        if (out == nullptr) {
            set_message(error_out, error_size, "out of memory allocating Apple RT closest-hit rows");
            return 11;
        }
        std::memcpy(out, rows.data(), rows.size() * sizeof(RtdlRayClosestHitRow));
        *rows_out = out;
        *row_count_out = rows.size();
        return 0;
    }
}

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_prepare_ray_closest_hit_3d(
    const RtdlTriangle3D* triangles,
    size_t triangle_count,
    void** handle_out,
    char* error_out,
    size_t error_size) {
    if (handle_out == nullptr) {
        set_message(error_out, error_size, "null handle output passed to rtdl_apple_rt_prepare_ray_closest_hit_3d");
        return 1;
    }
    *handle_out = nullptr;
    if (triangle_count > 0 && triangles == nullptr) {
        set_message(error_out, error_size, "null triangles passed to rtdl_apple_rt_prepare_ray_closest_hit_3d");
        return 1;
    }

    @autoreleasepool {
        auto* prepared = new (std::nothrow) AppleRtClosestHitPrepared();
        if (prepared == nullptr) {
            set_message(error_out, error_size, "out of memory allocating Apple RT prepared closest-hit handle");
            return 2;
        }
        prepared->device = MTLCreateSystemDefaultDevice();
        if (prepared->device == nil) {
            delete prepared;
            set_message(error_out, error_size, "Metal default device is unavailable");
            return 3;
        }
        prepared->command_queue = [prepared->device newCommandQueue];
        if (prepared->command_queue == nil) {
            delete prepared;
            set_message(error_out, error_size, "Metal command queue creation failed");
            return 4;
        }
        prepared->intersector = [[MPSRayIntersector alloc] initWithDevice:prepared->device];
        if (prepared->intersector == nil) {
            delete prepared;
            set_message(error_out, error_size, "MPSRayIntersector initialization failed");
            return 5;
        }
        prepared->intersector.cullMode = MTLCullModeNone;
        prepared->intersector.rayDataType = MPSRayDataTypeOriginMinDistanceDirectionMaxDistance;
        prepared->intersector.intersectionDataType = MPSIntersectionDataTypeDistancePrimitiveIndex;
        prepared->intersector.rayStride = sizeof(MPSRayOriginMinDistanceDirectionMaxDistance);
        prepared->intersector.intersectionStride = sizeof(MPSIntersectionDistancePrimitiveIndex);

        if (triangle_count > 0) {
            std::vector<MPSPackedFloat3> vertices;
            vertices.reserve(triangle_count * 3);
            prepared->triangle_ids.reserve(triangle_count);
            for (size_t i = 0; i < triangle_count; ++i) {
                const RtdlTriangle3D& tri = triangles[i];
                vertices.emplace_back(static_cast<float>(tri.x0), static_cast<float>(tri.y0), static_cast<float>(tri.z0));
                vertices.emplace_back(static_cast<float>(tri.x1), static_cast<float>(tri.y1), static_cast<float>(tri.z1));
                vertices.emplace_back(static_cast<float>(tri.x2), static_cast<float>(tri.y2), static_cast<float>(tri.z2));
                prepared->triangle_ids.push_back(tri.id);
            }
            prepared->vertex_buffer = [prepared->device newBufferWithBytes:vertices.data()
                                                                    length:vertices.size() * sizeof(MPSPackedFloat3)
                                                                   options:MTLResourceStorageModeShared];
            if (prepared->vertex_buffer == nil) {
                delete prepared;
                set_message(error_out, error_size, "Metal vertex buffer creation failed");
                return 6;
            }
            prepared->accel = [[MPSTriangleAccelerationStructure alloc] initWithDevice:prepared->device];
            if (prepared->accel == nil) {
                delete prepared;
                set_message(error_out, error_size, "MPSTriangleAccelerationStructure initialization failed");
                return 7;
            }
            prepared->accel.vertexBuffer = prepared->vertex_buffer;
            prepared->accel.vertexStride = sizeof(MPSPackedFloat3);
            prepared->accel.triangleCount = triangle_count;
            [prepared->accel rebuild];
        }
        *handle_out = prepared;
        return 0;
    }
}

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_run_prepared_ray_closest_hit_3d(
    void* handle,
    const RtdlRay3D* rays,
    size_t ray_count,
    RtdlRayClosestHitRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    @autoreleasepool {
        return run_closest_hit_prepared(
            static_cast<AppleRtClosestHitPrepared*>(handle),
            rays,
            ray_count,
            rows_out,
            row_count_out,
            error_out,
            error_size);
    }
}

extern "C" RTDL_APPLE_RT_EXPORT void rtdl_apple_rt_destroy_prepared_ray_closest_hit_3d(void* handle) {
    delete static_cast<AppleRtClosestHitPrepared*>(handle);
}

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_run_ray_hitcount_3d(
    const RtdlRay3D* rays,
    size_t ray_count,
    const RtdlTriangle3D* triangles,
    size_t triangle_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    if (rows_out == nullptr || row_count_out == nullptr) {
        set_message(error_out, error_size, "null output passed to rtdl_apple_rt_run_ray_hitcount_3d");
        return 1;
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if ((ray_count > 0 && rays == nullptr) || (triangle_count > 0 && triangles == nullptr)) {
        set_message(error_out, error_size, "null input passed to rtdl_apple_rt_run_ray_hitcount_3d");
        return 1;
    }
    if (ray_count == 0) {
        return 0;
    }

    @autoreleasepool {
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (device == nil) {
            set_message(error_out, error_size, "Metal default device is unavailable");
            return 2;
        }
        id<MTLCommandQueue> command_queue = [device newCommandQueue];
        if (command_queue == nil) {
            set_message(error_out, error_size, "Metal command queue creation failed");
            return 3;
        }

        std::vector<MPSRayOriginMinDistanceDirectionMaxDistance> mps_rays(ray_count);
        for (size_t i = 0; i < ray_count; ++i) {
            if (!valid_ray(rays[i])) {
                mps_rays[i].origin = MPSPackedFloat3(INFINITY, INFINITY, INFINITY);
                mps_rays[i].minDistance = 0.0f;
                mps_rays[i].direction = MPSPackedFloat3(0.0f, 0.0f, 0.0f);
                mps_rays[i].maxDistance = -1.0f;
                continue;
            }
            mps_rays[i].origin = MPSPackedFloat3(static_cast<float>(rays[i].ox), static_cast<float>(rays[i].oy), static_cast<float>(rays[i].oz));
            mps_rays[i].minDistance = 0.0f;
            mps_rays[i].direction = MPSPackedFloat3(static_cast<float>(rays[i].dx), static_cast<float>(rays[i].dy), static_cast<float>(rays[i].dz));
            mps_rays[i].maxDistance = finite_tmax(rays[i].tmax);
        }

        id<MTLBuffer> ray_buffer = [device newBufferWithBytes:mps_rays.data()
                                                       length:mps_rays.size() * sizeof(MPSRayOriginMinDistanceDirectionMaxDistance)
                                                      options:MTLResourceStorageModeShared];
        if (ray_buffer == nil) {
            set_message(error_out, error_size, "Metal ray buffer creation failed");
            return 4;
        }

        std::vector<uint32_t> counts(ray_count, 0);
        std::vector<MPSIntersectionDistance> intersections(ray_count);
        id<MTLBuffer> intersection_buffer = [device newBufferWithLength:intersections.size() * sizeof(MPSIntersectionDistance)
                                                                 options:MTLResourceStorageModeShared];
        if (intersection_buffer == nil) {
            set_message(error_out, error_size, "Metal intersection buffer creation failed");
            return 5;
        }

        MPSRayIntersector* intersector = [[MPSRayIntersector alloc] initWithDevice:device];
        if (intersector == nil) {
            set_message(error_out, error_size, "MPSRayIntersector initialization failed");
            return 6;
        }
        intersector.cullMode = MTLCullModeNone;
        intersector.rayDataType = MPSRayDataTypeOriginMinDistanceDirectionMaxDistance;
        intersector.intersectionDataType = MPSIntersectionDataTypeDistance;
        intersector.rayStride = sizeof(MPSRayOriginMinDistanceDirectionMaxDistance);
        intersector.intersectionStride = sizeof(MPSIntersectionDistance);

        for (size_t tri_index = 0; tri_index < triangle_count; ++tri_index) {
            const RtdlTriangle3D& tri = triangles[tri_index];
            MPSPackedFloat3 vertices[3] = {
                MPSPackedFloat3(static_cast<float>(tri.x0), static_cast<float>(tri.y0), static_cast<float>(tri.z0)),
                MPSPackedFloat3(static_cast<float>(tri.x1), static_cast<float>(tri.y1), static_cast<float>(tri.z1)),
                MPSPackedFloat3(static_cast<float>(tri.x2), static_cast<float>(tri.y2), static_cast<float>(tri.z2)),
            };
            id<MTLBuffer> vertex_buffer = [device newBufferWithBytes:vertices
                                                              length:sizeof(vertices)
                                                             options:MTLResourceStorageModeShared];
            if (vertex_buffer == nil) {
                set_message(error_out, error_size, "Metal vertex buffer creation failed");
                return 7;
            }
            MPSTriangleAccelerationStructure* accel = [[MPSTriangleAccelerationStructure alloc] initWithDevice:device];
            if (accel == nil) {
                set_message(error_out, error_size, "MPSTriangleAccelerationStructure initialization failed");
                return 8;
            }
            accel.vertexBuffer = vertex_buffer;
            accel.vertexStride = sizeof(MPSPackedFloat3);
            accel.triangleCount = 1;
            [accel rebuild];

            id<MTLCommandBuffer> command_buffer = [command_queue commandBuffer];
            if (command_buffer == nil) {
                set_message(error_out, error_size, "Metal command buffer creation failed");
                return 9;
            }
            [intersector encodeIntersectionToCommandBuffer:command_buffer
                                          intersectionType:MPSIntersectionTypeAny
                                                 rayBuffer:ray_buffer
                                           rayBufferOffset:0
                                        intersectionBuffer:intersection_buffer
                                  intersectionBufferOffset:0
                                                  rayCount:ray_count
                                     accelerationStructure:accel];
            [command_buffer commit];
            [command_buffer waitUntilCompleted];
            NSError* error = [command_buffer error];
            if (error != nil) {
                set_message(error_out, error_size, [[error localizedDescription] UTF8String]);
                return 10;
            }
            const auto* gpu_intersections = static_cast<const MPSIntersectionDistance*>([intersection_buffer contents]);
            for (size_t ray_index = 0; ray_index < ray_count; ++ray_index) {
                if (gpu_intersections[ray_index].distance >= 0.0f) {
                    counts[ray_index] += 1;
                }
            }
        }

        auto* out = static_cast<RtdlRayHitCountRow*>(std::malloc(ray_count * sizeof(RtdlRayHitCountRow)));
        if (out == nullptr) {
            set_message(error_out, error_size, "out of memory allocating Apple RT hit-count rows");
            return 11;
        }
        for (size_t i = 0; i < ray_count; ++i) {
            out[i] = RtdlRayHitCountRow{rays[i].id, counts[i]};
        }
        *rows_out = out;
        *row_count_out = ray_count;
        return 0;
    }
}

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_run_lsi(
    const RtdlSegment* left_segments,
    size_t left_count,
    const RtdlSegment* right_segments,
    size_t right_count,
    RtdlLsiRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    if (rows_out == nullptr || row_count_out == nullptr) {
        set_message(error_out, error_size, "null output passed to rtdl_apple_rt_run_lsi");
        return 1;
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if ((left_count > 0 && left_segments == nullptr) || (right_count > 0 && right_segments == nullptr)) {
        set_message(error_out, error_size, "null input passed to rtdl_apple_rt_run_lsi");
        return 1;
    }
    if (left_count == 0 || right_count == 0) {
        return 0;
    }

    @autoreleasepool {
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (device == nil) {
            set_message(error_out, error_size, "Metal default device is unavailable");
            return 2;
        }
        id<MTLCommandQueue> command_queue = [device newCommandQueue];
        if (command_queue == nil) {
            set_message(error_out, error_size, "Metal command queue creation failed");
            return 3;
        }

        std::vector<MPSRayOriginMinDistanceDirectionMaxDistance> rays(left_count);
        for (size_t i = 0; i < left_count; ++i) {
            const RtdlSegment& seg = left_segments[i];
            if (!valid_segment_ray(seg)) {
                rays[i].origin = MPSPackedFloat3(INFINITY, INFINITY, INFINITY);
                rays[i].minDistance = 0.0f;
                rays[i].direction = MPSPackedFloat3(0.0f, 0.0f, 0.0f);
                rays[i].maxDistance = -1.0f;
                continue;
            }
            rays[i].origin = MPSPackedFloat3(static_cast<float>(seg.x0), static_cast<float>(seg.y0), 0.0f);
            rays[i].minDistance = 0.0f;
            rays[i].direction = MPSPackedFloat3(static_cast<float>(seg.x1 - seg.x0), static_cast<float>(seg.y1 - seg.y0), 0.0f);
            // Keep RT traversal inclusive of segment endpoints; analytic refinement below enforces exact RTDL bounds.
            rays[i].maxDistance = 1.000001f;
        }

        id<MTLBuffer> ray_buffer = [device newBufferWithBytes:rays.data()
                                                       length:rays.size() * sizeof(MPSRayOriginMinDistanceDirectionMaxDistance)
                                                      options:MTLResourceStorageModeShared];
        if (ray_buffer == nil) {
            set_message(error_out, error_size, "Metal ray buffer creation failed");
            return 4;
        }

        id<MTLBuffer> intersection_buffer = [device newBufferWithLength:left_count * sizeof(MPSIntersectionDistance)
                                                                 options:MTLResourceStorageModeShared];
        if (intersection_buffer == nil) {
            set_message(error_out, error_size, "Metal intersection buffer creation failed");
            return 5;
        }

        MPSRayIntersector* intersector = [[MPSRayIntersector alloc] initWithDevice:device];
        if (intersector == nil) {
            set_message(error_out, error_size, "MPSRayIntersector initialization failed");
            return 6;
        }
        intersector.cullMode = MTLCullModeNone;
        intersector.rayDataType = MPSRayDataTypeOriginMinDistanceDirectionMaxDistance;
        intersector.intersectionDataType = MPSIntersectionDataTypeDistance;
        intersector.rayStride = sizeof(MPSRayOriginMinDistanceDirectionMaxDistance);
        intersector.intersectionStride = sizeof(MPSIntersectionDistance);

        std::vector<std::vector<RtdlLsiRow>> rows_by_left(left_count);
        constexpr float z_extent = 1.0f;
        for (size_t right_index = 0; right_index < right_count; ++right_index) {
            const RtdlSegment& right = right_segments[right_index];
            if (!valid_segment_ray(right)) {
                continue;
            }
            MPSPackedFloat3 vertices[4] = {
                MPSPackedFloat3(static_cast<float>(right.x0), static_cast<float>(right.y0), -z_extent),
                MPSPackedFloat3(static_cast<float>(right.x1), static_cast<float>(right.y1), -z_extent),
                MPSPackedFloat3(static_cast<float>(right.x1), static_cast<float>(right.y1), z_extent),
                MPSPackedFloat3(static_cast<float>(right.x0), static_cast<float>(right.y0), z_extent),
            };
            id<MTLBuffer> vertex_buffer = [device newBufferWithBytes:vertices
                                                              length:sizeof(vertices)
                                                             options:MTLResourceStorageModeShared];
            if (vertex_buffer == nil) {
                set_message(error_out, error_size, "Metal quad vertex buffer creation failed");
                return 7;
            }

            MPSQuadrilateralAccelerationStructure* accel = [[MPSQuadrilateralAccelerationStructure alloc] initWithDevice:device];
            if (accel == nil) {
                set_message(error_out, error_size, "MPSQuadrilateralAccelerationStructure initialization failed");
                return 8;
            }
            accel.vertexBuffer = vertex_buffer;
            accel.vertexStride = sizeof(MPSPackedFloat3);
            accel.quadrilateralCount = 1;
            [accel rebuild];

            id<MTLCommandBuffer> command_buffer = [command_queue commandBuffer];
            if (command_buffer == nil) {
                set_message(error_out, error_size, "Metal command buffer creation failed");
                return 9;
            }
            [intersector encodeIntersectionToCommandBuffer:command_buffer
                                          intersectionType:MPSIntersectionTypeAny
                                                 rayBuffer:ray_buffer
                                           rayBufferOffset:0
                                        intersectionBuffer:intersection_buffer
                                  intersectionBufferOffset:0
                                                  rayCount:left_count
                                     accelerationStructure:accel];
            [command_buffer commit];
            [command_buffer waitUntilCompleted];
            NSError* error = [command_buffer error];
            if (error != nil) {
                set_message(error_out, error_size, [[error localizedDescription] UTF8String]);
                return 10;
            }

            const auto* hits = static_cast<const MPSIntersectionDistance*>([intersection_buffer contents]);
            for (size_t left_index = 0; left_index < left_count; ++left_index) {
                const float distance = hits[left_index].distance;
                if (distance < 0.0f || distance > 1.0f) {
                    continue;
                }
                const RtdlSegment& left = left_segments[left_index];
                double ix = 0.0;
                double iy = 0.0;
                if (!segment_intersection_point(left, right, &ix, &iy)) {
                    continue;
                }
                rows_by_left[left_index].push_back(RtdlLsiRow{left.id, right.id, ix, iy});
            }
        }

        std::vector<RtdlLsiRow> rows;
        rows.reserve(std::min(left_count * right_count, static_cast<size_t>(1024)));
        for (const auto& left_rows : rows_by_left) {
            rows.insert(rows.end(), left_rows.begin(), left_rows.end());
        }

        if (rows.empty()) {
            return 0;
        }
        auto* out = static_cast<RtdlLsiRow*>(std::malloc(rows.size() * sizeof(RtdlLsiRow)));
        if (out == nullptr) {
            set_message(error_out, error_size, "out of memory allocating Apple RT segment-intersection rows");
            return 11;
        }
        std::memcpy(out, rows.data(), rows.size() * sizeof(RtdlLsiRow));
        *rows_out = out;
        *row_count_out = rows.size();
        return 0;
    }
}

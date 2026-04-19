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

struct RtdlRayClosestHitRow {
    uint32_t ray_id;
    uint32_t triangle_id;
    double t;
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

}  // namespace

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_get_version(int* major, int* minor, int* patch) {
    if (major == nullptr || minor == nullptr || patch == nullptr) {
        return 1;
    }
    *major = 0;
    *minor = 9;
    *patch = 1;
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

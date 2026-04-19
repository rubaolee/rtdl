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

struct __attribute__((packed)) RtdlRay2D {
    uint32_t id;
    double ox;
    double oy;
    double dx;
    double dy;
    double tmax;
};

struct __attribute__((packed)) RtdlTriangle2D {
    uint32_t id;
    double x0;
    double y0;
    double x1;
    double y1;
    double x2;
    double y2;
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

bool valid_ray_2d(const RtdlRay2D& ray) {
    return std::isfinite(ray.ox) && std::isfinite(ray.oy) &&
           std::isfinite(ray.dx) && std::isfinite(ray.dy) &&
           std::isfinite(ray.tmax) && ray.tmax >= 0.0 &&
           (ray.dx != 0.0 || ray.dy != 0.0);
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

bool point_in_triangle_2d(double x, double y, const RtdlTriangle2D& tri) {
    const double d1 = (x - tri.x1) * (tri.y0 - tri.y1) - (tri.x0 - tri.x1) * (y - tri.y1);
    const double d2 = (x - tri.x2) * (tri.y1 - tri.y2) - (tri.x1 - tri.x2) * (y - tri.y2);
    const double d3 = (x - tri.x0) * (tri.y2 - tri.y0) - (tri.x2 - tri.x0) * (y - tri.y0);
    const bool has_neg = (d1 < -1.0e-9) || (d2 < -1.0e-9) || (d3 < -1.0e-9);
    const bool has_pos = (d1 > 1.0e-9) || (d2 > 1.0e-9) || (d3 > 1.0e-9);
    return !(has_neg && has_pos);
}

bool segment_intersects_segment_2d(
    double ax0,
    double ay0,
    double ax1,
    double ay1,
    double bx0,
    double by0,
    double bx1,
    double by1) {
    const double rx = ax1 - ax0;
    const double ry = ay1 - ay0;
    const double sx = bx1 - bx0;
    const double sy = by1 - by0;
    const double denom = rx * sy - ry * sx;
    const double qpx = bx0 - ax0;
    const double qpy = by0 - ay0;
    if (std::abs(denom) < 1.0e-9) {
        const double cross = qpx * ry - qpy * rx;
        if (std::abs(cross) > 1.0e-9) {
            return false;
        }
        const double rr = rx * rx + ry * ry;
        if (rr < 1.0e-18) {
            return false;
        }
        const double t0 = (qpx * rx + qpy * ry) / rr;
        const double t1 = t0 + (sx * rx + sy * ry) / rr;
        return std::max(std::min(t0, t1), 0.0) <= std::min(std::max(t0, t1), 1.0) + 1.0e-9;
    }
    const double t = (qpx * sy - qpy * sx) / denom;
    const double u = (qpx * ry - qpy * rx) / denom;
    return t >= -1.0e-9 && t <= 1.0 + 1.0e-9 && u >= -1.0e-9 && u <= 1.0 + 1.0e-9;
}

bool ray_hits_triangle_2d(const RtdlRay2D& ray, const RtdlTriangle2D& tri) {
    if (!valid_ray_2d(ray)) {
        return false;
    }
    const double ex = ray.ox + ray.dx * ray.tmax;
    const double ey = ray.oy + ray.dy * ray.tmax;
    if (point_in_triangle_2d(ray.ox, ray.oy, tri) || point_in_triangle_2d(ex, ey, tri)) {
        return true;
    }
    return segment_intersects_segment_2d(ray.ox, ray.oy, ex, ey, tri.x0, tri.y0, tri.x1, tri.y1) ||
           segment_intersects_segment_2d(ray.ox, ray.oy, ex, ey, tri.x1, tri.y1, tri.x2, tri.y2) ||
           segment_intersects_segment_2d(ray.ox, ray.oy, ex, ey, tri.x2, tri.y2, tri.x0, tri.y0);
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
    *patch = 3;
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

        std::vector<MPSRayOriginMaskDirectionMaxDistance> mps_rays(ray_count);
        for (size_t i = 0; i < ray_count; ++i) {
            if (!valid_ray(rays[i])) {
                mps_rays[i].origin = MPSPackedFloat3(INFINITY, INFINITY, INFINITY);
                mps_rays[i].mask = 0;
                mps_rays[i].direction = MPSPackedFloat3(0.0f, 0.0f, 0.0f);
                mps_rays[i].maxDistance = -1.0f;
                continue;
            }
            mps_rays[i].origin = MPSPackedFloat3(static_cast<float>(rays[i].ox), static_cast<float>(rays[i].oy), static_cast<float>(rays[i].oz));
            mps_rays[i].mask = 0xFFFFFFFFu;
            mps_rays[i].direction = MPSPackedFloat3(static_cast<float>(rays[i].dx), static_cast<float>(rays[i].dy), static_cast<float>(rays[i].dz));
            mps_rays[i].maxDistance = finite_tmax(rays[i].tmax);
        }

        id<MTLBuffer> ray_buffer = [device newBufferWithBytes:mps_rays.data()
                                                       length:mps_rays.size() * sizeof(MPSRayOriginMaskDirectionMaxDistance)
                                                      options:MTLResourceStorageModeShared];
        if (ray_buffer == nil) {
            set_message(error_out, error_size, "Metal ray buffer creation failed");
            return 4;
        }

        std::vector<uint32_t> counts(ray_count, 0);
        id<MTLBuffer> intersection_buffer = [device newBufferWithLength:ray_count * sizeof(MPSIntersectionDistancePrimitiveIndex)
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
        intersector.rayDataType = MPSRayDataTypeOriginMaskDirectionMaxDistance;
        intersector.rayMaskOptions = MPSRayMaskOptionPrimitive;
        intersector.rayMaskOperator = MPSRayMaskOperatorAnd;
        intersector.intersectionDataType = MPSIntersectionDataTypeDistancePrimitiveIndex;
        intersector.rayStride = sizeof(MPSRayOriginMaskDirectionMaxDistance);
        intersector.intersectionStride = sizeof(MPSIntersectionDistancePrimitiveIndex);

        constexpr size_t chunk_size = 32;
        for (size_t chunk_begin = 0; chunk_begin < triangle_count; chunk_begin += chunk_size) {
            const size_t chunk_count = std::min(chunk_size, triangle_count - chunk_begin);
            const uint32_t full_chunk_mask = chunk_count == 32 ? 0xFFFFFFFFu : ((1u << chunk_count) - 1u);

            auto* gpu_rays = static_cast<MPSRayOriginMaskDirectionMaxDistance*>([ray_buffer contents]);
            for (size_t ray_index = 0; ray_index < ray_count; ++ray_index) {
                gpu_rays[ray_index].mask = valid_ray(rays[ray_index]) ? full_chunk_mask : 0u;
            }

            std::vector<MPSPackedFloat3> vertices;
            vertices.reserve(chunk_count * 3);
            std::vector<uint32_t> primitive_masks;
            primitive_masks.reserve(chunk_count);
            for (size_t local_index = 0; local_index < chunk_count; ++local_index) {
                const RtdlTriangle3D& tri = triangles[chunk_begin + local_index];
                vertices.emplace_back(static_cast<float>(tri.x0), static_cast<float>(tri.y0), static_cast<float>(tri.z0));
                vertices.emplace_back(static_cast<float>(tri.x1), static_cast<float>(tri.y1), static_cast<float>(tri.z1));
                vertices.emplace_back(static_cast<float>(tri.x2), static_cast<float>(tri.y2), static_cast<float>(tri.z2));
                primitive_masks.push_back(1u << local_index);
            }

            id<MTLBuffer> vertex_buffer = [device newBufferWithBytes:vertices.data()
                                                              length:vertices.size() * sizeof(MPSPackedFloat3)
                                                             options:MTLResourceStorageModeShared];
            if (vertex_buffer == nil) {
                set_message(error_out, error_size, "Metal vertex buffer creation failed");
                return 7;
            }
            id<MTLBuffer> mask_buffer = [device newBufferWithBytes:primitive_masks.data()
                                                            length:primitive_masks.size() * sizeof(uint32_t)
                                                           options:MTLResourceStorageModeShared];
            if (mask_buffer == nil) {
                [vertex_buffer release];
                set_message(error_out, error_size, "Metal primitive mask buffer creation failed");
                return 8;
            }
            MPSTriangleAccelerationStructure* accel = [[MPSTriangleAccelerationStructure alloc] initWithDevice:device];
            if (accel == nil) {
                [mask_buffer release];
                [vertex_buffer release];
                set_message(error_out, error_size, "MPSTriangleAccelerationStructure initialization failed");
                return 9;
            }
            accel.vertexBuffer = vertex_buffer;
            accel.vertexStride = sizeof(MPSPackedFloat3);
            accel.maskBuffer = mask_buffer;
            accel.triangleCount = chunk_count;
            [accel rebuild];

            for (size_t pass = 0; pass < chunk_count; ++pass) {
                id<MTLCommandBuffer> command_buffer = [command_queue commandBuffer];
                if (command_buffer == nil) {
                    [accel release];
                    [mask_buffer release];
                    [vertex_buffer release];
                    set_message(error_out, error_size, "Metal command buffer creation failed");
                    return 10;
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
                    [accel release];
                    [mask_buffer release];
                    [vertex_buffer release];
                    set_message(error_out, error_size, [[error localizedDescription] UTF8String]);
                    return 11;
                }
                const auto* gpu_intersections = static_cast<const MPSIntersectionDistancePrimitiveIndex*>([intersection_buffer contents]);
                size_t active_hits = 0;
                size_t active_masks = 0;
                for (size_t ray_index = 0; ray_index < ray_count; ++ray_index) {
                    const float distance = gpu_intersections[ray_index].distance;
                    const uint32_t primitive_index = gpu_intersections[ray_index].primitiveIndex;
                    if (distance >= 0.0f && primitive_index < chunk_count) {
                        const uint32_t bit = 1u << primitive_index;
                        if ((gpu_rays[ray_index].mask & bit) != 0u) {
                            counts[ray_index] += 1;
                            gpu_rays[ray_index].mask &= ~bit;
                            active_hits += 1;
                        }
                    }
                    if (gpu_rays[ray_index].mask != 0u) {
                        active_masks += 1;
                    }
                }
                if (active_hits == 0 || active_masks == 0) {
                    break;
                }
            }
            [accel release];
            [mask_buffer release];
            [vertex_buffer release];
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

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_run_ray_hitcount_2d(
    const RtdlRay2D* rays,
    size_t ray_count,
    const RtdlTriangle2D* triangles,
    size_t triangle_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    if (rows_out == nullptr || row_count_out == nullptr) {
        set_message(error_out, error_size, "null output passed to rtdl_apple_rt_run_ray_hitcount_2d");
        return 1;
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if ((ray_count > 0 && rays == nullptr) || (triangle_count > 0 && triangles == nullptr)) {
        set_message(error_out, error_size, "null input passed to rtdl_apple_rt_run_ray_hitcount_2d");
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

        std::vector<MPSRayOriginMaskDirectionMaxDistance> mps_rays(ray_count);
        for (size_t i = 0; i < ray_count; ++i) {
            if (!valid_ray_2d(rays[i])) {
                mps_rays[i].origin = MPSPackedFloat3(INFINITY, INFINITY, INFINITY);
                mps_rays[i].mask = 0;
                mps_rays[i].direction = MPSPackedFloat3(0.0f, 0.0f, 0.0f);
                mps_rays[i].maxDistance = -1.0f;
                continue;
            }
            // Parameter t in MPS maps to the full finite RTDL ray segment:
            // xy(t) = origin + direction * (ray.tmax * t), z(t) = -1 + 2t.
            // The z sweep makes contained 2D cases intersect the triangle prism.
            mps_rays[i].origin = MPSPackedFloat3(static_cast<float>(rays[i].ox), static_cast<float>(rays[i].oy), -1.0f);
            mps_rays[i].mask = 0xFFFFFFFFu;
            mps_rays[i].direction = MPSPackedFloat3(
                static_cast<float>(rays[i].dx * rays[i].tmax),
                static_cast<float>(rays[i].dy * rays[i].tmax),
                2.0f);
            mps_rays[i].maxDistance = 1.000001f;
        }

        id<MTLBuffer> ray_buffer = [device newBufferWithBytes:mps_rays.data()
                                                       length:mps_rays.size() * sizeof(MPSRayOriginMaskDirectionMaxDistance)
                                                      options:MTLResourceStorageModeShared];
        if (ray_buffer == nil) {
            set_message(error_out, error_size, "Metal ray buffer creation failed");
            return 4;
        }

        id<MTLBuffer> intersection_buffer = [device newBufferWithLength:ray_count * sizeof(MPSIntersectionDistancePrimitiveIndex)
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
        intersector.rayDataType = MPSRayDataTypeOriginMaskDirectionMaxDistance;
        intersector.rayMaskOptions = MPSRayMaskOptionPrimitive;
        intersector.rayMaskOperator = MPSRayMaskOperatorAnd;
        intersector.intersectionDataType = MPSIntersectionDataTypeDistancePrimitiveIndex;
        intersector.rayStride = sizeof(MPSRayOriginMaskDirectionMaxDistance);
        intersector.intersectionStride = sizeof(MPSIntersectionDistancePrimitiveIndex);

        std::vector<uint32_t> counts(ray_count, 0);
        constexpr size_t chunk_size = 32;
        for (size_t chunk_begin = 0; chunk_begin < triangle_count; chunk_begin += chunk_size) {
            const size_t chunk_count = std::min(chunk_size, triangle_count - chunk_begin);
            const uint32_t full_chunk_mask = chunk_count == 32 ? 0xFFFFFFFFu : ((1u << chunk_count) - 1u);

            auto* gpu_rays = static_cast<MPSRayOriginMaskDirectionMaxDistance*>([ray_buffer contents]);
            for (size_t ray_index = 0; ray_index < ray_count; ++ray_index) {
                gpu_rays[ray_index].mask = valid_ray_2d(rays[ray_index]) ? full_chunk_mask : 0u;
            }

            std::vector<MPSPackedFloat3> vertices;
            std::vector<uint32_t> primitive_masks;
            std::vector<size_t> primitive_triangle_offsets;
            vertices.reserve(chunk_count * 24);
            primitive_masks.reserve(chunk_count * 8);
            primitive_triangle_offsets.reserve(chunk_count * 8);

            auto add_triangle = [&](float ax, float ay, float az, float bx, float by, float bz, float cx, float cy, float cz, uint32_t mask, size_t local_index) {
                vertices.emplace_back(ax, ay, az);
                vertices.emplace_back(bx, by, bz);
                vertices.emplace_back(cx, cy, cz);
                primitive_masks.push_back(mask);
                primitive_triangle_offsets.push_back(local_index);
            };

            for (size_t local_index = 0; local_index < chunk_count; ++local_index) {
                const RtdlTriangle2D& tri = triangles[chunk_begin + local_index];
                const uint32_t mask = 1u << local_index;
                const float x0 = static_cast<float>(tri.x0);
                const float y0 = static_cast<float>(tri.y0);
                const float x1 = static_cast<float>(tri.x1);
                const float y1 = static_cast<float>(tri.y1);
                const float x2 = static_cast<float>(tri.x2);
                const float y2 = static_cast<float>(tri.y2);
                constexpr float z0 = -1.0f;
                constexpr float z1 = 1.0f;

                add_triangle(x0, y0, z0, x1, y1, z0, x2, y2, z0, mask, local_index);
                add_triangle(x0, y0, z1, x2, y2, z1, x1, y1, z1, mask, local_index);

                add_triangle(x0, y0, z0, x1, y1, z0, x1, y1, z1, mask, local_index);
                add_triangle(x0, y0, z0, x1, y1, z1, x0, y0, z1, mask, local_index);
                add_triangle(x1, y1, z0, x2, y2, z0, x2, y2, z1, mask, local_index);
                add_triangle(x1, y1, z0, x2, y2, z1, x1, y1, z1, mask, local_index);
                add_triangle(x2, y2, z0, x0, y0, z0, x0, y0, z1, mask, local_index);
                add_triangle(x2, y2, z0, x0, y0, z1, x2, y2, z1, mask, local_index);
            }

            id<MTLBuffer> vertex_buffer = [device newBufferWithBytes:vertices.data()
                                                              length:vertices.size() * sizeof(MPSPackedFloat3)
                                                             options:MTLResourceStorageModeShared];
            if (vertex_buffer == nil) {
                set_message(error_out, error_size, "Metal 2D hit-count prism vertex buffer creation failed");
                return 7;
            }
            id<MTLBuffer> mask_buffer = [device newBufferWithBytes:primitive_masks.data()
                                                            length:primitive_masks.size() * sizeof(uint32_t)
                                                           options:MTLResourceStorageModeShared];
            if (mask_buffer == nil) {
                [vertex_buffer release];
                set_message(error_out, error_size, "Metal 2D hit-count primitive mask buffer creation failed");
                return 8;
            }

            MPSTriangleAccelerationStructure* accel = [[MPSTriangleAccelerationStructure alloc] initWithDevice:device];
            if (accel == nil) {
                [mask_buffer release];
                [vertex_buffer release];
                set_message(error_out, error_size, "MPSTriangleAccelerationStructure initialization failed for 2D hit-count");
                return 9;
            }
            accel.vertexBuffer = vertex_buffer;
            accel.vertexStride = sizeof(MPSPackedFloat3);
            accel.maskBuffer = mask_buffer;
            accel.triangleCount = primitive_masks.size();
            [accel rebuild];

            for (size_t pass = 0; pass < chunk_count; ++pass) {
                id<MTLCommandBuffer> command_buffer = [command_queue commandBuffer];
                if (command_buffer == nil) {
                    [accel release];
                    [mask_buffer release];
                    [vertex_buffer release];
                    set_message(error_out, error_size, "Metal command buffer creation failed");
                    return 10;
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
                    [accel release];
                    [mask_buffer release];
                    [vertex_buffer release];
                    set_message(error_out, error_size, [[error localizedDescription] UTF8String]);
                    return 11;
                }
                const auto* gpu_intersections = static_cast<const MPSIntersectionDistancePrimitiveIndex*>([intersection_buffer contents]);
                size_t active_hits = 0;
                size_t active_masks = 0;
                for (size_t ray_index = 0; ray_index < ray_count; ++ray_index) {
                    const float distance = gpu_intersections[ray_index].distance;
                    const uint32_t primitive_index = gpu_intersections[ray_index].primitiveIndex;
                    if (distance >= 0.0f && distance <= 1.000001f && primitive_index < primitive_triangle_offsets.size()) {
                        const size_t local_index = primitive_triangle_offsets[primitive_index];
                        const uint32_t bit = 1u << local_index;
                        if ((gpu_rays[ray_index].mask & bit) != 0u) {
                            const RtdlTriangle2D& tri = triangles[chunk_begin + local_index];
                            if (ray_hits_triangle_2d(rays[ray_index], tri)) {
                                counts[ray_index] += 1;
                            }
                            gpu_rays[ray_index].mask &= ~bit;
                            active_hits += 1;
                        }
                    }
                    if (gpu_rays[ray_index].mask != 0u) {
                        active_masks += 1;
                    }
                }
                if (active_hits == 0 || active_masks == 0) {
                    break;
                }
            }
            [accel release];
            [mask_buffer release];
            [vertex_buffer release];
        }

        auto* out = static_cast<RtdlRayHitCountRow*>(std::malloc(ray_count * sizeof(RtdlRayHitCountRow)));
        if (out == nullptr) {
            set_message(error_out, error_size, "out of memory allocating Apple RT 2D hit-count rows");
            return 12;
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

        std::vector<MPSRayOriginMaskDirectionMaxDistance> rays(left_count);
        for (size_t i = 0; i < left_count; ++i) {
            const RtdlSegment& seg = left_segments[i];
            if (!valid_segment_ray(seg)) {
                rays[i].origin = MPSPackedFloat3(INFINITY, INFINITY, INFINITY);
                rays[i].mask = 0;
                rays[i].direction = MPSPackedFloat3(0.0f, 0.0f, 0.0f);
                rays[i].maxDistance = -1.0f;
                continue;
            }
            rays[i].origin = MPSPackedFloat3(static_cast<float>(seg.x0), static_cast<float>(seg.y0), 0.0f);
            rays[i].mask = 0xFFFFFFFFu;
            rays[i].direction = MPSPackedFloat3(static_cast<float>(seg.x1 - seg.x0), static_cast<float>(seg.y1 - seg.y0), 0.0f);
            // Keep RT traversal inclusive of segment endpoints; analytic refinement below enforces exact RTDL bounds.
            rays[i].maxDistance = 1.000001f;
        }

        id<MTLBuffer> ray_buffer = [device newBufferWithBytes:rays.data()
                                                       length:rays.size() * sizeof(MPSRayOriginMaskDirectionMaxDistance)
                                                      options:MTLResourceStorageModeShared];
        if (ray_buffer == nil) {
            set_message(error_out, error_size, "Metal ray buffer creation failed");
            return 4;
        }

        id<MTLBuffer> intersection_buffer = [device newBufferWithLength:left_count * sizeof(MPSIntersectionDistancePrimitiveIndex)
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
        intersector.rayDataType = MPSRayDataTypeOriginMaskDirectionMaxDistance;
        intersector.rayMaskOptions = MPSRayMaskOptionPrimitive;
        intersector.rayMaskOperator = MPSRayMaskOperatorAnd;
        intersector.intersectionDataType = MPSIntersectionDataTypeDistancePrimitiveIndex;
        intersector.rayStride = sizeof(MPSRayOriginMaskDirectionMaxDistance);
        intersector.intersectionStride = sizeof(MPSIntersectionDistancePrimitiveIndex);

        std::vector<std::vector<std::pair<size_t, RtdlLsiRow>>> rows_by_left(left_count);
        constexpr float z_extent = 1.0f;
        constexpr size_t chunk_size = 32;
        for (size_t chunk_begin = 0; chunk_begin < right_count; chunk_begin += chunk_size) {
            std::vector<size_t> right_indices;
            right_indices.reserve(chunk_size);
            for (size_t offset = 0; offset < chunk_size && chunk_begin + offset < right_count; ++offset) {
                const size_t right_index = chunk_begin + offset;
                if (valid_segment_ray(right_segments[right_index])) {
                    right_indices.push_back(right_index);
                }
            }
            const size_t chunk_count = right_indices.size();
            if (chunk_count == 0) {
                continue;
            }
            const uint32_t full_chunk_mask = chunk_count == 32 ? 0xFFFFFFFFu : ((1u << chunk_count) - 1u);

            auto* gpu_rays = static_cast<MPSRayOriginMaskDirectionMaxDistance*>([ray_buffer contents]);
            for (size_t left_index = 0; left_index < left_count; ++left_index) {
                gpu_rays[left_index].mask = valid_segment_ray(left_segments[left_index]) ? full_chunk_mask : 0u;
            }

            std::vector<MPSPackedFloat3> vertices;
            vertices.reserve(chunk_count * 4);
            std::vector<uint32_t> primitive_masks;
            primitive_masks.reserve(chunk_count);
            for (size_t local_index = 0; local_index < chunk_count; ++local_index) {
                const RtdlSegment& right = right_segments[right_indices[local_index]];
                vertices.emplace_back(static_cast<float>(right.x0), static_cast<float>(right.y0), -z_extent);
                vertices.emplace_back(static_cast<float>(right.x1), static_cast<float>(right.y1), -z_extent);
                vertices.emplace_back(static_cast<float>(right.x1), static_cast<float>(right.y1), z_extent);
                vertices.emplace_back(static_cast<float>(right.x0), static_cast<float>(right.y0), z_extent);
                primitive_masks.push_back(1u << local_index);
            }
            id<MTLBuffer> vertex_buffer = [device newBufferWithBytes:vertices.data()
                                                              length:vertices.size() * sizeof(MPSPackedFloat3)
                                                             options:MTLResourceStorageModeShared];
            if (vertex_buffer == nil) {
                set_message(error_out, error_size, "Metal quad vertex buffer creation failed");
                return 7;
            }
            id<MTLBuffer> mask_buffer = [device newBufferWithBytes:primitive_masks.data()
                                                            length:primitive_masks.size() * sizeof(uint32_t)
                                                           options:MTLResourceStorageModeShared];
            if (mask_buffer == nil) {
                [vertex_buffer release];
                set_message(error_out, error_size, "Metal primitive mask buffer creation failed");
                return 8;
            }

            MPSQuadrilateralAccelerationStructure* accel = [[MPSQuadrilateralAccelerationStructure alloc] initWithDevice:device];
            if (accel == nil) {
                [mask_buffer release];
                [vertex_buffer release];
                set_message(error_out, error_size, "MPSQuadrilateralAccelerationStructure initialization failed");
                return 9;
            }
            accel.vertexBuffer = vertex_buffer;
            accel.vertexStride = sizeof(MPSPackedFloat3);
            accel.maskBuffer = mask_buffer;
            accel.quadrilateralCount = chunk_count;
            [accel rebuild];

            for (size_t pass = 0; pass < chunk_count; ++pass) {
                id<MTLCommandBuffer> command_buffer = [command_queue commandBuffer];
                if (command_buffer == nil) {
                    [accel release];
                    [mask_buffer release];
                    [vertex_buffer release];
                    set_message(error_out, error_size, "Metal command buffer creation failed");
                    return 10;
                }
                [intersector encodeIntersectionToCommandBuffer:command_buffer
                                              intersectionType:MPSIntersectionTypeNearest
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
                    [accel release];
                    [mask_buffer release];
                    [vertex_buffer release];
                    set_message(error_out, error_size, [[error localizedDescription] UTF8String]);
                    return 11;
                }
                const auto* hits = static_cast<const MPSIntersectionDistancePrimitiveIndex*>([intersection_buffer contents]);
                size_t active_hits = 0;
                size_t active_masks = 0;
                for (size_t left_index = 0; left_index < left_count; ++left_index) {
                    const float distance = hits[left_index].distance;
                    const uint32_t primitive_index = hits[left_index].primitiveIndex;
                    if (distance >= 0.0f && distance <= 1.000001f && primitive_index < chunk_count) {
                        const uint32_t bit = 1u << primitive_index;
                        if ((gpu_rays[left_index].mask & bit) != 0u) {
                            const size_t right_index = right_indices[primitive_index];
                            const RtdlSegment& left = left_segments[left_index];
                            const RtdlSegment& right = right_segments[right_index];
                            double ix = 0.0;
                            double iy = 0.0;
                            if (segment_intersection_point(left, right, &ix, &iy)) {
                                rows_by_left[left_index].push_back({right_index, RtdlLsiRow{left.id, right.id, ix, iy}});
                            }
                            gpu_rays[left_index].mask &= ~bit;
                            active_hits += 1;
                        }
                    }
                    if (gpu_rays[left_index].mask != 0u) {
                        active_masks += 1;
                    }
                }
                if (active_hits == 0 || active_masks == 0) {
                    break;
                }
            }
            [accel release];
            [mask_buffer release];
            [vertex_buffer release];
        }

        std::vector<RtdlLsiRow> rows;
        rows.reserve(std::min(left_count * right_count, static_cast<size_t>(1024)));
        for (auto& left_rows : rows_by_left) {
            std::sort(left_rows.begin(), left_rows.end(), [](const auto& a, const auto& b) {
                return a.first < b.first;
            });
            for (const auto& item : left_rows) {
                rows.push_back(item.second);
            }
        }

        if (rows.empty()) {
            return 0;
        }
        auto* out = static_cast<RtdlLsiRow*>(std::malloc(rows.size() * sizeof(RtdlLsiRow)));
        if (out == nullptr) {
            set_message(error_out, error_size, "out of memory allocating Apple RT segment-intersection rows");
            return 12;
        }
        std::memcpy(out, rows.data(), rows.size() * sizeof(RtdlLsiRow));
        *rows_out = out;
        *row_count_out = rows.size();
        return 0;
    }
}

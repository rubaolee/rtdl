#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <MetalPerformanceShaders/MetalPerformanceShaders.h>

#include <algorithm>
#include <chrono>
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

struct __attribute__((packed)) RtdlPoint2D {
    uint32_t id;
    double x;
    double y;
};

struct __attribute__((packed)) RtdlPoint3D {
    uint32_t id;
    double x;
    double y;
    double z;
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

struct RtdlRayAnyHitRow {
    uint32_t ray_id;
    uint32_t any_hit;
};

struct RtdlAppleRtAnyHitProfile {
    double total_seconds;
    double buffer_seconds;
    double ray_pack_seconds;
    double dispatch_wait_seconds;
    double result_scan_seconds;
    double output_seconds;
    uint64_t chunk_count;
    uint64_t ray_count;
    uint64_t hit_count;
};

struct RtdlNeighborRow {
    uint32_t query_id;
    uint32_t neighbor_id;
    double distance;
};

struct RtdlPolygonBounds2D {
    uint32_t id;
    double minx;
    double miny;
    double maxx;
    double maxy;
};

struct RtdlPointPolygonCandidateRow {
    uint32_t point_id;
    uint32_t polygon_id;
};

struct RtdlSegmentPolygonCandidateRow {
    uint32_t segment_id;
    uint32_t polygon_id;
};

struct RtdlAppleDbNumericClause {
    uint32_t field_index;
    uint32_t op;
    float value;
    float value_hi;
};

struct RtdlAppleFrontierVertex {
    uint32_t vertex_id;
    uint32_t level;
};

struct RtdlAppleBfsRow {
    uint32_t src_vertex;
    uint32_t dst_vertex;
    uint32_t level;
};

struct RtdlAppleEdgeSeed {
    uint32_t u;
    uint32_t v;
};

struct RtdlAppleTriangleRow {
    uint32_t u;
    uint32_t v;
    uint32_t w;
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

struct AppleRtAnyHit2DPrepared {
    id<MTLDevice> device = nil;
    id<MTLCommandQueue> command_queue = nil;
    id<MTLBuffer> vertex_buffer = nil;
    id<MTLBuffer> mask_buffer = nil;
    MPSTriangleAccelerationStructure* accel = nil;
    MPSRayIntersector* intersector = nil;
    id<MTLBuffer> ray_buffer = nil;
    id<MTLBuffer> intersection_buffer = nil;
    size_t ray_capacity = 0;
    size_t triangle_count = 0;

    ~AppleRtAnyHit2DPrepared() {
        [intersection_buffer release];
        [ray_buffer release];
        [intersector release];
        [accel release];
        [mask_buffer release];
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

double point_distance_2d(const RtdlPoint2D& query, const RtdlPoint2D& point) {
    const double dx = query.x - point.x;
    const double dy = query.y - point.y;
    return std::sqrt(dx * dx + dy * dy);
}

double point_distance_3d(const RtdlPoint3D& query, const RtdlPoint3D& point) {
    const double dx = query.x - point.x;
    const double dy = query.y - point.y;
    const double dz = query.z - point.z;
    return std::sqrt(dx * dx + dy * dy + dz * dz);
}

using Clock = std::chrono::steady_clock;

double elapsed_seconds(Clock::time_point begin, Clock::time_point end) {
    return std::chrono::duration<double>(end - begin).count();
}

void fill_mps_rays_2d(const RtdlRay2D* rays, size_t ray_count, MPSRayOriginMaskDirectionMaxDistance* out) {
    for (size_t i = 0; i < ray_count; ++i) {
        if (!valid_ray_2d(rays[i])) {
            out[i].origin = MPSPackedFloat3(INFINITY, INFINITY, INFINITY);
            out[i].mask = 0;
            out[i].direction = MPSPackedFloat3(0.0f, 0.0f, 0.0f);
            out[i].maxDistance = -1.0f;
            continue;
        }
        out[i].origin = MPSPackedFloat3(static_cast<float>(rays[i].ox), static_cast<float>(rays[i].oy), -1.0f);
        out[i].mask = 0xFFFFFFFFu;
        out[i].direction = MPSPackedFloat3(
            static_cast<float>(rays[i].dx * rays[i].tmax),
            static_cast<float>(rays[i].dy * rays[i].tmax),
            2.0f);
        out[i].maxDistance = 1.000001f;
    }
}

int ensure_anyhit_2d_work_buffers(AppleRtAnyHit2DPrepared* prepared, size_t ray_count, char* error_out, size_t error_size) {
    if (ray_count <= prepared->ray_capacity) {
        return 0;
    }
    [prepared->ray_buffer release];
    [prepared->intersection_buffer release];
    prepared->ray_buffer = [prepared->device newBufferWithLength:ray_count * sizeof(MPSRayOriginMaskDirectionMaxDistance)
                                                         options:MTLResourceStorageModeShared];
    prepared->intersection_buffer = [prepared->device newBufferWithLength:ray_count * sizeof(MPSIntersectionDistancePrimitiveIndex)
                                                                   options:MTLResourceStorageModeShared];
    if (prepared->ray_buffer == nil || prepared->intersection_buffer == nil) {
        prepared->ray_capacity = 0;
        set_message(error_out, error_size, "Metal prepared 2D any-hit work-buffer creation failed");
        return 2;
    }
    prepared->ray_capacity = ray_count;
    return 0;
}

int run_anyhit_2d_prepared(
    AppleRtAnyHit2DPrepared* prepared,
    const RtdlRay2D* rays,
    size_t ray_count,
    RtdlRayAnyHitRow** rows_out,
    size_t* row_count_out,
    uint64_t* hit_count_out,
    RtdlAppleRtAnyHitProfile* profile_out,
    bool emit_rows,
    char* error_out,
    size_t error_size) {
    const auto total_begin = Clock::now();
    if (prepared == nullptr || (emit_rows && rows_out == nullptr) || row_count_out == nullptr || hit_count_out == nullptr) {
        set_message(error_out, error_size, "null handle or output passed to Apple RT prepared 2D any-hit run");
        return 1;
    }
    if (emit_rows) {
        *rows_out = nullptr;
    }
    *row_count_out = 0;
    *hit_count_out = 0;
    if (ray_count > 0 && rays == nullptr) {
        set_message(error_out, error_size, "null rays passed to Apple RT prepared 2D any-hit run");
        return 1;
    }
    if (ray_count == 0 || prepared->triangle_count == 0) {
        if (emit_rows && ray_count > 0) {
            auto* out = static_cast<RtdlRayAnyHitRow*>(std::malloc(ray_count * sizeof(RtdlRayAnyHitRow)));
            if (out == nullptr) {
                set_message(error_out, error_size, "out of memory allocating empty Apple RT prepared 2D any-hit rows");
                return 2;
            }
            for (size_t i = 0; i < ray_count; ++i) {
                out[i] = RtdlRayAnyHitRow{rays[i].id, 0u};
            }
            *rows_out = out;
            *row_count_out = ray_count;
        }
        if (profile_out != nullptr) {
            const auto total_end = Clock::now();
            *profile_out = RtdlAppleRtAnyHitProfile{
                elapsed_seconds(total_begin, total_end), 0.0, 0.0, 0.0, 0.0, 0.0,
                prepared->triangle_count == 0 ? 0u : 1u,
                static_cast<uint64_t>(ray_count),
                0u,
            };
        }
        return 0;
    }

    const auto buffer_begin = Clock::now();
    int status = ensure_anyhit_2d_work_buffers(prepared, ray_count, error_out, error_size);
    const auto buffer_end = Clock::now();
    if (status != 0) {
        return status;
    }

    const auto pack_begin = Clock::now();
    auto* gpu_rays = static_cast<MPSRayOriginMaskDirectionMaxDistance*>([prepared->ray_buffer contents]);
    fill_mps_rays_2d(rays, ray_count, gpu_rays);
    const auto pack_end = Clock::now();

    const auto dispatch_begin = Clock::now();
    id<MTLCommandBuffer> command_buffer = [prepared->command_queue commandBuffer];
    if (command_buffer == nil) {
        set_message(error_out, error_size, "Metal command buffer creation failed");
        return 3;
    }
    [prepared->intersector encodeIntersectionToCommandBuffer:command_buffer
                                            intersectionType:MPSIntersectionTypeNearest
                                                   rayBuffer:prepared->ray_buffer
                                             rayBufferOffset:0
                                          intersectionBuffer:prepared->intersection_buffer
                                    intersectionBufferOffset:0
                                                    rayCount:ray_count
                                       accelerationStructure:prepared->accel];
    [command_buffer commit];
    [command_buffer waitUntilCompleted];
    NSError* error = [command_buffer error];
    const auto dispatch_end = Clock::now();
    if (error != nil) {
        set_message(error_out, error_size, [[error localizedDescription] UTF8String]);
        return 4;
    }

    const auto scan_begin = Clock::now();
    const auto* gpu_intersections = static_cast<const MPSIntersectionDistancePrimitiveIndex*>([prepared->intersection_buffer contents]);
    std::vector<uint32_t> any_hits;
    if (emit_rows) {
        any_hits.resize(ray_count, 0u);
    }
    uint64_t hit_count = 0;
    for (size_t i = 0; i < ray_count; ++i) {
        const float distance = gpu_intersections[i].distance;
        const bool hit = valid_ray_2d(rays[i]) && distance >= 0.0f && distance <= 1.000001f;
        if (hit) {
            hit_count += 1;
        }
        if (emit_rows) {
            any_hits[i] = hit ? 1u : 0u;
        }
    }
    const auto scan_end = Clock::now();

    const auto output_begin = Clock::now();
    if (emit_rows) {
        auto* out = static_cast<RtdlRayAnyHitRow*>(std::malloc(ray_count * sizeof(RtdlRayAnyHitRow)));
        if (out == nullptr) {
            set_message(error_out, error_size, "out of memory allocating Apple RT prepared 2D any-hit rows");
            return 5;
        }
        for (size_t i = 0; i < ray_count; ++i) {
            out[i] = RtdlRayAnyHitRow{rays[i].id, any_hits[i]};
        }
        *rows_out = out;
        *row_count_out = ray_count;
    }
    *hit_count_out = hit_count;
    const auto output_end = Clock::now();

    if (profile_out != nullptr) {
        const auto total_end = Clock::now();
        *profile_out = RtdlAppleRtAnyHitProfile{
            elapsed_seconds(total_begin, total_end),
            elapsed_seconds(buffer_begin, buffer_end),
            elapsed_seconds(pack_begin, pack_end),
            elapsed_seconds(dispatch_begin, dispatch_end),
            elapsed_seconds(scan_begin, scan_end),
            elapsed_seconds(output_begin, output_end),
            1u,
            static_cast<uint64_t>(ray_count),
            hit_count,
        };
    }
    return 0;
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

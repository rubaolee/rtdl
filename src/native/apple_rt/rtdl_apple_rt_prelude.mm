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

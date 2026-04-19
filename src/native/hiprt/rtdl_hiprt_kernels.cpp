const char* ray_hitcount_kernel_source() {
    return R"KERNEL(
#include <hiprt/hiprt_device.h>
#include <hiprt/hiprt_vec.h>

struct RtdlHiprtRay3DDevice {
    uint32_t id;
    float ox;
    float oy;
    float oz;
    float dx;
    float dy;
    float dz;
    float tmax;
};

struct RtdlRayHitCountRow {
    uint32_t ray_id;
    uint32_t hit_count;
};

extern "C" __global__ void RtdlRayHitcount3DKernel(
    hiprtGeometry geom,
    const RtdlHiprtRay3DDevice* rays,
    uint32_t ray_count,
    RtdlRayHitCountRow* rows) {
    const uint32_t index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index >= ray_count) {
        return;
    }
    const RtdlHiprtRay3DDevice in = rays[index];
    hiprtRay ray;
    ray.origin = {in.ox, in.oy, in.oz};
    ray.direction = {in.dx, in.dy, in.dz};
    ray.maxT = in.tmax;

    uint32_t hit_count = 0;
    hiprtGeomTraversalAnyHit traversal(geom, ray, hiprtTraversalHintDefault);
    while (traversal.getCurrentState() != hiprtTraversalStateFinished) {
        hiprtHit hit = traversal.getNextHit();
        if (hit.hasHit()) {
            ++hit_count;
        }
    }
    rows[index].ray_id = in.id;
    rows[index].hit_count = hit_count;
}
)KERNEL";
}

const char* lsi_2d_kernel_source() {
    return R"KERNEL(
#include <hiprt/hiprt_device.h>
#include <hiprt/hiprt_vec.h>

struct RtdlHiprtSegmentDevice {
    uint32_t id;
    float x0;
    float y0;
    float x1;
    float y1;
};

struct RtdlLsiRow {
    uint32_t left_id;
    uint32_t right_id;
    double intersection_point_x;
    double intersection_point_y;
};

__device__ bool intersectRtdlSegment2D(const hiprtRay& ray, const void* data, void* payload, hiprtHit& hit) {
    const RtdlHiprtSegmentDevice* right_segments = reinterpret_cast<const RtdlHiprtSegmentDevice*>(data);
    const RtdlHiprtSegmentDevice right = right_segments[hit.primID];
    const float px = ray.origin.x;
    const float py = ray.origin.y;
    const float rx = ray.direction.x;
    const float ry = ray.direction.y;
    const float qx = right.x0;
    const float qy = right.y0;
    const float sx = right.x1 - right.x0;
    const float sy = right.y1 - right.y0;
    const float denom = rx * sy - ry * sx;
    if (fabsf(denom) < 1.0e-7f) {
        return false;
    }
    const float qpx = qx - px;
    const float qpy = qy - py;
    const float t = (qpx * sy - qpy * sx) / denom;
    const float u = (qpx * ry - qpy * rx) / denom;
    if (t < 0.0f || t > 1.0f || u < 0.0f || u > 1.0f) {
        return false;
    }
    hit.t = t;
    return true;
}

extern "C" __global__ void RtdlLsi2DKernel(
    hiprtGeometry geom,
    const RtdlHiprtSegmentDevice* left_segments,
    const RtdlHiprtSegmentDevice* right_segments,
    uint32_t left_count,
    uint32_t right_count,
    RtdlLsiRow* rows,
    uint32_t* counts,
    hiprtFuncTable table) {
    const uint32_t index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index >= left_count) {
        return;
    }
    const RtdlHiprtSegmentDevice left = left_segments[index];
    hiprtRay ray;
    ray.origin = {left.x0, left.y0, 0.0f};
    ray.direction = {left.x1 - left.x0, left.y1 - left.y0, 0.0f};
    ray.minT = 0.0f;
    ray.maxT = 1.0f;

    uint32_t count = 0u;
    hiprtGeomCustomTraversalAnyHit traversal(geom, ray, hiprtTraversalHintDefault, nullptr, table);
    while (traversal.getCurrentState() != hiprtTraversalStateFinished) {
        hiprtHit hit = traversal.getNextHit();
        if (!hit.hasHit()) {
            continue;
        }
        const RtdlHiprtSegmentDevice right = right_segments[hit.primID];
        const float ix = left.x0 + hit.t * (left.x1 - left.x0);
        const float iy = left.y0 + hit.t * (left.y1 - left.y0);
        const uint32_t out_index = index * right_count + count;
        rows[out_index].left_id = left.id;
        rows[out_index].right_id = right.id;
        rows[out_index].intersection_point_x = static_cast<double>(ix);
        rows[out_index].intersection_point_y = static_cast<double>(iy);
        ++count;
    }
    counts[index] = count;
}
)KERNEL";
}

const char* ray_hitcount_2d_kernel_source() {
    return R"KERNEL(
#include <hiprt/hiprt_device.h>
#include <hiprt/hiprt_vec.h>

struct RtdlHiprtRay2DDevice {
    uint32_t id;
    float ox;
    float oy;
    float dx;
    float dy;
    float tmax;
};

struct RtdlHiprtTriangle2DDevice {
    uint32_t id;
    float x0;
    float y0;
    float x1;
    float y1;
    float x2;
    float y2;
};

struct RtdlRayHitCountRow {
    uint32_t ray_id;
    uint32_t hit_count;
};

__device__ bool pointInTriangle2D(float x, float y, const RtdlHiprtTriangle2DDevice& tri) {
    const float ax = tri.x0;
    const float ay = tri.y0;
    const float bx = tri.x1;
    const float by = tri.y1;
    const float cx = tri.x2;
    const float cy = tri.y2;
    const float v0x = cx - ax;
    const float v0y = cy - ay;
    const float v1x = bx - ax;
    const float v1y = by - ay;
    const float v2x = x - ax;
    const float v2y = y - ay;
    const float dot00 = v0x * v0x + v0y * v0y;
    const float dot01 = v0x * v1x + v0y * v1y;
    const float dot02 = v0x * v2x + v0y * v2y;
    const float dot11 = v1x * v1x + v1y * v1y;
    const float dot12 = v1x * v2x + v1y * v2y;
    const float denom = dot00 * dot11 - dot01 * dot01;
    if (fabsf(denom) < 1.0e-7f) {
        return false;
    }
    const float inv = 1.0f / denom;
    const float u = (dot11 * dot02 - dot01 * dot12) * inv;
    const float v = (dot00 * dot12 - dot01 * dot02) * inv;
    return u >= 0.0f && v >= 0.0f && (u + v) <= 1.0f;
}

__device__ bool finiteSegmentIntersectsSegment2D(
    float px,
    float py,
    float rx,
    float ry,
    float qx,
    float qy,
    float sx,
    float sy) {
    const float denom = rx * sy - ry * sx;
    if (fabsf(denom) < 1.0e-7f) {
        return false;
    }
    const float qpx = qx - px;
    const float qpy = qy - py;
    const float t = (qpx * sy - qpy * sx) / denom;
    const float u = (qpx * ry - qpy * rx) / denom;
    return t >= 0.0f && t <= 1.0f && u >= 0.0f && u <= 1.0f;
}

__device__ bool finiteRayHitsTriangle2D(const hiprtRay& ray, const RtdlHiprtTriangle2DDevice& tri) {
    const float sx = ray.origin.x;
    const float sy = ray.origin.y;
    const float ex = ray.origin.x + ray.direction.x;
    const float ey = ray.origin.y + ray.direction.y;
    if (pointInTriangle2D(sx, sy, tri) || pointInTriangle2D(ex, ey, tri)) {
        return true;
    }
    const float rx = ex - sx;
    const float ry = ey - sy;
    return finiteSegmentIntersectsSegment2D(sx, sy, rx, ry, tri.x0, tri.y0, tri.x1 - tri.x0, tri.y1 - tri.y0) ||
           finiteSegmentIntersectsSegment2D(sx, sy, rx, ry, tri.x1, tri.y1, tri.x2 - tri.x1, tri.y2 - tri.y1) ||
           finiteSegmentIntersectsSegment2D(sx, sy, rx, ry, tri.x2, tri.y2, tri.x0 - tri.x2, tri.y0 - tri.y2);
}

__device__ bool intersectRtdlTriangle2D(const hiprtRay& ray, const void* data, void* payload, hiprtHit& hit) {
    const RtdlHiprtTriangle2DDevice* triangles = reinterpret_cast<const RtdlHiprtTriangle2DDevice*>(data);
    const RtdlHiprtTriangle2DDevice tri = triangles[hit.primID];
    if (!finiteRayHitsTriangle2D(ray, tri)) {
        return false;
    }
    hit.t = 0.0f;
    return true;
}

extern "C" __global__ void RtdlRayHitcount2DKernel(
    hiprtGeometry geom,
    const RtdlHiprtRay2DDevice* rays,
    uint32_t ray_count,
    RtdlRayHitCountRow* rows,
    hiprtFuncTable table) {
    const uint32_t index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index >= ray_count) {
        return;
    }
    const RtdlHiprtRay2DDevice in = rays[index];
    hiprtRay ray;
    ray.origin = {in.ox, in.oy, 0.0f};
    ray.direction = {in.dx * in.tmax, in.dy * in.tmax, 0.0f};
    ray.minT = 0.0f;
    ray.maxT = 1.0f;

    uint32_t hit_count = 0u;
    hiprtGeomCustomTraversalAnyHit traversal(geom, ray, hiprtTraversalHintDefault, nullptr, table);
    while (traversal.getCurrentState() != hiprtTraversalStateFinished) {
        hiprtHit hit = traversal.getNextHit();
        if (hit.hasHit()) {
            ++hit_count;
        }
    }
    rows[index].ray_id = in.id;
    rows[index].hit_count = hit_count;
}
)KERNEL";
}

const char* pip_2d_kernel_source() {
    return R"KERNEL(
#include <hiprt/hiprt_device.h>
#include <hiprt/hiprt_vec.h>

struct RtdlHiprtPoint2DDevice {
    uint32_t id;
    float x;
    float y;
};

struct RtdlHiprtPolygonRefDevice {
    uint32_t id;
    uint32_t vertex_offset;
    uint32_t vertex_count;
};

struct RtdlHiprtVertex2DDevice {
    float x;
    float y;
};

struct RtdlHiprtPipDataDevice {
    const RtdlHiprtPolygonRefDevice* polygons;
    const RtdlHiprtVertex2DDevice* vertices;
};

struct RtdlPipRow {
    uint32_t point_id;
    uint32_t polygon_id;
    uint32_t contains;
};

__device__ bool pointOnSegment2D(float px, float py, float ax, float ay, float bx, float by) {
    const float eps = 1.0e-6f;
    const float vx = bx - ax;
    const float vy = by - ay;
    const float wx = px - ax;
    const float wy = py - ay;
    const float length_sq = vx * vx + vy * vy;
    if (length_sq <= eps * eps) {
        return fabsf(px - ax) <= eps && fabsf(py - ay) <= eps;
    }
    const float cross = wx * vy - wy * vx;
    if (fabsf(cross) > eps * sqrtf(length_sq)) {
        return false;
    }
    const float dot = wx * vx + wy * vy;
    const float length = sqrtf(length_sq);
    const float along_eps = eps * length;
    return dot >= -along_eps && dot - length_sq <= along_eps;
}

__device__ bool pointInPolygon2D(float x, float y, const RtdlHiprtPolygonRefDevice& polygon, const RtdlHiprtVertex2DDevice* vertices) {
    if (polygon.vertex_count < 3u) {
        return false;
    }
    bool inside = false;
    uint32_t prev = polygon.vertex_count - 1u;
    for (uint32_t i = 0; i < polygon.vertex_count; ++i) {
        const RtdlHiprtVertex2DDevice a = vertices[polygon.vertex_offset + prev];
        const RtdlHiprtVertex2DDevice b = vertices[polygon.vertex_offset + i];
        if (pointOnSegment2D(x, y, a.x, a.y, b.x, b.y)) {
            return true;
        }
        const bool crossing = ((b.y > y) != (a.y > y)) &&
            (x <= (a.x - b.x) * (y - b.y) / ((a.y - b.y) == 0.0f ? 1.0e-20f : (a.y - b.y)) + b.x);
        if (crossing) {
            inside = !inside;
        }
        prev = i;
    }
    return inside;
}

__device__ bool intersectRtdlPolygon2D(const hiprtRay& ray, const void* data, void* payload, hiprtHit& hit) {
    const RtdlHiprtPipDataDevice* pip = reinterpret_cast<const RtdlHiprtPipDataDevice*>(data);
    const RtdlHiprtPolygonRefDevice polygon = pip->polygons[hit.primID];
    if (!pointInPolygon2D(ray.origin.x, ray.origin.y, polygon, pip->vertices)) {
        return false;
    }
    hit.t = 0.0f;
    return true;
}

extern "C" __global__ void RtdlPip2DKernel(
    hiprtGeometry geom,
    const RtdlHiprtPoint2DDevice* points,
    const RtdlHiprtPolygonRefDevice* polygons,
    uint32_t point_count,
    uint32_t polygon_count,
    RtdlPipRow* rows,
    hiprtFuncTable table) {
    const uint32_t index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index >= point_count) {
        return;
    }
    const RtdlHiprtPoint2DDevice point = points[index];
    const uint32_t base = index * polygon_count;
    for (uint32_t polygon_index = 0; polygon_index < polygon_count; ++polygon_index) {
        rows[base + polygon_index].point_id = point.id;
        rows[base + polygon_index].polygon_id = polygons[polygon_index].id;
        rows[base + polygon_index].contains = 0u;
    }

    hiprtRay ray;
    ray.origin = {point.x, point.y, 0.0f};
    ray.direction = {0.0f, 0.0f, 1.0f};
    ray.minT = 0.0f;
    ray.maxT = 0.0f;

    hiprtGeomCustomTraversalAnyHit traversal(geom, ray, hiprtTraversalHintDefault, nullptr, table);
    while (traversal.getCurrentState() != hiprtTraversalStateFinished) {
        hiprtHit hit = traversal.getNextHit();
        if (hit.hasHit()) {
            rows[base + hit.primID].contains = 1u;
        }
    }
}
)KERNEL";
}

const char* point_nearest_segment_2d_kernel_source() {
    return R"KERNEL(
#include <hiprt/hiprt_device.h>
#include <hiprt/hiprt_vec.h>

struct RtdlHiprtPoint2DDevice {
    uint32_t id;
    float x;
    float y;
};

struct RtdlHiprtSegmentDevice {
    uint32_t id;
    float x0;
    float y0;
    float x1;
    float y1;
};

struct RtdlHiprtPointSegmentParams {
    float radius;
};

struct RtdlPointNearestSegmentRow {
    uint32_t point_id;
    uint32_t segment_id;
    double distance;
};

__device__ float pointSegmentDistance2D(float px, float py, const RtdlHiprtSegmentDevice& segment) {
    const float vx = segment.x1 - segment.x0;
    const float vy = segment.y1 - segment.y0;
    const float wx = px - segment.x0;
    const float wy = py - segment.y0;
    const float denom = vx * vx + vy * vy;
    if (denom < 1.0e-12f) {
        const float dx = px - segment.x0;
        const float dy = py - segment.y0;
        return sqrtf(dx * dx + dy * dy);
    }
    float t = (wx * vx + wy * vy) / denom;
    t = fminf(1.0f, fmaxf(0.0f, t));
    const float cx = segment.x0 + t * vx;
    const float cy = segment.y0 + t * vy;
    const float dx = px - cx;
    const float dy = py - cy;
    return sqrtf(dx * dx + dy * dy);
}

__device__ bool intersectRtdlPointSegmentDistance2D(const hiprtRay& ray, const void* data, void* payload, hiprtHit& hit) {
    const RtdlHiprtSegmentDevice* segments = reinterpret_cast<const RtdlHiprtSegmentDevice*>(data);
    const RtdlHiprtPointSegmentParams* params = reinterpret_cast<const RtdlHiprtPointSegmentParams*>(payload);
    const RtdlHiprtSegmentDevice segment = segments[hit.primID];
    const float distance = pointSegmentDistance2D(ray.origin.x, ray.origin.y, segment);
    if (distance > params->radius) {
        return false;
    }
    hit.t = distance;
    return true;
}

extern "C" __global__ void RtdlPointNearestSegment2DKernel(
    hiprtGeometry geom,
    const RtdlHiprtPoint2DDevice* points,
    const RtdlHiprtSegmentDevice* segments,
    uint32_t point_count,
    RtdlPointNearestSegmentRow* rows,
    uint32_t* has_row,
    RtdlHiprtPointSegmentParams* params,
    hiprtFuncTable table) {
    const uint32_t index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index >= point_count) {
        return;
    }
    const RtdlHiprtPoint2DDevice point = points[index];
    float best_distance = 3.402823466e+38F;
    uint32_t best_segment_id = 0xFFFFFFFFu;
    bool found = false;

    hiprtRay ray;
    ray.origin = {point.x, point.y, 0.0f};
    ray.direction = {0.0f, 0.0f, 1.0f};
    ray.minT = 0.0f;
    ray.maxT = 0.0f;

    hiprtGeomCustomTraversalAnyHit traversal(geom, ray, hiprtTraversalHintDefault, params, table);
    while (traversal.getCurrentState() != hiprtTraversalStateFinished) {
        hiprtHit hit = traversal.getNextHit();
        if (!hit.hasHit()) {
            continue;
        }
        const RtdlHiprtSegmentDevice segment = segments[hit.primID];
        const float distance = hit.t;
        if (!found || distance < best_distance - 1.0e-7f ||
            (fabsf(distance - best_distance) <= 1.0e-7f && segment.id < best_segment_id)) {
            found = true;
            best_distance = distance;
            best_segment_id = segment.id;
        }
    }

    has_row[index] = found ? 1u : 0u;
    rows[index].point_id = point.id;
    rows[index].segment_id = best_segment_id;
    rows[index].distance = static_cast<double>(best_distance);
}
)KERNEL";
}

const char* segment_polygon_2d_kernel_source() {
    return R"KERNEL(
#include <hiprt/hiprt_device.h>
#include <hiprt/hiprt_vec.h>

struct RtdlHiprtSegmentDevice {
    uint32_t id;
    float x0;
    float y0;
    float x1;
    float y1;
};

struct RtdlHiprtPolygonRefDevice {
    uint32_t id;
    uint32_t vertex_offset;
    uint32_t vertex_count;
};

struct RtdlHiprtVertex2DDevice {
    float x;
    float y;
};

struct RtdlHiprtPipDataDevice {
    const RtdlHiprtPolygonRefDevice* polygons;
    const RtdlHiprtVertex2DDevice* vertices;
};

struct RtdlSegmentPolygonHitCountRow {
    uint32_t segment_id;
    uint32_t hit_count;
};

struct RtdlSegmentPolygonAnyHitRow {
    uint32_t segment_id;
    uint32_t polygon_id;
};

__device__ float orient2D(float ax, float ay, float bx, float by, float cx, float cy) {
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax);
}

__device__ bool pointOnSegment2D(float px, float py, float ax, float ay, float bx, float by) {
    const float eps = 1.0e-6f;
    const float vx = bx - ax;
    const float vy = by - ay;
    const float wx = px - ax;
    const float wy = py - ay;
    const float length_sq = vx * vx + vy * vy;
    if (length_sq <= eps * eps) {
        return fabsf(px - ax) <= eps && fabsf(py - ay) <= eps;
    }
    const float cross = wx * vy - wy * vx;
    if (fabsf(cross) > eps * sqrtf(length_sq)) {
        return false;
    }
    const float dot = wx * vx + wy * vy;
    const float length = sqrtf(length_sq);
    const float along_eps = eps * length;
    return dot >= -along_eps && dot - length_sq <= along_eps;
}

__device__ bool segmentsIntersect2D(float ax, float ay, float bx, float by, float cx, float cy, float dx, float dy) {
    const float eps = 1.0e-6f;
    const float o1 = orient2D(ax, ay, bx, by, cx, cy);
    const float o2 = orient2D(ax, ay, bx, by, dx, dy);
    const float o3 = orient2D(cx, cy, dx, dy, ax, ay);
    const float o4 = orient2D(cx, cy, dx, dy, bx, by);
    if ((o1 > eps && o2 < -eps || o1 < -eps && o2 > eps) &&
        (o3 > eps && o4 < -eps || o3 < -eps && o4 > eps)) {
        return true;
    }
    if (fabsf(o1) <= eps && pointOnSegment2D(cx, cy, ax, ay, bx, by)) return true;
    if (fabsf(o2) <= eps && pointOnSegment2D(dx, dy, ax, ay, bx, by)) return true;
    if (fabsf(o3) <= eps && pointOnSegment2D(ax, ay, cx, cy, dx, dy)) return true;
    if (fabsf(o4) <= eps && pointOnSegment2D(bx, by, cx, cy, dx, dy)) return true;
    return false;
}

__device__ bool pointInPolygon2D(float x, float y, const RtdlHiprtPolygonRefDevice& polygon, const RtdlHiprtVertex2DDevice* vertices) {
    if (polygon.vertex_count < 3u) {
        return false;
    }
    bool inside = false;
    uint32_t prev = polygon.vertex_count - 1u;
    for (uint32_t i = 0; i < polygon.vertex_count; ++i) {
        const RtdlHiprtVertex2DDevice a = vertices[polygon.vertex_offset + prev];
        const RtdlHiprtVertex2DDevice b = vertices[polygon.vertex_offset + i];
        if (pointOnSegment2D(x, y, a.x, a.y, b.x, b.y)) {
            return true;
        }
        const bool crossing = ((b.y > y) != (a.y > y)) &&
            (x <= (a.x - b.x) * (y - b.y) / ((a.y - b.y) == 0.0f ? 1.0e-20f : (a.y - b.y)) + b.x);
        if (crossing) {
            inside = !inside;
        }
        prev = i;
    }
    return inside;
}

__device__ bool segmentHitsPolygon2D(
    float sx0,
    float sy0,
    float sx1,
    float sy1,
    const RtdlHiprtPolygonRefDevice& polygon,
    const RtdlHiprtVertex2DDevice* vertices) {
    if (pointInPolygon2D(sx0, sy0, polygon, vertices) || pointInPolygon2D(sx1, sy1, polygon, vertices)) {
        return true;
    }
    if (polygon.vertex_count < 2u) {
        return false;
    }
    uint32_t prev = polygon.vertex_count - 1u;
    for (uint32_t i = 0; i < polygon.vertex_count; ++i) {
        const RtdlHiprtVertex2DDevice a = vertices[polygon.vertex_offset + prev];
        const RtdlHiprtVertex2DDevice b = vertices[polygon.vertex_offset + i];
        if (segmentsIntersect2D(sx0, sy0, sx1, sy1, a.x, a.y, b.x, b.y)) {
            return true;
        }
        prev = i;
    }
    return false;
}

__device__ bool intersectRtdlSegmentPolygon2D(const hiprtRay& ray, const void* data, void* payload, hiprtHit& hit) {
    const RtdlHiprtPipDataDevice* pip = reinterpret_cast<const RtdlHiprtPipDataDevice*>(data);
    const RtdlHiprtPolygonRefDevice polygon = pip->polygons[hit.primID];
    const float sx0 = ray.origin.x;
    const float sy0 = ray.origin.y;
    const float sx1 = ray.origin.x + ray.direction.x;
    const float sy1 = ray.origin.y + ray.direction.y;
    if (!segmentHitsPolygon2D(sx0, sy0, sx1, sy1, polygon, pip->vertices)) {
        return false;
    }
    hit.t = 0.0f;
    return true;
}

extern "C" __global__ void RtdlSegmentPolygonHitcount2DKernel(
    hiprtGeometry geom,
    const RtdlHiprtSegmentDevice* segments,
    uint32_t segment_count,
    RtdlSegmentPolygonHitCountRow* rows,
    hiprtFuncTable table) {
    const uint32_t index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index >= segment_count) {
        return;
    }
    const RtdlHiprtSegmentDevice segment = segments[index];
    uint32_t hit_count = 0u;

    hiprtRay ray;
    ray.origin = {segment.x0, segment.y0, 0.0f};
    ray.direction = {segment.x1 - segment.x0, segment.y1 - segment.y0, 0.0f};
    ray.minT = 0.0f;
    ray.maxT = 1.0f;

    hiprtGeomCustomTraversalAnyHit traversal(geom, ray, hiprtTraversalHintDefault, nullptr, table);
    while (traversal.getCurrentState() != hiprtTraversalStateFinished) {
        hiprtHit hit = traversal.getNextHit();
        if (hit.hasHit()) {
            ++hit_count;
        }
    }
    rows[index].segment_id = segment.id;
    rows[index].hit_count = hit_count;
}

extern "C" __global__ void RtdlSegmentPolygonAnyhit2DKernel(
    hiprtGeometry geom,
    const RtdlHiprtSegmentDevice* segments,
    const RtdlHiprtPolygonRefDevice* polygons,
    uint32_t segment_count,
    uint32_t polygon_count,
    RtdlSegmentPolygonAnyHitRow* rows,
    uint32_t* counts,
    hiprtFuncTable table) {
    const uint32_t index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index >= segment_count) {
        return;
    }
    const RtdlHiprtSegmentDevice segment = segments[index];
    uint32_t count = 0u;

    hiprtRay ray;
    ray.origin = {segment.x0, segment.y0, 0.0f};
    ray.direction = {segment.x1 - segment.x0, segment.y1 - segment.y0, 0.0f};
    ray.minT = 0.0f;
    ray.maxT = 1.0f;

    hiprtGeomCustomTraversalAnyHit traversal(geom, ray, hiprtTraversalHintDefault, nullptr, table);
    while (traversal.getCurrentState() != hiprtTraversalStateFinished) {
        hiprtHit hit = traversal.getNextHit();
        if (hit.hasHit() && count < polygon_count) {
            const uint32_t out_index = index * polygon_count + count;
            rows[out_index].segment_id = segment.id;
            rows[out_index].polygon_id = polygons[hit.primID].id;
            ++count;
        }
    }
    counts[index] = count;
}
)KERNEL";
}

const char* fixed_radius_neighbors_3d_kernel_source() {
    return R"KERNEL(
#include <hiprt/hiprt_device.h>
#include <hiprt/hiprt_vec.h>

struct RtdlHiprtPoint3DDevice {
    uint32_t id;
    float x;
    float y;
    float z;
};

struct RtdlFixedRadiusNeighborRow {
    uint32_t query_id;
    uint32_t neighbor_id;
    double distance;
};

struct RtdlHiprtFixedRadiusParams {
    float radius;
};

__device__ bool intersectRtdlPointRadius3D(const hiprtRay& ray, const void* data, void* payload, hiprtHit& hit) {
    const RtdlHiprtPoint3DDevice* points = reinterpret_cast<const RtdlHiprtPoint3DDevice*>(data);
    const RtdlHiprtFixedRadiusParams* params = reinterpret_cast<const RtdlHiprtFixedRadiusParams*>(payload);
    const RtdlHiprtPoint3DDevice point = points[hit.primID];
    const float dx = ray.origin.x - point.x;
    const float dy = ray.origin.y - point.y;
    const float dz = ray.origin.z - point.z;
    const float dist_sq = dx * dx + dy * dy + dz * dz;
    const float radius = params->radius;
    if (dist_sq > radius * radius) {
        return false;
    }
    hit.t = sqrtf(dist_sq);
    return true;
}

extern "C" __global__ void RtdlFixedRadiusNeighbors3DKernel(
    hiprtGeometry geom,
    const RtdlHiprtPoint3DDevice* queries,
    const RtdlHiprtPoint3DDevice* search_points,
    uint32_t query_count,
    uint32_t k_max,
    RtdlFixedRadiusNeighborRow* rows,
    uint32_t* counts,
    RtdlHiprtFixedRadiusParams* params,
    hiprtFuncTable table) {
    const uint32_t index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index >= query_count) {
        return;
    }
    if (k_max > 64u) {
        counts[index] = 0u;
        return;
    }

    const RtdlHiprtPoint3DDevice query = queries[index];
    float best_dist[64];
    uint32_t best_id[64];
    uint32_t count = 0u;
    for (uint32_t i = 0; i < k_max; ++i) {
        best_dist[i] = 3.402823466e+38F;
        best_id[i] = 0xFFFFFFFFu;
    }

    hiprtRay ray;
    ray.origin = {query.x, query.y, query.z};
    ray.direction = {0.0f, 0.0f, 1.0f};
    ray.minT = 0.0f;
    ray.maxT = 0.0f;

    hiprtGeomCustomTraversalAnyHit traversal(geom, ray, hiprtTraversalHintDefault, params, table);
    while (traversal.getCurrentState() != hiprtTraversalStateFinished) {
        hiprtHit hit = traversal.getNextHit();
        if (!hit.hasHit()) {
            continue;
        }
        const RtdlHiprtPoint3DDevice neighbor = search_points[hit.primID];
        const float dist = hit.t;
        uint32_t insert_at = count < k_max ? count : k_max;
        for (uint32_t pos = 0; pos < count && pos < k_max; ++pos) {
            if (dist < best_dist[pos] || (dist == best_dist[pos] && neighbor.id < best_id[pos])) {
                insert_at = pos;
                break;
            }
        }
        if (insert_at >= k_max) {
            continue;
        }
        const uint32_t limit = count < k_max ? count : k_max - 1u;
        for (uint32_t pos = limit; pos > insert_at; --pos) {
            best_dist[pos] = best_dist[pos - 1u];
            best_id[pos] = best_id[pos - 1u];
        }
        best_dist[insert_at] = dist;
        best_id[insert_at] = neighbor.id;
        if (count < k_max) {
            ++count;
        }
    }

    counts[index] = count;
    const uint32_t base = index * k_max;
    for (uint32_t rank = 0; rank < count; ++rank) {
        rows[base + rank].query_id = query.id;
        rows[base + rank].neighbor_id = best_id[rank];
        rows[base + rank].distance = static_cast<double>(best_dist[rank]);
    }
}
)KERNEL";
}

const char* overlay_2d_kernel_source() {
    return R"KERNEL(
#include <hiprt/hiprt_device.h>
#include <hiprt/hiprt_vec.h>

struct RtdlHiprtPolygonRefDevice {
    uint32_t id;
    uint32_t vertex_offset;
    uint32_t vertex_count;
};

struct RtdlHiprtVertex2DDevice {
    float x;
    float y;
};

struct RtdlOverlayRow {
    uint32_t left_polygon_id;
    uint32_t right_polygon_id;
    uint32_t requires_lsi;
    uint32_t requires_pip;
};

__device__ bool pointOnSegment2D(float px, float py, float ax, float ay, float bx, float by) {
    const float eps = 1.0e-6f;
    const float vx = bx - ax;
    const float vy = by - ay;
    const float wx = px - ax;
    const float wy = py - ay;
    const float length_sq = vx * vx + vy * vy;
    if (length_sq <= eps * eps) {
        return fabsf(px - ax) <= eps && fabsf(py - ay) <= eps;
    }
    const float cross = wx * vy - wy * vx;
    if (fabsf(cross) > eps * sqrtf(length_sq)) {
        return false;
    }
    const float dot = wx * vx + wy * vy;
    const float length = sqrtf(length_sq);
    const float along_eps = eps * length;
    return dot >= -along_eps && dot - length_sq <= along_eps;
}

__device__ bool pointInPolygon2D(float x, float y, const RtdlHiprtPolygonRefDevice& polygon, const RtdlHiprtVertex2DDevice* vertices) {
    if (polygon.vertex_count < 3u) {
        return false;
    }
    bool inside = false;
    uint32_t prev = polygon.vertex_count - 1u;
    for (uint32_t i = 0; i < polygon.vertex_count; ++i) {
        const RtdlHiprtVertex2DDevice a = vertices[polygon.vertex_offset + prev];
        const RtdlHiprtVertex2DDevice b = vertices[polygon.vertex_offset + i];
        if (pointOnSegment2D(x, y, a.x, a.y, b.x, b.y)) {
            return true;
        }
        const bool crossing = ((b.y > y) != (a.y > y)) &&
            (x <= (a.x - b.x) * (y - b.y) / ((a.y - b.y) == 0.0f ? 1.0e-20f : (a.y - b.y)) + b.x);
        if (crossing) {
            inside = !inside;
        }
        prev = i;
    }
    return inside;
}

__device__ float orient2D(float ax, float ay, float bx, float by, float cx, float cy) {
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax);
}

__device__ bool segmentsIntersect2D(float ax, float ay, float bx, float by, float cx, float cy, float dx, float dy) {
    const float eps = 1.0e-6f;
    const float o1 = orient2D(ax, ay, bx, by, cx, cy);
    const float o2 = orient2D(ax, ay, bx, by, dx, dy);
    const float o3 = orient2D(cx, cy, dx, dy, ax, ay);
    const float o4 = orient2D(cx, cy, dx, dy, bx, by);
    if ((o1 > eps && o2 < -eps || o1 < -eps && o2 > eps) &&
        (o3 > eps && o4 < -eps || o3 < -eps && o4 > eps)) {
        return true;
    }
    if (fabsf(o1) <= eps && pointOnSegment2D(cx, cy, ax, ay, bx, by)) return true;
    if (fabsf(o2) <= eps && pointOnSegment2D(dx, dy, ax, ay, bx, by)) return true;
    if (fabsf(o3) <= eps && pointOnSegment2D(ax, ay, cx, cy, dx, dy)) return true;
    if (fabsf(o4) <= eps && pointOnSegment2D(bx, by, cx, cy, dx, dy)) return true;
    return false;
}

__device__ bool polygonsHaveLsi2D(
    const RtdlHiprtPolygonRefDevice& left,
    const RtdlHiprtVertex2DDevice* left_vertices,
    const RtdlHiprtPolygonRefDevice& right,
    const RtdlHiprtVertex2DDevice* right_vertices) {
    if (left.vertex_count < 2u || right.vertex_count < 2u) {
        return false;
    }
    uint32_t left_prev = left.vertex_count - 1u;
    for (uint32_t li = 0; li < left.vertex_count; ++li) {
        const RtdlHiprtVertex2DDevice la = left_vertices[left.vertex_offset + left_prev];
        const RtdlHiprtVertex2DDevice lb = left_vertices[left.vertex_offset + li];
        uint32_t right_prev = right.vertex_count - 1u;
        for (uint32_t ri = 0; ri < right.vertex_count; ++ri) {
            const RtdlHiprtVertex2DDevice ra = right_vertices[right.vertex_offset + right_prev];
            const RtdlHiprtVertex2DDevice rb = right_vertices[right.vertex_offset + ri];
            if (segmentsIntersect2D(la.x, la.y, lb.x, lb.y, ra.x, ra.y, rb.x, rb.y)) {
                return true;
            }
            right_prev = ri;
        }
        left_prev = li;
    }
    return false;
}

__device__ bool intersectRtdlOverlayCandidate2D(const hiprtRay& ray, const void* data, void* payload, hiprtHit& hit) {
    hit.t = 0.0f;
    return true;
}

extern "C" __global__ void RtdlOverlay2DKernel(
    hiprtGeometry geom,
    const RtdlHiprtPolygonRefDevice* left_polygons,
    const RtdlHiprtVertex2DDevice* left_vertices,
    const RtdlHiprtPolygonRefDevice* right_polygons,
    const RtdlHiprtVertex2DDevice* right_vertices,
    uint32_t left_count,
    uint32_t right_count,
    RtdlOverlayRow* rows,
    hiprtFuncTable table) {
    const uint32_t left_index = blockIdx.x * blockDim.x + threadIdx.x;
    if (left_index >= left_count) {
        return;
    }
    const RtdlHiprtPolygonRefDevice left = left_polygons[left_index];
    const RtdlHiprtVertex2DDevice left_first = left_vertices[left.vertex_offset];

    const uint32_t base = left_index * right_count;
    for (uint32_t right_index = 0; right_index < right_count; ++right_index) {
        rows[base + right_index].left_polygon_id = left.id;
        rows[base + right_index].right_polygon_id = right_polygons[right_index].id;
        rows[base + right_index].requires_lsi = 0u;
        rows[base + right_index].requires_pip = 0u;
    }

    hiprtRay ray;
    ray.origin = {left_first.x, left_first.y, 0.0f};
    ray.direction = {0.0f, 0.0f, 1.0f};
    ray.minT = 0.0f;
    ray.maxT = 0.0f;

    hiprtGeomCustomTraversalAnyHit traversal(geom, ray, hiprtTraversalHintDefault, nullptr, table);
    while (traversal.getCurrentState() != hiprtTraversalStateFinished) {
        hiprtHit hit = traversal.getNextHit();
        if (!hit.hasHit()) {
            continue;
        }
        const uint32_t right_index = hit.primID;
        if (right_index >= right_count) {
            continue;
        }
        const RtdlHiprtPolygonRefDevice right = right_polygons[right_index];
        const RtdlHiprtVertex2DDevice right_first = right_vertices[right.vertex_offset];
        RtdlOverlayRow& row = rows[base + right_index];
        row.requires_lsi = polygonsHaveLsi2D(left, left_vertices, right, right_vertices) ? 1u : 0u;
        const bool left_in_right = pointInPolygon2D(left_first.x, left_first.y, right, right_vertices);
        const bool right_in_left = pointInPolygon2D(right_first.x, right_first.y, left, left_vertices);
        row.requires_pip = (left_in_right || right_in_left) ? 1u : 0u;
    }
}
)KERNEL";
}

const char* fixed_radius_neighbors_2d_kernel_source() {
    return R"KERNEL(
#include <hiprt/hiprt_device.h>
#include <hiprt/hiprt_vec.h>

struct RtdlHiprtPoint2DDevice {
    uint32_t id;
    float x;
    float y;
};

struct RtdlFixedRadiusNeighborRow {
    uint32_t query_id;
    uint32_t neighbor_id;
    double distance;
};

struct RtdlHiprtFixedRadiusParams {
    float radius;
};

__device__ bool intersectRtdlPointRadius2D(const hiprtRay& ray, const void* data, void* payload, hiprtHit& hit) {
    const RtdlHiprtPoint2DDevice* points = reinterpret_cast<const RtdlHiprtPoint2DDevice*>(data);
    const RtdlHiprtFixedRadiusParams* params = reinterpret_cast<const RtdlHiprtFixedRadiusParams*>(payload);
    const RtdlHiprtPoint2DDevice point = points[hit.primID];
    const float dx = ray.origin.x - point.x;
    const float dy = ray.origin.y - point.y;
    const float dist_sq = dx * dx + dy * dy;
    const float radius = params->radius;
    if (dist_sq > radius * radius) {
        return false;
    }
    hit.t = sqrtf(dist_sq);
    return true;
}

extern "C" __global__ void RtdlFixedRadiusNeighbors2DKernel(
    hiprtGeometry geom,
    const RtdlHiprtPoint2DDevice* queries,
    const RtdlHiprtPoint2DDevice* search_points,
    uint32_t query_count,
    uint32_t k_max,
    RtdlFixedRadiusNeighborRow* rows,
    uint32_t* counts,
    RtdlHiprtFixedRadiusParams* params,
    hiprtFuncTable table) {
    const uint32_t index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index >= query_count) {
        return;
    }
    if (k_max > 64u) {
        counts[index] = 0u;
        return;
    }

    const RtdlHiprtPoint2DDevice query = queries[index];
    float best_dist[64];
    uint32_t best_id[64];
    uint32_t count = 0u;
    for (uint32_t i = 0; i < k_max; ++i) {
        best_dist[i] = 3.402823466e+38F;
        best_id[i] = 0xFFFFFFFFu;
    }

    hiprtRay ray;
    ray.origin = {query.x, query.y, 0.0f};
    ray.direction = {0.0f, 0.0f, 1.0f};
    ray.minT = 0.0f;
    ray.maxT = 0.0f;

    hiprtGeomCustomTraversalAnyHit traversal(geom, ray, hiprtTraversalHintDefault, params, table);
    while (traversal.getCurrentState() != hiprtTraversalStateFinished) {
        hiprtHit hit = traversal.getNextHit();
        if (!hit.hasHit()) {
            continue;
        }
        const RtdlHiprtPoint2DDevice neighbor = search_points[hit.primID];
        const float dist = hit.t;
        uint32_t insert_at = count < k_max ? count : k_max;
        for (uint32_t pos = 0; pos < count && pos < k_max; ++pos) {
            if (dist < best_dist[pos] || (dist == best_dist[pos] && neighbor.id < best_id[pos])) {
                insert_at = pos;
                break;
            }
        }
        if (insert_at >= k_max) {
            continue;
        }
        const uint32_t limit = count < k_max ? count : k_max - 1u;
        for (uint32_t pos = limit; pos > insert_at; --pos) {
            best_dist[pos] = best_dist[pos - 1u];
            best_id[pos] = best_id[pos - 1u];
        }
        best_dist[insert_at] = dist;
        best_id[insert_at] = neighbor.id;
        if (count < k_max) {
            ++count;
        }
    }

    counts[index] = count;
    const uint32_t base = index * k_max;
    for (uint32_t rank = 0; rank < count; ++rank) {
        rows[base + rank].query_id = query.id;
        rows[base + rank].neighbor_id = best_id[rank];
        rows[base + rank].distance = static_cast<double>(best_dist[rank]);
    }
}
)KERNEL";
}

const char* bfs_expand_kernel_source() {
    return R"KERNEL(
#include <hiprt/hiprt_device.h>
#include <hiprt/hiprt_vec.h>

struct RtdlFrontierVertex {
    uint32_t vertex_id;
    uint32_t level;
};

struct RtdlBfsRow {
    uint32_t src_vertex;
    uint32_t dst_vertex;
    uint32_t level;
};

struct RtdlHiprtGraphEdgeDevice {
    uint32_t src;
    uint32_t dst;
};

__device__ bool intersectRtdlGraphEdgeBySource(const hiprtRay& ray, const void* data, void* payload, hiprtHit& hit) {
    hit.t = 0.0f;
    return true;
}

__device__ bool containsVertex(const uint32_t* values, uint32_t count, uint32_t vertex) {
    for (uint32_t i = 0; i < count; ++i) {
        if (values[i] == vertex) {
            return true;
        }
    }
    return false;
}

extern "C" __global__ void RtdlBfsExpandKernel(
    hiprtGeometry geom,
    const RtdlFrontierVertex* frontier,
    uint32_t frontier_count,
    const uint32_t* visited,
    uint32_t visited_count,
    const RtdlHiprtGraphEdgeDevice* edges,
    uint32_t edge_count,
    uint32_t* discovered,
    uint32_t vertex_count,
    uint32_t dedupe,
    RtdlBfsRow* rows,
    uint32_t* row_count,
    hiprtFuncTable table) {
    if (dedupe != 0u) {
        if (blockIdx.x != 0u || threadIdx.x != 0u) {
            return;
        }
        for (uint32_t frontier_index = 0; frontier_index < frontier_count; ++frontier_index) {
            const RtdlFrontierVertex item = frontier[frontier_index];
            hiprtRay ray;
            ray.origin = {static_cast<float>(item.vertex_id), 0.0f, -1.0f};
            ray.direction = {0.0f, 0.0f, 1.0f};
            ray.minT = 0.0f;
            ray.maxT = 2.0f;

            hiprtGeomCustomTraversalAnyHit traversal(geom, ray, hiprtTraversalHintDefault, nullptr, table);
            while (traversal.getCurrentState() != hiprtTraversalStateFinished) {
                hiprtHit hit = traversal.getNextHit();
                if (!hit.hasHit() || hit.primID >= edge_count) {
                    continue;
                }
                const RtdlHiprtGraphEdgeDevice edge = edges[hit.primID];
                if (edge.src != item.vertex_id) {
                    continue;
                }
                if (containsVertex(visited, visited_count, edge.dst)) {
                    continue;
                }
                if (edge.dst < vertex_count) {
                    if (atomicCAS(&discovered[edge.dst], 0u, 1u) != 0u) {
                        continue;
                    }
                }
                const uint32_t out_index = atomicAdd(row_count, 1u);
                rows[out_index].src_vertex = edge.src;
                rows[out_index].dst_vertex = edge.dst;
                rows[out_index].level = item.level + 1u;
            }
        }
        return;
    }

    const uint32_t frontier_index = blockIdx.x * blockDim.x + threadIdx.x;
    if (frontier_index >= frontier_count) {
        return;
    }
    const RtdlFrontierVertex item = frontier[frontier_index];
    hiprtRay ray;
    ray.origin = {static_cast<float>(item.vertex_id), 0.0f, -1.0f};
    ray.direction = {0.0f, 0.0f, 1.0f};
    ray.minT = 0.0f;
    ray.maxT = 2.0f;

    hiprtGeomCustomTraversalAnyHit traversal(geom, ray, hiprtTraversalHintDefault, nullptr, table);
    while (traversal.getCurrentState() != hiprtTraversalStateFinished) {
        hiprtHit hit = traversal.getNextHit();
        if (!hit.hasHit() || hit.primID >= edge_count) {
            continue;
        }
        const RtdlHiprtGraphEdgeDevice edge = edges[hit.primID];
        if (edge.src != item.vertex_id) {
            continue;
        }
        if (containsVertex(visited, visited_count, edge.dst)) {
            continue;
        }
        const uint32_t out_index = atomicAdd(row_count, 1u);
        rows[out_index].src_vertex = edge.src;
        rows[out_index].dst_vertex = edge.dst;
        rows[out_index].level = item.level + 1u;
    }
}
)KERNEL";
}

const char* triangle_probe_kernel_source() {
    return R"KERNEL(
#include <hiprt/hiprt_device.h>
#include <hiprt/hiprt_vec.h>

struct RtdlEdgeSeed {
    uint32_t u;
    uint32_t v;
};

struct RtdlHiprtGraphEdgeDevice {
    uint32_t src;
    uint32_t dst;
};

struct RtdlHiprtTriangleCandidateRow {
    uint32_t seed_index;
    uint32_t u;
    uint32_t v;
    uint32_t w;
};

__device__ bool intersectRtdlTriangleGraphEdgeBySource(const hiprtRay& ray, const void* data, void* payload, hiprtHit& hit) {
    hit.t = 0.0f;
    return true;
}

__device__ bool hasGraphEdge(
    const uint32_t* row_offsets,
    const uint32_t* column_indices,
    uint32_t src,
    uint32_t dst) {
    const uint32_t begin = row_offsets[src];
    const uint32_t end = row_offsets[src + 1u];
    for (uint32_t index = begin; index < end; ++index) {
        if (column_indices[index] == dst) {
            return true;
        }
    }
    return false;
}

extern "C" __global__ void RtdlTriangleProbeKernel(
    hiprtGeometry geom,
    const RtdlEdgeSeed* seeds,
    uint32_t seed_count,
    const uint32_t* row_offsets,
    const uint32_t* column_indices,
    const RtdlHiprtGraphEdgeDevice* edges,
    uint32_t edge_count,
    uint32_t vertex_count,
    uint32_t enforce_id_ascending,
    RtdlHiprtTriangleCandidateRow* rows,
    uint32_t* row_count,
    hiprtFuncTable table) {
    const uint32_t seed_index = blockIdx.x * blockDim.x + threadIdx.x;
    if (seed_index >= seed_count) {
        return;
    }
    const RtdlEdgeSeed seed = seeds[seed_index];
    const uint32_t u = seed.u;
    const uint32_t v = seed.v;
    if (u >= vertex_count || v >= vertex_count || u == v) {
        return;
    }
    if (enforce_id_ascending != 0u && !(u < v)) {
        return;
    }

    hiprtRay ray;
    ray.origin = {static_cast<float>(u), 0.0f, -1.0f};
    ray.direction = {0.0f, 0.0f, 1.0f};
    ray.minT = 0.0f;
    ray.maxT = 2.0f;

    hiprtGeomCustomTraversalAnyHit traversal(geom, ray, hiprtTraversalHintDefault, nullptr, table);
    while (traversal.getCurrentState() != hiprtTraversalStateFinished) {
        hiprtHit hit = traversal.getNextHit();
        if (!hit.hasHit() || hit.primID >= edge_count) {
            continue;
        }
        const RtdlHiprtGraphEdgeDevice edge = edges[hit.primID];
        if (edge.src != u) {
            continue;
        }
        const uint32_t w = edge.dst;
        if (enforce_id_ascending != 0u && !(v < w)) {
            continue;
        }
        if (!hasGraphEdge(row_offsets, column_indices, v, w)) {
            continue;
        }
        const uint32_t out_index = atomicAdd(row_count, 1u);
        rows[out_index].seed_index = seed_index;
        rows[out_index].u = u;
        rows[out_index].v = v;
        rows[out_index].w = w;
    }
}
)KERNEL";
}

const char* db_match_kernel_source() {
    return R"KERNEL(
#include <hiprt/hiprt_device.h>
#include <hiprt/hiprt_vec.h>

struct RtdlDbScalar {
    uint32_t kind;
    int64_t int_value;
    double double_value;
    const char* string_value;
};

struct RtdlHiprtDbClauseDevice {
    uint32_t field_index;
    uint32_t op;
    RtdlDbScalar value;
    RtdlDbScalar value_hi;
};

__device__ bool intersectRtdlDbRowAabb(const hiprtRay& ray, const void* data, void* payload, hiprtHit& hit) {
    hit.t = 0.0f;
    return true;
}

__device__ double dbScalarAsDouble(const RtdlDbScalar& value) {
    if (value.kind == 2u) {
        return value.double_value;
    }
    return static_cast<double>(value.int_value);
}

__device__ int dbCompareScalar(const RtdlDbScalar& left, const RtdlDbScalar& right) {
    const double lhs = dbScalarAsDouble(left);
    const double rhs = dbScalarAsDouble(right);
    if (lhs < rhs) {
        return -1;
    }
    if (lhs > rhs) {
        return 1;
    }
    return 0;
}

__device__ bool dbClauseMatches(const RtdlHiprtDbClauseDevice& clause, const RtdlDbScalar& value) {
    const int cmp_lo = dbCompareScalar(value, clause.value);
    if (clause.op == 1u) {
        return cmp_lo == 0;
    }
    if (clause.op == 2u) {
        return cmp_lo < 0;
    }
    if (clause.op == 3u) {
        return cmp_lo <= 0;
    }
    if (clause.op == 4u) {
        return cmp_lo > 0;
    }
    if (clause.op == 5u) {
        return cmp_lo >= 0;
    }
    if (clause.op == 6u) {
        return cmp_lo >= 0 && dbCompareScalar(value, clause.value_hi) <= 0;
    }
    return false;
}

__device__ bool dbRowMatches(
    const RtdlDbScalar* row_values,
    uint32_t row_index,
    uint32_t field_count,
    const RtdlHiprtDbClauseDevice* clauses,
    uint32_t clause_count) {
    for (uint32_t clause_index = 0; clause_index < clause_count; ++clause_index) {
        const RtdlHiprtDbClauseDevice clause = clauses[clause_index];
        const RtdlDbScalar value = row_values[row_index * field_count + clause.field_index];
        if (!dbClauseMatches(clause, value)) {
            return false;
        }
    }
    return true;
}

extern "C" __global__ void RtdlDbMatchKernel(
    hiprtGeometry geom,
    const RtdlDbScalar* row_values,
    uint32_t row_count,
    uint32_t field_count,
    const RtdlHiprtDbClauseDevice* clauses,
    uint32_t clause_count,
    uint32_t* matched_indices,
    uint32_t* matched_count,
    hiprtFuncTable table) {
    const uint32_t row_index = blockIdx.x * blockDim.x + threadIdx.x;
    if (row_index >= row_count) {
        return;
    }
    hiprtRay ray;
    ray.origin = {static_cast<float>(row_index), 0.0f, -1.0f};
    ray.direction = {0.0f, 0.0f, 1.0f};
    ray.minT = 0.0f;
    ray.maxT = 2.0f;

    hiprtGeomCustomTraversalAnyHit traversal(geom, ray, hiprtTraversalHintDefault, nullptr, table);
    while (traversal.getCurrentState() != hiprtTraversalStateFinished) {
        hiprtHit hit = traversal.getNextHit();
        if (!hit.hasHit() || hit.primID >= row_count) {
            continue;
        }
        if (hit.primID != row_index) {
            continue;
        }
        if (!dbRowMatches(row_values, hit.primID, field_count, clauses, clause_count)) {
            continue;
        }
        const uint32_t out_index = atomicAdd(matched_count, 1u);
        matched_indices[out_index] = hit.primID;
    }
}
)KERNEL";
}

oroFunction build_trace_kernel_from_source(
    hiprtContext context,
    const char* source,
    const char* module_name,
    const char* function_name,
    hiprtFuncNameSet* func_name_sets = nullptr,
    uint32_t num_geom_types = 0,
    uint32_t num_ray_types = 1) {
    std::vector<const char*> options;
    options.push_back("--device-c");
    options.push_back("-arch=compute_60");
    options.push_back("-std=c++17");
    options.push_back("-I" RTDL_HIPRT_INCLUDE_DIR);

    orortcProgram program{};
    check_orortc(
        "orortcCreateProgram",
        orortcCreateProgram(&program, source, module_name, 0, nullptr, nullptr));
    try {
        check_orortc("orortcAddNameExpression", orortcAddNameExpression(program, function_name));
        orortcResult compile_result = orortcCompileProgram(program, static_cast<int>(options.size()), options.data());
        if (compile_result != ORORTC_SUCCESS) {
            size_t log_size = 0;
            orortcGetProgramLogSize(program, &log_size);
            std::string log(log_size, '\0');
            if (log_size > 0) {
                orortcGetProgramLog(program, log.data());
            }
            throw std::runtime_error(orortc_error_message("orortcCompileProgram", compile_result) + ": " + log);
        }
        size_t code_size = 0;
        check_orortc("orortcGetCodeSize", orortcGetCodeSize(program, &code_size));
        std::string code(code_size, '\0');
        check_orortc("orortcGetCode", orortcGetCode(program, code.data()));

        hiprtApiFunction api_function{};
        check_hiprt(
            "hiprtBuildTraceKernelsFromBitcode",
            hiprtBuildTraceKernelsFromBitcode(
                context,
                1,
                &function_name,
                module_name,
                code.data(),
                code.size(),
                num_geom_types,
                num_ray_types,
                func_name_sets,
                &api_function,
                false));
        check_orortc("orortcDestroyProgram", orortcDestroyProgram(&program));
        return *reinterpret_cast<oroFunction*>(&api_function);
    } catch (...) {
        orortcDestroyProgram(&program);
        throw;
    }
}

oroFunction build_trace_kernel(hiprtContext context, const char* function_name) {
    return build_trace_kernel_from_source(
        context,
        ray_hitcount_kernel_source(),
        "rtdl_hiprt_ray_hitcount.cu",
        function_name);
}

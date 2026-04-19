#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <functional>
#include <limits>
#include <map>
#include <memory>
#include <unordered_map>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include <hiprt/hiprt.h>
#include <Orochi/Orochi.h>

namespace {

std::string oro_error_message(const char* op, oroError err);
std::string oro_initialize_error_message(int err);
std::string hiprt_error_message(const char* op, hiprtError err);

struct RtdlTriangle3D {
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
} __attribute__((packed));

struct RtdlTriangle {
    uint32_t id;
    double x0;
    double y0;
    double x1;
    double y1;
    double x2;
    double y2;
};

struct RtdlRay2D {
    uint32_t id;
    double ox;
    double oy;
    double dx;
    double dy;
    double tmax;
} __attribute__((packed));

struct RtdlRay3D {
    uint32_t id;
    double ox;
    double oy;
    double oz;
    double dx;
    double dy;
    double dz;
    double tmax;
} __attribute__((packed));

struct RtdlRayHitCountRow {
    uint32_t ray_id;
    uint32_t hit_count;
};

struct RtdlSegment {
    uint32_t id;
    double x0;
    double y0;
    double x1;
    double y1;
};

struct RtdlPoint {
    uint32_t id;
    double x;
    double y;
};

struct RtdlPolygonRef {
    uint32_t id;
    uint32_t vertex_offset;
    uint32_t vertex_count;
};

struct RtdlLsiRow {
    uint32_t left_id;
    uint32_t right_id;
    double intersection_point_x;
    double intersection_point_y;
};

struct RtdlPipRow {
    uint32_t point_id;
    uint32_t polygon_id;
    uint32_t contains;
};

struct RtdlOverlayRow {
    uint32_t left_polygon_id;
    uint32_t right_polygon_id;
    uint32_t requires_lsi;
    uint32_t requires_pip;
};

struct RtdlPointNearestSegmentRow {
    uint32_t point_id;
    uint32_t segment_id;
    double distance;
};

struct RtdlSegmentPolygonHitCountRow {
    uint32_t segment_id;
    uint32_t hit_count;
};

struct RtdlSegmentPolygonAnyHitRow {
    uint32_t segment_id;
    uint32_t polygon_id;
};

struct RtdlPoint3D {
    uint32_t id;
    double x;
    double y;
    double z;
};

struct RtdlFixedRadiusNeighborRow {
    uint32_t query_id;
    uint32_t neighbor_id;
    double distance;
};

struct RtdlFrontierVertex {
    uint32_t vertex_id;
    uint32_t level;
};

struct RtdlBfsRow {
    uint32_t src_vertex;
    uint32_t dst_vertex;
    uint32_t level;
};

struct RtdlEdgeSeed {
    uint32_t u;
    uint32_t v;
};

struct RtdlTriangleRow {
    uint32_t u;
    uint32_t v;
    uint32_t w;
};

struct RtdlDbField {
    const char* name;
    uint32_t kind;
};

struct RtdlDbScalar {
    uint32_t kind;
    int64_t int_value;
    double double_value;
    const char* string_value;
};

struct RtdlDbClause {
    const char* field;
    uint32_t op;
    RtdlDbScalar value;
    RtdlDbScalar value_hi;
};

struct RtdlDbRowIdRow {
    uint32_t row_id;
};

struct RtdlDbGroupedCountRow {
    int64_t group_key;
    int64_t count;
};

struct RtdlDbGroupedSumRow {
    int64_t group_key;
    double sum;
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

struct RtdlHiprtDbClauseDevice {
    uint32_t field_index;
    uint32_t op;
    RtdlDbScalar value;
    RtdlDbScalar value_hi;
};

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

struct RtdlHiprtSegmentDevice {
    uint32_t id;
    float x0;
    float y0;
    float x1;
    float y1;
};

struct RtdlHiprtPoint3DDevice {
    uint32_t id;
    float x;
    float y;
    float z;
};

struct RtdlHiprtFixedRadiusParams {
    float radius;
};

struct RtdlHiprtPointSegmentParams {
    float radius;
};

struct RtdlHiprtAabb {
    hiprtFloat4 min;
    hiprtFloat4 max;
};

constexpr uint32_t RTDL_DB_KIND_INT64 = 1u;
constexpr uint32_t RTDL_DB_KIND_FLOAT64 = 2u;
constexpr uint32_t RTDL_DB_KIND_BOOL = 3u;
constexpr uint32_t RTDL_DB_OP_EQ = 1u;
constexpr uint32_t RTDL_DB_OP_LT = 2u;
constexpr uint32_t RTDL_DB_OP_LE = 3u;
constexpr uint32_t RTDL_DB_OP_GT = 4u;
constexpr uint32_t RTDL_DB_OP_GE = 5u;
constexpr uint32_t RTDL_DB_OP_BETWEEN = 6u;

struct HiprtRuntime {
    oroDevice device{};
    oroCtx ctx{};
    hiprtContext context{};

    ~HiprtRuntime() {
        if (context != nullptr) {
            hiprtDestroyContext(context);
        }
        if (ctx != nullptr) {
            oroCtxDestroy(ctx);
        }
    }

    HiprtRuntime(const HiprtRuntime&) = delete;
    HiprtRuntime& operator=(const HiprtRuntime&) = delete;
    HiprtRuntime(HiprtRuntime&& other) noexcept : device(other.device), ctx(other.ctx), context(other.context) {
        other.ctx = nullptr;
        other.context = nullptr;
    }
    HiprtRuntime& operator=(HiprtRuntime&& other) noexcept {
        if (this != &other) {
            if (context != nullptr) {
                hiprtDestroyContext(context);
            }
            if (ctx != nullptr) {
                oroCtxDestroy(ctx);
            }
            device = other.device;
            ctx = other.ctx;
            context = other.context;
            other.ctx = nullptr;
            other.context = nullptr;
        }
        return *this;
    }
    HiprtRuntime() = default;
};

class DeviceAllocation {
  public:
    DeviceAllocation() = default;
    explicit DeviceAllocation(size_t bytes) {
        if (bytes == 0) {
            return;
        }
        oroError err = oroMalloc(reinterpret_cast<oroDeviceptr*>(&ptr_), bytes);
        if (err != oroSuccess) {
            throw std::runtime_error(oro_error_message("oroMalloc", err));
        }
    }
    ~DeviceAllocation() {
        if (ptr_ != nullptr) {
            oroFree(reinterpret_cast<oroDeviceptr>(ptr_));
        }
    }
    DeviceAllocation(const DeviceAllocation&) = delete;
    DeviceAllocation& operator=(const DeviceAllocation&) = delete;
    DeviceAllocation(DeviceAllocation&& other) noexcept : ptr_(other.ptr_) { other.ptr_ = nullptr; }
    DeviceAllocation& operator=(DeviceAllocation&& other) noexcept {
        if (this != &other) {
            if (ptr_ != nullptr) {
                oroFree(reinterpret_cast<oroDeviceptr>(ptr_));
            }
            ptr_ = other.ptr_;
            other.ptr_ = nullptr;
        }
        return *this;
    }
    void* get() const { return ptr_; }
    oroDeviceptr oro_ptr() const { return reinterpret_cast<oroDeviceptr>(ptr_); }

  private:
    void* ptr_ = nullptr;
};

void set_message(char* buffer, size_t buffer_size, const std::string& message) {
    if (buffer == nullptr || buffer_size == 0) {
        return;
    }
    const size_t bytes = std::min(buffer_size - 1, message.size());
    std::memcpy(buffer, message.data(), bytes);
    buffer[bytes] = '\0';
}

std::string oro_error_message(const char* op, oroError err) {
    return std::string(op) + " failed with Orochi error " + std::to_string(static_cast<int>(err));
}

std::string oro_initialize_error_message(int err) {
    return "oroInitialize(CUDA) failed with Orochi error " + std::to_string(err);
}

std::string hiprt_error_message(const char* op, hiprtError err) {
    return std::string(op) + " failed with HIPRT error " + std::to_string(static_cast<int>(err));
}

std::string orortc_error_message(const char* op, orortcResult err) {
    return std::string(op) + " failed with ORORTC error " + std::to_string(static_cast<int>(err));
}

void check_oro(const char* op, oroError err) {
    if (err != oroSuccess) {
        throw std::runtime_error(oro_error_message(op, err));
    }
}

void check_hiprt(const char* op, hiprtError err) {
    if (err != hiprtSuccess) {
        throw std::runtime_error(hiprt_error_message(op, err));
    }
}

void check_orortc(const char* op, orortcResult err) {
    if (err != ORORTC_SUCCESS) {
        throw std::runtime_error(orortc_error_message(op, err));
    }
}

HiprtRuntime create_runtime() {
    int init_err = oroInitialize(static_cast<oroApi>(ORO_API_CUDA), 0);
    if (init_err != static_cast<int>(oroSuccess)) {
        throw std::runtime_error(oro_initialize_error_message(init_err));
    }
    HiprtRuntime runtime;
    check_oro("oroInit", oroInit(0));
    check_oro("oroDeviceGet(0)", oroDeviceGet(&runtime.device, 0));
    check_oro("oroCtxCreate", oroCtxCreate(&runtime.ctx, 0, runtime.device));

    oroDeviceProp props{};
    check_oro("oroGetDeviceProperties", oroGetDeviceProperties(&props, runtime.device));
    hiprtContextCreationInput input{};
    input.ctxt = oroGetRawCtx(runtime.ctx);
    input.device = oroGetRawDevice(runtime.device);
    input.deviceType = std::strstr(props.name, "NVIDIA") != nullptr ? hiprtDeviceNVIDIA : hiprtDeviceAMD;
    check_hiprt("hiprtCreateContext", hiprtCreateContext(HIPRT_API_VERSION, input, runtime.context));
    return runtime;
}

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

template <typename T>
void copy_host_to_device(DeviceAllocation& allocation, const std::vector<T>& values) {
    if (values.empty()) {
        return;
    }
    check_oro(
        "oroMemcpyHtoD",
        oroMemcpyHtoD(allocation.oro_ptr(), const_cast<T*>(values.data()), values.size() * sizeof(T)));
}

template <typename T>
void copy_device_to_host(std::vector<T>& values, const DeviceAllocation& allocation) {
    if (values.empty()) {
        return;
    }
    check_oro(
        "oroMemcpyDtoH",
        oroMemcpyDtoH(values.data(), allocation.oro_ptr(), values.size() * sizeof(T)));
}

struct PreparedRayHitcount3D {
    HiprtRuntime runtime;
    DeviceAllocation vertex_device;
    hiprtGeometry geometry{};
    oroFunction kernel{};

    PreparedRayHitcount3D(
        HiprtRuntime&& runtime_in,
        DeviceAllocation&& vertex_device_in,
        hiprtGeometry geometry_in,
        oroFunction kernel_in)
        : runtime(std::move(runtime_in)),
          vertex_device(std::move(vertex_device_in)),
          geometry(geometry_in),
          kernel(kernel_in) {}

    ~PreparedRayHitcount3D() {
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
            geometry = nullptr;
        }
    }

    PreparedRayHitcount3D(const PreparedRayHitcount3D&) = delete;
    PreparedRayHitcount3D& operator=(const PreparedRayHitcount3D&) = delete;
    PreparedRayHitcount3D(PreparedRayHitcount3D&&) = delete;
    PreparedRayHitcount3D& operator=(PreparedRayHitcount3D&&) = delete;
};

struct PreparedFixedRadiusNeighbors3D {
    HiprtRuntime runtime;
    DeviceAllocation search_device;
    DeviceAllocation aabb_device;
    DeviceAllocation params_device;
    hiprtGeometry geometry{};
    hiprtFuncTable func_table{};
    oroFunction kernel{};
    size_t search_count{};

    PreparedFixedRadiusNeighbors3D(
        HiprtRuntime&& runtime_in,
        DeviceAllocation&& search_device_in,
        DeviceAllocation&& aabb_device_in,
        DeviceAllocation&& params_device_in,
        hiprtGeometry geometry_in,
        hiprtFuncTable func_table_in,
        oroFunction kernel_in,
        size_t search_count_in)
        : runtime(std::move(runtime_in)),
          search_device(std::move(search_device_in)),
          aabb_device(std::move(aabb_device_in)),
          params_device(std::move(params_device_in)),
          geometry(geometry_in),
          func_table(func_table_in),
          kernel(kernel_in),
          search_count(search_count_in) {}

    ~PreparedFixedRadiusNeighbors3D() {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
            func_table = nullptr;
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
            geometry = nullptr;
        }
    }

    PreparedFixedRadiusNeighbors3D(const PreparedFixedRadiusNeighbors3D&) = delete;
    PreparedFixedRadiusNeighbors3D& operator=(const PreparedFixedRadiusNeighbors3D&) = delete;
    PreparedFixedRadiusNeighbors3D(PreparedFixedRadiusNeighbors3D&&) = delete;
    PreparedFixedRadiusNeighbors3D& operator=(PreparedFixedRadiusNeighbors3D&&) = delete;
};

struct PreparedGraphCSR {
    HiprtRuntime runtime;
    DeviceAllocation row_offset_device;
    DeviceAllocation column_device;
    DeviceAllocation edge_device;
    DeviceAllocation aabb_device;
    hiprtGeometry geometry{};
    hiprtFuncTable bfs_func_table{};
    hiprtFuncTable triangle_func_table{};
    oroFunction bfs_kernel{};
    oroFunction triangle_kernel{};
    uint32_t vertex_count{};
    uint32_t edge_count{};

    PreparedGraphCSR(
        HiprtRuntime&& runtime_in,
        DeviceAllocation&& row_offset_device_in,
        DeviceAllocation&& column_device_in,
        DeviceAllocation&& edge_device_in,
        DeviceAllocation&& aabb_device_in,
        hiprtGeometry geometry_in,
        hiprtFuncTable bfs_func_table_in,
        hiprtFuncTable triangle_func_table_in,
        oroFunction bfs_kernel_in,
        oroFunction triangle_kernel_in,
        uint32_t vertex_count_in,
        uint32_t edge_count_in)
        : runtime(std::move(runtime_in)),
          row_offset_device(std::move(row_offset_device_in)),
          column_device(std::move(column_device_in)),
          edge_device(std::move(edge_device_in)),
          aabb_device(std::move(aabb_device_in)),
          geometry(geometry_in),
          bfs_func_table(bfs_func_table_in),
          triangle_func_table(triangle_func_table_in),
          bfs_kernel(bfs_kernel_in),
          triangle_kernel(triangle_kernel_in),
          vertex_count(vertex_count_in),
          edge_count(edge_count_in) {}

    ~PreparedGraphCSR() {
        if (bfs_func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, bfs_func_table);
            bfs_func_table = nullptr;
        }
        if (triangle_func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, triangle_func_table);
            triangle_func_table = nullptr;
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
            geometry = nullptr;
        }
    }

    PreparedGraphCSR(const PreparedGraphCSR&) = delete;
    PreparedGraphCSR& operator=(const PreparedGraphCSR&) = delete;
    PreparedGraphCSR(PreparedGraphCSR&&) = delete;
    PreparedGraphCSR& operator=(PreparedGraphCSR&&) = delete;
};

std::vector<hiprtFloat3> encode_triangle_vertices(const RtdlTriangle3D* triangles, size_t triangle_count) {
    std::vector<hiprtFloat3> vertices;
    vertices.reserve(triangle_count * 3);
    for (size_t i = 0; i < triangle_count; ++i) {
        vertices.push_back({static_cast<float>(triangles[i].x0), static_cast<float>(triangles[i].y0), static_cast<float>(triangles[i].z0)});
        vertices.push_back({static_cast<float>(triangles[i].x1), static_cast<float>(triangles[i].y1), static_cast<float>(triangles[i].z1)});
        vertices.push_back({static_cast<float>(triangles[i].x2), static_cast<float>(triangles[i].y2), static_cast<float>(triangles[i].z2)});
    }
    return vertices;
}

std::vector<RtdlHiprtRay3DDevice> encode_rays(const RtdlRay3D* rays, size_t ray_count) {
    std::vector<RtdlHiprtRay3DDevice> ray_values;
    ray_values.reserve(ray_count);
    for (size_t i = 0; i < ray_count; ++i) {
        ray_values.push_back({
            rays[i].id,
            static_cast<float>(rays[i].ox),
            static_cast<float>(rays[i].oy),
            static_cast<float>(rays[i].oz),
            static_cast<float>(rays[i].dx),
            static_cast<float>(rays[i].dy),
            static_cast<float>(rays[i].dz),
            static_cast<float>(rays[i].tmax),
        });
    }
    return ray_values;
}

std::vector<RtdlHiprtRay2DDevice> encode_rays_2d(const RtdlRay2D* rays, size_t ray_count) {
    std::vector<RtdlHiprtRay2DDevice> values;
    values.reserve(ray_count);
    for (size_t i = 0; i < ray_count; ++i) {
        values.push_back({
            rays[i].id,
            static_cast<float>(rays[i].ox),
            static_cast<float>(rays[i].oy),
            static_cast<float>(rays[i].dx),
            static_cast<float>(rays[i].dy),
            static_cast<float>(rays[i].tmax),
        });
    }
    return values;
}

std::vector<RtdlHiprtPoint2DDevice> encode_points_2d(const RtdlPoint* points, size_t point_count) {
    std::vector<RtdlHiprtPoint2DDevice> values;
    values.reserve(point_count);
    for (size_t i = 0; i < point_count; ++i) {
        values.push_back({
            points[i].id,
            static_cast<float>(points[i].x),
            static_cast<float>(points[i].y),
        });
    }
    return values;
}

std::vector<RtdlHiprtTriangle2DDevice> encode_triangles_2d(const RtdlTriangle* triangles, size_t triangle_count) {
    std::vector<RtdlHiprtTriangle2DDevice> values;
    values.reserve(triangle_count);
    for (size_t i = 0; i < triangle_count; ++i) {
        values.push_back({
            triangles[i].id,
            static_cast<float>(triangles[i].x0),
            static_cast<float>(triangles[i].y0),
            static_cast<float>(triangles[i].x1),
            static_cast<float>(triangles[i].y1),
            static_cast<float>(triangles[i].x2),
            static_cast<float>(triangles[i].y2),
        });
    }
    return values;
}

std::vector<RtdlHiprtPolygonRefDevice> encode_polygon_refs_2d(const RtdlPolygonRef* polygons, size_t polygon_count) {
    std::vector<RtdlHiprtPolygonRefDevice> values;
    values.reserve(polygon_count);
    for (size_t i = 0; i < polygon_count; ++i) {
        values.push_back({polygons[i].id, polygons[i].vertex_offset, polygons[i].vertex_count});
    }
    return values;
}

std::vector<RtdlHiprtVertex2DDevice> encode_vertices_2d(const double* vertices_xy, size_t vertex_xy_count) {
    std::vector<RtdlHiprtVertex2DDevice> values;
    values.reserve(vertex_xy_count / 2);
    for (size_t i = 0; i + 1 < vertex_xy_count; i += 2) {
        values.push_back({static_cast<float>(vertices_xy[i]), static_cast<float>(vertices_xy[i + 1])});
    }
    return values;
}

std::vector<RtdlHiprtSegmentDevice> encode_segments(const RtdlSegment* segments, size_t segment_count) {
    std::vector<RtdlHiprtSegmentDevice> values;
    values.reserve(segment_count);
    for (size_t i = 0; i < segment_count; ++i) {
        values.push_back({
            segments[i].id,
            static_cast<float>(segments[i].x0),
            static_cast<float>(segments[i].y0),
            static_cast<float>(segments[i].x1),
            static_cast<float>(segments[i].y1),
        });
    }
    return values;
}

std::vector<RtdlHiprtPoint3DDevice> encode_points(const RtdlPoint3D* points, size_t point_count) {
    std::vector<RtdlHiprtPoint3DDevice> values;
    values.reserve(point_count);
    for (size_t i = 0; i < point_count; ++i) {
        values.push_back({
            points[i].id,
            static_cast<float>(points[i].x),
            static_cast<float>(points[i].y),
            static_cast<float>(points[i].z),
        });
    }
    return values;
}

std::vector<RtdlHiprtAabb> encode_point_aabbs(const RtdlHiprtPoint3DDevice* points, size_t point_count, float radius) {
    std::vector<RtdlHiprtAabb> aabbs;
    aabbs.reserve(point_count);
    for (size_t i = 0; i < point_count; ++i) {
        aabbs.push_back({
            {points[i].x - radius, points[i].y - radius, points[i].z - radius, 0.0f},
            {points[i].x + radius, points[i].y + radius, points[i].z + radius, 0.0f},
        });
    }
    return aabbs;
}

std::vector<RtdlHiprtAabb> encode_point_2d_aabbs(const RtdlHiprtPoint2DDevice* points, size_t point_count, float radius) {
    std::vector<RtdlHiprtAabb> aabbs;
    aabbs.reserve(point_count);
    constexpr float eps = 1.0e-4f;
    const float z_pad = std::max(radius, eps);
    for (size_t i = 0; i < point_count; ++i) {
        aabbs.push_back({
            {points[i].x - radius, points[i].y - radius, -z_pad, 0.0f},
            {points[i].x + radius, points[i].y + radius, z_pad, 0.0f},
        });
    }
    return aabbs;
}

std::vector<RtdlHiprtAabb> encode_segment_aabbs(const RtdlHiprtSegmentDevice* segments, size_t segment_count) {
    std::vector<RtdlHiprtAabb> aabbs;
    aabbs.reserve(segment_count);
    constexpr float eps = 1.0e-4f;
    for (size_t i = 0; i < segment_count; ++i) {
        const float min_x = std::min(segments[i].x0, segments[i].x1);
        const float min_y = std::min(segments[i].y0, segments[i].y1);
        const float max_x = std::max(segments[i].x0, segments[i].x1);
        const float max_y = std::max(segments[i].y0, segments[i].y1);
        aabbs.push_back({
            {min_x - eps, min_y - eps, -eps, 0.0f},
            {max_x + eps, max_y + eps, eps, 0.0f},
        });
    }
    return aabbs;
}

std::vector<RtdlHiprtAabb> encode_segment_expanded_aabbs(
    const RtdlHiprtSegmentDevice* segments,
    size_t segment_count,
    float radius) {
    std::vector<RtdlHiprtAabb> aabbs;
    aabbs.reserve(segment_count);
    constexpr float eps = 1.0e-4f;
    const float pad = radius + eps;
    for (size_t i = 0; i < segment_count; ++i) {
        const float min_x = std::min(segments[i].x0, segments[i].x1);
        const float min_y = std::min(segments[i].y0, segments[i].y1);
        const float max_x = std::max(segments[i].x0, segments[i].x1);
        const float max_y = std::max(segments[i].y0, segments[i].y1);
        aabbs.push_back({
            {min_x - pad, min_y - pad, -eps, 0.0f},
            {max_x + pad, max_y + pad, eps, 0.0f},
        });
    }
    return aabbs;
}

float global_point_segment_radius(
    const RtdlHiprtPoint2DDevice* points,
    size_t point_count,
    const RtdlHiprtSegmentDevice* segments,
    size_t segment_count) {
    float min_x = 0.0f;
    float max_x = 0.0f;
    float min_y = 0.0f;
    float max_y = 0.0f;
    bool initialized = false;
    auto add_point = [&](float x, float y) {
        if (!initialized) {
            min_x = max_x = x;
            min_y = max_y = y;
            initialized = true;
            return;
        }
        min_x = std::min(min_x, x);
        max_x = std::max(max_x, x);
        min_y = std::min(min_y, y);
        max_y = std::max(max_y, y);
    };
    for (size_t i = 0; i < point_count; ++i) {
        add_point(points[i].x, points[i].y);
    }
    for (size_t i = 0; i < segment_count; ++i) {
        add_point(segments[i].x0, segments[i].y0);
        add_point(segments[i].x1, segments[i].y1);
    }
    const float dx = max_x - min_x;
    const float dy = max_y - min_y;
    return std::sqrt(dx * dx + dy * dy) + 1.0e-4f;
}

std::vector<RtdlHiprtAabb> encode_triangle_2d_aabbs(const RtdlHiprtTriangle2DDevice* triangles, size_t triangle_count) {
    std::vector<RtdlHiprtAabb> aabbs;
    aabbs.reserve(triangle_count);
    constexpr float eps = 1.0e-4f;
    for (size_t i = 0; i < triangle_count; ++i) {
        const float min_x = std::min({triangles[i].x0, triangles[i].x1, triangles[i].x2});
        const float min_y = std::min({triangles[i].y0, triangles[i].y1, triangles[i].y2});
        const float max_x = std::max({triangles[i].x0, triangles[i].x1, triangles[i].x2});
        const float max_y = std::max({triangles[i].y0, triangles[i].y1, triangles[i].y2});
        aabbs.push_back({
            {min_x - eps, min_y - eps, -eps, 0.0f},
            {max_x + eps, max_y + eps, eps, 0.0f},
        });
    }
    return aabbs;
}

std::vector<RtdlHiprtAabb> encode_polygon_aabbs(
    const RtdlHiprtPolygonRefDevice* polygons,
    size_t polygon_count,
    const RtdlHiprtVertex2DDevice* vertices,
    size_t vertex_count) {
    std::vector<RtdlHiprtAabb> aabbs;
    aabbs.reserve(polygon_count);
    constexpr float eps = 1.0e-4f;
    for (size_t i = 0; i < polygon_count; ++i) {
        if (polygons[i].vertex_count == 0 || polygons[i].vertex_offset + polygons[i].vertex_count > vertex_count) {
            throw std::runtime_error("polygon vertex range is invalid");
        }
        float min_x = vertices[polygons[i].vertex_offset].x;
        float max_x = min_x;
        float min_y = vertices[polygons[i].vertex_offset].y;
        float max_y = min_y;
        for (uint32_t j = 1; j < polygons[i].vertex_count; ++j) {
            const RtdlHiprtVertex2DDevice vertex = vertices[polygons[i].vertex_offset + j];
            min_x = std::min(min_x, vertex.x);
            max_x = std::max(max_x, vertex.x);
            min_y = std::min(min_y, vertex.y);
            max_y = std::max(max_y, vertex.y);
        }
        aabbs.push_back({
            {min_x - eps, min_y - eps, -eps, 0.0f},
            {max_x + eps, max_y + eps, eps, 0.0f},
        });
    }
    return aabbs;
}

std::vector<RtdlHiprtAabb> encode_overlay_candidate_aabbs(
    const RtdlHiprtPolygonRefDevice* right_polygons,
    size_t right_count,
    const RtdlHiprtPolygonRefDevice* left_polygons,
    size_t left_count,
    const RtdlHiprtVertex2DDevice* left_vertices,
    size_t left_vertex_count) {
    if (left_count == 0) {
        return {};
    }
    constexpr float eps = 1.0e-4f;
    float min_x = 0.0f;
    float max_x = 0.0f;
    float min_y = 0.0f;
    float max_y = 0.0f;
    bool initialized = false;
    for (size_t i = 0; i < left_count; ++i) {
        if (left_polygons[i].vertex_count == 0 || left_polygons[i].vertex_offset >= left_vertex_count) {
            throw std::runtime_error("left polygon vertex range is invalid");
        }
        const RtdlHiprtVertex2DDevice vertex = left_vertices[left_polygons[i].vertex_offset];
        if (!initialized) {
            min_x = max_x = vertex.x;
            min_y = max_y = vertex.y;
            initialized = true;
        } else {
            min_x = std::min(min_x, vertex.x);
            max_x = std::max(max_x, vertex.x);
            min_y = std::min(min_y, vertex.y);
            max_y = std::max(max_y, vertex.y);
        }
    }
    std::vector<RtdlHiprtAabb> aabbs;
    aabbs.reserve(right_count);
    for (size_t i = 0; i < right_count; ++i) {
        if (right_polygons[i].vertex_count == 0) {
            throw std::runtime_error("right polygon vertex range is invalid");
        }
        aabbs.push_back({
            {min_x - eps, min_y - eps, -eps, 0.0f},
            {max_x + eps, max_y + eps, eps, 0.0f},
        });
    }
    return aabbs;
}

std::vector<RtdlHiprtGraphEdgeDevice> encode_graph_edges(
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t edge_count,
    uint32_t vertex_count) {
    if (row_offset_count != static_cast<size_t>(vertex_count) + 1u) {
        throw std::runtime_error("HIPRT bfs_discover row_offset_count must equal vertex_count + 1");
    }
    if (row_offset_count == 0 || row_offsets[0] != 0u) {
        throw std::runtime_error("HIPRT bfs_discover row_offsets must start at 0");
    }
    if (row_offsets[row_offset_count - 1u] != edge_count) {
        throw std::runtime_error("HIPRT bfs_discover final row_offset must equal edge_count");
    }

    std::vector<RtdlHiprtGraphEdgeDevice> edges;
    edges.reserve(edge_count);
    for (uint32_t src = 0; src < vertex_count; ++src) {
        const uint32_t begin = row_offsets[src];
        const uint32_t end = row_offsets[src + 1u];
        if (end < begin || end > edge_count) {
            throw std::runtime_error("HIPRT bfs_discover row_offsets must be non-decreasing and within edge_count");
        }
        for (uint32_t index = begin; index < end; ++index) {
            const uint32_t dst = column_indices[index];
            if (dst >= vertex_count) {
                throw std::runtime_error("HIPRT bfs_discover column_indices must be valid vertex IDs");
            }
            edges.push_back({src, dst});
        }
    }
    return edges;
}

std::vector<RtdlHiprtAabb> encode_graph_edge_source_aabbs(const RtdlHiprtGraphEdgeDevice* edges, size_t edge_count) {
    std::vector<RtdlHiprtAabb> aabbs;
    aabbs.reserve(edge_count);
    constexpr float eps = 1.0e-4f;
    for (size_t i = 0; i < edge_count; ++i) {
        const float src = static_cast<float>(edges[i].src);
        aabbs.push_back({
            {src - eps, -eps, -eps, 0.0f},
            {src + eps, eps, eps, 0.0f},
        });
    }
    return aabbs;
}

std::vector<RtdlHiprtAabb> encode_db_row_aabbs(size_t row_count) {
    std::vector<RtdlHiprtAabb> aabbs;
    aabbs.reserve(row_count);
    constexpr float eps = 0.25f;
    for (size_t i = 0; i < row_count; ++i) {
        const float row = static_cast<float>(i);
        aabbs.push_back({
            {row - eps, -eps, -eps, 0.0f},
            {row + eps, eps, eps, 0.0f},
        });
    }
    return aabbs;
}

size_t db_find_field_index_or_throw(const RtdlDbField* fields, size_t field_count, const char* name) {
    for (size_t index = 0; index < field_count; ++index) {
        if (std::strcmp(fields[index].name, name) == 0) {
            return index;
        }
    }
    throw std::runtime_error(std::string("DB field not found: ") + name);
}

bool db_scalar_is_numeric(const RtdlDbScalar& value) {
    return value.kind == RTDL_DB_KIND_INT64 || value.kind == RTDL_DB_KIND_FLOAT64 || value.kind == RTDL_DB_KIND_BOOL;
}

double db_scalar_as_double(const RtdlDbScalar& value) {
    if (value.kind == RTDL_DB_KIND_FLOAT64) {
        return value.double_value;
    }
    return static_cast<double>(value.int_value);
}

std::vector<RtdlHiprtDbClauseDevice> encode_db_clauses_for_device(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbClause* clauses,
    size_t clause_count) {
    std::vector<RtdlHiprtDbClauseDevice> output;
    output.reserve(clause_count);
    for (size_t i = 0; i < clause_count; ++i) {
        const size_t field_index = db_find_field_index_or_throw(fields, field_count, clauses[i].field);
        if (!db_scalar_is_numeric(clauses[i].value) ||
            (clauses[i].op == RTDL_DB_OP_BETWEEN && !db_scalar_is_numeric(clauses[i].value_hi))) {
            throw std::runtime_error("HIPRT DB first wave requires numeric or text-encoded predicate values");
        }
        output.push_back({
            static_cast<uint32_t>(field_index),
            clauses[i].op,
            clauses[i].value,
            clauses[i].value_hi,
        });
    }
    return output;
}

hiprtGeometry build_triangle_geometry(
    hiprtContext context,
    DeviceAllocation& vertex_device,
    size_t vertex_count,
    size_t triangle_count) {
    hiprtTriangleMeshPrimitive mesh{};
    mesh.triangleCount = static_cast<uint32_t>(triangle_count);
    mesh.triangleStride = 0;
    mesh.triangleIndices = nullptr;
    mesh.vertexCount = static_cast<uint32_t>(vertex_count);
    mesh.vertexStride = sizeof(hiprtFloat3);
    mesh.vertices = vertex_device.get();

    hiprtGeometryBuildInput geom_input{};
    geom_input.type = hiprtPrimitiveTypeTriangleMesh;
    geom_input.primitive.triangleMesh = mesh;

    hiprtBuildOptions options{};
    options.buildFlags = hiprtBuildFlagBitPreferFastBuild;
    size_t temp_size = 0;
    check_hiprt("hiprtGetGeometryBuildTemporaryBufferSize", hiprtGetGeometryBuildTemporaryBufferSize(context, geom_input, options, temp_size));
    DeviceAllocation temp_device(temp_size);
    hiprtGeometry geometry{};
    check_hiprt("hiprtCreateGeometry", hiprtCreateGeometry(context, geom_input, options, geometry));
    try {
        check_hiprt(
            "hiprtBuildGeometry",
            hiprtBuildGeometry(context, hiprtBuildOperationBuild, geom_input, options, temp_device.get(), 0, geometry));
    } catch (...) {
        if (geometry != nullptr) {
            hiprtDestroyGeometry(context, geometry);
        }
        throw;
    }
    return geometry;
}

hiprtGeometry build_aabb_geometry(
    hiprtContext context,
    DeviceAllocation& aabb_device,
    size_t aabb_count) {
    hiprtAABBListPrimitive list{};
    list.aabbCount = static_cast<uint32_t>(aabb_count);
    list.aabbStride = sizeof(RtdlHiprtAabb);
    list.aabbs = aabb_device.get();

    hiprtGeometryBuildInput geom_input{};
    geom_input.type = hiprtPrimitiveTypeAABBList;
    geom_input.primitive.aabbList = list;
    geom_input.geomType = 0;

    hiprtBuildOptions options{};
    options.buildFlags = hiprtBuildFlagBitPreferFastBuild;
    size_t temp_size = 0;
    check_hiprt("hiprtGetGeometryBuildTemporaryBufferSize", hiprtGetGeometryBuildTemporaryBufferSize(context, geom_input, options, temp_size));
    DeviceAllocation temp_device(temp_size);
    hiprtGeometry geometry{};
    check_hiprt("hiprtCreateGeometry", hiprtCreateGeometry(context, geom_input, options, geometry));
    try {
        check_hiprt(
            "hiprtBuildGeometry",
            hiprtBuildGeometry(context, hiprtBuildOperationBuild, geom_input, options, temp_device.get(), 0, geometry));
    } catch (...) {
        if (geometry != nullptr) {
            hiprtDestroyGeometry(context, geometry);
        }
        throw;
    }
    return geometry;
}

RtdlRayHitCountRow* copy_rows_to_heap(const std::vector<RtdlRayHitCountRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlRayHitCountRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlRayHitCountRow));
    }
    return reinterpret_cast<RtdlRayHitCountRow*>(rows);
}

RtdlLsiRow* copy_lsi_rows_to_heap(const std::vector<RtdlLsiRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlLsiRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlLsiRow));
    }
    return reinterpret_cast<RtdlLsiRow*>(rows);
}

RtdlPipRow* copy_pip_rows_to_heap(const std::vector<RtdlPipRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlPipRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlPipRow));
    }
    return reinterpret_cast<RtdlPipRow*>(rows);
}

RtdlOverlayRow* copy_overlay_rows_to_heap(const std::vector<RtdlOverlayRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlOverlayRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlOverlayRow));
    }
    return reinterpret_cast<RtdlOverlayRow*>(rows);
}

RtdlPointNearestSegmentRow* copy_pns_rows_to_heap(const std::vector<RtdlPointNearestSegmentRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlPointNearestSegmentRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlPointNearestSegmentRow));
    }
    return reinterpret_cast<RtdlPointNearestSegmentRow*>(rows);
}

RtdlSegmentPolygonHitCountRow* copy_segment_polygon_hitcount_rows_to_heap(
    const std::vector<RtdlSegmentPolygonHitCountRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlSegmentPolygonHitCountRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlSegmentPolygonHitCountRow));
    }
    return reinterpret_cast<RtdlSegmentPolygonHitCountRow*>(rows);
}

RtdlSegmentPolygonAnyHitRow* copy_segment_polygon_anyhit_rows_to_heap(
    const std::vector<RtdlSegmentPolygonAnyHitRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlSegmentPolygonAnyHitRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlSegmentPolygonAnyHitRow));
    }
    return reinterpret_cast<RtdlSegmentPolygonAnyHitRow*>(rows);
}

RtdlFixedRadiusNeighborRow* copy_frn_rows_to_heap(const std::vector<RtdlFixedRadiusNeighborRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlFixedRadiusNeighborRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlFixedRadiusNeighborRow));
    }
    return reinterpret_cast<RtdlFixedRadiusNeighborRow*>(rows);
}

RtdlBfsRow* copy_bfs_rows_to_heap(const std::vector<RtdlBfsRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlBfsRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlBfsRow));
    }
    return reinterpret_cast<RtdlBfsRow*>(rows);
}

RtdlTriangleRow* copy_triangle_rows_to_heap(const std::vector<RtdlTriangleRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlTriangleRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlTriangleRow));
    }
    return reinterpret_cast<RtdlTriangleRow*>(rows);
}

RtdlDbRowIdRow* copy_db_row_id_rows_to_heap(const std::vector<RtdlDbRowIdRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlDbRowIdRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlDbRowIdRow));
    }
    return reinterpret_cast<RtdlDbRowIdRow*>(rows);
}

RtdlDbGroupedCountRow* copy_db_grouped_count_rows_to_heap(const std::vector<RtdlDbGroupedCountRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlDbGroupedCountRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlDbGroupedCountRow));
    }
    return reinterpret_cast<RtdlDbGroupedCountRow*>(rows);
}

RtdlDbGroupedSumRow* copy_db_grouped_sum_rows_to_heap(const std::vector<RtdlDbGroupedSumRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlDbGroupedSumRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlDbGroupedSumRow));
    }
    return reinterpret_cast<RtdlDbGroupedSumRow*>(rows);
}

void run_prepared_ray_hitcount_3d(
    PreparedRayHitcount3D& prepared,
    const RtdlRay3D* rays,
    size_t ray_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out) {
    std::vector<RtdlHiprtRay3DDevice> ray_values = encode_rays(rays, ray_count);
    DeviceAllocation ray_device(ray_values.size() * sizeof(RtdlHiprtRay3DDevice));
    copy_host_to_device(ray_device, ray_values);
    std::vector<RtdlRayHitCountRow> output(ray_count);
    DeviceAllocation output_device(output.size() * sizeof(RtdlRayHitCountRow));

    void* ray_device_ptr = ray_device.get();
    void* output_device_ptr = output_device.get();
    uint32_t ray_count_u32 = static_cast<uint32_t>(ray_count);
    uint32_t block_size = 128;
    uint32_t grid_size = static_cast<uint32_t>((ray_count + block_size - 1) / block_size);
    void* args[] = {&prepared.geometry, &ray_device_ptr, &ray_count_u32, &output_device_ptr};
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(prepared.kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
    copy_device_to_host(output, output_device);

    *rows_out = copy_rows_to_heap(output);
    *row_count_out = output.size();
}

void run_fixed_radius_neighbors_3d(
    const RtdlPoint3D* queries,
    size_t query_count,
    const RtdlPoint3D* search_points,
    size_t search_count,
    double radius,
    uint32_t k_max,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out) {
    if (k_max == 0) {
        throw std::runtime_error("fixed_radius_neighbors k_max must be positive");
    }
    if (k_max > 64) {
        throw std::runtime_error("HIPRT fixed_radius_neighbors_3d currently supports k_max <= 64");
    }
    if (radius < 0.0) {
        throw std::runtime_error("fixed_radius_neighbors radius must be non-negative");
    }
    if (query_count > std::numeric_limits<uint32_t>::max() || search_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT fixed_radius_neighbors_3d currently supports at most 2^32-1 query/search points");
    }
    if (query_count != 0 && k_max > std::numeric_limits<size_t>::max() / query_count) {
        throw std::runtime_error("HIPRT fixed_radius_neighbors_3d output capacity overflow");
    }
    if (query_count > 0 && queries == nullptr) {
        throw std::runtime_error("query point pointer must not be null when query_count is nonzero");
    }
    if (search_count > 0 && search_points == nullptr) {
        throw std::runtime_error("search point pointer must not be null when search_count is nonzero");
    }
    if (query_count == 0 || search_count == 0) {
        std::vector<RtdlFixedRadiusNeighborRow> empty;
        *rows_out = copy_frn_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }

    std::vector<RtdlHiprtPoint3DDevice> query_values = encode_points(queries, query_count);
    std::vector<RtdlHiprtPoint3DDevice> search_values = encode_points(search_points, search_count);
    std::vector<RtdlHiprtAabb> aabb_values = encode_point_aabbs(search_values.data(), search_values.size(), static_cast<float>(radius));
    RtdlHiprtFixedRadiusParams params{static_cast<float>(radius)};

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation query_device(query_values.size() * sizeof(RtdlHiprtPoint3DDevice));
    DeviceAllocation search_device(search_values.size() * sizeof(RtdlHiprtPoint3DDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    DeviceAllocation params_device(sizeof(RtdlHiprtFixedRadiusParams));
    copy_host_to_device(query_device, query_values);
    copy_host_to_device(search_device, search_values);
    copy_host_to_device(aabb_device, aabb_values);
    check_oro("oroMemcpyHtoD", oroMemcpyHtoD(params_device.oro_ptr(), &params, sizeof(params)));

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlPointRadius3D";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = search_device.get();
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            fixed_radius_neighbors_3d_kernel_source(),
            "rtdl_hiprt_fixed_radius_neighbors_3d.cu",
            "RtdlFixedRadiusNeighbors3DKernel",
            &func_name_set,
            1,
            1);

        const size_t output_capacity = query_count * static_cast<size_t>(k_max);
        std::vector<RtdlFixedRadiusNeighborRow> output(output_capacity);
        std::vector<uint32_t> counts(query_count);
        DeviceAllocation output_device(output.size() * sizeof(RtdlFixedRadiusNeighborRow));
        DeviceAllocation counts_device(counts.size() * sizeof(uint32_t));

        void* query_device_ptr = query_device.get();
        void* search_device_ptr = search_device.get();
        void* output_device_ptr = output_device.get();
        void* counts_device_ptr = counts_device.get();
        void* params_device_ptr = params_device.get();
        uint32_t query_count_u32 = static_cast<uint32_t>(query_count);
        uint32_t block_size = 128;
        uint32_t grid_size = static_cast<uint32_t>((query_count + block_size - 1) / block_size);
        void* args[] = {
            &geometry,
            &query_device_ptr,
            &search_device_ptr,
            &query_count_u32,
            &k_max,
            &output_device_ptr,
            &counts_device_ptr,
            &params_device_ptr,
            &func_table,
        };
        check_oro(
            "oroModuleLaunchKernel",
            oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
        copy_device_to_host(output, output_device);
        copy_device_to_host(counts, counts_device);

        std::vector<RtdlFixedRadiusNeighborRow> compacted;
        for (size_t query_index = 0; query_index < query_count; ++query_index) {
            uint32_t count = std::min(counts[query_index], k_max);
            size_t base = query_index * static_cast<size_t>(k_max);
            for (uint32_t rank = 0; rank < count; ++rank) {
                compacted.push_back(output[base + rank]);
            }
        }
        *rows_out = copy_frn_rows_to_heap(compacted);
        *row_count_out = compacted.size();
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
}

std::unique_ptr<PreparedFixedRadiusNeighbors3D> prepare_fixed_radius_neighbors_3d(
    const RtdlPoint3D* search_points,
    size_t search_count,
    double radius) {
    if (radius < 0.0) {
        throw std::runtime_error("fixed_radius_neighbors radius must be non-negative");
    }
    if (search_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT fixed_radius_neighbors_3d currently supports at most 2^32-1 search points");
    }
    if (search_count > 0 && search_points == nullptr) {
        throw std::runtime_error("search point pointer must not be null when search_count is nonzero");
    }
    if (search_count == 0) {
        throw std::runtime_error("prepared HIPRT fixed_radius_neighbors_3d requires at least one search point");
    }

    std::vector<RtdlHiprtPoint3DDevice> search_values = encode_points(search_points, search_count);
    std::vector<RtdlHiprtAabb> aabb_values = encode_point_aabbs(search_values.data(), search_values.size(), static_cast<float>(radius));
    RtdlHiprtFixedRadiusParams params{static_cast<float>(radius)};

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation search_device(search_values.size() * sizeof(RtdlHiprtPoint3DDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    DeviceAllocation params_device(sizeof(RtdlHiprtFixedRadiusParams));
    copy_host_to_device(search_device, search_values);
    copy_host_to_device(aabb_device, aabb_values);
    check_oro("oroMemcpyHtoD", oroMemcpyHtoD(params_device.oro_ptr(), &params, sizeof(params)));

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlPointRadius3D";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = search_device.get();
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            fixed_radius_neighbors_3d_kernel_source(),
            "rtdl_hiprt_fixed_radius_neighbors_3d.cu",
            "RtdlFixedRadiusNeighbors3DKernel",
            &func_name_set,
            1,
            1);
        auto prepared = std::make_unique<PreparedFixedRadiusNeighbors3D>(
            std::move(runtime),
            std::move(search_device),
            std::move(aabb_device),
            std::move(params_device),
            geometry,
            func_table,
            kernel,
            search_count);
        geometry = nullptr;
        func_table = nullptr;
        return prepared;
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
}

void run_prepared_fixed_radius_neighbors_3d(
    PreparedFixedRadiusNeighbors3D& prepared,
    const RtdlPoint3D* queries,
    size_t query_count,
    uint32_t k_max,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out) {
    if (k_max == 0) {
        throw std::runtime_error("fixed_radius_neighbors k_max must be positive");
    }
    if (k_max > 64) {
        throw std::runtime_error("HIPRT fixed_radius_neighbors_3d currently supports k_max <= 64");
    }
    if (query_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT fixed_radius_neighbors_3d currently supports at most 2^32-1 query points");
    }
    if (query_count != 0 && k_max > std::numeric_limits<size_t>::max() / query_count) {
        throw std::runtime_error("HIPRT fixed_radius_neighbors_3d output capacity overflow");
    }
    if (query_count > 0 && queries == nullptr) {
        throw std::runtime_error("query point pointer must not be null when query_count is nonzero");
    }
    if (query_count == 0 || prepared.search_count == 0) {
        std::vector<RtdlFixedRadiusNeighborRow> empty;
        *rows_out = copy_frn_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }

    std::vector<RtdlHiprtPoint3DDevice> query_values = encode_points(queries, query_count);
    DeviceAllocation query_device(query_values.size() * sizeof(RtdlHiprtPoint3DDevice));
    copy_host_to_device(query_device, query_values);

    const size_t output_capacity = query_count * static_cast<size_t>(k_max);
    std::vector<RtdlFixedRadiusNeighborRow> output(output_capacity);
    std::vector<uint32_t> counts(query_count);
    DeviceAllocation output_device(output.size() * sizeof(RtdlFixedRadiusNeighborRow));
    DeviceAllocation counts_device(counts.size() * sizeof(uint32_t));

    void* query_device_ptr = query_device.get();
    void* search_device_ptr = prepared.search_device.get();
    void* output_device_ptr = output_device.get();
    void* counts_device_ptr = counts_device.get();
    void* params_device_ptr = prepared.params_device.get();
    uint32_t query_count_u32 = static_cast<uint32_t>(query_count);
    uint32_t block_size = 128;
    uint32_t grid_size = static_cast<uint32_t>((query_count + block_size - 1) / block_size);
    void* args[] = {
        &prepared.geometry,
        &query_device_ptr,
        &search_device_ptr,
        &query_count_u32,
        &k_max,
        &output_device_ptr,
        &counts_device_ptr,
        &params_device_ptr,
        &prepared.func_table,
    };
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(prepared.kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
    copy_device_to_host(output, output_device);
    copy_device_to_host(counts, counts_device);

    std::vector<RtdlFixedRadiusNeighborRow> compacted;
    for (size_t query_index = 0; query_index < query_count; ++query_index) {
        uint32_t count = std::min(counts[query_index], k_max);
        size_t base = query_index * static_cast<size_t>(k_max);
        for (uint32_t rank = 0; rank < count; ++rank) {
            compacted.push_back(output[base + rank]);
        }
    }
    *rows_out = copy_frn_rows_to_heap(compacted);
    *row_count_out = compacted.size();
}

void run_fixed_radius_neighbors_2d(
    const RtdlPoint* queries,
    size_t query_count,
    const RtdlPoint* search_points,
    size_t search_count,
    double radius,
    uint32_t k_max,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out) {
    if (k_max == 0) {
        throw std::runtime_error("fixed_radius_neighbors k_max must be positive");
    }
    if (k_max > 64) {
        throw std::runtime_error("HIPRT fixed_radius_neighbors_2d currently supports k_max <= 64");
    }
    if (radius < 0.0) {
        throw std::runtime_error("fixed_radius_neighbors radius must be non-negative");
    }
    if (query_count > std::numeric_limits<uint32_t>::max() || search_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT fixed_radius_neighbors_2d currently supports at most 2^32-1 query/search points");
    }
    if (query_count != 0 && k_max > std::numeric_limits<size_t>::max() / query_count) {
        throw std::runtime_error("HIPRT fixed_radius_neighbors_2d output capacity overflow");
    }
    if (query_count > 0 && queries == nullptr) {
        throw std::runtime_error("query point pointer must not be null when query_count is nonzero");
    }
    if (search_count > 0 && search_points == nullptr) {
        throw std::runtime_error("search point pointer must not be null when search_count is nonzero");
    }
    if (query_count == 0 || search_count == 0) {
        std::vector<RtdlFixedRadiusNeighborRow> empty;
        *rows_out = copy_frn_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }

    std::vector<RtdlHiprtPoint2DDevice> query_values = encode_points_2d(queries, query_count);
    std::vector<RtdlHiprtPoint2DDevice> search_values = encode_points_2d(search_points, search_count);
    std::vector<RtdlHiprtAabb> aabb_values = encode_point_2d_aabbs(search_values.data(), search_values.size(), static_cast<float>(radius));
    RtdlHiprtFixedRadiusParams params{static_cast<float>(radius)};

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation query_device(query_values.size() * sizeof(RtdlHiprtPoint2DDevice));
    DeviceAllocation search_device(search_values.size() * sizeof(RtdlHiprtPoint2DDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    DeviceAllocation params_device(sizeof(RtdlHiprtFixedRadiusParams));
    copy_host_to_device(query_device, query_values);
    copy_host_to_device(search_device, search_values);
    copy_host_to_device(aabb_device, aabb_values);
    check_oro("oroMemcpyHtoD", oroMemcpyHtoD(params_device.oro_ptr(), &params, sizeof(params)));

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlPointRadius2D";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = search_device.get();
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            fixed_radius_neighbors_2d_kernel_source(),
            "rtdl_hiprt_fixed_radius_neighbors_2d.cu",
            "RtdlFixedRadiusNeighbors2DKernel",
            &func_name_set,
            1,
            1);

        const size_t output_capacity = query_count * static_cast<size_t>(k_max);
        std::vector<RtdlFixedRadiusNeighborRow> output(output_capacity);
        std::vector<uint32_t> counts(query_count);
        DeviceAllocation output_device(output.size() * sizeof(RtdlFixedRadiusNeighborRow));
        DeviceAllocation counts_device(counts.size() * sizeof(uint32_t));

        void* query_device_ptr = query_device.get();
        void* search_device_ptr = search_device.get();
        void* output_device_ptr = output_device.get();
        void* counts_device_ptr = counts_device.get();
        void* params_device_ptr = params_device.get();
        uint32_t query_count_u32 = static_cast<uint32_t>(query_count);
        uint32_t block_size = 128;
        uint32_t grid_size = static_cast<uint32_t>((query_count + block_size - 1) / block_size);
        void* args[] = {
            &geometry,
            &query_device_ptr,
            &search_device_ptr,
            &query_count_u32,
            &k_max,
            &output_device_ptr,
            &counts_device_ptr,
            &params_device_ptr,
            &func_table,
        };
        check_oro(
            "oroModuleLaunchKernel",
            oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
        copy_device_to_host(output, output_device);
        copy_device_to_host(counts, counts_device);

        std::vector<RtdlFixedRadiusNeighborRow> compacted;
        for (size_t query_index = 0; query_index < query_count; ++query_index) {
            uint32_t count = std::min(counts[query_index], k_max);
            size_t base = query_index * static_cast<size_t>(k_max);
            for (uint32_t rank = 0; rank < count; ++rank) {
                compacted.push_back(output[base + rank]);
            }
        }
        *rows_out = copy_frn_rows_to_heap(compacted);
        *row_count_out = compacted.size();
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
}

void sort_lsi_rows_by_input_order(
    std::vector<RtdlLsiRow>& rows,
    const RtdlSegment* left,
    size_t left_count,
    const RtdlSegment* right,
    size_t right_count) {
    std::unordered_map<uint32_t, size_t> left_order;
    std::unordered_map<uint32_t, size_t> right_order;
    left_order.reserve(left_count);
    right_order.reserve(right_count);
    for (size_t i = 0; i < left_count; ++i) {
        left_order.emplace(left[i].id, i);
    }
    for (size_t i = 0; i < right_count; ++i) {
        right_order.emplace(right[i].id, i);
    }
    std::sort(rows.begin(), rows.end(), [&](const RtdlLsiRow& a, const RtdlLsiRow& b) {
        const size_t left_a = left_order.count(a.left_id) ? left_order[a.left_id] : std::numeric_limits<size_t>::max();
        const size_t left_b = left_order.count(b.left_id) ? left_order[b.left_id] : std::numeric_limits<size_t>::max();
        if (left_a != left_b) {
            return left_a < left_b;
        }
        const size_t right_a = right_order.count(a.right_id) ? right_order[a.right_id] : std::numeric_limits<size_t>::max();
        const size_t right_b = right_order.count(b.right_id) ? right_order[b.right_id] : std::numeric_limits<size_t>::max();
        return right_a < right_b;
    });
}

void sort_segment_polygon_anyhit_rows_by_input_order(
    std::vector<RtdlSegmentPolygonAnyHitRow>& rows,
    const RtdlSegment* segments,
    size_t segment_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count) {
    std::unordered_map<uint32_t, size_t> segment_order;
    std::unordered_map<uint32_t, size_t> polygon_order;
    segment_order.reserve(segment_count);
    polygon_order.reserve(polygon_count);
    for (size_t i = 0; i < segment_count; ++i) {
        segment_order.emplace(segments[i].id, i);
    }
    for (size_t i = 0; i < polygon_count; ++i) {
        polygon_order.emplace(polygons[i].id, i);
    }
    std::sort(rows.begin(), rows.end(), [&](const RtdlSegmentPolygonAnyHitRow& a, const RtdlSegmentPolygonAnyHitRow& b) {
        const size_t segment_a = segment_order.count(a.segment_id) ? segment_order[a.segment_id] : std::numeric_limits<size_t>::max();
        const size_t segment_b = segment_order.count(b.segment_id) ? segment_order[b.segment_id] : std::numeric_limits<size_t>::max();
        if (segment_a != segment_b) {
            return segment_a < segment_b;
        }
        const size_t polygon_a = polygon_order.count(a.polygon_id) ? polygon_order[a.polygon_id] : std::numeric_limits<size_t>::max();
        const size_t polygon_b = polygon_order.count(b.polygon_id) ? polygon_order[b.polygon_id] : std::numeric_limits<size_t>::max();
        return polygon_a < polygon_b;
    });
}

void run_lsi_2d(
    const RtdlSegment* left,
    size_t left_count,
    const RtdlSegment* right,
    size_t right_count,
    RtdlLsiRow** rows_out,
    size_t* row_count_out) {
    if (left_count > std::numeric_limits<uint32_t>::max() || right_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT segment_intersection currently supports at most 2^32-1 left/right segments");
    }
    if (left_count != 0 && right_count > std::numeric_limits<size_t>::max() / left_count) {
        throw std::runtime_error("HIPRT segment_intersection output capacity overflow");
    }
    if (left_count > 0 && left == nullptr) {
        throw std::runtime_error("left segment pointer must not be null when left_count is nonzero");
    }
    if (right_count > 0 && right == nullptr) {
        throw std::runtime_error("right segment pointer must not be null when right_count is nonzero");
    }
    if (left_count == 0 || right_count == 0) {
        std::vector<RtdlLsiRow> empty;
        *rows_out = copy_lsi_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }

    std::vector<RtdlHiprtSegmentDevice> left_values = encode_segments(left, left_count);
    std::vector<RtdlHiprtSegmentDevice> right_values = encode_segments(right, right_count);
    std::vector<RtdlHiprtAabb> aabb_values = encode_segment_aabbs(right_values.data(), right_values.size());

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation left_device(left_values.size() * sizeof(RtdlHiprtSegmentDevice));
    DeviceAllocation right_device(right_values.size() * sizeof(RtdlHiprtSegmentDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    copy_host_to_device(left_device, left_values);
    copy_host_to_device(right_device, right_values);
    copy_host_to_device(aabb_device, aabb_values);

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlSegment2D";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = right_device.get();
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            lsi_2d_kernel_source(),
            "rtdl_hiprt_lsi_2d.cu",
            "RtdlLsi2DKernel",
            &func_name_set,
            1,
            1);

        const size_t output_capacity = left_count * right_count;
        std::vector<RtdlLsiRow> output(output_capacity);
        std::vector<uint32_t> counts(left_count);
        DeviceAllocation output_device(output.size() * sizeof(RtdlLsiRow));
        DeviceAllocation counts_device(counts.size() * sizeof(uint32_t));

        void* left_device_ptr = left_device.get();
        void* right_device_ptr = right_device.get();
        void* output_device_ptr = output_device.get();
        void* counts_device_ptr = counts_device.get();
        uint32_t left_count_u32 = static_cast<uint32_t>(left_count);
        uint32_t right_count_u32 = static_cast<uint32_t>(right_count);
        uint32_t block_size = 128;
        uint32_t grid_size = static_cast<uint32_t>((left_count + block_size - 1) / block_size);
        void* args[] = {
            &geometry,
            &left_device_ptr,
            &right_device_ptr,
            &left_count_u32,
            &right_count_u32,
            &output_device_ptr,
            &counts_device_ptr,
            &func_table,
        };
        check_oro(
            "oroModuleLaunchKernel",
            oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
        copy_device_to_host(output, output_device);
        copy_device_to_host(counts, counts_device);

        std::vector<RtdlLsiRow> compacted;
        for (size_t left_index = 0; left_index < left_count; ++left_index) {
            uint32_t count = std::min<uint32_t>(counts[left_index], static_cast<uint32_t>(right_count));
            size_t base = left_index * right_count;
            for (uint32_t rank = 0; rank < count; ++rank) {
                compacted.push_back(output[base + rank]);
            }
        }
        sort_lsi_rows_by_input_order(compacted, left, left_count, right, right_count);
        *rows_out = copy_lsi_rows_to_heap(compacted);
        *row_count_out = compacted.size();
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
}

void run_segment_polygon_2d_common(
    const RtdlSegment* segments,
    size_t segment_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    bool anyhit_rows,
    RtdlSegmentPolygonHitCountRow** hitcount_rows_out,
    RtdlSegmentPolygonAnyHitRow** anyhit_rows_out,
    size_t* row_count_out) {
    if (segment_count > std::numeric_limits<uint32_t>::max() || polygon_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT segment_polygon currently supports at most 2^32-1 segments/polygons");
    }
    if (segment_count != 0 && polygon_count > std::numeric_limits<size_t>::max() / segment_count) {
        throw std::runtime_error("HIPRT segment_polygon output capacity overflow");
    }
    if (segment_count > 0 && segments == nullptr) {
        throw std::runtime_error("segment pointer must not be null when segment_count is nonzero");
    }
    if (polygon_count > 0 && polygons == nullptr) {
        throw std::runtime_error("polygon pointer must not be null when polygon_count is nonzero");
    }
    if (vertex_xy_count % 2 != 0) {
        throw std::runtime_error("polygon vertex_xy_count must be even");
    }
    if (vertex_xy_count > 0 && vertices_xy == nullptr) {
        throw std::runtime_error("polygon vertices pointer must not be null when vertex_xy_count is nonzero");
    }
    if (segment_count == 0) {
        *row_count_out = 0;
        if (anyhit_rows) {
            std::vector<RtdlSegmentPolygonAnyHitRow> empty;
            *anyhit_rows_out = copy_segment_polygon_anyhit_rows_to_heap(empty);
        } else {
            std::vector<RtdlSegmentPolygonHitCountRow> empty;
            *hitcount_rows_out = copy_segment_polygon_hitcount_rows_to_heap(empty);
        }
        return;
    }
    if (polygon_count == 0) {
        if (anyhit_rows) {
            std::vector<RtdlSegmentPolygonAnyHitRow> empty;
            *anyhit_rows_out = copy_segment_polygon_anyhit_rows_to_heap(empty);
            *row_count_out = 0;
        } else {
            std::vector<RtdlSegmentPolygonHitCountRow> output;
            output.reserve(segment_count);
            for (size_t i = 0; i < segment_count; ++i) {
                output.push_back({segments[i].id, 0u});
            }
            *hitcount_rows_out = copy_segment_polygon_hitcount_rows_to_heap(output);
            *row_count_out = output.size();
        }
        return;
    }

    std::vector<RtdlHiprtSegmentDevice> segment_values = encode_segments(segments, segment_count);
    std::vector<RtdlHiprtPolygonRefDevice> polygon_values = encode_polygon_refs_2d(polygons, polygon_count);
    std::vector<RtdlHiprtVertex2DDevice> vertex_values = encode_vertices_2d(vertices_xy, vertex_xy_count);
    std::vector<RtdlHiprtAabb> aabb_values =
        encode_polygon_aabbs(polygon_values.data(), polygon_values.size(), vertex_values.data(), vertex_values.size());

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation segment_device(segment_values.size() * sizeof(RtdlHiprtSegmentDevice));
    DeviceAllocation polygon_device(polygon_values.size() * sizeof(RtdlHiprtPolygonRefDevice));
    DeviceAllocation vertex_device(vertex_values.size() * sizeof(RtdlHiprtVertex2DDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    DeviceAllocation pip_data_device(sizeof(RtdlHiprtPipDataDevice));
    copy_host_to_device(segment_device, segment_values);
    copy_host_to_device(polygon_device, polygon_values);
    copy_host_to_device(vertex_device, vertex_values);
    copy_host_to_device(aabb_device, aabb_values);
    RtdlHiprtPipDataDevice pip_data{reinterpret_cast<const RtdlHiprtPolygonRefDevice*>(polygon_device.get()),
                                    reinterpret_cast<const RtdlHiprtVertex2DDevice*>(vertex_device.get())};
    check_oro("oroMemcpyHtoD", oroMemcpyHtoD(pip_data_device.oro_ptr(), &pip_data, sizeof(pip_data)));

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlSegmentPolygon2D";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = pip_data_device.get();
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));

        void* segment_device_ptr = segment_device.get();
        void* polygon_device_ptr = polygon_device.get();
        uint32_t segment_count_u32 = static_cast<uint32_t>(segment_count);
        uint32_t polygon_count_u32 = static_cast<uint32_t>(polygon_count);
        uint32_t block_size = 128;
        uint32_t grid_size = static_cast<uint32_t>((segment_count + block_size - 1) / block_size);

        if (anyhit_rows) {
            oroFunction kernel = build_trace_kernel_from_source(
                runtime.context,
                segment_polygon_2d_kernel_source(),
                "rtdl_hiprt_segment_polygon_2d.cu",
                "RtdlSegmentPolygonAnyhit2DKernel",
                &func_name_set,
                1,
                1);
            const size_t output_capacity = segment_count * polygon_count;
            std::vector<RtdlSegmentPolygonAnyHitRow> output(output_capacity);
            std::vector<uint32_t> counts(segment_count);
            DeviceAllocation output_device(output.size() * sizeof(RtdlSegmentPolygonAnyHitRow));
            DeviceAllocation counts_device(counts.size() * sizeof(uint32_t));
            void* output_device_ptr = output_device.get();
            void* counts_device_ptr = counts_device.get();
            void* args[] = {
                &geometry,
                &segment_device_ptr,
                &polygon_device_ptr,
                &segment_count_u32,
                &polygon_count_u32,
                &output_device_ptr,
                &counts_device_ptr,
                &func_table,
            };
            check_oro(
                "oroModuleLaunchKernel",
                oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
            copy_device_to_host(output, output_device);
            copy_device_to_host(counts, counts_device);

            std::vector<RtdlSegmentPolygonAnyHitRow> compacted;
            for (size_t segment_index = 0; segment_index < segment_count; ++segment_index) {
                const uint32_t count = std::min<uint32_t>(counts[segment_index], static_cast<uint32_t>(polygon_count));
                const size_t base = segment_index * polygon_count;
                for (uint32_t rank = 0; rank < count; ++rank) {
                    compacted.push_back(output[base + rank]);
                }
            }
            sort_segment_polygon_anyhit_rows_by_input_order(compacted, segments, segment_count, polygons, polygon_count);
            *anyhit_rows_out = copy_segment_polygon_anyhit_rows_to_heap(compacted);
            *row_count_out = compacted.size();
        } else {
            oroFunction kernel = build_trace_kernel_from_source(
                runtime.context,
                segment_polygon_2d_kernel_source(),
                "rtdl_hiprt_segment_polygon_2d.cu",
                "RtdlSegmentPolygonHitcount2DKernel",
                &func_name_set,
                1,
                1);
            std::vector<RtdlSegmentPolygonHitCountRow> output(segment_count);
            DeviceAllocation output_device(output.size() * sizeof(RtdlSegmentPolygonHitCountRow));
            void* output_device_ptr = output_device.get();
            void* args[] = {
                &geometry,
                &segment_device_ptr,
                &segment_count_u32,
                &output_device_ptr,
                &func_table,
            };
            check_oro(
                "oroModuleLaunchKernel",
                oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
            copy_device_to_host(output, output_device);
            *hitcount_rows_out = copy_segment_polygon_hitcount_rows_to_heap(output);
            *row_count_out = output.size();
        }
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
}

void run_segment_polygon_hitcount_2d(
    const RtdlSegment* segments,
    size_t segment_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    RtdlSegmentPolygonHitCountRow** rows_out,
    size_t* row_count_out) {
    RtdlSegmentPolygonAnyHitRow* unused = nullptr;
    run_segment_polygon_2d_common(
        segments,
        segment_count,
        polygons,
        polygon_count,
        vertices_xy,
        vertex_xy_count,
        false,
        rows_out,
        &unused,
        row_count_out);
}

void run_segment_polygon_anyhit_rows_2d(
    const RtdlSegment* segments,
    size_t segment_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    RtdlSegmentPolygonAnyHitRow** rows_out,
    size_t* row_count_out) {
    RtdlSegmentPolygonHitCountRow* unused = nullptr;
    run_segment_polygon_2d_common(
        segments,
        segment_count,
        polygons,
        polygon_count,
        vertices_xy,
        vertex_xy_count,
        true,
        &unused,
        rows_out,
        row_count_out);
}

void run_ray_hitcount_2d(
    const RtdlRay2D* rays,
    size_t ray_count,
    const RtdlTriangle* triangles,
    size_t triangle_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out) {
    if (ray_count > std::numeric_limits<uint32_t>::max() || triangle_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT 2D ray_triangle_hit_count currently supports at most 2^32-1 rays/triangles");
    }
    if (ray_count > 0 && rays == nullptr) {
        throw std::runtime_error("ray pointer must not be null when ray_count is nonzero");
    }
    if (triangle_count > 0 && triangles == nullptr) {
        throw std::runtime_error("triangle pointer must not be null when triangle_count is nonzero");
    }
    if (ray_count == 0) {
        std::vector<RtdlRayHitCountRow> empty;
        *rows_out = copy_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }
    if (triangle_count == 0) {
        std::vector<RtdlRayHitCountRow> output;
        output.reserve(ray_count);
        for (size_t i = 0; i < ray_count; ++i) {
            output.push_back({rays[i].id, 0u});
        }
        *rows_out = copy_rows_to_heap(output);
        *row_count_out = output.size();
        return;
    }

    std::vector<RtdlHiprtRay2DDevice> ray_values = encode_rays_2d(rays, ray_count);
    std::vector<RtdlHiprtTriangle2DDevice> triangle_values = encode_triangles_2d(triangles, triangle_count);
    std::vector<RtdlHiprtAabb> aabb_values = encode_triangle_2d_aabbs(triangle_values.data(), triangle_values.size());

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation ray_device(ray_values.size() * sizeof(RtdlHiprtRay2DDevice));
    DeviceAllocation triangle_device(triangle_values.size() * sizeof(RtdlHiprtTriangle2DDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    copy_host_to_device(ray_device, ray_values);
    copy_host_to_device(triangle_device, triangle_values);
    copy_host_to_device(aabb_device, aabb_values);

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlTriangle2D";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = triangle_device.get();
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            ray_hitcount_2d_kernel_source(),
            "rtdl_hiprt_ray_hitcount_2d.cu",
            "RtdlRayHitcount2DKernel",
            &func_name_set,
            1,
            1);

        std::vector<RtdlRayHitCountRow> output(ray_count);
        DeviceAllocation output_device(output.size() * sizeof(RtdlRayHitCountRow));
        void* ray_device_ptr = ray_device.get();
        void* output_device_ptr = output_device.get();
        uint32_t ray_count_u32 = static_cast<uint32_t>(ray_count);
        uint32_t block_size = 128;
        uint32_t grid_size = static_cast<uint32_t>((ray_count + block_size - 1) / block_size);
        void* args[] = {
            &geometry,
            &ray_device_ptr,
            &ray_count_u32,
            &output_device_ptr,
            &func_table,
        };
        check_oro(
            "oroModuleLaunchKernel",
            oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
        copy_device_to_host(output, output_device);

        *rows_out = copy_rows_to_heap(output);
        *row_count_out = output.size();
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
}

void run_pip_2d(
    const RtdlPoint* points,
    size_t point_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    RtdlPipRow** rows_out,
    size_t* row_count_out) {
    if (point_count > std::numeric_limits<uint32_t>::max() || polygon_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT point_in_polygon currently supports at most 2^32-1 points/polygons");
    }
    if (point_count != 0 && polygon_count > std::numeric_limits<size_t>::max() / point_count) {
        throw std::runtime_error("HIPRT point_in_polygon output capacity overflow");
    }
    if (point_count > 0 && points == nullptr) {
        throw std::runtime_error("point pointer must not be null when point_count is nonzero");
    }
    if (polygon_count > 0 && polygons == nullptr) {
        throw std::runtime_error("polygon pointer must not be null when polygon_count is nonzero");
    }
    if (vertex_xy_count % 2 != 0) {
        throw std::runtime_error("polygon vertex_xy_count must be even");
    }
    if (vertex_xy_count > 0 && vertices_xy == nullptr) {
        throw std::runtime_error("polygon vertices pointer must not be null when vertex_xy_count is nonzero");
    }
    if (point_count == 0 || polygon_count == 0) {
        std::vector<RtdlPipRow> empty;
        *rows_out = copy_pip_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }

    std::vector<RtdlHiprtPoint2DDevice> point_values = encode_points_2d(points, point_count);
    std::vector<RtdlHiprtPolygonRefDevice> polygon_values = encode_polygon_refs_2d(polygons, polygon_count);
    std::vector<RtdlHiprtVertex2DDevice> vertex_values = encode_vertices_2d(vertices_xy, vertex_xy_count);
    std::vector<RtdlHiprtAabb> aabb_values =
        encode_polygon_aabbs(polygon_values.data(), polygon_values.size(), vertex_values.data(), vertex_values.size());

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation point_device(point_values.size() * sizeof(RtdlHiprtPoint2DDevice));
    DeviceAllocation polygon_device(polygon_values.size() * sizeof(RtdlHiprtPolygonRefDevice));
    DeviceAllocation vertex_device(vertex_values.size() * sizeof(RtdlHiprtVertex2DDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    DeviceAllocation pip_data_device(sizeof(RtdlHiprtPipDataDevice));
    copy_host_to_device(point_device, point_values);
    copy_host_to_device(polygon_device, polygon_values);
    copy_host_to_device(vertex_device, vertex_values);
    copy_host_to_device(aabb_device, aabb_values);
    RtdlHiprtPipDataDevice pip_data{reinterpret_cast<const RtdlHiprtPolygonRefDevice*>(polygon_device.get()),
                                    reinterpret_cast<const RtdlHiprtVertex2DDevice*>(vertex_device.get())};
    check_oro("oroMemcpyHtoD", oroMemcpyHtoD(pip_data_device.oro_ptr(), &pip_data, sizeof(pip_data)));

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlPolygon2D";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = pip_data_device.get();
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            pip_2d_kernel_source(),
            "rtdl_hiprt_pip_2d.cu",
            "RtdlPip2DKernel",
            &func_name_set,
            1,
            1);

        const size_t output_capacity = point_count * polygon_count;
        std::vector<RtdlPipRow> output(output_capacity);
        DeviceAllocation output_device(output.size() * sizeof(RtdlPipRow));
        void* point_device_ptr = point_device.get();
        void* polygon_device_ptr = polygon_device.get();
        void* output_device_ptr = output_device.get();
        uint32_t point_count_u32 = static_cast<uint32_t>(point_count);
        uint32_t polygon_count_u32 = static_cast<uint32_t>(polygon_count);
        uint32_t block_size = 128;
        uint32_t grid_size = static_cast<uint32_t>((point_count + block_size - 1) / block_size);
        void* args[] = {
            &geometry,
            &point_device_ptr,
            &polygon_device_ptr,
            &point_count_u32,
            &polygon_count_u32,
            &output_device_ptr,
            &func_table,
        };
        check_oro(
            "oroModuleLaunchKernel",
            oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
        copy_device_to_host(output, output_device);
        *rows_out = copy_pip_rows_to_heap(output);
        *row_count_out = output.size();
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
}

void run_overlay_2d(
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count,
    RtdlOverlayRow** rows_out,
    size_t* row_count_out) {
    if (left_count > std::numeric_limits<uint32_t>::max() || right_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT overlay_compose currently supports at most 2^32-1 left/right polygons");
    }
    if (left_count != 0 && right_count > std::numeric_limits<size_t>::max() / left_count) {
        throw std::runtime_error("HIPRT overlay_compose output capacity overflow");
    }
    if (left_count > 0 && left_polygons == nullptr) {
        throw std::runtime_error("left polygon pointer must not be null when left_count is nonzero");
    }
    if (right_count > 0 && right_polygons == nullptr) {
        throw std::runtime_error("right polygon pointer must not be null when right_count is nonzero");
    }
    if (left_vertex_xy_count % 2 != 0 || right_vertex_xy_count % 2 != 0) {
        throw std::runtime_error("polygon vertex_xy_count must be even");
    }
    if (left_vertex_xy_count > 0 && left_vertices_xy == nullptr) {
        throw std::runtime_error("left polygon vertices pointer must not be null when vertex count is nonzero");
    }
    if (right_vertex_xy_count > 0 && right_vertices_xy == nullptr) {
        throw std::runtime_error("right polygon vertices pointer must not be null when vertex count is nonzero");
    }
    if (left_count == 0 || right_count == 0) {
        std::vector<RtdlOverlayRow> empty;
        *rows_out = copy_overlay_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }

    std::vector<RtdlHiprtPolygonRefDevice> left_values = encode_polygon_refs_2d(left_polygons, left_count);
    std::vector<RtdlHiprtVertex2DDevice> left_vertex_values = encode_vertices_2d(left_vertices_xy, left_vertex_xy_count);
    std::vector<RtdlHiprtPolygonRefDevice> right_values = encode_polygon_refs_2d(right_polygons, right_count);
    std::vector<RtdlHiprtVertex2DDevice> right_vertex_values = encode_vertices_2d(right_vertices_xy, right_vertex_xy_count);
    std::vector<RtdlHiprtAabb> aabb_values = encode_overlay_candidate_aabbs(
        right_values.data(),
        right_values.size(),
        left_values.data(),
        left_values.size(),
        left_vertex_values.data(),
        left_vertex_values.size());

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation left_device(left_values.size() * sizeof(RtdlHiprtPolygonRefDevice));
    DeviceAllocation left_vertex_device(left_vertex_values.size() * sizeof(RtdlHiprtVertex2DDevice));
    DeviceAllocation right_device(right_values.size() * sizeof(RtdlHiprtPolygonRefDevice));
    DeviceAllocation right_vertex_device(right_vertex_values.size() * sizeof(RtdlHiprtVertex2DDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    copy_host_to_device(left_device, left_values);
    copy_host_to_device(left_vertex_device, left_vertex_values);
    copy_host_to_device(right_device, right_values);
    copy_host_to_device(right_vertex_device, right_vertex_values);
    copy_host_to_device(aabb_device, aabb_values);

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlOverlayCandidate2D";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = nullptr;
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            overlay_2d_kernel_source(),
            "rtdl_hiprt_overlay_2d.cu",
            "RtdlOverlay2DKernel",
            &func_name_set,
            1,
            1);

        const size_t output_capacity = left_count * right_count;
        std::vector<RtdlOverlayRow> output(output_capacity);
        DeviceAllocation output_device(output.size() * sizeof(RtdlOverlayRow));
        void* left_device_ptr = left_device.get();
        void* left_vertex_device_ptr = left_vertex_device.get();
        void* right_device_ptr = right_device.get();
        void* right_vertex_device_ptr = right_vertex_device.get();
        void* output_device_ptr = output_device.get();
        uint32_t left_count_u32 = static_cast<uint32_t>(left_count);
        uint32_t right_count_u32 = static_cast<uint32_t>(right_count);
        uint32_t block_size = 128;
        uint32_t grid_size = static_cast<uint32_t>((left_count + block_size - 1) / block_size);
        void* args[] = {
            &geometry,
            &left_device_ptr,
            &left_vertex_device_ptr,
            &right_device_ptr,
            &right_vertex_device_ptr,
            &left_count_u32,
            &right_count_u32,
            &output_device_ptr,
            &func_table,
        };
        check_oro(
            "oroModuleLaunchKernel",
            oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
        copy_device_to_host(output, output_device);
        *rows_out = copy_overlay_rows_to_heap(output);
        *row_count_out = output.size();
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
}

void run_point_nearest_segment_2d(
    const RtdlPoint* points,
    size_t point_count,
    const RtdlSegment* segments,
    size_t segment_count,
    RtdlPointNearestSegmentRow** rows_out,
    size_t* row_count_out) {
    if (point_count > std::numeric_limits<uint32_t>::max() || segment_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT point_nearest_segment currently supports at most 2^32-1 points/segments");
    }
    if (point_count > 0 && points == nullptr) {
        throw std::runtime_error("point pointer must not be null when point_count is nonzero");
    }
    if (segment_count > 0 && segments == nullptr) {
        throw std::runtime_error("segment pointer must not be null when segment_count is nonzero");
    }
    if (point_count == 0 || segment_count == 0) {
        std::vector<RtdlPointNearestSegmentRow> empty;
        *rows_out = copy_pns_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }

    std::vector<RtdlHiprtPoint2DDevice> point_values = encode_points_2d(points, point_count);
    std::vector<RtdlHiprtSegmentDevice> segment_values = encode_segments(segments, segment_count);
    const float radius = global_point_segment_radius(point_values.data(), point_values.size(), segment_values.data(), segment_values.size());
    std::vector<RtdlHiprtAabb> aabb_values = encode_segment_expanded_aabbs(segment_values.data(), segment_values.size(), radius);
    RtdlHiprtPointSegmentParams params{radius};

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation point_device(point_values.size() * sizeof(RtdlHiprtPoint2DDevice));
    DeviceAllocation segment_device(segment_values.size() * sizeof(RtdlHiprtSegmentDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    DeviceAllocation params_device(sizeof(RtdlHiprtPointSegmentParams));
    copy_host_to_device(point_device, point_values);
    copy_host_to_device(segment_device, segment_values);
    copy_host_to_device(aabb_device, aabb_values);
    check_oro("oroMemcpyHtoD", oroMemcpyHtoD(params_device.oro_ptr(), &params, sizeof(params)));

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlPointSegmentDistance2D";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = segment_device.get();
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            point_nearest_segment_2d_kernel_source(),
            "rtdl_hiprt_point_nearest_segment_2d.cu",
            "RtdlPointNearestSegment2DKernel",
            &func_name_set,
            1,
            1);

        std::vector<RtdlPointNearestSegmentRow> output(point_count);
        std::vector<uint32_t> has_row(point_count);
        DeviceAllocation output_device(output.size() * sizeof(RtdlPointNearestSegmentRow));
        DeviceAllocation has_row_device(has_row.size() * sizeof(uint32_t));
        void* point_device_ptr = point_device.get();
        void* segment_device_ptr = segment_device.get();
        void* output_device_ptr = output_device.get();
        void* has_row_device_ptr = has_row_device.get();
        void* params_device_ptr = params_device.get();
        uint32_t point_count_u32 = static_cast<uint32_t>(point_count);
        uint32_t block_size = 128;
        uint32_t grid_size = static_cast<uint32_t>((point_count + block_size - 1) / block_size);
        void* args[] = {
            &geometry,
            &point_device_ptr,
            &segment_device_ptr,
            &point_count_u32,
            &output_device_ptr,
            &has_row_device_ptr,
            &params_device_ptr,
            &func_table,
        };
        check_oro(
            "oroModuleLaunchKernel",
            oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
        copy_device_to_host(output, output_device);
        copy_device_to_host(has_row, has_row_device);

        std::vector<RtdlPointNearestSegmentRow> compacted;
        for (size_t i = 0; i < point_count; ++i) {
            if (has_row[i] != 0u) {
                compacted.push_back(output[i]);
            }
        }
        *rows_out = copy_pns_rows_to_heap(compacted);
        *row_count_out = compacted.size();
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
}

void run_bfs_expand(
    const RtdlFrontierVertex* frontier,
    size_t frontier_count,
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t edge_count,
    uint32_t vertex_count,
    const uint32_t* visited,
    size_t visited_count,
    bool dedupe,
    RtdlBfsRow** rows_out,
    size_t* row_count_out) {
    if (frontier_count > std::numeric_limits<uint32_t>::max() ||
        edge_count > std::numeric_limits<uint32_t>::max() ||
        visited_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT bfs_discover currently supports at most 2^32-1 frontier/edge/visited rows");
    }
    if (frontier_count != 0 && edge_count > std::numeric_limits<size_t>::max() / frontier_count) {
        throw std::runtime_error("HIPRT bfs_discover output capacity overflow");
    }
    if (frontier_count > 0 && frontier == nullptr) {
        throw std::runtime_error("frontier pointer must not be null when frontier_count is nonzero");
    }
    if (row_offset_count > 0 && row_offsets == nullptr) {
        throw std::runtime_error("row_offsets pointer must not be null when row_offset_count is nonzero");
    }
    if (edge_count > 0 && column_indices == nullptr) {
        throw std::runtime_error("column_indices pointer must not be null when edge_count is nonzero");
    }
    if (visited_count > 0 && visited == nullptr) {
        throw std::runtime_error("visited pointer must not be null when visited_count is nonzero");
    }
    for (size_t i = 0; i < frontier_count; ++i) {
        if (frontier[i].vertex_id >= vertex_count) {
            throw std::runtime_error("HIPRT bfs_discover frontier vertex_id must be a valid graph vertex");
        }
    }
    for (size_t i = 0; i < visited_count; ++i) {
        if (visited[i] >= vertex_count) {
            throw std::runtime_error("HIPRT bfs_discover visited vertices must be valid graph vertex IDs");
        }
    }

    std::vector<RtdlHiprtGraphEdgeDevice> edge_values =
        encode_graph_edges(row_offsets, row_offset_count, column_indices, edge_count, vertex_count);
    if (frontier_count == 0 || edge_values.empty()) {
        std::vector<RtdlBfsRow> empty;
        *rows_out = copy_bfs_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }
    std::vector<RtdlHiprtAabb> aabb_values = encode_graph_edge_source_aabbs(edge_values.data(), edge_values.size());

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    std::vector<RtdlFrontierVertex> frontier_values(frontier, frontier + frontier_count);
    std::vector<uint32_t> visited_values(visited, visited + visited_count);
    std::vector<uint32_t> discovered(vertex_count, 0u);
    std::vector<uint32_t> row_count_device_host(1, 0u);

    DeviceAllocation frontier_device(frontier_values.size() * sizeof(RtdlFrontierVertex));
    DeviceAllocation visited_device(visited_values.size() * sizeof(uint32_t));
    DeviceAllocation edge_device(edge_values.size() * sizeof(RtdlHiprtGraphEdgeDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    DeviceAllocation discovered_device(discovered.size() * sizeof(uint32_t));
    DeviceAllocation row_count_device(sizeof(uint32_t));
    copy_host_to_device(frontier_device, frontier_values);
    copy_host_to_device(visited_device, visited_values);
    copy_host_to_device(edge_device, edge_values);
    copy_host_to_device(aabb_device, aabb_values);
    copy_host_to_device(discovered_device, discovered);
    copy_host_to_device(row_count_device, row_count_device_host);

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlGraphEdgeBySource";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = nullptr;
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            bfs_expand_kernel_source(),
            "rtdl_hiprt_bfs_expand.cu",
            "RtdlBfsExpandKernel",
            &func_name_set,
            1,
            1);

        const size_t output_capacity = frontier_count * edge_values.size();
        std::vector<RtdlBfsRow> output(output_capacity);
        DeviceAllocation output_device(output.size() * sizeof(RtdlBfsRow));
        void* frontier_device_ptr = frontier_device.get();
        void* visited_device_ptr = visited_device.get();
        void* edge_device_ptr = edge_device.get();
        void* discovered_device_ptr = discovered_device.get();
        void* output_device_ptr = output_device.get();
        void* row_count_device_ptr = row_count_device.get();
        uint32_t frontier_count_u32 = static_cast<uint32_t>(frontier_count);
        uint32_t visited_count_u32 = static_cast<uint32_t>(visited_count);
        uint32_t edge_count_u32 = static_cast<uint32_t>(edge_values.size());
        uint32_t dedupe_u32 = dedupe ? 1u : 0u;
        uint32_t block_size = 128;
        uint32_t grid_size = static_cast<uint32_t>((frontier_count + block_size - 1) / block_size);
        void* args[] = {
            &geometry,
            &frontier_device_ptr,
            &frontier_count_u32,
            &visited_device_ptr,
            &visited_count_u32,
            &edge_device_ptr,
            &edge_count_u32,
            &discovered_device_ptr,
            &vertex_count,
            &dedupe_u32,
            &output_device_ptr,
            &row_count_device_ptr,
            &func_table,
        };
        check_oro(
            "oroModuleLaunchKernel",
            oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
        copy_device_to_host(row_count_device_host, row_count_device);
        const uint32_t produced = std::min<uint32_t>(row_count_device_host[0], static_cast<uint32_t>(output.size()));
        output.resize(produced);
        copy_device_to_host(output, output_device);
        std::sort(output.begin(), output.end(), [](const RtdlBfsRow& a, const RtdlBfsRow& b) {
            if (a.level != b.level) {
                return a.level < b.level;
            }
            if (a.dst_vertex != b.dst_vertex) {
                return a.dst_vertex < b.dst_vertex;
            }
            return a.src_vertex < b.src_vertex;
        });
        *rows_out = copy_bfs_rows_to_heap(output);
        *row_count_out = output.size();
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
}

std::unique_ptr<PreparedGraphCSR> prepare_graph_csr(
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t edge_count,
    uint32_t vertex_count) {
    if (row_offset_count == 0 || row_offsets == nullptr) {
        throw std::runtime_error("HIPRT prepared graph CSR row_offsets must not be empty");
    }
    if (edge_count > 0 && column_indices == nullptr) {
        throw std::runtime_error("HIPRT prepared graph CSR column_indices pointer must not be null when edge_count is nonzero");
    }
    if (row_offset_count - 1u != vertex_count) {
        throw std::runtime_error("HIPRT prepared graph CSR row_offset_count must equal vertex_count + 1");
    }
    if (edge_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT prepared graph CSR currently supports at most 2^32-1 edges");
    }
    std::vector<RtdlHiprtGraphEdgeDevice> edge_values =
        encode_graph_edges(row_offsets, row_offset_count, column_indices, edge_count, vertex_count);
    if (edge_values.empty()) {
        throw std::runtime_error("prepared HIPRT graph CSR requires at least one edge");
    }
    std::vector<RtdlHiprtAabb> aabb_values = encode_graph_edge_source_aabbs(edge_values.data(), edge_values.size());
    std::vector<uint32_t> row_offset_values(row_offsets, row_offsets + row_offset_count);
    std::vector<uint32_t> column_values(column_indices, column_indices + edge_count);

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation row_offset_device(row_offset_values.size() * sizeof(uint32_t));
    DeviceAllocation column_device(column_values.size() * sizeof(uint32_t));
    DeviceAllocation edge_device(edge_values.size() * sizeof(RtdlHiprtGraphEdgeDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    copy_host_to_device(row_offset_device, row_offset_values);
    copy_host_to_device(column_device, column_values);
    copy_host_to_device(edge_device, edge_values);
    copy_host_to_device(aabb_device, aabb_values);

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable bfs_func_table{};
    hiprtFuncTable triangle_func_table{};
    try {
        hiprtFuncNameSet bfs_func_name_set{};
        bfs_func_name_set.intersectFuncName = "intersectRtdlGraphEdgeBySource";
        hiprtFuncDataSet bfs_func_data_set{};
        bfs_func_data_set.intersectFuncData = nullptr;
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, bfs_func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, bfs_func_table, 0, 0, bfs_func_data_set));
        oroFunction bfs_kernel = build_trace_kernel_from_source(
            runtime.context,
            bfs_expand_kernel_source(),
            "rtdl_hiprt_bfs_expand.cu",
            "RtdlBfsExpandKernel",
            &bfs_func_name_set,
            1,
            1);

        hiprtFuncNameSet triangle_func_name_set{};
        triangle_func_name_set.intersectFuncName = "intersectRtdlTriangleGraphEdgeBySource";
        hiprtFuncDataSet triangle_func_data_set{};
        triangle_func_data_set.intersectFuncData = nullptr;
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, triangle_func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, triangle_func_table, 0, 0, triangle_func_data_set));
        oroFunction triangle_kernel = build_trace_kernel_from_source(
            runtime.context,
            triangle_probe_kernel_source(),
            "rtdl_hiprt_triangle_probe.cu",
            "RtdlTriangleProbeKernel",
            &triangle_func_name_set,
            1,
            1);

        auto prepared = std::make_unique<PreparedGraphCSR>(
            std::move(runtime),
            std::move(row_offset_device),
            std::move(column_device),
            std::move(edge_device),
            std::move(aabb_device),
            geometry,
            bfs_func_table,
            triangle_func_table,
            bfs_kernel,
            triangle_kernel,
            vertex_count,
            static_cast<uint32_t>(edge_values.size()));
        geometry = nullptr;
        bfs_func_table = nullptr;
        triangle_func_table = nullptr;
        return prepared;
    } catch (...) {
        if (bfs_func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, bfs_func_table);
        }
        if (triangle_func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, triangle_func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
}

void run_prepared_bfs_expand(
    PreparedGraphCSR& prepared,
    const RtdlFrontierVertex* frontier,
    size_t frontier_count,
    const uint32_t* visited,
    size_t visited_count,
    bool dedupe,
    RtdlBfsRow** rows_out,
    size_t* row_count_out) {
    if (frontier_count > std::numeric_limits<uint32_t>::max() ||
        visited_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT prepared bfs_discover currently supports at most 2^32-1 frontier/visited rows");
    }
    if (frontier_count != 0 && static_cast<size_t>(prepared.edge_count) > std::numeric_limits<size_t>::max() / frontier_count) {
        throw std::runtime_error("HIPRT prepared bfs_discover output capacity overflow");
    }
    if (frontier_count > 0 && frontier == nullptr) {
        throw std::runtime_error("frontier pointer must not be null when frontier_count is nonzero");
    }
    if (visited_count > 0 && visited == nullptr) {
        throw std::runtime_error("visited pointer must not be null when visited_count is nonzero");
    }
    for (size_t i = 0; i < frontier_count; ++i) {
        if (frontier[i].vertex_id >= prepared.vertex_count) {
            throw std::runtime_error("HIPRT prepared bfs_discover frontier vertex_id must be a valid graph vertex");
        }
    }
    for (size_t i = 0; i < visited_count; ++i) {
        if (visited[i] >= prepared.vertex_count) {
            throw std::runtime_error("HIPRT prepared bfs_discover visited vertices must be valid graph vertex IDs");
        }
    }
    if (frontier_count == 0 || prepared.edge_count == 0) {
        std::vector<RtdlBfsRow> empty;
        *rows_out = copy_bfs_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }

    std::vector<RtdlFrontierVertex> frontier_values(frontier, frontier + frontier_count);
    std::vector<uint32_t> visited_values(visited, visited + visited_count);
    std::vector<uint32_t> discovered(prepared.vertex_count, 0u);
    std::vector<uint32_t> row_count_device_host(1, 0u);
    DeviceAllocation frontier_device(frontier_values.size() * sizeof(RtdlFrontierVertex));
    DeviceAllocation visited_device(visited_values.size() * sizeof(uint32_t));
    DeviceAllocation discovered_device(discovered.size() * sizeof(uint32_t));
    DeviceAllocation row_count_device(sizeof(uint32_t));
    copy_host_to_device(frontier_device, frontier_values);
    copy_host_to_device(visited_device, visited_values);
    copy_host_to_device(discovered_device, discovered);
    copy_host_to_device(row_count_device, row_count_device_host);

    const size_t output_capacity = frontier_count * static_cast<size_t>(prepared.edge_count);
    std::vector<RtdlBfsRow> output(output_capacity);
    DeviceAllocation output_device(output.size() * sizeof(RtdlBfsRow));
    void* frontier_device_ptr = frontier_device.get();
    void* visited_device_ptr = visited_device.get();
    void* edge_device_ptr = prepared.edge_device.get();
    void* discovered_device_ptr = discovered_device.get();
    void* output_device_ptr = output_device.get();
    void* row_count_device_ptr = row_count_device.get();
    uint32_t frontier_count_u32 = static_cast<uint32_t>(frontier_count);
    uint32_t visited_count_u32 = static_cast<uint32_t>(visited_count);
    uint32_t dedupe_u32 = dedupe ? 1u : 0u;
    uint32_t block_size = 128;
    uint32_t grid_size = static_cast<uint32_t>((frontier_count + block_size - 1) / block_size);
    void* args[] = {
        &prepared.geometry,
        &frontier_device_ptr,
        &frontier_count_u32,
        &visited_device_ptr,
        &visited_count_u32,
        &edge_device_ptr,
        &prepared.edge_count,
        &discovered_device_ptr,
        &prepared.vertex_count,
        &dedupe_u32,
        &output_device_ptr,
        &row_count_device_ptr,
        &prepared.bfs_func_table,
    };
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(prepared.bfs_kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
    copy_device_to_host(row_count_device_host, row_count_device);
    const uint32_t produced = std::min<uint32_t>(row_count_device_host[0], static_cast<uint32_t>(output.size()));
    output.resize(produced);
    copy_device_to_host(output, output_device);
    std::sort(output.begin(), output.end(), [](const RtdlBfsRow& a, const RtdlBfsRow& b) {
        if (a.level != b.level) {
            return a.level < b.level;
        }
        if (a.dst_vertex != b.dst_vertex) {
            return a.dst_vertex < b.dst_vertex;
        }
        return a.src_vertex < b.src_vertex;
    });
    *rows_out = copy_bfs_rows_to_heap(output);
    *row_count_out = output.size();
}

void run_triangle_probe(
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t edge_count,
    const RtdlEdgeSeed* seeds,
    size_t seed_count,
    bool enforce_id_ascending,
    bool unique,
    RtdlTriangleRow** rows_out,
    size_t* row_count_out) {
    if (row_offset_count == 0 || row_offsets == nullptr) {
        throw std::runtime_error("HIPRT triangle_match CSR row_offsets must not be empty");
    }
    if (edge_count > 0 && column_indices == nullptr) {
        throw std::runtime_error("HIPRT triangle_match column_indices pointer must not be null when edge_count is nonzero");
    }
    if (seed_count > 0 && seeds == nullptr) {
        throw std::runtime_error("HIPRT triangle_match seed pointer must not be null when seed_count is nonzero");
    }
    if (row_offset_count - 1u > std::numeric_limits<uint32_t>::max() ||
        edge_count > std::numeric_limits<uint32_t>::max() ||
        seed_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT triangle_match currently supports at most 2^32-1 vertices/edges/seeds");
    }
    if (seed_count != 0 && edge_count > std::numeric_limits<size_t>::max() / seed_count) {
        throw std::runtime_error("HIPRT triangle_match output capacity overflow");
    }
    uint32_t vertex_count = static_cast<uint32_t>(row_offset_count - 1u);
    std::vector<RtdlHiprtGraphEdgeDevice> edge_values =
        encode_graph_edges(row_offsets, row_offset_count, column_indices, edge_count, vertex_count);
    for (size_t i = 0; i < seed_count; ++i) {
        if (seeds[i].u >= vertex_count || seeds[i].v >= vertex_count) {
            throw std::runtime_error("HIPRT triangle_match edge seed vertices must be valid graph vertex IDs");
        }
    }
    if (seed_count == 0 || edge_values.empty()) {
        std::vector<RtdlTriangleRow> empty;
        *rows_out = copy_triangle_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }
    std::vector<RtdlHiprtAabb> aabb_values = encode_graph_edge_source_aabbs(edge_values.data(), edge_values.size());
    std::vector<uint32_t> row_offset_values(row_offsets, row_offsets + row_offset_count);
    std::vector<uint32_t> column_values(column_indices, column_indices + edge_count);
    std::vector<RtdlEdgeSeed> seed_values(seeds, seeds + seed_count);
    std::vector<uint32_t> row_count_device_host(1, 0u);

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation row_offset_device(row_offset_values.size() * sizeof(uint32_t));
    DeviceAllocation column_device(column_values.size() * sizeof(uint32_t));
    DeviceAllocation seed_device(seed_values.size() * sizeof(RtdlEdgeSeed));
    DeviceAllocation edge_device(edge_values.size() * sizeof(RtdlHiprtGraphEdgeDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    DeviceAllocation row_count_device(sizeof(uint32_t));
    copy_host_to_device(row_offset_device, row_offset_values);
    copy_host_to_device(column_device, column_values);
    copy_host_to_device(seed_device, seed_values);
    copy_host_to_device(edge_device, edge_values);
    copy_host_to_device(aabb_device, aabb_values);
    copy_host_to_device(row_count_device, row_count_device_host);

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlTriangleGraphEdgeBySource";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = nullptr;
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            triangle_probe_kernel_source(),
            "rtdl_hiprt_triangle_probe.cu",
            "RtdlTriangleProbeKernel",
            &func_name_set,
            1,
            1);

        const size_t output_capacity = seed_count * edge_values.size();
        std::vector<RtdlHiprtTriangleCandidateRow> candidates(output_capacity);
        DeviceAllocation candidate_device(candidates.size() * sizeof(RtdlHiprtTriangleCandidateRow));
        void* seed_device_ptr = seed_device.get();
        void* row_offset_device_ptr = row_offset_device.get();
        void* column_device_ptr = column_device.get();
        void* edge_device_ptr = edge_device.get();
        void* candidate_device_ptr = candidate_device.get();
        void* row_count_device_ptr = row_count_device.get();
        uint32_t seed_count_u32 = static_cast<uint32_t>(seed_count);
        uint32_t edge_count_u32 = static_cast<uint32_t>(edge_values.size());
        uint32_t enforce_u32 = enforce_id_ascending ? 1u : 0u;
        uint32_t block_size = 128;
        uint32_t grid_size = static_cast<uint32_t>((seed_count + block_size - 1) / block_size);
        void* args[] = {
            &geometry,
            &seed_device_ptr,
            &seed_count_u32,
            &row_offset_device_ptr,
            &column_device_ptr,
            &edge_device_ptr,
            &edge_count_u32,
            &vertex_count,
            &enforce_u32,
            &candidate_device_ptr,
            &row_count_device_ptr,
            &func_table,
        };
        check_oro(
            "oroModuleLaunchKernel",
            oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
        copy_device_to_host(row_count_device_host, row_count_device);
        const uint32_t produced = std::min<uint32_t>(row_count_device_host[0], static_cast<uint32_t>(candidates.size()));
        candidates.resize(produced);
        copy_device_to_host(candidates, candidate_device);
        std::sort(candidates.begin(), candidates.end(), [](const RtdlHiprtTriangleCandidateRow& a, const RtdlHiprtTriangleCandidateRow& b) {
            if (a.seed_index != b.seed_index) {
                return a.seed_index < b.seed_index;
            }
            if (a.w != b.w) {
                return a.w < b.w;
            }
            if (a.u != b.u) {
                return a.u < b.u;
            }
            return a.v < b.v;
        });

        std::vector<RtdlTriangleRow> output;
        output.reserve(candidates.size());
        for (const RtdlHiprtTriangleCandidateRow& candidate : candidates) {
            RtdlTriangleRow row{candidate.u, candidate.v, candidate.w};
            if (unique) {
                const bool seen = std::any_of(output.begin(), output.end(), [&](const RtdlTriangleRow& existing) {
                    return existing.u == row.u && existing.v == row.v && existing.w == row.w;
                });
                if (seen) {
                    continue;
                }
            }
            output.push_back(row);
        }
        *rows_out = copy_triangle_rows_to_heap(output);
        *row_count_out = output.size();
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
}

void run_prepared_triangle_probe(
    PreparedGraphCSR& prepared,
    const RtdlEdgeSeed* seeds,
    size_t seed_count,
    bool enforce_id_ascending,
    bool unique,
    RtdlTriangleRow** rows_out,
    size_t* row_count_out) {
    if (seed_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT prepared triangle_match currently supports at most 2^32-1 seeds");
    }
    if (seed_count != 0 && static_cast<size_t>(prepared.edge_count) > std::numeric_limits<size_t>::max() / seed_count) {
        throw std::runtime_error("HIPRT prepared triangle_match output capacity overflow");
    }
    if (seed_count > 0 && seeds == nullptr) {
        throw std::runtime_error("HIPRT prepared triangle_match seed pointer must not be null when seed_count is nonzero");
    }
    for (size_t i = 0; i < seed_count; ++i) {
        if (seeds[i].u >= prepared.vertex_count || seeds[i].v >= prepared.vertex_count) {
            throw std::runtime_error("HIPRT prepared triangle_match edge seed vertices must be valid graph vertex IDs");
        }
    }
    if (seed_count == 0 || prepared.edge_count == 0) {
        std::vector<RtdlTriangleRow> empty;
        *rows_out = copy_triangle_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }

    std::vector<RtdlEdgeSeed> seed_values(seeds, seeds + seed_count);
    std::vector<uint32_t> row_count_device_host(1, 0u);
    DeviceAllocation seed_device(seed_values.size() * sizeof(RtdlEdgeSeed));
    DeviceAllocation row_count_device(sizeof(uint32_t));
    copy_host_to_device(seed_device, seed_values);
    copy_host_to_device(row_count_device, row_count_device_host);

    const size_t output_capacity = seed_count * static_cast<size_t>(prepared.edge_count);
    std::vector<RtdlHiprtTriangleCandidateRow> candidates(output_capacity);
    DeviceAllocation candidate_device(candidates.size() * sizeof(RtdlHiprtTriangleCandidateRow));
    void* seed_device_ptr = seed_device.get();
    void* row_offset_device_ptr = prepared.row_offset_device.get();
    void* column_device_ptr = prepared.column_device.get();
    void* edge_device_ptr = prepared.edge_device.get();
    void* candidate_device_ptr = candidate_device.get();
    void* row_count_device_ptr = row_count_device.get();
    uint32_t seed_count_u32 = static_cast<uint32_t>(seed_count);
    uint32_t enforce_u32 = enforce_id_ascending ? 1u : 0u;
    uint32_t block_size = 128;
    uint32_t grid_size = static_cast<uint32_t>((seed_count + block_size - 1) / block_size);
    void* args[] = {
        &prepared.geometry,
        &seed_device_ptr,
        &seed_count_u32,
        &row_offset_device_ptr,
        &column_device_ptr,
        &edge_device_ptr,
        &prepared.edge_count,
        &prepared.vertex_count,
        &enforce_u32,
        &candidate_device_ptr,
        &row_count_device_ptr,
        &prepared.triangle_func_table,
    };
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(prepared.triangle_kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
    copy_device_to_host(row_count_device_host, row_count_device);
    const uint32_t produced = std::min<uint32_t>(row_count_device_host[0], static_cast<uint32_t>(candidates.size()));
    candidates.resize(produced);
    copy_device_to_host(candidates, candidate_device);
    std::sort(candidates.begin(), candidates.end(), [](const RtdlHiprtTriangleCandidateRow& a, const RtdlHiprtTriangleCandidateRow& b) {
        if (a.seed_index != b.seed_index) {
            return a.seed_index < b.seed_index;
        }
        if (a.w != b.w) {
            return a.w < b.w;
        }
        if (a.u != b.u) {
            return a.u < b.u;
        }
        return a.v < b.v;
    });

    std::vector<RtdlTriangleRow> output;
    output.reserve(candidates.size());
    for (const RtdlHiprtTriangleCandidateRow& candidate : candidates) {
        RtdlTriangleRow row{candidate.u, candidate.v, candidate.w};
        if (unique) {
            const bool seen = std::any_of(output.begin(), output.end(), [&](const RtdlTriangleRow& existing) {
                return existing.u == row.u && existing.v == row.v && existing.w == row.w;
            });
            if (seen) {
                continue;
            }
        }
        output.push_back(row);
    }
    *rows_out = copy_triangle_rows_to_heap(output);
    *row_count_out = output.size();
}

struct PreparedDbTable {
    HiprtRuntime runtime;
    std::vector<std::string> field_names;
    std::vector<uint32_t> field_kinds;
    std::vector<RtdlDbScalar> row_values;
    DeviceAllocation row_value_device;
    DeviceAllocation aabb_device;
    hiprtGeometry geometry{};
    hiprtFuncTable func_table{};
    oroFunction match_kernel{};
    uint32_t row_count{};
    uint32_t field_count{};

    ~PreparedDbTable() {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
    }

    PreparedDbTable() = default;
    PreparedDbTable(const PreparedDbTable&) = delete;
    PreparedDbTable& operator=(const PreparedDbTable&) = delete;
};

std::vector<RtdlDbField> prepared_db_field_views(const PreparedDbTable& prepared) {
    std::vector<RtdlDbField> fields;
    fields.reserve(prepared.field_names.size());
    for (size_t index = 0; index < prepared.field_names.size(); ++index) {
        fields.push_back({prepared.field_names[index].c_str(), prepared.field_kinds[index]});
    }
    return fields;
}

std::unique_ptr<PreparedDbTable> prepare_db_table(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count) {
    if (row_count > std::numeric_limits<uint32_t>::max() || field_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT DB prepare currently supports at most 2^32-1 rows/fields");
    }
    if (field_count == 0 || fields == nullptr) {
        throw std::runtime_error("HIPRT DB prepare fields must not be empty");
    }
    if (row_count > 0 && row_values == nullptr) {
        throw std::runtime_error("HIPRT DB prepare row_values pointer must not be null when row_count is nonzero");
    }
    if (row_count == 0) {
        throw std::runtime_error("HIPRT DB prepare currently requires at least one row");
    }

    auto prepared = std::make_unique<PreparedDbTable>();
    prepared->field_names.reserve(field_count);
    prepared->field_kinds.reserve(field_count);
    for (size_t index = 0; index < field_count; ++index) {
        if (fields[index].name == nullptr) {
            throw std::runtime_error("HIPRT DB prepare field names must not be null");
        }
        prepared->field_names.emplace_back(fields[index].name);
        prepared->field_kinds.push_back(fields[index].kind);
    }
    prepared->row_values.assign(row_values, row_values + row_count * field_count);
    prepared->row_count = static_cast<uint32_t>(row_count);
    prepared->field_count = static_cast<uint32_t>(field_count);

    std::vector<RtdlHiprtAabb> aabb_values = encode_db_row_aabbs(row_count);
    prepared->runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);
    prepared->row_value_device = DeviceAllocation(prepared->row_values.size() * sizeof(RtdlDbScalar));
    prepared->aabb_device = DeviceAllocation(aabb_values.size() * sizeof(RtdlHiprtAabb));
    copy_host_to_device(prepared->row_value_device, prepared->row_values);
    copy_host_to_device(prepared->aabb_device, aabb_values);
    prepared->geometry = build_aabb_geometry(prepared->runtime.context, prepared->aabb_device, aabb_values.size());

    hiprtFuncNameSet func_name_set{};
    func_name_set.intersectFuncName = "intersectRtdlDbRowAabb";
    hiprtFuncDataSet func_data_set{};
    func_data_set.intersectFuncData = nullptr;
    check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(prepared->runtime.context, 1, 1, prepared->func_table));
    check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(prepared->runtime.context, prepared->func_table, 0, 0, func_data_set));
    prepared->match_kernel = build_trace_kernel_from_source(
        prepared->runtime.context,
        db_match_kernel_source(),
        "rtdl_hiprt_db_match_prepared.cu",
        "RtdlDbMatchKernel",
        &func_name_set,
        1,
        1);
    return prepared;
}

std::vector<uint32_t> run_prepared_db_match_indices(
    PreparedDbTable& prepared,
    const RtdlDbClause* clauses,
    size_t clause_count) {
    if (clause_count > 0 && clauses == nullptr) {
        throw std::runtime_error("HIPRT prepared DB clauses pointer must not be null when clause_count is nonzero");
    }
    std::vector<RtdlDbField> fields = prepared_db_field_views(prepared);
    std::vector<RtdlHiprtDbClauseDevice> clause_values =
        encode_db_clauses_for_device(fields.data(), fields.size(), clauses, clause_count);
    std::vector<uint32_t> matched(prepared.row_count, 0u);
    std::vector<uint32_t> matched_count_host(1, 0u);
    DeviceAllocation clause_device(clause_values.size() * sizeof(RtdlHiprtDbClauseDevice));
    DeviceAllocation matched_device(matched.size() * sizeof(uint32_t));
    DeviceAllocation matched_count_device(sizeof(uint32_t));
    copy_host_to_device(clause_device, clause_values);
    copy_host_to_device(matched_count_device, matched_count_host);

    void* row_value_device_ptr = prepared.row_value_device.get();
    void* clause_device_ptr = clause_device.get();
    void* matched_device_ptr = matched_device.get();
    void* matched_count_device_ptr = matched_count_device.get();
    uint32_t clause_count_u32 = static_cast<uint32_t>(clause_values.size());
    void* args[] = {
        &prepared.geometry,
        &row_value_device_ptr,
        &prepared.row_count,
        &prepared.field_count,
        &clause_device_ptr,
        &clause_count_u32,
        &matched_device_ptr,
        &matched_count_device_ptr,
        &prepared.func_table,
    };
    constexpr uint32_t block_size = 128;
    const uint32_t grid_size = static_cast<uint32_t>((prepared.row_count + block_size - 1) / block_size);
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(prepared.match_kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
    copy_device_to_host(matched_count_host, matched_count_device);
    const uint32_t produced = std::min<uint32_t>(matched_count_host[0], static_cast<uint32_t>(matched.size()));
    matched.resize(produced);
    copy_device_to_host(matched, matched_device);
    std::sort(matched.begin(), matched.end());
    return matched;
}

void run_prepared_db_conjunctive_scan(
    PreparedDbTable& prepared,
    const RtdlDbClause* clauses,
    size_t clause_count,
    RtdlDbRowIdRow** rows_out,
    size_t* row_count_out) {
    std::vector<RtdlDbField> fields = prepared_db_field_views(prepared);
    const size_t row_id_index = db_find_field_index_or_throw(fields.data(), fields.size(), "row_id");
    std::vector<uint32_t> matched = run_prepared_db_match_indices(prepared, clauses, clause_count);
    std::vector<RtdlDbRowIdRow> output;
    output.reserve(matched.size());
    for (uint32_t row_index : matched) {
        const RtdlDbScalar& row_id = prepared.row_values[static_cast<size_t>(row_index) * prepared.field_count + row_id_index];
        if (!db_scalar_is_numeric(row_id)) {
            throw std::runtime_error("HIPRT prepared DB row_id must be numeric");
        }
        output.push_back({static_cast<uint32_t>(db_scalar_as_double(row_id))});
    }
    *rows_out = copy_db_row_id_rows_to_heap(output);
    *row_count_out = output.size();
}

void run_prepared_db_grouped_count(
    PreparedDbTable& prepared,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    RtdlDbGroupedCountRow** rows_out,
    size_t* row_count_out) {
    std::vector<RtdlDbField> fields = prepared_db_field_views(prepared);
    const size_t group_index = db_find_field_index_or_throw(fields.data(), fields.size(), group_key_field);
    std::vector<uint32_t> matched = run_prepared_db_match_indices(prepared, clauses, clause_count);
    std::map<int64_t, int64_t> counts;
    for (uint32_t row_index : matched) {
        const RtdlDbScalar& group_value = prepared.row_values[static_cast<size_t>(row_index) * prepared.field_count + group_index];
        if (!db_scalar_is_numeric(group_value)) {
            throw std::runtime_error("HIPRT prepared grouped_count requires numeric or text-encoded group keys");
        }
        counts[static_cast<int64_t>(db_scalar_as_double(group_value))] += 1;
    }
    std::vector<RtdlDbGroupedCountRow> output;
    output.reserve(counts.size());
    for (const auto& item : counts) {
        output.push_back({item.first, item.second});
    }
    *rows_out = copy_db_grouped_count_rows_to_heap(output);
    *row_count_out = output.size();
}

void run_prepared_db_grouped_sum(
    PreparedDbTable& prepared,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    const char* value_field,
    RtdlDbGroupedSumRow** rows_out,
    size_t* row_count_out) {
    std::vector<RtdlDbField> fields = prepared_db_field_views(prepared);
    const size_t group_index = db_find_field_index_or_throw(fields.data(), fields.size(), group_key_field);
    const size_t value_index = db_find_field_index_or_throw(fields.data(), fields.size(), value_field);
    std::vector<uint32_t> matched = run_prepared_db_match_indices(prepared, clauses, clause_count);
    std::map<int64_t, double> sums;
    for (uint32_t row_index : matched) {
        const RtdlDbScalar& group_value = prepared.row_values[static_cast<size_t>(row_index) * prepared.field_count + group_index];
        const RtdlDbScalar& sum_value = prepared.row_values[static_cast<size_t>(row_index) * prepared.field_count + value_index];
        if (!db_scalar_is_numeric(group_value) || !db_scalar_is_numeric(sum_value)) {
            throw std::runtime_error("HIPRT prepared grouped_sum requires numeric or text-encoded group keys and numeric values");
        }
        sums[static_cast<int64_t>(db_scalar_as_double(group_value))] += db_scalar_as_double(sum_value);
    }
    std::vector<RtdlDbGroupedSumRow> output;
    output.reserve(sums.size());
    for (const auto& item : sums) {
        output.push_back({item.first, item.second});
    }
    *rows_out = copy_db_grouped_sum_rows_to_heap(output);
    *row_count_out = output.size();
}

std::vector<uint32_t> run_db_match_indices(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count) {
    if (row_count > std::numeric_limits<uint32_t>::max() || field_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT DB first wave currently supports at most 2^32-1 rows/fields");
    }
    if (field_count == 0 || fields == nullptr) {
        throw std::runtime_error("HIPRT DB fields must not be empty");
    }
    if (row_count > 0 && row_values == nullptr) {
        throw std::runtime_error("HIPRT DB row_values pointer must not be null when row_count is nonzero");
    }
    if (clause_count > 0 && clauses == nullptr) {
        throw std::runtime_error("HIPRT DB clauses pointer must not be null when clause_count is nonzero");
    }
    if (row_count == 0) {
        return {};
    }
    std::vector<RtdlHiprtDbClauseDevice> clause_values =
        encode_db_clauses_for_device(fields, field_count, clauses, clause_count);
    std::vector<RtdlDbScalar> row_value_vector(row_values, row_values + row_count * field_count);
    std::vector<RtdlHiprtAabb> aabb_values = encode_db_row_aabbs(row_count);
    std::vector<uint32_t> matched(row_count, 0u);
    std::vector<uint32_t> matched_count_host(1, 0u);

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation row_value_device(row_value_vector.size() * sizeof(RtdlDbScalar));
    DeviceAllocation clause_device(clause_values.size() * sizeof(RtdlHiprtDbClauseDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    DeviceAllocation matched_device(matched.size() * sizeof(uint32_t));
    DeviceAllocation matched_count_device(sizeof(uint32_t));
    copy_host_to_device(row_value_device, row_value_vector);
    copy_host_to_device(clause_device, clause_values);
    copy_host_to_device(aabb_device, aabb_values);
    copy_host_to_device(matched_count_device, matched_count_host);

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlDbRowAabb";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = nullptr;
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            db_match_kernel_source(),
            "rtdl_hiprt_db_match.cu",
            "RtdlDbMatchKernel",
            &func_name_set,
            1,
            1);

        void* row_value_device_ptr = row_value_device.get();
        void* clause_device_ptr = clause_device.get();
        void* matched_device_ptr = matched_device.get();
        void* matched_count_device_ptr = matched_count_device.get();
        uint32_t row_count_u32 = static_cast<uint32_t>(row_count);
        uint32_t field_count_u32 = static_cast<uint32_t>(field_count);
        uint32_t clause_count_u32 = static_cast<uint32_t>(clause_values.size());
        void* args[] = {
            &geometry,
            &row_value_device_ptr,
            &row_count_u32,
            &field_count_u32,
            &clause_device_ptr,
            &clause_count_u32,
            &matched_device_ptr,
            &matched_count_device_ptr,
            &func_table,
        };
        constexpr uint32_t block_size = 128;
        const uint32_t grid_size = static_cast<uint32_t>((row_count + block_size - 1) / block_size);
        check_oro(
            "oroModuleLaunchKernel",
            oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
        copy_device_to_host(matched_count_host, matched_count_device);
        const uint32_t produced = std::min<uint32_t>(matched_count_host[0], static_cast<uint32_t>(matched.size()));
        matched.resize(produced);
        copy_device_to_host(matched, matched_device);
        std::sort(matched.begin(), matched.end());
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
    return matched;
}

void run_db_conjunctive_scan(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count,
    RtdlDbRowIdRow** rows_out,
    size_t* row_count_out) {
    const size_t row_id_index = db_find_field_index_or_throw(fields, field_count, "row_id");
    std::vector<uint32_t> matched = run_db_match_indices(fields, field_count, row_values, row_count, clauses, clause_count);
    std::vector<RtdlDbRowIdRow> output;
    output.reserve(matched.size());
    for (uint32_t row_index : matched) {
        const RtdlDbScalar& row_id = row_values[static_cast<size_t>(row_index) * field_count + row_id_index];
        if (!db_scalar_is_numeric(row_id)) {
            throw std::runtime_error("HIPRT DB row_id must be numeric");
        }
        output.push_back({static_cast<uint32_t>(db_scalar_as_double(row_id))});
    }
    *rows_out = copy_db_row_id_rows_to_heap(output);
    *row_count_out = output.size();
}

void run_db_grouped_count(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    RtdlDbGroupedCountRow** rows_out,
    size_t* row_count_out) {
    const size_t group_index = db_find_field_index_or_throw(fields, field_count, group_key_field);
    std::vector<uint32_t> matched = run_db_match_indices(fields, field_count, row_values, row_count, clauses, clause_count);
    std::map<int64_t, int64_t> counts;
    for (uint32_t row_index : matched) {
        const RtdlDbScalar& group_value = row_values[static_cast<size_t>(row_index) * field_count + group_index];
        if (!db_scalar_is_numeric(group_value)) {
            throw std::runtime_error("HIPRT grouped_count requires numeric or text-encoded group keys");
        }
        counts[static_cast<int64_t>(db_scalar_as_double(group_value))] += 1;
    }
    std::vector<RtdlDbGroupedCountRow> output;
    output.reserve(counts.size());
    for (const auto& item : counts) {
        output.push_back({item.first, item.second});
    }
    *rows_out = copy_db_grouped_count_rows_to_heap(output);
    *row_count_out = output.size();
}

void run_db_grouped_sum(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    const char* value_field,
    RtdlDbGroupedSumRow** rows_out,
    size_t* row_count_out) {
    const size_t group_index = db_find_field_index_or_throw(fields, field_count, group_key_field);
    const size_t value_index = db_find_field_index_or_throw(fields, field_count, value_field);
    std::vector<uint32_t> matched = run_db_match_indices(fields, field_count, row_values, row_count, clauses, clause_count);
    std::map<int64_t, double> sums;
    for (uint32_t row_index : matched) {
        const RtdlDbScalar& group_value = row_values[static_cast<size_t>(row_index) * field_count + group_index];
        const RtdlDbScalar& sum_value = row_values[static_cast<size_t>(row_index) * field_count + value_index];
        if (!db_scalar_is_numeric(group_value) || !db_scalar_is_numeric(sum_value)) {
            throw std::runtime_error("HIPRT grouped_sum requires numeric or text-encoded group keys and numeric values");
        }
        sums[static_cast<int64_t>(db_scalar_as_double(group_value))] += db_scalar_as_double(sum_value);
    }
    std::vector<RtdlDbGroupedSumRow> output;
    output.reserve(sums.size());
    for (const auto& item : sums) {
        output.push_back({item.first, item.second});
    }
    *rows_out = copy_db_grouped_sum_rows_to_heap(output);
    *row_count_out = output.size();
}

int handle_call(const std::function<void()>& fn, char* error_out, size_t error_size) {
    set_message(error_out, error_size, "");
    try {
        fn();
        return 0;
    } catch (const std::exception& exc) {
        set_message(error_out, error_size, exc.what());
        return 1;
    } catch (...) {
        set_message(error_out, error_size, "unknown HIPRT backend error");
        return 1;
    }
}

}  // namespace

extern "C" int rtdl_hiprt_get_version(int* major, int* minor, int* patch) {
    if (major == nullptr || minor == nullptr || patch == nullptr) {
        return 1;
    }
    *major = HIPRT_MAJOR_VERSION;
    *minor = HIPRT_MINOR_VERSION;
    *patch = HIPRT_PATCH_VERSION;
    return 0;
}

extern "C" void rtdl_hiprt_free_rows(void* rows) {
    delete[] reinterpret_cast<unsigned char*>(rows);
}

extern "C" int rtdl_hiprt_prepare_ray_hitcount_3d(
    const RtdlTriangle3D* triangles,
    size_t triangle_count,
    void** prepared_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared_out == nullptr) {
            throw std::runtime_error("prepared_out must not be null");
        }
        *prepared_out = nullptr;
        if (triangle_count > 0 && triangles == nullptr) {
            throw std::runtime_error("triangle pointer must not be null when triangle_count is nonzero");
        }
        std::vector<hiprtFloat3> vertices = encode_triangle_vertices(triangles, triangle_count);
        HiprtRuntime runtime = create_runtime();
        hiprtSetLogLevel(hiprtLogLevelError);
        DeviceAllocation vertex_device(vertices.size() * sizeof(hiprtFloat3));
        copy_host_to_device(vertex_device, vertices);
        hiprtGeometry geometry = build_triangle_geometry(runtime.context, vertex_device, vertices.size(), triangle_count);
        try {
            oroFunction kernel = build_trace_kernel(runtime.context, "RtdlRayHitcount3DKernel");
            *prepared_out = new PreparedRayHitcount3D(std::move(runtime), std::move(vertex_device), geometry, kernel);
            geometry = nullptr;
        } catch (...) {
            if (geometry != nullptr) {
                hiprtDestroyGeometry(runtime.context, geometry);
            }
            throw;
        }
    }, error_out, error_size);
}

extern "C" void rtdl_hiprt_destroy_prepared_ray_hitcount_3d(void* prepared) {
    delete reinterpret_cast<PreparedRayHitcount3D*>(prepared);
}

extern "C" int rtdl_hiprt_run_prepared_ray_hitcount_3d(
    void* prepared,
    const RtdlRay3D* rays,
    size_t ray_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT ray-hitcount handle must not be null");
        }
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        if (ray_count > 0 && rays == nullptr) {
            throw std::runtime_error("ray pointer must not be null when ray_count is nonzero");
        }
        run_prepared_ray_hitcount_3d(
            *reinterpret_cast<PreparedRayHitcount3D*>(prepared),
            rays,
            ray_count,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_ray_hitcount_3d(
    const RtdlRay3D* rays,
    size_t ray_count,
    const RtdlTriangle3D* triangles,
    size_t triangle_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        if ((ray_count > 0 && rays == nullptr) || (triangle_count > 0 && triangles == nullptr)) {
            throw std::runtime_error("input pointers must not be null when counts are nonzero");
        }

        std::vector<hiprtFloat3> vertices;
        vertices.reserve(triangle_count * 3);
        for (size_t i = 0; i < triangle_count; ++i) {
            vertices.push_back({static_cast<float>(triangles[i].x0), static_cast<float>(triangles[i].y0), static_cast<float>(triangles[i].z0)});
            vertices.push_back({static_cast<float>(triangles[i].x1), static_cast<float>(triangles[i].y1), static_cast<float>(triangles[i].z1)});
            vertices.push_back({static_cast<float>(triangles[i].x2), static_cast<float>(triangles[i].y2), static_cast<float>(triangles[i].z2)});
        }
        std::vector<RtdlHiprtRay3DDevice> ray_values;
        ray_values.reserve(ray_count);
        for (size_t i = 0; i < ray_count; ++i) {
            ray_values.push_back({
                rays[i].id,
                static_cast<float>(rays[i].ox),
                static_cast<float>(rays[i].oy),
                static_cast<float>(rays[i].oz),
                static_cast<float>(rays[i].dx),
                static_cast<float>(rays[i].dy),
                static_cast<float>(rays[i].dz),
                static_cast<float>(rays[i].tmax),
            });
        }

        HiprtRuntime runtime = create_runtime();
        hiprtSetLogLevel(hiprtLogLevelError);

        DeviceAllocation vertex_device(vertices.size() * sizeof(hiprtFloat3));
        copy_host_to_device(vertex_device, vertices);

        hiprtTriangleMeshPrimitive mesh{};
        mesh.triangleCount = static_cast<uint32_t>(triangle_count);
        mesh.triangleStride = sizeof(hiprtInt3);
        mesh.triangleIndices = nullptr;
        mesh.vertexCount = static_cast<uint32_t>(vertices.size());
        mesh.vertexStride = sizeof(hiprtFloat3);
        mesh.vertices = vertex_device.get();

        hiprtGeometryBuildInput geom_input{};
        geom_input.type = hiprtPrimitiveTypeTriangleMesh;
        geom_input.primitive.triangleMesh = mesh;

        hiprtBuildOptions options{};
        options.buildFlags = hiprtBuildFlagBitPreferFastBuild;
        size_t temp_size = 0;
        check_hiprt("hiprtGetGeometryBuildTemporaryBufferSize", hiprtGetGeometryBuildTemporaryBufferSize(runtime.context, geom_input, options, temp_size));
        DeviceAllocation temp_device(temp_size);
        hiprtGeometry geometry{};
        check_hiprt("hiprtCreateGeometry", hiprtCreateGeometry(runtime.context, geom_input, options, geometry));
        try {
            check_hiprt(
                "hiprtBuildGeometry",
                hiprtBuildGeometry(runtime.context, hiprtBuildOperationBuild, geom_input, options, temp_device.get(), 0, geometry));

            DeviceAllocation ray_device(ray_values.size() * sizeof(RtdlHiprtRay3DDevice));
            copy_host_to_device(ray_device, ray_values);
            std::vector<RtdlRayHitCountRow> output(ray_count);
            DeviceAllocation output_device(output.size() * sizeof(RtdlRayHitCountRow));

            oroFunction kernel = build_trace_kernel(runtime.context, "RtdlRayHitcount3DKernel");
            uint32_t block_size = 128;
            uint32_t grid_size = static_cast<uint32_t>((ray_count + block_size - 1) / block_size);
            void* ray_device_ptr = ray_device.get();
            void* output_device_ptr = output_device.get();
            uint32_t ray_count_u32 = static_cast<uint32_t>(ray_count);
            void* args[] = {&geometry, &ray_device_ptr, &ray_count_u32, &output_device_ptr};
            check_oro(
                "oroModuleLaunchKernel",
                oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
            copy_device_to_host(output, output_device);

            auto* rows = new unsigned char[output.size() * sizeof(RtdlRayHitCountRow)];
            if (!output.empty()) {
                std::memcpy(rows, output.data(), output.size() * sizeof(RtdlRayHitCountRow));
            }
            *rows_out = reinterpret_cast<RtdlRayHitCountRow*>(rows);
            *row_count_out = output.size();
            check_hiprt("hiprtDestroyGeometry", hiprtDestroyGeometry(runtime.context, geometry));
            geometry = nullptr;
        } catch (...) {
            if (geometry != nullptr) {
                hiprtDestroyGeometry(runtime.context, geometry);
            }
            throw;
        }
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_fixed_radius_neighbors_3d(
    const RtdlPoint3D* queries,
    size_t query_count,
    const RtdlPoint3D* search_points,
    size_t search_count,
    double radius,
    uint32_t k_max,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_fixed_radius_neighbors_3d(
            queries,
            query_count,
            search_points,
            search_count,
            radius,
            k_max,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_prepare_fixed_radius_neighbors_3d(
    const RtdlPoint3D* search_points,
    size_t search_count,
    double radius,
    void** prepared_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared_out == nullptr) {
            throw std::runtime_error("prepared_out must not be null");
        }
        *prepared_out = nullptr;
        auto prepared = prepare_fixed_radius_neighbors_3d(search_points, search_count, radius);
        *prepared_out = prepared.release();
    }, error_out, error_size);
}

extern "C" void rtdl_hiprt_destroy_prepared_fixed_radius_neighbors_3d(void* prepared) {
    delete reinterpret_cast<PreparedFixedRadiusNeighbors3D*>(prepared);
}

extern "C" int rtdl_hiprt_run_prepared_fixed_radius_neighbors_3d(
    void* prepared,
    const RtdlPoint3D* queries,
    size_t query_count,
    uint32_t k_max,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT fixed-radius-neighbors handle must not be null");
        }
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_prepared_fixed_radius_neighbors_3d(
            *reinterpret_cast<PreparedFixedRadiusNeighbors3D*>(prepared),
            queries,
            query_count,
            k_max,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_fixed_radius_neighbors_2d(
    const RtdlPoint* queries,
    size_t query_count,
    const RtdlPoint* search_points,
    size_t search_count,
    double radius,
    uint32_t k_max,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_fixed_radius_neighbors_2d(
            queries,
            query_count,
            search_points,
            search_count,
            radius,
            k_max,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_lsi(
    const RtdlSegment* left,
    size_t left_count,
    const RtdlSegment* right,
    size_t right_count,
    RtdlLsiRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_lsi_2d(left, left_count, right, right_count, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_ray_hitcount_2d(
    const RtdlRay2D* rays,
    size_t ray_count,
    const RtdlTriangle* triangles,
    size_t triangle_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_ray_hitcount_2d(rays, ray_count, triangles, triangle_count, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_pip(
    const RtdlPoint* points,
    size_t point_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    RtdlPipRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_pip_2d(points, point_count, polygons, polygon_count, vertices_xy, vertex_xy_count, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_overlay(
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count,
    RtdlOverlayRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_overlay_2d(
            left_polygons,
            left_count,
            left_vertices_xy,
            left_vertex_xy_count,
            right_polygons,
            right_count,
            right_vertices_xy,
            right_vertex_xy_count,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_point_nearest_segment(
    const RtdlPoint* points,
    size_t point_count,
    const RtdlSegment* segments,
    size_t segment_count,
    RtdlPointNearestSegmentRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_point_nearest_segment_2d(points, point_count, segments, segment_count, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_segment_polygon_hitcount(
    const RtdlSegment* segments,
    size_t segment_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    RtdlSegmentPolygonHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_segment_polygon_hitcount_2d(
            segments,
            segment_count,
            polygons,
            polygon_count,
            vertices_xy,
            vertex_xy_count,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_segment_polygon_anyhit_rows(
    const RtdlSegment* segments,
    size_t segment_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    RtdlSegmentPolygonAnyHitRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_segment_polygon_anyhit_rows_2d(
            segments,
            segment_count,
            polygons,
            polygon_count,
            vertices_xy,
            vertex_xy_count,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_bfs_expand(
    const RtdlFrontierVertex* frontier,
    size_t frontier_count,
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t edge_count,
    uint32_t vertex_count,
    const uint32_t* visited,
    size_t visited_count,
    int dedupe,
    RtdlBfsRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_bfs_expand(
            frontier,
            frontier_count,
            row_offsets,
            row_offset_count,
            column_indices,
            edge_count,
            vertex_count,
            visited,
            visited_count,
            dedupe != 0,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_prepare_graph_csr(
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t edge_count,
    uint32_t vertex_count,
    void** prepared_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared_out == nullptr) {
            throw std::runtime_error("prepared_out must not be null");
        }
        *prepared_out = nullptr;
        auto prepared = prepare_graph_csr(row_offsets, row_offset_count, column_indices, edge_count, vertex_count);
        *prepared_out = prepared.release();
    }, error_out, error_size);
}

extern "C" void rtdl_hiprt_destroy_prepared_graph_csr(void* prepared) {
    delete reinterpret_cast<PreparedGraphCSR*>(prepared);
}

extern "C" int rtdl_hiprt_run_prepared_bfs_expand(
    void* prepared,
    const RtdlFrontierVertex* frontier,
    size_t frontier_count,
    const uint32_t* visited,
    size_t visited_count,
    int dedupe,
    RtdlBfsRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT graph CSR handle must not be null");
        }
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_prepared_bfs_expand(
            *reinterpret_cast<PreparedGraphCSR*>(prepared),
            frontier,
            frontier_count,
            visited,
            visited_count,
            dedupe != 0,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_triangle_probe(
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t column_index_count,
    const RtdlEdgeSeed* seeds,
    size_t seed_count,
    uint32_t enforce_id_ascending,
    uint32_t unique,
    RtdlTriangleRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_triangle_probe(
            row_offsets,
            row_offset_count,
            column_indices,
            column_index_count,
            seeds,
            seed_count,
            enforce_id_ascending != 0u,
            unique != 0u,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_prepared_triangle_probe(
    void* prepared,
    const RtdlEdgeSeed* seeds,
    size_t seed_count,
    int enforce_id_ascending,
    int unique,
    RtdlTriangleRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT graph CSR handle must not be null");
        }
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_prepared_triangle_probe(
            *reinterpret_cast<PreparedGraphCSR*>(prepared),
            seeds,
            seed_count,
            enforce_id_ascending != 0,
            unique != 0,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_conjunctive_scan(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count,
    RtdlDbRowIdRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_db_conjunctive_scan(
            fields,
            field_count,
            row_values,
            row_count,
            clauses,
            clause_count,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_grouped_count(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    RtdlDbGroupedCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_db_grouped_count(
            fields,
            field_count,
            row_values,
            row_count,
            clauses,
            clause_count,
            group_key_field,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_grouped_sum(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    const char* value_field,
    RtdlDbGroupedSumRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_db_grouped_sum(
            fields,
            field_count,
            row_values,
            row_count,
            clauses,
            clause_count,
            group_key_field,
            value_field,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_prepare_db_table(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    void** prepared_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared_out == nullptr) {
            throw std::runtime_error("prepared_out pointer must not be null");
        }
        *prepared_out = nullptr;
        auto prepared = prepare_db_table(fields, field_count, row_values, row_count);
        *prepared_out = prepared.release();
    }, error_out, error_size);
}

extern "C" void rtdl_hiprt_destroy_prepared_db_table(void* prepared) {
    delete reinterpret_cast<PreparedDbTable*>(prepared);
}

extern "C" int rtdl_hiprt_run_prepared_conjunctive_scan(
    void* prepared,
    const RtdlDbClause* clauses,
    size_t clause_count,
    RtdlDbRowIdRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT DB table handle must not be null");
        }
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_prepared_db_conjunctive_scan(
            *reinterpret_cast<PreparedDbTable*>(prepared),
            clauses,
            clause_count,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_prepared_grouped_count(
    void* prepared,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    RtdlDbGroupedCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT DB table handle must not be null");
        }
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_prepared_db_grouped_count(
            *reinterpret_cast<PreparedDbTable*>(prepared),
            clauses,
            clause_count,
            group_key_field,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_prepared_grouped_sum(
    void* prepared,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    const char* value_field,
    RtdlDbGroupedSumRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT DB table handle must not be null");
        }
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_prepared_db_grouped_sum(
            *reinterpret_cast<PreparedDbTable*>(prepared),
            clauses,
            clause_count,
            group_key_field,
            value_field,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_context_probe(
    char* device_name,
    size_t device_name_size,
    int* device_type,
    int* api_version,
    char* error,
    size_t error_size) {
    set_message(error, error_size, "");
    if (device_name == nullptr || device_name_size == 0 || device_type == nullptr || api_version == nullptr) {
        set_message(error, error_size, "null output passed to rtdl_hiprt_context_probe");
        return 1;
    }
    device_name[0] = '\0';
    *device_type = -1;
    *api_version = HIPRT_API_VERSION;

    int init_err = oroInitialize(static_cast<oroApi>(ORO_API_CUDA), 0);
    if (init_err != static_cast<int>(oroSuccess)) {
        set_message(error, error_size, oro_initialize_error_message(init_err));
        return 2;
    }
    oroError oro_err = oroInit(0);
    if (oro_err != oroSuccess) {
        set_message(error, error_size, oro_error_message("oroInit", oro_err));
        return 3;
    }

    oroDevice device{};
    oro_err = oroDeviceGet(&device, 0);
    if (oro_err != oroSuccess) {
        set_message(error, error_size, oro_error_message("oroDeviceGet(0)", oro_err));
        return 4;
    }

    oroCtx ctx{};
    oro_err = oroCtxCreate(&ctx, 0, device);
    if (oro_err != oroSuccess) {
        set_message(error, error_size, oro_error_message("oroCtxCreate", oro_err));
        return 5;
    }

    oroDeviceProp props{};
    oro_err = oroGetDeviceProperties(&props, device);
    if (oro_err != oroSuccess) {
        oroCtxDestroy(ctx);
        set_message(error, error_size, oro_error_message("oroGetDeviceProperties", oro_err));
        return 6;
    }
    set_message(device_name, device_name_size, props.name);

    hiprtContextCreationInput input{};
    input.ctxt = oroGetRawCtx(ctx);
    input.device = oroGetRawDevice(device);
    input.deviceType = std::strstr(props.name, "NVIDIA") != nullptr ? hiprtDeviceNVIDIA : hiprtDeviceAMD;
    *device_type = static_cast<int>(input.deviceType);

    hiprtContext hiprt_ctx{};
    hiprtError hiprt_err = hiprtCreateContext(HIPRT_API_VERSION, input, hiprt_ctx);
    if (hiprt_err != hiprtSuccess) {
        oroCtxDestroy(ctx);
        set_message(error, error_size, hiprt_error_message("hiprtCreateContext", hiprt_err));
        return 7;
    }
    hiprt_err = hiprtDestroyContext(hiprt_ctx);
    oroCtxDestroy(ctx);
    if (hiprt_err != hiprtSuccess) {
        set_message(error, error_size, hiprt_error_message("hiprtDestroyContext", hiprt_err));
        return 8;
    }
    return 0;
}

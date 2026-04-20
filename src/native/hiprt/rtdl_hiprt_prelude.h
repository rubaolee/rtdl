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

struct RtdlRayAnyHitRow {
    uint32_t ray_id;
    uint32_t any_hit;
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

// rtdl_optix.cpp — NVIDIA OptiX 7 backend for rtdl
//
// Implements all six workloads (LSI, PIP, Overlay, RayHitCount,
// SegmentPolygonHitcount, PointNearestSegment) through the OptiX backend.
// The mature RT-traversal workloads use OptiX 7 custom-geometry BVH traversal.
// Some families still follow a bounded local maturity story:
// - SegmentPolygonHitcount now defaults to a host-indexed candidate-reduction
//   path; the older OptiX custom-AABB traversal path remains available as an
//   explicit experimental mode
// - PointNearestSegment uses CUDA-parallel brute-force
//
// Device kernels are embedded as CUDA source strings and compiled to PTX at
// runtime via NVRTC.  Compiled pipelines are cached across calls in static
// singletons so the JIT cost is paid only once per workload type per process.
//
// Build requirements:
//   - CUDA Toolkit ≥ 11.0  (nvrtc.h, cuda.h, cuda_runtime.h)
//   - OptiX SDK 7.x  (optix.h)
//   - C++17
//
// Typical compile invocation:
//   nvcc -std=c++17 -O3 -shared -fPIC \
//        -I/path/to/optix/include \
//        -I/path/to/cuda/include \
//        -DRTDL_OPTIX_INCLUDE_DIR='"/path/to/optix/include"' \
//        -DRTDL_CUDA_INCLUDE_DIR='"/path/to/cuda/include"' \
//        -lcuda -lnvrtc \
//        rtdl_optix.cpp -o librtdl_optix.so

#include <optix.h>
#include <optix_function_table_definition.h>
#include <optix_stack_size.h>
#include <optix_stubs.h>

#include <cuda.h>
#include <cuda_runtime.h>
#include <nvrtc.h>

#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <filesystem>
#include <memory>
#include <mutex>
#include <new>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <sys/wait.h>
#include <unistd.h>
#include <vector>

#if defined(__has_include)
#  if __has_include(<geos_c.h>)
#    include <geos_c.h>
#    define RTDL_OPTIX_HAS_GEOS 1
#  else
#    define RTDL_OPTIX_HAS_GEOS 0
#  endif
#else
#  define RTDL_OPTIX_HAS_GEOS 0
#endif

// ──────────────────────────────────────────────────────────────────────────────
// Public C ABI (mirrors rtdl_embree.cpp)
// ──────────────────────────────────────────────────────────────────────────────

extern "C" {

struct RtdlSegment {
    uint32_t id;
    double x0, y0, x1, y1;
};

struct RtdlPoint {
    uint32_t id;
    double x, y;
};

struct RtdlPolygonRef {
    uint32_t id;
    uint32_t vertex_offset;
    uint32_t vertex_count;
};

struct RtdlTriangle {
    uint32_t id;
    double x0, y0, x1, y1, x2, y2;
};

struct RtdlRay2D {
    uint32_t id;
    double ox, oy, dx, dy, tmax;
};

struct RtdlLsiRow {
    uint32_t left_id, right_id;
    double intersection_point_x, intersection_point_y;
};

struct RtdlPipRow {
    uint32_t point_id, polygon_id, contains;
};

struct RtdlOverlayRow {
    uint32_t left_polygon_id, right_polygon_id;
    uint32_t requires_lsi, requires_pip;
};

struct RtdlRayHitCountRow {
    uint32_t ray_id, hit_count;
};

struct RtdlSegmentPolygonHitCountRow {
    uint32_t segment_id, hit_count;
};

struct RtdlSegmentPolygonAnyHitRow {
    uint32_t segment_id, polygon_id;
};

struct RtdlPointNearestSegmentRow {
    uint32_t point_id, segment_id;
    double distance;
};

int  rtdl_optix_get_version(int* major_out, int* minor_out, int* patch_out);
int  rtdl_optix_run_lsi(
         const RtdlSegment* left,  size_t left_count,
         const RtdlSegment* right, size_t right_count,
         RtdlLsiRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_pip(
         const RtdlPoint* points,     size_t point_count,
         const RtdlPolygonRef* polys, size_t poly_count,
         const double* vertices_xy,   size_t vertex_xy_count,
         uint32_t positive_only,
         RtdlPipRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_overlay(
         const RtdlPolygonRef* left_polys,  size_t left_count,
         const double* left_verts_xy,       size_t left_vert_xy_count,
         const RtdlPolygonRef* right_polys, size_t right_count,
         const double* right_verts_xy,      size_t right_vert_xy_count,
         RtdlOverlayRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_ray_hitcount(
         const RtdlRay2D*    rays,      size_t ray_count,
         const RtdlTriangle* triangles, size_t triangle_count,
         RtdlRayHitCountRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_segment_polygon_hitcount(
         const RtdlSegment*   segments,  size_t segment_count,
         const RtdlPolygonRef* polygons, size_t polygon_count,
         const double* vertices_xy,      size_t vertex_xy_count,
         RtdlSegmentPolygonHitCountRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_segment_polygon_anyhit_rows(
         const RtdlSegment*   segments,  size_t segment_count,
         const RtdlPolygonRef* polygons, size_t polygon_count,
         const double* vertices_xy,      size_t vertex_xy_count,
         RtdlSegmentPolygonAnyHitRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_point_nearest_segment(
         const RtdlPoint*   points,   size_t point_count,
         const RtdlSegment* segments, size_t segment_count,
         RtdlPointNearestSegmentRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
void rtdl_optix_free_rows(void* rows);

} // extern "C"

// ──────────────────────────────────────────────────────────────────────────────
// Internal helpers
// ──────────────────────────────────────────────────────────────────────────────

namespace {

// ---------- error helpers ---------------------------------------------------

template <typename T>
void set_error(const std::string& msg, T* buf, size_t sz) {
    if (!buf || !sz) return;
    size_t n = std::min(sz - 1, msg.size());
    std::memcpy(buf, msg.data(), n);
    buf[n] = '\0';
}

#define CUDA_CHECK(call)                                                        \
    do {                                                                        \
        cudaError_t _e = (call);                                               \
        if (_e != cudaSuccess)                                                  \
            throw std::runtime_error(std::string("CUDA error: ") +             \
                                     cudaGetErrorString(_e));                   \
    } while (0)

#define CU_CHECK(call)                                                          \
    do {                                                                        \
        CUresult _r = (call);                                                   \
        if (_r != CUDA_SUCCESS) {                                               \
            const char* _s = nullptr;                                           \
            cuGetErrorString(_r, &_s);                                          \
            throw std::runtime_error(std::string("CUDA driver error: ") +      \
                                     (_s ? _s : "unknown"));                    \
        }                                                                       \
    } while (0)

#define OPTIX_CHECK(call)                                                       \
    do {                                                                        \
        OptixResult _r = (call);                                                \
        if (_r != OPTIX_SUCCESS)                                                \
            throw std::runtime_error(std::string("OptiX error: ") +            \
                                     optixGetErrorString(_r));                  \
    } while (0)

#define NVRTC_CHECK(call)                                                       \
    do {                                                                        \
        nvrtcResult _r = (call);                                                \
        if (_r != NVRTC_SUCCESS)                                                \
            throw std::runtime_error(std::string("NVRTC error: ") +            \
                                     nvrtcGetErrorString(_r));                  \
    } while (0)

template <typename Fn>
int handle_native_call(Fn&& fn, char* error_out, size_t error_size) {
    try {
        fn();
        return 0;
    } catch (const std::exception& ex) {
        set_error(ex.what(), error_out, error_size);
        return 1;
    }
}

// ---------- CUDA device pointer RAII ----------------------------------------

struct DevPtr {
    CUdeviceptr ptr = 0;
    explicit DevPtr(size_t bytes) {
        if (bytes == 0) return;
        CU_CHECK(cuMemAlloc(&ptr, bytes));
    }
    ~DevPtr() {
        if (ptr) cuMemFree(ptr);
    }
    DevPtr(const DevPtr&)            = delete;
    DevPtr& operator=(const DevPtr&) = delete;
    void* as_void() const { return reinterpret_cast<void*>(ptr); }
};

template <typename T>
void upload(CUdeviceptr dst, const T* src, size_t count) {
    if (count == 0) return;
    CU_CHECK(cuMemcpyHtoD(dst, src, sizeof(T) * count));
}

template <typename T>
void download(T* dst, CUdeviceptr src, size_t count) {
    if (count == 0) return;
    CU_CHECK(cuMemcpyDtoH(dst, src, sizeof(T) * count));
}

// ---------- NVRTC compilation -----------------------------------------------

static std::string compile_to_ptx_with_nvcc(const char* cuda_src,
                                            const char* name,
                                            const std::string& optix_inc,
                                            const std::string& cuda_inc,
                                            const std::string& cuda_sys_inc,
                                            const std::vector<const char*>& extra_opts)
{
    namespace fs = std::filesystem;
    char dir_template[] = "/tmp/rtdl-optix-XXXXXX";
    char* tmp_dir = mkdtemp(dir_template);
    if (!tmp_dir) {
        throw std::runtime_error("failed to create temporary directory for nvcc PTX compilation");
    }
    fs::path tmp_root(tmp_dir);
    struct TempDirCleanup {
        fs::path path;
        ~TempDirCleanup() {
            std::error_code ignored;
            fs::remove_all(path, ignored);
        }
    } cleanup{tmp_root};

    fs::path src_path = tmp_root / name;
    fs::path ptx_path = src_path;
    ptx_path += ".ptx";
    fs::path log_path = src_path;
    log_path += ".log";
    {
        std::ofstream src_file(src_path, std::ios::binary);
        if (!src_file) {
            throw std::runtime_error("failed to write temporary CUDA source for nvcc PTX compilation");
        }
        src_file.write(cuda_src, static_cast<std::streamsize>(std::strlen(cuda_src)));
    }
    std::string nvcc = std::getenv("RTDL_NVCC") ? std::getenv("RTDL_NVCC") : "/usr/bin/nvcc";
    std::vector<std::string> argv_storage = {
        nvcc,
        "-ptx",
        "--std=c++14",
        "-O3",
        optix_inc,
        cuda_inc,
    };
    if (std::strlen(RTDL_CUDA_SYSTEM_INCLUDE_DIR) > 0) {
        argv_storage.push_back(cuda_sys_inc);
    }
    for (const char* opt : extra_opts) {
        argv_storage.push_back(opt);
    }
    argv_storage.push_back(src_path.string());
    argv_storage.push_back("-o");
    argv_storage.push_back(ptx_path.string());

    std::vector<char*> argv;
    argv.reserve(argv_storage.size() + 1);
    for (std::string& arg : argv_storage) {
        argv.push_back(arg.data());
    }
    argv.push_back(nullptr);

    pid_t pid = fork();
    if (pid < 0) {
        throw std::runtime_error("failed to fork nvcc PTX compilation process");
    }
    if (pid == 0) {
        FILE* log_file = std::fopen(log_path.c_str(), "wb");
        if (!log_file) _exit(127);
        int log_fd = fileno(log_file);
        if (dup2(log_fd, STDOUT_FILENO) < 0 || dup2(log_fd, STDERR_FILENO) < 0) {
            std::fclose(log_file);
            _exit(127);
        }
        std::fclose(log_file);
        execvp(nvcc.c_str(), argv.data());
        _exit(127);
    }

    int status = 0;
    if (waitpid(pid, &status, 0) < 0) {
        throw std::runtime_error("failed to wait for nvcc PTX compilation process");
    }
    if (!WIFEXITED(status) || WEXITSTATUS(status) != 0) {
        std::ifstream log_file(log_path, std::ios::binary);
        std::string log((std::istreambuf_iterator<char>(log_file)),
                        std::istreambuf_iterator<char>());
        throw std::runtime_error("nvcc PTX compile failed for " + std::string(name) + ":\n" + log);
    }
    std::ifstream ptx_file(ptx_path, std::ios::binary);
    if (!ptx_file) {
        throw std::runtime_error("nvcc PTX compile succeeded but PTX output was not found");
    }
    return std::string((std::istreambuf_iterator<char>(ptx_file)),
                       std::istreambuf_iterator<char>());
}

std::string compile_to_ptx(const char* cuda_src,
                           const char* name,
                           const std::vector<const char*>& extra_opts = {}) {
#ifndef RTDL_OPTIX_INCLUDE_DIR
#define RTDL_OPTIX_INCLUDE_DIR ""
#endif
#ifndef RTDL_CUDA_INCLUDE_DIR
#define RTDL_CUDA_INCLUDE_DIR ""
#endif
#ifndef RTDL_CUDA_SYSTEM_INCLUDE_DIR
#define RTDL_CUDA_SYSTEM_INCLUDE_DIR ""
#endif
    std::string optix_inc = std::string("-I") + RTDL_OPTIX_INCLUDE_DIR;
    std::string cuda_inc  = std::string("-I") + RTDL_CUDA_INCLUDE_DIR;
    std::string cuda_sys_inc = std::string("-I") + RTDL_CUDA_SYSTEM_INCLUDE_DIR;

    if (const char* compiler = std::getenv("RTDL_OPTIX_PTX_COMPILER");
        compiler && std::string(compiler) == "nvcc") {
        return compile_to_ptx_with_nvcc(cuda_src, name, optix_inc, cuda_inc, cuda_sys_inc, extra_opts);
    }

    std::vector<const char*> opts = {
        optix_inc.c_str(),
        cuda_inc.c_str(),
        "--std=c++14",
    };
    if (std::strlen(RTDL_CUDA_SYSTEM_INCLUDE_DIR) > 0) {
        opts.push_back(cuda_sys_inc.c_str());
    }
    for (const char* o : extra_opts) opts.push_back(o);

    nvrtcProgram prog;
    NVRTC_CHECK(nvrtcCreateProgram(&prog, cuda_src, name, 0, nullptr, nullptr));

    nvrtcResult compile_result = nvrtcCompileProgram(prog,
                                                     static_cast<int>(opts.size()),
                                                     opts.data());
    if (compile_result != NVRTC_SUCCESS) {
        size_t log_size = 0;
        nvrtcGetProgramLogSize(prog, &log_size);
        std::string log(log_size, '\0');
        nvrtcGetProgramLog(prog, log.data());
        nvrtcDestroyProgram(&prog);
        try {
            return compile_to_ptx_with_nvcc(cuda_src, name, optix_inc, cuda_inc, cuda_sys_inc, extra_opts);
        } catch (const std::exception& fallback_error) {
            throw std::runtime_error("NVRTC compile failed for " +
                                     std::string(name) + ":\n" + log +
                                     "\nFallback nvcc compile also failed:\n" +
                                     fallback_error.what());
        }
    }

    size_t ptx_size = 0;
    NVRTC_CHECK(nvrtcGetPTXSize(prog, &ptx_size));
    std::string ptx(ptx_size, '\0');
    NVRTC_CHECK(nvrtcGetPTX(prog, ptx.data()));
    nvrtcDestroyProgram(&prog);

    if (const char* dump_dir = std::getenv("RTDL_DUMP_PTX_DIR")) {
        std::string path = std::string(dump_dir) + "/" + name + ".ptx";
        std::ofstream out(path, std::ios::binary);
        if (out) out.write(ptx.data(), static_cast<std::streamsize>(ptx.size()));
    }
    return ptx;
}

// ---------- OptiX context singleton -----------------------------------------

static OptixDeviceContext g_optix_ctx = nullptr;
static std::once_flag     g_optix_init_flag;

static void optix_log_callback(unsigned int level, const char* tag, const char* message, void*) {
    std::fprintf(stderr, "[optix][%u][%s] %s\n", level, tag ? tag : "", message ? message : "");
}

static void init_optix_context() {
    CU_CHECK(cuInit(0));
    CUdevice  dev;
    CUcontext cu_ctx;
    CU_CHECK(cuDeviceGet(&dev, 0));
    CU_CHECK(cuCtxCreate(&cu_ctx, 0, dev));
    OPTIX_CHECK(optixInit());
    OptixDeviceContextOptions opts = {};
    if (const char* log_level = std::getenv("RTDL_OPTIX_LOG_LEVEL")) {
        opts.logCallbackFunction = optix_log_callback;
        opts.logCallbackLevel = static_cast<unsigned int>(std::max(0, std::atoi(log_level)));
    }
    OPTIX_CHECK(optixDeviceContextCreate(cu_ctx, &opts, &g_optix_ctx));
}

static OptixDeviceContext get_optix_context() {
    std::call_once(g_optix_init_flag, init_optix_context);
    return g_optix_ctx;
}

// ---------- SBT record types ------------------------------------------------

template <typename T>
struct alignas(OPTIX_SBT_RECORD_ALIGNMENT) SbtRecord {
    char header[OPTIX_SBT_RECORD_HEADER_SIZE];
    T    data;
};

struct EmptyData {};

using RaygenRecord = SbtRecord<EmptyData>;
using MissRecord   = SbtRecord<EmptyData>;
using HitRecord    = SbtRecord<EmptyData>;

// ---------- AABB helpers ----------------------------------------------------

// OptiX positive-hit PIP uses GPU-side candidate generation followed by host
// exact finalize. Candidate generation must therefore bias toward false
// positives, not false negatives. The clean-clone release regression showed
// that the earlier polygon AABB pad was too tight for the float32 broad phase
// on the exact-source county/zipcode surface.
constexpr float kAabbPad = 1.0e-3f;
constexpr float kSegmentAabbPad = 1.0e-4f;
constexpr float kLsiTraceTmaxPad = 1.0e-4f;

OptixAabb aabb_for_segment(float x0, float y0, float x1, float y1) {
    OptixAabb a;
    a.minX = std::min(x0, x1) - kSegmentAabbPad;
    a.minY = std::min(y0, y1) - kSegmentAabbPad;
    a.minZ = -kSegmentAabbPad;
    a.maxX = std::max(x0, x1) + kSegmentAabbPad;
    a.maxY = std::max(y0, y1) + kSegmentAabbPad;
    a.maxZ =  kSegmentAabbPad;
    return a;
}

OptixAabb aabb_for_polygon(const double* verts_xy, uint32_t offset, uint32_t count) {
    OptixAabb a;
    a.minX = a.maxX = static_cast<float>(verts_xy[offset * 2]);
    a.minY = a.maxY = static_cast<float>(verts_xy[offset * 2 + 1]);
    a.minZ = -kAabbPad;
    a.maxZ =  kAabbPad;
    for (uint32_t i = 1; i < count; ++i) {
        float px = static_cast<float>(verts_xy[(offset + i) * 2]);
        float py = static_cast<float>(verts_xy[(offset + i) * 2 + 1]);
        a.minX = std::min(a.minX, px);
        a.minY = std::min(a.minY, py);
        a.maxX = std::max(a.maxX, px);
        a.maxY = std::max(a.maxY, py);
    }
    a.minX -= kAabbPad;
    a.minY -= kAabbPad;
    a.maxX += kAabbPad;
    a.maxY += kAabbPad;
    return a;
}

OptixAabb aabb_for_triangle(float x0, float y0,
                             float x1, float y1,
                             float x2, float y2) {
    OptixAabb a;
    a.minX = std::min({x0, x1, x2}) - kAabbPad;
    a.minY = std::min({y0, y1, y2}) - kAabbPad;
    a.minZ = -kAabbPad;
    a.maxX = std::max({x0, x1, x2}) + kAabbPad;
    a.maxY = std::max({y0, y1, y2}) + kAabbPad;
    a.maxZ =  kAabbPad;
    return a;
}

// ---------- BVH construction ------------------------------------------------

struct AccelHolder {
    CUdeviceptr output_buf   = 0;
    CUdeviceptr aabb_buf     = 0;
    OptixTraversableHandle handle = 0;

    AccelHolder() = default;
    ~AccelHolder() {
        if (output_buf) cuMemFree(output_buf);
        if (aabb_buf)   cuMemFree(aabb_buf);
    }
    AccelHolder(const AccelHolder&)            = delete;
    AccelHolder& operator=(const AccelHolder&) = delete;
    AccelHolder(AccelHolder&& other) noexcept
        : output_buf(other.output_buf),
          aabb_buf(other.aabb_buf),
          handle(other.handle) {
        other.output_buf = 0;
        other.aabb_buf = 0;
        other.handle = 0;
    }
    AccelHolder& operator=(AccelHolder&& other) noexcept {
        if (this != &other) {
            if (output_buf) cuMemFree(output_buf);
            if (aabb_buf) cuMemFree(aabb_buf);
            output_buf = other.output_buf;
            aabb_buf = other.aabb_buf;
            handle = other.handle;
            other.output_buf = 0;
            other.aabb_buf = 0;
            other.handle = 0;
        }
        return *this;
    }
};

static AccelHolder build_custom_accel(OptixDeviceContext ctx,
                                      const std::vector<OptixAabb>& aabbs) {
    AccelHolder result;
    size_t aabb_bytes = sizeof(OptixAabb) * aabbs.size();
    CU_CHECK(cuMemAlloc(&result.aabb_buf, aabb_bytes));
    CU_CHECK(cuMemcpyHtoD(result.aabb_buf, aabbs.data(), aabb_bytes));

    OptixBuildInput build_input = {};
    build_input.type = OPTIX_BUILD_INPUT_TYPE_CUSTOM_PRIMITIVES;
    auto& cpp = build_input.customPrimitiveArray;
    cpp.aabbBuffers   = &result.aabb_buf;
    cpp.numPrimitives = static_cast<unsigned>(aabbs.size());
    cpp.strideInBytes = sizeof(OptixAabb);
    uint32_t flags_arr = OPTIX_GEOMETRY_FLAG_NONE;
    cpp.flags          = &flags_arr;
    cpp.numSbtRecords  = 1;

    OptixAccelBuildOptions accel_opts = {};
    accel_opts.buildFlags = OPTIX_BUILD_FLAG_ALLOW_RANDOM_VERTEX_ACCESS;
    accel_opts.operation  = OPTIX_BUILD_OPERATION_BUILD;

    OptixAccelBufferSizes sizes = {};
    OPTIX_CHECK(optixAccelComputeMemoryUsage(ctx, &accel_opts, &build_input, 1, &sizes));

    DevPtr temp_buf(sizes.tempSizeInBytes);
    CU_CHECK(cuMemAlloc(&result.output_buf, sizes.outputSizeInBytes));

    CUstream stream = 0;
    OPTIX_CHECK(optixAccelBuild(ctx, stream, &accel_opts, &build_input, 1,
                                 temp_buf.ptr, sizes.tempSizeInBytes,
                                 result.output_buf, sizes.outputSizeInBytes,
                                 &result.handle, nullptr, 0));
    CU_CHECK(cuStreamSynchronize(stream));
    return result;
}

// ---------- Pipeline builder ------------------------------------------------

struct PipelineHolder {
    OptixModule        module    = nullptr;
    OptixProgramGroup  raygen_pg = nullptr;
    OptixProgramGroup  miss_pg   = nullptr;
    OptixProgramGroup  hit_pg    = nullptr;
    OptixPipeline      pipeline  = nullptr;
    CUdeviceptr        sbt_buf   = 0;
    OptixShaderBindingTable sbt  = {};

    ~PipelineHolder() {
        if (pipeline) optixPipelineDestroy(pipeline);
        if (hit_pg)   optixProgramGroupDestroy(hit_pg);
        if (miss_pg)  optixProgramGroupDestroy(miss_pg);
        if (raygen_pg) optixProgramGroupDestroy(raygen_pg);
        if (module)   optixModuleDestroy(module);
        if (sbt_buf)  cuMemFree(sbt_buf);
    }
    PipelineHolder() = default;
    PipelineHolder(const PipelineHolder&)            = delete;
    PipelineHolder& operator=(const PipelineHolder&) = delete;
};

static std::unique_ptr<PipelineHolder> build_pipeline(
        OptixDeviceContext ctx,
        const std::string& ptx,
        const char* raygen_name,
        const char* miss_name,
        const char* intersection_name,       // null → skip custom intersection
        const char* anyhit_name,             // null → skip anyhit
        const char* closesthit_name,         // null → skip closesthit
        int max_payload_values               // number of payload registers
) {
    auto holder = std::make_unique<PipelineHolder>();

    // Compile module
    OptixModuleCompileOptions mco = {};
    mco.maxRegisterCount = OPTIX_COMPILE_DEFAULT_MAX_REGISTER_COUNT;
    mco.optLevel         = OPTIX_COMPILE_OPTIMIZATION_DEFAULT;
    mco.debugLevel       = OPTIX_COMPILE_DEBUG_LEVEL_NONE;

    OptixPipelineCompileOptions pco = {};
    pco.usesMotionBlur                   = 0;
    pco.traversableGraphFlags            = OPTIX_TRAVERSABLE_GRAPH_FLAG_ALLOW_SINGLE_GAS;
    pco.numPayloadValues                 = max_payload_values;
    pco.numAttributeValues               = 0;
    pco.exceptionFlags                   = OPTIX_EXCEPTION_FLAG_NONE;
    pco.pipelineLaunchParamsVariableName = "params";
    pco.usesPrimitiveTypeFlags           = OPTIX_PRIMITIVE_TYPE_FLAGS_CUSTOM;

    OPTIX_CHECK(optixModuleCreate(ctx, &mco, &pco,
                                   ptx.c_str(), ptx.size(),
                                   nullptr, nullptr,
                                   &holder->module));

    // Raygen group
    {
        OptixProgramGroupDesc desc = {};
        desc.kind = OPTIX_PROGRAM_GROUP_KIND_RAYGEN;
        desc.raygen.module            = holder->module;
        desc.raygen.entryFunctionName = raygen_name;
        OptixProgramGroupOptions opts = {};
        OPTIX_CHECK(optixProgramGroupCreate(ctx, &desc, 1, &opts,
                                             nullptr, nullptr,
                                             &holder->raygen_pg));
    }
    // Miss group
    {
        OptixProgramGroupDesc desc = {};
        desc.kind = OPTIX_PROGRAM_GROUP_KIND_MISS;
        desc.miss.module            = holder->module;
        desc.miss.entryFunctionName = miss_name;
        OptixProgramGroupOptions opts = {};
        OPTIX_CHECK(optixProgramGroupCreate(ctx, &desc, 1, &opts,
                                             nullptr, nullptr,
                                             &holder->miss_pg));
    }
    // Hit group
    {
        OptixProgramGroupDesc desc = {};
        desc.kind = OPTIX_PROGRAM_GROUP_KIND_HITGROUP;
        if (intersection_name) {
            desc.hitgroup.moduleIS            = holder->module;
            desc.hitgroup.entryFunctionNameIS = intersection_name;
        }
        if (anyhit_name) {
            desc.hitgroup.moduleAH            = holder->module;
            desc.hitgroup.entryFunctionNameAH = anyhit_name;
        }
        if (closesthit_name) {
            desc.hitgroup.moduleCH            = holder->module;
            desc.hitgroup.entryFunctionNameCH = closesthit_name;
        }
        OptixProgramGroupOptions opts = {};
        OPTIX_CHECK(optixProgramGroupCreate(ctx, &desc, 1, &opts,
                                             nullptr, nullptr,
                                             &holder->hit_pg));
    }

    // Pipeline
    OptixProgramGroup pgs[3] = {holder->raygen_pg, holder->miss_pg, holder->hit_pg};
    OptixPipelineLinkOptions plo = {};
    plo.maxTraceDepth = 1;
    OPTIX_CHECK(optixPipelineCreate(ctx, &pco, &plo, pgs, 3,
                                     nullptr, nullptr,
                                     &holder->pipeline));

    // OptiX requires an explicit stack-size configuration before launch.
    OptixStackSizes stack_sizes = {};
    OPTIX_CHECK(optixUtilAccumulateStackSizes(holder->raygen_pg, &stack_sizes, holder->pipeline));
    OPTIX_CHECK(optixUtilAccumulateStackSizes(holder->miss_pg, &stack_sizes, holder->pipeline));
    OPTIX_CHECK(optixUtilAccumulateStackSizes(holder->hit_pg, &stack_sizes, holder->pipeline));

    uint32_t dc_from_traversal = 0;
    uint32_t dc_from_state = 0;
    uint32_t continuation = 0;
    OPTIX_CHECK(optixUtilComputeStackSizes(&stack_sizes,
                                           plo.maxTraceDepth,
                                           0,  // no continuation callables
                                           0,  // no direct callables
                                           &dc_from_traversal,
                                           &dc_from_state,
                                           &continuation));
    OPTIX_CHECK(optixPipelineSetStackSize(holder->pipeline,
                                          dc_from_traversal,
                                          dc_from_state,
                                          continuation,
                                          1));

    // SBT
    RaygenRecord raygen_rec = {};
    MissRecord   miss_rec   = {};
    HitRecord    hit_rec    = {};
    OPTIX_CHECK(optixSbtRecordPackHeader(holder->raygen_pg, &raygen_rec));
    OPTIX_CHECK(optixSbtRecordPackHeader(holder->miss_pg,   &miss_rec));
    OPTIX_CHECK(optixSbtRecordPackHeader(holder->hit_pg,    &hit_rec));

    size_t sbt_bytes = sizeof(RaygenRecord) + sizeof(MissRecord) + sizeof(HitRecord);
    CU_CHECK(cuMemAlloc(&holder->sbt_buf, sbt_bytes));
    CUdeviceptr p = holder->sbt_buf;
    CU_CHECK(cuMemcpyHtoD(p, &raygen_rec, sizeof(RaygenRecord)));
    p += sizeof(RaygenRecord);
    CU_CHECK(cuMemcpyHtoD(p, &miss_rec, sizeof(MissRecord)));
    p += sizeof(MissRecord);
    CU_CHECK(cuMemcpyHtoD(p, &hit_rec, sizeof(HitRecord)));

    holder->sbt.raygenRecord                = holder->sbt_buf;
    holder->sbt.missRecordBase              = holder->sbt_buf + sizeof(RaygenRecord);
    holder->sbt.missRecordStrideInBytes     = sizeof(MissRecord);
    holder->sbt.missRecordCount             = 1;
    holder->sbt.hitgroupRecordBase          = holder->sbt_buf + sizeof(RaygenRecord) + sizeof(MissRecord);
    holder->sbt.hitgroupRecordStrideInBytes = sizeof(HitRecord);
    holder->sbt.hitgroupRecordCount         = 1;

    return holder;
}

// ──────────────────────────────────────────────────────────────────────────────
// Device kernel source strings
// ──────────────────────────────────────────────────────────────────────────────

// ---------- LSI kernel -------------------------------------------------------

static const char* kLsiKernelSrc = R"CUDA(
#include <optix_device.h>

struct GpuSegment {
    float x0, y0, x1, y1;
    unsigned int id;
};

struct LsiRecord {
    unsigned int left_id, right_id;
    float ix, iy;
};

struct LsiParams {
    OptixTraversableHandle traversable;
    const GpuSegment* left_segs;
    const GpuSegment* right_segs;
    LsiRecord* output;
    unsigned int* output_count;
    unsigned int  output_capacity;
    unsigned int  probe_count;
};

extern "C" {
__constant__ LsiParams params;
}

static __forceinline__ __device__ float dabsf(float x) {
    return x < 0.0f ? -x : x;
}

static __forceinline__ __device__ bool seg_intersect(
        float ax0, float ay0, float ax1, float ay1,
        float bx0, float by0, float bx1, float by1,
        float* t_out, float* ix_out, float* iy_out)
{
    float rx = ax1 - ax0, ry = ay1 - ay0;
    float sx = bx1 - bx0, sy = by1 - by0;
    float denom = rx * sy - ry * sx;
    if (dabsf(denom) < 1.0e-7f) return false;
    float qpx = bx0 - ax0, qpy = by0 - ay0;
    float t = (qpx * sy - qpy * sx) / denom;
    float u = (qpx * ry - qpy * rx) / denom;
    if (t < 0.0f || t > 1.0f || u < 0.0f || u > 1.0f) return false;
    *t_out  = t;
    *ix_out = ax0 + t * rx;
    *iy_out = ay0 + t * ry;
    return true;
}

extern "C" __global__ void __raygen__lsi_probe() {
    const unsigned int idx = optixGetLaunchIndex().x;
    if (idx >= params.probe_count) return;
    const GpuSegment p = params.left_segs[idx];
    unsigned int p0 = idx, p1 = 0u, p2 = 0u, p3 = 0u;
    optixTrace(params.traversable,
               make_float3(p.x0, p.y0, 0.0f),
               make_float3(p.x1 - p.x0, p.y1 - p.y0, 0.0f),
               0.0f, 1.0f + 1.0e-4f, 0.0f,
               OptixVisibilityMask(255),
               OPTIX_RAY_FLAG_NONE,
               0, 1, 0,
               p0, p1, p2, p3);
}

extern "C" __global__ void __miss__lsi_miss() {}

extern "C" __global__ void __intersection__lsi_isect() {
    const unsigned int prim = optixGetPrimitiveIndex();
    optixSetPayload_1(prim);
    optixSetPayload_2(0u);
    optixSetPayload_3(0u);
    // Report the AABB overlap as a candidate; host-side exact refine decides
    // the true segment-segment intersection and removes false positives.
    optixReportIntersection(0.5f, 0u);
}

extern "C" __global__ void __anyhit__lsi_anyhit() {
    const unsigned int pidx = optixGetPayload_0();
    const unsigned int bidx = optixGetPayload_1();
    const float    ix   = __uint_as_float(optixGetPayload_2());
    const float    iy   = __uint_as_float(optixGetPayload_3());
    const unsigned int slot = atomicAdd(params.output_count, 1u);
    if (slot < params.output_capacity) {
        LsiRecord r;
        r.left_id  = params.left_segs[pidx].id;
        r.right_id = params.right_segs[bidx].id;
        r.ix = ix; r.iy = iy;
        params.output[slot] = r;
    }
    optixIgnoreIntersection();
}
)CUDA";

// ---------- PIP kernel -------------------------------------------------------

static const char* kPipKernelSrc = R"CUDA(
#include <optix_device.h>
#include <stdint.h>
#include <math.h>

struct GpuPolygonRef {
    uint32_t id;
    uint32_t vertex_offset;
    uint32_t vertex_count;
};

struct PipRecord {
    uint32_t point_id, polygon_id, contains;
};

struct PipParams {
    OptixTraversableHandle traversable;
    const float* points_x;
    const float* points_y;
    const uint32_t* point_ids;
    const GpuPolygonRef* polygons;
    const float* vertices_x;
    const float* vertices_y;
    uint32_t* hit_words;
    PipRecord* output;
    uint32_t* output_count;
    uint32_t output_capacity;
    uint32_t positive_only;
    uint32_t hit_word_count;
    uint32_t polygon_count;
    uint32_t probe_count;
};

extern "C" {
__constant__ PipParams params;
}

static __forceinline__ __device__ bool point_in_polygon(
        float px, float py,
        const GpuPolygonRef& poly)
{
    // This helper is used only outside positive_only mode. In positive_only
    // mode, candidate generation now bypasses this test entirely and reports
    // all AABB candidates so host exact finalize sees every plausible hit. The
    // wider epsilon here is still useful for the non-positive-only float32
    // path, where false negatives are also undesirable.
    const float point_eps = 1.0e-4f;
    uint32_t n = poly.vertex_count;
    uint32_t off = poly.vertex_offset;
    // Boundary check
    for (uint32_t i = 0; i < n; ++i) {
        float ax = params.vertices_x[off + i];
        float ay = params.vertices_y[off + i];
        float bx = params.vertices_x[off + (i + 1) % n];
        float by = params.vertices_y[off + (i + 1) % n];
        // Check if point lies on this edge
        float len2 = (bx - ax) * (bx - ax) + (by - ay) * (by - ay);
        if (len2 <= point_eps * point_eps) {
            if (fabsf(px - ax) <= point_eps && fabsf(py - ay) <= point_eps)
                return true;
            continue;
        }
        float cross = (px - ax) * (by - ay) - (py - ay) * (bx - ax);
        if (fabsf(cross) <= point_eps * sqrtf(len2)) {
            float dot = (px - ax) * (bx - ax) + (py - ay) * (by - ay);
            if (dot >= -point_eps && dot <= len2 + point_eps)
                return true;
        }
    }
    // Ray casting
    bool inside = false;
    for (uint32_t i = 0, j = n - 1; i < n; j = i++) {
        float xi = params.vertices_x[off + i], yi = params.vertices_y[off + i];
        float xj = params.vertices_x[off + j], yj = params.vertices_y[off + j];
        if (((yi > py) != (yj > py)) &&
            (px <= (xj - xi) * (py - yi) / ((yj - yi) != 0.0f ? (yj - yi) : 1.0e-20f) + xi))
            inside = !inside;
    }
    return inside;
}

extern "C" __global__ void __raygen__pip_probe() {
    const uint32_t idx = optixGetLaunchIndex().x;
    if (idx >= params.probe_count) return;
    float px = params.points_x[idx];
    float py = params.points_y[idx];
    unsigned int p0 = idx, p1 = 0u, p2 = 0u, p3 = 0u;
    // Vertical ray upward from the point
    optixTrace(params.traversable,
               make_float3(px, py, 0.0f),
               make_float3(0.0f, 1.0f, 0.0f),
               0.0f, 1.0e30f, 0.0f,
               OptixVisibilityMask(255),
               OPTIX_RAY_FLAG_NONE,
               0, 1, 0,
               p0, p1, p2, p3);
}

extern "C" __global__ void __miss__pip_miss() {}

extern "C" __global__ void __intersection__pip_isect() {
    const uint32_t prim = optixGetPrimitiveIndex();
    const uint32_t pidx = optixGetPayload_0();
    if (params.positive_only != 0u) {
        // In positive-hit mode, OptiX is only a conservative candidate
        // generator. Final inclusive truth is decided on the host. Reporting
        // every AABB candidate here avoids float32 false negatives in the GPU
        // point-in-polygon path.
        optixSetPayload_1(prim);
        optixReportIntersection(0.5f, 0u);
        return;
    }
    const GpuPolygonRef poly = params.polygons[prim];
    float px = params.points_x[pidx];
    float py = params.points_y[pidx];
    if (!point_in_polygon(px, py, poly)) return;
    optixSetPayload_1(prim);
    optixReportIntersection(0.5f, 0u);
}

    extern "C" __global__ void __anyhit__pip_anyhit() {
        const uint32_t pidx = optixGetPayload_0();
        const uint32_t prim = optixGetPayload_1();
        if (params.positive_only != 0u) {
            const uint32_t slot = pidx * params.polygon_count + prim;
            const uint32_t word = slot >> 5;
            const uint32_t bit  = 1u << (slot & 31u);
            if (word < params.hit_word_count) {
                atomicOr(&params.hit_words[word], bit);
            }
            optixIgnoreIntersection();
            return;
        }
    const uint32_t slot = pidx * params.polygon_count + prim;
    params.output[slot].contains = 1u;
    optixIgnoreIntersection();
}
)CUDA";

// ---------- Overlay kernel ---------------------------------------------------

static const char* kOverlayKernelSrc = R"CUDA(
#include <optix_device.h>
#include <stdint.h>
#include <math.h>

struct GpuPolygonRef {
    uint32_t id;
    uint32_t vertex_offset;
    uint32_t vertex_count;
};

struct OverlayFlags {
    uint32_t requires_lsi;
    uint32_t requires_pip;
};

struct OverlayParams {
    OptixTraversableHandle traversable;
    const GpuPolygonRef* left_polygons;
    const GpuPolygonRef* right_polygons;
    const float* left_vx;
    const float* left_vy;
    const float* right_vx;
    const float* right_vy;
    OverlayFlags* output;         // left_count * right_count elements
    uint32_t  right_count;
    uint32_t  left_count;
    uint32_t  launch_count;       // total raygen threads
    uint32_t  max_edges_per_poly; // raygen stride
};

extern "C" {
__constant__ OverlayParams params;
}

static __forceinline__ __device__ bool seg_intersect_flag(
        float ax0, float ay0, float ax1, float ay1,
        float bx0, float by0, float bx1, float by1)
{
    float rx = ax1 - ax0, ry = ay1 - ay0;
    float sx = bx1 - bx0, sy = by1 - by0;
    float denom = rx * sy - ry * sx;
    if (fabsf(denom) < 1.0e-7f) return false;
    float qpx = bx0 - ax0, qpy = by0 - ay0;
    float t = (qpx * sy - qpy * sx) / denom;
    float u = (qpx * ry - qpy * rx) / denom;
    return t >= 0.0f && t <= 1.0f && u >= 0.0f && u <= 1.0f;
}

static __forceinline__ __device__ bool point_in_polygon_dev(
        float px, float py,
        const GpuPolygonRef& poly,
        const float* vx, const float* vy)
{
    uint32_t n = poly.vertex_count;
    uint32_t off = poly.vertex_offset;
    bool inside = false;
    for (uint32_t i = 0, j = n - 1; i < n; j = i++) {
        float xi = vx[off + i], yi = vy[off + i];
        float xj = vx[off + j], yj = vy[off + j];
        if (((yi > py) != (yj > py)) &&
            (px <= (xj - xi) * (py - yi) / ((yj - yi) != 0.0f ? (yj - yi) : 1.0e-20f) + xi))
            inside = !inside;
    }
    return inside;
}

// Launch layout: one thread per (left_polygon, left_edge_index)
// left_polygon_idx = launch_idx / max_edges_per_poly
// edge_idx         = launch_idx % max_edges_per_poly
extern "C" __global__ void __raygen__overlay_probe() {
    const uint32_t gidx = optixGetLaunchIndex().x;
    if (gidx >= params.launch_count) return;
    const uint32_t lpidx   = gidx / params.max_edges_per_poly;
    const uint32_t edge_i  = gidx % params.max_edges_per_poly;
    if (lpidx >= params.left_count) return;
    const GpuPolygonRef lp = params.left_polygons[lpidx];
    if (edge_i >= lp.vertex_count) return;

    uint32_t i0 = lp.vertex_offset + edge_i;
    uint32_t i1 = lp.vertex_offset + (edge_i + 1) % lp.vertex_count;
    float ex0 = params.left_vx[i0], ey0 = params.left_vy[i0];
    float ex1 = params.left_vx[i1], ey1 = params.left_vy[i1];
    float dx = ex1 - ex0, dy = ey1 - ey0;

    unsigned int p0 = lpidx, p1 = edge_i, p2 = 0u, p3 = 0u;
    optixTrace(params.traversable,
               make_float3(ex0, ey0, 0.0f),
               make_float3(dx, dy, 0.0f),
               0.0f, 1.0f, 0.0f,
               OptixVisibilityMask(255),
               OPTIX_RAY_FLAG_NONE,
               0, 1, 0,
               p0, p1, p2, p3);
}

extern "C" __global__ void __miss__overlay_miss() {}

extern "C" __global__ void __intersection__overlay_isect() {
    const uint32_t rpidx = optixGetPrimitiveIndex();
    const uint32_t lpidx = optixGetPayload_0();
    const uint32_t eidx  = optixGetPayload_1();
    const GpuPolygonRef lp = params.left_polygons[lpidx];
    const GpuPolygonRef rp = params.right_polygons[rpidx];
    // Test probe edge against each right polygon edge
    uint32_t i0 = lp.vertex_offset + eidx;
    uint32_t i1 = lp.vertex_offset + (eidx + 1) % lp.vertex_count;
    float ax0 = params.left_vx[i0], ay0 = params.left_vy[i0];
    float ax1 = params.left_vx[i1], ay1 = params.left_vy[i1];
    bool lsi_hit = false;
    for (uint32_t k = 0; k < rp.vertex_count; ++k) {
        uint32_t j0 = rp.vertex_offset + k;
        uint32_t j1 = rp.vertex_offset + (k + 1) % rp.vertex_count;
        float bx0 = params.right_vx[j0], by0 = params.right_vy[j0];
        float bx1 = params.right_vx[j1], by1 = params.right_vy[j1];
        if (seg_intersect_flag(ax0, ay0, ax1, ay1, bx0, by0, bx1, by1)) {
            lsi_hit = true;
            break;
        }
    }
    if (lsi_hit) {
        optixSetPayload_2(rpidx);
        optixReportIntersection(0.5f, 1u);  // hit_kind=1 → LSI
    }
}

extern "C" __global__ void __anyhit__overlay_anyhit() {
    const uint32_t lpidx = optixGetPayload_0();
    const uint32_t rpidx = optixGetPayload_2();
    const uint32_t slot  = lpidx * params.right_count + rpidx;
    atomicOr(&params.output[slot].requires_lsi, 1u);
    optixIgnoreIntersection();
}
)CUDA";

// ---------- Ray-triangle hit count kernel ------------------------------------

static const char* kRayHitCountKernelSrc = R"CUDA(
#include <optix_device.h>

typedef unsigned int uint32_t;

static __forceinline__ __device__ float rt_absf(float x)
{
    return x < 0.0f ? -x : x;
}

static __forceinline__ __device__ float rt_sqrtf(float x)
{
    if (x <= 0.0f) return 0.0f;
    float r = x > 1.0f ? x : 1.0f;
    for (int i = 0; i < 8; ++i) {
        r = 0.5f * (r + x / r);
    }
    return r;
}

struct GpuTriangle {
    float x0, y0, x1, y1, x2, y2;
    uint32_t id;
};

struct GpuRay {
    float ox, oy, dx, dy, tmax;
    uint32_t id;
};

struct RayHitCountRecord {
    uint32_t ray_id, hit_count;
};

struct RayHitCountParams {
    OptixTraversableHandle traversable;
    const GpuRay*      rays;
    const GpuTriangle* triangles;
    RayHitCountRecord* output;
    uint32_t ray_count;
};

extern "C" {
__constant__ RayHitCountParams params;
}

static __forceinline__ __device__ bool ray_hits_triangle(
        float ox, float oy,
        float dx, float dy,
        float tmax,
        float x0, float y0,
        float x1, float y1,
        float x2, float y2)
{
    // Check if a 2D ray segment intersects a 2D triangle
    // ray end point
    float ex = ox + dx * tmax, ey = oy + dy * tmax;
    // Test ray vs each triangle edge
    auto seg_hit = [&](float ax, float ay, float bx, float by) -> bool {
        float rx = ex - ox, ry = ey - oy;
        float sx = bx - ax, sy = by - ay;
        float denom = rx * sy - ry * sx;
        if (rt_absf(denom) < 1.0e-7f) return false;
        float qpx = ax - ox, qpy = ay - oy;
        float t = (qpx * sy - qpy * sx) / denom;
        float u = (qpx * ry - qpy * rx) / denom;
        return t >= 0.0f && t <= 1.0f && u >= 0.0f && u <= 1.0f;
    };
    // Edge intersection
    if (seg_hit(x0, y0, x1, y1) ||
        seg_hit(x1, y1, x2, y2) ||
        seg_hit(x2, y2, x0, y0))
        return true;
    // Ray origin inside triangle (barycentric test)
    auto sign = [](float a, float b, float c, float d, float e, float f) {
        return (a - f) * (d - f) - (c - f) * (b - f);
    };
    float d1 = sign(ox, oy, x0, y0, x1, y1);
    float d2 = sign(ox, oy, x1, y1, x2, y2);
    float d3 = sign(ox, oy, x2, y2, x0, y0);
    bool has_neg = (d1 < 0) || (d2 < 0) || (d3 < 0);
    bool has_pos = (d1 > 0) || (d2 > 0) || (d3 > 0);
    return !(has_neg && has_pos);
}

extern "C" __global__ void __raygen__rayhit_probe() {
    const uint32_t idx = optixGetLaunchIndex().x;
    if (idx >= params.ray_count) return;
    const GpuRay r = params.rays[idx];
    float len = rt_sqrtf(r.dx * r.dx + r.dy * r.dy);
    if (len < 1.0e-10f) {
        params.output[idx] = {r.id, 0u};
        return;
    }
    unsigned int p0 = idx, p1 = 0u, p2 = 0u, p3 = 0u;
    optixTrace(params.traversable,
               make_float3(r.ox, r.oy, 0.0f),
               make_float3(r.dx / len, r.dy / len, 0.0f),
               0.0f, r.tmax * len, 0.0f,
               OptixVisibilityMask(255),
               OPTIX_RAY_FLAG_NONE,
               0, 1, 0,
               p0, p1, p2, p3);
    params.output[idx] = {r.id, p1};
}

extern "C" __global__ void __miss__rayhit_miss() {}

extern "C" __global__ void __intersection__rayhit_isect() {
    const uint32_t prim = optixGetPrimitiveIndex();
    const uint32_t ridx = optixGetPayload_0();
    const GpuRay r = params.rays[ridx];
    const GpuTriangle t = params.triangles[prim];
    if (!ray_hits_triangle(r.ox, r.oy, r.dx, r.dy, r.tmax,
                           t.x0, t.y0, t.x1, t.y1, t.x2, t.y2))
        return;
    optixReportIntersection(0.5f, 0u);
}

extern "C" __global__ void __anyhit__rayhit_anyhit() {
    uint32_t count = optixGetPayload_1();
    optixSetPayload_1(count + 1u);
    optixIgnoreIntersection();
}
)CUDA";

// ---------- Segment-polygon hitcount kernel ----------------------------------

static const char* kSegPolyHitcountKernelSrc = R"CUDA(
#include <optix_device.h>
#include <stdint.h>
#include <math.h>

struct GpuSegment {
    float x0, y0, x1, y1;
    uint32_t id;
};

struct GpuPolygonRef {
    uint32_t id;
    uint32_t vertex_offset;
    uint32_t vertex_count;
};

struct SegPolyHitRecord {
    uint32_t segment_id, hit_count;
};

struct SegPolyParams {
    OptixTraversableHandle traversable;
    const GpuSegment*    segments;
    const GpuPolygonRef* polygons;
    const float* vertices_x;
    const float* vertices_y;
    SegPolyHitRecord* output;
    uint32_t segment_count;
};

extern "C" {
__constant__ SegPolyParams params;
}

static __forceinline__ __device__ float segpoly_absf(float x)
{
    return x < 0.0f ? -x : x;
}

static __forceinline__ __device__ bool point_on_segment_dev(
        float px, float py,
        float ax, float ay,
        float bx, float by)
{
    const float cross = (px - ax) * (by - ay) - (py - ay) * (bx - ax);
    if (segpoly_absf(cross) > 1.0e-5f) return false;
    const float min_x = ax < bx ? ax : bx;
    const float max_x = ax > bx ? ax : bx;
    const float min_y = ay < by ? ay : by;
    const float max_y = ay > by ? ay : by;
    return px >= min_x - 1.0e-5f && px <= max_x + 1.0e-5f &&
           py >= min_y - 1.0e-5f && py <= max_y + 1.0e-5f;
}

static __forceinline__ __device__ bool point_in_polygon_inclusive_dev(
        float px, float py,
        const GpuPolygonRef& poly)
{
    const uint32_t n = poly.vertex_count;
    const uint32_t off = poly.vertex_offset;
    for (uint32_t i = 0, j = n - 1; i < n; j = i++) {
        const float xi = params.vertices_x[off + i], yi = params.vertices_y[off + i];
        const float xj = params.vertices_x[off + j], yj = params.vertices_y[off + j];
        if (point_on_segment_dev(px, py, xi, yi, xj, yj)) {
            return true;
        }
    }
    bool inside = false;
    for (uint32_t i = 0, j = n - 1; i < n; j = i++) {
        const float xi = params.vertices_x[off + i], yi = params.vertices_y[off + i];
        const float xj = params.vertices_x[off + j], yj = params.vertices_y[off + j];
        if (((yi > py) != (yj > py)) &&
            (px <= (xj - xi) * (py - yi) / ((yj - yi) != 0.0f ? (yj - yi) : 1.0e-20f) + xi)) {
            inside = !inside;
        }
    }
    return inside;
}

static __forceinline__ __device__ bool seg_edge_hit_dev(
        float sx0, float sy0, float sx1, float sy1,
        float ax, float ay, float bx, float by)
{
    const float rx = sx1 - sx0;
    const float ry = sy1 - sy0;
    const float ex = bx - ax;
    const float ey = by - ay;
    const float denom = rx * ey - ry * ex;
    if (segpoly_absf(denom) < 1.0e-7f) {
        return point_on_segment_dev(sx0, sy0, ax, ay, bx, by) ||
               point_on_segment_dev(sx1, sy1, ax, ay, bx, by) ||
               point_on_segment_dev(ax, ay, sx0, sy0, sx1, sy1) ||
               point_on_segment_dev(bx, by, sx0, sy0, sx1, sy1);
    }
    const float qpx = ax - sx0;
    const float qpy = ay - sy0;
    const float t = (qpx * ey - qpy * ex) / denom;
    const float u = (qpx * ry - qpy * rx) / denom;
    return t >= 0.0f && t <= 1.0f && u >= 0.0f && u <= 1.0f;
}

static __forceinline__ __device__ bool seg_hits_polygon(
        float sx0, float sy0, float sx1, float sy1,
        const GpuPolygonRef& poly)
{
    const uint32_t n = poly.vertex_count;
    const uint32_t off = poly.vertex_offset;
    if (point_in_polygon_inclusive_dev(sx0, sy0, poly) ||
        point_in_polygon_inclusive_dev(sx1, sy1, poly)) {
        return true;
    }
    for (uint32_t i = 0; i < n; ++i) {
        const float ax = params.vertices_x[off + i], ay = params.vertices_y[off + i];
        const float bx = params.vertices_x[off + (i + 1) % n], by = params.vertices_y[off + (i + 1) % n];
        if (seg_edge_hit_dev(sx0, sy0, sx1, sy1, ax, ay, bx, by)) {
            return true;
        }
    }
    return false;
}

extern "C" __global__ void __raygen__segpoly_probe() {
    const uint32_t idx = optixGetLaunchIndex().x;
    if (idx >= params.segment_count) return;
    const GpuSegment s = params.segments[idx];
    float dx = s.x1 - s.x0, dy = s.y1 - s.y0;
    float len = sqrtf(dx * dx + dy * dy);
    if (len < 1.0e-10f) {
        params.output[idx] = {s.id, 0u};
        return;
    }
    unsigned int p0 = idx, p1 = 0u, p2 = 0u, p3 = 0u;
    optixTrace(params.traversable,
               make_float3(s.x0, s.y0, 0.0f),
               make_float3(dx / len, dy / len, 0.0f),
               0.0f, len, 0.0f,
               OptixVisibilityMask(255),
               OPTIX_RAY_FLAG_NONE,
               0, 1, 0,
               p0, p1, p2, p3);
    params.output[idx] = {s.id, p1};
}

extern "C" __global__ void __miss__segpoly_miss() {}

extern "C" __global__ void __intersection__segpoly_isect() {
    const uint32_t prim = optixGetPrimitiveIndex();
    const uint32_t sidx = optixGetPayload_0();
    const GpuSegment s = params.segments[sidx];
    const GpuPolygonRef poly = params.polygons[prim];
    if (!seg_hits_polygon(s.x0, s.y0, s.x1, s.y1, poly)) return;
    optixReportIntersection(0.5f, 0u);
}

extern "C" __global__ void __anyhit__segpoly_anyhit() {
    uint32_t count = optixGetPayload_1();
    optixSetPayload_1(count + 1u);
    optixIgnoreIntersection();
}
)CUDA";

// ---------- Point-nearest-segment: CUDA kernel (no OptiX BVH) ---------------
//
// PointNearestSegment does not map well to OptiX ray traversal (it needs a
// radius/distance query, not a ray-AABB intersection). We use a plain CUDA
// kernel that is GPU-parallel but brute-force: one warp per point, each warp
// threads split the segment list.

static const char* kPointNearestKernelSrc = R"CUDA(
#include <stdint.h>
#include <math.h>
#include <float.h>

struct GpuPoint { float x, y; uint32_t id; };
struct GpuSegment { float x0, y0, x1, y1; uint32_t id; };
struct PnsRecord { uint32_t point_id, segment_id; float distance; };

extern "C" __global__ void point_nearest_segment(
        const GpuPoint*   points,
        uint32_t          point_count,
        const GpuSegment* segs,
        uint32_t          seg_count,
        PnsRecord*        output)
{
    const uint32_t pidx = blockIdx.x * blockDim.x + threadIdx.x;
    if (pidx >= point_count) return;
    float px = points[pidx].x, py = points[pidx].y;
    float best_dist = FLT_MAX;
    uint32_t best_seg_id = 0;
    for (uint32_t s = 0; s < seg_count; ++s) {
        float ax = segs[s].x0, ay = segs[s].y0;
        float bx = segs[s].x1, by = segs[s].y1;
        float vx = bx - ax, vy = by - ay;
        float wx = px - ax, wy = py - ay;
        float denom = vx * vx + vy * vy;
        float t = (denom < 1.0e-12f) ? 0.0f
                                      : fminf(1.0f, fmaxf(0.0f, (wx * vx + wy * vy) / denom));
        float proj_x = ax + t * vx, proj_y = ay + t * vy;
        float dx = px - proj_x, dy = py - proj_y;
        float dist = sqrtf(dx * dx + dy * dy);
        if (dist < best_dist ||
            (fabsf(dist - best_dist) < 1.0e-7f && segs[s].id < best_seg_id)) {
            best_dist   = dist;
            best_seg_id = segs[s].id;
        }
    }
    output[pidx] = {points[pidx].id, best_seg_id, best_dist};
}
)CUDA";

// ──────────────────────────────────────────────────────────────────────────────
// Cached pipeline singletons
// ──────────────────────────────────────────────────────────────────────────────

struct LsiPipeline {
    PipelineHolder* pipe = nullptr;
    std::once_flag   init;
};

struct PipPipeline {
    PipelineHolder* pipe = nullptr;
    std::once_flag   init;
};

struct OverlayPipeline {
    PipelineHolder* pipe = nullptr;
    std::once_flag   init;
};

struct RayHitCountPipeline {
    PipelineHolder* pipe = nullptr;
    std::once_flag   init;
};

struct SegPolyPipeline {
    PipelineHolder* pipe = nullptr;
    std::once_flag   init;
};

struct PnsCuFunction {
    CUmodule   module   = nullptr;
    CUfunction fn       = nullptr;
    std::once_flag init;
};

static LsiPipeline        g_lsi;
static PipPipeline        g_pip;
static OverlayPipeline    g_overlay;
static RayHitCountPipeline g_rayhit;
static SegPolyPipeline    g_segpoly;
static PnsCuFunction      g_pns;

// GPU structs for upload

#pragma pack(push, 1)
struct GpuSegment { float x0, y0, x1, y1; uint32_t id; };
struct GpuPoint   { float x, y;           uint32_t id; };
struct GpuPolygonRef { uint32_t id, vertex_offset, vertex_count; };
struct GpuTriangle { float x0, y0, x1, y1, x2, y2; uint32_t id; };
struct GpuRay { float ox, oy, dx, dy, tmax; uint32_t id; };
#pragma pack(pop)

// Output structs (GPU-side, float coords)
#pragma pack(push, 1)
struct GpuLsiRecord  { uint32_t left_id, right_id; float ix, iy; };
struct GpuPipRecord  { uint32_t point_id, polygon_id, contains; };
struct GpuOverlayFlags { uint32_t requires_lsi, requires_pip; };
struct GpuRayHitRecord { uint32_t ray_id, hit_count; };
struct GpuSegPolyRecord { uint32_t segment_id, hit_count; };
struct GpuPnsRecord     { uint32_t point_id, segment_id; float distance; };
#pragma pack(pop)

struct Bounds2D {
    double min_x, min_y, max_x, max_y;
};

static bool exact_segment_intersection(
        const RtdlSegment& left,
        const RtdlSegment& right,
        double* ix_out,
        double* iy_out)
{
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
    if (!(0.0 <= t && t <= 1.0 && 0.0 <= u && u <= 1.0)) {
        return false;
    }

    *ix_out = px + t * rx;
    *iy_out = py + t * ry;
    return true;
}

#if RTDL_OPTIX_HAS_GEOS
class GeosPreparedPolygonRefs {
  public:
    GeosPreparedPolygonRefs(const RtdlPolygonRef* polys, size_t poly_count, const double* vertices_xy)
        : context_(GEOS_init_r()) {
        if (context_ == nullptr) {
            throw std::runtime_error("failed to initialize GEOS context");
        }
        geometries_.reserve(poly_count);
        prepared_.reserve(poly_count);
        for (size_t i = 0; i < poly_count; ++i) {
            GEOSGeometry* geometry = build_polygon_geometry(polys[i], vertices_xy);
            if (geometry == nullptr) {
                throw std::runtime_error("failed to build GEOS polygon geometry");
            }
            const GEOSPreparedGeometry* prepared = GEOSPrepare_r(context_, geometry);
            if (prepared == nullptr) {
                GEOSGeom_destroy_r(context_, geometry);
                throw std::runtime_error("failed to prepare GEOS polygon geometry");
            }
            geometries_.push_back(geometry);
            prepared_.push_back(prepared);
        }
    }

    GeosPreparedPolygonRefs(const GeosPreparedPolygonRefs&) = delete;
    GeosPreparedPolygonRefs& operator=(const GeosPreparedPolygonRefs&) = delete;

    ~GeosPreparedPolygonRefs() {
        if (context_ == nullptr) return;
        for (const GEOSPreparedGeometry* prepared : prepared_) {
            if (prepared != nullptr) {
                GEOSPreparedGeom_destroy_r(context_, prepared);
            }
        }
        for (GEOSGeometry* geometry : geometries_) {
            if (geometry != nullptr) {
                GEOSGeom_destroy_r(context_, geometry);
            }
        }
        GEOS_finish_r(context_);
    }

    bool covers(size_t polygon_index, double x, double y) const {
        GEOSGeometry* point = build_point_geometry(x, y);
        if (point == nullptr) {
            throw std::runtime_error("failed to build GEOS point geometry");
        }
        char covers_value = GEOSPreparedCovers_r(context_, prepared_.at(polygon_index), point);
        GEOSGeom_destroy_r(context_, point);
        if (covers_value == 2) {
            throw std::runtime_error("GEOSPreparedCovers_r failed");
        }
        return covers_value == 1;
    }

  private:
    GEOSGeometry* build_point_geometry(double x, double y) const {
        GEOSCoordSequence* sequence = GEOSCoordSeq_create_r(context_, 1, 2);
        if (sequence == nullptr) return nullptr;
        if (!GEOSCoordSeq_setX_r(context_, sequence, 0, x) ||
            !GEOSCoordSeq_setY_r(context_, sequence, 0, y)) {
            GEOSCoordSeq_destroy_r(context_, sequence);
            return nullptr;
        }
        return GEOSGeom_createPoint_r(context_, sequence);
    }

    GEOSGeometry* build_polygon_geometry(const RtdlPolygonRef& poly, const double* vertices_xy) const {
        size_t ring_size = poly.vertex_count;
        bool closed = ring_size > 0 &&
                      vertices_xy[poly.vertex_offset * 2] == vertices_xy[(poly.vertex_offset + poly.vertex_count - 1) * 2] &&
                      vertices_xy[poly.vertex_offset * 2 + 1] == vertices_xy[(poly.vertex_offset + poly.vertex_count - 1) * 2 + 1];
        if (!closed) {
            ring_size += 1;
        }
        GEOSCoordSequence* sequence = GEOSCoordSeq_create_r(context_, ring_size, 2);
        if (sequence == nullptr) return nullptr;
        for (size_t i = 0; i < poly.vertex_count; ++i) {
            const size_t vertex_index = poly.vertex_offset + i;
            if (!GEOSCoordSeq_setX_r(context_, sequence, i, vertices_xy[vertex_index * 2]) ||
                !GEOSCoordSeq_setY_r(context_, sequence, i, vertices_xy[vertex_index * 2 + 1])) {
                GEOSCoordSeq_destroy_r(context_, sequence);
                return nullptr;
            }
        }
        if (!closed) {
            if (!GEOSCoordSeq_setX_r(context_, sequence, ring_size - 1, vertices_xy[poly.vertex_offset * 2]) ||
                !GEOSCoordSeq_setY_r(context_, sequence, ring_size - 1, vertices_xy[poly.vertex_offset * 2 + 1])) {
                GEOSCoordSeq_destroy_r(context_, sequence);
                return nullptr;
            }
        }
        GEOSGeometry* ring = GEOSGeom_createLinearRing_r(context_, sequence);
        if (ring == nullptr) return nullptr;
        GEOSGeometry* polygon = GEOSGeom_createPolygon_r(context_, ring, nullptr, 0);
        if (polygon == nullptr) {
            GEOSGeom_destroy_r(context_, ring);
            return nullptr;
        }
        return polygon;
    }

    GEOSContextHandle_t context_;
    std::vector<GEOSGeometry*> geometries_;
    std::vector<const GEOSPreparedGeometry*> prepared_;
};
#endif

static bool exact_point_on_segment(
        double px,
        double py,
        double ax,
        double ay,
        double bx,
        double by)
{
    const double point_eps = 1.0e-12;
    const double len2 = (bx - ax) * (bx - ax) + (by - ay) * (by - ay);
    if (len2 <= point_eps * point_eps) {
        return std::abs(px - ax) <= point_eps && std::abs(py - ay) <= point_eps;
    }
    const double len = std::sqrt(len2);
    const double cross = (px - ax) * (by - ay) - (py - ay) * (bx - ax);
    if (std::abs(cross) > point_eps * len) {
        return false;
    }
    const double dot = (px - ax) * (bx - ax) + (py - ay) * (by - ay);
    const double along_eps = point_eps * len;
    if (dot < -along_eps) {
        return false;
    }
    return dot <= len2 + along_eps;
}

static bool exact_point_in_polygon(
        double x,
        double y,
        const RtdlPolygonRef& poly,
        const double* vertices_xy)
{
    const uint32_t n = poly.vertex_count;
    const uint32_t off = poly.vertex_offset;
    for (uint32_t i = 0; i < n; ++i) {
        const uint32_t j = (i + 1) % n;
        const double ax = vertices_xy[(off + i) * 2];
        const double ay = vertices_xy[(off + i) * 2 + 1];
        const double bx = vertices_xy[(off + j) * 2];
        const double by = vertices_xy[(off + j) * 2 + 1];
        if (exact_point_on_segment(x, y, ax, ay, bx, by)) {
            return true;
        }
    }

    bool inside = false;
    for (uint32_t i = 0, j = n - 1; i < n; j = i++) {
        const double xi = vertices_xy[(off + i) * 2];
        const double yi = vertices_xy[(off + i) * 2 + 1];
        const double xj = vertices_xy[(off + j) * 2];
        const double yj = vertices_xy[(off + j) * 2 + 1];
        if ((yi > y) != (yj > y)) {
            const double denom = (yj - yi) != 0.0 ? (yj - yi) : 1.0e-20;
            const double x_cross = (xj - xi) * (y - yi) / denom + xi;
            if (x <= x_cross) {
                inside = !inside;
            }
        }
    }
    return inside;
}

static bool exact_segment_hits_polygon(
        const RtdlSegment& segment,
        const RtdlPolygonRef& poly,
        const double* vertices_xy)
{
    if (exact_point_in_polygon(segment.x0, segment.y0, poly, vertices_xy) ||
        exact_point_in_polygon(segment.x1, segment.y1, poly, vertices_xy)) {
        return true;
    }
    const uint32_t n = poly.vertex_count;
    const uint32_t off = poly.vertex_offset;
    for (uint32_t i = 0; i < n; ++i) {
        const uint32_t j = (i + 1) % n;
        RtdlSegment edge{
            poly.id,
            vertices_xy[(off + i) * 2],
            vertices_xy[(off + i) * 2 + 1],
            vertices_xy[(off + j) * 2],
            vertices_xy[(off + j) * 2 + 1],
        };
        double ix = 0.0;
        double iy = 0.0;
        if (exact_segment_intersection(segment, edge, &ix, &iy)) {
            return true;
        }
    }
    return false;
}

static Bounds2D bounds_for_segment(const RtdlSegment& segment)
{
    return {
        std::min(segment.x0, segment.x1),
        std::min(segment.y0, segment.y1),
        std::max(segment.x0, segment.x1),
        std::max(segment.y0, segment.y1),
    };
}

static Bounds2D bounds_for_polygon(const RtdlPolygonRef& poly, const double* vertices_xy)
{
    Bounds2D bounds{
        vertices_xy[poly.vertex_offset * 2],
        vertices_xy[poly.vertex_offset * 2 + 1],
        vertices_xy[poly.vertex_offset * 2],
        vertices_xy[poly.vertex_offset * 2 + 1],
    };
    for (uint32_t i = 0; i < poly.vertex_count; ++i) {
        const size_t base = static_cast<size_t>(poly.vertex_offset + i) * 2;
        const double x = vertices_xy[base];
        const double y = vertices_xy[base + 1];
        bounds.min_x = std::min(bounds.min_x, x);
        bounds.min_y = std::min(bounds.min_y, y);
        bounds.max_x = std::max(bounds.max_x, x);
        bounds.max_y = std::max(bounds.max_y, y);
    }
    return bounds;
}

static bool bounds_overlap(const Bounds2D& left, const Bounds2D& right)
{
    return !(left.max_x < right.min_x || right.max_x < left.min_x ||
             left.max_y < right.min_y || right.max_y < left.min_y);
}

struct PolygonBucketIndex {
    double origin_x;
    double bucket_width;
    std::vector<std::vector<size_t>> buckets;
};

static PolygonBucketIndex build_polygon_bucket_index(const std::vector<Bounds2D>& polygon_bounds)
{
    if (polygon_bounds.empty()) {
        return {0.0, 1.0, {}};
    }
    double global_min = polygon_bounds.front().min_x;
    double global_max = polygon_bounds.front().max_x;
    for (const Bounds2D& bounds : polygon_bounds) {
        global_min = std::min(global_min, bounds.min_x);
        global_max = std::max(global_max, bounds.max_x);
    }
    const double span = std::max(global_max - global_min, 1.0e-9);
    const size_t bucket_count = std::max<size_t>(16, std::min<size_t>(polygon_bounds.size() * 2, 8192));
    const double bucket_width = span / static_cast<double>(bucket_count);
    std::vector<std::vector<size_t>> buckets(bucket_count);
    for (size_t polygon_index = 0; polygon_index < polygon_bounds.size(); ++polygon_index) {
        const Bounds2D& bounds = polygon_bounds[polygon_index];
        const auto first = static_cast<size_t>(std::clamp(
            static_cast<long long>(std::floor((bounds.min_x - global_min) / bucket_width)),
            0LL,
            static_cast<long long>(bucket_count - 1)));
        const auto last = static_cast<size_t>(std::clamp(
            static_cast<long long>(std::floor((bounds.max_x - global_min) / bucket_width)),
            0LL,
            static_cast<long long>(bucket_count - 1)));
        for (size_t bucket_id = first; bucket_id <= last; ++bucket_id) {
            buckets[bucket_id].push_back(polygon_index);
        }
    }
    return {global_min, bucket_width, std::move(buckets)};
}

static void run_seg_poly_hitcount_optix_host_indexed(
        const RtdlSegment*    segments,  size_t segment_count,
        const RtdlPolygonRef* polygons,  size_t polygon_count,
        const double* vertices_xy,
        RtdlSegmentPolygonHitCountRow** rows_out, size_t* row_count_out)
{
    std::vector<Bounds2D> polygon_bounds;
    polygon_bounds.reserve(polygon_count);
    for (size_t i = 0; i < polygon_count; ++i) {
        polygon_bounds.push_back(bounds_for_polygon(polygons[i], vertices_xy));
    }
    const PolygonBucketIndex bucket_index = build_polygon_bucket_index(polygon_bounds);
    std::vector<size_t> seen(polygon_count, 0);
    size_t stamp = 1;

    auto* out = static_cast<RtdlSegmentPolygonHitCountRow*>(
        std::malloc(sizeof(RtdlSegmentPolygonHitCountRow) * segment_count));
    if (!out && segment_count > 0) throw std::bad_alloc();
    for (size_t i = 0; i < segment_count; ++i) {
        const Bounds2D seg_bounds = bounds_for_segment(segments[i]);
        const size_t bucket_count = bucket_index.buckets.size();
        size_t first = 0;
        size_t last = 0;
        if (bucket_count > 0) {
            first = static_cast<size_t>(std::clamp(
                static_cast<long long>(std::floor((seg_bounds.min_x - bucket_index.origin_x) / bucket_index.bucket_width)),
                0LL,
                static_cast<long long>(bucket_count - 1)));
            last = static_cast<size_t>(std::clamp(
                static_cast<long long>(std::floor((seg_bounds.max_x - bucket_index.origin_x) / bucket_index.bucket_width)),
                0LL,
                static_cast<long long>(bucket_count - 1)));
        }
        uint32_t hit_count = 0;
        for (size_t bucket_id = first; bucket_id <= last && bucket_count > 0; ++bucket_id) {
            for (size_t polygon_index : bucket_index.buckets[bucket_id]) {
                if (seen[polygon_index] == stamp) {
                    continue;
                }
                seen[polygon_index] = stamp;
                if (!bounds_overlap(seg_bounds, polygon_bounds[polygon_index])) {
                    continue;
                }
                if (exact_segment_hits_polygon(segments[i], polygons[polygon_index], vertices_xy)) {
                    hit_count += 1;
                }
            }
        }
        out[i] = {segments[i].id, hit_count};
        stamp += 1;
        if (stamp == 0) {
            std::fill(seen.begin(), seen.end(), 0);
            stamp = 1;
        }
    }
    *rows_out = out;
    *row_count_out = segment_count;
}

static void run_seg_poly_anyhit_rows_optix_host_indexed(
        const RtdlSegment* segments, size_t segment_count,
        const RtdlPolygonRef* polygons, size_t polygon_count,
        const double* vertices_xy,
        RtdlSegmentPolygonAnyHitRow** rows_out, size_t* row_count_out)
{
    std::vector<Bounds2D> polygon_bounds;
    polygon_bounds.reserve(polygon_count);
    for (size_t i = 0; i < polygon_count; ++i) {
        polygon_bounds.push_back(bounds_for_polygon(polygons[i], vertices_xy));
    }
    const PolygonBucketIndex bucket_index = build_polygon_bucket_index(polygon_bounds);
    std::vector<size_t> seen(polygon_count, 0);
    size_t stamp = 1;
    std::vector<RtdlSegmentPolygonAnyHitRow> out_rows;
    out_rows.reserve(segment_count);

    for (size_t i = 0; i < segment_count; ++i) {
        const Bounds2D seg_bounds = bounds_for_segment(segments[i]);
        const size_t bucket_count = bucket_index.buckets.size();
        size_t first = 0;
        size_t last = 0;
        if (bucket_count > 0) {
            first = static_cast<size_t>(std::clamp(
                static_cast<long long>(std::floor((seg_bounds.min_x - bucket_index.origin_x) / bucket_index.bucket_width)),
                0LL,
                static_cast<long long>(bucket_count - 1)));
            last = static_cast<size_t>(std::clamp(
                static_cast<long long>(std::floor((seg_bounds.max_x - bucket_index.origin_x) / bucket_index.bucket_width)),
                0LL,
                static_cast<long long>(bucket_count - 1)));
        }
        for (size_t bucket_id = first; bucket_id <= last && bucket_count > 0; ++bucket_id) {
            for (size_t polygon_index : bucket_index.buckets[bucket_id]) {
                if (seen[polygon_index] == stamp) {
                    continue;
                }
                seen[polygon_index] = stamp;
                if (!bounds_overlap(seg_bounds, polygon_bounds[polygon_index])) {
                    continue;
                }
                if (exact_segment_hits_polygon(segments[i], polygons[polygon_index], vertices_xy)) {
                    out_rows.push_back({segments[i].id, polygons[polygon_index].id});
                }
            }
        }
        stamp += 1;
        if (stamp == 0) {
            std::fill(seen.begin(), seen.end(), 0);
            stamp = 1;
        }
    }

    auto* out = static_cast<RtdlSegmentPolygonAnyHitRow*>(
        std::malloc(sizeof(RtdlSegmentPolygonAnyHitRow) * out_rows.size()));
    if (!out && !out_rows.empty()) throw std::bad_alloc();
    if (!out_rows.empty()) {
        std::memcpy(out, out_rows.data(), sizeof(RtdlSegmentPolygonAnyHitRow) * out_rows.size());
    }
    *rows_out = out;
    *row_count_out = out_rows.size();
}

// ──────────────────────────────────────────────────────────────────────────────
// Workload implementations
// ──────────────────────────────────────────────────────────────────────────────

// ---------- LSI --------------------------------------------------------------

struct LsiLaunchParams {
    OptixTraversableHandle traversable;
    const GpuSegment* left_segs;
    const GpuSegment* right_segs;
    GpuLsiRecord*     output;
    uint32_t*         output_count;
    uint32_t          output_capacity;
    uint32_t          probe_count;
};

static void run_lsi_optix(
        const RtdlSegment* left,  size_t left_count,
        const RtdlSegment* right, size_t right_count,
        RtdlLsiRow** rows_out, size_t* row_count_out)
{
    std::call_once(g_lsi.init, [&]() {
        std::string ptx = compile_to_ptx(kLsiKernelSrc, "lsi_kernel.cu");
        g_lsi.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__lsi_probe",
            "__miss__lsi_miss",
            "__intersection__lsi_isect",
            "__anyhit__lsi_anyhit",
            nullptr,   // no closesthit
            4).release();
    });

    // Upload segments
    std::vector<GpuSegment> gpu_left(left_count), gpu_right(right_count);
    for (size_t i = 0; i < left_count; ++i)
        gpu_left[i]  = {(float)left[i].x0,  (float)left[i].y0,
                        (float)left[i].x1,  (float)left[i].y1,  left[i].id};
    for (size_t i = 0; i < right_count; ++i)
        gpu_right[i] = {(float)right[i].x0, (float)right[i].y0,
                        (float)right[i].x1, (float)right[i].y1, right[i].id};

    DevPtr d_left (sizeof(GpuSegment) * left_count);
    DevPtr d_right(sizeof(GpuSegment) * right_count);
    upload(d_left.ptr,  gpu_left.data(),  left_count);
    upload(d_right.ptr, gpu_right.data(), right_count);

    // Build BVH over right (build) segments
    std::vector<OptixAabb> aabbs(right_count);
    for (size_t i = 0; i < right_count; ++i)
        aabbs[i] = aabb_for_segment(gpu_right[i].x0, gpu_right[i].y0,
                                    gpu_right[i].x1, gpu_right[i].y1);
    AccelHolder accel = build_custom_accel(get_optix_context(), aabbs);

    // Output buffer
    uint32_t capacity = static_cast<uint32_t>(left_count * right_count);
    DevPtr d_output  (sizeof(GpuLsiRecord) * capacity);
    DevPtr d_count   (sizeof(uint32_t));
    uint32_t zero = 0;
    upload<uint32_t>(d_count.ptr, &zero, 1);

    // Launch params
    LsiLaunchParams lp;
    lp.traversable      = accel.handle;
    lp.left_segs        = reinterpret_cast<const GpuSegment*>(d_left.ptr);
    lp.right_segs       = reinterpret_cast<const GpuSegment*>(d_right.ptr);
    lp.output           = reinterpret_cast<GpuLsiRecord*>(d_output.ptr);
    lp.output_count     = reinterpret_cast<uint32_t*>(d_count.ptr);
    lp.output_capacity  = capacity;
    lp.probe_count      = static_cast<uint32_t>(left_count);

    DevPtr d_params(sizeof(LsiLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_lsi.pipe->pipeline, stream,
                             d_params.ptr, sizeof(LsiLaunchParams),
                             &g_lsi.pipe->sbt,
                             static_cast<unsigned>(left_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    // Read back results
    uint32_t gpu_count = 0;
    download(&gpu_count, d_count.ptr, 1);
    if (gpu_count > capacity)
        throw std::runtime_error("LSI output overflowed capacity");

    std::vector<GpuLsiRecord> gpu_rows(gpu_count);
    if (gpu_count > 0)
        download(gpu_rows.data(), d_output.ptr, gpu_count);

    std::unordered_map<uint32_t, const RtdlSegment*> left_by_id;
    std::unordered_map<uint32_t, const RtdlSegment*> right_by_id;
    left_by_id.reserve(left_count);
    right_by_id.reserve(right_count);
    for (size_t i = 0; i < left_count; ++i) {
        left_by_id.emplace(left[i].id, &left[i]);
    }
    for (size_t i = 0; i < right_count; ++i) {
        right_by_id.emplace(right[i].id, &right[i]);
    }

    std::vector<RtdlLsiRow> refined;
    refined.reserve(gpu_count);
    std::unordered_set<uint64_t> seen_pairs;
    seen_pairs.reserve(gpu_count * 2 + 1);

    for (uint32_t i = 0; i < gpu_count; ++i) {
        const auto left_it = left_by_id.find(gpu_rows[i].left_id);
        const auto right_it = right_by_id.find(gpu_rows[i].right_id);
        if (left_it == left_by_id.end() || right_it == right_by_id.end()) {
            continue;
        }
        const uint64_t pair_key =
            (static_cast<uint64_t>(gpu_rows[i].left_id) << 32) |
            static_cast<uint64_t>(gpu_rows[i].right_id);
        if (seen_pairs.find(pair_key) != seen_pairs.end()) {
            continue;
        }
        double ix = 0.0;
        double iy = 0.0;
        if (!exact_segment_intersection(*left_it->second, *right_it->second, &ix, &iy)) {
            continue;
        }
        seen_pairs.insert(pair_key);
        refined.push_back(
            RtdlLsiRow{
                gpu_rows[i].left_id,
                gpu_rows[i].right_id,
                ix,
                iy,
            });
    }

    auto* out = static_cast<RtdlLsiRow*>(std::malloc(sizeof(RtdlLsiRow) * refined.size()));
    if (!out && !refined.empty()) throw std::bad_alloc();
    for (size_t i = 0; i < refined.size(); ++i) {
        out[i] = refined[i];
    }
    *rows_out      = out;
    *row_count_out = refined.size();
}

// ---------- PIP --------------------------------------------------------------

struct PipLaunchParams {
    OptixTraversableHandle traversable;
    const float*     points_x;
    const float*     points_y;
    const uint32_t*  point_ids;
    const GpuPolygonRef* polygons;
    const float*     vertices_x;
    const float*     vertices_y;
    uint32_t*        hit_words;
    GpuPipRecord*    output;
    uint32_t*        output_count;
    uint32_t         output_capacity;
    uint32_t         positive_only;
    uint32_t         hit_word_count;
    uint32_t         polygon_count;
    uint32_t         probe_count;
};

static void run_pip_optix(
        const RtdlPoint* points,     size_t point_count,
        const RtdlPolygonRef* polys, size_t poly_count,
        const double* vertices_xy,   size_t vertex_xy_count,
        uint32_t positive_only,
        RtdlPipRow** rows_out, size_t* row_count_out)
{
    std::call_once(g_pip.init, [&]() {
        std::string ptx = compile_to_ptx(kPipKernelSrc, "pip_kernel.cu");
        g_pip.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__pip_probe",
            "__miss__pip_miss",
            "__intersection__pip_isect",
            "__anyhit__pip_anyhit",
            nullptr, 4).release();
    });

    size_t vert_count = vertex_xy_count / 2;

    // Build GPU polygon refs and vertex arrays
    std::vector<GpuPolygonRef> gpu_polys(poly_count);
    for (size_t i = 0; i < poly_count; ++i)
        gpu_polys[i] = {polys[i].id, polys[i].vertex_offset, polys[i].vertex_count};

    std::vector<float> vx(vert_count), vy(vert_count);
    for (size_t i = 0; i < vert_count; ++i) {
        vx[i] = static_cast<float>(vertices_xy[i * 2]);
        vy[i] = static_cast<float>(vertices_xy[i * 2 + 1]);
    }

    std::vector<float>    pts_x(point_count), pts_y(point_count);
    std::vector<uint32_t> pt_ids(point_count);
    for (size_t i = 0; i < point_count; ++i) {
        pts_x[i] = static_cast<float>(points[i].x);
        pts_y[i] = static_cast<float>(points[i].y);
        pt_ids[i] = points[i].id;
    }

    DevPtr d_polys  (sizeof(GpuPolygonRef) * poly_count);
    DevPtr d_vx     (sizeof(float) * vert_count);
    DevPtr d_vy     (sizeof(float) * vert_count);
    DevPtr d_pts_x  (sizeof(float) * point_count);
    DevPtr d_pts_y  (sizeof(float) * point_count);
    DevPtr d_pt_ids (sizeof(uint32_t) * point_count);
    upload(d_polys.ptr,   gpu_polys.data(), poly_count);
    upload(d_vx.ptr,      vx.data(),        vert_count);
    upload(d_vy.ptr,      vy.data(),        vert_count);
    upload(d_pts_x.ptr,   pts_x.data(),     point_count);
    upload(d_pts_y.ptr,   pts_y.data(),     point_count);
    upload(d_pt_ids.ptr,  pt_ids.data(),    point_count);

    // BVH over polygons
    std::vector<OptixAabb> aabbs(poly_count);
    for (size_t i = 0; i < poly_count; ++i)
        aabbs[i] = aabb_for_polygon(vertices_xy, polys[i].vertex_offset, polys[i].vertex_count);
    AccelHolder accel = build_custom_accel(get_optix_context(), aabbs);

    size_t out_count = point_count * poly_count;
    DevPtr d_count(sizeof(uint32_t));
    uint32_t zero = 0;
    upload<uint32_t>(d_count.ptr, &zero, 1);
    std::unique_ptr<DevPtr> d_hit_words;
    std::unique_ptr<DevPtr> d_output;
    if (positive_only == 0u) {
        d_output = std::make_unique<DevPtr>(sizeof(GpuPipRecord) * out_count);
        std::vector<GpuPipRecord> init_output(out_count);
        for (size_t pi = 0; pi < point_count; ++pi)
            for (size_t qi = 0; qi < poly_count; ++qi) {
                init_output[pi * poly_count + qi] = {pt_ids[pi], gpu_polys[qi].id, 0u};
            }
        upload(d_output->ptr, init_output.data(), out_count);
    } else {
        const size_t hit_word_count = (out_count + 31u) / 32u;
        d_hit_words = std::make_unique<DevPtr>(sizeof(uint32_t) * hit_word_count);
        CU_CHECK(cuMemsetD8(d_hit_words->ptr, 0, sizeof(uint32_t) * hit_word_count));
    }

    PipLaunchParams lp;
    lp.traversable    = accel.handle;
    lp.points_x       = reinterpret_cast<const float*>(d_pts_x.ptr);
    lp.points_y       = reinterpret_cast<const float*>(d_pts_y.ptr);
    lp.point_ids      = reinterpret_cast<const uint32_t*>(d_pt_ids.ptr);
    lp.polygons       = reinterpret_cast<const GpuPolygonRef*>(d_polys.ptr);
    lp.vertices_x     = reinterpret_cast<const float*>(d_vx.ptr);
    lp.vertices_y     = reinterpret_cast<const float*>(d_vy.ptr);
    const uint32_t hit_word_count = positive_only == 0u
        ? 0u
        : static_cast<uint32_t>((out_count + 31u) / 32u);
    lp.hit_words      = d_hit_words ? reinterpret_cast<uint32_t*>(d_hit_words->ptr) : nullptr;
    lp.output         = d_output ? reinterpret_cast<GpuPipRecord*>(d_output->ptr) : nullptr;
    lp.output_count   = reinterpret_cast<uint32_t*>(d_count.ptr);
    lp.output_capacity = d_output ? static_cast<uint32_t>(out_count) : 0u;
    lp.positive_only  = positive_only;
    lp.hit_word_count = hit_word_count;
    lp.polygon_count  = static_cast<uint32_t>(poly_count);
    lp.probe_count    = static_cast<uint32_t>(point_count);

    DevPtr d_params(sizeof(PipLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    if (positive_only == 0u) {
        OPTIX_CHECK(optixLaunch(g_pip.pipe->pipeline, stream,
                                 d_params.ptr, sizeof(PipLaunchParams),
                                 &g_pip.pipe->sbt,
                                 static_cast<unsigned>(point_count), 1, 1));
        CU_CHECK(cuStreamSynchronize(stream));
    }

    // Read back
    if (positive_only != 0u) {
        // Single positive-only launch: reset the shared output counter just
        // before launch. The launch params themselves are unchanged.
        upload<uint32_t>(d_count.ptr, &zero, 1);
        OPTIX_CHECK(optixLaunch(g_pip.pipe->pipeline, stream,
                                 d_params.ptr, sizeof(PipLaunchParams),
                                 &g_pip.pipe->sbt,
                                 static_cast<unsigned>(point_count), 1, 1));
        CU_CHECK(cuStreamSynchronize(stream));
        std::vector<uint32_t> hit_words(hit_word_count);
        if (hit_word_count > 0) {
            download(hit_words.data(), d_hit_words->ptr, hit_word_count);
        }
        std::vector<RtdlPipRow> rows;
        rows.reserve(out_count / 64u);
#if RTDL_OPTIX_HAS_GEOS
        GeosPreparedPolygonRefs geos(polys, poly_count, vertices_xy);
#endif
        for (size_t pi = 0; pi < point_count; ++pi) {
            for (size_t qi = 0; qi < poly_count; ++qi) {
                const size_t slot = pi * poly_count + qi;
                const uint32_t word = static_cast<uint32_t>(slot >> 5);
                const uint32_t bit  = 1u << (slot & 31u);
                if ((hit_words[word] & bit) == 0u) {
                    continue;
                }
                const RtdlPoint& point = points[pi];
                const RtdlPolygonRef& polygon = polys[qi];
#if RTDL_OPTIX_HAS_GEOS
                if (!geos.covers(qi, point.x, point.y)) {
                    continue;
                }
#else
                if (!exact_point_in_polygon(point.x, point.y, polygon, vertices_xy)) {
                    continue;
                }
#endif
                rows.push_back({point.id, polygon.id, 1u});
            }
        }
        auto* out = static_cast<RtdlPipRow*>(std::malloc(sizeof(RtdlPipRow) * rows.size()));
        if (!out && !rows.empty()) throw std::bad_alloc();
        for (size_t i = 0; i < rows.size(); ++i) {
            out[i] = rows[i];
        }
        *rows_out = out;
        *row_count_out = rows.size();
        return;
    }

    std::vector<GpuPipRecord> gpu_rows(out_count);
    download(gpu_rows.data(), d_output->ptr, out_count);

    auto* out = static_cast<RtdlPipRow*>(std::malloc(sizeof(RtdlPipRow) * out_count));
    if (!out) throw std::bad_alloc();
    for (size_t i = 0; i < out_count; ++i) {
        out[i].point_id   = gpu_rows[i].point_id;
        out[i].polygon_id = gpu_rows[i].polygon_id;
        out[i].contains   = gpu_rows[i].contains;
    }

#if RTDL_OPTIX_HAS_GEOS
    GeosPreparedPolygonRefs geos(polys, poly_count, vertices_xy);
    for (size_t pi = 0; pi < point_count; ++pi) {
        for (size_t qi = 0; qi < poly_count; ++qi) {
            const size_t out_index = pi * poly_count + qi;
            out[out_index].point_id = points[pi].id;
            out[out_index].polygon_id = polys[qi].id;
            out[out_index].contains = geos.covers(qi, points[pi].x, points[pi].y) ? 1u : 0u;
        }
    }
#else
    std::unordered_map<uint32_t, const RtdlPoint*> point_by_id;
    std::unordered_map<uint32_t, const RtdlPolygonRef*> poly_by_id;
    point_by_id.reserve(point_count);
    poly_by_id.reserve(poly_count);
    for (size_t i = 0; i < point_count; ++i) {
        point_by_id.emplace(points[i].id, &points[i]);
    }
    for (size_t i = 0; i < poly_count; ++i) {
        poly_by_id.emplace(polys[i].id, &polys[i]);
    }
    for (size_t i = 0; i < out_count; ++i) {
        const auto point_it = point_by_id.find(out[i].point_id);
        const auto poly_it = poly_by_id.find(out[i].polygon_id);
        if (point_it == point_by_id.end() || poly_it == poly_by_id.end()) {
            out[i].contains = 0;
            continue;
        }
        out[i].contains = exact_point_in_polygon(
            point_it->second->x,
            point_it->second->y,
            *poly_it->second,
            vertices_xy)
            ? 1u
            : 0u;
    }
#endif
    *rows_out      = out;
    *row_count_out = out_count;
}

// ---------- Overlay ----------------------------------------------------------

struct OverlayLaunchParams {
    OptixTraversableHandle traversable;
    const GpuPolygonRef* left_polygons;
    const GpuPolygonRef* right_polygons;
    const float* left_vx;
    const float* left_vy;
    const float* right_vx;
    const float* right_vy;
    GpuOverlayFlags* output;
    uint32_t  right_count;
    uint32_t  left_count;
    uint32_t  launch_count;
    uint32_t  max_edges_per_poly;
};

static void run_overlay_optix(
        const RtdlPolygonRef* left_polys,  size_t left_count,
        const double* left_verts_xy,       size_t left_vert_xy_count,
        const RtdlPolygonRef* right_polys, size_t right_count,
        const double* right_verts_xy,      size_t right_vert_xy_count,
        RtdlOverlayRow** rows_out, size_t* row_count_out)
{
    std::call_once(g_overlay.init, [&]() {
        std::string ptx = compile_to_ptx(kOverlayKernelSrc, "overlay_kernel.cu");
        g_overlay.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__overlay_probe",
            "__miss__overlay_miss",
            "__intersection__overlay_isect",
            "__anyhit__overlay_anyhit",
            nullptr, 4).release();
    });

    size_t lv_count = left_vert_xy_count / 2;
    size_t rv_count = right_vert_xy_count / 2;

    std::vector<GpuPolygonRef> gpu_lp(left_count), gpu_rp(right_count);
    for (size_t i = 0; i < left_count;  ++i)
        gpu_lp[i] = {left_polys[i].id,  left_polys[i].vertex_offset,  left_polys[i].vertex_count};
    for (size_t i = 0; i < right_count; ++i)
        gpu_rp[i] = {right_polys[i].id, right_polys[i].vertex_offset, right_polys[i].vertex_count};

    std::vector<float> lvx(lv_count), lvy(lv_count), rvx(rv_count), rvy(rv_count);
    for (size_t i = 0; i < lv_count; ++i) {
        lvx[i] = static_cast<float>(left_verts_xy[i * 2]);
        lvy[i] = static_cast<float>(left_verts_xy[i * 2 + 1]);
    }
    for (size_t i = 0; i < rv_count; ++i) {
        rvx[i] = static_cast<float>(right_verts_xy[i * 2]);
        rvy[i] = static_cast<float>(right_verts_xy[i * 2 + 1]);
    }

    // Find max edges across all left polygons for launch stride
    uint32_t max_edges = 0;
    for (size_t i = 0; i < left_count; ++i)
        max_edges = std::max(max_edges, left_polys[i].vertex_count);

    DevPtr d_lp  (sizeof(GpuPolygonRef) * left_count);
    DevPtr d_rp  (sizeof(GpuPolygonRef) * right_count);
    DevPtr d_lvx (sizeof(float) * lv_count);
    DevPtr d_lvy (sizeof(float) * lv_count);
    DevPtr d_rvx (sizeof(float) * rv_count);
    DevPtr d_rvy (sizeof(float) * rv_count);
    upload(d_lp.ptr,  gpu_lp.data(), left_count);
    upload(d_rp.ptr,  gpu_rp.data(), right_count);
    upload(d_lvx.ptr, lvx.data(), lv_count);
    upload(d_lvy.ptr, lvy.data(), lv_count);
    upload(d_rvx.ptr, rvx.data(), rv_count);
    upload(d_rvy.ptr, rvy.data(), rv_count);

    // BVH over right polygon bboxes
    std::vector<OptixAabb> aabbs(right_count);
    for (size_t i = 0; i < right_count; ++i)
        aabbs[i] = aabb_for_polygon(right_verts_xy, right_polys[i].vertex_offset, right_polys[i].vertex_count);
    AccelHolder accel = build_custom_accel(get_optix_context(), aabbs);

    // Pre-allocated output: left_count * right_count, all zeros
    size_t out_count = left_count * right_count;
    DevPtr d_output(sizeof(GpuOverlayFlags) * out_count);
    CU_CHECK(cuMemsetD8(d_output.ptr, 0, sizeof(GpuOverlayFlags) * out_count));

    uint32_t launch_count = static_cast<uint32_t>(left_count) * max_edges;

    OverlayLaunchParams lp;
    lp.traversable         = accel.handle;
    lp.left_polygons       = reinterpret_cast<const GpuPolygonRef*>(d_lp.ptr);
    lp.right_polygons      = reinterpret_cast<const GpuPolygonRef*>(d_rp.ptr);
    lp.left_vx             = reinterpret_cast<const float*>(d_lvx.ptr);
    lp.left_vy             = reinterpret_cast<const float*>(d_lvy.ptr);
    lp.right_vx            = reinterpret_cast<const float*>(d_rvx.ptr);
    lp.right_vy            = reinterpret_cast<const float*>(d_rvy.ptr);
    lp.output              = reinterpret_cast<GpuOverlayFlags*>(d_output.ptr);
    lp.right_count         = static_cast<uint32_t>(right_count);
    lp.left_count          = static_cast<uint32_t>(left_count);
    lp.launch_count        = launch_count;
    lp.max_edges_per_poly  = max_edges;

    DevPtr d_params(sizeof(OverlayLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_overlay.pipe->pipeline, stream,
                             d_params.ptr, sizeof(OverlayLaunchParams),
                             &g_overlay.pipe->sbt,
                             launch_count, 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    // Also compute PIP flags: for each (left_poly, right_poly) pair, check if
    // any vertex of one polygon is inside the other.  Done on CPU after the
    // GPU LSI pass to keep the device kernel simple.
    std::vector<GpuOverlayFlags> gpu_flags(out_count);
    download(gpu_flags.data(), d_output.ptr, out_count);

    // CPU PIP supplement: match the current RTDL oracle semantics exactly.
    // overlay_compose_cpu checks only the first vertex of each polygon.
#if RTDL_OPTIX_HAS_GEOS
    GeosPreparedPolygonRefs left_geos(left_polys, left_count, left_verts_xy);
    GeosPreparedPolygonRefs right_geos(right_polys, right_count, right_verts_xy);
#endif

    for (size_t li = 0; li < left_count; ++li) {
        for (size_t ri = 0; ri < right_count; ++ri) {
            size_t slot = li * right_count + ri;
            if (gpu_flags[slot].requires_pip) continue; // already set by GPU
            bool found = false;
            if (left_polys[li].vertex_count > 0) {
                double lxv = left_verts_xy[left_polys[li].vertex_offset * 2];
                double lyv = left_verts_xy[left_polys[li].vertex_offset * 2 + 1];
#if RTDL_OPTIX_HAS_GEOS
                if (right_geos.covers(ri, lxv, lyv))
#else
                if (exact_point_in_polygon(lxv, lyv, right_polys[ri], right_verts_xy))
#endif
                    found = true;
            }
            if (!found && right_polys[ri].vertex_count > 0) {
                double rxv = right_verts_xy[right_polys[ri].vertex_offset * 2];
                double ryv = right_verts_xy[right_polys[ri].vertex_offset * 2 + 1];
#if RTDL_OPTIX_HAS_GEOS
                if (left_geos.covers(li, rxv, ryv))
#else
                if (exact_point_in_polygon(rxv, ryv, left_polys[li], left_verts_xy))
#endif
                    found = true;
            }
            if (found)
                gpu_flags[slot].requires_pip = 1;
        }
    }

    auto* out = static_cast<RtdlOverlayRow*>(std::malloc(sizeof(RtdlOverlayRow) * out_count));
    if (!out) throw std::bad_alloc();
    for (size_t i = 0; i < out_count; ++i) {
        size_t li = i / right_count, ri = i % right_count;
        out[i].left_polygon_id  = left_polys[li].id;
        out[i].right_polygon_id = right_polys[ri].id;
        out[i].requires_lsi     = gpu_flags[i].requires_lsi;
        out[i].requires_pip     = gpu_flags[i].requires_pip;
    }
    *rows_out      = out;
    *row_count_out = out_count;
}

// ---------- Ray-triangle hit count ------------------------------------------

struct RayHitCountLaunchParams {
    OptixTraversableHandle traversable;
    const GpuRay*          rays;
    const GpuTriangle*     triangles;
    GpuRayHitRecord*       output;
    uint32_t               ray_count;
};

static void run_ray_hitcount_optix(
        const RtdlRay2D*    rays,      size_t ray_count,
        const RtdlTriangle* triangles, size_t triangle_count,
        RtdlRayHitCountRow** rows_out, size_t* row_count_out)
{
    std::call_once(g_rayhit.init, [&]() {
        std::string ptx = compile_to_ptx(kRayHitCountKernelSrc, "rayhit_kernel.cu");
        g_rayhit.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__rayhit_probe",
            "__miss__rayhit_miss",
            "__intersection__rayhit_isect",
            "__anyhit__rayhit_anyhit",
            nullptr, 4).release();
    });

    std::vector<GpuRay>      gpu_rays(ray_count);
    std::vector<GpuTriangle> gpu_tris(triangle_count);
    for (size_t i = 0; i < ray_count; ++i)
        gpu_rays[i] = {(float)rays[i].ox, (float)rays[i].oy,
                       (float)rays[i].dx, (float)rays[i].dy,
                       (float)rays[i].tmax, rays[i].id};
    for (size_t i = 0; i < triangle_count; ++i)
        gpu_tris[i] = {(float)triangles[i].x0, (float)triangles[i].y0,
                       (float)triangles[i].x1, (float)triangles[i].y1,
                       (float)triangles[i].x2, (float)triangles[i].y2, triangles[i].id};

    DevPtr d_rays(sizeof(GpuRay)      * ray_count);
    DevPtr d_tris(sizeof(GpuTriangle) * triangle_count);
    upload(d_rays.ptr, gpu_rays.data(), ray_count);
    upload(d_tris.ptr, gpu_tris.data(), triangle_count);

    std::vector<OptixAabb> aabbs(triangle_count);
    for (size_t i = 0; i < triangle_count; ++i)
        aabbs[i] = aabb_for_triangle(gpu_tris[i].x0, gpu_tris[i].y0,
                                     gpu_tris[i].x1, gpu_tris[i].y1,
                                     gpu_tris[i].x2, gpu_tris[i].y2);
    AccelHolder accel = build_custom_accel(get_optix_context(), aabbs);

    DevPtr d_output(sizeof(GpuRayHitRecord) * ray_count);

    RayHitCountLaunchParams lp;
    lp.traversable = accel.handle;
    lp.rays        = reinterpret_cast<const GpuRay*>(d_rays.ptr);
    lp.triangles   = reinterpret_cast<const GpuTriangle*>(d_tris.ptr);
    lp.output      = reinterpret_cast<GpuRayHitRecord*>(d_output.ptr);
    lp.ray_count   = static_cast<uint32_t>(ray_count);

    DevPtr d_params(sizeof(RayHitCountLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_rayhit.pipe->pipeline, stream,
                             d_params.ptr, sizeof(RayHitCountLaunchParams),
                             &g_rayhit.pipe->sbt,
                             static_cast<unsigned>(ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    std::vector<GpuRayHitRecord> gpu_rows(ray_count);
    download(gpu_rows.data(), d_output.ptr, ray_count);

    auto* out = static_cast<RtdlRayHitCountRow*>(
        std::malloc(sizeof(RtdlRayHitCountRow) * ray_count));
    if (!out && ray_count > 0) throw std::bad_alloc();
    for (size_t i = 0; i < ray_count; ++i) {
        out[i].ray_id    = gpu_rows[i].ray_id;
        out[i].hit_count = gpu_rows[i].hit_count;
    }
    *rows_out      = out;
    *row_count_out = ray_count;
}

// ---------- Segment-polygon hitcount ----------------------------------------

struct SegPolyLaunchParams {
    OptixTraversableHandle traversable;
    const GpuSegment*    segments;
    const GpuPolygonRef* polygons;
    const float* vertices_x;
    const float* vertices_y;
    GpuSegPolyRecord* output;
    uint32_t segment_count;
};

static void run_seg_poly_hitcount_optix(
        const RtdlSegment*    segments,  size_t segment_count,
        const RtdlPolygonRef* polygons,  size_t polygon_count,
        const double* vertices_xy,       size_t vertex_xy_count,
        RtdlSegmentPolygonHitCountRow** rows_out, size_t* row_count_out)
{
    if (const char* mode = std::getenv("RTDL_OPTIX_SEGPOLY_MODE");
        mode == nullptr || std::string(mode) != "native") {
        run_seg_poly_hitcount_optix_host_indexed(
            segments, segment_count, polygons, polygon_count, vertices_xy, rows_out, row_count_out);
        return;
    }

    if (polygon_count == 0) {
        auto* out = static_cast<RtdlSegmentPolygonHitCountRow*>(
            std::malloc(sizeof(RtdlSegmentPolygonHitCountRow) * segment_count));
        if (!out && segment_count > 0) throw std::bad_alloc();
        for (size_t i = 0; i < segment_count; ++i) {
            out[i].segment_id = segments[i].id;
            out[i].hit_count = 0u;
        }
        *rows_out = out;
        *row_count_out = segment_count;
        return;
    }

    std::call_once(g_segpoly.init, [&]() {
        std::string ptx = compile_to_ptx(kSegPolyHitcountKernelSrc, "segpoly_kernel.cu");
        g_segpoly.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__segpoly_probe",
            "__miss__segpoly_miss",
            "__intersection__segpoly_isect",
            "__anyhit__segpoly_anyhit",
            nullptr,
            4).release();
    });

    const size_t vert_count = vertex_xy_count / 2;
    std::vector<GpuSegment> gpu_segments(segment_count);
    std::vector<GpuPolygonRef> gpu_polygons(polygon_count);
    std::vector<float> vx(vert_count), vy(vert_count);
    for (size_t i = 0; i < segment_count; ++i) {
        gpu_segments[i] = {
            static_cast<float>(segments[i].x0),
            static_cast<float>(segments[i].y0),
            static_cast<float>(segments[i].x1),
            static_cast<float>(segments[i].y1),
            segments[i].id,
        };
    }
    for (size_t i = 0; i < polygon_count; ++i) {
        gpu_polygons[i] = {polygons[i].id, polygons[i].vertex_offset, polygons[i].vertex_count};
    }
    for (size_t i = 0; i < vert_count; ++i) {
        vx[i] = static_cast<float>(vertices_xy[i * 2]);
        vy[i] = static_cast<float>(vertices_xy[i * 2 + 1]);
    }

    DevPtr d_segments(sizeof(GpuSegment) * segment_count);
    DevPtr d_polygons(sizeof(GpuPolygonRef) * polygon_count);
    DevPtr d_vx(sizeof(float) * vert_count);
    DevPtr d_vy(sizeof(float) * vert_count);
    upload(d_segments.ptr, gpu_segments.data(), segment_count);
    upload(d_polygons.ptr, gpu_polygons.data(), polygon_count);
    upload(d_vx.ptr, vx.data(), vert_count);
    upload(d_vy.ptr, vy.data(), vert_count);

    std::vector<OptixAabb> aabbs(polygon_count);
    for (size_t i = 0; i < polygon_count; ++i) {
        aabbs[i] = aabb_for_polygon(vertices_xy, polygons[i].vertex_offset, polygons[i].vertex_count);
    }
    AccelHolder accel = build_custom_accel(get_optix_context(), aabbs);

    DevPtr d_output(sizeof(GpuSegPolyRecord) * segment_count);

    SegPolyLaunchParams lp;
    lp.traversable = accel.handle;
    lp.segments = reinterpret_cast<const GpuSegment*>(d_segments.ptr);
    lp.polygons = reinterpret_cast<const GpuPolygonRef*>(d_polygons.ptr);
    lp.vertices_x = reinterpret_cast<const float*>(d_vx.ptr);
    lp.vertices_y = reinterpret_cast<const float*>(d_vy.ptr);
    lp.output = reinterpret_cast<GpuSegPolyRecord*>(d_output.ptr);
    lp.segment_count = static_cast<uint32_t>(segment_count);

    DevPtr d_params(sizeof(SegPolyLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_segpoly.pipe->pipeline, stream,
                             d_params.ptr, sizeof(SegPolyLaunchParams),
                             &g_segpoly.pipe->sbt,
                             static_cast<unsigned>(segment_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    std::vector<GpuSegPolyRecord> gpu_rows(segment_count);
    download(gpu_rows.data(), d_output.ptr, segment_count);

    auto* out = static_cast<RtdlSegmentPolygonHitCountRow*>(
        std::malloc(sizeof(RtdlSegmentPolygonHitCountRow) * segment_count));
    if (!out && segment_count > 0) throw std::bad_alloc();
    for (size_t i = 0; i < segment_count; ++i) {
        out[i].segment_id = gpu_rows[i].segment_id;
        out[i].hit_count = gpu_rows[i].hit_count;
    }
    *rows_out = out;
    *row_count_out = segment_count;
}

// ---------- Point-nearest-segment (CUDA parallel brute-force) ---------------

static void run_point_nearest_segment_cuda(
        const RtdlPoint*   points,   size_t point_count,
        const RtdlSegment* segments, size_t segment_count,
        RtdlPointNearestSegmentRow** rows_out, size_t* row_count_out)
{
    std::call_once(g_pns.init, [&]() {
        std::string ptx = compile_to_ptx(kPointNearestKernelSrc, "pns_kernel.cu");
        CU_CHECK(cuModuleLoadData(&g_pns.module, ptx.c_str()));
        CU_CHECK(cuModuleGetFunction(&g_pns.fn, g_pns.module, "point_nearest_segment"));
    });

    struct GpuPt  { float x, y; uint32_t id; };
    struct GpuSeg { float x0, y0, x1, y1; uint32_t id; };
    struct GpuPnsRec { uint32_t point_id, segment_id; float distance; };

    std::vector<GpuPt>  gpu_pts (point_count);
    std::vector<GpuSeg> gpu_segs(segment_count);
    for (size_t i = 0; i < point_count; ++i)
        gpu_pts[i] = {(float)points[i].x, (float)points[i].y, points[i].id};
    for (size_t i = 0; i < segment_count; ++i)
        gpu_segs[i] = {(float)segments[i].x0, (float)segments[i].y0,
                       (float)segments[i].x1, (float)segments[i].y1, segments[i].id};

    DevPtr d_pts (sizeof(GpuPt)  * point_count);
    DevPtr d_segs(sizeof(GpuSeg) * segment_count);
    DevPtr d_out (sizeof(GpuPnsRec) * point_count);
    upload(d_pts.ptr,  gpu_pts.data(),  point_count);
    upload(d_segs.ptr, gpu_segs.data(), segment_count);

    uint32_t pc = static_cast<uint32_t>(point_count);
    uint32_t sc = static_cast<uint32_t>(segment_count);
    void* args[] = { &d_pts.ptr, &pc, &d_segs.ptr, &sc, &d_out.ptr };

    unsigned block = 256;
    unsigned grid  = (pc + block - 1) / block;
    CU_CHECK(cuLaunchKernel(g_pns.fn, grid, 1, 1, block, 1, 1,
                             0, nullptr, args, nullptr));
    CU_CHECK(cuStreamSynchronize(nullptr));

    std::vector<GpuPnsRec> gpu_rows(point_count);
    download(gpu_rows.data(), d_out.ptr, point_count);

    auto* out = static_cast<RtdlPointNearestSegmentRow*>(
        std::malloc(sizeof(RtdlPointNearestSegmentRow) * point_count));
    if (!out && point_count > 0) throw std::bad_alloc();
    for (size_t i = 0; i < point_count; ++i) {
        out[i].point_id   = gpu_rows[i].point_id;
        out[i].segment_id = gpu_rows[i].segment_id;
        out[i].distance   = static_cast<double>(gpu_rows[i].distance);
    }
    *rows_out      = out;
    *row_count_out = point_count;
}

} // anonymous namespace

// ──────────────────────────────────────────────────────────────────────────────
// Public C entry points
// ──────────────────────────────────────────────────────────────────────────────

extern "C" int rtdl_optix_get_version(int* major_out, int* minor_out, int* patch_out) {
    if (!major_out || !minor_out || !patch_out) return 1;
    *major_out = OPTIX_VERSION / 10000;
    *minor_out = (OPTIX_VERSION % 10000) / 100;
    *patch_out = OPTIX_VERSION % 100;
    return 0;
}

extern "C" int rtdl_optix_run_lsi(
        const RtdlSegment* left,  size_t left_count,
        const RtdlSegment* right, size_t right_count,
        RtdlLsiRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (left_count == 0 || right_count == 0) return;
        run_lsi_optix(left, left_count, right, right_count, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_pip(
        const RtdlPoint* points,     size_t point_count,
        const RtdlPolygonRef* polys, size_t poly_count,
        const double* vertices_xy,   size_t vertex_xy_count,
        uint32_t positive_only,
        RtdlPipRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (point_count == 0 || poly_count == 0) return;
        run_pip_optix(points, point_count, polys, poly_count,
                      vertices_xy, vertex_xy_count, positive_only, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_overlay(
        const RtdlPolygonRef* left_polys,  size_t left_count,
        const double* left_verts_xy,       size_t left_vert_xy_count,
        const RtdlPolygonRef* right_polys, size_t right_count,
        const double* right_verts_xy,      size_t right_vert_xy_count,
        RtdlOverlayRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (left_count == 0 || right_count == 0) return;
        run_overlay_optix(left_polys, left_count, left_verts_xy, left_vert_xy_count,
                          right_polys, right_count, right_verts_xy, right_vert_xy_count,
                          rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_ray_hitcount(
        const RtdlRay2D*    rays,      size_t ray_count,
        const RtdlTriangle* triangles, size_t triangle_count,
        RtdlRayHitCountRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (ray_count == 0) return;
        run_ray_hitcount_optix(rays, ray_count, triangles, triangle_count,
                               rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_segment_polygon_hitcount(
        const RtdlSegment*    segments,  size_t segment_count,
        const RtdlPolygonRef* polygons,  size_t polygon_count,
        const double* vertices_xy,       size_t vertex_xy_count,
        RtdlSegmentPolygonHitCountRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (segment_count == 0) return;
        run_seg_poly_hitcount_optix(segments, segment_count,
                                    polygons, polygon_count,
                                    vertices_xy, vertex_xy_count,
                                    rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_segment_polygon_anyhit_rows(
        const RtdlSegment* segments, size_t segment_count,
        const RtdlPolygonRef* polygons, size_t polygon_count,
        const double* vertices_xy, size_t vertex_xy_count,
        RtdlSegmentPolygonAnyHitRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (segment_count == 0 || polygon_count == 0) return;
        (void)vertex_xy_count;
        run_seg_poly_anyhit_rows_optix_host_indexed(
            segments, segment_count, polygons, polygon_count, vertices_xy, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_point_nearest_segment(
        const RtdlPoint*   points,   size_t point_count,
        const RtdlSegment* segments, size_t segment_count,
        RtdlPointNearestSegmentRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (point_count == 0) return;
        run_point_nearest_segment_cuda(points, point_count,
                                       segments, segment_count,
                                       rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_free_rows(void* rows) {
    std::free(rows);
}

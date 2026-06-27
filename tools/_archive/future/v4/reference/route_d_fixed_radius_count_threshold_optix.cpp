#include <optix.h>
#include <optix_function_table_definition.h>
#include <optix_stack_size.h>
#include <optix_stubs.h>

#include <cuda.h>
#include <nvrtc.h>

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

constexpr double kRadius = 0.35;
constexpr uint32_t kThreshold = 3;
constexpr float kRadiusPad = 1.0e-4f;

struct HostPoint {
    uint32_t id;
    double x;
    double y;
};

struct GpuPoint {
    float x;
    float y;
    uint32_t id;
    uint32_t pad;
};

struct CountRecord {
    uint32_t query_id;
    uint32_t neighbor_count;
    uint32_t threshold_reached;
};

struct LaunchParams {
    OptixTraversableHandle traversable;
    const GpuPoint* query_points;
    const GpuPoint* search_points;
    CountRecord* output;
    uint32_t* threshold_reached_count;
    uint32_t query_count;
    uint32_t threshold;
    float radius;
    float trace_tmax;
};

struct EmptyData {};

template <typename T>
struct alignas(OPTIX_SBT_RECORD_ALIGNMENT) SbtRecord {
    char header[OPTIX_SBT_RECORD_HEADER_SIZE];
    T data;
};

using RaygenRecord = SbtRecord<EmptyData>;
using MissRecord = SbtRecord<EmptyData>;
using HitRecord = SbtRecord<EmptyData>;

struct DevPtr {
    CUdeviceptr ptr = 0;

    DevPtr() = default;
    explicit DevPtr(size_t bytes) {
        if (bytes != 0) {
            check_cuda(cuMemAlloc(&ptr, bytes), "cuMemAlloc");
        }
    }

    ~DevPtr() {
        if (ptr != 0) {
            cuMemFree(ptr);
        }
    }

    DevPtr(const DevPtr&) = delete;
    DevPtr& operator=(const DevPtr&) = delete;

    DevPtr(DevPtr&& other) noexcept : ptr(other.ptr) {
        other.ptr = 0;
    }

    DevPtr& operator=(DevPtr&& other) noexcept {
        if (this != &other) {
            if (ptr != 0) {
                cuMemFree(ptr);
            }
            ptr = other.ptr;
            other.ptr = 0;
        }
        return *this;
    }

    static void check_cuda(CUresult result, const char* what) {
        if (result == CUDA_SUCCESS) {
            return;
        }
        const char* name = nullptr;
        const char* text = nullptr;
        cuGetErrorName(result, &name);
        cuGetErrorString(result, &text);
        std::ostringstream oss;
        oss << what << " failed: " << (name ? name : "CUDA_ERROR")
            << " " << (text ? text : "");
        throw std::runtime_error(oss.str());
    }
};

void check_cuda(CUresult result, const char* what) {
    DevPtr::check_cuda(result, what);
}

void check_nvrtc(nvrtcResult result, const char* what) {
    if (result != NVRTC_SUCCESS) {
        std::ostringstream oss;
        oss << what << " failed: " << nvrtcGetErrorString(result);
        throw std::runtime_error(oss.str());
    }
}

void check_optix(OptixResult result, const char* what) {
    if (result != OPTIX_SUCCESS) {
        std::ostringstream oss;
        oss << what << " failed: " << optixGetErrorString(result);
        throw std::runtime_error(oss.str());
    }
}

template <typename T>
void upload(CUdeviceptr dst, const T* src, size_t count) {
    if (count == 0) {
        return;
    }
    check_cuda(cuMemcpyHtoD(dst, src, sizeof(T) * count), "cuMemcpyHtoD");
}

template <typename T>
void download(T* dst, CUdeviceptr src, size_t count) {
    if (count == 0) {
        return;
    }
    check_cuda(cuMemcpyDtoH(dst, src, sizeof(T) * count), "cuMemcpyDtoH");
}

const char* kKernelSource = R"CUDA(
#include <optix_device.h>
#include <stdint.h>

typedef unsigned int uint32_t;

struct GpuPoint { float x, y; uint32_t id; uint32_t pad; };
struct CountRecord { uint32_t query_id, neighbor_count, threshold_reached; };

struct LaunchParams {
    OptixTraversableHandle traversable;
    const GpuPoint* query_points;
    const GpuPoint* search_points;
    CountRecord* output;
    uint32_t* threshold_reached_count;
    uint32_t query_count;
    uint32_t threshold;
    float radius;
    float trace_tmax;
};

extern "C" {
__constant__ LaunchParams params;
}

extern "C" __global__ void __raygen__fixed_radius_count_threshold() {
    const uint32_t idx = optixGetLaunchIndex().x;
    if (idx >= params.query_count) return;
    const GpuPoint q = params.query_points[idx];
    unsigned int p0 = idx;
    unsigned int p1 = 0u;
    unsigned int p2 = 0u;
    optixTrace(params.traversable,
               make_float3(q.x, q.y, -params.radius),
               make_float3(0.0f, 0.0f, 1.0f),
               0.0f, params.trace_tmax, 0.0f,
               OptixVisibilityMask(255),
               OPTIX_RAY_FLAG_NONE,
               0, 1, 0,
               p0, p1, p2);
    if (params.output) {
        params.output[idx] = {q.id, p1, p2};
    }
    if (params.threshold_reached_count && p2 != 0u) {
        atomicAdd(params.threshold_reached_count, 1u);
    }
}

extern "C" __global__ void __miss__fixed_radius_count_threshold() {}

extern "C" __global__ void __intersection__fixed_radius_count_threshold() {
    const uint32_t prim = optixGetPrimitiveIndex();
    const uint32_t qidx = optixGetPayload_0();
    const GpuPoint q = params.query_points[qidx];
    const GpuPoint t = params.search_points[prim];
    const float dx = t.x - q.x;
    const float dy = t.y - q.y;
    const float radius_sq = params.radius * params.radius;
    if ((dx * dx + dy * dy) > radius_sq) {
        return;
    }
    optixReportIntersection(params.radius, 0u);
}

extern "C" __global__ void __anyhit__fixed_radius_count_threshold() {
    uint32_t count = optixGetPayload_1() + 1u;
    optixSetPayload_1(count);
    if (params.threshold != 0u && count >= params.threshold) {
        optixSetPayload_2(1u);
        optixTerminateRay();
        return;
    }
    optixIgnoreIntersection();
}
)CUDA";

std::vector<HostPoint> make_fixture(uint32_t copies) {
    const HostPoint base[] = {
        {1, 0.00, 0.00},
        {2, 0.12, 0.04},
        {3, -0.10, 0.08},
        {4, 2.00, 2.00},
        {5, 2.14, 2.05},
        {6, 1.88, 1.94},
        {7, 4.50, 0.00},
        {8, -3.00, 2.50},
    };
    std::vector<HostPoint> points;
    points.reserve(static_cast<size_t>(copies) * 8u);
    for (uint32_t copy = 0; copy < copies; ++copy) {
        const uint32_t id_offset = 100u * copy;
        const double x_offset = 7.0 * static_cast<double>(copy);
        for (const HostPoint& point : base) {
            points.push_back({point.id + id_offset, point.x + x_offset, point.y});
        }
    }
    return points;
}

std::vector<GpuPoint> to_gpu_points(const std::vector<HostPoint>& points) {
    std::vector<GpuPoint> gpu;
    gpu.reserve(points.size());
    for (const HostPoint& point : points) {
        gpu.push_back({
            static_cast<float>(point.x),
            static_cast<float>(point.y),
            point.id,
            0u,
        });
    }
    return gpu;
}

std::string read_file(const std::filesystem::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        throw std::runtime_error("failed to read " + path.string());
    }
    std::ostringstream buffer;
    buffer << input.rdbuf();
    return buffer.str();
}

std::string compile_ptx(const std::string& source, int compute_major, int compute_minor) {
    namespace fs = std::filesystem;
    char dir_template[] = "/tmp/rtdl-route-d-XXXXXX";
    char* raw_dir = mkdtemp(dir_template);
    if (!raw_dir) {
        throw std::runtime_error("mkdtemp failed for Route D PTX compilation");
    }
    const fs::path temp_dir(raw_dir);
    struct Cleanup {
        fs::path path;
        ~Cleanup() {
            std::error_code ignored;
            fs::remove_all(path, ignored);
        }
    } cleanup{temp_dir};

    const fs::path source_path = temp_dir / "route_d_fixed_radius.cu";
    const fs::path ptx_path = temp_dir / "route_d_fixed_radius.ptx";
    const fs::path log_path = temp_dir / "nvcc.log";
    {
        std::ofstream output(source_path, std::ios::binary);
        if (!output) {
            throw std::runtime_error("failed to write " + source_path.string());
        }
        output << source;
    }

    const std::string arch = "--gpu-architecture=compute_" +
        std::to_string(compute_major) + std::to_string(compute_minor);
    std::ostringstream command;
    command
        << "/usr/local/cuda-12.8/bin/nvcc"
        << " -ptx -std=c++14"
        << " " << arch
        << " -I/root/vendor/optix-dev/include"
        << " -I/usr/local/cuda-12.8/include"
        << " " << source_path.string()
        << " -o " << ptx_path.string()
        << " > " << log_path.string()
        << " 2>&1";
    const int rc = std::system(command.str().c_str());
    if (rc != 0) {
        throw std::runtime_error("nvcc PTX compile failed:\n" + read_file(log_path));
    }
    return read_file(ptx_path);
}

struct OptixState {
    CUcontext cuda_context = nullptr;
    OptixDeviceContext optix_context = nullptr;
    int compute_major = 0;
    int compute_minor = 0;

    OptixState() {
        check_cuda(cuInit(0), "cuInit");
        CUdevice device = 0;
        check_cuda(cuDeviceGet(&device, 0), "cuDeviceGet");
        check_cuda(cuDeviceGetAttribute(&compute_major, CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MAJOR, device),
                   "cuDeviceGetAttribute major");
        check_cuda(cuDeviceGetAttribute(&compute_minor, CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MINOR, device),
                   "cuDeviceGetAttribute minor");
        check_cuda(cuDevicePrimaryCtxRetain(&cuda_context, device), "cuDevicePrimaryCtxRetain");
        check_cuda(cuCtxSetCurrent(cuda_context), "cuCtxSetCurrent");
        check_optix(optixInit(), "optixInit");
        OptixDeviceContextOptions options = {};
        check_optix(optixDeviceContextCreate(cuda_context, &options, &optix_context),
                    "optixDeviceContextCreate");
    }

    ~OptixState() {
        if (optix_context) {
            optixDeviceContextDestroy(optix_context);
        }
        if (cuda_context) {
            CUdevice device = 0;
            if (cuCtxGetDevice(&device) == CUDA_SUCCESS) {
                cuDevicePrimaryCtxRelease(device);
            }
        }
    }

    OptixState(const OptixState&) = delete;
    OptixState& operator=(const OptixState&) = delete;
};

struct Accel {
    CUdeviceptr output = 0;
    CUdeviceptr aabbs = 0;
    OptixTraversableHandle handle = 0;

    ~Accel() {
        if (output) {
            cuMemFree(output);
        }
        if (aabbs) {
            cuMemFree(aabbs);
        }
    }

    Accel(const Accel&) = delete;
    Accel& operator=(const Accel&) = delete;
    Accel() = default;

    Accel(Accel&& other) noexcept
        : output(other.output),
          aabbs(other.aabbs),
          handle(other.handle) {
        other.output = 0;
        other.aabbs = 0;
        other.handle = 0;
    }

    Accel& operator=(Accel&& other) noexcept {
        if (this != &other) {
            if (output) {
                cuMemFree(output);
            }
            if (aabbs) {
                cuMemFree(aabbs);
            }
            output = other.output;
            aabbs = other.aabbs;
            handle = other.handle;
            other.output = 0;
            other.aabbs = 0;
            other.handle = 0;
        }
        return *this;
    }
};

Accel build_accel(OptixDeviceContext ctx, const std::vector<GpuPoint>& points) {
    Accel accel;
    std::vector<OptixAabb> aabbs(points.size());
    const float aabb_radius = static_cast<float>(kRadius) + kRadiusPad;
    for (size_t i = 0; i < points.size(); ++i) {
        const GpuPoint& point = points[i];
        OptixAabb aabb = {};
        aabb.minX = point.x - aabb_radius;
        aabb.minY = point.y - aabb_radius;
        aabb.minZ = -aabb_radius;
        aabb.maxX = point.x + aabb_radius;
        aabb.maxY = point.y + aabb_radius;
        aabb.maxZ = aabb_radius;
        aabbs[i] = aabb;
    }

    const size_t aabb_bytes = sizeof(OptixAabb) * aabbs.size();
    check_cuda(cuMemAlloc(&accel.aabbs, aabb_bytes), "cuMemAlloc aabbs");
    check_cuda(cuMemcpyHtoD(accel.aabbs, aabbs.data(), aabb_bytes), "cuMemcpyHtoD aabbs");

    OptixBuildInput input = {};
    input.type = OPTIX_BUILD_INPUT_TYPE_CUSTOM_PRIMITIVES;
    input.customPrimitiveArray.aabbBuffers = &accel.aabbs;
    input.customPrimitiveArray.numPrimitives = static_cast<unsigned int>(aabbs.size());
    input.customPrimitiveArray.strideInBytes = sizeof(OptixAabb);
    uint32_t flags = OPTIX_GEOMETRY_FLAG_NONE;
    input.customPrimitiveArray.flags = &flags;
    input.customPrimitiveArray.numSbtRecords = 1;

    OptixAccelBuildOptions options = {};
    options.buildFlags = OPTIX_BUILD_FLAG_ALLOW_RANDOM_VERTEX_ACCESS;
    options.operation = OPTIX_BUILD_OPERATION_BUILD;

    OptixAccelBufferSizes sizes = {};
    check_optix(optixAccelComputeMemoryUsage(ctx, &options, &input, 1, &sizes),
                "optixAccelComputeMemoryUsage");
    DevPtr temp(sizes.tempSizeInBytes);
    check_cuda(cuMemAlloc(&accel.output, sizes.outputSizeInBytes), "cuMemAlloc accel output");
    check_optix(optixAccelBuild(ctx, 0, &options, &input, 1,
                                temp.ptr, sizes.tempSizeInBytes,
                                accel.output, sizes.outputSizeInBytes,
                                &accel.handle, nullptr, 0),
                "optixAccelBuild");
    check_cuda(cuStreamSynchronize(0), "cuStreamSynchronize accel");
    return accel;
}

struct Pipeline {
    OptixModule module = nullptr;
    OptixProgramGroup raygen = nullptr;
    OptixProgramGroup miss = nullptr;
    OptixProgramGroup hit = nullptr;
    OptixPipeline pipeline = nullptr;
    CUdeviceptr sbt_buffer = 0;
    OptixShaderBindingTable sbt = {};

    ~Pipeline() {
        if (pipeline) optixPipelineDestroy(pipeline);
        if (hit) optixProgramGroupDestroy(hit);
        if (miss) optixProgramGroupDestroy(miss);
        if (raygen) optixProgramGroupDestroy(raygen);
        if (module) optixModuleDestroy(module);
        if (sbt_buffer) cuMemFree(sbt_buffer);
    }

    Pipeline(const Pipeline&) = delete;
    Pipeline& operator=(const Pipeline&) = delete;
    Pipeline() = default;

    Pipeline(Pipeline&& other) noexcept
        : module(other.module),
          raygen(other.raygen),
          miss(other.miss),
          hit(other.hit),
          pipeline(other.pipeline),
          sbt_buffer(other.sbt_buffer),
          sbt(other.sbt) {
        other.module = nullptr;
        other.raygen = nullptr;
        other.miss = nullptr;
        other.hit = nullptr;
        other.pipeline = nullptr;
        other.sbt_buffer = 0;
        other.sbt = {};
    }

    Pipeline& operator=(Pipeline&& other) noexcept {
        if (this != &other) {
            if (pipeline) optixPipelineDestroy(pipeline);
            if (hit) optixProgramGroupDestroy(hit);
            if (miss) optixProgramGroupDestroy(miss);
            if (raygen) optixProgramGroupDestroy(raygen);
            if (module) optixModuleDestroy(module);
            if (sbt_buffer) cuMemFree(sbt_buffer);
            module = other.module;
            raygen = other.raygen;
            miss = other.miss;
            hit = other.hit;
            pipeline = other.pipeline;
            sbt_buffer = other.sbt_buffer;
            sbt = other.sbt;
            other.module = nullptr;
            other.raygen = nullptr;
            other.miss = nullptr;
            other.hit = nullptr;
            other.pipeline = nullptr;
            other.sbt_buffer = 0;
            other.sbt = {};
        }
        return *this;
    }
};

Pipeline build_pipeline(OptixDeviceContext ctx, const std::string& ptx) {
    Pipeline result;

    OptixModuleCompileOptions module_options = {};
    module_options.maxRegisterCount = OPTIX_COMPILE_DEFAULT_MAX_REGISTER_COUNT;
    module_options.optLevel = OPTIX_COMPILE_OPTIMIZATION_DEFAULT;
    module_options.debugLevel = OPTIX_COMPILE_DEBUG_LEVEL_NONE;

    OptixPipelineCompileOptions pipeline_options = {};
    pipeline_options.usesMotionBlur = 0;
    pipeline_options.traversableGraphFlags = OPTIX_TRAVERSABLE_GRAPH_FLAG_ALLOW_SINGLE_GAS;
    pipeline_options.numPayloadValues = 3;
    pipeline_options.numAttributeValues = 0;
    pipeline_options.exceptionFlags = OPTIX_EXCEPTION_FLAG_NONE;
    pipeline_options.pipelineLaunchParamsVariableName = "params";
    pipeline_options.usesPrimitiveTypeFlags = OPTIX_PRIMITIVE_TYPE_FLAGS_CUSTOM;

    char log[8192] = {};
    size_t log_size = sizeof(log);
    OptixResult module_result = optixModuleCreate(
        ctx,
        &module_options,
        &pipeline_options,
        ptx.c_str(),
        ptx.size(),
        log,
        &log_size,
        &result.module);
    if (module_result != OPTIX_SUCCESS) {
        std::ostringstream oss;
        oss << "optixModuleCreate failed: " << optixGetErrorString(module_result);
        if (log_size > 1 && log[0] != '\0') {
            oss << "\n" << log;
        }
        throw std::runtime_error(oss.str());
    }

    OptixProgramGroupOptions pg_options = {};
    OptixProgramGroupDesc raygen_desc = {};
    raygen_desc.kind = OPTIX_PROGRAM_GROUP_KIND_RAYGEN;
    raygen_desc.raygen.module = result.module;
    raygen_desc.raygen.entryFunctionName = "__raygen__fixed_radius_count_threshold";
    check_optix(optixProgramGroupCreate(ctx, &raygen_desc, 1, &pg_options, nullptr, nullptr, &result.raygen),
                "optixProgramGroupCreate raygen");

    OptixProgramGroupDesc miss_desc = {};
    miss_desc.kind = OPTIX_PROGRAM_GROUP_KIND_MISS;
    miss_desc.miss.module = result.module;
    miss_desc.miss.entryFunctionName = "__miss__fixed_radius_count_threshold";
    check_optix(optixProgramGroupCreate(ctx, &miss_desc, 1, &pg_options, nullptr, nullptr, &result.miss),
                "optixProgramGroupCreate miss");

    OptixProgramGroupDesc hit_desc = {};
    hit_desc.kind = OPTIX_PROGRAM_GROUP_KIND_HITGROUP;
    hit_desc.hitgroup.moduleIS = result.module;
    hit_desc.hitgroup.entryFunctionNameIS = "__intersection__fixed_radius_count_threshold";
    hit_desc.hitgroup.moduleAH = result.module;
    hit_desc.hitgroup.entryFunctionNameAH = "__anyhit__fixed_radius_count_threshold";
    check_optix(optixProgramGroupCreate(ctx, &hit_desc, 1, &pg_options, nullptr, nullptr, &result.hit),
                "optixProgramGroupCreate hit");

    OptixProgramGroup groups[3] = {result.raygen, result.miss, result.hit};
    OptixPipelineLinkOptions link_options = {};
    link_options.maxTraceDepth = 1;
    check_optix(optixPipelineCreate(ctx, &pipeline_options, &link_options, groups, 3,
                                    nullptr, nullptr, &result.pipeline),
                "optixPipelineCreate");

    OptixStackSizes stack_sizes = {};
    check_optix(optixUtilAccumulateStackSizes(result.raygen, &stack_sizes, result.pipeline),
                "optixUtilAccumulateStackSizes raygen");
    check_optix(optixUtilAccumulateStackSizes(result.miss, &stack_sizes, result.pipeline),
                "optixUtilAccumulateStackSizes miss");
    check_optix(optixUtilAccumulateStackSizes(result.hit, &stack_sizes, result.pipeline),
                "optixUtilAccumulateStackSizes hit");

    uint32_t direct_callable_stack_from_traversal = 0;
    uint32_t direct_callable_stack_from_state = 0;
    uint32_t continuation_stack = 0;
    check_optix(optixUtilComputeStackSizes(&stack_sizes, 1, 0, 0,
                                           &direct_callable_stack_from_traversal,
                                           &direct_callable_stack_from_state,
                                           &continuation_stack),
                "optixUtilComputeStackSizes");
    check_optix(optixPipelineSetStackSize(result.pipeline,
                                          direct_callable_stack_from_traversal,
                                          direct_callable_stack_from_state,
                                          continuation_stack,
                                          1),
                "optixPipelineSetStackSize");

    RaygenRecord raygen_record = {};
    MissRecord miss_record = {};
    HitRecord hit_record = {};
    check_optix(optixSbtRecordPackHeader(result.raygen, &raygen_record),
                "optixSbtRecordPackHeader raygen");
    check_optix(optixSbtRecordPackHeader(result.miss, &miss_record),
                "optixSbtRecordPackHeader miss");
    check_optix(optixSbtRecordPackHeader(result.hit, &hit_record),
                "optixSbtRecordPackHeader hit");

    const size_t sbt_bytes = sizeof(RaygenRecord) + sizeof(MissRecord) + sizeof(HitRecord);
    check_cuda(cuMemAlloc(&result.sbt_buffer, sbt_bytes), "cuMemAlloc sbt");
    CUdeviceptr cursor = result.sbt_buffer;
    check_cuda(cuMemcpyHtoD(cursor, &raygen_record, sizeof(RaygenRecord)), "cuMemcpyHtoD raygen record");
    cursor += sizeof(RaygenRecord);
    check_cuda(cuMemcpyHtoD(cursor, &miss_record, sizeof(MissRecord)), "cuMemcpyHtoD miss record");
    cursor += sizeof(MissRecord);
    check_cuda(cuMemcpyHtoD(cursor, &hit_record, sizeof(HitRecord)), "cuMemcpyHtoD hit record");

    result.sbt.raygenRecord = result.sbt_buffer;
    result.sbt.missRecordBase = result.sbt_buffer + sizeof(RaygenRecord);
    result.sbt.missRecordStrideInBytes = sizeof(MissRecord);
    result.sbt.missRecordCount = 1;
    result.sbt.hitgroupRecordBase = result.sbt_buffer + sizeof(RaygenRecord) + sizeof(MissRecord);
    result.sbt.hitgroupRecordStrideInBytes = sizeof(HitRecord);
    result.sbt.hitgroupRecordCount = 1;

    return result;
}

double now_s() {
    using Clock = std::chrono::steady_clock;
    static const auto start = Clock::now();
    return std::chrono::duration<double>(Clock::now() - start).count();
}

struct PreparedScene {
    std::vector<GpuPoint> points;
    DevPtr d_search;
    Accel accel;

    PreparedScene(OptixDeviceContext ctx, const std::vector<HostPoint>& host_points)
        : points(to_gpu_points(host_points)),
          d_search(sizeof(GpuPoint) * points.size()),
          accel() {
        upload(d_search.ptr, points.data(), points.size());
        accel = build_accel(ctx, points);
    }

    PreparedScene(const PreparedScene&) = delete;
    PreparedScene& operator=(const PreparedScene&) = delete;
};

struct Timing {
    std::vector<double> values;

    double median() const {
        std::vector<double> copy = values;
        std::sort(copy.begin(), copy.end());
        const size_t n = copy.size();
        if (n == 0) {
            return 0.0;
        }
        if (n % 2 == 1) {
            return copy[n / 2];
        }
        return 0.5 * (copy[n / 2 - 1] + copy[n / 2]);
    }

    double min() const {
        return *std::min_element(values.begin(), values.end());
    }

    double max() const {
        return *std::max_element(values.begin(), values.end());
    }
};

uint32_t run_scalar(const Pipeline& pipeline, const PreparedScene& scene) {
    DevPtr d_queries(sizeof(GpuPoint) * scene.points.size());
    upload(d_queries.ptr, scene.points.data(), scene.points.size());

    DevPtr d_threshold_count(sizeof(uint32_t));
    const uint32_t zero = 0;
    upload(d_threshold_count.ptr, &zero, 1);

    LaunchParams params = {};
    params.traversable = scene.accel.handle;
    params.query_points = reinterpret_cast<const GpuPoint*>(d_queries.ptr);
    params.search_points = reinterpret_cast<const GpuPoint*>(scene.d_search.ptr);
    params.output = nullptr;
    params.threshold_reached_count = reinterpret_cast<uint32_t*>(d_threshold_count.ptr);
    params.query_count = static_cast<uint32_t>(scene.points.size());
    params.threshold = kThreshold;
    params.radius = static_cast<float>(kRadius);
    params.trace_tmax = 2.0f * (static_cast<float>(kRadius) + kRadiusPad);

    DevPtr d_params(sizeof(LaunchParams));
    upload(d_params.ptr, &params, 1);

    check_optix(optixLaunch(pipeline.pipeline, 0,
                            d_params.ptr,
                            sizeof(LaunchParams),
                            &pipeline.sbt,
                            static_cast<unsigned int>(scene.points.size()), 1, 1),
                "optixLaunch scalar");
    check_cuda(cuStreamSynchronize(0), "cuStreamSynchronize scalar");

    uint32_t threshold_count = 0;
    download(&threshold_count, d_threshold_count.ptr, 1);
    return threshold_count;
}

std::vector<CountRecord> run_rows(const Pipeline& pipeline, const PreparedScene& scene) {
    DevPtr d_queries(sizeof(GpuPoint) * scene.points.size());
    upload(d_queries.ptr, scene.points.data(), scene.points.size());

    DevPtr d_output(sizeof(CountRecord) * scene.points.size());

    LaunchParams params = {};
    params.traversable = scene.accel.handle;
    params.query_points = reinterpret_cast<const GpuPoint*>(d_queries.ptr);
    params.search_points = reinterpret_cast<const GpuPoint*>(scene.d_search.ptr);
    params.output = reinterpret_cast<CountRecord*>(d_output.ptr);
    params.threshold_reached_count = nullptr;
    params.query_count = static_cast<uint32_t>(scene.points.size());
    params.threshold = kThreshold;
    params.radius = static_cast<float>(kRadius);
    params.trace_tmax = 2.0f * (static_cast<float>(kRadius) + kRadiusPad);

    DevPtr d_params(sizeof(LaunchParams));
    upload(d_params.ptr, &params, 1);

    check_optix(optixLaunch(pipeline.pipeline, 0,
                            d_params.ptr,
                            sizeof(LaunchParams),
                            &pipeline.sbt,
                            static_cast<unsigned int>(scene.points.size()), 1, 1),
                "optixLaunch rows");
    check_cuda(cuStreamSynchronize(0), "cuStreamSynchronize rows");

    std::vector<CountRecord> rows(scene.points.size());
    download(rows.data(), d_output.ptr, rows.size());
    return rows;
}

Timing measure_scalar(const Pipeline& pipeline, const PreparedScene& scene, int repeat, int warmup) {
    for (int i = 0; i < warmup; ++i) {
        (void)run_scalar(pipeline, scene);
    }
    Timing timing;
    for (int i = 0; i < repeat; ++i) {
        const double start = now_s();
        (void)run_scalar(pipeline, scene);
        timing.values.push_back(now_s() - start);
    }
    return timing;
}

Timing measure_rows(const Pipeline& pipeline, const PreparedScene& scene, int repeat, int warmup) {
    for (int i = 0; i < warmup; ++i) {
        (void)run_rows(pipeline, scene);
    }
    Timing timing;
    for (int i = 0; i < repeat; ++i) {
        const double start = now_s();
        (void)run_rows(pipeline, scene);
        timing.values.push_back(now_s() - start);
    }
    return timing;
}

struct Correctness {
    uint32_t scalar_threshold_count = 0;
    uint32_t rows_threshold_count = 0;
    uint32_t rows_outlier_count = 0;
    bool scalar_passed = false;
    bool rows_passed = false;
    bool all_passed = false;
};

Correctness validate_correctness(const Pipeline& pipeline, const PreparedScene& scene, uint32_t copies) {
    Correctness correctness;
    correctness.scalar_threshold_count = run_scalar(pipeline, scene);
    const std::vector<CountRecord> rows = run_rows(pipeline, scene);
    for (const CountRecord& row : rows) {
        if (row.threshold_reached != 0u) {
            correctness.rows_threshold_count += 1u;
        } else {
            correctness.rows_outlier_count += 1u;
        }
    }
    const uint32_t expected_threshold = 6u * copies;
    const uint32_t expected_outliers = 2u * copies;
    correctness.scalar_passed = correctness.scalar_threshold_count == expected_threshold;
    correctness.rows_passed =
        correctness.rows_threshold_count == expected_threshold &&
        correctness.rows_outlier_count == expected_outliers;
    correctness.all_passed = correctness.scalar_passed && correctness.rows_passed;
    return correctness;
}

std::string json_array(const std::vector<double>& values) {
    std::ostringstream oss;
    oss << "[";
    for (size_t i = 0; i < values.size(); ++i) {
        if (i != 0) {
            oss << ", ";
        }
        oss << std::setprecision(10) << values[i];
    }
    oss << "]";
    return oss.str();
}

void print_timing_json(const char* name, const Timing& timing, int indent) {
    const std::string spaces(static_cast<size_t>(indent), ' ');
    std::cout << spaces << "\"" << name << "\": {\n";
    std::cout << spaces << "  \"timings_s\": " << json_array(timing.values) << ",\n";
    std::cout << spaces << "  \"median_s\": " << std::setprecision(10) << timing.median() << ",\n";
    std::cout << spaces << "  \"min_s\": " << std::setprecision(10) << timing.min() << ",\n";
    std::cout << spaces << "  \"max_s\": " << std::setprecision(10) << timing.max() << "\n";
    std::cout << spaces << "}";
}

struct Args {
    uint32_t copies = 8192;
    int repeat = 7;
    int warmup = 1;
};

Args parse_args(int argc, char** argv) {
    Args args;
    for (int i = 1; i < argc; ++i) {
        const std::string item = argv[i];
        if (item == "--copies" && i + 1 < argc) {
            args.copies = static_cast<uint32_t>(std::stoul(argv[++i]));
        } else if (item == "--repeat" && i + 1 < argc) {
            args.repeat = std::stoi(argv[++i]);
        } else if (item == "--warmup" && i + 1 < argc) {
            args.warmup = std::stoi(argv[++i]);
        } else if (item == "--help") {
            std::cout << "usage: route_d_fixed_radius_count_threshold_optix --copies N --repeat N --warmup N\n";
            std::exit(0);
        } else {
            throw std::runtime_error("unknown or incomplete argument: " + item);
        }
    }
    if (args.copies < 1) {
        throw std::runtime_error("--copies must be positive");
    }
    if (args.repeat < 1) {
        throw std::runtime_error("--repeat must be positive");
    }
    if (args.warmup < 0) {
        throw std::runtime_error("--warmup must be non-negative");
    }
    return args;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const Args args = parse_args(argc, argv);

        OptixState state;
        const double pipeline_start = now_s();
        const std::string ptx = compile_ptx(kKernelSource, state.compute_major, state.compute_minor);
        Pipeline pipeline = build_pipeline(state.optix_context, ptx);
        const double pipeline_s = now_s() - pipeline_start;

        const std::vector<HostPoint> host_points = make_fixture(args.copies);
        const double prepare_start = now_s();
        PreparedScene scene(state.optix_context, host_points);
        const double prepare_s = now_s() - prepare_start;

        const Correctness correctness = validate_correctness(pipeline, scene, args.copies);
        if (!correctness.all_passed) {
            std::cerr << "Route D correctness failed\n";
            return 2;
        }

        const Timing scalar = measure_scalar(pipeline, scene, args.repeat, args.warmup);
        const Timing rows = measure_rows(pipeline, scene, args.repeat, args.warmup);

        std::cout << "{\n";
        std::cout << "  \"route\": \"route_d_independent_handwritten_optix_fixed_radius_count_threshold_2d\",\n";
        std::cout << "  \"independence_contract\": {\n";
        std::cout << "    \"imports_product_runtime\": false,\n";
        std::cout << "    \"links_product_runtime_library\": false,\n";
        std::cout << "    \"calls_product_runtime_symbols\": false,\n";
        std::cout << "    \"uses_product_python_app_route\": false,\n";
        std::cout << "    \"standalone_cuda_driver_optix\": true\n";
        std::cout << "  },\n";
        std::cout << "  \"copies\": " << args.copies << ",\n";
        std::cout << "  \"point_count\": " << host_points.size() << ",\n";
        std::cout << "  \"radius\": " << kRadius << ",\n";
        std::cout << "  \"threshold\": " << kThreshold << ",\n";
        std::cout << "  \"repeat\": " << args.repeat << ",\n";
        std::cout << "  \"warmup\": " << args.warmup << ",\n";
        std::cout << "  \"timing_boundary\": \"prepared hot path; fixture/pipeline/GAS excluded; host query upload, launch, sync, result download included\",\n";
        std::cout << "  \"pipeline_build_s\": " << std::setprecision(10) << pipeline_s << ",\n";
        std::cout << "  \"prepare_scene_s\": " << std::setprecision(10) << prepare_s << ",\n";
        std::cout << "  \"correctness\": {\n";
        std::cout << "    \"correctness_passed\": " << (correctness.all_passed ? "true" : "false") << ",\n";
        std::cout << "    \"expected_threshold_reached_count\": " << (6u * args.copies) << ",\n";
        std::cout << "    \"expected_outlier_count\": " << (2u * args.copies) << ",\n";
        std::cout << "    \"scalar_threshold_reached_count\": " << correctness.scalar_threshold_count << ",\n";
        std::cout << "    \"rows_threshold_reached_count\": " << correctness.rows_threshold_count << ",\n";
        std::cout << "    \"rows_outlier_count\": " << correctness.rows_outlier_count << "\n";
        std::cout << "  },\n";
        std::cout << "  \"routes\": {\n";
        print_timing_json("route_d_scalar_threshold_count", scalar, 4);
        std::cout << ",\n";
        print_timing_json("route_d_count_rows", rows, 4);
        std::cout << "\n";
        std::cout << "  }\n";
        std::cout << "}\n";
        return 0;
    } catch (const std::exception& ex) {
        std::cerr << "Route D error: " << ex.what() << "\n";
        return 1;
    }
}

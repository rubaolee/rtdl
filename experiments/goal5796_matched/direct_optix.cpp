#include <optix.h>
#include <optix_function_table_definition.h>
#include <optix_stack_size.h>
#include <optix_stubs.h>

#include <cuda.h>
#include <nvrtc.h>
#include <vector_types.h>

#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <memory>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#define CU_CHECK(call) do { \
    CUresult result_ = (call); \
    if (result_ != CUDA_SUCCESS) { \
        const char* text_ = nullptr; cuGetErrorString(result_, &text_); \
        throw std::runtime_error(std::string("CUDA: ") + (text_ ? text_ : "unknown")); \
    } \
} while (0)

#define OPTIX_CHECK(call) do { \
    OptixResult result_ = (call); \
    if (result_ != OPTIX_SUCCESS) \
        throw std::runtime_error(std::string("OptiX: ") + optixGetErrorString(result_)); \
} while (0)

#define NVRTC_CHECK(call) do { \
    nvrtcResult result_ = (call); \
    if (result_ != NVRTC_SUCCESS) \
        throw std::runtime_error(std::string("NVRTC: ") + nvrtcGetErrorString(result_)); \
} while (0)

static OptixResult optix_module_create_compat(
        OptixDeviceContext context,
        const OptixModuleCompileOptions* module_options,
        const OptixPipelineCompileOptions* pipeline_options,
        const char* ptx,
        std::size_t ptx_size,
        char* log,
        std::size_t* log_size,
        OptixModule* module) {
#if OPTIX_VERSION >= 70700
    return optixModuleCreate(
        context, module_options, pipeline_options, ptx, ptx_size,
        log, log_size, module);
#else
    return optixModuleCreateFromPTX(
        context, module_options, pipeline_options, ptx, ptx_size,
        log, log_size, module);
#endif
}

static OptixResult optix_accumulate_stack_sizes_compat(
        OptixProgramGroup group,
        OptixStackSizes* sizes,
        OptixPipeline pipeline) {
#if OPTIX_VERSION >= 70700
    return optixUtilAccumulateStackSizes(group, sizes, pipeline);
#else
    (void)pipeline;
    return optixUtilAccumulateStackSizes(group, sizes);
#endif
}

struct Box {
    float lower_x, lower_y, lower_z;
    float upper_x, upper_y, upper_z;
    std::uint32_t item_id;
};

struct RelationRow { std::uint32_t source_id, item_id; };

struct Ray {
    float origin_x, origin_y, origin_z;
    float direction_x, direction_y, direction_z;
};

struct Params {
    OptixTraversableHandle traversable;
    const Box* boxes;
    const Box* queries;
    RelationRow* rows;
    std::uint32_t* row_count;
    std::uint32_t* overflow;
    std::uint32_t box_count;
    std::uint32_t query_count;
    std::uint32_t raw_row_capacity;
    std::uint32_t reverse_orientation;
    float minimum_overlap;
    float tmin;
    float tmax;
    std::uint32_t reserved0;
    const Ray* rays;
    const std::uint64_t* weights;
    std::uint64_t* per_ray;
    std::uint64_t* weighted_sum;
    std::uint32_t* status;
};

static_assert(sizeof(Box) == 28, "Box ABI drift");
static_assert(sizeof(RelationRow) == 8, "row ABI drift");
static_assert(sizeof(Ray) == 24, "ray ABI drift");
static_assert(sizeof(Params) == 120, "params ABI drift");

struct DeviceBuffer {
    CUdeviceptr ptr = 0;
    std::size_t bytes = 0;
    DeviceBuffer() = default;
    explicit DeviceBuffer(std::size_t count) : bytes(count) {
        if (bytes) CU_CHECK(cuMemAlloc(&ptr, bytes));
    }
    ~DeviceBuffer() { if (ptr) cuMemFree(ptr); }
    DeviceBuffer(const DeviceBuffer&) = delete;
    DeviceBuffer& operator=(const DeviceBuffer&) = delete;
    DeviceBuffer(DeviceBuffer&& other) noexcept : ptr(other.ptr), bytes(other.bytes) {
        other.ptr = 0; other.bytes = 0;
    }
    DeviceBuffer& operator=(DeviceBuffer&& other) noexcept {
        if (this != &other) {
            if (ptr) cuMemFree(ptr);
            ptr = other.ptr; bytes = other.bytes; other.ptr = 0; other.bytes = 0;
        }
        return *this;
    }
};

template <typename T>
DeviceBuffer upload_vector(const std::vector<T>& values) {
    DeviceBuffer result(sizeof(T) * values.size());
    if (!values.empty()) CU_CHECK(cuMemcpyHtoD(result.ptr, values.data(), result.bytes));
    return result;
}

template <typename T>
std::vector<T> download_vector(CUdeviceptr source, std::size_t count) {
    std::vector<T> result(count);
    if (count) CU_CHECK(cuMemcpyDtoH(result.data(), source, sizeof(T) * count));
    return result;
}

static std::string read_file(const std::string& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) throw std::runtime_error("cannot read device source: " + path);
    return std::string(std::istreambuf_iterator<char>(input), std::istreambuf_iterator<char>());
}

static std::string compile_ptx(
        const std::string& source, const std::string& source_name,
        const std::string& optix_include, const std::string& cuda_include) {
    nvrtcProgram program = nullptr;
    NVRTC_CHECK(nvrtcCreateProgram(
        &program, source.c_str(), source_name.c_str(), 0, nullptr, nullptr));
    std::vector<std::string> option_storage = {
        "--std=c++17", "--device-as-default-execution-space",
        "--relocatable-device-code=true", "-I" + optix_include,
        "-I" + cuda_include,
    };
    std::vector<const char*> options;
    for (const auto& option : option_storage) options.push_back(option.c_str());
    nvrtcResult compile_result = nvrtcCompileProgram(
        program, static_cast<int>(options.size()), options.data());
    if (compile_result != NVRTC_SUCCESS) {
        std::size_t size = 0; nvrtcGetProgramLogSize(program, &size);
        std::string log(size, '\0'); if (size) nvrtcGetProgramLog(program, log.data());
        nvrtcDestroyProgram(&program);
        throw std::runtime_error("NVRTC compile failed:\n" + log);
    }
    std::size_t size = 0;
    NVRTC_CHECK(nvrtcGetPTXSize(program, &size));
    std::string ptx(size, '\0');
    NVRTC_CHECK(nvrtcGetPTX(program, ptx.data()));
    NVRTC_CHECK(nvrtcDestroyProgram(&program));
    return ptx;
}

static void optix_log(unsigned int level, const char* tag, const char* message, void*) {
    if (level <= 2) std::cerr << "[optix][" << level << "][" << (tag ? tag : "")
                              << "] " << (message ? message : "") << "\n";
}

struct Context {
    CUdevice device = 0;
    CUcontext cuda = nullptr;
    OptixDeviceContext optix = nullptr;
    Context() {
        CU_CHECK(cuInit(0));
        CU_CHECK(cuDeviceGet(&device, 0));
        CU_CHECK(cuDevicePrimaryCtxRetain(&cuda, device));
        CU_CHECK(cuCtxSetCurrent(cuda));
        OPTIX_CHECK(optixInit());
        OptixDeviceContextOptions options = {};
        options.logCallbackFunction = optix_log;
        options.logCallbackLevel = 2;
        options.validationMode = OPTIX_DEVICE_CONTEXT_VALIDATION_MODE_ALL;
        OPTIX_CHECK(optixDeviceContextCreate(cuda, &options, &optix));
    }
    ~Context() {
        if (optix) optixDeviceContextDestroy(optix);
        if (cuda) cuDevicePrimaryCtxRelease(device);
    }
};

struct Accel {
    DeviceBuffer geometry;
    DeviceBuffer output;
    OptixTraversableHandle handle = 0;
};

static Accel custom_accel(OptixDeviceContext context, const std::vector<Box>& boxes) {
    std::vector<OptixAabb> aabbs;
    for (const auto& box : boxes) {
        OptixAabb row = {};
        row.minX = box.lower_x; row.minY = box.lower_y; row.minZ = -0.001f;
        row.maxX = box.upper_x; row.maxY = box.upper_y; row.maxZ = 0.001f;
        aabbs.push_back(row);
    }
    Accel result;
    result.geometry = upload_vector(aabbs);
    OptixBuildInput input = {};
    input.type = OPTIX_BUILD_INPUT_TYPE_CUSTOM_PRIMITIVES;
    input.customPrimitiveArray.aabbBuffers = &result.geometry.ptr;
    input.customPrimitiveArray.numPrimitives = static_cast<unsigned int>(aabbs.size());
    input.customPrimitiveArray.strideInBytes = sizeof(OptixAabb);
    std::uint32_t flags = OPTIX_GEOMETRY_FLAG_NONE;
    input.customPrimitiveArray.flags = &flags;
    input.customPrimitiveArray.numSbtRecords = 1;
    OptixAccelBuildOptions options = {};
    options.buildFlags = OPTIX_BUILD_FLAG_PREFER_FAST_TRACE;
    options.operation = OPTIX_BUILD_OPERATION_BUILD;
    OptixAccelBufferSizes sizes = {};
    OPTIX_CHECK(optixAccelComputeMemoryUsage(context, &options, &input, 1, &sizes));
    DeviceBuffer temporary(sizes.tempSizeInBytes);
    result.output = DeviceBuffer(sizes.outputSizeInBytes);
    OPTIX_CHECK(optixAccelBuild(
        context, 0, &options, &input, 1,
        temporary.ptr, temporary.bytes, result.output.ptr, result.output.bytes,
        &result.handle, nullptr, 0));
    CU_CHECK(cuStreamSynchronize(0));
    return result;
}

static Accel triangle_accel(OptixDeviceContext context, const std::vector<float3>& vertices) {
    Accel result;
    result.geometry = upload_vector(vertices);
    OptixBuildInput input = {};
    input.type = OPTIX_BUILD_INPUT_TYPE_TRIANGLES;
    input.triangleArray.vertexBuffers = &result.geometry.ptr;
    input.triangleArray.numVertices = static_cast<unsigned int>(vertices.size());
    input.triangleArray.vertexFormat = OPTIX_VERTEX_FORMAT_FLOAT3;
    input.triangleArray.vertexStrideInBytes = sizeof(float3);
    input.triangleArray.indexFormat = OPTIX_INDICES_FORMAT_NONE;
    std::uint32_t flags = OPTIX_GEOMETRY_FLAG_NONE;
    input.triangleArray.flags = &flags;
    input.triangleArray.numSbtRecords = 1;
    OptixAccelBuildOptions options = {};
    options.buildFlags = OPTIX_BUILD_FLAG_PREFER_FAST_TRACE;
    options.operation = OPTIX_BUILD_OPERATION_BUILD;
    OptixAccelBufferSizes sizes = {};
    OPTIX_CHECK(optixAccelComputeMemoryUsage(context, &options, &input, 1, &sizes));
    DeviceBuffer temporary(sizes.tempSizeInBytes);
    result.output = DeviceBuffer(sizes.outputSizeInBytes);
    OPTIX_CHECK(optixAccelBuild(
        context, 0, &options, &input, 1,
        temporary.ptr, temporary.bytes, result.output.ptr, result.output.bytes,
        &result.handle, nullptr, 0));
    CU_CHECK(cuStreamSynchronize(0));
    return result;
}

template <typename T>
struct alignas(OPTIX_SBT_RECORD_ALIGNMENT) SbtRecord {
    char header[OPTIX_SBT_RECORD_HEADER_SIZE];
    T data;
};
struct Empty {};
using Record = SbtRecord<Empty>;

struct Pipeline {
    OptixModule module = nullptr;
    OptixProgramGroup raygen = nullptr, miss = nullptr, hit = nullptr;
    OptixPipeline pipeline = nullptr;
    DeviceBuffer records;
    OptixShaderBindingTable sbt = {};
    ~Pipeline() {
        if (pipeline) optixPipelineDestroy(pipeline);
        if (hit) optixProgramGroupDestroy(hit);
        if (miss) optixProgramGroupDestroy(miss);
        if (raygen) optixProgramGroupDestroy(raygen);
        if (module) optixModuleDestroy(module);
    }
};

static std::unique_ptr<Pipeline> build_pipeline(
        OptixDeviceContext context, const std::string& ptx, bool relation) {
    auto result = std::make_unique<Pipeline>();
    OptixModuleCompileOptions module_options = {};
    module_options.maxRegisterCount = OPTIX_COMPILE_DEFAULT_MAX_REGISTER_COUNT;
    module_options.optLevel = OPTIX_COMPILE_OPTIMIZATION_DEFAULT;
    module_options.debugLevel = OPTIX_COMPILE_DEBUG_LEVEL_NONE;
    OptixPipelineCompileOptions pipeline_options = {};
    pipeline_options.traversableGraphFlags = OPTIX_TRAVERSABLE_GRAPH_FLAG_ALLOW_SINGLE_GAS;
    pipeline_options.numPayloadValues = 2;
    pipeline_options.numAttributeValues = relation ? 1 : 2;
    pipeline_options.exceptionFlags = OPTIX_EXCEPTION_FLAG_NONE;
    pipeline_options.pipelineLaunchParamsVariableName = "params";
    pipeline_options.usesPrimitiveTypeFlags = relation
        ? OPTIX_PRIMITIVE_TYPE_FLAGS_CUSTOM : OPTIX_PRIMITIVE_TYPE_FLAGS_TRIANGLE;
    char log[8192] = {};
    std::size_t log_size = sizeof(log);
    OptixResult module_result = optix_module_create_compat(
        context, &module_options, &pipeline_options, ptx.data(), ptx.size(),
        log, &log_size, &result->module);
    if (module_result != OPTIX_SUCCESS)
        throw std::runtime_error(std::string("module: ") + optixGetErrorString(module_result) + "\n" + log);
    auto make_group = [&](OptixProgramGroupDesc& desc, OptixProgramGroup* output) {
        OptixProgramGroupOptions options = {};
        char group_log[4096] = {}; std::size_t group_log_size = sizeof(group_log);
        OptixResult code = optixProgramGroupCreate(
            context, &desc, 1, &options, group_log, &group_log_size, output);
        if (code != OPTIX_SUCCESS)
            throw std::runtime_error(std::string("program group: ") + optixGetErrorString(code) + "\n" + group_log);
    };
    OptixProgramGroupDesc raygen_desc = {};
    raygen_desc.kind = OPTIX_PROGRAM_GROUP_KIND_RAYGEN;
    raygen_desc.raygen.module = result->module;
    raygen_desc.raygen.entryFunctionName = relation
        ? "__raygen__goal5796_relation" : "__raygen__goal5796_triangle";
    make_group(raygen_desc, &result->raygen);
    OptixProgramGroupDesc miss_desc = {};
    miss_desc.kind = OPTIX_PROGRAM_GROUP_KIND_MISS;
    miss_desc.miss.module = result->module;
    miss_desc.miss.entryFunctionName = relation
        ? "__miss__goal5796_relation" : "__miss__goal5796_triangle";
    make_group(miss_desc, &result->miss);
    OptixProgramGroupDesc hit_desc = {};
    hit_desc.kind = OPTIX_PROGRAM_GROUP_KIND_HITGROUP;
    hit_desc.hitgroup.moduleAH = result->module;
    hit_desc.hitgroup.entryFunctionNameAH = relation
        ? "__anyhit__goal5796_relation" : "__anyhit__goal5796_triangle";
    if (relation) {
        hit_desc.hitgroup.moduleIS = result->module;
        hit_desc.hitgroup.entryFunctionNameIS = "__intersection__goal5796_relation";
    }
    make_group(hit_desc, &result->hit);
    OptixProgramGroup groups[] = {result->raygen, result->miss, result->hit};
    OptixPipelineLinkOptions link = {}; link.maxTraceDepth = 1;
    OPTIX_CHECK(optixPipelineCreate(
        context, &pipeline_options, &link, groups, 3,
        nullptr, nullptr, &result->pipeline));
    OptixStackSizes stack = {};
    for (auto group : groups)
        OPTIX_CHECK(optix_accumulate_stack_sizes_compat(group, &stack, result->pipeline));
    std::uint32_t dc_trav = 0, dc_state = 0, continuation = 0;
    OPTIX_CHECK(optixUtilComputeStackSizes(
        &stack, 1, 0, 0, &dc_trav, &dc_state, &continuation));
    OPTIX_CHECK(optixPipelineSetStackSize(
        result->pipeline, dc_trav, dc_state, continuation, 1));
    Record host_records[3] = {};
    OPTIX_CHECK(optixSbtRecordPackHeader(result->raygen, &host_records[0]));
    OPTIX_CHECK(optixSbtRecordPackHeader(result->miss, &host_records[1]));
    OPTIX_CHECK(optixSbtRecordPackHeader(result->hit, &host_records[2]));
    result->records = DeviceBuffer(sizeof(host_records));
    CU_CHECK(cuMemcpyHtoD(result->records.ptr, host_records, sizeof(host_records)));
    result->sbt.raygenRecord = result->records.ptr;
    result->sbt.missRecordBase = result->records.ptr + sizeof(Record);
    result->sbt.missRecordStrideInBytes = sizeof(Record);
    result->sbt.missRecordCount = 1;
    result->sbt.hitgroupRecordBase = result->records.ptr + 2 * sizeof(Record);
    result->sbt.hitgroupRecordStrideInBytes = sizeof(Record);
    result->sbt.hitgroupRecordCount = 1;
    return result;
}

static void launch(const Pipeline& pipeline, const Params& params, unsigned width) {
    DeviceBuffer device_params(sizeof(Params));
    CU_CHECK(cuMemcpyHtoD(device_params.ptr, &params, sizeof(params)));
    OPTIX_CHECK(optixLaunch(
        pipeline.pipeline, 0, device_params.ptr, sizeof(params),
        &pipeline.sbt, width, 1, 1));
    CU_CHECK(cuStreamSynchronize(0));
}

struct RelationResult {
    std::vector<std::pair<std::uint32_t, std::uint32_t>> rows;
    std::uint32_t raw_count = 0;
};

static RelationResult run_relation(
        OptixDeviceContext context, const Pipeline& pipeline,
        const std::vector<Box>& indexed, const std::vector<Box>& sources,
        float threshold, std::uint32_t semantic_capacity) {
    const std::uint32_t raw_capacity = static_cast<std::uint32_t>(
        std::max<std::size_t>(1, 2 * indexed.size() * sources.size()));
    DeviceBuffer d_indexed = upload_vector(indexed);
    DeviceBuffer d_sources = upload_vector(sources);
    DeviceBuffer d_rows(sizeof(RelationRow) * raw_capacity);
    DeviceBuffer d_count(sizeof(std::uint32_t));
    DeviceBuffer d_overflow(sizeof(std::uint32_t));
    DeviceBuffer d_status(sizeof(std::uint32_t));
    CU_CHECK(cuMemsetD8(d_rows.ptr, 0, d_rows.bytes));
    CU_CHECK(cuMemsetD8(d_count.ptr, 0, d_count.bytes));
    CU_CHECK(cuMemsetD8(d_overflow.ptr, 0, d_overflow.bytes));
    CU_CHECK(cuMemsetD8(d_status.ptr, 0, d_status.bytes));
    Accel indexed_accel = custom_accel(context, indexed);
    Accel source_accel = custom_accel(context, sources);
    for (unsigned reverse = 0; reverse < 2; ++reverse) {
        Params params = {};
        params.traversable = reverse ? source_accel.handle : indexed_accel.handle;
        params.boxes = reinterpret_cast<const Box*>(reverse ? d_sources.ptr : d_indexed.ptr);
        params.queries = reinterpret_cast<const Box*>(reverse ? d_indexed.ptr : d_sources.ptr);
        params.rows = reinterpret_cast<RelationRow*>(d_rows.ptr);
        params.row_count = reinterpret_cast<std::uint32_t*>(d_count.ptr);
        params.overflow = reinterpret_cast<std::uint32_t*>(d_overflow.ptr);
        params.box_count = static_cast<std::uint32_t>(reverse ? sources.size() : indexed.size());
        params.query_count = static_cast<std::uint32_t>(reverse ? indexed.size() : sources.size());
        params.raw_row_capacity = raw_capacity;
        params.reverse_orientation = reverse;
        params.minimum_overlap = threshold;
        params.status = reinterpret_cast<std::uint32_t*>(d_status.ptr);
        launch(pipeline, params, params.query_count);
    }
    const auto count = download_vector<std::uint32_t>(d_count.ptr, 1)[0];
    const auto overflow = download_vector<std::uint32_t>(d_overflow.ptr, 1)[0];
    const auto status = download_vector<std::uint32_t>(d_status.ptr, 1)[0];
    if (overflow || status || count > raw_capacity)
        throw std::runtime_error("direct relation device status failure");
    auto raw = download_vector<RelationRow>(d_rows.ptr, count);
    std::set<std::pair<std::uint32_t, std::uint32_t>> canonical;
    for (const auto& row : raw) canonical.emplace(row.source_id, row.item_id);
    if (canonical.size() > semantic_capacity)
        throw std::runtime_error("direct relation capacity exceeded; partial result withheld");
    return {std::vector<std::pair<std::uint32_t, std::uint32_t>>(
        canonical.begin(), canonical.end()), count};
}

static std::pair<std::vector<std::uint64_t>, std::uint64_t> run_triangle(
        OptixDeviceContext context, const Pipeline& pipeline) {
    std::vector<float3> vertices = {
        {-1,-1,1},{1,-1,1},{0,1,1}, {-1,-1,2},{1,-1,2},{0,1,2},
        {-1,-1,3},{1,-1,3},{0,1,3}, {2,-1,1},{4,-1,1},{3,1,1},
        {2,-1,1},{4,-1,1},{3,1,1},
    };
    std::vector<Ray> rays = {
        {0,0,0,0,0,1}, {3,0,0,0,0,1}, {6,0,0,0,0,1}, {0,0,2.5f,0,0,1},
    };
    std::vector<std::uint64_t> weights = {1,3,5,7};
    Accel accel = triangle_accel(context, vertices);
    DeviceBuffer d_rays = upload_vector(rays);
    DeviceBuffer d_weights = upload_vector(weights);
    DeviceBuffer d_counts(sizeof(std::uint64_t) * rays.size());
    DeviceBuffer d_weighted(sizeof(std::uint64_t));
    DeviceBuffer d_status(sizeof(std::uint32_t));
    CU_CHECK(cuMemsetD8(d_counts.ptr, 0, d_counts.bytes));
    CU_CHECK(cuMemsetD8(d_weighted.ptr, 0, d_weighted.bytes));
    CU_CHECK(cuMemsetD8(d_status.ptr, 0, d_status.bytes));
    Params params = {};
    params.traversable = accel.handle;
    params.query_count = static_cast<std::uint32_t>(rays.size());
    params.tmin = 0.0f; params.tmax = 10.0f;
    params.rays = reinterpret_cast<const Ray*>(d_rays.ptr);
    params.weights = reinterpret_cast<const std::uint64_t*>(d_weights.ptr);
    params.per_ray = reinterpret_cast<std::uint64_t*>(d_counts.ptr);
    params.weighted_sum = reinterpret_cast<std::uint64_t*>(d_weighted.ptr);
    params.status = reinterpret_cast<std::uint32_t*>(d_status.ptr);
    launch(pipeline, params, params.query_count);
    const auto status = download_vector<std::uint32_t>(d_status.ptr, 1)[0];
    if (status) throw std::runtime_error("direct triangle device status failure");
    return {download_vector<std::uint64_t>(d_counts.ptr, rays.size()),
            download_vector<std::uint64_t>(d_weighted.ptr, 1)[0]};
}

static Box box(float x0, float y0, float x1, float y1, std::uint32_t id) {
    return {x0, y0, 0.0f, x1, y1, 0.0f, id};
}

static void json_rows(std::ostream& out, const RelationResult& result) {
    out << '[';
    for (std::size_t i = 0; i < result.rows.size(); ++i) {
        if (i) out << ',';
        out << '[' << result.rows[i].first << ',' << result.rows[i].second << ']';
    }
    out << ']';
}

int main(int argc, char** argv) {
    try {
        if (argc != 5) {
            std::cerr << "usage: direct_optix DEVICE_CU OPTIX_INCLUDE CUDA_INCLUDE SPEC_SHA256\n";
            return 2;
        }
        Context context;
        const std::string source = read_file(argv[1]);
        const std::string ptx = compile_ptx(source, argv[1], argv[2], argv[3]);
        auto relation_pipeline = build_pipeline(context.optix, ptx, true);
        auto triangle_pipeline = build_pipeline(context.optix, ptx, false);

        RelationResult diagnostic = run_relation(
            context.optix, *relation_pipeline,
            {box(0,0,4,1,10), box(0,0,1,4,20)},
            {box(2,.25f,3,.75f,100), box(.25f,2,.75f,3,101)}, 0.0f, 2);
        const std::vector<Box> librts_indexed = {
            box(0,0,2,2,0), box(1,1,3,3,1), box(-2,-2,-1,-1,2), box(10,10,11,11,3)};
        const std::vector<Box> librts_sources = {
            box(1.25f,1.25f,1.75f,1.75f,0), box(0,0,2,2,1),
            box(.5f,.5f,2.5f,2.5f,2), box(-1.75f,-1.75f,-1.25f,-1.25f,3),
            box(10,10,11,11,4)};
        RelationResult broad = run_relation(
            context.optix, *relation_pipeline, librts_indexed, librts_sources, 0.0f, 8);
        RelationResult filtered = run_relation(
            context.optix, *relation_pipeline, librts_indexed, librts_sources, .75f, 5);
        bool overflow_witness_rejected = false;
        try {
            (void)run_relation(
                context.optix, *relation_pipeline,
                librts_indexed, librts_sources, 0.0f, 7);
        } catch (const std::runtime_error& error) {
            if (std::string(error.what()) !=
                    "direct relation capacity exceeded; partial result withheld")
                throw;
            overflow_witness_rejected = true;
        }
        if (!overflow_witness_rejected)
            throw std::runtime_error("direct relation overflow witness was accepted");
        RelationResult boundary = run_relation(
            context.optix, *relation_pipeline, {box(0,0,1,1,7)},
            {box(1,.25f,2,.75f,201), box(1,1,2,2,202),
             box(0.9999999403953552f,.25f,2,.75f,203),
             box(1.0000001192092896f,.25f,2,.75f,204)}, 0.0f, 3);
        auto triangle = run_triangle(context.optix, *triangle_pipeline);

        std::ostringstream output;
        output << "{\n  \"arm\":\"A_DIRECT_CUDA_OPTIX\",\n"
               << "  \"device_authoring_path\":\"CUDA_CPP_NVRTC_FROM_CPP_HOST\",\n"
               << "  \"outputs\":{\"bounded_relation\":{";
        output << "\"binary32_closed_boundary\":"; json_rows(output, boundary); output << ',';
        output << "\"diagnostic_cross\":"; json_rows(output, diagnostic); output << ',';
        output << "\"librts_tiny_broad\":"; json_rows(output, broad); output << ',';
        output << "\"librts_tiny_overlap_075\":"; json_rows(output, filtered);
        output << "},\"triangle\":{\"per_ray\":[";
        for (std::size_t i = 0; i < triangle.first.size(); ++i) {
            if (i) output << ',';
            output << triangle.first[i];
        }
        output << "],\"weighted_sum\":" << triangle.second << "}},\n"
               << "  \"performance_claimed\":false,\n"
               << "  \"registered_performance_timing_count\":0,\n"
               << "  \"capacity_overflow_witness\":{"
               << "\"application_result_exposed\":false,"
               << "\"capacity\":7,\"expected_unique_row_count\":8,"
               << "\"status\":\"FAIL_CLOSED\"},\n"
               << "  \"schema\":\"rtdl.goal5796.direct_optix_matched_functional.v1\",\n"
               << "  \"spec_sha256\":\"" << argv[4] << "\",\n"
               << "  \"status\":\"PASS\",\n"
               << "  \"optix_header_version\":" << OPTIX_VERSION << ",\n"
               << "  \"raw_event_counts\":{"
               << "\"binary32_closed_boundary\":" << boundary.raw_count << ','
               << "\"diagnostic_cross\":" << diagnostic.raw_count << ','
               << "\"librts_tiny_broad\":" << broad.raw_count << ','
               << "\"librts_tiny_overlap_075\":" << filtered.raw_count << "}\n}\n";
        std::cout << output.str();
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}

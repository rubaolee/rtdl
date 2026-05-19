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

inline std::string cuda_driver_error_message(CUresult result) {
    const char* raw = nullptr;
    cuGetErrorString(result, &raw);
    std::string message = std::string("CUDA driver error: ") + (raw ? raw : "unknown");
    if (raw && std::string(raw).find("unsupported toolchain") != std::string::npos) {
        message +=
            ". RTDL generated PTX that this CUDA driver cannot load. "
            "Use a CUDA toolkit/NVRTC version supported by the installed driver, "
            "put the driver's CUDA compat libraries first in LD_LIBRARY_PATH when required, "
            "or set RTDL_OPTIX_PTX_ARCH=compute_XX for the target GPU before rerunning.";
    }
    return message;
}

#define CU_CHECK(call)                                                          \
    do {                                                                        \
        CUresult _r = (call);                                                   \
        if (_r != CUDA_SUCCESS) {                                               \
            throw std::runtime_error(cuda_driver_error_message(_r));            \
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
                                            const std::vector<std::string>& include_opts,
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
    if (!std::getenv("RTDL_NVCC")) {
        std::error_code ignored;
        if (!std::filesystem::exists(nvcc, ignored)
            && std::filesystem::exists("/usr/local/cuda/bin/nvcc", ignored)) {
            nvcc = "/usr/local/cuda/bin/nvcc";
        }
    }
    std::vector<std::string> argv_storage = {
        nvcc,
        "-ptx",
        "--std=c++14",
        "-allow-unsupported-compiler",
        "-O3",
    };
    std::string configured_arch;
    if (const char* arch = std::getenv("RTDL_OPTIX_PTX_ARCH"); arch && arch[0] != '\0') {
        configured_arch = std::string("-arch=") + arch;
        argv_storage.push_back(configured_arch);
    }
    for (const std::string& include_opt : include_opts) {
        argv_storage.push_back(include_opt);
    }
    std::string ccbin;
    if (const char* configured_ccbin = std::getenv("RTDL_NVCC_CCBIN")) {
        ccbin = configured_ccbin;
    } else {
        std::error_code ignored;
        if (std::filesystem::exists("/usr/bin/g++-12", ignored)) {
            ccbin = "/usr/bin/g++-12";
        }
    }
    if (!ccbin.empty()) {
        argv_storage.push_back("-ccbin");
        argv_storage.push_back(ccbin);
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

static void append_include_arg(std::vector<std::string>& include_opts,
                               std::unordered_set<std::string>& seen,
                               const std::string& include_dir) {
    if (include_dir.empty()) return;
    std::error_code ignored;
    if (!std::filesystem::is_directory(include_dir, ignored)) return;
    std::string include_arg = "-I" + include_dir;
    if (seen.insert(include_arg).second) {
        include_opts.push_back(include_arg);
    }
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
    std::vector<std::string> nvcc_include_opts;
    std::unordered_set<std::string> seen_nvcc_include_opts;
    append_include_arg(nvcc_include_opts, seen_nvcc_include_opts, RTDL_OPTIX_INCLUDE_DIR);
    append_include_arg(nvcc_include_opts, seen_nvcc_include_opts, RTDL_CUDA_INCLUDE_DIR);

    std::vector<std::string> nvrtc_include_opts = nvcc_include_opts;
    std::unordered_set<std::string> seen_nvrtc_include_opts = seen_nvcc_include_opts;
    append_include_arg(nvrtc_include_opts, seen_nvrtc_include_opts, RTDL_CUDA_SYSTEM_INCLUDE_DIR);
    append_include_arg(nvrtc_include_opts, seen_nvrtc_include_opts, "/usr/include");
    append_include_arg(nvrtc_include_opts, seen_nvrtc_include_opts, "/usr/include/x86_64-linux-gnu");

    if (const char* compiler = std::getenv("RTDL_OPTIX_PTX_COMPILER");
        compiler && std::string(compiler) == "nvcc") {
        return compile_to_ptx_with_nvcc(cuda_src, name, nvcc_include_opts, extra_opts);
    }

    std::vector<std::string> option_storage;
    if (const char* arch = std::getenv("RTDL_OPTIX_PTX_ARCH"); arch && arch[0] != '\0') {
        option_storage.push_back(std::string("--gpu-architecture=") + arch);
    }
    std::vector<const char*> opts;
    opts.reserve(nvrtc_include_opts.size() + extra_opts.size() + 3);
    for (const std::string& include_opt : nvrtc_include_opts) {
        opts.push_back(include_opt.c_str());
    }
    for (const std::string& stored_opt : option_storage) {
        opts.push_back(stored_opt.c_str());
    }
    opts.push_back("--std=c++14");
#if defined(__linux__) && defined(__x86_64__)
    // CUDA 13 NVRTC can include glibc headers without the host architecture
    // predefines, which makes gnu/stubs.h look for missing 32-bit stubs.
    opts.push_back("-D__x86_64__=1");
    opts.push_back("-D__LP64__=1");
#endif
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
            return compile_to_ptx_with_nvcc(cuda_src, name, nvcc_include_opts, extra_opts);
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
    CU_CHECK(cuDevicePrimaryCtxRetain(&cu_ctx, dev));
    CU_CHECK(cuCtxSetCurrent(cu_ctx));
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
constexpr float kSegmentPairIntersectionTraceTmaxPad = 1.0e-4f;

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

OptixAabb aabb_for_triangle_3d(float x0, float y0, float z0,
                                float x1, float y1, float z1,
                                float x2, float y2, float z2) {
    OptixAabb a;
    a.minX = std::min({x0, x1, x2}) - kAabbPad;
    a.minY = std::min({y0, y1, y2}) - kAabbPad;
    a.minZ = std::min({z0, z1, z2}) - kAabbPad;
    a.maxX = std::max({x0, x1, x2}) + kAabbPad;
    a.maxY = std::max({y0, y1, y2}) + kAabbPad;
    a.maxZ = std::max({z0, z1, z2}) + kAabbPad;
    return a;
}

// ---------- BVH construction ------------------------------------------------

struct AccelHolder {
    CUdeviceptr output_buf   = 0;
    CUdeviceptr aabb_buf     = 0;
    bool owns_aabb_buf       = true;
    OptixTraversableHandle handle = 0;

    AccelHolder() = default;
    ~AccelHolder() {
        if (output_buf) cuMemFree(output_buf);
        if (aabb_buf && owns_aabb_buf) cuMemFree(aabb_buf);
    }
    AccelHolder(const AccelHolder&)            = delete;
    AccelHolder& operator=(const AccelHolder&) = delete;
    AccelHolder(AccelHolder&& other) noexcept
        : output_buf(other.output_buf),
          aabb_buf(other.aabb_buf),
          owns_aabb_buf(other.owns_aabb_buf),
          handle(other.handle) {
        other.output_buf = 0;
        other.aabb_buf = 0;
        other.owns_aabb_buf = true;
        other.handle = 0;
    }
    AccelHolder& operator=(AccelHolder&& other) noexcept {
        if (this != &other) {
            if (output_buf) cuMemFree(output_buf);
            if (aabb_buf && owns_aabb_buf) cuMemFree(aabb_buf);
            output_buf = other.output_buf;
            aabb_buf = other.aabb_buf;
            owns_aabb_buf = other.owns_aabb_buf;
            handle = other.handle;
            other.output_buf = 0;
            other.aabb_buf = 0;
            other.owns_aabb_buf = true;
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

static AccelHolder build_custom_accel_from_device_aabbs(
        OptixDeviceContext ctx,
        CUdeviceptr source_aabbs,
        size_t aabb_count) {
    AccelHolder result;
    if (aabb_count == 0) return result;
    if (!source_aabbs)
        throw std::runtime_error("device AABB buffer must not be null when aabb_count is nonzero");
    size_t aabb_bytes = sizeof(OptixAabb) * aabb_count;
    CU_CHECK(cuMemAlloc(&result.aabb_buf, aabb_bytes));
    CU_CHECK(cuMemcpyDtoD(result.aabb_buf, source_aabbs, aabb_bytes));

    OptixBuildInput build_input = {};
    build_input.type = OPTIX_BUILD_INPUT_TYPE_CUSTOM_PRIMITIVES;
    auto& cpp = build_input.customPrimitiveArray;
    cpp.aabbBuffers   = &result.aabb_buf;
    cpp.numPrimitives = static_cast<unsigned>(aabb_count);
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

static AccelHolder build_custom_accel_from_borrowed_device_aabbs(
        OptixDeviceContext ctx,
        CUdeviceptr source_aabbs,
        size_t aabb_count) {
    AccelHolder result;
    if (aabb_count == 0) return result;
    if (!source_aabbs)
        throw std::runtime_error("borrowed device AABB buffer must not be null when aabb_count is nonzero");
    result.aabb_buf = source_aabbs;
    result.owns_aabb_buf = false;

    OptixBuildInput build_input = {};
    build_input.type = OPTIX_BUILD_INPUT_TYPE_CUSTOM_PRIMITIVES;
    auto& cpp = build_input.customPrimitiveArray;
    cpp.aabbBuffers   = &result.aabb_buf;
    cpp.numPrimitives = static_cast<unsigned>(aabb_count);
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
        const char* intersection_name,       // null -> skip custom intersection
        const char* anyhit_name,             // null -> skip anyhit
        const char* closesthit_name,         // null -> skip closesthit
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

    char module_log[8192] = {};
    size_t module_log_size = sizeof(module_log);
    OptixResult module_result = optixModuleCreate(ctx, &mco, &pco,
                                                  ptx.c_str(), ptx.size(),
                                                  module_log, &module_log_size,
                                                  &holder->module);
    if (module_result != OPTIX_SUCCESS) {
        std::string message = std::string("OptiX module compile error: ") +
                              optixGetErrorString(module_result);
        if (module_log_size > 1 && module_log[0] != '\0') {
            message += "\n" + std::string(module_log);
        }
        throw std::runtime_error(message);
    }

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

// ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
// Device kernel source strings
// ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

// ---------- segment-pair intersection kernel -------------------------------------------------------

static const char* kSegmentPairIntersectionKernelSrc = R"CUDA(
#include <optix_device.h>

struct GpuSegment {
    float x0, y0, x1, y1;
    unsigned int id;
};

struct SegmentPairIntersectionRecord {
    unsigned int left_id, right_id;
    unsigned int left_index, right_index;
};

struct SegmentPairIntersectionParams {
    OptixTraversableHandle traversable;
    const GpuSegment* left_segs;
    const GpuSegment* right_segs;
    SegmentPairIntersectionRecord* output;
    unsigned int* output_count;
    unsigned int  output_capacity;
    unsigned int  probe_count;
    unsigned int  left_offset;
};

extern "C" {
__constant__ SegmentPairIntersectionParams params;
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

static __forceinline__ __device__ bool seg_intersect_conservative_candidate(
        float ax0, float ay0, float ax1, float ay1,
        float bx0, float by0, float bx1, float by1,
        float* ix_out, float* iy_out)
{
    float rx = ax1 - ax0, ry = ay1 - ay0;
    float sx = bx1 - bx0, sy = by1 - by0;
    float denom = rx * sy - ry * sx;
    if (dabsf(denom) < 1.0e-7f) {
        *ix_out = ax0;
        *iy_out = ay0;
        return true;
    }
    float qpx = bx0 - ax0, qpy = by0 - ay0;
    float t = (qpx * sy - qpy * sx) / denom;
    float u = (qpx * ry - qpy * rx) / denom;
    const float slack = 1.0e-4f;
    if (t < -slack || t > 1.0f + slack || u < -slack || u > 1.0f + slack) {
        return false;
    }
    *ix_out = ax0 + t * rx;
    *iy_out = ay0 + t * ry;
    return true;
}

extern "C" __global__ void __raygen__segment_pair_intersection_probe() {
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

extern "C" __global__ void __miss__segment_pair_intersection_miss() {}

extern "C" __global__ void __intersection__segment_pair_intersection_isect() {
    const unsigned int prim = optixGetPrimitiveIndex();
    optixSetPayload_1(prim);
    optixSetPayload_2(0u);
    optixSetPayload_3(0u);
    // Report the AABB overlap as a candidate; the any-hit stage may compact
    // obvious misses, and host-side exact refine remains the final authority.
    optixReportIntersection(0.5f, 0u);
}

extern "C" __global__ void __anyhit__segment_pair_intersection_anyhit() {
    const unsigned int pidx = optixGetPayload_0();
    const unsigned int bidx = optixGetPayload_1();
    const GpuSegment left = params.left_segs[pidx];
    const GpuSegment right = params.right_segs[bidx];
    float ix = 0.0f;
    float iy = 0.0f;
    if (!seg_intersect_conservative_candidate(
            left.x0, left.y0, left.x1, left.y1,
            right.x0, right.y0, right.x1, right.y1,
            &ix, &iy)) {
        optixIgnoreIntersection();
        return;
    }
    const unsigned int slot = atomicAdd(params.output_count, 1u);
    if (slot < params.output_capacity) {
        SegmentPairIntersectionRecord r;
        r.left_id  = left.id;
        r.right_id = right.id;
        r.left_index = params.left_offset + pidx;
        r.right_index = bidx;
        params.output[slot] = r;
    }
    optixIgnoreIntersection();
}
)CUDA";

// ---------- segment first-hit kernel --------------------------------------------------------------

static const char* kSegmentFirstHitKernelSrc = R"CUDA(
#include <optix_device.h>
#include <stdint.h>
#include <math.h>

struct GpuSegment {
    float x0, y0, x1, y1;
    unsigned int id;
};

struct SegmentFirstHitParams {
    OptixTraversableHandle traversable;
    const GpuSegment* probes;
    const GpuSegment* primitives;
    unsigned long long* best_pair;
    unsigned int probe_count;
};

extern "C" {
__constant__ SegmentFirstHitParams params;
}

static __forceinline__ __device__ float dabsf(float x) {
    return x < 0.0f ? -x : x;
}

static __forceinline__ __device__ bool seg_intersect_t(
        float ax0, float ay0, float ax1, float ay1,
        float bx0, float by0, float bx1, float by1,
        float* t_out)
{
    float rx = ax1 - ax0, ry = ay1 - ay0;
    float sx = bx1 - bx0, sy = by1 - by0;
    float denom = rx * sy - ry * sx;
    if (dabsf(denom) < 1.0e-7f) return false;
    float qpx = bx0 - ax0, qpy = by0 - ay0;
    float t = (qpx * sy - qpy * sx) / denom;
    float u = (qpx * ry - qpy * rx) / denom;
    const float slack = 1.0e-6f;
    if (t < -slack || t > 1.0f + slack || u < -slack || u > 1.0f + slack) {
        return false;
    }
    *t_out = fminf(fmaxf(t, 0.0f), 1.0f);
    return true;
}

extern "C" __global__ void __raygen__segment_first_hit_probe() {
    const unsigned int idx = optixGetLaunchIndex().x;
    if (idx >= params.probe_count) return;
    const GpuSegment p = params.probes[idx];
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

extern "C" __global__ void __miss__segment_first_hit_miss() {}

extern "C" __global__ void __intersection__segment_first_hit_isect() {
    optixSetPayload_1(optixGetPrimitiveIndex());
    optixReportIntersection(0.5f, 0u);
}

extern "C" __global__ void __anyhit__segment_first_hit_anyhit() {
    const unsigned int pidx = optixGetPayload_0();
    const unsigned int bidx = optixGetPayload_1();
    const GpuSegment probe = params.probes[pidx];
    const GpuSegment primitive = params.primitives[bidx];
    float t = 0.0f;
    if (!seg_intersect_t(
            probe.x0, probe.y0, probe.x1, probe.y1,
            primitive.x0, primitive.y0, primitive.x1, primitive.y1,
            &t)) {
        optixIgnoreIntersection();
        return;
    }
    const unsigned int t_key =
        ((unsigned int)(fminf(fmaxf(t, 0.0f), 1.0f) * 4294967294.0f)) + 1u;
    const unsigned long long candidate =
        (((unsigned long long)t_key) << 32) | ((unsigned long long)bidx);
    unsigned long long* slot = params.best_pair + pidx;
    unsigned long long old = *slot;
    while (candidate < old) {
        const unsigned long long observed = atomicCAS(slot, old, candidate);
        if (observed == old) {
            break;
        }
        old = observed;
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
    uint32_t point_index_offset;
    uint32_t device_prefilter;
};

extern "C" {
__constant__ PipParams params;
}

static __forceinline__ __device__ bool point_in_polygon(
        float px, float py,
        const GpuPolygonRef& poly)
{
    // The wider epsilon is useful for the non-positive-only float32 path and
    // for the opt-in positive-only device prefilter, where false negatives are
    // worse than extra host exact-refine candidates.
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
    const float query_half_extent = 0.5f;
    // Bounded vertical probe through the point. Closed-shape membership only
    // needs shapes whose AABB contains the point, not every shape above it.
    optixTrace(params.traversable,
               make_float3(px, py - query_half_extent, 0.0f),
               make_float3(0.0f, 1.0f, 0.0f),
               0.0f, 2.0f * query_half_extent, 0.0f,
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
        if (params.device_prefilter != 0u) {
            const GpuPolygonRef poly = params.polygons[prim];
            const float px = params.points_x[pidx];
            const float py = params.points_y[pidx];
            if (!point_in_polygon(px, py, poly)) {
                return;
            }
        }
        // In positive-hit mode, OptiX is only a conservative candidate
        // generator. Final inclusive truth is decided on the host. The default
        // reports every AABB candidate; the opt-in device prefilter only
        // removes obvious non-hits before host exact refinement.
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
            const uint32_t slot = atomicAdd(params.output_count, 1u);
            if (slot < params.output_capacity && params.output != nullptr) {
                PipRecord r;
                r.point_id = params.point_index_offset + pidx;
                r.polygon_id = prim;
                r.contains = 1u;
                params.output[slot] = r;
            }
            optixIgnoreIntersection();
            return;
        }
    const uint32_t slot = pidx * params.polygon_count + prim;
    params.output[slot].contains = 1u;
    optixIgnoreIntersection();
}
)CUDA";

// ---------- shape-pair relation kernel ---------------------------------------------------

static const char* kShapePairRelationKernelSrc = R"CUDA(
#include <optix_device.h>
#include <stdint.h>
#include <math.h>

struct GpuPolygonRef {
    uint32_t id;
    uint32_t vertex_offset;
    uint32_t vertex_count;
};

struct ShapePairRelationFlags {
    uint32_t requires_segment_intersection;
    uint32_t requires_point_containment;
};

struct ShapePairRelationParams {
    OptixTraversableHandle traversable;
    const GpuPolygonRef* left_polygons;
    const GpuPolygonRef* right_polygons;
    const float* left_vx;
    const float* left_vy;
    const float* right_vx;
    const float* right_vy;
    ShapePairRelationFlags* output;         // left_count * right_count elements
    uint32_t  right_count;
    uint32_t  left_count;
    uint32_t  launch_count;       // total raygen threads
    uint32_t  max_edges_per_poly; // raygen stride
};

extern "C" {
__constant__ ShapePairRelationParams params;
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
extern "C" __global__ void __raygen__shape_pair_relation_probe() {
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

extern "C" __global__ void __miss__shape_pair_relation_miss() {}

extern "C" __global__ void __intersection__shape_pair_relation_isect() {
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
    bool segment_pair_intersection_hit = false;
    for (uint32_t k = 0; k < rp.vertex_count; ++k) {
        uint32_t j0 = rp.vertex_offset + k;
        uint32_t j1 = rp.vertex_offset + (k + 1) % rp.vertex_count;
        float bx0 = params.right_vx[j0], by0 = params.right_vy[j0];
        float bx1 = params.right_vx[j1], by1 = params.right_vy[j1];
        if (seg_intersect_flag(ax0, ay0, ax1, ay1, bx0, by0, bx1, by1)) {
            segment_pair_intersection_hit = true;
            break;
        }
    }
    if (segment_pair_intersection_hit) {
        optixSetPayload_2(rpidx);
        optixReportIntersection(0.5f, 1u);  // hit_kind=1 -> segment-pair intersection
    }
}

extern "C" __global__ void __anyhit__shape_pair_relation_anyhit() {
    const uint32_t lpidx = optixGetPayload_0();
    const uint32_t rpidx = optixGetPayload_2();
    const uint32_t slot  = lpidx * params.right_count + rpidx;
    atomicOr(&params.output[slot].requires_segment_intersection, 1u);
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
    float ex = ox + dx * tmax, ey = oy + dy * tmax;

    auto point_in_triangle = [&](float px, float py) -> bool {
        const float v0x = x2 - x0;
        const float v0y = y2 - y0;
        const float v1x = x1 - x0;
        const float v1y = y1 - y0;
        const float v2x = px - x0;
        const float v2y = py - y0;

        const float dot00 = v0x * v0x + v0y * v0y;
        const float dot01 = v0x * v1x + v0y * v1y;
        const float dot02 = v0x * v2x + v0y * v2y;
        const float dot11 = v1x * v1x + v1y * v1y;
        const float dot12 = v1x * v2x + v1y * v2y;
        const float denom = dot00 * dot11 - dot01 * dot01;
        if (rt_absf(denom) < 1.0e-7f) return false;
        const float inv = 1.0f / denom;
        const float u = (dot11 * dot02 - dot01 * dot12) * inv;
        const float v = (dot00 * dot12 - dot01 * dot02) * inv;
        return u >= 0.0f && v >= 0.0f && (u + v) <= 1.0f;
    };

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

    if (point_in_triangle(ox, oy) || point_in_triangle(ex, ey)) {
        return true;
    }

    if (seg_hit(x0, y0, x1, y1) ||
        seg_hit(x1, y1, x2, y2) ||
        seg_hit(x2, y2, x0, y0))
        return true;
    return false;
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
    // Any-hit only needs a valid interval-local t. A fixed 0.5f drops
    // legitimate short rays whose world-space trace interval is below 0.5.
    float hit_t = optixGetRayTmin() + 1.0e-6f;
    if (hit_t > optixGetRayTmax()) hit_t = optixGetRayTmax();
    optixReportIntersection(hit_t, 0u);
}

extern "C" __global__ void __anyhit__rayhit_anyhit() {
    uint32_t count = optixGetPayload_1();
    optixSetPayload_1(count + 1u);
    optixIgnoreIntersection();
}
)CUDA";

// ---------- 3-D ray-triangle hit count kernel --------------------------------

static const char* kRayHitCount3DKernelSrc = R"CUDA(
#include <optix_device.h>

typedef unsigned int uint32_t;

// GPU-side 3-D ray: direction is pre-normalised; tmax is in world units.
struct GpuRay3D {
    float ox, oy, oz;
    float dx, dy, dz;  // unit-length
    float tmax;
    uint32_t id;
};

// GPU-side triangle (float32 coordinates).
struct GpuTriangle3D {
    float x0, y0, z0;
    float x1, y1, z1;
    float x2, y2, z2;
    uint32_t id;
};

struct RayHitCount3DRecord {
    uint32_t ray_id, hit_count;
};

struct RayHitCount3DParams {
    OptixTraversableHandle   traversable;
    const GpuRay3D*          rays;
    const GpuTriangle3D*     triangles;
    RayHitCount3DRecord*     output;
    uint32_t                 ray_count;
};

extern "C" {
__constant__ RayHitCount3DParams params;
}

// M-¶ller-Trumbore ray-triangle intersection.
// Returns the hit parameter t in [0, tmax], or -1 if no hit.
static __forceinline__ __device__ float ray_hits_triangle_3d(
        float ox, float oy, float oz,
        float dx, float dy, float dz,
        float tmax,
        float x0, float y0, float z0,
        float x1, float y1, float z1,
        float x2, float y2, float z2)
{
    const float edge1x = x1 - x0, edge1y = y1 - y0, edge1z = z1 - z0;
    const float edge2x = x2 - x0, edge2y = y2 - y0, edge2z = z2 - z0;

    // pvec = dir x edge2
    const float pvx = dy * edge2z - dz * edge2y;
    const float pvy = dz * edge2x - dx * edge2z;
    const float pvz = dx * edge2y - dy * edge2x;

    const float det = edge1x * pvx + edge1y * pvy + edge1z * pvz;
    if (det > -1.0e-8f && det < 1.0e-8f) return -1.0f;
    const float inv_det = 1.0f / det;

    // tvec = ray_origin - v0
    const float tvx = ox - x0, tvy = oy - y0, tvz = oz - z0;

    const float u = (tvx * pvx + tvy * pvy + tvz * pvz) * inv_det;
    if (u < 0.0f || u > 1.0f) return -1.0f;

    // qvec = tvec x edge1
    const float qvx = tvy * edge1z - tvz * edge1y;
    const float qvy = tvz * edge1x - tvx * edge1z;
    const float qvz = tvx * edge1y - tvy * edge1x;

    const float v = (dx * qvx + dy * qvy + dz * qvz) * inv_det;
    if (v < 0.0f || (u + v) > 1.0f) return -1.0f;

    const float t = (edge2x * qvx + edge2y * qvy + edge2z * qvz) * inv_det;
    if (t < 0.0f || t > tmax) return -1.0f;
    return t;
}

extern "C" __global__ void __raygen__rayhit3d_probe() {
    const uint32_t idx = optixGetLaunchIndex().x;
    if (idx >= params.ray_count) return;
    const GpuRay3D r = params.rays[idx];
    // Direction is already normalised; skip rays with zero direction.
    if (r.dx == 0.0f && r.dy == 0.0f && r.dz == 0.0f) {
        params.output[idx] = {r.id, 0u};
        return;
    }
    // Payload: p0 = ray index, p1 = accumulating hit count.
    unsigned int p0 = idx, p1 = 0u;
    optixTrace(params.traversable,
               make_float3(r.ox, r.oy, r.oz),
               make_float3(r.dx, r.dy, r.dz),
               0.0f, r.tmax, 0.0f,
               OptixVisibilityMask(255),
               OPTIX_RAY_FLAG_NONE,
               0, 1, 0,
               p0, p1);
    params.output[idx] = {r.id, p1};
}

extern "C" __global__ void __miss__rayhit3d_miss() {}

extern "C" __global__ void __intersection__rayhit3d_isect() {
    const uint32_t prim = optixGetPrimitiveIndex();
    const uint32_t ridx = optixGetPayload_0();
    const GpuRay3D     r = params.rays[ridx];
    const GpuTriangle3D t = params.triangles[prim];

    const float hit_t = ray_hits_triangle_3d(
            r.ox, r.oy, r.oz, r.dx, r.dy, r.dz, r.tmax,
            t.x0, t.y0, t.z0, t.x1, t.y1, t.z1, t.x2, t.y2, t.z2);
    if (hit_t < 0.0f) return;
    // Report hit at the computed t; AABB z-extent is used so t must be in
    // [optixGetRayTmin(), optixGetRayTmax()].  Because we set tmax on the
    // optixTrace call to r.tmax, and hit_t <= r.tmax, this is satisfied.
    optixReportIntersection(hit_t, 0u);
}

extern "C" __global__ void __anyhit__rayhit3d_anyhit() {
    // Count this hit and keep traversing all triangles.
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
    // Segment/polygon traces use unit directions and tmax=segment length.
    // Report a t inside that interval so short segments are not discarded.
    float hit_t = optixGetRayTmin() + 1.0e-6f;
    if (hit_t > optixGetRayTmax()) hit_t = optixGetRayTmax();
    optixReportIntersection(hit_t, 0u);
}

extern "C" __global__ void __anyhit__segpoly_anyhit() {
    uint32_t count = optixGetPayload_1();
    optixSetPayload_1(count + 1u);
    optixIgnoreIntersection();
}
)CUDA";

static const char* kSegPolyAnyhitRowsKernelSrc = R"CUDA(
#include <optix.h>
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

struct SegPolyPairRecord {
    uint32_t segment_id, polygon_id;
};

struct SegPolyRowsParams {
    OptixTraversableHandle traversable;
    const GpuSegment* segments;
    const GpuPolygonRef* polygons;
    const float* vertices_x;
    const float* vertices_y;
    SegPolyPairRecord* output;
    uint32_t* output_count;
    uint32_t* overflowed;
    uint32_t output_capacity;
    uint32_t segment_count;
};

extern "C" {
__constant__ SegPolyRowsParams params;
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

extern "C" __global__ void __raygen__segpoly_rows_probe() {
    const uint32_t idx = optixGetLaunchIndex().x;
    if (idx >= params.segment_count) return;
    const GpuSegment s = params.segments[idx];
    float dx = s.x1 - s.x0, dy = s.y1 - s.y0;
    float len = sqrtf(dx * dx + dy * dy);
    if (len < 1.0e-10f) return;
    unsigned int p0 = idx, p1 = 0u, p2 = 0u, p3 = 0u;
    optixTrace(params.traversable,
               make_float3(s.x0, s.y0, 0.0f),
               make_float3(dx / len, dy / len, 0.0f),
               0.0f, len, 0.0f,
               OptixVisibilityMask(255),
               OPTIX_RAY_FLAG_NONE,
               0, 1, 0,
               p0, p1, p2, p3);
}

extern "C" __global__ void __miss__segpoly_rows_miss() {}

extern "C" __global__ void __intersection__segpoly_rows_isect() {
    const uint32_t prim = optixGetPrimitiveIndex();
    const uint32_t sidx = optixGetPayload_0();
    const GpuSegment s = params.segments[sidx];
    const GpuPolygonRef poly = params.polygons[prim];
    if (!seg_hits_polygon(s.x0, s.y0, s.x1, s.y1, poly)) return;
    float hit_t = optixGetRayTmin() + 1.0e-6f;
    if (hit_t > optixGetRayTmax()) hit_t = optixGetRayTmax();
    optixReportIntersection(hit_t, 0u);
}

extern "C" __global__ void __anyhit__segpoly_rows_anyhit() {
    const uint32_t sidx = optixGetPayload_0();
    const uint32_t prim = optixGetPrimitiveIndex();
    const uint32_t slot = atomicAdd(params.output_count, 1u);
    if (slot < params.output_capacity && params.output != nullptr) {
        params.output[slot] = {params.segments[sidx].id, params.polygons[prim].id};
    } else if (params.overflowed != nullptr) {
        atomicExch(params.overflowed, 1u);
    }
    optixIgnoreIntersection();
}
)CUDA";

// ---------- Point-nearest-segment: CUDA kernel (no OptiX BVH) ---------------
//
// PointNearestSegment does not map well to OptiX ray traversal (it needs a
// radius/distance query, not a ray-AABB intersection). We use a plain CUDA
// kernel that is GPU-parallel but brute-force: one thread owns one point and
// scans the full segment list.

static const char* kPointNearestKernelSrc = R"CUDA(
#include <stdint.h>
#include <math.h>
#include <float.h>

struct GpuPoint { float x, y; uint32_t id; uint32_t pad; };
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

static const char* kFixedRadiusNeighborsKernelSrc = R"CUDA(
#include <stdint.h>
#include <math.h>
#include <float.h>

struct GpuPoint { float x, y; uint32_t id; uint32_t pad; };
struct FrnRecord { uint32_t query_id, neighbor_id; float distance; };

extern "C" __global__ void fixed_radius_neighbors(
        const GpuPoint* query_points,
        uint32_t        query_count,
        const GpuPoint* search_points,
        uint32_t        search_count,
        float           radius,
        uint32_t        k_max,
        FrnRecord*      output)
{
    const uint32_t qidx = blockIdx.x * blockDim.x + threadIdx.x;
    if (qidx >= query_count) return;

    FrnRecord* query_out = output + static_cast<size_t>(qidx) * static_cast<size_t>(k_max);
    for (uint32_t slot = 0; slot < k_max; ++slot) {
        query_out[slot].query_id = query_points[qidx].id;
        query_out[slot].neighbor_id = 0xffffffffu;
        query_out[slot].distance = INFINITY;
    }

    const float px = query_points[qidx].x;
    const float py = query_points[qidx].y;
    const float radius_sq = radius * radius;

    for (uint32_t sidx = 0; sidx < search_count; ++sidx) {
        const float dx = search_points[sidx].x - px;
        const float dy = search_points[sidx].y - py;
        const float distance_sq = dx * dx + dy * dy;
        if (distance_sq > radius_sq) {
            continue;
        }
        const float distance = sqrtf(distance_sq);
        const uint32_t neighbor_id = search_points[sidx].id;

        uint32_t insert_at = k_max;
        for (uint32_t slot = 0; slot < k_max; ++slot) {
            const bool empty = query_out[slot].neighbor_id == 0xffffffffu;
            const bool better_distance = distance < query_out[slot].distance - 1.0e-7f;
            const bool same_distance = fabsf(distance - query_out[slot].distance) <= 1.0e-7f;
            const bool better_id = same_distance && neighbor_id < query_out[slot].neighbor_id;
            if (empty || better_distance || better_id) {
                insert_at = slot;
                break;
            }
        }
        if (insert_at == k_max) {
            continue;
        }
        for (uint32_t slot = k_max - 1; slot > insert_at; --slot) {
            query_out[slot] = query_out[slot - 1];
        }
        query_out[insert_at].query_id = query_points[qidx].id;
        query_out[insert_at].neighbor_id = neighbor_id;
        query_out[insert_at].distance = distance;
    }
}
)CUDA";

static const char* kCollectKBoundedI64KernelSrc = R"CUDA(
#include <stdint.h>
#include <stddef.h>

__device__ bool collect_k_rows_equal(
        const int64_t* rows,
        size_t lhs,
        size_t rhs,
        size_t row_width)
{
    for (size_t column = 0; column < row_width; ++column) {
        if (rows[lhs * row_width + column] != rows[rhs * row_width + column])
            return false;
    }
    return true;
}

__device__ int collect_k_compare_rows(
        const int64_t* rows,
        size_t lhs,
        size_t rhs,
        size_t row_width)
{
    for (size_t column = 0; column < row_width; ++column) {
        const int64_t left = rows[lhs * row_width + column];
        const int64_t right = rows[rhs * row_width + column];
        if (left < right)
            return -1;
        if (left > right)
            return 1;
    }
    return 0;
}

extern "C" __global__ void collect_k_bounded_i64(
        const int64_t* candidate_rows,
        size_t candidate_count,
        size_t row_width,
        int64_t* rows_out,
        size_t row_capacity,
        size_t* emitted_count,
        uint32_t* overflowed)
{
    if (blockIdx.x != 0 || threadIdx.x != 0)
        return;

    size_t unique_count = 0;
    for (size_t row_index = 0; row_index < candidate_count; ++row_index) {
        bool seen = false;
        for (size_t prior = 0; prior < row_index; ++prior) {
            if (collect_k_rows_equal(candidate_rows, row_index, prior, row_width)) {
                seen = true;
                break;
            }
        }
        if (!seen)
            ++unique_count;
    }

    *emitted_count = unique_count;
    *overflowed = 0u;
    if (unique_count > row_capacity) {
        *overflowed = 1u;
        return;
    }

    bool have_last = false;
    size_t last_index = 0;
    for (size_t out_index = 0; out_index < unique_count; ++out_index) {
        bool have_best = false;
        size_t best_index = 0;

        for (size_t row_index = 0; row_index < candidate_count; ++row_index) {
            const bool greater_than_last =
                !have_last || collect_k_compare_rows(candidate_rows, row_index, last_index, row_width) > 0;
            const bool less_than_best =
                !have_best || collect_k_compare_rows(candidate_rows, row_index, best_index, row_width) < 0;
            if (greater_than_last && less_than_best) {
                best_index = row_index;
                have_best = true;
            }
        }

        for (size_t column = 0; column < row_width; ++column) {
            rows_out[out_index * row_width + column] = candidate_rows[best_index * row_width + column];
        }
        last_index = best_index;
        have_last = true;
    }
}
)CUDA";

static const char* kCollectKBoundedI64RowWidth2SortKernelSrc = R"CUDA(
#include <stdint.h>
#include <stddef.h>
#include <limits.h>

__device__ int collect_k_pair_compare(int64_t lhs0, int64_t lhs1, int64_t rhs0, int64_t rhs1)
{
    if (lhs0 < rhs0)
        return -1;
    if (lhs0 > rhs0)
        return 1;
    if (lhs1 < rhs1)
        return -1;
    if (lhs1 > rhs1)
        return 1;
    return 0;
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_sort(
        const int64_t* candidate_rows,
        size_t candidate_count,
        size_t padded_count,
        int64_t* rows_out,
        size_t row_capacity,
        size_t* emitted_count,
        uint32_t* overflowed)
{
    extern __shared__ int64_t shared[];
    int64_t* first = shared;
    int64_t* second = shared + padded_count;
    uint8_t* valid = reinterpret_cast<uint8_t*>(shared + padded_count * 2);
    const size_t tid = static_cast<size_t>(threadIdx.x);
    const size_t stride = static_cast<size_t>(blockDim.x);

    for (size_t index = tid; index < padded_count; index += stride) {
        if (index < candidate_count) {
            first[index] = candidate_rows[index * 2];
            second[index] = candidate_rows[index * 2 + 1];
            valid[index] = 1u;
        } else {
            first[index] = 0;
            second[index] = 0;
            valid[index] = 0u;
        }
    }
    __syncthreads();

    for (size_t k = 2; k <= padded_count; k <<= 1) {
        for (size_t j = k >> 1; j > 0; j >>= 1) {
            for (size_t index = tid; index < padded_count; index += stride) {
                const size_t peer = index ^ j;
                if (peer > index && peer < padded_count) {
                    const bool ascending = (index & k) == 0;
                    int cmp = 0;
                    if (valid[index] != valid[peer]) {
                        cmp = valid[index] ? -1 : 1;
                    } else if (valid[index]) {
                        cmp = collect_k_pair_compare(first[index], second[index], first[peer], second[peer]);
                    }
                    const bool should_swap = ascending ? (cmp > 0) : (cmp < 0);
                    if (should_swap) {
                        const int64_t tmp_first = first[index];
                        const int64_t tmp_second = second[index];
                        const uint8_t tmp_valid = valid[index];
                        first[index] = first[peer];
                        second[index] = second[peer];
                        valid[index] = valid[peer];
                        first[peer] = tmp_first;
                        second[peer] = tmp_second;
                        valid[peer] = tmp_valid;
                    }
                }
            }
            __syncthreads();
        }
    }

    if (tid != 0)
        return;

    size_t unique_count = 0;
    for (size_t index = 0; index < padded_count; ++index) {
        if (!valid[index])
            break;
        if (index == 0 || first[index] != first[index - 1] || second[index] != second[index - 1])
            ++unique_count;
    }

    *emitted_count = unique_count;
    *overflowed = 0u;
    if (unique_count > row_capacity) {
        *overflowed = 1u;
        return;
    }

    size_t out_index = 0;
    for (size_t index = 0; index < padded_count && out_index < unique_count; ++index) {
        if (!valid[index])
            break;
        if (index != 0 && first[index] == first[index - 1] && second[index] == second[index - 1])
            continue;
        rows_out[out_index * 2] = first[index];
        rows_out[out_index * 2 + 1] = second[index];
        ++out_index;
    }
}
)CUDA";

static const char* kCollectKBoundedI64RowWidth2CubSortKernelSrc = R"CUDA(
#include <stdint.h>
#include <stddef.h>
#include <cub/block/block_merge_sort.cuh>

struct CollectKRow2 {
    int64_t first;
    int64_t second;
};

struct CollectKRow2Less {
    __device__ bool operator()(const CollectKRow2& lhs, const CollectKRow2& rhs) const
    {
        if (lhs.first != rhs.first)
            return lhs.first < rhs.first;
        return lhs.second < rhs.second;
    }
};

extern "C" __global__ void collect_k_bounded_i64_row_width2_cub_sort(
        const int64_t* candidate_rows,
        size_t candidate_count,
        int64_t* rows_out,
        size_t row_capacity,
        size_t* emitted_count,
        uint32_t* overflowed)
{
    constexpr int block_threads = 256;
    constexpr int items_per_thread = 8;
    constexpr size_t tile_capacity = static_cast<size_t>(block_threads * items_per_thread);
    using BlockSort = cub::BlockMergeSort<CollectKRow2, block_threads, items_per_thread>;

    __shared__ typename BlockSort::TempStorage temp_storage;
    CollectKRow2 rows[items_per_thread];

    const size_t tid = static_cast<size_t>(threadIdx.x);
    #pragma unroll
    for (int item = 0; item < items_per_thread; ++item) {
        const size_t index = tid * static_cast<size_t>(items_per_thread) + static_cast<size_t>(item);
        if (index < candidate_count) {
            rows[item].first = candidate_rows[index * 2];
            rows[item].second = candidate_rows[index * 2 + 1];
        } else {
            rows[item].first = INT64_MAX;
            rows[item].second = INT64_MAX;
        }
    }

    BlockSort(temp_storage).Sort(rows, CollectKRow2Less());

    #pragma unroll
    for (int item = 0; item < items_per_thread; ++item) {
        const size_t index = tid * static_cast<size_t>(items_per_thread) + static_cast<size_t>(item);
        if (index < candidate_count && index < row_capacity) {
            rows_out[index * 2] = rows[item].first;
            rows_out[index * 2 + 1] = rows[item].second;
        }
    }

    if (threadIdx.x == 0) {
        *emitted_count = candidate_count < tile_capacity ? candidate_count : tile_capacity;
        *overflowed = candidate_count > row_capacity ? 1u : 0u;
    }
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_cub_sort_tiles(
        const int64_t* candidate_rows,
        size_t candidate_count,
        int64_t* rows_out,
        size_t* emitted_counts,
        uint32_t* overflowed_flags)
{
    constexpr int block_threads = 256;
    constexpr int items_per_thread = 8;
    constexpr size_t tile_capacity = static_cast<size_t>(block_threads * items_per_thread);
    using BlockSort = cub::BlockMergeSort<CollectKRow2, block_threads, items_per_thread>;

    __shared__ typename BlockSort::TempStorage temp_storage;
    CollectKRow2 rows[items_per_thread];

    const size_t tile_index = static_cast<size_t>(blockIdx.x);
    const size_t tile_offset = tile_index * tile_capacity;
    if (tile_offset >= candidate_count)
        return;
    const size_t tile_candidate_count =
        candidate_count - tile_offset < tile_capacity ? candidate_count - tile_offset : tile_capacity;
    const size_t tid = static_cast<size_t>(threadIdx.x);

    #pragma unroll
    for (int item = 0; item < items_per_thread; ++item) {
        const size_t index = tid * static_cast<size_t>(items_per_thread) + static_cast<size_t>(item);
        if (index < tile_candidate_count) {
            const size_t input_index = tile_offset + index;
            rows[item].first = candidate_rows[input_index * 2];
            rows[item].second = candidate_rows[input_index * 2 + 1];
        } else {
            rows[item].first = INT64_MAX;
            rows[item].second = INT64_MAX;
        }
    }

    BlockSort(temp_storage).Sort(rows, CollectKRow2Less());

    int64_t* tile_rows_out = rows_out + tile_index * tile_capacity * 2;
    #pragma unroll
    for (int item = 0; item < items_per_thread; ++item) {
        const size_t index = tid * static_cast<size_t>(items_per_thread) + static_cast<size_t>(item);
        if (index < tile_candidate_count) {
            tile_rows_out[index * 2] = rows[item].first;
            tile_rows_out[index * 2 + 1] = rows[item].second;
        }
    }

    if (threadIdx.x == 0) {
        emitted_counts[tile_index] = tile_candidate_count;
        overflowed_flags[tile_index] = 0u;
    }
}
)CUDA";

static const char* kCollectKBoundedI64RowWidth2MergeTwoKernelSrc = R"CUDA(
#include <stdint.h>
#include <stddef.h>

__device__ int collect_k_merge_pair_compare(int64_t lhs0, int64_t lhs1, int64_t rhs0, int64_t rhs1)
{
    if (lhs0 < rhs0)
        return -1;
    if (lhs0 > rhs0)
        return 1;
    if (lhs1 < rhs1)
        return -1;
    if (lhs1 > rhs1)
        return 1;
    return 0;
}

__device__ void collect_k_merge_next_pair(
        const int64_t* first_rows,
        size_t first_count,
        const int64_t* second_rows,
        size_t second_count,
        size_t* first_index,
        size_t* second_index,
        int64_t* value0,
        int64_t* value1)
{
    if (*second_index >= second_count) {
        *value0 = first_rows[*first_index * 2];
        *value1 = first_rows[*first_index * 2 + 1];
        ++(*first_index);
        return;
    }
    if (*first_index >= first_count) {
        *value0 = second_rows[*second_index * 2];
        *value1 = second_rows[*second_index * 2 + 1];
        ++(*second_index);
        return;
    }

    const int64_t first0 = first_rows[*first_index * 2];
    const int64_t first1 = first_rows[*first_index * 2 + 1];
    const int64_t second0 = second_rows[*second_index * 2];
    const int64_t second1 = second_rows[*second_index * 2 + 1];
    const int cmp = collect_k_merge_pair_compare(first0, first1, second0, second1);
    if (cmp <= 0) {
        *value0 = first0;
        *value1 = first1;
        ++(*first_index);
        if (cmp == 0)
            ++(*second_index);
    } else {
        *value0 = second0;
        *value1 = second1;
        ++(*second_index);
    }
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_merge_two(
        const int64_t* first_rows,
        size_t first_count,
        const int64_t* second_rows,
        size_t second_count,
        int64_t* rows_out,
        size_t row_capacity,
        size_t* emitted_count,
        uint32_t* overflowed)
{
    if (blockIdx.x != 0 || threadIdx.x != 0)
        return;

    size_t first_index = 0;
    size_t second_index = 0;
    size_t unique_count = 0;
    bool have_last = false;
    int64_t last0 = 0;
    int64_t last1 = 0;
    while (first_index < first_count || second_index < second_count) {
        int64_t value0 = 0;
        int64_t value1 = 0;
        collect_k_merge_next_pair(
            first_rows, first_count, second_rows, second_count,
            &first_index, &second_index, &value0, &value1);
        if (have_last && value0 == last0 && value1 == last1)
            continue;
        if (unique_count < row_capacity) {
            rows_out[unique_count * 2] = value0;
            rows_out[unique_count * 2 + 1] = value1;
        }
        last0 = value0;
        last1 = value1;
        have_last = true;
        ++unique_count;
    }

    *emitted_count = unique_count;
    *overflowed = unique_count > row_capacity ? 1u : 0u;
}
)CUDA";

static const char* kCollectKBoundedI64RowWidth2MergeLevelKernelSrc = R"CUDA(
#include <stdint.h>
#include <stddef.h>

__device__ int collect_k_merge_pair_compare(int64_t lhs0, int64_t lhs1, int64_t rhs0, int64_t rhs1)
{
    if (lhs0 < rhs0)
        return -1;
    if (lhs0 > rhs0)
        return 1;
    if (lhs1 < rhs1)
        return -1;
    if (lhs1 > rhs1)
        return 1;
    return 0;
}

__device__ void collect_k_merge_next_pair(
        const int64_t* first_rows,
        size_t first_count,
        const int64_t* second_rows,
        size_t second_count,
        size_t* first_index,
        size_t* second_index,
        int64_t* value0,
        int64_t* value1)
{
    if (*second_index >= second_count) {
        *value0 = first_rows[*first_index * 2];
        *value1 = first_rows[*first_index * 2 + 1];
        ++(*first_index);
        return;
    }
    if (*first_index >= first_count) {
        *value0 = second_rows[*second_index * 2];
        *value1 = second_rows[*second_index * 2 + 1];
        ++(*second_index);
        return;
    }

    const int64_t first0 = first_rows[*first_index * 2];
    const int64_t first1 = first_rows[*first_index * 2 + 1];
    const int64_t second0 = second_rows[*second_index * 2];
    const int64_t second1 = second_rows[*second_index * 2 + 1];
    const int cmp = collect_k_merge_pair_compare(first0, first1, second0, second1);
    if (cmp <= 0) {
        *value0 = first0;
        *value1 = first1;
        ++(*first_index);
        if (cmp == 0)
            ++(*second_index);
    } else {
        *value0 = second0;
        *value1 = second1;
        ++(*second_index);
    }
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_merge_level(
        const uint64_t* first_row_ptrs,
        const size_t* first_counts,
        const uint64_t* second_row_ptrs,
        const size_t* second_counts,
        const uint64_t* output_row_ptrs,
        size_t output_capacity,
        size_t* emitted_counts,
        uint32_t* overflowed,
        size_t pair_count)
{
    const size_t pair_index = blockIdx.x;
    if (pair_index >= pair_count || threadIdx.x != 0)
        return;

    const int64_t* first_rows =
        reinterpret_cast<const int64_t*>(static_cast<uintptr_t>(first_row_ptrs[pair_index]));
    const int64_t* second_rows =
        reinterpret_cast<const int64_t*>(static_cast<uintptr_t>(second_row_ptrs[pair_index]));
    int64_t* rows_out =
        reinterpret_cast<int64_t*>(static_cast<uintptr_t>(output_row_ptrs[pair_index]));
    const size_t first_count = first_counts[pair_index];
    const size_t second_count = second_counts[pair_index];

    size_t first_index = 0;
    size_t second_index = 0;
    size_t unique_count = 0;
    bool have_last = false;
    int64_t last0 = 0;
    int64_t last1 = 0;
    while (first_index < first_count || second_index < second_count) {
        int64_t value0 = 0;
        int64_t value1 = 0;
        collect_k_merge_next_pair(
            first_rows, first_count, second_rows, second_count,
            &first_index, &second_index, &value0, &value1);
        if (have_last && value0 == last0 && value1 == last1)
            continue;
        if (unique_count < output_capacity) {
            rows_out[unique_count * 2] = value0;
            rows_out[unique_count * 2 + 1] = value1;
        }
        last0 = value0;
        last1 = value1;
        have_last = true;
        ++unique_count;
    }

    emitted_counts[pair_index] = unique_count;
    overflowed[pair_index] = unique_count > output_capacity ? 1u : 0u;
}
)CUDA";

static const char* kCollectKCooperativeLaunchSmokeKernelSrc = R"CUDA(
#include <stdint.h>
#include <cooperative_groups.h>

namespace cg = cooperative_groups;

extern "C" __global__ void collect_k_cooperative_launch_smoke(uint32_t* observed)
{
    cg::grid_group grid = cg::this_grid();
    if (threadIdx.x == 0)
        atomicAdd(&observed[0], 1u);
    grid.sync();
    if (grid.thread_rank() == 0)
        observed[1] = observed[0];
}
)CUDA";

static const char* kCollectKBoundedI64RowWidth2FinalCompactKernelSrc = R"CUDA(
#include <stdint.h>
#include <stddef.h>

__device__ int collect_k_final_pair_compare(int64_t lhs0, int64_t lhs1, int64_t rhs0, int64_t rhs1)
{
    if (lhs0 < rhs0)
        return -1;
    if (lhs0 > rhs0)
        return 1;
    if (lhs1 < rhs1)
        return -1;
    if (lhs1 > rhs1)
        return 1;
    return 0;
}

__device__ size_t collect_k_final_lower_bound(
        const int64_t* rows,
        size_t count,
        int64_t value0,
        int64_t value1)
{
    size_t low = 0;
    size_t high = count;
    while (low < high) {
        const size_t mid = low + (high - low) / 2;
        const int64_t mid0 = rows[mid * 2];
        const int64_t mid1 = rows[mid * 2 + 1];
        if (collect_k_final_pair_compare(mid0, mid1, value0, value1) < 0)
            low = mid + 1;
        else
            high = mid;
    }
    return low;
}

__device__ size_t collect_k_final_upper_bound(
        const int64_t* rows,
        size_t count,
        int64_t value0,
        int64_t value1)
{
    size_t low = 0;
    size_t high = count;
    while (low < high) {
        const size_t mid = low + (high - low) / 2;
        const int64_t mid0 = rows[mid * 2];
        const int64_t mid1 = rows[mid * 2 + 1];
        if (collect_k_final_pair_compare(mid0, mid1, value0, value1) <= 0)
            low = mid + 1;
        else
            high = mid;
    }
    return low;
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_final_materialize(
        const int64_t* first_rows,
        size_t first_count,
        const int64_t* second_rows,
        size_t second_count,
        int64_t* merged_rows)
{
    const size_t total = first_count + second_count;
    const size_t index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index >= total)
        return;

    if (index < first_count) {
        const int64_t value0 = first_rows[index * 2];
        const int64_t value1 = first_rows[index * 2 + 1];
        const size_t output_index =
            index + collect_k_final_lower_bound(second_rows, second_count, value0, value1);
        merged_rows[output_index * 2] = value0;
        merged_rows[output_index * 2 + 1] = value1;
        return;
    }

    const size_t second_index = index - first_count;
    const int64_t value0 = second_rows[second_index * 2];
    const int64_t value1 = second_rows[second_index * 2 + 1];
    const size_t output_index =
        second_index + collect_k_final_upper_bound(first_rows, first_count, value0, value1);
    merged_rows[output_index * 2] = value0;
    merged_rows[output_index * 2 + 1] = value1;
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_final_materialize_counts(
        const int64_t* first_rows,
        const int64_t* second_rows,
        const size_t* counts,
        int64_t* merged_rows)
{
    const size_t first_count = counts[0];
    const size_t second_count = counts[1];
    const size_t total = first_count + second_count;
    const size_t index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index >= total)
        return;

    if (index < first_count) {
        const int64_t value0 = first_rows[index * 2];
        const int64_t value1 = first_rows[index * 2 + 1];
        const size_t output_index =
            index + collect_k_final_lower_bound(second_rows, second_count, value0, value1);
        merged_rows[output_index * 2] = value0;
        merged_rows[output_index * 2 + 1] = value1;
        return;
    }

    const size_t second_index = index - first_count;
    const int64_t value0 = second_rows[second_index * 2];
    const int64_t value1 = second_rows[second_index * 2 + 1];
    const size_t output_index =
        second_index + collect_k_final_upper_bound(first_rows, first_count, value0, value1);
    merged_rows[output_index * 2] = value0;
    merged_rows[output_index * 2 + 1] = value1;
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_final_materialize_level(
        const uint64_t* first_row_ptrs,
        const size_t* first_counts,
        const uint64_t* second_row_ptrs,
        const size_t* second_counts,
        size_t output_capacity,
        int64_t* merged_rows,
        size_t pair_count,
        size_t blocks_per_pair)
{
    const size_t pair_index = blockIdx.x / blocks_per_pair;
    if (pair_index >= pair_count)
        return;
    const size_t local_block = blockIdx.x - pair_index * blocks_per_pair;
    const size_t index = local_block * blockDim.x + threadIdx.x;
    const int64_t* first_rows =
        reinterpret_cast<const int64_t*>(static_cast<uintptr_t>(first_row_ptrs[pair_index]));
    const int64_t* second_rows =
        reinterpret_cast<const int64_t*>(static_cast<uintptr_t>(second_row_ptrs[pair_index]));
    const size_t first_count = first_counts[pair_index];
    const size_t second_count = second_counts[pair_index];
    const size_t total = first_count + second_count;
    if (index >= total)
        return;

    int64_t* pair_merged_rows = merged_rows + pair_index * output_capacity * 2;
    if (index < first_count) {
        const int64_t value0 = first_rows[index * 2];
        const int64_t value1 = first_rows[index * 2 + 1];
        const size_t output_index =
            index + collect_k_final_lower_bound(second_rows, second_count, value0, value1);
        pair_merged_rows[output_index * 2] = value0;
        pair_merged_rows[output_index * 2 + 1] = value1;
        return;
    }

    const size_t second_index = index - first_count;
    const int64_t value0 = second_rows[second_index * 2];
    const int64_t value1 = second_rows[second_index * 2 + 1];
    const size_t output_index =
        second_index + collect_k_final_upper_bound(first_rows, first_count, value0, value1);
    pair_merged_rows[output_index * 2] = value0;
    pair_merged_rows[output_index * 2 + 1] = value1;
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_final_materialize_level_counts_pointers(
        const uint64_t* first_row_ptrs,
        const uint64_t* second_row_ptrs,
        const size_t* current_counts,
        size_t output_capacity,
        int64_t* merged_rows,
        size_t pair_count,
        size_t blocks_per_pair)
{
    const size_t pair_index = blockIdx.x / blocks_per_pair;
    if (pair_index >= pair_count)
        return;
    const size_t local_block = blockIdx.x - pair_index * blocks_per_pair;
    const size_t index = local_block * blockDim.x + threadIdx.x;
    const int64_t* first_rows =
        reinterpret_cast<const int64_t*>(static_cast<uintptr_t>(first_row_ptrs[pair_index]));
    const int64_t* second_rows =
        reinterpret_cast<const int64_t*>(static_cast<uintptr_t>(second_row_ptrs[pair_index]));
    const size_t first_count = current_counts[pair_index * 2];
    const size_t second_count = current_counts[pair_index * 2 + 1];
    const size_t total = first_count + second_count;
    if (index >= total)
        return;

    int64_t* pair_merged_rows = merged_rows + pair_index * output_capacity * 2;
    if (index < first_count) {
        const int64_t value0 = first_rows[index * 2];
        const int64_t value1 = first_rows[index * 2 + 1];
        const size_t output_index =
            index + collect_k_final_lower_bound(second_rows, second_count, value0, value1);
        pair_merged_rows[output_index * 2] = value0;
        pair_merged_rows[output_index * 2 + 1] = value1;
        return;
    }

    const size_t second_index = index - first_count;
    const int64_t value0 = second_rows[second_index * 2];
    const int64_t value1 = second_rows[second_index * 2 + 1];
    const size_t output_index =
        second_index + collect_k_final_upper_bound(first_rows, first_count, value0, value1);
    pair_merged_rows[output_index * 2] = value0;
    pair_merged_rows[output_index * 2 + 1] = value1;
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_final_materialize_level_derived(
        const int64_t* current_base,
        const size_t* first_counts,
        const size_t* second_counts,
        size_t segment_capacity,
        size_t output_capacity,
        int64_t* merged_rows,
        size_t pair_count,
        size_t blocks_per_pair)
{
    const size_t pair_index = blockIdx.x / blocks_per_pair;
    if (pair_index >= pair_count)
        return;
    const size_t local_block = blockIdx.x - pair_index * blocks_per_pair;
    const size_t index = local_block * blockDim.x + threadIdx.x;
    const int64_t* first_rows = current_base + (pair_index * 2) * segment_capacity * 2;
    const int64_t* second_rows = current_base + (pair_index * 2 + 1) * segment_capacity * 2;
    const size_t first_count = first_counts[pair_index];
    const size_t second_count = second_counts[pair_index];
    const size_t total = first_count + second_count;
    if (index >= total)
        return;

    int64_t* pair_merged_rows = merged_rows + pair_index * output_capacity * 2;
    if (index < first_count) {
        const int64_t value0 = first_rows[index * 2];
        const int64_t value1 = first_rows[index * 2 + 1];
        const size_t output_index =
            index + collect_k_final_lower_bound(second_rows, second_count, value0, value1);
        pair_merged_rows[output_index * 2] = value0;
        pair_merged_rows[output_index * 2 + 1] = value1;
        return;
    }

    const size_t second_index = index - first_count;
    const int64_t value0 = second_rows[second_index * 2];
    const int64_t value1 = second_rows[second_index * 2 + 1];
    const size_t output_index =
        second_index + collect_k_final_upper_bound(first_rows, first_count, value0, value1);
    pair_merged_rows[output_index * 2] = value0;
    pair_merged_rows[output_index * 2 + 1] = value1;
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_final_materialize_level_counts_derived(
        const int64_t* current_base,
        const size_t* current_counts,
        size_t segment_capacity,
        size_t output_capacity,
        int64_t* merged_rows,
        size_t pair_count,
        size_t blocks_per_pair)
{
    const size_t pair_index = blockIdx.x / blocks_per_pair;
    if (pair_index >= pair_count)
        return;
    const size_t local_block = blockIdx.x - pair_index * blocks_per_pair;
    const size_t index = local_block * blockDim.x + threadIdx.x;
    const int64_t* first_rows = current_base + (pair_index * 2) * segment_capacity * 2;
    const int64_t* second_rows = current_base + (pair_index * 2 + 1) * segment_capacity * 2;
    const size_t first_count = current_counts[pair_index * 2];
    const size_t second_count = current_counts[pair_index * 2 + 1];
    const size_t total = first_count + second_count;
    if (index >= total)
        return;

    int64_t* pair_merged_rows = merged_rows + pair_index * output_capacity * 2;
    if (index < first_count) {
        const int64_t value0 = first_rows[index * 2];
        const int64_t value1 = first_rows[index * 2 + 1];
        const size_t output_index =
            index + collect_k_final_lower_bound(second_rows, second_count, value0, value1);
        pair_merged_rows[output_index * 2] = value0;
        pair_merged_rows[output_index * 2 + 1] = value1;
        return;
    }

    const size_t second_index = index - first_count;
    const int64_t value0 = second_rows[second_index * 2];
    const int64_t value1 = second_rows[second_index * 2 + 1];
    const size_t output_index =
        second_index + collect_k_final_upper_bound(first_rows, first_count, value0, value1);
    pair_merged_rows[output_index * 2] = value0;
    pair_merged_rows[output_index * 2 + 1] = value1;
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_final_mark_counts(
        const int64_t* merged_rows,
        size_t total_count,
        uint32_t* marks,
        uint32_t* block_counts)
{
    extern __shared__ uint32_t shared_counts[];
    const size_t index = blockIdx.x * blockDim.x + threadIdx.x;
    uint32_t mark = 0;
    if (index < total_count) {
        if (index == 0) {
            mark = 1;
        } else {
            const int64_t value0 = merged_rows[index * 2];
            const int64_t value1 = merged_rows[index * 2 + 1];
            const int64_t prev0 = merged_rows[(index - 1) * 2];
            const int64_t prev1 = merged_rows[(index - 1) * 2 + 1];
            mark = (value0 != prev0 || value1 != prev1) ? 1u : 0u;
        }
        marks[index] = mark;
    }
    shared_counts[threadIdx.x] = mark;
    __syncthreads();

    for (unsigned stride = blockDim.x / 2; stride > 0; stride >>= 1) {
        if (threadIdx.x < stride)
            shared_counts[threadIdx.x] += shared_counts[threadIdx.x + stride];
        __syncthreads();
    }
    if (threadIdx.x == 0)
        block_counts[blockIdx.x] = shared_counts[0];
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_final_mark_counts_counts(
        const int64_t* merged_rows,
        const size_t* counts,
        uint32_t* marks,
        uint32_t* block_counts)
{
    extern __shared__ uint32_t shared_counts[];
    const size_t total_count = counts[0] + counts[1];
    const size_t index = blockIdx.x * blockDim.x + threadIdx.x;
    uint32_t mark = 0;
    if (index < total_count) {
        if (index == 0) {
            mark = 1;
        } else {
            const int64_t value0 = merged_rows[index * 2];
            const int64_t value1 = merged_rows[index * 2 + 1];
            const int64_t prev0 = merged_rows[(index - 1) * 2];
            const int64_t prev1 = merged_rows[(index - 1) * 2 + 1];
            mark = (value0 != prev0 || value1 != prev1) ? 1u : 0u;
        }
        marks[index] = mark;
    }
    shared_counts[threadIdx.x] = mark;
    __syncthreads();

    for (unsigned stride = blockDim.x / 2; stride > 0; stride >>= 1) {
        if (threadIdx.x < stride)
            shared_counts[threadIdx.x] += shared_counts[threadIdx.x + stride];
        __syncthreads();
    }
    if (threadIdx.x == 0)
        block_counts[blockIdx.x] = shared_counts[0];
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_final_mark_counts_level(
        const int64_t* merged_rows,
        const size_t* first_counts,
        const size_t* second_counts,
        size_t output_capacity,
        size_t pair_count,
        uint32_t* marks,
        uint32_t* block_counts,
        size_t blocks_per_pair)
{
    extern __shared__ uint32_t shared_counts[];
    const size_t pair_index = blockIdx.x / blocks_per_pair;
    const size_t local_block = blockIdx.x - pair_index * blocks_per_pair;
    const size_t local_index = local_block * blockDim.x + threadIdx.x;
    uint32_t mark = 0;
    if (pair_index < pair_count) {
        const size_t total = first_counts[pair_index] + second_counts[pair_index];
        if (local_index < total) {
            const int64_t* pair_merged_rows = merged_rows + pair_index * output_capacity * 2;
            if (local_index == 0) {
                mark = 1;
            } else {
                const int64_t value0 = pair_merged_rows[local_index * 2];
                const int64_t value1 = pair_merged_rows[local_index * 2 + 1];
                const int64_t prev0 = pair_merged_rows[(local_index - 1) * 2];
                const int64_t prev1 = pair_merged_rows[(local_index - 1) * 2 + 1];
                mark = (value0 != prev0 || value1 != prev1) ? 1u : 0u;
            }
        }
    }

    const size_t global_index = blockIdx.x * blockDim.x + threadIdx.x;
    marks[global_index] = mark;
    shared_counts[threadIdx.x] = mark;
    __syncthreads();
    for (unsigned stride = blockDim.x / 2; stride > 0; stride >>= 1) {
        if (threadIdx.x < stride)
            shared_counts[threadIdx.x] += shared_counts[threadIdx.x + stride];
        __syncthreads();
    }
    if (threadIdx.x == 0)
        block_counts[blockIdx.x] = shared_counts[0];
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_final_mark_counts_level_counts(
        const int64_t* merged_rows,
        const size_t* current_counts,
        size_t output_capacity,
        size_t pair_count,
        uint32_t* marks,
        uint32_t* block_counts,
        size_t blocks_per_pair)
{
    extern __shared__ uint32_t shared_counts[];
    const size_t pair_index = blockIdx.x / blocks_per_pair;
    const size_t local_block = blockIdx.x - pair_index * blocks_per_pair;
    const size_t local_index = local_block * blockDim.x + threadIdx.x;
    uint32_t mark = 0;
    if (pair_index < pair_count) {
        const size_t total = current_counts[pair_index * 2] + current_counts[pair_index * 2 + 1];
        if (local_index < total) {
            const int64_t* pair_merged_rows = merged_rows + pair_index * output_capacity * 2;
            if (local_index == 0) {
                mark = 1;
            } else {
                const int64_t value0 = pair_merged_rows[local_index * 2];
                const int64_t value1 = pair_merged_rows[local_index * 2 + 1];
                const int64_t prev0 = pair_merged_rows[(local_index - 1) * 2];
                const int64_t prev1 = pair_merged_rows[(local_index - 1) * 2 + 1];
                mark = (value0 != prev0 || value1 != prev1) ? 1u : 0u;
            }
        }
    }

    const size_t global_index = blockIdx.x * blockDim.x + threadIdx.x;
    marks[global_index] = mark;
    shared_counts[threadIdx.x] = mark;
    __syncthreads();
    for (unsigned stride = blockDim.x / 2; stride > 0; stride >>= 1) {
        if (threadIdx.x < stride)
            shared_counts[threadIdx.x] += shared_counts[threadIdx.x + stride];
        __syncthreads();
    }
    if (threadIdx.x == 0)
        block_counts[blockIdx.x] = shared_counts[0];
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_final_mark_counts_level_counts_pointers(
        const int64_t* merged_rows,
        const size_t* current_counts,
        size_t output_capacity,
        size_t pair_count,
        uint32_t* marks,
        uint32_t* block_counts,
        size_t blocks_per_pair)
{
    extern __shared__ uint32_t shared_counts[];
    const size_t pair_index = blockIdx.x / blocks_per_pair;
    const size_t local_block = blockIdx.x - pair_index * blocks_per_pair;
    const size_t local_index = local_block * blockDim.x + threadIdx.x;
    uint32_t mark = 0;
    if (pair_index < pair_count) {
        const size_t total = current_counts[pair_index * 2] + current_counts[pair_index * 2 + 1];
        if (local_index < total) {
            const int64_t* pair_merged_rows = merged_rows + pair_index * output_capacity * 2;
            if (local_index == 0) {
                mark = 1;
            } else {
                const int64_t value0 = pair_merged_rows[local_index * 2];
                const int64_t value1 = pair_merged_rows[local_index * 2 + 1];
                const int64_t prev0 = pair_merged_rows[(local_index - 1) * 2];
                const int64_t prev1 = pair_merged_rows[(local_index - 1) * 2 + 1];
                mark = (value0 != prev0 || value1 != prev1) ? 1u : 0u;
            }
        }
    }

    const size_t global_index = blockIdx.x * blockDim.x + threadIdx.x;
    marks[global_index] = mark;
    shared_counts[threadIdx.x] = mark;
    __syncthreads();
    for (unsigned stride = blockDim.x / 2; stride > 0; stride >>= 1) {
        if (threadIdx.x < stride)
            shared_counts[threadIdx.x] += shared_counts[threadIdx.x + stride];
        __syncthreads();
    }
    if (threadIdx.x == 0)
        block_counts[blockIdx.x] = shared_counts[0];
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_final_materialize_mark_counts_level_counts(
        const int64_t* current_base,
        const size_t* current_counts,
        size_t segment_capacity,
        size_t output_capacity,
        int64_t* merged_rows,
        size_t pair_count,
        uint32_t* marks,
        uint32_t* block_counts,
        size_t blocks_per_pair)
{
    const size_t pair_index = blockIdx.x / blocks_per_pair;
    if (pair_index >= pair_count)
        return;

    const size_t local_block = blockIdx.x - pair_index * blocks_per_pair;
    const size_t index = local_block * blockDim.x + threadIdx.x;
    const int64_t* first_rows = current_base + (pair_index * 2) * segment_capacity * 2;
    const int64_t* second_rows = current_base + (pair_index * 2 + 1) * segment_capacity * 2;
    const size_t first_count = current_counts[pair_index * 2];
    const size_t second_count = current_counts[pair_index * 2 + 1];
    const size_t total = first_count + second_count;
    if (index >= total)
        return;

    int64_t value0 = 0;
    int64_t value1 = 0;
    int64_t prev0 = 0;
    int64_t prev1 = 0;
    bool has_prev = false;
    size_t output_index = 0;

    if (index < first_count) {
        value0 = first_rows[index * 2];
        value1 = first_rows[index * 2 + 1];
        const size_t less_second = collect_k_final_lower_bound(second_rows, second_count, value0, value1);
        output_index = index + less_second;

        if (index > 0) {
            prev0 = first_rows[(index - 1) * 2];
            prev1 = first_rows[(index - 1) * 2 + 1];
            has_prev = true;
        }
        if (less_second > 0) {
            const int64_t candidate0 = second_rows[(less_second - 1) * 2];
            const int64_t candidate1 = second_rows[(less_second - 1) * 2 + 1];
            if (!has_prev || collect_k_final_pair_compare(prev0, prev1, candidate0, candidate1) < 0) {
                prev0 = candidate0;
                prev1 = candidate1;
                has_prev = true;
            }
        }
    } else {
        const size_t second_index = index - first_count;
        value0 = second_rows[second_index * 2];
        value1 = second_rows[second_index * 2 + 1];
        const size_t le_first = collect_k_final_upper_bound(first_rows, first_count, value0, value1);
        output_index = second_index + le_first;

        if (second_index > 0) {
            prev0 = second_rows[(second_index - 1) * 2];
            prev1 = second_rows[(second_index - 1) * 2 + 1];
            has_prev = true;
        }
        if (le_first > 0) {
            const int64_t candidate0 = first_rows[(le_first - 1) * 2];
            const int64_t candidate1 = first_rows[(le_first - 1) * 2 + 1];
            if (!has_prev || collect_k_final_pair_compare(prev0, prev1, candidate0, candidate1) < 0) {
                prev0 = candidate0;
                prev1 = candidate1;
                has_prev = true;
            }
        }
    }

    if (output_index >= output_capacity)
        return;

    int64_t* pair_merged_rows = merged_rows + pair_index * output_capacity * 2;
    pair_merged_rows[output_index * 2] = value0;
    pair_merged_rows[output_index * 2 + 1] = value1;

    const uint32_t mark =
        (!has_prev || value0 != prev0 || value1 != prev1) ? 1u : 0u;
    const size_t output_block = output_index / blockDim.x;
    const size_t global_output_index =
        (pair_index * blocks_per_pair + output_block) * blockDim.x + (output_index % blockDim.x);
    marks[global_output_index] = mark;
    if (mark)
        atomicAdd(&block_counts[pair_index * blocks_per_pair + output_block], 1u);
}

__device__ size_t collect_k_final_stable_partition(
        const int64_t* first_rows,
        size_t first_count,
        const int64_t* second_rows,
        size_t second_count,
        size_t output_index)
{
    size_t low = output_index > second_count ? output_index - second_count : 0;
    size_t high = output_index < first_count ? output_index : first_count;
    while (low <= high) {
        const size_t first_take = low + (high - low) / 2;
        const size_t second_take = output_index - first_take;
        const bool too_many_first =
            first_take > 0 && second_take < second_count &&
            collect_k_final_pair_compare(
                first_rows[(first_take - 1) * 2],
                first_rows[(first_take - 1) * 2 + 1],
                second_rows[second_take * 2],
                second_rows[second_take * 2 + 1]) > 0;
        const bool too_few_first =
            second_take > 0 && first_take < first_count &&
            collect_k_final_pair_compare(
                second_rows[(second_take - 1) * 2],
                second_rows[(second_take - 1) * 2 + 1],
                first_rows[first_take * 2],
                first_rows[first_take * 2 + 1]) >= 0;
        if (too_many_first) {
            if (first_take == 0)
                return 0;
            high = first_take - 1;
        } else if (too_few_first) {
            low = first_take + 1;
        } else {
            return first_take;
        }
    }
    return low;
}

__device__ void collect_k_final_select_stable_output(
        const int64_t* first_rows,
        size_t first_count,
        const int64_t* second_rows,
        size_t second_count,
        size_t output_index,
        int64_t* value0,
        int64_t* value1)
{
    const size_t first_take =
        collect_k_final_stable_partition(first_rows, first_count, second_rows, second_count, output_index);
    const size_t second_take = output_index - first_take;
    if (first_take < first_count &&
        (second_take >= second_count ||
         collect_k_final_pair_compare(
             first_rows[first_take * 2],
             first_rows[first_take * 2 + 1],
             second_rows[second_take * 2],
             second_rows[second_take * 2 + 1]) <= 0)) {
        *value0 = first_rows[first_take * 2];
        *value1 = first_rows[first_take * 2 + 1];
        return;
    }
    *value0 = second_rows[second_take * 2];
    *value1 = second_rows[second_take * 2 + 1];
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_final_output_indexed_materialize_mark_counts_level_counts(
        const int64_t* current_base,
        const size_t* current_counts,
        size_t segment_capacity,
        size_t output_capacity,
        int64_t* merged_rows,
        size_t pair_count,
        uint32_t* marks,
        uint32_t* block_counts,
        size_t blocks_per_pair)
{
    extern __shared__ uint32_t shared_counts[];
    const size_t pair_index = blockIdx.x / blocks_per_pair;
    const size_t local_block = blockIdx.x - pair_index * blocks_per_pair;
    const size_t local_index = local_block * blockDim.x + threadIdx.x;
    uint32_t mark = 0;

    if (pair_index < pair_count) {
        const int64_t* first_rows = current_base + (pair_index * 2) * segment_capacity * 2;
        const int64_t* second_rows = current_base + (pair_index * 2 + 1) * segment_capacity * 2;
        const size_t first_count = current_counts[pair_index * 2];
        const size_t second_count = current_counts[pair_index * 2 + 1];
        const size_t total = first_count + second_count;
        if (local_index < total && local_index < output_capacity) {
            int64_t value0 = 0;
            int64_t value1 = 0;
            collect_k_final_select_stable_output(
                first_rows, first_count, second_rows, second_count, local_index, &value0, &value1);
            int64_t* pair_merged_rows = merged_rows + pair_index * output_capacity * 2;
            pair_merged_rows[local_index * 2] = value0;
            pair_merged_rows[local_index * 2 + 1] = value1;
            if (local_index == 0) {
                mark = 1;
            } else {
                int64_t prev0 = 0;
                int64_t prev1 = 0;
                collect_k_final_select_stable_output(
                    first_rows, first_count, second_rows, second_count, local_index - 1, &prev0, &prev1);
                mark = (value0 != prev0 || value1 != prev1) ? 1u : 0u;
            }
        }
    }

    const size_t global_index = blockIdx.x * blockDim.x + threadIdx.x;
    marks[global_index] = mark;
    shared_counts[threadIdx.x] = mark;
    __syncthreads();
    for (unsigned stride = blockDim.x / 2; stride > 0; stride >>= 1) {
        if (threadIdx.x < stride)
            shared_counts[threadIdx.x] += shared_counts[threadIdx.x + stride];
        __syncthreads();
    }
    if (threadIdx.x == 0)
        block_counts[blockIdx.x] = shared_counts[0];
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_four_way_materialize_mark_counts_derived(
        const int64_t* current_base,
        const size_t* current_counts,
        size_t segment_capacity,
        size_t output_capacity,
        int64_t* merged_rows,
        size_t group_count,
        uint32_t* marks,
        uint32_t* block_counts,
        size_t blocks_per_group)
{
    const size_t group_index = blockIdx.x / blocks_per_group;
    if (group_index >= group_count)
        return;

    const size_t local_block = blockIdx.x - group_index * blocks_per_group;
    const size_t raw_index = local_block * blockDim.x + threadIdx.x;
    const size_t segment_slot = raw_index / segment_capacity;
    if (segment_slot >= 4)
        return;

    const size_t local_index = raw_index - segment_slot * segment_capacity;
    const size_t segment_base = group_index * 4;
    const size_t own_count = current_counts[segment_base + segment_slot];
    if (local_index >= own_count)
        return;

    const int64_t* own_rows =
        current_base + (segment_base + segment_slot) * segment_capacity * 2;
    const int64_t value0 = own_rows[local_index * 2];
    const int64_t value1 = own_rows[local_index * 2 + 1];

    size_t output_index = local_index;
    bool has_prior_duplicate = false;
    if (local_index > 0) {
        const int64_t prev0 = own_rows[(local_index - 1) * 2];
        const int64_t prev1 = own_rows[(local_index - 1) * 2 + 1];
        has_prior_duplicate = (prev0 == value0 && prev1 == value1);
    }

    for (size_t peer_slot = 0; peer_slot < 4; ++peer_slot) {
        if (peer_slot == segment_slot)
            continue;
        const int64_t* peer_rows =
            current_base + (segment_base + peer_slot) * segment_capacity * 2;
        const size_t peer_count = current_counts[segment_base + peer_slot];
        const size_t lower =
            collect_k_final_lower_bound(peer_rows, peer_count, value0, value1);
        const size_t upper =
            collect_k_final_upper_bound(peer_rows, peer_count, value0, value1);
        output_index += peer_slot < segment_slot ? upper : lower;
        if (peer_slot < segment_slot && lower < upper)
            has_prior_duplicate = true;
    }

    if (output_index >= output_capacity)
        return;

    int64_t* group_merged_rows =
        merged_rows + group_index * output_capacity * 2;
    group_merged_rows[output_index * 2] = value0;
    group_merged_rows[output_index * 2 + 1] = value1;

    const uint32_t mark = has_prior_duplicate ? 0u : 1u;
    const size_t output_block = output_index / blockDim.x;
    const size_t global_output_index =
        (group_index * blocks_per_group + output_block) * blockDim.x + (output_index % blockDim.x);
    marks[global_output_index] = mark;
    if (mark)
        atomicAdd(&block_counts[group_index * blocks_per_group + output_block], 1u);
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_final_compact(
        const int64_t* merged_rows,
        const uint32_t* marks,
        const uint32_t* block_offsets,
        size_t total_count,
        int64_t* rows_out,
        size_t row_capacity)
{
    extern __shared__ uint32_t shared_marks[];
    const size_t index = blockIdx.x * blockDim.x + threadIdx.x;
    const uint32_t mark = index < total_count ? marks[index] : 0u;
    shared_marks[threadIdx.x] = mark;
    __syncthreads();

    for (unsigned offset = 1; offset < blockDim.x; offset <<= 1) {
        const uint32_t value = threadIdx.x >= offset ? shared_marks[threadIdx.x - offset] : 0u;
        __syncthreads();
        shared_marks[threadIdx.x] += value;
        __syncthreads();
    }

    if (index < total_count && mark) {
        const size_t output_index =
            static_cast<size_t>(block_offsets[blockIdx.x]) + shared_marks[threadIdx.x] - 1u;
        if (output_index < row_capacity) {
            rows_out[output_index * 2] = merged_rows[index * 2];
            rows_out[output_index * 2 + 1] = merged_rows[index * 2 + 1];
        }
    }
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_final_compact_counts(
        const int64_t* merged_rows,
        const uint32_t* marks,
        const uint32_t* block_offsets,
        const size_t* counts,
        int64_t* rows_out,
        size_t row_capacity)
{
    extern __shared__ uint32_t shared_marks[];
    const size_t total_count = counts[0] + counts[1];
    const size_t index = blockIdx.x * blockDim.x + threadIdx.x;
    const uint32_t mark = index < total_count ? marks[index] : 0u;
    shared_marks[threadIdx.x] = mark;
    __syncthreads();

    for (unsigned offset = 1; offset < blockDim.x; offset <<= 1) {
        const uint32_t value = threadIdx.x >= offset ? shared_marks[threadIdx.x - offset] : 0u;
        __syncthreads();
        shared_marks[threadIdx.x] += value;
        __syncthreads();
    }

    if (index < total_count && mark) {
        const size_t output_index =
            static_cast<size_t>(block_offsets[blockIdx.x]) + shared_marks[threadIdx.x] - 1u;
        if (output_index < row_capacity) {
            rows_out[output_index * 2] = merged_rows[index * 2];
            rows_out[output_index * 2 + 1] = merged_rows[index * 2 + 1];
        }
    }
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_final_compact_level(
        const int64_t* merged_rows,
        const uint32_t* marks,
        const uint32_t* block_offsets,
        const uint32_t* pair_offsets,
        const uint64_t* output_row_ptrs,
        size_t output_capacity,
        size_t pair_count,
        size_t blocks_per_pair)
{
    extern __shared__ uint32_t shared_marks[];
    const size_t pair_index = blockIdx.x / blocks_per_pair;
    if (pair_index >= pair_count)
        return;
    const size_t local_block = blockIdx.x - pair_index * blocks_per_pair;
    const size_t local_index = local_block * blockDim.x + threadIdx.x;
    if (local_index >= output_capacity)
        return;

    const size_t global_index = blockIdx.x * blockDim.x + threadIdx.x;
    const uint32_t mark = marks[global_index];
    shared_marks[threadIdx.x] = mark;
    __syncthreads();
    for (unsigned offset = 1; offset < blockDim.x; offset <<= 1) {
        const uint32_t value = threadIdx.x >= offset ? shared_marks[threadIdx.x - offset] : 0u;
        __syncthreads();
        shared_marks[threadIdx.x] += value;
        __syncthreads();
    }

    if (mark) {
        const size_t output_index =
            static_cast<size_t>(block_offsets[blockIdx.x] + shared_marks[threadIdx.x] - 1u - pair_offsets[pair_index]);
        int64_t* rows_out =
            reinterpret_cast<int64_t*>(static_cast<uintptr_t>(output_row_ptrs[pair_index]));
        const int64_t* pair_merged_rows = merged_rows + pair_index * output_capacity * 2;
        rows_out[output_index * 2] = pair_merged_rows[local_index * 2];
        rows_out[output_index * 2 + 1] = pair_merged_rows[local_index * 2 + 1];
    }
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_final_compact_level_derived(
        const int64_t* merged_rows,
        const uint32_t* marks,
        const uint32_t* block_offsets,
        const uint32_t* pair_offsets,
        int64_t* output_base,
        size_t output_capacity,
        size_t pair_count,
        size_t blocks_per_pair)
{
    extern __shared__ uint32_t shared_marks[];
    const size_t pair_index = blockIdx.x / blocks_per_pair;
    if (pair_index >= pair_count)
        return;
    const size_t local_block = blockIdx.x - pair_index * blocks_per_pair;
    const size_t local_index = local_block * blockDim.x + threadIdx.x;
    if (local_index >= output_capacity)
        return;

    const size_t global_index = blockIdx.x * blockDim.x + threadIdx.x;
    const uint32_t mark = marks[global_index];
    shared_marks[threadIdx.x] = mark;
    __syncthreads();
    for (unsigned offset = 1; offset < blockDim.x; offset <<= 1) {
        const uint32_t value = threadIdx.x >= offset ? shared_marks[threadIdx.x - offset] : 0u;
        __syncthreads();
        shared_marks[threadIdx.x] += value;
        __syncthreads();
    }

    if (mark) {
        const size_t output_index =
            static_cast<size_t>(block_offsets[blockIdx.x] + shared_marks[threadIdx.x] - 1u - pair_offsets[pair_index]);
        int64_t* rows_out = output_base + pair_index * output_capacity * 2;
        const int64_t* pair_merged_rows = merged_rows + pair_index * output_capacity * 2;
        rows_out[output_index * 2] = pair_merged_rows[local_index * 2];
        rows_out[output_index * 2 + 1] = pair_merged_rows[local_index * 2 + 1];
    }
}

extern "C" __global__ void collect_k_bounded_i64_row_width2_final_prefix_offsets_level(
        const uint32_t* block_counts,
        size_t pair_count,
        size_t blocks_per_pair,
        uint32_t* block_offsets,
        uint32_t* pair_offsets,
        size_t* pair_counts)
{
    const size_t pair_index = blockIdx.x;
    if (pair_index >= pair_count || threadIdx.x != 0)
        return;

    uint32_t running_total = 0;
    for (size_t block_index = 0; block_index < blocks_per_pair; ++block_index) {
        const size_t global_block = pair_index * blocks_per_pair + block_index;
        block_offsets[global_block] = running_total;
        running_total += block_counts[global_block];
    }
    // Offsets are local to each pair in this path; the existing compact kernel
    // subtracts pair_offsets[pair_index], so keep the pair base at zero.
    pair_offsets[pair_index] = 0;
    pair_counts[pair_index] = static_cast<size_t>(running_total);
}
)CUDA";

static const char* kFixedRadiusNeighbors3DKernelSrc = R"CUDA(
#include <stdint.h>
#include <math.h>
#include <float.h>

struct GpuPoint3D { float x, y, z; uint32_t id; };
struct FrnRecord { uint32_t query_id, neighbor_id; float distance; };

extern "C" __global__ void fixed_radius_neighbors_3d(
        const GpuPoint3D* query_points,
        uint32_t          query_count,
        const GpuPoint3D* search_points,
        uint32_t          search_count,
        float             radius,
        uint32_t          k_max,
        FrnRecord*        output)
{
    const uint32_t qidx = blockIdx.x * blockDim.x + threadIdx.x;
    if (qidx >= query_count) return;

    FrnRecord* query_out = output + static_cast<size_t>(qidx) * static_cast<size_t>(k_max);
    for (uint32_t slot = 0; slot < k_max; ++slot) {
        query_out[slot].query_id = query_points[qidx].id;
        query_out[slot].neighbor_id = 0xffffffffu;
        query_out[slot].distance = INFINITY;
    }

    const float px = query_points[qidx].x;
    const float py = query_points[qidx].y;
    const float pz = query_points[qidx].z;
    const float radius_sq = radius * radius;

    for (uint32_t sidx = 0; sidx < search_count; ++sidx) {
        const float dx = search_points[sidx].x - px;
        const float dy = search_points[sidx].y - py;
        const float dz = search_points[sidx].z - pz;
        const float distance_sq = dx * dx + dy * dy + dz * dz;
        if (distance_sq > radius_sq) {
            continue;
        }
        const float distance = sqrtf(distance_sq);
        const uint32_t neighbor_id = search_points[sidx].id;

        uint32_t insert_at = k_max;
        for (uint32_t slot = 0; slot < k_max; ++slot) {
            const bool empty = query_out[slot].neighbor_id == 0xffffffffu;
            const bool better_distance = distance < query_out[slot].distance - 1.0e-7f;
            const bool same_distance = fabsf(distance - query_out[slot].distance) <= 1.0e-7f;
            const bool better_id = same_distance && neighbor_id < query_out[slot].neighbor_id;
            if (empty || better_distance || better_id) {
                insert_at = slot;
                break;
            }
        }
        if (insert_at == k_max) {
            continue;
        }
        for (uint32_t slot = k_max - 1; slot > insert_at; --slot) {
            query_out[slot] = query_out[slot - 1];
        }
        query_out[insert_at].query_id = query_points[qidx].id;
        query_out[insert_at].neighbor_id = neighbor_id;
        query_out[insert_at].distance = distance;
    }
}
)CUDA";

static const char* kFixedRadiusNeighbors3DRtKernelSrc = R"CUDA(
#include <optix_device.h>
#include <stdint.h>
#include <math.h>
#include <float.h>

typedef unsigned int uint32_t;

struct GpuPoint3D { float x, y, z; uint32_t id; };
struct FrnRecord { uint32_t query_id, neighbor_id; float distance; };

struct FixedRadiusNeighbors3DRtParams {
    OptixTraversableHandle traversable;
    const GpuPoint3D* query_points;
    const GpuPoint3D* search_points;
    FrnRecord* output;
    uint32_t query_count;
    uint32_t k_max;
    float radius;
    float trace_tmax;
};

extern "C" {
__constant__ FixedRadiusNeighbors3DRtParams params;
}

extern "C" __global__ void __raygen__frn3d_probe() {
    const uint32_t qidx = optixGetLaunchIndex().x;
    if (qidx >= params.query_count) return;

    const GpuPoint3D q = params.query_points[qidx];
    FrnRecord* query_out = params.output + static_cast<unsigned long long>(qidx) * static_cast<unsigned long long>(params.k_max);
    for (uint32_t slot = 0; slot < params.k_max; ++slot) {
        query_out[slot].query_id = q.id;
        query_out[slot].neighbor_id = 0xffffffffu;
        query_out[slot].distance = INFINITY;
    }

    unsigned int p0 = qidx;
    optixTrace(params.traversable,
               make_float3(q.x, q.y, q.z),
               make_float3(1.0f, 0.0f, 0.0f),
               0.0f, params.trace_tmax, 0.0f,
               OptixVisibilityMask(255),
               OPTIX_RAY_FLAG_NONE,
               0, 1, 0,
               p0);
}

extern "C" __global__ void __miss__frn3d_miss() {}

extern "C" __global__ void __intersection__frn3d_isect() {
    const uint32_t prim = optixGetPrimitiveIndex();
    const uint32_t qidx = optixGetPayload_0();
    const GpuPoint3D q = params.query_points[qidx];
    const GpuPoint3D t = params.search_points[prim];
    const float dx = t.x - q.x;
    const float dy = t.y - q.y;
    const float dz = t.z - q.z;
    const float d2 = dx * dx + dy * dy + dz * dz;
    const float radius_sq = params.radius * params.radius;
    if (d2 > radius_sq) {
        return;
    }
    optixReportIntersection(params.radius, 0u);
}

extern "C" __global__ void __anyhit__frn3d_anyhit() {
    const uint32_t prim = optixGetPrimitiveIndex();
    const uint32_t qidx = optixGetPayload_0();
    const GpuPoint3D q = params.query_points[qidx];
    const GpuPoint3D t = params.search_points[prim];
    const float dx = t.x - q.x;
    const float dy = t.y - q.y;
    const float dz = t.z - q.z;
    const float d2 = dx * dx + dy * dy + dz * dz;
    const float distance = sqrtf(d2);
    FrnRecord* query_out = params.output + static_cast<unsigned long long>(qidx) * static_cast<unsigned long long>(params.k_max);

    uint32_t insert_at = params.k_max;
    for (uint32_t slot = 0; slot < params.k_max; ++slot) {
        const bool empty = query_out[slot].neighbor_id == 0xffffffffu;
        const bool better_distance = distance < query_out[slot].distance - 1.0e-7f;
        const bool same_distance = fabsf(distance - query_out[slot].distance) <= 1.0e-7f;
        const bool better_id = same_distance && t.id < query_out[slot].neighbor_id;
        if (empty || better_distance || better_id) {
            insert_at = slot;
            break;
        }
    }
    if (insert_at < params.k_max) {
        for (uint32_t slot = params.k_max - 1u; slot > insert_at; --slot) {
            query_out[slot] = query_out[slot - 1u];
        }
        query_out[insert_at].query_id = q.id;
        query_out[insert_at].neighbor_id = t.id;
        query_out[insert_at].distance = distance;
    }
    optixIgnoreIntersection();
}
)CUDA";

static const char* kFixedRadiusNeighbors3DGridKernelSrc = R"CUDA(
#include <stdint.h>

typedef unsigned int uint32_t;

struct GpuPoint3D { float x, y, z; uint32_t id; };
struct ExactPoint3D { uint32_t id; double x, y, z; };
struct FrnRecord { uint32_t query_id, neighbor_id; float distance; };
struct FrnSummary { unsigned long long count; double min_distance; double max_distance; double sum_distance; };

static __device__ __forceinline__ float abs_float(float value)
{
    return value < 0.0f ? -value : value;
}

static __device__ __forceinline__ int floor_to_int_float(float value)
{
    int raw = static_cast<int>(value);
    if (static_cast<float>(raw) > value) {
        raw -= 1;
    }
    return raw;
}

static __device__ __forceinline__ int floor_to_int_exact(double value)
{
    long long raw = static_cast<long long>(value);
    if (static_cast<double>(raw) > value) {
        raw -= 1ll;
    }
    return static_cast<int>(raw);
}

static __device__ __forceinline__ void insert_neighbor(
        FrnRecord* query_out,
        uint32_t k_max,
        uint32_t* count,
        uint32_t query_id,
        uint32_t neighbor_id,
        float distance)
{
    uint32_t insert_at = k_max;
    const uint32_t used = *count < k_max ? *count : k_max;
    for (uint32_t slot = 0; slot < used; ++slot) {
        const bool better_distance = distance < query_out[slot].distance - 1.0e-7f;
        const bool same_distance = abs_float(distance - query_out[slot].distance) <= 1.0e-7f;
        const bool better_id = same_distance && neighbor_id < query_out[slot].neighbor_id;
        if (better_distance || better_id) {
            insert_at = slot;
            break;
        }
    }
    if (insert_at == k_max && used < k_max) {
        insert_at = used;
    }
    if (insert_at == k_max) {
        return;
    }
    const uint32_t last_slot = used < k_max ? used : (k_max - 1u);
    for (uint32_t slot = last_slot; slot > insert_at; --slot) {
        query_out[slot] = query_out[slot - 1u];
    }
    query_out[insert_at].query_id = query_id;
    query_out[insert_at].neighbor_id = neighbor_id;
    query_out[insert_at].distance = distance;
    if (*count < k_max) {
        *count += 1u;
    }
}

extern "C" __global__ void fixed_radius_neighbors_3d_grid(
        const GpuPoint3D* query_points,
        uint32_t query_count,
        const GpuPoint3D* sorted_search_points,
        const uint32_t* cell_offsets,
        uint32_t grid_x,
        uint32_t grid_y,
        uint32_t grid_z,
        float min_x,
        float min_y,
        float min_z,
        float inv_cell_size,
        float radius,
        uint32_t k_max,
        uint32_t* counts_out,
        FrnRecord* output)
{
    const uint32_t qidx = blockIdx.x * blockDim.x + threadIdx.x;
    if (qidx >= query_count) return;

    const GpuPoint3D q = query_points[qidx];
    FrnRecord* query_out = output + static_cast<unsigned long long>(qidx) * static_cast<unsigned long long>(k_max);
    uint32_t count = 0u;

    const int cx = floor_to_int_float((q.x - min_x) * inv_cell_size);
    const int cy = floor_to_int_float((q.y - min_y) * inv_cell_size);
    const int cz = floor_to_int_float((q.z - min_z) * inv_cell_size);
    const float radius_sq = radius * radius;

    for (int dz = -1; dz <= 1; ++dz) {
        const int gz_i = cz + dz;
        if (gz_i < 0 || gz_i >= static_cast<int>(grid_z)) continue;
        const uint32_t gz_u = static_cast<uint32_t>(gz_i);
        for (int dy = -1; dy <= 1; ++dy) {
            const int gy_i = cy + dy;
            if (gy_i < 0 || gy_i >= static_cast<int>(grid_y)) continue;
            const uint32_t gy_u = static_cast<uint32_t>(gy_i);
            for (int dx_cell = -1; dx_cell <= 1; ++dx_cell) {
                const int gx_i = cx + dx_cell;
                if (gx_i < 0 || gx_i >= static_cast<int>(grid_x)) continue;
                const uint32_t gx_u = static_cast<uint32_t>(gx_i);
                const uint32_t cell = (gz_u * grid_y + gy_u) * grid_x + gx_u;
                const uint32_t begin = cell_offsets[cell];
                const uint32_t end = cell_offsets[cell + 1u];
                for (uint32_t pos = begin; pos < end; ++pos) {
                    const GpuPoint3D t = sorted_search_points[pos];
                    const float sx = t.x - q.x;
                    const float sy = t.y - q.y;
                    const float sz = t.z - q.z;
                    const float d2 = sx * sx + sy * sy + sz * sz;
                    if (d2 > radius_sq) continue;
                    insert_neighbor(query_out, k_max, &count, q.id, t.id, sqrtf(d2));
                }
            }
        }
    }
    counts_out[qidx] = count;
}

extern "C" __global__ void fixed_radius_neighbors_3d_grid_count(
        const GpuPoint3D* query_points,
        uint32_t query_count,
        const GpuPoint3D* sorted_search_points,
        const uint32_t* cell_offsets,
        uint32_t grid_x,
        uint32_t grid_y,
        uint32_t grid_z,
        float min_x,
        float min_y,
        float min_z,
        float inv_cell_size,
        float radius,
        uint32_t k_max,
        uint32_t* counts_out)
{
    const uint32_t qidx = blockIdx.x * blockDim.x + threadIdx.x;
    if (qidx >= query_count) return;

    const GpuPoint3D q = query_points[qidx];
    const int cx = floor_to_int_float((q.x - min_x) * inv_cell_size);
    const int cy = floor_to_int_float((q.y - min_y) * inv_cell_size);
    const int cz = floor_to_int_float((q.z - min_z) * inv_cell_size);
    const float radius_sq = radius * radius;
    uint32_t count = 0u;

    for (int dz = -1; dz <= 1 && count < k_max; ++dz) {
        const int gz_i = cz + dz;
        if (gz_i < 0 || gz_i >= static_cast<int>(grid_z)) continue;
        const uint32_t gz_u = static_cast<uint32_t>(gz_i);
        for (int dy = -1; dy <= 1 && count < k_max; ++dy) {
            const int gy_i = cy + dy;
            if (gy_i < 0 || gy_i >= static_cast<int>(grid_y)) continue;
            const uint32_t gy_u = static_cast<uint32_t>(gy_i);
            for (int dx_cell = -1; dx_cell <= 1 && count < k_max; ++dx_cell) {
                const int gx_i = cx + dx_cell;
                if (gx_i < 0 || gx_i >= static_cast<int>(grid_x)) continue;
                const uint32_t gx_u = static_cast<uint32_t>(gx_i);
                const uint32_t cell = (gz_u * grid_y + gy_u) * grid_x + gx_u;
                const uint32_t begin = cell_offsets[cell];
                const uint32_t end = cell_offsets[cell + 1u];
                for (uint32_t pos = begin; pos < end && count < k_max; ++pos) {
                    const GpuPoint3D t = sorted_search_points[pos];
                    const float sx = t.x - q.x;
                    const float sy = t.y - q.y;
                    const float sz = t.z - q.z;
                    const float d2 = sx * sx + sy * sy + sz * sz;
                    if (d2 <= radius_sq) {
                        count += 1u;
                    }
                }
            }
        }
    }
    counts_out[qidx] = count;
}

extern "C" __global__ void fixed_radius_neighbors_3d_grid_exact_count(
        const ExactPoint3D* query_points,
        uint32_t query_count,
        const ExactPoint3D* sorted_search_points,
        const uint32_t* cell_offsets,
        uint32_t grid_x,
        uint32_t grid_y,
        uint32_t grid_z,
        double min_x,
        double min_y,
        double min_z,
        double inv_cell_size,
        double radius,
        uint32_t k_max,
        uint32_t* counts_out)
{
    const uint32_t qidx = blockIdx.x * blockDim.x + threadIdx.x;
    if (qidx >= query_count) return;

    const ExactPoint3D q = query_points[qidx];
    const int cx = floor_to_int_exact((q.x - min_x) * inv_cell_size);
    const int cy = floor_to_int_exact((q.y - min_y) * inv_cell_size);
    const int cz = floor_to_int_exact((q.z - min_z) * inv_cell_size);
    const double radius_sq = radius * radius;
    uint32_t count = 0u;

    for (int dz = -1; dz <= 1 && count < k_max; ++dz) {
        const int gz_i = cz + dz;
        if (gz_i < 0 || gz_i >= static_cast<int>(grid_z)) continue;
        const uint32_t gz_u = static_cast<uint32_t>(gz_i);
        for (int dy = -1; dy <= 1 && count < k_max; ++dy) {
            const int gy_i = cy + dy;
            if (gy_i < 0 || gy_i >= static_cast<int>(grid_y)) continue;
            const uint32_t gy_u = static_cast<uint32_t>(gy_i);
            for (int dx_cell = -1; dx_cell <= 1 && count < k_max; ++dx_cell) {
                const int gx_i = cx + dx_cell;
                if (gx_i < 0 || gx_i >= static_cast<int>(grid_x)) continue;
                const uint32_t gx_u = static_cast<uint32_t>(gx_i);
                const uint32_t cell = (gz_u * grid_y + gy_u) * grid_x + gx_u;
                const uint32_t begin = cell_offsets[cell];
                const uint32_t end = cell_offsets[cell + 1u];
                for (uint32_t pos = begin; pos < end && count < k_max; ++pos) {
                    const ExactPoint3D t = sorted_search_points[pos];
                    const double sx = t.x - q.x;
                    const double sy = t.y - q.y;
                    const double sz = t.z - q.z;
                    const double d2 = sx * sx + sy * sy + sz * sz;
                    if (d2 <= radius_sq) {
                        count += 1u;
                    }
                }
            }
        }
    }
    counts_out[qidx] = count;
}

extern "C" __global__ void fixed_radius_neighbors_3d_grid_exact_summary(
        const ExactPoint3D* query_points,
        uint32_t query_count,
        const ExactPoint3D* sorted_search_points,
        const uint32_t* cell_offsets,
        uint32_t grid_x,
        uint32_t grid_y,
        uint32_t grid_z,
        double min_x,
        double min_y,
        double min_z,
        double inv_cell_size,
        double radius,
        uint32_t k_max,
        FrnSummary* summaries_out)
{
    const uint32_t qidx = blockIdx.x * blockDim.x + threadIdx.x;
    if (qidx >= query_count) return;

    const ExactPoint3D q = query_points[qidx];
    const int cx = floor_to_int_exact((q.x - min_x) * inv_cell_size);
    const int cy = floor_to_int_exact((q.y - min_y) * inv_cell_size);
    const int cz = floor_to_int_exact((q.z - min_z) * inv_cell_size);
    const double radius_sq = radius * radius;
    uint32_t count = 0u;
    double min_distance = 0.0;
    double max_distance = 0.0;
    double sum_distance = 0.0;

    for (int dz = -1; dz <= 1 && count < k_max; ++dz) {
        const int gz_i = cz + dz;
        if (gz_i < 0 || gz_i >= static_cast<int>(grid_z)) continue;
        const uint32_t gz_u = static_cast<uint32_t>(gz_i);
        for (int dy = -1; dy <= 1 && count < k_max; ++dy) {
            const int gy_i = cy + dy;
            if (gy_i < 0 || gy_i >= static_cast<int>(grid_y)) continue;
            const uint32_t gy_u = static_cast<uint32_t>(gy_i);
            for (int dx_cell = -1; dx_cell <= 1 && count < k_max; ++dx_cell) {
                const int gx_i = cx + dx_cell;
                if (gx_i < 0 || gx_i >= static_cast<int>(grid_x)) continue;
                const uint32_t gx_u = static_cast<uint32_t>(gx_i);
                const uint32_t cell = (gz_u * grid_y + gy_u) * grid_x + gx_u;
                const uint32_t begin = cell_offsets[cell];
                const uint32_t end = cell_offsets[cell + 1u];
                for (uint32_t pos = begin; pos < end && count < k_max; ++pos) {
                    const ExactPoint3D t = sorted_search_points[pos];
                    const double sx = t.x - q.x;
                    const double sy = t.y - q.y;
                    const double sz = t.z - q.z;
                    const double d2 = sx * sx + sy * sy + sz * sz;
                    if (d2 > radius_sq) continue;
                    const double distance = sqrt(d2);
                    if (count == 0u || distance < min_distance) {
                        min_distance = distance;
                    }
                    if (count == 0u || distance > max_distance) {
                        max_distance = distance;
                    }
                    sum_distance += distance;
                    count += 1u;
                }
            }
        }
    }
    FrnSummary summary;
    summary.count = static_cast<unsigned long long>(count);
    summary.min_distance = min_distance;
    summary.max_distance = max_distance;
    summary.sum_distance = sum_distance;
    summaries_out[qidx] = summary;
}

extern "C" __global__ void fixed_radius_neighbors_3d_grid_compact(
        const GpuPoint3D* query_points,
        uint32_t query_count,
        const GpuPoint3D* sorted_search_points,
        const uint32_t* cell_offsets,
        const uint32_t* row_offsets,
        uint32_t grid_x,
        uint32_t grid_y,
        uint32_t grid_z,
        float min_x,
        float min_y,
        float min_z,
        float inv_cell_size,
        float radius,
        uint32_t k_max,
        FrnRecord* output)
{
    const uint32_t qidx = blockIdx.x * blockDim.x + threadIdx.x;
    if (qidx >= query_count) return;

    const uint32_t row_begin = row_offsets[qidx];
    const uint32_t row_end = row_offsets[qidx + 1u];
    const uint32_t capacity = row_end - row_begin;
    if (capacity == 0u) return;

    const GpuPoint3D q = query_points[qidx];
    FrnRecord* query_out = output + row_begin;
    uint32_t count = 0u;
    const int cx = floor_to_int_float((q.x - min_x) * inv_cell_size);
    const int cy = floor_to_int_float((q.y - min_y) * inv_cell_size);
    const int cz = floor_to_int_float((q.z - min_z) * inv_cell_size);
    const float radius_sq = radius * radius;

    for (int dz = -1; dz <= 1; ++dz) {
        const int gz_i = cz + dz;
        if (gz_i < 0 || gz_i >= static_cast<int>(grid_z)) continue;
        const uint32_t gz_u = static_cast<uint32_t>(gz_i);
        for (int dy = -1; dy <= 1; ++dy) {
            const int gy_i = cy + dy;
            if (gy_i < 0 || gy_i >= static_cast<int>(grid_y)) continue;
            const uint32_t gy_u = static_cast<uint32_t>(gy_i);
            for (int dx_cell = -1; dx_cell <= 1; ++dx_cell) {
                const int gx_i = cx + dx_cell;
                if (gx_i < 0 || gx_i >= static_cast<int>(grid_x)) continue;
                const uint32_t gx_u = static_cast<uint32_t>(gx_i);
                const uint32_t cell = (gz_u * grid_y + gy_u) * grid_x + gx_u;
                const uint32_t begin = cell_offsets[cell];
                const uint32_t end = cell_offsets[cell + 1u];
                for (uint32_t pos = begin; pos < end; ++pos) {
                    const GpuPoint3D t = sorted_search_points[pos];
                    const float sx = t.x - q.x;
                    const float sy = t.y - q.y;
                    const float sz = t.z - q.z;
                    const float d2 = sx * sx + sy * sy + sz * sz;
                    if (d2 > radius_sq) continue;
                    insert_neighbor(query_out, capacity, &count, q.id, t.id, sqrtf(d2));
                }
            }
        }
    }
}
)CUDA";

static const char* kFixedRadiusCountRtKernelSrc = R"CUDA(
#include <optix_device.h>
#include <stdint.h>

typedef unsigned int uint32_t;

struct GpuPoint { float x, y; uint32_t id; uint32_t pad; };
struct FixedRadiusCountRecord { uint32_t query_id, neighbor_count, threshold_reached; };

struct FixedRadiusCountParams {
    OptixTraversableHandle traversable;
    const GpuPoint* query_points;
    const GpuPoint* search_points;
    const uint32_t* query_ids;
    const double* query_x;
    const double* query_y;
    const uint32_t* search_ids;
    const double* search_x;
    const double* search_y;
    FixedRadiusCountRecord* output;
    uint32_t* query_ids_out;
    uint32_t* neighbor_counts_out;
    uint32_t* threshold_flags_out;
    uint32_t* threshold_reached_count;
    uint32_t query_count;
    uint32_t threshold;
    uint32_t use_device_columns;
    float radius;
    float trace_tmax;
};

extern "C" {
__constant__ FixedRadiusCountParams params;
}

extern "C" __global__ void __raygen__frn_count_probe() {
    const uint32_t idx = optixGetLaunchIndex().x;
    if (idx >= params.query_count) return;
    const uint32_t query_id = params.use_device_columns ? params.query_ids[idx] : params.query_points[idx].id;
    const float query_x = params.use_device_columns ? static_cast<float>(params.query_x[idx]) : params.query_points[idx].x;
    const float query_y = params.use_device_columns ? static_cast<float>(params.query_y[idx]) : params.query_points[idx].y;
    unsigned int p0 = idx, p1 = 0u, p2 = 0u;
    optixTrace(params.traversable,
               make_float3(query_x, query_y, -params.radius),
               make_float3(0.0f, 0.0f, 1.0f),
               0.0f, params.trace_tmax, 0.0f,
               OptixVisibilityMask(255),
               OPTIX_RAY_FLAG_NONE,
               0, 1, 0,
               p0, p1, p2);
    if (params.output) {
        params.output[idx] = {query_id, p1, p2};
    }
    if (params.query_ids_out) {
        params.query_ids_out[idx] = query_id;
    }
    if (params.neighbor_counts_out) {
        params.neighbor_counts_out[idx] = p1;
    }
    if (params.threshold_flags_out) {
        params.threshold_flags_out[idx] = p2 ? 1u : 0u;
    }
    if (params.threshold_reached_count && p2 != 0u) {
        atomicAdd(params.threshold_reached_count, 1u);
    }
}

extern "C" __global__ void __miss__frn_count_miss() {}

extern "C" __global__ void __intersection__frn_count_isect() {
    const uint32_t prim = optixGetPrimitiveIndex();
    const uint32_t qidx = optixGetPayload_0();
    const float query_x = params.use_device_columns ? static_cast<float>(params.query_x[qidx]) : params.query_points[qidx].x;
    const float query_y = params.use_device_columns ? static_cast<float>(params.query_y[qidx]) : params.query_points[qidx].y;
    const float target_x = params.use_device_columns ? static_cast<float>(params.search_x[prim]) : params.search_points[prim].x;
    const float target_y = params.use_device_columns ? static_cast<float>(params.search_y[prim]) : params.search_points[prim].y;
    const float dx = target_x - query_x;
    const float dy = target_y - query_y;
    const float radius_sq = params.radius * params.radius;
    if ((dx * dx + dy * dy) > radius_sq) {
        return;
    }
    optixReportIntersection(params.radius, 0u);
}

extern "C" __global__ void __anyhit__frn_count_anyhit() {
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

static const char* kFixedRadiusCountHostRtKernelSrc = R"CUDA(
#include <optix_device.h>
#include <stdint.h>

typedef unsigned int uint32_t;

struct GpuPoint { float x, y; uint32_t id; uint32_t pad; };
struct FixedRadiusCountRecord { uint32_t query_id, neighbor_count, threshold_reached; };

struct FixedRadiusCountHostParams {
    OptixTraversableHandle traversable;
    const GpuPoint* query_points;
    const GpuPoint* search_points;
    FixedRadiusCountRecord* output;
    uint32_t* threshold_reached_count;
    uint32_t query_count;
    uint32_t threshold;
    float radius;
    float trace_tmax;
};

extern "C" {
__constant__ FixedRadiusCountHostParams params;
}

extern "C" __global__ void __raygen__frn_count_host_probe() {
    const uint32_t idx = optixGetLaunchIndex().x;
    if (idx >= params.query_count) return;
    const GpuPoint q = params.query_points[idx];
    unsigned int p0 = idx, p1 = 0u, p2 = 0u;
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

extern "C" __global__ void __miss__frn_count_host_miss() {}

extern "C" __global__ void __intersection__frn_count_host_isect() {
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

extern "C" __global__ void __anyhit__frn_count_host_anyhit() {
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

static const char* kFixedRadiusNearestRtKernelSrc = R"CUDA(
#include <optix_device.h>
#include <stdint.h>

typedef unsigned int uint32_t;

struct GpuPoint { float x, y; uint32_t id; uint32_t pad; };
struct FixedRadiusNearestRecord { uint32_t query_id, neighbor_id; float distance; };

struct FixedRadiusNearestParams {
    OptixTraversableHandle traversable;
    const GpuPoint* query_points;
    const GpuPoint* search_points;
    FixedRadiusNearestRecord* output;
    uint32_t query_count;
    float radius;
    float trace_tmax;
};

extern "C" {
__constant__ FixedRadiusNearestParams params;
}

extern "C" __global__ void __raygen__frn_nearest_probe() {
    const uint32_t idx = optixGetLaunchIndex().x;
    if (idx >= params.query_count) return;
    const GpuPoint q = params.query_points[idx];
    unsigned int p0 = idx;
    unsigned int p1 = __float_as_uint(3.4028234663852886e38f);
    unsigned int p2 = 0xFFFFFFFFu;
    unsigned int p3 = 0u;
    optixTrace(params.traversable,
               make_float3(q.x, q.y, -params.radius),
               make_float3(0.0f, 0.0f, 1.0f),
               0.0f, params.trace_tmax, 0.0f,
               OptixVisibilityMask(255),
               OPTIX_RAY_FLAG_NONE,
               0, 1, 0,
               p0, p1, p2, p3);
    params.output[idx] = {q.id, p2, p3 ? sqrtf(__uint_as_float(p1)) : 3.4028234663852886e38f};
}

extern "C" __global__ void __miss__frn_nearest_miss() {}

extern "C" __global__ void __intersection__frn_nearest_isect() {
    const uint32_t prim = optixGetPrimitiveIndex();
    const uint32_t qidx = optixGetPayload_0();
    const GpuPoint q = params.query_points[qidx];
    const GpuPoint t = params.search_points[prim];
    const float dx = t.x - q.x;
    const float dy = t.y - q.y;
    const float d2 = dx * dx + dy * dy;
    const float radius_sq = params.radius * params.radius;
    if (d2 > radius_sq) return;
    optixReportIntersection(params.radius, 0u);
}

extern "C" __global__ void __anyhit__frn_nearest_anyhit() {
    const uint32_t prim = optixGetPrimitiveIndex();
    const uint32_t qidx = optixGetPayload_0();
    const GpuPoint q = params.query_points[qidx];
    const GpuPoint t = params.search_points[prim];
    const float dx = t.x - q.x;
    const float dy = t.y - q.y;
    const float d2 = dx * dx + dy * dy;
    const float best = __uint_as_float(optixGetPayload_1());
    const uint32_t best_id = optixGetPayload_2();
    if (d2 < best || (d2 == best && t.id < best_id)) {
        optixSetPayload_1(__float_as_uint(d2));
        optixSetPayload_2(t.id);
        optixSetPayload_3(1u);
    }
    optixIgnoreIntersection();
}
)CUDA";

static const char* kPointGroupThresholdRtKernelSrc = R"CUDA(
#include <optix_device.h>
#include <stdint.h>
#include <math.h>

typedef unsigned int uint32_t;

struct GpuPoint { float x, y; uint32_t id; uint32_t pad; };
struct PointGroupBounds { float min_x, min_y, max_x, max_y; uint32_t id, point_offset, point_count, pad; };

struct PointGroupThresholdParams {
    OptixTraversableHandle traversable;
    const GpuPoint* query_points;
    const GpuPoint* search_points;
    const PointGroupBounds* groups;
    uint32_t* threshold_reached_count;
    uint32_t* threshold_flags;
    uint32_t query_count;
    uint32_t threshold;
    float radius;
    float trace_tmax;
};

extern "C" {
__constant__ PointGroupThresholdParams params;
}

static __forceinline__ __device__ float min_distance_sq_to_group(const GpuPoint q, const PointGroupBounds g) {
    const float dx = q.x < g.min_x ? (g.min_x - q.x) : (q.x > g.max_x ? (q.x - g.max_x) : 0.0f);
    const float dy = q.y < g.min_y ? (g.min_y - q.y) : (q.y > g.max_y ? (q.y - g.max_y) : 0.0f);
    return dx * dx + dy * dy;
}

extern "C" __global__ void __raygen__point_group_threshold_probe() {
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
    if (params.threshold_reached_count && p2 != 0u) {
        atomicAdd(params.threshold_reached_count, 1u);
    }
    if (params.threshold_flags) {
        params.threshold_flags[idx] = p2 != 0u ? 1u : 0u;
    }
}

extern "C" __global__ void __miss__point_group_threshold_miss() {}

extern "C" __global__ void __intersection__point_group_threshold_isect() {
    const uint32_t prim = optixGetPrimitiveIndex();
    const uint32_t qidx = optixGetPayload_0();
    const GpuPoint q = params.query_points[qidx];
    const PointGroupBounds g = params.groups[prim];
    const float radius_sq = params.radius * params.radius;
    if (min_distance_sq_to_group(q, g) > radius_sq) {
        return;
    }
    optixReportIntersection(params.radius, 0u);
}

extern "C" __global__ void __anyhit__point_group_threshold_anyhit() {
    const uint32_t prim = optixGetPrimitiveIndex();
    const uint32_t qidx = optixGetPayload_0();
    const GpuPoint q = params.query_points[qidx];
    const PointGroupBounds g = params.groups[prim];
    const float radius_sq = params.radius * params.radius;
    uint32_t count = optixGetPayload_1();
    for (uint32_t i = 0; i < g.point_count; ++i) {
        const GpuPoint t = params.search_points[g.point_offset + i];
        const float dx = t.x - q.x;
        const float dy = t.y - q.y;
        if ((dx * dx + dy * dy) <= radius_sq) {
            ++count;
            if (params.threshold != 0u && count >= params.threshold) {
                optixSetPayload_1(count);
                optixSetPayload_2(1u);
                optixTerminateRay();
                return;
            }
        }
    }
    optixSetPayload_1(count);
    optixIgnoreIntersection();
}
)CUDA";

static const char* kPointGroupNearestRtKernelSrc = R"CUDA(
#include <optix_device.h>
#include <stdint.h>
#include <math.h>

typedef unsigned int uint32_t;

struct GpuPoint { float x, y; uint32_t id; uint32_t pad; };
struct PointGroupBounds { float min_x, min_y, max_x, max_y; uint32_t id, point_offset, point_count, pad; };
struct FixedRadiusNearestRecord { uint32_t query_id, neighbor_id; float distance; };

struct PointGroupNearestParams {
    OptixTraversableHandle traversable;
    const GpuPoint* query_points;
    const GpuPoint* search_points;
    const PointGroupBounds* groups;
    FixedRadiusNearestRecord* output;
    uint32_t query_count;
    float radius;
    float trace_tmax;
};

extern "C" {
__constant__ PointGroupNearestParams params;
}

static __forceinline__ __device__ float nearest_min_distance_sq_to_group(const GpuPoint q, const PointGroupBounds g) {
    const float dx = q.x < g.min_x ? (g.min_x - q.x) : (q.x > g.max_x ? (q.x - g.max_x) : 0.0f);
    const float dy = q.y < g.min_y ? (g.min_y - q.y) : (q.y > g.max_y ? (q.y - g.max_y) : 0.0f);
    return dx * dx + dy * dy;
}

extern "C" __global__ void __raygen__point_group_nearest_probe() {
    const uint32_t idx = optixGetLaunchIndex().x;
    if (idx >= params.query_count) return;
    const GpuPoint q = params.query_points[idx];
    unsigned int p0 = idx;
    unsigned int p1 = __float_as_uint(3.4028234663852886e38f);
    unsigned int p2 = 0xFFFFFFFFu;
    unsigned int p3 = 0u;
    optixTrace(params.traversable,
               make_float3(q.x, q.y, -params.radius),
               make_float3(0.0f, 0.0f, 1.0f),
               0.0f, params.trace_tmax, 0.0f,
               OptixVisibilityMask(255),
               OPTIX_RAY_FLAG_NONE,
               0, 1, 0,
               p0, p1, p2, p3);
    params.output[idx] = {q.id, p2, p3 ? sqrtf(__uint_as_float(p1)) : 3.4028234663852886e38f};
}

extern "C" __global__ void __miss__point_group_nearest_miss() {}

extern "C" __global__ void __intersection__point_group_nearest_isect() {
    const uint32_t prim = optixGetPrimitiveIndex();
    const uint32_t qidx = optixGetPayload_0();
    const GpuPoint q = params.query_points[qidx];
    const PointGroupBounds g = params.groups[prim];
    const float radius_sq = params.radius * params.radius;
    if (nearest_min_distance_sq_to_group(q, g) > radius_sq) {
        return;
    }
    optixReportIntersection(params.radius, 0u);
}

extern "C" __global__ void __anyhit__point_group_nearest_anyhit() {
    const uint32_t prim = optixGetPrimitiveIndex();
    const uint32_t qidx = optixGetPayload_0();
    const GpuPoint q = params.query_points[qidx];
    const PointGroupBounds g = params.groups[prim];
    const float radius_sq = params.radius * params.radius;
    float best = __uint_as_float(optixGetPayload_1());
    uint32_t best_id = optixGetPayload_2();
    uint32_t found = optixGetPayload_3();
    for (uint32_t i = 0; i < g.point_count; ++i) {
        const GpuPoint t = params.search_points[g.point_offset + i];
        const float dx = t.x - q.x;
        const float dy = t.y - q.y;
        const float d2 = dx * dx + dy * dy;
        if (d2 > radius_sq) {
            continue;
        }
        if (d2 < best || (d2 == best && t.id < best_id)) {
            best = d2;
            best_id = t.id;
            found = 1u;
        }
    }
    optixSetPayload_1(__float_as_uint(best));
    optixSetPayload_2(best_id);
    optixSetPayload_3(found);
    optixIgnoreIntersection();
}
)CUDA";

static const char* kPointGroupNearestMaxReduceKernelSrc = R"CUDA(
#include <stdint.h>
#include <math.h>

typedef unsigned int uint32_t;

struct FixedRadiusNearestRecord { uint32_t query_id, neighbor_id; float distance; };

static __forceinline__ __device__ bool better_max_record(
        const FixedRadiusNearestRecord candidate,
        const FixedRadiusNearestRecord incumbent)
{
    if (candidate.distance > incumbent.distance) return true;
    if (candidate.distance < incumbent.distance) return false;
    if (candidate.query_id < incumbent.query_id) return true;
    if (candidate.query_id > incumbent.query_id) return false;
    return candidate.neighbor_id < incumbent.neighbor_id;
}

extern "C" __global__ void reduce_point_group_nearest_max_distance(
        const FixedRadiusNearestRecord* input,
        uint32_t count,
        FixedRadiusNearestRecord* output)
{
    __shared__ FixedRadiusNearestRecord scratch[256];
    const uint32_t tid = threadIdx.x;
    FixedRadiusNearestRecord best = {0xffffffffu, 0xffffffffu, -1.0f};
    for (uint32_t index = tid; index < count; index += blockDim.x) {
        FixedRadiusNearestRecord row = input[index];
        if (row.neighbor_id == 0xffffffffu || !isfinite(row.distance)) {
            row.distance = INFINITY;
        }
        if (better_max_record(row, best)) {
            best = row;
        }
    }
    scratch[tid] = best;
    __syncthreads();
    for (uint32_t stride = blockDim.x >> 1; stride > 0; stride >>= 1) {
        if (tid < stride && better_max_record(scratch[tid + stride], scratch[tid])) {
            scratch[tid] = scratch[tid + stride];
        }
        __syncthreads();
    }
    if (tid == 0) {
        output[0] = scratch[0];
    }
}
)CUDA";

static const char* kKnnRowsKernelSrc = R"CUDA(
#include <stdint.h>
#include <math.h>
#include <float.h>

struct GpuPoint { float x, y; uint32_t id; uint32_t pad; };
struct KnnRecord { uint32_t query_id, neighbor_id; float distance; uint32_t neighbor_rank; };

extern "C" __global__ void knn_rows(
        const GpuPoint* query_points,
        uint32_t        query_count,
        const GpuPoint* search_points,
        uint32_t        search_count,
        uint32_t        k,
        KnnRecord*      output)
{
    const uint32_t qidx = blockIdx.x * blockDim.x + threadIdx.x;
    if (qidx >= query_count) return;

    KnnRecord* query_out = output + static_cast<size_t>(qidx) * static_cast<size_t>(k);
    for (uint32_t slot = 0; slot < k; ++slot) {
        query_out[slot].query_id = query_points[qidx].id;
        query_out[slot].neighbor_id = 0xffffffffu;
        query_out[slot].distance = INFINITY;
        query_out[slot].neighbor_rank = 0u;
    }

    const float px = query_points[qidx].x;
    const float py = query_points[qidx].y;
    for (uint32_t sidx = 0; sidx < search_count; ++sidx) {
        const float dx = search_points[sidx].x - px;
        const float dy = search_points[sidx].y - py;
        const float distance = sqrtf(dx * dx + dy * dy);
        const uint32_t neighbor_id = search_points[sidx].id;

        uint32_t insert_at = k;
        for (uint32_t slot = 0; slot < k; ++slot) {
            const bool empty = query_out[slot].neighbor_id == 0xffffffffu;
            const bool better_distance = distance < query_out[slot].distance - 1.0e-7f;
            const bool same_distance = fabsf(distance - query_out[slot].distance) <= 1.0e-7f;
            const bool better_id = same_distance && neighbor_id < query_out[slot].neighbor_id;
            if (empty || better_distance || better_id) {
                insert_at = slot;
                break;
            }
        }
        if (insert_at == k) {
            continue;
        }
        for (uint32_t slot = k - 1; slot > insert_at; --slot) {
            query_out[slot] = query_out[slot - 1];
        }
        query_out[insert_at].query_id = query_points[qidx].id;
        query_out[insert_at].neighbor_id = neighbor_id;
        query_out[insert_at].distance = distance;
    }

    for (uint32_t slot = 0; slot < k; ++slot) {
        if (query_out[slot].neighbor_id == 0xffffffffu) {
            break;
        }
        query_out[slot].neighbor_rank = slot + 1;
    }
}
)CUDA";

static const char* kPackPoint2DDeviceAabbsKernelSrc = R"CUDA(
#include <stdint.h>

struct RtdlDeviceAabb {
    float minX, minY, minZ;
    float maxX, maxY, maxZ;
};

extern "C" __global__ void pack_point2d_fixed_radius_aabbs(
        const double* x,
        const double* y,
        RtdlDeviceAabb* aabbs,
        uint32_t point_count,
        float aabb_radius)
{
    const uint32_t idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= point_count) return;
    const float px = static_cast<float>(x[idx]);
    const float py = static_cast<float>(y[idx]);
    RtdlDeviceAabb aabb;
    aabb.minX = px - aabb_radius;
    aabb.minY = py - aabb_radius;
    aabb.minZ = -aabb_radius;
    aabb.maxX = px + aabb_radius;
    aabb.maxY = py + aabb_radius;
    aabb.maxZ = aabb_radius;
    aabbs[idx] = aabb;
}
)CUDA";

static const char* kPackRay2DDeviceColumnsKernelSrc = R"CUDA(
#include <stdint.h>

struct GpuRay {
    float ox, oy, dx, dy, tmax;
    uint32_t id;
};

extern "C" __global__ void pack_ray2d_device_columns(
        const uint32_t* ids,
        const double* ox,
        const double* oy,
        const double* dx,
        const double* dy,
        const double* tmax,
        GpuRay* output,
        uint32_t ray_count)
{
    const uint32_t idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= ray_count) return;
    GpuRay ray;
    ray.ox = static_cast<float>(ox[idx]);
    ray.oy = static_cast<float>(oy[idx]);
    ray.dx = static_cast<float>(dx[idx]);
    ray.dy = static_cast<float>(dy[idx]);
    ray.tmax = static_cast<float>(tmax[idx]);
    ray.id = ids[idx];
    output[idx] = ray;
}
)CUDA";

static const char* kPackTriangle2DDeviceColumnsKernelSrc = R"CUDA(
#include <stdint.h>
#include <math.h>

struct GpuTriangle {
    float x0, y0, x1, y1, x2, y2;
    uint32_t id;
};

struct RtdlDeviceAabb {
    float minX, minY, minZ;
    float maxX, maxY, maxZ;
};

extern "C" __global__ void pack_triangle2d_device_columns(
        const uint32_t* ids,
        const double* x0,
        const double* y0,
        const double* x1,
        const double* y1,
        const double* x2,
        const double* y2,
        GpuTriangle* triangles,
        RtdlDeviceAabb* aabbs,
        uint32_t triangle_count)
{
    const uint32_t idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= triangle_count) return;
    GpuTriangle tri;
    tri.x0 = static_cast<float>(x0[idx]);
    tri.y0 = static_cast<float>(y0[idx]);
    tri.x1 = static_cast<float>(x1[idx]);
    tri.y1 = static_cast<float>(y1[idx]);
    tri.x2 = static_cast<float>(x2[idx]);
    tri.y2 = static_cast<float>(y2[idx]);
    tri.id = ids[idx];
    triangles[idx] = tri;

    const float min_x = fminf(fminf(tri.x0, tri.x1), tri.x2);
    const float min_y = fminf(fminf(tri.y0, tri.y1), tri.y2);
    const float max_x = fmaxf(fmaxf(tri.x0, tri.x1), tri.x2);
    const float max_y = fmaxf(fmaxf(tri.y0, tri.y1), tri.y2);
    RtdlDeviceAabb aabb;
    aabb.minX = min_x;
    aabb.minY = min_y;
    aabb.minZ = -1.0e-4f;
    aabb.maxX = max_x;
    aabb.maxY = max_y;
    aabb.maxZ = 1.0e-4f;
    aabbs[idx] = aabb;
}
)CUDA";

// ---------- DB conjunctive_scan kernel --------------------------------------

static const char* kDbScanKernelSrc = R"CUDA(
#include <optix_device.h>
#include <stdint.h>

struct DbScanParams {
    OptixTraversableHandle traversable;
    uint32_t* hit_words;
    uint32_t hit_word_count;
    uint32_t x_lo;
    uint32_t y_lo;
    uint32_t z_lo;
    uint32_t z_hi;
    uint32_t x_count;
    uint32_t y_count;
};

extern "C" {
__constant__ DbScanParams params;
}

extern "C" __global__ void __raygen__db_scan_probe() {
    const uint32_t x_index = optixGetLaunchIndex().x;
    const uint32_t y_index = optixGetLaunchIndex().y;
    if (x_index >= params.x_count || y_index >= params.y_count) {
        return;
    }
    const float origin_x = static_cast<float>(params.x_lo + x_index);
    const float origin_y = static_cast<float>(params.y_lo + y_index);
    const float origin_z = static_cast<float>(params.z_lo) - 1.0f;
    const float tmax = static_cast<float>((params.z_hi - params.z_lo) + 2u);
    optixTrace(
        params.traversable,
        make_float3(origin_x, origin_y, origin_z),
        make_float3(0.0f, 0.0f, 1.0f),
        0.0f,
        tmax,
        0.0f,
        OptixVisibilityMask(255),
        OPTIX_RAY_FLAG_NONE,
        0, 1, 0);
}

extern "C" __global__ void __miss__db_scan_miss() {}

extern "C" __global__ void __intersection__db_scan_isect() {
    optixReportIntersection(0.5f, 0u);
}

extern "C" __global__ void __anyhit__db_scan_anyhit() {
    const uint32_t prim = optixGetPrimitiveIndex();
    const uint32_t word = prim >> 5;
    if (word < params.hit_word_count) {
        const uint32_t bit = 1u << (prim & 31u);
        atomicOr(params.hit_words + word, bit);
    }
    optixIgnoreIntersection();
}
)CUDA";

static const char* kGraphBfsRayKernelSrc = R"CUDA(
#include <optix_device.h>
#include <stdint.h>

struct FrontierVertex {
    uint32_t vertex_id;
    uint32_t level;
};

struct EdgeSeed {
    uint32_t u;
    uint32_t v;
};

struct GraphEdge {
    uint32_t src;
    uint32_t dst;
};

struct BfsRow {
    uint32_t src_vertex;
    uint32_t dst_vertex;
    uint32_t level;
};

struct GraphBfsParams {
    OptixTraversableHandle traversable;
    const GraphEdge* edges;
    const FrontierVertex* frontier;
    const uint32_t* visited_flags;
    uint32_t* discovered_flags;
    BfsRow* output;
    uint32_t* output_count;
    uint32_t output_capacity;
    uint32_t frontier_count;
    uint32_t vertex_count;
    uint32_t dedupe;
};

extern "C" {
__constant__ GraphBfsParams params;
}

extern "C" __global__ void __raygen__graph_bfs_probe() {
    const uint32_t idx = optixGetLaunchIndex().x;
    if (idx >= params.frontier_count) {
        return;
    }
    const FrontierVertex f = params.frontier[idx];
    if (f.vertex_id >= params.vertex_count) {
        return;
    }
    uint32_t p0 = idx;
    optixTrace(
        params.traversable,
        make_float3(static_cast<float>(f.vertex_id), -1.0f, 0.0f),
        make_float3(0.0f, 1.0f, 0.0f),
        0.0f,
        static_cast<float>(params.vertex_count + 2u),
        0.0f,
        OptixVisibilityMask(255),
        OPTIX_RAY_FLAG_NONE,
        0, 1, 0,
        p0);
}

extern "C" __global__ void __miss__graph_bfs_miss() {}

extern "C" __global__ void __intersection__graph_bfs_isect() {
    optixReportIntersection(optixGetRayTmin() + 1.0e-6f, 0u);
}

extern "C" __global__ void __anyhit__graph_bfs_anyhit() {
    const uint32_t frontier_index = optixGetPayload_0();
    const uint32_t prim = optixGetPrimitiveIndex();
    const FrontierVertex f = params.frontier[frontier_index];
    const GraphEdge edge = params.edges[prim];
    if (edge.src != f.vertex_id) {
        optixIgnoreIntersection();
        return;
    }
    if (params.visited_flags[edge.dst] != 0u) {
        optixIgnoreIntersection();
        return;
    }
    if (params.dedupe != 0u) {
        if (atomicExch(params.discovered_flags + edge.dst, 1u) != 0u) {
            optixIgnoreIntersection();
            return;
        }
    }
    const uint32_t slot = atomicAdd(params.output_count, 1u);
    if (slot < params.output_capacity) {
        params.output[slot] = {edge.src, edge.dst, f.level + 1u};
    }
    optixIgnoreIntersection();
}
)CUDA";

static const char* kGraphTriangleRayKernelSrc = R"CUDA(
#include <optix_device.h>
#include <stdint.h>

struct EdgeSeed {
    uint32_t u;
    uint32_t v;
};

struct GraphEdge {
    uint32_t src;
    uint32_t dst;
};

struct TriangleCandidate {
    uint32_t seed_index;
    uint32_t side;
    uint32_t dst_vertex;
};

struct GraphTriangleParams {
    OptixTraversableHandle traversable;
    const GraphEdge* edges;
    const EdgeSeed* seeds;
    TriangleCandidate* output;
    uint32_t* output_count;
    uint32_t output_capacity;
    uint32_t seed_count;
    uint32_t vertex_count;
};

extern "C" {
__constant__ GraphTriangleParams params;
}

extern "C" __global__ void __raygen__graph_triangle_cycle_candidates() {
    const uint32_t ray_index = optixGetLaunchIndex().x;
    const uint32_t seed_index = ray_index >> 1;
    if (seed_index >= params.seed_count) {
        return;
    }
    const EdgeSeed seed = params.seeds[seed_index];
    const uint32_t src = (ray_index & 1u) == 0u ? seed.u : seed.v;
    if (src >= params.vertex_count) {
        return;
    }
    uint32_t p0 = ray_index;
    optixTrace(
        params.traversable,
        make_float3(static_cast<float>(src), -1.0f, 0.0f),
        make_float3(0.0f, 1.0f, 0.0f),
        0.0f,
        static_cast<float>(params.vertex_count + 2u),
        0.0f,
        OptixVisibilityMask(255),
        OPTIX_RAY_FLAG_NONE,
        0, 1, 0,
        p0);
}

extern "C" __global__ void __miss__graph_triangle_miss() {}

extern "C" __global__ void __intersection__graph_triangle_isect() {
    optixReportIntersection(optixGetRayTmin() + 1.0e-6f, 0u);
}

extern "C" __global__ void __anyhit__graph_triangle_anyhit() {
    const uint32_t ray_index = optixGetPayload_0();
    const uint32_t seed_index = ray_index >> 1;
    const uint32_t side = ray_index & 1u;
    const EdgeSeed seed = params.seeds[seed_index];
    const uint32_t src = side == 0u ? seed.u : seed.v;
    const GraphEdge edge = params.edges[optixGetPrimitiveIndex()];
    if (edge.src != src) {
        optixIgnoreIntersection();
        return;
    }
    const uint32_t slot = atomicAdd(params.output_count, 1u);
    if (slot < params.output_capacity) {
        params.output[slot] = {seed_index, side, edge.dst};
    }
    optixIgnoreIntersection();
}
)CUDA";

static const char* kKnnRows3DKernelSrc = R"CUDA(
#include <stdint.h>
#include <math.h>
#include <float.h>

struct GpuPoint3D { float x, y, z; uint32_t id; };
struct KnnRecord { uint32_t query_id, neighbor_id; float distance; uint32_t neighbor_rank; };

extern "C" __global__ void knn_rows_3d(
        const GpuPoint3D* query_points,
        uint32_t          query_count,
        const GpuPoint3D* search_points,
        uint32_t          search_count,
        uint32_t          k,
        KnnRecord*        output)
{
    const uint32_t qidx = blockIdx.x * blockDim.x + threadIdx.x;
    if (qidx >= query_count) return;

    KnnRecord* query_out = output + static_cast<size_t>(qidx) * static_cast<size_t>(k);
    for (uint32_t slot = 0; slot < k; ++slot) {
        query_out[slot].query_id = query_points[qidx].id;
        query_out[slot].neighbor_id = 0xffffffffu;
        query_out[slot].distance = INFINITY;
        query_out[slot].neighbor_rank = 0u;
    }

    const float px = query_points[qidx].x;
    const float py = query_points[qidx].y;
    const float pz = query_points[qidx].z;
    for (uint32_t sidx = 0; sidx < search_count; ++sidx) {
        const float dx = search_points[sidx].x - px;
        const float dy = search_points[sidx].y - py;
        const float dz = search_points[sidx].z - pz;
        const float distance = sqrtf(dx * dx + dy * dy + dz * dz);
        const uint32_t neighbor_id = search_points[sidx].id;

        uint32_t insert_at = k;
        for (uint32_t slot = 0; slot < k; ++slot) {
            const bool empty = query_out[slot].neighbor_id == 0xffffffffu;
            const bool better_distance = distance < query_out[slot].distance - 1.0e-7f;
            const bool same_distance = fabsf(distance - query_out[slot].distance) <= 1.0e-7f;
            const bool better_id = same_distance && neighbor_id < query_out[slot].neighbor_id;
            if (empty || better_distance || better_id) {
                insert_at = slot;
                break;
            }
        }
        if (insert_at == k) {
            continue;
        }
        for (uint32_t slot = k - 1; slot > insert_at; --slot) {
            query_out[slot] = query_out[slot - 1];
        }
        query_out[insert_at].query_id = query_points[qidx].id;
        query_out[insert_at].neighbor_id = neighbor_id;
        query_out[insert_at].distance = distance;
    }

    for (uint32_t slot = 0; slot < k; ++slot) {
        if (query_out[slot].neighbor_id == 0xffffffffu) {
            break;
        }
        query_out[slot].neighbor_rank = slot + 1;
    }
}
)CUDA";

// ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
// Cached pipeline singletons
// ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

struct SegmentPairIntersectionPipeline {
    PipelineHolder* pipe = nullptr;
    std::once_flag   init;
};

struct SegmentFirstHitPipeline {
    PipelineHolder* pipe = nullptr;
    std::once_flag   init;
};

struct PipPipeline {
    PipelineHolder* pipe = nullptr;
    std::once_flag   init;
};

struct ShapePairRelationPipeline {
    PipelineHolder* pipe = nullptr;
    std::once_flag   init;
};

struct RayHitCountPipeline {
    PipelineHolder* pipe = nullptr;
    std::once_flag   init;
};

struct RayAnyHitPipeline {
    PipelineHolder* pipe = nullptr;
    std::once_flag   init;
};

struct SegPolyPipeline {
    PipelineHolder* pipe = nullptr;
    std::once_flag   init;
};

struct RayHitCount3DPipeline {
    PipelineHolder* pipe = nullptr;
    std::once_flag   init;
};

struct DbScanPipeline {
    PipelineHolder* pipe = nullptr;
    std::once_flag init;
};

struct GraphEdgePipeline {
    PipelineHolder* pipe = nullptr;
    std::once_flag init;
};

struct PnsCuFunction {
    CUmodule   module   = nullptr;
    CUfunction fn       = nullptr;
    std::once_flag init;
};

struct FrnCuFunction {
    CUmodule   module   = nullptr;
    CUfunction fn       = nullptr;
    std::once_flag init;
};

struct KnnCuFunction {
    CUmodule   module   = nullptr;
    CUfunction fn       = nullptr;
    std::once_flag init;
};

static SegmentPairIntersectionPipeline         g_segment_pair_intersection;
static SegmentFirstHitPipeline                 g_segment_first_hit;
static PipPipeline         g_pip;
static ShapePairRelationPipeline     g_shape_pair_relation;
static RayHitCountPipeline  g_rayhit;
static RayHitCount3DPipeline g_rayhit3d;
static RayAnyHitPipeline    g_rayanyhit;
static RayAnyHitPipeline    g_rayanyhit3d;
static RayAnyHitPipeline    g_rayanyhit_count;
static RayAnyHitPipeline    g_rayanyhit_count_device_ray_columns;
static RayAnyHitPipeline    g_rayanyhit_count_device_columns;
static RayAnyHitPipeline    g_rayanyhit_flags_device_columns;
static RayAnyHitPipeline    g_rayanyhit_witness_device_columns;
static RayAnyHitPipeline    g_rayanyhit_all_witnesses_device_columns;
static RayAnyHitPipeline    g_rayanyhit_group_flags;
static RayAnyHitPipeline    g_frn_count_rt;
static RayAnyHitPipeline    g_frn_count_host_rt;
static RayAnyHitPipeline    g_frn_nearest_rt;
static RayAnyHitPipeline    g_frn3d_rt;
static RayAnyHitPipeline    g_point_group_threshold_rt;
static RayAnyHitPipeline    g_point_group_nearest_rt;
static KnnCuFunction       g_point_group_nearest_reduce;
static SegPolyPipeline     g_segpoly;
static SegPolyPipeline     g_segpoly_rows;
static DbScanPipeline      g_dbscan;
static GraphEdgePipeline   g_graph_bfs;
static GraphEdgePipeline   g_graph_triangle;
static PnsCuFunction      g_pns;
static FrnCuFunction      g_frn;
static FrnCuFunction      g_frn3d;
static FrnCuFunction      g_frn3d_grid;
static FrnCuFunction      g_frn3d_grid_count;
static FrnCuFunction      g_frn3d_grid_exact_count;
static FrnCuFunction      g_frn3d_grid_exact_summary;
static FrnCuFunction      g_frn3d_grid_compact;
static KnnCuFunction      g_partner_ray2d_pack;
static KnnCuFunction      g_partner_triangle2d_pack;
static KnnCuFunction      g_partner_point2d_aabb_pack;
static KnnCuFunction      g_knn;
static KnnCuFunction      g_knn3d;
static KnnCuFunction      g_collect_k_i64;
static KnnCuFunction      g_collect_k_i64_row_width2_sort;
static KnnCuFunction      g_collect_k_i64_row_width2_cub_sort;
static KnnCuFunction      g_collect_k_i64_row_width2_cub_sort_tiles;
static KnnCuFunction      g_collect_k_i64_row_width2_merge_two;
static KnnCuFunction      g_collect_k_i64_row_width2_merge_level;
static KnnCuFunction      g_collect_k_cooperative_launch_smoke;
static KnnCuFunction      g_collect_k_i64_row_width2_final_materialize;
static KnnCuFunction      g_collect_k_i64_row_width2_final_materialize_counts;
static KnnCuFunction      g_collect_k_i64_row_width2_final_mark_counts;
static KnnCuFunction      g_collect_k_i64_row_width2_final_mark_counts_counts;
static KnnCuFunction      g_collect_k_i64_row_width2_final_compact;
static KnnCuFunction      g_collect_k_i64_row_width2_final_compact_counts;
static KnnCuFunction      g_collect_k_i64_row_width2_final_materialize_level;
static KnnCuFunction      g_collect_k_i64_row_width2_final_mark_counts_level;
static KnnCuFunction      g_collect_k_i64_row_width2_final_compact_level;
static KnnCuFunction      g_collect_k_i64_row_width2_final_materialize_level_derived;
static KnnCuFunction      g_collect_k_i64_row_width2_final_materialize_level_counts_derived;
static KnnCuFunction      g_collect_k_i64_row_width2_final_materialize_level_counts_pointers;
static KnnCuFunction      g_collect_k_i64_row_width2_final_mark_counts_level_counts;
static KnnCuFunction      g_collect_k_i64_row_width2_final_mark_counts_level_counts_pointers;
static KnnCuFunction      g_collect_k_i64_row_width2_final_materialize_mark_counts_level_counts;
static KnnCuFunction      g_collect_k_i64_row_width2_final_output_indexed_materialize_mark_counts_level_counts;
static KnnCuFunction      g_collect_k_i64_row_width2_four_way_materialize_mark_counts_derived;
static KnnCuFunction      g_collect_k_i64_row_width2_final_compact_level_derived;
static KnnCuFunction      g_collect_k_i64_row_width2_final_prefix_offsets_level;

// GPU structs for upload

#pragma pack(push, 1)
struct GpuSegment   { float x0, y0, x1, y1; uint32_t id; };
struct GpuPoint     { float x, y;           uint32_t id; uint32_t pad; };
struct GpuPoint3DHost { float x, y, z;      uint32_t id; };
struct GpuPolygonRef { uint32_t id, vertex_offset, vertex_count; };
struct GpuTriangle  { float x0, y0, x1, y1, x2, y2; uint32_t id; };
struct GpuRay       { float ox, oy, dx, dy, tmax; uint32_t id; };
// 3-D counterparts - direction is pre-normalised before upload.
struct GpuRay3DHost { float ox, oy, oz, dx, dy, dz, tmax; uint32_t id; };
struct GpuTriangle3DHost { float x0, y0, z0, x1, y1, z1, x2, y2, z2; uint32_t id; };
#pragma pack(pop)

// Output structs (GPU-side, float coords)
#pragma pack(push, 1)
struct GpuSegmentPairIntersectionRecord  { uint32_t left_id, right_id, left_index, right_index; };
struct GpuPipRecord  { uint32_t point_id, polygon_id, contains; };
struct GpuShapePairRelationFlags { uint32_t requires_segment_intersection, requires_point_containment; };
struct GpuRayHitRecord { uint32_t ray_id, hit_count; };
struct GpuRayAnyHitRecord { uint32_t ray_id, any_hit; };
struct GpuFixedRadiusCountRecord { uint32_t query_id, neighbor_count, threshold_reached; };
struct GpuSegPolyRecord { uint32_t segment_id, hit_count; };
struct GpuPnsRecord     { uint32_t point_id, segment_id; float distance; };
struct GpuFrnRecord     { uint32_t query_id, neighbor_id; float distance; };
struct GpuKnnRecord     { uint32_t query_id, neighbor_id; float distance; uint32_t neighbor_rank; };
#pragma pack(pop)

struct Bounds2D {
    double min_x, min_y, max_x, max_y;
};

static bool segment_intersection_denominator_is_degenerate(
        double denom,
        double rx,
        double ry,
        double sx,
        double sy)
{
    const double scale = std::hypot(rx, ry) * std::hypot(sx, sy);
    const double threshold = 64.0 * std::numeric_limits<double>::epsilon() * std::max(1.0, scale);
    return std::abs(denom) <= threshold;
}

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
    if (segment_intersection_denominator_is_degenerate(denom, rx, ry, sx, sy)) {
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

static bool exact_point_in_triangle(
        double x,
        double y,
        const RtdlTriangle& triangle)
{
    const double v0x = triangle.x2 - triangle.x0;
    const double v0y = triangle.y2 - triangle.y0;
    const double v1x = triangle.x1 - triangle.x0;
    const double v1y = triangle.y1 - triangle.y0;
    const double v2x = x - triangle.x0;
    const double v2y = y - triangle.y0;

    const double dot00 = v0x * v0x + v0y * v0y;
    const double dot01 = v0x * v1x + v0y * v1y;
    const double dot02 = v0x * v2x + v0y * v2y;
    const double dot11 = v1x * v1x + v1y * v1y;
    const double dot12 = v1x * v2x + v1y * v2y;
    const double denom = dot00 * dot11 - dot01 * dot01;
    if (std::abs(denom) < 1.0e-7) {
        return false;
    }

    const double inv = 1.0 / denom;
    const double u = (dot11 * dot02 - dot01 * dot12) * inv;
    const double v = (dot00 * dot12 - dot01 * dot02) * inv;
    return u >= 0.0 && v >= 0.0 && (u + v) <= 1.0;
}

static bool exact_ray_hits_triangle(
        const RtdlRay2D& ray,
        const RtdlTriangle& triangle)
{
    const double ex = ray.ox + ray.dx * ray.tmax;
    const double ey = ray.oy + ray.dy * ray.tmax;
    const RtdlSegment ray_segment{ray.id, ray.ox, ray.oy, ex, ey};

    if (exact_point_in_triangle(ray.ox, ray.oy, triangle) ||
        exact_point_in_triangle(ex, ey, triangle)) {
        return true;
    }

    const RtdlSegment edges[3] = {
        {triangle.id, triangle.x0, triangle.y0, triangle.x1, triangle.y1},
        {triangle.id, triangle.x1, triangle.y1, triangle.x2, triangle.y2},
        {triangle.id, triangle.x2, triangle.y2, triangle.x0, triangle.y0},
    };
    for (const auto& edge : edges) {
        double ix = 0.0;
        double iy = 0.0;
        if (exact_segment_intersection(ray_segment, edge, &ix, &iy)) {
            return true;
        }
    }
    return false;
}

static bool exact_ray_hits_triangle_3d(
        const RtdlRay3D& ray,
        const RtdlTriangle3D& triangle)
{
    const double edge1x = triangle.x1 - triangle.x0;
    const double edge1y = triangle.y1 - triangle.y0;
    const double edge1z = triangle.z1 - triangle.z0;
    const double edge2x = triangle.x2 - triangle.x0;
    const double edge2y = triangle.y2 - triangle.y0;
    const double edge2z = triangle.z2 - triangle.z0;

    const double pvx = ray.dy * edge2z - ray.dz * edge2y;
    const double pvy = ray.dz * edge2x - ray.dx * edge2z;
    const double pvz = ray.dx * edge2y - ray.dy * edge2x;
    const double det = edge1x * pvx + edge1y * pvy + edge1z * pvz;
    if (std::abs(det) <= 1.0e-8) {
        return false;
    }

    const double inv_det = 1.0 / det;
    const double tvx = ray.ox - triangle.x0;
    const double tvy = ray.oy - triangle.y0;
    const double tvz = ray.oz - triangle.z0;
    const double u = (tvx * pvx + tvy * pvy + tvz * pvz) * inv_det;
    if (u < 0.0 || u > 1.0) {
        return false;
    }

    const double qvx = tvy * edge1z - tvz * edge1y;
    const double qvy = tvz * edge1x - tvx * edge1z;
    const double qvz = tvx * edge1y - tvy * edge1x;
    const double v = (ray.dx * qvx + ray.dy * qvy + ray.dz * qvz) * inv_det;
    if (v < 0.0 || (u + v) > 1.0) {
        return false;
    }

    const double t = (edge2x * qvx + edge2y * qvy + edge2z * qvz) * inv_det;
    return t >= 0.0 && t <= ray.tmax;
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

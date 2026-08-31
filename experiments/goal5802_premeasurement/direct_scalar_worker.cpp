// Goal5802 matched Direct CUDA/C++/OptiX arm.
//
// This is a new worker.  It deliberately does not include or call the
// Goal5798 measurement worker.  The frozen Goal5796 implementation supplies
// the low-level OptiX construction and device ABI; this translation unit owns
// a persistent launch-parameter buffer and exposes status plus a scalar-only
// triangle product.

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <algorithm>
#include <array>
#include <chrono>
#include <cctype>
#include <dlfcn.h>
#include <cstring>
#include <cstdlib>
#include <fcntl.h>
#include <fstream>
#include <iomanip>
#include <limits>
#include <map>
#include <memory>
#include <numeric>
#include <regex>
#include <sstream>
#include <string>
#include <sys/stat.h>
#include <type_traits>
#include <unistd.h>
#include <vector>

#define main goal5796_functional_main_disabled
#include "../goal5796_matched/direct_optix.cpp"
#undef main

namespace {

using Clock = std::chrono::steady_clock;
using Nanoseconds = std::chrono::nanoseconds;
constexpr std::uint32_t kRelationSize = 4096;
constexpr std::uint32_t kRelationRawCapacity = 2 * kRelationSize;
constexpr float kRelationMinimumOverlap = 1.0f;
constexpr std::uint32_t kTriangleSize = 16384;
constexpr int kSteadyWarmups = 8;
constexpr int kSteadyRepetitions = 64;
constexpr const char* kRelationTask =
    "CUSTOM_AABB_CLOSED_RELATION_COUNT_V2_MATCHED";
constexpr const char* kTriangleTask =
    "BUILTIN_TRIANGLE_WEIGHTED_SCALAR_V2_MATCHED";

std::string compile_ptx_exact_arch(
        const std::string& source, const std::string& source_name,
        const std::string& optix_include, const std::string& cuda_include,
        const std::string& compute_architecture) {
    if (compute_architecture.rfind("compute_", 0) != 0
            || compute_architecture.size() <= 8
            || !std::all_of(
                compute_architecture.begin() + 8,
                compute_architecture.end(),
                [](unsigned char value) { return std::isdigit(value); }))
        throw std::runtime_error(
            "Direct BUILD_COLD compute architecture invalid");
    nvrtcProgram program = nullptr;
    NVRTC_CHECK(nvrtcCreateProgram(
        &program, source.c_str(), source_name.c_str(), 0, nullptr, nullptr));
    std::vector<std::string> option_storage = {
        "--std=c++17", "--device-as-default-execution-space",
        "--relocatable-device-code=true",
        "--gpu-architecture=" + compute_architecture,
        "-I" + optix_include, "-I" + cuda_include,
        "-I" + cuda_include + "/nv",
    };
    std::vector<const char*> options;
    for (const auto& option : option_storage) options.push_back(option.c_str());
    const nvrtcResult compile_result = nvrtcCompileProgram(
        program, static_cast<int>(options.size()), options.data());
    if (compile_result != NVRTC_SUCCESS) {
        std::size_t size = 0;
        nvrtcGetProgramLogSize(program, &size);
        std::string log(size, '\0');
        if (size) nvrtcGetProgramLog(program, log.data());
        nvrtcDestroyProgram(&program);
        throw std::runtime_error("Goal5802 exact-arch NVRTC failed:\n" + log);
    }
    std::size_t size = 0;
    NVRTC_CHECK(nvrtcGetPTXSize(program, &size));
    std::string ptx(size, '\0');
    NVRTC_CHECK(nvrtcGetPTX(program, ptx.data()));
    NVRTC_CHECK(nvrtcDestroyProgram(&program));
    const std::string expected_target =
        "sm_" + compute_architecture.substr(8);
    const std::regex target_pattern(
        R"((^|\n)\.target[ \t]+(sm_[0-9]+)([ \t,\r\n]|$))");
    std::sregex_iterator current(ptx.begin(), ptx.end(), target_pattern);
    const std::sregex_iterator end;
    std::vector<std::string> targets;
    for (; current != end; ++current) {
        const auto target = (*current)[2].str();
        targets.push_back(target);
    }
    if (targets.size() != 1 || targets.front() != expected_target)
        throw std::runtime_error(
            "Direct BUILD_COLD PTX target differs from exact architecture");
    return ptx;
}

// The Goal5797 error-acceptance KAT deliberately used OptiX validation ALL.
// Comparative timing must not charge that diagnostic mode to Direct while
// RTDL runs the product default OFF, so Goal5802 owns an explicit OFF context.
struct ComparativeContext {
    CUdevice device = 0;
    CUcontext cuda = nullptr;
    OptixDeviceContext optix = nullptr;
    ComparativeContext() {
        CU_CHECK(cuInit(0));
        CU_CHECK(cuDeviceGet(&device, 0));
        CU_CHECK(cuDevicePrimaryCtxRetain(&cuda, device));
        CU_CHECK(cuCtxSetCurrent(cuda));
        OPTIX_CHECK(optixInit());
        OptixDeviceContextOptions options = {};
        options.validationMode = OPTIX_DEVICE_CONTEXT_VALIDATION_MODE_OFF;
        OPTIX_CHECK(optixDeviceContextCreate(cuda, &options, &optix));
    }
    ~ComparativeContext() {
        if (optix) optixDeviceContextDestroy(optix);
        if (cuda) cuDevicePrimaryCtxRelease(device);
    }
};

std::uint64_t elapsed_ns(Clock::time_point start) {
    return static_cast<std::uint64_t>(
        std::chrono::duration_cast<Nanoseconds>(Clock::now() - start).count());
}

std::uint64_t between_ns(Clock::time_point start, Clock::time_point end) {
    return static_cast<std::uint64_t>(
        std::chrono::duration_cast<Nanoseconds>(end - start).count());
}

std::uint64_t monotonic_epoch_ns() {
    return static_cast<std::uint64_t>(
        std::chrono::duration_cast<Nanoseconds>(
            Clock::now().time_since_epoch()).count());
}

std::uint32_t rotate_right(std::uint32_t value, unsigned count) {
    return (value >> count) | (value << (32U - count));
}

std::string sha256_bytes(const std::string& input) {
    static constexpr std::array<std::uint32_t, 64> constants = {
        0x428a2f98U,0x71374491U,0xb5c0fbcfU,0xe9b5dba5U,0x3956c25bU,0x59f111f1U,0x923f82a4U,0xab1c5ed5U,
        0xd807aa98U,0x12835b01U,0x243185beU,0x550c7dc3U,0x72be5d74U,0x80deb1feU,0x9bdc06a7U,0xc19bf174U,
        0xe49b69c1U,0xefbe4786U,0x0fc19dc6U,0x240ca1ccU,0x2de92c6fU,0x4a7484aaU,0x5cb0a9dcU,0x76f988daU,
        0x983e5152U,0xa831c66dU,0xb00327c8U,0xbf597fc7U,0xc6e00bf3U,0xd5a79147U,0x06ca6351U,0x14292967U,
        0x27b70a85U,0x2e1b2138U,0x4d2c6dfcU,0x53380d13U,0x650a7354U,0x766a0abbU,0x81c2c92eU,0x92722c85U,
        0xa2bfe8a1U,0xa81a664bU,0xc24b8b70U,0xc76c51a3U,0xd192e819U,0xd6990624U,0xf40e3585U,0x106aa070U,
        0x19a4c116U,0x1e376c08U,0x2748774cU,0x34b0bcb5U,0x391c0cb3U,0x4ed8aa4aU,0x5b9cca4fU,0x682e6ff3U,
        0x748f82eeU,0x78a5636fU,0x84c87814U,0x8cc70208U,0x90befffaU,0xa4506cebU,0xbef9a3f7U,0xc67178f2U,
    };
    std::vector<unsigned char> bytes(input.begin(), input.end());
    const std::uint64_t bit_count = static_cast<std::uint64_t>(bytes.size()) * 8U;
    bytes.push_back(0x80U);
    while (bytes.size() % 64U != 56U) bytes.push_back(0U);
    for (int shift = 56; shift >= 0; shift -= 8)
        bytes.push_back(static_cast<unsigned char>((bit_count >> shift) & 0xffU));
    std::array<std::uint32_t, 8> state = {
        0x6a09e667U,0xbb67ae85U,0x3c6ef372U,0xa54ff53aU,
        0x510e527fU,0x9b05688cU,0x1f83d9abU,0x5be0cd19U};
    for (std::size_t offset = 0; offset < bytes.size(); offset += 64U) {
        std::array<std::uint32_t, 64> words{};
        for (std::size_t index = 0; index < 16U; ++index) {
            const std::size_t base = offset + 4U * index;
            words[index] = (static_cast<std::uint32_t>(bytes[base]) << 24U)
                | (static_cast<std::uint32_t>(bytes[base + 1U]) << 16U)
                | (static_cast<std::uint32_t>(bytes[base + 2U]) << 8U)
                | static_cast<std::uint32_t>(bytes[base + 3U]);
        }
        for (std::size_t index = 16U; index < 64U; ++index) {
            const auto s0 = rotate_right(words[index - 15U], 7U)
                ^ rotate_right(words[index - 15U], 18U)
                ^ (words[index - 15U] >> 3U);
            const auto s1 = rotate_right(words[index - 2U], 17U)
                ^ rotate_right(words[index - 2U], 19U)
                ^ (words[index - 2U] >> 10U);
            words[index] = words[index - 16U] + s0 + words[index - 7U] + s1;
        }
        auto a=state[0]; auto b=state[1]; auto c=state[2]; auto d=state[3];
        auto e=state[4]; auto f=state[5]; auto g=state[6]; auto h=state[7];
        for (std::size_t index = 0; index < 64U; ++index) {
            const auto s1 = rotate_right(e,6U)^rotate_right(e,11U)^rotate_right(e,25U);
            const auto choose = (e & f) ^ ((~e) & g);
            const auto temp1 = h + s1 + choose + constants[index] + words[index];
            const auto s0 = rotate_right(a,2U)^rotate_right(a,13U)^rotate_right(a,22U);
            const auto majority = (a & b) ^ (a & c) ^ (b & c);
            const auto temp2 = s0 + majority;
            h=g; g=f; f=e; e=d+temp1; d=c; c=b; b=a; a=temp1+temp2;
        }
        state[0]+=a; state[1]+=b; state[2]+=c; state[3]+=d;
        state[4]+=e; state[5]+=f; state[6]+=g; state[7]+=h;
    }
    std::ostringstream output;
    output << std::hex << std::setfill('0');
    for (const auto value : state) output << std::setw(8) << value;
    return output.str();
}

struct LoadedNvrtcIdentity {
    std::string resolved_path;
    std::uint64_t bytes = 0;
    std::string sha256;
    int version_major = -1;
    int version_minor = -1;
};

struct LoadedRegularFileIdentity {
    std::string resolved_path;
    std::uint64_t bytes = 0;
    std::string sha256;
};

struct MinimalNvrtcCompileKat {
    std::string source_utf8;
    std::string source_sha256;
    std::vector<std::string> compile_options;
    std::uint64_t product_bytes = 0;
    std::string product_sha256;
    bool compile_success = false;
    bool program_destroyed = false;
};

struct ScopedFileDescriptor {
    int value = -1;
    explicit ScopedFileDescriptor(int descriptor) : value(descriptor) {}
    ~ScopedFileDescriptor() { if (value >= 0) ::close(value); }
    ScopedFileDescriptor(const ScopedFileDescriptor&) = delete;
    ScopedFileDescriptor& operator=(const ScopedFileDescriptor&) = delete;
};

std::string json_escape(const std::string& value) {
    std::ostringstream output;
    output << std::hex << std::setfill('0');
    for (const unsigned char byte : value) {
        switch (byte) {
            case '"': output << "\\\""; break;
            case '\\': output << "\\\\"; break;
            case '\b': output << "\\b"; break;
            case '\f': output << "\\f"; break;
            case '\n': output << "\\n"; break;
            case '\r': output << "\\r"; break;
            case '\t': output << "\\t"; break;
            default:
                if (byte < 0x20U)
                    output << "\\u00" << std::setw(2)
                           << static_cast<unsigned>(byte);
                else
                    output << static_cast<char>(byte);
        }
    }
    return output.str();
}

LoadedNvrtcIdentity loaded_nvrtc_identity() {
    LoadedNvrtcIdentity result;
    NVRTC_CHECK(nvrtcVersion(&result.version_major, &result.version_minor));
    if (result.version_major < 0 || result.version_minor < 0)
        throw std::runtime_error("loaded NVRTC version is invalid");

    Dl_info info{};
    const void* const symbol_address = reinterpret_cast<const void*>(
        reinterpret_cast<std::uintptr_t>(&nvrtcVersion));
    if (::dladdr(symbol_address, &info) == 0 || info.dli_fname == nullptr
            || info.dli_fname[0] == '\0')
        throw std::runtime_error(
            "dladdr could not identify the loaded nvrtcVersion symbol");
    std::unique_ptr<char, decltype(&std::free)> canonical(
        ::realpath(info.dli_fname, nullptr), &std::free);
    if (!canonical || canonical.get()[0] != '/')
        throw std::runtime_error(
            "loaded NVRTC path is not absolute and canonically resolved");
    result.resolved_path = canonical.get();

    struct stat path_before{};
    if (::lstat(result.resolved_path.c_str(), &path_before) != 0
            || S_ISLNK(path_before.st_mode)
            || !S_ISREG(path_before.st_mode)
            || path_before.st_size <= 0)
        throw std::runtime_error(
            "resolved loaded NVRTC path is not one unambiguous regular file");
    ScopedFileDescriptor file(::open(
        result.resolved_path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW));
    if (file.value < 0)
        throw std::runtime_error(
            "resolved loaded NVRTC file cannot be opened without symlinks");
    struct stat opened_before{};
    if (::fstat(file.value, &opened_before) != 0
            || !S_ISREG(opened_before.st_mode)
            || opened_before.st_dev != path_before.st_dev
            || opened_before.st_ino != path_before.st_ino
            || opened_before.st_size != path_before.st_size)
        throw std::runtime_error(
            "loaded NVRTC path and opened file identity differ");
    if (static_cast<std::uintmax_t>(opened_before.st_size)
            > std::numeric_limits<std::size_t>::max())
        throw std::runtime_error("loaded NVRTC file is too large to identify");

    std::string exact_bytes(
        static_cast<std::size_t>(opened_before.st_size), '\0');
    std::size_t offset = 0;
    while (offset < exact_bytes.size()) {
        const ssize_t count = ::read(
            file.value, exact_bytes.data() + offset,
            exact_bytes.size() - offset);
        if (count <= 0)
            throw std::runtime_error("loaded NVRTC exact-byte read failed");
        offset += static_cast<std::size_t>(count);
    }
    char extra = '\0';
    if (::read(file.value, &extra, 1) != 0)
        throw std::runtime_error("loaded NVRTC grew during exact-byte read");
    struct stat opened_after{};
    struct stat path_after{};
    if (::fstat(file.value, &opened_after) != 0
            || ::lstat(result.resolved_path.c_str(), &path_after) != 0
            || S_ISLNK(path_after.st_mode) || !S_ISREG(path_after.st_mode)
            || opened_after.st_dev != opened_before.st_dev
            || opened_after.st_ino != opened_before.st_ino
            || opened_after.st_size != opened_before.st_size
            || path_after.st_dev != opened_before.st_dev
            || path_after.st_ino != opened_before.st_ino
            || path_after.st_size != opened_before.st_size)
        throw std::runtime_error(
            "loaded NVRTC file identity changed during exact-byte read");
    result.bytes = static_cast<std::uint64_t>(exact_bytes.size());
    result.sha256 = sha256_bytes(exact_bytes);
    return result;
}

// Reuse the one retained-byte SHA-256 implementation for the compile KAT and
// the maps-derived builtins identity; there is no second digest algorithm.
std::string identity_sha256_bytes(const std::string& input) {
    return sha256_bytes(input);
}

MinimalNvrtcCompileKat run_minimal_nvrtc_compile_kat() {
    MinimalNvrtcCompileKat result;
    result.source_utf8 =
        "extern \"C\" __global__ void goal5802_nvrtc_identity_probe() {}\n";
    result.source_sha256 = identity_sha256_bytes(result.source_utf8);
    result.compile_options = {"--std=c++11"};

    nvrtcProgram program = nullptr;
    const nvrtcResult create_result = nvrtcCreateProgram(
        &program, result.source_utf8.c_str(),
        "goal5802_nvrtc_identity_probe.cu", 0, nullptr, nullptr);
    if (create_result != NVRTC_SUCCESS || program == nullptr)
        throw std::runtime_error(
            "minimal NVRTC identity program creation failed");
    const char* const options[] = {result.compile_options.front().c_str()};
    const nvrtcResult compile_result = nvrtcCompileProgram(program, 1, options);
    if (compile_result != NVRTC_SUCCESS) {
        std::size_t log_size = 0;
        (void)nvrtcGetProgramLogSize(program, &log_size);
        std::string log(log_size, '\0');
        if (log_size) (void)nvrtcGetProgramLog(program, log.data());
        const nvrtcResult destroy_result = nvrtcDestroyProgram(&program);
        if (destroy_result != NVRTC_SUCCESS)
            throw std::runtime_error(
                "minimal NVRTC identity compile and destroy both failed");
        throw std::runtime_error(
            "minimal NVRTC identity compile failed:\n" + log);
    }
    result.compile_success = true;

    std::size_t product_size = 0;
    const nvrtcResult size_result = nvrtcGetPTXSize(program, &product_size);
    if (size_result != NVRTC_SUCCESS || product_size == 0) {
        (void)nvrtcDestroyProgram(&program);
        throw std::runtime_error(
            "minimal NVRTC identity product size is unavailable");
    }
    std::string product(product_size, '\0');
    const nvrtcResult product_result = nvrtcGetPTX(program, product.data());
    if (product_result != NVRTC_SUCCESS) {
        (void)nvrtcDestroyProgram(&program);
        throw std::runtime_error(
            "minimal NVRTC identity product retrieval failed");
    }
    const nvrtcResult destroy_result = nvrtcDestroyProgram(&program);
    if (destroy_result != NVRTC_SUCCESS || program != nullptr)
        throw std::runtime_error(
            "minimal NVRTC identity program destruction failed");
    result.program_destroyed = true;
    result.product_bytes = static_cast<std::uint64_t>(product.size());
    result.product_sha256 = identity_sha256_bytes(product);
    return result;
}

bool is_nvrtc_builtins_basename(const std::string& path) {
    const std::size_t slash = path.find_last_of('/');
    const std::string basename =
        slash == std::string::npos ? path : path.substr(slash + 1);
    return basename == "libnvrtc-builtins.so"
        || basename.rfind("libnvrtc-builtins.so.", 0) == 0;
}

LoadedRegularFileIdentity loaded_regular_file_identity(
        const std::string& canonical_path, const std::string& label) {
    if (canonical_path.empty() || canonical_path.front() != '/')
        throw std::runtime_error(label + " path is not absolute");
    std::unique_ptr<char, decltype(&std::free)> resolved(
        ::realpath(canonical_path.c_str(), nullptr), &std::free);
    if (!resolved || canonical_path != resolved.get())
        throw std::runtime_error(label + " path is not canonical");

    struct stat path_before{};
    if (::lstat(canonical_path.c_str(), &path_before) != 0
            || S_ISLNK(path_before.st_mode)
            || !S_ISREG(path_before.st_mode)
            || path_before.st_size <= 0)
        throw std::runtime_error(
            label + " path is not one canonical regular file");
    ScopedFileDescriptor file(::open(
        canonical_path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW));
    if (file.value < 0)
        throw std::runtime_error(
            label + " file cannot be opened without symlinks");
    struct stat opened_before{};
    if (::fstat(file.value, &opened_before) != 0
            || !S_ISREG(opened_before.st_mode)
            || opened_before.st_dev != path_before.st_dev
            || opened_before.st_ino != path_before.st_ino
            || opened_before.st_size != path_before.st_size)
        throw std::runtime_error(label + " path/open identities differ");
    if (static_cast<std::uintmax_t>(opened_before.st_size)
            > std::numeric_limits<std::size_t>::max())
        throw std::runtime_error(label + " file is too large to identify");

    std::string exact_bytes(
        static_cast<std::size_t>(opened_before.st_size), '\0');
    std::size_t offset = 0;
    while (offset < exact_bytes.size()) {
        const ssize_t count = ::read(
            file.value, exact_bytes.data() + offset,
            exact_bytes.size() - offset);
        if (count <= 0)
            throw std::runtime_error(label + " exact-byte read failed");
        offset += static_cast<std::size_t>(count);
    }
    char extra = '\0';
    if (::read(file.value, &extra, 1) != 0)
        throw std::runtime_error(label + " grew during exact-byte read");
    struct stat opened_after{};
    struct stat path_after{};
    if (::fstat(file.value, &opened_after) != 0
            || ::lstat(canonical_path.c_str(), &path_after) != 0
            || S_ISLNK(path_after.st_mode) || !S_ISREG(path_after.st_mode)
            || opened_after.st_dev != opened_before.st_dev
            || opened_after.st_ino != opened_before.st_ino
            || opened_after.st_size != opened_before.st_size
            || path_after.st_dev != opened_before.st_dev
            || path_after.st_ino != opened_before.st_ino
            || path_after.st_size != opened_before.st_size)
        throw std::runtime_error(
            label + " file identity changed during exact-byte read");

    LoadedRegularFileIdentity result;
    result.resolved_path = canonical_path;
    result.bytes = static_cast<std::uint64_t>(exact_bytes.size());
    result.sha256 = identity_sha256_bytes(exact_bytes);
    return result;
}

LoadedRegularFileIdentity loaded_nvrtc_builtins_identity_from_proc_maps() {
    std::ifstream maps("/proc/self/maps", std::ios::binary);
    if (!maps)
        throw std::runtime_error("current-process maps cannot be opened");
    std::vector<std::string> candidates;
    std::string line;
    while (std::getline(maps, line)) {
        const std::size_t path_start = line.find('/');
        if (path_start == std::string::npos) continue;
        std::string mapped_path = line.substr(path_start);
        const bool deleted = mapped_path.size() >= 10
            && mapped_path.compare(
                mapped_path.size() - 10, 10, " (deleted)") == 0;
        if (deleted) mapped_path.resize(mapped_path.size() - 10);
        if (!is_nvrtc_builtins_basename(mapped_path)) continue;
        if (deleted)
            throw std::runtime_error(
                "mapped NVRTC builtins identity is deleted");
        std::unique_ptr<char, decltype(&std::free)> canonical(
            ::realpath(mapped_path.c_str(), nullptr), &std::free);
        if (!canonical || canonical.get()[0] != '/'
                || !is_nvrtc_builtins_basename(canonical.get()))
            throw std::runtime_error(
                "mapped NVRTC builtins path is not canonical");
        candidates.emplace_back(canonical.get());
    }
    if (maps.bad())
        throw std::runtime_error("current-process maps read failed");
    std::sort(candidates.begin(), candidates.end());
    candidates.erase(
        std::unique(candidates.begin(), candidates.end()), candidates.end());
    if (candidates.size() != 1)
        throw std::runtime_error(
            "current process does not map exactly one canonical NVRTC "
            "builtins library");
    return loaded_regular_file_identity(
        candidates.front(), "loaded NVRTC builtins");
}

template <typename T>
struct PinnedHost {
    T* pointer = nullptr;
    explicit PinnedHost(std::size_t count = 1) {
        CU_CHECK(cuMemHostAlloc(
            reinterpret_cast<void**>(&pointer), sizeof(T) * count,
            CU_MEMHOSTALLOC_PORTABLE));
        std::memset(pointer, 0, sizeof(T) * count);
    }
    ~PinnedHost() { if (pointer) cuMemFreeHost(pointer); }
    PinnedHost(const PinnedHost&) = delete;
    PinnedHost& operator=(const PinnedHost&) = delete;
};

std::vector<Box> relation_boxes() {
    std::vector<Box> result;
    result.reserve(kRelationSize);
    for (std::uint32_t id = 0; id < kRelationSize; ++id) {
        const float lower = static_cast<float>(2 * id);
        result.push_back(box(lower, 0.0f, lower + 1.0f, 1.0f, id));
    }
    return result;
}

std::vector<Box> relation_k_plus_one_indexed() {
    return {box(0.0f, 0.0f, 4.0f, 4.0f,
                std::numeric_limits<std::uint32_t>::max())};
}

std::vector<Box> relation_k_plus_one_sources() {
    std::vector<Box> result;
    result.reserve(kRelationSize + 1);
    for (std::uint32_t id = 0; id <= kRelationSize; ++id)
        result.push_back(box(0.125f, 2.0f, 1.125f, 3.0f, id));
    result.push_back(box(
        0.125f, 2.0f, 0.625f, 3.0f, kRelationSize + 1));
    return result;
}

void append_u32_le(std::string& output, std::uint32_t value) {
    for (unsigned shift = 0; shift < 32; shift += 8)
        output.push_back(static_cast<char>((value >> shift) & 0xffU));
}

void append_f32_le(std::string& output, float value) {
    std::uint32_t bits = 0;
    static_assert(sizeof(bits) == sizeof(value), "binary32 width drift");
    std::memcpy(&bits, &value, sizeof(bits));
    append_u32_le(output, bits);
}

std::uint32_t f32_bits(float value) {
    std::uint32_t bits = 0;
    std::memcpy(&bits, &value, sizeof(bits));
    return bits;
}

std::string relation_k_plus_one_packed_input() {
    static constexpr char prefix[] = "goal5802-relation-k-plus-one-v1";
    const auto indexed = relation_k_plus_one_indexed();
    const auto sources = relation_k_plus_one_sources();
    std::string output(prefix, sizeof(prefix));  // include terminal NUL
    append_u32_le(output, static_cast<std::uint32_t>(indexed.size()));
    append_u32_le(output, static_cast<std::uint32_t>(sources.size()));
    append_f32_le(output, kRelationMinimumOverlap);
    append_u32_le(output, kRelationSize);
    append_u32_le(output, kRelationRawCapacity);
    const auto append_box = [&](const Box& item) {
        append_f32_le(output, item.lower_x);
        append_f32_le(output, item.lower_y);
        append_f32_le(output, item.lower_z);
        append_f32_le(output, item.upper_x);
        append_f32_le(output, item.upper_y);
        append_f32_le(output, item.upper_z);
        append_u32_le(output, item.item_id);
    };
    for (const auto& item : indexed) append_box(item);
    for (const auto& item : sources) append_box(item);
    return output;
}

std::vector<float3> triangle_vertices() {
    std::vector<float3> result;
    result.reserve(3 * kTriangleSize);
    for (std::uint32_t id = 0; id < kTriangleSize; ++id) {
        const float x = static_cast<float>(3 * id);
        result.push_back(float3{x - 1.0f, -1.0f, 1.0f});
        result.push_back(float3{x + 1.0f, -1.0f, 1.0f});
        result.push_back(float3{x, 1.0f, 1.0f});
    }
    return result;
}

std::vector<Ray> triangle_rays() {
    std::vector<Ray> result;
    result.reserve(kTriangleSize);
    for (std::uint32_t id = 0; id < kTriangleSize; ++id) {
        const float x = static_cast<float>(3 * id);
        result.push_back({x, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f});
    }
    return result;
}

std::vector<std::uint64_t> triangle_weights() {
    std::vector<std::uint64_t> result;
    result.reserve(kTriangleSize);
    for (std::uint32_t id = 0; id < kTriangleSize; ++id)
        result.push_back(1 + id % 7);
    if (std::accumulate(result.begin(), result.end(), std::uint64_t{0}) != 65530)
        throw std::runtime_error("Goal5802 Direct scalar oracle drift");
    return result;
}

struct OperationTrace {
    std::uint64_t optix_launch_count = 0;
    std::uint64_t compaction_launch_count = 0;
    std::uint64_t async_h2d_call_count = 0;
    std::uint64_t async_h2d_bytes = 0;
    std::uint64_t async_d2h_call_count = 0;
    std::uint64_t async_d2h_bytes = 0;
    std::uint64_t async_d2d_call_count = 0;
    std::uint64_t async_d2d_bytes = 0;
    std::uint64_t host_blocking_boundary_count = 0;
};

struct RelationCompactionModule {
    CUmodule module = nullptr;
    CUfunction function = nullptr;

    explicit RelationCompactionModule(const std::string& cubin) {
        if (cubin.size() < 4 || cubin.compare(0, 4, "\x7f" "ELF") != 0)
            throw std::runtime_error("Direct relation compaction cubin invalid");
        CU_CHECK(cuModuleLoadData(&module, cubin.data()));
        CU_CHECK(cuModuleGetFunction(
            &function, module, "goal5802_relation_unique_compact"));
    }
    ~RelationCompactionModule() { if (module) cuModuleUnload(module); }
    RelationCompactionModule(const RelationCompactionModule&) = delete;
    RelationCompactionModule& operator=(
        const RelationCompactionModule&) = delete;
};

struct DynamicInputTrace {
    bool prepared_input_reused = false;
    std::uint64_t dynamic_device_upload_call_count = 0;
    std::uint64_t dynamic_device_upload_bytes = 0;
    std::uint64_t dynamic_accel_build_count = 0;
    std::uint64_t dynamic_explicit_sync_count = 0;
    std::uint64_t dynamic_blocking_upload_call_count = 0;
    std::uint64_t dynamic_input_generation = 0;
};

struct NoMeasurementTrace {};

template <bool Observe, typename Trace, typename T>
DeviceBuffer upload_dynamic_async(
        Trace& trace, const T* pinned_values,
        std::size_t value_count, CUstream stream) {
    DeviceBuffer result(sizeof(T) * value_count);
    if (value_count) {
        CU_CHECK(cuMemcpyHtoDAsync(
            result.ptr, pinned_values, result.bytes, stream));
        if constexpr (Observe) {
            ++trace.dynamic_device_upload_call_count;
            trace.dynamic_device_upload_bytes += result.bytes;
        }
    }
    return result;
}

// The build temporary is retained until owner close, so the dynamic source
// GAS can remain ordered before the later launches on stream 0 without adding
// a baseline-only host synchronization.  Static GAS construction remains in
// the prepare phase and uses the inherited Goal5796 helper.
struct DeferredCustomAccel {
    DeviceBuffer geometry;
    DeviceBuffer temporary;
    DeviceBuffer output;
    OptixTraversableHandle handle = 0;
};

template <bool Observe, typename Trace>
DeferredCustomAccel build_dynamic_custom_accel(
        OptixDeviceContext context, const std::vector<Box>& boxes,
        PinnedHost<OptixAabb>& pinned_aabbs, Trace& trace,
        CUstream stream) {
    for (std::size_t index = 0; index < boxes.size(); ++index) {
        const auto& row = boxes[index];
        OptixAabb aabb = {};
        aabb.minX = row.lower_x; aabb.minY = row.lower_y; aabb.minZ = -0.001f;
        aabb.maxX = row.upper_x; aabb.maxY = row.upper_y; aabb.maxZ = 0.001f;
        pinned_aabbs.pointer[index] = aabb;
    }
    DeferredCustomAccel result;
    result.geometry = upload_dynamic_async<Observe>(
        trace, pinned_aabbs.pointer, boxes.size(), stream);
    OptixBuildInput input = {};
    input.type = OPTIX_BUILD_INPUT_TYPE_CUSTOM_PRIMITIVES;
    input.customPrimitiveArray.aabbBuffers = &result.geometry.ptr;
    input.customPrimitiveArray.numPrimitives =
        static_cast<unsigned int>(boxes.size());
    input.customPrimitiveArray.strideInBytes = sizeof(OptixAabb);
    std::uint32_t flags = OPTIX_GEOMETRY_FLAG_NONE;
    input.customPrimitiveArray.flags = &flags;
    input.customPrimitiveArray.numSbtRecords = 1;
    OptixAccelBuildOptions options = {};
    options.buildFlags = OPTIX_BUILD_FLAG_NONE;
    options.operation = OPTIX_BUILD_OPERATION_BUILD;
    OptixAccelBufferSizes sizes = {};
    OPTIX_CHECK(optixAccelComputeMemoryUsage(
        context, &options, &input, 1, &sizes));
    result.temporary = DeviceBuffer(sizes.tempSizeInBytes);
    result.output = DeviceBuffer(sizes.outputSizeInBytes);
    OPTIX_CHECK(optixAccelBuild(
        context, stream, &options, &input, 1,
        result.temporary.ptr, result.temporary.bytes,
        result.output.ptr, result.output.bytes, &result.handle, nullptr, 0));
    if constexpr (Observe) ++trace.dynamic_accel_build_count;
    return result;
}

template <bool Observe, typename Trace>
void traced_h2d(
        Trace& trace, CUdeviceptr destination, const void* source,
        std::size_t bytes, CUstream stream) {
    if constexpr (Observe) {
        ++trace.async_h2d_call_count;
        trace.async_h2d_bytes += bytes;
    }
    CU_CHECK(cuMemcpyHtoDAsync(destination, source, bytes, stream));
}

template <bool Observe, typename Trace>
void traced_d2h(
        Trace& trace, void* destination, CUdeviceptr source,
        std::size_t bytes, CUstream stream) {
    if constexpr (Observe) {
        ++trace.async_d2h_call_count;
        trace.async_d2h_bytes += bytes;
    }
    CU_CHECK(cuMemcpyDtoHAsync(destination, source, bytes, stream));
}

template <bool Observe, typename Trace>
void traced_d2d(
        Trace& trace, CUdeviceptr destination, CUdeviceptr source,
        std::size_t bytes, CUstream stream) {
    if constexpr (Observe) {
        ++trace.async_d2d_call_count;
        trace.async_d2d_bytes += bytes;
    }
    CU_CHECK(cuMemcpyDtoDAsync(destination, source, bytes, stream));
}

template <bool Observe, typename Trace>
void traced_sync(Trace& trace, CUstream stream) {
    if constexpr (Observe) ++trace.host_blocking_boundary_count;
    CU_CHECK(cuStreamSynchronize(stream));
}

template <bool Observe, typename Trace>
void traced_launch(
        Trace& trace, const Pipeline& pipeline,
        CUdeviceptr device_params, unsigned width) {
    if constexpr (Observe) ++trace.optix_launch_count;
    OPTIX_CHECK(optixLaunch(
        pipeline.pipeline, 0, device_params, sizeof(Params),
        &pipeline.sbt, width, 1, 1));
}

template <bool Observe, typename Trace>
void enqueue_launch(
        Trace& trace,
        const Pipeline& pipeline, CUdeviceptr device_params,
        const Params* host_params, unsigned width) {
    traced_h2d<Observe>(trace, device_params, host_params, sizeof(Params), 0);
    traced_launch<Observe>(trace, pipeline, device_params, width);
}

template <bool Observe, typename Trace>
void enqueue_relation_compaction(
        Trace& trace, CUfunction function,
        CUdeviceptr raw_rows, CUdeviceptr unique_rows, CUdeviceptr control,
        CUdeviceptr keys, CUdeviceptr max_key_seen, CUdeviceptr unique_count,
        std::uint32_t raw_capacity, std::uint32_t semantic_capacity,
        std::uint32_t key_capacity, CUstream stream) {
    void* arguments[] = {
        &raw_rows, &unique_rows, &control, &keys, &max_key_seen,
        &unique_count, &raw_capacity, &semantic_capacity, &key_capacity,
    };
    constexpr unsigned block_size = 256;
    const unsigned grid_size = (raw_capacity + block_size - 1) / block_size;
    if constexpr (Observe) ++trace.compaction_launch_count;
    CU_CHECK(cuLaunchKernel(
        function, grid_size, 1, 1, block_size, 1, 1, 0, stream,
        arguments, nullptr));
}

struct RelationOutput {
    std::vector<std::pair<std::uint32_t, std::uint32_t>> rows;
    std::uint32_t raw_count = 0;
    std::uint32_t unique_count = 0;
    std::uint32_t status = 0;
    std::uint32_t overflow = 0;
};

struct ObservedRelationOutput {
    RelationOutput value;
    OperationTrace trace;
    DynamicInputTrace dynamic_input;
};

struct ObservedRelationDeviceStatusFailure : std::runtime_error {
    std::uint32_t raw_count;
    std::uint32_t unique_count;
    std::uint32_t overflow;
    std::uint32_t status;
    OperationTrace trace;
    DynamicInputTrace dynamic_input;

    ObservedRelationDeviceStatusFailure(
            std::uint32_t raw, std::uint32_t unique,
            std::uint32_t did_overflow, std::uint32_t device_status,
            OperationTrace observed_trace, DynamicInputTrace dynamic)
        : std::runtime_error(
              "Direct relation status rejected before application output"),
          raw_count(raw), unique_count(unique), overflow(did_overflow),
          status(device_status), trace(observed_trace),
          dynamic_input(dynamic) {}
};

struct PreparedRelationScalarContract {
    const Pipeline& pipeline;
    CUfunction compaction_function = nullptr;
    OptixDeviceContext context;
    std::vector<Box> indexed;
    std::vector<Box> queries;
    DeviceBuffer d_indexed, d_queries, d_rows, d_unique_rows, d_control;
    DeviceBuffer d_keys, d_max_key_seen, d_unique_count;
    DeviceBuffer d_params;
    Accel indexed_accel;
    DeferredCustomAccel query_accel;
    PinnedHost<Params> h_params;
    PinnedHost<std::uint32_t> h_control;
    PinnedHost<RelationRow> h_rows;
    PinnedHost<Box> h_dynamic_queries;
    PinnedHost<OptixAabb> h_dynamic_aabbs;
    float minimum_overlap;
    bool dynamic_input_ready = false;
    std::uint64_t dynamic_input_generation = 0;

    PreparedRelationScalarContract(
             OptixDeviceContext context, const Pipeline& owned_pipeline,
             CUfunction relation_compaction_function,
             std::vector<Box> static_input,
             std::vector<Box> dynamic_queries,
             float required_minimum_overlap)
        : pipeline(owned_pipeline),
          compaction_function(relation_compaction_function), context(context),
          indexed(std::move(static_input)), queries(std::move(dynamic_queries)),
          d_indexed(upload_vector(indexed)),
          d_rows(sizeof(RelationRow) * kRelationRawCapacity),
          d_unique_rows(sizeof(RelationRow) * kRelationSize),
          d_control(4 * sizeof(std::uint32_t)),
          d_keys(sizeof(std::uint64_t) * kRelationRawCapacity),
          d_max_key_seen(sizeof(std::uint32_t)),
          d_unique_count(sizeof(std::uint32_t)), d_params(sizeof(Params)),
          indexed_accel(custom_accel(context, indexed)), h_params(2),
          h_control(4), h_rows(kRelationSize),
          h_dynamic_queries(queries.size()),
          h_dynamic_aabbs(queries.size()),
          minimum_overlap(required_minimum_overlap) {
        if (!compaction_function)
            throw std::runtime_error("Direct relation compaction function absent");
        if (indexed.empty() || queries.empty())
            throw std::runtime_error("Direct relation inputs must be nonempty");
    }

    template <bool Observe>
    auto materialize_dynamic_input() {
        using Trace = std::conditional_t<Observe, DynamicInputTrace,
                                         NoMeasurementTrace>;
        Trace trace;
        if constexpr (Observe) {
            trace.prepared_input_reused = dynamic_input_ready;
            trace.dynamic_input_generation = dynamic_input_generation;
        }
        if (dynamic_input_ready) return trace;
        std::copy(
            queries.begin(), queries.end(), h_dynamic_queries.pointer);
        d_queries = upload_dynamic_async<Observe>(
            trace, h_dynamic_queries.pointer, queries.size(), 0);
        query_accel = build_dynamic_custom_accel<Observe>(
            context, queries, h_dynamic_aabbs, trace, 0);
        dynamic_input_ready = true;
        ++dynamic_input_generation;
        if constexpr (Observe)
            trace.dynamic_input_generation = dynamic_input_generation;
        if constexpr (Observe) if (trace.dynamic_device_upload_call_count == 0
                || trace.dynamic_accel_build_count != 1
                || trace.dynamic_explicit_sync_count != 0)
            throw std::runtime_error(
                "Direct relation dynamic-input materialization drift");
        return trace;
    }

    template <bool Observe>
    auto execute_core() {
        const auto dynamic_input = materialize_dynamic_input<Observe>();
        using Trace = std::conditional_t<Observe, OperationTrace,
                                         NoMeasurementTrace>;
        Trace trace;
        CU_CHECK(cuMemsetD8Async(d_control.ptr, 0, d_control.bytes, 0));
        CU_CHECK(cuMemsetD8Async(d_keys.ptr, 0xff, d_keys.bytes, 0));
        CU_CHECK(cuMemsetD8Async(
            d_max_key_seen.ptr, 0, d_max_key_seen.bytes, 0));
        CU_CHECK(cuMemsetD8Async(
            d_unique_count.ptr, 0, d_unique_count.bytes, 0));
        for (unsigned reverse = 0; reverse < 2; ++reverse) {
            Params& params = h_params.pointer[reverse];
            params = {};
            params.traversable = reverse ? query_accel.handle : indexed_accel.handle;
            params.boxes = reinterpret_cast<const Box*>(
                reverse ? d_queries.ptr : d_indexed.ptr);
            params.queries = reinterpret_cast<const Box*>(
                reverse ? d_indexed.ptr : d_queries.ptr);
            params.rows = reinterpret_cast<RelationRow*>(d_rows.ptr);
            params.row_count = reinterpret_cast<std::uint32_t*>(d_control.ptr);
            params.overflow = reinterpret_cast<std::uint32_t*>(
                d_control.ptr + 2 * sizeof(std::uint32_t));
            params.status = reinterpret_cast<std::uint32_t*>(
                d_control.ptr + 3 * sizeof(std::uint32_t));
            const auto primitive_count = reverse ? queries.size() : indexed.size();
            const auto query_count = reverse ? indexed.size() : queries.size();
            if (primitive_count > std::numeric_limits<std::uint32_t>::max()
                    || query_count > std::numeric_limits<std::uint32_t>::max())
                throw std::runtime_error("Direct relation input count overflow");
            params.box_count = static_cast<std::uint32_t>(primitive_count);
            params.query_count = static_cast<std::uint32_t>(query_count);
            params.raw_row_capacity = kRelationRawCapacity;
            params.reverse_orientation = reverse;
            params.minimum_overlap = minimum_overlap;
            params.reserved0 = kRelationSize;
            enqueue_launch<Observe>(
                trace, pipeline, d_params.ptr, &params,
                static_cast<std::uint32_t>(query_count));
        }
        enqueue_relation_compaction<Observe>(
            trace, compaction_function, d_rows.ptr, d_unique_rows.ptr,
            d_control.ptr, d_keys.ptr, d_max_key_seen.ptr,
            d_unique_count.ptr, kRelationRawCapacity, kRelationSize,
            kRelationRawCapacity, 0);
        traced_d2d<Observe>(
            trace, d_control.ptr + sizeof(std::uint32_t),
            d_unique_count.ptr, sizeof(std::uint32_t), 0);
        traced_d2h<Observe>(
            trace, h_control.pointer, d_control.ptr,
            4 * sizeof(std::uint32_t), 0);
        traced_sync<Observe>(trace, 0);
        const auto raw_count = h_control.pointer[0];
        const auto unique_count = h_control.pointer[1];
        const auto overflow = h_control.pointer[2];
        const auto status = h_control.pointer[3];
        if (overflow || status || raw_count > kRelationRawCapacity
                || unique_count > kRelationSize) {
            if constexpr (Observe)
                throw ObservedRelationDeviceStatusFailure(
                    raw_count, unique_count, overflow, status, trace,
                    dynamic_input);
            throw std::runtime_error(
                "Direct relation status rejected before application output");
        }
        traced_d2h<Observe>(
            trace, h_rows.pointer, d_unique_rows.ptr,
            sizeof(RelationRow) * unique_count, 0);
        traced_sync<Observe>(trace, 0);
        std::vector<std::pair<std::uint32_t, std::uint32_t>> canonical_rows;
        canonical_rows.reserve(unique_count);
        for (std::uint32_t index = 0; index < unique_count; ++index)
            canonical_rows.emplace_back(
                h_rows.pointer[index].source_id, h_rows.pointer[index].item_id);
        std::sort(canonical_rows.begin(), canonical_rows.end());
        if (canonical_rows.size() != kRelationSize)
            throw std::runtime_error("Direct relation row-count mismatch");
        std::uint32_t expected = 0;
        for (const auto& row : canonical_rows) {
            if (row.first != expected || row.second != expected)
                throw std::runtime_error("Direct relation oracle mismatch");
            ++expected;
        }
        RelationOutput value{std::move(canonical_rows), raw_count, unique_count,
                             status, overflow};
        if constexpr (Observe)
            return ObservedRelationOutput{
                std::move(value), trace, dynamic_input};
        else
            return value;
    }

    RelationOutput execute() { return execute_core<false>(); }
    ObservedRelationOutput execute_observed() { return execute_core<true>(); }
};

struct TriangleOutput {
    std::uint64_t reduced = 0;
    std::uint32_t status = 0;
};

struct ObservedTriangleOutput {
    TriangleOutput value;
    OperationTrace trace;
    DynamicInputTrace dynamic_input;
};

struct PreparedTriangleScalar {
    const Pipeline& pipeline;
    std::vector<float3> vertices;
    std::vector<Ray> rays;
    std::vector<std::uint64_t> weights;
    Accel accel;
    DeviceBuffer d_rays, d_weights, d_per_ray, d_reduced, d_status, d_params;
    PinnedHost<Params> h_params;
    PinnedHost<std::uint32_t> h_status;
    PinnedHost<std::uint64_t> h_reduced;
    PinnedHost<Ray> h_dynamic_rays;
    PinnedHost<std::uint64_t> h_dynamic_weights;
    bool dynamic_input_ready = false;
    std::uint64_t dynamic_input_generation = 0;

    PreparedTriangleScalar(
            OptixDeviceContext context, const Pipeline& owned_pipeline,
             std::vector<float3> input_vertices, std::vector<Ray> input_rays,
             std::vector<std::uint64_t> input_weights)
        : pipeline(owned_pipeline), vertices(std::move(input_vertices)),
          rays(std::move(input_rays)), weights(std::move(input_weights)),
          accel(triangle_accel(context, vertices)),
          d_per_ray(sizeof(std::uint64_t) * rays.size()),
          d_reduced(sizeof(std::uint64_t)), d_status(sizeof(std::uint32_t)),
          d_params(sizeof(Params)), h_params(), h_status(), h_reduced(),
          h_dynamic_rays(kTriangleSize), h_dynamic_weights(kTriangleSize) {}

    template <bool Observe>
    auto materialize_dynamic_input() {
        using Trace = std::conditional_t<Observe, DynamicInputTrace,
                                         NoMeasurementTrace>;
        Trace trace;
        if constexpr (Observe) {
            trace.prepared_input_reused = dynamic_input_ready;
            trace.dynamic_input_generation = dynamic_input_generation;
        }
        if (dynamic_input_ready) return trace;
        std::copy(rays.begin(), rays.end(), h_dynamic_rays.pointer);
        std::copy(weights.begin(), weights.end(), h_dynamic_weights.pointer);
        d_rays = upload_dynamic_async<Observe>(
            trace, h_dynamic_rays.pointer, rays.size(), 0);
        d_weights = upload_dynamic_async<Observe>(
            trace, h_dynamic_weights.pointer, weights.size(), 0);
        Params& params = *h_params.pointer;
        params = {};
        params.traversable = accel.handle;
        params.query_count = kTriangleSize;
        params.tmin = 0.0f;
        params.tmax = 2.0f;
        params.rays = reinterpret_cast<const Ray*>(d_rays.ptr);
        params.weights = reinterpret_cast<const std::uint64_t*>(d_weights.ptr);
        params.per_ray = reinterpret_cast<std::uint64_t*>(d_per_ray.ptr);
        params.weighted_sum = reinterpret_cast<std::uint64_t*>(d_reduced.ptr);
        params.status = reinterpret_cast<std::uint32_t*>(d_status.ptr);
        dynamic_input_ready = true;
        ++dynamic_input_generation;
        if constexpr (Observe)
            trace.dynamic_input_generation = dynamic_input_generation;
        if constexpr (Observe) if (trace.dynamic_device_upload_call_count == 0
                || trace.dynamic_accel_build_count != 0
                || trace.dynamic_explicit_sync_count != 0)
            throw std::runtime_error(
                "Direct triangle dynamic-input materialization drift");
        return trace;
    }

    template <bool Observe>
    auto execute_core() {
        const auto dynamic_input = materialize_dynamic_input<Observe>();
        using Trace = std::conditional_t<Observe, OperationTrace,
                                         NoMeasurementTrace>;
        Trace trace;
        CU_CHECK(cuMemsetD8Async(d_per_ray.ptr, 0, d_per_ray.bytes, 0));
        CU_CHECK(cuMemsetD8Async(d_reduced.ptr, 0, d_reduced.bytes, 0));
        CU_CHECK(cuMemsetD8Async(d_status.ptr, 0, d_status.bytes, 0));
        enqueue_launch<Observe>(
            trace, pipeline, d_params.ptr, h_params.pointer, kTriangleSize);
        traced_d2h<Observe>(
            trace, h_status.pointer, d_status.ptr, sizeof(std::uint32_t), 0);
        traced_sync<Observe>(trace, 0);
        if (*h_status.pointer != 0)
            throw std::runtime_error("Direct triangle status rejected before output");
        traced_d2h<Observe>(
            trace, h_reduced.pointer, d_reduced.ptr, sizeof(std::uint64_t), 0);
        traced_sync<Observe>(trace, 0);
        if (*h_reduced.pointer != 65530)
            throw std::runtime_error("Direct triangle scalar oracle mismatch");
        TriangleOutput value{*h_reduced.pointer, *h_status.pointer};
        if constexpr (Observe)
            return ObservedTriangleOutput{value, trace, dynamic_input};
        else
            return value;
    }

    TriangleOutput execute() { return execute_core<false>(); }
    ObservedTriangleOutput execute_observed() { return execute_core<true>(); }
};

struct Arguments {
    std::string worker_id;
    std::string task;
    std::string regime;
    std::string freeze_sha256;
    std::string authority_sha256;
    std::string runtime_manifest_sha256;
    std::string device_source;
    std::string optix_include;
    std::string cuda_include;
    std::string ptx;
    std::string ptx_sha256;
    std::string compaction_cubin;
    std::string compaction_cubin_sha256;
    std::string build_ptx_output;
    std::string compute_architecture;
    bool local_untimed = false;
    bool local_untimed_build = false;
};

void require_formal_runtime_preflight_receipt(
        const std::string& runtime_manifest_sha256) {
    // Accidental/direct-entry guard only.  These unkeyed hashes do not
    // authenticate against a malicious owner; exact-byte external review and
    // the independent raw recount remain the scientific trust boundary.
    const char* path_text = std::getenv(
        "GOAL5802_RUNTIME_PREFLIGHT_RECEIPT_PATH");
    const char* file_sha_text = std::getenv(
        "GOAL5802_RUNTIME_PREFLIGHT_RECEIPT_FILE_SHA256");
    const char* self_sha_text = std::getenv(
        "GOAL5802_RUNTIME_PREFLIGHT_SHA256");
    if (!path_text || !file_sha_text || !self_sha_text
            || std::strlen(file_sha_text) != 64
            || std::strlen(self_sha_text) != 64
            || runtime_manifest_sha256.size() != 64)
        throw std::runtime_error(
            "formal Direct worker preflight gate is absent");
    const std::string path(path_text);
    const auto identity = loaded_regular_file_identity(
        path, "formal runtime preflight receipt");
    if (identity.sha256 != file_sha_text)
        throw std::runtime_error(
            "formal Direct worker preflight file identity differs");
    const std::string payload = read_file(path);
    const auto require_exact_line = [&](const std::string& line) {
        const std::string needle = "\n" + line + "\n";
        const auto first = payload.find(needle);
        if (first == std::string::npos
                || payload.find(needle, first + needle.size())
                    != std::string::npos)
            throw std::runtime_error(
                "formal Direct worker preflight receipt field differs");
    };
    require_exact_line(
        "  \"schema\": \"rtdl.goal5802.formal_runtime_preflight.v1\",");
    require_exact_line(
        "  \"status\": \"PASS__LIVE_TARGET_AND_CROSS_ARM_NVRTC_BEFORE_WORKER_ZERO\",");
    require_exact_line(
        "  \"runtime_manifest_file_sha256\": \""
        + runtime_manifest_sha256 + "\",");
    require_exact_line(
        "  \"preflight_sha256\": \"" + std::string(self_sha_text) + "\",");
    for (const char* field : {
            "clock_read_count", "registered_performance_timing_count",
            "gpu_kernel_launch_count", "formal_worker_count"})
        require_exact_line("  \"" + std::string(field) + "\": 0,");
}

void consume_live_controller_capability(
        const std::string& worker_id,
        const std::string& runtime_manifest_sha256) {
    const char* parent_text = std::getenv("GOAL5802_FORMAL_CONTROLLER_PID");
    const char* file_sha_text = std::getenv(
        "GOAL5802_RUNTIME_PREFLIGHT_RECEIPT_FILE_SHA256");
    const char* self_sha_text = std::getenv(
        "GOAL5802_RUNTIME_PREFLIGHT_SHA256");
    if (!parent_text || !file_sha_text || !self_sha_text
            || worker_id.empty())
        throw std::runtime_error(
            "formal Direct live controller capability inputs are absent");
    if (!std::all_of(
            worker_id.begin(), worker_id.end(), [](unsigned char value) {
                return std::isalnum(value) || value == '_';
            }))
        throw std::runtime_error(
            "formal Direct worker id cannot enter capability frame");
    std::string frame;
    if (!std::getline(std::cin, frame))
        throw std::runtime_error(
            "formal Direct live controller capability is absent");
    char extra = '\0';
    if (std::cin.get(extra))
        throw std::runtime_error(
            "formal Direct live controller capability has extra bytes");
    const std::string prefix =
        "{\"controller_pid\":" + std::string(parent_text)
        + ",\"nonce\":\"";
    const std::string suffix =
        "\",\"preflight_receipt_file_sha256\":\""
        + std::string(file_sha_text)
        + "\",\"preflight_sha256\":\"" + std::string(self_sha_text)
        + "\",\"runtime_manifest_sha256\":\""
        + runtime_manifest_sha256
        + "\",\"schema\":\"rtdl.goal5802.live_controller_worker_capability.v1\""
        + ",\"worker_id\":\"" + worker_id + "\"}";
    if (frame.size() != prefix.size() + 64 + suffix.size()
            || frame.compare(0, prefix.size(), prefix) != 0
            || frame.compare(frame.size() - suffix.size(), suffix.size(), suffix)
                != 0)
        throw std::runtime_error(
            "formal Direct live controller capability frame differs");
    const std::string nonce = frame.substr(prefix.size(), 64);
    if (!std::all_of(nonce.begin(), nonce.end(), [](unsigned char value) {
            return (value >= '0' && value <= '9')
                || (value >= 'a' && value <= 'f');
        }))
        throw std::runtime_error(
            "formal Direct live controller nonce differs");
}

Arguments parse_arguments(int argc, char** argv) {
    Arguments result;
    if (argc == 2 && std::string(argv[1]) == "--local-plan") return result;
    std::map<std::string, std::string*> destinations = {
        {"--worker-id", &result.worker_id},
        {"--task", &result.task}, {"--regime", &result.regime},
        {"--freeze-sha256", &result.freeze_sha256},
        {"--authority-sha256", &result.authority_sha256},
        {"--runtime-manifest-sha256", &result.runtime_manifest_sha256},
        {"--device-source", &result.device_source},
        {"--optix-include", &result.optix_include},
        {"--cuda-include", &result.cuda_include},
        {"--ptx", &result.ptx},
        {"--ptx-sha256", &result.ptx_sha256},
        {"--compaction-cubin", &result.compaction_cubin},
        {"--compaction-cubin-sha256", &result.compaction_cubin_sha256},
        {"--build-ptx-output", &result.build_ptx_output},
        {"--compute-architecture", &result.compute_architecture},
    };
    for (int index = 1; index < argc; ++index) {
        const std::string token = argv[index];
        if (token == "--local-untimed-functional") {
            result.local_untimed = true;
            continue;
        }
        if (token == "--local-untimed-build-ptx") {
            result.local_untimed_build = true;
            continue;
        }
        const auto found = destinations.find(token);
        if (found == destinations.end() || index + 1 >= argc)
            throw std::runtime_error("invalid Direct Goal5802 arguments");
        *found->second = argv[++index];
    }
    const bool build_mode = !result.build_ptx_output.empty();
    if (build_mode) {
        if (result.device_source.empty() || result.optix_include.empty()
                || result.cuda_include.empty() || result.task.empty()
                || result.compute_architecture.empty())
            throw std::runtime_error("incomplete Direct Goal5802 build arguments");
    } else if (result.task.empty() || result.ptx.empty()
            || (result.task == kRelationTask && result.compaction_cubin.empty())
            || (result.task == kTriangleTask && !result.compaction_cubin.empty())) {
        throw std::runtime_error("incomplete Direct Goal5802 runtime arguments");
    }
    if (build_mode && !result.local_untimed_build) {
        const char* parent = std::getenv("GOAL5802_BUILD_WORKER_PID");
        const char* authority = std::getenv("GOAL5802_EXECUTION_AUTHORITY_SHA256");
        const char* runtime = std::getenv("GOAL5802_RUNTIME_MANIFEST_SHA256");
        if (result.worker_id.empty() || result.freeze_sha256.size() != 64
                || result.authority_sha256.size() != 64
                || result.runtime_manifest_sha256.size() != 64 || !parent
                || std::to_string(::getppid()) != parent || !authority
                || std::strlen(authority) != 64
                || !runtime || std::strlen(runtime) != 64
                || result.authority_sha256 != authority
                || result.runtime_manifest_sha256 != runtime)
            throw std::runtime_error(
                "formal Direct BUILD_COLD lacks two-key build-worker authority");
        require_formal_runtime_preflight_receipt(
            result.runtime_manifest_sha256);
    } else if (!build_mode && !result.local_untimed) {
        const char* parent = std::getenv("GOAL5802_FORMAL_CONTROLLER_PID");
        const char* authority = std::getenv("GOAL5802_EXECUTION_AUTHORITY_SHA256");
        const char* runtime = std::getenv("GOAL5802_RUNTIME_MANIFEST_SHA256");
        const char* freeze = std::getenv("GOAL5802_FREEZE_FILE_SHA256");
        if (result.worker_id.empty() || result.freeze_sha256.size() != 64
                || result.authority_sha256.size() != 64
                || result.runtime_manifest_sha256.size() != 64
                || result.ptx_sha256.size() != 64
                || (result.task == kRelationTask
                    && result.compaction_cubin_sha256.size() != 64)
                || (result.task == kTriangleTask
                    && !result.compaction_cubin_sha256.empty())
                || !parent || std::to_string(::getppid()) != parent || !authority
                || std::strlen(authority) != 64
                || !runtime || std::strlen(runtime) != 64
                || !freeze || std::strlen(freeze) != 64
                || result.authority_sha256 != authority
                || result.runtime_manifest_sha256 != runtime
                || result.freeze_sha256 != freeze)
            throw std::runtime_error("formal Direct worker lacks two-key controller authority");
        require_formal_runtime_preflight_receipt(
            result.runtime_manifest_sha256);
        consume_live_controller_capability(
            result.worker_id, result.runtime_manifest_sha256);
    }
    return result;
}

void json_u64_array(std::ostream& output, const std::vector<std::uint64_t>& values) {
    output << '[';
    for (std::size_t index = 0; index < values.size(); ++index) {
        if (index) output << ',';
        output << values[index];
    }
    output << ']';
}

void json_relation_rows(
        std::ostream& output,
        const std::vector<std::pair<std::uint32_t, std::uint32_t>>& rows) {
    output << '[';
    for (std::size_t index = 0; index < rows.size(); ++index) {
        if (index) output << ',';
        output << '[' << rows[index].first << ',' << rows[index].second << ']';
    }
    output << ']';
}

void json_dynamic_input_receipt(
        std::ostream& output, const DynamicInputTrace& row) {
    output << "{\"prepared_input_reused\":"
               << (row.prepared_input_reused ? "true" : "false")
               << ",\"dynamic_device_upload_call_count\":"
               << row.dynamic_device_upload_call_count
               << ",\"dynamic_device_upload_bytes\":"
               << row.dynamic_device_upload_bytes
               << ",\"dynamic_accel_build_count\":"
               << row.dynamic_accel_build_count
               << ",\"dynamic_explicit_sync_count\":"
               << row.dynamic_explicit_sync_count
               << ",\"dynamic_blocking_upload_call_count\":"
               << row.dynamic_blocking_upload_call_count
               << ",\"dynamic_input_generation\":"
               << row.dynamic_input_generation << '}';
}

void json_dynamic_input_receipts(
        std::ostream& output, const std::vector<DynamicInputTrace>& rows) {
    output << '[';
    for (std::size_t index = 0; index < rows.size(); ++index) {
        if (index) output << ',';
        json_dynamic_input_receipt(output, rows[index]);
    }
    output << ']';
}

void json_operation_trace(std::ostream& output, const OperationTrace& row) {
    output << "{\"optix_launch_count\":" << row.optix_launch_count
           << ",\"compaction_launch_count\":" << row.compaction_launch_count
           << ",\"async_h2d_call_count\":" << row.async_h2d_call_count
           << ",\"async_h2d_bytes\":" << row.async_h2d_bytes
           << ",\"async_d2h_call_count\":" << row.async_d2h_call_count
           << ",\"async_d2h_bytes\":" << row.async_d2h_bytes
           << ",\"async_d2d_call_count\":" << row.async_d2d_call_count
           << ",\"async_d2d_bytes\":" << row.async_d2d_bytes
           << ",\"host_blocking_boundary_count\":"
           << row.host_blocking_boundary_count << '}';
}

void json_operation_traces(
        std::ostream& output, const std::vector<OperationTrace>& rows) {
    output << '[';
    for (std::size_t index = 0; index < rows.size(); ++index) {
        if (index) output << ',';
        json_operation_trace(output, rows[index]);
    }
    output << ']';
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc == 2 && std::string(argv[1]) == "--local-nvrtc-identity") {
            const MinimalNvrtcCompileKat compile_kat =
                run_minimal_nvrtc_compile_kat();
            const LoadedNvrtcIdentity identity = loaded_nvrtc_identity();
            const LoadedRegularFileIdentity builtins =
                loaded_nvrtc_builtins_identity_from_proc_maps();
            std::cout
                << "{\"schema\":\"rtdl.goal5802.direct_loaded_nvrtc_identity.v2\","
                << "\"status\":\"PASS__UNTIMED_NO_GPU\","
                << "\"discovery\":\"MINIMAL_NVRTC_COMPILE_THEN_"
                   "DLADDR_NVRTCVERSION_AND_PROC_SELF_MAPS_UNIQUE_BUILTINS_"
                   "REALPATH_OPEN_NOFOLLOW_FSTAT\","
                << "\"loaded_library_path\":\""
                << json_escape(identity.resolved_path) << "\","
                << "\"loaded_library_bytes\":" << identity.bytes << ','
                << "\"loaded_library_sha256\":\"" << identity.sha256 << "\","
                << "\"loaded_builtins_path\":\""
                << json_escape(builtins.resolved_path) << "\","
                << "\"loaded_builtins_bytes\":" << builtins.bytes << ','
                << "\"loaded_builtins_sha256\":\"" << builtins.sha256
                << "\","
                << "\"nvrtc_version\":{\"major\":"
                << identity.version_major << ",\"minor\":"
                << identity.version_minor << "},"
                << "\"nvrtc_compile_kat\":{\"source_utf8\":\""
                << json_escape(compile_kat.source_utf8) << "\","
                << "\"source_sha256\":\"" << compile_kat.source_sha256
                << "\",\"compile_options\":[\"--std=c++11\"],"
                << "\"product_bytes\":" << compile_kat.product_bytes << ','
                << "\"product_sha256\":\"" << compile_kat.product_sha256
                << "\",\"compile_success\":"
                << (compile_kat.compile_success ? "true" : "false") << ','
                << "\"program_destroyed\":"
                << (compile_kat.program_destroyed ? "true" : "false") << "},"
                << "\"clock_read_count\":0,"
                << "\"registered_performance_timing_count\":0,"
                << "\"gpu_kernel_launch_count\":0,"
                << "\"formal_worker_count\":0}\n";
            return 0;
        }
        if (argc == 2 && std::string(argv[1]) == "--local-sha256-kat") {
            const std::string observed = sha256_bytes("abc");
            const std::string expected =
                "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
            if (observed != expected)
                throw std::runtime_error("Direct retained-byte SHA-256 KAT failed");
            std::cout
                << "{\"schema\":\"rtdl.goal5802.direct_sha256_kat.v1\","
                << "\"status\":\"PASS__UNTIMED_NO_GPU\","
                << "\"input_utf8\":\"abc\",\"sha256\":\"" << observed
                << "\",\"registered_performance_timing_count\":0,"
                << "\"gpu_kernel_launch_count\":0}\n";
            return 0;
        }
        const Arguments args = parse_arguments(argc, argv);
        if (args.task.empty()) {
            std::cout
                << "{\"schema\":\"rtdl.goal5802.direct_scalar.plan.v1\","
                << "\"status\":\"PASS__LOCAL_PLAN_ONLY__ZERO_TIMINGS\","
                << "\"legacy_goal5798_worker_used\":false,"
                << "\"triangle_per_ray_d2h_bytes\":0,"
                << "\"triangle_status_d2h_bytes\":4,"
                << "\"triangle_scalar_d2h_bytes\":8,"
                << "\"triangle_sync_count\":2,"
                << "\"comparative_load_uses_prebuilt_ptx\":true,"
                << "\"comparative_load_invokes_nvrtc\":false,"
                << "\"formal_execution_authorized\":false}\n";
            return 0;
        }

        if (!args.build_ptx_output.empty()) {
            const std::string source = read_file(args.device_source);
            const std::string ptx = compile_ptx_exact_arch(
                source, args.device_source, args.optix_include,
                args.cuda_include, args.compute_architecture);
            const std::string ptx_target =
                "sm_" + args.compute_architecture.substr(8);
            std::ifstream existing(args.build_ptx_output, std::ios::binary);
            if (existing.good())
                throw std::runtime_error("Direct BUILD_COLD PTX output already exists");
            std::ofstream built(args.build_ptx_output, std::ios::binary);
            if (!built) throw std::runtime_error("cannot create Direct BUILD_COLD PTX");
            built.write(ptx.data(), static_cast<std::streamsize>(ptx.size()));
            built.close();
            if (!built) throw std::runtime_error("cannot finish Direct BUILD_COLD PTX");
            std::cout
                << "{\"schema\":\"rtdl.goal5802.direct_build_ptx.v1\","
                << "\"status\":\"PASS\",\"task\":\"" << args.task << "\","
                << "\"worker_id\":\"" << args.worker_id << "\","
                << "\"true_nvrtc_compile_executed\":true,"
                << "\"gpu_architecture_option\":\"--gpu-architecture="
                << args.compute_architecture << "\","
                << "\"ptx_target\":\"" << ptx_target << "\","
                << "\"prebuilt_ptx_read\":false,"
                << "\"registered_performance_timing_count\":0}\n";
            return 0;
        }

        const bool relation = args.task == kRelationTask;
        if (!relation && args.task != kTriangleTask)
            throw std::runtime_error("unsupported Direct Goal5802 task");
        const bool formal = !args.local_untimed;
        std::uint64_t admission_ns = 0;
        if (formal) {
            const char* controller_start_text = std::getenv(
                "GOAL5802_CONTROLLER_ENVELOPE_START_NS");
            if (!controller_start_text)
                throw std::runtime_error(
                    "formal Direct controller start clock absent");
            const std::uint64_t controller_start = std::stoull(
                controller_start_text);
            const std::uint64_t now = monotonic_epoch_ns();
            if (controller_start == 0 || now <= controller_start)
                throw std::runtime_error(
                    "formal Direct admission duration invalid");
            admission_ns = now - controller_start;
        }
        const auto input_start = formal ? Clock::now() : Clock::time_point{};
        auto boxes = relation ? relation_boxes() : std::vector<Box>{};
        auto source_boxes = relation ? relation_boxes() : std::vector<Box>{};
        auto vertices = relation ? std::vector<float3>{} : triangle_vertices();
        auto rays = relation ? std::vector<Ray>{} : triangle_rays();
        auto weights = relation ? std::vector<std::uint64_t>{} : triangle_weights();
        const auto input_end = formal ? Clock::now() : Clock::time_point{};
        const std::uint64_t input_ns = formal
            ? between_ns(input_start, input_end) : 0;

        const auto deployment_start = formal ? Clock::now() : Clock::time_point{};
        const auto load_start = deployment_start;
        const std::string ptx = read_file(args.ptx);
        if (ptx.empty() || ptx.find(".version") == std::string::npos)
            throw std::runtime_error("Goal5802 Direct matched prebuilt PTX is invalid");
        const std::string compaction_cubin = relation
            ? read_file(args.compaction_cubin) : std::string{};
        if (relation && (compaction_cubin.size() < 4
                || compaction_cubin.compare(0, 4, "\x7f" "ELF") != 0))
            throw std::runtime_error(
                "Goal5802 Direct target compaction cubin is invalid");
        const auto load_end = formal ? Clock::now() : Clock::time_point{};
        const std::uint64_t load_ns = formal ? between_ns(load_start, load_end) : 0;
        const auto prepare_start = load_end;
        auto context = std::make_unique<ComparativeContext>();
        OPTIX_CHECK(optixDeviceContextSetCacheEnabled(context->optix, 0));
        auto pipeline = build_pipeline(context->optix, ptx, relation);
        std::unique_ptr<RelationCompactionModule> compaction_module;
        if (relation)
            compaction_module = std::make_unique<RelationCompactionModule>(
                compaction_cubin);
        std::unique_ptr<PreparedRelationScalarContract> relation_owner;
        std::unique_ptr<PreparedTriangleScalar> triangle_owner;
        if (relation)
             relation_owner = std::make_unique<PreparedRelationScalarContract>(
                 context->optix, *pipeline, compaction_module->function,
                 std::move(boxes), std::move(source_boxes),
                 kRelationMinimumOverlap);
        else
            triangle_owner = std::make_unique<PreparedTriangleScalar>(
                context->optix, *pipeline, std::move(vertices), std::move(rays),
                std::move(weights));
        const auto prepare_end = formal ? Clock::now() : Clock::time_point{};
        const std::uint64_t prepare_ns = formal
            ? between_ns(prepare_start, prepare_end) : 0;

        std::vector<std::uint64_t> durations;
        RelationOutput relation_output;
        TriangleOutput triangle_output;
        OperationTrace observed_operation_trace;
        DynamicInputTrace observed_dynamic_trace;
        bool relation_k_plus_one_failure_observed = false;
        std::uint32_t relation_k_plus_one_raw_count = 0;
        std::uint32_t relation_k_plus_one_unique_count = 0;
        std::uint32_t relation_k_plus_one_overflow = 0;
        std::uint32_t relation_k_plus_one_status = 0;
        std::uint32_t relation_k_plus_one_minimum_overlap_bits = 0;
        std::uint32_t relation_k_plus_one_semantic_capacity = 0;
        std::uint32_t relation_k_plus_one_raw_capacity = 0;
        OperationTrace relation_k_plus_one_trace;
        DynamicInputTrace relation_k_plus_one_dynamic_trace;
        std::uint64_t deployment_execute_ns = 0;
        std::uint64_t steady_execute_ns = 0;
        std::uint64_t warmup_execute_ns = 0;
        std::uint64_t measurement_evidence_ns = 0;
        std::vector<DynamicInputTrace> dynamic_input_receipts;
        std::vector<OperationTrace> untimed_observed_operation_traces;
        auto retain_dynamic_receipt = [&]() {
            const auto evidence_start = formal ? Clock::now() : Clock::time_point{};
            if (args.local_untimed) {
                dynamic_input_receipts.push_back(observed_dynamic_trace);
            } else {
                const bool reused = !dynamic_input_receipts.empty();
                dynamic_input_receipts.push_back({
                    reused,
                    reused ? 0u : 2u,
                    reused ? 0u : (relation ? 212992u : 524288u),
                    reused ? 0u : (relation ? 1u : 0u),
                    0u, 0u, 1u,
                });
            }
            if (formal)
                measurement_evidence_ns += elapsed_ns(evidence_start);
        };
        auto execute = [&]() {
            // Release the previous 4096-row vector before the clock starts;
            // move-assignment below must never hide prior-result destruction.
            if (relation_owner) {
                const auto release_start = Clock::now();
                relation_output = RelationOutput{};
                measurement_evidence_ns += elapsed_ns(release_start);
            }
            const auto start = Clock::now();
            if (relation_owner) relation_output = relation_owner->execute();
            else triangle_output = triangle_owner->execute();
            const auto duration = elapsed_ns(start);
            retain_dynamic_receipt();
            return duration;
        };
        if (args.local_untimed) {
            // The preworker KAT must observe both first materialization and
            // exact-owner reuse through the same template core as formal.
            for (int execution_index = 0; execution_index < 2;
                    ++execution_index) {
                if (relation_owner) {
                    auto observed = relation_owner->execute_observed();
                    relation_output = std::move(observed.value);
                    observed_operation_trace = observed.trace;
                    observed_dynamic_trace = observed.dynamic_input;
                } else {
                    auto observed = triangle_owner->execute_observed();
                    triangle_output = observed.value;
                    observed_operation_trace = observed.trace;
                    observed_dynamic_trace = observed.dynamic_input;
                }
                untimed_observed_operation_traces.push_back(
                    observed_operation_trace);
                retain_dynamic_receipt();
            }
            if (relation_owner) {
                auto hostile_owner =
                    std::make_unique<PreparedRelationScalarContract>(
                        context->optix, *pipeline,
                        compaction_module->function,
                        relation_k_plus_one_indexed(),
                        relation_k_plus_one_sources(),
                        kRelationMinimumOverlap);
                try {
                    static_cast<void>(hostile_owner->execute_observed());
                } catch (const ObservedRelationDeviceStatusFailure& failure) {
                    relation_k_plus_one_failure_observed = true;
                    relation_k_plus_one_raw_count = failure.raw_count;
                    relation_k_plus_one_unique_count = failure.unique_count;
                    relation_k_plus_one_overflow = failure.overflow;
                    relation_k_plus_one_status = failure.status;
                    relation_k_plus_one_trace = failure.trace;
                    relation_k_plus_one_dynamic_trace = failure.dynamic_input;
                }
                if (!relation_k_plus_one_failure_observed)
                    throw std::runtime_error(
                        "Direct K+1 semantic-capacity workload did not fail");
                for (unsigned orientation = 0; orientation < 2; ++orientation) {
                    const Params& actual = hostile_owner->h_params.pointer[
                        orientation];
                    const auto overlap_bits = f32_bits(actual.minimum_overlap);
                    if (orientation == 0) {
                        relation_k_plus_one_minimum_overlap_bits = overlap_bits;
                        relation_k_plus_one_semantic_capacity = actual.reserved0;
                        relation_k_plus_one_raw_capacity = actual.raw_row_capacity;
                    } else if (overlap_bits
                            != relation_k_plus_one_minimum_overlap_bits
                            || actual.reserved0
                            != relation_k_plus_one_semantic_capacity
                            || actual.raw_row_capacity
                            != relation_k_plus_one_raw_capacity) {
                        throw std::runtime_error(
                            "Direct K+1 orientation parameters differ");
                    }
                }
                if (relation_k_plus_one_raw_count != kRelationSize + 1
                        || relation_k_plus_one_unique_count != kRelationSize + 1
                        || relation_k_plus_one_overflow != 1
                        || relation_k_plus_one_status != 0xffff5102U
                        || relation_k_plus_one_minimum_overlap_bits
                        != f32_bits(kRelationMinimumOverlap)
                        || relation_k_plus_one_semantic_capacity != kRelationSize
                        || relation_k_plus_one_raw_capacity
                        != kRelationRawCapacity
                        || relation_k_plus_one_raw_count >= kRelationRawCapacity
                        || relation_k_plus_one_trace.async_d2h_call_count != 1
                        || relation_k_plus_one_trace.async_d2h_bytes != 16
                        || relation_k_plus_one_trace.host_blocking_boundary_count != 1)
                    throw std::runtime_error(
                        "Direct K+1 semantic-capacity evidence differs");
            }
        } else if (args.regime == "STEADY_E2E") {
            for (int index = 0; index < kSteadyWarmups; ++index)
                warmup_execute_ns += execute();
            for (int index = 0; index < kSteadyRepetitions; ++index) {
                const auto duration = execute();
                durations.push_back(duration);
                steady_execute_ns += duration;
            }
        } else if (args.regime == "PREPARE") {
            durations.push_back(prepare_ns);
            if (relation_owner) {
                const auto release_start = Clock::now();
                relation_output = RelationOutput{};
                measurement_evidence_ns += elapsed_ns(release_start);
            }
            const auto execute_start = Clock::now();
            if (relation_owner) relation_output = relation_owner->execute();
            else triangle_output = triangle_owner->execute();
            const auto execute_end = Clock::now();
            retain_dynamic_receipt();
            deployment_execute_ns = between_ns(execute_start, execute_end);
        } else if (args.regime == "DEPLOYMENT_COLD") {
            const auto execute_start = prepare_end;
            if (relation_owner) relation_output = relation_owner->execute();
            else triangle_output = triangle_owner->execute();
            const auto deployment_end = Clock::now();
            retain_dynamic_receipt();
            deployment_execute_ns = between_ns(execute_start, deployment_end);
            durations.push_back(between_ns(deployment_start, deployment_end));
        } else {
            throw std::runtime_error("unsupported Direct Goal5802 regime");
        }

        const auto evidence_validation_start = formal
            ? Clock::now() : Clock::time_point{};
        if (args.local_untimed) {
            if (untimed_observed_operation_traces.size() != 2)
                throw std::runtime_error(
                    "Direct untimed operation trace count drift");
            for (const auto& trace : untimed_observed_operation_traces) {
                if (relation && (trace.optix_launch_count != 2
                        || trace.compaction_launch_count != 1
                        || trace.async_h2d_call_count != 2
                        || trace.async_h2d_bytes != 240
                        || trace.async_d2h_call_count != 2
                        || trace.async_d2h_bytes != 32784
                        || trace.async_d2d_call_count != 1
                        || trace.async_d2d_bytes != 4
                        || trace.host_blocking_boundary_count != 2))
                    throw std::runtime_error(
                        "Direct relation observed operation trace drift");
                if (!relation && (trace.optix_launch_count != 1
                        || trace.compaction_launch_count != 0
                        || trace.async_h2d_call_count != 1
                        || trace.async_h2d_bytes != 120
                        || trace.async_d2h_call_count != 2
                        || trace.async_d2h_bytes != 12
                        || trace.async_d2d_call_count != 0
                        || trace.async_d2d_bytes != 0
                        || trace.host_blocking_boundary_count != 2))
                    throw std::runtime_error(
                        "Direct triangle observed operation trace drift");
            }
        }
        if (formal)
            measurement_evidence_ns += elapsed_ns(evidence_validation_start);

        const auto close_start = formal ? Clock::now() : Clock::time_point{};
        relation_owner.reset();
        triangle_owner.reset();
        pipeline.reset();
        compaction_module.reset();
        context.reset();
        const auto close_end = formal ? Clock::now() : Clock::time_point{};
        const std::uint64_t close_ns = formal
            ? between_ns(close_start, close_end) : 0;
        const auto identity_start = formal ? Clock::now() : Clock::time_point{};
        const std::string retained_ptx_sha256 = sha256_bytes(ptx);
        const std::string retained_compaction_cubin_sha256 = relation
            ? sha256_bytes(compaction_cubin) : std::string{};
        if (formal && retained_ptx_sha256 != args.ptx_sha256)
            throw std::runtime_error(
                "Direct retained executed PTX identity differs");
        if (formal && relation && retained_compaction_cubin_sha256
                != args.compaction_cubin_sha256)
            throw std::runtime_error(
                "Direct retained compaction module identity differs");
        const auto identity_end = formal ? Clock::now() : Clock::time_point{};
        const std::uint64_t post_identity_ns = formal
            ? between_ns(identity_start, identity_end) : 0;

        std::ostringstream output;
        output << "{\"schema\":\"rtdl.goal5802.direct_scalar.worker.v1\","
               << "\"status\":\"PASS\",\"arm\":\"A_DIRECT_CUDA_OPTIX\","
               << "\"worker_id\":\"" << args.worker_id << "\","
               << "\"freeze_file_sha256\":\"" << args.freeze_sha256 << "\","
               << "\"execution_authority_sha256\":\"" << args.authority_sha256 << "\","
               << "\"runtime_manifest_sha256\":\""
               << args.runtime_manifest_sha256 << "\","
               << "\"task\":\"" << args.task << "\","
               << "\"regime\":\"" << (args.local_untimed ? "LOCAL_UNTIMED" : args.regime)
               << "\",\"registered_performance_timing_count\":" << durations.size()
               << ",\"phase_durations_ns\":{\"process_startup_and_admission\":"
               << (formal ? std::to_string(admission_ns) : "null")
               << ",\"input_materialization\":"
               << (formal ? std::to_string(input_ns) : "null")
               << ",\"load_or_deploy\":"
               << (formal ? std::to_string(load_ns) : "null")
               << ",\"prepare\":"
               << (formal ? std::to_string(prepare_ns) : "null")
               << ",\"steady_warmups\":"
               << (formal ? std::to_string(warmup_execute_ns) : "null")
               << ",\"complete_execute\":"
                << (formal && args.regime == "DEPLOYMENT_COLD"
                   ? std::to_string(deployment_execute_ns)
                   : formal && args.regime == "STEADY_E2E"
                       ? std::to_string(steady_execute_ns)
                        : formal && args.regime == "PREPARE"
                            ? std::to_string(deployment_execute_ns) : "null")
               << ",\"measurement_evidence_materialization\":"
               << (formal ? std::to_string(measurement_evidence_ns) : "null")
               << ",\"close\":"
               << (formal ? std::to_string(close_ns) : "null")
               << ",\"post_execution_identity_validation\":"
               << (formal ? std::to_string(post_identity_ns) : "null")
               << "},\"execute_or_regime_durations_ns\":";
        json_u64_array(output, durations);
        output << ",\"execution_lifecycle_receipts\":";
        json_dynamic_input_receipts(output, dynamic_input_receipts);
        if (args.local_untimed) {
            output << ",\"untimed_observed_operation_traces\":";
            json_operation_traces(output, untimed_observed_operation_traces);
        }
        if (relation) {
            output << ",\"correctness\":{\"oracle_exact\":true,"
                   << "\"canonical_row_count\":" << relation_output.rows.size()
                   << ",\"canonical_rows\":";
            json_relation_rows(output, relation_output.rows);
            output
                   << ",\"raw_event_count\":" << relation_output.raw_count
                   << ",\"semantic_unique_count\":"
                   << relation_output.unique_count
                   << ",\"device_status\":" << relation_output.status
                   << ",\"device_overflow\":" << relation_output.overflow << "},";
            if (args.local_untimed) {
                output << "\"relation_k_plus_one_hostile\":{"
                   << "\"schema\":\"rtdl.goal5802.relation_k_plus_one_"
                      "device_failure.v1\","
                   << "\"task\":\"" << kRelationTask << "\","
                   << "\"packed_input_sha256\":\""
                   << sha256_bytes(relation_k_plus_one_packed_input()) << "\","
                   << "\"indexed_count\":1,\"source_count\":"
                   << (kRelationSize + 2) << ","
                   << "\"raw_count_below_raw_capacity\":true,"
                   << "\"compact_control\":{\"raw_event_count\":"
                   << relation_k_plus_one_raw_count
                   << ",\"unique_event_count\":"
                   << relation_k_plus_one_unique_count
                   << ",\"overflowed\":" << relation_k_plus_one_overflow
                   << ",\"status\":" << relation_k_plus_one_status
                   << ",\"semantic_capacity\":" << kRelationSize
                   << ",\"raw_capacity\":" << kRelationRawCapacity
                   << ",\"control_d2h_bytes\":16},"
                   << "\"executed_parameter_projection\":{"
                   << "\"orientation_count\":2,"
                   << "\"minimum_overlap_f32_bits\":"
                   << relation_k_plus_one_minimum_overlap_bits
                   << ",\"semantic_capacity\":"
                   << relation_k_plus_one_semantic_capacity
                   << ",\"raw_capacity\":"
                   << relation_k_plus_one_raw_capacity << "},"
                   << "\"status_output_commit_blocking_boundary_count\":1,"
                   << "\"application_output_exposed\":false,"
                   << "\"application_output_d2h_call_count\":0,"
                   << "\"application_output_d2h_bytes\":0,"
                   << "\"observed_operation_trace\":";
            json_operation_trace(output, relation_k_plus_one_trace);
            output << ",\"dynamic_input_receipt\":";
            json_dynamic_input_receipt(
                output, relation_k_plus_one_dynamic_trace);
                output << "},";
            }
            output << "\"operation_ledger\":{\"optix_launch_count\":"
                   << 2 << ","
                   << "\"semantic_compaction_launch_count\":"
                   << 1 << ","
                   << "\"semantic_compaction_key_capacity\":"
                   << kRelationRawCapacity << ","
                   << "\"semantic_compaction_scratch_bytes\":"
                   << (sizeof(std::uint64_t) * kRelationRawCapacity
                       + sizeof(RelationRow) * kRelationSize
                       + 2 * sizeof(std::uint32_t)) << ","
                   << "\"callback_status_kernel_launch_count\":0,"
                   << "\"checked_product_kernel_launch_count\":0,"
                   << "\"compact_control_finalizer_kernel_launch_count\":0,"
                   << "\"total_auxiliary_cuda_kernel_launch_count\":1,"
                   << "\"execution_parameter_h2d_bytes\":240,"
                   << "\"execution_parameter_h2d_copy_call_count\":2,"
                   << "\"stream_ordered_memset_call_count\":4,"
                   << "\"status_d2h_copy_call_count\":1,"
                   << "\"output_d2h_copy_call_count\":1,"
                   << "\"async_h2d_call_count\":"
                   << 2 << ","
                   << "\"async_h2d_bytes\":"
                   << 240 << ","
                   << "\"async_d2h_call_count\":"
                   << 2 << ","
                   << "\"compact_status_control_d2h_bytes\":"
                   << (4 * sizeof(std::uint32_t)) << ","
                   << "\"application_output_d2h_bytes\":"
                   << (static_cast<std::uint64_t>(relation_output.unique_count)
                       * sizeof(RelationRow)) << ","
                   << "\"user_visible_output_bytes\":"
                   << (static_cast<std::uint64_t>(relation_output.rows.size())
                       * sizeof(RelationRow)) << ","
                   << "\"total_success_d2h_bytes\":"
                   << 32784 << ","
                   << "\"status_output_commit_blocking_boundary_count\":"
                   << 2 << ","
                   << "\"per_ray_d2h_bytes\":0,\"dynamic_input_receipt\":";
            json_dynamic_input_receipt(output, dynamic_input_receipts.back());
            output << ",\"optix_module_disk_cache_enabled\":false,"
                   << "\"optix_validation_mode\":\"OFF\","
                   << "\"optix_log_callback_mode\":\"OFF\","
                   << "\"module_optimization_level\":\"DEFAULT\","
                   << "\"module_debug_level\":\"NONE\","
                   << "\"operation_evidence_source\":\"UNTIMED_OBSERVER_"
                      "SAME_TEMPLATE_CORE_AND_EXACT_SOURCE_AUDIT\","
                   << "\"live_operation_trace_inside_timer\":false}";
        } else {
            output << ",\"correctness\":{\"oracle_exact\":true,"
                   << "\"device_status\":" << triangle_output.status
                   << ",\"reduced_u64\":" << triangle_output.reduced << "},"
                   << "\"operation_ledger\":{\"optix_launch_count\":"
                   << 1 << ","
                   << "\"async_h2d_call_count\":"
                   << 1 << ","
                   << "\"async_h2d_bytes\":"
                   << 120 << ","
                   << "\"async_d2h_call_count\":"
                   << 2 << ","
                   << "\"device_intermediate_per_ray_bytes\":131072,"
                   << "\"device_reset_bytes\":131084,"
                   << "\"h2d_launch_parameter_bytes\":120,"
                   << "\"semantic_compaction_launch_count\":0,"
                   << "\"semantic_compaction_key_capacity\":0,"
                   << "\"semantic_compaction_scratch_bytes\":0,"
                   << "\"callback_status_kernel_launch_count\":0,"
                   << "\"checked_product_kernel_launch_count\":0,"
                   << "\"compact_control_finalizer_kernel_launch_count\":0,"
                   << "\"total_auxiliary_cuda_kernel_launch_count\":0,"
                   << "\"execution_parameter_h2d_bytes\":120,"
                   << "\"execution_parameter_h2d_copy_call_count\":1,"
                   << "\"stream_ordered_memset_call_count\":3,"
                   << "\"status_d2h_copy_call_count\":1,"
                   << "\"output_d2h_copy_call_count\":1,"
                   << "\"compact_status_control_d2h_bytes\":4,"
                   << "\"application_output_d2h_bytes\":8,"
                   << "\"total_success_d2h_bytes\":"
                   << 12 << ","
                   << "\"status_output_commit_blocking_boundary_count\":"
                   << 2 << ","
                   << "\"per_ray_d2h_bytes\":0,\"dynamic_input_receipt\":";
            json_dynamic_input_receipt(output, dynamic_input_receipts.back());
            output << ",\"optix_module_disk_cache_enabled\":false,"
                   << "\"optix_validation_mode\":\"OFF\","
                   << "\"optix_log_callback_mode\":\"OFF\","
                   << "\"module_optimization_level\":\"DEFAULT\","
                   << "\"module_debug_level\":\"NONE\","
                   << "\"operation_evidence_source\":\"UNTIMED_OBSERVER_"
                      "SAME_TEMPLATE_CORE_AND_EXACT_SOURCE_AUDIT\","
                   << "\"live_operation_trace_inside_timer\":false}";
        }
        output << ",\"receipt_serialization_inside_timer\":false,"
               << "\"retained_executed_ptx_sha256\":\""
               << retained_ptx_sha256 << "\",";
        if (relation)
            output << "\"retained_compaction_cubin_sha256\":\""
                   << retained_compaction_cubin_sha256 << "\",";
        output << "\"close_inside_primary_timer\":false}\n";
        std::cout << output.str();
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}

// Goal5798 formal Direct CUDA/C++/OptiX worker.
//
// The included Goal5796 source is the frozen baseline implementation.  This
// translation unit reuses its exact CUDA/OptiX helpers and adds only the
// formal matched workloads, prepared ownership, phase timing, and JSON output.

#include <chrono>
#include <cstdlib>
#include <filesystem>
#include <fcntl.h>
#include <iomanip>
#include <map>
#include <numeric>
#include <thread>
#include <sys/resource.h>
#include <unistd.h>

#define main goal5796_functional_main_disabled
#include "../goal5796_matched/direct_optix.cpp"
#undef main

namespace {

using Clock = std::chrono::steady_clock;
using Nanoseconds = std::chrono::nanoseconds;
constexpr std::uint32_t kRelationSize = 4096;
constexpr std::uint32_t kRelationRawCapacity = 8194;
constexpr std::uint32_t kTriangleSize = 16384;
constexpr int kWarmups = 8;
constexpr int kTimed = 64;

std::uint64_t elapsed_ns(Clock::time_point start) {
    return static_cast<std::uint64_t>(
        std::chrono::duration_cast<Nanoseconds>(Clock::now() - start).count());
}

void create_only_text(const std::filesystem::path& path, const std::string& text) {
    std::filesystem::create_directories(path.parent_path());
    int descriptor = ::open(path.c_str(), O_WRONLY | O_CREAT | O_EXCL, 0600);
    if (descriptor < 0) throw std::runtime_error("cannot create barrier file: " + path.string());
    const char* cursor = text.data();
    std::size_t remaining = text.size();
    while (remaining) {
        const auto written = ::write(descriptor, cursor, remaining);
        if (written <= 0) {
            ::close(descriptor);
            throw std::runtime_error("cannot write barrier file: " + path.string());
        }
        cursor += written;
        remaining -= static_cast<std::size_t>(written);
    }
    ::fsync(descriptor);
    ::close(descriptor);
}

void memory_barrier(const std::filesystem::path& directory, const std::string& worker_id) {
    std::ostringstream ready;
    ready << "{\"schema\":\"rtdl.goal5798.prepared_memory_barrier.v1\","
          << "\"worker_id\":\"" << worker_id << "\",\"pid\":" << ::getpid()
          << ",\"arm\":\"A_DIRECT_CUDA_OPTIX\"}\n";
    create_only_text(directory / "prepared.ready.json", ready.str());
    const auto continuation = directory / "controller.continue";
    const auto deadline = Clock::now() + std::chrono::seconds(300);
    while (!std::filesystem::is_regular_file(continuation)) {
        if (Clock::now() >= deadline)
            throw std::runtime_error("memory controller did not release prepared barrier");
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    if (read_file(continuation.string()) != "CONTINUE\n")
        throw std::runtime_error("memory continuation token mismatch");
}

std::vector<Box> relation_boxes() {
    std::vector<Box> result;
    result.reserve(kRelationSize);
    for (std::uint32_t id = 0; id < kRelationSize; ++id) {
        const float lower = static_cast<float>(2 * id);
        result.push_back(box(lower, 0.0f, lower + 1.0f, 1.0f, id));
    }
    return result;
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
    return result;
}

struct FormalRelationResult {
    std::vector<std::pair<std::uint32_t, std::uint32_t>> rows;
    std::uint32_t raw_count = 0;
    std::uint32_t status = 0;
    std::uint32_t overflow = 0;
};

struct PreparedRelation {
    const Pipeline& pipeline;
    std::vector<Box> indexed;
    std::vector<Box> queries;
    DeviceBuffer d_indexed;
    DeviceBuffer d_queries;
    DeviceBuffer d_rows;
    DeviceBuffer d_count;
    DeviceBuffer d_overflow;
    DeviceBuffer d_status;
    Accel indexed_accel;
    Accel query_accel;

    PreparedRelation(OptixDeviceContext context, const Pipeline& owned_pipeline,
                     std::vector<Box> input)
        : pipeline(owned_pipeline), indexed(std::move(input)), queries(indexed),
          d_indexed(upload_vector(indexed)), d_queries(upload_vector(queries)),
          d_rows(sizeof(RelationRow) * kRelationRawCapacity),
          d_count(sizeof(std::uint32_t)), d_overflow(sizeof(std::uint32_t)),
          d_status(sizeof(std::uint32_t)), indexed_accel(custom_accel(context, indexed)),
          query_accel(custom_accel(context, queries)) {}

    FormalRelationResult execute() {
        CU_CHECK(cuMemsetD8(d_rows.ptr, 0, d_rows.bytes));
        CU_CHECK(cuMemsetD8(d_count.ptr, 0, d_count.bytes));
        CU_CHECK(cuMemsetD8(d_overflow.ptr, 0, d_overflow.bytes));
        CU_CHECK(cuMemsetD8(d_status.ptr, 0, d_status.bytes));
        for (unsigned reverse = 0; reverse < 2; ++reverse) {
            Params params = {};
            params.traversable = reverse ? query_accel.handle : indexed_accel.handle;
            params.boxes = reinterpret_cast<const Box*>(reverse ? d_queries.ptr : d_indexed.ptr);
            params.queries = reinterpret_cast<const Box*>(reverse ? d_indexed.ptr : d_queries.ptr);
            params.rows = reinterpret_cast<RelationRow*>(d_rows.ptr);
            params.row_count = reinterpret_cast<std::uint32_t*>(d_count.ptr);
            params.overflow = reinterpret_cast<std::uint32_t*>(d_overflow.ptr);
            params.box_count = kRelationSize;
            params.query_count = kRelationSize;
            params.raw_row_capacity = kRelationRawCapacity;
            params.reverse_orientation = reverse;
            params.minimum_overlap = 1.0f;
            params.status = reinterpret_cast<std::uint32_t*>(d_status.ptr);
            launch(pipeline, params, kRelationSize);
        }
        const auto count = download_vector<std::uint32_t>(d_count.ptr, 1)[0];
        const auto overflow = download_vector<std::uint32_t>(d_overflow.ptr, 1)[0];
        const auto status = download_vector<std::uint32_t>(d_status.ptr, 1)[0];
        if (overflow || status || count > kRelationRawCapacity)
            throw std::runtime_error("direct formal relation device status failure");
        auto raw = download_vector<RelationRow>(d_rows.ptr, count);
        std::set<std::pair<std::uint32_t, std::uint32_t>> canonical;
        for (const auto& row : raw) canonical.emplace(row.source_id, row.item_id);
        return {{canonical.begin(), canonical.end()}, count, status, overflow};
    }
};

struct FormalTriangleResult {
    std::vector<std::uint64_t> per_ray;
    std::uint64_t weighted = 0;
    std::uint32_t status = 0;
};

struct PreparedTriangle {
    const Pipeline& pipeline;
    std::vector<float3> vertices;
    std::vector<Ray> rays;
    std::vector<std::uint64_t> weights;
    Accel accel;
    DeviceBuffer d_rays;
    DeviceBuffer d_weights;
    DeviceBuffer d_per_ray;
    DeviceBuffer d_weighted;
    DeviceBuffer d_status;

    PreparedTriangle(OptixDeviceContext context, const Pipeline& owned_pipeline,
                     std::vector<float3> input_vertices, std::vector<Ray> input_rays,
                     std::vector<std::uint64_t> input_weights)
        : pipeline(owned_pipeline), vertices(std::move(input_vertices)),
          rays(std::move(input_rays)), weights(std::move(input_weights)),
          accel(triangle_accel(context, vertices)), d_rays(upload_vector(rays)),
          d_weights(upload_vector(weights)), d_per_ray(sizeof(std::uint64_t) * rays.size()),
          d_weighted(sizeof(std::uint64_t)), d_status(sizeof(std::uint32_t)) {}

    FormalTriangleResult execute(bool include_auxiliary_per_ray = true) {
        CU_CHECK(cuMemsetD8(d_per_ray.ptr, 0, d_per_ray.bytes));
        CU_CHECK(cuMemsetD8(d_weighted.ptr, 0, d_weighted.bytes));
        CU_CHECK(cuMemsetD8(d_status.ptr, 0, d_status.bytes));
        Params params = {};
        params.traversable = accel.handle;
        params.query_count = kTriangleSize;
        params.tmin = 0.0f;
        params.tmax = 2.0f;
        params.rays = reinterpret_cast<const Ray*>(d_rays.ptr);
        params.weights = reinterpret_cast<const std::uint64_t*>(d_weights.ptr);
        params.per_ray = reinterpret_cast<std::uint64_t*>(d_per_ray.ptr);
        params.weighted_sum = reinterpret_cast<std::uint64_t*>(d_weighted.ptr);
        params.status = reinterpret_cast<std::uint32_t*>(d_status.ptr);
        launch(pipeline, params, kTriangleSize);
        FormalTriangleResult result;
        result.status = download_vector<std::uint32_t>(d_status.ptr, 1)[0];
        if (include_auxiliary_per_ray)
            result.per_ray = download_vector<std::uint64_t>(d_per_ray.ptr, kTriangleSize);
        result.weighted = download_vector<std::uint64_t>(d_weighted.ptr, 1)[0];
        if (result.status) throw std::runtime_error("direct formal triangle device status failure");
        return result;
    }
};

void validate_relation_oracle(const FormalRelationResult& result) {
    if (result.rows.size() != kRelationSize)
        throw std::runtime_error("direct formal relation row-count mismatch");
    std::uint32_t expected = 0;
    for (const auto& row : result.rows) {
        if (row.first != expected || row.second != expected)
            throw std::runtime_error("direct formal relation oracle mismatch");
        ++expected;
    }
}

void validate_triangle_public_oracle(const FormalTriangleResult& result) {
    if (result.weighted != 65530)
        throw std::runtime_error("direct formal triangle public oracle mismatch");
}

void validate_triangle_full_oracle(const FormalTriangleResult& result) {
    validate_triangle_public_oracle(result);
    if (result.per_ray.size() != kTriangleSize ||
        !std::all_of(result.per_ray.begin(), result.per_ray.end(),
                     [](std::uint64_t value) { return value == 1; }))
        throw std::runtime_error("direct formal triangle auxiliary oracle mismatch");
}

struct Arguments {
    std::string worker_id, task, mode, device_source, optix_include, cuda_include;
    std::string freeze_sha256, controller_ticket, barrier_dir, measurement_contract;
};

Arguments parse_arguments(int argc, char** argv) {
    Arguments result;
    std::map<std::string, std::string*> destinations = {
        {"--worker-id", &result.worker_id}, {"--task", &result.task},
        {"--mode", &result.mode}, {"--device-source", &result.device_source},
        {"--optix-include", &result.optix_include}, {"--cuda-include", &result.cuda_include},
        {"--freeze-sha256", &result.freeze_sha256},
        {"--controller-ticket", &result.controller_ticket}, {"--barrier-dir", &result.barrier_dir},
        {"--measurement-contract", &result.measurement_contract},
    };
    for (int index = 1; index < argc; index += 2) {
        if (index + 1 >= argc || !destinations.count(argv[index]))
            throw std::runtime_error("invalid direct worker arguments");
        *destinations.at(argv[index]) = argv[index + 1];
    }
    if (result.worker_id.empty() || result.task.empty() || result.mode.empty()
            || result.device_source.empty() || result.optix_include.empty()
            || result.cuda_include.empty() || result.freeze_sha256.size() != 64
            || result.controller_ticket.size() != 64)
        throw std::runtime_error("incomplete direct worker arguments");
    const char* parent = std::getenv("GOAL5798_FORMAL_CONTROLLER_PID");
    if (!parent || std::to_string(::getppid()) != parent)
        throw std::runtime_error("direct worker was not spawned by the formal controller");
    if (result.mode == "MEMORY_SEPARATE_NON_TIMED" && result.barrier_dir.empty())
        throw std::runtime_error("memory worker lacks barrier directory");
    if (result.mode != "MEMORY_SEPARATE_NON_TIMED" && !result.barrier_dir.empty())
        throw std::runtime_error("timed direct worker carries a memory barrier");
    return result;
}

void json_durations(std::ostream& output, const std::vector<std::uint64_t>& values) {
    output << '[';
    for (std::size_t index = 0; index < values.size(); ++index) {
        if (index) output << ',';
        output << values[index];
    }
    output << ']';
}

std::uint64_t host_rusage_maxrss_bytes() {
    struct rusage usage = {};
    if (::getrusage(RUSAGE_SELF, &usage) != 0)
        throw std::runtime_error("getrusage failed");
    return static_cast<std::uint64_t>(usage.ru_maxrss) * 1024ULL;
}

} // namespace

int main(int argc, char** argv) {
    try {
        const Arguments args = parse_arguments(argc, argv);
        const bool goal5842_public =
            args.measurement_contract == "GOAL5842_PUBLIC_OUTPUT_V1";
        const bool goal5842_witness =
            args.measurement_contract == "GOAL5842_WITNESS_NO_TIMING_V1";
        if (!args.measurement_contract.empty() && !goal5842_public && !goal5842_witness)
            throw std::runtime_error("unsupported measurement contract");
        if (goal5842_witness !=
            (args.mode == "CORRECTNESS_WITNESS_NO_TIMING"))
            throw std::runtime_error(
                "Direct witness mode and measurement contract must be paired");

        if (goal5842_witness) {
            const std::string source = read_file(args.device_source);
            const std::string ptx = compile_ptx(
                source, args.device_source, args.optix_include, args.cuda_include);
            Context context;
            auto pipeline = build_pipeline(
                context.optix, ptx,
                args.task == "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1");
            FormalRelationResult relation_result;
            FormalTriangleResult triangle_result;
            if (args.task == "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1") {
                PreparedRelation relation(context.optix, *pipeline, relation_boxes());
                relation_result = relation.execute();
                validate_relation_oracle(relation_result);
            } else if (args.task == "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1") {
                PreparedTriangle triangle(
                    context.optix, *pipeline, triangle_vertices(), triangle_rays(),
                    triangle_weights());
                triangle_result = triangle.execute(true);
                validate_triangle_full_oracle(triangle_result);
            } else {
                throw std::runtime_error("unsupported direct witness task");
            }
            std::ostringstream output;
            output << "{\"schema\":\"rtdl.goal5842.direct_identity_witness_raw.v1\","
                   << "\"status\":\"PASS\",\"worker_id\":\"" << args.worker_id << "\","
                   << "\"task\":\"" << args.task << "\","
                   << "\"mode\":\"" << args.mode << "\","
                   << "\"freeze_sha256\":\"" << args.freeze_sha256 << "\","
                   << "\"controller_ticket\":\"" << args.controller_ticket << "\","
                   << "\"optix_header_version\":" << OPTIX_VERSION << ','
                   << "\"clock_api_called_by_witness_path\":false,"
                   << "\"duration_field_count\":0,"
                   << "\"gpu_complete_execution_call_count\":1,"
                   << "\"optix_launch_count\":" << (relation_result.rows.empty() ? 1 : 2)
                   << ",\"correctness\":";
            if (!relation_result.rows.empty()) {
                output << "{\"full_oracle_exact\":true,\"canonical_rows\":[";
                for (std::size_t index = 0; index < relation_result.rows.size(); ++index) {
                    if (index) output << ',';
                    output << '[' << relation_result.rows[index].first << ','
                           << relation_result.rows[index].second << ']';
                }
                output << "],\"device_status\":" << relation_result.status
                       << ",\"device_overflow\":" << relation_result.overflow << '}';
            } else {
                output << "{\"full_oracle_exact\":true,\"per_ray\":";
                json_durations(output, triangle_result.per_ray);
                output << ",\"weighted_sum\":" << triangle_result.weighted
                       << ",\"device_status\":" << triangle_result.status << '}';
            }
            output << "}\n";
            std::cout << output.str();
            return 0;
        }

        std::uint64_t input_ns = 0, compile_ns = 0, pipeline_ns = 0, static_ns = 0;
        const auto input_start = Clock::now();
        std::vector<Box> boxes;
        std::vector<float3> vertices;
        std::vector<Ray> rays;
        std::vector<std::uint64_t> weights;
        if (args.task == "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1") boxes = relation_boxes();
        else if (args.task == "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1") {
            vertices = triangle_vertices(); rays = triangle_rays(); weights = triangle_weights();
        } else throw std::runtime_error("unsupported direct task");
        input_ns = elapsed_ns(input_start);

        const auto preparation_start = Clock::now();
        const auto compile_start = Clock::now();
        const std::string source = read_file(args.device_source);
        const std::string ptx = compile_ptx(
            source, args.device_source, args.optix_include, args.cuda_include);
        compile_ns = elapsed_ns(compile_start);
        const auto pipeline_start = Clock::now();
        Context context;
        auto pipeline = build_pipeline(
            context.optix, ptx, args.task == "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1");
        pipeline_ns = elapsed_ns(pipeline_start);

        std::unique_ptr<PreparedRelation> relation;
        std::unique_ptr<PreparedTriangle> triangle;
        const auto static_start = Clock::now();
        if (!boxes.empty())
            relation = std::make_unique<PreparedRelation>(context.optix, *pipeline, std::move(boxes));
        else
            triangle = std::make_unique<PreparedTriangle>(
                context.optix, *pipeline, std::move(vertices), std::move(rays), std::move(weights));
        static_ns = elapsed_ns(static_start);
        const auto preparation_ns = elapsed_ns(preparation_start);

        std::vector<std::uint64_t> durations;
        FormalRelationResult relation_result;
        FormalTriangleResult triangle_result;
        auto execute = [&]() {
            const auto start = Clock::now();
            if (relation) {
                relation_result = relation->execute();
                if (!goal5842_public) validate_relation_oracle(relation_result);
            } else {
                triangle_result = triangle->execute(!goal5842_public);
                if (!goal5842_public) validate_triangle_full_oracle(triangle_result);
            }
            const auto duration = elapsed_ns(start);
            if (goal5842_public) {
                if (relation) validate_relation_oracle(relation_result);
                else validate_triangle_public_oracle(triangle_result);
            }
            return duration;
        };
        if (args.mode == "PREPARED_EXECUTION") {
            for (int index = 0; index < kWarmups; ++index) (void)execute();
            for (int index = 0; index < kTimed; ++index) durations.push_back(execute());
        } else if (args.mode == "MEMORY_SEPARATE_NON_TIMED") {
            for (int index = 0; index < kWarmups; ++index) (void)execute();
            memory_barrier(args.barrier_dir, args.worker_id);
            durations.push_back(execute());
        } else if (args.mode == "COLD_FRESH_PROCESS") {
            durations.push_back(execute());
        } else throw std::runtime_error("unsupported direct mode");

        std::ostringstream output;
        output << "{\"schema\":\""
               << (goal5842_public ? "rtdl.goal5842.direct_public_output_raw.v1"
                                   : "rtdl.goal5798.direct_raw_worker.v1")
               << "\","
               << "\"status\":\"PASS\",\"worker_id\":\"" << args.worker_id << "\","
               << "\"task\":\"" << args.task << "\",\"mode\":\"" << args.mode << "\","
               << "\"freeze_sha256\":\"" << args.freeze_sha256 << "\","
               << "\"controller_ticket\":\"" << args.controller_ticket << "\","
               << "\"optix_header_version\":" << OPTIX_VERSION << ','
               << "\"host_rusage_maxrss_bytes\":" << host_rusage_maxrss_bytes() << ','
               << "\"phase_durations_ns\":{\"deterministic_input_materialization\":" << input_ns
               << ",\"protocol_validation_and_codegen\":null,\"device_compile\":" << compile_ns
               << ",\"module_program_pipeline_sbt\":" << pipeline_ns
               << ",\"gas_and_static_prepare\":" << static_ns
               << ",\"common_preparation_total\":" << preparation_ns << "},"
               << "\"execute_durations_ns\":";
        json_durations(output, durations);
        output << ",\"measurement_contract\":\""
               << (goal5842_public ? "GOAL5842_PUBLIC_OUTPUT_V1" : "LEGACY_GOAL5798")
               << "\",\"oracle_validation_outside_execute_durations\":"
               << (goal5842_public ? "true" : "false") << ','
               << "\"correctness\":";
        if (relation) {
            output << (goal5842_public
                           ? "{\"public_output_oracle_exact\":true,"
                             "\"public_output_contract_id\":"
                             "\"canonical_relation_rows.v1\",\"canonical_rows\":"
                           : "{\"oracle_exact\":true,\"canonical_rows\":");
            output << '[';
            for (std::size_t index = 0; index < relation_result.rows.size(); ++index) {
                if (index) output << ',';
                output << '[' << relation_result.rows[index].first << ','
                       << relation_result.rows[index].second << ']';
            }
            output << "],\"raw_event_count\":" << relation_result.raw_count
                   << ",\"raw_event_capacity\":" << kRelationRawCapacity
                   << ",\"device_status\":" << relation_result.status
                   << ",\"device_overflow\":" << relation_result.overflow << '}';
        } else {
            if (goal5842_public) {
                output << "{\"public_output_oracle_exact\":true,"
                       << "\"public_output_contract_id\":"
                       << "\"checked_u64_weighted_scalar.v1\","
                       << "\"weighted_sum\":" << triangle_result.weighted
                       << ",\"device_status\":" << triangle_result.status << '}';
            } else {
                output << "{\"oracle_exact\":true,\"per_ray\":";
                json_durations(output, triangle_result.per_ray);
                output << ",\"weighted_sum\":" << triangle_result.weighted
                       << ",\"device_status\":" << triangle_result.status << '}';
            }
        }
        output << "}\n";
        std::cout << output.str();
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}

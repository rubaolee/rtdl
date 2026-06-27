from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import statistics
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
for path in (SRC, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from rtdsl.v4_goal4687_tier3_wrapper_compile_probe import extract_numba_callback_symbol_from_ptx
from rtdsl.v4_goal4688_tier3_module_link_probe import compose_goal4688_combined_ptx
from rtdsl.v4_goal4713_custom_predicate_early_exit_protocol import (
    validate_v4_goal4713_custom_predicate_early_exit_protocol,
)
from rtdsl.v4_goal4715_custom_predicate_early_exit_timing_result import (
    classify_v4_goal4715_custom_predicate_early_exit_timing,
    validate_v4_goal4715_custom_predicate_early_exit_timing_result_contract,
)
from v4_goal4688_tier3_module_link_probe import _find_cuda_lib_dir
from v4_goal4688_tier3_module_link_probe import _find_cuda_root
from v4_goal4688_tier3_module_link_probe import _find_nvcc
from v4_goal4688_tier3_module_link_probe import _find_optix_include
from v4_goal4688_tier3_module_link_probe import _run
from v4_tier3_numba_ptx_probe import _configure_numba_legacy_nvvm_env
from v4_tier3_numba_ptx_probe import _maybe_reexec_with_nvvm_ld_path


DEFAULT_WARMUPS = 2
DEFAULT_REPEAT = 7
DEFAULT_SCALES = (65536, 131072)
ROOT_V2_14 = Path("/root/rtdl_v2_14_tag")
ROOT_V3_0_2 = Path("/root/rtdl_v3_0_2_tag")

KEY_VALUE_RE = re.compile(r"^([A-Za-z0-9_]+)=([^\n]+)$", re.MULTILINE)
SAMPLE_RE = re.compile(r"^sample_([A-Za-z0-9_]+)_ms=([0-9.eE+-]+)$", re.MULTILINE)


def accept_layer_predicate(hit_distance, primitive_id, candidates_per_ray, accept_layer):
    if accept_layer < 0.0:
        return 0.0
    k = int(candidates_per_ray)
    layer = primitive_id % k
    return 1.0 if layer == int(accept_layer) else 0.0


VARIANT_FUNCTIONS = {"accept_layer_predicate": accept_layer_predicate}


CPP_SOURCE = r"""
#include <cuda.h>
#include <cuda_runtime.h>
#include <optix.h>
#include <optix_function_table_definition.h>
#include <optix_stubs.h>

#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

template <typename T>
struct alignas(OPTIX_SBT_RECORD_ALIGNMENT) SbtRecord {
    char header[OPTIX_SBT_RECORD_HEADER_SIZE];
    T data;
};

struct EmptyData { unsigned int unused = 0; };
using RaygenRecord = SbtRecord<EmptyData>;
using MissRecord = SbtRecord<EmptyData>;
using HitRecord = SbtRecord<EmptyData>;

struct Params {
    OptixTraversableHandle handle;
    unsigned int* accepted_flags;
    unsigned int* materialized_layers;
    unsigned long long* anyhit_invocations;
    unsigned long long* accepted_count;
    unsigned int ray_count;
    unsigned int candidates_per_ray;
    int accept_layer;
    unsigned int route_mode;
};

struct Float3 { float x; float y; float z; };
struct UInt3 { unsigned int x; unsigned int y; unsigned int z; };

__global__ void predicate_materialized_hits_kernel(
    const unsigned int* materialized_layers,
    unsigned int* flags,
    unsigned int ray_count,
    unsigned int candidates_per_ray,
    int accept_layer) {
    unsigned int ray = blockIdx.x * blockDim.x + threadIdx.x;
    if (ray >= ray_count) return;
    unsigned int accepted = 0u;
    if (accept_layer >= 0 && candidates_per_ray > 0u) {
        unsigned int wanted = (unsigned int)accept_layer;
        if (wanted < candidates_per_ray) {
            unsigned int marker = materialized_layers[ray * candidates_per_ray + wanted];
            accepted = marker != 0u ? 1u : 0u;
        }
    }
    flags[ray] = accepted;
}

__global__ void reduce_flags_kernel(const unsigned int* flags, unsigned long long* output, unsigned int n) {
    unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x;
    unsigned int stride = blockDim.x * gridDim.x;
    unsigned long long local = 0ull;
    for (unsigned int i = idx; i < n; i += stride) {
        local += (unsigned long long)flags[i];
    }
    if (local != 0ull) atomicAdd(output, local);
}

static std::string read_text(const char* path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) throw std::runtime_error(std::string("failed to open PTX file: ") + path);
    std::ostringstream buffer;
    buffer << in.rdbuf();
    return buffer.str();
}

static void check_runtime(cudaError_t result, const char* what) {
    if (result == cudaSuccess) return;
    throw std::runtime_error(std::string(what) + ": " + cudaGetErrorString(result));
}

static void check_cuda(CUresult result, const char* what) {
    if (result == CUDA_SUCCESS) return;
    const char* raw = nullptr;
    cuGetErrorString(result, &raw);
    throw std::runtime_error(std::string(what) + ": " + (raw ? raw : "unknown CUDA error"));
}

static void check_optix(OptixResult result, const char* what) {
    if (result == OPTIX_SUCCESS) return;
    throw std::runtime_error(std::string(what) + ": " + optixGetErrorString(result));
}

static OptixProgramGroup create_program_group(OptixDeviceContext ctx, const OptixProgramGroupDesc& desc, const char* what) {
    OptixProgramGroupOptions options = {};
    char log[8192] = {};
    size_t log_size = sizeof(log);
    OptixProgramGroup group = nullptr;
    OptixResult result = optixProgramGroupCreate(ctx, &desc, 1, &options, log, &log_size, &group);
    std::cout << what << "_result=" << static_cast<int>(result) << "\n";
    check_optix(result, what);
    return group;
}

static unsigned int active_ray_count_for(const std::string& regime, unsigned int ray_count) {
    if (regime.find("sparse") != std::string::npos) return (ray_count + 3u) / 4u;
    if (regime == "no_hit_empty") return 0u;
    return ray_count;
}

static int accept_layer_for(const std::string& regime, unsigned int candidates_per_ray) {
    if (regime.find("reject_all") != std::string::npos || regime == "no_hit_empty") return -1;
    if (regime.find("late_accept") != std::string::npos) return (int)candidates_per_ray - 1;
    return 0;
}

static void launch_reduce_flags(unsigned int* flags_dev, unsigned long long* accepted_count_dev, unsigned int ray_count) {
    unsigned int block = 256u;
    unsigned int grid = (ray_count + block - 1u) / block;
    if (grid > 4096u) grid = 4096u;
    reduce_flags_kernel<<<grid, block>>>(flags_dev, accepted_count_dev, ray_count);
    check_runtime(cudaGetLastError(), "reduce flags launch");
}

static void launch_predicate_materialized(
    unsigned int* materialized_layers_dev,
    unsigned int* flags_dev,
    unsigned int ray_count,
    unsigned int candidates_per_ray,
    int accept_layer) {
    unsigned int block = 256u;
    unsigned int grid = (ray_count + block - 1u) / block;
    if (grid > 4096u) grid = 4096u;
    predicate_materialized_hits_kernel<<<grid, block>>>(materialized_layers_dev, flags_dev, ray_count, candidates_per_ray, accept_layer);
    check_runtime(cudaGetLastError(), "predicate materialized launch");
}

static void run_route(
    const char* route_name,
    unsigned int route_mode,
    OptixPipeline pipeline,
    const OptixShaderBindingTable* sbt,
    CUdeviceptr params_dev,
    Params* params_host,
    unsigned int* flags_dev,
    unsigned int* materialized_layers_dev,
    unsigned long long* invocations_dev,
    unsigned long long* accepted_count_dev,
    unsigned int ray_count,
    unsigned int candidates_per_ray,
    unsigned int materialized_slots,
    unsigned int warmups,
    unsigned int measured) {

    params_host->route_mode = route_mode;
    check_runtime(cudaMemcpy(reinterpret_cast<void*>(params_dev), params_host, sizeof(Params), cudaMemcpyHostToDevice),
                  "copy params route");
    for (unsigned int i = 0; i < warmups; ++i) {
        check_runtime(cudaMemset(flags_dev, 0, sizeof(unsigned int) * ray_count), "warmup reset flags");
        check_runtime(cudaMemset(invocations_dev, 0, sizeof(unsigned long long)), "warmup reset invocations");
        check_runtime(cudaMemset(accepted_count_dev, 0, sizeof(unsigned long long)), "warmup reset accepted count");
        if (route_mode == 0u) {
            check_runtime(cudaMemset(materialized_layers_dev, 0, sizeof(unsigned int) * materialized_slots), "warmup reset materialized");
        }
        check_optix(optixLaunch(pipeline, 0, params_dev, sizeof(Params), sbt, ray_count, 1, 1), "warmup optixLaunch");
        if (route_mode == 0u) {
            launch_predicate_materialized(materialized_layers_dev, flags_dev, ray_count, candidates_per_ray, params_host->accept_layer);
        }
        launch_reduce_flags(flags_dev, accepted_count_dev, ray_count);
        check_runtime(cudaDeviceSynchronize(), "warmup sync");
    }

    cudaEvent_t start = nullptr;
    cudaEvent_t stop = nullptr;
    check_runtime(cudaEventCreate(&start), "event start create");
    check_runtime(cudaEventCreate(&stop), "event stop create");
    for (unsigned int i = 0; i < measured; ++i) {
        check_runtime(cudaEventRecord(start, 0), "event start");
        check_runtime(cudaMemset(flags_dev, 0, sizeof(unsigned int) * ray_count), "measured reset flags");
        check_runtime(cudaMemset(invocations_dev, 0, sizeof(unsigned long long)), "measured reset invocations");
        check_runtime(cudaMemset(accepted_count_dev, 0, sizeof(unsigned long long)), "measured reset accepted count");
        if (route_mode == 0u) {
            check_runtime(cudaMemset(materialized_layers_dev, 0, sizeof(unsigned int) * materialized_slots), "measured reset materialized");
        }
        check_optix(optixLaunch(pipeline, 0, params_dev, sizeof(Params), sbt, ray_count, 1, 1), "measured optixLaunch");
        if (route_mode == 0u) {
            launch_predicate_materialized(materialized_layers_dev, flags_dev, ray_count, candidates_per_ray, params_host->accept_layer);
        }
        launch_reduce_flags(flags_dev, accepted_count_dev, ray_count);
        check_runtime(cudaEventRecord(stop, 0), "event stop");
        check_runtime(cudaEventSynchronize(stop), "event sync");
        float ms = 0.0f;
        check_runtime(cudaEventElapsedTime(&ms, start, stop), "event elapsed");
        std::cout << "sample_" << route_name << "_ms=" << ms << "\n";
    }
    check_runtime(cudaDeviceSynchronize(), "measured sync");
    unsigned long long invocations = 0ull;
    unsigned long long accepted_count = 0ull;
    check_runtime(cudaMemcpy(&invocations, invocations_dev, sizeof(unsigned long long), cudaMemcpyDeviceToHost), "copy invocations");
    check_runtime(cudaMemcpy(&accepted_count, accepted_count_dev, sizeof(unsigned long long), cudaMemcpyDeviceToHost), "copy accepted count");
    std::cout << route_name << "_anyhit_invocations=" << invocations << "\n";
    std::cout << route_name << "_accepted_count=" << accepted_count << "\n";
    check_runtime(cudaEventDestroy(start), "event start destroy");
    check_runtime(cudaEventDestroy(stop), "event stop destroy");
}

int main(int argc, char** argv) {
    try {
        if (argc != 7) {
            std::cerr << "usage: v4_goal4715_timing <ptx> <regime> <ray_count> <candidates_per_ray> <warmups> <measured>\n";
            return 64;
        }
        std::string ptx = read_text(argv[1]);
        std::string regime = argv[2];
        unsigned int ray_count = static_cast<unsigned int>(std::stoul(argv[3]));
        unsigned int candidates_per_ray = static_cast<unsigned int>(std::stoul(argv[4]));
        unsigned int warmups = static_cast<unsigned int>(std::stoul(argv[5]));
        unsigned int measured = static_cast<unsigned int>(std::stoul(argv[6]));
        int accept_layer = accept_layer_for(regime, candidates_per_ray);
        unsigned int active_rays = active_ray_count_for(regime, ray_count);
        unsigned int triangle_count = regime == "no_hit_empty" ? 1u : active_rays * candidates_per_ray;
        unsigned int materialized_slots = std::max(1u, ray_count * std::max(1u, candidates_per_ray));

        check_runtime(cudaFree(nullptr), "cuda init");
        CUcontext cu_ctx = nullptr;
        check_cuda(cuCtxGetCurrent(&cu_ctx), "cuCtxGetCurrent");
        check_optix(optixInit(), "optixInit");
        OptixDeviceContextOptions context_options = {};
        OptixDeviceContext optix_ctx = nullptr;
        check_optix(optixDeviceContextCreate(cu_ctx, &context_options, &optix_ctx), "optixDeviceContextCreate");

        std::vector<Float3> vertices;
        std::vector<UInt3> indices;
        vertices.reserve(static_cast<size_t>(triangle_count) * 3u);
        indices.reserve(triangle_count);
        for (unsigned int h = 0; h < triangle_count; ++h) {
            unsigned int active_ray = candidates_per_ray ? h / candidates_per_ray : 0u;
            unsigned int layer = candidates_per_ray ? h % candidates_per_ray : 0u;
            unsigned int ray_idx = regime.find("sparse") != std::string::npos ? active_ray * 4u : active_ray;
            float x = static_cast<float>((ray_idx % 256u) * 2u);
            float y = static_cast<float>((ray_idx / 256u) * 2u);
            float z = regime == "no_hit_empty" ? 100.0f : 1.0f + 0.02f * (float)layer;
            float half = 0.40f;
            unsigned int base = h * 3u;
            vertices.push_back(Float3{x - half, y - half, z});
            vertices.push_back(Float3{x + half, y - half, z});
            vertices.push_back(Float3{x, y + half, z});
            indices.push_back(UInt3{base, base + 1u, base + 2u});
        }

        Float3* vertices_dev = nullptr;
        UInt3* indices_dev = nullptr;
        check_runtime(cudaMalloc(reinterpret_cast<void**>(&vertices_dev), vertices.size() * sizeof(Float3)), "alloc vertices");
        check_runtime(cudaMalloc(reinterpret_cast<void**>(&indices_dev), indices.size() * sizeof(UInt3)), "alloc indices");
        check_runtime(cudaMemcpy(vertices_dev, vertices.data(), vertices.size() * sizeof(Float3), cudaMemcpyHostToDevice), "copy vertices");
        check_runtime(cudaMemcpy(indices_dev, indices.data(), indices.size() * sizeof(UInt3), cudaMemcpyHostToDevice), "copy indices");

        CUdeviceptr vertices_ptr = reinterpret_cast<CUdeviceptr>(vertices_dev);
        CUdeviceptr indices_ptr = reinterpret_cast<CUdeviceptr>(indices_dev);
        OptixBuildInput build_input = {};
        build_input.type = OPTIX_BUILD_INPUT_TYPE_TRIANGLES;
        build_input.triangleArray.vertexBuffers = &vertices_ptr;
        build_input.triangleArray.numVertices = static_cast<unsigned int>(vertices.size());
        build_input.triangleArray.vertexFormat = OPTIX_VERTEX_FORMAT_FLOAT3;
        build_input.triangleArray.vertexStrideInBytes = sizeof(Float3);
        build_input.triangleArray.indexBuffer = indices_ptr;
        build_input.triangleArray.numIndexTriplets = triangle_count;
        build_input.triangleArray.indexFormat = OPTIX_INDICES_FORMAT_UNSIGNED_INT3;
        build_input.triangleArray.indexStrideInBytes = sizeof(UInt3);
        unsigned int geometry_flags = OPTIX_GEOMETRY_FLAG_REQUIRE_SINGLE_ANYHIT_CALL;
        build_input.triangleArray.flags = &geometry_flags;
        build_input.triangleArray.numSbtRecords = 1;

        OptixAccelBuildOptions accel_options = {};
        accel_options.buildFlags = OPTIX_BUILD_FLAG_ALLOW_COMPACTION;
        accel_options.operation = OPTIX_BUILD_OPERATION_BUILD;
        OptixAccelBufferSizes accel_sizes = {};
        check_optix(optixAccelComputeMemoryUsage(optix_ctx, &accel_options, &build_input, 1, &accel_sizes), "accel sizes");
        void* temp_dev = nullptr;
        void* gas_dev = nullptr;
        check_runtime(cudaMalloc(&temp_dev, accel_sizes.tempSizeInBytes), "alloc temp");
        check_runtime(cudaMalloc(&gas_dev, accel_sizes.outputSizeInBytes), "alloc gas");
        OptixTraversableHandle gas_handle = 0;
        check_optix(optixAccelBuild(optix_ctx, 0, &accel_options, &build_input, 1,
                                    reinterpret_cast<CUdeviceptr>(temp_dev), accel_sizes.tempSizeInBytes,
                                    reinterpret_cast<CUdeviceptr>(gas_dev), accel_sizes.outputSizeInBytes,
                                    &gas_handle, nullptr, 0),
                    "accel build");
        check_runtime(cudaDeviceSynchronize(), "gas sync");

        OptixModuleCompileOptions module_options = {};
        module_options.maxRegisterCount = OPTIX_COMPILE_DEFAULT_MAX_REGISTER_COUNT;
        module_options.optLevel = OPTIX_COMPILE_OPTIMIZATION_DEFAULT;
        module_options.debugLevel = OPTIX_COMPILE_DEBUG_LEVEL_NONE;
        OptixPipelineCompileOptions pipeline_options = {};
        pipeline_options.usesMotionBlur = 0;
        pipeline_options.traversableGraphFlags = OPTIX_TRAVERSABLE_GRAPH_FLAG_ALLOW_SINGLE_GAS;
        pipeline_options.numPayloadValues = 0;
        pipeline_options.numAttributeValues = 2;
        pipeline_options.exceptionFlags = OPTIX_EXCEPTION_FLAG_NONE;
        pipeline_options.pipelineLaunchParamsVariableName = "params";
        pipeline_options.usesPrimitiveTypeFlags = OPTIX_PRIMITIVE_TYPE_FLAGS_TRIANGLE;
        char module_log[16384] = {};
        size_t module_log_size = sizeof(module_log);
        OptixModule module = nullptr;
#if defined(OPTIX_VERSION) && OPTIX_VERSION < 70700
        OptixResult module_result = optixModuleCreateFromPTX(optix_ctx, &module_options, &pipeline_options,
                                                             ptx.c_str(), ptx.size(), module_log, &module_log_size, &module);
#else
        OptixResult module_result = optixModuleCreate(optix_ctx, &module_options, &pipeline_options,
                                                      ptx.c_str(), ptx.size(), module_log, &module_log_size, &module);
#endif
        std::cout << "optix_module_create_result=" << static_cast<int>(module_result) << "\n";
        check_optix(module_result, "module create");

        OptixProgramGroupDesc raygen_desc = {};
        raygen_desc.kind = OPTIX_PROGRAM_GROUP_KIND_RAYGEN;
        raygen_desc.raygen.module = module;
        raygen_desc.raygen.entryFunctionName = "__raygen__rtdl_goal4715_predicate";
        OptixProgramGroupDesc miss_desc = {};
        miss_desc.kind = OPTIX_PROGRAM_GROUP_KIND_MISS;
        miss_desc.miss.module = module;
        miss_desc.miss.entryFunctionName = "__miss__rtdl_goal4715_predicate";
        OptixProgramGroupDesc hit_desc = {};
        hit_desc.kind = OPTIX_PROGRAM_GROUP_KIND_HITGROUP;
        hit_desc.hitgroup.moduleAH = module;
        hit_desc.hitgroup.entryFunctionNameAH = "__anyhit__rtdl_goal4715_predicate";
        OptixProgramGroup raygen_pg = create_program_group(optix_ctx, raygen_desc, "raygen_program_group");
        OptixProgramGroup miss_pg = create_program_group(optix_ctx, miss_desc, "miss_program_group");
        OptixProgramGroup hit_pg = create_program_group(optix_ctx, hit_desc, "hit_program_group");
        std::vector<OptixProgramGroup> groups = {raygen_pg, miss_pg, hit_pg};
        OptixPipelineLinkOptions link_options = {};
        link_options.maxTraceDepth = 1;
        char pipeline_log[16384] = {};
        size_t pipeline_log_size = sizeof(pipeline_log);
        OptixPipeline pipeline = nullptr;
        check_optix(optixPipelineCreate(optix_ctx, &pipeline_options, &link_options,
                                        groups.data(), static_cast<unsigned int>(groups.size()),
                                        pipeline_log, &pipeline_log_size, &pipeline),
                    "pipeline create");
        check_optix(optixPipelineSetStackSize(pipeline, 8192, 8192, 8192, 1), "stack size");

        RaygenRecord raygen_rec = {};
        MissRecord miss_rec = {};
        HitRecord hit_rec = {};
        check_optix(optixSbtRecordPackHeader(raygen_pg, &raygen_rec), "pack raygen");
        check_optix(optixSbtRecordPackHeader(miss_pg, &miss_rec), "pack miss");
        check_optix(optixSbtRecordPackHeader(hit_pg, &hit_rec), "pack hit");
        void* raygen_dev = nullptr; void* miss_dev = nullptr; void* hit_dev = nullptr;
        check_runtime(cudaMalloc(&raygen_dev, sizeof(RaygenRecord)), "alloc raygen");
        check_runtime(cudaMalloc(&miss_dev, sizeof(MissRecord)), "alloc miss");
        check_runtime(cudaMalloc(&hit_dev, sizeof(HitRecord)), "alloc hit");
        check_runtime(cudaMemcpy(raygen_dev, &raygen_rec, sizeof(RaygenRecord), cudaMemcpyHostToDevice), "copy raygen");
        check_runtime(cudaMemcpy(miss_dev, &miss_rec, sizeof(MissRecord), cudaMemcpyHostToDevice), "copy miss");
        check_runtime(cudaMemcpy(hit_dev, &hit_rec, sizeof(HitRecord), cudaMemcpyHostToDevice), "copy hit");
        OptixShaderBindingTable sbt = {};
        sbt.raygenRecord = reinterpret_cast<CUdeviceptr>(raygen_dev);
        sbt.missRecordBase = reinterpret_cast<CUdeviceptr>(miss_dev);
        sbt.missRecordStrideInBytes = sizeof(MissRecord);
        sbt.missRecordCount = 1;
        sbt.hitgroupRecordBase = reinterpret_cast<CUdeviceptr>(hit_dev);
        sbt.hitgroupRecordStrideInBytes = sizeof(HitRecord);
        sbt.hitgroupRecordCount = 1;

        unsigned int* flags_dev = nullptr;
        unsigned int* materialized_layers_dev = nullptr;
        unsigned long long* invocations_dev = nullptr;
        unsigned long long* accepted_count_dev = nullptr;
        Params* params_dev_raw = nullptr;
        check_runtime(cudaMalloc(reinterpret_cast<void**>(&flags_dev), sizeof(unsigned int) * ray_count), "alloc flags");
        check_runtime(cudaMalloc(reinterpret_cast<void**>(&materialized_layers_dev), sizeof(unsigned int) * materialized_slots), "alloc materialized");
        check_runtime(cudaMalloc(reinterpret_cast<void**>(&invocations_dev), sizeof(unsigned long long)), "alloc invocations");
        check_runtime(cudaMalloc(reinterpret_cast<void**>(&accepted_count_dev), sizeof(unsigned long long)), "alloc accepted count");
        check_runtime(cudaMalloc(reinterpret_cast<void**>(&params_dev_raw), sizeof(Params)), "alloc params");
        Params params = {};
        params.handle = gas_handle;
        params.accepted_flags = flags_dev;
        params.materialized_layers = materialized_layers_dev;
        params.anyhit_invocations = invocations_dev;
        params.accepted_count = accepted_count_dev;
        params.ray_count = ray_count;
        params.candidates_per_ray = candidates_per_ray;
        params.accept_layer = accept_layer;
        params.route_mode = 0u;
        CUdeviceptr params_dev = reinterpret_cast<CUdeviceptr>(params_dev_raw);

        run_route("v4_early_exit", 1u, pipeline, &sbt, params_dev, &params, flags_dev, materialized_layers_dev,
                  invocations_dev, accepted_count_dev, ray_count, candidates_per_ray, materialized_slots, warmups, measured);
        run_route("materialized_fallback", 0u, pipeline, &sbt, params_dev, &params, flags_dev, materialized_layers_dev,
                  invocations_dev, accepted_count_dev, ray_count, candidates_per_ray, materialized_slots, warmups, measured);

        unsigned long long expected_accepted = accept_layer >= 0 ? (unsigned long long)active_rays : 0ull;
        std::cout << "regime=" << regime << "\n";
        std::cout << "ray_count=" << ray_count << "\n";
        std::cout << "candidates_per_ray=" << candidates_per_ray << "\n";
        std::cout << "active_rays=" << active_rays << "\n";
        std::cout << "accept_layer=" << accept_layer << "\n";
        std::cout << "expected_accepted=" << expected_accepted << "\n";
        return 0;
    } catch (const std::exception& exc) {
        std::cerr << exc.what() << "\n";
        return 3;
    }
}
"""


def _callback_wrapper_source(callback_symbol: str) -> str:
    return f"""
#include <optix.h>
#include <optix_device.h>

extern "C" __device__ double {callback_symbol}(
    double hit_t,
    unsigned int primitive_id,
    double candidates_per_ray,
    double accept_layer);

struct RtdlGoal4715Params {{
    OptixTraversableHandle handle;
    unsigned int* accepted_flags;
    unsigned int* materialized_layers;
    unsigned long long* anyhit_invocations;
    unsigned long long* accepted_count;
    unsigned int ray_count;
    unsigned int candidates_per_ray;
    int accept_layer;
    unsigned int route_mode;
}};

extern "C" {{
__constant__ RtdlGoal4715Params params;
}}

extern "C" __global__ void __raygen__rtdl_goal4715_predicate() {{
    const unsigned int idx = optixGetLaunchIndex().x;
    if (idx >= params.ray_count) return;
    const float x = (float)((idx % 256u) * 2u);
    const float y = (float)((idx / 256u) * 2u);
    const float3 origin = make_float3(x, y, 0.0f);
    const float3 direction = make_float3(0.0f, 0.0f, 1.0f);
    optixTrace(params.handle, origin, direction, 0.0f, 100.0f, 0.0f,
               OptixVisibilityMask(255), OPTIX_RAY_FLAG_DISABLE_CLOSESTHIT,
               0, 1, 0);
}}

extern "C" __global__ void __miss__rtdl_goal4715_predicate() {{
}}

extern "C" __global__ void __anyhit__rtdl_goal4715_predicate() {{
    atomicAdd(params.anyhit_invocations, 1ull);
    const unsigned int primitive_id = optixGetPrimitiveIndex();
    const unsigned int launch_idx = optixGetLaunchIndex().x;
    if (params.route_mode == 0u) {{
        if (params.candidates_per_ray > 0u) {{
            const unsigned int layer = primitive_id % params.candidates_per_ray;
            params.materialized_layers[launch_idx * params.candidates_per_ray + layer] = layer + 1u;
        }}
        optixIgnoreIntersection();
        return;
    }}
    const double accept = {callback_symbol}(1.0, primitive_id, (double)params.candidates_per_ray, (double)params.accept_layer);
    if (accept >= 0.5) {{
        params.accepted_flags[launch_idx] = 1u;
        optixTerminateRay();
    }} else {{
        optixIgnoreIntersection();
    }}
}}
""".strip()


def _toolchain() -> dict[str, object]:
    cuda_root = _find_cuda_root()
    optix_include = _find_optix_include()
    return {
        "optix_include": str(optix_include) if optix_include else None,
        "cuda_root": str(cuda_root) if cuda_root else None,
        "cuda_lib_dir": str(_find_cuda_lib_dir(cuda_root)) if cuda_root else None,
        "nvcc": _find_nvcc(),
    }


def _compile_predicate_ptx() -> tuple[str | None, dict[str, object]]:
    payload: dict[str, object] = {"variant": "accept_layer_predicate", "status": "unknown"}
    try:
        from rtdsl.numba_partner_continuation import configure_numba_cuda_toolchain_environment

        toolchain = configure_numba_cuda_toolchain_environment()
        payload["numba_toolchain_environment"] = toolchain
        payload["numba_nvvm_reexec_environment"] = _maybe_reexec_with_nvvm_ld_path(toolchain)
        payload["numba_legacy_nvvm_environment"] = _configure_numba_legacy_nvvm_env(toolchain)
        from numba import cuda, types

        ptx, return_type = cuda.compile_ptx(
            VARIANT_FUNCTIONS["accept_layer_predicate"],
            (types.float64, types.uint32, types.float64, types.float64),
            device=True,
            fastmath=False,
            abi="c",
        )
        payload.update({"status": "ptx_generated", "return_type": str(return_type), "ptx_length": len(ptx)})
        return ptx, payload
    except Exception as exc:
        payload.update({"status": "blocked", "error_type": type(exc).__name__, "error": str(exc)})
        return None, payload


def _median(values: list[float]) -> float | None:
    return float(statistics.median(values)) if values else None


def _parse_stdout(stdout: str) -> dict[str, object]:
    samples: dict[str, list[float]] = {"v4_early_exit": [], "materialized_fallback": []}
    for match in SAMPLE_RE.finditer(stdout):
        samples.setdefault(match.group(1), []).append(float(match.group(2)))
    pairs = {match.group(1): match.group(2).strip() for match in KEY_VALUE_RE.finditer(stdout)}
    parsed: dict[str, object] = {"samples_ms": samples}
    for route in ("v4_early_exit", "materialized_fallback"):
        route_samples = samples.get(route, [])
        median_ms = _median(route_samples)
        parsed[f"{route}_sample_count"] = len(route_samples)
        parsed[f"{route}_median_ms"] = median_ms
        parsed[f"{route}_median_s"] = (median_ms / 1000.0) if median_ms is not None else None
        inv_key = f"{route}_anyhit_invocations"
        accepted_key = f"{route}_accepted_count"
        parsed[inv_key] = int(pairs[inv_key]) if inv_key in pairs else None
        parsed[accepted_key] = int(pairs[accepted_key]) if accepted_key in pairs else None
    for key in ("ray_count", "candidates_per_ray", "active_rays", "accept_layer", "expected_accepted"):
        if key in pairs:
            parsed[key] = int(pairs[key])
    expected = parsed.get("expected_accepted")
    parsed["v4_correctness_passed"] = (
        parsed.get("v4_early_exit_accepted_count") == expected if expected is not None else False
    )
    parsed["materialized_fallback_correctness_passed"] = (
        parsed.get("materialized_fallback_accepted_count") == expected if expected is not None else False
    )
    v4_inv = parsed.get("v4_early_exit_anyhit_invocations")
    fb_inv = parsed.get("materialized_fallback_anyhit_invocations")
    parsed["early_termination_observed"] = (
        isinstance(v4_inv, int) and isinstance(fb_inv, int) and v4_inv < fb_inv
    )
    return parsed


def _scan_for_custom_predicate_route(root: Path) -> dict[str, object]:
    result: dict[str, object] = {
        "root": str(root),
        "exists": root.exists(),
        "has_custom_predicate_early_exit_route": False,
        "matched_files": [],
    }
    if not root.exists():
        result["selected_baseline"] = "root_missing_materialized_all_hit_ids_plus_device_predicate_reduce_fallback"
        return result
    patterns = ("custom_predicate_early_exit", "terminate_on_first_accept", "predicate early-exit")
    matched: list[str] = []
    for base in ("src", "scripts"):
        search_root = root / base
        if not search_root.exists():
            continue
        for path in search_root.rglob("*"):
            if path.suffix.lower() not in {".py", ".cu", ".cpp", ".h", ".hpp", ".md"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if any(pattern in text for pattern in patterns):
                matched.append(str(path))
    result["matched_files"] = matched[:20]
    result["has_custom_predicate_early_exit_route"] = bool(matched)
    result["selected_baseline"] = (
        "exact_repo_custom_predicate_early_exit_route_requires_manual_selection"
        if matched
        else "materialized_all_hit_ids_plus_device_predicate_reduce_fallback"
    )
    return result


def _denominator_discovery(v2_root: Path, v3_root: Path) -> dict[str, object]:
    v2 = _scan_for_custom_predicate_route(v2_root)
    v3 = _scan_for_custom_predicate_route(v3_root)
    no_custom = not v2["has_custom_predicate_early_exit_route"] and not v3["has_custom_predicate_early_exit_route"]
    return {
        "completed_before_v4_timing": True,
        "v2_14": v2,
        "v3_0_2": v3,
        "quality": "strong_materialized_device_fallback_after_no_custom_repo_route_found" if no_custom else "custom_repo_route_detected_manual_denominator_required",
        "fallback_description": (
            "The fallback traces the same OptiX geometry, materializes all hit layers on device, "
            "then evaluates the predicate and reduces accepted flags in separate device kernels. "
            "It does not receive V4 any-hit predicate early termination."
        ),
    }


def _compile_loader(tmp_path: Path, env: dict[str, str], toolchain: dict[str, object]) -> tuple[Path | None, dict[str, object]]:
    source = tmp_path / "v4_goal4715_timing.cu"
    binary = tmp_path / "v4_goal4715_timing"
    source.write_text(CPP_SOURCE, encoding="utf-8")
    proc = _run(
        [
            str(toolchain["nvcc"]),
            "-std=c++17",
            "-O2",
            "-I",
            str(toolchain["optix_include"]),
            "-I",
            str(Path(str(toolchain["cuda_root"])) / "include"),
            str(source),
            "-L",
            str(toolchain["cuda_lib_dir"]),
            "-lcuda",
            "-ldl",
            "-o",
            str(binary),
        ],
        cwd=tmp_path,
        env=env,
    )
    record = {"returncode": proc.returncode, "stdout": proc.stdout.strip()[:4000], "stderr": proc.stderr.strip()[:4000]}
    return (binary if proc.returncode == 0 and binary.exists() else None), record


def _base_payload(
    dry_run: bool,
    scales: tuple[int, ...],
    warmups: int,
    repeat: int,
) -> dict[str, object]:
    return {
        "schema": "rtdl.v4.goal4715_custom_predicate_early_exit_timing.v1",
        "status": "dry_run" if dry_run else "unknown",
        "dry_run": dry_run,
        "parameters": {"scales": scales, "warmups": warmups, "repeat": repeat},
        "protocol_validation": validate_v4_goal4713_custom_predicate_early_exit_protocol(),
        "result_contract_validation": validate_v4_goal4715_custom_predicate_early_exit_timing_result_contract(),
        "denominator_discovery": None,
        "rows": [],
        "classification": None,
        "release_authorized": False,
        "formal_high_performance_authorized": False,
        "app_level_speed_claim_authorized": False,
        "public_tier3_support_authorized": False,
        "arbitrary_callback_authorized": False,
        "raw_optix_callback_authorized": False,
    }


def _regime_rows() -> tuple[tuple[str, int, str], ...]:
    return (
        ("dense_early_accept_k8", 8, "primary"),
        ("dense_early_accept_k32", 32, "primary"),
        ("sparse_early_accept_k32", 32, "primary"),
        ("dense_late_accept_k32", 32, "control"),
        ("dense_reject_all_k32", 32, "control"),
        ("no_hit_empty", 0, "control"),
    )


def _run_timing(
    dry_run: bool,
    scales: tuple[int, ...],
    warmups: int,
    repeat: int,
    v2_root: Path,
    v3_root: Path,
) -> dict[str, object]:
    payload = _base_payload(dry_run, scales, warmups, repeat)
    if dry_run:
        payload["denominator_discovery"] = {
            "completed_before_v4_timing": True,
            "v2_14": {"selected_baseline": "materialized_all_hit_ids_plus_device_predicate_reduce_fallback"},
            "v3_0_2": {"selected_baseline": "materialized_all_hit_ids_plus_device_predicate_reduce_fallback"},
        }
        payload["status"] = (
            "dry_run_contract_passed"
            if payload["protocol_validation"]["status"] == "passed"
            and payload["result_contract_validation"]["status"] == "passed"
            else "dry_run_contract_failed"
        )
        return payload

    denominator_discovery = _denominator_discovery(v2_root, v3_root)
    payload["denominator_discovery"] = denominator_discovery
    toolchain = _toolchain()
    payload["toolchain"] = toolchain
    if not all(toolchain.values()):
        payload.update({"status": "blocked", "blocked_stage": "toolchain_discovery"})
        return payload
    with tempfile.TemporaryDirectory(prefix="rtdl-v4-goal4715-timing-") as tmp:
        tmp_path = Path(tmp)
        env = dict(os.environ)
        env["LD_LIBRARY_PATH"] = os.pathsep.join(
            [str(toolchain["cuda_lib_dir"]), "/usr/lib/x86_64-linux-gnu", env.get("LD_LIBRARY_PATH", "")]
        )
        binary, loader_compile = _compile_loader(tmp_path, env, toolchain)
        payload["loader_compile"] = loader_compile
        if binary is None:
            payload.update({"status": "blocked", "blocked_stage": "loader_compile"})
            return payload
        callback_ptx, ptx_payload = _compile_predicate_ptx()
        payload["ptx_generation"] = ptx_payload
        if callback_ptx is None:
            payload.update({"status": "blocked", "blocked_stage": "numba_ptx_generation"})
            return payload
        symbol_probe = extract_numba_callback_symbol_from_ptx(callback_ptx, callback_name_hint="accept_layer_predicate")
        payload["symbol_probe"] = symbol_probe.as_dict()
        if symbol_probe.status != "symbol_extracted" or not symbol_probe.symbol:
            payload.update({"status": "blocked", "blocked_stage": "callback_symbol_extraction"})
            return payload
        wrapper_cu = tmp_path / "goal4715_wrapper.cu"
        wrapper_ptx = tmp_path / "goal4715_wrapper.ptx"
        wrapper_cu.write_text(_callback_wrapper_source(symbol_probe.symbol) + "\n", encoding="utf-8")
        wrapper_compile = _run(
            [
                str(toolchain["nvcc"]),
                "-ptx",
                "-std=c++17",
                "--keep-device-functions",
                "-I",
                str(toolchain["optix_include"]),
                str(wrapper_cu),
                "-o",
                str(wrapper_ptx),
            ],
            cwd=tmp_path,
            env=env,
        )
        payload["wrapper_compile"] = {
            "returncode": wrapper_compile.returncode,
            "stdout": wrapper_compile.stdout.strip()[:4000],
            "stderr": wrapper_compile.stderr.strip()[:4000],
        }
        if wrapper_compile.returncode != 0 or not wrapper_ptx.exists():
            payload.update({"status": "blocked", "blocked_stage": "wrapper_compile"})
            return payload
        combined_ptx = tmp_path / "goal4715_combined.ptx"
        combined_ptx.write_text(
            compose_goal4688_combined_ptx(callback_ptx, wrapper_ptx.read_text(encoding="utf-8")),
            encoding="utf-8",
        )
        rows = []
        for scale in scales:
            for regime, candidates, role in _regime_rows():
                print(f"goal4715 timing start scale={scale} regime={regime} candidates={candidates}", file=sys.stderr, flush=True)
                proc = _run(
                    [str(binary), str(combined_ptx), regime, str(scale), str(candidates), str(warmups), str(repeat)],
                    cwd=tmp_path,
                    env=env,
                )
                parsed = _parse_stdout(proc.stdout)
                v4_s = parsed.get("v4_early_exit_median_s")
                fallback_s = parsed.get("materialized_fallback_median_s")
                row = {
                    "regime": regime,
                    "row_role": role,
                    "scale": scale,
                    "candidates_per_ray": candidates,
                    "returncode": proc.returncode,
                    "stdout": proc.stdout.strip()[:12000],
                    "stderr": proc.stderr.strip()[:4000],
                    "v4_median_s": v4_s,
                    "materialized_fallback_median_s": fallback_s,
                    "v2_baseline_median_s": fallback_s,
                    "v3_baseline_median_s": fallback_s,
                    "v2_baseline_over_v4_ratio": (float(fallback_s) / float(v4_s)) if v4_s and fallback_s else None,
                    "v3_baseline_over_v4_ratio": (float(fallback_s) / float(v4_s)) if v4_s and fallback_s else None,
                    "v4_correctness_passed": proc.returncode == 0 and bool(parsed.get("v4_correctness_passed")),
                    "materialized_fallback_correctness_passed": proc.returncode == 0 and bool(parsed.get("materialized_fallback_correctness_passed")),
                    "v4_anyhit_invocations": parsed.get("v4_early_exit_anyhit_invocations"),
                    "fallback_all_hit_invocations": parsed.get("materialized_fallback_anyhit_invocations"),
                    "early_termination_observed": bool(parsed.get("early_termination_observed")),
                    "parsed": parsed,
                    "route_boundary": "v4_any_hit_predicate_early_exit_vs_materialized_all_hit_ids_device_predicate_reduce_fallback",
                }
                rows.append(row)
                print(
                    f"goal4715 timing done scale={scale} regime={regime} correctness="
                    f"{row['v4_correctness_passed'] and row['materialized_fallback_correctness_passed']} "
                    f"ratio={row['v3_baseline_over_v4_ratio']}",
                    file=sys.stderr,
                    flush=True,
                )
                if proc.returncode != 0:
                    payload["rows"] = rows
                    payload.update({"status": "blocked", "blocked_stage": f"row_{scale}_{regime}"})
                    return payload
        payload["rows"] = rows
        payload["classification"] = classify_v4_goal4715_custom_predicate_early_exit_timing(rows, denominator_discovery)
        payload["status"] = "goal4715_custom_predicate_early_exit_timing_measured_not_release"
        return payload


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    classification = payload.get("classification") or {}
    lines = [
        "# V4 Goal4715 Custom Predicate Early-Exit Timing",
        "",
        f"- status: `{payload['status']}`",
        f"- classification: `{classification.get('classification')}`",
        f"- primary geomean V3 speedup: `{classification.get('primary_geomean_v3_speedup')}`",
        f"- min primary V3 speedup: `{classification.get('min_primary_v3_speedup')}`",
        "",
        "| scale | regime | role | ok | V4 s | fallback s | fallback/V4 | V4 invocations | fallback invocations |",
        "|---:|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in payload.get("rows", []):
        ratio = row.get("v3_baseline_over_v4_ratio")
        lines.append(
            "| {scale} | `{regime}` | `{role}` | {ok} | {v4:.9f} | {fallback:.9f} | {ratio} | {v4_inv} | {fb_inv} |".format(
                scale=row["scale"],
                regime=row["regime"],
                role=row["row_role"],
                ok=str(bool(row.get("v4_correctness_passed") and row.get("materialized_fallback_correctness_passed"))).lower(),
                v4=float(row.get("v4_median_s") or 0.0),
                fallback=float(row.get("materialized_fallback_median_s") or 0.0),
                ratio=f"{float(ratio):.3f}x" if ratio is not None else "n/a",
                v4_inv=row.get("v4_anyhit_invocations"),
                fb_inv=row.get("fallback_all_hit_invocations"),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This gate compares V4 any-hit predicate early termination against a materialized-device fallback that traces the same geometry, writes all hit layers to device memory, then evaluates the predicate and reduces accepted flags in separate device kernels. It does not authorize release, public Tier-3 support, arbitrary callback support, raw OptiX callback support, or all-app claims.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V4 Goal4715 custom predicate early-exit focused POD timing gate.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--scales", default=",".join(str(item) for item in DEFAULT_SCALES))
    parser.add_argument("--warmups", type=int, default=DEFAULT_WARMUPS)
    parser.add_argument("--repeat", type=int, default=DEFAULT_REPEAT)
    parser.add_argument("--v2-root", type=Path, default=ROOT_V2_14)
    parser.add_argument("--v3-root", type=Path, default=ROOT_V3_0_2)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()
    scales = tuple(int(item) for item in str(args.scales).split(",") if item.strip())
    payload = _run_timing(
        dry_run=bool(args.dry_run),
        scales=scales,
        warmups=int(args.warmups),
        repeat=int(args.repeat),
        v2_root=args.v2_root,
        v3_root=args.v3_root,
    )
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        _write_markdown(args.md_out, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] in {"dry_run_contract_passed", "goal4715_custom_predicate_early_exit_timing_measured_not_release"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

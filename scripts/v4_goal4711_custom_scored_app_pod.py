from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import statistics
import sys
import tempfile
import time
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
for path in (SRC, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from rtdsl.v4_goal4687_tier3_wrapper_compile_probe import extract_numba_callback_symbol_from_ptx
from rtdsl.v4_goal4688_tier3_module_link_probe import compose_goal4688_combined_ptx
from rtdsl.v4_goal4698_specialized_tier3_compile_cache import plan_v4_goal4698_specialized_tier3_compile
from rtdsl.v4_goal4710_custom_scored_app_protocol import validate_v4_goal4710_custom_scored_app_protocol
from rtdsl.v4_goal4711_custom_scored_app_result import (
    classify_v4_goal4711_custom_scored_app_result,
    validate_v4_goal4711_custom_scored_app_result_contract,
)
from v4_goal4688_tier3_module_link_probe import _compiler
from v4_goal4688_tier3_module_link_probe import _find_cuda_lib_dir
from v4_goal4688_tier3_module_link_probe import _find_cuda_root
from v4_goal4688_tier3_module_link_probe import _find_nvcc
from v4_goal4688_tier3_module_link_probe import _find_optix_include
from v4_goal4688_tier3_module_link_probe import _run
from v4_tier3_numba_ptx_probe import _configure_numba_legacy_nvvm_env
from v4_tier3_numba_ptx_probe import _maybe_reexec_with_nvvm_ld_path


DEFAULT_WARMUPS = 2
DEFAULT_REPEAT = 7
DEFAULT_SCALES = (262144, 524288)
DEFAULT_REGIMES = ("dense_hits", "sparse_hits", "no_hit_empty_reduction")
ROOT_V2_14 = Path("/root/rtdl_v2_14_tag")
ROOT_V3_0_2 = Path("/root/rtdl_v3_0_2_tag")
KEY_VALUE_RE = re.compile(r"^([A-Za-z0-9_]+)=([^\n]+)$", re.MULTILINE)
SAMPLE_RE = re.compile(r"^sample_([A-Za-z0-9_]+)_ms=([0-9.eE+-]+)$", re.MULTILINE)


VARIANT_META: dict[str, dict[str, str]] = {
    "custom_scalar_reduce_weighted_sum": {
        "protocol_callback": "weighted_sum",
        "callback_role": "control",
        "contract_shape": "custom_scalar_reduce",
    },
    "custom_score_affine": {
        "protocol_callback": "affine_score",
        "callback_role": "primary",
        "contract_shape": "custom_score",
    },
    "custom_threshold_flag": {
        "protocol_callback": "threshold_score",
        "callback_role": "primary",
        "contract_shape": "custom_threshold",
    },
    "custom_minmax_score": {
        "protocol_callback": "minmax_score",
        "callback_role": "primary",
        "contract_shape": "custom_minmax",
    },
}


def custom_scalar_reduce_weighted_sum(hit_distance, primitive_id, weight, state):
    return state + hit_distance * weight + primitive_id * 0.0


def custom_score_affine(hit_distance, primitive_id, weight, state):
    return state + weight * 2.0 + 3.0 + hit_distance * 0.0 + primitive_id * 0.0


def custom_threshold_flag(hit_distance, primitive_id, weight, state):
    return 1.0 if weight >= 1.0 else 0.0


def custom_minmax_score(hit_distance, primitive_id, weight, state):
    return (primitive_id % 17) + 1.0 + hit_distance * 0.0 + weight * 0.0 + state * 0.0


VARIANT_FUNCTIONS: dict[str, Callable[..., float]] = {
    "custom_scalar_reduce_weighted_sum": custom_scalar_reduce_weighted_sum,
    "custom_score_affine": custom_score_affine,
    "custom_threshold_flag": custom_threshold_flag,
    "custom_minmax_score": custom_minmax_score,
}


CPP_SOURCE = r"""
#include <cuda.h>
#include <cuda_runtime.h>
#include <optix.h>
#include <optix_function_table_definition.h>
#include <optix_stubs.h>

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
    unsigned long long* output_sum;
    unsigned long long* materialized_values;
    unsigned int ray_count;
    unsigned int route_mode;
};

struct Float3 { float x; float y; float z; };
struct UInt3 { unsigned int x; unsigned int y; unsigned int z; };

__global__ void reduce_u64_kernel(const unsigned long long* values, unsigned long long* output, unsigned int n) {
    unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x;
    unsigned int stride = blockDim.x * gridDim.x;
    unsigned long long local = 0ull;
    for (unsigned int i = idx; i < n; i += stride) {
        local += values[i];
    }
    if (local != 0ull) {
        atomicAdd(output, local);
    }
}

__device__ unsigned long long score_from_hit_id_plus_one(unsigned long long hit_id_plus_one, unsigned int variant_code) {
    if (hit_id_plus_one == 0ull) return 0ull;
    unsigned long long primitive_id = hit_id_plus_one - 1ull;
    if (variant_code == 0u) {
        return hit_id_plus_one;
    }
    if (variant_code == 1u) {
        return 2ull * hit_id_plus_one + 3ull;
    }
    if (variant_code == 2u) {
        return 1ull;
    }
    return (primitive_id % 17ull) + 1ull;
}

__global__ void reduce_hit_id_callback_kernel(
    const unsigned long long* hit_ids_plus_one,
    unsigned long long* output,
    unsigned int n,
    unsigned int variant_code) {
    unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x;
    unsigned int stride = blockDim.x * gridDim.x;
    unsigned long long local = 0ull;
    for (unsigned int i = idx; i < n; i += stride) {
        local += score_from_hit_id_plus_one(hit_ids_plus_one[i], variant_code);
    }
    if (local != 0ull) {
        atomicAdd(output, local);
    }
}

static std::string read_text(const char* path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) throw std::runtime_error(std::string("failed to open PTX file: ") + path);
    std::ostringstream buffer;
    buffer << in.rdbuf();
    return buffer.str();
}

static void check_cuda(CUresult result, const char* what) {
    if (result == CUDA_SUCCESS) return;
    const char* raw = nullptr;
    cuGetErrorString(result, &raw);
    throw std::runtime_error(std::string(what) + ": " + (raw ? raw : "unknown CUDA error"));
}

static void check_runtime(cudaError_t result, const char* what) {
    if (result == cudaSuccess) return;
    throw std::runtime_error(std::string(what) + ": " + cudaGetErrorString(result));
}

static void check_optix(OptixResult result, const char* what) {
    if (result == OPTIX_SUCCESS) return;
    throw std::runtime_error(std::string(what) + ": " + optixGetErrorString(result));
}

static OptixProgramGroup create_program_group(
    OptixDeviceContext ctx,
    const OptixProgramGroupDesc& desc,
    const char* what) {
    OptixProgramGroupOptions options = {};
    char log[8192] = {};
    size_t log_size = sizeof(log);
    OptixProgramGroup group = nullptr;
    OptixResult result = optixProgramGroupCreate(ctx, &desc, 1, &options, log, &log_size, &group);
    std::cout << what << "_result=" << static_cast<int>(result) << "\n";
    check_optix(result, what);
    return group;
}

static unsigned int hit_count_for(const std::string& dataset, unsigned int ray_count) {
    if (dataset == "dense_hits") return ray_count;
    if (dataset == "sparse_hits") return (ray_count + 3u) / 4u;
    return 0u;
}

static unsigned long long expected_for(const std::string& variant, unsigned int hit_count) {
    unsigned long long total = 0ull;
    for (unsigned int i = 0; i < hit_count; ++i) {
        if (variant == "custom_scalar_reduce_weighted_sum") {
            total += static_cast<unsigned long long>(i + 1u);
        } else if (variant == "custom_score_affine") {
            total += static_cast<unsigned long long>(2u * (i + 1u) + 3u);
        } else if (variant == "custom_threshold_flag") {
            total += 1ull;
        } else if (variant == "custom_minmax_score") {
            total += static_cast<unsigned long long>((i % 17u) + 1u);
        }
    }
    return total;
}

static unsigned int variant_code_for(const std::string& variant) {
    if (variant == "custom_scalar_reduce_weighted_sum") return 0u;
    if (variant == "custom_score_affine") return 1u;
    if (variant == "custom_threshold_flag") return 2u;
    return 3u;
}

static void run_one_route(
    const char* route_name,
    unsigned int route_mode,
    OptixPipeline pipeline,
    const OptixShaderBindingTable* sbt,
    CUdeviceptr params_dev,
    Params* params_host,
    unsigned long long* output_dev,
    unsigned long long* materialized_dev,
    unsigned int ray_count,
    unsigned int variant_code,
    unsigned int warmups,
    unsigned int measured) {

    params_host->route_mode = route_mode;
    check_runtime(cudaMemcpy(reinterpret_cast<void*>(params_dev), params_host, sizeof(Params), cudaMemcpyHostToDevice),
                  "copy params route");
    for (unsigned int i = 0; i < warmups; ++i) {
        check_runtime(cudaMemset(output_dev, 0, sizeof(unsigned long long)), "warmup reset output");
        if (route_mode == 1u || route_mode == 2u) {
            check_runtime(cudaMemset(materialized_dev, 0, sizeof(unsigned long long) * ray_count), "warmup reset materialized");
        }
        check_optix(optixLaunch(pipeline, 0, params_dev, sizeof(Params), sbt, ray_count, 1, 1), "warmup optixLaunch");
        if (route_mode == 1u) {
            unsigned int block = 256u;
            unsigned int grid = (ray_count + block - 1u) / block;
            if (grid > 4096u) grid = 4096u;
            reduce_u64_kernel<<<grid, block>>>(materialized_dev, output_dev, ray_count);
            check_runtime(cudaGetLastError(), "warmup reduce launch");
        } else if (route_mode == 2u) {
            unsigned int block = 256u;
            unsigned int grid = (ray_count + block - 1u) / block;
            if (grid > 4096u) grid = 4096u;
            reduce_hit_id_callback_kernel<<<grid, block>>>(materialized_dev, output_dev, ray_count, variant_code);
            check_runtime(cudaGetLastError(), "warmup hit-id callback reduce launch");
        }
        check_runtime(cudaDeviceSynchronize(), "warmup sync");
    }

    cudaEvent_t start = nullptr;
    cudaEvent_t stop = nullptr;
    check_runtime(cudaEventCreate(&start), "event start create");
    check_runtime(cudaEventCreate(&stop), "event stop create");
    for (unsigned int i = 0; i < measured; ++i) {
        check_runtime(cudaEventRecord(start, 0), "event start");
        check_runtime(cudaMemset(output_dev, 0, sizeof(unsigned long long)), "measured reset output");
        if (route_mode == 1u || route_mode == 2u) {
            check_runtime(cudaMemset(materialized_dev, 0, sizeof(unsigned long long) * ray_count), "measured reset materialized");
        }
        check_optix(optixLaunch(pipeline, 0, params_dev, sizeof(Params), sbt, ray_count, 1, 1), "measured optixLaunch");
        if (route_mode == 1u) {
            unsigned int block = 256u;
            unsigned int grid = (ray_count + block - 1u) / block;
            if (grid > 4096u) grid = 4096u;
            reduce_u64_kernel<<<grid, block>>>(materialized_dev, output_dev, ray_count);
            check_runtime(cudaGetLastError(), "measured reduce launch");
        } else if (route_mode == 2u) {
            unsigned int block = 256u;
            unsigned int grid = (ray_count + block - 1u) / block;
            if (grid > 4096u) grid = 4096u;
            reduce_hit_id_callback_kernel<<<grid, block>>>(materialized_dev, output_dev, ray_count, variant_code);
            check_runtime(cudaGetLastError(), "measured hit-id callback reduce launch");
        }
        check_runtime(cudaEventRecord(stop, 0), "event stop");
        check_runtime(cudaEventSynchronize(stop), "event sync");
        float ms = 0.0f;
        check_runtime(cudaEventElapsedTime(&ms, start, stop), "event elapsed");
        std::cout << "sample_" << route_name << "_ms=" << ms << "\n";
    }
    check_runtime(cudaDeviceSynchronize(), "measured sync");
    unsigned long long output_value = 0ull;
    check_runtime(cudaMemcpy(&output_value, output_dev, sizeof(unsigned long long), cudaMemcpyDeviceToHost),
                  "copy route output");
    std::cout << "output_" << route_name << "=" << output_value << "\n";
    check_runtime(cudaEventDestroy(start), "event start destroy");
    check_runtime(cudaEventDestroy(stop), "event stop destroy");
}

int main(int argc, char** argv) {
    try {
        if (argc != 7) {
            std::cerr << "usage: v4_goal4711_custom_scored_app <ptx> <variant> <dataset> <ray_count> <warmups> <measured>\n";
            return 64;
        }
        std::string ptx = read_text(argv[1]);
        std::string variant = argv[2];
        std::string dataset = argv[3];
        unsigned int ray_count = static_cast<unsigned int>(std::stoul(argv[4]));
        unsigned int warmups = static_cast<unsigned int>(std::stoul(argv[5]));
        unsigned int measured = static_cast<unsigned int>(std::stoul(argv[6]));
        unsigned int hit_count = hit_count_for(dataset, ray_count);
        unsigned int triangle_count = dataset == "no_hit_empty_reduction" ? 1u : hit_count;

        check_runtime(cudaFree(nullptr), "cuda init");
        CUcontext cu_ctx = nullptr;
        check_cuda(cuCtxGetCurrent(&cu_ctx), "cuCtxGetCurrent");
        if (cu_ctx == nullptr) throw std::runtime_error("no current CUDA context after runtime initialization");
        check_optix(optixInit(), "optixInit");
        OptixDeviceContextOptions context_options = {};
        OptixDeviceContext optix_ctx = nullptr;
        check_optix(optixDeviceContextCreate(cu_ctx, &context_options, &optix_ctx), "optixDeviceContextCreate");

        std::vector<Float3> vertices;
        std::vector<UInt3> indices;
        vertices.reserve(static_cast<size_t>(triangle_count) * 3u);
        indices.reserve(triangle_count);
        for (unsigned int h = 0; h < triangle_count; ++h) {
            unsigned int ray_idx = dataset == "sparse_hits" ? h * 4u : h;
            float x = static_cast<float>((ray_idx % 256u) * 2u);
            float y = static_cast<float>((ray_idx / 256u) * 2u);
            float z = dataset == "no_hit_empty_reduction" ? 100.0f : 1.0f;
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
        check_runtime(cudaMemcpy(vertices_dev, vertices.data(), vertices.size() * sizeof(Float3), cudaMemcpyHostToDevice),
                      "copy vertices");
        check_runtime(cudaMemcpy(indices_dev, indices.data(), indices.size() * sizeof(UInt3), cudaMemcpyHostToDevice),
                      "copy indices");

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
        unsigned int geometry_flags = OPTIX_GEOMETRY_FLAG_NONE;
        build_input.triangleArray.flags = &geometry_flags;
        build_input.triangleArray.numSbtRecords = 1;

        OptixAccelBuildOptions accel_options = {};
        accel_options.buildFlags = OPTIX_BUILD_FLAG_ALLOW_COMPACTION;
        accel_options.operation = OPTIX_BUILD_OPERATION_BUILD;
        OptixAccelBufferSizes accel_sizes = {};
        check_optix(optixAccelComputeMemoryUsage(optix_ctx, &accel_options, &build_input, 1, &accel_sizes),
                    "optixAccelComputeMemoryUsage");
        void* temp_dev = nullptr;
        void* gas_dev = nullptr;
        check_runtime(cudaMalloc(&temp_dev, accel_sizes.tempSizeInBytes), "alloc temp");
        check_runtime(cudaMalloc(&gas_dev, accel_sizes.outputSizeInBytes), "alloc gas");
        OptixTraversableHandle gas_handle = 0;
        check_optix(optixAccelBuild(optix_ctx, 0, &accel_options, &build_input, 1,
                                    reinterpret_cast<CUdeviceptr>(temp_dev), accel_sizes.tempSizeInBytes,
                                    reinterpret_cast<CUdeviceptr>(gas_dev), accel_sizes.outputSizeInBytes,
                                    &gas_handle, nullptr, 0),
                    "optixAccelBuild");
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
        check_optix(module_result, "optixModuleCreate");

        OptixProgramGroupDesc raygen_desc = {};
        raygen_desc.kind = OPTIX_PROGRAM_GROUP_KIND_RAYGEN;
        raygen_desc.raygen.module = module;
        raygen_desc.raygen.entryFunctionName = "__raygen__rtdl_goal4711_custom_scored";
        OptixProgramGroupDesc miss_desc = {};
        miss_desc.kind = OPTIX_PROGRAM_GROUP_KIND_MISS;
        miss_desc.miss.module = module;
        miss_desc.miss.entryFunctionName = "__miss__rtdl_goal4711_custom_scored";
        OptixProgramGroupDesc hit_desc = {};
        hit_desc.kind = OPTIX_PROGRAM_GROUP_KIND_HITGROUP;
        hit_desc.hitgroup.moduleAH = module;
        hit_desc.hitgroup.entryFunctionNameAH = "__anyhit__rtdl_goal4711_custom_scored";
        OptixProgramGroup raygen_pg = create_program_group(optix_ctx, raygen_desc, "raygen_program_group");
        OptixProgramGroup miss_pg = create_program_group(optix_ctx, miss_desc, "miss_program_group");
        OptixProgramGroup hit_pg = create_program_group(optix_ctx, hit_desc, "hit_program_group");
        std::vector<OptixProgramGroup> groups = {raygen_pg, miss_pg, hit_pg};
        OptixPipelineLinkOptions link_options = {};
        link_options.maxTraceDepth = 1;
        char pipeline_log[16384] = {};
        size_t pipeline_log_size = sizeof(pipeline_log);
        OptixPipeline pipeline = nullptr;
        OptixResult pipeline_result = optixPipelineCreate(optix_ctx, &pipeline_options, &link_options,
                                                          groups.data(), static_cast<unsigned int>(groups.size()),
                                                          pipeline_log, &pipeline_log_size, &pipeline);
        std::cout << "pipeline_create_result=" << static_cast<int>(pipeline_result) << "\n";
        check_optix(pipeline_result, "optixPipelineCreate");

        check_optix(optixPipelineSetStackSize(pipeline, 8192, 8192, 8192, 1),
                    "optixPipelineSetStackSize");

        RaygenRecord raygen_rec = {};
        MissRecord miss_rec = {};
        HitRecord hit_rec = {};
        check_optix(optixSbtRecordPackHeader(raygen_pg, &raygen_rec), "pack raygen");
        check_optix(optixSbtRecordPackHeader(miss_pg, &miss_rec), "pack miss");
        check_optix(optixSbtRecordPackHeader(hit_pg, &hit_rec), "pack hit");
        void* raygen_dev = nullptr;
        void* miss_dev = nullptr;
        void* hit_dev = nullptr;
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

        unsigned long long* output_dev = nullptr;
        unsigned long long* materialized_dev = nullptr;
        Params* params_dev_raw = nullptr;
        check_runtime(cudaMalloc(reinterpret_cast<void**>(&output_dev), sizeof(unsigned long long)), "alloc output");
        check_runtime(cudaMalloc(reinterpret_cast<void**>(&materialized_dev), sizeof(unsigned long long) * ray_count), "alloc materialized");
        check_runtime(cudaMalloc(reinterpret_cast<void**>(&params_dev_raw), sizeof(Params)), "alloc params");
        Params params = {};
        params.handle = gas_handle;
        params.output_sum = output_dev;
        params.materialized_values = materialized_dev;
        params.ray_count = ray_count;
        params.route_mode = 0u;
        CUdeviceptr params_dev = reinterpret_cast<CUdeviceptr>(params_dev_raw);
        unsigned int variant_code = variant_code_for(variant);

        run_one_route("global_atomic_control", 0u, pipeline, &sbt, params_dev, &params, output_dev, materialized_dev,
                      ray_count, variant_code, warmups, measured);
        run_one_route("v4_callback_contribution", 1u, pipeline, &sbt, params_dev, &params, output_dev,
                      materialized_dev, ray_count, variant_code, warmups, measured);
        run_one_route("hit_id_fallback", 2u, pipeline, &sbt, params_dev, &params, output_dev,
                      materialized_dev, ray_count, variant_code, warmups, measured);

        unsigned long long expected = expected_for(variant, hit_count);
        std::cout << "variant=" << variant << "\n";
        std::cout << "dataset=" << dataset << "\n";
        std::cout << "ray_count=" << ray_count << "\n";
        std::cout << "hit_count=" << hit_count << "\n";
        std::cout << "expected_sum=" << expected << "\n";
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
    double payload0,
    double state0);

struct RtdlGoal4711Params {{
    OptixTraversableHandle handle;
    unsigned long long* output_sum;
    unsigned long long* materialized_values;
    unsigned int ray_count;
    unsigned int route_mode;
}};

extern "C" {{
__constant__ RtdlGoal4711Params params;
}}

extern "C" __global__ void __raygen__rtdl_goal4711_custom_scored() {{
    const unsigned int idx = optixGetLaunchIndex().x;
    if (idx >= params.ray_count) return;
    const float x = (float)((idx % 256u) * 2u);
    const float y = (float)((idx / 256u) * 2u);
    const float3 origin = make_float3(x, y, 0.0f);
    const float3 direction = make_float3(0.0f, 0.0f, 1.0f);
    optixTrace(params.handle, origin, direction, 0.0f, 10.0f, 0.0f,
               OptixVisibilityMask(255), OPTIX_RAY_FLAG_DISABLE_CLOSESTHIT,
               0, 1, 0);
}}

extern "C" __global__ void __miss__rtdl_goal4711_custom_scored() {{
}}

extern "C" __global__ void __anyhit__rtdl_goal4711_custom_scored() {{
    const unsigned int launch_idx = optixGetLaunchIndex().x;
    const unsigned int primitive_id = optixGetPrimitiveIndex();
    const double weight = (double)(primitive_id + 1u);
    const double value = {callback_symbol}(1.0, primitive_id, weight, 0.0);
    const unsigned long long contribution = value < 0.0 ? 0ull : (unsigned long long)(value + 0.5);
    if (params.route_mode == 0u) {{
        atomicAdd(params.output_sum, contribution);
    }} else if (params.route_mode == 1u) {{
        params.materialized_values[launch_idx] = contribution;
    }} else {{
        params.materialized_values[launch_idx] = (unsigned long long)(primitive_id + 1u);
    }}
    optixTerminateRay();
}}
""".strip()


def _median(values: list[float]) -> float | None:
    return float(statistics.median(values)) if values else None


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _scan_root_for_routes(root: Path) -> dict[str, object]:
    terms = {
        "specialized_tier3": ("specialized_tier3", "module_specialized_direct_device_callback"),
        "custom_callbacks": ("custom_score_affine", "custom_threshold_flag", "custom_minmax_score", "numba_cabi_device_function"),
        "weighted_sum": ("ray_triangle_any_hit_weighted_sum", "weighted_any_hit_sum", "weighted_sum"),
    }
    result: dict[str, object] = {
        "root": str(root),
        "exists": root.exists(),
        "hits": {name: [] for name in terms},
        "has_specialized_custom_callback_route": False,
        "has_weighted_sum_route": False,
        "selected_baseline": None,
        "baseline_reason": "",
    }
    if not root.exists():
        result["selected_baseline"] = "missing_root_invalid"
        result["baseline_reason"] = "root does not exist"
        return result

    search_roots = [root / "src", root / "scripts", root / "examples"]
    suffixes = {".py", ".cu", ".cpp", ".h", ".hpp", ".md"}
    file_count = 0
    for base in search_roots:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            file_count += 1
            if file_count > 6000:
                break
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for name, needles in terms.items():
                if any(needle in text for needle in needles):
                    hits = result["hits"][name]
                    if isinstance(hits, list) and len(hits) < 20:
                        hits.append(str(path.relative_to(root)))
        if file_count > 6000:
            break
    result["file_count_scanned"] = file_count
    result["has_specialized_custom_callback_route"] = bool(result["hits"]["specialized_tier3"] or result["hits"]["custom_callbacks"])
    result["has_weighted_sum_route"] = bool(result["hits"]["weighted_sum"])
    if result["has_specialized_custom_callback_route"]:
        result["selected_baseline"] = "exact_repo_custom_callback_route_requires_manual_selection"
        result["baseline_reason"] = "repo contains custom callback route strings; automatic fallback selection is invalid"
    else:
        result["selected_baseline"] = "materialized_hit_id_plus_device_callback_reduce_fallback"
        result["baseline_reason"] = (
            "no specialized custom-callback route strings found; use strong device fallback "
            "with same OptiX hit discovery, materialized hit IDs, and separate device callback/reduction"
        )
    return result


def _discover_denominators(v2_root: Path, v3_root: Path) -> dict[str, object]:
    started = _now()
    v2 = _scan_root_for_routes(v2_root)
    v3 = _scan_root_for_routes(v3_root)
    completed = _now()
    no_custom = not bool(v2.get("has_specialized_custom_callback_route")) and not bool(v3.get("has_specialized_custom_callback_route"))
    return {
        "started_utc": started,
        "completed_utc": completed,
        "completed_before_v4_timing": True,
        "v2_14": v2,
        "v3_0_2": v3,
        "quality": (
            "strong_materialized_device_fallback_after_no_custom_repo_route_found"
            if no_custom
            else "custom_repo_route_detected_manual_denominator_required"
        ),
    "fallback_description": (
        "The fallback is not a slow CPU path: it traces the same OptiX geometry, materializes hit IDs on device, "
        "then evaluates the callback and reduces in a separate device kernel. It does not get V4's callback-in-hit fusion."
    ),
    }


def _parse_route_output(stdout: str) -> dict[str, object]:
    samples: dict[str, list[float]] = {
        "global_atomic_control": [],
        "v4_callback_contribution": [],
        "hit_id_fallback": [],
    }
    for match in SAMPLE_RE.finditer(stdout):
        samples.setdefault(match.group(1), []).append(float(match.group(2)))
    pairs = {match.group(1): match.group(2).strip() for match in KEY_VALUE_RE.finditer(stdout)}
    parsed: dict[str, object] = {"samples_ms": samples}
    for route in ("global_atomic_control", "v4_callback_contribution", "hit_id_fallback"):
        route_samples = samples.get(route, [])
        median_ms = _median(route_samples)
        parsed[f"{route}_sample_count"] = len(route_samples)
        parsed[f"{route}_median_ms"] = median_ms
        parsed[f"{route}_median_s"] = (median_ms / 1000.0) if median_ms is not None else None
        output_key = f"output_{route}"
        parsed[f"{route}_output_sum"] = int(pairs[output_key]) if output_key in pairs else None
    for key in ("ray_count", "hit_count", "expected_sum"):
        if key in pairs:
            parsed[key] = int(pairs[key])
    for key in ("variant", "dataset"):
        if key in pairs:
            parsed[key] = pairs[key]
    expected = parsed.get("expected_sum")
    for route in ("global_atomic_control", "v4_callback_contribution", "hit_id_fallback"):
        parsed[f"{route}_correctness_passed"] = (
            parsed.get(f"{route}_output_sum") == expected if expected is not None else False
        )
    return parsed


def _compile_variant_ptx(variant: str) -> tuple[str | None, dict[str, object]]:
    payload: dict[str, object] = {"variant": variant, "status": "unknown"}
    try:
        from rtdsl.numba_partner_continuation import configure_numba_cuda_toolchain_environment

        toolchain = configure_numba_cuda_toolchain_environment()
        payload["numba_toolchain_environment"] = toolchain
        payload["numba_nvvm_reexec_environment"] = _maybe_reexec_with_nvvm_ld_path(toolchain)
        payload["numba_legacy_nvvm_environment"] = _configure_numba_legacy_nvvm_env(toolchain)
        from numba import cuda, types
    except Exception as exc:
        payload.update({"status": "blocked", "stage": "numba_ptx_generation", "error_type": type(exc).__name__, "error": str(exc)})
        return None, payload

    try:
        ptx, return_type = cuda.compile_ptx(
            VARIANT_FUNCTIONS[variant],
            (types.float64, types.uint32, types.float64, types.float64),
            device=True,
            fastmath=False,
            abi="c",
        )
        payload.update({"status": "ptx_generated", "return_type": str(return_type), "ptx_length": len(ptx)})
        return ptx, payload
    except Exception as exc:
        payload.update({"status": "blocked", "stage": "numba_ptx_generation", "error_type": type(exc).__name__, "error": str(exc)})
        return None, payload


def _toolchain() -> dict[str, object]:
    optix_include = _find_optix_include()
    cuda_root = _find_cuda_root()
    cuda_lib_dir = _find_cuda_lib_dir(cuda_root)
    return {
        "optix_include": str(optix_include) if optix_include else None,
        "cuda_root": str(cuda_root) if cuda_root else None,
        "cuda_lib_dir": str(cuda_lib_dir) if cuda_lib_dir else None,
        "nvcc": _find_nvcc(),
        "compiler": _compiler(),
    }


def _compile_loader(tmp_path: Path, env: dict[str, str], toolchain: dict[str, object]) -> tuple[Path | None, dict[str, object]]:
    source = tmp_path / "v4_goal4711_custom_scored_app.cu"
    binary = tmp_path / "v4_goal4711_custom_scored_app"
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


def _base_payload(dry_run: bool, scales: tuple[int, ...], regimes: tuple[str, ...], warmups: int, repeat: int) -> dict[str, object]:
    protocol_validation = validate_v4_goal4710_custom_scored_app_protocol()
    result_contract = validate_v4_goal4711_custom_scored_app_result_contract()
    return {
        "schema": "rtdl.v4.goal4711_custom_scored_app_pod.v1",
        "status": "dry_run" if dry_run else "unknown",
        "dry_run": dry_run,
        "protocol_validation": protocol_validation,
        "result_contract_validation": result_contract,
        "protocol": protocol_validation["protocol"],
        "parameters": {
            "scales": scales,
            "regimes": regimes,
            "warmups": warmups,
            "repeat": repeat,
        },
        "denominator_discovery": None,
        "toolchain": None,
        "rows": [],
        "classification": None,
        "release_authorized": False,
        "formal_high_performance_authorized": False,
        "app_level_speed_claim_authorized": False,
        "tier3_public_support_authorized": False,
        "arbitrary_callback_authorized": False,
        "raw_optix_callback_authorized": False,
    }


def _run_goal4711(
    *,
    dry_run: bool,
    scales: tuple[int, ...],
    regimes: tuple[str, ...],
    warmups: int,
    repeat: int,
    v2_root: Path,
    v3_root: Path,
) -> dict[str, object]:
    payload = _base_payload(dry_run, scales, regimes, warmups, repeat)
    if dry_run:
        payload["status"] = (
            "dry_run_contract_passed"
            if payload["protocol_validation"]["status"] == "passed"
            and payload["result_contract_validation"]["status"] == "passed"
            else "dry_run_contract_failed"
        )
        return payload

    denominator_discovery = _discover_denominators(v2_root, v3_root)
    payload["denominator_discovery"] = denominator_discovery
    if denominator_discovery["quality"] == "custom_repo_route_detected_manual_denominator_required":
        payload["status"] = "blocked_custom_repo_route_detected_manual_denominator_required"
        return payload

    toolchain = _toolchain()
    payload["toolchain"] = toolchain
    if not all(toolchain.values()):
        payload.update({"status": "blocked", "blocked_stage": "toolchain_discovery"})
        return payload

    with tempfile.TemporaryDirectory(prefix="rtdl-v4-goal4711-custom-scored-") as tmp:
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

        rows: list[dict[str, object]] = []
        for variant, meta in VARIANT_META.items():
            print(f"goal4711 variant compile start {variant}", file=sys.stderr, flush=True)
            callback_ptx, ptx_payload = _compile_variant_ptx(variant)
            variant_record: dict[str, object] = {"variant": variant, "ptx_generation": ptx_payload}
            if callback_ptx is None:
                payload.update({"status": "blocked", "blocked_stage": f"numba_ptx_generation_{variant}", "variant_record": variant_record})
                return payload
            symbol_probe = extract_numba_callback_symbol_from_ptx(callback_ptx, callback_name_hint=variant)
            variant_record["symbol_probe"] = symbol_probe.as_dict()
            if symbol_probe.status != "symbol_extracted" or not symbol_probe.symbol:
                payload.update({"status": "blocked", "blocked_stage": f"callback_symbol_extraction_{variant}", "variant_record": variant_record})
                return payload

            compile_plan = plan_v4_goal4698_specialized_tier3_compile(
                callback_shape=meta["contract_shape"],
                callback_language="numba",
                numba_cabi_device_function=True,
                callback_symbol=symbol_probe.symbol,
                callback_ptx=callback_ptx,
                toolchain_fingerprint=json.dumps(toolchain, sort_keys=True),
                optix_abi="8.0",
                compute_target="sm_86",
            ).as_dict()
            variant_record["compile_plan"] = compile_plan
            if not compile_plan["internal_compile_allowed"]:
                payload.update({"status": "blocked", "blocked_stage": f"compile_plan_{variant}", "variant_record": variant_record})
                return payload

            wrapper_cu = tmp_path / f"{variant}_wrapper.cu"
            wrapper_ptx = tmp_path / f"{variant}_wrapper.ptx"
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
            variant_record["wrapper_compile"] = {
                "returncode": wrapper_compile.returncode,
                "stdout": wrapper_compile.stdout.strip()[:4000],
                "stderr": wrapper_compile.stderr.strip()[:4000],
            }
            if wrapper_compile.returncode != 0 or not wrapper_ptx.exists():
                payload.update({"status": "blocked", "blocked_stage": f"wrapper_compile_{variant}", "variant_record": variant_record})
                return payload
            combined_ptx = tmp_path / f"{variant}_combined.ptx"
            combined_ptx.write_text(
                compose_goal4688_combined_ptx(callback_ptx, wrapper_ptx.read_text(encoding="utf-8")),
                encoding="utf-8",
            )
            payload.setdefault("variant_records", []).append(variant_record)

            for scale in scales:
                for regime in regimes:
                    print(
                        f"goal4711 row start variant={variant} callback={meta['protocol_callback']} "
                        f"regime={regime} scale={scale}",
                        file=sys.stderr,
                        flush=True,
                    )
                    proc = _run(
                        [str(binary), str(combined_ptx), variant, regime, str(scale), str(warmups), str(repeat)],
                        cwd=tmp_path,
                        env=env,
                    )
                    parsed = _parse_route_output(proc.stdout)
                    v4_s = parsed.get("v4_callback_contribution_median_s")
                    fallback_s = parsed.get("hit_id_fallback_median_s")
                    row = {
                        "variant": variant,
                        "protocol_callback": meta["protocol_callback"],
                        "callback_role": meta["callback_role"],
                        "regime": regime,
                        "scale": int(scale),
                        "returncode": proc.returncode,
                        "stdout": proc.stdout.strip()[:12000],
                        "stderr": proc.stderr.strip()[:4000],
                        "expected_sum": parsed.get("expected_sum"),
                        "global_atomic_control_output_sum": parsed.get("global_atomic_control_output_sum"),
                        "v4_fused_output_sum": parsed.get("v4_callback_contribution_output_sum"),
                        "materialized_fallback_output_sum": parsed.get("hit_id_fallback_output_sum"),
                        "global_atomic_control_correctness_passed": proc.returncode == 0 and bool(parsed.get("global_atomic_control_correctness_passed")),
                        "v4_fused_correctness_passed": proc.returncode == 0 and bool(parsed.get("v4_callback_contribution_correctness_passed")),
                        "materialized_fallback_correctness_passed": proc.returncode == 0 and bool(parsed.get("hit_id_fallback_correctness_passed")),
                        "global_atomic_control_median_s": parsed.get("global_atomic_control_median_s"),
                        "v4_fused_median_s": v4_s,
                        "materialized_fallback_median_s": fallback_s,
                        "v2_baseline_median_s": fallback_s,
                        "v3_baseline_median_s": fallback_s,
                        "v2_baseline_selected": denominator_discovery["v2_14"]["selected_baseline"],
                        "v3_baseline_selected": denominator_discovery["v3_0_2"]["selected_baseline"],
                        "v2_baseline_over_v4_ratio": (float(fallback_s) / float(v4_s)) if v4_s and fallback_s else None,
                        "v3_baseline_over_v4_ratio": (float(fallback_s) / float(v4_s)) if v4_s and fallback_s else None,
                        "counts_toward_primary_claim": meta["callback_role"] == "primary",
                        "route_boundary": "v4_callback_in_hit_contribution_route_vs_materialized_hit_id_device_callback_reduce_fallback",
                        "parsed": parsed,
                    }
                    rows.append(row)
                    print(
                        f"goal4711 row done variant={variant} regime={regime} scale={scale} "
                        f"ratio={row['v3_baseline_over_v4_ratio']}",
                        file=sys.stderr,
                        flush=True,
                    )
                    if proc.returncode != 0:
                        payload["rows"] = rows
                        payload.update({"status": "blocked", "blocked_stage": f"row_{variant}_{regime}_{scale}"})
                        return payload

        payload["rows"] = rows
        payload["classification"] = classify_v4_goal4711_custom_scored_app_result(rows, denominator_discovery)
        payload["status"] = "goal4711_custom_scored_app_measured_not_release"
        return payload


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    classification = payload.get("classification") or {}
    lines = [
        "# V4 Goal4711 Custom Scored App Focused POD Result",
        "",
        f"- status: `{payload['status']}`",
        f"- classification: `{classification.get('classification')}`",
        f"- primary geomean V2 speedup: `{classification.get('primary_geomean_v2_speedup')}`",
        f"- primary geomean V3 speedup: `{classification.get('primary_geomean_v3_speedup')}`",
        f"- min primary V3 speedup: `{classification.get('min_primary_v3_speedup')}`",
        f"- denominator quality: `{classification.get('denominator_quality')}`",
        "",
        "## Rows",
        "",
        "| callback | role | regime | scale | correctness | V4 fused s | fallback s | V3 baseline/V4 |",
        "|---|---|---|---:|---|---:|---:|---:|",
    ]
    for row in payload.get("rows", []):
        ratio = row.get("v3_baseline_over_v4_ratio")
        lines.append(
            "| {callback} | {role} | {regime} | {scale} | {ok} | {v4:.9f} | {fallback:.9f} | {ratio} |".format(
                callback=row["protocol_callback"],
                role=row["callback_role"],
                regime=row["regime"],
                scale=row["scale"],
                ok=str(bool(row["v4_fused_correctness_passed"] and row["materialized_fallback_correctness_passed"])).lower(),
                v4=float(row["v4_fused_median_s"] or 0.0),
                fallback=float(row["materialized_fallback_median_s"] or 0.0),
                ratio=f"{float(ratio):.3f}x" if ratio is not None else "n/a",
            )
        )
    lines.extend(
        [
            "",
            "## Denominator Boundary",
            "",
            "V2.14 and V3.0.2 denominator discovery is recorded before V4 timing. If no exact custom-callback route is found, this run uses a strong materialized-device fallback: same OptiX hit discovery, device hit-id materialization, then a separate device callback/reduction kernel. It does not receive V4 callback-in-hit fusion, so the comparison targets the V4 increment while still requiring external denominator review before any public app-level claim.",
            "",
            "## Non-Authorization",
            "",
            "- V4 release is not authorized.",
            "- Formal high-performance V4 wording is not authorized.",
            "- Public Tier-3 support is not authorized.",
            "- Arbitrary callback or raw OptiX callback support is not authorized.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V4 Goal4711 custom-scored app focused POD benchmark.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--scales", default=",".join(str(item) for item in DEFAULT_SCALES))
    parser.add_argument("--regimes", default=",".join(DEFAULT_REGIMES))
    parser.add_argument("--warmups", type=int, default=DEFAULT_WARMUPS)
    parser.add_argument("--repeat", type=int, default=DEFAULT_REPEAT)
    parser.add_argument("--v2-root", type=Path, default=ROOT_V2_14)
    parser.add_argument("--v3-root", type=Path, default=ROOT_V3_0_2)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    scales = tuple(int(item) for item in str(args.scales).split(",") if item.strip())
    regimes = tuple(item.strip() for item in str(args.regimes).split(",") if item.strip())
    payload = _run_goal4711(
        dry_run=bool(args.dry_run),
        scales=scales,
        regimes=regimes,
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
    return 0 if payload["status"] in {"dry_run_contract_passed", "goal4711_custom_scored_app_measured_not_release"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

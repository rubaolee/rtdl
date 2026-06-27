from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Callable


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
from rtdsl.v4_goal4714_custom_predicate_early_exit_smoke_result import (
    classify_v4_goal4714_custom_predicate_early_exit_smoke,
    validate_v4_goal4714_custom_predicate_early_exit_smoke_result_contract,
)
from v4_goal4688_tier3_module_link_probe import _find_cuda_lib_dir
from v4_goal4688_tier3_module_link_probe import _find_cuda_root
from v4_goal4688_tier3_module_link_probe import _find_nvcc
from v4_goal4688_tier3_module_link_probe import _find_optix_include
from v4_goal4688_tier3_module_link_probe import _run
from v4_tier3_numba_ptx_probe import _configure_numba_legacy_nvvm_env
from v4_tier3_numba_ptx_probe import _maybe_reexec_with_nvvm_ld_path


KEY_VALUE_RE = re.compile(r"^([A-Za-z0-9_]+)=([^\n]+)$", re.MULTILINE)


def accept_layer_predicate(hit_distance, primitive_id, candidates_per_ray, accept_layer):
    if accept_layer < 0.0:
        return 0.0
    k = int(candidates_per_ray)
    layer = primitive_id % k
    return 1.0 if layer == int(accept_layer) else 0.0


VARIANT_FUNCTIONS: dict[str, Callable[..., float]] = {
    "accept_layer_predicate": accept_layer_predicate,
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
    unsigned int* accepted_flags;
    unsigned long long* anyhit_invocations;
    unsigned int ray_count;
    unsigned int candidates_per_ray;
    int accept_layer;
    unsigned int route_mode;
};

struct Float3 { float x; float y; float z; };
struct UInt3 { unsigned int x; unsigned int y; unsigned int z; };

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

int main(int argc, char** argv) {
    try {
        if (argc != 5) {
            std::cerr << "usage: v4_goal4714_smoke <ptx> <regime> <ray_count> <candidates_per_ray>\n";
            return 64;
        }
        std::string ptx = read_text(argv[1]);
        std::string regime = argv[2];
        unsigned int ray_count = static_cast<unsigned int>(std::stoul(argv[3]));
        unsigned int candidates_per_ray = static_cast<unsigned int>(std::stoul(argv[4]));
        int accept_layer = accept_layer_for(regime, candidates_per_ray);
        unsigned int active_rays = active_ray_count_for(regime, ray_count);
        unsigned int triangle_count = regime == "no_hit_empty" ? 1u : active_rays * candidates_per_ray;

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
        raygen_desc.raygen.entryFunctionName = "__raygen__rtdl_goal4714_predicate";
        OptixProgramGroupDesc miss_desc = {};
        miss_desc.kind = OPTIX_PROGRAM_GROUP_KIND_MISS;
        miss_desc.miss.module = module;
        miss_desc.miss.entryFunctionName = "__miss__rtdl_goal4714_predicate";
        OptixProgramGroupDesc hit_desc = {};
        hit_desc.kind = OPTIX_PROGRAM_GROUP_KIND_HITGROUP;
        hit_desc.hitgroup.moduleAH = module;
        hit_desc.hitgroup.entryFunctionNameAH = "__anyhit__rtdl_goal4714_predicate";
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
        unsigned long long* invocations_dev = nullptr;
        unsigned long long* accepted_count_dev = nullptr;
        Params* params_dev_raw = nullptr;
        check_runtime(cudaMalloc(reinterpret_cast<void**>(&flags_dev), sizeof(unsigned int) * ray_count), "alloc flags");
        check_runtime(cudaMalloc(reinterpret_cast<void**>(&invocations_dev), sizeof(unsigned long long)), "alloc invocations");
        check_runtime(cudaMalloc(reinterpret_cast<void**>(&accepted_count_dev), sizeof(unsigned long long)), "alloc accepted count");
        check_runtime(cudaMalloc(reinterpret_cast<void**>(&params_dev_raw), sizeof(Params)), "alloc params");
        Params params = {};
        params.handle = gas_handle;
        params.accepted_flags = flags_dev;
        params.anyhit_invocations = invocations_dev;
        params.ray_count = ray_count;
        params.candidates_per_ray = candidates_per_ray;
        params.accept_layer = accept_layer;
        params.route_mode = 1u;
        CUdeviceptr params_dev = reinterpret_cast<CUdeviceptr>(params_dev_raw);

        check_runtime(cudaMemset(flags_dev, 0, sizeof(unsigned int) * ray_count), "reset flags v4");
        check_runtime(cudaMemset(invocations_dev, 0, sizeof(unsigned long long)), "reset invocations v4");
        check_runtime(cudaMemcpy(params_dev_raw, &params, sizeof(Params), cudaMemcpyHostToDevice), "copy params v4");
        check_optix(optixLaunch(pipeline, 0, params_dev, sizeof(Params), &sbt, ray_count, 1, 1), "launch v4");
        check_runtime(cudaDeviceSynchronize(), "sync v4");
        check_runtime(cudaMemset(accepted_count_dev, 0, sizeof(unsigned long long)), "reset accepted reduce");
        unsigned int block = 256u;
        unsigned int grid = (ray_count + block - 1u) / block;
        if (grid > 4096u) grid = 4096u;
        reduce_flags_kernel<<<grid, block>>>(flags_dev, accepted_count_dev, ray_count);
        check_runtime(cudaGetLastError(), "reduce flags");
        check_runtime(cudaDeviceSynchronize(), "sync reduce");
        unsigned long long v4_invocations = 0ull;
        unsigned long long v4_accepted = 0ull;
        check_runtime(cudaMemcpy(&v4_invocations, invocations_dev, sizeof(unsigned long long), cudaMemcpyDeviceToHost), "copy invocations v4");
        check_runtime(cudaMemcpy(&v4_accepted, accepted_count_dev, sizeof(unsigned long long), cudaMemcpyDeviceToHost), "copy accepted v4");

        params.route_mode = 0u;
        check_runtime(cudaMemset(flags_dev, 0, sizeof(unsigned int) * ray_count), "reset flags fallback");
        check_runtime(cudaMemset(invocations_dev, 0, sizeof(unsigned long long)), "reset invocations fallback");
        check_runtime(cudaMemcpy(params_dev_raw, &params, sizeof(Params), cudaMemcpyHostToDevice), "copy params fallback");
        check_optix(optixLaunch(pipeline, 0, params_dev, sizeof(Params), &sbt, ray_count, 1, 1), "launch fallback");
        check_runtime(cudaDeviceSynchronize(), "sync fallback");
        unsigned long long fallback_invocations = 0ull;
        check_runtime(cudaMemcpy(&fallback_invocations, invocations_dev, sizeof(unsigned long long), cudaMemcpyDeviceToHost), "copy invocations fallback");

        unsigned long long expected_accepted = accept_layer >= 0 ? (unsigned long long)active_rays : 0ull;
        std::cout << "regime=" << regime << "\n";
        std::cout << "ray_count=" << ray_count << "\n";
        std::cout << "candidates_per_ray=" << candidates_per_ray << "\n";
        std::cout << "active_rays=" << active_rays << "\n";
        std::cout << "accept_layer=" << accept_layer << "\n";
        std::cout << "expected_accepted=" << expected_accepted << "\n";
        std::cout << "v4_accepted=" << v4_accepted << "\n";
        std::cout << "v4_anyhit_invocations=" << v4_invocations << "\n";
        std::cout << "fallback_all_hit_invocations=" << fallback_invocations << "\n";
        std::cout << "correctness_passed=" << (v4_accepted == expected_accepted ? 1 : 0) << "\n";
        std::cout << "early_termination_observed=" << (v4_invocations < fallback_invocations ? 1 : 0) << "\n";
        return v4_accepted == expected_accepted ? 0 : 6;
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

struct RtdlGoal4714Params {{
    OptixTraversableHandle handle;
    unsigned int* accepted_flags;
    unsigned long long* anyhit_invocations;
    unsigned int ray_count;
    unsigned int candidates_per_ray;
    int accept_layer;
    unsigned int route_mode;
}};

extern "C" {{
__constant__ RtdlGoal4714Params params;
}}

extern "C" __global__ void __raygen__rtdl_goal4714_predicate() {{
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

extern "C" __global__ void __miss__rtdl_goal4714_predicate() {{
}}

extern "C" __global__ void __anyhit__rtdl_goal4714_predicate() {{
    atomicAdd(params.anyhit_invocations, 1ull);
    const unsigned int primitive_id = optixGetPrimitiveIndex();
    if (params.route_mode == 0u) {{
        optixIgnoreIntersection();
        return;
    }}
    const double accept = {callback_symbol}(1.0, primitive_id, (double)params.candidates_per_ray, (double)params.accept_layer);
    if (accept >= 0.5) {{
        params.accepted_flags[optixGetLaunchIndex().x] = 1u;
        optixTerminateRay();
    }} else {{
        optixIgnoreIntersection();
    }}
}}
""".strip()


def _toolchain() -> dict[str, object]:
    cuda_root = _find_cuda_root()
    return {
        "optix_include": str(_find_optix_include()) if _find_optix_include() else None,
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


def _parse_stdout(stdout: str) -> dict[str, object]:
    values = {match.group(1): match.group(2).strip() for match in KEY_VALUE_RE.finditer(stdout)}
    parsed: dict[str, object] = {}
    for key in ("ray_count", "candidates_per_ray", "active_rays", "accept_layer", "expected_accepted", "v4_accepted", "v4_anyhit_invocations", "fallback_all_hit_invocations"):
        if key in values:
            parsed[key] = int(values[key])
    if "regime" in values:
        parsed["regime"] = values["regime"]
    for key in ("correctness_passed", "early_termination_observed"):
        if key in values:
            parsed[key] = values[key] == "1"
    return parsed


def _compile_loader(tmp_path: Path, env: dict[str, str], toolchain: dict[str, object]) -> tuple[Path | None, dict[str, object]]:
    source = tmp_path / "v4_goal4714_smoke.cu"
    binary = tmp_path / "v4_goal4714_smoke"
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


def _base_payload(dry_run: bool, ray_count: int) -> dict[str, object]:
    return {
        "schema": "rtdl.v4.goal4714_custom_predicate_early_exit_smoke.v1",
        "status": "dry_run" if dry_run else "unknown",
        "dry_run": dry_run,
        "ray_count": ray_count,
        "protocol_validation": validate_v4_goal4713_custom_predicate_early_exit_protocol(),
        "result_contract_validation": validate_v4_goal4714_custom_predicate_early_exit_smoke_result_contract(),
        "rows": [],
        "classification": None,
        "pod_timing_authorized": False,
        "release_authorized": False,
        "formal_high_performance_authorized": False,
        "app_level_speed_claim_authorized": False,
        "public_tier3_support_authorized": False,
        "arbitrary_callback_authorized": False,
        "raw_optix_callback_authorized": False,
    }


def _run_smoke(dry_run: bool, ray_count: int) -> dict[str, object]:
    payload = _base_payload(dry_run, ray_count)
    if dry_run:
        payload["status"] = (
            "dry_run_contract_passed"
            if payload["protocol_validation"]["status"] == "passed"
            and payload["result_contract_validation"]["status"] == "passed"
            else "dry_run_contract_failed"
        )
        return payload

    toolchain = _toolchain()
    payload["toolchain"] = toolchain
    if not all(toolchain.values()):
        payload.update({"status": "blocked", "blocked_stage": "toolchain_discovery"})
        return payload
    with tempfile.TemporaryDirectory(prefix="rtdl-v4-goal4714-smoke-") as tmp:
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
        wrapper_cu = tmp_path / "goal4714_wrapper.cu"
        wrapper_ptx = tmp_path / "goal4714_wrapper.ptx"
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
        payload["wrapper_compile"] = {"returncode": wrapper_compile.returncode, "stdout": wrapper_compile.stdout.strip()[:4000], "stderr": wrapper_compile.stderr.strip()[:4000]}
        if wrapper_compile.returncode != 0 or not wrapper_ptx.exists():
            payload.update({"status": "blocked", "blocked_stage": "wrapper_compile"})
            return payload
        combined_ptx = tmp_path / "goal4714_combined.ptx"
        combined_ptx.write_text(compose_goal4688_combined_ptx(callback_ptx, wrapper_ptx.read_text(encoding="utf-8")), encoding="utf-8")
        regimes = (
            ("dense_early_accept_k8", 8, "primary"),
            ("dense_early_accept_k32", 32, "primary"),
            ("dense_reject_all_k32", 32, "control"),
            ("no_hit_empty", 0, "control"),
        )
        rows = []
        for regime, candidates, role in regimes:
            print(f"goal4714 smoke start regime={regime} candidates={candidates}", file=sys.stderr, flush=True)
            proc = _run([str(binary), str(combined_ptx), regime, str(ray_count), str(candidates)], cwd=tmp_path, env=env)
            parsed = _parse_stdout(proc.stdout)
            row = {
                "regime": regime,
                "row_role": role,
                "returncode": proc.returncode,
                "stdout": proc.stdout.strip()[:8000],
                "stderr": proc.stderr.strip()[:4000],
                **parsed,
            }
            row["correctness_passed"] = proc.returncode == 0 and bool(parsed.get("correctness_passed"))
            rows.append(row)
            print(
                f"goal4714 smoke done regime={regime} correctness={row['correctness_passed']} "
                f"early={row.get('early_termination_observed')}",
                file=sys.stderr,
                flush=True,
            )
            if proc.returncode != 0:
                payload["rows"] = rows
                payload.update({"status": "blocked", "blocked_stage": f"row_{regime}"})
                return payload
        payload["rows"] = rows
        payload["classification"] = classify_v4_goal4714_custom_predicate_early_exit_smoke(rows)
        payload["status"] = "goal4714_custom_predicate_early_exit_smoke_measured_not_timing"
        return payload


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    classification = payload.get("classification") or {}
    lines = [
        "# V4 Goal4714 Custom Predicate Early-Exit Smoke",
        "",
        f"- status: `{payload['status']}`",
        f"- classification: `{classification.get('classification')}`",
        f"- correctness all passed: `{classification.get('correctness_all_passed')}`",
        f"- early termination primary passed: `{classification.get('early_termination_primary_passed')}`",
        "",
        "| regime | role | correctness | v4 invocations | fallback invocations | early termination |",
        "|---|---|---|---:|---:|---|",
    ]
    for row in payload.get("rows", []):
        lines.append(
            f"| `{row['regime']}` | `{row['row_role']}` | `{row.get('correctness_passed')}` | "
            f"{row.get('v4_anyhit_invocations')} | {row.get('fallback_all_hit_invocations')} | "
            f"`{row.get('early_termination_observed')}` |"
        )
    lines.extend(["", "This smoke does not authorize POD timing, release, public Tier-3 support, or performance claims."])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V4 Goal4714 custom predicate early-exit POD smoke.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--ray-count", type=int, default=4096)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()
    payload = _run_smoke(bool(args.dry_run), int(args.ray_count))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        _write_markdown(args.md_out, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] in {"dry_run_contract_passed", "goal4714_custom_predicate_early_exit_smoke_measured_not_timing"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

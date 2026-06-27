from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
for path in (SRC, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from rtdsl.v4_goal4687_tier3_wrapper_compile_probe import extract_numba_callback_symbol_from_ptx
from rtdsl.v4_goal4688_tier3_module_link_probe import compose_goal4688_combined_ptx
from rtdsl.v4_goal4698_specialized_tier3_compile_cache import classify_v4_goal4698_compile_failure
from rtdsl.v4_goal4698_specialized_tier3_compile_cache import plan_v4_goal4698_specialized_tier3_compile
from rtdsl.v4_goal4702_specialized_tier3_reliability_protocol import (
    validate_v4_goal4702_specialized_tier3_reliability_protocol,
)
from rtdsl.v4_goal4703_specialized_tier3_reliability_result import (
    classify_v4_goal4703_specialized_tier3_reliability_result,
    validate_v4_goal4703_specialized_tier3_reliability_result_contract,
)
from v4_goal4688_tier3_module_link_probe import _compiler
from v4_goal4688_tier3_module_link_probe import _find_cuda_lib_dir
from v4_goal4688_tier3_module_link_probe import _find_cuda_root
from v4_goal4688_tier3_module_link_probe import _find_nvcc
from v4_goal4688_tier3_module_link_probe import _find_optix_include
from v4_goal4688_tier3_module_link_probe import _run
from v4_tier3_numba_ptx_probe import _configure_numba_legacy_nvvm_env
from v4_tier3_numba_ptx_probe import _maybe_reexec_with_nvvm_ld_path


DEFAULT_RAY_COUNT = 32768
DEFAULT_WARMUPS = 1
VARIANT_TO_CONTRACT_SHAPE = {
    "custom_scalar_reduce_weighted_sum": "custom_scalar_reduce",
    "custom_score_affine": "custom_score",
    "custom_threshold_flag": "custom_threshold",
    "custom_minmax_score": "custom_minmax",
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
#include <optix.h>
#include <optix_function_table_definition.h>
#include <optix_stack_size.h>
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
    unsigned int ray_count;
};

struct Float3 { float x; float y; float z; };
struct UInt3 { unsigned int x; unsigned int y; unsigned int z; };

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
    unsigned long long total = 0;
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

int main(int argc, char** argv) {
    try {
        if (argc != 6) {
            std::cerr << "usage: v4_goal4703_reliability <ptx> <variant> <dataset> <ray_count> <warmups>\n";
            return 64;
        }
        std::string ptx = read_text(argv[1]);
        std::string variant = argv[2];
        std::string dataset = argv[3];
        unsigned int ray_count = static_cast<unsigned int>(std::stoul(argv[4]));
        unsigned int warmups = static_cast<unsigned int>(std::stoul(argv[5]));
        unsigned int hit_count = hit_count_for(dataset, ray_count);
        unsigned int triangle_count = dataset == "no_hit_empty_reduction" ? 1u : hit_count;

        check_cuda(cuInit(0), "cuInit");
        CUdevice dev = 0;
        check_cuda(cuDeviceGet(&dev, 0), "cuDeviceGet");
        CUcontext cu_ctx = nullptr;
        check_cuda(cuDevicePrimaryCtxRetain(&cu_ctx, dev), "cuDevicePrimaryCtxRetain");
        check_cuda(cuCtxSetCurrent(cu_ctx), "cuCtxSetCurrent");
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

        CUdeviceptr vertices_dev = 0, indices_dev = 0;
        check_cuda(cuMemAlloc(&vertices_dev, vertices.size() * sizeof(Float3)), "alloc vertices");
        check_cuda(cuMemAlloc(&indices_dev, indices.size() * sizeof(UInt3)), "alloc indices");
        check_cuda(cuMemcpyHtoD(vertices_dev, vertices.data(), vertices.size() * sizeof(Float3)), "copy vertices");
        check_cuda(cuMemcpyHtoD(indices_dev, indices.data(), indices.size() * sizeof(UInt3)), "copy indices");

        OptixBuildInput build_input = {};
        build_input.type = OPTIX_BUILD_INPUT_TYPE_TRIANGLES;
        build_input.triangleArray.vertexBuffers = &vertices_dev;
        build_input.triangleArray.numVertices = static_cast<unsigned int>(vertices.size());
        build_input.triangleArray.vertexFormat = OPTIX_VERTEX_FORMAT_FLOAT3;
        build_input.triangleArray.vertexStrideInBytes = sizeof(Float3);
        build_input.triangleArray.indexBuffer = indices_dev;
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
        CUdeviceptr temp_dev = 0, gas_dev = 0;
        check_cuda(cuMemAlloc(&temp_dev, accel_sizes.tempSizeInBytes), "alloc temp");
        check_cuda(cuMemAlloc(&gas_dev, accel_sizes.outputSizeInBytes), "alloc gas");
        OptixTraversableHandle gas_handle = 0;
        check_optix(optixAccelBuild(optix_ctx, 0, &accel_options, &build_input, 1,
                                    temp_dev, accel_sizes.tempSizeInBytes,
                                    gas_dev, accel_sizes.outputSizeInBytes,
                                    &gas_handle, nullptr, 0),
                    "optixAccelBuild");
        check_cuda(cuStreamSynchronize(0), "gas sync");

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
        raygen_desc.raygen.entryFunctionName = "__raygen__rtdl_tier3_reliability";
        OptixProgramGroupDesc miss_desc = {};
        miss_desc.kind = OPTIX_PROGRAM_GROUP_KIND_MISS;
        miss_desc.miss.module = module;
        miss_desc.miss.entryFunctionName = "__miss__rtdl_tier3_reliability";
        OptixProgramGroupDesc hit_desc = {};
        hit_desc.kind = OPTIX_PROGRAM_GROUP_KIND_HITGROUP;
        hit_desc.hitgroup.moduleAH = module;
        hit_desc.hitgroup.entryFunctionNameAH = "__anyhit__rtdl_tier3_reliability";
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

        OptixStackSizes stack_sizes = {};
#if defined(OPTIX_VERSION) && OPTIX_VERSION < 70700
        check_optix(optixUtilAccumulateStackSizes(raygen_pg, &stack_sizes), "stack raygen");
        check_optix(optixUtilAccumulateStackSizes(miss_pg, &stack_sizes), "stack miss");
        check_optix(optixUtilAccumulateStackSizes(hit_pg, &stack_sizes), "stack hit");
#else
        check_optix(optixUtilAccumulateStackSizes(raygen_pg, &stack_sizes, pipeline), "stack raygen");
        check_optix(optixUtilAccumulateStackSizes(miss_pg, &stack_sizes, pipeline), "stack miss");
        check_optix(optixUtilAccumulateStackSizes(hit_pg, &stack_sizes, pipeline), "stack hit");
#endif
        uint32_t dc_from_traversal = 0, dc_from_state = 0, continuation = 0;
        check_optix(optixUtilComputeStackSizes(&stack_sizes, 1, 0, 0, &dc_from_traversal, &dc_from_state, &continuation),
                    "optixUtilComputeStackSizes");
        check_optix(optixPipelineSetStackSize(pipeline, dc_from_traversal, dc_from_state, continuation, 1),
                    "optixPipelineSetStackSize");

        RaygenRecord raygen_rec = {};
        MissRecord miss_rec = {};
        HitRecord hit_rec = {};
        check_optix(optixSbtRecordPackHeader(raygen_pg, &raygen_rec), "pack raygen");
        check_optix(optixSbtRecordPackHeader(miss_pg, &miss_rec), "pack miss");
        check_optix(optixSbtRecordPackHeader(hit_pg, &hit_rec), "pack hit");
        CUdeviceptr raygen_dev = 0, miss_dev = 0, hit_dev = 0;
        check_cuda(cuMemAlloc(&raygen_dev, sizeof(RaygenRecord)), "alloc raygen");
        check_cuda(cuMemAlloc(&miss_dev, sizeof(MissRecord)), "alloc miss");
        check_cuda(cuMemAlloc(&hit_dev, sizeof(HitRecord)), "alloc hit");
        check_cuda(cuMemcpyHtoD(raygen_dev, &raygen_rec, sizeof(RaygenRecord)), "copy raygen");
        check_cuda(cuMemcpyHtoD(miss_dev, &miss_rec, sizeof(MissRecord)), "copy miss");
        check_cuda(cuMemcpyHtoD(hit_dev, &hit_rec, sizeof(HitRecord)), "copy hit");
        OptixShaderBindingTable sbt = {};
        sbt.raygenRecord = raygen_dev;
        sbt.missRecordBase = miss_dev;
        sbt.missRecordStrideInBytes = sizeof(MissRecord);
        sbt.missRecordCount = 1;
        sbt.hitgroupRecordBase = hit_dev;
        sbt.hitgroupRecordStrideInBytes = sizeof(HitRecord);
        sbt.hitgroupRecordCount = 1;

        CUdeviceptr output_dev = 0, params_dev = 0;
        check_cuda(cuMemAlloc(&output_dev, sizeof(unsigned long long)), "alloc output");
        Params params = {};
        params.handle = gas_handle;
        params.output_sum = reinterpret_cast<unsigned long long*>(output_dev);
        params.ray_count = ray_count;
        check_cuda(cuMemAlloc(&params_dev, sizeof(Params)), "alloc params");
        check_cuda(cuMemcpyHtoD(params_dev, &params, sizeof(Params)), "copy params");

        unsigned long long zero = 0;
        for (unsigned int i = 0; i < warmups + 1u; ++i) {
            check_cuda(cuMemcpyHtoD(output_dev, &zero, sizeof(unsigned long long)), "reset output");
            check_optix(optixLaunch(pipeline, 0, params_dev, sizeof(Params), &sbt, ray_count, 1, 1), "optixLaunch");
            check_cuda(cuStreamSynchronize(0), "launch sync");
        }
        unsigned long long output_value = 0;
        check_cuda(cuMemcpyDtoH(&output_value, output_dev, sizeof(unsigned long long)), "copy output");
        unsigned long long expected = expected_for(variant, hit_count);
        std::cout << "variant=" << variant << "\n";
        std::cout << "dataset=" << dataset << "\n";
        std::cout << "ray_count=" << ray_count << "\n";
        std::cout << "hit_count=" << hit_count << "\n";
        std::cout << "output_sum=" << output_value << "\n";
        std::cout << "expected_sum=" << expected << "\n";
        std::cout << "output_matches_expected=" << (output_value == expected ? 1 : 0) << "\n";
        return output_value == expected ? 0 : 6;
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

struct RtdlTier3ReliabilityParams {{
    OptixTraversableHandle handle;
    unsigned long long* output_sum;
    unsigned int ray_count;
}};

extern "C" {{
__constant__ RtdlTier3ReliabilityParams params;
}}

extern "C" __global__ void __raygen__rtdl_tier3_reliability() {{
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

extern "C" __global__ void __miss__rtdl_tier3_reliability() {{
}}

extern "C" __global__ void __anyhit__rtdl_tier3_reliability() {{
    const unsigned int primitive_id = optixGetPrimitiveIndex();
    const double weight = (double)(primitive_id + 1u);
    const double value = {callback_symbol}(1.0, primitive_id, weight, 0.0);
    const unsigned long long contribution = value < 0.0 ? 0ull : (unsigned long long)(value + 0.5);
    atomicAdd(params.output_sum, contribution);
    optixTerminateRay();
}}
""".strip()


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


def _parse_stdout(stdout: str) -> dict[str, object]:
    values: dict[str, object] = {}
    for line in stdout.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    for key in ("ray_count", "hit_count", "output_sum", "expected_sum"):
        if key in values:
            values[key] = int(str(values[key]))
    if "output_matches_expected" in values:
        values["output_matches_expected"] = str(values["output_matches_expected"]) == "1"
    return values


def _failure(stage: str, message: str) -> dict[str, object]:
    return classify_v4_goal4698_compile_failure(stage, message)


def _base_payload(dry_run: bool, ray_count: int, warmups: int) -> dict[str, object]:
    protocol_validation = validate_v4_goal4702_specialized_tier3_reliability_protocol()
    result_contract = validate_v4_goal4703_specialized_tier3_reliability_result_contract()
    return {
        "schema": "rtdl.v4.goal4703_specialized_tier3_reliability_matrix_pod.v1",
        "status": "dry_run" if dry_run else "unknown",
        "dry_run": dry_run,
        "protocol_validation": protocol_validation,
        "result_contract_validation": result_contract,
        "protocol": protocol_validation["protocol"],
        "ray_count": ray_count,
        "warmups": warmups,
        "attempts": [],
        "cache_checks": {},
        "summary": None,
        "tier3_public_support_authorized": False,
        "release_authorized": False,
        "performance_claim_authorized": False,
        "arbitrary_callback_authorized": False,
        "raw_optix_callback_authorized": False,
    }


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
    cpp_path = tmp_path / "v4_goal4703_reliability.cpp"
    binary_path = tmp_path / "v4_goal4703_reliability"
    cpp_path.write_text(CPP_SOURCE, encoding="utf-8")
    proc = _run(
        [
            str(toolchain["compiler"]),
            "-std=c++17",
            "-O2",
            "-I",
            str(toolchain["optix_include"]),
            "-I",
            str(Path(str(toolchain["cuda_root"])) / "include"),
            str(cpp_path),
            "-L",
            str(toolchain["cuda_lib_dir"]),
            "-lcuda",
            "-ldl",
            "-o",
            str(binary_path),
        ],
        cwd=tmp_path,
        env=env,
    )
    record = {"returncode": proc.returncode, "stdout": proc.stdout.strip()[:4000], "stderr": proc.stderr.strip()[:4000]}
    return (binary_path if proc.returncode == 0 else None), record


def _run_matrix(dry_run: bool, ray_count: int, warmups: int) -> dict[str, object]:
    payload = _base_payload(dry_run, ray_count, warmups)
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
        failure = _failure("numba_ptx_generation", "toolchain discovery failed: " + json.dumps(toolchain, sort_keys=True))
        payload.update({"status": "blocked", "blocked_stage": "toolchain_discovery", "failure_classification": failure})
        return payload

    with tempfile.TemporaryDirectory(prefix="rtdl-v4-goal4703-reliability-") as tmp:
        tmp_path = Path(tmp)
        env = dict(os.environ)
        env["LD_LIBRARY_PATH"] = os.pathsep.join(
            [str(toolchain["cuda_lib_dir"]), "/usr/lib/x86_64-linux-gnu", env.get("LD_LIBRARY_PATH", "")]
        )
        binary, loader_compile = _compile_loader(tmp_path, env, toolchain)
        payload["loader_compile"] = loader_compile
        if binary is None:
            failure = _failure("wrapper_specialization", loader_compile["stderr"] or loader_compile["stdout"])
            payload.update({"status": "blocked", "blocked_stage": "loader_compile", "failure_classification": failure})
            return payload

        protocol = payload["protocol"]
        datasets = list(protocol["datasets"])
        attempts: list[dict[str, object]] = []
        cache_checks_by_variant: dict[str, list[dict[str, object]]] = {}
        for variant in protocol["callback_variants"]:
            variant = str(variant)
            for attempt_index in range(int(protocol["attempts_per_variant"])):
                print(f"goal4703 progress start variant={variant} attempt={attempt_index}", file=sys.stderr, flush=True)
                attempt: dict[str, object] = {
                    "variant": variant,
                    "attempt_index": attempt_index,
                    "compile_link_launch_success": False,
                    "correctness_passed": False,
                    "dataset_results": [],
                    "failure_classification": None,
                }
                callback_ptx, ptx_payload = _compile_variant_ptx(variant)
                attempt["ptx_generation"] = ptx_payload
                if callback_ptx is None:
                    attempt["failure_classification"] = _failure("numba_ptx_generation", str(ptx_payload.get("error")))
                    attempts.append(attempt)
                    continue
                symbol_probe = extract_numba_callback_symbol_from_ptx(callback_ptx, callback_name_hint=variant)
                attempt["symbol_probe"] = symbol_probe.as_dict()
                if symbol_probe.status != "symbol_extracted" or not symbol_probe.symbol:
                    attempt["failure_classification"] = _failure("callback_symbol_extraction", symbol_probe.reason)
                    attempts.append(attempt)
                    continue

                compile_plan = plan_v4_goal4698_specialized_tier3_compile(
                    callback_shape=VARIANT_TO_CONTRACT_SHAPE[variant],
                    callback_language="numba",
                    numba_cabi_device_function=True,
                    callback_symbol=symbol_probe.symbol,
                    callback_ptx=callback_ptx,
                    toolchain_fingerprint=json.dumps(toolchain, sort_keys=True),
                    optix_abi="8.0",
                    compute_target="sm_86",
                ).as_dict()
                attempt["compile_plan"] = compile_plan
                if compile_plan.get("cache_key"):
                    repeated_plan = plan_v4_goal4698_specialized_tier3_compile(
                        callback_shape=VARIANT_TO_CONTRACT_SHAPE[variant],
                        callback_language="numba",
                        numba_cabi_device_function=True,
                        callback_symbol=symbol_probe.symbol,
                        callback_ptx=callback_ptx,
                        toolchain_fingerprint=json.dumps(toolchain, sort_keys=True),
                        optix_abi="8.0",
                        compute_target="sm_86",
                    ).as_dict()
                    changed_toolchain_plan = plan_v4_goal4698_specialized_tier3_compile(
                        callback_shape=VARIANT_TO_CONTRACT_SHAPE[variant],
                        callback_language="numba",
                        numba_cabi_device_function=True,
                        callback_symbol=symbol_probe.symbol,
                        callback_ptx=callback_ptx,
                        toolchain_fingerprint=json.dumps({**toolchain, "changed": True}, sort_keys=True),
                        optix_abi="8.0",
                        compute_target="sm_86",
                    ).as_dict()
                    changed_ptx_plan = plan_v4_goal4698_specialized_tier3_compile(
                        callback_shape=VARIANT_TO_CONTRACT_SHAPE[variant],
                        callback_language="numba",
                        numba_cabi_device_function=True,
                        callback_symbol=symbol_probe.symbol,
                        callback_ptx=callback_ptx + "\n// rtdl-goal4703-cache-sensitivity\n",
                        toolchain_fingerprint=json.dumps(toolchain, sort_keys=True),
                        optix_abi="8.0",
                        compute_target="sm_86",
                    ).as_dict()
                    cache_check = {
                        "attempt_index": attempt_index,
                        "cache_key": compile_plan["cache_key"],
                        "callback_ptx_sha256": compile_plan["cache_components"]["callback_ptx_sha256"],
                        "same_ptx_repeat_key": repeated_plan.get("cache_key"),
                        "same_ptx_repeat_key_match": repeated_plan.get("cache_key") == compile_plan["cache_key"],
                        "changed_toolchain_key": changed_toolchain_plan.get("cache_key"),
                        "changed_toolchain_changes_key": changed_toolchain_plan.get("cache_key") != compile_plan["cache_key"],
                        "changed_ptx_key": changed_ptx_plan.get("cache_key"),
                        "changed_ptx_changes_key": changed_ptx_plan.get("cache_key") != compile_plan["cache_key"],
                    }
                    attempt["cache_check"] = cache_check
                    cache_checks_by_variant.setdefault(variant, []).append(cache_check)
                if not compile_plan["internal_compile_allowed"]:
                    attempt["failure_classification"] = _failure("contract_validation", str(compile_plan.get("error_message")))
                    attempts.append(attempt)
                    continue

                wrapper_cu = tmp_path / f"{variant}_{attempt_index}_wrapper.cu"
                wrapper_ptx = tmp_path / f"{variant}_{attempt_index}_wrapper.ptx"
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
                attempt["wrapper_compile"] = {
                    "returncode": wrapper_compile.returncode,
                    "stdout": wrapper_compile.stdout.strip()[:4000],
                    "stderr": wrapper_compile.stderr.strip()[:4000],
                }
                if wrapper_compile.returncode != 0 or not wrapper_ptx.exists():
                    attempt["failure_classification"] = _failure("nvcc_wrapper_compile", wrapper_compile.stderr or wrapper_compile.stdout)
                    attempts.append(attempt)
                    continue

                combined_ptx = tmp_path / f"{variant}_{attempt_index}_combined.ptx"
                combined_ptx.write_text(
                    compose_goal4688_combined_ptx(callback_ptx, wrapper_ptx.read_text(encoding="utf-8")),
                    encoding="utf-8",
                )
                dataset_rows = []
                for dataset in datasets:
                    proc = _run(
                        [str(binary), str(combined_ptx), variant, str(dataset), str(ray_count), str(warmups)],
                        cwd=tmp_path,
                        env=env,
                    )
                    parsed = _parse_stdout(proc.stdout)
                    row = {
                        "dataset": dataset,
                        "returncode": proc.returncode,
                        "stdout": proc.stdout.strip()[:8000],
                        "stderr": proc.stderr.strip()[:4000],
                        "parsed": parsed,
                        "correctness_passed": proc.returncode == 0 and bool(parsed.get("output_matches_expected")),
                    }
                    dataset_rows.append(row)
                    if proc.returncode != 0:
                        attempt["failure_classification"] = _failure("launch_validation", proc.stderr or proc.stdout)
                        break
                attempt["dataset_results"] = dataset_rows
                attempt["correctness_passed"] = bool(dataset_rows) and all(bool(row["correctness_passed"]) for row in dataset_rows)
                attempt["compile_link_launch_success"] = bool(attempt["correctness_passed"])
                attempts.append(attempt)
                print(
                    f"goal4703 progress done variant={variant} attempt={attempt_index} "
                    f"success={attempt['compile_link_launch_success']}",
                    file=sys.stderr,
                    flush=True,
                )

        payload["attempts"] = attempts
        cache_checks: dict[str, object] = {}
        for variant in protocol["callback_variants"]:
            checks = cache_checks_by_variant.get(str(variant), [])
            hashes = [str(row["callback_ptx_sha256"]) for row in checks if row.get("callback_ptx_sha256")]
            cache_checks[str(variant)] = {
                "attempt_cache_checks": checks,
                "same_ptx_repeat_key_match": bool(checks) and all(bool(row["same_ptx_repeat_key_match"]) for row in checks),
                "changed_toolchain_changes_key": bool(checks) and all(bool(row["changed_toolchain_changes_key"]) for row in checks),
                "changed_ptx_changes_key": bool(checks) and all(bool(row["changed_ptx_changes_key"]) for row in checks),
                "compiled_ptx_hashes_unique_count": len(set(hashes)),
                "compiled_ptx_hash_stable_across_recompile": bool(hashes) and len(set(hashes)) == 1,
            }
        payload["cache_checks"] = cache_checks
        cache_checks_passed = bool(cache_checks) and all(
            bool(row["same_ptx_repeat_key_match"])
            and bool(row["changed_toolchain_changes_key"])
            and bool(row["changed_ptx_changes_key"])
            for row in cache_checks.values()
        )
        payload["summary"] = classify_v4_goal4703_specialized_tier3_reliability_result(
            attempts,
            success_floor=float(protocol["compile_link_launch_success_floor"]),
            cache_checks_passed=cache_checks_passed,
        )
        payload["status"] = "specialized_tier3_reliability_matrix_measured_not_public_support"
        return payload


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    summary = payload.get("summary") or {}
    lines = [
        "# V4 Goal4703 Specialized Tier-3 Reliability Matrix POD Result",
        "",
        f"- status: `{payload['status']}`",
        f"- classification: `{summary.get('classification')}`",
        f"- attempts: `{summary.get('successful_attempts')}/{summary.get('total_attempts')}`",
        f"- success rate: `{summary.get('success_rate')}`",
        f"- correctness passed: `{summary.get('correctness_passed')}`",
        f"- cache checks passed: `{summary.get('cache_checks_passed')}`",
        "",
        "## Reliability Matrix",
        "",
        "| variant | attempt | success | correctness |",
        "|---|---:|---|---|",
    ]
    for attempt in payload.get("attempts", []):
        lines.append(
            f"| `{attempt['variant']}` | {attempt['attempt_index']} | "
            f"`{attempt['compile_link_launch_success']}` | `{attempt['correctness_passed']}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This result does not authorize public Tier-3 support, arbitrary callback support, raw OptiX callbacks, release wording, or performance claims.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V4 Goal4703 specialized Tier-3 reliability matrix on POD.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--ray-count", type=int, default=DEFAULT_RAY_COUNT)
    parser.add_argument("--warmups", type=int, default=DEFAULT_WARMUPS)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    payload = _run_matrix(bool(args.dry_run), int(args.ray_count), int(args.warmups))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        _write_markdown(args.md_out, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] in {"dry_run_contract_passed", "specialized_tier3_reliability_matrix_measured_not_public_support"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

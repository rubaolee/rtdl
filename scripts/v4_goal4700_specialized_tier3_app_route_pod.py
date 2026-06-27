from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import statistics
import subprocess
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
for path in (SRC, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from rtdsl.v4_goal4687_tier3_wrapper_compile_probe import extract_numba_callback_symbol_from_ptx
from rtdsl.v4_goal4688_tier3_module_link_probe import compose_goal4688_combined_ptx
from rtdsl.v4_goal4698_specialized_tier3_compile_cache import plan_v4_goal4698_specialized_tier3_compile
from rtdsl.v4_goal4699_specialized_tier3_app_route_protocol import v4_goal4699_specialized_tier3_app_route_protocol
from rtdsl.v4_goal4700_specialized_tier3_app_route_result import (
    classify_v4_goal4700_specialized_tier3_app_route_result,
    validate_v4_goal4700_specialized_tier3_app_route_result_contract,
)
from v4_goal4688_tier3_module_link_probe import PTX_PROBE
from v4_goal4688_tier3_module_link_probe import _compiler
from v4_goal4688_tier3_module_link_probe import _find_cuda_lib_dir
from v4_goal4688_tier3_module_link_probe import _find_cuda_root
from v4_goal4688_tier3_module_link_probe import _find_nvcc
from v4_goal4688_tier3_module_link_probe import _find_optix_include
from v4_goal4688_tier3_module_link_probe import _run


SAMPLE_RE = re.compile(r"sample_ms=([0-9.eE+-]+)")
KEY_VALUE_RE = re.compile(r"^([A-Za-z0-9_]+)=([^\n]+)$", re.MULTILINE)
BUILTIN_SCRIPT = SCRIPTS / "v4_ray_triangle_weighted_sum_device_output_validation.py"


CPP_SOURCE = r"""
#include <cuda.h>
#include <optix.h>
#include <optix_function_table_definition.h>
#include <optix_stack_size.h>
#include <optix_stubs.h>

#include <cmath>
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

struct Float3 {
    float x;
    float y;
    float z;
};

struct UInt3 {
    unsigned int x;
    unsigned int y;
    unsigned int z;
};

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

int main(int argc, char** argv) {
    try {
        if (argc != 5) {
            std::cerr << "usage: v4_goal4700_specialized_tier3_app_route_pod <ptx> <ray_count> <warmups> <measured>\n";
            return 64;
        }
        std::string ptx = read_text(argv[1]);
        unsigned int ray_count = static_cast<unsigned int>(std::stoul(argv[2]));
        unsigned int warmups = static_cast<unsigned int>(std::stoul(argv[3]));
        unsigned int measured = static_cast<unsigned int>(std::stoul(argv[4]));

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
        vertices.reserve(static_cast<size_t>(ray_count) * 3u);
        indices.reserve(ray_count);
        for (unsigned int i = 0; i < ray_count; ++i) {
            float x = static_cast<float>((i % 256u) * 2u);
            float y = static_cast<float>((i / 256u) * 2u);
            float h = 0.40f;
            unsigned int base = i * 3u;
            vertices.push_back(Float3{x - h, y - h, 1.0f});
            vertices.push_back(Float3{x + h, y - h, 1.0f});
            vertices.push_back(Float3{x, y + h, 1.0f});
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
        build_input.triangleArray.numIndexTriplets = ray_count;
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
        raygen_desc.raygen.entryFunctionName = "__raygen__rtdl_tier3_weighted_sum";
        OptixProgramGroupDesc miss_desc = {};
        miss_desc.kind = OPTIX_PROGRAM_GROUP_KIND_MISS;
        miss_desc.miss.module = module;
        miss_desc.miss.entryFunctionName = "__miss__rtdl_tier3_weighted_sum";
        OptixProgramGroupDesc hit_desc = {};
        hit_desc.kind = OPTIX_PROGRAM_GROUP_KIND_HITGROUP;
        hit_desc.hitgroup.moduleAH = module;
        hit_desc.hitgroup.entryFunctionNameAH = "__anyhit__rtdl_tier3_weighted_sum";
        OptixProgramGroup raygen_pg = create_program_group(optix_ctx, raygen_desc, "raygen_program_group");
        OptixProgramGroup miss_pg = create_program_group(optix_ctx, miss_desc, "miss_program_group");
        OptixProgramGroup hit_pg = create_program_group(optix_ctx, hit_desc, "hit_program_group");
        std::vector<OptixProgramGroup> groups = {raygen_pg, miss_pg, hit_pg};
        OptixPipelineLinkOptions link_options = {};
        link_options.maxTraceDepth = 1;
        OptixPipeline pipeline = nullptr;
        char pipeline_log[16384] = {};
        size_t pipeline_log_size = sizeof(pipeline_log);
        OptixResult pipeline_result = optixPipelineCreate(optix_ctx, &pipeline_options, &link_options,
                                                          groups.data(), static_cast<unsigned int>(groups.size()),
                                                          pipeline_log, &pipeline_log_size, &pipeline);
        std::cout << "pipeline_create_result=" << static_cast<int>(pipeline_result) << "\n";
        check_optix(pipeline_result, "optixPipelineCreate");
        if (pipeline_log_size > 1 && pipeline_log[0] != '\0') {
            std::cout << "pipeline_log_begin\n" << pipeline_log << "\npipeline_log_end\n";
        }

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
        for (unsigned int i = 0; i < warmups; ++i) {
            check_cuda(cuMemcpyHtoD(output_dev, &zero, sizeof(unsigned long long)), "reset warmup output");
            check_optix(optixLaunch(pipeline, 0, params_dev, sizeof(Params), &sbt, ray_count, 1, 1), "warmup launch");
        }
        check_cuda(cuStreamSynchronize(0), "warmup sync");

        CUevent start = nullptr, stop = nullptr;
        check_cuda(cuEventCreate(&start, CU_EVENT_DEFAULT), "event start create");
        check_cuda(cuEventCreate(&stop, CU_EVENT_DEFAULT), "event stop create");
        for (unsigned int i = 0; i < measured; ++i) {
            check_cuda(cuEventRecord(start, 0), "event record start");
            check_cuda(cuMemcpyHtoD(output_dev, &zero, sizeof(unsigned long long)), "reset measured output");
            check_optix(optixLaunch(pipeline, 0, params_dev, sizeof(Params), &sbt, ray_count, 1, 1), "measured launch");
            check_cuda(cuEventRecord(stop, 0), "event record stop");
            check_cuda(cuEventSynchronize(stop), "event sync");
            float ms = 0.0f;
            check_cuda(cuEventElapsedTime(&ms, start, stop), "event elapsed");
            std::cout << "sample_ms=" << ms << "\n";
        }
        check_cuda(cuStreamSynchronize(0), "measured sync");
        unsigned long long output_value = 0;
        check_cuda(cuMemcpyDtoH(&output_value, output_dev, sizeof(unsigned long long)), "copy output");
        unsigned long long expected = (static_cast<unsigned long long>(ray_count) * (static_cast<unsigned long long>(ray_count) + 1ull)) / 2ull;
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

struct RtdlTier3WeightedSumParams {{
    OptixTraversableHandle handle;
    unsigned long long* output_sum;
    unsigned int ray_count;
}};

extern "C" {{
__constant__ RtdlTier3WeightedSumParams params;
}}

extern "C" __global__ void __raygen__rtdl_tier3_weighted_sum() {{
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

extern "C" __global__ void __miss__rtdl_tier3_weighted_sum() {{
}}

extern "C" __global__ void __anyhit__rtdl_tier3_weighted_sum() {{
    const unsigned int primitive_id = optixGetPrimitiveIndex();
    const double weight = (double)(primitive_id + 1u);
    const double value = {callback_symbol}(1.0, primitive_id, weight, 0.0);
    const unsigned long long contribution = (unsigned long long)(value + 0.5);
    atomicAdd(params.output_sum, contribution);
    optixTerminateRay();
}}
""".strip()


def _summarize_callback_stdout(stdout: str, stderr: str, returncode: int) -> dict[str, Any]:
    samples = [float(match.group(1)) for match in SAMPLE_RE.finditer(stdout)]
    pairs = {match.group(1): match.group(2).strip() for match in KEY_VALUE_RE.finditer(stdout)}
    return {
        "returncode": returncode,
        "stdout": stdout.strip()[:12000],
        "stderr": stderr.strip()[:4000],
        "sample_count": len(samples),
        "samples_ms": samples,
        "median_ms": statistics.median(samples) if samples else None,
        "median_s": (statistics.median(samples) / 1000.0) if samples else None,
        "min_ms": min(samples) if samples else None,
        "max_ms": max(samples) if samples else None,
        "output_sum": int(pairs["output_sum"]) if "output_sum" in pairs else None,
        "expected_sum": int(pairs["expected_sum"]) if "expected_sum" in pairs else None,
        "output_matches_expected": pairs.get("output_matches_expected") == "1",
    }


def _base_payload(dry_run: bool) -> dict[str, Any]:
    protocol = v4_goal4699_specialized_tier3_app_route_protocol().as_dict()
    return {
        "schema": "rtdl.v4.goal4700_specialized_tier3_app_route_pod.v1",
        "status": "dry_run" if dry_run else "unknown",
        "dry_run": dry_run,
        "protocol": protocol,
        "contract_validation": validate_v4_goal4700_specialized_tier3_app_route_result_contract(),
        "rows": [],
        "classification": None,
        "release_authorized": False,
        "tier3_public_support_authorized": False,
        "app_level_speed_claim_authorized": False,
        "performance_claim_authorized": False,
    }


def _run_builtin_denominators(protocol: dict[str, Any], tmp_path: Path, env: dict[str, str]) -> dict[str, Any]:
    counts = ",".join(str(item) for item in protocol["ray_counts"])
    json_out = tmp_path / "builtin_weighted_sum.json"
    proc = _run(
        [
            sys.executable,
            str(BUILTIN_SCRIPT),
            "--ray-counts",
            counts,
            "--repeat",
            str(protocol["repeat"]),
            "--warmup",
            str(protocol["warmup"]),
            "--json-out",
            str(json_out),
        ],
        cwd=ROOT,
        env=env,
    )
    payload = json.loads(json_out.read_text(encoding="utf-8")) if json_out.exists() else None
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip()[:12000],
        "stderr": proc.stderr.strip()[:4000],
        "payload": payload,
    }


def _run_probe(dry_run: bool) -> dict[str, Any]:
    payload = _base_payload(dry_run)
    if dry_run:
        payload["status"] = "dry_run_contract_passed" if payload["contract_validation"]["status"] == "passed" else "dry_run_contract_failed"
        return payload

    optix_include = _find_optix_include()
    cuda_root = _find_cuda_root()
    cuda_lib_dir = _find_cuda_lib_dir(cuda_root)
    nvcc = _find_nvcc()
    compiler = _compiler()
    payload["toolchain"] = {
        "optix_include": str(optix_include) if optix_include else None,
        "cuda_root": str(cuda_root) if cuda_root else None,
        "cuda_lib_dir": str(cuda_lib_dir) if cuda_lib_dir else None,
        "nvcc": nvcc,
        "compiler": compiler,
    }
    if not all((optix_include, cuda_root, cuda_lib_dir, nvcc, compiler)):
        payload.update({"status": "blocked", "blocked_stage": "toolchain_discovery"})
        return payload

    protocol = payload["protocol"]
    with tempfile.TemporaryDirectory(prefix="rtdl-v4-goal4700-app-route-") as tmp:
        tmp_path = Path(tmp)
        env = dict(os.environ)
        env["LD_LIBRARY_PATH"] = os.pathsep.join(
            [str(cuda_lib_dir), "/usr/lib/x86_64-linux-gnu", env.get("LD_LIBRARY_PATH", "")]
        )
        builtin = _run_builtin_denominators(protocol, tmp_path, env)
        payload["builtin_denominator_run"] = builtin
        if builtin["returncode"] != 0 or not builtin.get("payload"):
            payload.update({"status": "blocked", "blocked_stage": "builtin_denominator_run"})
            return payload

        callback_ptx = tmp_path / "callback.ptx"
        ptx_json = tmp_path / "callback.json"
        ptx_proc = _run([sys.executable, str(PTX_PROBE), "--json-out", str(ptx_json), "--ptx-out", str(callback_ptx)], cwd=ROOT, env=env)
        payload["ptx_probe"] = {"returncode": ptx_proc.returncode, "stdout": ptx_proc.stdout.strip()[:4000], "stderr": ptx_proc.stderr.strip()[:4000]}
        if ptx_proc.returncode != 0 or not callback_ptx.exists():
            payload.update({"status": "blocked", "blocked_stage": "numba_ptx_generation"})
            return payload
        callback_text = callback_ptx.read_text(encoding="utf-8")
        symbol_probe = extract_numba_callback_symbol_from_ptx(callback_text)
        payload["symbol_probe"] = symbol_probe.as_dict()
        if symbol_probe.status != "symbol_extracted" or not symbol_probe.symbol:
            payload.update({"status": "blocked", "blocked_stage": "callback_symbol_extraction"})
            return payload

        compile_plan = plan_v4_goal4698_specialized_tier3_compile(
            callback_shape="custom_scalar_reduce",
            callback_language="numba",
            numba_cabi_device_function=True,
            callback_symbol=symbol_probe.symbol,
            callback_ptx=callback_text,
            toolchain_fingerprint=json.dumps(payload["toolchain"], sort_keys=True),
            optix_abi="8.0",
            compute_target="sm_86",
        ).as_dict()
        payload["compile_plan"] = compile_plan
        if not compile_plan["internal_compile_allowed"]:
            payload.update({"status": "blocked", "blocked_stage": "compile_plan"})
            return payload

        wrapper_cu = tmp_path / "tier3_weighted_sum_wrapper.cu"
        wrapper_ptx = tmp_path / "tier3_weighted_sum_wrapper.ptx"
        wrapper_cu.write_text(_callback_wrapper_source(symbol_probe.symbol) + "\n", encoding="utf-8")
        compile_proc = _run(
            [str(nvcc), "-ptx", "-std=c++17", "--keep-device-functions", "-I", str(optix_include), str(wrapper_cu), "-o", str(wrapper_ptx)],
            cwd=tmp_path,
            env=env,
        )
        payload["wrapper_compile"] = {"returncode": compile_proc.returncode, "stdout": compile_proc.stdout.strip()[:4000], "stderr": compile_proc.stderr.strip()[:4000]}
        if compile_proc.returncode != 0 or not wrapper_ptx.exists():
            payload.update({"status": "blocked", "blocked_stage": "wrapper_compile"})
            return payload
        combined_ptx = tmp_path / "tier3_weighted_sum_combined.ptx"
        combined_ptx.write_text(compose_goal4688_combined_ptx(callback_text, wrapper_ptx.read_text(encoding="utf-8")), encoding="utf-8")

        cpp_path = tmp_path / "v4_goal4700_specialized_tier3_app_route_pod.cpp"
        binary_path = tmp_path / "v4_goal4700_specialized_tier3_app_route_pod"
        cpp_path.write_text(CPP_SOURCE, encoding="utf-8")
        loader_compile = _run(
            [
                str(compiler),
                "-std=c++17",
                "-O2",
                "-I",
                str(optix_include),
                "-I",
                str(cuda_root / "include"),
                str(cpp_path),
                "-L",
                str(cuda_lib_dir),
                "-lcuda",
                "-ldl",
                "-o",
                str(binary_path),
            ],
            cwd=tmp_path,
            env=env,
        )
        payload["loader_compile"] = {"returncode": loader_compile.returncode, "stdout": loader_compile.stdout.strip()[:4000], "stderr": loader_compile.stderr.strip()[:4000]}
        if loader_compile.returncode != 0:
            payload.update({"status": "blocked", "blocked_stage": "loader_compile"})
            return payload

        builtin_by_count = {int(row["ray_count"]): row for row in builtin["payload"]["results"]}
        rows: list[dict[str, Any]] = []
        for count in protocol["ray_counts"]:
            run_proc = _run(
                [str(binary_path), str(combined_ptx), str(count), str(protocol["warmup"]), str(protocol["repeat"])],
                cwd=tmp_path,
                env=env,
            )
            callback = _summarize_callback_stdout(run_proc.stdout, run_proc.stderr, run_proc.returncode)
            builtin_row = builtin_by_count[int(count)]
            tier2_s = float(builtin_row["routes"]["device_output_frontdoor"]["median_s"])
            host_s = float(builtin_row["routes"]["host_scalar_route"]["median_s"])
            callback_s = float(callback["median_s"] or 0.0)
            row = {
                "ray_count": int(count),
                "parity_passed": bool(callback["output_matches_expected"] and builtin_row["parity_passed"]),
                "expected_sum": callback["expected_sum"],
                "callback_output_sum": callback["output_sum"],
                "tier2_builtin_output_sum": builtin_row["device_output_weighted_sum"],
                "tier3_callback_route_median_s": callback_s,
                "tier2_builtin_route_median_s": tier2_s,
                "legacy_host_scalar_route_median_s": host_s,
                "callback_over_tier2_ratio": (callback_s / tier2_s) if tier2_s > 0.0 else None,
                "legacy_host_over_callback_ratio": (host_s / callback_s) if callback_s > 0.0 else None,
                "callback_run": callback,
            }
            rows.append(row)
            if run_proc.returncode != 0 or not row["parity_passed"]:
                payload["rows"] = rows
                payload.update({"status": "blocked", "blocked_stage": f"callback_route_count_{count}"})
                return payload
        payload["rows"] = rows
        payload["classification"] = classify_v4_goal4700_specialized_tier3_app_route_result(rows)
        payload["status"] = "specialized_tier3_app_route_measured_not_public_support"
        return payload


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# V4 Goal4700 Specialized Tier-3 App-Route POD Result",
        "",
        f"- status: `{payload['status']}`",
        f"- classification: `{(payload.get('classification') or {}).get('classification')}`",
        f"- tier3 public support authorized: `{payload['tier3_public_support_authorized']}`",
        "",
        "| rays | parity | callback median s | Tier-2 median s | host median s | callback/Tier-2 | host/callback |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in payload.get("rows", []):
        lines.append(
            "| {ray_count} | {parity} | {callback:.9f} | {tier2:.9f} | {host:.9f} | {ratio:.3f}x | {host_ratio:.3f}x |".format(
                ray_count=row["ray_count"],
                parity=str(bool(row["parity_passed"])).lower(),
                callback=float(row["tier3_callback_route_median_s"]),
                tier2=float(row["tier2_builtin_route_median_s"]),
                host=float(row["legacy_host_scalar_route_median_s"]),
                ratio=float(row["callback_over_tier2_ratio"]),
                host_ratio=float(row["legacy_host_over_callback_ratio"]),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This measurement does not authorize public Tier-3 support, arbitrary callback support, app-level speed claims, or V4 release wording.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V4 Goal4700 specialized Tier-3 app-route POD validation.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()
    payload = _run_probe(bool(args.dry_run))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        _write_markdown(args.md_out, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] in {"dry_run_contract_passed", "specialized_tier3_app_route_measured_not_public_support"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

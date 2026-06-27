from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import statistics
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
from rtdsl.v4_goal4690_tier3_overhead_protocol import v4_goal4690_tier3_overhead_protocol
from rtdsl.v4_goal4691_tier3_overhead_measurement import classify_v4_goal4691_overhead_ratio
from rtdsl.v4_goal4691_tier3_overhead_measurement import validate_v4_goal4691_tier3_overhead_measurement_contract
from v4_goal4688_tier3_module_link_probe import CALLABLE_ENTRY_RE
from v4_goal4688_tier3_module_link_probe import PTX_PROBE
from v4_goal4688_tier3_module_link_probe import _compiler
from v4_goal4688_tier3_module_link_probe import _find_cuda_lib_dir
from v4_goal4688_tier3_module_link_probe import _find_cuda_root
from v4_goal4688_tier3_module_link_probe import _find_nvcc
from v4_goal4688_tier3_module_link_probe import _find_optix_include
from v4_goal4688_tier3_module_link_probe import _run


SAMPLE_RE = re.compile(r"sample_ms=([0-9.eE+-]+)")
KEY_VALUE_RE = re.compile(r"^([A-Za-z0-9_]+)=([^\n]+)$", re.MULTILINE)


CPP_SOURCE = r"""
#include <cuda.h>
#include <optix.h>
#include <optix_function_table_definition.h>
#include <optix_stack_size.h>
#include <optix_stubs.h>

#include <cmath>
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

struct EmptyData {
    unsigned int unused = 0;
};

using RaygenRecord = SbtRecord<EmptyData>;
using MissRecord = SbtRecord<EmptyData>;
using HitRecord = SbtRecord<EmptyData>;
using CallableRecord = SbtRecord<EmptyData>;

struct Params {
    double* output_state;
    unsigned int iterations;
    unsigned int primitive_id;
    double hit_t;
    double weight;
    double state0;
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
    if (log_size > 1 && log[0] != '\0') {
        std::cout << what << "_log_begin\n" << log << "\n" << what << "_log_end\n";
    }
    check_optix(result, what);
    return group;
}

int main(int argc, char** argv) {
    try {
        if (argc != 7) {
            std::cerr << "usage: v4_goal4691_tier3_overhead_measurement <ptx> <variant> <callable_entry_or_none> <iterations> <warmups> <measured>\n";
            return 64;
        }
        std::string ptx = read_text(argv[1]);
        std::string variant = argv[2];
        std::string callable_entry_name = argv[3];
        unsigned int iterations = static_cast<unsigned int>(std::stoul(argv[4]));
        unsigned int warmups = static_cast<unsigned int>(std::stoul(argv[5]));
        unsigned int measured = static_cast<unsigned int>(std::stoul(argv[6]));
        bool has_callable = (variant == "direct_callable");

        check_cuda(cuInit(0), "cuInit");
        CUdevice dev = 0;
        check_cuda(cuDeviceGet(&dev, 0), "cuDeviceGet");
        CUcontext cu_ctx = nullptr;
        check_cuda(cuDevicePrimaryCtxRetain(&cu_ctx, dev), "cuDevicePrimaryCtxRetain");
        check_cuda(cuCtxSetCurrent(cu_ctx), "cuCtxSetCurrent");
        check_optix(optixInit(), "optixInit");

        OptixDeviceContextOptions context_options = {};
        OptixDeviceContext optix_ctx = nullptr;
        check_optix(optixDeviceContextCreate(cu_ctx, &context_options, &optix_ctx),
                    "optixDeviceContextCreate");

        OptixModuleCompileOptions module_options = {};
        module_options.maxRegisterCount = OPTIX_COMPILE_DEFAULT_MAX_REGISTER_COUNT;
        module_options.optLevel = OPTIX_COMPILE_OPTIMIZATION_DEFAULT;
        module_options.debugLevel = OPTIX_COMPILE_DEBUG_LEVEL_NONE;

        OptixPipelineCompileOptions pipeline_options = {};
        pipeline_options.usesMotionBlur = 0;
        pipeline_options.traversableGraphFlags = OPTIX_TRAVERSABLE_GRAPH_FLAG_ALLOW_SINGLE_GAS;
        pipeline_options.numPayloadValues = 0;
        pipeline_options.numAttributeValues = 0;
        pipeline_options.exceptionFlags = OPTIX_EXCEPTION_FLAG_NONE;
        pipeline_options.pipelineLaunchParamsVariableName = "params";
        pipeline_options.usesPrimitiveTypeFlags = OPTIX_PRIMITIVE_TYPE_FLAGS_CUSTOM;

        char module_log[16384] = {};
        size_t module_log_size = sizeof(module_log);
        OptixModule module = nullptr;
#if defined(OPTIX_VERSION) && OPTIX_VERSION < 70700
        OptixResult module_result = optixModuleCreateFromPTX(
            optix_ctx, &module_options, &pipeline_options,
            ptx.c_str(), ptx.size(), module_log, &module_log_size, &module);
#else
        OptixResult module_result = optixModuleCreate(
            optix_ctx, &module_options, &pipeline_options,
            ptx.c_str(), ptx.size(), module_log, &module_log_size, &module);
#endif
        std::cout << "optix_module_create_result=" << static_cast<int>(module_result) << "\n";
        check_optix(module_result, "optixModuleCreate");

        OptixProgramGroupDesc raygen_desc = {};
        raygen_desc.kind = OPTIX_PROGRAM_GROUP_KIND_RAYGEN;
        raygen_desc.raygen.module = module;
        raygen_desc.raygen.entryFunctionName = "__raygen__rtdl_tier3_probe";
        OptixProgramGroup raygen_pg = create_program_group(optix_ctx, raygen_desc, "raygen_program_group");

        OptixProgramGroupDesc miss_desc = {};
        miss_desc.kind = OPTIX_PROGRAM_GROUP_KIND_MISS;
        miss_desc.miss.module = module;
        miss_desc.miss.entryFunctionName = "__miss__rtdl_tier3_probe";
        OptixProgramGroup miss_pg = create_program_group(optix_ctx, miss_desc, "miss_program_group");

        OptixProgramGroupDesc hit_desc = {};
        hit_desc.kind = OPTIX_PROGRAM_GROUP_KIND_HITGROUP;
        hit_desc.hitgroup.moduleCH = module;
        hit_desc.hitgroup.entryFunctionNameCH = "__closesthit__rtdl_tier3_probe";
        OptixProgramGroup hit_pg = create_program_group(optix_ctx, hit_desc, "hit_program_group");

        OptixProgramGroup callable_pg = nullptr;
        std::vector<OptixProgramGroup> groups = {raygen_pg, miss_pg, hit_pg};
        if (has_callable) {
            OptixProgramGroupDesc call_desc = {};
            call_desc.kind = OPTIX_PROGRAM_GROUP_KIND_CALLABLES;
            call_desc.callables.moduleDC = module;
            call_desc.callables.entryFunctionNameDC = callable_entry_name.c_str();
            callable_pg = create_program_group(optix_ctx, call_desc, "callable_program_group");
            groups.push_back(callable_pg);
        }

        OptixPipelineLinkOptions link_options = {};
        link_options.maxTraceDepth = 1;
        char pipeline_log[16384] = {};
        size_t pipeline_log_size = sizeof(pipeline_log);
        OptixPipeline pipeline = nullptr;
        OptixResult pipeline_result = optixPipelineCreate(
            optix_ctx,
            &pipeline_options,
            &link_options,
            groups.data(),
            static_cast<unsigned int>(groups.size()),
            pipeline_log,
            &pipeline_log_size,
            &pipeline);
        std::cout << "pipeline_create_result=" << static_cast<int>(pipeline_result) << "\n";
        if (pipeline_log_size > 1 && pipeline_log[0] != '\0') {
            std::cout << "pipeline_log_begin\n" << pipeline_log << "\npipeline_log_end\n";
        }
        check_optix(pipeline_result, "optixPipelineCreate");

        OptixStackSizes stack_sizes = {};
#if defined(OPTIX_VERSION) && OPTIX_VERSION < 70700
        check_optix(optixUtilAccumulateStackSizes(raygen_pg, &stack_sizes), "stack raygen");
        check_optix(optixUtilAccumulateStackSizes(miss_pg, &stack_sizes), "stack miss");
        check_optix(optixUtilAccumulateStackSizes(hit_pg, &stack_sizes), "stack hit");
        if (callable_pg) check_optix(optixUtilAccumulateStackSizes(callable_pg, &stack_sizes), "stack callable");
#else
        check_optix(optixUtilAccumulateStackSizes(raygen_pg, &stack_sizes, pipeline), "stack raygen");
        check_optix(optixUtilAccumulateStackSizes(miss_pg, &stack_sizes, pipeline), "stack miss");
        check_optix(optixUtilAccumulateStackSizes(hit_pg, &stack_sizes, pipeline), "stack hit");
        if (callable_pg) check_optix(optixUtilAccumulateStackSizes(callable_pg, &stack_sizes, pipeline), "stack callable");
#endif
        uint32_t dc_from_traversal = 0;
        uint32_t dc_from_state = 0;
        uint32_t continuation = 0;
        check_optix(
            optixUtilComputeStackSizes(
                &stack_sizes,
                link_options.maxTraceDepth,
                0,
                has_callable ? 1 : 0,
                &dc_from_traversal,
                &dc_from_state,
                &continuation),
            "optixUtilComputeStackSizes");
        check_optix(
            optixPipelineSetStackSize(pipeline, dc_from_traversal, dc_from_state, continuation, 1),
            "optixPipelineSetStackSize");

        RaygenRecord raygen_rec = {};
        MissRecord miss_rec = {};
        HitRecord hit_rec = {};
        check_optix(optixSbtRecordPackHeader(raygen_pg, &raygen_rec), "pack raygen");
        check_optix(optixSbtRecordPackHeader(miss_pg, &miss_rec), "pack miss");
        check_optix(optixSbtRecordPackHeader(hit_pg, &hit_rec), "pack hit");
        CUdeviceptr raygen_dev = 0;
        CUdeviceptr miss_dev = 0;
        CUdeviceptr hit_dev = 0;
        check_cuda(cuMemAlloc(&raygen_dev, sizeof(RaygenRecord)), "cuMemAlloc raygen");
        check_cuda(cuMemAlloc(&miss_dev, sizeof(MissRecord)), "cuMemAlloc miss");
        check_cuda(cuMemAlloc(&hit_dev, sizeof(HitRecord)), "cuMemAlloc hit");
        check_cuda(cuMemcpyHtoD(raygen_dev, &raygen_rec, sizeof(RaygenRecord)), "copy raygen");
        check_cuda(cuMemcpyHtoD(miss_dev, &miss_rec, sizeof(MissRecord)), "copy miss");
        check_cuda(cuMemcpyHtoD(hit_dev, &hit_rec, sizeof(HitRecord)), "copy hit");

        CUdeviceptr callable_dev = 0;
        if (has_callable) {
            CallableRecord callable_rec = {};
            check_optix(optixSbtRecordPackHeader(callable_pg, &callable_rec), "pack callable");
            check_cuda(cuMemAlloc(&callable_dev, sizeof(CallableRecord)), "cuMemAlloc callable");
            check_cuda(cuMemcpyHtoD(callable_dev, &callable_rec, sizeof(CallableRecord)), "copy callable");
        }

        OptixShaderBindingTable sbt = {};
        sbt.raygenRecord = raygen_dev;
        sbt.missRecordBase = miss_dev;
        sbt.missRecordStrideInBytes = sizeof(MissRecord);
        sbt.missRecordCount = 1;
        sbt.hitgroupRecordBase = hit_dev;
        sbt.hitgroupRecordStrideInBytes = sizeof(HitRecord);
        sbt.hitgroupRecordCount = 1;
        if (has_callable) {
            sbt.callablesRecordBase = callable_dev;
            sbt.callablesRecordStrideInBytes = sizeof(CallableRecord);
            sbt.callablesRecordCount = 1;
        }

        CUdeviceptr output_dev = 0;
        CUdeviceptr params_dev = 0;
        double initial_value = -777.0;
        check_cuda(cuMemAlloc(&output_dev, sizeof(double)), "cuMemAlloc output");
        check_cuda(cuMemcpyHtoD(output_dev, &initial_value, sizeof(double)), "copy output init");
        Params params = {};
        params.output_state = reinterpret_cast<double*>(output_dev);
        params.iterations = iterations;
        params.primitive_id = 0u;
        params.hit_t = 1.0;
        params.weight = 2.0;
        params.state0 = 3.0;
        check_cuda(cuMemAlloc(&params_dev, sizeof(Params)), "cuMemAlloc params");
        check_cuda(cuMemcpyHtoD(params_dev, &params, sizeof(Params)), "copy params");

        for (unsigned int i = 0; i < warmups; ++i) {
            check_optix(optixLaunch(pipeline, 0, params_dev, sizeof(Params), &sbt, 1, 1, 1), "warmup optixLaunch");
        }
        check_cuda(cuStreamSynchronize(0), "warmup synchronize");

        CUevent start = nullptr;
        CUevent stop = nullptr;
        check_cuda(cuEventCreate(&start, CU_EVENT_DEFAULT), "cuEventCreate start");
        check_cuda(cuEventCreate(&stop, CU_EVENT_DEFAULT), "cuEventCreate stop");
        for (unsigned int i = 0; i < measured; ++i) {
            check_cuda(cuEventRecord(start, 0), "event start");
            check_optix(optixLaunch(pipeline, 0, params_dev, sizeof(Params), &sbt, 1, 1, 1), "measured optixLaunch");
            check_cuda(cuEventRecord(stop, 0), "event stop");
            check_cuda(cuEventSynchronize(stop), "event synchronize");
            float ms = 0.0f;
            check_cuda(cuEventElapsedTime(&ms, start, stop), "event elapsed");
            std::cout << "sample_ms=" << ms << "\n";
        }
        check_cuda(cuStreamSynchronize(0), "measured synchronize");

        double output_value = 0.0;
        check_cuda(cuMemcpyDtoH(&output_value, output_dev, sizeof(double)), "copy output back");
        double expected_value = static_cast<double>(iterations) * 5.0;
        bool matches = std::abs(output_value - expected_value) <= 1.0e-6 * expected_value;
        std::cout << "variant=" << variant << "\n";
        std::cout << "iterations=" << iterations << "\n";
        std::cout << "warmups=" << warmups << "\n";
        std::cout << "measured=" << measured << "\n";
        std::cout << "output_value=" << output_value << "\n";
        std::cout << "expected_value=" << expected_value << "\n";
        std::cout << "output_matches_expected=" << (matches ? 1 : 0) << "\n";

        cuEventDestroy(stop);
        cuEventDestroy(start);
        cuMemFree(params_dev);
        cuMemFree(output_dev);
        if (callable_dev) cuMemFree(callable_dev);
        cuMemFree(hit_dev);
        cuMemFree(miss_dev);
        cuMemFree(raygen_dev);
        optixPipelineDestroy(pipeline);
        if (callable_pg) optixProgramGroupDestroy(callable_pg);
        optixProgramGroupDestroy(hit_pg);
        optixProgramGroupDestroy(miss_pg);
        optixProgramGroupDestroy(raygen_pg);
        optixModuleDestroy(module);
        optixDeviceContextDestroy(optix_ctx);
        return matches ? 0 : 6;
    } catch (const std::exception& exc) {
        std::cerr << exc.what() << "\n";
        return 3;
    }
}
"""


def goal4691_wrapper_source(variant: str, callback_symbol: str | None) -> str:
    common_params = """
struct RtdlTier3ProbeParams {
    double* output_state;
    unsigned int iterations;
    unsigned int primitive_id;
    double hit_t;
    double weight;
    double state0;
};

extern "C" {
__constant__ RtdlTier3ProbeParams params;
}
""".strip()
    if variant == "inline_formula":
        body = """
extern "C" __global__ void __raygen__rtdl_tier3_probe() {
    double acc = 0.0;
    for (unsigned int i = 0; i < params.iterations; ++i) {
        acc += params.state0 + params.hit_t * params.weight + params.primitive_id * 0.0;
    }
    params.output_state[0] = acc;
}

extern "C" __global__ void __miss__rtdl_tier3_probe() {
}

extern "C" __global__ void __closesthit__rtdl_tier3_probe() {
}
""".strip()
        return "\n\n".join(("#include <optix.h>\n#include <optix_device.h>", common_params, body))
    if not callback_symbol:
        raise ValueError("callback_symbol is required for callback variants")
    callback_decl = f"""
extern "C" __device__ double {callback_symbol}(
    double hit_t,
    unsigned int primitive_id,
    double payload0,
    double state0);
""".strip()
    if variant == "direct_device":
        body = f"""
extern "C" __global__ void __raygen__rtdl_tier3_probe() {{
    double acc = 0.0;
    for (unsigned int i = 0; i < params.iterations; ++i) {{
        acc += {callback_symbol}(params.hit_t, params.primitive_id, params.weight, params.state0);
    }}
    params.output_state[0] = acc;
}}

extern "C" __global__ void __miss__rtdl_tier3_probe() {{
}}

extern "C" __global__ void __closesthit__rtdl_tier3_probe() {{
}}
""".strip()
        return "\n\n".join(("#include <optix.h>\n#include <optix_device.h>", callback_decl, common_params, body))
    if variant == "direct_callable":
        body = f"""
extern "C" __device__ __noinline__ double __direct_callable__rtdl_tier3_scalar_reduce(
    double hit_t,
    unsigned int primitive_id,
    double payload0,
    double state0) {{
    return {callback_symbol}(hit_t, primitive_id, payload0, state0);
}}

extern "C" __global__ void __raygen__rtdl_tier3_probe() {{
    double acc = 0.0;
    for (unsigned int i = 0; i < params.iterations; ++i) {{
        acc += optixDirectCall<double, double, unsigned int, double, double>(
            0, params.hit_t, params.primitive_id, params.weight, params.state0);
    }}
    params.output_state[0] = acc;
}}

extern "C" __global__ void __miss__rtdl_tier3_probe() {{
}}

extern "C" __global__ void __closesthit__rtdl_tier3_probe() {{
}}
""".strip()
        return "\n\n".join(("#include <optix.h>\n#include <optix_device.h>", callback_decl, common_params, body))
    raise ValueError(f"unknown variant: {variant}")


def _base_payload(dry_run: bool) -> dict[str, Any]:
    protocol = v4_goal4690_tier3_overhead_protocol().as_dict()
    return {
        "schema": "rtdl.v4.goal4691_tier3_overhead_measurement.v1",
        "status": "dry_run" if dry_run else "unknown",
        "dry_run": dry_run,
        "protocol": protocol,
        "variants": {},
        "primary_ratio": None,
        "classification": None,
        "performance_claim_authorized": False,
        "tier3_public_support_authorized": False,
        "release_authorized": False,
        "app_identity_kernel_authorized": False,
    }


def _summarize_run(stdout: str, returncode: int, stderr: str) -> dict[str, Any]:
    samples = [float(match.group(1)) for match in SAMPLE_RE.finditer(stdout)]
    pairs = {match.group(1): match.group(2).strip() for match in KEY_VALUE_RE.finditer(stdout)}
    return {
        "returncode": returncode,
        "stdout": stdout.strip()[:16000],
        "stderr": stderr.strip()[:4000],
        "sample_count": len(samples),
        "samples_ms": samples,
        "median_ms": statistics.median(samples) if samples else None,
        "min_ms": min(samples) if samples else None,
        "max_ms": max(samples) if samples else None,
        "output_value": float(pairs["output_value"]) if "output_value" in pairs else None,
        "expected_value": float(pairs["expected_value"]) if "expected_value" in pairs else None,
        "output_matches_expected": pairs.get("output_matches_expected") == "1",
        "pipeline_create_succeeded": "pipeline_create_result=0" in stdout,
        "optix_module_link_succeeded": "optix_module_create_result=0" in stdout,
    }


def _run_probe(dry_run: bool) -> dict[str, Any]:
    payload = _base_payload(dry_run)
    contract = validate_v4_goal4691_tier3_overhead_measurement_contract()
    payload["contract_validation"] = contract
    if dry_run:
        payload["status"] = "dry_run_contract_passed" if contract["status"] == "passed" else "dry_run_contract_failed"
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
    missing = [
        name
        for name, value in {
            "optix_include": optix_include,
            "cuda_root": cuda_root,
            "cuda_lib_dir": cuda_lib_dir,
            "nvcc": nvcc,
            "compiler": compiler,
        }.items()
        if value is None
    ]
    if missing:
        payload.update({"status": "blocked", "blocked_stage": "toolchain_discovery", "missing": missing})
        return payload

    protocol = v4_goal4690_tier3_overhead_protocol()
    iterations = protocol.inner_iterations
    warmups = protocol.warmup_launches
    measured = protocol.measured_launches

    with tempfile.TemporaryDirectory(prefix="rtdl-v4-goal4691-overhead-") as tmp:
        tmp_path = Path(tmp)
        callback_ptx = tmp_path / "callback.ptx"
        ptx_json = tmp_path / "callback.json"
        ptx_proc = _run(
            [sys.executable, str(PTX_PROBE), "--json-out", str(ptx_json), "--ptx-out", str(callback_ptx)],
            cwd=ROOT,
        )
        payload["ptx_probe"] = {
            "returncode": ptx_proc.returncode,
            "stdout": ptx_proc.stdout.strip()[:4000],
            "stderr": ptx_proc.stderr.strip()[:4000],
        }
        if ptx_json.exists():
            payload["ptx_probe_payload"] = json.loads(ptx_json.read_text(encoding="utf-8"))
        if ptx_proc.returncode != 0 or not callback_ptx.exists():
            payload.update({"status": "blocked", "blocked_stage": "numba_ptx_generation"})
            return payload
        callback_text = callback_ptx.read_text(encoding="utf-8")
        symbol_probe = extract_numba_callback_symbol_from_ptx(callback_text)
        payload["symbol_probe"] = symbol_probe.as_dict()
        if symbol_probe.status != "symbol_extracted" or not symbol_probe.symbol:
            payload.update({"status": "blocked", "blocked_stage": "callback_symbol_extraction"})
            return payload

        cpp_path = tmp_path / "v4_goal4691_tier3_overhead_measurement.cpp"
        binary_path = tmp_path / "v4_goal4691_tier3_overhead_measurement"
        cpp_path.write_text(CPP_SOURCE, encoding="utf-8")
        compile_loader = _run(
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
        )
        payload["loader_compile"] = {
            "returncode": compile_loader.returncode,
            "stdout": compile_loader.stdout.strip()[:4000],
            "stderr": compile_loader.stderr.strip()[:4000],
        }
        if compile_loader.returncode != 0:
            payload.update({"status": "blocked", "blocked_stage": "loader_compile"})
            return payload

        env = dict(os.environ)
        env["LD_LIBRARY_PATH"] = os.pathsep.join(
            [str(cuda_lib_dir), "/usr/lib/x86_64-linux-gnu", env.get("LD_LIBRARY_PATH", "")]
        )
        for variant in ("inline_formula", "direct_device", "direct_callable"):
            wrapper_cu = tmp_path / f"{variant}.cu"
            wrapper_ptx = tmp_path / f"{variant}.ptx"
            wrapper_cu.write_text(goal4691_wrapper_source(variant, symbol_probe.symbol), encoding="utf-8")
            compile_proc = _run(
                [
                    str(nvcc),
                    "-ptx",
                    "-std=c++17",
                    "--keep-device-functions",
                    "-I",
                    str(optix_include),
                    str(wrapper_cu),
                    "-o",
                    str(wrapper_ptx),
                ],
                cwd=tmp_path,
            )
            variant_payload: dict[str, Any] = {
                "wrapper_compile": {
                    "returncode": compile_proc.returncode,
                    "stdout": compile_proc.stdout.strip()[:4000],
                    "stderr": compile_proc.stderr.strip()[:4000],
                }
            }
            if compile_proc.returncode != 0 or not wrapper_ptx.exists():
                variant_payload.update({"status": "blocked", "blocked_stage": "wrapper_compile"})
                payload["variants"][variant] = variant_payload
                payload.update({"status": "blocked", "blocked_stage": f"{variant}_wrapper_compile"})
                return payload
            wrapper_text = wrapper_ptx.read_text(encoding="utf-8")
            if variant == "inline_formula":
                run_ptx = wrapper_ptx
                callable_entry_name = "none"
            else:
                run_ptx = tmp_path / f"{variant}_combined.ptx"
                run_ptx.write_text(compose_goal4688_combined_ptx(callback_text, wrapper_text), encoding="utf-8")
                raw_callable_names = set(CALLABLE_ENTRY_RE.findall(wrapper_text))
                callable_names = sorted(
                    name
                    for name in raw_callable_names
                    if "_param" not in name
                )
                callable_entry_name = (
                    "__direct_callable__rtdl_tier3_scalar_reduce"
                    if "__direct_callable__rtdl_tier3_scalar_reduce" in callable_names
                    else (callable_names[0] if callable_names else "__direct_callable__rtdl_tier3_scalar_reduce")
                )
                variant_payload["raw_callable_entry_candidates"] = sorted(raw_callable_names)
                variant_payload["callable_entry_candidates"] = callable_names
                variant_payload["callable_entry_name_selected"] = callable_entry_name
            run_proc = _run(
                [
                    str(binary_path),
                    str(run_ptx),
                    variant.replace("_formula", "").replace("_device", "_device").replace("_callable", "_callable"),
                    callable_entry_name,
                    str(iterations),
                    str(warmups),
                    str(measured),
                ],
                cwd=tmp_path,
                env=env,
            )
            variant_payload.update(_summarize_run(run_proc.stdout, run_proc.returncode, run_proc.stderr))
            if run_proc.returncode == 0 and variant_payload["output_matches_expected"]:
                variant_payload["status"] = "passed"
            else:
                variant_payload["status"] = "blocked"
                variant_payload["blocked_stage"] = "variant_run_or_correctness"
                payload["variants"][variant] = variant_payload
                payload.update({"status": "blocked", "blocked_stage": f"{variant}_run_or_correctness"})
                return payload
            payload["variants"][variant] = variant_payload

    direct_callable = payload["variants"]["direct_callable"]["median_ms"]
    direct_device = payload["variants"]["direct_device"]["median_ms"]
    ratio = None if not direct_callable or not direct_device else float(direct_callable) / float(direct_device)
    payload["primary_ratio"] = ratio
    payload["classification"] = classify_v4_goal4691_overhead_ratio(ratio)
    payload["status"] = "tier3_overhead_measured_not_support"
    return payload


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# V4 Goal4691 Tier-3 Callback Overhead Measurement",
        "",
        "Status: measured overhead gate, not Tier-3 support and not release authorization",
        "",
        f"- status: `{payload['status']}`",
        f"- primary ratio: `{payload.get('primary_ratio')}`",
        f"- classification: `{payload.get('classification')}`",
        "",
        "## Variants",
        "",
    ]
    for name, row in payload.get("variants", {}).items():
        lines.extend(
            [
                f"### `{name}`",
                "",
                f"- status: `{row.get('status')}`",
                f"- median ms: `{row.get('median_ms')}`",
                f"- sample count: `{row.get('sample_count')}`",
                f"- output matches expected: `{row.get('output_matches_expected')}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Boundary",
            "",
            "This measurement does not authorize public Tier-3 callback support. It only classifies the overhead of the minimal scalar callback shape against the frozen Goal4690 denominator.",
            "",
        ]
    )
    if payload.get("status") == "blocked":
        lines.extend(["## Blocked Stage", "", f"- blocked stage: `{payload.get('blocked_stage')}`", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure V4 Goal4691 Tier-3 direct-callable overhead.")
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
    return 0 if payload["status"] in {"dry_run_contract_passed", "tier3_overhead_measured_not_support"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

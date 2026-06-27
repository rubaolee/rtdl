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
from rtdsl.v4_goal4694_specialized_hit_overhead_protocol import v4_goal4694_specialized_hit_overhead_protocol
from rtdsl.v4_goal4695_specialized_hit_overhead_measurement import classify_v4_goal4695_hit_overhead_ratio
from rtdsl.v4_goal4695_specialized_hit_overhead_measurement import validate_v4_goal4695_specialized_hit_overhead_measurement_contract
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

struct EmptyData { unsigned int unused = 0; };
using RaygenRecord = SbtRecord<EmptyData>;
using MissRecord = SbtRecord<EmptyData>;
using HitRecord = SbtRecord<EmptyData>;

struct Params {
    OptixTraversableHandle handle;
    double* output_state;
    unsigned int iterations;
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
            std::cerr << "usage: v4_goal4695_specialized_hit_overhead_measurement <ptx> <iterations> <warmups> <measured>\n";
            return 64;
        }
        std::string ptx = read_text(argv[1]);
        unsigned int iterations = static_cast<unsigned int>(std::stoul(argv[2]));
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

        OptixAabb aabb = {};
        aabb.minX = 0.0f; aabb.minY = -1.0f; aabb.minZ = -1.0f;
        aabb.maxX = 2.0f; aabb.maxY = 1.0f; aabb.maxZ = 1.0f;
        CUdeviceptr aabb_dev = 0;
        check_cuda(cuMemAlloc(&aabb_dev, sizeof(OptixAabb)), "cuMemAlloc aabb");
        check_cuda(cuMemcpyHtoD(aabb_dev, &aabb, sizeof(OptixAabb)), "copy aabb");
        OptixBuildInput build_input = {};
        build_input.type = OPTIX_BUILD_INPUT_TYPE_CUSTOM_PRIMITIVES;
        build_input.customPrimitiveArray.aabbBuffers = &aabb_dev;
        build_input.customPrimitiveArray.numPrimitives = 1;
        build_input.customPrimitiveArray.strideInBytes = sizeof(OptixAabb);
        unsigned int geometry_flags = OPTIX_GEOMETRY_FLAG_NONE;
        build_input.customPrimitiveArray.flags = &geometry_flags;
        build_input.customPrimitiveArray.numSbtRecords = 1;
        OptixAccelBuildOptions accel_options = {};
        accel_options.buildFlags = OPTIX_BUILD_FLAG_ALLOW_COMPACTION;
        accel_options.operation = OPTIX_BUILD_OPERATION_BUILD;
        OptixAccelBufferSizes accel_sizes = {};
        check_optix(optixAccelComputeMemoryUsage(optix_ctx, &accel_options, &build_input, 1, &accel_sizes),
                    "optixAccelComputeMemoryUsage");
        CUdeviceptr temp_dev = 0, gas_dev = 0;
        check_cuda(cuMemAlloc(&temp_dev, accel_sizes.tempSizeInBytes), "cuMemAlloc temp");
        check_cuda(cuMemAlloc(&gas_dev, accel_sizes.outputSizeInBytes), "cuMemAlloc gas");
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
        pipeline_options.numAttributeValues = 0;
        pipeline_options.exceptionFlags = OPTIX_EXCEPTION_FLAG_NONE;
        pipeline_options.pipelineLaunchParamsVariableName = "params";
        pipeline_options.usesPrimitiveTypeFlags = OPTIX_PRIMITIVE_TYPE_FLAGS_CUSTOM;
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
        raygen_desc.raygen.entryFunctionName = "__raygen__rtdl_tier3_probe";
        OptixProgramGroupDesc miss_desc = {};
        miss_desc.kind = OPTIX_PROGRAM_GROUP_KIND_MISS;
        miss_desc.miss.module = module;
        miss_desc.miss.entryFunctionName = "__miss__rtdl_tier3_probe";
        OptixProgramGroupDesc hit_desc = {};
        hit_desc.kind = OPTIX_PROGRAM_GROUP_KIND_HITGROUP;
        hit_desc.hitgroup.moduleIS = module;
        hit_desc.hitgroup.entryFunctionNameIS = "__intersection__rtdl_tier3_probe";
        hit_desc.hitgroup.moduleCH = module;
        hit_desc.hitgroup.entryFunctionNameCH = "__closesthit__rtdl_tier3_probe";
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
        double initial_value = -777.0;
        check_cuda(cuMemAlloc(&output_dev, sizeof(double)), "alloc output");
        check_cuda(cuMemcpyHtoD(output_dev, &initial_value, sizeof(double)), "init output");
        Params params = {};
        params.handle = gas_handle;
        params.output_state = reinterpret_cast<double*>(output_dev);
        params.iterations = iterations;
        check_cuda(cuMemAlloc(&params_dev, sizeof(Params)), "alloc params");
        check_cuda(cuMemcpyHtoD(params_dev, &params, sizeof(Params)), "copy params");

        for (unsigned int i = 0; i < warmups; ++i) {
            check_optix(optixLaunch(pipeline, 0, params_dev, sizeof(Params), &sbt, 1, 1, 1), "warmup launch");
        }
        check_cuda(cuStreamSynchronize(0), "warmup sync");
        CUevent start = nullptr, stop = nullptr;
        check_cuda(cuEventCreate(&start, CU_EVENT_DEFAULT), "event start create");
        check_cuda(cuEventCreate(&stop, CU_EVENT_DEFAULT), "event stop create");
        for (unsigned int i = 0; i < measured; ++i) {
            check_cuda(cuEventRecord(start, 0), "event record start");
            check_optix(optixLaunch(pipeline, 0, params_dev, sizeof(Params), &sbt, 1, 1, 1), "measured launch");
            check_cuda(cuEventRecord(stop, 0), "event record stop");
            check_cuda(cuEventSynchronize(stop), "event sync");
            float ms = 0.0f;
            check_cuda(cuEventElapsedTime(&ms, start, stop), "event elapsed");
            std::cout << "sample_ms=" << ms << "\n";
        }
        check_cuda(cuStreamSynchronize(0), "measured sync");
        double output_value = 0.0;
        check_cuda(cuMemcpyDtoH(&output_value, output_dev, sizeof(double)), "copy output");
        bool matches = std::abs(output_value - 5.0) <= 1.0e-9;
        std::cout << "output_value=" << output_value << "\n";
        std::cout << "expected_value=5\n";
        std::cout << "output_matches_expected=" << (matches ? 1 : 0) << "\n";

        return matches ? 0 : 6;
    } catch (const std::exception& exc) {
        std::cerr << exc.what() << "\n";
        return 3;
    }
}
"""


def goal4695_hit_loop_source(variant: str, callback_symbol: str | None) -> str:
    params = """
struct RtdlTier3ProbeParams {
    OptixTraversableHandle handle;
    double* output_state;
    unsigned int iterations;
};

extern "C" {
__constant__ RtdlTier3ProbeParams params;
}
""".strip()
    raygen = """
extern "C" __global__ void __raygen__rtdl_tier3_probe() {
    const float3 origin = make_float3(-1.0f, 0.0f, 0.0f);
    const float3 direction = make_float3(1.0f, 0.0f, 0.0f);
    for (unsigned int i = 0; i < params.iterations; ++i) {
        optixTrace(params.handle, origin, direction, 0.0f, 10.0f, 0.0f,
                   OptixVisibilityMask(255), OPTIX_RAY_FLAG_NONE, 0, 1, 0);
    }
}

extern "C" __global__ void __intersection__rtdl_tier3_probe() {
    optixReportIntersection(1.0f, 0);
}

extern "C" __global__ void __miss__rtdl_tier3_probe() {
    params.output_state[0] = -1.0;
}
""".strip()
    if variant == "inline":
        closest = """
extern "C" __global__ void __closesthit__rtdl_tier3_probe() {
    params.output_state[0] = 3.0 + 1.0 * 2.0 + optixGetPrimitiveIndex() * 0.0;
}
""".strip()
        return "\n\n".join(("#include <optix.h>\n#include <optix_device.h>", params, raygen, closest))
    if not callback_symbol:
        raise ValueError("callback_symbol is required for callback variant")
    decl = f"""
extern "C" __device__ double {callback_symbol}(
    double hit_t,
    unsigned int primitive_id,
    double payload0,
    double state0);
""".strip()
    closest = f"""
extern "C" __global__ void __closesthit__rtdl_tier3_probe() {{
    params.output_state[0] = {callback_symbol}(1.0, optixGetPrimitiveIndex(), 2.0, 3.0);
}}
""".strip()
    return "\n\n".join(("#include <optix.h>\n#include <optix_device.h>", decl, params, raygen, closest))


def _base_payload(dry_run: bool) -> dict[str, Any]:
    protocol = v4_goal4694_specialized_hit_overhead_protocol().as_dict()
    return {
        "schema": "rtdl.v4.goal4695_specialized_hit_overhead_measurement.v1",
        "status": "dry_run" if dry_run else "unknown",
        "dry_run": dry_run,
        "protocol": protocol,
        "variants": {},
        "primary_ratio": None,
        "classification": None,
        "release_authorized": False,
        "tier3_public_support_authorized": False,
        "performance_claim_authorized": False,
    }


def _summarize(stdout: str, stderr: str, returncode: int) -> dict[str, Any]:
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
    }


def _run_probe(dry_run: bool) -> dict[str, Any]:
    payload = _base_payload(dry_run)
    contract = validate_v4_goal4695_specialized_hit_overhead_measurement_contract()
    payload["contract_validation"] = contract
    if dry_run:
        payload["status"] = "dry_run_contract_passed" if contract["status"] == "passed" else "dry_run_contract_failed"
        return payload
    optix_include = _find_optix_include()
    cuda_root = _find_cuda_root()
    cuda_lib_dir = _find_cuda_lib_dir(cuda_root)
    nvcc = _find_nvcc()
    compiler = _compiler()
    if not all((optix_include, cuda_root, cuda_lib_dir, nvcc, compiler)):
        payload.update({"status": "blocked", "blocked_stage": "toolchain_discovery"})
        return payload
    protocol = v4_goal4694_specialized_hit_overhead_protocol()
    with tempfile.TemporaryDirectory(prefix="rtdl-v4-goal4695-hit-overhead-") as tmp:
        tmp_path = Path(tmp)
        callback_ptx = tmp_path / "callback.ptx"
        ptx_json = tmp_path / "callback.json"
        ptx_proc = _run([sys.executable, str(PTX_PROBE), "--json-out", str(ptx_json), "--ptx-out", str(callback_ptx)], cwd=ROOT)
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
        cpp_path = tmp_path / "v4_goal4695_specialized_hit_overhead_measurement.cpp"
        binary_path = tmp_path / "v4_goal4695_specialized_hit_overhead_measurement"
        cpp_path.write_text(CPP_SOURCE, encoding="utf-8")
        compile_loader = _run([
            str(compiler), "-std=c++17", "-O2", "-I", str(optix_include), "-I", str(cuda_root / "include"),
            str(cpp_path), "-L", str(cuda_lib_dir), "-lcuda", "-ldl", "-o", str(binary_path)
        ], cwd=tmp_path)
        payload["loader_compile"] = {"returncode": compile_loader.returncode, "stdout": compile_loader.stdout.strip()[:4000], "stderr": compile_loader.stderr.strip()[:4000]}
        if compile_loader.returncode != 0:
            payload.update({"status": "blocked", "blocked_stage": "loader_compile"})
            return payload
        env = dict(os.environ)
        env["LD_LIBRARY_PATH"] = os.pathsep.join([str(cuda_lib_dir), "/usr/lib/x86_64-linux-gnu", env.get("LD_LIBRARY_PATH", "")])
        for variant in ("inline", "callback"):
            wrapper_cu = tmp_path / f"{variant}.cu"
            wrapper_ptx = tmp_path / f"{variant}.ptx"
            wrapper_cu.write_text(goal4695_hit_loop_source(variant, symbol_probe.symbol), encoding="utf-8")
            compile_proc = _run([
                str(nvcc), "-ptx", "-std=c++17", "--keep-device-functions", "-I", str(optix_include),
                str(wrapper_cu), "-o", str(wrapper_ptx)
            ], cwd=tmp_path)
            if compile_proc.returncode != 0 or not wrapper_ptx.exists():
                payload["variants"][variant] = {"status": "blocked", "blocked_stage": "wrapper_compile", "stderr": compile_proc.stderr.strip()[:4000]}
                payload.update({"status": "blocked", "blocked_stage": f"{variant}_wrapper_compile"})
                return payload
            run_ptx = wrapper_ptx
            if variant == "callback":
                run_ptx = tmp_path / "callback_combined.ptx"
                run_ptx.write_text(compose_goal4688_combined_ptx(callback_text, wrapper_ptx.read_text(encoding="utf-8")), encoding="utf-8")
            run_proc = _run([
                str(binary_path), str(run_ptx), str(protocol.trace_iterations),
                str(protocol.warmup_launches), str(protocol.measured_launches)
            ], cwd=tmp_path, env=env)
            summary = _summarize(run_proc.stdout, run_proc.stderr, run_proc.returncode)
            summary["status"] = "passed" if run_proc.returncode == 0 and summary["output_matches_expected"] else "blocked"
            payload["variants"][variant] = summary
            if summary["status"] != "passed":
                payload.update({"status": "blocked", "blocked_stage": f"{variant}_run_or_correctness"})
                return payload
    inline_ms = payload["variants"]["inline"]["median_ms"]
    callback_ms = payload["variants"]["callback"]["median_ms"]
    ratio = None if not inline_ms or not callback_ms else float(callback_ms) / float(inline_ms)
    payload["primary_ratio"] = ratio
    payload["classification"] = classify_v4_goal4695_hit_overhead_ratio(ratio)
    payload["status"] = "specialized_hit_overhead_measured_not_support"
    return payload


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# V4 Goal4695 Specialized Hit Callback Overhead Measurement",
        "",
        f"- status: `{payload['status']}`",
        f"- primary ratio: `{payload.get('primary_ratio')}`",
        f"- classification: `{payload.get('classification')}`",
        "",
    ]
    for name, row in payload.get("variants", {}).items():
        lines.extend([
            f"## `{name}`",
            "",
            f"- status: `{row.get('status')}`",
            f"- median ms: `{row.get('median_ms')}`",
            f"- output matches expected: `{row.get('output_matches_expected')}`",
            "",
        ])
    lines.extend(["## Boundary", "", "No Tier-3 support, performance claim, or release is authorized by this measurement alone.", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure V4 Goal4695 specialized hit callback overhead.")
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
    return 0 if payload["status"] in {"dry_run_contract_passed", "specialized_hit_overhead_measured_not_support"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

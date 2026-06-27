from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4687_tier3_wrapper_compile_probe import extract_numba_callback_symbol_from_ptx
from rtdsl.v4_goal4687_tier3_wrapper_compile_probe import specialize_semantic_wrapper_source
from rtdsl.v4_goal4688_tier3_module_link_probe import compose_goal4688_combined_ptx
from rtdsl.v4_goal4688_tier3_module_link_probe import validate_v4_goal4688_tier3_module_link_probe_contract


PTX_PROBE = ROOT / "scripts" / "v4_tier3_numba_ptx_probe.py"
CALLABLE_ENTRY_RE = re.compile(r"__direct_callable__rtdl_tier3_scalar_reduce(?:_[A-Za-z0-9]+)?")


CPP_SOURCE = r"""
#include <cuda.h>
#include <optix.h>
#include <optix_function_table_definition.h>
#include <optix_stubs.h>

#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

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

static std::string find_direct_callable_entry_name(const char* log) {
    std::string text = log ? std::string(log) : std::string();
    std::string prefix = "Properties for entry function \"__direct_callable__rtdl_tier3_scalar_reduce";
    std::size_t start = text.find(prefix);
    if (start == std::string::npos) {
        return "__direct_callable__rtdl_tier3_scalar_reduce";
    }
    start += std::string("Properties for entry function \"").size();
    std::size_t end = text.find("\"", start);
    if (end == std::string::npos || end <= start) {
        return "__direct_callable__rtdl_tier3_scalar_reduce";
    }
    return text.substr(start, end - start);
}

int main(int argc, char** argv) {
    try {
        if (argc != 2 && argc != 3) {
            std::cerr << "usage: v4_goal4688_tier3_module_link_probe <combined.ptx> [callable_entry_name]\n";
            return 64;
        }
        std::string ptx = read_text(argv[1]);
        std::string callable_entry_name_arg = argc == 3 ? std::string(argv[2]) : std::string();
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
            optix_ctx,
            &module_options,
            &pipeline_options,
            ptx.c_str(),
            ptx.size(),
            module_log,
            &module_log_size,
            &module);
#else
        OptixResult module_result = optixModuleCreate(
            optix_ctx,
            &module_options,
            &pipeline_options,
            ptx.c_str(),
            ptx.size(),
            module_log,
            &module_log_size,
            &module);
#endif
        std::cout << "optix_module_create_result=" << static_cast<int>(module_result) << "\n";
        std::cout << "optix_module_create_error=" << optixGetErrorString(module_result) << "\n";
        if (module_log_size > 1 && module_log[0] != '\0') {
            std::cout << "optix_module_log_begin\n" << module_log << "\noptix_module_log_end\n";
        }
        if (module_result != OPTIX_SUCCESS) {
            optixDeviceContextDestroy(optix_ctx);
            return 2;
        }

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
        hit_desc.hitgroup.moduleCH = module;
        hit_desc.hitgroup.entryFunctionNameCH = "__closesthit__rtdl_tier3_probe";

        std::string callable_entry_name = callable_entry_name_arg.empty()
            ? find_direct_callable_entry_name(module_log)
            : callable_entry_name_arg;
        std::cout << "callable_entry_name_used=" << callable_entry_name << "\n";

        OptixProgramGroupDesc call_desc = {};
        call_desc.kind = OPTIX_PROGRAM_GROUP_KIND_CALLABLES;
        call_desc.callables.moduleDC = module;
        call_desc.callables.entryFunctionNameDC = callable_entry_name.c_str();

        std::vector<OptixProgramGroup> groups;
        groups.push_back(create_program_group(optix_ctx, raygen_desc, "raygen_program_group"));
        groups.push_back(create_program_group(optix_ctx, miss_desc, "miss_program_group"));
        groups.push_back(create_program_group(optix_ctx, hit_desc, "hit_program_group"));
        groups.push_back(create_program_group(optix_ctx, call_desc, "callable_program_group"));

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
        if (pipeline_result != OPTIX_SUCCESS) {
            for (auto group : groups) optixProgramGroupDestroy(group);
            optixModuleDestroy(module);
            optixDeviceContextDestroy(optix_ctx);
            return 4;
        }

        optixPipelineDestroy(pipeline);
        for (auto group : groups) optixProgramGroupDestroy(group);
        optixModuleDestroy(module);
        optixDeviceContextDestroy(optix_ctx);
        return 0;
    } catch (const std::exception& exc) {
        std::cerr << exc.what() << "\n";
        return 3;
    }
}
"""


def _base_payload(dry_run: bool) -> dict[str, Any]:
    return {
        "schema": "rtdl.v4.goal4688_tier3_module_link_probe.v1",
        "status": "dry_run" if dry_run else "unknown",
        "dry_run": dry_run,
        "numba_ptx_generated": False,
        "symbol_probe": None,
        "wrapper_compile_succeeded": False,
        "combined_ptx_generated": False,
        "optix_module_link_attempted": False,
        "optix_module_link_succeeded": None,
        "program_group_create_attempted": False,
        "program_group_create_succeeded": None,
        "pipeline_create_attempted": False,
        "pipeline_create_succeeded": None,
        "pipeline_launch_attempted": False,
        "pod_authorized": False,
        "tier3_public_support_authorized": False,
        "raw_optix_callback_authorized": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "app_identity_kernel_authorized": False,
    }


def _first_existing_path(candidates: list[Path]) -> Path | None:
    for path in candidates:
        if path.exists():
            return path
    return None


def _find_optix_include() -> Path | None:
    env = os.environ.get("RTDL_OPTIX_INCLUDE_DIR") or os.environ.get("OPTIX_INCLUDE_DIR")
    if env:
        path = Path(env)
        if (path / "optix.h").exists() and (path / "optix_stubs.h").exists():
            return path
    return _first_existing_path(
        [
            Path("/root/vendor/optix-dev/include"),
            Path("/usr/local/optix/include"),
            Path("/opt/optix/include"),
        ]
    )


def _find_cuda_root() -> Path | None:
    for name in (os.environ.get("CUDA_HOME"), os.environ.get("CUDA_PATH"), "/usr/local/cuda", "/usr/local/cuda-12"):
        if name and (Path(name) / "include" / "cuda.h").exists():
            return Path(name)
    return None


def _find_cuda_lib_dir(cuda_root: Path | None) -> Path | None:
    candidates: list[Path] = []
    if cuda_root is not None:
        candidates.extend([cuda_root / "lib64", cuda_root / "targets" / "x86_64-linux" / "lib"])
    candidates.extend([Path("/usr/lib/x86_64-linux-gnu"), Path("/usr/local/cuda/lib64")])
    for path in candidates:
        if (path / "libcuda.so").exists() or (path / "libcuda.so.1").exists():
            return path
    return None


def _find_nvcc() -> str | None:
    for name in (os.environ.get("RTDL_NVCC"), os.environ.get("NVCC"), "/usr/local/cuda/bin/nvcc", "nvcc"):
        if name and shutil.which(name):
            return str(shutil.which(name))
        if name and Path(name).exists():
            return str(Path(name))
    return None


def _compiler() -> str | None:
    for name in [os.environ.get("CXX"), "g++", "c++"]:
        if name and shutil.which(name):
            return name
    return None


def _run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _run_probe(dry_run: bool) -> dict[str, Any]:
    payload = _base_payload(dry_run)
    contract = validate_v4_goal4688_tier3_module_link_probe_contract()
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

    with tempfile.TemporaryDirectory(prefix="rtdl-v4-goal4688-module-link-") as tmp:
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
        payload["numba_ptx_generated"] = True
        callback_text = callback_ptx.read_text(encoding="utf-8")
        symbol_probe = extract_numba_callback_symbol_from_ptx(callback_text)
        payload["symbol_probe"] = symbol_probe.as_dict()
        if symbol_probe.status != "symbol_extracted" or not symbol_probe.symbol:
            payload.update({"status": "blocked", "blocked_stage": "callback_symbol_extraction"})
            return payload

        wrapper_cu = tmp_path / "tier3_wrapper.cu"
        wrapper_ptx = tmp_path / "tier3_wrapper.ptx"
        wrapper_cu.write_text(specialize_semantic_wrapper_source(symbol_probe.symbol) + "\n", encoding="utf-8")
        wrapper_compile_args = [
            str(nvcc),
            "-ptx",
            "-std=c++17",
            "--keep-device-functions",
            "-I",
            str(optix_include),
            str(wrapper_cu),
            "-o",
            str(wrapper_ptx),
        ]
        payload["wrapper_compile_args"] = wrapper_compile_args
        compile_proc = _run(wrapper_compile_args, cwd=tmp_path)
        payload["wrapper_compile"] = {
            "returncode": compile_proc.returncode,
            "stdout": compile_proc.stdout.strip()[:4000],
            "stderr": compile_proc.stderr.strip()[:4000],
        }
        if compile_proc.returncode != 0 or not wrapper_ptx.exists():
            payload.update({"status": "blocked", "blocked_stage": "semantic_wrapper_compile"})
            return payload
        payload["wrapper_compile_succeeded"] = True
        wrapper_text = wrapper_ptx.read_text(encoding="utf-8")
        callable_names = sorted(set(CALLABLE_ENTRY_RE.findall(wrapper_text)), key=len, reverse=True)
        payload["callable_entry_candidates"] = callable_names
        callable_entry_name = callable_names[0] if callable_names else "__direct_callable__rtdl_tier3_scalar_reduce"
        payload["callable_entry_name_selected"] = callable_entry_name

        combined_ptx = tmp_path / "combined.ptx"
        combined_ptx.write_text(
            compose_goal4688_combined_ptx(callback_text, wrapper_text),
            encoding="utf-8",
        )
        payload["combined_ptx_generated"] = True
        payload["combined_ptx_length"] = combined_ptx.stat().st_size

        cpp_path = tmp_path / "v4_goal4688_tier3_module_link_probe.cpp"
        binary_path = tmp_path / "v4_goal4688_tier3_module_link_probe"
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
        payload["optix_module_link_attempted"] = True
        payload["program_group_create_attempted"] = True
        payload["pipeline_create_attempted"] = True
        run_proc = _run([str(binary_path), str(combined_ptx), callable_entry_name], cwd=tmp_path, env=env)
        payload["module_probe"] = {
            "returncode": run_proc.returncode,
            "stdout": run_proc.stdout.strip()[:12000],
            "stderr": run_proc.stderr.strip()[:4000],
        }
        stdout = run_proc.stdout
        payload["optix_module_link_succeeded"] = "optix_module_create_result=0" in stdout
        payload["program_group_create_succeeded"] = (
            "raygen_program_group_result=0" in stdout
            and "miss_program_group_result=0" in stdout
            and "hit_program_group_result=0" in stdout
            and "callable_program_group_result=0" in stdout
        )
        payload["pipeline_create_succeeded"] = "pipeline_create_result=0" in stdout
        if run_proc.returncode == 0:
            payload.update({"status": "semantic_module_pipeline_created_no_launch", "next_stage": "Goal4689 minimal launch probe"})
        elif payload["optix_module_link_succeeded"] is False:
            payload.update({"status": "blocked", "blocked_stage": "optix_module_create"})
        elif payload["program_group_create_succeeded"] is False:
            payload.update({"status": "blocked", "blocked_stage": "program_group_create"})
        elif payload["pipeline_create_succeeded"] is False:
            payload.update({"status": "blocked", "blocked_stage": "pipeline_create"})
        else:
            payload.update({"status": "blocked", "blocked_stage": "unknown_module_probe"})
    return payload


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# V4 Goal4688 Tier-3 Module-Link Probe",
        "",
        "Status: module/program-group/pipeline probe only, not Tier-3 support and not release authorization",
        "",
        f"- status: `{payload['status']}`",
        f"- Numba PTX generated: `{payload['numba_ptx_generated']}`",
        f"- wrapper compile succeeded: `{payload['wrapper_compile_succeeded']}`",
        f"- combined PTX generated: `{payload['combined_ptx_generated']}`",
        f"- OptiX module link attempted: `{payload['optix_module_link_attempted']}`",
        f"- OptiX module link succeeded: `{payload['optix_module_link_succeeded']}`",
        f"- program group create succeeded: `{payload['program_group_create_succeeded']}`",
        f"- pipeline create succeeded: `{payload['pipeline_create_succeeded']}`",
        f"- pipeline launch attempted: `{payload['pipeline_launch_attempted']}`",
        "",
        "## Boundary",
        "",
        "This probe does not measure overhead, does not validate callback correctness, and does not authorize Tier-3 public support.",
        "",
    ]
    if payload.get("status") == "blocked":
        lines.extend(["## Blocked Stage", "", f"- blocked stage: `{payload.get('blocked_stage')}`", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe V4 Goal4688 Tier-3 semantic wrapper OptiX module-link path.")
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
    return 0 if payload["status"] in {"dry_run_contract_passed", "semantic_module_pipeline_created_no_launch"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

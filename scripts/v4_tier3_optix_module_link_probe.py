from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PTX_PROBE = ROOT / "scripts" / "v4_tier3_numba_ptx_probe.py"


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

static std::string read_text(const char* path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) {
        throw std::runtime_error(std::string("failed to open PTX file: ") + path);
    }
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

int main(int argc, char** argv) {
    try {
        if (argc != 2) {
            std::cerr << "usage: v4_tier3_optix_module_link_probe <callback.ptx>\n";
            return 64;
        }
        std::string ptx = read_text(argv[1]);
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

        char log[16384] = {};
        size_t log_size = sizeof(log);
        OptixModule module = nullptr;
        OptixResult module_result = optixModuleCreate(
            optix_ctx,
            &module_options,
            &pipeline_options,
            ptx.c_str(),
            ptx.size(),
            log,
            &log_size,
            &module);

        std::cout << "optix_module_create_result=" << static_cast<int>(module_result) << "\n";
        std::cout << "optix_module_create_error=" << optixGetErrorString(module_result) << "\n";
        std::cout << "optix_module_log_size=" << log_size << "\n";
        if (log_size > 1 && log[0] != '\0') {
            std::cout << "optix_module_log_begin\n" << log << "\noptix_module_log_end\n";
        }

        if (module_result != OPTIX_SUCCESS) {
            if (module) optixModuleDestroy(module);
            optixDeviceContextDestroy(optix_ctx);
            return 2;
        }

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
        "schema": "rtdl.v4.tier3_optix_module_link_probe.v1",
        "status": "dry_run" if dry_run else "unknown",
        "probe": "numba_ptx_to_optix_module_create",
        "tier": "tier3_spike_only_not_v4_0_release_surface",
        "ptx_generated": False,
        "optix_module_link_attempted": False,
        "optix_module_link_succeeded": None,
        "program_group_create_attempted": False,
        "pipeline_launch_attempted": False,
        "release_claim_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "raw_optix_callback_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
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
    env = os.environ.get("CUDA_HOME") or os.environ.get("CUDA_PATH")
    candidates: list[Path] = []
    if env:
        candidates.append(Path(env))
    candidates.extend([Path("/usr/local/cuda"), Path("/usr/local/cuda-12.8"), Path("/usr/local/cuda-12")])
    for path in candidates:
        if (path / "include" / "cuda.h").exists():
            return path
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


def _compiler() -> str | None:
    for name in [os.environ.get("CXX"), "g++", "c++"]:
        if name and shutil.which(name):
            return name
    return None


def _run_command(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
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
    if dry_run:
        payload["reason"] = "dry_run_does_not_compile_numba_ptx_or_touch_optix"
        return payload

    optix_include = _find_optix_include()
    cuda_root = _find_cuda_root()
    cuda_lib_dir = _find_cuda_lib_dir(cuda_root)
    compiler = _compiler()
    payload["toolchain"] = {
        "compiler": compiler,
        "optix_include": str(optix_include) if optix_include else None,
        "cuda_root": str(cuda_root) if cuda_root else None,
        "cuda_lib_dir": str(cuda_lib_dir) if cuda_lib_dir else None,
    }
    missing = [
        name
        for name, value in {
            "compiler": compiler,
            "optix_include": optix_include,
            "cuda_root": cuda_root,
            "cuda_lib_dir": cuda_lib_dir,
        }.items()
        if value is None
    ]
    if missing:
        payload.update({"status": "blocked", "blocked_stage": "toolchain_discovery", "missing": missing})
        return payload

    with tempfile.TemporaryDirectory(prefix="rtdl-v4-tier3-optix-module-") as tmp:
        tmp_path = Path(tmp)
        ptx_path = tmp_path / "numba_scalar_callback.ptx"
        ptx_json_path = tmp_path / "numba_ptx.json"
        ptx_proc = _run_command(
            [
                sys.executable,
                str(PTX_PROBE),
                "--json-out",
                str(ptx_json_path),
                "--ptx-out",
                str(ptx_path),
            ],
            cwd=ROOT,
        )
        payload["ptx_probe_returncode"] = ptx_proc.returncode
        payload["ptx_probe_stderr"] = ptx_proc.stderr.strip()
        if ptx_json_path.exists():
            payload["ptx_probe_payload"] = json.loads(ptx_json_path.read_text(encoding="utf-8"))
        if ptx_proc.returncode != 0 or not ptx_path.exists():
            payload.update(
                {
                    "status": "blocked",
                    "blocked_stage": "numba_ptx_generation",
                    "ptx_probe_stdout": ptx_proc.stdout.strip()[:4000],
                }
            )
            return payload
        payload["ptx_generated"] = True
        payload["ptx_length"] = ptx_path.stat().st_size

        cpp_path = tmp_path / "v4_tier3_optix_module_link_probe.cpp"
        binary_path = tmp_path / "v4_tier3_optix_module_link_probe"
        cpp_path.write_text(CPP_SOURCE, encoding="utf-8")
        compile_command = [
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
        ]
        compile_proc = _run_command(compile_command, cwd=tmp_path)
        payload["compile"] = {
            "command": compile_command,
            "returncode": compile_proc.returncode,
            "stdout": compile_proc.stdout.strip()[:4000],
            "stderr": compile_proc.stderr.strip()[:4000],
        }
        if compile_proc.returncode != 0:
            payload.update({"status": "blocked", "blocked_stage": "cpp_probe_compile"})
            return payload

        env = dict(os.environ)
        lib_parts = [str(cuda_lib_dir), "/usr/lib/x86_64-linux-gnu"]
        existing_ld = env.get("LD_LIBRARY_PATH")
        if existing_ld:
            lib_parts.append(existing_ld)
        env["LD_LIBRARY_PATH"] = os.pathsep.join(lib_parts)
        payload["optix_module_link_attempted"] = True
        run_proc = _run_command([str(binary_path), str(ptx_path)], cwd=tmp_path, env=env)
        payload["module_probe"] = {
            "returncode": run_proc.returncode,
            "stdout": run_proc.stdout.strip()[:8000],
            "stderr": run_proc.stderr.strip()[:4000],
        }
        if run_proc.returncode == 0:
            payload.update(
                {
                    "status": "optix_module_created",
                    "optix_module_link_succeeded": True,
                    "next_stage": "direct_callable_or_module_composition_spike",
                }
            )
        else:
            payload.update(
                {
                    "status": "blocked",
                    "blocked_stage": "optix_module_create",
                    "optix_module_link_succeeded": False,
                }
            )
    return payload


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# V4 Tier-3 OptiX Module-Link Probe",
        "",
        "Status: spike evidence only, not Tier-3 support and not a release authorization",
        "",
        f"- status: `{payload['status']}`",
        f"- PTX generated: `{payload['ptx_generated']}`",
        f"- OptiX module link attempted: `{payload['optix_module_link_attempted']}`",
        f"- OptiX module link succeeded: `{payload['optix_module_link_succeeded']}`",
        f"- program group create attempted: `{payload['program_group_create_attempted']}`",
        f"- pipeline launch attempted: `{payload['pipeline_launch_attempted']}`",
        "",
        "## Boundary",
        "",
        "This probe checks only whether Numba-generated scalar callback PTX is accepted by `optixModuleCreate`. It does not prove OptiX callable wiring, program group creation, traversal integration, callback overhead, or public Tier-3 support.",
        "",
        "## Non-Authorization",
        "",
        "This probe does not authorize V4 release, Tier-3 callback/PTX support claims, raw OptiX callbacks, broad speedup wording, or app-specific native kernels.",
        "",
    ]
    if payload.get("status") == "blocked":
        lines.extend(
            [
                "## Blocked Stage",
                "",
                f"- blocked stage: `{payload.get('blocked_stage')}`",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe whether Numba PTX can be accepted by OptiX module creation.")
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
    return 0 if payload["status"] in {"dry_run", "optix_module_created"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

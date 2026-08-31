#!/usr/bin/env python3
"""Run one non-formal two-application phase diagnosis on the Home GPU.

This deliberately does not weaken or reuse the Goal5809 A4500 execution gate.
It reuses the already-tested Goal5809 arm helpers, exact target admission and
oracles, but emits only Home/Pascal engineering evidence.  Its clock readings
are descriptive diagnostics and are never registered paper measurements.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Mapping

from scripts import goal5809_pyoptix_two_app_pilot as py_worker
from scripts import goal5809_runtime_session_two_app_pilot as rtdl_worker


SCHEMA = "rtdl.goal5810.home_two_app_phase_diagnostic.v1"
STATUS = "COMPLETE__HOME_PASCAL_NONFORMAL_TWO_APP_PHASE_DIAGNOSTIC"
TASKS = ("relation", "triangle")


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def _file_row(path: Path) -> dict[str, object]:
    resolved = path.resolve(strict=True)
    return {
        "path": str(resolved),
        "bytes": resolved.stat().st_size,
        "sha256": _sha(resolved),
    }


def _module_row(module: Any) -> dict[str, object]:
    path = Path(str(module.__file__)).resolve(strict=True)
    return _file_row(path)


def _cuda_identity() -> dict[str, object]:
    cuda = ctypes.CDLL("libcuda.so.1")
    cuda.cuInit.argtypes = [ctypes.c_uint]
    cuda.cuInit.restype = ctypes.c_int
    if int(cuda.cuInit(0)) != 0:
        raise RuntimeError("Goal5810 cuInit failed")
    device = ctypes.c_int()
    cuda.cuDeviceGet.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
    cuda.cuDeviceGet.restype = ctypes.c_int
    if int(cuda.cuDeviceGet(ctypes.byref(device), 0)) != 0:
        raise RuntimeError("Goal5810 cuDeviceGet failed")
    major = ctypes.c_int()
    minor = ctypes.c_int()
    cuda.cuDeviceComputeCapability.argtypes = [
        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
        ctypes.c_int,
    ]
    cuda.cuDeviceComputeCapability.restype = ctypes.c_int
    if int(cuda.cuDeviceComputeCapability(
            ctypes.byref(major), ctypes.byref(minor), device.value)) != 0:
        raise RuntimeError("Goal5810 cuDeviceComputeCapability failed")
    name_buffer = ctypes.create_string_buffer(256)
    cuda.cuDeviceGetName.argtypes = [
        ctypes.c_char_p, ctypes.c_int, ctypes.c_int,
    ]
    cuda.cuDeviceGetName.restype = ctypes.c_int
    if int(cuda.cuDeviceGetName(name_buffer, 256, device.value)) != 0:
        raise RuntimeError("Goal5810 cuDeviceGetName failed")
    result = {
        "device_ordinal": device.value,
        "gpu_name": name_buffer.value.decode("utf-8", errors="strict"),
        "compute_capability": [major.value, minor.value],
    }
    if result["gpu_name"] != "NVIDIA GeForce GTX 1070" \
            or result["compute_capability"] != [6, 1]:
        raise RuntimeError({"Goal5810_wrong_home_gpu": result})
    return result


def _scope(arm: str) -> dict[str, object]:
    return {
        "arm": arm,
        "diagnostic_only": True,
        "home_pascal_only": True,
        "rt_core_evidence": False,
        "formal_evidence": False,
        "paper_evidence": False,
        "claim_authorized": False,
        "threshold_or_pass_fail_gate_present": False,
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
        "descriptive_perf_counter_phase_durations_present": True,
        "may_replace_goal5806_goal5807_or_goal5809": False,
    }


def _isolate_caches(root: Path) -> dict[str, str]:
    resolved = root.absolute()
    if resolved.exists():
        raise RuntimeError("Goal5810 cache root already exists")
    resolved.mkdir(parents=True)
    paths = {
        "CUDA_CACHE_PATH": resolved / "cuda",
        "CUPY_CACHE_DIR": resolved / "cupy",
        "NUMBA_CACHE_DIR": resolved / "numba",
        "OPTIX_CACHE_PATH": resolved / "optix",
        "TMPDIR": resolved / "tmp",
        "XDG_CACHE_HOME": resolved / "xdg",
    }
    for path in paths.values():
        path.mkdir()
    values = {
        "CUDA_CACHE_DISABLE": "1",
        "OPTIX_CACHE_ENABLED": "0",
        "OPTIX_CACHE_MAXSIZE": "0",
        "RTDL_DISABLE_CUBIN_CACHE": "1",
        "RTDL_OPTIX_DISABLE_CUBIN_CACHE": "1",
        **{key: str(path) for key, path in paths.items()},
    }
    for key in (
            "RTDL_DUMP_PTX_DIR", "RTDL_GOAL5807_PROFILE_NATIVE",
            "RTDL_OPTIX_LOG_LEVEL"):
        os.environ.pop(key, None)
    os.environ.update(values)
    return values


def _run_rtdl(
    *, target_path: Path, target_sha256: str, first_task: str,
) -> dict[str, Any]:
    ledger = rtdl_worker._PhaseLedger(time.perf_counter_ns)
    with ledger.phase("input_admission"):
        admitted = rtdl_worker._admit_target(
            target_path, expected_file_sha256=target_sha256)
        second_task = "triangle" if first_task == "relation" else "relation"

    with ledger.phase("runtime_preload"):
        workload_module, runtime, implementation, preload_receipt, bulk_input = \
            rtdl_worker._preload_runtime()
        numpy = importlib.import_module("numpy")

    with ledger.phase("workload_materialization"):
        workloads = {
            "relation": workload_module.relation_workload(),
            "triangle": workload_module.triangle_workload(),
        }

    loaded: dict[str, Any] = {}
    for task in TASKS:
        with ledger.phase(f"load_{task}"):
            loaded[task] = rtdl_worker._load_application(
                task_key=task, admitted=admitted, runtime=runtime)

    session = None
    prepared: list[Any] = []
    applications: dict[str, Any] = {}
    prepare_breakdown: dict[str, dict[str, object]] = {}
    primary_error: BaseException | None = None
    close_error: BaseException | None = None
    try:
        with ledger.phase("first_session_admission"):
            native = Path(admitted["target"]["files"]["native_library"]["path"])
            session = loaded[first_task].open_runtime_session(native)
        for ordinal, task in enumerate((first_task, second_task)):
            label = "first_app" if ordinal == 0 else "second_app"
            with ledger.phase(f"{label}_prepare"):
                prepare_start = time.perf_counter_ns()
                static, batch, oracle, packing = \
                    rtdl_worker._build_public_inputs(
                        task_key=task, workload=workloads[task],
                        runtime=runtime, numpy=numpy, bulk_input=bulk_input)
                public_inputs_end = time.perf_counter_ns()
                owner = session.prepare(loaded[task], static)
                session_prepare_end = time.perf_counter_ns()
                prepare_breakdown[label] = {
                    "task": task,
                    "public_input_construction_ns": (
                        public_inputs_end - prepare_start),
                    "runtime_session_prepare_ns": (
                        session_prepare_end - public_inputs_end),
                    "accounted_total_ns": (
                        session_prepare_end - prepare_start),
                    "clock": "time.perf_counter_ns",
                    "descriptive_only": True,
                    "registered_performance_timing_count": 0,
                }
                prepared.append(owner)
            with ledger.phase(f"{label}_first_exact_execute"):
                applications[task] = rtdl_worker._execute_once(
                    task_key=task, prepared=owner, batch=batch, oracle=oracle,
                    packing_receipt=packing, loaded=loaded[task])
    except BaseException as error:  # preserve primary plus cleanup failure
        primary_error = error
    finally:
        with ledger.phase("close"):
            try:
                rtdl_worker._close_all(prepared, session)
            except BaseException as error:
                close_error = error
    if primary_error is not None:
        if close_error is not None:
            raise RuntimeError({
                "primary_error": repr(primary_error),
                "close_error": repr(close_error),
            }) from primary_error
        raise primary_error
    if close_error is not None:
        raise close_error
    if session is None or not session.closed:
        raise RuntimeError("Goal5810 RTDL runtime session did not close")

    return {
        "scope": _scope("RTDL_SHARED_RUNTIME_SESSION"),
        "app_order": [first_task, second_task],
        "phase_times_absolute": ledger.finish(),
        "applications": applications,
        "prepare_breakdown": prepare_breakdown,
        "lifecycle": {
            "loaded_executable_count": 2,
            "runtime_session_count": 1,
            "provider_admission_count": 1,
            "prepare_call_count": 2,
            "execute_call_count": 2,
            "one_provider_shared_across_both_apps": True,
            "all_owners_and_session_closed": True,
        },
        "runtime": {
            "preload_receipt": rtdl_worker._plain(preload_receipt),
            "runtime_module": _module_row(runtime),
            "implementation_module": _module_row(implementation),
            "workload_module": _module_row(workload_module),
            "bulk_input_module": _module_row(bulk_input),
        },
    }


def _run_pyoptix(
    *, target_path: Path, target_sha256: str, first_task: str,
) -> dict[str, Any]:
    ledger = rtdl_worker._PhaseLedger(
        time.perf_counter_ns, required_phases=py_worker.REQUIRED_PHASES)
    with ledger.phase("input_admission"):
        admitted = rtdl_worker._admit_target(
            target_path, expected_file_sha256=target_sha256)
        second_task = "triangle" if first_task == "relation" else "relation"

    with ledger.phase("runtime_preload"):
        workload_module, arm, baseline, preload_receipt, bulk_input = \
            py_worker._preload_runtime()

    with ledger.phase("workload_materialization"):
        workloads = {
            "relation": workload_module.relation_workload(),
            "triangle": workload_module.triangle_workload(),
        }

    adapters: dict[str, Any] = {}
    shared_context = None
    applications: dict[str, Any] = {}
    primary_error: BaseException | None = None
    close_error: BaseException | None = None
    try:
        for task in TASKS:
            with ledger.phase(f"load_{task}"):
                adapters[task] = py_worker._load_application(
                    task_key=task, target=admitted["target"],
                    workload=workloads[task], arm=arm, baseline=baseline,
                    preload_receipt=preload_receipt)
        with ledger.phase("first_session_admission"):
            shared_context, _logger = py_worker._admit_shared_context(
                arm=arm, baseline=baseline)
        for ordinal, task in enumerate((first_task, second_task)):
            label = "first_app" if ordinal == 0 else "second_app"
            with ledger.phase(f"{label}_prepare"):
                py_worker._prepare_once(
                    task_key=task, adapter=adapters[task], arm=arm,
                    bulk_input=bulk_input, shared_context=shared_context)
            with ledger.phase(f"{label}_first_exact_execute"):
                applications[task] = py_worker._execute_once(
                    task_key=task, adapter=adapters[task],
                    workload=workloads[task])
    except BaseException as error:
        primary_error = error
    finally:
        with ledger.phase("close"):
            try:
                py_worker._close_all([
                    adapters[task] for task in (first_task, second_task)
                    if task in adapters
                ])
            except BaseException as error:
                close_error = error
    if primary_error is not None:
        if close_error is not None:
            raise RuntimeError({
                "primary_error": repr(primary_error),
                "close_error": repr(close_error),
            }) from primary_error
        raise primary_error
    if close_error is not None:
        raise close_error
    if shared_context is None \
            or any(adapter.context is not shared_context
                   for adapter in adapters.values()) \
            or any(adapter.owner is not None for adapter in adapters.values()):
        raise RuntimeError("Goal5810 PyOptiX shared-context lifecycle differs")

    return {
        "scope": _scope("PYOPTIX_SHARED_DEVICE_CONTEXT"),
        "app_order": [first_task, second_task],
        "phase_times_absolute": ledger.finish(),
        "applications": applications,
        "lifecycle": {
            "loaded_application_count": 2,
            "shared_device_context_count": 1,
            "prepare_call_count": 2,
            "execute_call_count": 2,
            "one_device_context_shared_across_both_apps": True,
            "all_application_owners_closed": True,
        },
        "runtime": {
            "preload_receipt": rtdl_worker._plain(preload_receipt),
            "baseline_module": _module_row(baseline),
            "arm_module": _module_row(arm),
            "workload_module": _module_row(workload_module),
            "bulk_input_module": _module_row(bulk_input),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=("rtdl", "pyoptix"), required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--expected-target-manifest-sha256", required=True)
    parser.add_argument("--first-app", choices=TASKS, required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument(
        "--enable-native-profile", action="store_true",
        help=(
            "enable the existing stderr-only Goal5807 native phase channel; "
            "diagnostic only and never a registered timing"),
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise RuntimeError("Goal5810 output already exists")
    cache_environment = _isolate_caches(args.cache_root)
    if args.enable_native_profile:
        # Cache isolation clears inherited diagnostic knobs.  Re-enable this
        # one explicitly so it cannot arrive accidentally from the caller.
        os.environ["RTDL_GOAL5807_PROFILE_NATIVE"] = "1"

    arm_result = (
        _run_rtdl(
            target_path=args.target_manifest,
            target_sha256=args.expected_target_manifest_sha256,
            first_task=args.first_app)
        if args.arm == "rtdl" else
        _run_pyoptix(
            target_path=args.target_manifest,
            target_sha256=args.expected_target_manifest_sha256,
            first_task=args.first_app)
    )
    cuda_identity = _cuda_identity()
    body = {
        "schema": SCHEMA,
        "status": STATUS,
        "process_pid": os.getpid(),
        "python": {
            "executable": str(Path(sys.executable).absolute()),
            "version": sys.version,
        },
        "cuda": cuda_identity,
        "loader_environment": {
            "LD_LIBRARY_PATH": os.environ.get("LD_LIBRARY_PATH"),
            "LD_PRELOAD": os.environ.get("LD_PRELOAD"),
        },
        "isolated_cache_environment": cache_environment,
        "native_profile": {
            "enabled": bool(args.enable_native_profile),
            "channel": (
                "STDERR_ONLY__RTDL_GOAL5807_NATIVE_PHASE"
                if args.enable_native_profile else "DISABLED"),
            "registered_performance_timing_count": 0,
            "paper_evidence": False,
        },
        "target_manifest": _file_row(args.target_manifest),
        "worker_source": _file_row(Path(__file__)),
        **arm_result,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }
    result = {**body, "diagnostic_sha256": hashlib.sha256(
        _canonical(body)).hexdigest()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as handle:
        handle.write(_canonical(result) + b"\n")
    print(json.dumps({
        "status": STATUS,
        "arm": args.arm,
        "first_app": args.first_app,
        "output": str(args.output.resolve(strict=True)),
        "diagnostic_sha256": result["diagnostic_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

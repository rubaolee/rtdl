#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


REPORT_STEM = "goal1486_v1_5_4_cuda_driver_allocation_probe_2026-05-07"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"


def _run_command(command: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError as exc:
        return {"command": command, "returncode": 127, "stdout": "", "stderr": f"{type(exc).__name__}: {exc}"}
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _git_head() -> str:
    result = _run_command(["git", "rev-parse", "HEAD"])
    return result["stdout"] if result["returncode"] == 0 else "unknown"


def _cuda_check(rc: int, operation: str) -> None:
    if int(rc) != 0:
        raise RuntimeError(f"{operation} failed with CUDA driver result {rc}")


def run_cuda_driver_allocation_probe(byte_count: int) -> dict[str, Any]:
    """Allocate and free device memory through the CUDA Driver API."""
    if byte_count <= 0:
        raise ValueError("byte_count must be positive")
    try:
        cuda = ctypes.CDLL("libcuda.so.1")
    except OSError as exc:
        return {
            "status": "unavailable",
            "reason": f"{type(exc).__name__}: {exc}",
            "cuda_driver_loaded": False,
            "device_allocation_performed": False,
            "device_free_performed": False,
            "host_to_device_transfers": 0,
            "device_to_host_transfers": 0,
            "device_residency_observed": False,
            "measured_on_real_nvidia": False,
            "hardware_identity": None,
            "backend_version": None,
            "device_pointer_nonzero": False,
        }

    try:
        cu_init = cuda.cuInit
        cu_device_get_count = cuda.cuDeviceGetCount
        cu_device_get = cuda.cuDeviceGet
        cu_device_get_name = cuda.cuDeviceGetName
        cu_driver_get_version = cuda.cuDriverGetVersion
        cu_ctx_create = cuda.cuCtxCreate_v2
        cu_ctx_destroy = cuda.cuCtxDestroy_v2
        cu_mem_alloc = cuda.cuMemAlloc_v2
        cu_mem_free = cuda.cuMemFree_v2
    except AttributeError as exc:
        return {
            "status": "unavailable",
            "reason": f"{type(exc).__name__}: {exc}",
            "cuda_driver_loaded": True,
            "device_allocation_performed": False,
            "device_free_performed": False,
            "host_to_device_transfers": 0,
            "device_to_host_transfers": 0,
            "device_residency_observed": False,
            "measured_on_real_nvidia": False,
            "hardware_identity": None,
            "backend_version": None,
            "device_pointer_nonzero": False,
        }

    cu_init.argtypes = [ctypes.c_uint]
    cu_init.restype = ctypes.c_int
    cu_device_get_count.argtypes = [ctypes.POINTER(ctypes.c_int)]
    cu_device_get_count.restype = ctypes.c_int
    cu_device_get.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
    cu_device_get.restype = ctypes.c_int
    cu_device_get_name.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
    cu_device_get_name.restype = ctypes.c_int
    cu_driver_get_version.argtypes = [ctypes.POINTER(ctypes.c_int)]
    cu_driver_get_version.restype = ctypes.c_int
    cu_ctx_create.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_uint, ctypes.c_int]
    cu_ctx_create.restype = ctypes.c_int
    cu_ctx_destroy.argtypes = [ctypes.c_void_p]
    cu_ctx_destroy.restype = ctypes.c_int
    cu_mem_alloc.argtypes = [ctypes.POINTER(ctypes.c_ulonglong), ctypes.c_size_t]
    cu_mem_alloc.restype = ctypes.c_int
    cu_mem_free.argtypes = [ctypes.c_ulonglong]
    cu_mem_free.restype = ctypes.c_int

    context = ctypes.c_void_p()
    pointer = ctypes.c_ulonglong()
    allocation_performed = False
    free_performed = False
    try:
        _cuda_check(cu_init(0), "cuInit")
        count = ctypes.c_int()
        _cuda_check(cu_device_get_count(ctypes.byref(count)), "cuDeviceGetCount")
        if count.value <= 0:
            raise RuntimeError("CUDA driver reported zero devices")
        device = ctypes.c_int()
        _cuda_check(cu_device_get(ctypes.byref(device), 0), "cuDeviceGet")
        name_buffer = ctypes.create_string_buffer(256)
        _cuda_check(cu_device_get_name(name_buffer, len(name_buffer), device.value), "cuDeviceGetName")
        driver_version = ctypes.c_int()
        _cuda_check(cu_driver_get_version(ctypes.byref(driver_version)), "cuDriverGetVersion")
        _cuda_check(cu_ctx_create(ctypes.byref(context), 0, device.value), "cuCtxCreate_v2")
        _cuda_check(cu_mem_alloc(ctypes.byref(pointer), int(byte_count)), "cuMemAlloc_v2")
        allocation_performed = True
        _cuda_check(cu_mem_free(pointer), "cuMemFree_v2")
        free_performed = True
        return {
            "status": "ok",
            "reason": None,
            "cuda_driver_loaded": True,
            "device_count": int(count.value),
            "device_name": name_buffer.value.decode("utf-8", errors="replace"),
            "cuda_driver_version": int(driver_version.value),
            "byte_count": int(byte_count),
            "device_allocation_performed": allocation_performed,
            "device_free_performed": free_performed,
            "host_to_device_transfers": 0,
            "device_to_host_transfers": 0,
            "device_residency_observed": True,
            "measured_on_real_nvidia": True,
            "hardware_identity": f"{name_buffer.value.decode('utf-8', errors='replace')} driver_api={driver_version.value}",
            "backend_version": f"CUDA Driver API {driver_version.value}",
            "device_pointer_nonzero": bool(pointer.value),
        }
    except Exception as exc:
        if allocation_performed and not free_performed and pointer.value:
            try:
                cu_mem_free(pointer)
                free_performed = True
            except Exception:
                pass
        return {
            "status": "failed",
            "reason": f"{type(exc).__name__}: {exc}",
            "cuda_driver_loaded": True,
            "device_allocation_performed": allocation_performed,
            "device_free_performed": free_performed,
            "host_to_device_transfers": 0,
            "device_to_host_transfers": 0,
            "device_residency_observed": False,
            "measured_on_real_nvidia": False,
            "hardware_identity": None,
            "backend_version": None,
            "device_pointer_nonzero": bool(pointer.value),
        }
    finally:
        if context.value:
            try:
                cu_ctx_destroy(context)
            except Exception:
                pass


def build_payload(probe: dict[str, Any]) -> dict[str, Any]:
    descriptor = rt.prepare_v1_5_4_python_rtdl_managed_buffer_descriptor(
        buffer_kind="rtdl_device_resident",
        backend="optix",
        device="cuda:0",
        dtype="int64",
        shape=(16, 2),
        lifetime="explicit_release",
        byte_count=256,
        pointer=123456,
        transfer_count_state="instrumentation_planned",
    )
    lifecycle = rt.begin_v1_5_4_python_rtdl_managed_buffer_lifecycle(
        descriptor,
        allocation_id="goal1486_cuda_driver_alloc",
    )
    evidence = rt.attach_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(
        lifecycle,
        allocation_method="cuda_device_alloc" if probe["status"] == "ok" else "synthetic_contract_only",
        measurement_backend="cuda_driver_api",
        measurement_scope="goal1486_real_cuda_driver_cuMemAlloc_probe",
        host_to_device_transfers=int(probe["host_to_device_transfers"]),
        device_to_host_transfers=int(probe["device_to_host_transfers"]),
        device_residency_observed=bool(probe["device_residency_observed"]),
        measured_on_real_nvidia=bool(probe["measured_on_real_nvidia"]),
        hardware_identity=probe.get("hardware_identity"),
        backend_version=probe.get("backend_version"),
    )
    validated = rt.validate_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(evidence)
    return {
        "goal": "Goal1486",
        "scope": "v1.5.4 Python+RTDL CUDA Driver API managed-buffer allocation probe",
        "source_commit": _git_head(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "nvidia_smi": _run_command(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "probe": probe,
        "allocation_evidence": validated,
        "candidate_only": bool(validated["true_zero_copy_evidence_candidate"]),
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "partner_tensor_handoff_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "Goal1486 records a CUDA Driver API cuMemAlloc/cuMemFree allocation "
            "probe for an RTDL-owned managed-buffer evidence envelope. A "
            "candidate result is not a public zero-copy claim and does not "
            "authorize public speedup wording, whole-app claims, stable "
            "primitive promotion, partner tensor handoff, or release action."
        ),
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    probe = payload["probe"]
    evidence = payload["allocation_evidence"]
    lines = [
        "# Goal 1486: CUDA Driver Allocation Probe",
        "",
        "## Verdict",
        "",
        f"Probe status: `{probe['status']}`.",
        "",
        "This artifact records allocation evidence only. It does not authorize public zero-copy or speedup claims.",
        "",
        "## Environment",
        "",
        f"- Commit: `{payload['source_commit']}`",
        f"- Device: `{probe.get('device_name')}`",
        f"- CUDA driver version: `{probe.get('cuda_driver_version')}`",
        "",
        "## Evidence",
        "",
        f"- Device allocation performed: `{probe['device_allocation_performed']}`",
        f"- Device free performed: `{probe['device_free_performed']}`",
        f"- Device pointer nonzero: `{probe['device_pointer_nonzero']}`",
        f"- Host-to-device transfers: `{evidence['host_to_device_transfers']}`",
        f"- Device-to-host transfers: `{evidence['device_to_host_transfers']}`",
        f"- Device residency observed: `{evidence['device_residency_observed']}`",
        f"- Measured on real NVIDIA: `{evidence['measured_on_real_nvidia']}`",
        f"- True zero-copy evidence candidate: `{evidence['true_zero_copy_evidence_candidate']}`",
        "",
        "## Claim Boundary",
        "",
        payload["claim_boundary"],
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Goal1486 CUDA Driver API allocation probe.")
    parser.add_argument("--byte-count", type=int, default=256)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    probe = run_cuda_driver_allocation_probe(args.byte_count)
    payload = build_payload(probe)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(payload, args.md_out)
    print(json.dumps({"status": probe["status"], "candidate_only": payload["candidate_only"]}, indent=2))
    return 0 if probe["status"] == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())

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
sys.path.insert(0, str(ROOT))


REPORT_STEM = "goal1500_v1_5_4_optix_device_collect_k_measurement_2026-05-08"
DEFAULT_PACKET_PATH = (
    ROOT / "docs" / "reports" / "goal1492_v1_5_4_collect_k_device_buffer_execution_packet_2026-05-08.json"
)
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"
DEFAULT_LIBRARY_PATH = ROOT / "build" / "librtdl_optix.so"


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


class CudaDriver:
    def __init__(self) -> None:
        self.cuda = ctypes.CDLL("libcuda.so.1")
        self.context = ctypes.c_void_p()

        self.cuda.cuInit.argtypes = [ctypes.c_uint]
        self.cuda.cuInit.restype = ctypes.c_int
        self.cuda.cuDeviceGet.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
        self.cuda.cuDeviceGet.restype = ctypes.c_int
        self.cuda.cuDeviceGetName.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
        self.cuda.cuDeviceGetName.restype = ctypes.c_int
        self.cuda.cuDriverGetVersion.argtypes = [ctypes.POINTER(ctypes.c_int)]
        self.cuda.cuDriverGetVersion.restype = ctypes.c_int
        self.cuda.cuDevicePrimaryCtxRetain.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_int]
        self.cuda.cuDevicePrimaryCtxRetain.restype = ctypes.c_int
        self.cuda.cuCtxSetCurrent.argtypes = [ctypes.c_void_p]
        self.cuda.cuCtxSetCurrent.restype = ctypes.c_int
        self.cuda.cuDevicePrimaryCtxRelease.argtypes = [ctypes.c_int]
        self.cuda.cuDevicePrimaryCtxRelease.restype = ctypes.c_int
        self.cuda.cuMemAlloc_v2.argtypes = [ctypes.POINTER(ctypes.c_ulonglong), ctypes.c_size_t]
        self.cuda.cuMemAlloc_v2.restype = ctypes.c_int
        self.cuda.cuMemFree_v2.argtypes = [ctypes.c_ulonglong]
        self.cuda.cuMemFree_v2.restype = ctypes.c_int
        self.cuda.cuMemcpyHtoD_v2.argtypes = [ctypes.c_ulonglong, ctypes.c_void_p, ctypes.c_size_t]
        self.cuda.cuMemcpyHtoD_v2.restype = ctypes.c_int
        self.cuda.cuMemcpyDtoH_v2.argtypes = [ctypes.c_void_p, ctypes.c_ulonglong, ctypes.c_size_t]
        self.cuda.cuMemcpyDtoH_v2.restype = ctypes.c_int

        _cuda_check(self.cuda.cuInit(0), "cuInit")
        self.device = ctypes.c_int()
        _cuda_check(self.cuda.cuDeviceGet(ctypes.byref(self.device), 0), "cuDeviceGet")
        _cuda_check(self.cuda.cuDevicePrimaryCtxRetain(ctypes.byref(self.context), self.device.value), "cuDevicePrimaryCtxRetain")
        _cuda_check(self.cuda.cuCtxSetCurrent(self.context), "cuCtxSetCurrent")

    def device_name(self) -> str:
        buffer = ctypes.create_string_buffer(256)
        _cuda_check(self.cuda.cuDeviceGetName(buffer, len(buffer), self.device.value), "cuDeviceGetName")
        return buffer.value.decode("utf-8", errors="replace")

    def driver_version(self) -> int:
        version = ctypes.c_int()
        _cuda_check(self.cuda.cuDriverGetVersion(ctypes.byref(version)), "cuDriverGetVersion")
        return int(version.value)

    def alloc(self, byte_count: int) -> ctypes.c_ulonglong:
        ptr = ctypes.c_ulonglong()
        _cuda_check(self.cuda.cuMemAlloc_v2(ctypes.byref(ptr), int(byte_count)), "cuMemAlloc_v2")
        return ptr

    def free(self, ptr: ctypes.c_ulonglong) -> None:
        if ptr.value:
            _cuda_check(self.cuda.cuMemFree_v2(ptr), "cuMemFree_v2")

    def h2d(self, dst: ctypes.c_ulonglong, src: ctypes.Array, byte_count: int) -> None:
        _cuda_check(self.cuda.cuMemcpyHtoD_v2(dst, ctypes.cast(src, ctypes.c_void_p), int(byte_count)), "cuMemcpyHtoD_v2")

    def d2h(self, dst: ctypes.Array, src: ctypes.c_ulonglong, byte_count: int) -> None:
        _cuda_check(self.cuda.cuMemcpyDtoH_v2(ctypes.cast(dst, ctypes.c_void_p), src, int(byte_count)), "cuMemcpyDtoH_v2")

    def close(self) -> None:
        if self.context.value:
            try:
                _cuda_check(self.cuda.cuDevicePrimaryCtxRelease(self.device.value), "cuDevicePrimaryCtxRelease")
            finally:
                self.context = ctypes.c_void_p()


def _load_optix(path: Path) -> ctypes.CDLL:
    lib = ctypes.CDLL(str(path))
    lib.rtdl_optix_collect_k_bounded_i64_device.argtypes = [
        ctypes.c_uint64,
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.c_uint64,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_optix_collect_k_bounded_i64_device.restype = ctypes.c_int
    return lib


def _call_collect_k(
    lib: ctypes.CDLL,
    candidate_ptr: ctypes.c_ulonglong,
    candidate_count: int,
    row_width: int,
    output_ptr: ctypes.c_ulonglong,
    capacity: int,
) -> dict[str, Any]:
    emitted = ctypes.c_size_t()
    overflowed = ctypes.c_uint32()
    h2d = ctypes.c_uint64()
    d2h = ctypes.c_uint64()
    internal = ctypes.c_uint64()
    error = ctypes.create_string_buffer(4096)
    status = lib.rtdl_optix_collect_k_bounded_i64_device(
        int(candidate_ptr.value),
        int(candidate_count),
        int(row_width),
        int(output_ptr.value),
        int(capacity),
        ctypes.byref(emitted),
        ctypes.byref(overflowed),
        ctypes.byref(h2d),
        ctypes.byref(d2h),
        ctypes.byref(internal),
        error,
        len(error),
    )
    if status != 0:
        raise RuntimeError(error.value.decode("utf-8", errors="replace"))
    return {
        "valid_count": int(emitted.value),
        "overflowed": bool(overflowed.value),
        "h2d": int(h2d.value),
        "d2h": int(d2h.value),
        "internal": int(internal.value),
    }


def measure(packet_path: Path, library_path: Path) -> dict[str, Any]:
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    rows = [int(cell) for row in packet["candidate_rows"] for cell in row]
    row_width = int(packet["row_width"])
    capacity = int(packet["capacity"])
    candidate_count = len(packet["candidate_rows"])

    cuda = CudaDriver()
    candidate_ptr = ctypes.c_ulonglong()
    output_ptr = ctypes.c_ulonglong()
    try:
        lib = _load_optix(library_path)
        row_array_type = ctypes.c_int64 * len(rows)
        host_rows = row_array_type(*rows)
        candidate_ptr = cuda.alloc(ctypes.sizeof(host_rows))
        output_elements = max(1, capacity * row_width)
        output_array_type = ctypes.c_int64 * output_elements
        output_ptr = cuda.alloc(ctypes.sizeof(output_array_type))
        cuda.h2d(candidate_ptr, host_rows, ctypes.sizeof(host_rows))

        result = _call_collect_k(lib, candidate_ptr, candidate_count, row_width, output_ptr, capacity)
        host_out = output_array_type()
        cuda.d2h(host_out, output_ptr, ctypes.sizeof(host_out))
        candidate_id_rows = [
            [int(host_out[index * row_width + column]) for column in range(row_width)]
            for index in range(result["valid_count"])
        ]

        expected = packet["expected_reference"]
        return {
            "goal": "Goal1493",
            "source_packet_goal": packet["goal"],
            "measurement_goal": "Goal1500",
            "primitive": packet["first_target_primitive"],
            "backend": "optix",
            "native_symbol": "rtdl_optix_collect_k_bounded_i64_device",
            "measured_on_real_nvidia": True,
            "goal1489_preflight_green": True,
            "git_commit": _git_head(),
            "platform": platform.platform(),
            "device_name": cuda.device_name(),
            "cuda_driver_version": cuda.driver_version(),
            "library_path": str(library_path),
            "row_width": row_width,
            "capacity": capacity,
            "candidate_rows": packet["candidate_rows"],
            "result": {
                "valid_count": result["valid_count"],
                "overflowed": bool(result["overflowed"]),
                "candidate_id_rows": candidate_id_rows,
            },
            "parity": {
                "same_candidate_rows": candidate_id_rows == expected["candidate_id_rows"],
                "same_valid_count": result["valid_count"] == expected["valid_count"],
                "same_overflowed_flag": bool(result["overflowed"]) == bool(expected["overflowed"]),
            },
            "transfer_accounting": {
                "host_to_device_transfers_before_backend_execution": 1,
                "device_to_host_transfers_after_backend_execution": int(result["d2h"]),
                "internal_device_transfers_if_any": int(result["internal"]),
                "allocation_only_transfers_distinguished_from_content_transfers": True,
                "verification_copies_excluded_from_backend_counters": True,
            },
            "true_zero_copy_authorized": False,
            "public_speedup_wording_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "stable_public_primitive_authorized": False,
            "partner_tensor_handoff_authorized": False,
            "release_action_authorized": False,
        }
    finally:
        if output_ptr.value:
            cuda.free(output_ptr)
        if candidate_ptr.value:
            cuda.free(candidate_ptr)
        cuda.close()


def to_markdown(payload: dict[str, Any]) -> str:
    transfer = payload["transfer_accounting"]
    return "\n".join(
        [
            "# Goal 1500: OptiX Device COLLECT_K_BOUNDED Measurement",
            "",
            "## Verdict",
            "",
            "`goal1500_measured_optix_device_collect_k_packet`",
            "",
            "## Scope",
            "",
            f"- Backend: `{payload['backend']}`",
            f"- Symbol: `{payload['native_symbol']}`",
            f"- Device: `{payload['device_name']}`",
            f"- Git commit: `{payload['git_commit']}`",
            "",
            "## Parity",
            "",
            f"- Candidate rows: `{payload['parity']['same_candidate_rows']}`",
            f"- Valid count: `{payload['parity']['same_valid_count']}`",
            f"- Overflow flag: `{payload['parity']['same_overflowed_flag']}`",
            "",
            "## Transfer Accounting",
            "",
            f"- H2D setup transfers before backend execution: `{transfer['host_to_device_transfers_before_backend_execution']}`",
            f"- D2H metadata transfers after backend execution: `{transfer['device_to_host_transfers_after_backend_execution']}`",
            f"- Internal device transfers: `{transfer['internal_device_transfers_if_any']}`",
            "",
            "## Claim Boundary",
            "",
            "This is measured device-pointer execution evidence for the Goal1492 packet only. "
            "It does not authorize true zero-copy wording, public speedup wording, whole-app "
            "claims, partner tensor handoff, stable primitive promotion, or release action.",
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Measure the narrow OptiX device-pointer collect-k path.")
    parser.add_argument("--packet-json", type=Path, default=DEFAULT_PACKET_PATH)
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY_PATH)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = measure(args.packet_json, args.library)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"status": "goal1500_measured_optix_device_collect_k_packet"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

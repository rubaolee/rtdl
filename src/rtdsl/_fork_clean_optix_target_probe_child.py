"""Minimal disposable OptiX target probe.

This file is executed by path, not imported through the :mod:`rtdsl` package.
That boundary is deliberate: a fork-clean capability probe must not pay for or
initialize the complete Action compiler/runtime module graph merely to validate
one already-selected OptiX provider and read the visible device memory limit.
"""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Mapping


REQUEST_SCHEMA = "rtdl.fast_fork_clean_optix_target_probe_request.v1"
RESPONSE_SCHEMA = "rtdl.fast_fork_clean_optix_target_probe_response.v1"
_TARGET_FIELDS = (
    "optix_available",
    "numba_available",
    "embree_available",
    "cpu_reference_available",
    "optix_max_inline_state_bytes",
    "numba_max_device_state_bytes",
    "embree_max_host_state_bytes",
    "max_output_bytes",
    "profile_source",
    "device_memory_limit_bytes",
    "production_selection_policy",
)


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_nonnegative_optional_int(value: object, *, field: str) -> None:
    if value is not None and (
        isinstance(value, bool) or not isinstance(value, int) or value < 0
    ):
        raise ValueError("FAST_OPTIX_TARGET_PROBE_LIMIT_INVALID:" + field)


def _probe_provider_version(provider_path: Path) -> tuple[int, int, int]:
    library = ctypes.CDLL(str(provider_path))
    function = library.rtdl_optix_get_version
    function.argtypes = [ctypes.POINTER(ctypes.c_int)] * 3
    function.restype = ctypes.c_int
    major = ctypes.c_int()
    minor = ctypes.c_int()
    patch = ctypes.c_int()
    status = int(
        function(ctypes.byref(major), ctypes.byref(minor), ctypes.byref(patch))
    )
    if status != 0 or major.value <= 0:
        raise RuntimeError("FAST_OPTIX_TARGET_PROBE_PROVIDER_VERSION_FAILED")
    return major.value, minor.value, patch.value


def _probe_visible_device_total_memory() -> int:
    driver = ctypes.CDLL("libcuda.so.1")
    driver.cuInit.argtypes = [ctypes.c_uint]
    driver.cuInit.restype = ctypes.c_int
    if int(driver.cuInit(0)) != 0:
        raise RuntimeError("FAST_OPTIX_TARGET_PROBE_CUDA_INIT_FAILED")
    device = ctypes.c_int()
    driver.cuDeviceGet.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
    driver.cuDeviceGet.restype = ctypes.c_int
    if int(driver.cuDeviceGet(ctypes.byref(device), 0)) != 0:
        raise RuntimeError("FAST_OPTIX_TARGET_PROBE_DEVICE_GET_FAILED")
    total = ctypes.c_size_t()
    total_memory = getattr(driver, "cuDeviceTotalMem_v2", None)
    if total_memory is None:
        total_memory = driver.cuDeviceTotalMem
    total_memory.argtypes = [ctypes.POINTER(ctypes.c_size_t), ctypes.c_int]
    total_memory.restype = ctypes.c_int
    if int(total_memory(ctypes.byref(total), device)) != 0 or total.value <= 0:
        raise RuntimeError("FAST_OPTIX_TARGET_PROBE_DEVICE_MEMORY_FAILED")
    return int(total.value)


def build_response(request: Mapping[str, object]) -> dict[str, object]:
    expected_fields = {
        "schema",
        "nonce",
        "required_backends",
        "certified_nearest",
        "cpu_reference_available",
        "optix_max_inline_state_bytes",
        "numba_max_device_state_bytes",
        "embree_max_host_state_bytes",
        "max_output_bytes",
        "action_api_sha256",
        "probe_child_sha256",
        "provider_library_path",
        "provider_library_sha256",
    }
    if set(request) != expected_fields:
        raise ValueError("FAST_OPTIX_TARGET_PROBE_REQUEST_FIELDS_INVALID")
    nonce = request["nonce"]
    if (
        request["schema"] != REQUEST_SCHEMA
        or not isinstance(nonce, str)
        or len(nonce) != 64
        or any(character not in "0123456789abcdef" for character in nonce)
        or request["required_backends"] != ["optix"]
        or request["certified_nearest"] is not False
        or not isinstance(request["cpu_reference_available"], bool)
    ):
        raise ValueError("FAST_OPTIX_TARGET_PROBE_REQUEST_IDENTITY_INVALID")
    child_path = Path(__file__).resolve(strict=True)
    action_api_path = child_path.with_name("action_api.py").resolve(strict=True)
    if request["probe_child_sha256"] != _sha256_file(child_path):
        raise ValueError("FAST_OPTIX_TARGET_PROBE_CHILD_SOURCE_MISMATCH")
    if request["action_api_sha256"] != _sha256_file(action_api_path):
        raise ValueError("FAST_OPTIX_TARGET_PROBE_ACTION_API_SOURCE_MISMATCH")
    for field in (
        "optix_max_inline_state_bytes",
        "numba_max_device_state_bytes",
        "embree_max_host_state_bytes",
        "max_output_bytes",
    ):
        _require_nonnegative_optional_int(request[field], field=field)
    provider_value = request["provider_library_path"]
    provider_sha = request["provider_library_sha256"]
    if (
        not isinstance(provider_value, str)
        or not provider_value
        or not isinstance(provider_sha, str)
        or len(provider_sha) != 64
    ):
        raise ValueError("FAST_OPTIX_TARGET_PROBE_PROVIDER_IDENTITY_REQUIRED")
    provider_path = Path(provider_value).resolve(strict=True)
    if _sha256_file(provider_path) != provider_sha:
        raise ValueError("FAST_OPTIX_TARGET_PROBE_PROVIDER_MISMATCH")
    environment_provider = os.environ.get("RTDL_OPTIX_LIB")
    if not environment_provider or Path(environment_provider).resolve() != provider_path:
        raise ValueError("FAST_OPTIX_TARGET_PROBE_PROVIDER_ENVIRONMENT_MISMATCH")

    provider_version = _probe_provider_version(provider_path)
    target_profile = {
        "optix_available": True,
        "numba_available": False,
        "embree_available": False,
        "cpu_reference_available": request["cpu_reference_available"],
        "optix_max_inline_state_bytes": request["optix_max_inline_state_bytes"],
        "numba_max_device_state_bytes": request["numba_max_device_state_bytes"],
        "embree_max_host_state_bytes": request["embree_max_host_state_bytes"],
        "max_output_bytes": request["max_output_bytes"],
        "profile_source": "runtime_capability_probe",
        "device_memory_limit_bytes": _probe_visible_device_total_memory(),
        "production_selection_policy": "compiler_owned_default",
    }
    if tuple(target_profile) != _TARGET_FIELDS:
        raise AssertionError("FAST_OPTIX_TARGET_PROBE_TARGET_FIELD_ORDER_INVALID")
    body: dict[str, object] = {
        "schema": RESPONSE_SCHEMA,
        "nonce": nonce,
        "required_backends": ["optix"],
        "action_api_sha256": request["action_api_sha256"],
        "probe_child_sha256": request["probe_child_sha256"],
        "provider_library_sha256": provider_sha,
        "provider_version": list(provider_version),
        "target_profile": target_profile,
        "probe_process_pid": os.getpid(),
        "parent_process_pid": os.getppid(),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "nvidia_visible_devices": os.environ.get("NVIDIA_VISIBLE_DEVICES"),
    }
    body["response_sha256"] = _canonical_sha256(body)
    return body


def main() -> int:
    request = json.loads(sys.stdin.read())
    if not isinstance(request, dict):
        raise ValueError("FAST_OPTIX_TARGET_PROBE_REQUEST_MAPPING_REQUIRED")
    response = build_response(request)
    sys.stdout.write(json.dumps(response, sort_keys=True, separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

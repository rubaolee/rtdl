"""Native execution boundary for a verified seven-role V4 callback program.

This module deliberately starts after verification and PTX composition.  It
does not accept Python callables or source and cannot select a callback or a
physical template.  It launches one exact composed module and binds the result
to RTDL's behavioral OptiX provenance receipt.
"""

from __future__ import annotations

import ctypes
import hashlib
import json
import math
from dataclasses import dataclass
from typing import Sequence

from .physical_execution_provenance import OptixTraversalAuditSession


class _NativeSphere(ctypes.Structure):
    _fields_ = [
        ("cx", ctypes.c_float), ("cy", ctypes.c_float),
        ("cz", ctypes.c_float), ("radius", ctypes.c_float),
        ("item_id", ctypes.c_uint32),
    ]


class _FormalStatus(ctypes.Structure):
    _fields_ = [
        ("first_error_claimed", ctypes.c_uint32),
        ("error_code", ctypes.c_uint32),
        ("stage", ctypes.c_uint32),
        ("role", ctypes.c_uint32),
        ("launch_index", ctypes.c_uint64),
        ("error_site", ctypes.c_uint32),
        ("effect_tag", ctypes.c_uint32),
        ("nonce_word", ctypes.c_uint32),
        ("invocation_mask", ctypes.c_uint32),
    ]


@dataclass(frozen=True)
class V4FormalCallbackResult:
    output_ids: tuple[int, ...]
    output_distance: tuple[float, ...]
    role_counters: tuple[int, ...]
    launch_status: tuple[dict[str, int], ...]
    traversal_receipt: dict[str, object]
    output_sha256: str
    composed_ptx_sha256: str


@dataclass(frozen=True)
class V4FormalCallbackFailureResult:
    expected_error_code: int
    launch_status: tuple[dict[str, int], ...]
    role_counters: tuple[int, ...]
    native_error: str
    composed_ptx_sha256: str
    output_accepted: bool = False


def _stable_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()


def _configure(library: object):
    symbol = getattr(library, "rtdl_optix_v4_run_formal_callback_v1", None)
    if symbol is None:
        raise RuntimeError("native library lacks Goal5751 formal callback ABI")
    symbol.argtypes = [
        ctypes.c_char_p,
        ctypes.POINTER(_NativeSphere), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(_FormalStatus), ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
    ]
    symbol.restype = ctypes.c_int
    return symbol


def run_formal_callback_ptx(
    composed_ptx: str,
    *,
    spheres: Sequence[tuple[Sequence[float], float, int]],
    queries: Sequence[tuple[Sequence[float], float]],
    semantic_digest: str,
    expected_output: Sequence[tuple[int, float]] | None = None,
    expected_device_error_code: int | None = None,
    library: object | None = None,
) -> V4FormalCallbackResult | V4FormalCallbackFailureResult:
    """Execute one exact composed callback module and fail closed on drift."""

    if not composed_ptx or not spheres or not queries:
        raise ValueError("formal callback PTX, spheres, and queries must be nonempty")
    if len(semantic_digest) != 64:
        raise ValueError("semantic digest must be an exact SHA-256")
    native_spheres = (_NativeSphere * len(spheres))()
    for index, (center, radius, item_id) in enumerate(spheres):
        if (len(center) != 3 or not all(math.isfinite(float(value)) for value in center)
                or not math.isfinite(float(radius)) or float(radius) < 0.0
                or not 0 <= int(item_id) <= 0xFFFFFFFF):
            raise ValueError(f"invalid sphere at index {index}")
        native_spheres[index] = _NativeSphere(
            float(center[0]), float(center[1]), float(center[2]),
            float(radius), int(item_id),
        )
    origins_flat: list[float] = []
    tmax_values: list[float] = []
    for index, (origin, tmax) in enumerate(queries):
        if (len(origin) != 3 or not all(math.isfinite(float(value)) for value in origin)
                or not math.isfinite(float(tmax)) or float(tmax) <= 0.0):
            raise ValueError(f"invalid query at index {index}")
        origins_flat.extend(float(value) for value in origin)
        tmax_values.append(float(tmax))
    origins = (ctypes.c_float * len(origins_flat))(*origins_flat)
    tmax = (ctypes.c_float * len(tmax_values))(*tmax_values)
    output_ids = (ctypes.c_uint32 * len(queries))()
    output_distance = (ctypes.c_float * len(queries))()
    statuses = (_FormalStatus * len(queries))()
    counters = (ctypes.c_uint64 * 7)()
    if library is None:
        from . import optix_runtime
        library = optix_runtime._load_optix_library()
    symbol = _configure(library)
    error = ctypes.create_string_buffer(16384)
    session = OptixTraversalAuditSession.open(library=library)
    try:
        native_status = int(symbol(
            composed_ptx.encode("utf-8"), native_spheres, len(spheres),
            origins, tmax, len(queries), output_ids, output_distance,
            statuses, counters, error, len(error),
        ))
        if native_status:
            status_rows = tuple({
                "first_error_claimed": int(item.first_error_claimed),
                "error_code": int(item.error_code), "stage": int(item.stage),
                "role": int(item.role), "launch_index": int(item.launch_index),
                "error_site": int(item.error_site), "effect_tag": int(item.effect_tag),
                "nonce_word": int(item.nonce_word),
                "invocation_mask": int(item.invocation_mask),
            } for item in statuses)
            counter_rows = tuple(int(item) for item in counters)
            if expected_device_error_code is not None:
                matching = [
                    item for item in status_rows
                    if item["error_code"] == int(expected_device_error_code)
                ]
                if not matching or any(item["first_error_claimed"] != 1 for item in matching):
                    raise RuntimeError(
                        "formal callback failed with the wrong/corrupt first-error status: "
                        f"{status_rows!r}")
                session.abort()
                return V4FormalCallbackFailureResult(
                    expected_error_code=int(expected_device_error_code),
                    launch_status=status_rows,
                    role_counters=counter_rows,
                    native_error=error.value.decode("utf-8", errors="replace"),
                    composed_ptx_sha256=hashlib.sha256(
                        composed_ptx.encode("utf-8")).hexdigest(),
                )
            diagnostics = tuple(
                (int(output_ids[index]), float(output_distance[index]))
                for index in range(len(queries))
            )
            message = error.value.decode("utf-8", errors="replace") or \
                f"formal callback native status {native_status}"
            raise RuntimeError(f"{message}; make_ray_diagnostics={diagnostics!r}")
        if expected_device_error_code is not None:
            raise RuntimeError("invalid formal callback output was accepted")
        observed = tuple(
            (int(output_ids[index]), float(output_distance[index]))
            for index in range(len(queries))
        )
        status_rows = tuple({
            "first_error_claimed": int(item.first_error_claimed),
            "error_code": int(item.error_code), "stage": int(item.stage),
            "role": int(item.role), "launch_index": int(item.launch_index),
            "error_site": int(item.error_site), "effect_tag": int(item.effect_tag),
            "nonce_word": int(item.nonce_word),
            "invocation_mask": int(item.invocation_mask),
        } for item in statuses)
        counter_rows = tuple(int(item) for item in counters)
        if expected_output is not None:
            expected = tuple((int(item[0]), float(item[1])) for item in expected_output)
            if len(expected) != len(observed):
                raise RuntimeError("formal callback expected-output cardinality mismatch")
            for index, (actual, reference) in enumerate(zip(observed, expected)):
                if actual[0] != reference[0] or ctypes.c_float(actual[1]).value != ctypes.c_float(reference[1]).value:
                    raise RuntimeError(
                        f"formal callback output mismatch at query {index}: "
                        f"{actual!r} != {reference!r}")
        if any(item["first_error_claimed"] or item["error_code"] for item in status_rows):
            raise RuntimeError("formal callback returned a nonzero device status")
        if any(item <= 0 for item in counter_rows):
            raise RuntimeError("formal callback did not exercise all seven roles")
        output_digest = _stable_digest(observed)
        receipt = session.finish(
            semantic_digest=semantic_digest,
            output_digest=output_digest,
            route_identity="v4_formal_callback_ir:seven_role_composed_v1",
            expected_program_bundles=("v4_formal_callback_ir_seven_role_composed",),
        )
    except Exception:
        session.abort()
        raise
    if receipt["physical_executor_classification"] != "optix_traversal_observed":
        raise RuntimeError("formal callback did not produce bound OptiX traversal")
    return V4FormalCallbackResult(
        output_ids=tuple(item[0] for item in observed),
        output_distance=tuple(item[1] for item in observed),
        role_counters=counter_rows,
        launch_status=status_rows,
        traversal_receipt=receipt,
        output_sha256=output_digest,
        composed_ptx_sha256=hashlib.sha256(composed_ptx.encode("utf-8")).hexdigest(),
    )


__all__ = [
    "V4FormalCallbackFailureResult", "V4FormalCallbackResult",
    "run_formal_callback_ptx",
]

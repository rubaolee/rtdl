"""Behaviorally evidenced native runner for the bounded Goal5749 callback PoC."""

from __future__ import annotations

import ctypes
import hashlib
import json
import math
from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .physical_execution_provenance import OptixTraversalAuditSession
from .v4_callback_poc import (
    CallbackRuntimeError,
    CallbackRole,
    DeviceFunctionArtifact,
    EffectKind,
    VerifiedCallbackModule,
    trace_spheres_with_interpreter,
    verify_sphere_aabb,
    verified_sphere_aabb,
)


class _NativeSphere(ctypes.Structure):
    _fields_ = [
        ("cx", ctypes.c_float), ("cy", ctypes.c_float),
        ("cz", ctypes.c_float), ("radius", ctypes.c_float),
        ("item_id", ctypes.c_uint32),
    ]


class _LaunchStatus(ctypes.Structure):
    _fields_ = [
        ("status", ctypes.c_uint32), ("stage", ctypes.c_uint32),
        ("nonce_word", ctypes.c_uint32), ("invocation_mask", ctypes.c_uint32),
    ]


@dataclass(frozen=True)
class V4CallbackPocResult:
    output_ids: tuple[int, ...]
    output_t: tuple[float, ...]
    callback_counters: tuple[int, ...]
    launch_status: tuple[dict[str, int], ...]
    traversal_receipt: dict[str, object]
    output_sha256: str
    interpreter_output_sha256: str
    route: str
    wrapper_numeric_mode: str
    leaf_numeric_modes: tuple[str, ...]


@dataclass(frozen=True)
class V4CallbackPocFailureResult:
    expected_status: int
    observed_statuses: tuple[dict[str, int], ...]
    callback_counters: tuple[int, ...]
    native_error: str
    route: str
    wrapper_numeric_mode: str
    output_accepted: bool = False


def _stable_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()


def _configure(library: object, *, two_module_diagnostic: bool = False):
    symbol_name = ("rtdl_optix_v4_run_verified_callback_two_module_diagnostic"
                   if two_module_diagnostic else
                   "rtdl_optix_v4_run_verified_callback_poc")
    symbol = getattr(library, symbol_name, None)
    if symbol is None:
        raise RuntimeError(f"native library lacks Goal5749 ABI {symbol_name}")
    prefix = [
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint32,
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint32,
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint32,
        ctypes.c_char_p, ctypes.c_char_p,
    ]
    mode = [ctypes.c_int] if two_module_diagnostic else [ctypes.c_int, ctypes.c_int]
    suffix = [
        ctypes.POINTER(_NativeSphere), ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.c_size_t,
        ctypes.c_float, ctypes.c_float,
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(_LaunchStatus), ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
    ]
    symbol.argtypes = prefix + mode + suffix
    symbol.restype = ctypes.c_int
    return symbol


def run_verified_callback_poc(
    module: VerifiedCallbackModule,
    artifacts: Sequence[DeviceFunctionArtifact],
    *,
    spheres: Sequence[tuple[Sequence[float], float, int]],
    rays: Sequence[tuple[Sequence[float], Sequence[float]]],
    tmin: float,
    tmax: float,
    route: str,
    wrapper_numeric_mode: str,
    scalar_probe: DeviceFunctionArtifact,
    expected_device_failure_status: int | None = None,
    library: object | None = None,
) -> V4CallbackPocResult | V4CallbackPocFailureResult:
    """Run one functional-only cohort and bind output to traversal evidence."""

    if route not in ("ordinary_composed", "direct_callable",
                     "ordinary_external_two_module_diagnostic"):
        raise ValueError(
            "route must be ordinary_composed, direct_callable, or the bounded "
            "ordinary_external_two_module_diagnostic")
    if wrapper_numeric_mode not in ("strict", "fast"):
        raise ValueError("wrapper numeric mode must be strict or fast")
    by_role = {CallbackRole(item.role): item for item in artifacts}
    if set(by_role) != set(CallbackRole) or len(artifacts) != 3:
        raise ValueError("exactly one artifact per PoC callback role is required")
    for role, artifact in by_role.items():
        if artifact.ir_sha256 != module.ir_sha256:
            raise ValueError(f"{role.value} artifact belongs to a different Callback IR")
        if (not artifact.abi_name.startswith("rtdl_v4_") or
                artifact.abi_name.startswith("__direct_callable__")):
            raise ValueError("artifact is not a compiler-owned ordinary device function")
    if scalar_probe.role != "scalar_probe" or scalar_probe.ir_sha256 != module.ir_sha256:
        raise ValueError("scalar probe does not belong to the verified Callback IR")
    if not scalar_probe.abi_name.startswith("rtdl_v4_scalar_probe_"):
        raise ValueError("scalar probe does not carry the compiler-owned ABI namespace")
    if not rays or not spheres:
        raise ValueError("functional PoC requires nonempty rays and verified spheres")
    if not math.isfinite(tmin) or not math.isfinite(tmax) or tmin < 0 or not tmin < tmax:
        raise ValueError("invalid finite ray interval")
    native_spheres = (_NativeSphere * len(spheres))()
    for index, (center, radius, item_id) in enumerate(spheres):
        verify_sphere_aabb(center, radius, verified_sphere_aabb(center, radius))
        if not 0 <= int(item_id) <= 0xFFFFFFFF:
            raise ValueError("sphere item ID is outside u32")
        native_spheres[index] = _NativeSphere(
            float(center[0]), float(center[1]), float(center[2]), float(radius), int(item_id))
    origin_values: list[float] = []
    direction_values: list[float] = []
    expected: list[tuple[int, float]] = []
    interpreter_failure_observed = False
    for origin, direction in rays:
        if len(origin) != 3 or len(direction) != 3:
            raise ValueError("ray origin/direction must be vec3")
        origin_values.extend(float(item) for item in origin)
        direction_values.extend(float(item) for item in direction)
        try:
            effect = trace_spheres_with_interpreter(
                module, origin=origin, direction=direction, tmin=tmin, tmax=tmax,
                spheres=spheres)
        except CallbackRuntimeError as exc:
            if (expected_device_failure_status is None or
                    int(exc.status) != int(expected_device_failure_status)):
                raise
            interpreter_failure_observed = True
            expected.append((0, 0.0))
            continue
        if effect.kind is not EffectKind.PAYLOAD:
            raise AssertionError("independent interpreter did not finalize a payload")
        expected.append((effect.u0, effect.f0))
    if expected_device_failure_status is not None and not interpreter_failure_observed:
        raise RuntimeError("independent interpreter did not observe the expected device fault")
    origins = (ctypes.c_float * len(origin_values))(*origin_values)
    directions = (ctypes.c_float * len(direction_values))(*direction_values)
    output_ids = (ctypes.c_uint32 * len(rays))()
    output_t = (ctypes.c_float * len(rays))()
    status_records = (_LaunchStatus * len(rays))()
    counters = (ctypes.c_uint64 * 7)()
    if library is None:
        from . import optix_runtime
        library = optix_runtime._load_optix_library()
    two_module_diagnostic = route == "ordinary_external_two_module_diagnostic"
    symbol = _configure(library, two_module_diagnostic=two_module_diagnostic)
    ordered = [by_role[role] for role in
               (CallbackRole.INTERSECTION, CallbackRole.ANY_HIT, CallbackRole.MISS)]
    semantic_digest = _stable_digest({
        "ir_sha256": module.ir_sha256,
        "artifacts": [item.ptx_sha256 for item in ordered],
        "scalar_probe_ptx_sha256": scalar_probe.ptx_sha256,
        "route": route,
        "wrapper_numeric_mode": wrapper_numeric_mode,
    })
    error = ctypes.create_string_buffer(8192)
    session = OptixTraversalAuditSession.open(library=library)
    try:
        native_arguments = [
            ordered[0].ptx.encode(), ordered[0].abi_name.encode(), ordered[0].nonce_word,
            ordered[1].ptx.encode(), ordered[1].abi_name.encode(), ordered[1].nonce_word,
            ordered[2].ptx.encode(), ordered[2].abi_name.encode(), ordered[2].nonce_word,
            scalar_probe.ptx.encode(), scalar_probe.abi_name.encode(),
        ]
        if not two_module_diagnostic:
            native_arguments.append(route == "direct_callable")
        native_arguments.extend([
            wrapper_numeric_mode == "fast",
            native_spheres, len(spheres), origins, directions, len(rays),
            float(tmin), float(tmax), output_ids, output_t, status_records, counters,
            error, len(error),
        ])
        native_status = int(symbol(*native_arguments))
        statuses = tuple({
            "status": int(item.status), "stage": int(item.stage),
            "nonce_word": int(item.nonce_word), "invocation_mask": int(item.invocation_mask),
        } for item in status_records)
        counts = tuple(int(item) for item in counters)
        if native_status and expected_device_failure_status is not None:
            session.abort()
            observed_codes = {item["status"] for item in statuses if item["status"] != 0}
            if int(expected_device_failure_status) not in observed_codes:
                raise RuntimeError(
                    f"device fault status mismatch: expected {expected_device_failure_status}, "
                    f"observed {sorted(observed_codes)}")
            return V4CallbackPocFailureResult(
                expected_status=int(expected_device_failure_status),
                observed_statuses=statuses,
                callback_counters=counts,
                native_error=error.value.decode("utf-8", errors="replace"),
                route=route,
                wrapper_numeric_mode=wrapper_numeric_mode,
            )
        if native_status:
            raise RuntimeError(error.value.decode("utf-8", errors="replace") or
                               f"V4 native callback failed with status {native_status}")
        if expected_device_failure_status is not None:
            raise RuntimeError("invalid callback output was accepted instead of failing closed")
        observed = tuple((int(output_ids[index]), float(output_t[index]))
                         for index in range(len(rays)))
        interpreter_output_digest = _stable_digest(expected)
        for index, (actual, reference) in enumerate(zip(observed, expected)):
            if actual[0] != reference[0] or np.float32(actual[1]) != np.float32(reference[1]):
                raise RuntimeError(
                    f"V4 callback output mismatch at query {index}: {actual!r} != {reference!r}")
        output_digest = _stable_digest(observed)
        program = (
            "v4_verified_callback_ordinary_external_two_module_diagnostic"
            if two_module_diagnostic else
            "v4_verified_callback_direct_callable_poc" if route == "direct_callable" else
            "v4_verified_callback_ordinary_composed_poc")
        receipt = session.finish(
            semantic_digest=semantic_digest,
            output_digest=output_digest,
            route_identity=f"v4_callback_poc:{route}",
            expected_program_bundles=(program,),
        )
    except Exception:
        session.abort()
        raise
    if any(item["status"] != 0 for item in statuses) or any(value <= 0 for value in counts):
        raise RuntimeError("V4 callback validation status/counters are incomplete")
    if receipt["physical_executor_classification"] != "optix_traversal_observed":
        raise RuntimeError("V4 callback did not produce complete bound OptiX traversal")
    return V4CallbackPocResult(
        output_ids=tuple(item[0] for item in observed),
        output_t=tuple(item[1] for item in observed),
        callback_counters=counts,
        launch_status=statuses,
        traversal_receipt=receipt,
        output_sha256=output_digest,
        interpreter_output_sha256=interpreter_output_digest,
        route=route,
        wrapper_numeric_mode=wrapper_numeric_mode,
        leaf_numeric_modes=tuple(item.numeric_mode for item in ordered),
    )

#!/usr/bin/env python3
"""Unregistered CUDA-driver context-call microprobe for Goal5805."""

from __future__ import annotations

import ctypes
import json
import statistics
import time


def main() -> int:
    cuda = ctypes.CDLL("libcuda.so.1")
    cuda.cuInit.argtypes = [ctypes.c_uint]
    cuda.cuDeviceGet.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
    cuda.cuDevicePrimaryCtxRetain.argtypes = [
        ctypes.POINTER(ctypes.c_void_p), ctypes.c_int]
    cuda.cuCtxGetCurrent.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
    cuda.cuCtxSetCurrent.argtypes = [ctypes.c_void_p]
    for symbol in (
            cuda.cuInit, cuda.cuDeviceGet, cuda.cuDevicePrimaryCtxRetain,
            cuda.cuCtxGetCurrent, cuda.cuCtxSetCurrent):
        symbol.restype = ctypes.c_int
    if cuda.cuInit(0):
        raise RuntimeError("cuInit failed")
    device = ctypes.c_int()
    if cuda.cuDeviceGet(ctypes.byref(device), 0):
        raise RuntimeError("cuDeviceGet failed")
    primary = ctypes.c_void_p()
    if cuda.cuDevicePrimaryCtxRetain(ctypes.byref(primary), device):
        raise RuntimeError("cuDevicePrimaryCtxRetain failed")
    prior = ctypes.c_void_p()
    if cuda.cuCtxGetCurrent(ctypes.byref(prior)):
        raise RuntimeError("cuCtxGetCurrent failed")

    def sample(callable_, repetitions: int = 1000) -> int:
        values = []
        for _ in range(repetitions):
            start = time.perf_counter_ns()
            callable_()
            values.append(time.perf_counter_ns() - start)
        return int(statistics.median(values))

    observed = ctypes.c_void_p()

    def get_only() -> None:
        if cuda.cuCtxGetCurrent(ctypes.byref(observed)):
            raise RuntimeError("get failed")

    def switch_restore() -> None:
        if cuda.cuCtxGetCurrent(ctypes.byref(observed)):
            raise RuntimeError("get failed")
        if cuda.cuCtxSetCurrent(primary):
            raise RuntimeError("select failed")
        if cuda.cuCtxSetCurrent(observed):
            raise RuntimeError("restore failed")

    print(json.dumps({
        "schema": "rtdl.goal5805.cuda_context_microprobe.v1",
        "registered_performance_timing_count": 0,
        "scientific_claim_authorized": False,
        "prior_is_null": prior.value is None,
        "get_only_median_ns": sample(get_only),
        "get_select_restore_median_ns": sample(switch_restore),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

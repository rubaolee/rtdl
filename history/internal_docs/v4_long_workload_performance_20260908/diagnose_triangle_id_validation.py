#!/usr/bin/env python3
"""Unsafe diagnostic upper bound for device-column ID value validation.

This script deliberately replaces only the two CuPy value scans performed by
the V4 triangle device-column validator.  It preserves type, dtype, shape,
contiguity, size, and device checks.  Its output is diagnostic-only and cannot
be pooled into a formal transaction because canonical ID values are not
checked.  The production fix must fuse those checks into native pack work.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repetitions", type=int, default=3)
    return parser.parse_args()


def main() -> int:
    args = _args()
    if args.output.exists():
        raise FileExistsError(args.output)
    if args.warmups < 0 or args.repetitions <= 0:
        raise ValueError("invalid diagnostic repetition count")

    root = args.source_root.resolve(strict=True)
    config = dict(json.loads(args.config.read_text(encoding="utf-8")))
    config["source_root"] = str(root)

    import cupy as cp
    from rtdsl import v4_triangle_reduction_device_runtime as runtime
    from scripts import v4_paper_apps_pyoptix_worker as worker

    def structural_only(cp_module, columns, keys, *, floating):
        if cp_module is not cp:
            raise RuntimeError("diagnostic received an unexpected CuPy module")
        if set(columns) != set(keys):
            raise ValueError(f"device columns must contain exactly {keys!r}")
        result = {}
        count = None
        device_id = None
        for key in keys:
            value = columns[key]
            if not isinstance(value, cp.ndarray):
                raise TypeError(f"{key} must be an existing CuPy array")
            expected = cp.float64 if key in floating else cp.uint32
            if value.dtype != expected or value.ndim != 1 or not value.flags.c_contiguous:
                raise TypeError(
                    f"{key} must be contiguous one-dimensional {expected}")
            if count is None:
                count = int(value.size)
                device_id = int(value.device.id)
            elif int(value.size) != count or int(value.device.id) != device_id:
                raise ValueError("device columns must have one count and device")
            result[key] = value
        if not count:
            raise ValueError("device columns must be nonempty")
        return result, count, device_id

    runtime._device_columns = structural_only
    data, input_identity = worker._load_input(
        "triangle_counting", config, operation=None)
    execute, close, method = worker._prepare_case(
        "triangle_counting", "v4", config, data)
    samples = []
    digests = []
    try:
        for _ in range(args.warmups):
            if execute().get("matched") is not True:
                raise RuntimeError("diagnostic warmup output mismatch")
        for _ in range(args.repetitions):
            started = time.perf_counter_ns()
            observed = execute()
            samples.append(time.perf_counter_ns() - started)
            if observed.get("matched") is not True:
                raise RuntimeError("diagnostic output mismatch")
            digests.append(str(observed["output_sha256"]))
    finally:
        close()
    if len(set(digests)) != 1:
        raise RuntimeError("diagnostic output changed")

    payload = {
        "schema": "rtdl.v4_long_workload.triangle_id_validation_upper_bound.v1",
        "formal_evidence": False,
        "pooling_into_formal_transaction_forbidden": True,
        "unsafe_canonical_id_value_check_disabled": True,
        "production_fix_requires_fused_native_validation": True,
        "input_identity": input_identity,
        "method": method,
        "samples_ns": samples,
        "median_ns": int(statistics.median(samples)),
        "output_sha256": digests[0],
    }
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS_DIAGNOSTIC_ONLY", **payload}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

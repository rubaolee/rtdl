#!/usr/bin/env python3
"""Home-GPU correctness and non-formal diagnostic for Goal5778."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics
import sys
import time

import numpy as np


U64_MAX = (1 << 64) - 1


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--rtdbscan-input-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    import cupy as cp
    helper_path = args.source_root / "src/rtdsl/v4_checked_u64_device_reduction.py"
    spec = importlib.util.spec_from_file_location("goal5778_checked_reduction", helper_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load checked reduction helper")
    helper = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = helper
    spec.loader.exec_module(helper)
    checked_u64_weighted_sum_device = helper.checked_u64_weighted_sum_device

    # Real non-Triangle consumer: the frozen RT-DBSCAN input contract carries
    # route-independent exact per-point neighbor counts and their exact
    # directed-edge total.  This consumes the same checked device reduction
    # without changing the RT-DBSCAN production route or timing it.
    rtdbscan_root = args.rtdbscan_input_root.resolve()
    rtdbscan_manifest_path = rtdbscan_root / "MANIFEST.json"
    rtdbscan_manifest = json.loads(rtdbscan_manifest_path.read_text(encoding="utf-8"))
    if rtdbscan_manifest.get("schema") != "rtdl.goal5776.rtdbscan_real_scale_input.v1":
        raise ValueError("unexpected RT-DBSCAN input schema")
    member = rtdbscan_manifest["members"]["neighbor_counts_u32.npy"]
    counts_path = rtdbscan_root / "neighbor_counts_u32.npy"
    if counts_path.stat().st_size != int(member["bytes"]) or sha(counts_path) != member["sha256"]:
        raise RuntimeError("RT-DBSCAN neighbor-count member identity mismatch")
    counts_host = np.load(counts_path, allow_pickle=False)
    if counts_host.dtype != np.uint32 or list(counts_host.shape) != member["shape"]:
        raise RuntimeError("RT-DBSCAN neighbor-count array contract mismatch")
    counts_device = cp.asarray(counts_host, dtype=cp.uint64)
    unit_weights = cp.ones(counts_device.shape, dtype=cp.uint64)
    rtdbscan_reduction = checked_u64_weighted_sum_device(
        counts_device,
        unit_weights,
        value_upper_bound=int(rtdbscan_manifest["oracle"]["neighbor_count_max"]),
    )
    expected_edge_count = int(rtdbscan_manifest["oracle"]["directed_edge_count"])
    if rtdbscan_reduction.value != expected_edge_count:
        raise AssertionError("RT-DBSCAN directed-edge total mismatch")
    rtdbscan_consumer = {
        "consumer": "RT-DBSCAN route-independent exact directed-edge total",
        "input_manifest_sha256": sha(rtdbscan_manifest_path),
        "neighbor_counts_sha256": sha(counts_path),
        "point_count": int(counts_host.size),
        "maximum_neighbor_count": rtdbscan_reduction.maximum_value,
        "directed_edge_count": rtdbscan_reduction.value,
        "expected_directed_edge_count": expected_edge_count,
        "exact": True,
        "same_checked_reduction_contract": True,
        "production_route_changed": False,
        "performance_observation_created": False,
    }

    exact_cases = []
    for count in (1, 257, 65_536, 1_000_000):
        indices = cp.arange(count, dtype=cp.uint64)
        values = (indices * cp.uint64(5) + cp.uint64(3)) % cp.uint64(17)
        weights = (indices * cp.uint64(7) + cp.uint64(2)) % cp.uint64(23)
        result = checked_u64_weighted_sum_device(
            values, weights, value_upper_bound=16)
        values_host = values.get().tolist()
        weights_host = weights.get().tolist()
        expected = sum(int(a) * int(b) for a, b in zip(values_host, weights_host, strict=True))
        if result.value != expected:
            raise AssertionError((count, result.value, expected))
        if result.maximum_value != max(int(x) for x in values_host):
            raise AssertionError("maximum-value mismatch")
        if result.maximum_weight != max(int(x) for x in weights_host):
            raise AssertionError("maximum-weight mismatch")
        if result.weight_sum != sum(int(x) for x in weights_host):
            raise AssertionError("weight-sum mismatch")
        exact_cases.append({
            "count": count,
            "exact": True,
            "value": result.value,
            "maximum_value": result.maximum_value,
            "maximum_weight": result.maximum_weight,
            "weight_sum": result.weight_sum,
            "device_kernel_launch_count": result.device_kernel_launch_count,
            "host_synchronization_count": result.host_synchronization_count,
        })

    attacks = []
    for name, values, weights, upper, expected_message in (
        (
            "weight_sum_bound",
            cp.ones(2, dtype=cp.uint64),
            cp.asarray([U64_MAX, U64_MAX], dtype=cp.uint64),
            1,
            "query-weight domain",
        ),
        (
            "weighted_value_bound",
            cp.ones(2, dtype=cp.uint64),
            cp.asarray([U64_MAX // 2, U64_MAX // 2], dtype=cp.uint64),
            2,
            "weighted hit-count",
        ),
    ):
        try:
            checked_u64_weighted_sum_device(
                values, weights, value_upper_bound=upper)
        except OverflowError as error:
            if expected_message not in str(error):
                raise
            attacks.append({"attack": name, "failed_closed": True, "message": str(error)})
        else:
            raise AssertionError(f"{name} did not fail closed")

    try:
        checked_u64_weighted_sum_device(
            cp.asarray([8, 1], dtype=cp.uint64),
            cp.asarray([1, 1], dtype=cp.uint64),
            value_upper_bound=7,
        )
    except ValueError as error:
        if "device values exceed declared upper bound" not in str(error):
            raise
        attacks.append({
            "attack": "value_exceeds_declared_bound",
            "failed_closed": True,
            "message": str(error),
        })
    else:
        raise AssertionError("value-exceeds-bound attack did not fail closed")

    count = 1_000_000
    indices = cp.arange(count, dtype=cp.uint64)
    values = (indices * cp.uint64(5) + cp.uint64(3)) % cp.uint64(17)
    weights = (indices * cp.uint64(7) + cp.uint64(2)) % cp.uint64(23)

    def old_path() -> int:
        maximum_weight = int(cp.max(weights).item())
        if maximum_weight and count > U64_MAX // maximum_weight:
            raise OverflowError
        weight_sum = int(cp.sum(weights, dtype=cp.uint64).item())
        if weight_sum and 16 > U64_MAX // weight_sum:
            raise OverflowError
        return int(cp.sum(values * weights, dtype=cp.uint64).item())

    def new_path() -> int:
        return checked_u64_weighted_sum_device(
            values, weights, value_upper_bound=16).value

    for _ in range(3):
        if old_path() != new_path():
            raise AssertionError("warm-up paths disagree")
    old_seconds, new_seconds = [], []
    for _ in range(12):
        started = time.perf_counter(); old_value = old_path(); old_seconds.append(time.perf_counter() - started)
        started = time.perf_counter(); new_value = new_path(); new_seconds.append(time.perf_counter() - started)
        if old_value != new_value:
            raise AssertionError("diagnostic paths disagree")

    old_median = float(statistics.median(old_seconds))
    new_median = float(statistics.median(new_seconds))
    properties = cp.cuda.runtime.getDeviceProperties(0)
    device_name = properties["name"]
    if isinstance(device_name, bytes):
        device_name = device_name.decode()
    capability = cp.cuda.Device().compute_capability
    if isinstance(capability, str):
        capability = f"{capability[0]}.{capability[1:]}"
    else:
        capability = ".".join(str(value) for value in capability)
    result = {
        "schema": "rtdl.goal5778.home_checked_u64_reduction_validation.v1",
        "claim_boundary": {
            "functional_and_diagnostic_only": True,
            "registered_performance_result": False,
            "target_rtx_saving_predicted": False,
            "paper_app_result_created": False,
            "pod_used": False,
        },
        "gpu": {
            "device_name": str(device_name),
            "compute_capability": capability,
            "cupy_version": cp.__version__,
        },
        "source": {
            "helper_sha256": sha(args.source_root / "src/rtdsl/v4_checked_u64_device_reduction.py"),
        },
        "exact_cases": exact_cases,
        "real_non_triangle_consumer": rtdbscan_consumer,
        "attacks": attacks,
        "diagnostic_only": {
            "count": count,
            "repeat_count": 12,
            "old_three_reduction_median_seconds": old_median,
            "new_fused_reduction_median_seconds": new_median,
            "old_over_new_median_ratio": old_median / new_median,
            "not_a_target_prediction": True,
        },
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

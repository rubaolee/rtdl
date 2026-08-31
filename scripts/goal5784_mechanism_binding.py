#!/usr/bin/env python3
"""Pure validation for Goal5784 per-worker mechanism evidence."""

from __future__ import annotations

import hashlib
import json


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def validate_triangle_reduction_receipts(
    receipts: list[dict[str, object]],
) -> dict[str, object]:
    if not receipts:
        raise RuntimeError("Goal5784 Triangle V4 omitted reduction receipts")
    for receipt in receipts:
        if (
            receipt.get("schema")
                != "rtdl.v4.checked_u64_weighted_reduction.receipt.v1"
            or receipt.get("device_kernel_launch_count") != 1
            or receipt.get("host_synchronization_count") != 1
            or receipt.get("provisional_sum_trusted_only_after_bounds") is not True
            or not isinstance(receipt.get("maximum_value"), int)
            or not isinstance(receipt.get("maximum_weight"), int)
            or not isinstance(receipt.get("weight_sum"), int)
            or not isinstance(receipt.get("value_count"), int)
            or not isinstance(receipt.get("value_upper_bound"), int)
        ):
            raise RuntimeError("Goal5784 Triangle reduction receipt is incomplete")
    return {
        "schema": "rtdl.goal5784.mechanism_binding.v1",
        "mechanism_id": "compiler_fused_checked_u64_device_reduction",
        "evidence_level": "actual_per_segment_device_reduction_receipts",
        "segment_count": len(receipts),
        "reduction_receipts_sha256": _digest(receipts),
        "all_segments_one_device_kernel_one_host_sync": True,
        "all_segments_bounds_validated_before_sum_trust": True,
        "observation_outside_registered_endpoint_timer": True,
    }


__all__ = ["validate_triangle_reduction_receipts"]

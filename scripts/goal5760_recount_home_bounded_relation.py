#!/usr/bin/env python3
"""Independent raw recount for Goal5760; imports no product/compiler/runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relation(sources, indexed, threshold):
    rows = []
    for source in sources:
        for item in indexed:
            dx = max(0.0, min(source[2], item[2]) - max(source[0], item[0]))
            dy = max(0.0, min(source[3], item[3]) - max(source[1], item[1]))
            closed = (item[0] <= source[2] and item[2] >= source[0]
                      and item[1] <= source[3] and item[3] >= source[1])
            if closed and dx * dy >= threshold:
                rows.append((int(source[4]), int(item[4])))
    return tuple(sorted(set(rows)))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result_path = args.raw / "RESULT.json"
    native_path = args.raw / "librtdl_optix.so"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if _sha(native_path) != result["native_library_sha256"]:
        raise RuntimeError("copied native bytes do not match result identity")
    rows = []
    for lane in result["lanes"]:
        expected = _relation(
            lane["source_boxes"], lane["indexed_boxes"],
            float(lane["minimum_overlap_f32"]))
        observed = tuple(tuple(item) for item in lane["observed_rows"])
        raw = tuple(tuple(item) for item in lane["raw_rows"])
        if expected != observed or tuple(sorted(set(raw))) != observed:
            raise RuntimeError(f"independent relation mismatch: {lane['lane']}")
        if len(raw) != lane["raw_event_count"] \
                or len(raw) - len(observed) != lane["duplicate_count"]:
            raise RuntimeError(f"raw count mismatch: {lane['lane']}")
        snapshot = lane["traversal_receipt"]["native_snapshot"]
        if lane["traversal_receipt"]["physical_executor_classification"] \
                != "optix_traversal_observed" \
                or snapshot["successful_launch_count"] != 2 \
                or snapshot["complete_context_launch_count"] != 2 \
                or snapshot["failed_launch_count"] \
                or snapshot["incomplete_context_launch_count"] \
                or snapshot["pending_context_at_finish"] \
                or snapshot["session_error"]:
            raise RuntimeError(f"behavioral receipt mismatch: {lane['lane']}")
        rows.append({
            "lane": lane["lane"], "expected_rows": expected,
            "raw_event_count": len(raw),
            "duplicate_count": len(raw) - len(observed),
            "exact": True, "behavioral_true_optix": True,
        })
    attack = result["overflow_attack"]
    if not attack["passed"] or attack["observed_code"] != "capacity_overflow" \
            or "raw_count=" not in attack["observed_message"]:
        raise RuntimeError("overflow attack did not independently attest rejection")
    recount = {
        "schema": "rtdl.goal5760.independent_home_bounded_relation_recount.v1",
        "raw_result_sha256": _sha(result_path),
        "native_library_sha256": _sha(native_path),
        "lane_count": len(rows),
        "exact_output_count": sum(item["exact"] for item in rows),
        "behavioral_true_optix_count": sum(
            item["behavioral_true_optix"] for item in rows),
        "overflow_attack_passed": True,
        "imports_product_compiler_or_runtime": False,
        "lanes": rows,
    }
    args.output.write_text(
        json.dumps(recount, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(recount, sort_keys=True))


if __name__ == "__main__":
    main()

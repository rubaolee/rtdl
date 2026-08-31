#!/usr/bin/env python3
"""One untimed Home probe of the Goal5784 Triangle mechanism capture path."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from goal5784_targeted_formal_contract import PREPARED, V4
from goal5784_targeted_worker import run_endpoint_with_mechanism_binding


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--edge-file", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    os.environ["RTDL_OPTIX_LIB"] = str(args.native.resolve())
    os.environ["RTDL_OPTIX_LIBRARY"] = str(args.native.resolve())
    runtime = {
        "source_root": str(args.source_root.resolve()),
        "native_library_path": str(args.native.resolve()),
        "compute_capability": [6, 1], "optix_sdk_version": "9.0.0",
        "optix_include": str(args.optix_include.resolve()),
        "cuda_include": str(args.cuda_include.resolve()),
        "execution_source_sha256": "home_probe__not_formal",
        "inputs": {
            "triangle__com_dblp__rt_2a1": {
                "edge_file": str(args.edge_file.resolve()),
                "expected_triangle_count": 2_224_385,
                "max_relation_rows": 1_000_000,
            },
        },
    }
    endpoint = run_endpoint_with_mechanism_binding(
        unit_id="triangle__com_dblp__rt_2a1", method=V4,
        lifecycle=PREPARED, runtime=runtime)
    binding = endpoint["goal5784_mechanism_binding"]
    if endpoint.get("matched") is not True or (
        binding.get("mechanism_id")
            != "compiler_fused_checked_u64_device_reduction"
        or binding.get("evidence_level")
            != "actual_per_segment_device_reduction_receipts"
        or binding.get("observation_outside_registered_endpoint_timer") is not True
    ):
        raise RuntimeError("Goal5784 Home mechanism capture failed")
    result = {
        "schema": "rtdl.goal5784.home_mechanism_probe.v1",
        "unit_id": "triangle__com_dblp__rt_2a1",
        "method": V4, "lifecycle": PREPARED,
        "correct": True,
        "behavioral_true_optix": True,
        "mechanism_binding": binding,
        "registered_performance_timing_retained": False,
        "formal_worker": False,
        "modern_rtx_or_performance_claimed": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8", newline="\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

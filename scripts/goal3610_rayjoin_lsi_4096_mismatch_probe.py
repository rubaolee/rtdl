#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from examples.benchmark_apps.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    run_rayjoin_prepared_optix_left_id_dense_count_workload,
)
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import (  # noqa: E402
    LSI_COUNT_KERNEL,
)
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import (  # noqa: E402
    _load_rayjoin_case,
)
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import (  # noqa: E402
    _segment_array,
)


SCHEMA = "rtdl.goal3610.rayjoin_lsi_4096_count_mismatch_probe.v1"
DEFAULT_DATASET = (
    f"{ROOT / 'data' / 'rayjoin_public_cdb' / 'br_county_start256_count4096.cdb'}"
    " + "
    f"{ROOT / 'data' / 'rayjoin_public_cdb' / 'br_soil_start256_count4096.cdb'}"
)
DEFAULT_OUTPUT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3610_rayjoin_lsi_4096_count_mismatch_probe_a5000"
    / "summary.json"
)


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _claim_boundary() -> dict[str, bool]:
    return {
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rayjoin_paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "native_default_route_authorized": False,
    }


def run_probe(dataset: str) -> dict[str, object]:
    import numpy as np
    import cupy as cp  # type: ignore

    print("[goal3610] load LSI compact-column case", flush=True)
    case = _load_rayjoin_case("lsi", dataset, segment_column_inputs=True)
    left = case.inputs["left"]
    right = case.inputs["right"]
    left_ids = np.asarray(left.ids, dtype=np.int64)
    left_count = int(left.count)
    right_count = int(right.count)
    pair_count = left_count * right_count
    print(f"[goal3610] left={left_count} right={right_count} pairs={pair_count}", flush=True)

    left_array = _segment_array(left, np)
    right_array = _segment_array(right, np)

    print("[goal3610] CuPy upload/flag allocation", flush=True)
    upload_start = time.perf_counter()
    left_gpu = cp.asarray(left_array)
    right_gpu = cp.asarray(right_array)
    flags = cp.zeros((pair_count,), dtype=cp.uint8)
    cp.cuda.Stream.null.synchronize()
    upload_alloc_sec = time.perf_counter() - upload_start

    kernel = cp.RawKernel(LSI_COUNT_KERNEL, "rtdl_goal3589_lsi_count_flags")
    threads = 256
    blocks = (pair_count + threads - 1) // threads
    print("[goal3610] CuPy dense all-pairs launch", flush=True)
    cupy_start = time.perf_counter()
    kernel(
        (blocks,),
        (threads,),
        (
            left_gpu,
            right_gpu,
            left_count,
            right_count,
            flags,
        ),
    )
    cp.cuda.Stream.null.synchronize()
    cupy_kernel_sec = time.perf_counter() - cupy_start

    print("[goal3610] CuPy per-left reduction", flush=True)
    reduce_start = time.perf_counter()
    cupy_counts = cp.asnumpy(flags.reshape((left_count, right_count)).sum(axis=1)).astype(np.int64)
    cupy_reduce_sec = time.perf_counter() - reduce_start
    cupy_total = int(cupy_counts.sum())
    del flags
    cp.get_default_memory_pool().free_all_blocks()

    print("[goal3610] RTDL/OptiX include_rows dense left-id count", flush=True)
    optix_start = time.perf_counter()
    payload = run_rayjoin_prepared_optix_left_id_dense_count_workload(
        "lsi",
        dataset=dataset,
        include_rows=True,
        query_repeat=1,
        warmup=0,
    )
    optix_include_rows_sec = time.perf_counter() - optix_start
    rtdl_total = int(payload["row_count"])

    rtdl_by_left_id = {int(row["left_id"]): int(row["count"]) for row in payload.get("rows", [])}
    diffs: list[dict[str, object]] = []
    for index, left_id in enumerate(left_ids):
        cupy_count = int(cupy_counts[index])
        rtdl_count = int(rtdl_by_left_id.get(int(left_id), 0))
        if cupy_count != rtdl_count:
            diffs.append(
                {
                    "left_index": int(index),
                    "left_id": int(left_id),
                    "cupy": cupy_count,
                    "rtdl_optix": rtdl_count,
                    "delta": rtdl_count - cupy_count,
                    "segment": [float(value) for value in left_array[index].tolist()],
                }
            )

    return {
        "schema": SCHEMA,
        "goal": 3610,
        "generated_at_unix": time.time(),
        "git_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "git_status_short": _command_output(["git", "status", "--short"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "dataset": dataset,
        "workload": "lsi",
        "output_contract": "segment_segment_intersection_count_by_left_id_dense_device_column",
        "left_segment_count": left_count,
        "right_segment_count": right_count,
        "candidate_pair_count": pair_count,
        "cupy_total": cupy_total,
        "rtdl_optix_total": rtdl_total,
        "diff_count": len(diffs),
        "delta_sum": sum(int(row["delta"]) for row in diffs),
        "diff_sample": diffs[:20],
        "diagnostic_timing_sec": {
            "cupy_upload_alloc": upload_alloc_sec,
            "cupy_dense_kernel": cupy_kernel_sec,
            "cupy_per_left_reduce": cupy_reduce_sec,
            "rtdl_optix_include_rows": optix_include_rows_sec,
        },
        "interpretation": (
            "Diagnostic only: the 4096-chain mixed RayJoin composite is blocked because "
            "the dense CuPy LSI baseline and the RTDL/OptiX dense left-id count route do "
            "not yet share an exact near-degenerate segment policy."
        ),
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3610 RayJoin LSI 4096 mismatch probe.")
    parser.add_argument("--dataset", default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = run_probe(args.dataset)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3610] wrote {args.output}", flush=True)
    print(json.dumps({key: payload[key] for key in ("cupy_total", "rtdl_optix_total", "diff_count", "delta_sum")}, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

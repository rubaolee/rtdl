from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def _gpu_name() -> str:
    try:
        return subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).splitlines()[0].strip()
    except Exception:
        return "unknown"


def _build_adapter(operation: str):
    return rt.build_segmented_typed_stream_adapter(
        ((0, 1.0),),
        row_schema=("group_ids", "values"),
        column_roles={"group_ids": "group_key", "values": "score"},
        page_capacity=1,
        stream_id=f"goal3145_{operation}",
        stream_kind="grouped_reduction_stream",
        producer_primitive="segmented_row_stream_reference",
        ordering="group_ordered",
        operation=operation,
        group_column="group_ids",
        value_columns=("values",),
        user_selected_partner="numba",
    )


def _run_case(*, operation: str, row_count: int, group_count: int) -> dict[str, object]:
    try:
        import _numba_cuda_redirector  # noqa: F401
    except ImportError:
        pass
    from numba import cuda

    print(f"[goal3145] running operation={operation} rows={row_count} groups={group_count}", flush=True)
    group_ids_host = np.arange(row_count, dtype=np.int64) % int(group_count)
    values_host = (group_ids_host.astype(np.float64) * 0.5) + ((np.arange(row_count) % 17).astype(np.float64) * 0.125)
    group_ids = cuda.to_device(group_ids_host)
    values = cuda.to_device(values_host.astype(np.float64, copy=False))
    adapter = _build_adapter(operation)
    started = time.perf_counter()
    result = rt.execute_segmented_typed_stream_partner_continuation(
        adapter,
        partner="numba",
        partner_columns={"group_ids": group_ids, "values": values},
        group_count=int(group_count),
    )
    elapsed = time.perf_counter() - started
    outputs = result["outputs"]
    expected = []
    for group in range(group_count):
        group_values = values_host[group_ids_host == group]
        if operation == "segmented_min_f64":
            expected.append(float(group_values.min()))
        else:
            expected.append(float(group_values.max()))
    value_name = "mins" if operation == "segmented_min_f64" else "maxes"
    observed = [float(value) for value in outputs[value_name]]
    max_abs_error = max(abs(left - right) for left, right in zip(observed, expected)) if expected else 0.0
    return {
        "operation": operation,
        "row_count": int(row_count),
        "group_count": int(group_count),
        "elapsed_sec": elapsed,
        "output_group_count": len(outputs["group_ids"]),
        "missing_group_count": len(outputs["missing_group_ids"]),
        "max_abs_error": max_abs_error,
        "matches_reference": max_abs_error <= 1.0e-12 and len(outputs["missing_group_ids"]) == 0,
        "canonical_output_host_compaction_used": bool(
            result["partner_metadata"]["canonical_output_host_compaction_used"]
        ),
        "partner_consumer_promoted": bool(result["partner_consumer_promoted"]),
        "release_authorized": bool(result["release_authorized"]),
        "public_speedup_claim_authorized": bool(result["public_speedup_claim_authorized"]),
        "rt_core_speedup_claim_authorized": bool(result["rt_core_speedup_claim_authorized"]),
        "true_zero_copy_claim_authorized": bool(result["true_zero_copy_claim_authorized"]),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal3145 segmented min/max front-door pod probe")
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--row-count", type=int, nargs="+", default=[65536, 1048576])
    parser.add_argument("--group-count", type=int, default=1024)
    args = parser.parse_args(argv)

    rows = [
        _run_case(operation=operation, row_count=int(row_count), group_count=int(args.group_count))
        for row_count in args.row_count
        for operation in ("segmented_min_f64", "segmented_max_f64")
    ]
    payload = {
        "goal": "Goal3145",
        "commit": _git_commit(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "gpu": _gpu_name(),
        "rows": rows,
        "all_match": all(bool(row["matches_reference"]) for row in rows),
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "v2_8_release_authorized": False,
        },
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[goal3145] wrote {args.json_out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

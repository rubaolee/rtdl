from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from time import perf_counter

import numpy as np

import rtdsl as rt


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def _build_adapter(row_count: int) -> object:
    return rt.build_segmented_typed_stream_adapter(
        ((0, 0, True),),
        row_schema=("group_ids", "values", "mask"),
        column_roles={"group_ids": "group_key", "values": "item_id", "mask": "mask"},
        page_capacity=1,
        stream_id=f"goal3147_compact_mask_{row_count}",
        stream_kind="candidate_stream",
        producer_primitive="segmented_row_stream_reference",
        ordering="stable_row_order",
        operation="compact_mask_i64",
        group_column="group_ids",
        value_columns=("values", "mask"),
        user_selected_partner="numba",
    )


def _as_host(values: object) -> np.ndarray:
    if hasattr(values, "copy_to_host"):
        return np.asarray(values.copy_to_host())
    if hasattr(values, "detach") and hasattr(values, "cpu"):
        return np.asarray(values.detach().cpu().numpy())
    if hasattr(values, "get"):
        return np.asarray(values.get())
    return np.asarray(values)


def _run_case(cuda: object, row_count: int, modulo: int, keep_lt: int) -> dict[str, object]:
    values_host = np.arange(row_count, dtype=np.int64)
    mask_host = (values_host % modulo) < keep_lt
    values = cuda.to_device(values_host)
    mask = cuda.to_device(mask_host.astype(np.bool_))
    adapter = _build_adapter(row_count)

    started = perf_counter()
    result = rt.execute_segmented_typed_stream_partner_continuation(
        adapter,
        partner="numba",
        partner_columns={"values": values, "mask": mask},
    )
    elapsed = perf_counter() - started
    out_values = _as_host(result["outputs"]["values"])
    out_indices = _as_host(result["outputs"]["original_indices"])
    expected_values = values_host[mask_host]
    expected_indices = np.nonzero(mask_host)[0].astype(np.int64)
    metadata = result["partner_metadata"]

    return {
        "row_count": int(row_count),
        "modulo": int(modulo),
        "keep_lt": int(keep_lt),
        "selected_count": int(expected_values.size),
        "elapsed_sec": float(elapsed),
        "values_match_reference": bool(np.array_equal(out_values, expected_values)),
        "indices_match_reference": bool(np.array_equal(out_indices, expected_indices)),
        "stable_input_order": bool(metadata["stable_input_order"]),
        "host_prefix_sum_used": bool(metadata["host_prefix_sum_used"]),
        "canonical_output_schema": list(metadata["canonical_output_schema"]),
        "partner_consumer_promoted": bool(result["partner_consumer_promoted"]),
        "release_authorized": bool(result["release_authorized"]),
        "public_speedup_claim_authorized": bool(result["public_speedup_claim_authorized"]),
        "rt_core_speedup_claim_authorized": bool(result["rt_core_speedup_claim_authorized"]),
        "true_zero_copy_claim_authorized": bool(result["true_zero_copy_claim_authorized"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--row-count", type=int, nargs="+", default=[1_000_000, 4_000_000])
    parser.add_argument("--modulo", type=int, default=13)
    parser.add_argument("--keep-lt", type=int, default=3)
    parser.add_argument("--warmup-rows", type=int, default=4096)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()

    from numba import cuda

    if args.warmup_rows:
        print(f"[goal3147] warmup rows={args.warmup_rows}", flush=True)
        _run_case(cuda, int(args.warmup_rows), int(args.modulo), int(args.keep_lt))

    rows = []
    for row_count in args.row_count:
        print(f"[goal3147] running rows={row_count} modulo={args.modulo} keep_lt={args.keep_lt}", flush=True)
        rows.append(_run_case(cuda, int(row_count), int(args.modulo), int(args.keep_lt)))

    payload = {
        "goal": "Goal3147",
        "commit": _git_commit(),
        "gpu": cuda.get_current_device().name.decode()
        if isinstance(cuda.get_current_device().name, bytes)
        else str(cuda.get_current_device().name),
        "all_match": all(row["values_match_reference"] and row["indices_match_reference"] for row in rows),
        "rows": rows,
        "claim_boundary": {
            "v2_8_release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[goal3147] wrote {args.json_out}", flush=True)


if __name__ == "__main__":
    main()

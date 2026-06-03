from __future__ import annotations

import argparse
import json
import socket
import subprocess
from pathlib import Path
from statistics import median
from time import perf_counter
from typing import Any

import numpy as np

from rtdsl.numba_partner_continuation import run_numba_grouped_argmax_f64
from rtdsl.numba_partner_continuation import run_numba_grouped_argmin_f64
from rtdsl.partner_adapters import grouped_argmax_f64_partner_columns
from rtdsl.partner_adapters import grouped_argmin_f64_partner_columns


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def _nvidia_smi() -> str:
    try:
        return subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            text=True,
        ).strip()
    except Exception:
        return "unavailable"


def _make_columns(cuda: Any, row_count: int, group_count: int) -> dict[str, Any]:
    host_rows = np.arange(row_count, dtype=np.int64)
    group_ids = np.mod(host_rows, int(group_count)).astype(np.int64)
    item_ids = host_rows.astype(np.int64)
    scores = ((host_rows * 1103515245 + 12345) % 1000003).astype(np.float64)
    scores = scores / 1000003.0
    return {
        "group_ids": cuda.to_device(group_ids),
        "item_ids": cuda.to_device(item_ids),
        "scores": cuda.to_device(scores),
    }


def _run_case(
    *,
    operation: str,
    layer: str,
    columns: dict[str, Any],
    group_count: int,
    validate_group_ids: bool,
    validate_nan_scores: bool,
    compact_present_groups: bool,
    repetitions: int,
) -> dict[str, Any]:
    if operation == "grouped_argmin_f64" and layer == "direct":
        call = lambda: run_numba_grouped_argmin_f64(
            columns["group_ids"],
            columns["item_ids"],
            columns["scores"],
            group_count=group_count,
            validate_group_ids=validate_group_ids,
            validate_nan_scores=validate_nan_scores,
            compact_present_groups=compact_present_groups,
        )
    elif operation == "grouped_argmax_f64" and layer == "direct":
        call = lambda: run_numba_grouped_argmax_f64(
            columns["group_ids"],
            columns["item_ids"],
            columns["scores"],
            group_count=group_count,
            validate_group_ids=validate_group_ids,
            validate_nan_scores=validate_nan_scores,
            compact_present_groups=compact_present_groups,
        )
    elif operation == "grouped_argmin_f64" and layer == "partner_adapter":
        call = lambda: grouped_argmin_f64_partner_columns(
            columns,
            group_count=group_count,
            partner="numba",
            validate_group_ids=validate_group_ids,
            validate_nan_scores=validate_nan_scores,
            compact_present_groups=compact_present_groups,
            return_metadata=True,
        )
    elif operation == "grouped_argmax_f64" and layer == "partner_adapter":
        call = lambda: grouped_argmax_f64_partner_columns(
            columns,
            group_count=group_count,
            partner="numba",
            validate_group_ids=validate_group_ids,
            validate_nan_scores=validate_nan_scores,
            compact_present_groups=compact_present_groups,
            return_metadata=True,
        )
    else:
        raise ValueError(f"unsupported case: {operation} {layer}")

    warm_start = perf_counter()
    warm_result = call()
    warm_seconds = perf_counter() - warm_start
    steady: list[float] = []
    partner_elapsed: list[float | None] = []
    for _ in range(repetitions):
        started = perf_counter()
        result = call()
        steady.append(perf_counter() - started)
        metadata = result.get("metadata", result) if isinstance(result, dict) else {}
        phases = metadata.get("phase_timing", {}).get("phases_sec", {}) if isinstance(metadata, dict) else {}
        partner_elapsed.append(phases.get("partner_continuation"))
    metadata = warm_result.get("metadata", warm_result) if isinstance(warm_result, dict) else {}
    return {
        "operation": operation,
        "layer": layer,
        "validate_group_ids": validate_group_ids,
        "validate_nan_scores": validate_nan_scores,
        "compact_present_groups": compact_present_groups,
        "warm_seconds": warm_seconds,
        "steady_seconds": steady,
        "steady_median_seconds": median(steady),
        "partner_elapsed_seconds": partner_elapsed,
        "metadata": metadata,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument(
        "--sizes",
        default="65536:1024,262144:4096,1048576:16384",
        help="comma separated row_count:group_count pairs",
    )
    args = parser.parse_args()

    from numba import cuda

    cases: list[dict[str, Any]] = []
    for shape in args.sizes.split(","):
        row_count_text, group_count_text = shape.split(":", 1)
        row_count = int(row_count_text)
        group_count = int(group_count_text)
        print(f"[goal3139] preparing row_count={row_count} group_count={group_count}", flush=True)
        columns = _make_columns(cuda, row_count, group_count)
        for operation in ("grouped_argmin_f64", "grouped_argmax_f64"):
            for layer in ("direct", "partner_adapter"):
                for label, validate_group_ids, validate_nan_scores, compact_present_groups in (
                    ("default_compact", True, True, True),
                    ("no_validate_dense", False, False, False),
                ):
                    print(f"[goal3139] case {operation} {layer} {label}", flush=True)
                    case = _run_case(
                        operation=operation,
                        layer=layer,
                        columns=columns,
                        group_count=group_count,
                        validate_group_ids=validate_group_ids,
                        validate_nan_scores=validate_nan_scores,
                        compact_present_groups=compact_present_groups,
                        repetitions=int(args.repetitions),
                    )
                    case.update({"label": label, "row_count": row_count, "group_count": group_count})
                    print(
                        f"[goal3139] median {case['steady_median_seconds']:.6f}s "
                        f"warm {case['warm_seconds']:.6f}s",
                        flush=True,
                    )
                    cases.append(case)

    output = {
        "goal": "Goal3139",
        "status": "completed",
        "claim_boundary": "diagnostic_timing_not_speedup_claim",
        "host": socket.gethostname(),
        "gpu": _nvidia_smi(),
        "commit": _git_head(),
        "cases": cases,
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3139] wrote {path}", flush=True)


if __name__ == "__main__":
    main()

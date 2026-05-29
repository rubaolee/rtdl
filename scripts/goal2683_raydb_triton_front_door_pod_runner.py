#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import statistics
import subprocess
from pathlib import Path
from time import perf_counter
from typing import Any, Callable

import rtdsl as rt
from examples.v2_0.research_benchmarks.raydb_style import (
    rtdl_raydb_style_benchmark_app as raydb_app,
)


ROOT = Path(__file__).resolve().parents[1]


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def _parse_row_counts(text: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in text.split(",") if item.strip())
    if not values:
        raise ValueError("row-counts must contain at least one integer")
    if any(value <= 0 for value in values):
        raise ValueError("row-counts must be positive")
    return values


def _median(values: list[float]) -> float:
    return float(statistics.median(values)) if values else 0.0


def _time_cuda(callable_obj: Callable[[], Any], *, torch, repeats: int) -> tuple[Any, float]:
    elapsed: list[float] = []
    last = None
    for _ in range(int(repeats)):
        torch.cuda.synchronize()
        started = perf_counter()
        last = callable_obj()
        torch.cuda.synchronize()
        elapsed.append(perf_counter() - started)
    return last, _median(elapsed)


def _torch_sum(torch, keys, values, group_count: int):
    out = torch.zeros((int(group_count),), dtype=values.dtype, device=values.device)
    if int(keys.numel()):
        out.scatter_add_(0, keys.to(torch.int64), values)
    return out


def _torch_minmax(torch, keys, values, group_count: int, *, reduce: str, initial: float):
    out = torch.full((int(group_count),), float(initial), dtype=values.dtype, device=values.device)
    if int(keys.numel()):
        out.scatter_reduce_(0, keys.to(torch.int64), values, reduce=reduce, include_self=True)
    return out


def _make_inputs(row_count: int, group_count: int, *, torch) -> dict[str, Any]:
    device = torch.device("cuda:0")
    row_ids = torch.arange(int(row_count), dtype=torch.int64, device=device)
    group_ids = ((row_ids * 17 + row_ids // 97 + 11) % int(group_count)).to(torch.int64)
    values = (row_ids.to(torch.float64) * 0.125 + ((row_ids % 31).to(torch.float64) + 1.0)).to(torch.float64)
    return {"group_ids": group_ids, "values": values, "group_count": int(group_count)}


def _case(row_count: int, group_count: int, repeats: int, *, torch) -> dict[str, object]:
    inputs = _make_inputs(row_count, group_count, torch=torch)
    keys = inputs["group_ids"]
    values = inputs["values"]

    mode_rows: list[dict[str, object]] = []
    for mode in ("count", "sum", "min", "max", "avg_as_sum_count"):
        result, front_door_sec = _time_cuda(
            lambda mode=mode: raydb_app.run_raydb_v2_5_partner_continuation_preview(
                mode,
                inputs,
                partner="triton",
                allow_reference_fallback=False,
            ),
            torch=torch,
            repeats=repeats,
        )

        if mode == "count":
            torch_output, torch_sec = _time_cuda(
                lambda: torch.bincount(keys, minlength=group_count).to(torch.uint32),
                torch=torch,
                repeats=repeats,
            )
            correct = bool(torch.equal(result["outputs"]["counts"], torch_output))
        elif mode == "sum":
            torch_output, torch_sec = _time_cuda(
                lambda: _torch_sum(torch, keys, values, group_count),
                torch=torch,
                repeats=repeats,
            )
            correct = bool(torch.allclose(result["outputs"]["sums"], torch_output))
        elif mode == "min":
            torch_output, torch_sec = _time_cuda(
                lambda: _torch_minmax(torch, keys, values, group_count, reduce="amin", initial=float("inf")),
                torch=torch,
                repeats=repeats,
            )
            correct = bool(torch.allclose(result["outputs"]["dense_mins"], torch_output))
        elif mode == "max":
            torch_output, torch_sec = _time_cuda(
                lambda: _torch_minmax(torch, keys, values, group_count, reduce="amax", initial=float("-inf")),
                torch=torch,
                repeats=repeats,
            )
            correct = bool(torch.allclose(result["outputs"]["dense_maxes"], torch_output))
        else:
            torch_sums, torch_sum_sec = _time_cuda(
                lambda: _torch_sum(torch, keys, values, group_count),
                torch=torch,
                repeats=repeats,
            )
            torch_counts, torch_count_sec = _time_cuda(
                lambda: torch.bincount(keys, minlength=group_count).to(torch.uint32),
                torch=torch,
                repeats=repeats,
            )
            torch_sec = torch_sum_sec + torch_count_sec
            correct = bool(
                torch.allclose(result["outputs"]["sums"], torch_sums)
                and torch.equal(result["outputs"]["counts"], torch_counts)
            )

        mode_rows.append(
            {
                "mode": mode,
                "correct_vs_torch_cuda": correct,
                "median_sec": {
                    "raydb_triton_public_front_door": front_door_sec,
                    "torch_cuda_baseline": torch_sec,
                },
                "metadata": {
                    "partner": result["partner"],
                    "execution_path": result["metadata"]["execution_path"],
                    "uses_cupy_partner": result["metadata"]["uses_cupy_partner"],
                    "uses_pytorch_partner": result["metadata"]["uses_pytorch_partner"],
                    "replaces_rt_traversal": result["metadata"]["replaces_rt_traversal"],
                    "promoted_performance_path": result["metadata"]["promoted_performance_path"],
                    "adapter_front_door_integrated": result["metadata"]["adapter_front_door_integrated"],
                },
            }
        )

    return {
        "row_count": int(row_count),
        "group_count": int(group_count),
        "repeats": int(repeats),
        "modes": tuple(mode_rows),
        "all_correct": all(bool(row["correct_vs_torch_cuda"]) for row in mode_rows),
    }


def run(args) -> dict[str, object]:
    row_counts = _parse_row_counts(args.row_counts)
    payload: dict[str, object] = {
        "goal": "Goal2683 RayDB v2.5 Triton public front-door app validation",
        "git_head": _git_head(),
        "repo_root": str(ROOT),
        "row_counts": row_counts,
        "group_count": int(args.group_count),
        "repeats": int(args.repeats),
        "no_public_speedup_claim": True,
        "rt_traversal_replaced": False,
        "scope": "post_rt_generic_continuation_only",
        "pod_validation_required": True,
    }
    if args.dry_run:
        payload["status"] = "dry_run"
        return payload
    if not rt.triton_partner_available():
        payload["status"] = "skipped"
        payload["reason"] = "triton+torch CUDA are not available"
        return payload

    import torch
    import triton

    payload["status"] = "ok"
    payload["python_version"] = platform.python_version()
    payload["torch_version"] = str(torch.__version__)
    payload["triton_version"] = str(triton.__version__)
    payload["device"] = str(torch.cuda.get_device_name(0))
    payload["cases"] = tuple(
        _case(row_count, int(args.group_count), int(args.repeats), torch=torch)
        for row_count in row_counts
    )
    payload["all_correct"] = all(bool(case["all_correct"]) for case in payload["cases"])  # type: ignore[index]
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--row-counts", default="1024,65536,1048576")
    parser.add_argument("--group-count", type=int, default=4096)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()

    payload = run(args)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()

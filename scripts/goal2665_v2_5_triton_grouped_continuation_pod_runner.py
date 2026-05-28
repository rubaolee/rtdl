#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import statistics
import subprocess
import sys
from pathlib import Path
from time import perf_counter
from typing import Any, Callable


def parse_row_counts(text: str) -> list[int]:
    row_counts: list[int] = []
    for token in text.split(","):
        token = token.strip()
        if not token:
            continue
        value = int(token)
        if value <= 0:
            raise argparse.ArgumentTypeError("row counts must be positive")
        row_counts.append(value)
    if not row_counts:
        raise argparse.ArgumentTypeError("at least one row count is required")
    return row_counts


def git_head(repo_root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return completed.stdout.strip()


def median(values: list[float]) -> float:
    return float(statistics.median(values))


def time_cuda_operation(torch: Any, operation: Callable[[], Any], *, repeats: int) -> tuple[Any, list[float]]:
    timings: list[float] = []
    last_output = None
    for _ in range(repeats):
        torch.cuda.synchronize()
        started = perf_counter()
        last_output = operation()
        torch.cuda.synchronize()
        timings.append(perf_counter() - started)
    return last_output, timings


def run_scale(row_count: int, *, group_count: int, repeats: int, seed: int) -> dict[str, object]:
    import torch

    import rtdsl as rt

    if not rt.triton_partner_available():
        raise RuntimeError("Triton/Torch CUDA is unavailable; run this script on a Linux NVIDIA pod")

    torch.manual_seed(seed + row_count)
    group_ids = torch.randint(0, group_count, (row_count,), dtype=torch.int64, device="cuda")
    values = torch.rand((row_count,), dtype=torch.float64, device="cuda")

    # Warm up JIT and allocator before measured repeats.
    rt.run_triton_segmented_count_i64(group_ids, group_count=group_count)
    rt.run_triton_segmented_sum_f64(group_ids, values, group_count=group_count)

    torch_count_output, torch_count_timings = time_cuda_operation(
        torch,
        lambda: torch.bincount(group_ids, minlength=group_count),
        repeats=repeats,
    )
    triton_count_result, triton_count_timings = time_cuda_operation(
        torch,
        lambda: rt.run_triton_segmented_count_i64(group_ids, group_count=group_count)["outputs"]["counts"],
        repeats=repeats,
    )

    def torch_sum() -> Any:
        output = torch.zeros((group_count,), dtype=torch.float64, device="cuda")
        output.scatter_add_(0, group_ids, values)
        return output

    torch_sum_output, torch_sum_timings = time_cuda_operation(torch, torch_sum, repeats=repeats)
    triton_sum_result, triton_sum_timings = time_cuda_operation(
        torch,
        lambda: rt.run_triton_segmented_sum_f64(group_ids, values, group_count=group_count)["outputs"]["sums"],
        repeats=repeats,
    )

    count_correct = bool(torch.equal(triton_count_result, torch_count_output))
    sum_correct = bool(torch.allclose(triton_sum_result, torch_sum_output, rtol=1e-10, atol=1e-8))

    triton_count_median = median(triton_count_timings)
    triton_sum_median = median(triton_sum_timings)
    torch_count_median = median(torch_count_timings)
    torch_sum_median = median(torch_sum_timings)

    return {
        "row_count": row_count,
        "group_count": group_count,
        "repeats": repeats,
        "correctness": {
            "segmented_count_i64_vs_torch_bincount": count_correct,
            "segmented_sum_f64_vs_torch_scatter_add": sum_correct,
        },
        "timings_seconds": {
            "rtdl_triton_segmented_count_i64": triton_count_timings,
            "torch_bincount": torch_count_timings,
            "rtdl_triton_segmented_sum_f64": triton_sum_timings,
            "torch_scatter_add_sum": torch_sum_timings,
        },
        "median_seconds": {
            "rtdl_triton_segmented_count_i64": triton_count_median,
            "torch_bincount": torch_count_median,
            "rtdl_triton_segmented_sum_f64": triton_sum_median,
            "torch_scatter_add_sum": torch_sum_median,
        },
        "speedups_vs_torch": {
            "count": torch_count_median / triton_count_median if triton_count_median > 0 else None,
            "sum": torch_sum_median / triton_sum_median if triton_sum_median > 0 else None,
        },
    }


def collect_environment(repo_root: Path) -> dict[str, object]:
    import torch
    import triton

    return {
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "git_head": git_head(repo_root),
        "torch_version": getattr(torch, "__version__", "unknown"),
        "triton_version": getattr(triton, "__version__", "unknown"),
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_version": getattr(torch.version, "cuda", None),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    }


def build_dry_run_report(args: argparse.Namespace, repo_root: Path) -> dict[str, object]:
    return {
        "goal": "Goal2665 v2.5 Triton grouped continuation pod runner",
        "status": "dry_run",
        "repo_root": str(repo_root),
        "git_head": git_head(repo_root),
        "row_counts": args.row_counts,
        "group_count": args.group_count,
        "repeats": args.repeats,
        "no_public_speedup_claim": True,
        "pod_validation_required": True,
    }


def run(args: argparse.Namespace, repo_root: Path) -> dict[str, object]:
    if args.dry_run:
        return build_dry_run_report(args, repo_root)

    scales = [
        run_scale(row_count, group_count=args.group_count, repeats=args.repeats, seed=args.seed)
        for row_count in args.row_counts
    ]
    accepted = all(
        scale["correctness"]["segmented_count_i64_vs_torch_bincount"]
        and scale["correctness"]["segmented_sum_f64_vs_torch_scatter_add"]
        for scale in scales
    )
    return {
        "goal": "Goal2665 v2.5 Triton grouped continuation pod runner",
        "status": "accept" if accepted else "reject",
        "claim_boundary": {
            "preview_not_promoted": True,
            "no_public_speedup_claim": True,
            "not_rt_traversal_replacement": True,
            "partner_continuation_only": True,
        },
        "environment": collect_environment(repo_root),
        "row_counts": args.row_counts,
        "group_count": args.group_count,
        "repeats": args.repeats,
        "scales": scales,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate v2.5 Triton grouped count/sum continuations on a CUDA pod."
    )
    parser.add_argument("--row-counts", type=parse_row_counts, default=parse_row_counts("100000,1000000,5000000"))
    parser.add_argument("--group-count", type=int, default=4096)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--seed", type=int, default=2665)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.group_count <= 0:
        parser.error("--group-count must be positive")
    if args.repeats <= 0:
        parser.error("--repeats must be positive")

    repo_root = Path(__file__).resolve().parents[1]
    report = run(args, repo_root)
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n")
    print(text)
    return 0 if report["status"] in {"accept", "dry_run"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

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


def run_scale(
    row_count: int,
    *,
    group_count: int,
    repeats: int,
    seed: int,
    include_numba: bool,
) -> dict[str, object]:
    import torch

    import rtdsl as rt

    if not rt.triton_partner_available():
        raise RuntimeError("Triton/Torch CUDA is unavailable; run this script on a Linux NVIDIA pod")

    torch.manual_seed(seed + row_count)
    group_ids = torch.randint(0, group_count, (row_count,), dtype=torch.int64, device="cuda")
    values = torch.rand((row_count,), dtype=torch.float64, device="cuda")
    item_ids = torch.arange(row_count, dtype=torch.int64, device="cuda")
    compact_values_input = torch.arange(row_count, dtype=torch.int64, device="cuda")
    compact_mask = (group_ids % 3) == 0
    bounded_group_ids = torch.arange(row_count, dtype=torch.int64, device="cuda") % group_count
    bounded_item_ids = torch.arange(row_count, dtype=torch.int64, device="cuda")
    bounded_k = (row_count + group_count - 1) // group_count

    # Warm up JIT and allocator before measured repeats.
    rt.run_triton_partner_continuation(
        "segmented_count_i64",
        {"group_ids": group_ids, "group_count": group_count},
    )
    rt.run_triton_partner_continuation(
        "segmented_sum_f64",
        {"group_ids": group_ids, "values": values, "group_count": group_count},
    )
    rt.run_triton_partner_continuation(
        "segmented_min_f64",
        {"group_ids": group_ids, "values": values, "group_count": group_count},
    )
    rt.run_triton_partner_continuation(
        "segmented_max_f64",
        {"group_ids": group_ids, "values": values, "group_count": group_count},
    )
    rt.run_triton_partner_continuation(
        "compact_mask_i64",
        {"values": compact_values_input, "mask": compact_mask},
    )
    rt.run_triton_partner_continuation(
        "grouped_argmin_f64",
        {"group_ids": group_ids, "item_ids": item_ids, "scores": values, "group_count": group_count},
    )
    rt.run_triton_partner_continuation(
        "bounded_collect_finalize_i64",
        {"group_ids": bounded_group_ids, "item_ids": bounded_item_ids, "group_count": group_count, "k": bounded_k},
    )

    torch_count_output, torch_count_timings = time_cuda_operation(
        torch,
        lambda: torch.bincount(group_ids, minlength=group_count),
        repeats=repeats,
    )
    triton_count_result, triton_count_timings = time_cuda_operation(
        torch,
        lambda: rt.run_triton_partner_continuation(
            "segmented_count_i64",
            {"group_ids": group_ids, "group_count": group_count},
        )["outputs"]["counts"],
        repeats=repeats,
    )

    def torch_sum() -> Any:
        output = torch.zeros((group_count,), dtype=torch.float64, device="cuda")
        output.scatter_add_(0, group_ids, values)
        return output

    torch_sum_output, torch_sum_timings = time_cuda_operation(torch, torch_sum, repeats=repeats)
    triton_sum_result, triton_sum_timings = time_cuda_operation(
        torch,
        lambda: rt.run_triton_partner_continuation(
            "segmented_sum_f64",
            {"group_ids": group_ids, "values": values, "group_count": group_count},
        )["outputs"]["sums"],
        repeats=repeats,
    )

    def torch_min() -> Any:
        output = torch.full((group_count,), float("inf"), dtype=torch.float64, device="cuda")
        output.scatter_reduce_(0, group_ids, values, reduce="amin", include_self=True)
        return output

    def torch_max() -> Any:
        output = torch.full((group_count,), float("-inf"), dtype=torch.float64, device="cuda")
        output.scatter_reduce_(0, group_ids, values, reduce="amax", include_self=True)
        return output

    torch_min_output, torch_min_timings = time_cuda_operation(torch, torch_min, repeats=repeats)
    triton_min_result, triton_min_timings = time_cuda_operation(
        torch,
        lambda: rt.run_triton_partner_continuation(
            "segmented_min_f64",
            {"group_ids": group_ids, "values": values, "group_count": group_count},
        )["outputs"]["dense_mins"],
        repeats=repeats,
    )
    torch_max_output, torch_max_timings = time_cuda_operation(torch, torch_max, repeats=repeats)
    triton_max_result, triton_max_timings = time_cuda_operation(
        torch,
        lambda: rt.run_triton_partner_continuation(
            "segmented_max_f64",
            {"group_ids": group_ids, "values": values, "group_count": group_count},
        )["outputs"]["dense_maxes"],
        repeats=repeats,
    )

    torch_compact_output, torch_compact_timings = time_cuda_operation(
        torch,
        lambda: (compact_values_input[compact_mask], torch.nonzero(compact_mask, as_tuple=False).reshape(-1)),
        repeats=repeats,
    )
    triton_compact_result, triton_compact_timings = time_cuda_operation(
        torch,
        lambda: rt.run_triton_partner_continuation(
            "compact_mask_i64",
            {"values": compact_values_input, "mask": compact_mask},
        )["outputs"],
        repeats=repeats,
    )

    def torch_argmin() -> dict[str, Any]:
        dense_scores = torch.full((group_count,), float("inf"), dtype=torch.float64, device="cuda")
        dense_scores.scatter_reduce_(0, group_ids, values, reduce="amin", include_self=True)
        max_item_id = torch.iinfo(torch.int64).max
        candidate_items = torch.where(values == dense_scores[group_ids], item_ids, max_item_id)
        dense_item_ids = torch.full((group_count,), max_item_id, dtype=torch.int64, device="cuda")
        dense_item_ids.scatter_reduce_(0, group_ids, candidate_items, reduce="amin", include_self=True)
        present_mask = dense_item_ids != max_item_id
        return {
            "group_ids": torch.nonzero(present_mask, as_tuple=False).reshape(-1).to(torch.int64),
            "item_ids": dense_item_ids[present_mask],
            "scores": dense_scores[present_mask],
            "missing_group_ids": torch.nonzero(~present_mask, as_tuple=False).reshape(-1).to(torch.int64),
            "dense_item_ids": dense_item_ids,
            "dense_scores": dense_scores,
        }

    torch_argmin_output, torch_argmin_timings = time_cuda_operation(torch, torch_argmin, repeats=repeats)
    triton_argmin_result, triton_argmin_timings = time_cuda_operation(
        torch,
        lambda: rt.run_triton_partner_continuation(
            "grouped_argmin_f64",
            {"group_ids": group_ids, "item_ids": item_ids, "scores": values, "group_count": group_count},
        )["outputs"],
        repeats=repeats,
    )

    def torch_bounded_collect() -> dict[str, Any]:
        counts = torch.bincount(bounded_group_ids, minlength=group_count)
        row_offsets = torch.empty((group_count + 1,), dtype=torch.int64, device="cuda")
        row_offsets[0] = 0
        row_offsets[1:] = torch.cumsum(counts, dim=0)
        order = torch.argsort(bounded_group_ids, stable=True)
        return {
            "group_ids": bounded_group_ids[order],
            "item_ids": bounded_item_ids[order],
            "row_offsets": row_offsets,
            "counts": counts,
        }

    torch_bounded_output, torch_bounded_timings = time_cuda_operation(torch, torch_bounded_collect, repeats=repeats)
    triton_bounded_result, triton_bounded_timings = time_cuda_operation(
        torch,
        lambda: rt.run_triton_partner_continuation(
            "bounded_collect_finalize_i64",
            {"group_ids": bounded_group_ids, "item_ids": bounded_item_ids, "group_count": group_count, "k": bounded_k},
        )["outputs"],
        repeats=repeats,
    )

    count_correct = bool(torch.equal(triton_count_result, torch_count_output))
    sum_correct = bool(torch.allclose(triton_sum_result, torch_sum_output, rtol=1e-10, atol=1e-8))
    min_correct = bool(torch.allclose(triton_min_result, torch_min_output, rtol=1e-10, atol=1e-8))
    max_correct = bool(torch.allclose(triton_max_result, torch_max_output, rtol=1e-10, atol=1e-8))
    compact_correct = bool(
        torch.equal(triton_compact_result["values"], torch_compact_output[0])
        and torch.equal(triton_compact_result["original_indices"], torch_compact_output[1])
    )
    argmin_correct = bool(
        torch.equal(triton_argmin_result["group_ids"], torch_argmin_output["group_ids"])
        and torch.equal(triton_argmin_result["item_ids"], torch_argmin_output["item_ids"])
        and torch.allclose(triton_argmin_result["scores"], torch_argmin_output["scores"], rtol=1e-10, atol=1e-8)
        and torch.equal(triton_argmin_result["missing_group_ids"], torch_argmin_output["missing_group_ids"])
    )
    bounded_sorted = torch.argsort(
        triton_bounded_result["group_ids"] * (row_count + 1) + triton_bounded_result["item_ids"],
        stable=True,
    )
    torch_bounded_sorted = torch.argsort(
        torch_bounded_output["group_ids"] * (row_count + 1) + torch_bounded_output["item_ids"],
        stable=True,
    )
    bounded_correct = bool(
        torch.equal(triton_bounded_result["row_offsets"], torch_bounded_output["row_offsets"])
        and torch.equal(triton_bounded_result["group_ids"][bounded_sorted], torch_bounded_output["group_ids"][torch_bounded_sorted])
        and torch.equal(triton_bounded_result["item_ids"][bounded_sorted], torch_bounded_output["item_ids"][torch_bounded_sorted])
    )

    triton_count_median = median(triton_count_timings)
    triton_sum_median = median(triton_sum_timings)
    triton_min_median = median(triton_min_timings)
    triton_max_median = median(triton_max_timings)
    triton_compact_median = median(triton_compact_timings)
    triton_argmin_median = median(triton_argmin_timings)
    triton_bounded_median = median(triton_bounded_timings)
    torch_count_median = median(torch_count_timings)
    torch_sum_median = median(torch_sum_timings)
    torch_min_median = median(torch_min_timings)
    torch_max_median = median(torch_max_timings)
    torch_compact_median = median(torch_compact_timings)
    torch_argmin_median = median(torch_argmin_timings)
    torch_bounded_median = median(torch_bounded_timings)

    scale: dict[str, object] = {
        "row_count": row_count,
        "group_count": group_count,
        "repeats": repeats,
        "include_numba": include_numba,
        "correctness": {
            "segmented_count_i64_vs_torch_bincount": count_correct,
            "segmented_sum_f64_vs_torch_scatter_add": sum_correct,
            "segmented_min_f64_vs_torch_scatter_reduce_amin": min_correct,
            "segmented_max_f64_vs_torch_scatter_reduce_amax": max_correct,
            "compact_mask_i64_vs_torch_mask_index": compact_correct,
            "grouped_argmin_f64_vs_torch_scatter_reduce_amin": argmin_correct,
            "bounded_collect_finalize_i64_vs_torch_group_sort": bounded_correct,
        },
        "timings_seconds": {
            "rtdl_triton_segmented_count_i64": triton_count_timings,
            "torch_bincount": torch_count_timings,
            "rtdl_triton_segmented_sum_f64": triton_sum_timings,
            "torch_scatter_add_sum": torch_sum_timings,
            "rtdl_triton_segmented_min_f64": triton_min_timings,
            "torch_scatter_reduce_min": torch_min_timings,
            "rtdl_triton_segmented_max_f64": triton_max_timings,
            "torch_scatter_reduce_max": torch_max_timings,
            "rtdl_triton_compact_mask_i64": triton_compact_timings,
            "torch_mask_index_compact": torch_compact_timings,
            "rtdl_triton_grouped_argmin_f64": triton_argmin_timings,
            "torch_scatter_reduce_argmin": torch_argmin_timings,
            "rtdl_triton_bounded_collect_finalize_i64": triton_bounded_timings,
            "torch_group_sort_bounded_collect": torch_bounded_timings,
        },
        "median_seconds": {
            "rtdl_triton_segmented_count_i64": triton_count_median,
            "torch_bincount": torch_count_median,
            "rtdl_triton_segmented_sum_f64": triton_sum_median,
            "torch_scatter_add_sum": torch_sum_median,
            "rtdl_triton_segmented_min_f64": triton_min_median,
            "torch_scatter_reduce_min": torch_min_median,
            "rtdl_triton_segmented_max_f64": triton_max_median,
            "torch_scatter_reduce_max": torch_max_median,
            "rtdl_triton_compact_mask_i64": triton_compact_median,
            "torch_mask_index_compact": torch_compact_median,
            "rtdl_triton_grouped_argmin_f64": triton_argmin_median,
            "torch_scatter_reduce_argmin": torch_argmin_median,
            "rtdl_triton_bounded_collect_finalize_i64": triton_bounded_median,
            "torch_group_sort_bounded_collect": torch_bounded_median,
        },
        "speedups_vs_torch": {
            "count": torch_count_median / triton_count_median if triton_count_median > 0 else None,
            "sum": torch_sum_median / triton_sum_median if triton_sum_median > 0 else None,
            "min": torch_min_median / triton_min_median if triton_min_median > 0 else None,
            "max": torch_max_median / triton_max_median if triton_max_median > 0 else None,
            "compact": torch_compact_median / triton_compact_median if triton_compact_median > 0 else None,
            "argmin": torch_argmin_median / triton_argmin_median if triton_argmin_median > 0 else None,
            "bounded_collect": torch_bounded_median / triton_bounded_median if triton_bounded_median > 0 else None,
        },
    }
    if include_numba:
        scale["numba"] = run_numba_scale(
            rt,
            torch,
            group_ids,
            values,
            torch_count_output,
            torch_sum_output,
            group_count=group_count,
            repeats=repeats,
        )
    return scale


def run_numba_scale(
    rt: Any,
    torch: Any,
    group_ids: Any,
    values: Any,
    torch_count_output: Any,
    torch_sum_output: Any,
    *,
    group_count: int,
    repeats: int,
) -> dict[str, object]:
    if not rt.numba_partner_available():
        return {
            "status": "skip",
            "reason": "numba CUDA unavailable",
            "trusted_valid_group_ids": True,
        }

    from numba import cuda

    host_group_ids = group_ids.detach().cpu().numpy()
    host_values = values.detach().cpu().numpy()
    numba_group_ids = cuda.to_device(host_group_ids)
    numba_values = cuda.to_device(host_values)

    rt.run_numba_segmented_count_i64(
        numba_group_ids,
        group_count=group_count,
        validate_group_ids=True,
    )
    rt.run_numba_segmented_sum_f64(
        numba_group_ids,
        numba_values,
        group_count=group_count,
        validate_group_ids=True,
    )

    numba_count_result, numba_count_timings = time_cuda_operation(
        cuda,
        lambda: rt.run_numba_segmented_count_i64(
            numba_group_ids,
            group_count=group_count,
            validate_group_ids=True,
        )["outputs"]["counts"].copy_to_host(),
        repeats=repeats,
    )
    numba_sum_result, numba_sum_timings = time_cuda_operation(
        cuda,
        lambda: rt.run_numba_segmented_sum_f64(
            numba_group_ids,
            numba_values,
            group_count=group_count,
            validate_group_ids=True,
        )["outputs"]["sums"].copy_to_host(),
        repeats=repeats,
    )

    torch_count_host = torch_count_output.detach().cpu().numpy()
    torch_sum_host = torch_sum_output.detach().cpu().numpy()
    numba_count_median = median(numba_count_timings)
    numba_sum_median = median(numba_sum_timings)

    return {
        "status": "accept",
        "trusted_valid_group_ids": True,
        "validation_note": (
            "Input ids are generated in-range by the runner. Numba validation "
            "uses the preview device-resident error-flag kernel instead of a "
            "full group-id host copy."
        ),
        "correctness": {
            "segmented_count_i64_vs_torch_bincount": bool((numba_count_result == torch_count_host).all()),
            "segmented_sum_f64_vs_torch_scatter_add": bool(
                abs(numba_sum_result - torch_sum_host).max() <= 1e-8
            ),
        },
        "timings_seconds": {
            "rtdl_numba_segmented_count_i64": numba_count_timings,
            "rtdl_numba_segmented_sum_f64": numba_sum_timings,
        },
        "median_seconds": {
            "rtdl_numba_segmented_count_i64": numba_count_median,
            "rtdl_numba_segmented_sum_f64": numba_sum_median,
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
        "include_numba": args.include_numba,
        "no_public_speedup_claim": True,
        "pod_validation_required": True,
    }


def run(args: argparse.Namespace, repo_root: Path) -> dict[str, object]:
    if args.dry_run:
        return build_dry_run_report(args, repo_root)

    scales = [
        run_scale(
            row_count,
            group_count=args.group_count,
            repeats=args.repeats,
            seed=args.seed,
            include_numba=args.include_numba,
        )
        for row_count in args.row_counts
    ]
    accepted = all(
        scale["correctness"]["segmented_count_i64_vs_torch_bincount"]
        and scale["correctness"]["segmented_sum_f64_vs_torch_scatter_add"]
        and scale["correctness"]["segmented_min_f64_vs_torch_scatter_reduce_amin"]
        and scale["correctness"]["segmented_max_f64_vs_torch_scatter_reduce_amax"]
        and scale["correctness"]["compact_mask_i64_vs_torch_mask_index"]
        and scale["correctness"]["grouped_argmin_f64_vs_torch_scatter_reduce_amin"]
        and scale["correctness"]["bounded_collect_finalize_i64_vs_torch_group_sort"]
        and (
            not args.include_numba
            or scale["numba"]["status"] == "skip"
            or (
                scale["numba"]["correctness"]["segmented_count_i64_vs_torch_bincount"]
                and scale["numba"]["correctness"]["segmented_sum_f64_vs_torch_scatter_add"]
            )
        )
        for scale in scales
    )
    return {
        "goal": "Goal2665 v2.5 Triton grouped continuation pod runner",
        "status": "accept" if accepted else "reject",
        "claim_boundary": {
            "primary_partner": "triton",
            "torch_is_tensor_carrier_not_partner": True,
            "preview_not_promoted": True,
            "no_public_speedup_claim": True,
            "not_rt_traversal_replacement": True,
            "partner_continuation_only": True,
        },
        "environment": collect_environment(repo_root),
        "row_counts": args.row_counts,
        "group_count": args.group_count,
        "repeats": args.repeats,
        "include_numba": args.include_numba,
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
    parser.add_argument("--include-numba", action="store_true")
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

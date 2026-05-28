#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from pathlib import Path
from time import perf_counter

import rtdsl as rt
from rtdsl import partner_adapters as adapters


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


def _time_cuda(callable_obj, *, torch, repeats: int):
    elapsed: list[float] = []
    last = None
    for _ in range(int(repeats)):
        torch.cuda.synchronize()
        started = perf_counter()
        last = callable_obj()
        torch.cuda.synchronize()
        elapsed.append(perf_counter() - started)
    return last, _median(elapsed)


def _torch_group_sum(torch, keys, values, group_count: int):
    out = torch.zeros((int(group_count),), dtype=values.dtype, device=values.device)
    if int(keys.numel()):
        out.scatter_add_(0, keys.to(torch.int64), values)
    return out


def _torch_group_minmax(torch, keys, values, group_count: int, *, reduce: str, initial: float):
    out = torch.full((int(group_count),), float(initial), dtype=values.dtype, device=values.device)
    if int(keys.numel()):
        out.scatter_reduce_(0, keys.to(torch.int64), values, reduce=reduce, include_self=True)
    return out


def _case(row_count: int, group_count: int, repeats: int, *, torch) -> dict[str, object]:
    device = torch.device("cuda:0")
    row_ids = torch.arange(row_count, dtype=torch.int64, device=device)
    keys = ((row_ids * 17 + 3) % int(group_count)).to(torch.int64)
    values = (row_ids.to(torch.float64) * 0.125 + 1.0).to(torch.float64)
    mask = ((row_ids % 3) != 1)

    count_result, count_sec = _time_cuda(
        lambda: adapters.partner_group_count_by_key(keys, group_count, partner="triton"),
        torch=torch,
        repeats=repeats,
    )
    torch_count, torch_count_sec = _time_cuda(
        lambda: torch.bincount(keys, minlength=group_count).to(torch.uint32),
        torch=torch,
        repeats=repeats,
    )

    sum_result, sum_sec = _time_cuda(
        lambda: adapters.partner_group_sum_by_key(keys, values, group_count, partner="triton"),
        torch=torch,
        repeats=repeats,
    )
    torch_sum, torch_sum_sec = _time_cuda(
        lambda: _torch_group_sum(torch, keys, values, group_count),
        torch=torch,
        repeats=repeats,
    )

    min_result, min_sec = _time_cuda(
        lambda: adapters.partner_group_min_by_key(keys, values, group_count, partner="triton", initial=1.0e30),
        torch=torch,
        repeats=repeats,
    )
    torch_min, torch_min_sec = _time_cuda(
        lambda: _torch_group_minmax(torch, keys, values, group_count, reduce="amin", initial=1.0e30),
        torch=torch,
        repeats=repeats,
    )

    max_result, max_sec = _time_cuda(
        lambda: adapters.partner_group_max_by_key(keys, values, group_count, partner="triton", initial=-1.0e30),
        torch=torch,
        repeats=repeats,
    )
    torch_max, torch_max_sec = _time_cuda(
        lambda: _torch_group_minmax(torch, keys, values, group_count, reduce="amax", initial=-1.0e30),
        torch=torch,
        repeats=repeats,
    )

    compact_result, compact_sec = _time_cuda(
        lambda: adapters.partner_mask_indices(mask, partner="triton"),
        torch=torch,
        repeats=repeats,
    )
    torch_compact, torch_compact_sec = _time_cuda(
        lambda: torch.nonzero(mask, as_tuple=False).reshape(-1).to(torch.int64),
        torch=torch,
        repeats=repeats,
    )

    columns = {
        "group": keys,
        "value": values,
        "row_id": row_ids,
        "_metadata": {"category_maps": {}},
    }
    predicate = (("value", "ge", float(row_count) * 0.05),)
    pred_count_result, pred_count_sec = _time_cuda(
        lambda: adapters.partner_columnar_predicate_reduce(
            columns,
            predicate,
            partner="triton",
            reduce="count",
            group_field="group",
            group_count=group_count,
        ),
        torch=torch,
        repeats=repeats,
    )
    pred_sum_result, pred_sum_sec = _time_cuda(
        lambda: adapters.partner_columnar_predicate_reduce(
            columns,
            predicate,
            partner="triton",
            reduce="sum",
            group_field="group",
            value_field="value",
            group_count=group_count,
        ),
        torch=torch,
        repeats=repeats,
    )
    predicate_mask = values >= float(row_count) * 0.05
    selected_keys = keys[predicate_mask]
    torch_pred_count = torch.bincount(selected_keys, minlength=group_count).to(torch.uint32)
    torch_pred_sum = _torch_group_sum(torch, keys, values * predicate_mask.to(torch.float64), group_count)

    return {
        "row_count": int(row_count),
        "group_count": int(group_count),
        "repeats": int(repeats),
        "correct": {
            "count": bool(torch.equal(count_result, torch_count)),
            "sum": bool(torch.allclose(sum_result, torch_sum)),
            "min": bool(torch.allclose(min_result, torch_min)),
            "max": bool(torch.allclose(max_result, torch_max)),
            "compact": bool(torch.equal(compact_result, torch_compact)),
            "predicate_count": bool(torch.equal(pred_count_result, torch_pred_count)),
            "predicate_sum": bool(torch.allclose(pred_sum_result, torch_pred_sum)),
        },
        "median_sec": {
            "triton_adapter_count": count_sec,
            "torch_count": torch_count_sec,
            "triton_adapter_sum": sum_sec,
            "torch_sum": torch_sum_sec,
            "triton_adapter_min": min_sec,
            "torch_min": torch_min_sec,
            "triton_adapter_max": max_sec,
            "torch_max": torch_max_sec,
            "triton_adapter_compact": compact_sec,
            "torch_compact": torch_compact_sec,
            "triton_adapter_predicate_count": pred_count_sec,
            "triton_adapter_predicate_sum": pred_sum_sec,
        },
    }


def run(args) -> dict[str, object]:
    row_counts = _parse_row_counts(args.row_counts)
    payload = {
        "goal": "Goal2682 v2.5 Triton adapter front-door pod runner",
        "git_head": _git_head(),
        "repo_root": str(ROOT),
        "row_counts": row_counts,
        "group_count": int(args.group_count),
        "repeats": int(args.repeats),
        "no_public_speedup_claim": True,
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

    torch.manual_seed(0)
    payload["status"] = "ok"
    payload["torch_version"] = str(torch.__version__)
    payload["device"] = str(torch.cuda.get_device_name(0))
    payload["cases"] = tuple(
        _case(row_count, int(args.group_count), int(args.repeats), torch=torch)
        for row_count in row_counts
    )
    payload["all_correct"] = all(
        all(bool(value) for value in case["correct"].values())  # type: ignore[index, union-attr]
        for case in payload["cases"]  # type: ignore[index]
    )
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

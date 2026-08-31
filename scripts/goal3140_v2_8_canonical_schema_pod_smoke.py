from __future__ import annotations

import argparse
import json
import socket
import subprocess
from pathlib import Path
from typing import Any

import numpy as np

import rtdsl as rt


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def _to_list(value: Any) -> list[Any]:
    if hasattr(value, "detach"):
        return value.detach().cpu().numpy().tolist()
    if hasattr(value, "copy_to_host"):
        return value.copy_to_host().tolist()
    if hasattr(value, "tolist"):
        return value.tolist()
    return list(value)


def _adapter(operation: str, *, user_selected_partner: str) -> rt.V28SegmentedTypedStreamAdapterResult:
    return rt.build_segmented_typed_stream_adapter(
        ((0, 10, 1.5), (0, 11, 2.5), (1, 20, 0.25)),
        row_schema=("group_ids", "item_ids", "scores"),
        column_roles={
            "group_ids": "group_key",
            "item_ids": "item_id",
            "scores": "score",
        },
        page_capacity=2,
        stream_id=f"goal3140_{operation}_{user_selected_partner}",
        stream_kind="ranked_summary_stream",
        producer_primitive="segmented_row_stream_reference",
        ordering="group_ordered",
        operation=operation,
        group_column="group_ids",
        value_columns=("scores",),
        item_column="item_ids",
        user_selected_partner=user_selected_partner,
    )


def _numba_columns() -> dict[str, Any]:
    from numba import cuda

    return {
        "group_ids": cuda.to_device(np.asarray([0, 0, 1], dtype=np.int64)),
        "item_ids": cuda.to_device(np.asarray([10, 11, 20], dtype=np.int64)),
        "scores": cuda.to_device(np.asarray([1.5, 2.5, 0.25], dtype=np.float64)),
    }


def _torch_columns() -> dict[str, Any]:
    import torch

    device = torch.device("cuda")
    return {
        "group_ids": torch.tensor([0, 0, 1], dtype=torch.int64, device=device),
        "item_ids": torch.tensor([10, 11, 20], dtype=torch.int64, device=device),
        "scores": torch.tensor([1.5, 2.5, 0.25], dtype=torch.float64, device=device),
    }


def _check(name: str, observed: dict[str, Any], expected_keys: tuple[str, ...], expected: dict[str, list[Any]]) -> dict[str, Any]:
    keys = tuple(observed)
    if keys != expected_keys:
        raise AssertionError(f"{name} keys mismatch: {keys} != {expected_keys}")
    host_outputs = {key: _to_list(value) for key, value in observed.items()}
    if host_outputs != expected:
        raise AssertionError(f"{name} outputs mismatch: {host_outputs} != {expected}")
    return {"name": name, "keys": keys, "host_outputs": host_outputs, "status": "passed"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    cases: list[dict[str, Any]] = []

    print("[goal3140] running Numba argmin front-door schema smoke", flush=True)
    result = rt.execute_segmented_typed_stream_partner_continuation(
        _adapter("grouped_argmin_f64", user_selected_partner="numba"),
        partner="numba",
        partner_columns=_numba_columns(),
        group_count=3,
    )
    cases.append(
        _check(
            "grouped_argmin_f64_numba",
            result["outputs"],
            ("group_ids", "item_ids", "scores", "missing_group_ids"),
            {"group_ids": [0, 1], "item_ids": [10, 20], "scores": [1.5, 0.25], "missing_group_ids": [2]},
        )
    )

    print("[goal3140] running Numba argmax front-door schema smoke", flush=True)
    result = rt.execute_segmented_typed_stream_partner_continuation(
        _adapter("grouped_argmax_f64", user_selected_partner="numba"),
        partner="numba",
        partner_columns=_numba_columns(),
        group_count=3,
    )
    cases.append(
        _check(
            "grouped_argmax_f64_numba",
            result["outputs"],
            ("group_ids", "item_ids", "scores", "missing_group_ids"),
            {"group_ids": [0, 1], "item_ids": [11, 20], "scores": [2.5, 0.25], "missing_group_ids": [2]},
        )
    )

    print("[goal3140] running Torch top-k front-door schema smoke", flush=True)
    result = rt.execute_segmented_typed_stream_partner_continuation(
        _adapter("grouped_topk_f64", user_selected_partner="torch"),
        partner="torch",
        partner_columns=_torch_columns(),
        group_count=2,
        k=1,
    )
    cases.append(
        _check(
            "grouped_topk_f64_torch",
            result["outputs"],
            ("group_ids", "item_ids", "scores", "ranks", "row_offsets", "missing_group_ids"),
            {
                "group_ids": [0, 1],
                "item_ids": [10, 20],
                "scores": [1.5, 0.25],
                "ranks": [1, 1],
                "row_offsets": [0, 1, 2],
                "missing_group_ids": [],
            },
        )
    )

    output = {
        "goal": "Goal3140",
        "status": "passed",
        "claim_boundary": "schema_smoke_not_release_or_speedup_claim",
        "host": socket.gethostname(),
        "commit": _git_head(),
        "cases": cases,
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3140] wrote {path}", flush=True)


if __name__ == "__main__":
    main()

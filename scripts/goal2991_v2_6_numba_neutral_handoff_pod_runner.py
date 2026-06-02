from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from time import perf_counter
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl as rt  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Goal2991 v2.6 Numba neutral-handoff pod runner"
    )
    parser.add_argument("--rows", type=int, default=1_000_000)
    parser.add_argument("--groups", type=int, default=4096)
    parser.add_argument("--block-size", type=int, default=256)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT
        / "docs"
        / "reports"
        / "goal2991_v2_6_numba_neutral_handoff_pod"
        / "goal2991_numba_neutral_handoff.json",
    )
    args = parser.parse_args(argv)

    started = perf_counter()
    print("[goal2991] importing Numba/CUDA stack", flush=True)
    try:
        import numpy as np
        from numba import cuda
    except Exception as exc:
        payload = _payload(
            status="fail",
            rows=args.rows,
            groups=args.groups,
            started=started,
            error=f"Numba/CUDA imports failed: {exc}",
        )
        _write(args.output, payload)
        return 2

    if not cuda.is_available():
        payload = _payload(
            status="fail",
            rows=args.rows,
            groups=args.groups,
            started=started,
            error="Numba CUDA is not available",
        )
        _write(args.output, payload)
        return 2

    rows = int(args.rows)
    groups = int(args.groups)
    block_size = int(args.block_size)
    if rows <= 0 or groups <= 0 or block_size <= 0:
        raise ValueError("rows, groups, and block-size must be positive")

    print(f"[goal2991] building fixture rows={rows} groups={groups}", flush=True)
    host_group_ids = (np.arange(rows, dtype=np.int64) * 17 + 3) % groups
    host_values = ((np.arange(rows, dtype=np.float64) % 97.0) + 0.25) / 7.0
    expected_counts = np.bincount(host_group_ids, minlength=groups).astype(np.int64)
    expected_sums = np.bincount(host_group_ids, weights=host_values, minlength=groups).astype(np.float64)

    print("[goal2991] copying fixture to device", flush=True)
    device_group_ids = cuda.to_device(host_group_ids)
    device_values = cuda.to_device(host_values)
    cuda.synchronize()

    print("[goal2991] preparing v2.6 neutral handoff packet", flush=True)
    handoff = rt.prepare_v2_6_neutral_partner_handoff(
        {
            "group_ids": device_group_ids,
            "values": device_values,
        },
        partner="numba",
    )
    handoff_validation = rt.validate_v2_6_neutral_partner_handoff(handoff)
    if handoff_validation["status"] != "accept":
        raise RuntimeError(f"neutral handoff rejected: {handoff_validation['errors']}")

    print("[goal2991] running Numba segmented count", flush=True)
    count_result = rt.run_numba_segmented_count_i64(
        device_group_ids,
        group_count=groups,
        block_size=block_size,
    )

    print("[goal2991] running Numba segmented sum", flush=True)
    sum_result = rt.run_numba_segmented_sum_f64(
        device_group_ids,
        device_values,
        group_count=groups,
        block_size=block_size,
    )

    print("[goal2991] validating CPU parity", flush=True)
    observed_counts = count_result["outputs"]["counts"].copy_to_host()
    observed_sums = sum_result["outputs"]["sums"].copy_to_host()
    counts_match = bool(np.array_equal(observed_counts, expected_counts))
    sums_match = bool(np.allclose(observed_sums, expected_sums, rtol=1.0e-10, atol=1.0e-8))
    status = "pass" if counts_match and sums_match else "fail"

    payload = _payload(
        status=status,
        rows=rows,
        groups=groups,
        started=started,
        block_size=block_size,
        handoff={
            "validation": handoff_validation,
            "selected_partner": handoff["selected_partner"],
            "all_columns_device_resident": handoff["all_columns_device_resident"],
            "torch_conversion_used": handoff["torch_conversion_used"],
            "torch_carrier_used": handoff["torch_carrier_used"],
            "runtime_observed_descriptor_count": handoff["runtime_observed_descriptor_count"],
            "all_leases_completed": handoff["all_leases_completed"],
        },
        count_phase_timing=count_result["phase_timing"],
        sum_phase_timing=sum_result["phase_timing"],
        counts_match_cpu=counts_match,
        sums_match_cpu=sums_match,
        max_sum_abs_error=float(np.max(np.abs(observed_sums - expected_sums))),
        gpu=str(cuda.get_current_device()),
        source_commit=_git("rev-parse", "HEAD"),
        source_dirty=_git("status", "--short").splitlines(),
    )
    _write(args.output, payload)
    print(f"[goal2991] wrote {args.output}", flush=True)
    print(f"[goal2991] status={status}", flush=True)
    return 0 if status == "pass" else 1


def _payload(*, status: str, rows: int, groups: int, started: float, **extra: Any) -> dict[str, Any]:
    return {
        "goal": "Goal2991",
        "status": status,
        "rows": int(rows),
        "groups": int(groups),
        "elapsed_sec": perf_counter() - started,
        **extra,
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "numba_speedup_claim_authorized": False,
        },
    }


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _git(*args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except Exception:
        return ""
    return completed.stdout.strip()


if __name__ == "__main__":
    raise SystemExit(main())

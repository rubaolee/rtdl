from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from time import perf_counter
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal2997 Numba compact-mask pod runner")
    parser.add_argument("--rows", type=int, default=1_000_000)
    parser.add_argument("--block-size", type=int, default=256)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT
        / "docs"
        / "reports"
        / "goal2997_numba_compact_mask_pod"
        / "goal2997_numba_compact_mask.json",
    )
    args = parser.parse_args(argv)

    started = perf_counter()
    print("[goal2997] importing Numba/CUDA stack", flush=True)
    try:
        import numpy as np
        import numba
        from numba import cuda
    except Exception as exc:
        payload = _payload(status="fail", rows=args.rows, started=started, error=str(exc))
        _write(args.output, payload)
        return 2
    if not cuda.is_available():
        payload = _payload(status="fail", rows=args.rows, started=started, error="Numba CUDA unavailable")
        _write(args.output, payload)
        return 2

    rows = int(args.rows)
    block_size = int(args.block_size)
    if rows <= 0 or block_size <= 0:
        raise ValueError("rows and block-size must be positive")

    print(f"[goal2997] building mask rows={rows}", flush=True)
    host_values = np.arange(rows, dtype=np.int64) * 3 + 7
    host_mask = ((np.arange(rows, dtype=np.int64) % 7) == 0) | ((np.arange(rows, dtype=np.int64) % 17) == 3)
    expected_indices = np.nonzero(host_mask)[0].astype(np.int64)
    expected_values = host_values[expected_indices]

    print("[goal2997] copying mask/value columns to device", flush=True)
    device_values = cuda.to_device(host_values)
    device_mask = cuda.to_device(host_mask.astype(np.bool_))
    cuda.synchronize()

    print("[goal2997] running compact_mask_i64", flush=True)
    compact = rt.run_numba_compact_mask_i64(device_values, device_mask, block_size=block_size)
    indices = rt.partner_mask_indices(device_mask, partner="numba")
    cuda.synchronize()

    observed_values = compact["outputs"]["values"].copy_to_host()
    observed_indices = compact["outputs"]["original_indices"].copy_to_host()
    observed_partner_indices = indices.copy_to_host()
    values_match = bool(np.array_equal(observed_values, expected_values))
    indices_match = bool(np.array_equal(observed_indices, expected_indices))
    partner_indices_match = bool(np.array_equal(observed_partner_indices, expected_indices))
    status = "pass" if values_match and indices_match and partner_indices_match else "fail"

    payload = _payload(
        status=status,
        rows=rows,
        started=started,
        block_size=block_size,
        selected_count=int(expected_indices.size),
        operation=compact["operation"],
        values_match_cpu=values_match,
        indices_match_cpu=indices_match,
        partner_indices_match_cpu=partner_indices_match,
        stable_input_order=bool(compact["stable_input_order"]),
        host_prefix_sum_used=bool(compact["host_prefix_sum_used"]),
        gpu=str(cuda.get_current_device()),
        toolchain={
            "python_version": sys.version.split()[0],
            "numpy_version": np.__version__,
            "numba_version": numba.__version__,
            "numba_cuda_module": str(getattr(cuda, "__file__", "")),
            "numba_cuda_use_nvidia_binding": os.environ.get(
                "NUMBA_CUDA_USE_NVIDIA_BINDING", ""
            ),
            "numba_cuda_enable_minor_version_compatibility": os.environ.get(
                "NUMBA_CUDA_ENABLE_MINOR_VERSION_COMPATIBILITY", ""
            ),
        },
        source_commit=_git("rev-parse", "HEAD"),
        source_dirty=_git("status", "--short").splitlines(),
    )
    _write(args.output, payload)
    print(f"[goal2997] wrote {args.output}", flush=True)
    print(f"[goal2997] status={status}", flush=True)
    return 0 if status == "pass" else 1


def _payload(*, status: str, rows: int, started: float, **extra: Any) -> dict[str, Any]:
    return {
        "goal": "Goal2997",
        "status": status,
        "rows": int(rows),
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

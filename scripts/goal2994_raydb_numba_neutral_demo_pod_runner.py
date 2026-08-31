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

from examples.current.research_benchmarks.raydb_style import (  # noqa: E402
    rtdl_raydb_style_benchmark_app as raydb,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Goal2994 RayDB-style v2.6 Numba neutral-front-door pod runner"
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
        / "goal2994_raydb_numba_neutral_demo_pod"
        / "goal2994_raydb_numba_neutral_demo.json",
    )
    args = parser.parse_args(argv)

    started = perf_counter()
    print("[goal2994] importing Numba/CUDA stack", flush=True)
    try:
        import numpy as np
        import numba
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

    print(f"[goal2994] building RayDB-style post-RT fixture rows={rows} groups={groups}", flush=True)
    host_group_ids = (np.arange(rows, dtype=np.int64) * 31 + 11) % groups
    host_values = ((np.arange(rows, dtype=np.float64) % 113.0) + 0.5) / 9.0
    expected_counts = np.bincount(host_group_ids, minlength=groups).astype(np.int64)
    expected_sums = np.bincount(host_group_ids, weights=host_values, minlength=groups).astype(np.float64)

    print("[goal2994] copying app-lowered columns to device", flush=True)
    device_group_ids = cuda.to_device(host_group_ids)
    device_values = cuda.to_device(host_values)
    cuda.synchronize()

    print("[goal2994] running RayDB v2.6 Numba neutral continuation", flush=True)
    continuation = raydb.run_raydb_v2_6_numba_neutral_continuation_preview(
        "avg_as_sum_count",
        {
            "group_ids": device_group_ids,
            "values": device_values,
            "group_count": groups,
        },
        block_size=block_size,
    )
    cuda.synchronize()

    print("[goal2994] validating CPU parity", flush=True)
    observed_counts = continuation["outputs"]["counts"].copy_to_host()
    observed_sums = continuation["outputs"]["sums"].copy_to_host()
    counts_match = bool(np.array_equal(observed_counts, expected_counts))
    sums_match = bool(np.allclose(observed_sums, expected_sums, rtol=1.0e-10, atol=1.0e-8))
    status = "pass" if counts_match and sums_match else "fail"

    payload = _payload(
        status=status,
        rows=rows,
        groups=groups,
        started=started,
        block_size=block_size,
        mode="avg_as_sum_count",
        app=continuation["app"],
        partner=continuation["partner"],
        operations=continuation["operations"],
        metadata=continuation["metadata"],
        continuation_paths=tuple(row["path"] for row in continuation["continuation_results"]),
        counts_match_cpu=counts_match,
        sums_match_cpu=sums_match,
        max_sum_abs_error=float(np.max(np.abs(observed_sums - expected_sums))),
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
    print(f"[goal2994] wrote {args.output}", flush=True)
    print(f"[goal2994] status={status}", flush=True)
    return 0 if status == "pass" else 1


def _payload(*, status: str, rows: int, groups: int, started: float, **extra: Any) -> dict[str, Any]:
    return {
        "goal": "Goal2994",
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
            "raydb_paper_reproduction_claim_authorized": False,
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

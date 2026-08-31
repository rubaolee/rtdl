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
from examples.current.research_benchmarks.triangle_counting import (  # noqa: E402
    rtdl_triangle_counting_benchmark_app as triangle,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Goal3000 triangle-counting Numba compact-mask pod runner"
    )
    parser.add_argument("--rows", type=int, default=1_000_000)
    parser.add_argument("--block-size", type=int, default=256)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT
        / "docs"
        / "reports"
        / "goal3000_triangle_counting_numba_compact_mask_pod"
        / "goal3000_triangle_counting_numba_compact_mask.json",
    )
    args = parser.parse_args(argv)

    started = perf_counter()
    print("[goal3000] importing Numba/CUDA stack", flush=True)
    try:
        try:
            import _numba_cuda_redirector  # noqa: F401
        except ImportError:
            pass
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

    print(f"[goal3000] building triangle witness mask rows={rows}", flush=True)
    row_ids = np.arange(rows, dtype=np.int64)
    host_candidate_row_ids = row_ids * 5 + 101
    host_valid_mask = ((row_ids % 11) == 2) | ((row_ids % 29) == 7) | ((row_ids % 31) == 13)
    host_valid_mask = host_valid_mask.astype(np.bool_, copy=False)
    expected_indices = np.nonzero(host_valid_mask)[0].astype(np.int64)
    expected_candidates = host_candidate_row_ids[expected_indices]

    print("[goal3000] copying candidate ids and mask to device", flush=True)
    device_candidate_row_ids = cuda.to_device(host_candidate_row_ids)
    device_valid_mask = cuda.to_device(host_valid_mask)
    cuda.synchronize()

    print("[goal3000] running triangle app v2.6 compact-mask preview", flush=True)
    result = triangle.run_triangle_counting_v2_6_numba_compact_mask_preview(
        {
            "candidate_row_ids": device_candidate_row_ids,
            "valid_triangle_mask": device_valid_mask,
        },
        block_size=block_size,
    )
    print("[goal3000] running generic partner_mask_indices cross-check", flush=True)
    partner_indices = rt.partner_mask_indices(device_valid_mask, partner="numba")
    cuda.synchronize()

    observed_candidates = result["outputs"]["selected_candidate_row_ids"].copy_to_host()
    observed_indices = result["outputs"]["original_indices"].copy_to_host()
    observed_partner_indices = partner_indices.copy_to_host()
    candidates_match = bool(np.array_equal(observed_candidates, expected_candidates))
    indices_match = bool(np.array_equal(observed_indices, expected_indices))
    partner_indices_match = bool(np.array_equal(observed_partner_indices, expected_indices))
    metadata = result["metadata"]
    handoff_validation = metadata["v2_6_neutral_handoff_validation"]
    status = "pass" if candidates_match and indices_match and partner_indices_match else "fail"

    payload = _payload(
        status=status,
        rows=rows,
        started=started,
        block_size=block_size,
        selected_count=int(expected_indices.size),
        app=result["app"],
        mode=result["mode"],
        operation=result["operation"],
        selected_partner=result["partner"],
        candidates_match_cpu=candidates_match,
        indices_match_cpu=indices_match,
        partner_indices_match_cpu=partner_indices_match,
        stable_input_order=bool(metadata["stable_input_order"]),
        host_prefix_sum_used=bool(metadata["host_prefix_sum_used"]),
        neutral_handoff_status=handoff_validation["status"],
        neutral_handoff_errors=tuple(handoff_validation["errors"]),
        uses_legacy_torch_carrier=bool(metadata["uses_legacy_torch_carrier"]),
        uses_torch_conversion=bool(metadata["uses_torch_conversion"]),
        replaces_rt_traversal=bool(metadata["replaces_rt_traversal"]),
        promoted_performance_path=bool(metadata["promoted_performance_path"]),
        first_observed_candidates=tuple(int(value) for value in observed_candidates[:8]),
        last_observed_candidates=tuple(int(value) for value in observed_candidates[-8:]),
        first_observed_indices=tuple(int(value) for value in observed_indices[:8]),
        last_observed_indices=tuple(int(value) for value in observed_indices[-8:]),
        gpu=str(cuda.get_current_device()),
        nvidia_smi=_nvidia_smi(),
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
        source_dirty=_git("status", "--short", "--untracked-files=no").splitlines(),
    )
    _write(args.output, payload)
    print(f"[goal3000] wrote {args.output}", flush=True)
    print(f"[goal3000] status={status}", flush=True)
    return 0 if status == "pass" else 1


def _payload(*, status: str, rows: int, started: float, **extra: Any) -> dict[str, Any]:
    return {
        "goal": "Goal3000",
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
            "triangle_counting_whole_app_speedup_claim_authorized": False,
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


def _nvidia_smi() -> str:
    try:
        completed = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
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

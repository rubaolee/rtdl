#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def _columns(torch, *, ids, x, y) -> dict[str, object]:
    return {
        "ids": torch.tensor(ids, dtype=torch.uint32, device="cuda"),
        "x": torch.tensor(x, dtype=torch.float64, device="cuda"),
        "y": torch.tensor(y, dtype=torch.float64, device="cuda"),
    }


def _read(outputs: dict[str, object]) -> dict[str, list[int]]:
    return {name: [int(value) for value in tensor.detach().cpu().tolist()] for name, tensor in outputs.items()}


def run() -> dict[str, object]:
    try:
        import torch
        import rtdsl
    except Exception as exc:  # pragma: no cover - depends on local GPU env
        raise RuntimeError(
            "V4 PyTorch hello requires PyTorch CUDA, this source tree on PYTHONPATH, and build/librtdl_optix.so"
        ) from exc
    if not torch.cuda.is_available():
        raise RuntimeError("PyTorch CUDA is not available")

    stream = torch.cuda.Stream()
    with torch.cuda.stream(stream):
        search = _columns(
            torch,
            ids=[10, 11, 12],
            x=[0.0, 4.0, 9.0],
            y=[0.0, 0.0, 9.0],
        )
        query = _columns(
            torch,
            ids=[1, 2, 3],
            x=[0.0, 4.0, 1.5],
            y=[0.0, 0.0, 1.5],
        )
        outputs = {
            "query_ids": torch.empty((3,), dtype=torch.uint32, device="cuda"),
            "neighbor_counts": torch.empty((3,), dtype=torch.uint32, device="cuda"),
            "threshold_flags": torch.empty((3,), dtype=torch.uint32, device="cuda"),
        }
        result = rtdsl.run_v4_fixed_radius_count_threshold_2d(
            query,
            search,
            radius=1.1,
            threshold=1,
            partner="torch",
            output_columns=outputs,
            stream=stream,
            return_metadata=True,
        )
    stream.synchronize()

    observed = _read(outputs)
    expected = {
        "query_ids": [1, 2, 3],
        "neighbor_counts": [1, 1, 0],
        "threshold_flags": [1, 1, 0],
    }
    if observed != expected:
        raise AssertionError(f"unexpected V4 PyTorch output: observed={observed!r} expected={expected!r}")

    metadata = result["metadata"]
    return {
        "status": "pass",
        "framework": "pytorch",
        "route_id": metadata["v4_route_id"],
        "observed": observed,
        "expected": expected,
        "metadata_subset": {
            "caller_stream_handle_nonzero": int(metadata["caller_stream_handle"]) != 0,
            "native_synchronized_before_return": bool(metadata["native_synchronized_before_return"]),
            "native_async_ready": bool(metadata["native_async_ready"]),
        },
        "claim_boundaries": {
            "v4_current_front_door_authorized": True,
            "package_install_claim_authorized": False,
            "full_pytorch_surface_claim_authorized": False,
            "public_true_zero_copy_claim_authorized": False,
            "async_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
        },
    }


def main() -> int:
    print(json.dumps(run(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

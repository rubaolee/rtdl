#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
RAYJOIN_APP = ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"
SCHEMA = "rtdl.goal5052.v2_14_4_public_api_pod_smoke.v1"


def _ensure_paths() -> None:
    for path in (str(SRC), str(RAYJOIN_APP.parent)):
        if path not in sys.path:
            sys.path.insert(0, path)
    if "RTDL_OPTIX_LIBRARY" not in os.environ:
        candidate = ROOT / "build" / "librtdl_optix.so"
        if candidate.exists():
            os.environ["RTDL_OPTIX_LIBRARY"] = str(candidate)


def _load_rayjoin_binary_app():
    spec = importlib.util.spec_from_file_location(
        "goal5052_section57_overlay_columnar_binary",
        RAYJOIN_APP,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {RAYJOIN_APP}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _cuda_module():
    try:
        from numba import cuda
    except Exception as exc:  # pragma: no cover - depends on environment.
        return None, f"numba import failed: {exc}"
    try:
        if cuda.is_available():
            return cuda, None
        cuda.current_context()
        return cuda, None
    except Exception as exc:  # pragma: no cover - depends on environment.
        return None, f"numba cuda unavailable: {exc}"


def _record_step(label: str, fn) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        payload = dict(fn())
        status = str(payload.pop("status", "pass"))
        return {
            "label": label,
            "status": status,
            "elapsed_sec": time.perf_counter() - started,
            **payload,
        }
    except Exception as exc:
        return {
            "label": label,
            "status": "fail",
            "elapsed_sec": time.perf_counter() - started,
            "error": f"{type(exc).__name__}: {exc}",
        }


def _smoke_public_numba_partner() -> dict[str, Any]:
    _ensure_paths()
    cuda, reason = _cuda_module()
    if cuda is None:
        return {"status": "skip", "reason": reason}
    import rtdsl as rt

    values = cuda.to_device(np.asarray([1, 7, 7, 3], dtype=np.uint32))
    buffer = rt.device_column_buffer(
        {"values": values},
        producer="goal5052_public_numba_values",
        producer_consumer_stream_ordering="same_stream",
        native_device_column_output_proven_on_hardware=True,
    )
    plan = rt.numba_partner_continuation(
        operation=rt.NUMBA_UINT32_EQUAL_MASK_OPERATION,
        input_buffer=buffer,
        input_bindings={"values": "values"},
        scalar_inputs={"target": 7},
    )
    result = rt.run_numba_partner_continuation(plan, skip_if_cuda_unavailable=False)
    mask = result.outputs["mask"].copy_to_host().astype(bool).tolist()
    expected = [False, True, True, False]
    if mask != expected:
        raise AssertionError(f"unexpected mask {mask}, expected {expected}")
    metadata = result.to_metadata()
    return {
        "status": "pass",
        "operation": rt.NUMBA_UINT32_EQUAL_MASK_OPERATION,
        "mask": mask,
        "host_fallback_used": bool(metadata["host_fallback_used"]),
        "public_speedup_claim_authorized": bool(metadata["public_speedup_claim_authorized"]),
        "true_zero_copy_claim_authorized": bool(metadata["true_zero_copy_claim_authorized"]),
    }


def _smoke_rayjoin_public_device_order_by_path() -> dict[str, Any]:
    _ensure_paths()
    cuda, reason = _cuda_module()
    if cuda is None:
        return {"status": "skip", "reason": reason}
    if not os.environ.get("RTDL_OPTIX_LIBRARY"):
        return {"status": "skip", "reason": "RTDL_OPTIX_LIBRARY is not set and build/librtdl_optix.so is absent"}

    app = _load_rayjoin_binary_app()
    edge = cuda.to_device(np.asarray([2, 1, 1, 2], dtype=np.int64))
    dist = cuda.to_device(np.asarray([0.5, 0.3, 0.2, 0.1], dtype=np.float64))
    tie = cuda.to_device(np.asarray([9, 5, 4, 7], dtype=np.int64))
    order = cuda.to_device(np.asarray([0, 1, 2, 3], dtype=np.int64))
    metadata = app._run_public_device_order_by_native_lexsort(
        edge,
        dist,
        tie,
        order,
        count=4,
        producer="goal5052_rayjoin_sort_keys",
    )
    observed_order = order.copy_to_host().astype(np.int64).tolist()
    expected_order = [2, 1, 3, 0]
    if observed_order != expected_order:
        raise AssertionError(f"unexpected sorted order {observed_order}, expected {expected_order}")
    return {
        "status": "pass",
        "observed_order": observed_order,
        "public_device_order_by_used": bool(metadata.get("public_device_order_by_used")),
        "backend": str(metadata.get("backend", "")),
        "contract_version": str(metadata.get("public_device_order_by_contract_version", "")),
    }


def run_smokes(*, strict: bool) -> dict[str, Any]:
    steps = [
        _record_step("public_numba_partner_continuation_cuda", _smoke_public_numba_partner),
        _record_step("rayjoin_public_device_order_by_native_cuda_path", _smoke_rayjoin_public_device_order_by_path),
    ]
    failed = [step for step in steps if step["status"] == "fail"]
    skipped = [step for step in steps if step["status"] == "skip"]
    overall = "pass"
    if failed:
        overall = "fail"
    elif strict and skipped:
        overall = "fail"
    elif skipped:
        overall = "partial_skip"
    return {
        "schema": SCHEMA,
        "strict": bool(strict),
        "overall_status": overall,
        "steps": steps,
        "not_authorized": {
            "public_speedup_claim": True,
            "true_zero_copy_claim": True,
            "author_parity_claim": True,
            "device_group_by_public_ready": True,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--strict", action="store_true", help="Treat skipped smoke steps as failure.")
    args = parser.parse_args(argv)

    payload = run_smokes(strict=bool(args.strict))
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["overall_status"] != "fail" else 1


if __name__ == "__main__":
    raise SystemExit(main())

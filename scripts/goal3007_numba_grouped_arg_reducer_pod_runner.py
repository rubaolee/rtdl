from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from time import perf_counter
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def _git_output(*args: str) -> str:
    return subprocess.check_output(("git", *args), cwd=ROOT, text=True).strip()


def _git_status() -> list[str]:
    return subprocess.check_output(("git", "status", "--short"), cwd=ROOT, text=True).splitlines()


def _activate_numba_cuda_redirector() -> None:
    try:
        import _numba_cuda_redirector  # noqa: F401
    except ImportError:
        pass


def _toolchain() -> dict[str, object]:
    _activate_numba_cuda_redirector()
    import numba
    from numba import cuda

    device = cuda.get_current_device()
    return {
        "python": sys.version.split()[0],
        "numba_version": numba.__version__,
        "numba_cuda_module": cuda.__file__,
        "cuda_available": bool(cuda.is_available()),
        "gpu_name": device.name.decode() if isinstance(device.name, bytes) else str(device.name),
        "compute_capability": list(device.compute_capability),
    }


def _make_tie_fixture(np) -> dict[str, object]:
    return {
        "name": "tie_fixture",
        "group_count": 4,
        "group_ids": np.asarray([0, 0, 1, 1, 1], dtype=np.int64),
        "item_ids": np.asarray([9, 8, 2, 1, 3], dtype=np.int64),
        "scores": np.asarray([4.0, 4.0, 7.0, 5.0, 5.0], dtype=np.float64),
    }


def _make_large_stream(np, *, row_count: int, group_count: int) -> dict[str, object]:
    rows = np.arange(row_count, dtype=np.int64)
    group_ids = rows % int(group_count)
    item_ids = ((rows * 17) + 11) % max(1, row_count * 3)
    scores = ((rows * 1009) % 1_000_003).astype(np.float64) / 1_000_003.0
    if row_count >= 8 and group_count >= 4:
        group_ids[:8] = np.asarray([0, 0, 1, 1, 2, 2, 3, 3], dtype=np.int64)
        item_ids[:8] = np.asarray([9, 8, 2, 1, 5, 4, 6, 7], dtype=np.int64)
        scores[:8] = np.asarray([4.0, 4.0, 7.0, 5.0, 5.0, 5.0, 1.0, 3.0], dtype=np.float64)
    return {
        "name": "large_stream",
        "group_count": int(group_count),
        "group_ids": group_ids,
        "item_ids": item_ids.astype(np.int64, copy=False),
        "scores": scores,
    }


def _reference_arg_reduce(np, group_ids, item_ids, scores, *, group_count: int, reduce: str) -> dict[str, object]:
    counts = np.zeros((group_count,), dtype=np.int64)
    fill = np.inf if reduce == "argmin" else -np.inf
    dense_scores = np.full((group_count,), fill, dtype=np.float64)
    dense_item_ids = np.full((group_count,), np.iinfo(np.int64).max, dtype=np.int64)
    for group, item, score in zip(group_ids, item_ids, scores):
        group_i = int(group)
        item_i = int(item)
        score_f = float(score)
        counts[group_i] += 1
        if reduce == "argmin":
            better = score_f < dense_scores[group_i]
        else:
            better = score_f > dense_scores[group_i]
        tied = score_f == dense_scores[group_i] and item_i < int(dense_item_ids[group_i])
        if better or tied:
            dense_scores[group_i] = score_f
            dense_item_ids[group_i] = item_i
    present = np.nonzero(counts > 0)[0].astype(np.int64)
    missing = np.nonzero(counts == 0)[0].astype(np.int64)
    return {
        "group_ids": present,
        "item_ids": dense_item_ids[present],
        "scores": dense_scores[present],
        "missing_group_ids": missing,
        "dense_item_ids": dense_item_ids,
        "dense_scores": dense_scores,
        "present_counts": counts,
    }


def _device_to_host(columns: dict[str, Any]) -> dict[str, Any]:
    return {name: value.copy_to_host() for name, value in columns.items()}


def _compare(np, expected: dict[str, Any], observed: dict[str, Any]) -> dict[str, bool]:
    return {
        "group_ids_match": bool(np.array_equal(observed["group_ids"], expected["group_ids"])),
        "item_ids_match": bool(np.array_equal(observed["item_ids"], expected["item_ids"])),
        "scores_match": bool(np.allclose(observed["scores"], expected["scores"], rtol=0.0, atol=0.0)),
        "missing_group_ids_match": bool(np.array_equal(observed["missing_group_ids"], expected["missing_group_ids"])),
        "dense_item_ids_match": bool(np.array_equal(observed["dense_item_ids"], expected["dense_item_ids"])),
        "dense_scores_match": bool(np.allclose(observed["dense_scores"], expected["dense_scores"], rtol=0.0, atol=0.0)),
        "present_counts_match": bool(np.array_equal(observed["present_counts"], expected["present_counts"])),
    }


def _all_true(values: dict[str, bool]) -> bool:
    return all(bool(value) for value in values.values())


def _run_case(rt, cuda, np, case: dict[str, object], *, block_size: int) -> dict[str, object]:
    print(f"[goal3007] running {case['name']} rows={len(case['group_ids'])} groups={case['group_count']}", flush=True)
    group_ids = cuda.to_device(case["group_ids"])
    item_ids = cuda.to_device(case["item_ids"])
    scores = cuda.to_device(case["scores"])
    group_count = int(case["group_count"])

    argmin_expected = _reference_arg_reduce(
        np,
        case["group_ids"],
        case["item_ids"],
        case["scores"],
        group_count=group_count,
        reduce="argmin",
    )
    argmax_expected = _reference_arg_reduce(
        np,
        case["group_ids"],
        case["item_ids"],
        case["scores"],
        group_count=group_count,
        reduce="argmax",
    )

    argmin_started = perf_counter()
    argmin_result = rt.run_numba_grouped_argmin_f64(
        group_ids,
        item_ids,
        scores,
        group_count=group_count,
        block_size=block_size,
    )
    cuda.synchronize()
    argmin_wall_sec = perf_counter() - argmin_started

    argmax_started = perf_counter()
    argmax_result = rt.grouped_argmax_f64_partner_columns(
        {"group_ids": group_ids, "item_ids": item_ids, "scores": scores},
        group_count=group_count,
        partner="numba",
        return_metadata=True,
    )
    cuda.synchronize()
    argmax_wall_sec = perf_counter() - argmax_started

    argmin_observed = _device_to_host(argmin_result["outputs"])
    argmax_observed = _device_to_host(argmax_result["columns"])
    argmin_matches = _compare(np, argmin_expected, argmin_observed)
    argmax_matches = _compare(np, argmax_expected, argmax_observed)
    print(
        f"[goal3007] {case['name']} argmin={_all_true(argmin_matches)} argmax={_all_true(argmax_matches)}",
        flush=True,
    )
    return {
        "case": str(case["name"]),
        "row_count": int(len(case["group_ids"])),
        "group_count": group_count,
        "block_size": int(block_size),
        "argmin_matches": argmin_matches,
        "argmax_matches": argmax_matches,
        "argmin_all_match": _all_true(argmin_matches),
        "argmax_all_match": _all_true(argmax_matches),
        "argmin_wall_sec": argmin_wall_sec,
        "argmax_wall_sec": argmax_wall_sec,
        "argmin_phase_sec": float(argmin_result["phase_timing"]["phases_sec"]["partner_continuation"]),
        "argmax_phase_sec": float(argmax_result["metadata"]["partner_elapsed_seconds"]),
        "argmin_tie_break": argmin_result["tie_break"],
        "argmax_tie_break": argmax_result["metadata"]["tie_break"],
        "argmin_host_present_group_compaction_used": bool(argmin_result["host_present_group_compaction_used"]),
        "argmax_partner": argmax_result["metadata"]["partner"],
        "argmax_adapter": argmax_result["metadata"]["adapter"],
        "argmax_rt_core_speedup_claim_authorized": bool(argmax_result["metadata"]["rt_core_speedup_claim_authorized"]),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal3007 Numba grouped arg reducer pod validation.")
    parser.add_argument("--rows", type=int, default=1_000_000)
    parser.add_argument("--groups", type=int, default=4096)
    parser.add_argument("--block-size", type=int, default=256)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    _activate_numba_cuda_redirector()
    import numpy as np
    from numba import cuda
    import rtdsl as rt

    if not cuda.is_available():
        raise RuntimeError("CUDA is required for Goal3007 pod validation")

    cases = (
        _make_tie_fixture(np),
        _make_large_stream(np, row_count=int(args.rows), group_count=int(args.groups)),
    )
    case_results = [_run_case(rt, cuda, np, case, block_size=int(args.block_size)) for case in cases]
    all_match = all(row["argmin_all_match"] and row["argmax_all_match"] for row in case_results)
    artifact = {
        "goal": "Goal3007",
        "status": "pass" if all_match else "fail",
        "app": "generic_partner_continuation",
        "operation_family": "numba_grouped_argmin_argmax_f64",
        "selected_partner": "numba",
        "source_commit": _git_output("rev-parse", "HEAD"),
        "source_dirty": _git_status(),
        "toolchain": _toolchain(),
        "case_results": case_results,
        "all_cases_match_cpu_reference": all_match,
        "uses_v2_6_neutral_partner_handoff": True,
        "uses_legacy_torch_carrier": False,
        "uses_torch_conversion": False,
        "replaces_rt_traversal": False,
        "host_present_group_compaction_used": True,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "numba_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "automatic_partner_selection_allowed": False,
        "app_specific_native_engine_logic_authorized": False,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3007] wrote {output} status={artifact['status']}", flush=True)
    return 0 if all_match else 1


if __name__ == "__main__":
    raise SystemExit(main())

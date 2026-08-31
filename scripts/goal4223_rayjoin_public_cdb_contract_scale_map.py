from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from time import perf_counter
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from examples.current.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    _load_rayjoin_case,
)
from scripts.goal2159_rayjoin_public_cdb_runner import CASES  # noqa: E402
from scripts.goal2159_rayjoin_public_cdb_runner import _materialize_slices  # noqa: E402
from scripts.goal2159_rayjoin_public_cdb_runner import _maybe_download_samples  # noqa: E402
from scripts.goal2159_rayjoin_public_cdb_runner import _resolve_dataset_template  # noqa: E402
from scripts.goal3834_rayjoin_public_cdb_numba_pip_partner_baseline import (  # noqa: E402
    run_numba_pip_baseline,
)
from scripts.goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_baseline import (  # noqa: E402
    run_numba_baseline_loaded_case,
    run_rtdl_optix_loaded_case,
)
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import _claim_boundary  # noqa: E402
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import run_rtdl_optix  # noqa: E402


SCHEMA = "rtdl.goal4223.rayjoin_public_cdb_contract_scale_map.v1"
DEFAULT_DATA_DIR = Path("/root/rtdl/data/rayjoin_public_cdb")
DEFAULT_CASES = (
    "pip_county512",
    "lsi_county256_soil256_count128",
    "lsi_county256_soil256_count256",
    "lsi_county256_soil256_count512",
    "overlay_county128_soil128",
    "overlay_county256_soil256",
    "overlay_county512_soil512",
)
CLAIM_BOUNDARY = {
    **_claim_boundary(),
    "automatic_partner_selection_authorized": False,
    "app_specific_native_engine_logic_allowed": False,
    "rayjoin_paper_reproduction_claim_authorized": False,
}


def _git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _nvidia_smi() -> str:
    try:
        return subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return ""


def _ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator == 0.0:
        return None
    return float(numerator) / float(denominator)


def _hot(row: dict[str, Any] | None) -> float | None:
    if not isinstance(row, dict):
        return None
    value = row.get("hot_median_sec")
    return None if value is None else float(value)


def _row_count(row: dict[str, Any] | None) -> int | None:
    if not isinstance(row, dict):
        return None
    value = row.get("row_count")
    return None if value is None else int(value)


def _input_counts(row: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(row, dict):
        return {}
    value = row.get("input_counts")
    return value if isinstance(value, dict) else {}


def _recommend(workload: str, rtdl_speedup_vs_numba: float | None) -> str:
    if rtdl_speedup_vs_numba is None:
        return "needs_more_evidence"
    if rtdl_speedup_vs_numba >= 1.0:
        if workload == "pip":
            return "rtdl_optix_prepared_point_shape_route"
        if workload == "lsi":
            return "rtdl_optix_prepared_segment_pair_count"
        return "rtdl_optix_prepared_shape_pair_active_count"
    return "numba_cuda_jit_scalar_count"


def _run_case(case_id: str, dataset: str, *, repeat: int, warmup: int, block_size: int) -> dict[str, Any]:
    case_spec = CASES[case_id]
    workload = case_spec.workload
    print(f"[goal4223] case begin {case_id} workload={workload}", flush=True)
    started = perf_counter()

    if workload == "pip":
        numba_row = run_numba_pip_baseline(dataset, repeat=repeat, warmup=warmup, block_size=block_size)
        rtdl_row = run_rtdl_optix("pip", dataset, repeat=repeat, warmup=warmup)
    else:
        loaded = _load_rayjoin_case(workload, dataset, segment_column_inputs=workload == "lsi")
        numba_row = run_numba_baseline_loaded_case(
            workload,
            dataset,
            case=loaded,
            repeat=repeat,
            warmup=warmup,
            block_size=block_size,
            load_case_sec=0.0,
            case_loaded_by_caller=True,
        )
        rtdl_row = run_rtdl_optix_loaded_case(
            workload,
            dataset,
            case=loaded,
            repeat=repeat,
            warmup=warmup,
        )

    numba_hot = _hot(numba_row)
    rtdl_hot = _hot(rtdl_row)
    speedup = _ratio(numba_hot, rtdl_hot)
    counts_match = _row_count(numba_row) == _row_count(rtdl_row)
    row = {
        "case_id": case_id,
        "workload": workload,
        "dataset": dataset,
        "numba_hot_median_sec": numba_hot,
        "rtdl_optix_hot_median_sec": rtdl_hot,
        "rtdl_optix_speedup_vs_numba": speedup,
        "numba_row_count": _row_count(numba_row),
        "rtdl_optix_row_count": _row_count(rtdl_row),
        "counts_match": counts_match,
        "numba_input_counts": _input_counts(numba_row),
        "numba_candidate_pair_count": numba_row.get("candidate_pair_count"),
        "rtdl_execution_route": rtdl_row.get("execution_route"),
        "rtdl_rt_core_accelerated": bool(rtdl_row.get("rt_core_accelerated", True)),
        "numba_rawkernel_required": bool(numba_row.get("raw_kernel_required", False)),
        "recommended_route": _recommend(workload, speedup),
        "elapsed_outer_sec": perf_counter() - started,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    print(
        f"[goal4223] case done {case_id} speedup={speedup} "
        f"recommended={row['recommended_route']}",
        flush=True,
    )
    return row


def _selected_cases(value: str) -> tuple[str, ...]:
    if value == "default":
        return DEFAULT_CASES
    selected = tuple(part.strip() for part in value.split(",") if part.strip())
    if not selected:
        raise ValueError("case list is empty")
    unknown = [case_id for case_id in selected if case_id not in CASES]
    if unknown:
        raise ValueError(f"unknown cases: {unknown}")
    return selected


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    started = perf_counter()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir = args.data_dir.resolve()
    selected_ids = _selected_cases(args.cases)
    selected_specs = tuple(CASES[case_id] for case_id in selected_ids)

    _maybe_download_samples(data_dir, download=args.download)
    slices = _materialize_slices(data_dir, selected_specs)
    manifest: dict[str, Any] = {
        "goal": "Goal4223",
        "schema": SCHEMA,
        "status": "running",
        "source_commit": _git("rev-parse", "--short", "HEAD"),
        "source_dirty": _git("status", "--short", "--untracked-files=no").splitlines(),
        "gpu": _nvidia_smi(),
        "data_dir": str(data_dir),
        "artifact_root": str(output_dir),
        "cases": list(selected_ids),
        "repeat": args.repeat,
        "warmup": args.warmup,
        "block_size": args.block_size,
        "slice_manifest": slices,
        "rows": [],
        "claim_boundary": CLAIM_BOUNDARY,
        "boundary": (
            "Internal RayJoin public-CDB contract scale map. This is route-policy "
            "evidence over bounded slices, not a RayJoin paper reproduction, not "
            "automatic dispatch, not public speedup evidence, and not release evidence."
        ),
    }
    _write(output_dir / "summary.json", manifest)
    print(
        f"[goal4223] start cases={selected_ids} repeat={args.repeat} warmup={args.warmup}",
        flush=True,
    )
    for case_id in selected_ids:
        dataset = _resolve_dataset_template(CASES[case_id].dataset, slices)
        row = _run_case(case_id, dataset, repeat=args.repeat, warmup=args.warmup, block_size=args.block_size)
        manifest["rows"].append(row)
        _write(output_dir / "summary.json", manifest)
        if not row["counts_match"]:
            manifest["status"] = "fail"
            _write(output_dir / "summary.json", manifest)
            raise RuntimeError(f"{case_id}: Numba and RTDL/OptiX counts differ")

    manifest["status"] = "pass"
    manifest["elapsed_sec"] = perf_counter() - started
    manifest["recommended_route_counts"] = {
        route: sum(1 for row in manifest["rows"] if row["recommended_route"] == route)
        for route in sorted({row["recommended_route"] for row in manifest["rows"]})
    }
    _write(output_dir / "summary.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True), flush=True)
    print("[goal4223] complete", flush=True)
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Map RayJoin same-contract route choices over public-CDB slices.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--cases", default="default")
    parser.add_argument("--repeat", type=int, default=20)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--block-size", type=int, default=128)
    parser.add_argument("--download", action="store_true")
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())

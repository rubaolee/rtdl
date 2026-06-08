from __future__ import annotations

import argparse
import contextlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.goal3310_rayjoin_pip_batch_scalar_count_probe import run_probe as run_pip_batch_probe  # noqa: E402
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import _claim_boundary  # noqa: E402
from scripts.goal3834_rayjoin_public_cdb_numba_pip_partner_baseline import run_probe as run_pip_probe  # noqa: E402
from scripts.goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_baseline import run_probe as run_lsi_overlay_probe  # noqa: E402


SCHEMA = "rtdl.goal3866.rayjoin_representative_scale_profile.v1"
DEFAULT_DATA_DIR_CANDIDATES = (
    "RTDL_RAYJOIN_PUBLIC_CDB_DIR",
    "/root/rtdl_goal3293/data/rayjoin_public_cdb",
    "/root/rtdl/data/rayjoin_public_cdb",
    "data/rayjoin_public_cdb",
    "data/rayjoin",
)
PIP_DATASET_NAME = "br_county_start256_count512.cdb"
SOIL_DATASET_NAME = "br_soil_start256_count512.cdb"


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _resolve_data_dir(value: str | None) -> Path:
    candidates: list[Path] = []
    if value:
        candidates.append(Path(value))
    for candidate in DEFAULT_DATA_DIR_CANDIDATES:
        env_value = os.environ.get(candidate)
        if env_value:
            candidates.append(Path(env_value))
        elif candidate.startswith(("data/", "/")):
            candidates.append(Path(candidate))

    for candidate in candidates:
        resolved = candidate if candidate.is_absolute() else ROOT / candidate
        if (resolved / PIP_DATASET_NAME).exists() and (resolved / SOIL_DATASET_NAME).exists():
            return resolved
    checked = [str(path if path.is_absolute() else ROOT / path) for path in candidates]
    raise FileNotFoundError(
        "RayJoin public-CDB data directory not found; checked: " + ", ".join(checked)
    )


def _ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator == 0.0:
        return None
    return float(numerator) / float(denominator)


@contextlib.contextmanager
def _temporary_env(name: str, value: str | None):
    old = os.environ.get(name)
    if value is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = value
    try:
        yield
    finally:
        if old is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = old


def _hot(row: dict[str, Any] | None) -> float | None:
    if not isinstance(row, dict):
        return None
    value = row.get("hot_median_sec")
    return None if value is None else float(value)


def _case_summary(row: dict[str, Any]) -> dict[str, Any]:
    numba = row.get("numba_cuda_jit_baseline")
    optix = row.get("rtdl_optix")
    numba_hot = _hot(numba if isinstance(numba, dict) else None)
    optix_hot = _hot(optix if isinstance(optix, dict) else None)
    return {
        "workload": row["workload"],
        "dataset": row["dataset"],
        "counts_match": bool(row["counts_match"]),
        "numba_hot_median_sec": numba_hot,
        "rtdl_optix_hot_median_sec": optix_hot,
        "rtdl_optix_speedup_vs_numba": _ratio(numba_hot, optix_hot),
        "numba_speedup_vs_rtdl_optix": _ratio(optix_hot, numba_hot),
        "numba_rawkernel_required": False,
        "recommended_route": (
            "numba_cuda_jit_scalar_count"
            if row["workload"] == "pip"
            else "rtdl_optix_prepared_scalar_count"
        ),
    }


def _pip_batch_summary(payload: dict[str, Any]) -> dict[str, Any]:
    rows = {
        int(row["request_count"]): row
        for row in payload.get("batch_rows", [])
        if isinstance(row, dict) and row.get("request_count") is not None
    }
    largest_request = max(rows) if rows else None
    largest = rows.get(largest_request) if largest_request is not None else None
    return {
        "dataset": payload.get("dataset"),
        "exact_count": payload.get("exact_count"),
        "point_count": payload.get("point_count"),
        "shape_count": payload.get("shape_count"),
        "single_ms_median": payload.get("single_ms_median"),
        "largest_request_count": largest_request,
        "largest_request_per_request_ms_median": (
            None if largest is None else largest.get("per_request_ms_median")
        ),
        "largest_request_total_ms_median": None if largest is None else largest.get("total_ms_median"),
        "largest_request_effective_streams": (
            None if largest is None else largest.get("batch_stream_count_effective")
        ),
        "recommended_route": "rtdl_optix_prepared_pip_batch_executor",
        "throughput_evidence_not_one_shot_latency": True,
    }


def _hot_path_summary(
    *,
    cases: list[dict[str, Any]],
    pip_batch: dict[str, Any],
    wrapper_elapsed_sec: float,
) -> dict[str, Any]:
    cases_by_workload = {str(row["workload"]): row for row in cases}
    pip_one_shot = cases_by_workload.get("pip", {})
    lsi = cases_by_workload.get("lsi", {})
    overlay = cases_by_workload.get("overlay_seed", {})
    pip_single_ms = pip_batch.get("single_ms_median")
    pip_batched_ms = pip_batch.get("largest_request_per_request_ms_median")
    pip_batch_speedup = _ratio(
        float(pip_single_ms) if pip_single_ms is not None else None,
        float(pip_batched_ms) if pip_batched_ms is not None else None,
    )
    return {
        "metric_scope": "per_contract_hot_medians_not_wrapper_wall_time",
        "scale_runner_elapsed_sec_is_not_hot_path_metric": True,
        "wrapper_elapsed_sec": float(wrapper_elapsed_sec),
        "contract_count": 4,
        "all_contract_counts_match": all(bool(row["counts_match"]) for row in cases),
        "pip_one_shot": {
            "recommended_route": "numba_cuda_jit_scalar_count_no_rawkernel",
            "numba_hot_median_sec": pip_one_shot.get("numba_hot_median_sec"),
            "rtdl_optix_hot_median_sec": pip_one_shot.get("rtdl_optix_hot_median_sec"),
            "rtdl_optix_speedup_vs_numba": pip_one_shot.get("rtdl_optix_speedup_vs_numba"),
            "reason": "bounded one-shot scalar count favors simple partner code at this slice",
        },
        "pip_repeated_requests": {
            "recommended_route": "rtdl_optix_prepared_batch_executor",
            "single_request_ms_median": pip_single_ms,
            "batched_per_request_ms_median": pip_batched_ms,
            "batch_request_count": pip_batch.get("largest_request_count"),
            "per_request_speedup_vs_single_request": pip_batch_speedup,
            "reason": "prepared scene and batched requests amortize traversal setup",
        },
        "lsi_scalar_count": {
            "recommended_route": "rtdl_optix_prepared_segment_pair_count",
            "numba_hot_median_sec": lsi.get("numba_hot_median_sec"),
            "rtdl_optix_hot_median_sec": lsi.get("rtdl_optix_hot_median_sec"),
            "rtdl_optix_speedup_vs_numba": lsi.get("rtdl_optix_speedup_vs_numba"),
            "reason": "fused generic segment-pair scalar count avoids dense partner looping",
        },
        "overlay_active_count": {
            "recommended_route": "rtdl_optix_prepared_shape_pair_active_count",
            "numba_hot_median_sec": overlay.get("numba_hot_median_sec"),
            "rtdl_optix_hot_median_sec": overlay.get("rtdl_optix_hot_median_sec"),
            "rtdl_optix_speedup_vs_numba": overlay.get("rtdl_optix_speedup_vs_numba"),
            "reason": "fused generic shape-pair active count avoids dense partner looping",
        },
        "recommended_route_summary": {
            "rtdl_optix_contracts": (
                "pip_repeated_requests",
                "lsi_scalar_count",
                "overlay_active_count",
            ),
            "numba_contracts": ("pip_one_shot",),
            "automatic_dispatch": False,
            "user_route_choice_visible": True,
        },
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "app_specific_native_engine_logic_allowed": False,
    }


def build_dry_run(args: argparse.Namespace) -> dict[str, Any]:
    data_dir = Path(args.data_dir) if args.data_dir else Path("<auto>")
    return {
        "schema": SCHEMA,
        "dry_run": True,
        "data_dir": str(data_dir),
        "repeat": args.repeat,
        "warmup": args.warmup,
        "block_size": args.block_size,
        "pip_batch_request_counts": args.pip_batch_request_counts,
        "planned_cases": (
            "PIP one-shot: Numba CUDA JIT scalar count, with RTDL/OptiX context",
            "PIP repeated: RTDL/OptiX prepared point/closed-shape batch executor",
            "LSI: RTDL/OptiX prepared segment-pair scalar count, with Numba reference",
            "Overlay active count: RTDL/OptiX prepared shape-pair active count, with Numba reference",
        ),
        "claim_boundary": _claim_boundary(),
    }


def run_representative_profile(args: argparse.Namespace) -> dict[str, Any]:
    profile_started = time.perf_counter()
    data_dir = _resolve_data_dir(args.data_dir)
    pip_dataset = data_dir / PIP_DATASET_NAME

    with contextlib.redirect_stdout(sys.stderr):
        pip_payload = run_pip_probe(
            data_dir=data_dir,
            repeat=args.repeat,
            warmup=args.warmup,
            block_size=args.block_size,
            skip_cupy=True,
            skip_optix=False,
        )
        lsi_overlay_payload = run_lsi_overlay_probe(
            data_dir=data_dir,
            cases=("lsi_county512_soil512", "overlay_county512_soil512"),
            repeat=args.repeat,
            warmup=args.warmup,
            block_size=args.block_size,
            skip_cupy=True,
            skip_optix=False,
        )
        with _temporary_env(
            "RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS",
            args.pip_batch_device_predicate_eps,
        ):
            pip_batch_payload = run_pip_batch_probe(
                SimpleNamespace(
                    dataset=pip_dataset,
                    query_axis=args.pip_batch_query_axis,
                    boundary_mode=args.pip_batch_boundary_mode,
                    scalar_count_pipeline=True,
                    batch_stream_count=args.pip_batch_stream_count,
                    batch_executor=True,
                    single_warmup=args.pip_batch_single_warmup,
                    single_repeat=args.pip_batch_single_repeat,
                    batch_warmup=args.pip_batch_warmup,
                    batch_repeat=args.pip_batch_repeat,
                    request_counts=args.pip_batch_request_counts,
                )
            )

    cases = [
        _case_summary(pip_payload),
        *(_case_summary(row) for row in lsi_overlay_payload["rows"]),
    ]
    pip_batch = _pip_batch_summary(pip_batch_payload)
    wrapper_elapsed_sec = time.perf_counter() - profile_started
    hot_path_summary = _hot_path_summary(
        cases=cases,
        pip_batch=pip_batch,
        wrapper_elapsed_sec=wrapper_elapsed_sec,
    )
    all_counts_match = (
        bool(pip_payload["counts_match"])
        and bool(lsi_overlay_payload["summary"]["all_counts_match"])
        and int(pip_batch_payload["exact_count"]) == int(pip_payload["summary"]["numba_row_count"])
    )

    return {
        "schema": SCHEMA,
        "dry_run": False,
        "generated_at_unix": time.time(),
        "git_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "git_status_short": _command_output(["git", "status", "--short"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "data_dir": str(data_dir),
        "repeat": args.repeat,
        "warmup": args.warmup,
        "block_size": args.block_size,
        "cases": cases,
        "pip_batch_executor": pip_batch,
        "representative_hot_path_summary": hot_path_summary,
        "wrapper_elapsed_sec": wrapper_elapsed_sec,
        "pip_batch_device_predicate_eps": args.pip_batch_device_predicate_eps,
        "recommended_route_summary": {
            "pip_one_shot": "numba_cuda_jit_scalar_count_no_rawkernel",
            "pip_repeated_requests": "rtdl_optix_prepared_batch_executor",
            "lsi_scalar_count": "rtdl_optix_prepared_segment_pair_count",
            "overlay_active_count": "rtdl_optix_prepared_shape_pair_active_count",
            "automatic_dispatch": False,
            "user_route_choice_visible": True,
        },
        "all_counts_match": all_counts_match,
        "numba_reference_available_for_custom_logic": True,
        "cupy_required_for_reference_route": False,
        "raw_cuda_kernel_required_for_reference_route": False,
        "representative_scale_profile": True,
        "boundary": (
            "Representative RayJoin current-route scale profile over bounded public-CDB slices. "
            "This is not a RayJoin paper reproduction, not automatic dispatch, not a public "
            "speedup claim, and not release evidence."
        ),
        "claim_boundary": {
            **_claim_boundary(),
            "automatic_partner_selection_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal3866 RayJoin representative current scale profile.")
    parser.add_argument("--data-dir", default=None)
    parser.add_argument("--repeat", type=int, default=50)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--block-size", type=int, default=128)
    parser.add_argument("--pip-batch-query-axis", default="z_point")
    parser.add_argument("--pip-batch-boundary-mode", default="inclusive")
    parser.add_argument("--pip-batch-device-predicate-eps", default="1e-9")
    parser.add_argument("--pip-batch-stream-count", default="auto")
    parser.add_argument("--pip-batch-single-warmup", type=int, default=3)
    parser.add_argument("--pip-batch-single-repeat", type=int, default=12)
    parser.add_argument("--pip-batch-warmup", type=int, default=3)
    parser.add_argument("--pip-batch-repeat", type=int, default=8)
    parser.add_argument("--pip-batch-request-counts", type=int, nargs="+", default=[1, 100])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.repeat <= 0:
        raise ValueError("--repeat must be positive")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")
    if args.block_size <= 0:
        raise ValueError("--block-size must be positive")
    if args.pip_batch_single_repeat <= 0 or args.pip_batch_repeat <= 0:
        raise ValueError("PIP batch repeat counts must be positive")
    if not args.pip_batch_request_counts or any(value <= 0 for value in args.pip_batch_request_counts):
        raise ValueError("--pip-batch-request-counts must contain positive integers")

    payload = build_dry_run(args) if args.dry_run else run_representative_profile(args)
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from argparse import Namespace
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts import goal2348_rtnn_v2_2_external_runner as rtnn_runner  # noqa: E402


GOAL2800_HARNESS_VERSION = "rtdl.goal2800.rtnn_v2_5_live_ranked_summary_harness.v1"
DEFAULT_DISTRIBUTIONS = ("uniform", "clustered", "shell")
CLAIM_BOUNDARY = {
    "canonical_live_harness": True,
    "tier_b_same_contract_opponent": True,
    "public_speedup_claim_authorized": False,
    "whole_app_speedup_claim_authorized": False,
    "rtdl_beats_rtnn_claim_authorized": False,
    "rtdl_beats_cupy_grid_claim_authorized": False,
    "broad_rt_core_speedup_claim_authorized": False,
    "triton_speedup_claim_authorized": False,
    "paper_reproduction_claim_authorized": False,
    "native_engine_customization": False,
}


def _check_output(args: list[str]) -> str | None:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def run_goal2800_rtnn_live_harness(
    *,
    point_count: int,
    distributions: tuple[str, ...] = DEFAULT_DISTRIBUTIONS,
    radius: float = 0.02,
    k_max: int = 50,
    query_batch_size: int | None = None,
    repeat: int = 3,
    run_cupy_grid: bool = True,
    work_dir: Path | None = None,
    fail_fast: bool = False,
) -> dict[str, Any]:
    started = time.perf_counter()
    if point_count <= 0:
        raise ValueError("point_count must be positive")
    if k_max <= 0:
        raise ValueError("k_max must be positive")
    batch_size = int(query_batch_size or point_count)
    rows: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="goal2800_rtnn_") as temp_name:
        temp_root = Path(temp_name) if work_dir is None else Path(work_dir)
        temp_root.mkdir(parents=True, exist_ok=True)
        for distribution in distributions:
            if distribution not in DEFAULT_DISTRIBUTIONS:
                raise ValueError(f"unsupported distribution: {distribution}")
            row_started = time.perf_counter()
            point_file = temp_root / f"{distribution}_{int(point_count)}.csv"
            try:
                generated = rtnn_runner.generate_point_file(
                    point_file,
                    point_count=int(point_count),
                    dimension=3,
                    seed=_seed_for_distribution(distribution),
                    distribution=distribution,
                )
                rtdl_payload = rtnn_runner.run_rtdl_batched_3d_neighbors(
                    Namespace(
                        point_file=point_file,
                        query_file=None,
                        radius=float(radius),
                        k_max=int(k_max),
                        backend="optix",
                        query_batch_size=batch_size,
                        result_mode="ranked-summary-raw",
                        repeat=int(repeat),
                        row_label=f"goal2800_rtdl_{distribution}_{int(point_count)}",
                    )
                )
                cupy_payload = None
                if run_cupy_grid:
                    cupy_payload = rtnn_runner.run_cupy_grid_3d_ranked_summary(
                        Namespace(
                            point_file=point_file,
                            query_file=None,
                            radius=float(radius),
                            k_max=int(k_max),
                            dtype="float32",
                            max_grid_cells=2_000_000,
                            repeat=int(repeat),
                            row_label=f"goal2800_cupy_grid_{distribution}_{int(point_count)}",
                        )
                    )
                rows.append(
                    _row_from_payloads(
                        distribution=distribution,
                        generated=generated,
                        rtdl_payload=rtdl_payload,
                        cupy_payload=cupy_payload,
                        elapsed_sec=time.perf_counter() - row_started,
                    )
                )
            except Exception as exc:
                if fail_fast:
                    raise
                rows.append(
                    {
                        "distribution": distribution,
                        "status": "error",
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                        "elapsed_sec": time.perf_counter() - row_started,
                    }
                )

    status = "pass" if rows and all(row["status"] == "pass" for row in rows) else "fail"
    return {
        "goal": "Goal2800",
        "harness_version": GOAL2800_HARNESS_VERSION,
        "status": status,
        "app": "rtnn",
        "benchmark_track": "tier_b_live_exact_fixed_radius_ranked_summary",
        "point_count": int(point_count),
        "radius": float(radius),
        "k_max": int(k_max),
        "query_batch_size": batch_size,
        "repeat": int(repeat),
        "source_commit": _check_output(["git", "rev-parse", "HEAD"]),
        "source_dirty": (_check_output(["git", "status", "--short"]) or "").splitlines(),
        "gpu": _check_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "run_cupy_grid": bool(run_cupy_grid),
        "distributions": distributions,
        "rows": tuple(rows),
        "row_count": len(rows),
        "elapsed_sec": time.perf_counter() - started,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _seed_for_distribution(distribution: str) -> int:
    return {
        "uniform": 2800,
        "clustered": 2801,
        "shell": 2802,
    }[distribution]


def _row_from_payloads(
    *,
    distribution: str,
    generated: dict[str, Any],
    rtdl_payload: dict[str, Any],
    cupy_payload: dict[str, Any] | None,
    elapsed_sec: float,
) -> dict[str, Any]:
    rtdl_candidate_count = _rtdl_raw_candidate_count(rtdl_payload)
    cupy_bounded_count = (
        int(cupy_payload["summary"]["bounded_neighbor_count"])
        if cupy_payload is not None and cupy_payload.get("summary")
        else None
    )
    rtdl_ok = bool(rtdl_payload.get("ok")) and int(rtdl_payload.get("row_count", -1)) == int(
        rtdl_payload.get("query_count", -2)
    )
    cupy_ok = cupy_payload is None or bool(cupy_payload.get("ok"))
    candidate_count_delta = (
        abs(int(cupy_bounded_count) - int(rtdl_candidate_count)) if cupy_bounded_count is not None else None
    )
    candidate_count_tolerance = (
        max(2, int(max(int(cupy_bounded_count), int(rtdl_candidate_count)) * 1.0e-6))
        if cupy_bounded_count is not None
        else None
    )
    candidate_count_matches = cupy_bounded_count is None or candidate_count_delta == 0
    candidate_count_within_tolerance = (
        cupy_bounded_count is None or int(candidate_count_delta) <= int(candidate_count_tolerance)
    )
    status = "pass" if rtdl_ok and cupy_ok and candidate_count_within_tolerance else "mismatch"
    rtdl_elapsed = float(rtdl_payload.get("elapsed_sec", 0.0))
    cupy_elapsed = float(cupy_payload.get("elapsed_sec", 0.0)) if cupy_payload is not None else None
    return {
        "distribution": distribution,
        "status": status,
        "generated": generated,
        "rtdl_ok": rtdl_ok,
        "cupy_grid_ok": cupy_ok if cupy_payload is not None else None,
        "candidate_count_matches_cupy_grid": candidate_count_matches if cupy_payload is not None else None,
        "candidate_count_within_tolerance": candidate_count_within_tolerance if cupy_payload is not None else None,
        "candidate_count_delta": candidate_count_delta,
        "candidate_count_tolerance": candidate_count_tolerance,
        "rtdl_raw_candidate_count": int(rtdl_candidate_count),
        "cupy_grid_bounded_neighbor_count": cupy_bounded_count,
        "rtdl_elapsed_sec": rtdl_elapsed,
        "cupy_grid_elapsed_sec": cupy_elapsed,
        "cupy_grid_over_rtdl_elapsed_ratio": (
            float(cupy_elapsed) / rtdl_elapsed if cupy_elapsed is not None and rtdl_elapsed > 0.0 else None
        ),
        "rtdl_row_count": int(rtdl_payload.get("row_count", 0)),
        "query_count": int(rtdl_payload.get("query_count", 0)),
        "search_count": int(rtdl_payload.get("search_count", 0)),
        "rtdl_prepare_sec": float(rtdl_payload.get("execution_prepare_sec", 0.0)),
        "rtdl_input_pack_sec": float(rtdl_payload.get("input_pack_sec", 0.0)),
        "rtdl_elapsed_runs_sec": tuple(float(value) for value in rtdl_payload.get("elapsed_runs_sec", ())),
        "cupy_grid_elapsed_runs_sec": (
            tuple(float(value) for value in cupy_payload.get("elapsed_runs_sec", ()))
            if cupy_payload is not None
            else None
        ),
        "rtdl_phase_summary": _rtdl_phase_summary(rtdl_payload),
        "cupy_grid_summary": cupy_payload.get("summary") if cupy_payload is not None else None,
        "contract": {
            "family": "fixed_radius_neighbors_3d",
            "mode": "ranked-summary",
            "exact": True,
            "bounded_k": int(rtdl_payload.get("k_max", 0)),
            "same_contract_opponent": "cupy_grid_exact_ranked_summary_3d" if cupy_payload is not None else None,
        },
        "claim_boundary": CLAIM_BOUNDARY,
        "elapsed_sec": float(elapsed_sec),
    }


def _rtdl_raw_candidate_count(payload: dict[str, Any]) -> int:
    return sum(int(item.get("raw_candidate_count", 0)) for item in payload.get("batch_phase_timings", ()))


def _rtdl_phase_summary(payload: dict[str, Any]) -> dict[str, Any]:
    phases = tuple(dict(item) for item in payload.get("batch_phase_timings", ()))
    return {
        "batch_count": len(phases),
        "raw_candidate_count": _rtdl_raw_candidate_count(payload),
        "candidate_count_pass_sec": sum(float(item.get("candidate_count_pass", 0.0)) for item in phases),
        "row_download_sec": sum(float(item.get("row_download", 0.0)) for item in phases),
        "upload_sec": sum(float(item.get("upload", 0.0)) for item in phases),
        "modes": tuple(str(item.get("mode", "")) for item in phases),
    }


def _parse_csv_strings(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal2800 RTNN v2.5 live ranked-summary harness.")
    parser.add_argument("--point-count", type=int, default=32768)
    parser.add_argument("--distributions", default=",".join(DEFAULT_DISTRIBUTIONS))
    parser.add_argument("--radius", type=float, default=0.02)
    parser.add_argument("--k-max", type=int, default=50)
    parser.add_argument("--query-batch-size", type=int)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--skip-cupy-grid", action="store_true")
    parser.add_argument("--fail-fast", action="store_true")
    args = parser.parse_args(argv)

    payload = run_goal2800_rtnn_live_harness(
        point_count=args.point_count,
        distributions=_parse_csv_strings(args.distributions),
        radius=args.radius,
        k_max=args.k_max,
        query_batch_size=args.query_batch_size,
        repeat=args.repeat,
        run_cupy_grid=not args.skip_cupy_grid,
        work_dir=args.work_dir,
        fail_fast=args.fail_fast,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

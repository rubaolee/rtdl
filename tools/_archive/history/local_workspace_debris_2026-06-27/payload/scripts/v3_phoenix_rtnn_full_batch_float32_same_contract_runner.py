#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts import goal2348_rtnn_v2_2_external_runner as rtnn_runner  # noqa: E402
from scripts import v3_optix_hardware_gate  # noqa: E402


DEFAULT_OUT_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_rtnn_full_batch_float32_same_contract_20260621"
)
SERIOUS_POINT_COUNT_FLOOR = 262_144
DEFAULT_SERIOUS_POINT_COUNT = 1_048_576
MATERIAL_SPEEDUP_FLOOR = 2.0
ALLOWED_ROUTES = ("optix", "cupy_grid")
POINT_COLUMN_SOURCE_CHOICES = ("csv", "numpy_csv", "npz")
DEFAULT_POINT_COLUMN_SOURCE = "npz"
RTDL_RESULT_MODE = "ranked-summary-aggregate-prepared-query-batch-float32"


def main() -> int:
    args = parse_args()
    routes = parse_routes(args.routes)
    out_dir = args.output_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    env_payload = environment_payload(require_rt_hardware=args.require_rt_hardware)
    (out_dir / "environment.json").write_text(
        json.dumps(env_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if args.dry_run:
        summary = build_summary(
            args=args,
            route_payloads={},
            environment=env_payload,
            run_errors={},
            point_manifest=point_manifest_for_plan(args, out_dir=out_dir),
            dry_run=True,
        )
        write_summary(out_dir, summary)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    if not args.allow_non_serious_local_smoke and args.point_count < SERIOUS_POINT_COUNT_FLOOR:
        raise SystemExit(
            "point-count is below the Phoenix RTNN serious scale floor; pass "
            "--allow-non-serious-local-smoke only for local smoke tests"
        )

    if "optix" in routes and args.require_rt_hardware and env_payload["hardware_gate"]["status"] != "pass":
        summary = build_summary(
            args=args,
            route_payloads={},
            environment=env_payload,
            run_errors={
                "optix_hardware_gate": env_payload["hardware_gate"]["fail_closed_reason"]
                or "OptiX RT hardware gate failed"
            },
            point_manifest=point_manifest_for_plan(args, out_dir=out_dir),
            dry_run=False,
        )
        write_summary(out_dir, summary)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 2

    point_manifest = ensure_point_file(args, out_dir=out_dir)
    route_payloads: dict[str, dict[str, Any]] = {}
    run_errors: dict[str, str] = {}
    for route in routes:
        try:
            payload = run_route(
                args=args,
                route=route,
                point_file=Path(point_manifest["path"]),
                point_manifest=point_manifest,
            )
            route_payloads[route] = payload
            (out_dir / f"rtnn_full_batch_float32_{route}.json").write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        except Exception as exc:  # pragma: no cover - backend/environment dependent
            run_errors[route] = repr(exc)
            (out_dir / f"rtnn_full_batch_float32_{route}.error.txt").write_text(
                repr(exc) + "\n",
                encoding="utf-8",
            )
            if args.fail_fast:
                break

    summary = build_summary(
        args=args,
        route_payloads=route_payloads,
        environment=env_payload,
        run_errors=run_errors,
        point_manifest=point_manifest,
        dry_run=False,
    )
    write_summary(out_dir, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["runner_completed"] else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run or stage Phoenix V3 RTNN full-batch float32 same-contract evidence. "
            "The runner compares RTDL OptiX full-batch ranked_summary aggregate against "
            "a same-contract CuPy grid reference and never authorizes M7 by itself."
        )
    )
    parser.add_argument("--point-file", type=Path)
    parser.add_argument("--point-count", type=int, default=DEFAULT_SERIOUS_POINT_COUNT)
    parser.add_argument("--distribution", choices=("uniform", "clustered", "shell"), default="uniform")
    parser.add_argument("--seed", type=int, default=4502)
    parser.add_argument("--radius", type=float, default=0.02)
    parser.add_argument("--k-max", type=int, default=50)
    parser.add_argument("--query-batch-size", type=int)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--max-grid-cells", type=int, default=2_000_000)
    parser.add_argument("--routes", default="optix,cupy_grid")
    parser.add_argument(
        "--point-column-source",
        choices=POINT_COLUMN_SOURCE_CHOICES,
        default=DEFAULT_POINT_COLUMN_SOURCE,
        help=(
            "Input column source for serious RTNN reruns. 'npz' is the V3 Phoenix "
            "column-ingestion path; 'csv' preserves the historical list path."
        ),
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--require-rt-hardware", action="store_true")
    parser.add_argument("--allow-non-serious-local-smoke", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--fail-fast", action="store_true")
    return parser.parse_args()


def parse_routes(value: str) -> tuple[str, ...]:
    raw = [part.strip().lower().replace("-", "_") for part in value.split(",") if part.strip()]
    aliases = {
        "rtdl": "optix",
        "cuda_optix": "optix",
        "nvidia_rt": "optix",
        "cupy": "cupy_grid",
        "cuda_core": "cupy_grid",
    }
    normalized = tuple(dict.fromkeys(aliases.get(part, part) for part in raw))
    bad = [part for part in normalized if part not in ALLOWED_ROUTES]
    if bad:
        raise ValueError(f"unsupported RTNN same-contract route(s): {bad}; allowed: {ALLOWED_ROUTES}")
    if not normalized:
        raise ValueError("at least one route is required")
    return normalized


def point_manifest_for_plan(args: argparse.Namespace, *, out_dir: Path) -> dict[str, Any]:
    point_file = args.point_file or (out_dir / "rtnn_full_batch_points.csv")
    point_column_source = str(getattr(args, "point_column_source", DEFAULT_POINT_COLUMN_SOURCE)).replace(
        "-",
        "_",
    )
    return {
        "path": str(point_file),
        "point_count": int(args.point_count),
        "dimension": 3,
        "seed": int(args.seed),
        "distribution": args.distribution,
        "format": "rtnn_csv_xyz",
        "point_column_source": point_column_source,
        "column_source_path": str(point_column_source_path(point_file, point_column_source)),
        "generated_by_runner": args.point_file is None,
        "runtime_materialized": False,
    }


def ensure_point_file(args: argparse.Namespace, *, out_dir: Path) -> dict[str, Any]:
    if args.point_file is not None:
        point_file = args.point_file.resolve()
        if not point_file.exists():
            raise FileNotFoundError(f"RTNN point file does not exist: {point_file}")
        manifest = {
            **point_manifest_for_plan(args, out_dir=out_dir),
            "path": str(point_file),
            "generated_by_runner": False,
            "runtime_materialized": True,
        }
        return ensure_point_column_source(manifest, point_file=point_file, args=args, out_dir=out_dir)

    point_file = out_dir / "rtnn_full_batch_points.csv"
    manifest = rtnn_runner.generate_point_file(
        point_file,
        point_count=int(args.point_count),
        dimension=3,
        seed=int(args.seed),
        distribution=args.distribution,
    )
    manifest["generated_by_runner"] = True
    manifest["runtime_materialized"] = True
    return ensure_point_column_source(manifest, point_file=point_file, args=args, out_dir=out_dir)


def point_column_source_path(point_file: Path, source: str) -> Path:
    normalized = source.replace("-", "_")
    if normalized == "npz":
        return point_file if point_file.suffix == ".npz" else Path(str(point_file) + ".npz")
    return point_file


def ensure_point_column_source(
    manifest: dict[str, Any],
    *,
    point_file: Path,
    args: argparse.Namespace,
    out_dir: Path,
) -> dict[str, Any]:
    source = str(getattr(args, "point_column_source", DEFAULT_POINT_COLUMN_SOURCE)).replace("-", "_")
    if source not in POINT_COLUMN_SOURCE_CHOICES:
        raise ValueError(f"unsupported point-column source: {source}")
    column_source_path = point_column_source_path(point_file, source)
    updated = {
        **manifest,
        "path": str(point_file),
        "point_column_source": source,
        "column_source_path": str(column_source_path),
        "column_source_runtime_materialized": source == "npz",
    }
    if source == "npz" and point_file.suffix != ".npz":
        updated["column_source_manifest"] = write_point_columns_npz(point_file, column_source_path)
    (out_dir / "point_manifest.json").write_text(
        json.dumps(updated, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return updated


def write_point_columns_npz(point_file: Path, column_source_path: Path) -> dict[str, Any]:
    try:
        import numpy as np  # noqa: PLC0415
    except Exception as exc:  # pragma: no cover - optional dependency path
        raise RuntimeError("NumPy is required for Phoenix V3 RTNN npz point-column source") from exc

    values = np.loadtxt(point_file, delimiter=",", dtype=np.float64)
    if values.ndim == 1:
        values = values.reshape(1, -1)
    if values.shape[1] != 3:
        raise ValueError("RTNN point CSV must have x,y,z columns")
    ids = np.arange(values.shape[0], dtype=np.uint32)
    column_source_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        column_source_path,
        ids=ids,
        x=values[:, 0].astype(np.float64, copy=False),
        y=values[:, 1].astype(np.float64, copy=False),
        z=values[:, 2].astype(np.float64, copy=False),
    )
    return {
        "path": str(column_source_path),
        "source_csv": str(point_file),
        "format": "rtnn_npz_xyz_columns_v1",
        "point_count": int(values.shape[0]),
        "ids_dtype": "uint32",
        "coordinate_dtype": "float64",
    }


def run_route(
    *,
    args: argparse.Namespace,
    route: str,
    point_file: Path,
    point_manifest: dict[str, Any],
) -> dict[str, Any]:
    if route == "optix":
        batch_size = int(args.query_batch_size or args.point_count)
        started = time.perf_counter()
        payload = rtnn_runner.run_rtdl_batched_3d_neighbors(
            SimpleNamespace(
                point_file=point_file,
                query_file=None,
                radius=float(args.radius),
                k_max=int(args.k_max),
                backend="optix",
                query_batch_size=batch_size,
                result_mode=RTDL_RESULT_MODE,
                aggregate_request_count=1,
                aggregate_radius_multipliers=None,
                aggregate_k_values=None,
                repeat=int(args.repeat),
                point_column_source=str(args.point_column_source).replace("-", "_"),
                point_column_file=point_manifest.get("column_source_path"),
                row_label="phoenix_v3_rtnn_full_batch_float32_optix",
                json_out=None,
            )
        )
        payload["phoenix_v3_runner_wall_sec"] = time.perf_counter() - started
        return payload
    if route == "cupy_grid":
        started = time.perf_counter()
        payload = rtnn_runner.run_cupy_grid_3d_ranked_summary(
            SimpleNamespace(
                point_file=point_file,
                query_file=None,
                radius=float(args.radius),
                k_max=int(args.k_max),
                dtype="float32",
                max_grid_cells=int(args.max_grid_cells),
                repeat=int(args.repeat),
                point_column_source=str(args.point_column_source).replace("-", "_"),
                point_column_file=point_manifest.get("column_source_path"),
                row_label="phoenix_v3_rtnn_full_batch_float32_cupy_grid_reference",
                json_out=None,
            )
        )
        payload["phoenix_v3_runner_wall_sec"] = time.perf_counter() - started
        return payload
    raise ValueError(f"unsupported route: {route}")


def environment_payload(*, require_rt_hardware: bool) -> dict[str, Any]:
    nvidia_smi = run_command_text(
        [
            "nvidia-smi",
            "--query-gpu=name,driver_version,compute_cap",
            "--format=csv,noheader",
        ]
    )
    git_head = run_command_text(["git", "rev-parse", "HEAD"], cwd=ROOT)
    hardware_gate = v3_optix_hardware_gate.build_payload(
        require_rt_hardware=require_rt_hardware,
        sample_nvidia_smi=None,
    )
    return {
        "tool": "v3_phoenix_rtnn_full_batch_float32_same_contract_environment",
        "python": sys.version,
        "cwd": str(ROOT),
        "git_head": git_head.strip(),
        "nvidia_smi": nvidia_smi.strip(),
        "hardware_gate": hardware_gate,
        "env": {
            "RTDL_OPTIX_LIBRARY": os.environ.get("RTDL_OPTIX_LIBRARY"),
            "PYTHONPATH": os.environ.get("PYTHONPATH"),
        },
    }


def run_command_text(command: list[str], *, cwd: Path | None = None) -> str:
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd) if cwd is not None else None,
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception as exc:  # pragma: no cover - host tool dependent
        return f"ERROR: {exc!r}"
    text = completed.stdout.strip()
    if completed.stderr.strip():
        text = (text + "\n" if text else "") + completed.stderr.strip()
    return text


def build_summary(
    *,
    args: argparse.Namespace,
    route_payloads: dict[str, dict[str, Any]],
    environment: dict[str, Any],
    run_errors: dict[str, str],
    point_manifest: dict[str, Any],
    dry_run: bool = False,
) -> dict[str, Any]:
    routes = parse_routes(args.routes)
    phase_rows = {
        route: phase_summary(route, payload)
        for route, payload in sorted(route_payloads.items())
    }
    comparisons = comparison_summary(phase_rows)
    parity = parity_summary(route_payloads)
    checks = {
        "runner_completed_without_route_errors": not run_errors and not dry_run,
        "serious_fixture_scale": int(args.point_count) >= SERIOUS_POINT_COUNT_FLOOR,
        "rtdl_optix_route_present": "optix" in route_payloads,
        "cupy_grid_reference_route_present": "cupy_grid" in route_payloads,
        "all_routes_ok": all(bool(payload.get("ok", False)) for payload in route_payloads.values())
        and bool(route_payloads),
        "same_contract_signature_match": bool(parity.get("same_contract_signature_match", False)),
        "phase_table_has_load_prepare_query_wall": all(
            row["has_load_prepare_query_wall"] for row in phase_rows.values()
        )
        and bool(phase_rows),
        "point_column_source_recorded": (
            dry_run
            or (
                all(bool(row.get("point_column_source")) for row in phase_rows.values())
                and bool(phase_rows)
            )
        ),
        "optix_rt_hardware_gate_passed_if_required": (
            not bool(getattr(args, "require_rt_hardware", False))
            or environment.get("hardware_gate", {}).get("status") == "pass"
        ),
        "material_rtdl_over_reference_speedup": bool(
            comparisons.get("rtdl_optix_over_cupy_grid_hot_speedup", 0.0) >= MATERIAL_SPEEDUP_FLOOR
        ),
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    pending_review = not failed_checks
    if dry_run:
        status = "rtnn_full_batch_float32_same_contract_runner_plan_not_m7"
    elif pending_review:
        status = "rtnn_full_batch_float32_same_contract_pod_evidence_pending_2ai_not_m7"
    elif route_payloads and not run_errors:
        status = "rtnn_full_batch_float32_same_contract_evidence_collected_not_m7"
    else:
        status = "rtnn_full_batch_float32_same_contract_evidence_incomplete_not_m7"

    return {
        "tool": "v3_phoenix_rtnn_full_batch_float32_same_contract_runner",
        "status": status,
        "runner_completed": bool(route_payloads) and not run_errors and not dry_run,
        "generic_capability": "ranked_summary",
        "candidate_scope": (
            "generic fixed_radius_neighbors_3d ranked_summary full-batch float32 aggregate; "
            "RTNN is only the evidence harness"
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_reopen_candidate_pending_2ai_review": pending_review,
        "material_speedup_floor": MATERIAL_SPEEDUP_FLOOR,
        "serious_point_count_floor": SERIOUS_POINT_COUNT_FLOOR,
        "parameters": {
            "point_count": int(args.point_count),
            "distribution": args.distribution,
            "seed": int(args.seed),
            "radius": float(args.radius),
            "k_max": int(args.k_max),
            "query_batch_size": int(args.query_batch_size or args.point_count),
            "repeat": int(args.repeat),
            "routes": list(routes),
            "result_mode": RTDL_RESULT_MODE,
            "point_column_source": str(
                getattr(args, "point_column_source", DEFAULT_POINT_COLUMN_SOURCE)
            ).replace("-", "_"),
            "dry_run": bool(dry_run),
        },
        "point_manifest": point_manifest,
        "environment": environment,
        "phase_rows": phase_rows,
        "comparisons": comparisons,
        "parity": parity,
        "checks": checks,
        "failed_checks": failed_checks,
        "run_errors": run_errors,
        "required_future_review": [
            "Save the full route payloads, environment, and point manifest from a real RTX run.",
            "Verify same-contract summary parity against the CuPy grid reference.",
            "Report load, pack/grid prepare, execution prepare, query wall, and cold-plus-query wall.",
            "Send the packet to Claude or Gemini and record Codex consensus before any M7 promotion.",
        ],
        "forbidden_public_wording": [
            "RTNN is solved",
            "V3 proves universal nearest-neighbor acceleration",
            "M106 787x is a public RTNN row",
            "float32 same-contract runner is M7 without 2-AI review",
            "RTDL beats the RTNN paper implementation for the whole app",
        ],
        "goal_level_decision_audit": {
            "decision": (
                "Stage RTNN full-batch float32 same-contract evidence through a reusable "
                "runner instead of promoting M106 directly."
            ),
            "was_i_foolish": "No. This follows the M112-approved rerun path and keeps all release flags false.",
            "foolish_actions": (
                "It would be foolish to quote the M106 787.53x-vs-Embree or 2.26x-vs-author "
                "figures as a public RTNN win without same-contract reference parity."
            ),
            "other_path": (
                "Repair the exact float64 tie policy first. That remains valid, but it is a "
                "semantic review path rather than the fastest route to fresh full-batch evidence."
            ),
            "different_path_now": (
                "Run this checked-in runner on an RTX pod with OptiX plus CuPy grid reference, "
                "then seek 2-AI review before reopening any RTNN M7 row."
            ),
        },
    }


def phase_summary(route: str, payload: dict[str, Any]) -> dict[str, Any]:
    if route == "optix":
        elapsed_samples = [float(value) for value in payload.get("elapsed_runs_sec", ())]
        query_sec = float(payload.get("elapsed_median_sec", 0.0))
        load_sec = float(payload.get("input_load_sec", 0.0))
        pack_sec = float(payload.get("input_pack_sec", 0.0))
        prepare_sec = float(payload.get("execution_prepare_sec", 0.0))
        return {
            "route": route,
            "mode": payload.get("result_mode"),
            "ok": bool(payload.get("ok")),
            "query_count": int(payload.get("query_count", 0)),
            "search_count": int(payload.get("search_count", 0)),
            "query_batch_size": int(payload.get("query_batch_size", 0)),
            "batch_count": int(payload.get("batch_count", 0)),
            "input_load_sec": load_sec,
            "input_pack_sec": pack_sec,
            "execution_prepare_sec": prepare_sec,
            "hot_query_median_sec": query_sec,
            "cold_plus_query_wall_sec": load_sec + pack_sec + prepare_sec + query_sec,
            "runner_wall_sec": float(payload.get("phoenix_v3_runner_wall_sec", 0.0)),
            "point_column_source": payload.get("point_column_source"),
            "point_column_file": payload.get("point_column_file"),
            "elapsed_samples_sec": elapsed_samples,
            "summary": payload.get("ranked_aggregate_summary"),
            "contract": payload.get("contract"),
            "has_load_prepare_query_wall": load_sec >= 0.0 and pack_sec >= 0.0 and prepare_sec >= 0.0 and query_sec > 0.0,
        }
    if route == "cupy_grid":
        elapsed_samples = [float(value) for value in payload.get("elapsed_runs_sec", ())]
        query_sec = statistics.median(elapsed_samples) if elapsed_samples else float(payload.get("elapsed_sec", 0.0))
        load_sec = float(payload.get("input_load_sec", 0.0))
        prepare_sec = float(payload.get("grid_prepare_sec", 0.0))
        return {
            "route": route,
            "mode": payload.get("mode"),
            "ok": bool(payload.get("ok")),
            "query_count": int(payload.get("query_count", 0)),
            "search_count": int(payload.get("search_count", 0)),
            "input_load_sec": load_sec,
            "grid_prepare_sec": prepare_sec,
            "hot_query_median_sec": query_sec,
            "cold_plus_query_wall_sec": load_sec + prepare_sec + query_sec,
            "runner_wall_sec": float(payload.get("phoenix_v3_runner_wall_sec", 0.0)),
            "point_column_source": payload.get("point_column_source"),
            "point_column_file": payload.get("point_column_file"),
            "elapsed_samples_sec": elapsed_samples,
            "summary": payload.get("summary"),
            "contract": payload.get("contract"),
            "grid_cell_count": int(payload.get("grid_cell_count", 0)),
            "occupied_cell_count": int(payload.get("occupied_cell_count", 0)),
            "has_load_prepare_query_wall": load_sec >= 0.0 and prepare_sec >= 0.0 and query_sec > 0.0,
        }
    raise ValueError(f"unsupported route payload: {route}")


def comparison_summary(phase_rows: dict[str, dict[str, Any]]) -> dict[str, float]:
    if not {"optix", "cupy_grid"}.issubset(phase_rows):
        return {}
    optix = phase_rows["optix"]
    cupy_grid = phase_rows["cupy_grid"]
    return {
        "rtdl_optix_over_cupy_grid_hot_speedup": speedup(
            cupy_grid["hot_query_median_sec"],
            optix["hot_query_median_sec"],
        ),
        "rtdl_optix_over_cupy_grid_cold_plus_query_speedup": speedup(
            cupy_grid["cold_plus_query_wall_sec"],
            optix["cold_plus_query_wall_sec"],
        ),
        "rtdl_optix_over_cupy_grid_runner_wall_speedup": speedup(
            cupy_grid["runner_wall_sec"],
            optix["runner_wall_sec"],
        ),
    }


def parity_summary(route_payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if not {"optix", "cupy_grid"}.issubset(route_payloads):
        return {
            "same_contract_signature_match": False,
            "reason": "optix and cupy_grid payloads are both required",
        }
    optix_summary = route_payloads["optix"].get("ranked_aggregate_summary") or {}
    reference_summary = route_payloads["cupy_grid"].get("summary") or {}
    delta = signature_delta(optix_summary, reference_summary)
    sum_distance_ref = abs(float(reference_summary.get("sum_distance", 0.0)))
    sum_distance_abs = abs(float(delta["sum_distance"]))
    sum_distance_rel = sum_distance_abs / max(1.0, sum_distance_ref)
    integer_match = all(
        int(delta[key]) == 0
        for key in ("row_count", "bounded_neighbor_count", "nearest_id_checksum", "kth_id_checksum")
    )
    return {
        "same_contract_signature_match": integer_match and sum_distance_rel <= 1e-4,
        "integer_signature_match": integer_match,
        "sum_distance_abs_error": sum_distance_abs,
        "sum_distance_relative_error": sum_distance_rel,
        "sum_distance_relative_tolerance": 1e-4,
        "delta_optix_minus_cupy_grid": delta,
        "optix_summary": optix_summary,
        "cupy_grid_reference_summary": reference_summary,
    }


def signature_delta(candidate: dict[str, Any], reference: dict[str, Any]) -> dict[str, Any]:
    keys = ("row_count", "bounded_neighbor_count", "nearest_id_checksum", "kth_id_checksum")
    delta: dict[str, Any] = {
        key: int(candidate.get(key, 0)) - int(reference.get(key, 0))
        for key in keys
    }
    delta["sum_distance"] = float(candidate.get("sum_distance", 0.0)) - float(
        reference.get("sum_distance", 0.0)
    )
    return delta


def speedup(baseline_sec: float, candidate_sec: float) -> float:
    if baseline_sec <= 0.0 or candidate_sec <= 0.0:
        return 0.0
    return float(baseline_sec) / float(candidate_sec)


def write_summary(out_dir: Path, summary: dict[str, Any]) -> None:
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "README.md").write_text(render_markdown(summary), encoding="utf-8")


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Phoenix V3 RTNN Full-Batch Float32 Same-Contract Evidence",
        "",
        f"Status: `{summary['status']}`.",
        "",
        "This is a generic `ranked_summary` evidence packet. RTNN is only the",
        "harness for fixed-radius 3-D ranked-summary aggregate work.",
        "",
        "```text",
        f"release_authorized: {str(summary['release_authorized']).lower()}",
        f"public_speedup_claim_authorized: {str(summary['public_speedup_claim_authorized']).lower()}",
        f"m7_promotion_authorized: {str(summary['m7_promotion_authorized']).lower()}",
        "```",
        "",
        "## Parameters",
        "",
    ]
    for key, value in summary["parameters"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## Phase Rows", ""])
    for route, row in summary["phase_rows"].items():
        lines.extend(
            [
                f"### {route}",
                "",
                f"- Hot query median: `{row['hot_query_median_sec']:.9f}` sec",
                f"- Cold-plus-query wall: `{row['cold_plus_query_wall_sec']:.9f}` sec",
                f"- Runner wall: `{row['runner_wall_sec']:.9f}` sec",
                "",
            ]
        )
    if summary["comparisons"]:
        lines.extend(["## Comparisons", ""])
        for key, value in summary["comparisons"].items():
            lines.append(f"- `{key}`: `{value:.6f}`")
        lines.append("")

    lines.extend(
        [
            "## Parity",
            "",
            f"- Same-contract signature match: `{summary['parity'].get('same_contract_signature_match')}`",
            f"- Integer signature match: `{summary['parity'].get('integer_signature_match')}`",
            f"- Sum-distance relative error: `{summary['parity'].get('sum_distance_relative_error')}`",
            "",
            "## Checks",
            "",
        ]
    )
    for key, value in summary["checks"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(
        [
            "",
            "## Forbidden Public Wording",
            "",
            *[f"- {item}" for item in summary["forbidden_public_wording"]],
            "",
            "## Goal-Level Decision Audit",
            "",
        ]
    )
    audit = summary["goal_level_decision_audit"]
    lines.extend(
        [
            f"Decision: {audit['decision']}",
            "",
            f"1. Was I foolish? {audit['was_i_foolish']}",
            f"2. If yes, what actions made the decision foolish? {audit['foolish_actions']}",
            f"3. Was there another path that would have avoided getting stuck on that idea? {audit['other_path']}",
            f"4. Can I now try a different path that actually solves the problem? {audit['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())

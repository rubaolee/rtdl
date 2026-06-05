from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
DEFAULT_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3532_rayjoin_promoted_contract_packet"


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _claim_boundary() -> dict[str, bool]:
    return {
        "internal_investigation_only": True,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "rayjoin_paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "full_overlay_area_claim_authorized": False,
        "app_specific_native_engine_shortcut_authorized": False,
    }


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


def _get_path(payload: dict[str, Any], path: tuple[str, ...]) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def _first_number(payload: dict[str, Any], paths: tuple[tuple[str, ...], ...]) -> tuple[float | None, str | None]:
    for path in paths:
        value = _get_path(payload, path)
        if isinstance(value, (int, float)):
            return float(value), ".".join(path)
    return None, None


def _json_from_stdout(stdout: str) -> dict[str, Any]:
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        pass
    start = stdout.find("{")
    end = stdout.rfind("}")
    if start >= 0 and end > start:
        return json.loads(stdout[start : end + 1])
    raise


def _run_json_command(
    *,
    label: str,
    command: list[str],
    cwd: Path,
    output_path: Path | None = None,
    timeout_sec: int,
) -> dict[str, Any]:
    print(f"[goal3532] start {label}: {' '.join(command)}", flush=True)
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=int(timeout_sec),
    )
    elapsed = time.perf_counter() - started
    result = {
        "label": label,
        "command": command,
        "returncode": completed.returncode,
        "elapsed_sec": elapsed,
        "stdout_tail": completed.stdout[-2000:],
        "stderr_tail": completed.stderr[-2000:],
        "output_path": str(output_path) if output_path is not None else None,
    }
    if completed.returncode != 0:
        raise RuntimeError(json.dumps(result, indent=2, sort_keys=True))
    if output_path is not None:
        payload = json.loads(output_path.read_text(encoding="utf-8"))
    else:
        payload = _json_from_stdout(completed.stdout)
    print(f"[goal3532] done {label}: elapsed={elapsed:.6f}s", flush=True)
    return {"run": result, "payload": payload}


def _python(args: argparse.Namespace, *parts: object) -> list[str]:
    return [str(args.python), *(str(part) for part in parts)]


def _dataset_arg(args: argparse.Namespace) -> str:
    return f"{args.left_cdb} + {args.right_cdb}"


def _count_parity_specs(args: argparse.Namespace) -> tuple[dict[str, Any], ...]:
    app = "examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py"
    return (
        {
            "row_id": "rayjoin_count_parity_pip_prepared_optix",
            "contract": "point_closed_shape_membership_count",
            "command": _python(
                args,
                app,
                "--workload",
                "pip",
                "--execution-route",
                "prepared_optix",
                "--result-mode",
                "count",
                "--dataset",
                _dataset_arg(args),
                "--no-rows",
            ),
            "metric_paths": (("phases_sec", "prepared_query_sec"), ("prepared_query_total_sec",)),
        },
        {
            "row_id": "rayjoin_count_parity_lsi_left_id_dense_count",
            "contract": "segment_pair_intersection_count_by_left_id",
            "command": _python(
                args,
                app,
                "--workload",
                "lsi",
                "--execution-route",
                "prepared_optix_left_id_dense_count",
                "--dataset",
                _dataset_arg(args),
                "--no-rows",
            ),
            "metric_paths": (
                ("phases_sec", "left_id_count_device_columns_sec"),
                ("phases_sec", "dense_count_sec"),
                ("phases_sec", "grouped_count_sec"),
                ("elapsed_sec",),
            ),
        },
        {
            "row_id": "rayjoin_count_parity_overlay_seed_active_count",
            "contract": "shape_pair_active_dependency_count",
            "command": _python(
                args,
                app,
                "--workload",
                "overlay_seed",
                "--execution-route",
                "prepared_optix_shape_pair_active_count",
                "--dataset",
                _dataset_arg(args),
                "--no-rows",
            ),
            "metric_paths": (
                ("phases_sec", "active_count_device_continuation_sec"),
                ("phases_sec", "active_count_sec"),
                ("elapsed_sec",),
            ),
        },
    )


_RELATION_ROW_SPECS = (
    ("rayjoin_relation_columns_cdb_pair", "shape_pair_relation_device_columns", ("relation_columns_sec", "median")),
    ("rayjoin_relation_grouped_count_cdb_pair", "shape_pair_relation_grouped_count_by_left", ("grouped_count_sec", "median")),
    ("rayjoin_shape_pair_payload_bounds_cdb_pair", "shape_pair_relation_bounds_overlap_area_payload", ("bounds_overlap_area_sec", "median")),
    ("rayjoin_shape_pair_payload_witness_cdb_pair", "shape_pair_relation_witness_payload", ("witness_continuation_sec", "median")),
)


_OVERLAY_ROW_SPECS = (
    (
        "rayjoin_overlay_area_relation_stream_cdb_pair",
        "shape_pair_relation_stream_steady_state",
        ("timing_sec", "active_relation_device_columns"),
    ),
    (
        "rayjoin_overlay_area_device_tile_planner_cdb_pair",
        "prepared_overlay_area_device_tile_task_planner",
        ("timing_sec", "device_tile_task_planning_best_repeat"),
    ),
    (
        "rayjoin_overlay_area_tile_executor_cdb_pair",
        "prepared_overlay_area_tile_task_executor",
        ("timing_sec", "cupy_tile_task_executor_best_repeat"),
    ),
)


def _dry_run_rows(args: argparse.Namespace) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in _count_parity_specs(args):
        rows.append(
            {
                "row_id": spec["row_id"],
                "contract": spec["contract"],
                "status": "planned_live_command",
                "command": spec["command"],
                "primary_metric_sec": None,
                "claim_boundary": _claim_boundary(),
            }
        )
    relation_command = _goal3465_command(args, Path("relation_continuation.json"))
    for row_id, contract, metric_path in _RELATION_ROW_SPECS:
        rows.append(
            {
                "row_id": row_id,
                "contract": contract,
                "status": "planned_goal3465_live_command",
                "command": relation_command,
                "primary_metric_sec": None,
                "primary_metric_source": ".".join(metric_path),
                "claim_boundary": _claim_boundary(),
            }
        )
    overlay_command = _goal3492_command(args, Path("overlay_area_tile_tasks.json"))
    for row_id, contract, metric_path in _OVERLAY_ROW_SPECS:
        rows.append(
            {
                "row_id": row_id,
                "contract": contract,
                "status": "planned_goal3492_live_command",
                "command": overlay_command,
                "primary_metric_sec": None,
                "primary_metric_source": ".".join(metric_path),
                "claim_boundary": _claim_boundary(),
            }
        )
    return rows


def _goal3465_command(args: argparse.Namespace, output: Path) -> list[str]:
    return _python(
        args,
        "scripts/goal3465_rayjoin_relation_continuation_packet.py",
        "--left-cdb",
        args.left_cdb,
        "--right-cdb",
        args.right_cdb,
        "--iterations",
        args.iterations,
        "--max-rows",
        args.max_rows,
        "--output",
        output,
    )


def _goal3492_command(args: argparse.Namespace, output: Path) -> list[str]:
    command = _python(
        args,
        "scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py",
        "--left-cdb",
        args.left_cdb,
        "--right-cdb",
        args.right_cdb,
        "--max-rows",
        args.max_rows,
        "--max-triangle-pairs-per-task",
        args.max_triangle_pairs_per_task,
        "--progress-every",
        args.progress_every,
        "--active-shapes-only",
        "--device-active-shape-ordinals",
        "--bounds-positive-filter",
        "--component-bounds-filter",
        "--device-tile-task-planner",
        "--resident-cupy-inputs",
        "--relation-column-warmup-repeats",
        args.relation_column_warmup_repeats,
        "--executor-repeats",
        args.overlay_executor_repeats,
        "--device-planner-repeats",
        args.overlay_device_planner_repeats,
        "--payload-workers",
        args.payload_workers,
        "--relation-stream-steady-state-evidence",
        "--output",
        output,
    )
    return command


def _normalize_count_row(spec: dict[str, Any], run: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    primary, metric_source = _first_number(payload, spec["metric_paths"])
    return {
        "row_id": spec["row_id"],
        "contract": spec["contract"],
        "contract_class": "same_contract_or_evolved_count_parity",
        "backend": "optix",
        "partner": "none",
        "status": "ok",
        "primary_metric_sec": primary,
        "primary_metric_source": metric_source,
        "run_elapsed_sec": run["elapsed_sec"],
        "summary": payload.get("summary", {}),
        "source_artifact": None,
        "command": run["command"],
        "claim_boundary": _claim_boundary(),
    }


def _normalize_relation_rows(path: Path, run: dict[str, Any], payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row_id, contract, metric_path in _RELATION_ROW_SPECS:
        primary, metric_source = _first_number(payload, (metric_path,))
        rows.append(
            {
                "row_id": row_id,
                "contract": contract,
                "contract_class": "promoted_relation_or_payload_continuation",
                "backend": "optix",
                "partner": "cupy",
                "status": "ok",
                "primary_metric_sec": primary,
                "primary_metric_source": metric_source,
                "measurement_metadata": {
                    "iterations": payload.get("iterations"),
                    "max_rows": payload.get("max_rows"),
                    "statistic": "median",
                },
                "run_elapsed_sec": run["elapsed_sec"],
                "row_count": payload.get("row_counts", [None])[0] if payload.get("row_counts") else None,
                "correctness": {
                    "all_row_counts_stable": payload.get("all_row_counts_stable"),
                    "all_grouped_sums_match_rows": payload.get("all_grouped_sums_match_rows"),
                    "all_witnesses_resolved": payload.get("all_witnesses_resolved"),
                },
                "source_artifact": str(path),
                "command": run["command"],
                "claim_boundary": _claim_boundary(),
            }
        )
    return rows


def _normalize_overlay_rows(path: Path, run: dict[str, Any], payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row_id, contract, metric_path in _OVERLAY_ROW_SPECS:
        primary, metric_source = _first_number(payload, (metric_path,))
        rows.append(
            {
                "row_id": row_id,
                "contract": contract,
                "contract_class": "promoted_overlay_area_continuation",
                "backend": "optix",
                "partner": "cupy",
                "status": "ok",
                "primary_metric_sec": primary,
                "primary_metric_source": metric_source,
                "measurement_metadata": {
                    "executor_repeats": payload.get("executor_repeats"),
                    "device_planner_repeats": payload.get("device_planner_repeats"),
                    "relation_column_warmup_repeats": len(
                        payload.get("timing_sec", {}).get("active_relation_device_columns_warmup_secs", [])
                    ),
                    "max_rows": payload.get("max_rows"),
                    "max_triangle_pairs_per_task": payload.get("max_triangle_pairs_per_task"),
                },
                "run_elapsed_sec": run["elapsed_sec"],
                "relation_row_count": payload.get("relation_row_count"),
                "candidate_relation_row_count": payload.get("candidate_relation_row_count"),
                "supported_relation_row_count": payload.get("supported_relation_row_count"),
                "correctness": {
                    "total_area_abs_error": payload.get("total_area_abs_error"),
                    "positive_row_count_match": payload.get("positive_row_count_match"),
                    "max_relation_abs_error": payload.get("max_relation_abs_error"),
                },
                "source_artifact": str(path),
                "command": run["command"],
                "claim_boundary": _claim_boundary(),
            }
        )
    return rows


def run_packet(args: argparse.Namespace) -> dict[str, Any]:
    artifact_dir = Path(args.artifact_dir)
    rows: list[dict[str, Any]] = []
    child_artifacts: list[str] = []
    if args.dry_run:
        rows = _dry_run_rows(args)
    else:
        artifact_dir.mkdir(parents=True, exist_ok=True)
        for spec in _count_parity_specs(args):
            result = _run_json_command(
                label=spec["row_id"],
                command=spec["command"],
                cwd=ROOT,
                timeout_sec=int(args.timeout_sec),
            )
            rows.append(_normalize_count_row(spec, result["run"], result["payload"]))

        relation_output = artifact_dir / "relation_continuation.json"
        relation_result = _run_json_command(
            label="rayjoin_relation_continuation",
            command=_goal3465_command(args, relation_output),
            cwd=ROOT,
            output_path=relation_output,
            timeout_sec=int(args.timeout_sec),
        )
        child_artifacts.append(str(relation_output))
        rows.extend(_normalize_relation_rows(relation_output, relation_result["run"], relation_result["payload"]))

        overlay_output = artifact_dir / "overlay_area_tile_tasks.json"
        overlay_result = _run_json_command(
            label="rayjoin_overlay_area_tile_tasks",
            command=_goal3492_command(args, overlay_output),
            cwd=ROOT,
            output_path=overlay_output,
            timeout_sec=int(args.overlay_timeout_sec),
        )
        child_artifacts.append(str(overlay_output))
        rows.extend(_normalize_overlay_rows(overlay_output, overlay_result["run"], overlay_result["payload"]))

    return {
        "schema": "rtdl.goal3532.rayjoin_promoted_contract_packet.v1",
        "goal": 3532,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "git_status_short": _command_output(["git", "status", "--short"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"]),
        "dry_run": bool(args.dry_run),
        "left_cdb": str(args.left_cdb),
        "right_cdb": str(args.right_cdb),
        "artifact_dir": str(artifact_dir),
        "child_artifacts": child_artifacts,
        "rows": rows,
        "row_count": len(rows),
        "claim_boundary": _claim_boundary(),
        "interpretation": (
            "Normalizes RayJoin promoted v2.8 contracts into separate rows. "
            "It does not compare against v2.3 and does not authorize public performance wording."
        ),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3532 RayJoin promoted-contract packet runner.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--left-cdb", type=Path, default=ROOT / "tests" / "fixtures" / "rayjoin" / "br_county_subset.cdb")
    parser.add_argument(
        "--right-cdb",
        type=Path,
        default=ROOT / "tests" / "fixtures" / "rayjoin" / "br_soil_subset.cdb",
    )
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--max-rows", type=int, default=65536)
    parser.add_argument("--progress-every", type=int, default=1000)
    parser.add_argument("--max-triangle-pairs-per-task", type=int, default=512)
    parser.add_argument("--relation-column-warmup-repeats", type=int, default=2)
    parser.add_argument("--overlay-executor-repeats", type=int, default=3)
    parser.add_argument("--overlay-device-planner-repeats", type=int, default=3)
    parser.add_argument("--payload-workers", type=int, default=4)
    parser.add_argument("--timeout-sec", type=int, default=300)
    parser.add_argument("--overlay-timeout-sec", type=int, default=1200)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = run_packet(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(_json_ready(payload), indent=2, sort_keys=True), flush=True)
    if not args.dry_run:
        missing = [row["row_id"] for row in payload["rows"] if row.get("primary_metric_sec") is None]
        if missing:
            raise SystemExit(f"missing primary metrics for rows: {missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

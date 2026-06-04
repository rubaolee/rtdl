from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.spatial_rayjoin import rtdl_rayjoin_v2_spatial_join_app as rayjoin
from scripts.goal2159_rayjoin_public_cdb_runner import CASES
from scripts.goal2159_rayjoin_public_cdb_runner import DEFAULT_DATA_DIR
from scripts.goal2159_rayjoin_public_cdb_runner import _materialize_slices
from scripts.goal2159_rayjoin_public_cdb_runner import _maybe_download_samples
from scripts.goal2159_rayjoin_public_cdb_runner import _resolve_dataset_template


DEFAULT_CASES = (
    "pip_county512",
    "overlay_county128_soil128",
    "overlay_county256_soil256",
)

CANONICAL_CLAIM_BOUNDARY = {
    "public_speedup_claim_authorized": False,
    "rt_core_speedup_claim_authorized": False,
    "true_zero_copy_claim_authorized": False,
    "rayjoin_paper_reproduction_claim_authorized": False,
    "rtdl_beats_rayjoin_claim_authorized": False,
    "release_authorized": False,
}


def _command_text(command: list[str]) -> str | None:
    try:
        return subprocess.check_output(command, stderr=subprocess.STDOUT, text=True).strip()
    except Exception:
        return None


def _first_command_text(commands: tuple[list[str], ...]) -> str | None:
    for command in commands:
        value = _command_text(command)
        if value:
            return value
    return None


def _commit() -> str:
    return _command_text(["git", "rev-parse", "HEAD"]) or "unknown"


def _hardware_metadata() -> dict[str, object]:
    return {
        "nvidia_smi": _first_command_text(
            (
                ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
                ["/usr/bin/nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            )
        ),
        "cuda_driver_query": _first_command_text(
            (
                ["nvidia-smi", "--query", "--display=COMPUTE"],
                ["/usr/bin/nvidia-smi", "--query", "--display=COMPUTE"],
            )
        ),
        "nvcc_version": _first_command_text(
            (
                ["nvcc", "--version"],
                ["/usr/local/cuda/bin/nvcc", "--version"],
            )
        ),
        "rtdl_optix_library": os.environ.get("RTDL_OPTIX_LIBRARY") or os.environ.get("RTDL_OPTIX_LIB"),
    }


def _median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def _row_set(workload: str, rows: tuple[dict[str, object], ...], *, source: str) -> set[tuple[int, ...]]:
    if workload == "pip":
        shape_key = "shape_id" if source == "prepared_optix" else "polygon_id"
        if source == "prepared_optix":
            bad_memberships = [
                int(row.get("membership", 0))
                for row in rows
                if int(row.get("membership", 0)) != 1
            ]
            if bad_memberships:
                raise ValueError(f"prepared PIP rows must be positive-only; found memberships {bad_memberships[:5]}")
        return {
            (int(row["point_id"]), int(row[shape_key]))
            for row in rows
        }
    if workload == "overlay_seed":
        return {
            (
                int(row["left_polygon_id"]),
                int(row["right_polygon_id"]),
                int(row["requires_lsi"]),
                int(row["requires_pip"]),
            )
            for row in rows
        }
    raise ValueError(f"unsupported workload for row continuation probe: {workload}")


def _active_overlay_rows(rows: tuple[dict[str, object], ...]) -> int | None:
    if not rows:
        return None
    if "requires_lsi" not in rows[0] or "requires_pip" not in rows[0]:
        return None
    return sum(
        1
        for row in rows
        if int(row["requires_lsi"]) == 1 or int(row["requires_pip"]) == 1
    )


def _compact_cpu_summary(workload: str, summary: dict[str, object]) -> dict[str, object]:
    compact = dict(summary)
    if workload == "pip" and "positive_assignments" in compact:
        compact["positive_assignments_count"] = len(tuple(compact["positive_assignments"]))  # type: ignore[arg-type]
        del compact["positive_assignments"]
    if workload == "overlay_seed" and "active_seed_pairs" in compact:
        compact["active_seed_pairs_count"] = len(tuple(compact["active_seed_pairs"]))  # type: ignore[arg-type]
        del compact["active_seed_pairs"]
    return compact


def _run_case(case_name: str, *, workload: str, dataset: str, repeats: int) -> dict[str, object]:
    cpu_start = time.perf_counter()
    cpu_payload = rayjoin.run_rayjoin_workload(
        workload,
        backend="cpu_python_reference",
        dataset=dataset,
        include_rows=True,
    )
    cpu_seconds = time.perf_counter() - cpu_start
    cpu_rows = tuple(cpu_payload["rows"])
    cpu_set = _row_set(workload, cpu_rows, source="cpu_python_reference")

    measurements: list[dict[str, Any]] = []
    for index in range(repeats):
        native_start = time.perf_counter()
        native_payload = rayjoin.run_rayjoin_prepared_optix_workload(
            workload,
            dataset=dataset,
            result_mode="rows",
            include_rows=True,
        )
        native_seconds = time.perf_counter() - native_start
        native_rows = tuple(native_payload["rows"])
        native_set = _row_set(workload, native_rows, source="prepared_optix")
        native_minus_cpu = sorted(native_set - cpu_set)
        cpu_minus_native = sorted(cpu_set - native_set)
        symdiff_count = len(native_minus_cpu) + len(cpu_minus_native)
        named_phase_total = sum(float(value) for value in native_payload.get("phases_sec", {}).values())
        measurements.append(
            {
                "repeat_index": index + 1,
                "prepared_total_seconds": native_seconds,
                "prepared_query_sec": native_payload["phases_sec"].get("prepared_query_sec"),
                "named_phase_total_sec": named_phase_total,
                "unattributed_prepared_total_minus_named_phases_sec": native_seconds - named_phase_total,
                "row_count": int(native_payload["row_count"]),
                "row_set_matches_cpu": symdiff_count == 0,
                "symmetric_difference_count": symdiff_count,
                "native_minus_cpu_sample": native_minus_cpu[:5],
                "cpu_minus_native_sample": cpu_minus_native[:5],
                "summary": native_payload.get("summary", {}),
                "phases_sec": native_payload.get("phases_sec", {}),
                "claim_boundary": dict(CANONICAL_CLAIM_BOUNDARY),
            }
        )
        print(
            f"[goal3232] repeat {case_name}/prepared_rows {index + 1}/{repeats} "
            f"sec={native_seconds:.6f} rows={native_payload['row_count']} symdiff={symdiff_count}",
            flush=True,
        )

    seconds = [float(row["prepared_total_seconds"]) for row in measurements]
    return {
        "case": case_name,
        "workload": workload,
        "dataset": dataset,
        "dataset_note": rayjoin._load_rayjoin_case(workload, dataset).note,
        "cpu_reference_seconds": cpu_seconds,
        "cpu_row_count": len(cpu_rows),
        "cpu_summary": _compact_cpu_summary(workload, dict(cpu_payload.get("summary", {}))),
        "cpu_active_overlay_rows": _active_overlay_rows(cpu_rows),
        "measurements": {
            "include_rows_measured": True,
            "prepared_optix_rows": measurements,
        },
        "medians": {
            "prepared_total_seconds": _median(seconds),
        },
        "all_repeats_match_cpu_rows": bool(measurements)
        and all(row["row_set_matches_cpu"] for row in measurements),
        "claim_boundary": dict(CANONICAL_CLAIM_BOUNDARY),
    }


def build_artifact(args: argparse.Namespace) -> dict[str, object]:
    selected = tuple(CASES[name] for name in args.cases.split(",") if name)
    for case in selected:
        if case.workload not in {"pip", "overlay_seed"}:
            raise ValueError("goal3232 row-continuation probe supports only PIP and overlay_seed cases")
    data_dir = Path(args.data_dir)
    _maybe_download_samples(data_dir, download=args.download)
    slices = _materialize_slices(data_dir, selected)
    rows = []
    for case in selected:
        dataset = _resolve_dataset_template(case.dataset, slices)
        rows.append(_run_case(case.label, workload=case.workload, dataset=dataset, repeats=args.repeats))
    return {
        "goal": args.artifact_goal,
        "schema": args.schema,
        "commit": _commit(),
        "hardware": _hardware_metadata(),
        "data_dir": str(data_dir),
        "slices": slices,
        "repeats": args.repeats,
        "rows": rows,
        "status": "pass" if rows and all(row["all_repeats_match_cpu_rows"] for row in rows) else "fail",
        "claim_boundary": dict(CANONICAL_CLAIM_BOUNDARY),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe public RayJoin PIP/overlay row continuation with prepared OptiX.")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--output", required=True)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--cases", default=",".join(DEFAULT_CASES))
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--artifact-goal", type=int, default=3232)
    parser.add_argument("--schema", default="rtdl.goal3232.rayjoin_public_row_continuation_probe.v1")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    artifact = build_artifact(args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(rayjoin._json_ready(artifact), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[goal3232] wrote {output}", flush=True)
    if artifact["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

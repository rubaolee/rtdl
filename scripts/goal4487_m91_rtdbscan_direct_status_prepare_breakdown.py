from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import time

from examples.current.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    run_rt_dbscan_benchmark,
)


POINT_COUNT = 1_048_576
OUT_JSON = Path("docs/reports/goal4487_v3_0_m91_rtdbscan_direct_status_prepare_breakdown_2026-06-17.json")
OUT_JSONL = Path("docs/reports/goal4487_v3_0_m91_rtdbscan_direct_status_prepare_breakdown_2026-06-17.jsonl")
DIAGNOSTIC_ENV_VAR = "RTDL_DIRECT_STATUS_PREPARE_DIAGNOSTICS"


def _gpu_info() -> str:
    try:
        return subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total,pci.bus_id",
                "--format=csv,noheader",
            ],
            text=True,
        ).strip()
    except Exception as exc:  # pragma: no cover - pod evidence helper
        return f"unavailable: {exc}"


def _cases() -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    for dataset in ("clustered3d", "road3d", "ngsim_dense"):
        cases.append({"dataset": dataset, "diagnostics": False})
        cases.append({"dataset": dataset, "diagnostics": True})
    return cases


def _set_diagnostics(enabled: bool) -> str | None:
    previous = os.environ.get(DIAGNOSTIC_ENV_VAR)
    if enabled:
        os.environ[DIAGNOSTIC_ENV_VAR] = "1"
    else:
        os.environ.pop(DIAGNOSTIC_ENV_VAR, None)
    return previous


def _restore_diagnostics(previous: str | None) -> None:
    if previous is None:
        os.environ.pop(DIAGNOSTIC_ENV_VAR, None)
    else:
        os.environ[DIAGNOSTIC_ENV_VAR] = previous


def _phase_summary(phase_sec: dict[str, object]) -> dict[str, object]:
    clean = {str(name): float(value) for name, value in phase_sec.items()}
    total = sum(clean.values())
    dominant = max(clean.items(), key=lambda item: item[1], default=(None, 0.0))
    return {
        "phase_sec": clean,
        "phase_total_sec": total,
        "dominant_phase": dominant[0],
        "dominant_phase_sec": dominant[1],
        "dominant_phase_fraction_of_phase_total": dominant[1] / total if total > 0.0 else None,
    }


def _row_from_payload(case: dict[str, object], payload: dict[str, object], wall_sec: float) -> dict[str, object]:
    metadata = payload["metadata"]
    prepare_metadata = dict(metadata.get("prepared_predicate_direct_status_union_prepare_metadata") or {})
    phase_sec = dict(prepare_metadata.get("prepare_phase_timing_sec") or {})
    phase = _phase_summary(phase_sec)
    timing_breakdown = dict(metadata.get("timing_breakdown_sec") or {})
    return {
        "status": "ok",
        "case": {
            **case,
            "mode_key": "predicate_direct_status_self_query",
            "point_count": POINT_COUNT,
            "repeat": 1,
            "warmup": 0,
        },
        "elapsed_sec": float(payload["elapsed_sec"]),
        "prepare_plus_replay_sec": float(metadata["prepare_plus_replay_median_sec"]),
        "prepared_predicate_direct_status_sec": float(metadata["prepared_predicate_direct_status_sec"]),
        "prepared_optix_count_threshold_sec": float(metadata["prepared_optix_count_threshold_sec"]),
        "predicate_direct_status_signature_sec": float(metadata["predicate_direct_status_signature_sec"]),
        "timing_breakdown_sec": {
            name: float(value)
            for name, value in timing_breakdown.items()
            if isinstance(value, (int, float))
        },
        "direct_status_prepare_metadata": {
            "prepare_phase_timing_available": bool(prepare_metadata.get("prepare_phase_timing_available", False)),
            "prepare_phase_timing_diagnostic_syncs": bool(
                prepare_metadata.get("prepare_phase_timing_diagnostic_syncs", False)
            ),
            "prepare_phase_timing_env_var": prepare_metadata.get("prepare_phase_timing_env_var"),
            "prepare_phase_timing_schema": prepare_metadata.get("prepare_phase_timing_schema"),
            "prepare_phase_timing_order": list(prepare_metadata.get("prepare_phase_timing_order") or ()),
            "prepare_phase_timing_total_observed_sec": prepare_metadata.get(
                "prepare_phase_timing_total_observed_sec"
            ),
            **phase,
            "point_count": prepare_metadata.get("point_count"),
            "partition_count": prepare_metadata.get("partition_count"),
            "cell_factor": prepare_metadata.get("cell_factor"),
            "cell_size": prepare_metadata.get("cell_size"),
            "point_coordinate_host_extraction": prepare_metadata.get("point_coordinate_host_extraction"),
            "point_coordinate_host_intermediate_tuple_avoided": prepare_metadata.get(
                "point_coordinate_host_intermediate_tuple_avoided"
            ),
        },
        "signature": payload["signature"],
        "wall_sec": wall_sec,
    }


def _dataset_pairs(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    pairs: dict[str, dict[str, object]] = {}
    ok_rows = [row for row in rows if row["status"] == "ok"]
    for dataset in sorted({str(row["case"]["dataset"]) for row in ok_rows}):
        off = next(
            row
            for row in ok_rows
            if str(row["case"]["dataset"]) == dataset and not bool(row["case"]["diagnostics"])
        )
        on = next(
            row
            for row in ok_rows
            if str(row["case"]["dataset"]) == dataset and bool(row["case"]["diagnostics"])
        )
        off_prepare = float(off["prepared_predicate_direct_status_sec"])
        on_prepare = float(on["prepared_predicate_direct_status_sec"])
        pairs[dataset] = {
            "production_prepare_sec": off_prepare,
            "diagnostic_prepare_sec": on_prepare,
            "diagnostic_over_production_prepare_ratio": on_prepare / off_prepare if off_prepare > 0.0 else None,
            "diagnostic_phase_total_sec": on["direct_status_prepare_metadata"]["phase_total_sec"],
            "diagnostic_total_observed_sec": on["direct_status_prepare_metadata"][
                "prepare_phase_timing_total_observed_sec"
            ],
            "dominant_phase": on["direct_status_prepare_metadata"]["dominant_phase"],
            "dominant_phase_sec": on["direct_status_prepare_metadata"]["dominant_phase_sec"],
            "dominant_phase_fraction_of_phase_total": on["direct_status_prepare_metadata"][
                "dominant_phase_fraction_of_phase_total"
            ],
            "signature_match": json.dumps(off["signature"], sort_keys=True)
            == json.dumps(on["signature"], sort_keys=True),
        }
    return pairs


def run_matrix() -> dict[str, object]:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSONL.write_text("", encoding="utf-8")

    rows: list[dict[str, object]] = []
    for case in _cases():
        previous = _set_diagnostics(bool(case["diagnostics"]))
        start = time.perf_counter()
        try:
            payload = run_rt_dbscan_benchmark(
                mode="optix_rt_core_flags_cupy_predicate_direct_status_column_signature_3d",
                dataset=str(case["dataset"]),
                point_count=POINT_COUNT,
                radius=None,
                min_neighbors=None,
                seed=20260519,
                partner="cupy",
                repeat=1,
                warmup=0,
                validate=False,
                include_rows=False,
            )
            row = _row_from_payload(case, payload, wall_sec=time.perf_counter() - start)
        except Exception as exc:  # pragma: no cover - pod evidence helper
            row = {
                "status": "error",
                "case": {**case, "point_count": POINT_COUNT},
                "error": repr(exc),
                "wall_sec": time.perf_counter() - start,
            }
        finally:
            _restore_diagnostics(previous)
        rows.append(row)
        with OUT_JSONL.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        print(
            json.dumps(
                {
                    "case": row["case"],
                    "status": row["status"],
                    "prepare_sec": row.get("prepared_predicate_direct_status_sec"),
                    "dominant_phase": (
                        row.get("direct_status_prepare_metadata", {}) or {}
                    ).get("dominant_phase"),
                },
                sort_keys=True,
            ),
            flush=True,
        )

    ok_rows = [row for row in rows if row["status"] == "ok"]
    packet = {
        "version": "rtdl.v3_0.rtdbscan_direct_status_prepare_breakdown.goal4487.v1",
        "point_count": POINT_COUNT,
        "case_count": len(rows),
        "ok_count": len(ok_rows),
        "error_count": len(rows) - len(ok_rows),
        "hardware": _gpu_info(),
        "env": {
            name: os.environ.get(name)
            for name in ("RTDL_OPTIX_LIBRARY", "CUDA_HOME", "NUMBA_CUDA_PREFIX")
        },
        "diagnostic_contract": {
            "env_var": DIAGNOSTIC_ENV_VAR,
            "diagnostic_syncs_are_opt_in": True,
            "production_rows_run_with_diagnostics_disabled": True,
            "diagnostic_rows_are_for_phase_accounting_not_public_timing": True,
        },
        "summary": {
            "dataset_pairs": _dataset_pairs(rows) if len(ok_rows) == len(rows) else {},
            "all_signatures_match_between_diagnostic_and_production": all(
                item["signature_match"] for item in _dataset_pairs(rows).values()
            )
            if len(ok_rows) == len(rows)
            else False,
        },
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(packet["summary"], indent=2, sort_keys=True), flush=True)
    return packet


if __name__ == "__main__":
    run_matrix()

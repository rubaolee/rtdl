from __future__ import annotations

import json
import os
from pathlib import Path
import time

from examples.benchmark_apps.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    run_rt_dbscan_benchmark,
)

from scripts.goal4487_m91_rtdbscan_direct_status_prepare_breakdown import (
    DIAGNOSTIC_ENV_VAR,
    POINT_COUNT,
    _cases,
    _dataset_pairs,
    _gpu_info,
    _restore_diagnostics,
    _row_from_payload,
    _set_diagnostics,
)


OUT_JSON = Path("docs/reports/goal4488_v3_0_m92_rtdbscan_direct_status_row_columnization_2026-06-17.json")
OUT_JSONL = Path("docs/reports/goal4488_v3_0_m92_rtdbscan_direct_status_row_columnization_2026-06-17.jsonl")
BASELINE_JSON = Path("docs/reports/goal4487_v3_0_m91_rtdbscan_direct_status_prepare_breakdown_2026-06-17.json")


def _baseline_pairs() -> dict[str, dict[str, object]]:
    if not BASELINE_JSON.exists():
        return {}
    packet = json.loads(BASELINE_JSON.read_text(encoding="utf-8"))
    return dict((packet.get("summary") or {}).get("dataset_pairs") or {})


def _compare_to_m91(current_pairs: dict[str, dict[str, object]]) -> dict[str, dict[str, object]]:
    baseline = _baseline_pairs()
    comparison: dict[str, dict[str, object]] = {}
    for dataset, current in current_pairs.items():
        old = baseline.get(dataset)
        if not old:
            continue
        old_prepare = float(old["production_prepare_sec"])
        new_prepare = float(current["production_prepare_sec"])
        old_diag_total = float(old["diagnostic_phase_total_sec"])
        new_diag_total = float(current["diagnostic_phase_total_sec"])
        comparison[dataset] = {
            "m91_production_prepare_sec": old_prepare,
            "m92_production_prepare_sec": new_prepare,
            "production_prepare_speedup": old_prepare / new_prepare if new_prepare > 0.0 else None,
            "production_prepare_delta_sec": new_prepare - old_prepare,
            "m91_diagnostic_phase_total_sec": old_diag_total,
            "m92_diagnostic_phase_total_sec": new_diag_total,
            "diagnostic_phase_total_speedup": old_diag_total / new_diag_total if new_diag_total > 0.0 else None,
            "m91_dominant_phase": old.get("dominant_phase"),
            "m92_dominant_phase": current.get("dominant_phase"),
        }
    return comparison


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
                    "coordinate_source": (
                        row.get("direct_status_prepare_metadata", {}) or {}
                    ).get("point_coordinate_host_extraction"),
                    "dominant_phase": (
                        row.get("direct_status_prepare_metadata", {}) or {}
                    ).get("dominant_phase"),
                },
                sort_keys=True,
            ),
            flush=True,
        )

    ok_rows = [row for row in rows if row["status"] == "ok"]
    current_pairs = _dataset_pairs(rows) if len(ok_rows) == len(rows) else {}
    packet = {
        "version": "rtdl.v3_0.rtdbscan_direct_status_row_columnization.goal4488.v1",
        "point_count": POINT_COUNT,
        "case_count": len(rows),
        "ok_count": len(ok_rows),
        "error_count": len(rows) - len(ok_rows),
        "hardware": _gpu_info(),
        "env": {
            name: os.environ.get(name)
            for name in ("RTDL_OPTIX_LIBRARY", "CUDA_HOME", "NUMBA_CUDA_PREFIX")
        },
        "baseline_packet": str(BASELINE_JSON),
        "change": (
            "direct-status prepare now builds host x/y/z lists directly for common "
            "Point3D, mapping, and sequence rows instead of first materializing a "
            "generic tuple-of-xyz intermediate"
        ),
        "diagnostic_contract": {
            "env_var": DIAGNOSTIC_ENV_VAR,
            "diagnostic_syncs_are_opt_in": True,
            "production_rows_run_with_diagnostics_disabled": True,
            "diagnostic_rows_are_for_phase_accounting_not_public_timing": True,
        },
        "summary": {
            "dataset_pairs": current_pairs,
            "m92_vs_m91": _compare_to_m91(current_pairs),
            "all_signatures_match_between_diagnostic_and_production": all(
                item["signature_match"] for item in current_pairs.values()
            )
            if current_pairs
            else False,
        },
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(packet["summary"], indent=2, sort_keys=True), flush=True)
    return packet


if __name__ == "__main__":
    run_matrix()

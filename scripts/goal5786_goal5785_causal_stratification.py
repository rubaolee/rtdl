#!/usr/bin/env python3
"""Read-only causal stratification of the immutable Goal5785 matrix.

The audit reconstructs all 34 rows from raw workers, verifies the frozen
bootstrap classification, and decomposes cold endpoint gaps into the mutually
exclusive loading/preparation/execute/close phases recorded by the worker.
Prepared rows are deliberately kept at the execute-envelope level because the
formal evidence exposes no mutually exclusive sub-phases inside that timer.

Observed component seconds are locations, not predicted savings.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
import tarfile
from collections import Counter
from pathlib import Path


V2 = "v2_direct_true_optix_backport"
V4 = "v4_restricted_callback_true_optix"
COLD = "installed_cold_compile_prepare_execute"
PREPARED = "prepared_first_execute"
PHASES = ("loading", "preparation", "execute", "close")
SEED_BASE = 57_760_000
BOOTSTRAP_DRAWS = 10_000
CI_LOW_INDEX = 249
CI_HIGH_INDEX = 9749


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def median(values: list[float]) -> float:
    return float(statistics.median(values))


def bootstrap_ci(values: list[float], row_index: int) -> list[float]:
    rng = random.Random(SEED_BASE + row_index)
    draws = sorted(
        median(rng.choices(values, k=len(values)))
        for _ in range(BOOTSTRAP_DRAWS)
    )
    return [draws[CI_LOW_INDEX], draws[CI_HIGH_INDEX]]


def classification(ci: list[float]) -> str:
    if ci[0] > 1.0:
        return "clear_win"
    if ci[1] < 1.0:
        return "clear_loss"
    return "uncertain"


def endpoint(worker: dict[str, object], row_id: str) -> float:
    selected = [row for row in worker["rows"] if row["row_id"] == row_id]
    if len(selected) != 1:
        raise RuntimeError(f"registered row missing or duplicated: {row_id}")
    return float(selected[0]["registered_complete_endpoint_seconds"])


def phases(worker: dict[str, object], row_id: str) -> dict[str, float]:
    accounting = worker["phase_accounting"]
    if accounting["same_worker_mutually_exclusive_phases"] is not True:
        raise RuntimeError("phase accounting is not mutually exclusive")
    return {
        "loading": float(accounting["loading_seconds"]),
        "preparation": float(accounting["preparation_seconds"]),
        "execute": float(accounting["row_execute_seconds"][row_id]),
        "close": float(accounting["close_seconds"]),
    }


def dominant_positive(delta: dict[str, float]) -> str:
    positive = {name: value for name, value in delta.items() if value > 0.0}
    return max(positive, key=positive.get) if positive else "none"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--evaluation", required=True, type=Path)
    parser.add_argument("--execution-source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    with tarfile.open(args.evidence, "r:gz") as archive:
        workers = [
            json.load(archive.extractfile(member))
            for member in archive.getmembers()
            if member.isfile()
            and member.name.startswith("RAW/workers/")
            and member.name.endswith(".json")
        ]
    workers.sort(key=lambda worker: int(worker["worker_index"]))
    if len(workers) != 464 or [int(w["worker_index"]) for w in workers] != list(range(464)):
        raise RuntimeError("Goal5785 worker universe is not exact")
    if len({int(worker["parent_pid"]) for worker in workers}) != 464:
        raise RuntimeError("Goal5785 parent processes are not fresh")
    if any(worker["matched"] is not True for worker in workers):
        raise RuntimeError("incorrect worker present")

    evaluation = json.loads(args.evaluation.read_text(encoding="utf-8"))
    submitted_rows = list(evaluation["rows"])
    if len(submitted_rows) != 34:
        raise RuntimeError("submitted row universe is not 34")

    indexed: dict[tuple[str, str, int, str], dict[str, object]] = {}
    for worker in workers:
        key = (
            str(worker["lifecycle"]),
            str(worker["unit_id"]),
            int(worker["pair_index"]),
            str(worker["method"]),
        )
        if key in indexed:
            raise RuntimeError(f"duplicate worker key: {key}")
        indexed[key] = worker

    output_rows: list[dict[str, object]] = []
    max_numeric_delta = 0.0
    for row_index, submitted in enumerate(submitted_rows):
        lifecycle = str(submitted["lifecycle"])
        unit_id = str(submitted["unit_id"])
        row_id = str(submitted["row_id"])
        pair_records: list[dict[str, object]] = []
        ratios: list[float] = []
        for pair_index in range(8):
            v2 = indexed[(lifecycle, unit_id, pair_index, V2)]
            v4 = indexed[(lifecycle, unit_id, pair_index, V4)]
            v2_seconds = endpoint(v2, row_id)
            v4_seconds = endpoint(v4, row_id)
            ratio = v2_seconds / v4_seconds
            ratios.append(ratio)
            pair_record: dict[str, object] = {
                "pair_index": pair_index,
                "v2_seconds": v2_seconds,
                "v4_seconds": v4_seconds,
                "v2_over_v4": ratio,
                "v4_minus_v2_endpoint_seconds": v4_seconds - v2_seconds,
            }
            if lifecycle == COLD:
                v2_phases = phases(v2, row_id)
                v4_phases = phases(v4, row_id)
                for worker, observed in ((v2, v2_phases), (v4, v4_phases)):
                    expected = endpoint(worker, row_id)
                    if not math.isclose(sum(observed.values()), expected, rel_tol=1e-10, abs_tol=1e-8):
                        raise RuntimeError(f"cold phase conservation failed: {row_id}")
                delta = {name: v4_phases[name] - v2_phases[name] for name in PHASES}
                if not math.isclose(sum(delta.values()), v4_seconds - v2_seconds,
                                    rel_tol=1e-10, abs_tol=1e-8):
                    raise RuntimeError(f"paired cold delta does not conserve: {row_id}")
                pair_record["v4_minus_v2_phase_seconds"] = delta
                pair_record["largest_positive_phase"] = dominant_positive(delta)
            else:
                for worker in (v2, v4):
                    observed = phases(worker, row_id)
                    if not math.isclose(observed["execute"], endpoint(worker, row_id),
                                        rel_tol=1e-12, abs_tol=1e-10):
                        raise RuntimeError(f"prepared registered timer is not execute envelope: {row_id}")
                    if worker["close_inside_registered_timer"] is not False:
                        raise RuntimeError("prepared close unexpectedly inside timer")
                pair_record["subphase_attribution_available"] = False
            pair_records.append(pair_record)

        row_median = median(ratios)
        row_ci = bootstrap_ci(ratios, row_index)
        submitted_ci = [float(value) for value in submitted["bootstrap_ci95"]]
        max_numeric_delta = max(
            max_numeric_delta,
            abs(row_median - float(submitted["paired_ratio_median"])),
            abs(row_ci[0] - submitted_ci[0]),
            abs(row_ci[1] - submitted_ci[1]),
        )
        if max_numeric_delta > 1e-12:
            raise RuntimeError(f"submitted statistic mismatch at {row_id}")

        result: dict[str, object] = {
            "row_index": row_index,
            "app": submitted["app"],
            "lifecycle": lifecycle,
            "unit_id": unit_id,
            "row_id": row_id,
            "paired_ratio_median_v2_over_v4": row_median,
            "bootstrap_ci95": row_ci,
            "ci_classification": classification(row_ci),
            "median_v2_seconds": median([float(pair["v2_seconds"]) for pair in pair_records]),
            "median_v4_seconds": median([float(pair["v4_seconds"]) for pair in pair_records]),
            "median_v4_minus_v2_endpoint_seconds": median([
                float(pair["v4_minus_v2_endpoint_seconds"]) for pair in pair_records
            ]),
            "pair_count": 8,
            "pairs": pair_records,
        }
        if lifecycle == COLD:
            dominance = Counter(str(pair["largest_positive_phase"]) for pair in pair_records)
            result["largest_positive_phase_counts"] = {
                name: dominance[name] for name in (*PHASES, "none")
            }
            result["dominant_phase_at_least_six_of_eight"] = next(
                (name for name in PHASES if dominance[name] >= 6), "heterogeneous"
            )
            result["median_v4_minus_v2_phase_seconds"] = {
                name: median([
                    float(pair["v4_minus_v2_phase_seconds"][name])
                    for pair in pair_records
                ])
                for name in PHASES
            }
        else:
            result["attribution_level"] = "registered_execute_envelope_only"
        output_rows.append(result)

    cold_rows = [row for row in output_rows if row["lifecycle"] == COLD]
    prepared_rows = [row for row in output_rows if row["lifecycle"] == PREPARED]
    cold_clear_losses = [row for row in cold_rows if row["ci_classification"] == "clear_loss"]
    prepared_clear_losses = [row for row in prepared_rows if row["ci_classification"] == "clear_loss"]
    phase_bins = Counter(str(row["dominant_phase_at_least_six_of_eight"])
                         for row in cold_clear_losses)

    v4_workers = [worker for worker in workers if worker["method"] == V4]
    result = {
        "schema": "rtdl.goal5786.goal5785_causal_stratification.v1",
        "status": "COMPLETE__READ_ONLY_CAUSAL_LOCATION__NO_REPAIR",
        "inputs": {
            "goal5785_evidence_sha256": sha256_file(args.evidence),
            "goal5785_evaluation_sha256": sha256_file(args.evaluation),
            "goal5785_execution_source_sha256": sha256_file(args.execution_source),
        },
        "reconstruction": {
            "worker_count": len(workers),
            "unique_parent_pid_count": len({int(worker["parent_pid"]) for worker in workers}),
            "row_count": len(output_rows),
            "max_submitted_statistic_delta": max_numeric_delta,
            "cold_phase_conservation_proven_per_pair": True,
            "prepared_subphase_attribution_available": False,
        },
        "classification": {
            "clear_win_count": sum(row["ci_classification"] == "clear_win" for row in output_rows),
            "clear_loss_count": sum(row["ci_classification"] == "clear_loss" for row in output_rows),
            "uncertain_count": sum(row["ci_classification"] == "uncertain" for row in output_rows),
            "cold_clear_loss_count": len(cold_clear_losses),
            "prepared_clear_loss_count": len(prepared_clear_losses),
            "cold_clear_loss_mechanism_bins": dict(sorted(phase_bins.items())),
            "prepared_clear_loss_rows": [str(row["row_id"]) for row in prepared_clear_losses],
        },
        "leaf_cache_census": {
            "hit_count": sum(int(worker["leaf_cache"].get("hit_count", 0)) for worker in v4_workers),
            "miss_count": sum(int(worker["leaf_cache"].get("miss_count", 0)) for worker in v4_workers),
            "disabled_count": sum(int(worker["leaf_cache"].get("disabled_count", 0)) for worker in v4_workers),
        },
        "rows": output_rows,
        "interpretation_contract": {
            "observed_component_seconds_are_predicted_savings": False,
            "component_medians_may_be_added_to_endpoint_median": False,
            "prepared_subphases_invented": False,
            "ci_crossing_rows_are_repair_targets": False,
            "clear_win_rows_are_negative_controls": True,
            "product_or_native_changed": False,
            "worker_or_gpu_used": False,
            "goal5785_changed_or_relabelled": False,
        },
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "output_sha256": sha256_file(args.output),
        "classification": result["classification"],
        "leaf_cache_census": result["leaf_cache_census"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

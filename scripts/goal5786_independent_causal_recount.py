#!/usr/bin/env python3
"""Independent compact recount for Goal5786.

Imports neither the primary Goal5786 audit nor the Goal5776 evaluator/recount.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import tarfile
from collections import Counter
from pathlib import Path


V2 = "v2_direct_true_optix_backport"
V4 = "v4_restricted_callback_true_optix"
COLD = "installed_cold_compile_prepare_execute"
PHASES = ("loading", "preparation", "execute", "close")


def med(values: list[float]) -> float:
    return float(statistics.median(values))


def endpoint(worker: dict, row_id: str) -> float:
    return float(next(row for row in worker["rows"] if row["row_id"] == row_id)[
        "registered_complete_endpoint_seconds"
    ])


def phase(worker: dict, row_id: str) -> dict[str, float]:
    observed = worker["phase_accounting"]
    return {
        "loading": float(observed["loading_seconds"]),
        "preparation": float(observed["preparation_seconds"]),
        "execute": float(observed["row_execute_seconds"][row_id]),
        "close": float(observed["close_seconds"]),
    }


def ci(values: list[float], index: int) -> list[float]:
    rng = random.Random(57_760_000 + index)
    draws = sorted(med(rng.choices(values, k=8)) for _ in range(10_000))
    return [draws[249], draws[9749]]


def cls(bounds: list[float]) -> str:
    return "clear_win" if bounds[0] > 1 else "clear_loss" if bounds[1] < 1 else "uncertain"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--evaluation", required=True, type=Path)
    parser.add_argument("--primary", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    with tarfile.open(args.evidence, "r:gz") as archive:
        workers = [json.load(archive.extractfile(member)) for member in archive.getmembers()
                   if member.isfile() and member.name.startswith("RAW/workers/")
                   and member.name.endswith(".json")]
    evaluation = json.loads(args.evaluation.read_text(encoding="utf-8"))
    primary = json.loads(args.primary.read_text(encoding="utf-8"))
    indexed = {(w["lifecycle"], w["unit_id"], int(w["pair_index"]), w["method"]): w
               for w in workers}
    rows = []
    for index, submitted in enumerate(evaluation["rows"]):
        life, unit, row_id = submitted["lifecycle"], submitted["unit_id"], submitted["row_id"]
        ratios, dominants = [], []
        for pair in range(8):
            v2, v4 = indexed[(life, unit, pair, V2)], indexed[(life, unit, pair, V4)]
            ratios.append(endpoint(v2, row_id) / endpoint(v4, row_id))
            if life == COLD:
                p2, p4 = phase(v2, row_id), phase(v4, row_id)
                delta = {name: p4[name] - p2[name] for name in PHASES}
                positive = {name: value for name, value in delta.items() if value > 0}
                dominants.append(max(positive, key=positive.get) if positive else "none")
        bounds = ci(ratios, index)
        counts = Counter(dominants)
        rows.append({
            "row_id": row_id,
            "lifecycle": life,
            "median": med(ratios),
            "ci": bounds,
            "classification": cls(bounds),
            "dominant_phase_at_least_six": next(
                (name for name in PHASES if counts[name] >= 6), "heterogeneous"
            ) if life == COLD else None,
        })
    primary_rows = primary["rows"]
    if len(primary_rows) != len(rows):
        raise RuntimeError("primary row count mismatch")
    for expected, actual in zip(primary_rows, rows, strict=True):
        if expected["row_id"] != actual["row_id"] \
                or expected["paired_ratio_median_v2_over_v4"] != actual["median"] \
                or expected["bootstrap_ci95"] != actual["ci"] \
                or expected["ci_classification"] != actual["classification"]:
            raise RuntimeError(f"primary mismatch: {actual['row_id']}")
        if actual["lifecycle"] == COLD \
                and expected["dominant_phase_at_least_six_of_eight"] \
                != actual["dominant_phase_at_least_six"]:
            raise RuntimeError(f"primary dominance mismatch: {actual['row_id']}")
    cold_losses = [row for row in rows if row["lifecycle"] == COLD
                   and row["classification"] == "clear_loss"]
    result = {
        "schema": "rtdl.goal5786.independent_causal_recount.v1",
        "status": "PASS__RAW_CLASSIFICATION_AND_COLD_DOMINANCE_REBUILT",
        "worker_count": len(workers),
        "row_count": len(rows),
        "classifications": dict(Counter(row["classification"] for row in rows)),
        "cold_clear_loss_mechanism_bins": dict(Counter(
            row["dominant_phase_at_least_six"] for row in cold_losses
        )),
        "prepared_clear_loss_rows": [row["row_id"] for row in rows
                                     if row["lifecycle"] != COLD
                                     and row["classification"] == "clear_loss"],
        "imports_primary_or_submitted_statistics_modules": False,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

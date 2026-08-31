#!/usr/bin/env python3
"""Independent Goal5819 reconstruction from frozen Goal5817 raw receipts.

This script imports no Goal5817 evaluator or experiment module.  It reads the
immutable evidence tar directly, reconstructs worker metrics, absolute cell
medians, paired-block ratios, and the registered fixed-seed bootstrap, then
checks the published Goal5817 result and exact frozen source identities.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import random
import re
import statistics
import tarfile
from pathlib import Path
from typing import Any


TASKS = ("relation", "triangle")
REGIMES = ("DEPLOYMENT_COLD", "PREPARE", "STEADY_E2E")
ARMS = ("DIRECT", "PYOPTIX", "RTDL")
COMPARISONS = (
    ("RTDL", "PYOPTIX"),
    ("PYOPTIX", "DIRECT"),
    ("RTDL", "DIRECT"),
)
BLOCK_COUNT = 18
BOOTSTRAP_DRAWS = 10_000
EXPECTED_WORKERS = 324
EXPECTED_REGISTERED_TIMINGS = 7_128
EXPECTED_ARCHIVE_SHA256 = (
    "a3ed54510166e33adb5f776d5832148feb796fba4f2290ff5f90dc6c15b7083b"
)
EXPECTED_RESULT_SHA256 = (
    "dbe4db254ba9e5e66ffaa51bd74cb48d4824f312e5edbda2e920228123303eed"
)
EXPECTED_FREEZE_SHA256 = (
    "7b859ab8f6a4027dc01bcdababcece922fc44a82bf8e116d389756afd63a7e0c"
)
EXPECTED_SOURCE_BUNDLE_SHA256 = (
    "91d2df6f126f885cd82372a82ee700f96614a1b778b8fa197eb77a11e2082b30"
)

WORKER_RE = re.compile(
    r"^results/formal_matrix_v1/workers/"
    r"(relation|triangle)_(deployment_cold|prepare|steady_e2e)_"
    r"b([0-9]{2})_p[0-2]_(direct|pyoptix|rtdl)/stdout[.]bin$"
)

SOURCE_IDENTITIES = {
    "outer:packet/source/experiments/goal5817_three_arm/formal_python_worker.py":
        "499ef4c598202b6ac709f3781030f29d65a953b753ca3a74b0e3e701814f66a5",
    "outer:packet/source/experiments/goal5817_three_arm/evaluate.py":
        "7e12504acc904bcd9c44d0c36f7854cc7ca2dc688e043a077d6fee0862784312",
    "outer:packet/source/experiments/goal5817_three_arm/protocol.py":
        "96bace00b345196fe323bcbeacabda33a2cb01b55993c5d578727058181d70c3",
    "outer:packet/source/experiments/goal5802_premeasurement/direct_scalar_worker.cpp":
        "078570a19000221890bd5421676c8d4857fd2196c5b7daae60eec7d511ffd165",
    "nested:source/experiments/goal5796_matched/direct_optix.cpp":
        "2533a14152e441f97690e8e427e97f1be5f1747ee8faa0f181cd05b438a01383",
    "nested:source/experiments/goal5802_premeasurement/pyoptix_scalar_arm.py":
        "a84ca53e951d12f683824f8df414268b4ea5624491a35572d3044877246692ba",
    "nested:source/experiments/goal5802_premeasurement/rtdlexe_arm.py":
        "d3be42107e57014ef1ae6c6d3b58067a707409a00f1b6d1e5cf6d52e6abe1ba9",
    "nested:source/src/rtdsl/v4_rtdlexe.py":
        "ea32830ec3ba273523adf947e4e85c460af2ca50aaa316eeb90e1caa39bda097",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def member_bytes(archive: tarfile.TarFile, name: str) -> bytes:
    handle = archive.extractfile(name)
    if handle is None:
        raise RuntimeError(f"missing regular tar member: {name}")
    return handle.read()


def percentile(sorted_values: list[float], probability: float) -> float:
    return sorted_values[int(probability * (len(sorted_values) - 1))]


def regime_from_slug(value: str) -> str:
    return value.upper()


def reconstruct(repo: Path) -> dict[str, Any]:
    docs = repo / "history" / "internal_docs"
    archive_path = docs / "goal5817_current_source_three_arm_formal_evidence_v1_20260829.tar.gz"
    result_path = docs / "goal5817_current_source_three_arm_formal_result_20260829.json"
    freeze_path = docs / "goal5817_current_source_three_arm_scientific_freeze_v6_20260829.json"

    archive_raw = archive_path.read_bytes()
    result_raw = result_path.read_bytes()
    freeze_raw = freeze_path.read_bytes()
    require(sha256(archive_raw) == EXPECTED_ARCHIVE_SHA256, "evidence archive identity differs")
    require(sha256(result_raw) == EXPECTED_RESULT_SHA256, "published result identity differs")
    require(sha256(freeze_raw) == EXPECTED_FREEZE_SHA256, "scientific freeze identity differs")
    published = json.loads(result_raw)

    workers: dict[tuple[str, str, int, str], dict[str, Any]] = {}
    timing_count = 0
    exact_source_observed: dict[str, str] = {}
    direct_phase_values: dict[tuple[str, str, str], list[int]] = {}

    with tarfile.open(fileobj=io.BytesIO(archive_raw), mode="r:gz") as outer:
        outer_names = {member.name for member in outer.getmembers()}
        for label, expected in SOURCE_IDENTITIES.items():
            if not label.startswith("outer:"):
                continue
            name = label.removeprefix("outer:")
            require(name in outer_names, f"outer source absent: {name}")
            observed = sha256(member_bytes(outer, name))
            require(observed == expected, f"outer source identity differs: {name}")
            exact_source_observed[label] = observed

        nested_name = (
            "packet/source/history/internal_docs/"
            "goal5805_performance_repair_source_bundle_v5_20260828.tar.gz"
        )
        nested_raw = member_bytes(outer, nested_name)
        require(sha256(nested_raw) == EXPECTED_SOURCE_BUNDLE_SHA256,
                "nested source bundle identity differs")
        with tarfile.open(fileobj=io.BytesIO(nested_raw), mode="r:gz") as nested:
            nested_names = {member.name for member in nested.getmembers()}
            source_freeze = json.loads(member_bytes(nested, "freeze.json"))
            source_manifest = {
                "source/" + row["path"]: row["sha256"]
                for row in source_freeze["source_manifest"]
            }
            for label, expected in SOURCE_IDENTITIES.items():
                if not label.startswith("nested:"):
                    continue
                name = label.removeprefix("nested:")
                require(name in nested_names, f"nested source absent: {name}")
                observed = sha256(member_bytes(nested, name))
                require(observed == expected, f"nested source identity differs: {name}")
                require(source_manifest.get(name) == expected,
                        f"nested source manifest differs: {name}")
                exact_source_observed[label] = observed

        for member in outer.getmembers():
            match = WORKER_RE.fullmatch(member.name)
            if match is None:
                continue
            task, regime_slug, block_text, arm_slug = match.groups()
            regime = regime_from_slug(regime_slug)
            block = int(block_text)
            arm = arm_slug.upper()
            document = json.loads(member_bytes(outer, member.name))
            require(document.get("status") == "PASS", f"worker not PASS: {member.name}")
            expected_arm = "A_DIRECT_CUDA_OPTIX" if arm == "DIRECT" else arm
            require(document.get("arm") == expected_arm, f"worker arm differs: {member.name}")
            require(document.get("worker_id") == member.name.split("/")[-2],
                    f"worker id differs: {member.name}")
            durations = document.get(
                "execute_or_regime_durations_ns" if arm == "DIRECT" else "durations_ns")
            expected_count = 64 if regime == "STEADY_E2E" else 1
            require(isinstance(durations, list) and len(durations) == expected_count,
                    f"worker duration count differs: {member.name}")
            require(all(type(value) is int and value > 0 for value in durations),
                    f"worker duration invalid: {member.name}")
            require(document.get("registered_performance_timing_count") == expected_count,
                    f"worker registered count differs: {member.name}")
            metric = int(statistics.median(durations))
            if arm != "DIRECT":
                require(document.get("metric_ns") == metric,
                        f"Python worker metric differs: {member.name}")
            key = (task, regime, block, arm)
            require(key not in workers, f"duplicate worker key: {key}")
            workers[key] = {
                "metric_ns": metric,
                "timing_count": expected_count,
            }
            timing_count += expected_count
            if arm == "DIRECT":
                phases = document.get("phase_durations_ns")
                require(isinstance(phases, dict), f"Direct phases absent: {member.name}")
                for phase, value in phases.items():
                    require(type(value) is int and value >= 0,
                            f"Direct phase invalid: {member.name}:{phase}")
                    direct_phase_values.setdefault((task, regime, phase), []).append(value)

    require(len(workers) == EXPECTED_WORKERS, "worker count differs")
    require(timing_count == EXPECTED_REGISTERED_TIMINGS, "registered timing count differs")
    require(all((task, regime, block, arm) in workers
                for task in TASKS for regime in REGIMES
                for block in range(BLOCK_COUNT) for arm in ARMS),
            "worker universe is incomplete")

    published_cells = {
        (row["task"], row["regime"], row["arm"]): row
        for row in published["formal"]["descriptive_cell_medians"]
    }
    absolute_cells: list[dict[str, Any]] = []
    for task in TASKS:
        for regime in REGIMES:
            medians: dict[str, float] = {}
            for arm in ARMS:
                values = [workers[(task, regime, block, arm)]["metric_ns"]
                          for block in range(BLOCK_COUNT)]
                median_ns = statistics.median(values)
                medians[arm] = median_ns
                published_row = published_cells[(task, regime, arm)]
                require(published_row["metric_median_ns"] == median_ns,
                        f"published absolute median differs: {(task, regime, arm)}")
                require(published_row["metric_min_ns"] == min(values),
                        f"published absolute minimum differs: {(task, regime, arm)}")
                require(published_row["metric_max_ns"] == max(values),
                        f"published absolute maximum differs: {(task, regime, arm)}")
            delta_ns = medians["RTDL"] - medians["PYOPTIX"]
            absolute_cells.append({
                "task": task,
                "regime": regime,
                "worker_count_per_arm": BLOCK_COUNT,
                "absolute_median_ns": medians,
                "absolute_median_ms": {
                    arm: medians[arm] / 1_000_000 for arm in ARMS
                },
                "rtdl_minus_pyoptix_ns": delta_ns,
                "rtdl_minus_pyoptix_ms": delta_ns / 1_000_000,
            })

    published_rows = {
        (row["task"], row["regime"], row["numerator"], row["denominator"]): row
        for row in published["formal"]["registered_rows"]
    }
    reconstructed_rows: list[dict[str, Any]] = []
    for task_index, task in enumerate(TASKS):
        for regime_index, regime in enumerate(REGIMES):
            for comparison_index, (numerator, denominator) in enumerate(COMPARISONS):
                ratios = [
                    workers[(task, regime, block, numerator)]["metric_ns"]
                    / workers[(task, regime, block, denominator)]["metric_ns"]
                    for block in range(BLOCK_COUNT)
                ]
                point = float(statistics.median(ratios))
                seed = (58_170_000 + task_index * 100
                        + regime_index * 10 + comparison_index)
                generator = random.Random(seed)
                draws = sorted(float(statistics.median([
                    ratios[generator.randrange(BLOCK_COUNT)]
                    for _ in range(BLOCK_COUNT)
                ])) for _ in range(BOOTSTRAP_DRAWS))
                interval = [percentile(draws, 0.025), percentile(draws, 0.975)]
                published_row = published_rows[(task, regime, numerator, denominator)]
                require(published_row["ratio"] == point,
                        f"published ratio differs: {(task, regime, numerator, denominator)}")
                require(published_row["ci95"] == interval,
                        f"published interval differs: {(task, regime, numerator, denominator)}")
                require(published_row["bootstrap_seed"] == seed,
                        f"published seed differs: {(task, regime, numerator, denominator)}")
                reconstructed_rows.append({
                    "task": task,
                    "regime": regime,
                    "numerator": numerator,
                    "denominator": denominator,
                    "paired_block_ratio_count": BLOCK_COUNT,
                    "ratio": point,
                    "ci95": interval,
                    "bootstrap_seed": seed,
                })

    published_direct_phases = {
        (row["task"], row["regime"]): row["phase_medians_ns"]
        for row in published["formal"]["descriptive_direct_phase_medians"]
    }
    reconstructed_direct_phases: list[dict[str, Any]] = []
    for task in TASKS:
        for regime in REGIMES:
            phases = {
                phase: statistics.median(values)
                for (row_task, row_regime, phase), values in direct_phase_values.items()
                if row_task == task and row_regime == regime
            }
            require(phases == published_direct_phases[(task, regime)],
                    f"published Direct phase medians differ: {(task, regime)}")
            reconstructed_direct_phases.append({
                "task": task,
                "regime": regime,
                "worker_count": BLOCK_COUNT,
                "phase_medians_ns": phases,
            })

    return {
        "schema": "rtdl.goal5819.frozen_performance_reconstruction.v1",
        "status": "PASS__RAW_RECEIPTS_AND_EXACT_SOURCES_RECONSTRUCTED",
        "scope": "NO_RERUN__FROZEN_GOAL5817_BYTES_ONLY",
        "source_identity": {
            "evidence_archive_bytes": len(archive_raw),
            "evidence_archive_sha256": sha256(archive_raw),
            "published_result_bytes": len(result_raw),
            "published_result_sha256": sha256(result_raw),
            "scientific_freeze_bytes": len(freeze_raw),
            "scientific_freeze_sha256": sha256(freeze_raw),
            "nested_source_bundle_sha256": EXPECTED_SOURCE_BUNDLE_SHA256,
            "exact_source_files": exact_source_observed,
        },
        "counts": {
            "task_count": 2,
            "regime_count": 3,
            "arm_count": 3,
            "formal_worker_count": len(workers),
            "worker_count_per_arm_task_regime": BLOCK_COUNT,
            "registered_performance_timing_count": timing_count,
            "cold_timings_per_worker": 1,
            "prepare_timings_per_worker": 1,
            "steady_warmups_per_worker_unregistered": 8,
            "steady_timings_per_worker": 64,
            "registered_comparison_row_count": len(reconstructed_rows),
        },
        "bootstrap_convention": {
            "point_estimator": "statistics.median of 18 paired block-local numerator/denominator ratios",
            "bootstrap_draws": BOOTSTRAP_DRAWS,
            "sample_depth_per_draw": BLOCK_COUNT,
            "sampler": "[ratios[generator.randrange(18)] for _ in range(18)]",
            "rng": "CPython random.Random at frozen Python 3.12.3 runtime",
            "seed_formula": "58170000 + task_index*100 + regime_index*10 + comparison_index",
            "task_order": list(TASKS),
            "regime_order": list(REGIMES),
            "comparison_order": [list(row) for row in COMPARISONS],
            "percentile_rule": "sorted_draws[int(p*(10000-1))]",
            "ci95_indices_zero_based": [249, 9749],
            "random_choices_used": False,
        },
        "absolute_cells": absolute_cells,
        "registered_rows": reconstructed_rows,
        "direct_phase_medians": reconstructed_direct_phases,
        "published_absolute_cells_exact": True,
        "published_registered_rows_and_intervals_exact": True,
        "published_direct_phase_medians_exact": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args()
    result = reconstruct(args.repo.resolve())
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

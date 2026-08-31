#!/usr/bin/env python3
"""Build the Goal5817 three-arm closeout from independently recounted evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics
from typing import Any


TASKS = ("relation", "triangle")
REGIMES = ("DEPLOYMENT_COLD", "PREPARE", "STEADY_E2E")
ARMS = ("DIRECT", "PYOPTIX", "RTDL")


def canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root is not an object: {path}")
    return value


def median_ns(values: list[int]) -> int | float:
    if not values or any(type(value) is not int or value <= 0 for value in values):
        raise RuntimeError("invalid duration population")
    return statistics.median(values)


def median_nonnegative_ns(values: list[int]) -> int | float:
    if not values or any(type(value) is not int or value < 0 for value in values):
        raise RuntimeError("invalid nonnegative duration population")
    return statistics.median(values)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--controller", type=Path, required=True)
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--independent-recount", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--target-observation", type=Path, required=True)
    parser.add_argument("--evidence-archive", type=Path, required=True)
    parser.add_argument("--prior-result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    output = args.output.absolute()
    if output.exists():
        raise FileExistsError(output)

    controller = load(args.controller)
    evaluation = load(args.evaluation)
    recount = load(args.independent_recount)
    freeze = load(args.freeze)
    authority = load(args.authority)
    target = load(args.target_manifest)
    target_observation = load(args.target_observation)
    prior = load(args.prior_result)

    workers = controller.get("workers")
    if not isinstance(workers, list) or len(workers) != 324:
        raise RuntimeError("formal worker universe differs")
    if controller.get("formal_worker_count") != 324 \
            or controller.get("registered_performance_timing_count") != 7_128 \
            or controller.get("status") != "COMPLETE__NO_RETRY_REPLACEMENT_OR_ROW_DROP":
        raise RuntimeError("controller closeout differs")
    if recount.get("status") != "PASS__324_RAW_WORKERS_AND_18_ROWS_EXACT" \
            or recount.get("rows") != evaluation.get("rows") \
            or recount.get("gated_pass_count") != 2 \
            or recount.get("retry_replacement_row_drop_count") != 0:
        raise RuntimeError("independent recount differs")
    if controller.get("freeze_file_sha256") != sha256(args.freeze) \
            or controller.get("authority_file_sha256") != sha256(args.authority) \
            or controller.get("target_manifest_file_sha256") != sha256(args.target_manifest):
        raise RuntimeError("controller authority chain differs")
    if authority.get("freeze_file", {}).get("sha256") != sha256(args.freeze):
        raise RuntimeError("authority/freeze binding differs")
    if target.get("files", {}).get("target_observation", {}).get("sha256") \
            != sha256(args.target_observation):
        raise RuntimeError("target manifest/observation binding differs")
    if target_observation.get("gpu_name") != "NVIDIA RTX 4000 Ada Generation":
        raise RuntimeError("target GPU differs")

    cell_rows = []
    direct_phase_rows = []
    for task in TASKS:
        for regime in REGIMES:
            for arm in ARMS:
                selected = [
                    row for row in workers
                    if row.get("task") == task
                    and row.get("regime") == regime
                    and row.get("arm") == arm
                ]
                if len(selected) != 18:
                    raise RuntimeError(f"cell worker count differs: {task}/{regime}/{arm}")
                values = [row.get("metric_ns") for row in selected]
                cell_rows.append({
                    "task": task,
                    "regime": regime,
                    "arm": arm,
                    "worker_count": len(selected),
                    "metric_median_ns": median_ns(values),
                    "metric_min_ns": min(values),
                    "metric_max_ns": max(values),
                    "interpretation": (
                        "DESCRIPTIVE_ABSOLUTE_MEDIAN__REGISTERED_INFERENCE_USES_"
                        "PAIRED_BLOCK_RATIOS"
                    ),
                })
                if arm == "DIRECT":
                    phase_names = set(selected[0]["raw_result"]["phase_durations_ns"])
                    if any(set(row["raw_result"]["phase_durations_ns"]) != phase_names
                           for row in selected):
                        raise RuntimeError("Direct phase universe differs")
                    direct_phase_rows.append({
                        "task": task,
                        "regime": regime,
                        "worker_count": len(selected),
                        "phase_medians_ns": {
                            name: median_nonnegative_ns([
                                row["raw_result"]["phase_durations_ns"][name]
                                for row in selected
                            ])
                            for name in sorted(phase_names)
                        },
                        "interpretation": (
                            "DESCRIPTIVE_DIRECT_IMPLEMENTATION_PHASES__NOT_A_"
                            "CAUSAL_DECOMPOSITION_OF_RTLD_OR_PYOPTIX"
                        ),
                    })

    registered_rows = evaluation["rows"]
    gated = [row for row in registered_rows if row["threshold"] is not None]
    if len(registered_rows) != 18 or len(gated) != 6:
        raise RuntimeError("registered row universe differs")
    pass_map = {(row["task"], row["regime"]): row["pass"] for row in gated}
    expected_pass_map = {
        (task, regime): regime == "STEADY_E2E"
        for task in TASKS for regime in REGIMES
    }
    if pass_map != expected_pass_map:
        raise RuntimeError("registered pass/fail pattern differs")

    prior_rows = prior["goal5805"]["formal"]["rows"]
    prior_pass_map = {
        (row["task"], row["regime"].replace("_POST_IMPORT", "")): row["pass"]
        for row in prior_rows
    }
    if prior_pass_map != expected_pass_map:
        raise RuntimeError("prior Goal5805 pass/fail pattern differs")

    result = {
        "schema": "rtdl.goal5817.three_arm_formal_closeout.v1",
        "date": "2026-08-29",
        "status": "COMPLETE__TWO_OF_SIX_RTDL_OVER_PYOPTIX_GATES__CURRENT_SOURCE_DIRECT_PRESENT",
        "source_and_custody": {
            "scientific_freeze": str(args.freeze),
            "scientific_freeze_file_sha256": sha256(args.freeze),
            "scientific_freeze_internal_sha256": freeze.get("freeze_sha256"),
            "formal_execution_authority": str(args.authority),
            "formal_execution_authority_file_sha256": sha256(args.authority),
            "target_manifest": str(args.target_manifest),
            "target_manifest_file_sha256": sha256(args.target_manifest),
            "controller_file_sha256": sha256(args.controller),
            "published_evaluation_file_sha256": sha256(args.evaluation),
            "independent_raw_recount_file_sha256": sha256(args.independent_recount),
            "independent_raw_recount_internal_sha256": recount.get("receipt_sha256"),
            "evidence_archive": str(args.evidence_archive),
            "evidence_archive_bytes": args.evidence_archive.stat().st_size,
            "evidence_archive_sha256": sha256(args.evidence_archive),
        },
        "target": {
            "gpu_name": target_observation["gpu_name"],
            "compute_capability": target_observation["compute_capability"],
            "driver_version": target_observation["driver_version"],
            "python_version": target_observation["python_version"],
            "cuda_toolchain": target_observation["nvcc_version"],
            "target_observation_file_sha256": sha256(args.target_observation),
            "provider_endpoint_in_scientific_claim": False,
        },
        "formal": {
            "worker_count": 324,
            "unique_pid_count": recount["unique_pid_count"],
            "empty_stderr_count": recount["empty_stderr_count"],
            "registered_performance_timing_count": 7_128,
            "row_count": 18,
            "gated_row_count": 6,
            "gated_pass_count": 2,
            "retry_replacement_row_drop_count": 0,
            "ratio_orientation": "numerator/denominator; lower favors numerator",
            "registered_rows": registered_rows,
            "descriptive_cell_medians": cell_rows,
            "descriptive_direct_phase_medians": direct_phase_rows,
        },
        "replication_check": {
            "prior_result": str(args.prior_result),
            "prior_result_sha256": sha256(args.prior_result),
            "prior_goal5805_gated_pass_count": 2,
            "goal5817_gated_pass_count": 2,
            "same_pass_fail_pattern": True,
            "interpretation": (
                "The independent successor reproduces the two steady passes and four "
                "cold/prepare failures. It adds a current-source same-target Direct arm; "
                "it does not pool prior timings."
            ),
        },
        "validated_findings": [
            "RTDL steady E2E is within the registered 5% margin relative to matched PyOptiX on both measured tasks.",
            "RTDL deployment-cold and prepare exceed the registered 10% margin relative to matched PyOptiX on both measured tasks.",
            "Current-source same-target Direct comparisons are available descriptively for all six task/regime cells.",
            "The two-of-six gate pattern independently reproduces Goal5805 without reusing any Goal5805 timing value.",
        ],
        "causal_limits": [
            "Goal5817 does not isolate checker cost from the rest of RTDL preparation; it measures complete arm boundaries.",
            "PyOptiX being faster than Direct during preparation is an implementation observation, not evidence that Python is intrinsically faster than C++ or raw OptiX.",
            "Direct steady comparisons include implementation and host-path differences and are descriptive, not universal lower bounds.",
            "Two authored tasks on one RTX target do not establish cross-application or cross-target performance generality.",
        ],
        "claim_ceiling": {
            "allowed": [
                "on two measured authored tasks and this RTX target, RTDL steady E2E is within 5% of matched PyOptiX",
                "on the same tasks and target, RTDL cold and prepare fail the registered 10% PyOptiX margin",
                "same-target current-source Direct comparisons are reported as descriptive decomposition",
                "the performance result independently reproduces the earlier two-steady-pass/four-lifecycle-fail pattern",
            ],
            "forbidden": [
                "RTDL has zero lifecycle overhead relative to PyOptiX",
                "RTDL cold or prepare is within 10% of PyOptiX",
                "the measured preparation gap is wholly caused by protocol checking",
                "RTDL matches or beats Direct CUDA/OptiX universally",
                "cross-application, cross-target, usability, productivity, or prospective-generalization claims",
            ],
        },
    }
    result["result_sha256"] = hashlib.sha256(canonical(result)).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(json.dumps(
        result, indent=2, allow_nan=False, sort_keys=True,
    ).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": result["status"],
        "result_sha256": result["result_sha256"],
        "output_file_sha256": sha256(output),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

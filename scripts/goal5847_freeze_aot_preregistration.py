#!/usr/bin/env python3
"""Freeze Goal5847's AOT comparison design before formal GPU timing."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

from experiments.goal5798_premeasurement.workload import relation_workload
from experiments.goal5844_compact_execution.provenance import (
    validate_pyoptix_build_receipt,
)
from experiments.goal5847_aot_startup.contracts import (
    PYOPTIX_ARM,
    PYOPTIX_COMMIT,
    PYOPTIX_TREE,
    RELATION_TASK,
    RTDL_ARM,
    digest,
)
from scripts.goal5847_run_aot_startup_comparison import (
    BLOCKS,
    POST_IMPORT_MEDIAN_RATIO_LIMIT,
    POST_IMPORT_WORST_RATIO_LIMIT,
    PRIMARY_MEDIAN_RATIO_LIMIT,
    PRIMARY_WORST_RATIO_LIMIT,
    REPETITIONS,
    RTDL_STEADY_REFERENCE_NS,
    RTDL_STEADY_REGRESSION_LIMIT,
    STEADY_RATIO_LIMIT,
    WARMUPS,
)

ROOT = Path(__file__).resolve().parents[1]


def _sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def _git_at(path: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(path), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _load_sealed(path: Path, field: str) -> dict[str, object]:
    value = json.loads(path.resolve(strict=True).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Goal5847 object required: {path}")
    body = dict(value)
    observed = body.pop(field, None)
    if observed != digest(body):
        raise RuntimeError(f"Goal5847 seal differs: {path}")
    return value


def _write_create(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            descriptor = -1
            stream.write(
                json.dumps(value, indent=2, sort_keys=True).encode("utf-8")
                + b"\n"
            )
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--implementation-source-commit", required=True)
    parser.add_argument("--candidate-manifest", type=Path, required=True)
    parser.add_argument("--precompiled-ptx", type=Path, required=True)
    parser.add_argument("--pyoptix-source", type=Path, required=True)
    parser.add_argument("--pyoptix-build-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source_commit = _git_at(ROOT, "rev-parse", "HEAD")
    source_tree = _git_at(ROOT, "rev-parse", "HEAD^{tree}")
    if source_commit != args.implementation_source_commit \
            or _git_at(ROOT, "status", "--porcelain=v1", "--untracked-files=all"):
        raise RuntimeError("Goal5847 preregistration requires clean implementation commit")
    pyoptix = args.pyoptix_source.resolve(strict=True)
    if _git_at(pyoptix, "rev-parse", "HEAD") != PYOPTIX_COMMIT \
            or _git_at(pyoptix, "rev-parse", "HEAD^{tree}") != PYOPTIX_TREE \
            or _git_at(pyoptix, "status", "--porcelain=v1", "--untracked-files=all"):
        raise RuntimeError("Goal5847 PyOptix identity differs")
    candidate_path = args.candidate_manifest.resolve(strict=True)
    candidate = _load_sealed(candidate_path, "manifest_sha256")
    if candidate.get("source_commit") != source_commit:
        raise RuntimeError("Goal5847 candidate implementation commit differs")
    rows = candidate.get("rows")
    if not isinstance(rows, dict) or set(rows) != {"relation", "triangle"}:
        raise RuntimeError("Goal5847 candidate families differ")
    receipt_path = args.pyoptix_build_receipt.resolve(strict=True)
    receipt = validate_pyoptix_build_receipt(receipt_path)
    workload = relation_workload()
    expected = tuple(tuple(row) for row in workload["expected_rows"])
    result: dict[str, object] = {
        "schema": "rtdl.goal5847.aot_startup_preregistration.v1",
        "status": "FROZEN_BEFORE_FORMAL_GPU_TRANSACTION",
        "implementation_source_commit": source_commit,
        "implementation_source_tree": source_tree,
        "question": (
            "Can one signed, family-bound deploy-only RTDL artifact reach the "
            "same result as a pinned precompiled-PTX PyOptix program without "
            "loading or invoking NVRTC, while preserving true OptiX evidence, "
            "fail-closed admission, and Goal5845 steady performance?"
        ),
        "task": {
            "id": RELATION_TASK,
            "indexed_count": 4096,
            "query_count": 4096,
            "canonical_row_count": 4096,
            "input_sha256": digest({
                "indexed": workload["indexed"],
                "sources": workload["sources"],
                "minimum_overlap": workload["minimum_overlap"],
                "capacity": workload["capacity"],
            }),
            "output_sha256": digest(expected),
            "output_contract": "canonical_u32_relation_rows",
        },
        "arms": [RTDL_ARM, PYOPTIX_ARM],
        "design": {
            "blocks": BLOCKS,
            "balanced_alternating_order": True,
            "fresh_process_per_arm_per_block": True,
            "warmups_per_worker": WARMUPS,
            "samples_per_worker": REPETITIONS,
            "samples_per_arm": BLOCKS * REPETITIONS,
            "sample_discard_count": 0,
            "primary_estimand": "parent_pre_spawn_to_first_correct_result_ns",
            "secondary_estimand": (
                "implementation_import_end_to_first_correct_result_ns"
            ),
            "steady_estimand": "complete_same_contract_execution_ns",
        },
        "pass_gates": {
            "all_workers_and_exact_oracles_pass": True,
            "all_registered_samples_retained": True,
            "primary_median_within_block_ratio_at_most": (
                PRIMARY_MEDIAN_RATIO_LIMIT
            ),
            "primary_worst_block_ratio_at_most": PRIMARY_WORST_RATIO_LIMIT,
            "post_import_median_within_block_ratio_at_most": (
                POST_IMPORT_MEDIAN_RATIO_LIMIT
            ),
            "post_import_worst_block_ratio_at_most": (
                POST_IMPORT_WORST_RATIO_LIMIT
            ),
            "pooled_steady_rtdl_to_pyoptix_ratio_at_most": STEADY_RATIO_LIMIT,
            "goal5845_rtdl_steady_reference_ns": RTDL_STEADY_REFERENCE_NS,
            "pooled_rtdl_steady_regression_at_most": (
                RTDL_STEADY_REGRESSION_LIMIT
            ),
        },
        "frozen_bindings": {
            "candidate_manifest_sha256": _sha256_file(candidate_path),
            "candidate_manifest_seal": candidate["manifest_sha256"],
            "native_library_sha256": candidate["native_sha256"],
            "relation_artifact_sha256": rows["relation"]["artifact_sha256"],
            "triangle_artifact_sha256": rows["triangle"]["artifact_sha256"],
            "precompiled_ptx_sha256": _sha256_file(
                args.precompiled_ptx.resolve(strict=True)
            ),
            "pyoptix_commit": PYOPTIX_COMMIT,
            "pyoptix_tree": PYOPTIX_TREE,
            "pyoptix_build_receipt_sha256": _sha256_file(receipt_path),
            "pyoptix_build_receipt_internal_seal": receipt["receipt_sha256"],
        },
        "required_rtdl_facts": {
            "runtime_compiler_attempt_count_before_and_after_zero": True,
            "nvrtc_mapping_absent": True,
            "compiler_modules_absent": True,
            "actual_optix_launch_count_per_execution": 2,
            "full_generic_family_identity_match": True,
            "exact_output_required": True,
            "application_specific_native_logic_added": False,
            "prepared_steady_regression_forbidden": True,
            "optional_batch_oracle_disabled_in_timed_path": True,
            "diagnostic_execution_occurs_after_steady_samples": True,
        },
        "comparison_boundary": {
            "both_arms_consume_precompiled_device_programs": True,
            "rtdl_arm_verifies_signed_artifact_authority_and_provider": True,
            "pyoptix_validation_mode": "OFF",
            "pyoptix_harness_calls_source_compiler": False,
            "pyoptix_dependency_stack_may_map_nvrtc": True,
            "primary_includes_interpreter_and_dependency_import": True,
            "secondary_excludes_implementation_import": True,
            "git_and_hardware_instrumentation_excluded_from_primary": True,
            "exact_result_validation_included_in_primary_endpoint": True,
            "steady_result_validation_outside_timed_action_for_both_arms": True,
            "storage_page_cache_state_not_controlled": True,
            "block_device_cold_io_claimed": False,
            "test_only_signing_not_production_key_custody": True,
        },
        "prior_exploration": {
            "disclosed": True,
            "pooled_into_formal_transaction": False,
            "used_to_select_metrics_or_thresholds": True,
            "reason": (
                "Exploration established that complete process startup and "
                "post-import setup answer different reviewer attacks; both are "
                "therefore frozen, and neither may be omitted."
            ),
        },
        "claim_boundary": {
            "internal_engineering_evidence_only": True,
            "public_or_manuscript_claim_authorized": False,
            "external_review_complete": False,
            "cross_hardware_generalization_authorized": False,
            "arbitrary_workload_claim_authorized": False,
            "production_signing_claim_authorized": False,
        },
    }
    result["preregistration_sha256"] = digest(result)
    _write_create(args.output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

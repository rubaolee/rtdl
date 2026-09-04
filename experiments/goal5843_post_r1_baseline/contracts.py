"""Standard-library-only contracts for the Goal5843 formal baseline."""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


PREREGISTRATION_SCHEMA = "rtdl.goal5843.post_r1_baseline_preregistration.v4"
EXECUTION_AUTHORITY_SCHEMA = "rtdl.goal5843.execution_authority.v1"
CACHE_PREPARATION_SCHEMA = "rtdl.goal5843.formal_leaf_cache_preparation.v1"
ORACLE_WITNESS_SCHEMA = "rtdl.goal5843.independent_oracle_witness.v1"
BOUND_ARTIFACTS_SCHEMA = "rtdl.goal5843.bound_artifacts_custody.v1"
SUBWORKER_SCHEMA = "rtdl.goal5843.baseline_subworker.v1"
CONTROLLER_SCHEMA = "rtdl.goal5843.baseline_controller.v1"
RECOUNT_SCHEMA = "rtdl.goal5843.independent_recount.v1"
FINAL_AUTHORITY_SCHEMA = "rtdl.goal5843.final_internal_authority.v1"

RELATION_TASK = "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1"
TRIANGLE_TASK = "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1"
TASKS = (RELATION_TASK, TRIANGLE_TASK)

DIRECT_ARM = "A_DIRECT_CUDA_OPTIX"
PYOPTIX_ARM = "B_CURRENT_NVIDIA_PYOPTIX_COMPATIBLE_API"
RTDL_ARM = "D_RTDL_PUBLIC_CHECK_ON_POST_R1"
ARMS = (DIRECT_ARM, PYOPTIX_ARM, RTDL_ARM)

FIRST_MODE = "FIRST_COMPLETE_EXECUTION"
STEADY_MODE = "STEADY_COMPLETE_EXECUTION"
MODES = (FIRST_MODE, STEADY_MODE)
BLOCKS = 18
STEADY_WARMUPS = 8
STEADY_REPETITIONS = 64
BOOTSTRAP_DRAWS = 10_000
BOOTSTRAP_LOWER_INDEX = 249
BOOTSTRAP_UPPER_INDEX = 9_749
BOOTSTRAP_SEED_BASE = 58_430_000

PERMUTATIONS = (
    (DIRECT_ARM, PYOPTIX_ARM, RTDL_ARM),
    (DIRECT_ARM, RTDL_ARM, PYOPTIX_ARM),
    (PYOPTIX_ARM, DIRECT_ARM, RTDL_ARM),
    (PYOPTIX_ARM, RTDL_ARM, DIRECT_ARM),
    (RTDL_ARM, DIRECT_ARM, PYOPTIX_ARM),
    (RTDL_ARM, PYOPTIX_ARM, DIRECT_ARM),
)

PHASE_KEYS = (
    "deterministic_input_materialization",
    "route_declaration_and_artifact_binding",
    "provider_projection_and_generic_family_admission",
    "runtime_target_and_toolchain_binding",
    "device_compile",
    "module_program_pipeline_sbt",
    "target_materialization",
    "native_prepare",
    "first_complete_execution",
    "steady_complete_execution",
    "close",
)

TASK_CONTRACTS = (
    {
        "task": RELATION_TASK,
        "role": "ADVERSE_ROW_RETURNING_NEGATIVE_CONTROL",
        "input_sha256": "8606dd3c22d424a7ee2d64b61918f6185d39d8090d1a0a64001de65054d25e0e",
        "full_oracle_sha256": "2fb668490480cbb5d4d9bbf5a8d357435eff5fc6bb3532427ac2726cdaa88c77",
        "public_output_sha256": "2fb668490480cbb5d4d9bbf5a8d357435eff5fc6bb3532427ac2726cdaa88c77",
        "public_output_contract_id": "canonical_relation_rows.v1",
        "public_output_scope": "FULL_CANONICAL_RELATION_ROWS",
        "primitive_count": 4_096,
        "query_count": 4_096,
    },
    {
        "task": TRIANGLE_TASK,
        "role": "PRIMARY_POST_R1_SCALAR_ESTIMAND",
        "input_sha256": "d994f80418995342d0faa4bda84b42c2ef3604b2798de413a2813dd28dc039a7",
        "full_oracle_sha256": "24f4651b65f2abc93ffae0a8a9603c6eff9e9c6acdc24b65fb20937d6f416d93",
        "public_output_sha256": "2df49102543561c678ce39e05cc6c79ce92c0ea919ad45134d53d19bb67174ef",
        "public_output_contract_id": "checked_u64_weighted_scalar.v1",
        "public_output_scope": "CHECKED_U64_WEIGHTED_SCALAR_ONLY",
        "primitive_count": 16_384,
        "query_count": 16_384,
    },
)

EVIDENCE_DIRECTORY = (
    "history/internal_docs/goal5843_post_r1_fair_baseline_20260904"
)
PREREGISTRATION_PATH = f"{EVIDENCE_DIRECTORY}/PREREGISTRATION.json"

REQUIRED_SOURCE_PATHS = (
    "experiments/goal5798_premeasurement/direct_measurement.cpp",
    "experiments/goal5798_premeasurement/build_direct_measurement.sh",
    "experiments/goal5798_premeasurement/pyoptix_worker.py",
    "experiments/goal5798_premeasurement/workload.py",
    "experiments/goal5796_matched/matched_device.cu",
    "experiments/goal5796_matched/pyoptix_baseline.py",
    "experiments/goal5796_matched/independent_oracle.py",
    "experiments/goal5842_causal_admission/baseline_worker.py",
    "experiments/goal5842_causal_admission/tasks.py",
    "experiments/goal5843_post_r1_baseline/__init__.py",
    "experiments/goal5843_post_r1_baseline/contracts.py",
    "experiments/goal5843_post_r1_baseline/runtime.py",
    "experiments/goal5843_post_r1_baseline/worker.py",
    "experiments/goal5843_post_r1_baseline/controller.py",
    "scripts/goal5843_build_preregistration.py",
    "scripts/goal5843_prepare_formal_leaf_cache.py",
    "scripts/goal5843_build_independent_oracle_witness.py",
    "scripts/goal5843_bind_execution_authority.py",
    "scripts/goal5843_preserve_bound_artifacts.py",
    "scripts/goal5843_run_transaction.py",
    "scripts/goal5843_independent_recount.py",
    "scripts/goal5843_verify_downloaded_archive.py",
    "scripts/goal5843_build_final_authority.py",
    "src/rtdsl/v4.py",
    "src/rtdsl/v4_callback_lifecycle.py",
    "src/rtdsl/v4_callback_numba_codegen.py",
    "src/rtdsl/v4_bounded_relation_optix_compiler.py",
    "src/rtdsl/v4_bounded_relation_prepared_runtime.py",
    "src/rtdsl/v4_family_route_adapters.py",
    "src/rtdsl/v4_triangle_reduction_optix_compiler.py",
    "src/rtdsl/v4_triangle_reduction_prepared_runtime.py",
    "src/rtdsl/v4_triangle_standard_library.py",
    "src/rtdsl/v4_family_schema.py",
    "src/rtdsl/v4_generic_family_lifecycle.py",
    "src/rtdsl/v4_family.py",
    "tests/goal5843_post_r1_baseline_test.py",
    f"{EVIDENCE_DIRECTORY}/DESIGN.md",
    f"{EVIDENCE_DIRECTORY}/PRE_EXECUTION_INTERNAL_HOSTILE_SELF_REVIEW.md",
    f"{EVIDENCE_DIRECTORY}/PRE_WORKER_ZERO_REPAIR_01.md",
    f"{EVIDENCE_DIRECTORY}/PRE_WORKER_ZERO_REPAIR_02.md",
    f"{EVIDENCE_DIRECTORY}/PREREGISTRATION_V3.json",
    (
        f"{EVIDENCE_DIRECTORY}/"
        "POST_WORKER_ZERO_V3_TERMINAL_ARCHIVE_VERIFIER_FAILURE.md"
    ),
    "history/internal_docs/goal5842_causal_admission_cost_20260903/PREREGISTRATION_V12.json",
    "history/internal_docs/goal5842_causal_admission_cost_20260903/GOAL5842_FINAL_INTERNAL_AUTHORITY.json",
    "history/internal_docs/goal5842r1_public_reuse_scalar_fastpath_20260903/GOAL5842R1_INTERNAL_AUTHORITY.json",
)


class Goal5843ContractError(ValueError):
    pass


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def pin_file(root: Path, relative: str) -> dict[str, object]:
    path = (root / relative).resolve(strict=True)
    if not path.is_file() or not path.is_relative_to(root.resolve()):
        raise Goal5843ContractError(f"invalid source pin: {relative}")
    return {
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def verify_pin(root: Path, row: Mapping[str, object]) -> None:
    if set(row) != {"path", "bytes", "sha256"}:
        raise Goal5843ContractError("source pin field set mismatch")
    relative = row["path"]
    if not isinstance(relative, str):
        raise Goal5843ContractError("source pin path must be text")
    observed = pin_file(root, relative)
    if observed != dict(row):
        raise Goal5843ContractError(f"source pin drift: {relative}")


def build_schedule() -> list[dict[str, object]]:
    schedule: list[dict[str, object]] = []
    counts: defaultdict[tuple[str, str], int] = defaultdict(int)
    sequence = 0
    for block in range(BLOCKS):
        task_order = TASKS if block % 2 == 0 else tuple(reversed(TASKS))
        for task_position, task in enumerate(task_order):
            permutation_index = (block + 2 * TASKS.index(task)) % len(PERMUTATIONS)
            for arm_position, arm in enumerate(PERMUTATIONS[permutation_index]):
                key = (task, arm)
                sample_index = counts[key]
                counts[key] += 1
                schedule.append(
                    {
                        "sequence_index": sequence,
                        "block": block,
                        "task": task,
                        "task_position": task_position,
                        "arm": arm,
                        "arm_position": arm_position,
                        "permutation_index": permutation_index,
                        "arm_sample_index": sample_index,
                        "worker_id": (
                            f"G5843_B{sequence:03d}__K{block:02d}__{task}__{arm}"
                        ),
                    }
                )
                sequence += 1
    return schedule


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise Goal5843ContractError(message)


def validate_schedule(schedule: object) -> None:
    _require(isinstance(schedule, list), "schedule must be a list")
    _require(len(schedule) == BLOCKS * len(TASKS) * len(ARMS), "schedule size")
    _require(
        [row.get("sequence_index") for row in schedule] == list(range(len(schedule))),
        "schedule sequence",
    )
    _require(len({row.get("worker_id") for row in schedule}) == len(schedule), "worker ids")
    pairs = Counter((row.get("task"), row.get("arm")) for row in schedule)
    _require(
        pairs == Counter({(task, arm): BLOCKS for task in TASKS for arm in ARMS}),
        "task/arm balance",
    )
    for block in range(BLOCKS):
        rows = [row for row in schedule if row.get("block") == block]
        _require(len(rows) == len(TASKS) * len(ARMS), "block size")
        for task in TASKS:
            task_rows = [row for row in rows if row.get("task") == task]
            _require(
                Counter(row.get("arm") for row in task_rows) == Counter(ARMS),
                "block arm balance",
            )
            _require(
                len({row.get("permutation_index") for row in task_rows}) == 1,
                "block permutation",
            )


def build_preregistration(root: Path) -> dict[str, object]:
    manifest = [pin_file(root, path) for path in REQUIRED_SOURCE_PATHS]
    result: dict[str, object] = {
        "schema": PREREGISTRATION_SCHEMA,
        "status": "FROZEN_BEFORE_GOAL5843_WORKER_ZERO",
        "purpose": (
            "fresh fair post-Goal5842R1 Direct CUDA/OptiX versus pinned "
            "PyOptiX-compatible versus ordinary public check-on RTDL baseline"
        ),
        "predecessors": {
            "goal5842_v12_authority_sha256": (
                "5c8044d9204df6b5d622142aecab8fcd25990e2ca1a19c7c5055ef4e16a31e43"
            ),
            "goal5842r1_authority_sha256": (
                "7897058f51dedc3b6b5c652b5c3d69418610919557f9ee9a9c70214a5f184248"
            ),
            "prior_timing_rows_pooled": False,
        },
        "pre_worker_zero_repairs": [
            {
                "repair_id": "PRE_WORKER_ZERO_REPAIR_01",
                "superseded_source_commit": (
                    "bc03f357ff1331b6b3edeb58ba33fab19445d258"
                ),
                "superseded_preregistration_sha256": (
                    "30857d8f7fe16ab3408c45be0e20123bb5d377400bbf09829ab9a099de0f2b00"
                ),
                "superseded_source_manifest_sha256": (
                    "e7d08869792913cd9b9b7a42ea29e95020575de9a0bf9bbb6b533fd3acbfed81"
                ),
                "formal_worker_zero_reached": False,
                "formal_timing_samples_recorded": 0,
                "repair_scope": (
                    "Goal5843 worker-only generic lifecycle receipt unwrapping "
                    "and generic public-result validation"
                ),
                "frozen_goal5838_core_changed": False,
            },
            {
                "repair_id": "PRE_WORKER_ZERO_REPAIR_02",
                "superseded_source_commit": (
                    "d5d77b0ad0b1121da12d700af28cefc7535b63f3"
                ),
                "superseded_preregistration_sha256": (
                    "a492b381904390c0fd05c607f33a0febfca04673a272f62fb782802b27dd2b1a"
                ),
                "superseded_source_manifest_sha256": (
                    "a5d31edd63d6ff0e0fd90cf3bbf22eaa2e4f0ba879675da72efb864ed624dd08"
                ),
                "formal_worker_zero_reached": False,
                "formal_timing_samples_recorded": 0,
                "repair_scope": (
                    "Goal5843 relation-control evidence selection from the "
                    "generic traversal receipt when no provider extension exists"
                ),
                "frozen_goal5838_core_changed": False,
            },
        ],
        "superseded_formal_transactions": [
            {
                "transaction_id": "GOAL5843_V3",
                "terminal_status": (
                    "TERMINAL__V3_POST_DOWNLOAD_ARCHIVE_VERIFIER_MODE_"
                    "NORMALIZATION_DEFECT__NO_RETRY"
                ),
                "source_commit": "ec4c9375833957f82149d165039aa3202dd791c6",
                "preregistration_sha256": (
                    "90c0e00f372df6fb9ba2985c80b43fe17b3ad00be60471f8f67d398ba1dc6b9a"
                ),
                "preregistration_file_sha256": (
                    "af04ea3df90b00e2639d24d9d2ec9bee30aa21f98b7cbda9183050191c2182eb"
                ),
                "source_manifest_sha256": (
                    "f2fbb9c0dbbddac69f423defe1cd38cbbb80db85761732394e6deb9612df7e6c"
                ),
                "execution_authority_sha256": (
                    "3a7bbc3fb4729ea0825afec4b9f69d306e01894bcc6fd0293fc4ee4ba5c7c0f2"
                ),
                "controller_result_sha256": (
                    "be8c147a646f960cae257db344f45643879ee97d595818d7a22aa5dbd8eafc85"
                ),
                "pod_recount_sha256": (
                    "1dd53706d5058d1d5156926ff53a88405b445c0105fd80b43282c8be22ddec69"
                ),
                "archive_sha256": (
                    "bf24cc9954e9f6970ea58ff6584f79bf1de32b2e5118003a06723cb8ba61f118"
                ),
                "formal_worker_zero_reached": True,
                "formal_composite_count": 108,
                "formal_subworker_receipt_count": 216,
                "formal_timing_samples_recorded": 7_020,
                "all_pod_stages_returned_zero": True,
                "post_worker_zero_retry_used": False,
                "rows_eligible_for_successor_pooling": False,
                "downloaded_archive_verification_complete": False,
                "failure_scope": (
                    "pinned local verifier compared tarfile-data-filtered modes "
                    "against original custody modes"
                ),
                "frozen_goal5838_core_changed": False,
            }
        ],
        "task_contracts": list(TASK_CONTRACTS),
        "arms": list(ARMS),
        "schedule": build_schedule(),
        "sampling": {
            "blocks": BLOCKS,
            "first_fresh_subworker_repetitions": 1,
            "steady_fresh_subworker_warmups": STEADY_WARMUPS,
            "steady_fresh_subworker_repetitions": STEADY_REPETITIONS,
            "subworker_retry_permitted": False,
            "all_adverse_rows_retained": True,
        },
        "phase_contract": {
            "phases": list(PHASE_KEYS),
            "setup_total_components": [
                "route_declaration_and_artifact_binding",
                "provider_projection_and_generic_family_admission",
                "runtime_target_and_toolchain_binding",
                "target_materialization",
                "native_prepare",
            ],
            "complete_execution_includes": [
                "output_reset",
                "launch_parameter_update",
                "provider_required_optix_launches",
                "required_public_output_transfer",
                "public_status_check",
                "gpu_completion_before_timer_stop",
            ],
            "oracle_comparison_outside_timed_interval": True,
            "process_startup_excluded_from_all_provider_phase_estimands": True,
            "provider_specific_setup_reported_descriptively_not_as_equivalent_work": True,
            "first_execution_query_upload_phase_differs_by_provider_and_is_descriptive_only": True,
        },
        "estimands": {
            "primary": {
                "task": TRIANGLE_TASK,
                "metric": "steady_complete_execution_median_ns",
                "ratios": ["RTDL/DIRECT", "RTDL/PYOPTIX"],
                "aggregation": "median_of_18_within_block_ratios",
            },
            "secondary": [
                "triangle first complete execution and descriptive setup phases",
                "relation first/steady complete execution and descriptive setup phases",
            ],
            "bootstrap": {
                "draws": BOOTSTRAP_DRAWS,
                "seed_base": BOOTSTRAP_SEED_BASE,
                "lower_order_index": BOOTSTRAP_LOWER_INDEX,
                "upper_order_index": BOOTSTRAP_UPPER_INDEX,
            },
            "registered_performance_success_threshold": None,
        },
        "fairness": {
            "same_deterministic_input_digest_per_task": True,
            "same_public_output_digest_per_task": True,
            "same_gpu_and_fresh_process_subworker_policy": True,
            "prepared_query_and_static_target_reuse_for_steady": True,
            "all_provider_execute_durations_wait_for_required_output": True,
            "triangle_all_arms_use_one_optix_launch_per_complete_execution": True,
            "relation_provider_launch_counts_may_differ_and_are_reported": True,
            "rtdl_uses_public_check_on_front_door": True,
            "rtdl_private_checker_off_forbidden": True,
            "rtdl_formal_leaf_cache_created_before_worker_zero_and_read_only_during_workers": True,
            "direct_transport_schema_inherited_from_goal5842_only": True,
            "hidden_implementation_work_not_claimed_identical": True,
        },
        "rtdl_triangle_receipt_gate": {
            "execution_path": "device_resident_checked_u64_scalar_v7",
            "steady_prepared_query_input_reused": True,
            "per_ray_u64_materialized_on_host": False,
            "event_rows_materialized_on_host": False,
            "public_output_scalar_bytes": 8,
            "optix_launch_count": 1,
            "dynamic_accel_build_count": 0,
            "first_dynamic_device_upload_required": True,
            "steady_dynamic_device_upload_call_count": 0,
            "steady_dynamic_device_upload_bytes": 0,
            "control_d2h_bytes": 12,
            "output_d2h_bytes": 8,
            "role_counters_materialized": False,
            "total_auxiliary_cuda_kernel_launch_count": 0,
        },
        "failure_policy": {
            "any_worker_failure_terminates_transaction": True,
            "failed_or_partial_transaction_not_reclassified_as_success": True,
            "post_worker_zero_repair_requires_new_preregistration": True,
            "adverse_performance_is_not_technical_failure": True,
        },
        "oracle_contract": {
            "implementation_imports_forbidden": True,
            "route_independent_structural_rederivation_before_worker_zero": True,
            "witness_bound_into_execution_authority_and_every_subworker": True,
            "relation_method": "prove_disjoint_unit_boxes_and_rederive_all_self_rows",
            "triangle_method": "prove x-axis separation and rederive one hit plus checked-u64 scalar",
        },
        "claim_ceiling": {
            "internal_technical_evidence_only": True,
            "public_performance_claim_authorized": False,
            "manuscript_performance_claim_authorized": False,
            "external_review_or_consensus_complete": False,
            "hardware_independent_claim_authorized": False,
            "general_language_performance_claim_authorized": False,
            "relation_is_scalar_fast_path": False,
            "direct_pyoptix_rtdl_hidden_work_is_identical": False,
        },
        "frozen_core_sha256": {
            "src/rtdsl/v4_family_schema.py": (
                "2d118697d10cb2bc2a8672700ae5a991eaf94e66834bb3e08fd898323720f224"
            ),
            "src/rtdsl/v4_generic_family_lifecycle.py": (
                "7ac68832de9d1e04fdd6f0f11bfa0de7d6109d892ab22e42c9aeb2825d28228c"
            ),
            "src/rtdsl/v4_family.py": (
                "d25c487823e966a8e9083092811c9a1a2b6aa0fef6ce8f3a0a5b8919c5b809e8"
            ),
        },
        "source_manifest": manifest,
        "source_manifest_sha256": digest(manifest),
    }
    result["preregistration_sha256"] = digest(result)
    return result


def validate_preregistration(
    value: object, root: Path, *, verify_files: bool
) -> dict[str, Any]:
    _require(isinstance(value, dict), "preregistration must be an object")
    prereg = dict(value)
    observed = prereg.pop("preregistration_sha256", None)
    _require(
        isinstance(observed, str) and observed == digest(prereg),
        "preregistration seal mismatch",
    )
    prereg["preregistration_sha256"] = observed
    _require(prereg.get("schema") == PREREGISTRATION_SCHEMA, "schema mismatch")
    _require(
        prereg.get("status") == "FROZEN_BEFORE_GOAL5843_WORKER_ZERO",
        "status mismatch",
    )
    _require(prereg.get("arms") == list(ARMS), "arm set mismatch")
    _require(prereg.get("task_contracts") == list(TASK_CONTRACTS), "task contracts")
    repairs = prereg.get("pre_worker_zero_repairs")
    _require(
        isinstance(repairs, list)
        and len(repairs) == 2
        and all(isinstance(row, dict) for row in repairs)
        and [row.get("repair_id") for row in repairs]
        == ["PRE_WORKER_ZERO_REPAIR_01", "PRE_WORKER_ZERO_REPAIR_02"]
        and all(row.get("formal_worker_zero_reached") is False for row in repairs)
        and all(row.get("formal_timing_samples_recorded") == 0 for row in repairs)
        and all(row.get("frozen_goal5838_core_changed") is False for row in repairs),
        "pre-worker-zero repair history mismatch",
    )
    superseded = prereg.get("superseded_formal_transactions")
    _require(
        isinstance(superseded, list)
        and len(superseded) == 1
        and isinstance(superseded[0], dict)
        and superseded[0].get("transaction_id") == "GOAL5843_V3"
        and superseded[0].get("formal_worker_zero_reached") is True
        and superseded[0].get("formal_composite_count") == 108
        and superseded[0].get("formal_subworker_receipt_count") == 216
        and superseded[0].get("formal_timing_samples_recorded") == 7_020
        and superseded[0].get("all_pod_stages_returned_zero") is True
        and superseded[0].get("post_worker_zero_retry_used") is False
        and superseded[0].get("rows_eligible_for_successor_pooling") is False
        and superseded[0].get("downloaded_archive_verification_complete") is False
        and superseded[0].get("frozen_goal5838_core_changed") is False,
        "superseded formal-transaction history mismatch",
    )
    validate_schedule(prereg.get("schedule"))
    sampling = prereg.get("sampling")
    _require(
        isinstance(sampling, dict)
        and sampling.get("blocks") == BLOCKS
        and sampling.get("steady_fresh_subworker_warmups") == STEADY_WARMUPS
        and sampling.get("steady_fresh_subworker_repetitions") == STEADY_REPETITIONS
        and sampling.get("subworker_retry_permitted") is False
        and sampling.get("all_adverse_rows_retained") is True,
        "sampling contract drift",
    )
    estimands = prereg.get("estimands")
    _require(
        isinstance(estimands, dict)
        and estimands.get("registered_performance_success_threshold") is None,
        "performance threshold introduced",
    )
    ceiling = prereg.get("claim_ceiling")
    _require(
        isinstance(ceiling, dict)
        and ceiling.get("public_performance_claim_authorized") is False
        and ceiling.get("manuscript_performance_claim_authorized") is False
        and ceiling.get("external_review_or_consensus_complete") is False,
        "claim ceiling widened",
    )
    pins = prereg.get("source_manifest")
    _require(isinstance(pins, list) and pins, "source manifest missing")
    _require(
        [row.get("path") for row in pins] == list(REQUIRED_SOURCE_PATHS),
        "source manifest path/order drift",
    )
    _require(prereg.get("source_manifest_sha256") == digest(pins), "manifest seal")
    _require(
        prereg == build_preregistration(root),
        "preregistration differs from canonical builder",
    )
    if verify_files:
        for row in pins:
            verify_pin(root, row)
        for path, expected in prereg["frozen_core_sha256"].items():
            _require(sha256_file(root / path) == expected, f"frozen core drift: {path}")
    return prereg


def load_preregistration(path: Path, root: Path, *, verify_files: bool) -> dict[str, Any]:
    return validate_preregistration(
        json.loads(path.read_text(encoding="utf-8")), root, verify_files=verify_files
    )


def task_contract(prereg: Mapping[str, object], task: str) -> dict[str, Any]:
    rows = [dict(row) for row in prereg["task_contracts"] if row["task"] == task]
    if len(rows) != 1:
        raise Goal5843ContractError(f"task contract not unique: {task}")
    return rows[0]


def schedule_row(prereg: Mapping[str, object], worker_id: str) -> dict[str, Any]:
    rows = [dict(row) for row in prereg["schedule"] if row["worker_id"] == worker_id]
    if len(rows) != 1:
        raise Goal5843ContractError(f"schedule worker id not unique: {worker_id}")
    return rows[0]


__all__ = [name for name in globals() if name.isupper()] + [
    "Goal5843ContractError",
    "build_preregistration",
    "build_schedule",
    "canonical_bytes",
    "digest",
    "load_preregistration",
    "pin_file",
    "schedule_row",
    "sha256_file",
    "task_contract",
    "validate_preregistration",
    "validate_schedule",
]

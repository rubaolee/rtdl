"""Pure experiment contract for Goal5842.

This module deliberately imports neither RTDL nor a GPU package.  It owns the
pre-result schedule and validation rules used by the preregistration builder,
workers, controller, and independent recount.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Any

V1_PREREGISTRATION_SCHEMA = "rtdl.goal5842.causal_admission_preregistration.v1"
V1_PREREGISTRATION_PATH = (
    "history/internal_docs/goal5842_causal_admission_cost_20260903/PREREGISTRATION.json"
)
V1_PREREGISTRATION_SHA256 = (
    "6f4cc3123e51d3a1d37193673fb943fca1610ab6536043c3cff774ed4d7f2536"
)
V1_PREREGISTRATION_FILE_SHA256 = (
    "1546e6977e3e7a6bfb43206973e98774af8fa666343c4d5b9f2bf5aa369a397b"
)
V2_PREREGISTRATION_SCHEMA = "rtdl.goal5842.causal_admission_preregistration.v2"
V2_PREREGISTRATION_PATH = (
    "history/internal_docs/goal5842_causal_admission_cost_20260903/"
    "PREREGISTRATION_V2.json"
)
V2_PREREGISTRATION_SHA256 = (
    "d00d569d11b9eea22a0762cb4c8b93e3e1cc156aff7b5eafa51b7619b42d986d"
)
V2_PREREGISTRATION_FILE_SHA256 = (
    "12d2acc7f26632e72552e588254ce319669044571eb6b32866737a9a9c31df6c"
)
V3_PREREGISTRATION_SCHEMA = "rtdl.goal5842.causal_admission_preregistration.v3"
V3_PREREGISTRATION_PATH = (
    "history/internal_docs/goal5842_causal_admission_cost_20260903/"
    "PREREGISTRATION_V3.json"
)
V3_PREREGISTRATION_SHA256 = (
    "aef2f97f917dfa8cd1d639c10bb76e41c1f31f0ba7035b83903a7040547f5b9f"
)
V3_PREREGISTRATION_FILE_SHA256 = (
    "73a9b6c86f4017f4ea9f0ab59eb23923b92d981182295cc81fc1ef1b6533dda0"
)
V4_PREREGISTRATION_SCHEMA = "rtdl.goal5842.causal_admission_preregistration.v4"
V4_PREREGISTRATION_PATH = (
    "history/internal_docs/goal5842_causal_admission_cost_20260903/"
    "PREREGISTRATION_V4.json"
)
V4_PREREGISTRATION_SHA256 = (
    "afdd4094f982285ab8843c578542da24303a1c77d3f877a2e6c5c9f1eda38710"
)
V4_PREREGISTRATION_FILE_SHA256 = (
    "7d66f2f93042786e4f7291d98d7a98ac1d5a00e961997cb4cd2fde58d3988b3a"
)
V5_PREREGISTRATION_SCHEMA = "rtdl.goal5842.causal_admission_preregistration.v5"
V5_PREREGISTRATION_PATH = (
    "history/internal_docs/goal5842_causal_admission_cost_20260903/"
    "PREREGISTRATION_V5.json"
)
V5_PREREGISTRATION_SHA256 = (
    "bcb1980055d608b4b4b7d0242defbfd3f11669aab5a2b6ecc716cb7e669e43cc"
)
V5_PREREGISTRATION_FILE_SHA256 = (
    "f2d6f7039d27b5fbddd0c5636e994669ab1ffdc22c522cb083bcb4ddc444fdf3"
)
V6_PREREGISTRATION_SCHEMA = "rtdl.goal5842.causal_admission_preregistration.v6"
V6_PREREGISTRATION_PATH = (
    "history/internal_docs/goal5842_causal_admission_cost_20260903/"
    "PREREGISTRATION_V6.json"
)
V6_PREREGISTRATION_SHA256 = (
    "214e81ab1a57f23eea06a762f12b07015b8e0052fa27e95c40245598b7f00ad1"
)
V6_PREREGISTRATION_FILE_SHA256 = (
    "b63a755694f6e8973c325171fc7da7970b7abe166d4809d446169d25aa33048f"
)
V7_PREREGISTRATION_SCHEMA = "rtdl.goal5842.causal_admission_preregistration.v7"
V7_PREREGISTRATION_PATH = (
    "history/internal_docs/goal5842_causal_admission_cost_20260903/"
    "PREREGISTRATION_V7.json"
)
V7_PREREGISTRATION_SHA256 = (
    "4eb544b6a61c8c7256bb165baa3cdf1141fededcc043b9f9b5822054788539ee"
)
V7_PREREGISTRATION_FILE_SHA256 = (
    "138e71fa9f4e1c4fd1437c38fcbab5a7356404c4967f810a1285f80c46d37b96"
)
V8_PREREGISTRATION_SCHEMA = "rtdl.goal5842.causal_admission_preregistration.v8"
V8_PREREGISTRATION_PATH = (
    "history/internal_docs/goal5842_causal_admission_cost_20260903/"
    "PREREGISTRATION_V8.json"
)
V8_PREREGISTRATION_SHA256 = (
    "5929d9d1c4fe69961f2c24412cf476c1f3cd4ec8a485b4038b53108ebdcf4017"
)
V8_PREREGISTRATION_FILE_SHA256 = (
    "1116b18b9e54ce942ac513488f2ab3468f775db5472af4615bde263f4a13e325"
)
V9_PREREGISTRATION_SCHEMA = "rtdl.goal5842.causal_admission_preregistration.v9"
V9_PREREGISTRATION_PATH = (
    "history/internal_docs/goal5842_causal_admission_cost_20260903/"
    "PREREGISTRATION_V9.json"
)
V9_PREREGISTRATION_SHA256 = (
    "88543c367920697e6d9e11052c923af2e79e8d373c87aea480e55d9a52c54e28"
)
V9_PREREGISTRATION_FILE_SHA256 = (
    "417ae18b5c249d439d9794bb6bd7a5d0bf890ea7a39203a38b9caa7f0146355a"
)
V10_PREREGISTRATION_SCHEMA = "rtdl.goal5842.causal_admission_preregistration.v10"
V10_PREREGISTRATION_PATH = (
    "history/internal_docs/goal5842_causal_admission_cost_20260903/"
    "PREREGISTRATION_V10.json"
)
V10_PREREGISTRATION_SHA256 = (
    "58ec90e1f9a8ddca789ff4999aaa22f64941edb40b18089e3b86c21820889a53"
)
V10_PREREGISTRATION_FILE_SHA256 = (
    "8b7f2bd1f62a6997ba0dfe4fd6762c07668994b563c5059bd56f0639c5824cf4"
)
V11_PREREGISTRATION_SCHEMA = "rtdl.goal5842.causal_admission_preregistration.v11"
V11_PREREGISTRATION_PATH = (
    "history/internal_docs/goal5842_causal_admission_cost_20260903/"
    "PREREGISTRATION_V11.json"
)
V11_PREREGISTRATION_SHA256 = (
    "6f1012d4c7f06c279426debfdf80ec9f046311f581488621ca4507854e9e1ff1"
)
V11_PREREGISTRATION_FILE_SHA256 = (
    "8290f51d7aabcb9022fd7d7e0582b2872f01b9dd7e93c705a03863f96543bccb"
)
PREREGISTRATION_SCHEMA = "rtdl.goal5842.causal_admission_preregistration.v12"
EXECUTION_AUTHORITY_SCHEMA = "rtdl.goal5842.execution_authority.v1"
WORKER_RECEIPT_SCHEMA = "rtdl.goal5842.causal_admission_worker.v1"
CONTROLLER_RESULT_SCHEMA = "rtdl.goal5842.causal_admission_controller.v1"
BASELINE_SUBWORKER_SCHEMA = "rtdl.goal5842.baseline_subworker.v2"
BASELINE_CONTROLLER_SCHEMA = "rtdl.goal5842.baseline_controller.v2"
GPU_IDENTITY_WITNESS_SCHEMA = "rtdl.goal5842.gpu_identity_witness.v5"
PYOPTIX_IDENTITY_WITNESS_SCHEMA = "rtdl.goal5842.pyoptix_identity_witness.v3"
DIRECT_IDENTITY_WITNESS_SCHEMA = "rtdl.goal5842.direct_identity_witness.v1"
INDEPENDENT_RECOUNT_SCHEMA = "rtdl.goal5842.independent_recount.v7"
CROSS_GENERATION_AUTHORITY_SCHEMA = "rtdl.goal5842.cross_generation_authority.v1"

CHECK_ON = "CHECK_ON_COLD_PUBLIC_ADMISSION"
CHECK_OFF = "CHECK_OFF_COLD_UNCHECKED_CONSTRUCTION"
CAUSAL_ARMS = (CHECK_ON, CHECK_OFF)

RELATION_TASK = "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1"
TRIANGLE_TASK = "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1"
SPHERE_TASK = "BUILTIN_SPHERE_ANY_HIT_COUNT_V1"
ADMISSION_TASKS = (RELATION_TASK, TRIANGLE_TASK, SPHERE_TASK)
BASELINE_TASKS = (RELATION_TASK, TRIANGLE_TASK)

DIRECT_ARM = "A_DIRECT_CUDA_OPTIX"
PYOPTIX_ARM = "B_CURRENT_NVIDIA_PYOPTIX_COMPATIBLE_API"
RTDL_ARM = "D_RTDL_PUBLIC_CHECK_ON"
BASELINE_ARMS = (DIRECT_ARM, PYOPTIX_ARM, RTDL_ARM)

CAUSAL_BLOCKS = 18
BASELINE_BLOCKS = 18
STEADY_WARMUPS = 8
STEADY_REPETITIONS = 64
FIRST_MODE = "FIRST_COMPLETE_EXECUTION"
STEADY_MODE = "STEADY_COMPLETE_EXECUTION"
BOOTSTRAP_DRAWS = 10_000
BOOTSTRAP_LOWER_INDEX = 249
BOOTSTRAP_UPPER_INDEX = 9_749
BOOTSTRAP_SEED_BASE = 58_420_000

ABBA = (CHECK_ON, CHECK_OFF, CHECK_OFF, CHECK_ON)
BAAB = (CHECK_OFF, CHECK_ON, CHECK_ON, CHECK_OFF)
BASELINE_PERMUTATIONS = (
    (DIRECT_ARM, PYOPTIX_ARM, RTDL_ARM),
    (DIRECT_ARM, RTDL_ARM, PYOPTIX_ARM),
    (PYOPTIX_ARM, DIRECT_ARM, RTDL_ARM),
    (PYOPTIX_ARM, RTDL_ARM, DIRECT_ARM),
    (RTDL_ARM, DIRECT_ARM, PYOPTIX_ARM),
    (RTDL_ARM, PYOPTIX_ARM, DIRECT_ARM),
)
CAUSAL_PHASE_BOUNDARIES = (
    "route_declaration_and_artifact_binding",
    "provider_projection_and_public_admission_or_unchecked_construction",
)
BASELINE_PHASE_BOUNDARIES = (
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
        "input_sha256": "8606dd3c22d424a7ee2d64b61918f6185d39d8090d1a0a64001de65054d25e0e",
        "full_oracle_sha256": "2fb668490480cbb5d4d9bbf5a8d357435eff5fc6bb3532427ac2726cdaa88c77",
        "public_output_sha256": "2fb668490480cbb5d4d9bbf5a8d357435eff5fc6bb3532427ac2726cdaa88c77",
        "public_output_contract_id": "canonical_relation_rows.v1",
        "public_output_scope": "FULL_CANONICAL_RELATION_ROWS",
        "auxiliary_full_oracle_required": False,
        "primitive_count": 4_096,
        "query_count": 4_096,
        "three_arm_baseline_included": True,
    },
    {
        "task": TRIANGLE_TASK,
        "input_sha256": "d994f80418995342d0faa4bda84b42c2ef3604b2798de413a2813dd28dc039a7",
        "full_oracle_sha256": "24f4651b65f2abc93ffae0a8a9603c6eff9e9c6acdc24b65fb20937d6f416d93",
        "public_output_sha256": "2df49102543561c678ce39e05cc6c79ce92c0ea919ad45134d53d19bb67174ef",
        "public_output_contract_id": "checked_u64_weighted_scalar.v1",
        "public_output_scope": "CHECKED_U64_WEIGHTED_SCALAR_ONLY",
        "auxiliary_full_oracle_required": True,
        "primitive_count": 16_384,
        "query_count": 16_384,
        "three_arm_baseline_included": True,
    },
    {
        "task": SPHERE_TASK,
        "input_sha256": "7144bd41ce7167b82e5fc5f33b9d12738a6e7d163cd64c615c5d6ef275231053",
        "full_oracle_sha256": "4aa93e65f6282776efbd54f4c9ea892d5b537277db851447f97f59a9d4e55789",
        "public_output_sha256": "4aa93e65f6282776efbd54f4c9ea892d5b537277db851447f97f59a9d4e55789",
        "public_output_contract_id": "per_query_count_vector.v1",
        "public_output_scope": "FULL_PER_QUERY_COUNT_VECTOR",
        "auxiliary_full_oracle_required": False,
        "primitive_count": 1_024,
        "query_count": 1_024,
        "three_arm_baseline_included": False,
    },
)
REQUIRED_SOURCE_PATHS = (
    "experiments/goal5798_premeasurement/direct_measurement.cpp",
    "experiments/goal5798_premeasurement/build_direct_measurement.sh",
    "experiments/goal5798_premeasurement/pyoptix_worker.py",
    "experiments/goal5798_premeasurement/worker_common.py",
    "experiments/goal5798_premeasurement/contract_runtime.py",
    "experiments/goal5798_premeasurement/workload.py",
    "experiments/goal5796_matched/direct_optix.cpp",
    "experiments/goal5796_matched/matched_device.cu",
    "experiments/goal5796_matched/pyoptix_baseline.py",
    "experiments/goal5842_causal_admission/__init__.py",
    "experiments/goal5842_causal_admission/admission_worker.py",
    "experiments/goal5842_causal_admission/baseline_controller.py",
    "experiments/goal5842_causal_admission/baseline_worker.py",
    "experiments/goal5842_causal_admission/controller.py",
    "experiments/goal5842_causal_admission/contracts.py",
    "experiments/goal5842_causal_admission/runtime.py",
    "experiments/goal5842_causal_admission/tasks.py",
    "scripts/goal5842_bind_execution_authority.py",
    "scripts/goal5842_build_cross_generation_authority.py",
    "scripts/goal5842_build_preregistration.py",
    "scripts/goal5842_direct_identity_witness.py",
    "scripts/goal5842_gpu_identity_witness.py",
    "scripts/goal5842_pyoptix_identity_witness.py",
    "scripts/goal5842_independent_recount.py",
    "scripts/goal5842_run_one_generation.py",
    "src/rtdsl/v4_callback_lifecycle.py",
    "src/rtdsl/v4_bounded_relation_prepared_runtime.py",
    "src/rtdsl/v4_family_route_adapters.py",
    "src/rtdsl/v4_family.py",
    "src/rtdsl/v4_family_schema.py",
    "src/rtdsl/v4_generic_family_lifecycle.py",
    "src/rtdsl/v4_sphere_any_hit_count_family_route.py",
    "src/rtdsl/v4_sphere_any_hit_count_prepared_runtime.py",
    "src/rtdsl/v4_triangle_reduction_prepared_runtime.py",
    "tests/goal5842_causal_admission_cost_test.py",
    "tests/goal5842_prepared_cache_commit_test.py",
    "history/internal_docs/goal5842_causal_admission_cost_20260903/DESIGN.md",
    V1_PREREGISTRATION_PATH,
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "PRE_WORKER_ZERO_REPAIR_01.md"
    ),
    V2_PREREGISTRATION_PATH,
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "PRE_WORKER_ZERO_REPAIR_02.md"
    ),
    V3_PREREGISTRATION_PATH,
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "PRE_WORKER_ZERO_REPAIR_03.md"
    ),
    V4_PREREGISTRATION_PATH,
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "FORMAL_TRANSACTION04_FAILURE_AND_REPLICATION_PLAN.md"
    ),
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "pod_artifacts/goal5842_transaction04_failure.tar.gz"
    ),
    V5_PREREGISTRATION_PATH,
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "FORMAL_REPLICATION05_FAILURE_AND_V6_PLAN.md"
    ),
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "PRE_EXECUTION_INTERNAL_HOSTILE_REVIEW_V6.md"
    ),
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "pod_artifacts/goal5842_replication05_failure.tar.gz"
    ),
    V6_PREREGISTRATION_PATH,
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "PRE_WORKER_ZERO_REPAIR_04.md"
    ),
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "PRE_EXECUTION_INTERNAL_HOSTILE_REVIEW_V7.md"
    ),
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "pod_artifacts/goal5842_v6_preworker_failures.tar.gz"
    ),
    V7_PREREGISTRATION_PATH,
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "PRE_WORKER_ZERO_REPAIR_05.md"
    ),
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "PRE_EXECUTION_INTERNAL_HOSTILE_REVIEW_V8.md"
    ),
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "pod_artifacts/goal5842_v7_preworker_failure.tar.gz"
    ),
    V8_PREREGISTRATION_PATH,
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "PRE_WORKER_ZERO_REPAIR_06.md"
    ),
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "PRE_EXECUTION_INTERNAL_HOSTILE_REVIEW_V9.md"
    ),
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "pod_artifacts/goal5842_v8_preworker_failure.tar.gz"
    ),
    V9_PREREGISTRATION_PATH,
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "PRE_WORKER_ZERO_REPAIR_07.md"
    ),
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "PRE_EXECUTION_INTERNAL_HOSTILE_REVIEW_V10.md"
    ),
    V10_PREREGISTRATION_PATH,
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "PRE_WORKER_ZERO_REPAIR_08.md"
    ),
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "PRE_EXECUTION_INTERNAL_HOSTILE_REVIEW_V11.md"
    ),
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "pod_artifacts/goal5842_v10_preworker_failure.tar.gz"
    ),
    V11_PREREGISTRATION_PATH,
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "FORMAL_V11_TERMINAL_RECOUNT_FAILURE_AND_V12_PLAN.md"
    ),
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "PRE_EXECUTION_INTERNAL_HOSTILE_REVIEW_V12.md"
    ),
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "pod_artifacts/goal5842_v11_ada_terminal_failure.tar.gz"
    ),
)


class Goal5842ContractError(ValueError):
    """Raised when preregistered Goal5842 evidence is structurally invalid."""


def v2_preregistration_supersession() -> dict[str, object]:
    """Return the immutable v2-to-v1 pre-worker-zero repair link."""

    return {
        "predecessor_path": V1_PREREGISTRATION_PATH,
        "predecessor_schema": V1_PREREGISTRATION_SCHEMA,
        "predecessor_preregistration_sha256": V1_PREREGISTRATION_SHA256,
        "predecessor_file_sha256": V1_PREREGISTRATION_FILE_SHA256,
        "reason_code": ("PRE_WORKER_ZERO_VENV_LAUNCHER_SYMLINK_RESOLUTION_DEFECT"),
        "failed_stage": "00_bind_execution_authority",
        "worker_zero_reached": False,
        "registered_timing_observation_count": 0,
        "gpu_execution_count": 0,
        "scientific_design_changed": False,
        "schedule_workload_statistics_changed": False,
        "repair_scope": "preserve_validated_virtualenv_python_entrypoint",
    }


def v3_preregistration_supersession() -> dict[str, object]:
    """Return the append-only pre-worker-zero repair chain for v3."""

    return {
        "predecessor_path": V2_PREREGISTRATION_PATH,
        "predecessor_schema": V2_PREREGISTRATION_SCHEMA,
        "predecessor_preregistration_sha256": V2_PREREGISTRATION_SHA256,
        "predecessor_file_sha256": V2_PREREGISTRATION_FILE_SHA256,
        "reason_code": "PRE_WORKER_ZERO_NATIVE_LOADER_BINDING_DEFECT",
        "failed_stage": "01_gpu_identity_witness_no_timing",
        "worker_zero_reached": False,
        "registered_timing_observation_count": 0,
        "gpu_complete_execution_call_count": 4,
        "gpu_call_count_basis": (
            "deterministic control flow completed relation and triangle on/off "
            "before sphere prepare raised"
        ),
        "scientific_design_changed": False,
        "schedule_workload_statistics_changed": False,
        "successful_transaction_repeats_full_witness_before_timing": True,
        "repair_scope": "bind_legacy_native_loader_to_authorized_dso",
    }


def v4_preregistration_supersession() -> dict[str, object]:
    """Return the append-only pre-worker-zero repair chain for v4."""

    return {
        "predecessor_path": V3_PREREGISTRATION_PATH,
        "predecessor_schema": V3_PREREGISTRATION_SCHEMA,
        "predecessor_preregistration_sha256": V3_PREREGISTRATION_SHA256,
        "predecessor_file_sha256": V3_PREREGISTRATION_FILE_SHA256,
        "reason_code": ("PRE_WORKER_ZERO_QUADRATIC_SPHERE_WITNESS_FIXTURE_DEFECT"),
        "failed_stage": "01_gpu_identity_witness_no_timing",
        "worker_zero_reached": False,
        "registered_timing_observation_count": 0,
        "gpu_complete_execution_call_count": 4,
        "cumulative_prior_untimed_gpu_complete_execution_call_count": 8,
        "gpu_call_count_basis": (
            "transaction03 completed relation and triangle CHECK_ON/CHECK_OFF; "
            "sphere CHECK_ON was interrupted in host exact-pair validation "
            "before its native GPU call"
        ),
        "scientific_design_changed": True,
        "schedule_changed": False,
        "workload_changed": True,
        "statistics_changed": False,
        "successful_transaction_repeats_full_witness_before_timing": True,
        "repair_scope": (
            "reduce the witness-only sphere fixture from 16384-square to "
            "1024-square while preserving its route and exact checks"
        ),
    }


def v5_post_failure_replication_provenance() -> dict[str, object]:
    """Bind V5 to the disclosed terminal V4 transaction without superseding it."""

    return {
        "predecessor_path": V4_PREREGISTRATION_PATH,
        "predecessor_schema": V4_PREREGISTRATION_SCHEMA,
        "predecessor_preregistration_sha256": V4_PREREGISTRATION_SHA256,
        "predecessor_file_sha256": V4_PREREGISTRATION_FILE_SHA256,
        "v4_transaction_source_commit": ("c1fe04d76511f5db57ea802e8ba7c305c1a088d3"),
        "v4_transaction_artifact_path": (
            "history/internal_docs/goal5842_causal_admission_cost_20260903/"
            "pod_artifacts/goal5842_transaction04_failure.tar.gz"
        ),
        "v4_transaction_artifact_bytes": 222_439,
        "v4_transaction_artifact_sha256": (
            "d22ccd42bb55c876c5f0e575aa3a50d2110d347b037cd325fb4a0fbf1a22a603"
        ),
        "v4_execution_authority_file_sha256": (
            "3edf3f9c84c66bb7cd13966f22e4a3c3aee2fc67ed49bcf4ba56c15ad101a043"
        ),
        "v4_gpu_identity_witness_file_sha256": (
            "d449a979ab7dad6ab0cc27717b2cd1faf0e8455cab10fd7bb565390da3379945"
        ),
        "v4_causal_result_file_sha256": (
            "828fbe5e63b9692a0bbc59a9fca4869fd4e78e6f2eb1b5e4c89af3155fbc71c1"
        ),
        "v4_failure_marker_file_sha256": (
            "7d2350daed571bbea14c509089a558ee47f9c5ef7e11c483305bdafc90b2e338"
        ),
        "v4_failed_pyoptix_marker_file_sha256": (
            "de6b7d6b34208a8bf5b32c31e3a8003444c76c3b75b49cce0ebf9c5fa81cf021"
        ),
        "v4_failed_pyoptix_stderr_file_sha256": (
            "c6cb5b2fdaad61768e0fb8b032497da3919859dff25529e8a8d97335c970cb99"
        ),
        "v4_worker_zero_reached": True,
        "v4_new_transaction_after_repair_permitted": False,
        "v4_completed_causal_worker_count": 216,
        "v4_completed_baseline_subworker_count": 2,
        "v4_failed_baseline_subworker_count": 1,
        "v4_registered_causal_worker_timing_vector_count": 216,
        "v4_registered_causal_phase_value_count": 432,
        "v4_registered_baseline_subworker_timing_vector_count": 2,
        "v4_registered_baseline_execution_sample_count": 65,
        "v4_unregistered_baseline_warmup_execution_count": 8,
        "v4_untimed_rtdl_identity_complete_execution_call_count": 6,
        "v4_direct_baseline_complete_execution_call_count": 73,
        "pre_v4_untimed_gpu_complete_execution_call_count": 8,
        "failure_code": "PYOPTIX_HISTORICAL_WORKER_PACKAGE_IMPORT_DEFECT",
        "failure_before_pyoptix_clock_or_gpu": True,
        "repair_scope": (
            "conditional package-relative imports with direct-script fallback"
        ),
        "v5_is_v4_retry": False,
        "v5_is_independent_full_replication": True,
        "v4_rows_pooled_into_v5_estimators": False,
        "task_schedule_phase_statistics_threshold_changed_from_v4": False,
    }


def post_failure_replication_provenance() -> dict[str, object]:
    """Bind V6 to terminal V5 without retrying or pooling failed transactions."""

    return {
        "predecessor_path": V5_PREREGISTRATION_PATH,
        "predecessor_schema": V5_PREREGISTRATION_SCHEMA,
        "predecessor_preregistration_sha256": V5_PREREGISTRATION_SHA256,
        "predecessor_file_sha256": V5_PREREGISTRATION_FILE_SHA256,
        "v5_transaction_source_commit": ("472b0fc963b317672ca2e3b0dbdb888cf414b3d4"),
        "v5_transaction_artifact_path": (
            "history/internal_docs/goal5842_causal_admission_cost_20260903/"
            "pod_artifacts/goal5842_replication05_failure.tar.gz"
        ),
        "v5_transaction_artifact_bytes": 227_006,
        "v5_transaction_artifact_sha256": (
            "0dcb379450de007b5494597771b3a50b85e5db572d4e571ef5114170c74e90ce"
        ),
        "v5_execution_authority_file_sha256": (
            "884f0f2eacb7cc58bea5221c1f3b409aa77a1dfd2288638d02f083d6428134ed"
        ),
        "v5_gpu_identity_witness_file_sha256": (
            "751450720094751e75325e018b247eb8e1315cf66881f7c2aa2a96550a47c156"
        ),
        "v5_pyoptix_identity_witness_file_sha256": (
            "3eee25d89378909c3a23ac1f4231a6c200ef15d9d0f01008cb9a572d72e7e3ac"
        ),
        "v5_causal_result_file_sha256": (
            "59561f75402918959d5293a15125e429ffe2b645f64a0970aff2f29956bf93c8"
        ),
        "v5_failure_marker_file_sha256": (
            "930a4815aa8c11adf5e3f072eb437e1bcb31e21f8ddb10ac98280bc849fc870c"
        ),
        "v5_failed_rtdl_marker_file_sha256": (
            "6eea83af0160ba75491768dc036bb7726cab7d383d43f3d85f0a825869b036ee"
        ),
        "v5_failed_rtdl_stderr_file_sha256": (
            "d6670eaa90509486b24eae37b90b77caff5ce80de08fd5aa9df08c72c1ccbb30"
        ),
        "v5_worker_zero_reached": True,
        "v5_new_transaction_after_repair_permitted": False,
        "v5_completed_causal_worker_count": 216,
        "v5_completed_baseline_subworker_count": 5,
        "v5_failed_baseline_subworker_count": 1,
        "v5_registered_causal_worker_timing_vector_count": 216,
        "v5_registered_causal_phase_value_count": 432,
        "v5_registered_baseline_subworker_timing_vector_count": 5,
        "v5_registered_baseline_execution_sample_count": 131,
        "v5_unregistered_successful_baseline_warmup_execution_count": 17,
        "v5_untimed_rtdl_identity_complete_execution_call_count": 6,
        "v5_untimed_pyoptix_identity_complete_execution_call_count": 2,
        "failure_code": "RTDL_PUBLIC_PREPARED_CACHE_COMMIT_HANDOFF_MISSING",
        "failed_task": RELATION_TASK,
        "failed_arm": RTDL_ARM,
        "failed_mode": STEADY_MODE,
        "failed_schedule_worker_id": (
            "B002__K00__CUSTOM_AABB_CLOSED_RELATION_COUNT_V1__D_RTDL_PUBLIC_CHECK_ON"
        ),
        "failed_process_returncode": -11,
        "python_exception_before_process_exit": (
            "V4 prepared bounded relation source-cache reuse is invalid"
        ),
        "repair_classification": (
            "GENERIC_RUNTIME_CORRECTNESS_REPAIR_NOT_POST_RESULT_OPTIMIZATION"
        ),
        "repair_scope": (
            "two-phase native cache commit and digest validation for the app-free "
            "public relation and triangle prepared owners"
        ),
        "v6_is_v5_retry": False,
        "v6_is_independent_full_replication": True,
        "v4_or_v5_rows_pooled_into_v6_estimators": False,
        "task_schedule_phase_statistics_threshold_changed_from_v5": False,
        "rtdl_provider_implementation_changed_from_v5": True,
    }


def v7_preregistration_supersession() -> dict[str, object]:
    """Bind V7 to both disclosed pre-worker-zero V6 attempts."""

    return {
        "predecessor_path": V6_PREREGISTRATION_PATH,
        "predecessor_schema": V6_PREREGISTRATION_SCHEMA,
        "predecessor_preregistration_sha256": V6_PREREGISTRATION_SHA256,
        "predecessor_file_sha256": V6_PREREGISTRATION_FILE_SHA256,
        "v6_source_commit": "1a2b98abf5c04c095f81f05b17f91a62e120ffca",
        "v6_preworker_artifact_path": (
            "history/internal_docs/goal5842_causal_admission_cost_20260903/"
            "pod_artifacts/goal5842_v6_preworker_failures.tar.gz"
        ),
        "v6_preworker_artifact_bytes": 3_761,
        "v6_preworker_artifact_sha256": (
            "9f32d8aab3be262148bc10eeac55c92f950d483207240c42323371b5a0839bb1"
        ),
        "v6_preflight_attempt_count": 2,
        "v6_attempt_1": {
            "failed_stage": "00_bind_execution_authority",
            "reason_code": "NVCC_NOT_VISIBLE_IN_NON_LOGIN_PATH",
            "worker_zero_reached": False,
            "registered_timing_observation_count": 0,
            "gpu_complete_execution_call_count": 0,
            "failure_marker_sha256": (
                "47d570cdd595b50a0f1db7fbe21433e29bc5f207962ef5438f70cea361ca23a9"
            ),
            "stderr_sha256": (
                "321af0fc3fe72c57cde9f3b6bce2b2ec66aedf61b007d64c3b51141e3baee0ab"
            ),
        },
        "v6_attempt_2": {
            "failed_stage": "01_gpu_identity_witness_no_timing",
            "reason_code": (
                "GENERIC_LIFECYCLE_PROVIDER_RECEIPT_NESTING_INTERPRETATION_DEFECT"
            ),
            "execution_authority_sha256": (
                "636132f8c4ff44af5c1d4df1ffe92ed563f71241ce0df6538e7512c5ea8b0087"
            ),
            "worker_zero_reached": False,
            "registered_timing_observation_count": 0,
            "gpu_complete_execution_call_count": 72,
            "gpu_call_count_basis": (
                "the timer-free relation CHECK_ON loop completed and validated all "
                "72 outputs and OptiX traversal receipts before the post-loop "
                "lifecycle assertion raised"
            ),
            "failure_marker_sha256": (
                "71222136e24031c38abfdec3ff4d276187b25b7eb3cacb701b630e05162ae4c6"
            ),
            "stdout_sha256": (
                "b49f4b12bd85968859dd4b43e49fc97bbb555781a5f143e713cb3fd3de02b5bc"
            ),
            "stderr_sha256": (
                "78a9dbb5c6c14205f4101d2d278aa82a9a7f8fef97b120e0e30fe45295e3bfdd"
            ),
        },
        "scientific_design_changed": False,
        "schedule_changed": False,
        "workload_changed": False,
        "statistics_changed": False,
        "hardware_design_changed": False,
        "witness_implementation_changed": True,
        "repair_scope": (
            "read and validate the provider execution count from the generic "
            "lifecycle receipt's nested provider_receipt"
        ),
        "successful_transaction_repeats_full_witness_before_timing": True,
        "v7_is_v6_retry": False,
        "v7_is_append_only_full_replication": True,
        "v6_untimed_calls_pooled_into_v7_estimators": False,
    }


def v8_preregistration_supersession() -> dict[str, object]:
    """Bind V8 to the disclosed pre-worker-zero V7 attempt."""

    return {
        "predecessor_path": V7_PREREGISTRATION_PATH,
        "predecessor_schema": V7_PREREGISTRATION_SCHEMA,
        "predecessor_preregistration_sha256": V7_PREREGISTRATION_SHA256,
        "predecessor_file_sha256": V7_PREREGISTRATION_FILE_SHA256,
        "v7_source_commit": "50c0c12bf4e96991edb2c6dcaca1f93508f87282",
        "v7_preworker_artifact_path": (
            "history/internal_docs/goal5842_causal_admission_cost_20260903/"
            "pod_artifacts/goal5842_v7_preworker_failure.tar.gz"
        ),
        "v7_preworker_artifact_bytes": 3_253,
        "v7_preworker_artifact_sha256": (
            "6ad034ebfb18e9158fb7a0b610590e25c9653001ccf2fe1d94365b8a97c0dfdc"
        ),
        "failed_stage": "01_gpu_identity_witness_no_timing",
        "reason_code": "PUBLIC_PROVIDER_LIFECYCLE_SCHEMA_CLASSIFICATION_DEFECT",
        "execution_authority_sha256": (
            "717cdc4db1666c891e8900d9d63e0fa562877b90d5af0b07f8d09036d5dbf821"
        ),
        "worker_zero_reached": False,
        "registered_timing_observation_count": 0,
        "gpu_complete_execution_call_count": 72,
        "gpu_call_count_basis": (
            "the timer-free relation CHECK_ON loop completed and validated all "
            "72 outputs and OptiX traversal receipts before the provider-schema "
            "assertion raised"
        ),
        "failure_marker_sha256": (
            "71222136e24031c38abfdec3ff4d276187b25b7eb3cacb701b630e05162ae4c6"
        ),
        "stdout_sha256": (
            "b49f4b12bd85968859dd4b43e49fc97bbb555781a5f143e713cb3fd3de02b5bc"
        ),
        "stderr_sha256": (
            "29c43574ccb2df1c8b1124a70dc727fe7346246917c76572779f8dba071c0d84"
        ),
        "scientific_design_changed": False,
        "schedule_changed": False,
        "workload_changed": False,
        "statistics_changed": False,
        "hardware_design_changed": False,
        "witness_implementation_changed": True,
        "repair_scope": (
            "validate relation and triangle against the public prepared-protocol "
            "provider receipt schema rather than its hidden owner schema"
        ),
        "successful_transaction_repeats_full_witness_before_timing": True,
        "v8_is_v7_retry": False,
        "v8_is_append_only_full_replication": True,
        "v7_untimed_calls_pooled_into_v8_estimators": False,
    }


def v9_preregistration_supersession() -> dict[str, object]:
    """Bind V9 to V8 and disclose the pre-result measurement-design correction."""

    return {
        "predecessor_path": V8_PREREGISTRATION_PATH,
        "predecessor_schema": V8_PREREGISTRATION_SCHEMA,
        "predecessor_preregistration_sha256": V8_PREREGISTRATION_SHA256,
        "predecessor_file_sha256": V8_PREREGISTRATION_FILE_SHA256,
        "v8_source_commit": "adb32fbb05e808cb50e2f7ee48e7f7aae4f854ad",
        "v8_preworker_artifact_path": (
            "history/internal_docs/goal5842_causal_admission_cost_20260903/"
            "pod_artifacts/goal5842_v8_preworker_failure.tar.gz"
        ),
        "v8_preworker_artifact_bytes": 3_346,
        "v8_preworker_artifact_sha256": (
            "b6a70ec90b40d13269d3b9301c23cb86335c52a2ea34572a6909555362394234"
        ),
        "failed_stage": "01_gpu_identity_witness_no_timing",
        "reason_code": "PUBLIC_RESULT_CONTRACT_AND_TIMED_ORACLE_ASYMMETRY_DEFECT",
        "execution_authority_sha256": (
            "7a1646533562b9a4f166668d81519723eeb483a272308e21d916cc7b932f43f9"
        ),
        "execution_authority_file_sha256": (
            "ee6738ab7e42bb7b8fd791442e87a29ef46053cddce076ca68a0ac3185b432fa"
        ),
        "worker_zero_reached": False,
        "registered_timing_observation_count": 0,
        "gpu_complete_execution_call_count": 145,
        "gpu_call_count_basis": (
            "the timer-free relation CHECK_ON and CHECK_OFF loops completed 72 "
            "calls each; the triangle CHECK_ON first call completed before the "
            "witness accessed a nonexistent generic-result details attribute"
        ),
        "failure_marker_sha256": (
            "71222136e24031c38abfdec3ff4d276187b25b7eb3cacb701b630e05162ae4c6"
        ),
        "command_sha256": (
            "cab7f10b70fc79a6b4447a3d7450cac5f8fb9af04d8a44a4640717d929a0c7e7"
        ),
        "stdout_sha256": (
            "527389b531cccfee4e65e0769a7134c6135608a9f8fa8ac6c5ddae28455d022f"
        ),
        "stderr_sha256": (
            "2af711b9a710f3d3484dfef9a809c1f5f82b3900e17b0f6b62e3ececec340293"
        ),
        "scientific_design_changed": True,
        "causal_estimand_changed": False,
        "schedule_changed": False,
        "workload_values_changed": False,
        "statistics_changed": False,
        "hardware_design_changed": False,
        "witness_contract_changed": True,
        "baseline_timing_boundary_changed": True,
        "prior_partial_timing_was_available": True,
        "design_change_motivated_by_source_contract_audit_not_observed_ratio": True,
        "repair_scope": (
            "treat the triangle generic result as its actual public weighted scalar; "
            "move experimental oracle comparisons outside every registered execute "
            "interval; add timer-free full-output witnesses for RTDL, PyOptiX, and Direct"
        ),
        "v9_is_v8_retry": False,
        "v9_is_append_only_new_fair_baseline_design": True,
        "v4_through_v8_rows_pooled_into_v9_estimators": False,
        "successful_transaction_repeats_all_witnesses_before_worker_zero": True,
    }


def v10_preregistration_supersession() -> dict[str, object]:
    """Bind V10 to the immutable V9 pre-execution source-contract freeze."""

    return {
        "predecessor_path": V9_PREREGISTRATION_PATH,
        "predecessor_schema": V9_PREREGISTRATION_SCHEMA,
        "predecessor_preregistration_sha256": V9_PREREGISTRATION_SHA256,
        "predecessor_file_sha256": V9_PREREGISTRATION_FILE_SHA256,
        "reason_code": "PRE_EXECUTION_INHERITED_SOURCE_CONTRACT_REGRESSION",
        "worker_zero_reached": False,
        "registered_timing_observation_count": 0,
        "formal_gpu_execution_count": 0,
        "prefreeze_unregistered_engineering_complete_execution_call_count": 6,
        "prefreeze_unregistered_engineering_optix_launch_count": 8,
        "prefreeze_engineering_timings_retained_or_used": False,
        "scientific_design_changed": False,
        "causal_estimand_changed": False,
        "schedule_changed": False,
        "workload_values_changed": False,
        "statistics_changed": False,
        "hardware_design_changed": False,
        "witness_contract_changed": False,
        "baseline_timing_boundary_changed": False,
        "runtime_semantics_changed": False,
        "changed_existing_source_paths": [
            {
                "path": "experiments/goal5798_premeasurement/pyoptix_worker.py",
                "v9_sha256": (
                    "b144b9d48ba68f5dd0c9c0fbe18aacb119b0ca229dc2e28305c95d536e162019"
                ),
                "v10_sha256": (
                    "b97d299a5a9021ddc49fba969c31f692dfe4416be727b4173d47a639b002c4c7"
                ),
                "change": (
                    "replace a semantically equivalent conditional expression with "
                    "the historical explicit bulk cp.asnumpy statement inside a "
                    "public_output_only guard"
                ),
            }
        ],
        "append_only_documents": [
            (
                "history/internal_docs/goal5842_causal_admission_cost_20260903/"
                "PRE_WORKER_ZERO_REPAIR_07.md"
            ),
            (
                "history/internal_docs/goal5842_causal_admission_cost_20260903/"
                "PRE_EXECUTION_INTERNAL_HOSTILE_REVIEW_V10.md"
            ),
        ],
        "v10_is_result_dependent_retry": False,
        "v10_is_append_only_preexecution_source_contract_correction": True,
        "v9_rows_pooled_into_v10_estimators": False,
    }


def v11_preregistration_supersession() -> dict[str, object]:
    """Bind V11 to the disclosed pre-worker-zero V10 attempt."""

    return {
        "predecessor_path": V10_PREREGISTRATION_PATH,
        "predecessor_schema": V10_PREREGISTRATION_SCHEMA,
        "predecessor_preregistration_sha256": V10_PREREGISTRATION_SHA256,
        "predecessor_file_sha256": V10_PREREGISTRATION_FILE_SHA256,
        "v10_source_commit": "3bf4413fab3ce4f95bf6db64f84a4ac03a55e5bd",
        "v10_preworker_artifact_path": (
            "history/internal_docs/goal5842_causal_admission_cost_20260903/"
            "pod_artifacts/goal5842_v10_preworker_failure.tar.gz"
        ),
        "v10_preworker_artifact_bytes": 3_524,
        "v10_preworker_artifact_sha256": (
            "6296e6782bf86f4e41cf069921478731744ec6b0a495bd5a153cbe3e0f6f8b74"
        ),
        "failed_stage": "01_gpu_identity_witness_no_timing",
        "reason_code": "SPHERE_PROVIDER_LIFECYCLE_SCHEMA_CLASSIFICATION_DEFECT",
        "execution_authority_sha256": (
            "17a8a8e4d3a4d99720d94317ae7aac523f4f4eb89be1e2eb52cc2ab01a9f113f"
        ),
        "execution_authority_file_sha256": (
            "d2352d6c4a4a06a9d29f7e6d07f275130fe81b3118ed92065c585fdd9ba696fd"
        ),
        "worker_zero_reached": False,
        "registered_timing_observation_count": 0,
        "gpu_complete_execution_call_count": 290,
        "gpu_call_count_basis": (
            "the timer-free relation and triangle CHECK_ON/CHECK_OFF loops "
            "completed 72 calls per arm, the triangle auxiliary oracle completed "
            "one call, and sphere CHECK_ON completed one call before its post-call "
            "provider-schema assertion raised"
        ),
        "failure_marker_sha256": (
            "71222136e24031c38abfdec3ff4d276187b25b7eb3cacb701b630e05162ae4c6"
        ),
        "command_sha256": (
            "461b879706a94cd4245b788d7053e01be10246a0cb4da9e499147473f72fdfa3"
        ),
        "stdout_sha256": (
            "dba67b7c32e690937efd40cf1cefbfc666b00223c322ee272a1fb00d7d7f0d51"
        ),
        "stderr_sha256": (
            "b15ad0cb114d5ad67177f0427eb2bdc354a3cb6f510224f537a9e99dfd5c45e2"
        ),
        "scientific_design_changed": False,
        "causal_estimand_changed": False,
        "schedule_changed": False,
        "workload_values_changed": False,
        "statistics_changed": False,
        "hardware_design_changed": False,
        "baseline_timing_boundary_changed": False,
        "runtime_semantics_changed": False,
        "witness_implementation_changed": True,
        "repair_scope": (
            "validate the selected sphere route against its actual prepared "
            "sphere-any-hit-count owner schema instead of the unrelated legacy "
            "built-in-sphere owner schema"
        ),
        "successful_transaction_repeats_all_witnesses_before_worker_zero": True,
        "v11_is_v10_retry": False,
        "v11_is_append_only_full_replication": True,
        "v10_untimed_calls_pooled_into_v11_estimators": False,
    }


def v12_preregistration_supersession() -> dict[str, object]:
    """Bind V12 to the disclosed terminal V11 recount failure."""

    return {
        "predecessor_path": V11_PREREGISTRATION_PATH,
        "predecessor_schema": V11_PREREGISTRATION_SCHEMA,
        "predecessor_preregistration_sha256": V11_PREREGISTRATION_SHA256,
        "predecessor_file_sha256": V11_PREREGISTRATION_FILE_SHA256,
        "v11_source_commit": "478876b257c2b4bb46f2deedf54a7ef2a6d8abff",
        "v11_terminal_artifact_path": (
            "history/internal_docs/goal5842_causal_admission_cost_20260903/"
            "pod_artifacts/goal5842_v11_ada_terminal_failure.tar.gz"
        ),
        "v11_terminal_artifact_bytes": 3_778_593,
        "v11_terminal_artifact_member_count": 2_324,
        "v11_terminal_artifact_sha256": (
            "9385c90ec126745ae44859f7bd46b16be1f7b7565fe274782613af4b975b8a15"
        ),
        "failed_stage": "06_independent_recount",
        "reason_code": "INDEPENDENT_RECOUNT_DIRECT_ONLY_FIELD_SET_DEFECT",
        "execution_authority_sha256": (
            "d955e8d48c91c6afb715e01118e6c0679a037bb7414cc537c329a279939fdbb3"
        ),
        "execution_authority_file_sha256": (
            "281d08a87e88a6bdf1a6aa42e9a597768097c0639f5d4b92ce18e1dff7020c17"
        ),
        "failure_marker_sha256": (
            "b47f288eb9fee428a2e01500549e04865fad9fd8c2ec02ecd4fe5377dc7e3b5f"
        ),
        "recount_command_sha256": (
            "224331a413bc65170d1b31839ae0c146343135f3dd416f1f6f9c34c33333f9f1"
        ),
        "recount_stdout_sha256": (
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        ),
        "recount_stderr_sha256": (
            "d3cb8983c909ec22c00bb18c46022ec22350a25fd4f20a41710f62a451f7762a"
        ),
        "causal_result_sha256": (
            "3be63b9c97c33e42d98d03f464576028044ae6b8702d87882c8e39f288347698"
        ),
        "baseline_result_sha256": (
            "0a79d83a592cd01f8cae4af6e87f4a6f8e82f14705462bd878a90f543b81fec3"
        ),
        "postmortem_diagnostic_recount_sha256": (
            "e344facbfd4e87d66f1edcd22acb72855969f1affa0a440d9e38063eb5445d9b"
        ),
        "worker_zero_reached": True,
        "new_transaction_after_repair_permitted": False,
        "registered_causal_worker_timing_vector_count": 216,
        "registered_baseline_subworker_timing_vector_count": 216,
        "registered_baseline_execution_sample_count": 7_020,
        "baseline_composite_count": 108,
        "formal_gpu_complete_execution_call_count": 8_321,
        "observed_results_available_before_v12_freeze": True,
        "v12_prefreeze_unregistered_complete_execution_call_count": 0,
        "v12_prefreeze_unregistered_optix_launch_count": 0,
        "scientific_design_changed": False,
        "causal_estimand_changed": False,
        "schedule_changed": False,
        "workload_values_changed": False,
        "statistics_changed": False,
        "hardware_design_changed": False,
        "baseline_timing_boundary_changed": False,
        "runtime_semantics_changed": False,
        "independent_recount_validation_changed": True,
        "repair_scope": (
            "require the documented direct_close_phase_available=false field "
            "only on Direct receipts and forbid it on Python-arm receipts"
        ),
        "changed_existing_non_self_referential_source_paths": [
            {
                "path": (
                    "history/internal_docs/goal5842_causal_admission_cost_20260903/"
                    "DESIGN.md"
                ),
                "v11_sha256": (
                    "48b207634dc93d8f2234a1ad09d31ceedf3aabe2368a8b1116af7cd03c5616b9"
                ),
                "v12_sha256": (
                    "4f34761de50488601304bcef367583a164bbe3d2f8bdc447a1276933c6a08d4d"
                ),
            },
            {
                "path": "scripts/goal5842_build_preregistration.py",
                "v11_sha256": (
                    "cd91e7795599739ef21e8bd66b4b12699158a81c57f7a2635d096fa7b46e4005"
                ),
                "v12_sha256": (
                    "45b785ec05102994bac1781ccd6444d78f6b601da3786829e74496c57e842c0d"
                ),
            },
            {
                "path": "scripts/goal5842_independent_recount.py",
                "v11_sha256": (
                    "d5e6b24b87b4d68e419ec7fcfc140c41c443196cc26f2ea1bd7a1a1f82f28fce"
                ),
                "v12_sha256": (
                    "c417b55c354705fc950aa2e8e8f40cbf9d95bfd6318f46529bcf3e2c025f5b89"
                ),
            },
            {
                "path": "tests/goal5842_causal_admission_cost_test.py",
                "v11_sha256": (
                    "5766750b080973ddacdd89ca83bf170bc488a50bb899ba4d5a7f4e3b80fc1ce9"
                ),
                "v12_sha256": (
                    "1f156bbca035e322a0093f9d54c9a779d576734e5b79eb72a4276d87c95f6889"
                ),
            },
        ],
        "self_referential_contract_source_change": {
            "path": "experiments/goal5842_causal_admission/contracts.py",
            "v11_sha256": (
                "e79c474741e802c591384d470ddee3b939bda7ac523f4ceb77b63ecd1784f83d"
            ),
            "v12_identity": (
                "BOUND_BY_V12_SOURCE_MANIFEST_TO_AVOID_EMBEDDED_SELF_HASH"
            ),
            "reason": "the V12 contract cannot contain its own whole-file digest",
        },
        "successful_transaction_repeats_all_witnesses_before_worker_zero": True,
        "v12_is_v11_retry": False,
        "v12_is_append_only_full_replication": True,
        "v12_is_result_blind": False,
        "v11_failed_transaction_reclassified_as_success": False,
        "v11_postmortem_diagnostic_called_formal_recount": False,
        "v11_rows_pooled_into_v12_estimators": False,
    }


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    block = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            block.update(chunk)
    return block.hexdigest()


def pin_file(root: Path, path: Path) -> dict[str, object]:
    resolved_root = root.resolve()
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise Goal5842ContractError(f"pin outside repository: {resolved}") from exc
    if not resolved.is_file():
        raise Goal5842ContractError(f"pin is not a file: {relative}")
    return {
        "path": relative.as_posix(),
        "bytes": resolved.stat().st_size,
        "sha256": sha256_file(resolved),
    }


def verify_pin(root: Path, row: Mapping[str, object]) -> None:
    if set(row) != {"path", "bytes", "sha256"}:
        raise Goal5842ContractError("file pin has unexpected fields")
    relative = row["path"]
    if not isinstance(relative, str):
        raise Goal5842ContractError("file pin path must be a string")
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise Goal5842ContractError(f"unsafe file pin: {relative}")
    target = root.resolve() / path
    if not target.is_file():
        raise Goal5842ContractError(f"pinned file missing: {relative}")
    if target.stat().st_size != row["bytes"]:
        raise Goal5842ContractError(f"pinned file byte drift: {relative}")
    if sha256_file(target) != row["sha256"]:
        raise Goal5842ContractError(f"pinned file digest drift: {relative}")


def build_causal_schedule() -> list[dict[str, object]]:
    schedule: list[dict[str, object]] = []
    sequence = 0
    for task_index, task in enumerate(ADMISSION_TASKS):
        for block in range(CAUSAL_BLOCKS):
            order = ABBA if (task_index + block) % 2 == 0 else BAAB
            seen: defaultdict[str, int] = defaultdict(int)
            for position, arm in enumerate(order):
                sample_index = 2 * block + seen[arm]
                seen[arm] += 1
                schedule.append(
                    {
                        "sequence_index": sequence,
                        "task": task,
                        "task_index": task_index,
                        "block": block,
                        "position": position,
                        "arm": arm,
                        "arm_sample_index": sample_index,
                        "worker_id": (
                            f"C{sequence:03d}__T{task_index}__B{block:02d}__"
                            f"P{position}__{arm}"
                        ),
                    }
                )
                sequence += 1
    return schedule


def build_baseline_schedule() -> list[dict[str, object]]:
    schedule: list[dict[str, object]] = []
    counts: defaultdict[tuple[str, str], int] = defaultdict(int)
    sequence = 0
    for block in range(BASELINE_BLOCKS):
        task_order = (
            BASELINE_TASKS if block % 2 == 0 else tuple(reversed(BASELINE_TASKS))
        )
        for task_position, task in enumerate(task_order):
            permutation_index = (block + 2 * BASELINE_TASKS.index(task)) % 6
            for arm_position, arm in enumerate(
                BASELINE_PERMUTATIONS[permutation_index]
            ):
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
                        "worker_id": (f"B{sequence:03d}__K{block:02d}__{task}__{arm}"),
                    }
                )
                sequence += 1
    return schedule


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise Goal5842ContractError(message)


def validate_causal_schedule(schedule: object) -> None:
    _require(isinstance(schedule, list), "causal schedule must be a list")
    expected = build_causal_schedule()
    _require(
        schedule == expected, "causal schedule differs from the frozen ABBA design"
    )
    ids = [row["worker_id"] for row in schedule]
    _require(len(ids) == len(set(ids)), "causal worker ids are not unique")
    counts = Counter((row["task"], row["arm"]) for row in schedule)
    _require(
        set(counts.values()) == {CAUSAL_BLOCKS * 2}
        and len(counts) == len(ADMISSION_TASKS) * len(CAUSAL_ARMS),
        "causal schedule is imbalanced",
    )


def validate_baseline_schedule(schedule: object) -> None:
    _require(isinstance(schedule, list), "baseline schedule must be a list")
    expected = build_baseline_schedule()
    _require(schedule == expected, "baseline schedule differs from frozen permutations")
    ids = [row["worker_id"] for row in schedule]
    _require(len(ids) == len(set(ids)), "baseline worker ids are not unique")
    counts = Counter((row["task"], row["arm"]) for row in schedule)
    _require(
        set(counts.values()) == {BASELINE_BLOCKS}
        and len(counts) == len(BASELINE_TASKS) * len(BASELINE_ARMS),
        "baseline schedule is imbalanced",
    )


def validate_preregistration(value: object, root: Path, *, verify_files: bool) -> None:
    _require(isinstance(value, dict), "preregistration must be an object")
    prereg: dict[str, Any] = value
    seal = prereg.get("preregistration_sha256")
    unsealed = dict(prereg)
    unsealed.pop("preregistration_sha256", None)
    _require(
        isinstance(seal, str) and digest(unsealed) == seal,
        "preregistration seal mismatch",
    )
    _require(
        prereg.get("schema") == PREREGISTRATION_SCHEMA,
        "preregistration schema mismatch",
    )
    _require(
        prereg.get("supersession") == v12_preregistration_supersession(),
        "V12 pre-execution supersession provenance mismatch",
    )
    _require(
        prereg.get("post_failure_replication") == post_failure_replication_provenance(),
        "post-failure replication provenance mismatch",
    )
    _require(
        prereg.get("status") == "FROZEN_BEFORE_INDEPENDENT_V12_FAIR_BASELINE_TIMING",
        "V12 fair-baseline preregistration is not frozen",
    )
    _require(
        prereg.get("registered_timing_observation_count") == 0,
        "pre-freeze timing exists",
    )
    _require(prereg.get("gpu_execution_count") == 0, "pre-freeze GPU execution exists")
    _require(
        prereg.get("gpu_execution_count_scope") == "FORMAL_V12_TRANSACTION_ONLY",
        "formal GPU execution counter scope mismatch",
    )
    _require(
        prereg.get("unregistered_engineering_preflight")
        == {
            "scope": "V12_ONLY_BEFORE_PREREGISTRATION_FREEZE",
            "complete_execution_call_count": 0,
            "optix_launch_count": 0,
            "registered_timing_observation_count": 0,
            "timings_retained_or_used": False,
            "included_in_estimators": False,
        },
        "unregistered engineering preflight disclosure mismatch",
    )
    _require(
        prereg.get("preregistration_build_counter_scope")
        == {
            "top_level_counters_cover_this_v12_fair_baseline_build_only": True,
            "prior_evidence_is_bound_in_provenance_fields": True,
            "pre_v4_untimed_gpu_complete_execution_call_count": 8,
            "v4_registered_causal_worker_timing_vector_count": 216,
            "v4_registered_baseline_subworker_timing_vector_count": 2,
            "v4_registered_baseline_execution_sample_count": 65,
            "v4_untimed_rtdl_identity_complete_execution_call_count": 6,
            "v4_direct_baseline_complete_execution_call_count": 73,
            "v5_registered_causal_worker_timing_vector_count": 216,
            "v5_registered_baseline_subworker_timing_vector_count": 5,
            "v5_registered_baseline_execution_sample_count": 131,
            "v5_untimed_rtdl_identity_complete_execution_call_count": 6,
            "v5_untimed_pyoptix_identity_complete_execution_call_count": 2,
            "v6_preworker_attempt_count": 2,
            "v6_registered_timing_observation_count": 0,
            "v6_untimed_rtdl_identity_complete_execution_call_count": 72,
            "v7_preworker_attempt_count": 1,
            "v7_registered_timing_observation_count": 0,
            "v7_untimed_rtdl_identity_complete_execution_call_count": 72,
            "v8_preworker_attempt_count": 1,
            "v8_registered_timing_observation_count": 0,
            "v8_untimed_rtdl_identity_complete_execution_call_count": 145,
            "v9_preexecution_freeze_count": 1,
            "v9_registered_timing_observation_count": 0,
            "v9_formal_gpu_execution_count": 0,
            "v9_unregistered_engineering_complete_execution_call_count": 6,
            "v9_unregistered_engineering_optix_launch_count": 8,
            "v10_preworker_attempt_count": 1,
            "v10_registered_timing_observation_count": 0,
            "v10_untimed_rtdl_identity_complete_execution_call_count": 290,
            "v11_registered_causal_worker_timing_vector_count": 216,
            "v11_registered_baseline_subworker_timing_vector_count": 216,
            "v11_registered_baseline_execution_sample_count": 7_020,
            "v11_baseline_composite_count": 108,
            "v11_formal_gpu_complete_execution_call_count": 8_321,
        },
        "replication counter scope or prior evidence disclosure differs",
    )
    witnesses = prereg.get("pre_worker_zero_witness_design")
    _require(isinstance(witnesses, dict), "pre-worker-zero witness design missing")
    _require(
        witnesses
        == {
            "rtdl_check_on_off_task_count": 3,
            "rtdl_relation_triangle_calls_per_arm": 72,
            "rtdl_sphere_calls_per_arm": 1,
            "rtdl_check_on_off_complete_execution_call_count": 290,
            "rtdl_triangle_auxiliary_full_oracle_call_count": 1,
            "rtdl_total_witness_complete_execution_call_count": 291,
            "rtdl_repeated_lifecycle_matches_steady_shape": True,
            "pyoptix_package_front_door_task_count": 2,
            "pyoptix_calls_per_task": 72,
            "pyoptix_complete_execution_call_count": 144,
            "pyoptix_optix_launch_count": 216,
            "direct_full_oracle_task_count": 2,
            "direct_complete_execution_call_count": 2,
            "direct_optix_launch_count": 3,
            "all_witnesses_register_no_timing": True,
            "worker_zero_after_all_witnesses_pass": True,
            "triangle_public_output_scope": "CHECKED_U64_WEIGHTED_SCALAR_ONLY",
            "triangle_auxiliary_per_ray_scope": "NON_PUBLIC_UNTIMED_FULL_ORACLE",
        },
        "pre-worker-zero witness design drift",
    )
    baseline_design = prereg.get("baseline_worker_design")
    _require(
        baseline_design
        == {
            "composite_workers": 108,
            "fresh_subworkers_per_composite": 2,
            "total_subworkers": 216,
            "first_and_steady_processes_are_independent": True,
            "direct_close_phase_available": False,
            "close_phase_cross_arm_ratio_forbidden": True,
            "input_materialization_reported_separately_from_setup": True,
            "setup_total_excludes_input_first_execution_and_close": True,
            "registered_execute_interval_ends_before_experimental_oracle_comparison": True,
            "every_registered_sample_checked_immediately_after_interval": True,
            "triangle_cross_arm_public_output": "CHECKED_U64_WEIGHTED_SCALAR_ONLY",
            "direct_and_pyoptix_triangle_timed_host_copy_excludes_per_ray_vector": True,
            "rtdl_internal_per_ray_materialization_is_retained_as_implementation_cost": True,
            "full_per_ray_correctness_proved_only_by_pre_worker_zero_witnesses": True,
        },
        "baseline worker timing/output contract drift",
    )
    _require(
        prereg.get("admission_tasks") == list(ADMISSION_TASKS),
        "admission task set drift",
    )
    _require(
        prereg.get("baseline_tasks") == list(BASELINE_TASKS), "baseline task set drift"
    )
    _require(
        prereg.get("task_contracts") == [dict(row) for row in TASK_CONTRACTS],
        "task input/oracle contract drift",
    )
    _require(prereg.get("causal_arms") == list(CAUSAL_ARMS), "causal arm set drift")
    _require(
        prereg.get("baseline_arms") == list(BASELINE_ARMS), "baseline arm set drift"
    )
    _require(
        prereg.get("causal_phase_boundaries") == list(CAUSAL_PHASE_BOUNDARIES),
        "causal phase boundary drift",
    )
    _require(
        prereg.get("baseline_phase_boundaries") == list(BASELINE_PHASE_BOUNDARIES),
        "baseline phase boundary drift",
    )
    cold = prereg.get("cold_counterfactual_design")
    _require(isinstance(cold, dict), "cold counterfactual design missing")
    _require(
        cold.get("route_factory_first_call_in_both_arms") is True,
        "causal arms are not both cold",
    )
    _require(
        cold.get("pre_timing_public_admission") is False,
        "pre-timing admission would warm the causal experiment",
    )
    _require(
        cold.get("materialization_revalidation_remains_outside_causal_estimand")
        is True,
        "materialization revalidation boundary missing",
    )
    reference = prereg.get("post_estimand_reference_admission")
    _require(isinstance(reference, dict), "post-estimand reference missing")
    _require(
        reference.get("included_in_causal_estimand") is False
        and reference.get("performed_after_registered_interval_in_both_arms") is True
        and reference.get("cannot_warm_registered_timing") is True,
        "post-estimand reference timing boundary drift",
    )
    validate_causal_schedule(prereg.get("causal_schedule"))
    validate_baseline_schedule(prereg.get("baseline_schedule"))
    _require(
        prereg.get("causal_schedule_sha256") == digest(prereg["causal_schedule"]),
        "causal schedule seal mismatch",
    )
    _require(
        prereg.get("baseline_schedule_sha256") == digest(prereg["baseline_schedule"]),
        "baseline schedule seal mismatch",
    )
    statistics = prereg.get("statistics")
    _require(isinstance(statistics, dict), "statistics missing")
    _require(
        statistics.get("causal_block_count") == CAUSAL_BLOCKS,
        "causal block count drift",
    )
    _require(
        statistics.get("baseline_block_count") == BASELINE_BLOCKS,
        "baseline block count drift",
    )
    _require(statistics.get("steady_warmups") == STEADY_WARMUPS, "warmup count drift")
    _require(
        statistics.get("steady_repetitions") == STEADY_REPETITIONS,
        "repetition count drift",
    )
    _require(
        statistics.get("bootstrap_draws") == BOOTSTRAP_DRAWS, "bootstrap count drift"
    )
    _require(
        statistics.get("bootstrap_lower_index") == BOOTSTRAP_LOWER_INDEX
        and statistics.get("bootstrap_upper_index") == BOOTSTRAP_UPPER_INDEX
        and statistics.get("bootstrap_seed_base") == BOOTSTRAP_SEED_BASE,
        "bootstrap procedure drift",
    )
    _require(
        statistics.get("primary_summary")
        == (
            "median_of_provider_projection_and_admission_phase_block_deltas_"
            "absolute_nanoseconds"
        ),
        "primary causal statistic drift",
    )
    _require(
        statistics.get("ratio_to_near_zero_control_is_forbidden") is True,
        "unsafe causal ratio enabled",
    )
    _require(
        statistics.get("success_threshold") is None,
        "post-result success threshold forbidden",
    )
    identity = prereg.get("byte_identity_invariant")
    _require(isinstance(identity, dict), "byte identity invariant missing")
    for key in (
        "family_plan",
        "family_artifacts",
        "provider_projection",
        "generated_executable",
        "composed_ptx",
        "native_library",
        "input",
        "output",
    ):
        _require(
            identity.get(key) == "EXACT_SHA256_EQUAL",
            f"identity invariant missing: {key}",
        )
    _require(
        prereg.get("byte_identity_invariant_scope")
        == {
            "applies_to": "CHECK_ON_VS_CHECK_OFF_WITHIN_EACH_RTDL_TASK",
            "provider_baseline_generated_bytes_must_match": False,
            "provider_baseline_same_semantic_input_output_contract": True,
            "provider_baseline_implementations_are_independent": True,
        },
        "byte-identity scope drift",
    )
    ceiling = prereg.get("claim_ceiling")
    _require(isinstance(ceiling, dict), "claim ceiling missing")
    for key in (
        "checker_off_is_public_api",
        "checker_off_is_safe_for_users",
        "checker_off_is_supported_optimization",
        "admission_delta_explains_entire_setup_gap",
        "two_task_baseline_result_generalizes_to_all_rt",
        "sphere_has_direct_pyoptix_or_owl_performance_claim",
        "cross_generation_equivalence",
        "one_generation_is_goal5842_complete",
        "external_review_or_consensus",
        "v4_transaction_reclassified_as_success",
        "v5_transaction_reclassified_as_success",
        "v4_or_v5_rows_pooled_into_v6_estimators",
        "v6_called_a_retry_of_v5",
        "v6_preworker_attempt_reclassified_as_success",
        "v6_untimed_calls_count_as_v7_witness",
        "v4_v5_or_v6_rows_pooled_into_v7_estimators",
        "v7_called_a_retry_of_v6",
        "v7_preworker_attempt_reclassified_as_success",
        "v7_untimed_calls_count_as_v8_witness",
        "v4_v5_v6_or_v7_rows_pooled_into_v8_estimators",
        "v8_called_a_retry_of_v7",
        "v8_preworker_attempt_reclassified_as_success",
        "v8_untimed_calls_count_as_v9_witness",
        "v4_through_v8_rows_pooled_into_v9_estimators",
        "v9_called_a_retry_of_v8",
        "prior_partial_timing_hidden",
        "v9_preexecution_freeze_reclassified_as_executed_result",
        "v9_rows_pooled_into_v10_estimators",
        "v10_called_a_result_dependent_retry",
        "v10_preworker_attempt_reclassified_as_success",
        "v10_untimed_calls_count_as_v11_witness",
        "v10_rows_pooled_into_v11_estimators",
        "v11_called_a_result_dependent_retry",
        "v11_failed_transaction_reclassified_as_success",
        "v11_postmortem_diagnostic_called_formal_recount",
        "v11_rows_pooled_into_v12_estimators",
        "v12_called_a_result_blind_replication",
        "v12_called_a_v11_retry",
    ):
        _require(ceiling.get(key) is False, f"claim ceiling widened: {key}")
    _require(
        ceiling.get("checker_off_is_experiment_only_counterfactual") is True
        and ceiling.get("materialization_still_revalidates_identity") is True,
        "counterfactual boundary drift",
    )
    hardware = prereg.get("hardware_design")
    _require(
        isinstance(hardware, dict)
        and hardware.get("minimum_distinct_gpu_architecture_generations") == 2
        and hardware.get("cross_machine_raw_time_ratio_forbidden") is True,
        "hardware evidence gate weakened",
    )
    pins = prereg.get("source_manifest")
    _require(isinstance(pins, list) and pins, "source manifest missing")
    _require(
        len({row.get("path") for row in pins}) == len(pins), "duplicate source pin"
    )
    _require(
        [row.get("path") for row in pins] == list(REQUIRED_SOURCE_PATHS),
        "required source manifest path set or order drift",
    )
    _require(
        prereg.get("source_manifest_sha256") == digest(pins),
        "source manifest seal mismatch",
    )
    if verify_files:
        for row in pins:
            verify_pin(root, row)


def load_preregistration(
    path: Path, root: Path, *, verify_files: bool
) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    validate_preregistration(value, root, verify_files=verify_files)
    return value


__all__ = [
    "ADMISSION_TASKS",
    "BASELINE_ARMS",
    "BASELINE_BLOCKS",
    "BASELINE_CONTROLLER_SCHEMA",
    "BASELINE_PHASE_BOUNDARIES",
    "BASELINE_SUBWORKER_SCHEMA",
    "BASELINE_TASKS",
    "BOOTSTRAP_DRAWS",
    "BOOTSTRAP_LOWER_INDEX",
    "BOOTSTRAP_SEED_BASE",
    "BOOTSTRAP_UPPER_INDEX",
    "CAUSAL_ARMS",
    "CAUSAL_BLOCKS",
    "CAUSAL_PHASE_BOUNDARIES",
    "CHECK_OFF",
    "CHECK_ON",
    "CONTROLLER_RESULT_SCHEMA",
    "CROSS_GENERATION_AUTHORITY_SCHEMA",
    "DIRECT_ARM",
    "DIRECT_IDENTITY_WITNESS_SCHEMA",
    "EXECUTION_AUTHORITY_SCHEMA",
    "FIRST_MODE",
    "GPU_IDENTITY_WITNESS_SCHEMA",
    "INDEPENDENT_RECOUNT_SCHEMA",
    "PREREGISTRATION_SCHEMA",
    "PYOPTIX_ARM",
    "PYOPTIX_IDENTITY_WITNESS_SCHEMA",
    "RELATION_TASK",
    "REQUIRED_SOURCE_PATHS",
    "RTDL_ARM",
    "SPHERE_TASK",
    "STEADY_MODE",
    "STEADY_REPETITIONS",
    "STEADY_WARMUPS",
    "TASK_CONTRACTS",
    "TRIANGLE_TASK",
    "V1_PREREGISTRATION_FILE_SHA256",
    "V1_PREREGISTRATION_PATH",
    "V1_PREREGISTRATION_SCHEMA",
    "V1_PREREGISTRATION_SHA256",
    "V2_PREREGISTRATION_FILE_SHA256",
    "V2_PREREGISTRATION_PATH",
    "V2_PREREGISTRATION_SCHEMA",
    "V2_PREREGISTRATION_SHA256",
    "V3_PREREGISTRATION_FILE_SHA256",
    "V3_PREREGISTRATION_PATH",
    "V3_PREREGISTRATION_SCHEMA",
    "V3_PREREGISTRATION_SHA256",
    "V4_PREREGISTRATION_FILE_SHA256",
    "V4_PREREGISTRATION_PATH",
    "V4_PREREGISTRATION_SCHEMA",
    "V4_PREREGISTRATION_SHA256",
    "V5_PREREGISTRATION_FILE_SHA256",
    "V5_PREREGISTRATION_PATH",
    "V5_PREREGISTRATION_SCHEMA",
    "V5_PREREGISTRATION_SHA256",
    "V6_PREREGISTRATION_FILE_SHA256",
    "V6_PREREGISTRATION_PATH",
    "V6_PREREGISTRATION_SCHEMA",
    "V6_PREREGISTRATION_SHA256",
    "V7_PREREGISTRATION_FILE_SHA256",
    "V7_PREREGISTRATION_PATH",
    "V7_PREREGISTRATION_SCHEMA",
    "V7_PREREGISTRATION_SHA256",
    "V8_PREREGISTRATION_FILE_SHA256",
    "V8_PREREGISTRATION_PATH",
    "V8_PREREGISTRATION_SCHEMA",
    "V8_PREREGISTRATION_SHA256",
    "V9_PREREGISTRATION_FILE_SHA256",
    "V9_PREREGISTRATION_PATH",
    "V9_PREREGISTRATION_SCHEMA",
    "V9_PREREGISTRATION_SHA256",
    "V10_PREREGISTRATION_FILE_SHA256",
    "V10_PREREGISTRATION_PATH",
    "V10_PREREGISTRATION_SCHEMA",
    "V10_PREREGISTRATION_SHA256",
    "V11_PREREGISTRATION_FILE_SHA256",
    "V11_PREREGISTRATION_PATH",
    "V11_PREREGISTRATION_SCHEMA",
    "V11_PREREGISTRATION_SHA256",
    "WORKER_RECEIPT_SCHEMA",
    "Goal5842ContractError",
    "build_baseline_schedule",
    "build_causal_schedule",
    "canonical_bytes",
    "digest",
    "load_preregistration",
    "pin_file",
    "post_failure_replication_provenance",
    "sha256_file",
    "v2_preregistration_supersession",
    "v3_preregistration_supersession",
    "v4_preregistration_supersession",
    "v5_post_failure_replication_provenance",
    "v7_preregistration_supersession",
    "v8_preregistration_supersession",
    "v9_preregistration_supersession",
    "v10_preregistration_supersession",
    "v11_preregistration_supersession",
    "v12_preregistration_supersession",
    "validate_baseline_schedule",
    "validate_causal_schedule",
    "validate_preregistration",
    "verify_pin",
]

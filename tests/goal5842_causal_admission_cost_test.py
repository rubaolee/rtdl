"""Adversarial no-timing tests for Goal5842 preregistration and task routes."""

from __future__ import annotations

import ast
import hashlib
import importlib
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
from collections import Counter
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

from experiments.goal5842_causal_admission.baseline_controller import (
    combine_subworkers,
)
from experiments.goal5842_causal_admission.baseline_controller import (
    summarize as summarize_baselines,
)
from experiments.goal5842_causal_admission.baseline_worker import (
    verify_public_output,
)
from experiments.goal5842_causal_admission.contracts import (
    ADMISSION_TASKS,
    BASELINE_ARMS,
    BASELINE_BLOCKS,
    BASELINE_CONTROLLER_SCHEMA,
    BASELINE_SUBWORKER_SCHEMA,
    BASELINE_TASKS,
    CAUSAL_BLOCKS,
    CHECK_OFF,
    CHECK_ON,
    CROSS_GENERATION_AUTHORITY_SCHEMA,
    DIRECT_IDENTITY_WITNESS_SCHEMA,
    INDEPENDENT_RECOUNT_SCHEMA,
    TASK_CONTRACTS,
    TRIANGLE_TASK,
    V1_PREREGISTRATION_FILE_SHA256,
    V1_PREREGISTRATION_PATH,
    V1_PREREGISTRATION_SCHEMA,
    V1_PREREGISTRATION_SHA256,
    V2_PREREGISTRATION_FILE_SHA256,
    V2_PREREGISTRATION_PATH,
    V2_PREREGISTRATION_SCHEMA,
    V2_PREREGISTRATION_SHA256,
    V3_PREREGISTRATION_FILE_SHA256,
    V3_PREREGISTRATION_PATH,
    V3_PREREGISTRATION_SCHEMA,
    V3_PREREGISTRATION_SHA256,
    V4_PREREGISTRATION_FILE_SHA256,
    V4_PREREGISTRATION_PATH,
    V4_PREREGISTRATION_SCHEMA,
    V4_PREREGISTRATION_SHA256,
    V5_PREREGISTRATION_FILE_SHA256,
    V5_PREREGISTRATION_PATH,
    V5_PREREGISTRATION_SCHEMA,
    V5_PREREGISTRATION_SHA256,
    V6_PREREGISTRATION_FILE_SHA256,
    V6_PREREGISTRATION_PATH,
    V6_PREREGISTRATION_SCHEMA,
    V6_PREREGISTRATION_SHA256,
    V7_PREREGISTRATION_FILE_SHA256,
    V7_PREREGISTRATION_PATH,
    V7_PREREGISTRATION_SCHEMA,
    V7_PREREGISTRATION_SHA256,
    V8_PREREGISTRATION_FILE_SHA256,
    V8_PREREGISTRATION_PATH,
    V8_PREREGISTRATION_SCHEMA,
    V8_PREREGISTRATION_SHA256,
    V9_PREREGISTRATION_FILE_SHA256,
    V9_PREREGISTRATION_PATH,
    V9_PREREGISTRATION_SCHEMA,
    V9_PREREGISTRATION_SHA256,
    Goal5842ContractError,
    build_baseline_schedule,
    build_causal_schedule,
    digest,
    post_failure_replication_provenance,
    sha256_file,
    v2_preregistration_supersession,
    v3_preregistration_supersession,
    v4_preregistration_supersession,
    v5_post_failure_replication_provenance,
    v7_preregistration_supersession,
    v8_preregistration_supersession,
    v9_preregistration_supersession,
    v10_preregistration_supersession,
    validate_preregistration,
)
from experiments.goal5842_causal_admission.controller import summarize
from experiments.goal5842_causal_admission.runtime import (
    bind_authorized_native_library,
)
from experiments.goal5842_causal_admission.tasks import (
    SPHERE_SIZE,
    build_task,
    checker_off_program,
    program_signature,
    sphere_workload,
)
from scripts.goal5842_bind_execution_authority import architecture_generation
from scripts.goal5842_build_cross_generation_authority import (
    build as build_cross_generation_authority,
)
from scripts.goal5842_build_preregistration import build
from scripts.goal5842_gpu_identity_witness import (
    execute_and_check,
    provider_lifecycle_evidence,
)
from scripts.goal5842_independent_recount import (
    baseline_summary as independently_summarize_baselines,
)
from scripts.goal5842_independent_recount import (
    causal_summary as independently_summarize_causal,
)
from scripts.goal5842_independent_recount import (
    recount_baseline,
    recount_causal,
    validate_direct_identity_witness,
    validate_identity_witness,
    validate_pyoptix_identity_witness,
)
from scripts.goal5842_run_one_generation import validated_python_entrypoint

ROOT = Path(__file__).resolve().parents[1]
PREREGISTRATION = ROOT / (
    "history/internal_docs/goal5842_causal_admission_cost_20260903/"
    "PREREGISTRATION_V10.json"
)
V1_PREREGISTRATION = ROOT / V1_PREREGISTRATION_PATH
V2_PREREGISTRATION = ROOT / V2_PREREGISTRATION_PATH
V3_PREREGISTRATION = ROOT / V3_PREREGISTRATION_PATH
V4_PREREGISTRATION = ROOT / V4_PREREGISTRATION_PATH
V5_PREREGISTRATION = ROOT / V5_PREREGISTRATION_PATH
V6_PREREGISTRATION = ROOT / V6_PREREGISTRATION_PATH
V7_PREREGISTRATION = ROOT / V7_PREREGISTRATION_PATH
V8_PREREGISTRATION = ROOT / V8_PREREGISTRATION_PATH
V9_PREREGISTRATION = ROOT / V9_PREREGISTRATION_PATH
FROZEN_CORE = (
    "src/rtdsl/v4_family_schema.py",
    "src/rtdsl/v4_generic_family_lifecycle.py",
    "src/rtdsl/v4_family.py",
)


def _reseal(value: dict[str, object]) -> None:
    value.pop("preregistration_sha256", None)
    value["preregistration_sha256"] = digest(value)


class Goal5842CausalAdmissionCostTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))

    def test_preregistration_rebuilds_exactly_without_timing(self) -> None:
        self.assertEqual(build(), self.prereg)
        validate_preregistration(self.prereg, ROOT, verify_files=True)
        self.assertEqual(self.prereg["registered_timing_observation_count"], 0)
        self.assertEqual(self.prereg["gpu_execution_count"], 0)

    def test_v5_history_binds_v4_failure_without_superseding_or_pooling_it(
        self,
    ) -> None:
        v1 = json.loads(V1_PREREGISTRATION.read_text(encoding="utf-8"))
        v2 = json.loads(V2_PREREGISTRATION.read_text(encoding="utf-8"))
        v3 = json.loads(V3_PREREGISTRATION.read_text(encoding="utf-8"))
        v4 = json.loads(V4_PREREGISTRATION.read_text(encoding="utf-8"))
        v5 = json.loads(V5_PREREGISTRATION.read_text(encoding="utf-8"))
        self.assertEqual(v1["schema"], V1_PREREGISTRATION_SCHEMA)
        self.assertEqual(
            v1["preregistration_sha256"],
            V1_PREREGISTRATION_SHA256,
        )
        self.assertEqual(
            sha256_file(V1_PREREGISTRATION),
            V1_PREREGISTRATION_FILE_SHA256,
        )
        self.assertEqual(v2["schema"], V2_PREREGISTRATION_SCHEMA)
        self.assertEqual(v2["preregistration_sha256"], V2_PREREGISTRATION_SHA256)
        self.assertEqual(
            sha256_file(V2_PREREGISTRATION), V2_PREREGISTRATION_FILE_SHA256
        )
        self.assertEqual(v2["supersession"], v2_preregistration_supersession())
        self.assertEqual(v3["schema"], V3_PREREGISTRATION_SCHEMA)
        self.assertEqual(v3["preregistration_sha256"], V3_PREREGISTRATION_SHA256)
        self.assertEqual(
            sha256_file(V3_PREREGISTRATION), V3_PREREGISTRATION_FILE_SHA256
        )
        self.assertEqual(v3["supersession"], v3_preregistration_supersession())
        self.assertFalse(v3["supersession"]["scientific_design_changed"])
        self.assertEqual(v3["supersession"]["gpu_complete_execution_call_count"], 4)
        self.assertEqual(v4["schema"], V4_PREREGISTRATION_SCHEMA)
        self.assertEqual(v4["preregistration_sha256"], V4_PREREGISTRATION_SHA256)
        self.assertEqual(
            sha256_file(V4_PREREGISTRATION), V4_PREREGISTRATION_FILE_SHA256
        )
        self.assertEqual(v4["supersession"], v4_preregistration_supersession())
        self.assertFalse(v4["supersession"]["worker_zero_reached"])
        self.assertTrue(v4["supersession"]["scientific_design_changed"])
        self.assertTrue(v4["supersession"]["workload_changed"])
        self.assertEqual(v5["schema"], V5_PREREGISTRATION_SCHEMA)
        self.assertEqual(v5["preregistration_sha256"], V5_PREREGISTRATION_SHA256)
        self.assertEqual(
            sha256_file(V5_PREREGISTRATION), V5_PREREGISTRATION_FILE_SHA256
        )
        self.assertNotIn("supersession", v5)
        self.assertEqual(
            v5["post_failure_replication"],
            v5_post_failure_replication_provenance(),
        )
        provenance = v5["post_failure_replication"]
        self.assertFalse(provenance["v5_is_v4_retry"])
        self.assertTrue(provenance["v5_is_independent_full_replication"])
        self.assertFalse(provenance["v4_rows_pooled_into_v5_estimators"])
        for key in (
            "admission_tasks",
            "baseline_tasks",
            "task_contracts",
            "causal_arms",
            "baseline_arms",
            "causal_phase_boundaries",
            "baseline_phase_boundaries",
            "causal_schedule",
            "causal_schedule_sha256",
            "baseline_schedule",
            "baseline_schedule_sha256",
            "statistics",
            "failure_policy",
        ):
            self.assertEqual(v5[key], v4[key], key)
        self.assertEqual(
            provenance["pre_v4_untimed_gpu_complete_execution_call_count"],
            8,
        )
        self.assertEqual(
            v5["preregistration_build_counter_scope"][
                "pre_v4_untimed_gpu_complete_execution_call_count"
            ],
            8,
        )
        self.assertTrue(
            v5["preregistration_build_counter_scope"][
                "prior_evidence_is_bound_in_post_failure_replication"
            ]
        )
        artifact = ROOT / provenance["v4_transaction_artifact_path"]
        self.assertEqual(
            artifact.stat().st_size,
            provenance["v4_transaction_artifact_bytes"],
        )
        self.assertEqual(
            sha256_file(artifact), provenance["v4_transaction_artifact_sha256"]
        )
        with tarfile.open(artifact, "r:gz") as archive:
            members = {member.name: member for member in archive.getmembers()}

            def archived_bytes(suffix: str) -> bytes:
                matches = [name for name in members if name.endswith(suffix)]
                self.assertEqual(len(matches), 1, suffix)
                extracted = archive.extractfile(members[matches[0]])
                self.assertIsNotNone(extracted)
                return extracted.read()

            internal = {
                "v4_execution_authority_file_sha256": archived_bytes(
                    "/execution_authority.json"
                ),
                "v4_gpu_identity_witness_file_sha256": archived_bytes(
                    "/gpu_identity_witness.json"
                ),
                "v4_causal_result_file_sha256": archived_bytes("/causal/result.json"),
                "v4_failure_marker_file_sha256": archived_bytes(
                    "/TRANSACTION_FAILED_NO_RETRY.json"
                ),
                "v4_failed_pyoptix_marker_file_sha256": archived_bytes(
                    "/baseline/001_B001__K00__CUSTOM_AABB_CLOSED_RELATION_COUNT_V1__"
                    "B_CURRENT_NVIDIA_PYOPTIX_COMPATIBLE_API/first/failure.json"
                ),
                "v4_failed_pyoptix_stderr_file_sha256": archived_bytes(
                    "/baseline/001_B001__K00__CUSTOM_AABB_CLOSED_RELATION_COUNT_V1__"
                    "B_CURRENT_NVIDIA_PYOPTIX_COMPATIBLE_API/first/stderr.txt"
                ),
            }
        for field, payload in internal.items():
            self.assertEqual(hashlib.sha256(payload).hexdigest(), provenance[field])
        causal = json.loads(internal["v4_causal_result_file_sha256"])
        failure = json.loads(internal["v4_failure_marker_file_sha256"])
        stderr = internal["v4_failed_pyoptix_stderr_file_sha256"].decode("utf-8")
        self.assertEqual(causal["worker_count"], 216)
        self.assertTrue(failure["worker_zero_reached"])
        self.assertFalse(failure["new_transaction_after_repair_permitted"])
        self.assertIn("No module named 'worker_common'", stderr)

    def test_v6_binds_v5_failure_and_excludes_all_prior_rows(self) -> None:
        v5 = json.loads(V5_PREREGISTRATION.read_text(encoding="utf-8"))
        v6 = json.loads(V6_PREREGISTRATION.read_text(encoding="utf-8"))
        self.assertEqual(v6["schema"], V6_PREREGISTRATION_SCHEMA)
        self.assertEqual(v6["preregistration_sha256"], V6_PREREGISTRATION_SHA256)
        self.assertEqual(
            sha256_file(V6_PREREGISTRATION), V6_PREREGISTRATION_FILE_SHA256
        )
        self.assertNotIn("supersession", v6)
        self.assertEqual(
            v6["post_failure_replication"],
            post_failure_replication_provenance(),
        )
        provenance = v6["post_failure_replication"]
        self.assertFalse(provenance["v6_is_v5_retry"])
        self.assertTrue(provenance["v6_is_independent_full_replication"])
        self.assertFalse(provenance["v4_or_v5_rows_pooled_into_v6_estimators"])
        self.assertEqual(
            provenance["repair_classification"],
            "GENERIC_RUNTIME_CORRECTNESS_REPAIR_NOT_POST_RESULT_OPTIMIZATION",
        )
        self.assertTrue(provenance["rtdl_provider_implementation_changed_from_v5"])
        for key in (
            "admission_tasks",
            "baseline_tasks",
            "task_contracts",
            "causal_arms",
            "baseline_arms",
            "causal_phase_boundaries",
            "baseline_phase_boundaries",
            "causal_schedule",
            "causal_schedule_sha256",
            "baseline_schedule",
            "baseline_schedule_sha256",
            "statistics",
            "failure_policy",
        ):
            self.assertEqual(v6[key], v5[key], key)
        witness = v6["pre_worker_zero_witness_design"]
        self.assertEqual(witness["rtdl_relation_triangle_calls_per_arm"], 72)
        self.assertEqual(
            witness["rtdl_check_on_off_complete_execution_call_count"], 290
        )
        self.assertEqual(witness["pyoptix_complete_execution_call_count"], 144)
        self.assertEqual(witness["pyoptix_optix_launch_count"], 216)

        artifact = ROOT / provenance["v5_transaction_artifact_path"]
        self.assertEqual(
            artifact.stat().st_size, provenance["v5_transaction_artifact_bytes"]
        )
        self.assertEqual(
            sha256_file(artifact), provenance["v5_transaction_artifact_sha256"]
        )
        with tarfile.open(artifact, "r:gz") as archive:
            members = {member.name: member for member in archive.getmembers()}

            def archived_bytes(suffix: str) -> bytes:
                matches = [name for name in members if name.endswith(suffix)]
                self.assertEqual(len(matches), 1, suffix)
                extracted = archive.extractfile(members[matches[0]])
                self.assertIsNotNone(extracted)
                return extracted.read()

            internal = {
                "v5_execution_authority_file_sha256": archived_bytes(
                    "/execution_authority.json"
                ),
                "v5_gpu_identity_witness_file_sha256": archived_bytes(
                    "/gpu_identity_witness.json"
                ),
                "v5_pyoptix_identity_witness_file_sha256": archived_bytes(
                    "/pyoptix_identity_witness.json"
                ),
                "v5_causal_result_file_sha256": archived_bytes("/causal/result.json"),
                "v5_failure_marker_file_sha256": archived_bytes(
                    "/TRANSACTION_FAILED_NO_RETRY.json"
                ),
                "v5_failed_rtdl_marker_file_sha256": archived_bytes(
                    "/baseline/002_B002__K00__CUSTOM_AABB_CLOSED_RELATION_COUNT_V1__"
                    "D_RTDL_PUBLIC_CHECK_ON/steady/failure.json"
                ),
                "v5_failed_rtdl_stderr_file_sha256": archived_bytes(
                    "/baseline/002_B002__K00__CUSTOM_AABB_CLOSED_RELATION_COUNT_V1__"
                    "D_RTDL_PUBLIC_CHECK_ON/steady/stderr.txt"
                ),
            }
            baseline_receipts = [
                name
                for name in members
                if "/baseline/" in name and name.endswith("/receipt.json")
            ]
            self.assertFalse(
                any(name.endswith("/independent_recount.json") for name in members)
            )
            self.assertFalse(
                any(name.endswith("/TRANSACTION_COMPLETE.json") for name in members)
            )
        for field, payload in internal.items():
            self.assertEqual(hashlib.sha256(payload).hexdigest(), provenance[field])
        self.assertEqual(len(baseline_receipts), 5)
        causal = json.loads(internal["v5_causal_result_file_sha256"])
        failure = json.loads(internal["v5_failure_marker_file_sha256"])
        stderr = internal["v5_failed_rtdl_stderr_file_sha256"].decode("utf-8")
        self.assertEqual(causal["worker_count"], 216)
        self.assertTrue(failure["worker_zero_reached"])
        self.assertFalse(failure["new_transaction_after_repair_permitted"])
        self.assertIn("source-cache reuse is invalid", stderr)
        pins = {row["path"] for row in v6["source_manifest"]}
        self.assertTrue(
            {
                "src/rtdsl/v4_bounded_relation_prepared_runtime.py",
                "src/rtdsl/v4_triangle_reduction_prepared_runtime.py",
                "tests/goal5842_prepared_cache_commit_test.py",
            }
            <= pins
        )

    def test_v7_binds_v6_preworker_failures_without_changing_science(self) -> None:
        v6 = json.loads(V6_PREREGISTRATION.read_text(encoding="utf-8"))
        v7 = json.loads(V7_PREREGISTRATION.read_text(encoding="utf-8"))
        self.assertEqual(v7["schema"], V7_PREREGISTRATION_SCHEMA)
        self.assertEqual(v7["preregistration_sha256"], V7_PREREGISTRATION_SHA256)
        self.assertEqual(
            sha256_file(V7_PREREGISTRATION), V7_PREREGISTRATION_FILE_SHA256
        )
        self.assertEqual(v7["supersession"], v7_preregistration_supersession())
        self.assertEqual(
            v7["post_failure_replication"],
            post_failure_replication_provenance(),
        )
        supersession = v7["supersession"]
        self.assertFalse(supersession["scientific_design_changed"])
        self.assertFalse(supersession["schedule_changed"])
        self.assertFalse(supersession["workload_changed"])
        self.assertFalse(supersession["statistics_changed"])
        self.assertTrue(supersession["witness_implementation_changed"])
        self.assertFalse(supersession["v7_is_v6_retry"])
        self.assertTrue(supersession["v7_is_append_only_full_replication"])
        self.assertFalse(supersession["v6_untimed_calls_pooled_into_v7_estimators"])
        self.assertEqual(
            supersession["v6_attempt_2"]["gpu_complete_execution_call_count"], 72
        )
        for key in (
            "scientific_question",
            "causal_estimand",
            "admission_tasks",
            "baseline_tasks",
            "task_contracts",
            "causal_arms",
            "baseline_arms",
            "cohort_boundary",
            "causal_phase_boundaries",
            "baseline_phase_boundaries",
            "cold_counterfactual_design",
            "post_estimand_reference_admission",
            "execution_identity_requirements",
            "pre_worker_zero_witness_design",
            "baseline_worker_design",
            "byte_identity_invariant",
            "byte_identity_invariant_scope",
            "causal_schedule",
            "causal_schedule_sha256",
            "baseline_schedule",
            "baseline_schedule_sha256",
            "statistics",
            "hardware_design",
            "failure_policy",
        ):
            self.assertEqual(v7[key], v6[key], key)
        artifact = ROOT / supersession["v6_preworker_artifact_path"]
        self.assertEqual(artifact.stat().st_size, 3_761)
        self.assertEqual(
            sha256_file(artifact), supersession["v6_preworker_artifact_sha256"]
        )
        with tarfile.open(artifact, "r:gz") as archive:

            def archived_bytes(name: str) -> bytes:
                extracted = archive.extractfile(name)
                self.assertIsNotNone(extracted)
                return extracted.read()

            attempt_1_marker = archived_bytes(
                "goal5842-ada-1a2b98abf-replication06/"
                "PREFLIGHT_FAILED_REPAIR_ALLOWED.json"
            )
            attempt_1_stderr = archived_bytes(
                "goal5842-ada-1a2b98abf-replication06/stage_logs/"
                "00_bind_execution_authority/stderr.txt"
            )
            attempt_2_marker = archived_bytes(
                "goal5842-ada-1a2b98abf-replication06-env02/"
                "PREFLIGHT_FAILED_REPAIR_ALLOWED.json"
            )
            attempt_2_stdout = archived_bytes(
                "goal5842-ada-1a2b98abf-replication06-env02/stage_logs/"
                "01_gpu_identity_witness_no_timing/stdout.txt"
            )
            attempt_2_stderr = archived_bytes(
                "goal5842-ada-1a2b98abf-replication06-env02/stage_logs/"
                "01_gpu_identity_witness_no_timing/stderr.txt"
            )
        for payload, expected in (
            (attempt_1_marker, supersession["v6_attempt_1"]["failure_marker_sha256"]),
            (attempt_1_stderr, supersession["v6_attempt_1"]["stderr_sha256"]),
            (attempt_2_marker, supersession["v6_attempt_2"]["failure_marker_sha256"]),
            (attempt_2_stdout, supersession["v6_attempt_2"]["stdout_sha256"]),
            (attempt_2_stderr, supersession["v6_attempt_2"]["stderr_sha256"]),
        ):
            self.assertEqual(hashlib.sha256(payload).hexdigest(), expected)
        self.assertIn(b"FileNotFoundError", attempt_1_stderr)
        self.assertIn(b"EXECUTE_CHECK_ON", attempt_2_stdout)
        self.assertIn(b"lifecycle execution count mismatch", attempt_2_stderr)
        claims = v7["claim_ceiling"]
        self.assertFalse(claims["v6_preworker_attempt_reclassified_as_success"])
        self.assertFalse(claims["v6_untimed_calls_count_as_v7_witness"])
        self.assertFalse(claims["v4_v5_or_v6_rows_pooled_into_v7_estimators"])
        self.assertFalse(claims["v7_called_a_retry_of_v6"])

    def test_v8_binds_v7_preworker_failure_without_changing_science(self) -> None:
        v7 = json.loads(V7_PREREGISTRATION.read_text(encoding="utf-8"))
        v8 = json.loads(V8_PREREGISTRATION.read_text(encoding="utf-8"))
        self.assertEqual(v8["supersession"], v8_preregistration_supersession())
        self.assertEqual(
            v8["post_failure_replication"],
            post_failure_replication_provenance(),
        )
        supersession = v8["supersession"]
        self.assertFalse(supersession["scientific_design_changed"])
        self.assertFalse(supersession["schedule_changed"])
        self.assertFalse(supersession["workload_changed"])
        self.assertFalse(supersession["statistics_changed"])
        self.assertTrue(supersession["witness_implementation_changed"])
        self.assertFalse(supersession["v8_is_v7_retry"])
        self.assertTrue(supersession["v8_is_append_only_full_replication"])
        self.assertFalse(supersession["v7_untimed_calls_pooled_into_v8_estimators"])
        self.assertEqual(supersession["gpu_complete_execution_call_count"], 72)
        for key in (
            "scientific_question",
            "causal_estimand",
            "admission_tasks",
            "baseline_tasks",
            "task_contracts",
            "causal_arms",
            "baseline_arms",
            "cohort_boundary",
            "causal_phase_boundaries",
            "baseline_phase_boundaries",
            "cold_counterfactual_design",
            "post_estimand_reference_admission",
            "execution_identity_requirements",
            "pre_worker_zero_witness_design",
            "baseline_worker_design",
            "byte_identity_invariant",
            "byte_identity_invariant_scope",
            "causal_schedule",
            "causal_schedule_sha256",
            "baseline_schedule",
            "baseline_schedule_sha256",
            "statistics",
            "hardware_design",
            "failure_policy",
        ):
            self.assertEqual(v8[key], v7[key], key)
        artifact = ROOT / supersession["v7_preworker_artifact_path"]
        self.assertEqual(artifact.stat().st_size, 3_253)
        self.assertEqual(
            sha256_file(artifact), supersession["v7_preworker_artifact_sha256"]
        )
        with tarfile.open(artifact, "r:gz") as archive:
            root = "goal5842-ada-50c0c12bf-replication07/"

            def archived_bytes(relative: str) -> bytes:
                extracted = archive.extractfile(root + relative)
                self.assertIsNotNone(extracted)
                return extracted.read()

            marker = archived_bytes("PREFLIGHT_FAILED_REPAIR_ALLOWED.json")
            authority = archived_bytes("execution_authority.json")
            stdout = archived_bytes(
                "stage_logs/01_gpu_identity_witness_no_timing/stdout.txt"
            )
            stderr = archived_bytes(
                "stage_logs/01_gpu_identity_witness_no_timing/stderr.txt"
            )
        for payload, expected in (
            (marker, supersession["failure_marker_sha256"]),
            (authority, supersession["execution_authority_sha256"]),
            (stdout, supersession["stdout_sha256"]),
            (stderr, supersession["stderr_sha256"]),
        ):
            self.assertEqual(hashlib.sha256(payload).hexdigest(), expected)
        self.assertIn(b"EXECUTE_CHECK_ON", stdout)
        self.assertIn(b"provider prepared lifecycle schema mismatch", stderr)
        claims = v8["claim_ceiling"]
        self.assertFalse(claims["v7_preworker_attempt_reclassified_as_success"])
        self.assertFalse(claims["v7_untimed_calls_count_as_v8_witness"])
        self.assertFalse(claims["v4_v5_v6_or_v7_rows_pooled_into_v8_estimators"])
        self.assertFalse(claims["v8_called_a_retry_of_v7"])

    def test_v9_binds_v8_and_discloses_fair_baseline_design_change(self) -> None:
        v8 = json.loads(V8_PREREGISTRATION.read_text(encoding="utf-8"))
        v9 = json.loads(V9_PREREGISTRATION.read_text(encoding="utf-8"))
        self.assertEqual(
            sha256_file(V8_PREREGISTRATION), V8_PREREGISTRATION_FILE_SHA256
        )
        self.assertEqual(v8["schema"], V8_PREREGISTRATION_SCHEMA)
        self.assertEqual(v8["preregistration_sha256"], V8_PREREGISTRATION_SHA256)
        self.assertEqual(v9["supersession"], v9_preregistration_supersession())
        supersession = v9["supersession"]
        self.assertTrue(supersession["scientific_design_changed"])
        self.assertFalse(supersession["causal_estimand_changed"])
        self.assertFalse(supersession["schedule_changed"])
        self.assertFalse(supersession["workload_values_changed"])
        self.assertFalse(supersession["statistics_changed"])
        self.assertTrue(supersession["witness_contract_changed"])
        self.assertTrue(supersession["baseline_timing_boundary_changed"])
        self.assertTrue(supersession["prior_partial_timing_was_available"])
        self.assertFalse(supersession["v9_is_v8_retry"])
        self.assertTrue(supersession["v9_is_append_only_new_fair_baseline_design"])
        self.assertFalse(supersession["v4_through_v8_rows_pooled_into_v9_estimators"])
        self.assertEqual(supersession["gpu_complete_execution_call_count"], 145)
        for key in (
            "scientific_question",
            "causal_estimand",
            "admission_tasks",
            "baseline_tasks",
            "causal_arms",
            "baseline_arms",
            "cohort_boundary",
            "causal_phase_boundaries",
            "baseline_phase_boundaries",
            "cold_counterfactual_design",
            "post_estimand_reference_admission",
            "execution_identity_requirements",
            "byte_identity_invariant",
            "byte_identity_invariant_scope",
            "causal_schedule",
            "causal_schedule_sha256",
            "baseline_schedule",
            "baseline_schedule_sha256",
            "statistics",
            "hardware_design",
            "failure_policy",
        ):
            self.assertEqual(v9[key], v8[key], key)
        stable_task_fields = {
            "task",
            "input_sha256",
            "full_oracle_sha256",
            "public_output_sha256",
            "primitive_count",
            "query_count",
            "three_arm_baseline_included",
        }
        for old, new in zip(v8["task_contracts"], v9["task_contracts"]):
            self.assertEqual(
                {key: old[key] for key in stable_task_fields},
                {key: new[key] for key in stable_task_fields},
            )
        artifact = ROOT / supersession["v8_preworker_artifact_path"]
        self.assertEqual(artifact.stat().st_size, 3_346)
        self.assertEqual(
            sha256_file(artifact), supersession["v8_preworker_artifact_sha256"]
        )
        with tarfile.open(artifact, "r:gz") as archive:
            root = "goal5842-ada-adb32fbb0-replication08/"

            def archived_bytes(relative: str) -> bytes:
                extracted = archive.extractfile(root + relative)
                self.assertIsNotNone(extracted)
                return extracted.read()

            marker = archived_bytes("PREFLIGHT_FAILED_REPAIR_ALLOWED.json")
            authority = archived_bytes("execution_authority.json")
            command = archived_bytes(
                "stage_logs/01_gpu_identity_witness_no_timing/command.json"
            )
            stdout = archived_bytes(
                "stage_logs/01_gpu_identity_witness_no_timing/stdout.txt"
            )
            stderr = archived_bytes(
                "stage_logs/01_gpu_identity_witness_no_timing/stderr.txt"
            )
        for payload, expected in (
            (marker, supersession["failure_marker_sha256"]),
            (authority, supersession["execution_authority_file_sha256"]),
            (command, supersession["command_sha256"]),
            (stdout, supersession["stdout_sha256"]),
            (stderr, supersession["stderr_sha256"]),
        ):
            self.assertEqual(hashlib.sha256(payload).hexdigest(), expected)
        self.assertIn(b"BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1", stdout)
        self.assertIn(b"has no attribute 'details'", stderr)
        design = v9["baseline_worker_design"]
        self.assertTrue(
            design[
                "registered_execute_interval_ends_before_experimental_oracle_comparison"
            ]
        )
        self.assertEqual(
            design["triangle_cross_arm_public_output"],
            "CHECKED_U64_WEIGHTED_SCALAR_ONLY",
        )
        claims = v9["claim_ceiling"]
        self.assertFalse(claims["v8_preworker_attempt_reclassified_as_success"])
        self.assertFalse(claims["v8_untimed_calls_count_as_v9_witness"])
        self.assertFalse(claims["v4_through_v8_rows_pooled_into_v9_estimators"])
        self.assertFalse(claims["v9_called_a_retry_of_v8"])
        self.assertFalse(claims["prior_partial_timing_hidden"])

    def test_v10_binds_v9_preexecution_source_contract_correction(self) -> None:
        v9 = json.loads(V9_PREREGISTRATION.read_text(encoding="utf-8"))
        self.assertEqual(
            sha256_file(V9_PREREGISTRATION), V9_PREREGISTRATION_FILE_SHA256
        )
        self.assertEqual(v9["schema"], V9_PREREGISTRATION_SCHEMA)
        self.assertEqual(v9["preregistration_sha256"], V9_PREREGISTRATION_SHA256)
        self.assertEqual(
            self.prereg["supersession"], v10_preregistration_supersession()
        )
        supersession = self.prereg["supersession"]
        self.assertFalse(supersession["worker_zero_reached"])
        self.assertEqual(supersession["registered_timing_observation_count"], 0)
        self.assertEqual(supersession["formal_gpu_execution_count"], 0)
        self.assertEqual(
            supersession[
                "prefreeze_unregistered_engineering_complete_execution_call_count"
            ],
            6,
        )
        self.assertEqual(
            supersession["prefreeze_unregistered_engineering_optix_launch_count"],
            8,
        )
        self.assertFalse(supersession["scientific_design_changed"])
        self.assertFalse(supersession["runtime_semantics_changed"])
        self.assertFalse(supersession["v10_is_result_dependent_retry"])
        self.assertTrue(
            supersession["v10_is_append_only_preexecution_source_contract_correction"]
        )
        self.assertFalse(supersession["v9_rows_pooled_into_v10_estimators"])
        for key in (
            "scientific_question",
            "causal_estimand",
            "admission_tasks",
            "baseline_tasks",
            "task_contracts",
            "causal_arms",
            "baseline_arms",
            "cohort_boundary",
            "causal_phase_boundaries",
            "baseline_phase_boundaries",
            "cold_counterfactual_design",
            "post_estimand_reference_admission",
            "execution_identity_requirements",
            "pre_worker_zero_witness_design",
            "baseline_worker_design",
            "byte_identity_invariant",
            "byte_identity_invariant_scope",
            "causal_schedule",
            "causal_schedule_sha256",
            "baseline_schedule",
            "baseline_schedule_sha256",
            "statistics",
            "hardware_design",
            "failure_policy",
        ):
            self.assertEqual(self.prereg[key], v9[key], key)
        changed = supersession["changed_existing_source_paths"]
        self.assertEqual(len(changed), 1)
        row = changed[0]
        path = ROOT / row["path"]
        self.assertEqual(
            row["v9_sha256"],
            "b144b9d48ba68f5dd0c9c0fbe18aacb119b0ca229dc2e28305c95d536e162019",
        )
        self.assertEqual(sha256_file(path), row["v10_sha256"])
        self.assertEqual(
            sha256_file(
                ROOT / "history/internal_docs/goal5842_causal_admission_cost_20260903/"
                "PRE_EXECUTION_INTERNAL_HOSTILE_REVIEW_V9.md"
            ),
            "c692655f54e8be377c5d8d4d727ba1720b487cbbbad61bec35dd8d092285f4cd",
        )
        self.assertEqual(
            self.prereg["gpu_execution_count_scope"],
            "FORMAL_V10_TRANSACTION_ONLY",
        )
        self.assertEqual(
            self.prereg["unregistered_engineering_preflight"],
            {
                "complete_execution_call_count": 6,
                "optix_launch_count": 8,
                "registered_timing_observation_count": 0,
                "timings_retained_or_used": False,
                "included_in_estimators": False,
            },
        )

    def test_gpu_entrypoints_bind_legacy_loader_to_authorized_native(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            native = Path(temporary) / "librtdl_optix.so"
            native.write_bytes(b"test native identity")
            authority = {"execution_paths": {"native_library": str(native.resolve())}}
            environment = {
                "RTDL_OPTIX_LIB": "/untrusted/ambient.so",
                "RTDL_OPTIX_LIBRARY": "/untrusted/ambient.so",
            }
            observed = bind_authorized_native_library(
                authority, native, environment=environment
            )
            self.assertEqual(observed, native.resolve())
            self.assertEqual(
                environment,
                {
                    "RTDL_OPTIX_LIB": str(native.resolve()),
                    "RTDL_OPTIX_LIBRARY": str(native.resolve()),
                },
            )
        for relative in (
            "scripts/goal5842_gpu_identity_witness.py",
            "experiments/goal5842_causal_admission/baseline_worker.py",
        ):
            self.assertIn(
                "bind_authorized_native_library",
                (ROOT / relative).read_text(encoding="utf-8"),
            )

    def test_one_generation_runner_preserves_virtualenv_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base = root / "base-python"
            base.write_text("#!/bin/sh\nexit 0\n", encoding="ascii")
            base.chmod(0o755)
            launcher = root / "venv" / "bin" / "python"
            launcher.parent.mkdir(parents=True)
            launcher.symlink_to(base)
            self.assertEqual(
                validated_python_entrypoint(str(launcher)),
                os.path.abspath(launcher),
            )
            self.assertNotEqual(
                validated_python_entrypoint(str(launcher)),
                str(base.resolve()),
            )

    def test_causal_schedule_is_balanced_abba_baab(self) -> None:
        schedule = build_causal_schedule()
        self.assertEqual(schedule, self.prereg["causal_schedule"])
        counts = Counter((row["task"], row["arm"]) for row in schedule)
        self.assertEqual(set(counts.values()), {CAUSAL_BLOCKS * 2})
        for task in ADMISSION_TASKS:
            for block in range(CAUSAL_BLOCKS):
                rows = [
                    row
                    for row in schedule
                    if row["task"] == task and row["block"] == block
                ]
                self.assertEqual(
                    Counter(row["arm"] for row in rows), {CHECK_ON: 2, CHECK_OFF: 2}
                )
                self.assertIn(
                    tuple(row["arm"] for row in rows),
                    {
                        (CHECK_ON, CHECK_OFF, CHECK_OFF, CHECK_ON),
                        (CHECK_OFF, CHECK_ON, CHECK_ON, CHECK_OFF),
                    },
                )

    def test_baseline_schedule_balances_three_arms_and_two_tasks(self) -> None:
        schedule = build_baseline_schedule()
        self.assertEqual(schedule, self.prereg["baseline_schedule"])
        counts = Counter((row["task"], row["arm"]) for row in schedule)
        self.assertEqual(
            set(counts),
            {(task, arm) for task in BASELINE_TASKS for arm in BASELINE_ARMS},
        )
        self.assertEqual(set(counts.values()), {BASELINE_BLOCKS})

    def test_three_routes_admit_and_counterfactual_is_identity_exact(self) -> None:
        signatures = {}
        for task_id in ADMISSION_TASKS:
            with self.subTest(task=task_id):
                task = build_task(task_id)
                route = task.route_factory()
                admitted = route.compile()
                bypass = checker_off_program(route)
                self.assertEqual(program_signature(admitted), program_signature(bypass))
                signatures[task_id] = program_signature(admitted)["plan_sha256"]
        self.assertEqual(len(set(signatures.values())), 3)

    def test_task_contracts_match_live_deterministic_inputs_and_oracles(self) -> None:
        for contract in TASK_CONTRACTS:
            with self.subTest(task=contract["task"]):
                task = build_task(contract["task"])
                self.assertEqual(task.input_sha256, contract["input_sha256"])
                self.assertEqual(
                    digest(task.expected_output), contract["full_oracle_sha256"]
                )
                public_output = (
                    task.expected_output["weighted_sum"]
                    if contract["task"] == TRIANGLE_TASK
                    else task.expected_output
                )
                self.assertEqual(
                    digest(public_output), contract["public_output_sha256"]
                )
                if task.provider_fixture is None:
                    primitive_count = query_count = SPHERE_SIZE
                elif contract["task"] == TRIANGLE_TASK:
                    primitive_count = len(task.provider_fixture["vertices"]) // 3
                    query_count = len(task.provider_fixture["rays"])
                else:
                    primitive_count = len(task.provider_fixture["indexed"])
                    query_count = len(task.provider_fixture["sources"])
                self.assertEqual(primitive_count, contract["primitive_count"])
                self.assertEqual(query_count, contract["query_count"])
                self.assertEqual(
                    contract["three_arm_baseline_included"],
                    contract["task"] in BASELINE_TASKS,
                )

    def test_sphere_fixture_is_deterministic_one_to_one_by_construction(self) -> None:
        first = sphere_workload()
        second = sphere_workload()
        self.assertEqual(first, second)
        self.assertEqual(SPHERE_SIZE, 1_024)
        self.assertEqual(SPHERE_SIZE * SPHERE_SIZE, 1_048_576)
        self.assertEqual(len(first["centers"]), SPHERE_SIZE)
        self.assertEqual(first["expected_counts"], (1,) * SPHERE_SIZE)
        for index in (0, 1, SPHERE_SIZE // 2, SPHERE_SIZE - 1):
            center = first["centers"][index]
            query = first["queries"][index]
            self.assertEqual(center[0], float(4 * index))
            self.assertEqual(query[0][0], center[0])
            self.assertEqual(query[1][0], center[0])
            self.assertLess(query[0][2], center[2])
            self.assertGreater(query[1][2], center[2])

    def test_sphere_is_not_fabricated_as_provider_baseline(self) -> None:
        self.assertNotIn("BUILTIN_SPHERE_ANY_HIT_COUNT_V1", BASELINE_TASKS)
        boundary = self.prereg["cohort_boundary"]
        self.assertEqual(
            boundary["sphere_provider_baseline_timing"],
            "EXCLUDED_NO_INDEPENDENT_EXACT_COMPARATOR",
        )

    def test_claim_ceiling_forbids_public_checker_bypass_and_overattribution(
        self,
    ) -> None:
        claims = self.prereg["claim_ceiling"]
        self.assertFalse(claims["checker_off_is_public_api"])
        self.assertFalse(claims["checker_off_is_safe_for_users"])
        self.assertFalse(claims["checker_off_is_supported_optimization"])
        self.assertTrue(claims["checker_off_is_experiment_only_counterfactual"])
        self.assertTrue(claims["materialization_still_revalidates_identity"])
        self.assertFalse(claims["admission_delta_explains_entire_setup_gap"])
        self.assertFalse(claims["external_review_or_consensus"])

    def test_identity_and_schedule_mutations_fail_closed(self) -> None:
        attacks = []
        dropped = deepcopy(self.prereg)
        dropped["causal_schedule"].pop()
        dropped["causal_schedule_sha256"] = digest(dropped["causal_schedule"])
        _reseal(dropped)
        attacks.append(dropped)
        identity = deepcopy(self.prereg)
        identity["byte_identity_invariant"]["composed_ptx"] = "SEMANTIC_ONLY"
        _reseal(identity)
        attacks.append(identity)
        threshold = deepcopy(self.prereg)
        threshold["statistics"]["success_threshold"] = 1.05
        _reseal(threshold)
        attacks.append(threshold)
        public_bypass = deepcopy(self.prereg)
        public_bypass["claim_ceiling"]["checker_off_is_public_api"] = True
        _reseal(public_bypass)
        attacks.append(public_bypass)
        warmed = deepcopy(self.prereg)
        warmed["cold_counterfactual_design"]["pre_timing_public_admission"] = True
        _reseal(warmed)
        attacks.append(warmed)
        changed_primary = deepcopy(self.prereg)
        changed_primary["statistics"]["primary_summary"] = (
            "median_of_total_process_wall"
        )
        _reseal(changed_primary)
        attacks.append(changed_primary)
        one_generation = deepcopy(self.prereg)
        one_generation["hardware_design"][
            "minimum_distinct_gpu_architecture_generations"
        ] = 1
        _reseal(one_generation)
        attacks.append(one_generation)
        fake_optimization = deepcopy(self.prereg)
        fake_optimization["claim_ceiling"]["checker_off_is_supported_optimization"] = (
            True
        )
        _reseal(fake_optimization)
        attacks.append(fake_optimization)
        pooled_prior = deepcopy(self.prereg)
        pooled_prior["claim_ceiling"]["v4_or_v5_rows_pooled_into_v6_estimators"] = True
        _reseal(pooled_prior)
        attacks.append(pooled_prior)
        hidden_failure = deepcopy(self.prereg)
        hidden_failure["post_failure_replication"]["v5_worker_zero_reached"] = False
        _reseal(hidden_failure)
        attacks.append(hidden_failure)
        swapped_input = deepcopy(self.prereg)
        swapped_input["task_contracts"][0]["input_sha256"] = "f" * 64
        _reseal(swapped_input)
        attacks.append(swapped_input)
        omitted_source = deepcopy(self.prereg)
        omitted_source["source_manifest"].pop()
        omitted_source["source_manifest_sha256"] = digest(
            omitted_source["source_manifest"]
        )
        _reseal(omitted_source)
        attacks.append(omitted_source)
        for attack in attacks:
            with self.assertRaises(Goal5842ContractError):
                validate_preregistration(attack, ROOT, verify_files=False)

    def test_counterfactual_private_token_is_confined_to_experiment(self) -> None:
        product_offenders = []
        for path in (ROOT / "src" / "rtdsl").glob("*.py"):
            source = path.read_text(encoding="utf-8")
            if "goal5842_causal_admission" in source or "checker_off_program" in source:
                product_offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(product_offenders, [])
        experiment_token_users = []
        for path in (ROOT / "experiments/goal5842_causal_admission").glob("*.py"):
            if "_CONSTRUCTION_TOKEN" in path.read_text(encoding="utf-8"):
                experiment_token_users.append(path.name)
        self.assertEqual(experiment_token_users, ["tasks.py"])
        source = (ROOT / "experiments/goal5842_causal_admission/tasks.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("experiment-only unchecked counterfactual", source)
        self.assertIn("_CONSTRUCTION_TOKEN", source)

    def test_causal_worker_has_no_pretiming_public_admission(self) -> None:
        source = (
            ROOT / "experiments/goal5842_causal_admission/admission_worker.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("reference_route", source)
        registered_start = source.index("gc.collect()")
        post_reference = source.index("reference_program = route.compile()")
        receipt = source.index("receipt: dict[str, object]")
        self.assertLess(registered_start, post_reference)
        self.assertLess(post_reference, receipt)
        self.assertIn("checker_off_program(route)", source)
        self.assertNotIn("checker_off_program(route,", source)

    def test_no_frozen_core_edit_is_part_of_goal5842_source_additions(self) -> None:
        pins = {row["path"] for row in self.prereg["source_manifest"]}
        self.assertTrue(set(FROZEN_CORE) <= pins)
        generator = ast.parse(
            (ROOT / "scripts/goal5842_build_preregistration.py").read_text(
                encoding="utf-8"
            )
        )
        calls = [node for node in ast.walk(generator) if isinstance(node, ast.Call)]
        self.assertFalse(
            any(
                isinstance(node.func, ast.Attribute)
                and node.func.attr in {"perf_counter", "perf_counter_ns"}
                for node in calls
            )
        )

    def test_causal_summary_uses_absolute_within_block_delta(self) -> None:
        receipts = []
        for row in self.prereg["causal_schedule"]:
            phases = {
                "route_declaration_and_artifact_binding": 200 + row["block"],
                "provider_projection_and_public_admission_or_unchecked_construction": (
                    1_100 + row["block"]
                    if row["arm"] == CHECK_ON
                    else 100 + row["block"]
                ),
            }
            receipts.append(
                {
                    **row,
                    "phases_ns": phases,
                    "registered_admission_total_ns": sum(phases.values()),
                }
            )
        summaries = summarize(receipts)
        self.assertEqual(summaries, independently_summarize_causal(receipts))
        self.assertEqual(len(summaries), len(ADMISSION_TASKS))
        for row in summaries:
            self.assertEqual(row["primary_causal_phase_delta_median_ns"], 1_000)
            self.assertEqual(
                row["primary_causal_phase_delta_bootstrap_95_percent_ns"],
                [1_000, 1_000],
            )
            self.assertEqual(
                row["route_declaration_negative_control_delta_median_ns"], 0
            )
            self.assertEqual(row["secondary_total_capability_delta_median_ns"], 1_000)
            self.assertFalse(row["ratio_to_check_off_reported"])

    def test_baseline_summary_recounts_all_three_arms_independently(self) -> None:
        values = {
            "A_DIRECT_CUDA_OPTIX": (50, 20, 10),
            "B_CURRENT_NVIDIA_PYOPTIX_COMPATIBLE_API": (100, 40, 20),
            "D_RTDL_PUBLIC_CHECK_ON": (200, 80, 40),
        }
        composites = []
        for row in self.prereg["baseline_schedule"]:
            setup, first, steady = values[row["arm"]]
            phases = {
                "deterministic_input_materialization": 7,
                "route_declaration_and_artifact_binding": None,
                "provider_projection_and_generic_family_admission": None,
                "runtime_target_and_toolchain_binding": None,
                "device_compile": 1,
                "module_program_pipeline_sbt": 1,
                "target_materialization": setup - 2,
                "native_prepare": 2,
                "first_complete_execution": first,
                "steady_complete_execution": [],
                "close": None if row["arm"] == "A_DIRECT_CUDA_OPTIX" else 3,
            }
            composites.append(
                {
                    "task": row["task"],
                    "arm": row["arm"],
                    "block": row["block"],
                    "setup_total_ns": setup,
                    "first_complete_execution_ns": first,
                    "steady_complete_execution_median_ns": steady,
                    "first_phases_ns": phases,
                }
            )
        controller = summarize_baselines(composites)
        independent = independently_summarize_baselines(composites)
        self.assertEqual(controller, independent)
        for task in controller:
            ratios = {
                (row["denominator"], row["metric"]): row["median_ratio"]
                for row in task["comparisons"]
            }
            self.assertEqual(
                ratios[("B_CURRENT_NVIDIA_PYOPTIX_COMPATIBLE_API", "setup_total_ns")],
                2.0,
            )
            self.assertEqual(ratios[("A_DIRECT_CUDA_OPTIX", "setup_total_ns")], 4.0)

    def test_admission_workers_are_gpu_free_and_witness_is_timer_free(self) -> None:
        worker = (
            ROOT / "experiments/goal5842_causal_admission/admission_worker.py"
        ).read_text(encoding="utf-8")
        worker_tree = ast.parse(worker)
        imported = set()
        for node in ast.walk(worker_tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertTrue(imported.isdisjoint({"cupy", "numba", "torch"}))
        self.assertNotIn("optix_runtime", worker)
        for relative in (
            "scripts/goal5842_gpu_identity_witness.py",
            "scripts/goal5842_pyoptix_identity_witness.py",
            "scripts/goal5842_direct_identity_witness.py",
        ):
            witness = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
            self.assertFalse(
                any(
                    isinstance(node, ast.Attribute)
                    and node.attr in {"perf_counter", "perf_counter_ns", "monotonic_ns"}
                    for node in ast.walk(witness)
                ),
                relative,
            )
            self.assertFalse(
                any(
                    isinstance(node, (ast.Import, ast.ImportFrom))
                    and (
                        any(alias.name == "time" for alias in node.names)
                        if isinstance(node, ast.Import)
                        else node.module == "time"
                    )
                    for node in ast.walk(witness)
                ),
                relative,
            )
        runner = (ROOT / "scripts/goal5842_run_one_generation.py").read_text(
            encoding="utf-8"
        )
        pyoptix_gate = runner.index("02_pyoptix_identity_witness_no_timing")
        direct_gate = runner.index("03_direct_identity_witness_no_timing")
        worker_zero = runner.index("04_causal_admission")
        self.assertLess(pyoptix_gate, worker_zero)
        self.assertLess(direct_gate, worker_zero)
        pyoptix_source = (
            ROOT / "scripts/goal5842_pyoptix_identity_witness.py"
        ).read_text(encoding="utf-8")
        self.assertEqual(pyoptix_source.count("baseline.compile_ptx("), 1)
        self.assertIn("ptx=ptx", pyoptix_source)

    def test_pyoptix_identity_witness_validator_fails_closed(self) -> None:
        authority = {
            "source_commit": "a" * 40,
            "authority_sha256": "b" * 64,
            "hardware": {"gpu_uuid": "GPU-TEST"},
            "pyoptix": {"repository_commit": "c" * 40},
            "execution_paths": {"device_source_sha256": "d" * 64},
            "toolchain": {"optix_sdk": "9.0.0"},
        }
        contracts = {row["task"]: row for row in self.prereg["task_contracts"]}
        rows = [
            {
                "task": task,
                "input_sha256": contracts[task]["input_sha256"],
                "output_sha256": contracts[task]["public_output_sha256"],
                "public_output_contract_id": contracts[task][
                    "public_output_contract_id"
                ],
                "full_oracle_sha256": contracts[task]["full_oracle_sha256"],
                "full_oracle_exact": True,
                "device_source_sha256": "d" * 64,
                "ptx_sha256": "e" * 64,
                "pyoptix_repository_commit": "c" * 40,
                "optix_api_version": "9.0.0",
                "complete_execution_call_count": 72,
            }
            for task in BASELINE_TASKS
        ]
        witness = {
            "schema": "rtdl.goal5842.pyoptix_identity_witness.v3",
            "status": (
                "PASS__PYOPTIX_PACKAGE_FRONT_DOOR_REPEATED_LIFECYCLE_NO_TIMING_OBSERVED"
            ),
            "source_commit": "a" * 40,
            "preregistration_sha256": self.prereg["preregistration_sha256"],
            "execution_authority_sha256": "b" * 64,
            "hardware": authority["hardware"],
            "tasks": rows,
            "task_count": 2,
            "gpu_complete_execution_call_count": 144,
            "optix_launch_count": 216,
            "registered_timing_observation_count": 0,
            "clock_api_called_by_witness_module": False,
            "duration_field_count": 0,
            "performance_claim_authorized": False,
        }
        witness["witness_sha256"] = digest(witness)
        validate_pyoptix_identity_witness(witness, self.prereg, authority)
        attacked = deepcopy(witness)
        attacked["registered_timing_observation_count"] = 1
        attacked.pop("witness_sha256")
        attacked["witness_sha256"] = digest(attacked)
        with self.assertRaisesRegex(RuntimeError, "contains timing"):
            validate_pyoptix_identity_witness(attacked, self.prereg, authority)
        hidden_duration = deepcopy(witness)
        hidden_duration["tasks"][0]["duration_ns"] = 1
        hidden_duration.pop("witness_sha256")
        hidden_duration["witness_sha256"] = digest(hidden_duration)
        with self.assertRaisesRegex(RuntimeError, "task field set mismatch"):
            validate_pyoptix_identity_witness(hidden_duration, self.prereg, authority)
        split_ptx = deepcopy(witness)
        split_ptx["tasks"][1]["ptx_sha256"] = "f" * 64
        split_ptx.pop("witness_sha256")
        split_ptx["witness_sha256"] = digest(split_ptx)
        with self.assertRaisesRegex(RuntimeError, "PTX identity differs"):
            validate_pyoptix_identity_witness(split_ptx, self.prereg, authority)

    def test_rtdl_identity_witness_validator_requires_repeated_lifecycle(self) -> None:
        authority = {
            "source_commit": "a" * 40,
            "authority_sha256": "b" * 64,
            "hardware": {"gpu_uuid": "GPU-TEST"},
            "execution_paths": {"native_library_sha256": "c" * 64},
        }
        rows = []
        for contract in self.prereg["task_contracts"]:
            calls = 1 if contract["task"].endswith("SPHERE_ANY_HIT_COUNT_V1") else 72
            provider_schema = (
                "rtdl.v4.prepared_builtin_sphere_owner.v1"
                if contract["task"].endswith("SPHERE_ANY_HIT_COUNT_V1")
                else "rtdl.v4.public_protocol_lifecycle.v1"
            )
            arm = {
                "output": None,
                "output_sha256": contract["public_output_sha256"],
                "public_output_contract_id": contract["public_output_contract_id"],
                "public_output_oracle_exact": True,
                "traversal_receipt_sha256": "d" * 64,
                "physical_executor_classification": "optix_traversal_observed",
                "complete_execution_call_count": calls,
                "generic_lifecycle_schema": "rtdl.generic_family_lifecycle.v1",
                "provider_lifecycle_schema": provider_schema,
                "prepared_lifecycle_execution_count": calls,
            }
            rows.append(
                {
                    "task": contract["task"],
                    "input_sha256": contract["input_sha256"],
                    "program_signature": {},
                    "executable_identity": {},
                    "on": deepcopy(arm),
                    "off": deepcopy(arm),
                    "auxiliary_full_oracle": (
                        {
                            "scope": (
                                "NON_PUBLIC_PROVIDER_PER_RAY_VECTOR_PLUS_PUBLIC_"
                                "WEIGHTED_SCALAR"
                            ),
                            "full_oracle_sha256": contract["full_oracle_sha256"],
                            "full_oracle_exact": True,
                            "complete_execution_call_count": 1,
                            "physical_executor_classification": (
                                "optix_traversal_observed"
                            ),
                            "output_sha256": contract["public_output_sha256"],
                            "traversal_receipt_sha256": "e" * 64,
                        }
                        if contract["task"] == TRIANGLE_TASK
                        else None
                    ),
                    "exact_identity_equal": True,
                }
            )
        witness = {
            "schema": "rtdl.goal5842.gpu_identity_witness.v5",
            "status": "PASS__IDENTITY_AND_REPEATED_LIFECYCLE_NO_TIMING_OBSERVED",
            "source_commit": "a" * 40,
            "preregistration_sha256": self.prereg["preregistration_sha256"],
            "execution_authority_sha256": "b" * 64,
            "hardware": authority["hardware"],
            "native_library_sha256": "c" * 64,
            "tasks": rows,
            "task_count": 3,
            "all_exact_identity_equal": True,
            "registered_timing_observation_count": 0,
            "generic_public_complete_execution_call_count": 290,
            "auxiliary_full_oracle_complete_execution_call_count": 1,
            "gpu_complete_execution_call_count": 291,
            "repeated_lifecycle_calls_per_baseline_task_arm": 72,
            "clock_api_called_by_witness_module": False,
            "duration_field_count": 0,
            "performance_claim_authorized": False,
        }
        witness["witness_sha256"] = digest(witness)
        validate_identity_witness(witness, self.prereg, authority)

        wrong_count = deepcopy(witness)
        wrong_count["tasks"][0]["on"]["complete_execution_call_count"] = 71
        wrong_count.pop("witness_sha256")
        wrong_count["witness_sha256"] = digest(wrong_count)
        with self.assertRaisesRegex(RuntimeError, "lifecycle count mismatch"):
            validate_identity_witness(wrong_count, self.prereg, authority)

        hidden_timing = deepcopy(witness)
        hidden_timing["tasks"][0]["on"]["duration_ns"] = 1
        hidden_timing.pop("witness_sha256")
        hidden_timing["witness_sha256"] = digest(hidden_timing)
        with self.assertRaisesRegex(RuntimeError, "field set mismatch"):
            validate_identity_witness(hidden_timing, self.prereg, authority)

    def test_generic_triangle_witness_uses_public_scalar_without_details(self) -> None:
        weighted = 17
        result = SimpleNamespace(
            output=weighted,
            output_sha256=digest(weighted),
            traversal_receipt={
                "physical_executor_classification": "optix_traversal_observed"
            },
        )

        class Prepared:
            def __init__(self) -> None:
                self.calls = 0

            def execute(self, batch: object) -> object:
                self.calls += 1
                return result

            @property
            def lifecycle_receipt(self) -> dict[str, object]:
                return {
                    "schema": "rtdl.generic_family_lifecycle.v1",
                    "provider_receipt": {
                        "schema": "rtdl.v4.public_protocol_lifecycle.v1",
                        "execution_count": self.calls,
                    },
                }

        task = SimpleNamespace(
            task_id=TRIANGLE_TASK,
            batch=object(),
            expected_output={"weighted_sum": weighted, "per_ray": (1, 1)},
        )
        observed = execute_and_check(Prepared(), task, 2)
        self.assertEqual(observed["output"], weighted)
        self.assertEqual(observed["output_sha256"], digest(weighted))
        self.assertEqual(
            observed["public_output_contract_id"],
            "checked_u64_weighted_scalar.v1",
        )
        self.assertTrue(observed["public_output_oracle_exact"])
        self.assertNotIn("full_output_sha256", observed)

    def test_v9_baseline_checks_public_output_without_fabricated_per_ray(self) -> None:
        expected = {"weighted_sum": 23, "per_ray": (7, 8)}
        self.assertEqual(
            verify_public_output(TRIANGLE_TASK, {"weighted_sum": 23}, expected),
            digest(23),
        )
        worker = (
            ROOT / "experiments/goal5842_causal_admission/baseline_worker.py"
        ).read_text(encoding="utf-8")
        direct = (
            ROOT / "experiments/goal5798_premeasurement/direct_measurement.cpp"
        ).read_text(encoding="utf-8")
        pyoptix = (
            ROOT / "experiments/goal5798_premeasurement/pyoptix_worker.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn('"per_ray": task.expected_output["per_ray"]', worker)
        self.assertIn("GOAL5842_PUBLIC_OUTPUT_V1", direct)
        self.assertIn("GOAL5842_WITNESS_NO_TIMING_V1", direct)
        self.assertIn('args.mode == "CORRECTNESS_WITNESS_NO_TIMING"', direct)
        self.assertIn("const auto duration = elapsed_ns(start);", direct)
        self.assertIn("if (goal5842_public)", direct)
        self.assertIn("public_output_only: bool = False", pyoptix)
        self.assertIn("public_output_only=True", worker)

    def test_direct_identity_witness_validator_requires_full_oracle_and_no_timing(
        self,
    ) -> None:
        authority = {
            "source_commit": "a" * 40,
            "authority_sha256": "b" * 64,
            "hardware": {"gpu_uuid": "GPU-TEST"},
            "execution_paths": {
                "direct_binary_sha256": "c" * 64,
                "device_source_sha256": "d" * 64,
            },
        }
        rows = []
        for contract in self.prereg["task_contracts"]:
            if not contract["three_arm_baseline_included"]:
                continue
            rows.append(
                {
                    "task": contract["task"],
                    "input_sha256": contract["input_sha256"],
                    "public_output_sha256": contract["public_output_sha256"],
                    "full_oracle_sha256": contract["full_oracle_sha256"],
                    "full_oracle_exact": True,
                    "gpu_complete_execution_call_count": 1,
                    "optix_launch_count": (
                        2 if contract["task"].startswith("CUSTOM_AABB") else 1
                    ),
                }
            )
        witness = {
            "schema": DIRECT_IDENTITY_WITNESS_SCHEMA,
            "status": "PASS__DIRECT_FULL_ORACLE_NO_TIMING_OBSERVED",
            "source_commit": "a" * 40,
            "preregistration_sha256": self.prereg["preregistration_sha256"],
            "execution_authority_sha256": "b" * 64,
            "hardware": authority["hardware"],
            "direct_binary_sha256": "c" * 64,
            "device_source_sha256": "d" * 64,
            "tasks": rows,
            "task_count": 2,
            "gpu_complete_execution_call_count": 2,
            "optix_launch_count": 3,
            "registered_timing_observation_count": 0,
            "clock_api_called_by_witness_module": False,
            "clock_api_called_by_direct_witness_path": False,
            "duration_field_count": 0,
            "performance_claim_authorized": False,
        }
        witness["witness_sha256"] = digest(witness)
        validate_direct_identity_witness(witness, self.prereg, authority)
        attacked = deepcopy(witness)
        attacked["tasks"][1]["full_oracle_exact"] = False
        attacked.pop("witness_sha256")
        attacked["witness_sha256"] = digest(attacked)
        with self.assertRaisesRegex(RuntimeError, "oracle/call count mismatch"):
            validate_direct_identity_witness(attacked, self.prereg, authority)

    def test_provider_lifecycle_evidence_requires_nested_provider_receipt(
        self,
    ) -> None:
        lifecycle = {
            "schema": "rtdl.generic_family_lifecycle.v1",
            "provider_receipt": {
                "schema": "rtdl.v4.public_protocol_lifecycle.v1",
                "execution_count": 72,
            },
        }
        self.assertEqual(
            provider_lifecycle_evidence(
                lifecycle,
                expected_execution_count=72,
                expected_provider_schema=("rtdl.v4.public_protocol_lifecycle.v1"),
            ),
            {
                "generic_lifecycle_schema": "rtdl.generic_family_lifecycle.v1",
                "provider_lifecycle_schema": ("rtdl.v4.public_protocol_lifecycle.v1"),
                "prepared_lifecycle_execution_count": 72,
            },
        )
        top_level_only = {
            "schema": "rtdl.generic_family_lifecycle.v1",
            "execution_count": 72,
        }
        with self.assertRaisesRegex(TypeError, "provider receipt is missing"):
            provider_lifecycle_evidence(
                top_level_only,
                expected_execution_count=72,
                expected_provider_schema=("rtdl.v4.public_protocol_lifecycle.v1"),
            )
        wrong_provider = deepcopy(lifecycle)
        wrong_provider["provider_receipt"]["schema"] = "wrong"
        with self.assertRaisesRegex(RuntimeError, "provider.*schema mismatch"):
            provider_lifecycle_evidence(
                wrong_provider,
                expected_execution_count=72,
                expected_provider_schema=("rtdl.v4.public_protocol_lifecycle.v1"),
            )

    def test_relation_triangle_provider_schema_is_the_public_protocol_owner(
        self,
    ) -> None:
        from types import SimpleNamespace

        from rtdsl.v4_callback_lifecycle import (
            PreparedProtocolProgram,
            ProtocolFamily,
        )

        owner = SimpleNamespace(prepare_seconds=0.0, close=lambda: None)
        identity = SimpleNamespace(identity_sha256="a" * 64)
        decision = SimpleNamespace(
            verdict="ACCEPT",
            to_mapping=lambda: {"decision_sha256": "b" * 64},
        )
        prepared = PreparedProtocolProgram(
            family=ProtocolFamily.BOUNDED_RELATION,
            owner=owner,
            identity=identity,
            materialize_seconds=0.0,
            protocol_contract_decision=decision,
        )
        try:
            self.assertEqual(
                prepared.lifecycle_receipt["schema"],
                "rtdl.v4.public_protocol_lifecycle.v1",
            )
        finally:
            prepared.close()

    def test_architecture_generation_is_explicit_and_unknown_fails_closed(self) -> None:
        self.assertEqual(architecture_generation("7.5"), "TURING")
        self.assertEqual(architecture_generation("8.6"), "AMPERE")
        self.assertEqual(architecture_generation("8.9"), "ADA")
        self.assertEqual(architecture_generation("9.0"), "HOPPER")
        self.assertEqual(architecture_generation("10.0"), "BLACKWELL")
        with self.assertRaisesRegex(RuntimeError, "unregistered compute capability"):
            architecture_generation("99.9")

    def test_final_source_manifest_contains_every_formal_entrypoint(self) -> None:
        paths = {row["path"] for row in self.prereg["source_manifest"]}
        self.assertTrue(
            {
                "experiments/goal5842_causal_admission/admission_worker.py",
                "experiments/goal5842_causal_admission/controller.py",
                "experiments/goal5842_causal_admission/baseline_controller.py",
                "experiments/goal5842_causal_admission/baseline_worker.py",
                "experiments/goal5842_causal_admission/runtime.py",
                "scripts/goal5842_bind_execution_authority.py",
                "scripts/goal5842_build_cross_generation_authority.py",
                "scripts/goal5842_direct_identity_witness.py",
                "scripts/goal5842_gpu_identity_witness.py",
                "scripts/goal5842_pyoptix_identity_witness.py",
                "scripts/goal5842_independent_recount.py",
                "scripts/goal5842_run_one_generation.py",
                "experiments/goal5796_matched/matched_device.cu",
                V3_PREREGISTRATION_PATH,
                V8_PREREGISTRATION_PATH,
                (
                    "history/internal_docs/goal5842_causal_admission_cost_20260903/"
                    "PRE_WORKER_ZERO_REPAIR_03.md"
                ),
                (
                    "history/internal_docs/goal5842_causal_admission_cost_20260903/"
                    "PRE_EXECUTION_INTERNAL_HOSTILE_REVIEW_V6.md"
                ),
            }
            <= paths
        )

    def test_pyoptix_worker_does_not_hide_second_input_construction(self) -> None:
        source = (
            ROOT / "experiments/goal5842_causal_admission/baseline_worker.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("relation_workload()", source)
        self.assertNotIn("triangle_workload()", source)
        for task_id in BASELINE_TASKS:
            task = build_task(task_id)
            self.assertIsInstance(task.provider_fixture, dict)

    def test_pyoptix_worker_is_importable_through_package_front_door(self) -> None:
        module = importlib.import_module(
            "experiments.goal5798_premeasurement.pyoptix_worker"
        )
        self.assertTrue(hasattr(module, "PyOptixRelationPrepared"))
        self.assertTrue(hasattr(module, "PyOptixTrianglePrepared"))
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "experiments/goal5798_premeasurement/pyoptix_worker.py"),
                "--help",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_direct_worker_constants_match_frozen_task_sizes_and_sampling(self) -> None:
        source = (
            ROOT / "experiments/goal5798_premeasurement/direct_measurement.cpp"
        ).read_text(encoding="utf-8")
        for fragment in (
            "kRelationSize = 4096",
            "kTriangleSize = 16384",
            "kWarmups = 8",
            "kTimed = 64",
            "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1",
            "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1",
        ):
            self.assertIn(fragment, source)

    def test_cross_generation_gate_rejects_one_or_duplicate_generation(self) -> None:
        def recount(generation: str, uuid: str) -> dict[str, object]:
            value: dict[str, object] = {
                "schema": INDEPENDENT_RECOUNT_SCHEMA,
                "status": "PASS__ONE_GPU_GENERATION_RECOUNT_COMPLETE",
                "source_commit": "a" * 40,
                "preregistration_sha256": "b" * 64,
                "hardware": {"gpu_uuid": uuid, "gpu_model": generation},
                "architecture_generation": generation,
                "causal_result_sha256": "c" * 64,
                "baseline_result_sha256": "d" * 64,
                "cross_generation_gate_passed": False,
                "public_performance_claim_authorized": False,
            }
            value["recount_sha256"] = digest(value)
            return value

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = []
            for index, value in enumerate(
                (
                    recount("ADA", "GPU-ADA"),
                    recount("ADA", "GPU-ADA-2"),
                    recount("AMPERE", "GPU-AMPERE"),
                )
            ):
                path = root / f"recount-{index}.json"
                path.write_text(json.dumps(value), encoding="utf-8")
                paths.append(path)
            with self.assertRaisesRegex(RuntimeError, "at least two"):
                build_cross_generation_authority(paths[:1])
            with self.assertRaisesRegex(RuntimeError, "two GPU generations"):
                build_cross_generation_authority(paths[:2])
            duplicate_uuid = root / "recount-duplicate-uuid.json"
            duplicate_uuid.write_text(
                json.dumps(recount("AMPERE", "GPU-ADA")), encoding="utf-8"
            )
            with self.assertRaisesRegex(RuntimeError, "physical GPU"):
                build_cross_generation_authority([paths[0], duplicate_uuid])
            authority = build_cross_generation_authority((paths[0], paths[2]))
            self.assertEqual(authority["schema"], CROSS_GENERATION_AUTHORITY_SCHEMA)
            self.assertEqual(authority["generation_count"], 2)
            self.assertFalse(authority["cross_machine_raw_time_ratios_computed"])
            self.assertFalse(authority["public_performance_claim_authorized"])

    def test_independent_recount_rebuilds_complete_synthetic_transactions(self) -> None:
        def write(path: Path, value: dict[str, object]) -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value), encoding="utf-8")

        authority = {
            "authority_sha256": "e" * 64,
            "source_commit": "a" * 40,
            "hardware": {"gpu_uuid": "GPU-SYNTHETIC", "gpu_model": "SYNTHETIC"},
        }
        signatures = {
            task: {
                "plan_sha256": f"{index + 1:x}" * 64,
                "artifacts_sha256": f"{index + 4:x}" * 64,
                "provider_projection_sha256": f"{index + 7:x}" * 64,
                "provider_descriptor_sha256": f"{index + 10:x}" * 64,
            }
            for index, task in enumerate(ADMISSION_TASKS)
        }
        contracts = {row["task"]: row for row in TASK_CONTRACTS}
        inputs = {task: contracts[task]["input_sha256"] for task in ADMISSION_TASKS}
        outputs = {
            task: contracts[task]["public_output_sha256"] for task in BASELINE_TASKS
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            causal_root = root / "causal"
            causal_receipts = []
            for index, row in enumerate(self.prereg["causal_schedule"]):
                phases = {
                    "route_declaration_and_artifact_binding": (
                        1_000 + row["block"] if row["arm"] == CHECK_ON else 20
                    ),
                    "provider_projection_and_public_admission_or_unchecked_construction": (
                        2_000 + row["block"] if row["arm"] == CHECK_ON else 30
                    ),
                }
                receipt: dict[str, object] = {
                    "schema": "rtdl.goal5842.causal_admission_worker.v1",
                    "status": "PASS",
                    "worker_id": row["worker_id"],
                    "task": row["task"],
                    "arm": row["arm"],
                    "block": row["block"],
                    "position": row["position"],
                    "arm_sample_index": row["arm_sample_index"],
                    "preregistration_sha256": self.prereg["preregistration_sha256"],
                    "execution_authority_sha256": authority["authority_sha256"],
                    "input_sha256": inputs[row["task"]],
                    "program_signature": signatures[row["task"]],
                    "post_estimand_public_admission_signature": signatures[row["task"]],
                    "normal_reference_admission_after_estimand": True,
                    "garbage_collector_disabled_during_registered_phases": True,
                    "clock": "time.perf_counter_ns",
                    "gpu_imported_or_executed": False,
                    "phases_ns": phases,
                    "registered_admission_total_ns": sum(phases.values()),
                }
                receipt["receipt_sha256"] = digest(receipt)
                write(
                    causal_root / f"{index:03d}_{row['worker_id']}" / "receipt.json",
                    receipt,
                )
                causal_receipts.append(receipt)
            causal_result: dict[str, object] = {
                "schema": "rtdl.goal5842.causal_admission_controller.v1",
                "status": "PASS__CAUSAL_ADMISSION_COHORT_COMPLETE",
                "source_commit": authority["source_commit"],
                "preregistration_sha256": self.prereg["preregistration_sha256"],
                "execution_authority_sha256": authority["authority_sha256"],
                "hardware": authority["hardware"],
                "worker_count": len(causal_receipts),
                "task_summaries": summarize(causal_receipts),
                "normal_reference_admission_after_estimand": True,
            }
            causal_result["result_sha256"] = digest(causal_result)
            write(causal_root / "result.json", causal_result)

            baseline_root = root / "baseline"
            composites = []
            for index, row in enumerate(self.prereg["baseline_schedule"]):
                identity = {"arm_identity": row["arm"]}
                common = {
                    "schema": BASELINE_SUBWORKER_SCHEMA,
                    "status": "PASS",
                    "schedule_worker_id": row["worker_id"],
                    "task": row["task"],
                    "arm": row["arm"],
                    "block": row["block"],
                    "preregistration_sha256": self.prereg["preregistration_sha256"],
                    "execution_authority_sha256": authority["authority_sha256"],
                    "input_sha256": inputs[row["task"]],
                    "output_sha256": outputs[row["task"]],
                    "public_output_contract_id": contracts[row["task"]][
                        "public_output_contract_id"
                    ],
                    "public_output_oracle_exact": True,
                    "oracle_validation_outside_registered_interval": True,
                    "auxiliary_full_oracle_witness_before_worker_zero": True,
                    "identity": identity,
                }
                direct = row["arm"] == "A_DIRECT_CUDA_OPTIX"
                first_phases = {
                    "deterministic_input_materialization": 5,
                    "route_declaration_and_artifact_binding": None if direct else 10,
                    "provider_projection_and_generic_family_admission": None
                    if direct
                    else 20,
                    "runtime_target_and_toolchain_binding": None if direct else 30,
                    "device_compile": 10 if direct else None,
                    "module_program_pipeline_sbt": 20 if direct else None,
                    "target_materialization": 40,
                    "native_prepare": 50,
                    "first_complete_execution": 60,
                    "steady_complete_execution": [],
                    "close": None if direct else 70,
                }
                steady_phases = dict(first_phases)
                steady_phases["first_complete_execution"] = None
                steady_phases["steady_complete_execution"] = list(range(1, 65))
                first: dict[str, object] = {
                    **common,
                    "subworker_id": f"{row['worker_id']}__FIRST_COMPLETE_EXECUTION",
                    "mode": "FIRST_COMPLETE_EXECUTION",
                    "phases_ns": first_phases,
                }
                steady: dict[str, object] = {
                    **common,
                    "subworker_id": f"{row['worker_id']}__STEADY_COMPLETE_EXECUTION",
                    "mode": "STEADY_COMPLETE_EXECUTION",
                    "phases_ns": steady_phases,
                }
                first["receipt_sha256"] = digest(first)
                steady["receipt_sha256"] = digest(steady)
                directory = baseline_root / f"{index:03d}_{row['worker_id']}"
                write(directory / "first/receipt.json", first)
                write(directory / "steady/receipt.json", steady)
                composites.append(combine_subworkers(first, steady, [80, 90]))
            baseline_result: dict[str, object] = {
                "schema": BASELINE_CONTROLLER_SCHEMA,
                "status": "PASS__TWO_TASK_THREE_ARM_BASELINE_COMPLETE",
                "source_commit": authority["source_commit"],
                "preregistration_sha256": self.prereg["preregistration_sha256"],
                "execution_authority_sha256": authority["authority_sha256"],
                "hardware": authority["hardware"],
                "composite_worker_count": len(composites),
                "subworker_count": 2 * len(composites),
                "task_summaries": summarize_baselines(composites),
                "composite_rows": composites,
                "cross_arm_public_input_output_contract_exact": True,
                "oracle_validation_outside_registered_intervals": True,
            }
            baseline_result["result_sha256"] = digest(baseline_result)
            write(baseline_root / "result.json", baseline_result)

            recounted_causal, rows = recount_causal(causal_root, self.prereg, authority)
            recounted_baseline, rebuilt = recount_baseline(
                baseline_root, self.prereg, authority
            )
            self.assertEqual(recounted_causal["task_summaries"], summarize(rows))
            self.assertEqual(recounted_baseline["composite_rows"], rebuilt)

            attacked_path = next(causal_root.glob("*/receipt.json"))
            attacked = json.loads(attacked_path.read_text(encoding="utf-8"))
            attacked["registered_admission_total_ns"] += 1
            attacked.pop("receipt_sha256")
            attacked["receipt_sha256"] = digest(attacked)
            attacked_path.write_text(json.dumps(attacked), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "causal total mismatch"):
                recount_causal(causal_root, self.prereg, authority)

            baseline_receipt_path = next(baseline_root.glob("*/first/receipt.json"))
            hidden = json.loads(baseline_receipt_path.read_text(encoding="utf-8"))
            hidden["hidden_duration_ns"] = 1
            hidden.pop("receipt_sha256")
            hidden["receipt_sha256"] = digest(hidden)
            baseline_receipt_path.write_text(json.dumps(hidden), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "field set mismatch"):
                recount_baseline(baseline_root, self.prereg, authority)


if __name__ == "__main__":
    unittest.main()

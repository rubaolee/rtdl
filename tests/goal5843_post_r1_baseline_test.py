"""Pre-execution contract tests for Goal5843."""

from __future__ import annotations

from collections import Counter
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from types import MappingProxyType, SimpleNamespace
import unittest
from unittest import mock

from experiments.goal5843_post_r1_baseline import controller
from experiments.goal5843_post_r1_baseline.contracts import (
    ARMS,
    BLOCKS,
    BOUND_ARTIFACTS_SCHEMA,
    DIRECT_ARM,
    FIRST_MODE,
    PHASE_KEYS,
    PYOPTIX_ARM,
    RELATION_TASK,
    RTDL_ARM,
    SUBWORKER_SCHEMA,
    TASKS,
    TRIANGLE_TASK,
    Goal5843ContractError,
    build_preregistration,
    build_schedule,
    digest,
    validate_preregistration,
    validate_schedule,
)
from scripts import goal5843_independent_recount as recount
from scripts import goal5843_run_transaction as transaction
from scripts import goal5843_verify_downloaded_archive as archive_verifier
from scripts.goal5843_prepare_formal_leaf_cache import validate_cache_lifecycle


ROOT = Path(__file__).resolve().parents[1]


class Goal5843PostR1BaselineTest(unittest.TestCase):
    def test_schedule_is_balanced_and_complete(self) -> None:
        schedule = build_schedule()
        validate_schedule(schedule)
        self.assertEqual(len(schedule), BLOCKS * len(TASKS) * len(ARMS))
        self.assertEqual(
            Counter((row["task"], row["arm"]) for row in schedule),
            Counter({(task, arm): BLOCKS for task in TASKS for arm in ARMS}),
        )
        for task in TASKS:
            orders = Counter(
                row["permutation_index"]
                for row in schedule
                if row["task"] == task and row["arm_position"] == 0
            )
            self.assertEqual(orders, Counter({index: 3 for index in range(6)}))

    def test_preregistration_is_sealed_and_claim_limited(self) -> None:
        prereg = build_preregistration(ROOT)
        self.assertEqual(
            validate_preregistration(prereg, ROOT, verify_files=True), prereg
        )
        self.assertIsNone(
            prereg["estimands"]["registered_performance_success_threshold"]
        )
        self.assertFalse(prereg["claim_ceiling"]["public_performance_claim_authorized"])
        self.assertFalse(
            prereg["claim_ceiling"]["manuscript_performance_claim_authorized"]
        )
        self.assertFalse(prereg["claim_ceiling"]["external_review_or_consensus_complete"])
        self.assertTrue(prereg["fairness"]["rtdl_private_checker_off_forbidden"])

    def test_preregistration_tamper_is_rejected(self) -> None:
        prereg = build_preregistration(ROOT)
        tampered = copy.deepcopy(prereg)
        tampered["sampling"]["steady_fresh_subworker_repetitions"] = 1
        with self.assertRaisesRegex(Goal5843ContractError, "seal"):
            validate_preregistration(tampered, ROOT, verify_files=False)
        tampered["preregistration_sha256"] = digest(
            {key: value for key, value in tampered.items() if key != "preregistration_sha256"}
        )
        with self.assertRaisesRegex(Goal5843ContractError, "sampling"):
            validate_preregistration(tampered, ROOT, verify_files=False)

        fairness_tamper = copy.deepcopy(prereg)
        fairness_tamper["fairness"]["rtdl_private_checker_off_forbidden"] = False
        fairness_tamper["preregistration_sha256"] = digest(
            {
                key: value
                for key, value in fairness_tamper.items()
                if key != "preregistration_sha256"
            }
        )
        with self.assertRaisesRegex(Goal5843ContractError, "canonical builder"):
            validate_preregistration(fairness_tamper, ROOT, verify_files=False)

        repair_tamper = copy.deepcopy(prereg)
        repair_tamper["pre_worker_zero_repairs"][0][
            "formal_timing_samples_recorded"
        ] = 1
        repair_tamper["preregistration_sha256"] = digest({
            key: value
            for key, value in repair_tamper.items()
            if key != "preregistration_sha256"
        })
        with self.assertRaisesRegex(Goal5843ContractError, "repair history"):
            validate_preregistration(repair_tamper, ROOT, verify_files=False)

        transaction_tamper = copy.deepcopy(prereg)
        transaction_tamper["superseded_formal_transactions"][0][
            "rows_eligible_for_successor_pooling"
        ] = True
        transaction_tamper["preregistration_sha256"] = digest({
            key: value
            for key, value in transaction_tamper.items()
            if key != "preregistration_sha256"
        })
        with self.assertRaisesRegex(
            Goal5843ContractError, "superseded formal-transaction history"
        ):
            validate_preregistration(
                transaction_tamper, ROOT, verify_files=False
            )

    def test_controller_and_independent_summary_agree(self) -> None:
        prereg = build_preregistration(ROOT)
        composites = []
        arm_scale = {DIRECT_ARM: 2, PYOPTIX_ARM: 3, RTDL_ARM: 5}
        for row in prereg["schedule"]:
            scale = arm_scale[row["arm"]]
            phases = {
                key: (
                    []
                    if key == "steady_complete_execution"
                    else None
                    if key in {"device_compile", "module_program_pipeline_sbt"}
                    and row["arm"] == RTDL_ARM
                    else scale * 100 + row["block"]
                )
                for key in PHASE_KEYS
            }
            composites.append(
                {
                    "schedule_worker_id": row["worker_id"],
                    "task": row["task"],
                    "arm": row["arm"],
                    "block": row["block"],
                    "input_sha256": "a" * 64,
                    "output_sha256": "b" * 64,
                    "public_output_contract_id": "synthetic",
                    "identity": {"synthetic": True},
                    "first_execution_boundary": {"synthetic": True},
                    "steady_execution_boundary": {"synthetic": True},
                    "first_phases_ns": phases,
                    "steady_phases_ns": phases,
                    "deterministic_input_materialization_ns": scale,
                    "setup_total_ns": scale * 1_000 + row["block"],
                    "first_complete_execution_ns": scale * 100 + row["block"],
                    "steady_complete_execution_median_ns": scale * 10 + row["block"],
                    "close_ns": scale,
                    "process_wall_ns": [scale, scale],
                    "public_output_oracle_exact": True,
                    "oracle_validation_outside_registered_interval": True,
                    "independent_oracle_witness_sha256": "c" * 64,
                }
            )
        self.assertEqual(
            controller.summarize(composites), recount.summarize(composites, prereg)
        )
        triangle = next(
            row
            for row in controller.summarize(composites)
            if row["task"] == TRIANGLE_TASK
        )
        steady_direct = next(
            row
            for row in triangle["comparisons"]
            if row["denominator"] == DIRECT_ARM
            and row["metric"] == "steady_complete_execution_median_ns"
        )
        self.assertIsNone(steady_direct["registered_gate"])
        self.assertEqual(len(steady_direct["within_block_scaled_ratios_1e9"]), BLOCKS)

    def test_triangle_boundary_gate_rejects_host_materialization(self) -> None:
        prereg = build_preregistration(ROOT)
        gate = prereg["rtdl_triangle_receipt_gate"]
        fast = {
            key: gate[key]
            for key in (
                "optix_launch_count",
                "dynamic_accel_build_count",
                "control_d2h_bytes",
                "output_d2h_bytes",
                "role_counters_materialized",
                "total_auxiliary_cuda_kernel_launch_count",
            )
        }
        fast["dynamic_device_upload_call_count"] = 0
        fast["dynamic_device_upload_bytes"] = 0
        fast["prepared_input_reused"] = True
        boundary = {
            "schema": "rtdl.v4.triangle_reduction_execution_boundary.v1",
            "execution_path": gate["execution_path"],
            "prepared_query_input_reused": True,
            "per_ray_u64_materialized_on_host": False,
            "event_rows_materialized_on_host": False,
            "public_output_scalar_bytes": 8,
            "fast_operation_receipt": fast,
        }
        from experiments.goal5843_post_r1_baseline.worker import (
            _validate_rtdl_triangle_boundary,
        )

        readonly = MappingProxyType({
            key: MappingProxyType(value) if key == "fast_operation_receipt" else value
            for key, value in boundary.items()
        })
        self.assertEqual(
            _validate_rtdl_triangle_boundary(
                readonly,
                mode="STEADY_COMPLETE_EXECUTION",
                prereg=prereg,
            ),
            boundary,
        )
        boundary["per_ray_u64_materialized_on_host"] = True
        with self.assertRaisesRegex(RuntimeError, "boundary mismatch"):
            _validate_rtdl_triangle_boundary(
                boundary, mode="STEADY_COMPLETE_EXECUTION", prereg=prereg
            )

    def test_worker_unwraps_readonly_generic_provider_receipt(self) -> None:
        from experiments.goal5843_post_r1_baseline.worker import (
            _provider_execution_boundary,
        )

        boundary = MappingProxyType({
            "schema": "test.execution.v1",
            "nested": MappingProxyType({"count": 7}),
        })
        receipt = MappingProxyType({
            "schema": "rtdl.generic_family_lifecycle.v1",
            "provider_receipt": MappingProxyType({
                "schema": "rtdl.v4.public_protocol_lifecycle.v1",
                "provider_execution": boundary,
            }),
        })
        prepared = SimpleNamespace(lifecycle_receipt=receipt)
        self.assertEqual(
            _provider_execution_boundary(prepared),
            {"schema": "test.execution.v1", "nested": {"count": 7}},
        )

        bad = SimpleNamespace(lifecycle_receipt=MappingProxyType({
            "schema": "rtdl.generic_family_lifecycle.v1",
            "provider_receipt": MappingProxyType({
                "schema": "wrong.provider.schema",
                "provider_execution": boundary,
            }),
        }))
        with self.assertRaisesRegex(RuntimeError, "provider lifecycle.*schema"):
            _provider_execution_boundary(bad)

    def test_worker_uses_traversal_receipt_for_relation_control(self) -> None:
        from experiments.goal5843_post_r1_baseline.worker import (
            _rtdl_execution_boundary,
        )

        provider = MappingProxyType({
            "schema": "rtdl.v4.public_protocol_lifecycle.v1",
            "execution_count": 72,
            "provider_execution": None,
        })
        prepared = SimpleNamespace(lifecycle_receipt=MappingProxyType({
            "schema": "rtdl.generic_family_lifecycle.v1",
            "provider_receipt": provider,
        }))
        traversal = MappingProxyType({
            "schema": "rtdl.physical_execution.traversal_receipt.v1",
            "physical_executor_classification": "optix_traversal_observed",
            "route_identity": "v4_callback_ir:custom_aabb_bounded_relation_v1",
        })
        boundary = _rtdl_execution_boundary(
            RELATION_TASK,
            prepared,
            SimpleNamespace(traversal_receipt=traversal),
        )
        self.assertEqual(boundary["provider_execution_count"], 72)
        self.assertFalse(boundary["provider_execution_boundary_available"])
        self.assertEqual(boundary["traversal_receipt"], dict(traversal))

        provider_with_extension = MappingProxyType({
            **dict(provider),
            "provider_execution": {"unexpected": True},
        })
        bad = SimpleNamespace(lifecycle_receipt=MappingProxyType({
            "schema": "rtdl.generic_family_lifecycle.v1",
            "provider_receipt": provider_with_extension,
        }))
        with self.assertRaisesRegex(RuntimeError, "unexpectedly exposed"):
            _rtdl_execution_boundary(
                RELATION_TASK,
                bad,
                SimpleNamespace(traversal_receipt=traversal),
            )

    def test_controller_and_recount_validate_relation_traversal_evidence(self) -> None:
        prereg = build_preregistration(ROOT)
        row = next(
            dict(item)
            for item in prereg["schedule"]
            if item["task"] == RELATION_TASK and item["arm"] == RTDL_ARM
        )
        contract = next(
            item
            for item in prereg["task_contracts"]
            if item["task"] == RELATION_TASK
        )
        authority = {
            "authority_sha256": "a" * 64,
            "independent_oracle_witness": {"witness_sha256": "b" * 64},
            "execution_paths": {"native_library_sha256": "c" * 64},
        }
        traversal = {
            "schema": "rtdl.physical_execution.traversal_receipt.v1",
            "physical_executor_classification": "optix_traversal_observed",
            "route_identity": "v4_callback_ir:custom_aabb_bounded_relation_v1",
            "provider_library_sha256": "c" * 64,
            "output_digest": contract["public_output_sha256"],
            "expected_program_observed_at_receipt_edge": True,
            "native_snapshot": {
                "attempted_launch_count": 2,
                "successful_launch_count": 2,
                "complete_context_launch_count": 2,
                "failed_launch_count": 0,
                "raygen_invocation_count": 8192,
            },
        }
        traversal["receipt_sha256"] = digest(traversal)
        boundary = {
            "schema": "rtdl.goal5843.rtdl_relation_execution_boundary.v1",
            "provider_execution_boundary_available": False,
            "evidence_source": "generic_result.traversal_receipt",
            "provider_lifecycle_schema": "rtdl.v4.public_protocol_lifecycle.v1",
            "provider_execution_count": 1,
            "physical_executor_classification": "optix_traversal_observed",
            "traversal_receipt": traversal,
        }
        phases = {key: None for key in PHASE_KEYS}
        phases["first_complete_execution"] = 1
        phases["steady_complete_execution"] = []
        receipt = {
            "schema": SUBWORKER_SCHEMA,
            "status": "PASS",
            "schedule_worker_id": row["worker_id"],
            "subworker_id": f"{row['worker_id']}__{FIRST_MODE}",
            "task": row["task"],
            "arm": row["arm"],
            "block": row["block"],
            "mode": FIRST_MODE,
            "preregistration_sha256": prereg["preregistration_sha256"],
            "execution_authority_sha256": authority["authority_sha256"],
            "input_sha256": contract["input_sha256"],
            "output_sha256": contract["public_output_sha256"],
            "public_output_contract_id": contract["public_output_contract_id"],
            "public_output_oracle_exact": True,
            "oracle_validation_outside_registered_interval": True,
            "independent_oracle_witness_sha256": "b" * 64,
            "phases_ns": phases,
            "identity": {"test": True},
            "latest_execution_boundary": boundary,
        }
        receipt["receipt_sha256"] = digest(receipt)
        controller.validate_receipt(
            receipt,
            row=row,
            mode=FIRST_MODE,
            authority=authority,
            prereg=prereg,
        )
        recount.validate_receipt(
            receipt,
            scheduled=row,
            mode=FIRST_MODE,
            authority=authority,
            prereg=prereg,
        )

        attacked = copy.deepcopy(receipt)
        attacked["latest_execution_boundary"]["traversal_receipt"][
            "route_identity"
        ] = "wrong.route"
        attacked["receipt_sha256"] = digest({
            key: value
            for key, value in attacked.items()
            if key != "receipt_sha256"
        })
        with self.assertRaisesRegex(RuntimeError, "relation traversal evidence"):
            controller.validate_receipt(
                attacked,
                row=row,
                mode=FIRST_MODE,
                authority=authority,
                prereg=prereg,
            )
        with self.assertRaisesRegex(RuntimeError, "relation traversal evidence"):
            recount.validate_receipt(
                attacked,
                scheduled=row,
                mode=FIRST_MODE,
                authority=authority,
                prereg=prereg,
            )

    def test_worker_validates_generic_public_result_shape(self) -> None:
        from experiments.goal5843_post_r1_baseline.worker import (
            _rtdl_public_value,
        )

        scalar = SimpleNamespace(output=65530)
        self.assertEqual(_rtdl_public_value(TRIANGLE_TASK, scalar), 65530)
        with self.assertRaisesRegex(RuntimeError, "diagnostic details"):
            _rtdl_public_value(
                TRIANGLE_TASK, SimpleNamespace(output=65530, details={})
            )
        with self.assertRaisesRegex(RuntimeError, "exact integer scalar"):
            _rtdl_public_value(TRIANGLE_TASK, SimpleNamespace(output="65530"))
        self.assertEqual(
            _rtdl_public_value(
                RELATION_TASK,
                SimpleNamespace(output=((0, 0), (1, 1))),
            ),
            {"output": ((0, 0), (1, 1))},
        )

    def test_formal_cache_replay_allows_cross_program_leaf_sharing(self) -> None:
        before = {"hit_count": 0, "miss_count": 0}
        after_fill = {"hit_count": 2, "miss_count": 5}
        after_verify = {"hit_count": 9, "miss_count": 5}
        self.assertEqual(
            validate_cache_lifecycle(before, after_fill, after_verify),
            (5, 7, 0),
        )
        with self.assertRaisesRegex(RuntimeError, "hit-only"):
            validate_cache_lifecycle(
                before,
                after_fill,
                {"hit_count": 9, "miss_count": 6},
            )

    def test_failed_stage_writes_terminal_no_retry_status(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output_root = Path(temporary)
            stage_root = output_root / "stages"
            stage_root.mkdir()
            with self.assertRaisesRegex(RuntimeError, "failed without retry"):
                transaction.run_stage(
                    name="00_expected_failure",
                    command=[sys.executable, "-c", "raise SystemExit(7)"],
                    stage_root=stage_root,
                    environment=os.environ.copy(),
                )
            status = json.loads(
                (output_root / "TRANSACTION_STATUS.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                status["status"],
                "FAIL__FORMAL_TRANSACTION_TERMINATED_WITHOUT_RETRY",
            )
            self.assertEqual(status["failure_stage"], "00_expected_failure")
            self.assertFalse(status["worker_zero_reached"])
            self.assertFalse(status["post_worker_zero_retry_permitted"])

    def test_archive_member_path_gate_rejects_escape_and_links_are_not_paths(self) -> None:
        self.assertEqual(
            archive_verifier.safe_member_path("goal5843/root.json").as_posix(),
            "goal5843/root.json",
        )
        for invalid in ("", "/absolute", "../escape", "root/../escape", "root\\file"):
            with self.subTest(invalid=invalid), self.assertRaises(RuntimeError):
                archive_verifier.safe_member_path(invalid)

    def test_archive_custody_checks_tar_mode_not_safely_filtered_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            transaction_root = Path(temporary) / "goal5843-test"
            artifact = transaction_root / "bound_artifacts/native/artifact.so"
            artifact.parent.mkdir(parents=True)
            artifact.write_bytes(b"exact-provider-bytes")
            os.chmod(artifact, 0o755)
            artifact_sha256 = hashlib.sha256(artifact.read_bytes()).hexdigest()
            authority = {
                "source_commit": "a" * 40,
                "preregistration_sha256": "b" * 64,
                "authority_sha256": "c" * 64,
            }
            binding = "execution_paths.native_library"
            receipt = {
                "schema": BOUND_ARTIFACTS_SCHEMA,
                "status": "PASS__EXACT_BOUND_EXECUTABLE_AND_PROVIDER_BYTES_PRESERVED",
                "source_commit": authority["source_commit"],
                "preregistration_sha256": authority["preregistration_sha256"],
                "execution_authority_sha256": authority["authority_sha256"],
                "artifact_count": 1,
                "artifacts": [
                    {
                        "authority_binding": binding,
                        "archived_path": "native/artifact.so",
                        "bytes": artifact.stat().st_size,
                        "sha256": artifact_sha256,
                        "source_mode": 0o777,
                    }
                ],
                "gpu_complete_execution_count": 0,
                "goal5843_registered_estimand_timing_observation_count": 0,
            }
            receipt["custody_sha256"] = digest(receipt)
            (transaction_root / "BOUND_ARTIFACTS.json").write_text(
                json.dumps(receipt), encoding="utf-8"
            )
            expected = {
                binding: {
                    "archived_path": "native/artifact.so",
                    "bytes": artifact.stat().st_size,
                    "sha256": artifact_sha256,
                }
            }
            archive_member = (
                "goal5843-test/bound_artifacts/native/artifact.so"
            )
            with mock.patch.object(
                archive_verifier,
                "expected_preserved_artifacts",
                return_value=expected,
            ):
                self.assertEqual(
                    archive_verifier.verify_preserved_artifacts(
                        transaction_root,
                        authority,
                        archive_modes={archive_member: 0o777},
                    ),
                    1,
                )
                with self.assertRaisesRegex(RuntimeError, "archive mode differs"):
                    archive_verifier.verify_preserved_artifacts(
                        transaction_root,
                        authority,
                        archive_modes={archive_member: 0o755},
                    )

    def test_v3_terminal_evidence_custody_is_preserved(self) -> None:
        from scripts.goal5843_build_preregistration import (
            _verify_v3_terminal_evidence,
        )

        _verify_v3_terminal_evidence()

    def test_inherited_provider_timers_wait_for_gpu_completion(self) -> None:
        direct = (ROOT / "experiments/goal5796_matched/direct_optix.cpp").read_text(
            encoding="utf-8"
        )
        pyoptix = (
            ROOT / "experiments/goal5796_matched/pyoptix_baseline.py"
        ).read_text(encoding="utf-8")
        self.assertIn("CU_CHECK(cuStreamSynchronize(0));", direct)
        self.assertIn("stream.synchronize()", pyoptix)

    def test_frozen_goal5838_core_is_unchanged(self) -> None:
        prereg = build_preregistration(ROOT)
        for relative, expected in prereg["frozen_core_sha256"].items():
            self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), expected)

    def test_recount_module_is_stdlib_only_at_top_level(self) -> None:
        source = (ROOT / "scripts/goal5843_independent_recount.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("import rtdsl", source)
        self.assertNotIn("goal5843_post_r1_baseline.controller", source)
        self.assertNotIn("experiments.goal5842_causal_admission", source)

    def test_stored_preregistration_matches_after_freeze(self) -> None:
        path = ROOT / (
            "history/internal_docs/goal5843_post_r1_fair_baseline_20260904/"
            "PREREGISTRATION.json"
        )
        if not path.exists():
            self.skipTest("preregistration is generated after pre-freeze tests pass")
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), build_preregistration(ROOT))


if __name__ == "__main__":
    unittest.main()

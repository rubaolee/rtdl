from __future__ import annotations

import copy
import hashlib
import unittest
from pathlib import Path
from unittest import mock

from experiments.goal5848_strong_baseline import contracts


class Goal5848StrongBaselineContractTest(unittest.TestCase):
    @staticmethod
    def _public_output(task):
        return (
            [[index, index] for index in range(4096)]
            if task == contracts.RELATION_TASK
            else sum(1 + index % 7 for index in range(16384))
        )

    @staticmethod
    def _rtdl_traversal(task):
        relation = task == contracts.RELATION_TASK
        bundle = contracts._RTDL_PROGRAM_BUNDLES[task]
        bundle_id = contracts._physical_program_bundle_id(bundle)
        launches = 2 if relation else 1
        first_traversable = 41
        last_traversable = 43 if relation else first_traversable
        traversable_mix = contracts._native_audit_mix_u64(
            0, first_traversable
        )
        if relation:
            traversable_mix = contracts._native_audit_mix_u64(
                traversable_mix, last_traversable
            )
        body = {
            "schema": contracts._FULL_TRAVERSAL_SCHEMA,
            "provider_library": "librtdl_optix",
            "provider_library_path": "/sealed/librtdl_optix.so",
            "provider_library_sha256": "d" * 64,
            "route_identity": contracts._RTDL_ROUTE_IDENTITIES[task],
            "semantic_digest": "e" * 64,
            "output_digest": contracts.TASK_CONTRACTS[task][
                "public_output_sha256"
            ],
            "physical_executor_classification": "optix_traversal_observed",
            "expected_program_bundles": [bundle],
            "expected_program_bundle_ids": [bundle_id],
            "expected_program_observed_at_receipt_edge": True,
            "nonce": {"hi": 7, "lo": 11},
            "native_snapshot": {
                "nonce_hi": 7,
                "nonce_lo": 11,
                "attempted_launch_count": launches,
                "successful_launch_count": launches,
                "failed_launch_count": 0,
                "complete_context_launch_count": launches,
                "incomplete_context_launch_count": 0,
                "context_bind_count": launches,
                "raygen_invocation_count": 8192 if relation else 16384,
                "program_bundle_mix": contracts._repeated_native_audit_mix(
                    bundle_id, launches
                ),
                "traversable_mix": traversable_mix,
                "pipeline_mix": 101,
                "sbt_mix": 103,
                "stream_mix": 107,
                "params_mix": 109,
                "callsite_mix": 113,
                "first_program_bundle_id": bundle_id,
                "last_program_bundle_id": bundle_id,
                "first_traversable": first_traversable,
                "last_traversable": last_traversable,
                "pending_context_at_finish": 0,
                "session_error": 0,
                "incomplete_callsite_record_count": 0,
                "incomplete_callsite_lines": [0] * 32,
            },
            "claim_rules": dict(contracts._FULL_TRAVERSAL_RULES),
        }
        body["receipt_sha256"] = contracts.digest(body)
        return body

    @classmethod
    def _arm_evidence(cls, row, samples):
        task = row["task"]
        relation = task == contracts.RELATION_TASK
        public_output = cls._public_output(task)
        evidence = {
            "output_sha256": contracts.TASK_CONTRACTS[task][
                "public_output_sha256"
            ],
            "public_output": public_output,
        }
        if row["arm"] in {
            contracts.RTDL_ARM,
            contracts.PREDECESSOR_RTDL_ARM,
        }:
            evidence.update({
                "runtime_compiler_attempt_count_before": 0,
                "runtime_compiler_attempt_count_after": 0,
                "runtime_compiler_modules": [],
                "nvrtc_mappings": [],
                "provider_initialization_phases_ns": {
                    "native_runtime_warm": 1,
                },
                "phase_instrumentation": True,
                "diagnostic_traversal_receipt": cls._rtdl_traversal(task),
                "latest_output_sha256": None,
            })
        elif row["arm"] == contracts.IDIOMATIC_PYOPTIX_ARM:
            evidence.update({
                "phase_instrumentation": True,
                "host_continuation_disclosed": relation,
                "raw_event_count": 8192 if relation else None,
                "source_compilation_inside_endpoint": False,
            })
        elif row["arm"] == contracts.STRONG_PYOPTIX_ARM:
            evidence.update({
                "phase_instrumentation": True,
                "source_compilation_inside_endpoint": False,
                "optix_module_disk_cache_enabled": False,
                "optix_validation_mode": "OFF",
                "optix_log_callback_mode": "OFF",
                "operation_evidence_source": (
                    "UNTIMED_PREWORKER_KAT_AND_EXACT_SOURCE_BOUNDARY"
                ),
                "live_execute_guard_inside_timer": False,
                "lifecycle": {
                    "prepared_input_reused": True,
                    "dynamic_device_upload_call_count": 0,
                    "dynamic_device_upload_bytes": 0,
                    "dynamic_accel_build_count": 0,
                    "dynamic_explicit_sync_count": 0,
                    "dynamic_blocking_upload_call_count": 0,
                    "dynamic_input_generation": 1,
                },
                "runtime_preload_receipt": {
                    "schema": "rtdl.goal5802.python_runtime_preload.v1",
                    "status": "PASS__BEFORE_PRIMARY_CLOCK",
                    "compiler_only_nvrtc_loaded": False,
                    "prebuilt_ptx_deployment": True,
                    "runtime_import_inside_primary_timer": False,
                },
                "application_output_d2h_bytes": (
                    contracts.TASK_CONTRACTS[task]["public_output_bytes"]
                ),
                "per_ray_d2h_bytes": 0,
                "per_ray_host_materialized": False,
                "status_output_commit_blocking_boundary_count": 2,
                "semantic_compaction_launch_count": 1 if relation else 0,
                "total_auxiliary_cuda_kernel_launch_count": 1 if relation else 0,
            })
            if relation:
                evidence.update({
                    "output": public_output,
                    "raw_event_count": 8192,
                    "semantic_unique_count": 4096,
                    "device_status": 0,
                    "device_overflow": 0,
                    "optix_launch_count": 2,
                })
            else:
                evidence.update({
                    "reduced_u64": public_output,
                    "device_status": 0,
                    "launch_count": 1,
                })
        else:
            direct_task = (
                "CUSTOM_AABB_CLOSED_RELATION_COUNT_V2_MATCHED"
                if relation
                else "BUILTIN_TRIANGLE_WEIGHTED_SCALAR_V2_MATCHED"
            )
            correctness = (
                {
                    "oracle_exact": True,
                    "canonical_rows": public_output,
                    "canonical_row_count": 4096,
                    "raw_event_count": 8192,
                    "semantic_unique_count": 4096,
                    "device_status": 0,
                    "device_overflow": 0,
                }
                if relation
                else {
                    "oracle_exact": True,
                    "reduced_u64": public_output,
                    "device_status": 0,
                }
            )
            evidence.update({
                "source_compilation_inside_endpoint": False,
                "direct_stdout_sha256": "f" * 64,
                "direct_stderr_sha256": hashlib.sha256(b"").hexdigest(),
                "direct_worker_receipt": {
                    "schema": "rtdl.goal5802.direct_scalar.worker.v1",
                    "status": "PASS",
                    "arm": "A_DIRECT_CUDA_OPTIX",
                    "worker_id": row["worker_id"],
                    "task": direct_task,
                    "regime": "STEADY_E2E",
                    "registered_performance_timing_count": (
                        contracts.STEADY_REPETITIONS
                    ),
                    "execute_or_regime_durations_ns": list(samples),
                    "execution_lifecycle_receipts": [
                        {"prepared_input_reused": index > 0}
                        for index in range(
                            contracts.STEADY_WARMUPS
                            + contracts.STEADY_REPETITIONS
                        )
                    ],
                    "correctness": correctness,
                    "operation_ledger": {
                        "optix_launch_count": 2 if relation else 1,
                        "semantic_compaction_launch_count": 1 if relation else 0,
                        "application_output_d2h_bytes": (
                            contracts.TASK_CONTRACTS[task]["public_output_bytes"]
                        ),
                        "per_ray_d2h_bytes": 0,
                        "status_output_commit_blocking_boundary_count": 2,
                    },
                },
            })
        return evidence

    @staticmethod
    def _receipt(
        row, *, post_import_ns=100, steady_ns=100,
        implementation_import_ns=1, implementation_gap_ns=1,
    ):
        partition = {name: 0 for name in contracts.PARTITION_KEYS}
        partition["canonical_input_construction"] = post_import_ns
        direct = row["arm"] == contracts.DIRECT_OPTIX_ARM
        samples = [steady_ns] * contracts.STEADY_REPETITIONS
        value = {
            "schema": contracts.WORKER_SCHEMA,
            "status": "PASS__GOAL5848_WORKER",
            "arm": row["arm"],
            "task": row["task"],
            "block": row["block"],
            "worker_id": row["worker_id"],
            "classification": "formal",
            "warmups": contracts.STEADY_WARMUPS,
            "repetitions": contracts.STEADY_REPETITIONS,
            "python": (
                contracts.DIRECT_RUNTIME_IDENTITY if direct else "3.12.14"
            ),
            "source": {
                "commit": (
                    "b" * 40
                    if row["arm"] == contracts.PREDECESSOR_RTDL_ARM
                    else "a" * 40
                ),
                "tree": "c" * 40,
                "status": "",
                "clean": True,
            },
            "hardware": {
                "gpu_name": "Synthetic RTX",
                "gpu_uuid": "GPU-synthetic",
                "driver_version": "580.0",
                "memory_mib": 16384,
                "compute_capability": "8.9",
            },
            "measurements": {
                "implementation_import_ns": (
                    None if direct else implementation_import_ns
                ),
                "implementation_entry_to_first_correct_result_ns": (
                    None
                    if direct
                    else post_import_ns
                    + implementation_import_ns
                    + implementation_gap_ns
                ),
                "implementation_import_to_endpoint_gap_ns": (
                    None if direct else implementation_gap_ns
                ),
                "post_import_to_first_correct_result_ns": (
                    None if direct else post_import_ns
                ),
                "endpoint_partition_ns": None if direct else partition,
                "partition_reconciliation": (
                    None
                    if direct
                    else {
                        "endpoint_ns": post_import_ns,
                        "partition_total_ns": post_import_ns,
                        "absolute_error_ns": 0,
                        "tolerance_ns": 2_000_000,
                    }
                ),
                "component_diagnostics_ns": {
                    name: None
                    for name in contracts.COMPONENT_DIAGNOSTIC_KEYS
                },
                "steady_complete_execution": {
                    "sample_count": contracts.STEADY_REPETITIONS,
                    "samples_ns": samples,
                    "minimum_ns": steady_ns,
                    "median_ns": steady_ns,
                    "maximum_ns": steady_ns,
                },
                "identity": (
                    {"native_library_sha256": "d" * 64}
                    if row["arm"] in {
                        contracts.RTDL_ARM,
                        contracts.PREDECESSOR_RTDL_ARM,
                    }
                    else {}
                ),
                "evidence": Goal5848StrongBaselineContractTest._arm_evidence(
                    row, samples
                ),
            },
            "claim_boundary": {
                "exploration_or_formal_classification_owned_by_controller": True,
                "public_or_manuscript_claim_authorized": False,
                "external_review_complete": False,
            },
        }
        value["result_sha256"] = contracts.digest(value)
        return value

    def test_schedule_is_balanced_and_deterministic(self):
        first = contracts.build_schedule()
        second = contracts.build_schedule()
        self.assertEqual(first, second)
        self.assertEqual(
            len(first),
            contracts.BLOCKS * len(contracts.TASKS) * len(contracts.ARMS),
        )
        contracts.validate_schedule(first)
        predecessor_positions = {
            row["arm_position"]
            for row in first
            if row["arm"] == contracts.PREDECESSOR_RTDL_ARM
        }
        self.assertEqual(predecessor_positions, set(range(len(contracts.ARMS))))

    def test_schedule_mutations_fail_closed(self):
        rows = list(contracts.build_schedule())
        rows[0] = {**rows[0], "arm": contracts.DIRECT_OPTIX_ARM}
        with self.assertRaises(contracts.Goal5848ContractError):
            contracts.validate_schedule(rows)

        rows = list(contracts.build_schedule())
        rows[0] = {**rows[0], "worker_id": rows[1]["worker_id"]}
        with self.assertRaises(contracts.Goal5848ContractError):
            contracts.validate_schedule(rows)

    def test_phase_partition_reconciles_only_nonoverlapping_wall_buckets(self):
        partition = {name: 1_000_000 for name in contracts.PARTITION_KEYS}
        endpoint = sum(partition.values()) + 500_000
        result = contracts.validate_phase_partition(
            partition,
            endpoint_ns=endpoint,
            uninstrumented_endpoint_median_ns=20_000_000,
            measured_instrumentation_overhead_ns=100_000,
        )
        self.assertEqual(result["absolute_error_ns"], 500_000)

    def test_phase_partition_rejects_gap_and_excessive_instrumentation(self):
        partition = {name: 1_000_000 for name in contracts.PARTITION_KEYS}
        with self.assertRaises(contracts.Goal5848ContractError):
            contracts.validate_phase_partition(
                partition,
                endpoint_ns=sum(partition.values()) + 3_000_000,
            )
        with self.assertRaises(contracts.Goal5848ContractError):
            contracts.validate_phase_partition(
                partition,
                endpoint_ns=sum(partition.values()),
                uninstrumented_endpoint_median_ns=20_000_000,
                measured_instrumentation_overhead_ns=1_000_001,
            )

    def test_component_diagnostics_are_exact_shape_but_not_summed(self):
        diagnostics = {
            name: None for name in contracts.COMPONENT_DIAGNOSTIC_KEYS
        }
        diagnostics["cuda_primary_context"] = 250_000_000
        diagnostics["native_image_read_and_hash"] = 40_000_000
        contracts.validate_component_diagnostics(diagnostics)
        diagnostics["app_specific_phase"] = 1
        with self.assertRaises(contracts.Goal5848ContractError):
            contracts.validate_component_diagnostics(diagnostics)

    def test_integer_ratio_avoids_float_authority(self):
        self.assertEqual(contracts.ratio_ppm(6, 5), 1_200_000)
        self.assertEqual(contracts.integer_median([4, 1, 3, 2]), 2)
        with self.assertRaises(contracts.Goal5848ContractError):
            contracts.ratio_ppm(1, 0)

    def test_formal_cache_policy_requires_both_disabled_controls(self):
        valid = {
            "CUDA_CACHE_DISABLE": "1",
            "RTDL_OPTIX_DISK_CACHE_POLICY": "disabled",
        }
        with mock.patch.dict("os.environ", valid, clear=True):
            contracts.require_formal_cache_policy()
        for missing in valid:
            hostile = dict(valid)
            del hostile[missing]
            with (
                self.subTest(missing=missing),
                mock.patch.dict("os.environ", hostile, clear=True),
                self.assertRaisesRegex(RuntimeError, "cache|CACHE"),
            ):
                contracts.require_formal_cache_policy()

    def test_all_primary_implementations_disable_optix_disk_cache(self):
        root = Path(__file__).resolve().parents[1]
        native = (root / "src/native/optix/rtdl_optix_core.cpp").read_text()
        strong = (
            root / "experiments/goal5848_strong_baseline/strong_pyoptix.py"
        ).read_text()
        direct = (
            root / "experiments/goal5802_premeasurement/"
            "direct_scalar_worker.cpp"
        ).read_text()
        worker = (
            root / "experiments/goal5848_strong_baseline/worker.py"
        ).read_text()
        runbook = (
            root / "scripts/goal5848_pod_prepare_and_run.sh"
        ).read_text()
        self.assertIn(
            'std::getenv("RTDL_OPTIX_DISK_CACHE_POLICY")', native
        )
        self.assertIn("if (rtdl_optix_disk_cache_disabled())", native)
        self.assertIn("optixDeviceContextSetCacheEnabled(created, 0)", native)
        self.assertNotIn(
            "Goal5848 compares fresh-process module admission", native
        )
        self.assertIn("set_cache_enabled(False)", worker)
        self.assertIn("set_cache_enabled(False)", strong)
        self.assertIn("optixDeviceContextSetCacheEnabled(context->optix, 0)", direct)
        self.assertIn(
            "export RTDL_OPTIX_DISK_CACHE_POLICY=disabled", runbook
        )

    def test_complete_transaction_recounts_every_gate(self):
        receipts = []
        for row in contracts.build_schedule():
            post_import = 110 if row["arm"] == contracts.RTDL_ARM else 100
            steady = {
                contracts.RTDL_ARM: 110,
                contracts.IDIOMATIC_PYOPTIX_ARM: 100,
                contracts.STRONG_PYOPTIX_ARM: 100,
                contracts.DIRECT_OPTIX_ARM: 100,
                contracts.PREDECESSOR_RTDL_ARM: 110,
            }[row["arm"]]
            receipts.append(self._receipt(
                row,
                post_import_ns=post_import,
                steady_ns=steady,
            ))
        result = contracts.evaluate_complete_transaction(
            receipts,
            expected_source_commit="a" * 40,
            expected_predecessor_commit="b" * 40,
        )
        self.assertEqual(result["worker_count"], 80)
        self.assertEqual(
            result["retained_steady_sample_count"],
            80 * contracts.STEADY_REPETITIONS,
        )

    def test_complete_transaction_rejects_bad_seal_and_threshold(self):
        schedule = contracts.build_schedule()
        receipts = [self._receipt(row) for row in schedule]
        bad_seal = copy.deepcopy(receipts)
        bad_seal[0]["measurements"]["steady_complete_execution"][
            "samples_ns"
        ][0] += 1
        with self.assertRaisesRegex(
            contracts.Goal5848ContractError, "seal"
        ):
            contracts.evaluate_complete_transaction(
                bad_seal,
                expected_source_commit="a" * 40,
                expected_predecessor_commit="b" * 40,
            )

        failed_gate = []
        for row in schedule:
            post_import = 200 if row["arm"] == contracts.RTDL_ARM else 100
            failed_gate.append(self._receipt(
                row,
                post_import_ns=post_import,
            ))
        with self.assertRaisesRegex(
            contracts.Goal5848ContractError, "performance gates"
        ):
            contracts.evaluate_complete_transaction(
                failed_gate,
                expected_source_commit="a" * 40,
                expected_predecessor_commit="b" * 40,
            )

    def test_lifecycle_gate_retains_non_gating_post_import_failure(self):
        receipts = []
        for row in contracts.build_schedule():
            if row["arm"] == contracts.RTDL_ARM:
                post_import = 200
                implementation_import = 1
            elif row["arm"] == contracts.STRONG_PYOPTIX_ARM:
                post_import = 100
                implementation_import = 200
            else:
                post_import = 100
                implementation_import = 1
            receipts.append(self._receipt(
                row,
                post_import_ns=post_import,
                implementation_import_ns=implementation_import,
            ))

        result = contracts.evaluate_complete_transaction(
            receipts,
            expected_source_commit="a" * 40,
            expected_predecessor_commit="b" * 40,
        )

        for task in contracts.TASKS:
            self.assertFalse(
                result["tasks"][task][
                    "post_import_diagnostic_reference_pass"
                ]
            )
            self.assertTrue(
                result["tasks"][task]["all_performance_gates_pass"]
            )

    def test_lifecycle_gate_cannot_be_replaced_by_post_import_pass(self):
        receipts = []
        for row in contracts.build_schedule():
            implementation_import = (
                200 if row["arm"] == contracts.RTDL_ARM else 1
            )
            receipts.append(self._receipt(
                row,
                post_import_ns=100,
                implementation_import_ns=implementation_import,
            ))

        with self.assertRaisesRegex(
            contracts.Goal5848ContractError, "performance gates"
        ):
            contracts.evaluate_complete_transaction(
                receipts,
                expected_source_commit="a" * 40,
                expected_predecessor_commit="b" * 40,
            )

    def test_worker_rejects_coherently_resealed_lifecycle_decomposition(self):
        row = next(
            row for row in contracts.build_schedule()
            if row["arm"] == contracts.RTDL_ARM
        )
        receipt = self._receipt(row)
        receipt["measurements"][
            "implementation_import_to_endpoint_gap_ns"
        ] += 1
        receipt["result_sha256"] = contracts.digest({
            key: value
            for key, value in receipt.items()
            if key != "result_sha256"
        })
        with self.assertRaisesRegex(
            contracts.Goal5848ContractError, "lifecycle endpoint"
        ):
            contracts.validate_worker_receipt(
                receipt,
                expected_row=row,
                expected_source_commit="a" * 40,
                expected_predecessor_commit="b" * 40,
            )

    def test_worker_rejects_coherently_resealed_direct_runtime_substitution(self):
        row = next(
            row for row in contracts.build_schedule()
            if row["arm"] == contracts.DIRECT_OPTIX_ARM
        )
        receipt = self._receipt(row)
        receipt["python"] = "3.12.14"
        receipt["result_sha256"] = contracts.digest({
            key: value
            for key, value in receipt.items()
            if key != "result_sha256"
        })
        with self.assertRaisesRegex(
            contracts.Goal5848ContractError, "Direct runtime identity"
        ):
            contracts.validate_worker_receipt(
                receipt,
                expected_row=row,
                expected_source_commit="a" * 40,
                expected_predecessor_commit="b" * 40,
            )

    def test_formal_rtdl_worker_requires_phase_instrumentation(self):
        row = next(
            row for row in contracts.build_schedule()
            if row["arm"] == contracts.RTDL_ARM
        )
        receipt = self._receipt(row)
        del receipt["measurements"]["evidence"]["phase_instrumentation"]
        receipt["result_sha256"] = contracts.digest({
            key: value
            for key, value in receipt.items()
            if key != "result_sha256"
        })
        with self.assertRaisesRegex(
            contracts.Goal5848ContractError, "RTDL execution evidence"
        ):
            contracts.validate_worker_receipt(
                receipt,
                expected_row=row,
                expected_source_commit="a" * 40,
                expected_predecessor_commit="b" * 40,
            )

    def test_formal_pyoptix_workers_require_phase_instrumentation(self):
        for arm, message in (
            (contracts.IDIOMATIC_PYOPTIX_ARM, "idiomatic PyOptix"),
            (contracts.STRONG_PYOPTIX_ARM, "strong PyOptix lifecycle"),
        ):
            with self.subTest(arm=arm):
                row = next(
                    row for row in contracts.build_schedule()
                    if row["arm"] == arm
                )
                receipt = self._receipt(row)
                del receipt["measurements"]["evidence"]["phase_instrumentation"]
                receipt["result_sha256"] = contracts.digest({
                    key: value
                    for key, value in receipt.items()
                    if key != "result_sha256"
                })
                with self.assertRaisesRegex(
                    contracts.Goal5848ContractError, message
                ):
                    contracts.validate_worker_receipt(
                        receipt,
                        expected_row=row,
                        expected_source_commit="a" * 40,
                        expected_predecessor_commit="b" * 40,
                    )

    def test_coherently_resealed_wrong_physical_routes_are_rejected(self):
        cases = (
            (contracts.RTDL_ARM, "full traversal native snapshot"),
            (contracts.IDIOMATIC_PYOPTIX_ARM, "idiomatic PyOptix"),
            (contracts.STRONG_PYOPTIX_ARM, "strong PyOptix operation"),
            (contracts.DIRECT_OPTIX_ARM, "Direct worker execution"),
        )
        for arm, message in cases:
            with self.subTest(arm=arm):
                row = next(
                    row for row in contracts.build_schedule()
                    if row["arm"] == arm
                    and row["task"] == contracts.RELATION_TASK
                )
                receipt = self._receipt(row)
                evidence = receipt["measurements"]["evidence"]
                if arm == contracts.RTDL_ARM:
                    traversal = evidence["diagnostic_traversal_receipt"]
                    traversal["native_snapshot"]["successful_launch_count"] = 0
                    traversal["receipt_sha256"] = contracts.digest({
                        key: value
                        for key, value in traversal.items()
                        if key != "receipt_sha256"
                    })
                elif arm == contracts.IDIOMATIC_PYOPTIX_ARM:
                    evidence["host_continuation_disclosed"] = False
                elif arm == contracts.STRONG_PYOPTIX_ARM:
                    evidence["optix_launch_count"] = 0
                else:
                    evidence["direct_worker_receipt"][
                        "execute_or_regime_durations_ns"
                    ][0] += 1
                receipt["result_sha256"] = contracts.digest({
                    key: value
                    for key, value in receipt.items()
                    if key != "result_sha256"
                })
                with self.assertRaisesRegex(
                    contracts.Goal5848ContractError, message
                ):
                    contracts.validate_worker_receipt(
                        receipt,
                        expected_row=row,
                        expected_source_commit="a" * 40,
                        expected_predecessor_commit="b" * 40,
                    )

    def test_rtdl_timed_fast_path_must_not_claim_an_uncomputed_digest(self):
        row = next(
            row for row in contracts.build_schedule()
            if row["arm"] == contracts.RTDL_ARM
        )
        receipt = self._receipt(row)
        receipt["measurements"]["evidence"]["latest_output_sha256"] = (
            contracts.TASK_CONTRACTS[row["task"]]["public_output_sha256"]
        )
        receipt["result_sha256"] = contracts.digest({
            key: value
            for key, value in receipt.items()
            if key != "result_sha256"
        })
        with self.assertRaisesRegex(
            contracts.Goal5848ContractError, "RTDL execution evidence"
        ):
            contracts.validate_worker_receipt(
                receipt,
                expected_row=row,
                expected_source_commit="a" * 40,
                expected_predecessor_commit="b" * 40,
            )

    def test_full_traversal_receipt_hostile_mutations_fail_closed(self):
        task = contracts.RELATION_TASK
        cases = []

        wrong_width = self._rtdl_traversal(task)
        wrong_width["native_snapshot"]["attempted_launch_count"] = True
        cases.append(wrong_width)

        incomplete_callsite = self._rtdl_traversal(task)
        incomplete_callsite["native_snapshot"][
            "incomplete_callsite_lines"
        ][0] = 17
        cases.append(incomplete_callsite)

        wrong_nonce = self._rtdl_traversal(task)
        wrong_nonce["native_snapshot"]["nonce_lo"] += 1
        cases.append(wrong_nonce)

        weakened_rule = self._rtdl_traversal(task)
        weakened_rule["claim_rules"][
            "successful_optix_launch_required"
        ] = False
        cases.append(weakened_rule)

        for receipt in cases:
            with self.subTest(receipt=receipt):
                receipt["receipt_sha256"] = contracts.digest({
                    key: value
                    for key, value in receipt.items()
                    if key != "receipt_sha256"
                })
                with self.assertRaises(contracts.Goal5848ContractError):
                    contracts._validate_rtdl_traversal_receipt(
                        receipt,
                        task=task,
                        provider_library_sha256="d" * 64,
                    )

    def test_coherently_resealed_wrong_public_output_is_rejected(self):
        row = contracts.build_schedule()[0]
        receipt = self._receipt(row)
        receipt["measurements"]["evidence"]["public_output"][0][1] = 17
        receipt["result_sha256"] = contracts.digest({
            key: value
            for key, value in receipt.items()
            if key != "result_sha256"
        })
        with self.assertRaisesRegex(
            contracts.Goal5848ContractError, "output evidence"
        ):
            contracts.validate_worker_receipt(
                receipt,
                expected_row=row,
                expected_source_commit="a" * 40,
                expected_predecessor_commit="b" * 40,
            )


if __name__ == "__main__":
    unittest.main()

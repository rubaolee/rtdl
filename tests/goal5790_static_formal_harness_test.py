from __future__ import annotations

import ast
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from scripts import goal5790_static_controller as controller
from scripts import goal5790_static_evaluate as evaluate
from scripts import goal5790_static_independent_recount as recount
from scripts.goal5790_static_formal_contract import (
    COLD,
    EXECUTION_STATE,
    FUSION_OFF,
    FUSION_ON,
    MECHANISM_ID,
    OPERATION_EVIDENCE_TCB,
    OUTPUT_CONTRACT_SHA256,
    PHYSICAL_ENCODING_SHA256,
    SEMANTIC_REQUEST_SHA256,
    SHARED_FREEZE_CONTENT_SHA256,
    SHARED_FREEZE_FILE_SHA256,
    SHARED_FREEZE_RELATIVE_PATH,
    contract_document,
    digest,
    expected_operation_contract,
    lifecycle_contract,
    schedule,
    statistical_rows,
    timer_contract,
    validate_shared_freeze,
)
from rtdsl.v4_fusion_ablation import (
    FusionVariant,
    build_checked_u64_product_sum_ablation_plan,
)
from tests.goal5790_fusion_ablation_contract_test import (
    _authority as _real_target_authority,
    _freeze as _real_shared_freeze,
)


ROOT = Path(__file__).resolve().parents[1]
SHARED_FREEZE = ROOT / SHARED_FREEZE_RELATIVE_PATH


def _sha(label: str) -> str:
    return digest({"synthetic_identity": label})


def _bundle_id(name: str) -> int:
    value = 1469598103934665603
    for byte in name.encode("utf-8"):
        value ^= byte
        value = (value * 1099511628211) & ((1 << 64) - 1)
    return value


def _behavioral_receipt(
    worker_index: int, segment_index: int, output_sha: str,
    native_sha: str, query_count: int, semantic_binding: dict[str, object],
) -> dict[str, object]:
    nonce_hi = 700_000 + worker_index
    nonce_lo = 900_000 + segment_index
    bundle_id = _bundle_id("v4_builtin_triangle_checked_reduction_composed")
    body = {
        "schema": "rtdl.physical_execution.traversal_receipt.v1",
        "provider_library": "librtdl_optix",
        "provider_library_path": "/synthetic/librtdl_optix.so",
        "provider_library_sha256": native_sha,
        "route_identity": (
            "v4_builtin_triangle_callback_ir:partner_resident_checked_count_v1"),
        "semantic_digest": digest(semantic_binding),
        "physical_executor_classification": "optix_traversal_observed",
        "output_digest": output_sha,
        "nonce": {"hi": nonce_hi, "lo": nonce_lo},
        "expected_program_bundles": [
            "v4_builtin_triangle_checked_reduction_composed"],
        "expected_program_bundle_ids": [bundle_id],
        "expected_program_observed_at_receipt_edge": True,
        "native_snapshot": {
            "nonce_hi": nonce_hi,
            "nonce_lo": nonce_lo,
            "attempted_launch_count": 2,
            "successful_launch_count": 2,
            "complete_context_launch_count": 2,
            "failed_launch_count": 0,
            "incomplete_context_launch_count": 0,
            "context_bind_count": 2,
            "raygen_invocation_count": query_count,
            "program_bundle_mix": bundle_id,
            "traversable_mix": 11,
            "pipeline_mix": 12,
            "sbt_mix": 13,
            "stream_mix": 14,
            "params_mix": 15,
            "callsite_mix": 16,
            "first_program_bundle_id": bundle_id,
            "last_program_bundle_id": bundle_id,
            "pending_context_at_finish": 0,
            "session_error": 0,
            "first_traversable": f"gas-first-{worker_index}-{segment_index}",
            "last_traversable": f"gas-last-{worker_index}-{segment_index}",
            "incomplete_callsite_record_count": 0,
            "incomplete_callsite_lines": [0] * 32,
        },
        "claim_rules": {
            "provider_name_alone_proves_traversal": False,
            "selected_template_alone_proves_traversal": False,
            "successful_optix_launch_required": True,
            "nonzero_traversable_binding_required": True,
            "program_bundle_binding_required": True,
            "output_digest_bound": True,
        },
    }
    return {**body, "receipt_sha256": digest(body)}


def _operation_receipt(
    *,
    worker_index: int,
    variant: str,
    plan: dict[str, object],
    output_sha: str,
    behavioral: dict[str, object],
) -> dict[str, object]:
    plan_sha = str(plan["plan_sha256"])
    value_count = int(plan["value_count"])
    requirements = plan["operation_requirements"]
    contract_body = {
        "schema": "rtdl.v4.operation_sequence_contract.v1",
        "plan_sha256": plan_sha,
        "mechanism_id": MECHANISM_ID,
        "variant": variant,
        "declared_value_count": value_count,
        "requirements": requirements,
        "tcb_statement": OPERATION_EVIDENCE_TCB,
        "timing_or_duration_recorded": False,
        "hardware_introspection_claimed": False,
    }
    contract_sha = digest(contract_body)
    previous = contract_sha
    events = []
    for index, requirement in enumerate(requirements):
        units = requirement["units_per_value"] * value_count + requirement["fixed_units"]
        byte_count = requirement["bytes_per_unit"] * units + requirement["fixed_bytes"]
        event = {
            "schema": "rtdl.v4.operation_evidence_event.v1",
            "sequence": index,
            "operation_id": requirement["operation_id"],
            "kind": requirement["kind"],
            "accounted_units": units,
            "accounted_bytes": byte_count,
            "previous_event_sha256": previous,
            "recorded_after_callable_success": True,
        }
        event["event_sha256"] = digest(event)
        previous = event["event_sha256"]
        events.append(event)
    body = {
        "schema": "rtdl.v4.operation_evidence_receipt.v1",
        "contract_sha256": contract_sha,
        "plan_sha256": plan_sha,
        "mechanism_id": MECHANISM_ID,
        "variant": variant,
        "execution_nonce": f"synthetic-goal5790-worker-{worker_index:04d}",
        "value_count": value_count,
        "output_sha256": output_sha,
        "traversal_receipt_sha256": behavioral["receipt_sha256"],
        "events": events,
        "event_chain_sha256": previous,
        "successful_event_count": len(events),
        "event_evidence_tcb": OPERATION_EVIDENCE_TCB,
        "hardware_introspection_claimed": False,
        "opaque_partner_kernel_count_claimed": False,
        "timing_or_duration_recorded": False,
    }
    return {**body, "receipt_sha256": digest(body)}


def _checked_reduction(
    variant: str, *, query_count: int, primitive_count: int, scalar_sum: int,
) -> dict[str, object]:
    on = variant == FUSION_ON
    return {
        "schema": "rtdl.v4.checked_u64_weighted_reduction.receipt.v1",
        "maximum_value": primitive_count if on else primitive_count,
        "maximum_weight": 1,
        "weight_sum": query_count,
        "value_count": query_count,
        "value_upper_bound": primitive_count,
        "device_kernel_launch_count": 1 if on else 0,
        "host_synchronization_count": 1 if on else 3,
        "logical_reduction_count": 0 if on else 3,
        "device_materialization_count": 0 if on else 1,
        "operation_counts_event_derived": True,
        "maximum_value_is_device_observed": on,
        "maximum_value_provenance": (
            "device_observed" if on
            else "optix_producer_declared_primitive_bound"),
        "provisional_sum_trusted_only_after_bounds": True,
    }


def _segments(
    *,
    schedule_row: dict[str, object],
    input_sha: str,
    output_contract_sha: str,
    oracle_contract_sha: str,
    timer_sha: str,
    lifecycle_sha: str,
    target_authority: dict[str, object],
) -> list[dict[str, object]]:
    variant = str(schedule_row["variant"])
    worker_index = int(schedule_row["worker_index"])
    result = []
    for segment_index, (query_count, scalar_sum) in enumerate(((5, 3), (7, 5), (4, 7))):
        relation_count = query_count * 2
        primitive_count = query_count * 3
        partition = {"kind": "synthetic_real_runtime_shape", "ordinal": segment_index}
        segment_input_sha = digest({
            "global_input_sha256": input_sha,
            "segment_id": segment_index,
            "partition": partition,
            "relation_count": relation_count,
            "primitive_count": primitive_count,
            "query_count": query_count,
        })
        plan = build_checked_u64_product_sum_ablation_plan(
            _real_shared_freeze(),
            variant=FusionVariant(variant),
            target_materialization=_real_target_authority(),
            input_sha256=segment_input_sha,
            output_contract_sha256=output_contract_sha,
            oracle_sha256=oracle_contract_sha,
            timer_contract_sha256=timer_sha,
            lifecycle_contract_sha256=lifecycle_sha,
            value_count=query_count,
        ).to_dict()
        self_target = _real_target_authority().to_dict()
        if self_target != target_authority:
            raise AssertionError("synthetic target authority drift")
        output_sha = digest(scalar_sum)
        semantic_binding = {
            "authority": target_authority["callback_authority_nonce"],
            "contract": target_authority["contract_sha256"],
            "abi": target_authority["abi_sha256"],
            "composed_ptx": target_authority["composed_program_sha256"],
            "native": target_authority["native_library_sha256"],
            "device_column_count": True,
        }
        behavioral = _behavioral_receipt(
            worker_index, segment_index, output_sha,
            str(target_authority["native_library_sha256"]), query_count,
            semantic_binding)
        operation = _operation_receipt(
            worker_index=worker_index,
            variant=variant,
            plan=plan,
            output_sha=output_sha,
            behavioral=behavioral,
        )
        result.append({
            "segment_id": segment_index,
            "partition": partition,
            "relation_count": relation_count,
            "primitive_count": primitive_count,
            "query_count": query_count,
            "scalar_sum": scalar_sum,
            "output_sha256": output_sha,
            "fusion_ablation_plan": plan,
            "operation_evidence_receipt": operation,
            "checked_u64_weighted_reduction": _checked_reduction(
                variant, query_count=query_count,
                primitive_count=primitive_count, scalar_sum=scalar_sum),
            "traversal_receipt": behavioral,
            "device_phase_terminal_state": "device_complete_unsealed",
            "evidence_phase_terminal_state": "sealed",
            "evidence_sealed_after_device_phase": True,
            "traversal_semantic_binding": semantic_binding,
        })
    return result


def _worker(schedule_row: dict[str, object], *, favor_fusion: bool) -> dict[str, object]:
    worker_index = int(schedule_row["worker_index"])
    row_id = str(schedule_row["row_id"])
    variant = str(schedule_row["variant"])
    pair_index = int(schedule_row["pair_index"])
    input_sha = _sha("input:" + str(schedule_row["dataset_id"]))
    output_scalar = 15
    output_sha = digest(output_scalar)
    output_contract_sha = OUTPUT_CONTRACT_SHA256
    oracle_contract_sha = _sha("oracle-contract:" + str(schedule_row["dataset_id"]))
    timer_value = timer_contract(str(schedule_row["lifecycle"]))
    lifecycle_value = lifecycle_contract(str(schedule_row["lifecycle"]))
    timer_sha = digest(timer_value)
    lifecycle_sha = digest(lifecycle_value)
    target = _real_target_authority().to_dict()
    baseline = 2.0 if variant == FUSION_OFF else 1.0
    if not favor_fusion:
        baseline = 1.0 if variant == FUSION_OFF else 2.0
    execute_seconds = baseline + pair_index * 0.001
    if schedule_row["lifecycle"] == COLD:
        phase = {
            "loading_seconds": 0.01,
            "preparation_seconds": 0.02,
            "execute_seconds": execute_seconds,
            "close_seconds": 0.01,
            "same_worker_mutually_exclusive_phases": True,
            "nested_phase_medians_summed": False,
        }
        registered = sum(
            phase[key]
            for key in (
                "loading_seconds",
                "preparation_seconds",
                "execute_seconds",
                "close_seconds",
            )
        )
    else:
        phase = {
            "loading_seconds": 0.01,
            "preparation_seconds": 0.02,
            "execute_seconds": execute_seconds,
            "close_seconds": 0.01,
            "same_worker_mutually_exclusive_phases": True,
            "nested_phase_medians_summed": False,
        }
        registered = execute_seconds
    return {
        "schema": evaluate.WORKER_SCHEMA,
        "goal": 5790,
        "synthetic_contract_test_only": True,
        "formal_worker": False,
        **schedule_row,
        "parent_pid": 100_000 + worker_index,
        "registered_complete_endpoint_seconds": registered,
        "phase_accounting": phase,
        "input_sha256": input_sha,
        "output_sha256": output_sha,
        "oracle_output_sha256": output_sha,
        "oracle_contract_sha256": oracle_contract_sha,
        "semantic_request_sha256": SEMANTIC_REQUEST_SHA256,
        "physical_encoding_sha256": PHYSICAL_ENCODING_SHA256,
        "shared_contract_freeze_file_sha256": SHARED_FREEZE_FILE_SHA256,
        "shared_contract_freeze_content_sha256": SHARED_FREEZE_CONTENT_SHA256,
        "execution_source_archive_sha256": target["execution_source_archive_sha256"],
        "execution_source_tree_sha256": target["execution_source_tree_sha256"],
        "native_library_sha256": target["native_library_sha256"],
        "timer_contract_sha256": timer_sha,
        "timer_contract": timer_value,
        "lifecycle_contract_sha256": lifecycle_sha,
        "lifecycle_contract": lifecycle_value,
        "output_contract_sha256": output_contract_sha,
        "output_scalar_u64": output_scalar,
        "oracle_output_scalar_u64": output_scalar,
        "target_materialization_authority": target,
        "segment_evidence": _segments(
            schedule_row=schedule_row,
            input_sha=input_sha,
            output_contract_sha=output_contract_sha,
            oracle_contract_sha=oracle_contract_sha,
            timer_sha=timer_sha,
            lifecycle_sha=lifecycle_sha,
            target_authority=target,
        ),
        "segment_count": 3,
        "two_phase_execution_evidence_seal_enforced": True,
        "evidence_hashing_or_serialization_inside_registered_timer": False,
        "comparator_inside_registered_timer": False,
        "receipt_serialization_inside_registered_timer": False,
        "retry_resume_replacement_row_drop_relabel_used": False,
    }


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _raw_cohort(root: Path, *, favor_fusion: bool = True) -> Path:
    root.mkdir()
    workers = root / "workers"
    workers.mkdir()
    _write_json(root / "FORMAL_CONTRACT.json", contract_document())
    _write_json(root / "SCHEDULE.json", list(schedule()))
    for row in schedule():
        _write_json(
            workers / f"worker_{int(row['worker_index']):04d}.json",
            _worker(row, favor_fusion=favor_fusion),
        )
    return root


class Goal5790StaticFormalHarnessTest(unittest.TestCase):
    def test_contract_freezes_six_rows_and_96_balanced_workers(self) -> None:
        validate_shared_freeze(SHARED_FREEZE)
        self.assertEqual(len(statistical_rows()), 6)
        self.assertEqual(len(schedule()), 96)
        self.assertEqual(len({row["dataset_id"] for row in statistical_rows()}), 3)
        self.assertEqual(len({row["lifecycle"] for row in statistical_rows()}), 2)
        self.assertEqual(contract_document()["particle_rows"], 0)
        for row in statistical_rows():
            workers = [item for item in schedule() if item["row_id"] == row["row_id"]]
            self.assertEqual(len(workers), 16)
            for pair_index in range(8):
                pair = [item for item in workers if item["pair_index"] == pair_index]
                expected = (
                    [FUSION_OFF, FUSION_ON]
                    if pair_index % 2 == 0
                    else [FUSION_ON, FUSION_OFF]
                )
                self.assertEqual(
                    [item["variant"] for item in sorted(pair, key=lambda item: item["order_ordinal"])],
                    expected,
                )

    def test_controller_is_create_only_and_cannot_launch_workers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "static"
            controller.prepare_static_draft(
                output_root=output, shared_freeze_path=SHARED_FREEZE
            )
            gate = json.loads((output / "EXECUTION_GATE.json").read_text())
            self.assertEqual(gate["execution_state"], EXECUTION_STATE)
            self.assertEqual(gate["target_worker_count"], 0)
            self.assertEqual(gate["registered_target_timing_count"], 0)
            with self.assertRaises(FileExistsError):
                controller.prepare_static_draft(
                    output_root=output, shared_freeze_path=SHARED_FREEZE
                )
            with self.assertRaises(PermissionError):
                controller.execute_target_workers()
        source = Path(controller.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        self.assertNotIn("subprocess", imported)
        self.assertFalse(any(
            isinstance(node, ast.Attribute) and node.attr == "Popen"
            for node in ast.walk(tree)
        ))

    def test_primary_and_independent_recount_match_on_synthetic_96_worker_cohort(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            raw = _raw_cohort(Path(temp) / "raw")
            primary = evaluate.build_evaluation(raw)
            independent = recount.build_recount(raw)
        self.assertEqual(primary["rows"], independent["rows"])
        self.assertEqual(primary["worker_count"], 96)
        self.assertEqual(primary["unique_parent_pid_count"], 96)
        self.assertEqual(primary["independent_row_count"], 6)
        self.assertTrue(all(row["paired_ratio_median"] > 1.0 for row in primary["rows"]))
        self.assertTrue(all(row["greater_than_one_favors"] == FUSION_ON for row in primary["rows"]))
        self.assertFalse(primary["cross_dataset_or_lifecycle_compensation_used"])
        self.assertFalse(primary["target_performance_observation"])

    def test_fixture_is_real_runtime_shaped_and_multisegment(self) -> None:
        worker = _worker(dict(schedule()[0]), favor_fusion=True)
        self.assertEqual(worker["segment_count"], 3)
        self.assertEqual(len(worker["segment_evidence"]), 3)
        self.assertEqual(
            worker["target_materialization_authority"]["schema"],
            "rtdl.v4.target_materialization_authority.v2",
        )
        for ordinal, segment in enumerate(worker["segment_evidence"]):
            self.assertEqual(segment["segment_id"], ordinal)
            self.assertEqual(
                segment["fusion_ablation_plan"]["schema"],
                "rtdl.v4.fusion_ablation_plan.v2",
            )
            self.assertEqual(
                segment["traversal_receipt"]["schema"],
                "rtdl.physical_execution.traversal_receipt.v1",
            )
            self.assertEqual(
                segment["device_phase_terminal_state"],
                "device_complete_unsealed",
            )
            self.assertTrue(segment["evidence_sealed_after_device_phase"])
        cold = _worker(dict(schedule()[0]), favor_fusion=True)
        prepared_row = next(row for row in schedule() if row["lifecycle"] != COLD)
        prepared = _worker(dict(prepared_row), favor_fusion=True)
        self.assertNotEqual(
            cold["timer_contract_sha256"], prepared["timer_contract_sha256"])
        self.assertNotEqual(
            cold["lifecycle_contract_sha256"],
            prepared["lifecycle_contract_sha256"],
        )

    def test_direction_reversal_is_reported_not_compensated(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            raw = _raw_cohort(Path(temp) / "raw", favor_fusion=False)
            primary = evaluate.build_evaluation(raw)
            independent = recount.build_recount(raw)
        self.assertEqual(primary["rows"], independent["rows"])
        self.assertTrue(all(row["paired_ratio_median"] < 1.0 for row in primary["rows"]))
        self.assertTrue(all(row["median_favors_fusion"] is False for row in primary["rows"]))

    def _assert_both_reject(self, mutate) -> None:
        with tempfile.TemporaryDirectory() as temp:
            raw = _raw_cohort(Path(temp) / "raw")
            worker_path = raw / "workers" / "worker_0000.json"
            worker = json.loads(worker_path.read_text())
            mutate(worker)
            _write_json(worker_path, worker)
            with self.assertRaises(RuntimeError):
                evaluate.build_evaluation(raw)
            with self.assertRaises(RuntimeError):
                recount.build_recount(raw)

    def test_missing_duplicate_reordered_and_forged_operation_events_fail_closed(self) -> None:
        def missing(worker):
            worker["segment_evidence"][0]["operation_evidence_receipt"]["events"].pop()

        def duplicate(worker):
            receipt = worker["segment_evidence"][0]["operation_evidence_receipt"]
            receipt["events"].append(
                deepcopy(receipt["events"][-1])
            )

        def reordered(worker):
            events = worker["segment_evidence"][0]["operation_evidence_receipt"]["events"]
            events[0], events[1] = events[1], events[0]

        def forged(worker):
            worker["segment_evidence"][0]["operation_evidence_receipt"][
                "events"][0]["accounted_units"] += 1

        for name, mutation in (
            ("missing", missing),
            ("duplicate", duplicate),
            ("reordered", reordered),
            ("forged", forged),
        ):
            with self.subTest(name=name):
                self._assert_both_reject(mutation)

    def test_resigned_wrong_declared_value_count_fails_closed(self) -> None:
        def resign_with_wrong_count(worker):
            segment = worker["segment_evidence"][0]
            old_plan = segment["fusion_ablation_plan"]
            wrong_plan = build_checked_u64_product_sum_ablation_plan(
                _real_shared_freeze(),
                variant=FusionVariant(str(worker["variant"])),
                target_materialization=_real_target_authority(),
                input_sha256=str(old_plan["input_sha256"]),
                output_contract_sha256=str(worker["output_contract_sha256"]),
                oracle_sha256=str(worker["oracle_contract_sha256"]),
                timer_contract_sha256=str(worker["timer_contract_sha256"]),
                lifecycle_contract_sha256=str(worker["lifecycle_contract_sha256"]),
                value_count=int(segment["query_count"]) + 1,
            ).to_dict()
            segment["fusion_ablation_plan"] = wrong_plan
            segment["operation_evidence_receipt"] = _operation_receipt(
                worker_index=int(worker["worker_index"]),
                variant=str(worker["variant"]),
                plan=wrong_plan,
                output_sha=str(segment["output_sha256"]),
                behavioral=segment["traversal_receipt"],
            )

        self._assert_both_reject(resign_with_wrong_count)

    def test_resigned_false_segment_output_still_fails_closed(self) -> None:
        def resign_local_false_output(worker):
            segment = worker["segment_evidence"][0]
            segment["scalar_sum"] = int(segment["scalar_sum"]) + 1
            segment["output_sha256"] = digest(segment["scalar_sum"])
            semantic = segment["traversal_semantic_binding"]
            traversal = _behavioral_receipt(
                int(worker["worker_index"]), int(segment["segment_id"]),
                str(segment["output_sha256"]),
                str(worker["native_library_sha256"]),
                int(segment["query_count"]), semantic,
            )
            segment["traversal_receipt"] = traversal
            segment["operation_evidence_receipt"] = _operation_receipt(
                worker_index=int(worker["worker_index"]),
                variant=str(worker["variant"]),
                plan=segment["fusion_ablation_plan"],
                output_sha=str(segment["output_sha256"]),
                behavioral=traversal,
            )

        self._assert_both_reject(resign_local_false_output)

    def test_resigned_target_authority_drift_and_segment_reorder_fail_closed(self) -> None:
        def resigned_target(worker):
            target = worker["target_materialization_authority"]
            target["execution_source_tree_sha256"] = _sha("forged-source-tree")
            worker["execution_source_tree_sha256"] = target[
                "execution_source_tree_sha256"]
            unsigned = dict(target)
            unsigned.pop("receipt_sha256")
            target["receipt_sha256"] = digest(unsigned)

        def reordered_segments(worker):
            segments = worker["segment_evidence"]
            segments[0], segments[1] = segments[1], segments[0]

        self._assert_both_reject(resigned_target)
        self._assert_both_reject(reordered_segments)

    def test_resigned_arbitrary_traversal_semantic_digest_fails_closed(self) -> None:
        def resigned_semantic(worker, field, value):
            segment = worker["segment_evidence"][0]
            binding = segment["traversal_semantic_binding"]
            binding[field] = value
            traversal = _behavioral_receipt(
                int(worker["worker_index"]), int(segment["segment_id"]),
                str(segment["output_sha256"]),
                str(worker["native_library_sha256"]),
                int(segment["query_count"]), binding,
            )
            segment["traversal_receipt"] = traversal
            segment["operation_evidence_receipt"] = _operation_receipt(
                worker_index=int(worker["worker_index"]),
                variant=str(worker["variant"]),
                plan=segment["fusion_ablation_plan"],
                output_sha=str(segment["output_sha256"]),
                behavioral=traversal,
            )
        for field, value in (
            ("authority", "synthetic-unbound-authority-0001"),
            ("contract", _sha("unbound-contract")),
            ("abi", _sha("unbound-abi")),
            ("composed_ptx", _sha("unbound-composed-ptx")),
        ):
            with self.subTest(field=field):
                self._assert_both_reject(
                    lambda worker, field=field, value=value:
                        resigned_semantic(worker, field, value))

    def test_resigned_structured_recipe_drift_fails_closed(self) -> None:
        def resigned_recipe(worker):
            target = worker["target_materialization_authority"]
            recipe = target["fusion_off_downstream_operation_recipe"]
            recipe["implementation"]["operations"][-1] = "cp.asnumpy(fake)"
            target["fusion_off_downstream_operation_recipe_sha256"] = digest(recipe)
            unsigned = dict(target)
            unsigned.pop("receipt_sha256")
            target["receipt_sha256"] = digest(unsigned)

        self._assert_both_reject(resigned_recipe)

    def test_output_behavioral_identity_and_pid_defects_fail_closed(self) -> None:
        mutations = {
            "output": lambda worker: worker.__setitem__(
                "oracle_output_sha256", _sha("wrong-output")
            ),
            "behavioral": lambda worker: worker["segment_evidence"][0][
                "traversal_receipt"]["native_snapshot"
            ].__setitem__("unbound_launch_count", 1),
            "identity": lambda worker: worker.__setitem__(
                "native_library_sha256", _sha("other-native")
            ),
            "pid": lambda worker: worker.__setitem__("parent_pid", 100_001),
        }
        for name, mutation in mutations.items():
            with self.subTest(name=name):
                self._assert_both_reject(mutation)

    def test_independent_recount_imports_no_controller_evaluator_or_application(self) -> None:
        source = Path(recount.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.add(node.module)
        joined = "\n".join(sorted(modules)).lower()
        self.assertNotIn("controller", joined)
        self.assertNotIn("evaluate", joined)
        self.assertNotIn("paper-reproduction-apps", joined)
        self.assertNotIn("rtdsl", joined)

    def test_selection_logic_has_no_app_dataset_result_or_timing_dispatch(self) -> None:
        contract_source = (ROOT / "scripts/goal5790_static_formal_contract.py").read_text(
            encoding="utf-8"
        )
        schedule_function = contract_source[
            contract_source.index("def schedule()") : contract_source.index(
                "def expected_operation_contract"
            )
        ]
        self.assertIn("pair_index % 2", schedule_function)
        tree = ast.parse(schedule_function)
        branch_tests = [node.test for node in ast.walk(tree) if isinstance(node, ast.IfExp)]
        self.assertEqual(len(branch_tests), 1)
        self.assertEqual(ast.unparse(branch_tests[0]), "pair_index % 2 == 0")
        self.assertFalse(any(isinstance(node, ast.If) for node in ast.walk(tree)))


if __name__ == "__main__":
    unittest.main()

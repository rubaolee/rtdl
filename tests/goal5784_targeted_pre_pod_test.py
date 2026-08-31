from __future__ import annotations

import ast
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
import unittest

import goal5784_targeted_controller as controller
import goal5784_targeted_evaluate as evaluator
import goal5784_targeted_recount as recount
from goal5784_mechanism_binding import validate_triangle_reduction_receipts
from goal5784_targeted_formal_contract import (
    COLD, TARGET_UNIT_IDS, UNIT_BY_ID, V2, V4, contract_document,
    contract_sha256, schedule,
    statistical_rows,
)
from goal5784_targeted_runtime_inputs import build_targeted_inputs


ROOT = Path.cwd()


def _artifact(env_name: str, fallback: str) -> Path:
    value = os.environ.get(env_name)
    return Path(value) if value else ROOT / fallback


def _harness_file(name: str) -> Path:
    root = os.environ.get("RTDL_GOAL5784_HARNESS_ROOT")
    return (Path(root) if root else ROOT / "scripts") / name


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _receipt(rows: list[dict[str, object]]) -> dict[str, object]:
    base = {
        "physical_executor_classification": "optix_traversal_observed",
        "native_snapshot": {
            "successful_launch_count": 1, "complete_context_launch_count": 1,
            "failed_launch_count": 0, "incomplete_context_launch_count": 0,
            "unbound_launch_count": 0, "pending_context_at_finish": 0,
            "session_error": 0, "first_traversable": "gas:first",
            "last_traversable": "gas:last",
        },
    }
    canonical = [{key: row[key] for key in (
        "row_id", "input_sha256", "output_sha256")} for row in rows]
    base["registered_row_binding"] = {
        "schema": "rtdl.goal5776.registered_row_binding.v1",
        "binding_scope": "post_timer_evidence_binding__not_native_claim",
        "row_count": len(canonical),
        "ordered_rows_sha256": _digest(canonical),
        "unbound_traversal_receipt_sha256": _digest(base),
    }
    return base


class Goal5784TargetedPrePodTest(unittest.TestCase):
    def _build_synthetic_raw(self, root: Path) -> None:
        workers = root / "workers"
        workers.mkdir(parents=True)
        (root / "FORMAL_CONTRACT.json").write_text(
            json.dumps(contract_document(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        (root / "SCHEDULE.json").write_text(
            json.dumps(list(schedule()), indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        reduction = validate_triangle_reduction_receipts([{
            "schema": "rtdl.v4.checked_u64_weighted_reduction.receipt.v1",
            "maximum_value": 7, "maximum_weight": 3, "weight_sum": 11,
            "value_count": 17, "value_upper_bound": 20,
            "device_kernel_launch_count": 1,
            "host_synchronization_count": 1,
            "provisional_sum_trusted_only_after_bounds": True,
        }])
        for spec in schedule():
            unit = UNIT_BY_ID[str(spec["unit_id"])]
            seconds = 2.0 if spec["method"] == V2 else 1.0
            row_id = unit.statistical_row_ids_for(str(spec["lifecycle"]))[0]
            timed = [{
                "row_id": row_id,
                "input_sha256": _digest({"unit": unit.unit_id, "input": 1}),
                "output_sha256": _digest({"row": row_id, "output": 7}),
                "registered_complete_endpoint_seconds": seconds,
            }]
            if spec["method"] == V2:
                mechanism = {"mode": "not_applicable_to_v2_direct"}
                cache = {"mode": "not_applicable_to_v2_direct"}
            elif unit.app == "triangle_counting":
                mechanism = reduction
                cache = ({"mode": "sealed_read_only_manifest", "hit_count": 1,
                          "miss_count": 0, "disabled_count": 0}
                         if unit.v4_numba_leaf_cache_required else
                         {"mode": "not_applicable_no_numba_leaf", "hit_count": 0,
                          "miss_count": 0, "disabled_count": 0})
            else:
                mechanism = {
                    "schema": "rtdl.goal5784.mechanism_binding.v1",
                    "mechanism_id": "canonical_packed_hierarchy_output_binding",
                    "evidence_level": "frozen_source_route__not_fusion",
                    "execution_source_sha256": "1" * 64,
                    "rt_barneshut_is_fusion": False,
                }
                cache = {"mode": "not_applicable_no_numba_leaf", "hit_count": 0,
                         "miss_count": 0, "disabled_count": 0}
            payload = {
                "schema": "rtdl.goal5784.targeted_formal_worker.v1",
                "run_goal_id": 5784,
                "worker_index": spec["worker_index"],
                "parent_pid": 100000 + int(spec["worker_index"]),
                "lifecycle": spec["lifecycle"], "unit_id": unit.unit_id,
                "method": spec["method"], "pair_index": spec["pair_index"],
                "order_ordinal": spec["order_ordinal"], "formal_worker": True,
                "matched": True,
                "registered_endpoint_boundary_id": (
                    "symmetric_user_input_to_canonical_output_bound_receipt_and_cold_teardown.v1"),
                "comparator_inside_registered_timer": False,
                "close_inside_registered_timer": spec["lifecycle"] == COLD,
                "loading_seconds_reported_separately": (
                    None if spec["lifecycle"] == COLD else 0.0),
                "preparation_seconds_reported_separately": (
                    None if spec["lifecycle"] == COLD else 0.0),
                "prepared_session_complete_wall_seconds_reported_separately": None,
                "default_selected_between_application_algorithms": False,
                "retry_resume_replacement_row_drop_relabel_used": False,
                "traversal_receipt": _receipt(timed),
                "phase_accounting": {
                    "loading_seconds": 0.0, "preparation_seconds": 0.0,
                    "close_seconds": 0.0, "row_execute_seconds": {row_id: seconds},
                    "same_worker_mutually_exclusive_phases": True,
                    "nested_phase_medians_summed": False,
                },
                "rows": timed, "leaf_cache": cache,
                "mechanism_binding": mechanism,
                "bundle_sha256": "0" * 64, "data_archive_sha256": "9" * 64,
                "execution_source_sha256": "1" * 64,
                "source_tree_sha256": "2" * 64,
                "rtdbscan_evidence_sha256": "b" * 64,
                "native_library_sha256": "3" * 64,
                "target_identity_sha256": "4" * 64,
                "prepared_identity_sha256": "8" * 64,
                "plan_sha256": "5" * 64, "formal_identity_sha256": "6" * 64,
                "leaf_cache_manifest_sha256": "7" * 64,
                "expected_value_statement_sha256": "c" * 64,
                "runtime_budget_sha256": "d" * 64,
                "preregistration_sha256": "e" * 64,
                "formal_contract_sha256": contract_sha256(),
                "runtime_sha256": "a" * 64,
            }
            (workers / f"{int(spec['worker_index']):04d}.json").write_text(
                json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    def test_exact_scope_is_four_units_eight_rows_128_workers(self) -> None:
        self.assertEqual(TARGET_UNIT_IDS, (
            "triangle__com_dblp__rt_2a1",
            "triangle__cit_patents__rt_2a1",
            "triangle__soc_livejournal1__rt_2a1",
            "rtbh__author_32768",
        ))
        self.assertEqual(len(statistical_rows()), 8)
        self.assertEqual(len(schedule()), 128)
        self.assertEqual(contract_document()["formal_worker_count"], 128)

    def test_abba_order_is_balanced_per_unit_lifecycle(self) -> None:
        for lifecycle in (
            "installed_cold_compile_prepare_execute", "prepared_first_execute"):
            for unit in TARGET_UNIT_IDS:
                rows = [row for row in schedule()
                        if row["lifecycle"] == lifecycle and row["unit_id"] == unit]
                self.assertEqual(len(rows), 16)
                for pair in range(8):
                    methods = [row["method"] for row in rows
                               if row["pair_index"] == pair]
                    self.assertEqual(methods, (
                        ["v2_direct_true_optix_backport",
                         "v4_restricted_callback_true_optix"] if pair % 2 == 0
                        else ["v4_restricted_callback_true_optix",
                              "v2_direct_true_optix_backport"]))

    def test_scope_excludes_rt1a2_unaffected_apps_v3_and_rtxrmq(self) -> None:
        encoded = json.dumps(contract_document(), sort_keys=True).lower()
        self.assertNotIn("rt_1a2::complete", encoded)
        exclusions = contract_document()["scope_exclusions"]
        self.assertTrue(all(exclusions.values()))

    def test_mechanism_claim_is_preregistered_not_cross_row(self) -> None:
        claim = contract_document()["mechanism_claim_contract"]
        self.assertFalse(claim["rt_barneshut_is_fusion"])
        self.assertFalse(contract_document()["statistics_contract"]
                         ["cross_row_or_lifecycle_compensation_allowed"])
        self.assertIn("ci95_lower_gt_1", claim[
            "triangle_may_become_second_named_fusion_family_only_if"])

    def test_targeted_input_map_has_only_exact_selected_paths(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = (
                root / "common/rt_barneshut/prepared_arrays.json",
                root / "common/rt_barneshut/expected_forces.txt",
                root / "triangle/com-dblp.edge",
                root / "triangle/cit-Patents.edge",
                root / "triangle/soc-LiveJournal1.edge",
            )
            for index, path in enumerate(paths):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(str(index), encoding="utf-8")
            result = build_targeted_inputs(root)
            self.assertEqual(set(result), set(TARGET_UNIT_IDS))

    def test_primary_and_recount_are_separate_implementations(self) -> None:
        primary = Path(evaluator.__file__).read_text(encoding="utf-8")
        independent = Path(recount.__file__).read_text(encoding="utf-8")
        self.assertIn("goal5776_evaluate_real_scale_v2_v4", primary)
        self.assertNotIn("goal5784_targeted_evaluate", independent)
        self.assertNotIn("goal5784_targeted_controller", independent)

    def test_worker_reuses_audited_endpoint_validation_but_targeted_schedule(self) -> None:
        source = _harness_file("goal5784_targeted_worker.py").read_text(
            encoding="utf-8")
        self.assertIn("goal5776_real_scale_formal_worker as base", source)
        self.assertIn("base.schedule = schedule", source)
        self.assertIn("base.contract_sha256 = contract_sha256", source)

    def test_functional_runtime_binds_execution_source_for_rtbh_evidence(self) -> None:
        functional = _harness_file(
            "goal5784_target_functional_prepare.py").read_text(
                encoding="utf-8")
        prepare = _harness_file("goal5784_target_prepare.py").read_text(
            encoding="utf-8")
        self.assertIn('parser.add_argument("--execution-source-sha256", required=True)',
                      functional)
        self.assertIn('"execution_source_sha256": execution_source_sha256',
                      functional)
        self.assertIn('"--execution-source-sha256", _sha(execution_source)',
                      prepare)

    def test_formal_runtime_carries_v4_target_contract_and_controller_gates_it(self) -> None:
        prepare = _harness_file("goal5784_target_prepare.py").read_text(
            encoding="utf-8")
        for required in (
            '"compute_capability": [8, 9]',
            '"optix_sdk_version": "9.0.0"',
            '"optix_include": str(optix / "include")',
            '"cuda_include": str(cuda_include)',
        ):
            self.assertIn(required, prepare)
        with self.assertRaisesRegex(
                PermissionError, "formal target contract is incomplete"):
            controller._validate_prepared({})

    def test_triangle_mechanism_binding_uses_actual_segment_receipts(self) -> None:
        receipt = {
            "schema": "rtdl.v4.checked_u64_weighted_reduction.receipt.v1",
            "maximum_value": 7, "maximum_weight": 3, "weight_sum": 11,
            "value_count": 17, "value_upper_bound": 20,
            "device_kernel_launch_count": 1,
            "host_synchronization_count": 1,
            "provisional_sum_trusted_only_after_bounds": True,
        }
        binding = validate_triangle_reduction_receipts([receipt, receipt])
        self.assertEqual(binding["segment_count"], 2)
        self.assertEqual(binding["evidence_level"],
                         "actual_per_segment_device_reduction_receipts")
        self.assertTrue(binding["observation_outside_registered_endpoint_timer"])

    def test_triangle_mechanism_binding_fails_closed_on_unobserved_kernel(self) -> None:
        receipt = {
            "schema": "rtdl.v4.checked_u64_weighted_reduction.receipt.v1",
            "maximum_value": 7, "maximum_weight": 3, "weight_sum": 11,
            "value_count": 17, "value_upper_bound": 20,
            "device_kernel_launch_count": 0,
            "host_synchronization_count": 1,
            "provisional_sum_trusted_only_after_bounds": True,
        }
        with self.assertRaises(RuntimeError):
            validate_triangle_reduction_receipts([receipt])

    def test_authority_tamper_fails_closed(self) -> None:
        runtime = {key: "a" * 64 for key in (
            "bundle_sha256", "execution_source_sha256", "data_archive_sha256",
            "native_library_sha256", "target_identity_sha256",
            "prepared_identity_sha256", "plan_sha256", "formal_identity_sha256",
            "leaf_cache_manifest_sha256", "expected_value_statement_sha256",
            "runtime_budget_sha256", "preregistration_sha256")}
        runtime["formal_contract_sha256"] = contract_sha256()
        runtime["formal_conservative_budget_seconds"] = 7873.533832750981
        authority = {
            "schema": "rtdl.goal5784.owner_formal_authority.v1",
            **runtime,
            "runtime_sha256": "b" * 64,
            "expected_worker_count": 128,
            "expected_independent_row_count": 8,
            "owner_authorized_exactly_once": True,
            "owner_confirmed_formal_budget_seconds": 7873.533832750981,
            "repair_retry_resume_replacement_row_drop_relabel_allowed": False,
            "authority_sha256": "0" * 64,
        }
        with self.assertRaises(PermissionError):
            controller._validate_authority(authority, runtime, "b" * 64)

    def test_exact_authority_passes_and_bound_fields_cannot_drift(self) -> None:
        bound = {key: chr(97 + index) * 64 for index, key in enumerate((
            "bundle_sha256", "execution_source_sha256", "data_archive_sha256",
            "native_library_sha256", "target_identity_sha256",
            "prepared_identity_sha256", "plan_sha256", "formal_identity_sha256",
            "leaf_cache_manifest_sha256", "expected_value_statement_sha256",
            "runtime_budget_sha256", "preregistration_sha256"))}
        runtime = {
            **bound,
            "formal_contract_sha256": contract_sha256(),
            "formal_conservative_budget_seconds": 7873.533832750981,
        }
        authority = {
            "schema": "rtdl.goal5784.owner_formal_authority.v1",
            **bound,
            "formal_contract_sha256": contract_sha256(),
            "runtime_sha256": "f" * 64,
            "expected_worker_count": 128,
            "expected_independent_row_count": 8,
            "owner_authorized_exactly_once": True,
            "owner_confirmed_formal_budget_seconds": 7873.533832750981,
            "repair_retry_resume_replacement_row_drop_relabel_allowed": False,
        }
        authority["authority_sha256"] = controller._digest(authority)
        controller._validate_authority(authority, runtime, "f" * 64)
        for key in ("preregistration_sha256", "runtime_budget_sha256"):
            tampered = dict(authority)
            tampered[key] = "0" * 64
            body = dict(tampered)
            body.pop("authority_sha256")
            tampered["authority_sha256"] = controller._digest(body)
            with self.assertRaises(PermissionError):
                controller._validate_authority(tampered, runtime, "f" * 64)

    def test_preregistration_matches_contract(self) -> None:
        prereg = json.loads(_artifact(
            "RTDL_GOAL5784_PREREGISTRATION_PATH",
            "history/internal_docs/goal5784_targeted_modern_rtx_preregistration_20260814.json",
        ).read_text(encoding="utf-8"))
        self.assertEqual(prereg["absolute_gates"]["worker_count"], 128)
        self.assertEqual(prereg["lifecycle_rows"]["total_independent_rows"], 8)
        self.assertEqual(prereg["target_units"], list(TARGET_UNIT_IDS))
        self.assertFalse(prereg["pod_authorized"])

    def test_budget_arithmetic_is_exact_and_owner_gated(self) -> None:
        budget = json.loads(_artifact(
            "RTDL_GOAL5784_RUNTIME_BUDGET_PATH",
            "history/internal_docs/goal5784_targeted_formal_runtime_budget_20260814.json",
        ).read_text(encoding="utf-8"))
        formal = (budget["source_registered_endpoint_sum_seconds"]
                  + budget["process_overhead_sum_seconds"]) * budget["safety_factor"]
        self.assertTrue(math.isclose(formal,
                                     budget["formal_conservative_budget_seconds"],
                                     rel_tol=0.0, abs_tol=1e-12))
        self.assertTrue(budget["owner_must_confirm_budget_before_worker_zero"])

    def test_no_result_is_assumed_and_no_retry_is_allowed(self) -> None:
        text = _artifact(
            "RTDL_GOAL5784_EXPECTED_VALUE_STATEMENT_PATH",
            "history/internal_docs/goal5784_pre_registered_expected_value_statement_20260814.md",
        ).read_text(encoding="utf-8")
        self.assertIn("no pass count is assumed", text)
        self.assertIn("No repair", text)
        self.assertIn("retry", text)

    def test_contract_digest_is_stable_hex(self) -> None:
        self.assertEqual(len(contract_sha256()), 64)
        int(contract_sha256(), 16)

    def test_synthetic_primary_and_recount_match_with_mechanism_binding(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._build_synthetic_raw(root)
            primary = json.loads(evaluator.evaluate(
                root, root / "PRIMARY.json").read_text(encoding="utf-8"))
            independent = json.loads(recount.recount(
                root, root / "RECOUNT.json").read_text(encoding="utf-8"))
            self.assertEqual(primary["rows"], independent["rows"])
            self.assertEqual(primary["triangle_v4_mechanism_bound_worker_count"], 48)
            self.assertTrue(primary["triangle_second_named_fusion_family_earned"])
            self.assertEqual(len(primary["triangle_clear_fusion_rows"]), 6)

    def test_missing_mechanism_binding_fails_both_statistics_paths(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._build_synthetic_raw(root)
            path = next(path for path in sorted((root / "workers").glob("*.json"))
                        if json.loads(path.read_text(encoding="utf-8"))[
                            "method"] == V4)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["mechanism_binding"] = {"mode": "missing"}
            path.write_text(json.dumps(payload, sort_keys=True) + "\n",
                            encoding="utf-8")
            with self.assertRaises(RuntimeError):
                evaluator.evaluate(root, root / "PRIMARY.json")
            with self.assertRaises(RuntimeError):
                recount.recount(root, root / "RECOUNT.json")


if __name__ == "__main__":
    unittest.main()

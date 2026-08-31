from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts import goal5791_formal_contract as contract


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "history" / "internal_docs"
SUCCESSOR = DOCS / "goal5791_successor_source_authority_v2_20260817.json"
PREDECESSOR_SUCCESSOR = DOCS / "goal5791_successor_source_authority_20260817.json"
BASE = DOCS / "goal5791_pre_pod_portable_base_and_bundle_audit_20260817.json"
AMENDMENT_A1 = DOCS / "goal5791_amendment_a1_pretimer_fusion_execution_token_result_20260817.json"
AMENDMENT_A2 = DOCS / "goal5791_amendment_a2_segment_plan_input_token_binding_result_20260817.json"
PRETARGET_V1 = DOCS / "goal5791_pretarget_preexecution_authority_20260817.json"
PRETARGET_V2 = DOCS / "goal5791_pretarget_preexecution_authority_v2_20260817.json"
POSTREVIEW_V11 = (
    DOCS / "goal5791_postreview_portable_v11_successor_authority_20260819.json"
)
POSTREVIEW_V11_TERMINAL = (
    DOCS / "goal5791_postreview_portable_v11_identity_error_terminal_20260819.json"
)
POSTREVIEW_V12 = (
    DOCS / "goal5791_postreview_portable_v12_successor_authority_20260819.json"
)
POSTREVIEW_V12_TERMINAL = (
    DOCS / "goal5791_postreview_portable_v12_clean_import_terminal_20260819.json"
)
POSTREVIEW_V13 = (
    DOCS / "goal5791_postreview_portable_v13_successor_authority_20260819.json"
)
POSTREVIEW_V13_TERMINAL = (
    DOCS / "goal5791_postreview_portable_v13_clean_missing_control_terminal_20260819.json"
)
POSTREVIEW_V14 = (
    DOCS / "goal5791_postreview_portable_v14_successor_authority_20260819.json"
)


class Goal5791SuccessorSourceAuthorityTest(unittest.TestCase):
    def test_base_stop_condition_is_replaced_only_by_exact_two_file_delta(self) -> None:
        base = json.loads(BASE.read_text(encoding="utf-8"))
        amendment_a1 = json.loads(AMENDMENT_A1.read_text(encoding="utf-8"))
        amendment_a2 = json.loads(AMENDMENT_A2.read_text(encoding="utf-8"))
        successor = contract.validate_source_authority(SUCCESSOR)

        self.assertEqual(
            base["mandatory_source_construction"][
                "product_source_overlay_allowlist"],
            [],
        )
        self.assertEqual(
            amendment_a1["supersession"]["superseded_gate_id"],
            "G2_ZERO_PRODUCT_DELTA",
        )
        self.assertEqual(
            [row["result_sha256"] for row in successor["append_only_amendments"]],
            [contract.file_sha256(AMENDMENT_A1), contract.file_sha256(AMENDMENT_A2)],
        )
        self.assertEqual(
            amendment_a2["supersession"]["predecessor_source_authority_sha256"],
            contract.file_sha256(PREDECESSOR_SUCCESSOR),
        )
        delta = successor["exact_product_source_delta"]
        self.assertEqual([row["path"] for row in delta], [
            "src/rtdsl/v4_operation_evidence.py",
            "src/rtdsl/v4_triangle_reduction_device_runtime.py",
        ])
        for row in delta:
            product = ROOT / Path(*row["path"].split("/"))
            self.assertEqual(contract.file_sha256(product), row["successor_sha256"])
            self.assertEqual(product.stat().st_size, row["successor_bytes"])

        postreview = json.loads(POSTREVIEW_V11.read_text(encoding="utf-8"))
        unsigned = dict(postreview)
        claimed = unsigned.pop("authority_sha256")
        self.assertEqual(contract.digest(unsigned), claimed)
        self.assertEqual(postreview["status"],
                         "FROZEN_LOCAL_SOURCE_HOME_BUNDLE_CONSTRUCTION_POLICY__NOT_STAGE_A_OR_STAGE_B_AUTHORITY")
        historical_v7_contract_sha256 = (
            "308f39366e0e32172d10bd99cc1b99c531e41f630713f6ed20de546c170caae5"
        )
        self.assertEqual(
            postreview["current_v7_freeze"]["formal_contract_file_sha256"],
            historical_v7_contract_sha256,
        )
        self.assertNotEqual(
            historical_v7_contract_sha256,
            contract.file_sha256(ROOT / "scripts" / "goal5791_formal_contract.py"),
        )
        self.assertEqual(
            postreview["current_v7_freeze"]["preregistration_file_sha256"],
            contract.file_sha256(
                DOCS / "goal5791_preregistration_v7_20260819.json"),
        )
        self.assertEqual(
            postreview["current_v7_freeze"]["pretarget_file_sha256"],
            contract.file_sha256(
                DOCS / "goal5791_pretarget_preexecution_authority_v7_20260819.json"),
        )
        self.assertEqual(
            postreview["portable_cpu_gate"]["workspace_concrete_test_id_count"],
            76,
        )
        self.assertEqual(
            postreview["portable_cpu_gate"]["clean_concrete_test_id_count"],
            70,
        )
        self.assertFalse(postreview["authorization"]["authorizes_stage_a"])
        self.assertFalse(postreview["authorization"]["authorizes_ssh_or_pod_connection"])

        terminal = json.loads(
            POSTREVIEW_V11_TERMINAL.read_text(encoding="utf-8"))
        terminal_unsigned = dict(terminal)
        terminal_claimed = terminal_unsigned.pop("terminal_authority_sha256")
        self.assertEqual(contract.digest(terminal_unsigned), terminal_claimed)
        self.assertEqual(
            terminal["superseded_authority"]["file_sha256"],
            contract.file_sha256(POSTREVIEW_V11),
        )
        self.assertFalse(terminal["failure_facts"]["builder_main_invoked"])
        self.assertTrue(all(
            item["exists"] is False
            for item in terminal["output_facts"].values()))
        self.assertTrue(all(
            value is False for value in terminal["authorization"].values()))

        current = json.loads(POSTREVIEW_V12.read_text(encoding="utf-8"))
        current_unsigned = dict(current)
        current_claimed = current_unsigned.pop("authority_sha256")
        self.assertEqual(contract.digest(current_unsigned), current_claimed)
        self.assertEqual(
            current["superseded_v11"]["terminal_file_sha256"],
            contract.file_sha256(POSTREVIEW_V11_TERMINAL),
        )
        self.assertEqual(
            current["portable_cpu_gate"]["workspace_concrete_test_id_count"],
            112,
        )
        self.assertEqual(
            current["portable_cpu_gate"]["clean_concrete_test_id_count"],
            106,
        )
        self.assertTrue(
            current["authorization"][
                "authorizes_one_local_portable_source_v12_build"])
        self.assertFalse(current["authorization"]["authorizes_stage_a"])
        self.assertFalse(
            current["authorization"]["authorizes_ssh_or_pod_connection"])

        v12_terminal = json.loads(
            POSTREVIEW_V12_TERMINAL.read_text(encoding="utf-8"))
        v12_terminal_unsigned = dict(v12_terminal)
        v12_terminal_claimed = v12_terminal_unsigned.pop(
            "terminal_authority_sha256")
        self.assertEqual(
            contract.digest(v12_terminal_unsigned), v12_terminal_claimed)
        self.assertEqual(
            v12_terminal["v12_authority"]["file_sha256"],
            contract.file_sha256(POSTREVIEW_V12),
        )
        self.assertEqual(
            v12_terminal["attempt_facts"]["clean_test_cases_executed"], 0)
        self.assertEqual(
            v12_terminal["attempt_facts"]["missing_clean_member"],
            "scripts/goal5791_trace_record_cost_diagnostic.py",
        )
        self.assertTrue(all(
            item["exists"] is False
            for item in v12_terminal["output_facts"].values()))

        v13 = json.loads(POSTREVIEW_V13.read_text(encoding="utf-8"))
        v13_unsigned = dict(v13)
        v13_claimed = v13_unsigned.pop("authority_sha256")
        self.assertEqual(contract.digest(v13_unsigned), v13_claimed)
        self.assertEqual(
            v13["predecessor"]["v12_terminal_file_sha256"],
            contract.file_sha256(POSTREVIEW_V12_TERMINAL),
        )
        self.assertEqual(
            v13["exact_successor_delta"]["added_overlay_sha256"],
            contract.file_sha256(
                ROOT / "scripts" / "goal5791_trace_record_cost_diagnostic.py"),
        )
        self.assertTrue(
            v13["authorization"][
                "authorizes_one_local_portable_source_v13_build"])
        self.assertFalse(v13["authorization"]["authorizes_stage_a"])

        v13_terminal = json.loads(
            POSTREVIEW_V13_TERMINAL.read_text(encoding="utf-8"))
        v13_terminal_unsigned = dict(v13_terminal)
        v13_terminal_claimed = v13_terminal_unsigned.pop(
            "terminal_authority_sha256")
        self.assertEqual(
            contract.digest(v13_terminal_unsigned), v13_terminal_claimed)
        self.assertEqual(
            v13_terminal["v13_authority"]["file_sha256"],
            contract.file_sha256(POSTREVIEW_V13),
        )
        self.assertTrue(
            v13_terminal["attempt_facts"]["clean_test_execution_started"])
        self.assertTrue(
            v13_terminal["attempt_facts"][
                "clean_completed_test_count_not_recorded_and_not_inferred"])

        v14 = json.loads(POSTREVIEW_V14.read_text(encoding="utf-8"))
        v14_unsigned = dict(v14)
        v14_claimed = v14_unsigned.pop("authority_sha256")
        self.assertEqual(contract.digest(v14_unsigned), v14_claimed)
        self.assertEqual(
            v14["predecessor"]["v13_terminal_file_sha256"],
            contract.file_sha256(POSTREVIEW_V13_TERMINAL),
        )
        self.assertEqual(
            [row["path"] for row in v14["exact_successor_delta"]],
            [
                "history/internal_docs/reviewer_project_state_and_remaining_work_to_cgo_20260817.md",
                "history/internal_docs/goal5792_unknown_lane_classification_work_authority_20260819.json",
            ],
        )
        for row in v14["exact_successor_delta"]:
            self.assertEqual(
                contract.file_sha256(ROOT / Path(*row["path"].split("/"))),
                row["sha256"],
            )
        self.assertTrue(
            v14["authorization"][
                "authorizes_one_local_portable_source_v14_build"])
        self.assertFalse(v14["authorization"]["authorizes_stage_a"])

    def test_v1_and_v2_are_zero_worker_pretarget_lineages(self) -> None:
        v1 = json.loads(PRETARGET_V1.read_text(encoding="utf-8"))
        v2 = json.loads(PRETARGET_V2.read_text(encoding="utf-8"))
        for value in (v1, v2):
            self.assertEqual(value["formal_worker_count"], 0)
            self.assertEqual(value["registered_performance_timing_count"], 0)
            self.assertFalse(value["authorization"]["authorizes_pod"])
            self.assertIsNone(value["target_materialization_binding"])
        self.assertEqual(v2["authority_records"]["source_authority"]["sha256"],
                         contract.file_sha256(PREDECESSOR_SUCCESSOR))
        self.assertNotEqual(v2["authority_records"]["source_authority"]["sha256"],
                            contract.SOURCE_AUTHORITY_FILE_SHA256)
        self.assertNotEqual(
            v1["authority_records"]["source_authority"]["sha256"],
            v2["authority_records"]["source_authority"]["sha256"],
        )

    def test_resigned_or_reauthored_successor_is_not_a_frozen_authority(self) -> None:
        value = json.loads(SUCCESSOR.read_text(encoding="utf-8"))
        value["exact_product_source_delta"][0]["successor_sha256"] = (
            contract.digest({"counterfeit": "product"})
        )
        unsigned = dict(value)
        unsigned.pop("authority_sha256")
        value["authority_sha256"] = contract.digest(unsigned)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "counterfeit.json"
            path.write_text(
                json.dumps(value, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(contract.Goal5791ContractError):
                contract.validate_source_authority(path)


if __name__ == "__main__":
    unittest.main()

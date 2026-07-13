from __future__ import annotations

import inspect
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5395_native_status_stream_abi_gate.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5395_native_status_stream_abi_gate.json"
)


class Goal5395NativeStatusStreamAbiGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_public_abi_contract_is_exported_and_valid(self) -> None:
        import rtdsl as rt

        self.assertIn("ACTIVE_QUERY_STATUS_STREAM_NATIVE_ABI_CONTRACT", rt.__all__)
        self.assertIn("ACTIVE_QUERY_STATUS_STREAM_NATIVE_ROW_SCHEMA", rt.__all__)
        self.assertIn("ACTIVE_QUERY_STATUS_STREAM_NATIVE_TELEMETRY_SCHEMA", rt.__all__)
        self.assertIn("active_query_status_stream_native_abi_contract", rt.__all__)
        self.assertIn("validate_active_query_status_stream_native_abi_contract", rt.__all__)

        validation = rt.validate_active_query_status_stream_native_abi_contract()
        self.assertEqual(validation["status"], "accept")
        contract = validation["contract"]
        self.assertEqual(contract["contract"], rt.ACTIVE_QUERY_STATUS_STREAM_NATIVE_ABI_CONTRACT)
        self.assertEqual(tuple(contract["output_row_schema"]), rt.ACTIVE_QUERY_STATUS_STREAM_NATIVE_ROW_SCHEMA)
        self.assertEqual(
            tuple(contract["telemetry_schema"]),
            rt.ACTIVE_QUERY_STATUS_STREAM_NATIVE_TELEMETRY_SCHEMA,
        )
        self.assertFalse(contract["executable"])
        self.assertTrue(contract["app_generic"])
        self.assertFalse(contract["explicit_app_option_support_claimed"])

    def test_core_contract_source_and_payload_are_app_neutral(self) -> None:
        import rtdsl as rt

        source = inspect.getsource(rt.active_query_status_stream_native_abi_contract).lower()
        contract_text = str(rt.active_query_status_stream_native_abi_contract()).lower()
        for forbidden in ("xhd", "x-hd", "hausdorff", "paper", "hd_exec", "figure"):
            self.assertNotIn(forbidden, source)
            self.assertNotIn(forbidden, contract_text)

    def test_goal5395_artifact_pins_target_and_v6_gap(self) -> None:
        payload = self.payload
        self.assertEqual(payload["goal"], "Goal5395")
        self.assertEqual(
            payload["exit_label"],
            "native_status_stream_abi_gate_ready__implement_v7_or_fail_closed_next",
        )

        target = payload["goal5394_target"]
        self.assertEqual(target["author_rows"], 27133990)
        self.assertEqual(target["author_rows_per_active"], 62)
        self.assertEqual(target["full_cover_rows"], 24508120)
        self.assertEqual(target["full_cover_rows_per_active"], 56)
        self.assertEqual(target["missing_rows"], 2625870)
        self.assertEqual(target["missing_rows_per_active"], 6)
        self.assertFalse(target["full_cover_is_correctness_claim"])

        audit = payload["current_native_surface_audit"]
        self.assertTrue(audit["latest_symbol_present_in_python_and_native_sources"])
        # This historical Goal5395 gate was written before Goal5397 began.
        # If later source work has already added the v7 symbol, Goal5395 still
        # remains only an ABI/gap gate; do not force the old "future symbol is
        # absent" snapshot to block the newer implementation goal.
        self.assertIsInstance(audit["future_symbol_already_present"], bool)
        self.assertTrue(audit["current_surface_is_single_launch_frontier_probe"])
        self.assertFalse(audit["current_surface_satisfies_goal5394_native_probe"])
        self.assertIn("transition_phase_code", audit["missing_required_output_columns"])
        self.assertIn("current_best_before_sq", audit["missing_required_output_columns"])
        self.assertIn("current_best_after_sq", audit["missing_required_output_columns"])
        self.assertIn("multi-round feedback state", audit["missing_required_semantics"])

    def test_claim_boundary_keeps_lb_unsupported(self) -> None:
        decision = self.payload["decision"]
        self.assertFalse(decision["native_code_implemented_by_goal5395"])
        self.assertTrue(decision["generic_native_abi_contract_added"])
        self.assertFalse(decision["existing_native_v6_is_sufficient"])
        self.assertTrue(decision["explicit_lb_support_remains_unsupported"])
        self.assertTrue(decision["next_gate_requires_pod"])

        forbidden_true = [
            "native_backend_completion_claimed",
            "existing_native_v6_parity_claimed",
            "explicit_lb_support_claimed",
            "row_count_parity_claimed",
            "hash_sample_parity_claimed",
            "figure7_reproduction_claimed",
            "figure11_reproduction_claimed",
            "same_denominator_memory_claimed",
            "author_rt_core_algorithm_parity_claimed",
            "performance_ratio_claimed",
            "exact_paper_dataset_reproduction_claimed",
            "full_xhd_paper_reproduction_claimed",
        ]
        boundary = self.payload["claim_boundary"]
        for key in forbidden_true:
            self.assertIs(boundary[key], False, key)


if __name__ == "__main__":
    unittest.main()

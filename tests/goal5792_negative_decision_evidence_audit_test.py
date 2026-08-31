from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5792_negative_decision_evidence_audit.py"


def _module():
    spec = importlib.util.spec_from_file_location("goal5792_negative_decision", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Goal5792NegativeDecisionEvidenceAuditTest(unittest.TestCase):
    def test_exact_frozen_chain_rebuilds_six_negative_decisions(self) -> None:
        result = _module().build_result(ROOT)
        self.assertEqual(6, result["summary"]["case_count"])
        self.assertEqual(6, result["summary"][
            "diagnostic_legally_executes_and_matches_own_oracle_count"])
        self.assertEqual(0, result["summary"]["diagnostic_matches_requested_semantics_count"])
        self.assertEqual(5, result["summary"]["public_facade_reject_count"])
        self.assertEqual(1, result["summary"]["typed_physical_schema_reject_count"])
        self.assertEqual(6, result["summary"]["diagnostic_traversal_receipt_count"])
        self.assertEqual(7, result["summary"]["diagnostic_successful_complete_launch_count"])
        self.assertEqual(9, result["summary"]["diagnostic_raygen_invocation_count"])

    def test_resigned_silent_wrong_or_reject_gate_claim_is_rejected(self) -> None:
        module = _module()
        _, blobs = module._read_pins(ROOT)
        result = module._strict_json(blobs["a1_result"], "a1_result")
        controller = module._strict_json(blobs["controller_result"], "controller_result")
        recount = module._strict_json(blobs["independent_recount"], "independent_recount")

        bad = copy.deepcopy(controller)
        bad["cases"][0]["arms"]["diagnostic_counterfactual"]["arm_result"][
            "matches_requested_semantics"] = True
        with self.assertRaisesRegex(RuntimeError, "legal silent-wrong"):
            module._validate_cases(result, bad, recount)

        bad = copy.deepcopy(controller)
        bad["cases"][4]["arms"]["product_admission_reject"]["arm_result"][
            "production_facade_called"] = True
        with self.assertRaisesRegex(RuntimeError, "five-plus-one"):
            module._validate_cases(result, bad, recount)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "Paper-reproduction-apps" / "librts-paper" / "results" / "goal5505_runtime_semantics_gate.json"


class Goal5505RuntimeSemanticsGateTest(unittest.TestCase):
    def test_runtime_localizes_the_disagreement_to_one_ulp_gap(self) -> None:
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "runtime_semantics_gate_completed")
        self.assertTrue(payload["input_identity"]["same_input_per_case"])
        self.assertEqual(payload["summary"]["case_count"], 5)
        self.assertEqual(payload["summary"]["author_runtime_total"], 5)
        self.assertEqual(payload["summary"]["rtdl_runtime_total"], 4)
        self.assertEqual(payload["summary"]["author_matches_source_emulation_count"], 5)
        self.assertEqual(payload["summary"]["author_matches_cpu_inclusive_count"], 4)
        self.assertEqual(payload["summary"]["rtdl_matches_cpu_inclusive_count"], 5)
        self.assertEqual(payload["summary"]["author_rtdl_mismatch_case_count"], 1)
        self.assertTrue(payload["interpretation"]["source_emulation_matches_author_runtime"])
        self.assertTrue(payload["interpretation"]["rtdl_matches_independent_cpu_contract"])
        self.assertEqual(payload["interpretation"]["localized_difference"], "one_ulp_gap_after_box_max")
        self.assertFalse(payload["interpretation"]["full_input_root_cause_resolved"])
        self.assertFalse(payload["claim_boundary"]["rtdl_core_change_authorized"])
        self.assertFalse(payload["claim_boundary"]["performance_ratio_authorized"])


if __name__ == "__main__":
    unittest.main()

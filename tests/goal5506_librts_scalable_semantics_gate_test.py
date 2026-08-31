from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "Paper-reproduction-apps" / "librts-paper" / "results" / "goal5506_scalable_semantics_gate.json"


class Goal5506ScalableSemanticsGateTest(unittest.TestCase):
    def test_scalable_probe_keeps_author_and_generic_contracts_distinct(self) -> None:
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "scalable_runtime_semantics_gate_completed")
        self.assertEqual(payload["input_identity"]["pair_count"], 8192)
        self.assertTrue(payload["input_identity"]["same_input_author_and_rtdl"])
        self.assertEqual(payload["counts"]["cpu_inclusive_oracle"], 20)
        self.assertEqual(payload["counts"]["source_rayparams_model"], 21)
        self.assertEqual(payload["counts"]["author_gpu_runtime"], 21)
        self.assertEqual(payload["counts"]["rtdl_optix_runtime"], 20)
        self.assertTrue(payload["classification"]["author_matches_source_model"])
        self.assertTrue(payload["classification"]["rtdl_matches_cpu_inclusive_oracle"])
        self.assertFalse(payload["classification"]["author_rtdl_counts_match"])
        self.assertFalse(payload["claim_boundary"]["full_input_root_cause_resolved"])
        self.assertFalse(payload["claim_boundary"]["rtdl_core_change_authorized"])
        self.assertFalse(payload["phase_observations"]["performance_ratio_authorized"])


if __name__ == "__main__":
    unittest.main()

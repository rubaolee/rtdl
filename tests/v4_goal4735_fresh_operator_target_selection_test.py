from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "future" / "v4" / "v4_goal4735_fresh_generic_operator_target_selection_2026-06-26.md"
EVIDENCE = ROOT / "future" / "v4" / "evidence" / "v4_goal4735_fresh_generic_operator_target_selection_2026-06-26.json"


class V4Goal4735FreshOperatorTargetSelectionTest(unittest.TestCase):
    def test_selects_barnes_hut_and_rejects_spatial_rayjoin_for_now(self) -> None:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        decision = payload["candidate_decision"]
        self.assertEqual(decision["selected"], "barnes_hut")
        self.assertEqual(decision["rejected_for_now"], "spatial_rayjoin")
        self.assertIn("complete current V4 app route", "\n".join(decision["spatial_rayjoin_rejected_reason"]))

    def test_goal4736_gates_are_frozen_before_measurement(self) -> None:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        thresholds = payload["goal4736_protocol"]["thresholds"]
        self.assertEqual(thresholds["v4_vs_v2_14_full_hot_min"], 1.20)
        self.assertEqual(thresholds["v4_vs_v2_14_full_wall_min"], 1.10)
        self.assertEqual(thresholds["v4_vs_v3_0_2_full_hot_min"], 0.98)
        self.assertTrue(thresholds["correctness_companion_required"])

    def test_non_authorization_and_no_app_identity_kernel(self) -> None:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        boundary = payload["claim_boundary"]
        self.assertFalse(boundary["release_authorized"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["barnes_hut_speedup_claim_authorized"])
        self.assertFalse(boundary["app_specific_native_kernel_authorized"])
        forbidden = "\n".join(payload["goal4736_protocol"]["forbidden"])
        self.assertIn("app-specific Barnes-Hut native kernel", forbidden)

    def test_doc_points_to_goal4736(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("Select Barnes-Hut for Goal4736", text)
        self.assertIn("prepared_aggregate_frontier_weighted_vector_optix", text)
        self.assertIn("V4/V3.0.2 full hot", text)


if __name__ == "__main__":
    unittest.main()

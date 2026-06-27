from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "future" / "v4" / "evidence" / "v4_goal4741_spatial_rayjoin_route_reopen_decision_2026-06-26.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4741_spatial_rayjoin_route_reopen_decision_2026-06-26.md"


class V4Goal4741SpatialRayjoinReopenDecisionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_route_inventory_blocks_reopen(self) -> None:
        inventory = self.payload["route_inventory"]
        self.assertEqual("no_v4_app_route_blocker", inventory["current_route_class"])
        self.assertFalse(inventory["full_current_v4_app_route_bound"])
        self.assertFalse(inventory["route_actually_uses_v4_code"])
        self.assertFalse(inventory["dry_run_possible"])
        self.assertTrue(inventory["old_symbols_present"])
        self.assertTrue(inventory["old_symbols_are_not_complete_v4_app_route"])

    def test_shape_pair_subprobe_failed_speed_credit(self) -> None:
        subprobe = self.payload["shape_pair_subprobe"]
        self.assertTrue(subprobe["correctness_companion_ok"])
        self.assertTrue(subprobe["serious_active_count_parity"])
        self.assertLess(subprobe["v4_hot_over_v2_14_same_primitive"], 1.0)
        self.assertLess(subprobe["v4_wall_over_v2_14_same_primitive"], 1.0)
        self.assertLess(subprobe["v4_hot_over_v3_0_2_control"], 0.98)
        self.assertFalse(subprobe["speed_credit_pass"])
        self.assertFalse(subprobe["subprobe_is_complete_spatial_rayjoin_app_route"])

    def test_classification_forbids_pod_rerun_without_new_route(self) -> None:
        classification = self.payload["classification"]
        self.assertEqual("closed_no_current_v4_app_route_blocker", classification["matrix_row"])
        self.assertFalse(classification["reopen_now"])
        self.assertFalse(classification["pod_rerun_authorized"])
        self.assertIn("Running it again without a new route would be process churn", REPORT.read_text(encoding="utf-8"))

    def test_reopen_condition_is_concrete(self) -> None:
        condition = set(self.payload["reopen_condition"])
        self.assertIn("complete_v4_app_route_not_only_subprobe", condition)
        self.assertIn("frozen_v2_14_denominator", condition)
        self.assertIn("correctness_parity_requirements", condition)
        self.assertIn("material_speed_bars", condition)
        self.assertIn("generic_relation_topology_no_app_identity_kernel", condition)

    def test_claim_boundary_blocks_spatial_overclaiming(self) -> None:
        boundary = self.payload["claim_boundary"]
        for key in (
            "release_authorized",
            "final_v4_tag_authorized",
            "spatial_rayjoin_speedup_claim_authorized",
            "rayjoin_paper_reproduction_claim_authorized",
            "all_benchmark_speedup_claim_authorized",
            "app_specific_native_kernel_authorized",
            "hidden_v2_v3_fallback_authorized",
            "true_zero_copy_wording_authorized",
        ):
            self.assertFalse(boundary[key], key)


if __name__ == "__main__":
    unittest.main()

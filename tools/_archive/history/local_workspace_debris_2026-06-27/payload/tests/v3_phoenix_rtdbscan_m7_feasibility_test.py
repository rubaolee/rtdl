import json
import unittest
from pathlib import Path

from scripts import v3_phoenix_rtdbscan_m7_feasibility as feasibility


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_rtdbscan_component_union_m7_feasibility_2026-06-20.json"
PACKET_MD = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_rtdbscan_component_union_m7_feasibility_2026-06-20.md"


class V3PhoenixRTDBSCANM7FeasibilityTest(unittest.TestCase):
    def payload(self):
        return json.loads(PACKET_JSON.read_text(encoding="utf-8"))

    def test_packet_is_not_promoted(self):
        payload = self.payload()
        self.assertEqual(payload["status"], "rtdbscan_component_union_m7_feasibility_not_promoted")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])
        self.assertFalse(payload["m7_promoted"])
        self.assertEqual(payload["m7_qualified_release_rows"], 0)

    def test_all_app_ratio_is_strong_but_validation_missing(self):
        row = self.payload()["all_app_ratio_row"]
        self.assertEqual(row["comparison_group"], "dbscan_cluster_signature")
        self.assertEqual(row["point_count"], 8192)
        self.assertGreater(row["optix_over_embree_speedup"], 1000.0)
        self.assertIsNone(row["matches_reference"])
        self.assertIsNone(row["reference_signature"])
        self.assertEqual(row["claim_status"], "internal_ratio_not_m7_validation_missing")
        self.assertEqual(row["main_blocker"], "all_app_ratio_row_has_matches_reference_null")

    def test_m23_scale_evidence_is_validated_but_no_baseline(self):
        m23 = self.payload()["m23_scale_evidence"]
        self.assertEqual(m23["point_count"], 524288)
        self.assertEqual(m23["copies"], 65536)
        self.assertEqual(m23["output_mode"], "component_signature")
        self.assertTrue(m23["all_match_oracle"])
        self.assertTrue(m23["cluster_size_signatures_match"])
        self.assertTrue(m23["core_counts_match"])
        self.assertTrue(m23["noise_counts_match"])
        self.assertTrue(m23["rt_core_accelerated"])
        self.assertFalse(m23["materializes_python_rows"])
        self.assertEqual(m23["partners_present"], ["cupy", "numba"])
        self.assertEqual(m23["main_blocker"], "no_same_scale_embree_baseline_for_m23_component_signature")

    def test_m7_blockers_force_fresh_rerun_packet(self):
        blockers = set(self.payload()["m7_blockers"])
        for blocker in [
            "all_app_ratio_row_has_matches_reference_null",
            "m23_scale_evidence_has_no_same_scale_embree_baseline",
            "component_signature_not_full_dbscan_labels",
            "no_public_component_union_contract",
            "no_final_external_public_row_review",
        ]:
            self.assertIn(blocker, blockers)
        requirements = "\n".join(self.payload()["next_rerun_requirements"])
        self.assertIn("same component-size signature contract for Embree and OptiX", requirements)
        self.assertIn("not matches_reference: null", requirements)

    def test_markdown_blocks_public_overread(self):
        text = PACKET_MD.read_text(encoding="utf-8")
        for phrase in [
            "not M7 promotion",
            "matches_reference",
            "no same-scale Embree baseline",
            "component_signature_not_full_dbscan_labels",
            "Do not claim RTDBSCAN V3 is 1483x faster end to end",
            "Phoenix M7-qualified release rows: 0",
        ]:
            self.assertIn(phrase, text)

    def test_generator_reproduces_saved_packet_shape(self):
        generated = feasibility.build_payload()
        current = self.payload()
        self.assertEqual(generated["status"], current["status"])
        self.assertEqual(generated["all_app_ratio_row"], current["all_app_ratio_row"])
        self.assertEqual(generated["m23_scale_evidence"], current["m23_scale_evidence"])


if __name__ == "__main__":
    unittest.main()

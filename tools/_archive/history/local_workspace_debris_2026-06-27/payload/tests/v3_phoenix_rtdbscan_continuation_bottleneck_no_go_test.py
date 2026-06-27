import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    REPO_ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtdbscan_continuation_bottleneck_no_go_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")


class V3PhoenixRTDBSCANContinuationBottleneckNoGoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")

    def test_packet_keeps_rtdbscan_out_of_m7(self):
        self.assertEqual(
            self.payload["status"],
            "rtdbscan_continuation_bottleneck_no_go_not_promoted",
        )
        self.assertFalse(self.payload["release_authorized"])
        self.assertFalse(self.payload["public_speedup_claim_authorized"])
        self.assertFalse(self.payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(self.payload["m7_promotion_authorized"])
        self.assertEqual(self.payload["m7_qualified_release_rows"], 0)
        self.assertEqual(
            self.payload["verdict"],
            "do_not_promote_rtdbscan_to_m7_from_current_evidence",
        )

    def test_same_contract_large_row_exposes_continuation_bottleneck(self):
        rows = {
            row["point_count"]: row for row in self.payload["same_contract_rows"]
        }
        large = rows[524288]
        self.assertAlmostEqual(large["optix_speedup_vs_embree"], 1.071038907298004)
        self.assertAlmostEqual(
            large["rt_threshold_speedup_vs_embree_compact_rows"],
            1.4703640801800524,
        )
        self.assertAlmostEqual(large["continuation_to_rt_threshold_ratio"], 5.27045490328335)
        self.assertGreater(large["optix_continuation_wall_share"], 0.8)
        self.assertTrue(large["continuation_dominates_optix"])
        self.assertTrue(large["same_canonical_component_signature"])

    def test_m23_internal_row_is_not_same_contract_public_evidence(self):
        row = self.payload["m23_grouped_stream_internal_row"]
        self.assertEqual(row["point_count"], 524288)
        self.assertEqual(row["output_mode"], "component_signature")
        self.assertEqual(row["partners"], ["cupy", "numba"])
        self.assertTrue(row["oracle_match"])
        self.assertTrue(row["cluster_size_signatures_match"])
        self.assertFalse(row["materializes_python_rows"])
        self.assertTrue(row["native_continuation_active"])
        self.assertTrue(row["rt_core_accelerated"])
        self.assertAlmostEqual(
            row["cupy_hot_component_label_elapsed_sec_median"],
            0.0005934387445449829,
        )
        self.assertAlmostEqual(
            row["numba_hot_component_label_elapsed_sec_median"],
            0.0006683692336082458,
        )
        self.assertEqual(
            row["promotion_blocker"],
            "different_contract_no_same_scale_embree_baseline",
        )

    def test_forbidden_wording_and_reopen_requirements_are_explicit(self):
        forbidden = "\n".join(self.payload["forbidden_public_wording"])
        self.assertIn("RTDBSCAN V3 is 1483x faster", forbidden)
        self.assertIn("RTDBSCAN is M7-qualified", forbidden)
        self.assertIn(
            "M23 grouped-stream component signature proves same-contract DBSCAN speedup",
            forbidden,
        )
        self.assertIn("component_signature is full DBSCAN labels", forbidden)
        reopen = "\n".join(self.payload["reopen_requirements"])
        self.assertIn("Optimize the shared component-signature continuation", reopen)
        self.assertIn("same-scale Embree baseline", reopen)

    def test_markdown_records_decision_audit_and_external_blockage(self):
        self.assertIn("Continuation-Bottleneck No-Go", self.text)
        self.assertIn("Phoenix M7-qualified release rows: 0", self.text)
        self.assertIn("Do not use the old `1483.603x` all-app row", self.text)
        self.assertIn("But M23 is not an M7 public row", self.text)
        self.assertIn(
            "external_review_blocked_phoenix_v3_rtdbscan_continuation_bottleneck_no_go_2026-06-21.md",
            self.text,
        )
        self.assertIn("Was I foolish?", self.text)
        self.assertIn("No. The current evidence already identifies the bottleneck", self.text)


if __name__ == "__main__":
    unittest.main()

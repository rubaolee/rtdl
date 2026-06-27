import json
import unittest
from pathlib import Path

from scripts import v3_phoenix_rtnn_self_query_graph_evidence as evidence


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_rtnn_self_query_graph_evidence_2026-06-21.json"
REPORT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_rtnn_self_query_graph_evidence_2026-06-21.md"


class V3PhoenixRtnnSelfQueryGraphEvidenceTest(unittest.TestCase):
    def test_build_payload_blocks_m7_because_material_floor_is_not_met(self) -> None:
        payload = evidence.build_payload()

        self.assertEqual(
            payload["status"],
            "rtnn_self_query_graph_large_scale_functional_not_m7_material_floor_not_met",
        )
        self.assertEqual(payload["failed_checks"], [])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertTrue(payload["checks"]["point_count_is_serious_1m"])
        self.assertTrue(payload["checks"]["same_contract_summary_parity"])
        self.assertTrue(payload["checks"]["graph_uses_prepared_search_as_query_points"])
        self.assertTrue(payload["checks"]["native_65536_graph_cap_removed"])
        self.assertTrue(payload["checks"]["policy_no_fixed_65536_cap"])
        self.assertTrue(payload["checks"]["material_speedup_floor_not_met"])
        self.assertLess(payload["comparisons"]["graph_over_direct_cold_plus_query_speedup"], 2.0)

    def test_checked_in_packet_and_report_record_boundary(self) -> None:
        payload = json.loads(PACKET.read_text(encoding="utf-8"))
        report = REPORT.read_text(encoding="utf-8")

        self.assertEqual(payload["failed_checks"], [])
        self.assertIn("not_m7", payload["status"])
        self.assertIn("1,048,576", payload["conclusion"])
        self.assertIn("M7 promotion: no", report)
        self.assertIn("Public speedup wording: no", report)
        self.assertIn("Graph over direct cold+query speedup", report)


if __name__ == "__main__":
    unittest.main()

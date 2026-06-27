import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtdbscan_component_signature_optimization_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")


class V3PhoenixRTDBSCANComponentSignatureOptimizationPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")

    def test_packet_records_code_optimization_not_release(self):
        self.assertEqual(
            self.payload["status"],
            "rtdbscan_component_signature_optimization_pending_rtx_evidence",
        )
        self.assertEqual(self.payload["generic_capability"], "component_union")
        self.assertFalse(self.payload["release_authorized"])
        self.assertFalse(self.payload["public_speedup_claim_authorized"])
        self.assertFalse(self.payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(self.payload["m7_promotion_authorized"])
        self.assertEqual(self.payload["m7_qualified_release_rows"], 0)

    def test_packet_preserves_generic_engine_boundary(self):
        self.assertIn("run_numba_label_count_and_flag_count_i64", self.payload["new_signature_strategy"])
        self.assertIn("does not add a DBSCAN-native ABI", self.payload["generic_engine_reason"])
        boundary = self.payload["evidence_boundary"]
        self.assertFalse(boundary["rtx_performance_rerun_completed"])
        self.assertFalse(boundary["same_contract_rtdbscan_no_go_superseded"])
        self.assertIn("RTX hardware", " ".join(boundary["required_before_reopen"]))

    def test_markdown_keeps_m7_blocked_until_rtx_rerun(self):
        self.assertIn("RTX evidence pending", self.text)
        self.assertIn("column_signature_materializes_point_ids: false", self.text)
        self.assertIn("does not add a DBSCAN-native ABI", self.text)
        self.assertIn("The previous RTDBSCAN no-go packet remains current", self.text)
        self.assertIn("Was I foolish?", self.text)


if __name__ == "__main__":
    unittest.main()

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_rtnn_m112_reconciliation_packet.py"
PACKET_JSON = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_rtnn_m112_reconciliation_packet_2026-06-21.json"
PACKET_MD = PACKET_JSON.with_suffix(".md")


class V3PhoenixRtnnM112ReconciliationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")

    def test_packet_reconciles_without_m7_promotion(self):
        payload = self.payload
        self.assertEqual(payload["status"], "rtnn_m112_reconciled_no_m7_promotion")
        self.assertEqual(payload["generic_capability"], "ranked_summary")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows"], 0)
        self.assertFalse(payload["existing_evidence_promotable_now"])
        self.assertEqual(payload["failed_checks"], [])

    def test_current_boundary_and_m112_strength_are_both_visible(self):
        current = self.payload["current_65k_raw_summary_boundary"]
        self.assertTrue(current["all_hot_optix_faster"])
        self.assertTrue(current["all_wall_optix_slower"])
        for ratio in current["wall_optix_over_embree"].values():
            self.assertLess(ratio, 1.0)

        m104 = self.payload["m104_exact_float64_same_input_gate"]
        self.assertGreater(m104["optix_over_embree_speedup"], 15.0)
        self.assertFalse(m104["strict_signature_match"])
        self.assertTrue(m104["tie_stable_signature_match"])

        m106 = self.payload["m106_full_batch_aggregate_route"]
        self.assertLess(m106["median_query_sec"], 0.2)
        self.assertGreater(m106["vs_m104_embree_speedup"], 700.0)
        self.assertFalse(m106["exact"])
        self.assertEqual(m106["precision"], "float32")
        self.assertFalse(m106["same_output_contract_author_vs_rtdl"])

    def test_partner_continuation_and_blockers_are_not_public_claims(self):
        partner = self.payload["m111_partner_continuation"]
        self.assertTrue(partner["all_signature_match"])
        self.assertTrue(partner["all_hot_no_hidden_column_copy_ready"])
        self.assertIn("uniform", partner["rows"])
        self.assertIn("clustered", partner["rows"])
        self.assertGreater(
            partner["rows"]["clustered"]["cupy_hot_device_run_seconds_median_sum"],
            partner["rows"]["uniform"]["cupy_hot_device_run_seconds_median_sum"],
        )
        blockers = set(self.payload["blocking_reasons"])
        self.assertIn("m104_exact_float64_has_tie_sensitive_kth_checksum_mismatch", blockers)
        self.assertIn("m106_fastest_full_batch_route_is_float32_and_exact_false", blockers)
        self.assertIn("fresh_phoenix_m7_review_not_done_for_any_rtnn_row", blockers)

    def test_markdown_records_next_paths_and_decision_audit(self):
        text = self.text
        self.assertIn("Phoenix M7-qualified release rows from this packet: 0", text)
        self.assertIn("M104 exact float64 KITTI same-input gate", text)
        self.assertIn("M106 full-batch aggregate", text)
        self.assertIn("rtnn_kitti_exact_tie_stable_aggregate_review", text)
        self.assertIn("rtnn_full_batch_float32_same_contract_m7_rerun", text)
        self.assertIn("Was I foolish?", text)
        self.assertIn("No. This prevents both under-reading M112", text)

    def test_script_rebuilds_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "packet.json"
            md_out = Path(tmp) / "packet.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            rebuilt = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertEqual(rebuilt["status"], self.payload["status"])
            self.assertEqual(rebuilt["blocking_reasons"], self.payload["blocking_reasons"])
            self.assertIn("RTNN M112 Reconciliation", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

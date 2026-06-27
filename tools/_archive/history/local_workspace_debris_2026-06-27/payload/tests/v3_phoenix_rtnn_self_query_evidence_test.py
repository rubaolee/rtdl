import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_rtnn_self_query_evidence.py"
PACKET_JSON = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_rtnn_prepared_self_query_evidence_2026-06-21.json"
PACKET_MD = PACKET_JSON.with_suffix(".md")


class V3PhoenixRtnnSelfQueryEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")

    def test_packet_records_material_prepared_path_but_not_m7(self):
        payload = self.payload
        self.assertEqual(
            payload["status"],
            "rtnn_prepared_self_query_hot_path_material_not_m7_wall_floor_not_met",
        )
        self.assertEqual(
            payload["generic_capability"],
            "fixed_radius_neighbors_3d_prepared_self_query_aggregate_batch",
        )
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)
        self.assertEqual(payload["review_records"]["external_review_status"], "blocked_no_external_ai_verdict")
        self.assertFalse(payload["review_records"]["two_ai_consensus_exists"])
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))

    def test_comparisons_keep_hot_win_and_wall_boundary_together(self):
        comparisons = self.payload["comparisons"]
        self.assertGreater(comparisons["old_prepared_query_to_new_self_query_hot_speedup"], 2.0)
        self.assertGreater(comparisons["input_pack_reduction_old_to_new"], 2.0)
        self.assertGreater(comparisons["new_self_query_over_cupy_hot_speedup"], 19.0)
        self.assertLess(comparisons["new_self_query_over_cupy_cold_plus_query_speedup"], 2.0)
        self.assertLess(comparisons["new_self_query_over_cupy_runner_wall_speedup"], 1.1)
        self.assertIn("1.030x", self.payload["not_m7_blockers"][1])

    def test_parity_and_contract_are_same_contract(self):
        payload = self.payload
        self.assertTrue(payload["parity"]["integer_signature_match_with_cupy"])
        self.assertTrue(payload["parity"]["integer_signature_match_with_old_prepared_query"])
        self.assertLess(payload["parity"]["sum_distance_relative_error"], 1.0e-4)
        self.assertIn("new_prepared_self_query.json", payload["evidence"]["new_prepared_self_query"])

    def test_markdown_keeps_forbidden_shortcuts_visible(self):
        for phrase in (
            "M7 rows added by this packet: 0",
            "Old prepared-query to new self-query hot speedup: `2.482x`",
            "New self-query over CuPy hot-query speedup: `19.437x`",
            "New self-query over CuPy runner-wall speedup: `1.030x`",
            "Do not quote 19.437x without saying it is hot-query prepared self-query only.",
            "Do not call 1.030x runner-wall speedup a major V3 performance win.",
            "2-AI consensus exists: `false`",
            "Goal-Level Decision Audit",
        ):
            self.assertIn(phrase, self.text)

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
                    "--pretty",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            rebuilt = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertEqual(rebuilt["status"], self.payload["status"])
            self.assertEqual(rebuilt["comparisons"], self.payload["comparisons"])
            self.assertIn("Phoenix V3 RTNN Prepared Self-Query Evidence", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

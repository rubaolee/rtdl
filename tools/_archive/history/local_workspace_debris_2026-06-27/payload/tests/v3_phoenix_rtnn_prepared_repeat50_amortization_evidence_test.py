import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_rtnn_prepared_repeat50_amortization_evidence.py"
PACKET = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_prepared_repeat50_amortization_evidence_2026-06-21.json"
)
REPORT = PACKET.with_suffix(".md")


class V3PhoenixRtnnPreparedRepeat50AmortizationEvidenceTest(unittest.TestCase):
    def load(self):
        return json.loads(PACKET.read_text(encoding="utf-8"))

    def test_packet_records_candidate_without_promotion(self):
        payload = self.load()
        self.assertEqual(
            payload["status"],
            "rtnn_prepared_repeat50_amortization_m7_candidate_pending_external_review_not_release",
        )
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)
        self.assertTrue(payload["m7_reopen_candidate_pending_2ai_review"])
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))

    def test_runner_wall_is_material_but_scope_is_repeat50(self):
        payload = self.load()
        self.assertEqual(payload["parameters"]["point_count"], 1_048_576)
        self.assertEqual(payload["parameters"]["repeat"], 50)
        self.assertEqual(payload["parameters"]["point_column_source"], "npz")
        self.assertGreater(
            payload["comparisons"]["runner_wall_speedup"],
            payload["material_speedup_floor"],
        )
        self.assertGreater(
            payload["comparisons"]["hot_query_speedup"],
            payload["material_speedup_floor"],
        )
        self.assertLess(
            payload["comparisons"]["cold_plus_query_speedup"],
            payload["material_speedup_floor"],
        )
        self.assertEqual(payload["measurements"]["optix"]["point_column_source"], "npz")
        self.assertEqual(payload["measurements"]["cupy_grid"]["point_column_source"], "npz")

    def test_parity_and_boundaries_are_explicit(self):
        payload = self.load()
        self.assertTrue(payload["parity"]["same_contract_signature_match"])
        self.assertTrue(payload["parity"]["integer_signature_match"])
        row_id = payload["candidate_row_ids"][0]
        self.assertIn("repeat50", row_id)
        self.assertIn("1048576", row_id)
        boundaries = "\n".join(payload["not_release_boundaries"])
        self.assertIn("No one-shot", boundaries)
        self.assertIn("No whole RTNN", boundaries)
        self.assertIn("No broad V3-over-V2", boundaries)
        self.assertIn("External Claude/Gemini review", "\n".join(payload["review_required_before_m7"]))

    def test_report_contains_decision_audit(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Phoenix V3 RTNN Prepared Repeat50 Amortization Evidence",
            "prepared-session candidate",
            "M7 rows added now: 0",
            "runner-wall speedup",
            "Goal-Level Decision Audit",
        ):
            self.assertIn(phrase, text)

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
            self.assertEqual(json.loads(json_out.read_text(encoding="utf-8")), self.load())
            self.assertIn("Repeat50", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

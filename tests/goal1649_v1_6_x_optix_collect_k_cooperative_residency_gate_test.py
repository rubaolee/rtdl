import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1649_v1_6_x_optix_collect_k_cooperative_residency_gate.py"
JSON_REPORT = ROOT / "docs" / "reports" / "goal1649_v1_6_x_optix_collect_k_cooperative_residency_gate_2026-05-10.json"
MD_REPORT = ROOT / "docs" / "reports" / "goal1649_v1_6_x_optix_collect_k_cooperative_residency_gate_2026-05-10.md"


class Goal1649OptixCollectKCooperativeResidencyGateTest(unittest.TestCase):
    def test_script_records_residency_gate_and_claim_boundary(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("full_level_cooperative_fusion_rejected_by_residency_gate", text)
        self.assertIn("max_resident_threads_bound", text)
        self.assertIn("\"performance_evidence_authorized\": False", text)
        self.assertIn("does not authorize public speedup wording", text)

    def test_report_rejects_full_level_fusion_for_a4500_long_shape(self) -> None:
        payload = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
        md = MD_REPORT.read_text(encoding="utf-8")

        self.assertEqual(payload["status"], "full_level_cooperative_fusion_rejected_by_residency_gate")
        self.assertFalse(payload["full_level_cooperative_fusion_allowed"])
        self.assertEqual(payload["candidate_count"], 262144)
        self.assertGreater(payload["levels"][0]["required_blocks"], payload["max_resident_blocks_bound"])
        self.assertGreater(payload["levels"][0]["required_threads"], payload["max_resident_threads_bound"])
        self.assertIn("not performance evidence", payload["claim_boundary"])
        self.assertIn("impossible full-level cooperative launch shape", md)


if __name__ == "__main__":
    unittest.main()

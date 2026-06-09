import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal4258_public_claim_wording_repair_closure_2026-06-09.md"
WORDING = ROOT / "docs/reports/goal4254_v2_10_public_claim_wording_candidate_2026-06-09.md"


class Goal4258PublicClaimWordingRepairClosureTest(unittest.TestCase):
    def test_report_records_all_claude_required_repairs(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("R1", text)
        self.assertIn("R2", text)
        self.assertIn("R3", text)
        self.assertIn("measured OptiX speedups", text)
        self.assertIn("where custom continuation logic is needed", text)
        self.assertIn("platform-specific setup", text)

    def test_wording_candidate_contains_repairs(self) -> None:
        text = WORDING.read_text(encoding="utf-8")

        self.assertIn("measured OptiX", text)
        self.assertIn("where custom continuation logic is needed", text)
        self.assertIn("see the README for platform-specific", text)
        self.assertIn("specific workload contracts and reviewed timing artifacts", text)
        self.assertNotIn("strong OptiX benefits", text)
        self.assertNotIn("where a benchmark needs custom continuation logic", text)
        self.assertNotIn("used from the source tree with `PYTHONPATH=src:.`", text)

    def test_report_keeps_release_boundary_closed(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("does not authorize release", text)
        self.assertIn("public", text)
        self.assertIn("speedup wording", text)
        self.assertIn("whole-app acceleration wording", text)
        self.assertIn("AMD/HIPRT", text)


if __name__ == "__main__":
    unittest.main()

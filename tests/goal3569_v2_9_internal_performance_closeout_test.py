from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3569_v2_9_internal_performance_closeout_2026-06-06.md"


class Goal3569V29InternalPerformanceCloseoutTest(unittest.TestCase):
    def test_report_closes_v2_9_as_internal_only(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("v2.9 is closed as an internal performance version", text)
        self.assertIn("This is not a release packet", text)
        self.assertIn("does not authorize", text)
        self.assertIn("internal benchmark evidence only", text)

    def test_evidence_chain_covers_required_reviews_and_repairs(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for goal in ("Goal3560", "Goal3562", "Goal3565", "Goal3566", "Goal3567", "Goal3568"):
            self.assertIn(goal, text)
        self.assertIn("RayDB sum repaired to `1.585627x`", text)
        self.assertIn("Gemini review of Goal3567", text)
        self.assertIn("Claude review of Goals3563-3565", text)

    def test_final_packet_summary_and_remaining_rows_are_honest(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("geomean speedup | 1.069163x", text)
        self.assertIn("median speedup | 1.009085x", text)
        self.assertIn("min speedup | 0.987619x", text)
        self.assertIn("RTNN is near parity: `1.010948x`", text)
        self.assertIn("LibRTS `0.993581x`", text)
        self.assertIn("sub-1%", text)

    def test_next_version_is_architectural_not_minor_v2_9_cleanup(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("larger architectural targets", text)
        self.assertIn("stronger grouped-reduction and row-stream primitives", text)
        self.assertIn("next version lane", text)


if __name__ == "__main__":
    unittest.main()

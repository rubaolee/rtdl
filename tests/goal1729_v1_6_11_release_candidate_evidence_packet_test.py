import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1729_v1_6_11_release_candidate_evidence_packet_2026-05-12.md"


class Goal1729V1611ReleaseCandidateEvidencePacketTest(unittest.TestCase):
    def test_packet_summarizes_required_evidence_chain(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for goal in ("Goal1714", "Goal1716", "Goal1718", "Goal1720", "Goal1722", "Goal1723", "Goal1726", "Goal1746-1750"):
            self.assertIn(goal, text)
        self.assertIn("Goal1727", text)
        self.assertIn("Goal1728", text)

    def test_packet_records_correct_counts(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Current-version Goal1659 active pod rows: `16/16`", text)
        self.assertIn("Goal1660 matrix rows: `36`", text)
        self.assertIn("Goal1660 real comparable rows: `16`", text)
        self.assertIn("Goal1660 blocked/excluded/current-only rows: `20`", text)
        self.assertIn("Comparable artifact pairs present: `16/16`", text)
        self.assertIn("Rows with clean parity or companion evidence: `16/16`", text)
        self.assertIn("Unresolved companion-evidence boundaries: `0`", text)

    def test_packet_does_not_authorize_release_or_public_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("does not publish v1.6.11", text)
        self.assertIn("does not itself authorize", text)
        self.assertIn("publishing or tagging v1.6.11", text)
        self.assertIn("public speedup wording", text)
        self.assertIn("Final release action requires an explicit user decision", text)

    def test_packet_treats_unsupported_v1_0_embree_rows_fail_closed(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Unsupported v1.0 Embree rows", text)
        self.assertIn("current-only unsupported rows", text)
        self.assertIn("not failed baselines", text)
        self.assertIn("not slower/faster timing evidence", text)
        self.assertIn("Post-packet clarification", text)
        self.assertIn("Goal1746 later recovered real v1.0 Embree app-level artifacts", text)
        self.assertIn("Goal1750 therefore preserves the conservative interpretation", text)
        self.assertIn("no public speedup wording is authorized", text)


if __name__ == "__main__":
    unittest.main()

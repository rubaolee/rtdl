import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1754_v1_8_commit_ready_inventory_after_perf_summary_2026-05-12.md"


class Goal1754V18CommitReadyInventoryAfterPerfSummaryTest(unittest.TestCase):
    def test_inventory_names_v1_8_decision_trail(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for goal in (
            "goal1737",
            "goal1738",
            "goal1739",
            "goal1740",
            "goal1741",
            "goal1742",
            "goal1743",
            "goal1745",
            "goal1753",
            "goal1758",
            "goal1759",
            "goal1760",
            "goal1761",
            "goal1762",
            "goal1763",
            "goal1764",
            "goal1765",
            "goal1766",
            "goal1767",
            "goal1768",
        ):
            self.assertIn(goal, text)
        self.assertIn("v1_8_inventory_ready_pending_user_release_authorization", text)

    def test_inventory_names_performance_clarification_chain(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for goal in ("goal1746", "goal1747", "goal1748", "goal1749", "goal1750", "goal1751"):
            self.assertIn(goal, text)
        self.assertIn("v1.0 customized-engine versus current generic-engine", text)

    def test_inventory_protects_local_files_and_missing_claude_review(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Do not stage local/protected files", text)
        self.assertIn("docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz", text)
        self.assertIn("id_ed25519_rtdl_codex", text)
        self.assertIn("rtdl_v0_4.tar.gz", text)
        self.assertIn("scratch/", text)
        self.assertIn("older attempted Claude output path remains absent", text)
        self.assertFalse(
            (ROOT / "docs" / "reviews" / "goal1752_claude_review_updated_goal1742_1750_v1_8_packet_2026-05-12.md").exists()
        )

    def test_inventory_records_gate_and_remaining_blockers(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Ran 167 tests", text)
        self.assertIn("OK (skipped=1)", text)
        self.assertIn("Explicit user authorization", text)
        self.assertIn("not a release decision", text)


if __name__ == "__main__":
    unittest.main()

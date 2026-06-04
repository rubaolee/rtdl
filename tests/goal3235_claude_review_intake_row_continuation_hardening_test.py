from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3235_claude_review_intake_row_continuation_hardening_2026-06-03.md"
SCRIPT = ROOT / "scripts" / "goal3232_rayjoin_public_row_continuation_probe.py"


class Goal3235ClaudeReviewIntakeRowContinuationHardeningTest(unittest.TestCase):
    def test_report_records_claude_findings_and_intake_actions(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3233 Claude review",
            "Rejects prepared PIP rows unless `membership == 1`",
            "unattributed_prepared_total_minus_named_phases_sec",
            "positive_assignments_count",
            "active_seed_pairs_count",
            "d19a8175d9e8c211aee2d1395dd5fa8b1ebb5223",
            "9 tests OK",
        ):
            self.assertIn(phrase, report)

    def test_script_contains_hardening_hooks(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "prepared PIP rows must be positive-only",
            "named_phase_total_sec",
            "unattributed_prepared_total_minus_named_phases_sec",
            "positive_assignments_count",
            "active_seed_pairs_count",
        ):
            self.assertIn(phrase, text)

    def test_report_preserves_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "does not authorize",
            "public speedup claims",
            "broad RT-core claims",
            "true zero-copy claims",
            "RTDL beats RayJoin",
            "RayJoin paper-reproduction claims",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()

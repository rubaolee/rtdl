from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reviews" / "goal1670_all_external_partner_analysis_consensus_2026-05-10.md"
EXTERNAL_CLAUDE = ROOT / "docs" / "reviews" / "goal1669_external_claude_python_partner_rtdl_design_analysis_2026-05-10.md"
EXTERNAL_GEMINI = ROOT / "docs" / "reviews" / "goal1669_external_gemini_v1_7_partner_architecture_analysis_2026-05-10.md"


class Goal1670AllExternalPartnerAnalysisConsensusTest(unittest.TestCase):
    def test_external_reports_are_preserved(self) -> None:
        for path in (EXTERNAL_CLAUDE, EXTERNAL_GEMINI):
            with self.subTest(path=path.name):
                self.assertTrue(path.exists())
                self.assertGreater(path.stat().st_size, 1000)

    def test_consensus_records_reconciled_partner_priority(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        for phrase in (
            "PyTorch as the primary public/reference partner",
            "CuPy as the lightweight conformance and CI validation partner",
            "Protocol first. PyTorch reference first. CuPy conformance alongside it.",
            "Engine absolutely app-agnostic throughout.",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_consensus_preserves_app_agnostic_and_claim_boundaries(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        for phrase in (
            "must not become a new app-specific native backdoor",
            "must not link directly against PyTorch",
            "True zero-copy is a measured claim boundary",
            "RTDL accelerates arbitrary PyTorch/CuPy programs",
            "RTDL native internals are fully app-agnostic",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

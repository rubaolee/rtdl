from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RT_MATRIX = ROOT / "docs" / "learn" / "rt_core_evidence_matrix.md"
GOAL_TIER = ROOT / "docs" / "audit" / "process" / "goal_tier_protocol.md"


class Goal4305Fable5EvidenceAndProcessDocsTest(unittest.TestCase):
    def test_rt_core_evidence_matrix_is_conservative_and_linked(self) -> None:
        text = RT_MATRIX.read_text(encoding="utf-8")
        self.assertIn("ten benchmark apps", text)
        self.assertIn("not ten broad RT-core speedup claims", text)
        self.assertIn("Strong RT evidence", text)
        self.assertIn("Mixed RT evidence", text)
        self.assertIn("Partner-led evidence", text)
        self.assertIn("Barnes-Hut", text)
        self.assertIn("Blocked wording", text)

        learn_index = (ROOT / "docs" / "learn" / "benchmark_evidence_index.md").read_text(encoding="utf-8")
        self.assertIn("RT-Core Evidence Matrix](rt_core_evidence_matrix.md)", learn_index)
        self.assertIn("A ten-app packet is not ten broad RT-core speedup claims", learn_index)

        learn_readme = (ROOT / "docs" / "learn" / "README.md").read_text(encoding="utf-8")
        self.assertIn("RT-Core Evidence Matrix](rt_core_evidence_matrix.md)", learn_readme)

        docs_readme = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        self.assertIn("RT-Core Evidence Matrix](learn/rt_core_evidence_matrix.md)", docs_readme)

    def test_goal_tier_protocol_reduces_ceremony_without_weakening_claim_rules(self) -> None:
        text = GOAL_TIER.read_text(encoding="utf-8")
        for phrase in (
            "Tier A: Light Goals",
            "Tier B: Runtime Or Contract Goals",
            "Tier C: Claim, Roadmap, Release, Or Major Evidence Goals",
            "Native engine remains app-agnostic",
            "Broad speedup and whole-app acceleration wording remain blocked",
            "Goal4301 Numba grouped top-k device rank",
        ):
            self.assertIn(phrase, text)

        audit_readme = (ROOT / "docs" / "audit" / "README.md").read_text(encoding="utf-8")
        self.assertIn("Goal Tier Protocol](process/goal_tier_protocol.md)", audit_readme)

        process_readme = (ROOT / "docs" / "audit" / "process" / "README.md").read_text(encoding="utf-8")
        self.assertIn("Goal tier protocol", process_readme)
        self.assertIn("goal_tier_protocol.md", process_readme)


if __name__ == "__main__":
    unittest.main()

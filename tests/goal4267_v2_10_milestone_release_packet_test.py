from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4267_v2_10_milestone_release_packet_2026-06-10.md"
GUIDE = ROOT / "docs/learn/partner_choice_for_custom_logic.md"
MATRIX = ROOT / "docs/learn/benchmark_partner_reference_matrix.md"


class Goal4267V210MilestoneReleasePacketTest(unittest.TestCase):
    def test_packet_records_milestone_identity_and_user_decision(self) -> None:
        text = PACKET.read_text(encoding="utf-8")

        self.assertIn("Goal4267 v2.10 Milestone Release Packet", text)
        self.assertIn("source-tree milestone", text)
        self.assertIn("Then go! Make this one a milestone version.", text)
        self.assertIn("0c842eb0", text)
        self.assertIn("Goal4266", text)
        self.assertIn("fresh 3-AI consensus", text)

    def test_packet_includes_current_partner_evidence_and_deferred_scope(self) -> None:
        text = PACKET.read_text(encoding="utf-8")
        lowered = text.lower()

        self.assertIn("large-scale cupy-vs-numba partner evidence", lowered)
        self.assertIn("same contract, same repeat count, CPU-oracle validation", text)
        self.assertIn("more than one second of aggregate hot time", text)
        self.assertIn("partner-continuation", text)
        self.assertIn("evidence only", text)
        self.assertIn("Embree + Numba CPU partner claim | not included; deferred to v2.11", text)

    def test_packet_blocks_overclaims(self) -> None:
        text = PACKET.read_text(encoding="utf-8")

        for phrase in (
            "package-install product readiness",
            "universal speedup",
            "broad RT-core speedup guarantee",
            "whole-application acceleration guarantee",
            "RTDL-beats-RayJoin wording",
            "full paper reproduction",
            "true-zero-copy product guarantee",
            "automatic backend or partner selection",
            "AMD/HIPRT performance or parity wording",
            "Embree + Numba CPU partner wording",
            "app-specific native-engine logic",
            "universal CuPy-vs-Numba winner claims",
        ):
            self.assertIn(phrase, text)

    def test_learner_docs_are_refreshed_after_goal4266(self) -> None:
        docs = GUIDE.read_text(encoding="utf-8") + "\n" + MATRIX.read_text(encoding="utf-8")

        stale_phrases = (
            "no current same-contract CuPy timing row for this unfused table",
            "no current same-contract CuPy compact-mask timing row",
        )
        for phrase in stale_phrases:
            self.assertNotIn(phrase, docs)

        self.assertIn("Goal4266", docs)
        self.assertIn("same repeat count", docs)
        self.assertIn("CPU-oracle validation", docs)
        self.assertIn("more than one second of aggregate hot time", docs)
        self.assertIn("partner-continuation evidence", docs)


if __name__ == "__main__":
    unittest.main()

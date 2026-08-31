import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs" / "reports" / "goal3522_v2_8_internal_closeout_packet_2026-06-05.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal3522_v2_8_internal_closeout_3ai_consensus_2026-06-05.md"
HANDOFFS = (
    ROOT / "docs" / "handoff" / "HANDOFF_CLAUDE_GOAL3522_V2_8_INTERNAL_CLOSEOUT_REVIEW_2026-06-05.md",
    ROOT / "docs" / "handoff" / "HANDOFF_GEMINI_GOAL3522_V2_8_INTERNAL_CLOSEOUT_REVIEW_2026-06-05.md",
)
REVIEWS = (
    ROOT / "docs" / "reviews" / "goal3522_claude_review_v2_8_internal_closeout_2026-06-05.md",
    ROOT / "docs" / "reviews" / "goal3522_gemini_review_v2_8_internal_closeout_2026-06-05.md",
)


class Goal3522V28InternalCloseoutPacketTest(unittest.TestCase):
    def test_packet_summarizes_required_closeout_chain(self):
        text = PACKET.read_text(encoding="utf-8")

        for goal in ("Goal3512", "Goal3516", "Goal3517", "Goal3518", "Goal3519", "Goal3520", "Goal3521"):
            self.assertIn(goal, text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("internal version", text)
        self.assertIn("not public release authorization", text)
        self.assertIn("9ad59f1e7abbe0b2a97e785b28f7358aaa14d6c8", text)

    def test_packet_blocks_public_claims(self):
        text = PACKET.read_text(encoding="utf-8").lower()

        for phrase in (
            "public v2.8 release authorization",
            "package-install",
            "public speedup wording",
            "broad rt-core speedup wording",
            "true zero-copy wording",
            "full rayjoin paper reproduction",
            "hidden partner selection",
            "app-specific native-engine behavior",
        ):
            self.assertIn(phrase, text)
        self.assertNotIn("v2.8 release authorized", text)
        self.assertNotIn("public speedup claim authorized", text)
        self.assertNotIn("true zero-copy authorized", text)
        self.assertNotIn("rtdl beats rayjoin is authorized", text)

    def test_packet_records_final_validation_rows(self):
        text = PACKET.read_text(encoding="utf-8")

        for phrase in (
            "Robot collision",
            "Contact manifold",
            "RT-DBSCAN",
            "Spatial RayJoin overlay",
            "0.003779787s",
            "4.897x",
            "9.23e-09",
        ):
            self.assertIn(phrase, text)

    def test_external_review_handoffs_exist(self):
        for path in HANDOFFS:
            text = path.read_text(encoding="utf-8")
            self.assertIn("Goal3522", text)
            self.assertIn("Required Output", text)
            self.assertIn("accept-with-boundary", text)

    def test_external_reviews_and_consensus_exist(self):
        for path in REVIEWS:
            text = path.read_text(encoding="utf-8").lower()
            self.assertIn("accept-with-boundary", text)

        consensus = CONSENSUS.read_text(encoding="utf-8").lower()
        self.assertIn("v2.8 is closed as an internal version", consensus)
        self.assertIn("raw rt-count row is `0.937x`", consensus)
        self.assertIn("does not authorize", consensus)
        self.assertNotIn("v2.8 release authorized", consensus)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2092_v2_0_release_consensus_gap_after_gemini_pro_2026-05-15.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2090_gemini_review_goal2088_post_streaming_v2_release_prep_2026-05-15.md"
COPILOT = ROOT / "docs" / "reviews" / "goal2091_copilot_supplemental_review_goal2088_post_streaming_v2_release_prep_2026-05-15.md"
AUTH = ROOT / "docs" / "handoff" / "USER_V2_0_RELEASE_AUTHORIZATION_2026-05-15.md"


class Goal2092V2ReleaseConsensusGapAfterGeminiProTest(unittest.TestCase):
    def test_report_records_gemini_and_copilot_without_replacing_claude(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Gemini Pro final review", text)
        self.assertIn("Copilot supplemental review", text)
        self.assertIn("Claude final review", text)
        self.assertIn("missing", text)
        self.assertIn("Copilot does not replace Claude", text)

    def test_review_and_authorization_files_exist(self) -> None:
        self.assertIn("accept-with-boundary", GEMINI.read_text(encoding="utf-8"))
        self.assertIn("accept-with-boundary", COPILOT.read_text(encoding="utf-8"))
        self.assertIn("release-authorized", AUTH.read_text(encoding="utf-8"))

    def test_options_require_explicit_governance_choice(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Wait for Claude", text)
        self.assertIn("explicitly relaxes the rule", text)
        self.assertIn("bounded pre-release tag", text)
        self.assertIn("only remaining issue is governance", text)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal4257_v2_10_release_candidate_packet_draft_2026-06-09.md"


class Goal4257V210ReleaseCandidatePacketDraftTest(unittest.TestCase):
    def test_packet_is_draft_not_authorization(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: draft packet, not release authorization", text)
        self.assertIn("does not tag, publish, or authorize release", text)
        self.assertIn("User release decision | pending", text)
        self.assertIn("Final 3-AI release consensus over this exact packet | pending", text)

    def test_packet_includes_current_evidence_chain(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for goal in (
            "Goal4235",
            "Goal4239",
            "Goal4243",
            "Goal4248",
            "Goal4249",
            "Goal4250",
            "Goal4251",
            "Goal4252",
            "Goal4253",
            "Goal4254",
            "Goal4255",
            "Goal4256",
            "Goal4258",
            "Goal4259",
            "Goal4260",
            "Goal4261",
            "Goal4262",
        ):
            self.assertIn(goal, text)

    def test_packet_excludes_overclaims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "package-install product readiness",
            "universal speedup",
            "broad RT-core speedup guarantee",
            "whole-application acceleration guarantee",
            "RTDL-beats-RayJoin wording",
            "full paper reproduction",
            "true-zero-copy product guarantee",
            "automatic backend/partner selection",
            "AMD/HIPRT performance or parity wording",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

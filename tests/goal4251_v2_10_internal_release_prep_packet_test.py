import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal4251_v2_10_internal_release_prep_packet_2026-06-09.md"


class Goal4251V210InternalReleasePrepPacketTest(unittest.TestCase):
    def test_packet_is_non_authorizing(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("not release authorization", text)
        self.assertIn("does not authorize release", text)
        self.assertIn("Broad RT-core speedup claim | blocked", text)
        self.assertIn("Whole-application acceleration claim | blocked", text)
        self.assertIn("RTDL-beats-RayJoin claim | blocked", text)
        self.assertIn("Package-install claim | blocked", text)
        self.assertIn("RTDL-beats-RayJoin wording", text)
        self.assertIn("AMD/HIPRT performance wording", text)
        self.assertIn("automatic partner/backend selection", text)

    def test_packet_references_current_evidence_chain(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for goal in (
            "Goal4235",
            "Goal4239",
            "Goal4243",
            "Goal4245",
            "Goal4248",
            "Goal4249",
            "Goal4250",
        ):
            self.assertIn(goal, text)

        self.assertIn("31 files, 116 claim-sensitive phrases, and 0 hard blockers", text)
        self.assertIn("22 tests OK", text)
        self.assertIn("rtdl.v2_10.current_major_performance_targets.goal4249.v1", text)

    def test_packet_keeps_user_chosen_partner_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("explicit user-chosen partners", text)
        self.assertIn("Partner and backend choice stays explicit and user-owned", text)
        self.assertIn("not an app library or hidden dispatcher", text)


if __name__ == "__main__":
    unittest.main()

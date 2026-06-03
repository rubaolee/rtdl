import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal3164_v2_8_front_door_chain_review_packet_2026-06-03.md"
HANDOFF = REPO_ROOT / "docs" / "handoff" / "HANDOFF_EXTERNAL_REVIEW_GOAL3164_V2_8_FRONT_DOOR_CHAIN_2026-06-03.md"


class Goal3164V28FrontDoorChainReviewPacketTest(unittest.TestCase):
    def test_packet_names_all_front_door_goals_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for goal in ("Goal3155", "Goal3156", "Goal3157", "Goal3158", "Goal3159", "Goal3160", "Goal3161", "Goal3162", "Goal3163"):
            self.assertIn(goal, text)
        for phrase in (
            "fixed-radius graph component front door",
            "directed_max_of_nearest_distance_2d_partner_columns",
            "execute_grouped_reduction_typed_stream_partner_columns",
            "compatibility alias",
            "None of these goals authorizes release",
            "true-zero-copy claims",
            "automatic partner selection",
            "app-specific native-engine logic",
            "accept-with-boundary",
        ):
            self.assertIn(phrase, text)

    def test_handoff_points_to_requested_review_path(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")
        self.assertIn("goal3164_v2_8_front_door_chain_review_packet_2026-06-03.md", text)
        self.assertIn("goal3164_external_review_v2_8_front_door_chain_2026-06-03.md", text)
        self.assertIn("engine/app boundary", text)


if __name__ == "__main__":
    unittest.main()

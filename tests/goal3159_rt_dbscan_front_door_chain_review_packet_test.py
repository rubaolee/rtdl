from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs" / "reports" / "goal3159_rt_dbscan_front_door_chain_review_packet_2026-06-03.md"
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_EXTERNAL_REVIEW_GOAL3159_RT_DBSCAN_FRONT_DOOR_CHAIN_2026-06-03.md"


class Goal3159RTDBSCANFrontDoorChainReviewPacketTest(unittest.TestCase):
    def test_packet_lists_all_chain_goals_and_files(self) -> None:
        packet = PACKET.read_text(encoding="utf-8")

        for phrase in (
            "Goal3155",
            "Goal3156",
            "Goal3157",
            "Goal3158",
            "src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py",
            "examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py",
            "tests/goal3158_fixed_radius_graph_typed_producer_metadata_test.py",
        ):
            self.assertIn(phrase, packet)

    def test_packet_and_handoff_block_claims(self) -> None:
        combined = "\n".join((PACKET.read_text(encoding="utf-8"), HANDOFF.read_text(encoding="utf-8")))

        for phrase in (
            "v2.8 release authorization",
            "public whole-app speedup authorization",
            "broad RT-core speedup authorization",
            "true-zero-copy authorization",
            "automatic partner selection",
            "app-specific native engine logic",
        ):
            self.assertIn(phrase, combined)

    def test_handoff_names_distinct_review_outputs(self) -> None:
        handoff = HANDOFF.read_text(encoding="utf-8")

        self.assertIn("goal3159_claude_review_rt_dbscan_front_door_chain_2026-06-03.md", handoff)
        self.assertIn("goal3159_gemini_review_rt_dbscan_front_door_chain_2026-06-03.md", handoff)
        self.assertIn("accept-with-boundary", handoff)


if __name__ == "__main__":
    unittest.main()

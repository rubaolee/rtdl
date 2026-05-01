from __future__ import annotations

import unittest

from scripts.goal1196_public_wording_decision_packet import build_packet
from scripts.goal1196_public_wording_decision_packet import to_markdown


class Goal1196PublicWordingDecisionPacketTest(unittest.TestCase):
    def test_promotes_only_positive_optix_over_embree_rows(self) -> None:
        payload = build_packet()
        self.assertEqual(
            payload["proposed_public_wording_reviewed_apps"],
            ["road_hazard_screening", "hausdorff_distance"],
        )
        self.assertEqual(
            payload["proposed_public_wording_blocked_apps"],
            [
                "database_analytics",
                "graph_analytics",
                "polygon_pair_overlap_area_rows",
                "polygon_set_jaccard",
            ],
        )
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)

    def test_blocked_rows_do_not_get_positive_wording(self) -> None:
        payload = build_packet()
        by_app = {row["app"]: row for row in payload["rows"]}
        for app in payload["proposed_public_wording_blocked_apps"]:
            self.assertEqual(by_app[app]["status_to_apply"], "public_wording_blocked")
            self.assertIn("No positive public RTX speedup wording", by_app[app]["candidate_public_wording"])
        self.assertIn("first pod run failed parity", by_app["polygon_set_jaccard"]["boundary"])
        self.assertIn("chunk-sensitive or nondeterministic behavior", by_app["polygon_set_jaccard"]["boundary"])

    def test_markdown_preserves_non_authorization_boundary(self) -> None:
        text = to_markdown(build_packet())
        self.assertIn("does not edit public docs or authorize release", text)
        self.assertIn("whole-app", text)
        self.assertIn("DBMS", text)
        self.assertIn("exact-distance", text)


if __name__ == "__main__":
    unittest.main()

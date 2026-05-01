from __future__ import annotations

import unittest

from scripts.goal1224_resolve_remaining_public_wording_rows import build_packet, to_markdown


class Goal1224ResolveRemainingPublicWordingRowsTest(unittest.TestCase):
    def test_decisions_resolve_three_remaining_rows(self) -> None:
        payload = build_packet()
        by_app = {row["app"]: row for row in payload["rows"]}

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["promote_to_public_wording_reviewed"], ["hausdorff_distance"])
        self.assertEqual(
            payload["mark_public_wording_blocked"],
            ["graph_analytics", "polygon_pair_overlap_area_rows"],
        )
        self.assertEqual(by_app["hausdorff_distance"]["decision"], "public_wording_reviewed")
        self.assertEqual(by_app["graph_analytics"]["decision"], "public_wording_blocked")
        self.assertEqual(by_app["polygon_pair_overlap_area_rows"]["decision"], "public_wording_blocked")

    def test_positive_public_speedup_requires_ratio_floor(self) -> None:
        payload = build_packet()
        by_app = {row["app"]: row for row in payload["rows"]}

        self.assertGreater(by_app["hausdorff_distance"]["raw_ratio_embree_over_optix"], payload["min_public_ratio"])
        self.assertLess(by_app["graph_analytics"]["raw_ratio_embree_over_optix"], payload["min_public_ratio"])
        self.assertLess(
            by_app["polygon_pair_overlap_area_rows"]["raw_ratio_embree_over_optix"],
            payload["min_public_ratio"],
        )

    def test_markdown_preserves_boundaries(self) -> None:
        text = to_markdown(build_packet())

        self.assertIn("does not move the v0.9.8 release tag", text)
        self.assertIn("whole-app claims", text)
        self.assertIn("exact Hausdorff distance", text)
        self.assertIn("exact polygon-area continuation", text)
        self.assertIn("BFS frontier bookkeeping", text)


if __name__ == "__main__":
    unittest.main()

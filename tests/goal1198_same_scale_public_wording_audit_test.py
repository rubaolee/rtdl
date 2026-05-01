from __future__ import annotations

import unittest

from scripts.goal1198_same_scale_public_wording_audit import build_audit
from scripts.goal1198_same_scale_public_wording_audit import to_markdown


class Goal1198SameScalePublicWordingAuditTest(unittest.TestCase):
    def test_hausdorff_positive_ratio_is_blocked_by_scale_mismatch(self) -> None:
        payload = build_audit()
        rows = {row["app"]: row for row in payload["rows"]}
        hausdorff = rows["hausdorff_distance"]
        self.assertEqual(hausdorff["embree_copies"], 2000)
        self.assertEqual(hausdorff["optix_copies"], 1200000)
        self.assertFalse(hausdorff["same_scale"])
        self.assertTrue(hausdorff["optix_faster"])
        self.assertFalse(hausdorff["public_ratio_safe"])
        self.assertIn("hausdorff_distance has OptiX-faster ratio but not same-scale artifacts", payload["blockers"])

    def test_only_road_hazard_has_safe_positive_ratio(self) -> None:
        payload = build_audit()
        self.assertEqual(payload["safe_positive_public_ratio_apps"], ["road_hazard_screening"])
        self.assertIn("hausdorff_distance", payload["unsafe_or_blocked_ratio_apps"])

    def test_markdown_supersedes_unsafe_hausdorff_promotion(self) -> None:
        markdown = to_markdown(build_audit())
        self.assertIn("Goal1196 Hausdorff positive wording proposal is unsafe", markdown)
        self.assertIn("same-scale", markdown)
        self.assertIn("road_hazard_screening", markdown)


if __name__ == "__main__":
    unittest.main()

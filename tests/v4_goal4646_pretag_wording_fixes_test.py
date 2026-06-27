from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4 import V4_AUTHORIZED_RELEASE_LABEL
from rtdsl.v4_goal4639_release_scorecard_decision import validate_v4_goal4639_release_scorecard_decision
from rtdsl.v4_goal4643_publication_decision import validate_v4_goal4643_publication_decision


PUBLIC_TAG_DOCS = (
    ROOT / "README.md",
    ROOT / "docs" / "current_v4_status.md",
    ROOT / "docs" / "learn" / "performance_wording.md",
    ROOT / "future" / "v4" / "README.md",
    ROOT / "future" / "v4" / "tier2_operator_catalog.md",
    ROOT / "future" / "v4" / "v4_goal4643_publication_decision_2026-06-25.md",
    ROOT / "future" / "v4" / "v4_goal4644_post_release_guardrails_2026-06-25.md",
)

OLD_UNQUALIFIED_LABEL = "RTDL v4.0.0 formal high-performance generic RT-core operator release"


class V4Goal4646PreTagWordingFixesTest(unittest.TestCase):
    def test_public_label_is_bounded_to_stated_baselines(self) -> None:
        publication = validate_v4_goal4643_publication_decision(ROOT)

        self.assertEqual(V4_AUTHORIZED_RELEASE_LABEL, publication["authorized_release_label"])
        self.assertIn("Python eDSL/operator-pushdown release candidate", publication["authorized_release_label"])
        self.assertIn("complete 10-app NVIDIA RT-core", publication["authorized_release_label"])
        self.assertIn("broad all-benchmark speedup remains unauthorized", publication["authorized_release_label"])
        self.assertNotEqual(OLD_UNQUALIFIED_LABEL, publication["authorized_release_label"])

    def test_public_docs_do_not_use_old_unqualified_label(self) -> None:
        for path in PUBLIC_TAG_DOCS:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn(OLD_UNQUALIFIED_LABEL, text)
                self.assertNotIn("near-OptiX performance from Python", text)
                self.assertNotIn("Representative operator geomean", text)

    def test_current_release_docs_report_distribution_not_geomean_headline(self) -> None:
        for path in (
            ROOT / "README.md",
            ROOT / "docs" / "current_v4_status.md",
            ROOT / "future" / "v4" / "README.md",
            ROOT / "future" / "v4" / "v4_goal4643_publication_decision_2026-06-25.md",
        ):
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                text = path.read_text(encoding="utf-8")
                self.assertIn("most measured operators", text)
                self.assertIn("1.2", text)
                self.assertIn("1.7x", text)
                self.assertIn("algorithmic-complexity", text)
                self.assertIn("brute-force partner/CPU baselines", text)

    def test_each_scorecard_surface_has_denominator_and_scale(self) -> None:
        decision = validate_v4_goal4639_release_scorecard_decision()
        ratios = decision["surface_representative_ratios"]
        denominators = decision["surface_denominators"]

        self.assertEqual(8, len(ratios))
        self.assertEqual(set(ratios), set(denominators))
        for surface, metadata in denominators.items():
            with self.subTest(surface=surface):
                self.assertTrue(metadata["baseline"])
                self.assertTrue(metadata["scale"])
                self.assertIn("presentation_class", metadata)

    def test_outliers_are_labeled_as_scale_dependent_complexity_wins(self) -> None:
        decision = validate_v4_goal4639_release_scorecard_decision()
        denominators = decision["surface_denominators"]

        self.assertEqual(
            "algorithmic_complexity_outlier_o_n2_vs_bvh",
            denominators["v4_point_group_nearest_witness_2d_device_arrays"]["presentation_class"],
        )
        self.assertEqual(
            "algorithmic_complexity_outlier_indexed_bvh_vs_slower_control",
            denominators["v4_aabb_index_query_2d_all_ops_count_prepared_runner"]["presentation_class"],
        )
        self.assertIn(
            "Do not headline the 5.185x geomean",
            decision["public_ratio_distribution"]["headline_rule"],
        )


if __name__ == "__main__":
    unittest.main()

import json
import math
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5271_level_b_pruning_diagnostic_2026-07-09.json"
)


class Goal5271LevelBPruningDiagnosticTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_only_correctness_clean_variants_enter_primary_diagnostic(self):
        rows = self.data["correctness_clean_profile_variants"]
        self.assertEqual([row["label"] for row in rows], ["noopt", "eb", "eb_prune"])
        self.assertTrue(all(row["matches_reference"] for row in rows))
        self.assertTrue(all(row["lb"] == 0 for row in rows))

    def test_derived_reductions_are_consistent_with_rows(self):
        rows = {row["label"]: row for row in self.data["correctness_clean_profile_variants"]}
        effects = self.data["derived_level_b_effects"]
        self.assertTrue(
            math.isclose(
                effects["eb_time_speedup_vs_noopt"],
                rows["noopt"]["running_avg_time_ms"] / rows["eb"]["running_avg_time_ms"],
                rel_tol=1e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                effects["eb_prune_time_speedup_vs_eb"],
                rows["eb"]["running_avg_time_ms"] / rows["eb_prune"]["running_avg_time_ms"],
                rel_tol=1e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                effects["eb_prune_compared_points_reduction_factor_vs_noopt"],
                rows["noopt"]["sum_ComparedPoints"] / rows["eb_prune"]["sum_ComparedPoints"],
                rel_tol=1e-12,
            )
        )

    def test_lb256_is_invalid_and_lb2048_is_not_figure6(self):
        controls = self.data["invalid_or_diagnostic_controls"]
        lb256 = controls["lb256_author_figure6_setting_on_candidate"]
        self.assertEqual(lb256["lb"], 256)
        self.assertFalse(lb256["matches_reference"])
        self.assertEqual(
            lb256["use_in_diagnostic"], "invalid_for_correctness_clean_level_b_diagnostic"
        )
        lb2048 = controls["lb2048_candidate_only_control"]
        self.assertEqual(lb2048["lb"], 2048)
        self.assertTrue(lb2048["matches_reference"])
        self.assertEqual(
            lb2048["use_in_diagnostic"],
            "correctness_clean_candidate_control_only_not_author_figure6_setting",
        )

    def test_claim_boundary_forbids_paper_figure_and_ratio_claims(self):
        boundary = self.data["claim_boundary"]
        for key in [
            "figure6_reproduced",
            "full_paper_reproduction_claimed",
            "exact_paper_dataset_identity_claimed",
            "author_rt_core_equivalence_claimed",
            "performance_ratio_claimed",
            "lb2048_substitute_authorized_as_figure6",
        ]:
            self.assertFalse(boundary[key], key)
        self.assertTrue(boundary["diagnostic_named_as_level_b_only"])


if __name__ == "__main__":
    unittest.main()

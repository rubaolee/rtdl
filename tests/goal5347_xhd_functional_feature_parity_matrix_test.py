import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5347_functional_feature_parity_matrix.json"
)


class Goal5347XhdFunctionalFeatureParityMatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.features = {
            row["author_feature"]: row
            for row in cls.summary["feature_groups"]
        }

    def test_matrix_refuses_full_parity_claims(self):
        self.assertEqual(
            self.summary["schema"],
            "rtdl.paper_reproduction.xhd.goal5347.functional_feature_parity_matrix.v1",
        )
        self.assertFalse(self.summary["interpretation"]["full_functional_parity_ready"])
        boundary = self.summary["claim_boundary"]
        self.assertFalse(boundary["full_functional_parity_claimed"])
        self.assertFalse(boundary["full_paper_reproduction_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])

    def test_exact_input_and_witness_gaps_are_blocking(self):
        input_feature = self.features["Author paper input loading and preprocessing"]
        self.assertTrue(input_feature["blocking_for_same_functionality"])
        self.assertEqual(input_feature["same_functionality_status"], "blocking_gap")
        self.assertIn("Exact paper input", input_feature["gap"])

        witness_feature = self.features["Exact per-source nearest witness output"]
        self.assertTrue(witness_feature["blocking_for_same_functionality"])
        self.assertEqual(witness_feature["same_functionality_status"], "blocking_gap_for_full_witness_equivalence")
        self.assertIn("Fast scalar route", witness_feature["gap"])

    def test_core_algorithm_features_are_classified_without_overclaim(self):
        directed = self.features["Directed Hausdorff input1-to-input2 semantics"]
        self.assertEqual(directed["same_functionality_status"], "covered_for_directed_scalar")

        grid = self.features["Uniform grid organization of target points"]
        self.assertEqual(grid["same_functionality_status"], "partial")

        pruning = self.features["HD estimator / pruning of non-contributing sources"]
        self.assertEqual(pruning["same_functionality_status"], "partial_value_only")
        self.assertIn("per-source witnesses", pruning["gap"])

        offload = self.features["Load-balance / heavy-cell offload to CUDA"]
        self.assertEqual(offload["same_functionality_status"], "blocking_gap_for_full_load_balance_equivalence")
        self.assertIn("shape", offload["rtdl_status"])

    def test_all_paper_figures_remain_unreproduced_or_partial(self):
        for figure in ["Figure 5", "Figure 6", "Figure 7", "Figure 8", "Figure 9", "Figure 10", "Figure 11"]:
            row = next(
                feature
                for feature in self.summary["feature_groups"]
                if feature["author_feature"].startswith(figure)
            )
            self.assertTrue(row["blocking_for_same_functionality"], row["author_feature"])
            self.assertIn("blocking_gap", row["same_functionality_status"], row["author_feature"])

    def test_performance_ratios_are_blocked(self):
        perf = self.features["Performance evaluation with aligned denominators"]
        self.assertTrue(perf["blocking_for_same_functionality"])
        self.assertEqual(perf["same_functionality_status"], "blocking_gap_for_full_performance")
        self.assertIn("Performance ratios remain unauthorized", perf["gap"])
        self.assertIn("full paper workload matrix coverage", self.summary["interpretation"]["main_blockers"])


if __name__ == "__main__":
    unittest.main()

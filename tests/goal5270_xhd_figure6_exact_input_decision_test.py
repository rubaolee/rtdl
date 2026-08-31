import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5270_figure6_exact_input_availability_decision_2026-07-09.json"
)


class Goal5270Figure6ExactInputDecisionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_exact_author_graphics_inputs_are_unavailable_on_current_pod(self):
        probe = self.data["pod_probe"]
        self.assertEqual(probe["preflight"], "POD_OK")
        self.assertFalse(probe["exact_dataset_roots"]["/local/storage/shared/HDDatasets"])
        self.assertFalse(
            probe["required_exact_paths"][
                "/local/storage/shared/HDDatasets/graphics/dragon.ply"
            ]
        )
        self.assertFalse(
            probe["required_exact_paths"][
                "/local/storage/shared/HDDatasets/graphics/asian_dragon.ply"
            ]
        )
        self.assertTrue(
            probe["available_candidate_paths"]["/tmp/xhd_goal5234/data/dragon.ply"]
        )
        self.assertTrue(
            probe["available_candidate_paths"][
                "/tmp/xhd_goal5234/data/asian_dragon_scaled_1e-3.ply"
            ]
        )

    def test_figure6_claims_remain_closed(self):
        boundary = self.data["claim_boundary"]
        for key in [
            "figure6_reproduced",
            "full_paper_reproduction_claimed",
            "exact_paper_dataset_identity_claimed",
            "author_rt_core_equivalence_claimed",
            "performance_ratio_claimed",
            "lb2048_substitute_authorized_as_figure6",
            "level_b_diagnostic_is_paper_figure",
        ]:
            self.assertFalse(boundary[key], key)

    def test_level_b_diagnostic_is_allowed_but_not_paper_figure(self):
        decision = self.data["decision"]
        self.assertEqual(decision["figure6_reproduction_status"], "not_reproduced")
        self.assertTrue(decision["exact_input_blocker"])
        self.assertTrue(decision["level_b_pruning_diagnostic_allowed"])
        self.assertTrue(decision["level_b_pruning_diagnostic_must_be_named_separately"])
        self.assertFalse(decision["lb2048_substitute_authorized_as_figure6"])

    def test_author_contract_still_requires_lb256_exact_paths(self):
        contract = self.data["author_figure6_contract"]
        self.assertEqual(
            contract["dataset1"], "/local/storage/shared/HDDatasets/graphics/dragon.ply"
        )
        self.assertEqual(
            contract["dataset2"],
            "/local/storage/shared/HDDatasets/graphics/asian_dragon.ply",
        )
        self.assertEqual(contract["paper_log_lb256"]["input_point_counts"], [437645, 3609600])
        variants = {row["label"]: row for row in contract["figure6_variants"]}
        self.assertEqual(variants["XHD"]["lb"], 256)
        self.assertTrue(variants["XHD"]["eb"])
        self.assertTrue(variants["XHD"]["prune"])

    def test_goal5269_lb_scan_is_carried_forward(self):
        evidence = self.data["current_level_b_candidate_evidence"]
        self.assertTrue(evidence["point_counts_match_paper_log"])
        self.assertTrue(evidence["mbrs_differ_from_paper_log"])
        summary = evidence["goal5269_summary"]
        self.assertEqual(summary["lb256_check_true_status"], "aborts_with_wrong_hausdorff_distance")
        self.assertTrue(summary["lb2048_check_true_passes"])
        self.assertFalse(summary["lb2048_is_figure6_substitute"])


if __name__ == "__main__":
    unittest.main()

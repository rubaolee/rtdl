import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5295_figures7_8_10_pod_dataset_availability_2026-07-09.json"
)


class Goal5295XhdFiguresPodDatasetAvailabilityTest(unittest.TestCase):
    def test_current_pod_lacks_exact_hddatasets_for_figures7_8_10(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(
            payload["status"],
            "pod_dataset_availability_checked__exact_hddatasets_missing__figures7_8_10_regeneration_blocked",
        )
        self.assertEqual(payload["pod"]["wrapper_preflight"], "POD_OK")
        self.assertFalse(payload["author_environment"]["dataset_root_exists"])
        self.assertFalse(payload["author_environment"]["shared_root_exists"])

        self.assertFalse(
            payload["figure7_load_balance_required_paths"][
                "complete_for_author_regeneration_on_current_pod"
            ]
        )
        self.assertFalse(
            payload["figure8_radius_strategy_required_paths"][
                "complete_for_author_regeneration_on_current_pod"
            ]
        )
        self.assertFalse(
            payload["figure10_scalability_required_paths"][
                "complete_for_author_regeneration_on_current_pod"
            ]
        )

        for section in (
            "figure7_load_balance_required_paths",
            "figure8_radius_strategy_required_paths",
            "figure10_scalability_required_paths",
        ):
            self.assertTrue(payload[section]["required_files"])
            self.assertFalse(any(payload[section]["required_files"].values()))

    def test_partial_tmp_inputs_are_not_promoted_to_paper_inputs(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        tmp_inputs = payload["partial_tmp_inputs_on_current_pod"]

        self.assertTrue(tmp_inputs["/tmp/xhd_goal5234/data/dragon.ply"])
        self.assertTrue(tmp_inputs["/tmp/xhd_goal5234/data/asian_dragon.ply"])
        self.assertTrue(tmp_inputs["/tmp/xhd_goal5234/data/asian_dragon_scaled_1e-3.ply"])
        self.assertFalse(tmp_inputs["/tmp/xhd_goal5234/data/thai_statuette.ply"])
        self.assertFalse(tmp_inputs["/tmp/xhd_goal5234/data/happy_buddha.ply"])
        self.assertIn("partial Dragon/Asian", tmp_inputs["interpretation"])

        boundary = payload["claim_boundary"]
        self.assertFalse(boundary["partial_tmp_inputs_claimed_as_paper_inputs"])
        self.assertFalse(boundary["author_matrix_regenerated"])

    def test_decision_blocks_rtdl_comparison_until_author_matrix_exists(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        decision = payload["decision"]

        self.assertFalse(decision["figures7_8_10_exact_author_regeneration_possible_on_current_pod"])
        self.assertFalse(decision["figure7_reproduced"])
        self.assertFalse(decision["figure8_reproduced"])
        self.assertFalse(decision["figure10_reproduced"])
        self.assertIn("/local/storage/shared/HDDatasets", decision["current_blocker"])

        steps = "\n".join(decision["next_allowed_steps"])
        self.assertIn("Mount or recover /local/storage/shared/HDDatasets", steps)
        self.assertIn("separately named Level-B diagnostics", steps)
        self.assertIn("Do not spend RTDL comparison work", steps)


if __name__ == "__main__":
    unittest.main()

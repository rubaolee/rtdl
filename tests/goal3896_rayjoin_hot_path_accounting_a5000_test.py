from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3896_rayjoin_hot_path_accounting_a5000"
SUMMARY = ARTIFACT_DIR / "summary.json"
EXIT_CODE = ARTIFACT_DIR / "exit_code"
REPORT = ROOT / "docs" / "reports" / "goal3896_rayjoin_hot_path_accounting_2026-06-08.md"


class Goal3896RayJoinHotPathAccountingA5000Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.hot = cls.summary["representative_hot_path_summary"]

    def test_clean_a5000_artifact_records_hot_path_summary(self) -> None:
        self.assertEqual(EXIT_CODE.read_text(encoding="utf-8").strip(), "0")
        self.assertEqual(self.summary["git_commit"][:8], "23723c6e")
        self.assertEqual(self.summary["git_status_short"], "")
        self.assertIn("NVIDIA RTX A5000", self.summary["gpu"])
        self.assertTrue(self.summary["all_counts_match"])
        self.assertGreater(self.summary["wrapper_elapsed_sec"], 1.0)
        self.assertEqual(
            self.hot["metric_scope"],
            "per_contract_hot_medians_not_wrapper_wall_time",
        )
        self.assertTrue(self.hot["scale_runner_elapsed_sec_is_not_hot_path_metric"])
        self.assertEqual(self.hot["contract_count"], 4)

    def test_rayjoin_routes_are_explicit_and_match_current_evidence(self) -> None:
        pip = self.hot["pip_one_shot"]
        self.assertEqual(
            pip["recommended_route"],
            "numba_cuda_jit_scalar_count_no_rawkernel",
        )
        self.assertLess(pip["rtdl_optix_speedup_vs_numba"], 1.0)

        pip_batch = self.hot["pip_repeated_requests"]
        self.assertEqual(
            pip_batch["recommended_route"],
            "rtdl_optix_prepared_batch_executor",
        )
        self.assertEqual(pip_batch["batch_request_count"], 100)
        self.assertGreater(pip_batch["per_request_speedup_vs_single_request"], 5.0)

        lsi = self.hot["lsi_scalar_count"]
        self.assertEqual(lsi["recommended_route"], "rtdl_optix_prepared_segment_pair_count")
        self.assertGreater(lsi["rtdl_optix_speedup_vs_numba"], 100.0)

        overlay = self.hot["overlay_active_count"]
        self.assertEqual(
            overlay["recommended_route"],
            "rtdl_optix_prepared_shape_pair_active_count",
        )
        self.assertGreater(overlay["rtdl_optix_speedup_vs_numba"], 100.0)

    def test_claim_flags_stay_closed_in_hot_path_summary_and_report(self) -> None:
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
            "true_zero_copy_claim_authorized",
            "automatic_partner_selection_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            with self.subTest(flag=flag):
                self.assertFalse(self.hot[flag])

        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3896",
            "scale-runner elapsed is not the hot-path metric",
            "does not authorize release action",
            "not automatic dispatch",
            "not a single 10-second row",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

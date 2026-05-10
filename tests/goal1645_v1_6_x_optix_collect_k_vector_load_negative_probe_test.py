import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
REPORT = ROOT / "docs" / "reports" / "goal1645_v1_6_x_optix_collect_k_vector_load_negative_probe_2026-05-09.md"
BASELINE = ROOT / "docs" / "reports" / "goal1645_ab_baseline_262144_repeats9.json"
CANDIDATE = ROOT / "docs" / "reports" / "goal1645_ab_vector_load_262144_repeats9.json"


class Goal1645OptixCollectKVectorLoadNegativeProbeTest(unittest.TestCase):
    def test_rejected_vector_load_helper_is_not_retained(self) -> None:
        text = CORE.read_text(encoding="utf-8")

        self.assertNotIn("CollectKFinalRow2", text)
        self.assertNotIn("collect_k_final_load_row2", text)

    def test_artifacts_show_parity_preserved_but_performance_regressed(self) -> None:
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))["cases"][0]
        candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))["cases"][0]

        self.assertTrue(candidate["same_candidate_rows"])
        self.assertTrue(candidate["same_valid_count"])
        self.assertTrue(candidate["same_overflowed_flag"])
        self.assertGreater(candidate["median_ms"], baseline["median_ms"])
        self.assertGreater(
            candidate["stage_profile"]["stage_median_ms"]["total_ms"],
            baseline["stage_profile"]["stage_median_ms"]["total_ms"],
        )

    def test_report_records_rejection_and_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("`vector_load_candidate_rejected`", text)
        self.assertIn("Wrapper median speedup: `0.926064x`", text)
        self.assertIn("candidate code is not retained", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()

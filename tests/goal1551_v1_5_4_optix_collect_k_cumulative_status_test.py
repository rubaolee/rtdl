from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1551_v1_5_4_optix_collect_k_cumulative_status_2026-05-08.md"
CURRENT_JSON = ROOT / "docs" / "reports" / "goal1551_v1_5_4_optix_collect_k_cumulative_current_probe_2026-05-08.json"
BASELINE_JSON = ROOT / "docs" / "reports" / "goal1545_v1_5_4_optix_collect_k_device_prefix_compact_candidate_probe_2026-05-08.json"


class Goal1551V154OptixCollectKCumulativeStatusTest(unittest.TestCase):
    def test_current_clean_commit_improves_goal1545_baseline(self) -> None:
        baseline = {
            case["candidate_count"]: case
            for case in json.loads(BASELINE_JSON.read_text(encoding="utf-8"))["cases"]
        }
        current_data = json.loads(CURRENT_JSON.read_text(encoding="utf-8"))
        current = {
            case["candidate_count"]: case
            for case in current_data["cases"]
        }

        self.assertIs(current_data["accepted_goal1506_evidence"], True)
        self.assertEqual(current_data["git_commit"], "1d11185542f93712029368ee477d09e22e579ae9")
        for count in (4097, 65537, 131072):
            with self.subTest(candidate_count=count):
                case = current[count]
                self.assertTrue(case["same_candidate_rows"])
                self.assertTrue(case["same_valid_count"])
                self.assertTrue(case["same_overflowed_flag"])
                self.assertTrue(case["profile_topology_matches_expected"])
                self.assertLess(
                    case["stage_profile"]["stage_median_ms"]["total_ms"],
                    baseline[count]["stage_profile"]["stage_median_ms"]["total_ms"],
                )

        self.assertLess(current[131072]["stage_profile"]["stage_median_ms"]["total_ms"], 0.32)

    def test_report_names_bottleneck_and_claim_boundary(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        self.assertIn("1.540x", text)
        self.assertIn("remaining high-order bottleneck is the multi-kernel merge pipeline", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()

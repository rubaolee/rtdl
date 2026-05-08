from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1545_v1_5_4_optix_collect_k_device_prefix_compact_intake_2026-05-08.md"
CONTROL_JSON = ROOT / "docs" / "reports" / "goal1545_v1_5_4_optix_collect_k_device_prefix_compact_control_goal1543_probe_2026-05-08.json"
CANDIDATE_JSON = ROOT / "docs" / "reports" / "goal1545_v1_5_4_optix_collect_k_device_prefix_compact_candidate_probe_2026-05-08.json"
SUMMARY_JSON = ROOT / "docs" / "reports" / "goal1545_v1_5_4_optix_collect_k_device_prefix_compact_confirm_summary_2026-05-08.json"


class Goal1545V154OptixCollectKDevicePrefixCompactIntakeTest(unittest.TestCase):
    def test_candidate_probe_is_clean_pod_evidence(self) -> None:
        data = json.loads(CANDIDATE_JSON.read_text(encoding="utf-8"))

        self.assertIs(data["accepted_goal1506_evidence"], True)
        self.assertIs(data["local_fallback_smoke_only"], False)
        self.assertEqual(data["git_commit"], "2a2000c30875b9221f607eda280f6c47bae9987c")
        self.assertEqual(data["device_name"], "NVIDIA RTX 4000 Ada Generation")
        for case in data["cases"]:
            with self.subTest(candidate_count=case["candidate_count"]):
                self.assertTrue(case["same_candidate_rows"])
                self.assertTrue(case["same_valid_count"])
                self.assertTrue(case["same_overflowed_flag"])
                self.assertTrue(case["profile_topology_matches_expected"])

    def test_device_prefix_improves_long_counts_only(self) -> None:
        control = {
            case["candidate_count"]: case
            for case in json.loads(CONTROL_JSON.read_text(encoding="utf-8"))["cases"]
        }
        candidate = {
            case["candidate_count"]: case
            for case in json.loads(CANDIDATE_JSON.read_text(encoding="utf-8"))["cases"]
        }

        for count in (65537, 131072):
            with self.subTest(candidate_count=count):
                old_stage = control[count]["stage_profile"]["stage_median_ms"]
                new_stage = candidate[count]["stage_profile"]["stage_median_ms"]
                old_topology = control[count]["stage_profile"]["topology"]
                new_topology = candidate[count]["stage_profile"]["topology"]

                self.assertLess(new_stage["total_ms"], old_stage["total_ms"])
                self.assertLess(new_stage["merge_launch_ms"], old_stage["merge_launch_ms"])
                self.assertGreater(new_topology["merge_launches"], old_topology["merge_launches"])

        self.assertGreater(
            candidate[4097]["stage_profile"]["stage_median_ms"]["total_ms"],
            control[4097]["stage_profile"]["stage_median_ms"]["total_ms"],
        )

    def test_runner_summary_and_report_bound_claim(self) -> None:
        summary = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        self.assertIs(summary["accepted_candidate_by_runner_rule"], True)
        self.assertIn("smallest target case", text)
        self.assertIn("compatibility library path was required", text)
        self.assertIn("not unordered atomics", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()

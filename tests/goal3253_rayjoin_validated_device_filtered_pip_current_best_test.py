from __future__ import annotations

import json
import statistics
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3253_rayjoin_validated_device_filtered_pip_current_best_2026-06-03.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3253_rayjoin_current_best_device_filtered_pip_pod_2026-06-03.json"
STDOUT = ROOT / "docs" / "reports" / "goal3253_rayjoin_current_best_device_filtered_pip_pod_2026-06-03.stdout"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "rtdl_rayjoin_v2_spatial_join_app.py"
RUNNER = ROOT / "scripts" / "goal3244_rayjoin_same_slice_repeated_count_runner.py"


class Goal3253RayJoinValidatedDeviceFilteredPipCurrentBestTest(unittest.TestCase):
    def test_report_records_current_best_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "RayJoin Validated Device-Filtered PIP Current Best",
            "count_mode = device_filtered_validated",
            "0.808567 ms",
            "4.03x",
            "1.16x",
            "0.992673 ms",
            "does not authorize release",
            "RayJoin is still faster",
        ):
            self.assertIn(phrase, text)

    def test_app_and_runner_expose_explicit_fail_closed_mode(self) -> None:
        app = APP.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn('_PIP_COUNT_MODES = ("exact", "device_filtered_validated")', app)
        self.assertIn("count_device_filtered(packed_points)", app)
        self.assertIn("validation_exact_query_sec", app)
        self.assertIn("did not match exact prepared count", app)
        self.assertIn("device_filtered_validated count_mode is only valid for PIP count workloads", app)

        self.assertIn("--rtdl-pip-count-mode", runner)
        self.assertIn("validation_exact_query_ms", runner)
        self.assertIn("device-filtered count was not validated against exact count", runner)

    def test_pod_artifact_is_clean_claim_bounded_and_uses_validated_fast_lane(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["rtdl_commit"], "995394aeb21c0bbbb05b09a44709f4b20608d160")
        self.assertEqual(data["source_dirty"], [])
        self.assertTrue(all(value is False for value in data["claim_boundary"].values()))

        pip = data["rtdl"]["pip"]
        self.assertEqual(pip["count_mode"], "device_filtered_validated")
        self.assertEqual(pip["counts"]["samples"], [1430] * 7)
        self.assertGreater(pip["validation_exact_query_ms"]["median"], pip["prepared_query_ms"]["median"])
        self.assertAlmostEqual(pip["prepared_query_ms"]["median"], 0.8085668087005615)
        self.assertAlmostEqual(pip["validation_exact_query_ms"]["median"], 0.9926725178956985)

        phase_samples = pip["native_phase_samples"]
        self.assertTrue(all(sample["mode"] == "device_filtered_count" for sample in phase_samples))
        self.assertTrue(all(sample["candidate_write_pass"] == 0.0 for sample in phase_samples))
        self.assertTrue(all(sample["candidate_download"] == 0.0 for sample in phase_samples))
        self.assertTrue(all(sample["exact_refine"] == 0.0 for sample in phase_samples))
        self.assertEqual([sample["raw_candidate_count"] for sample in phase_samples], [1430] * 7)
        self.assertGreater(statistics.median(sample["candidate_count_pass"] for sample in phase_samples), 0.0007)

    def test_comparison_rows_keep_rayjoin_gap_honest(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        rows = {row["workload"]: row for row in data["comparisons"]}

        self.assertEqual(rows["lsi"]["count_contract_status"], "matching_visible_lsi_count")
        self.assertEqual(rows["lsi"]["rayjoin_visible_count"], 269)
        self.assertEqual(rows["lsi"]["rtdl_count"], 269)
        self.assertGreater(rows["lsi"]["rtdl_over_rayjoin_query_ratio"], 2.0)

        self.assertEqual(rows["pip"]["count_contract_status"], "rayjoin_pip_count_not_visible")
        self.assertFalse(rows["pip"]["rayjoin_positive_assignment_count_available"])
        self.assertEqual(rows["pip"]["rtdl_count"], 1430)
        self.assertGreater(rows["pip"]["rtdl_over_rayjoin_query_ratio"], 4.0)

    def test_stdout_records_progress_and_clean_rerun(self) -> None:
        stdout = STDOUT.read_text(encoding="utf-8")

        self.assertIn("[goal3244] RayJoin lsi process 1/5", stdout)
        self.assertIn("[goal3244] RayJoin pip process 5/5", stdout)
        self.assertIn("[goal3244] RTDL pip repeat 7/7", stdout)
        self.assertIn('"count_mode": "device_filtered_validated"', stdout)
        self.assertIn('"source_dirty": []', stdout)
        self.assertIn('"status": "pass_with_optimization_gap"', stdout)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
REPORT = ROOT / "docs" / "reports" / "goal3294_tuned_rayjoin_count_route_same_slice_2026-06-04.md"
TUNED = ROOT / "docs" / "reports" / "goal3294_rayjoin_same_slice_tuned_current_pod_2026-06-04.json"
PREVIOUS = ROOT / "docs" / "reports" / "goal3293_rayjoin_same_slice_current_pod_2026-06-04.json"


class Goal3294TunedRayJoinCountRouteSameSliceTest(unittest.TestCase):
    def test_report_records_tuned_routes_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("left_id_dense_count", text)
        self.assertIn("device_filtered_validated", text)
        self.assertIn("z_point", text)
        self.assertIn("pass_with_optimization_gap", text)
        self.assertIn("1.41x", text)
        self.assertIn("1.61x", text)
        self.assertIn("does not authorize", text)
        self.assertIn("generic prepared closed-shape count route", text)

    def test_tuned_artifact_improves_gap_without_claim_leak(self) -> None:
        tuned = json.loads(TUNED.read_text(encoding="utf-8"))
        previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
        tuned_rows = {row["workload"]: row for row in tuned["comparisons"]}
        previous_rows = {row["workload"]: row for row in previous["comparisons"]}

        self.assertEqual(tuned["status"], "pass_with_optimization_gap")
        self.assertEqual(tuned["rtdl_commit"], "60009b58d8ad7616be7c666d664443da8cdd2cb2")
        self.assertIn("RTX A5000", tuned["gpu"])

        self.assertEqual(tuned["rtdl"]["lsi"]["lsi_count_route"], "left_id_dense_count")
        self.assertEqual(tuned_rows["lsi"]["count_contract_status"], "matching_visible_lsi_count")
        self.assertEqual(tuned_rows["lsi"]["rayjoin_visible_count"], 269)
        self.assertEqual(tuned_rows["lsi"]["rtdl_count"], 269)

        self.assertEqual(tuned["rtdl"]["pip"]["count_mode"], "device_filtered_validated")
        self.assertEqual(tuned["rtdl"]["pip"]["device_filtered_boundary_mode"], "inclusive")
        self.assertEqual(tuned["rtdl"]["pip"]["query_axis"], "z_point")
        self.assertTrue(tuned["rtdl"]["pip"]["pip_scalar_count_pipeline"])
        self.assertEqual(tuned_rows["pip"]["count_contract_status"], "rayjoin_pip_count_not_visible")

        self.assertLess(
            tuned_rows["lsi"]["rtdl_over_rayjoin_query_ratio"],
            previous_rows["lsi"]["rtdl_over_rayjoin_query_ratio"],
        )
        self.assertLess(
            tuned_rows["pip"]["rtdl_over_rayjoin_query_ratio"],
            previous_rows["pip"]["rtdl_over_rayjoin_query_ratio"],
        )
        self.assertGreater(tuned_rows["lsi"]["rtdl_over_rayjoin_query_ratio"], 1.0)
        self.assertGreater(tuned_rows["pip"]["rtdl_over_rayjoin_query_ratio"], 1.0)

        pip_native = tuned["rtdl"]["pip"]["native_phase_samples"][-1]
        self.assertEqual(pip_native["mode"], "device_filtered_count")
        self.assertEqual(pip_native["candidate_write_pass"], 0.0)
        self.assertEqual(pip_native["candidate_download"], 0.0)
        self.assertEqual(pip_native["exact_refine"], 0.0)

        for value in tuned["claim_boundary"].values():
            self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()

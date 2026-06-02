from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal3040_hausdorff_device_columns_numba_argmax_a4000_perf_2026-06-02.md"
ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal3040_hausdorff_device_columns_numba_argmax_a4000_perf_2026-06-02.json"


class Goal3040HausdorffDeviceColumnsNumbaArgmaxA4000PerfTest(unittest.TestCase):
    def _artifact(self) -> dict[str, object]:
        return json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_report_records_negative_perf_result_without_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3040",
            "NVIDIA RTX A4000, driver 580.159.03",
            "All rows matched",
            "536.328x slower",
            "153.308x slower",
            "75.961x slower",
            "negative but useful performance result",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

    def test_artifact_records_clean_source_and_boundaries(self) -> None:
        data = self._artifact()

        self.assertEqual(data["source_commit"], "1b455947a4d58ea371b2821779a0ca63648b49fd")
        self.assertEqual(data["source_dirty"], [])
        self.assertEqual(data["gpu"], "NVIDIA RTX A4000, 580.159.03")
        self.assertFalse(data["v2_6_release_authorized"])
        self.assertFalse(data["public_speedup_claim_authorized"])
        self.assertFalse(data["rt_core_speedup_claim_authorized"])
        self.assertFalse(data["true_zero_copy_claim_authorized"])

    def test_device_column_strategy_matches_value_but_loses_timing(self) -> None:
        data = self._artifact()
        method = "rtdl_rt_grouped_device_columns_numba_argmax_nearest_witness"
        reference = "cupy_grouped_grid_rawkernel"

        self.assertEqual(data["sizes"], [2048, 4096, 8192])
        for row in data["rows"]:
            results = row["results"]
            self.assertTrue(results[method]["matches_cupy_grouped_grid_distance"])
            self.assertGreater(results[method]["elapsed_sec"], results[reference]["elapsed_sec"])
            self.assertGreater(results[method]["ratio_vs_cupy_grouped_grid"], 1.0)

    def test_roadmap_indexes_perf_result_as_non_speedup(self) -> None:
        roadmap = rt.v2_6_roadmap()
        validation = rt.validate_v2_6_roadmap(repo_root=REPO_ROOT)

        self.assertEqual(roadmap["hausdorff_device_columns_numba_argmax_perf_goal"], "Goal3040")
        self.assertIn("negative_perf_result", roadmap["hausdorff_device_columns_numba_argmax_perf_status"])
        self.assertFalse(roadmap["public_speedup_claim_authorized"])
        self.assertEqual(validation["status"], "accept")


if __name__ == "__main__":
    unittest.main()

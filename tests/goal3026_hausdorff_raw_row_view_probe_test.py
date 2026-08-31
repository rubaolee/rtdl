from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal3026_hausdorff_raw_row_view_probe_2026-06-02.md"
ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal3026_hausdorff_raw_row_view_probe_2026-06-02.json"


class Goal3026HausdorffRawRowViewProbeTest(unittest.TestCase):
    def test_report_records_raw_view_improvement_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3026",
            "generic `OptixRowView`",
            "No native Hausdorff-specific ABI or kernel was added",
            "0.7013094132253148x",
            "`14.280106063192658x` slower than CuPy grouped-grid",
            "preferred current exact RTDL/OptiX adaptive Hausdorff method",
            "device-resident active-set compaction",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

    def test_artifact_records_clean_source_and_same_contract_rows(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["goal"], "Goal3026")
        self.assertEqual(data["source_commit"], "38b2d88ece9e9eedf0efe19624dec2f710a8ae64")
        self.assertEqual(data["source_dirty"], [])
        self.assertEqual(data["gpu"], "NVIDIA L4, 565.57.01")
        self.assertEqual(data["cuda_prefix"], "/usr/local/cuda-12.6")
        self.assertEqual(data["warmup"], 1)
        self.assertEqual(data["repeats"], 3)
        self.assertTrue(data["promote_raw_row_view_path"])
        self.assertAlmostEqual(data["ratios"]["raw_vs_old_ratio_512"], 0.8437807531279325)
        self.assertAlmostEqual(data["ratios"]["raw_vs_old_ratio_4096"], 0.7013094132253148)
        self.assertGreater(data["ratios"]["raw_vs_cupy_ratio_4096"], 10.0)

        rows = data["rows"]
        self.assertEqual(len(rows), 6)
        by_key = {(row["points"], row["method"]): row for row in rows}
        old_4096 = by_key[(4096, "rtdl_rt_grouped_adaptive_nearest_witness")]
        raw_4096 = by_key[(4096, "rtdl_rt_grouped_adaptive_raw_nearest_witness")]
        cupy_4096 = by_key[(4096, "cupy_grouped_grid_rawkernel")]
        self.assertTrue(old_4096["rt_core_accelerated"])
        self.assertTrue(raw_4096["rt_core_accelerated"])
        self.assertFalse(cupy_4096["rt_core_accelerated"])
        self.assertAlmostEqual(raw_4096["distance"], old_4096["distance"])
        self.assertEqual(raw_4096["source_index"], old_4096["source_index"])
        self.assertEqual(raw_4096["target_index"], old_4096["target_index"])
        self.assertLess(raw_4096["median_elapsed_sec"], old_4096["median_elapsed_sec"])
        self.assertGreater(raw_4096["median_elapsed_sec"], cupy_4096["median_elapsed_sec"])

        for field in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "app_specific_native_engine_logic_authorized",
        ):
            self.assertFalse(data[field])

    def test_v2_6_roadmap_indexes_goal3026_probe(self) -> None:
        roadmap = rt.v2_6_roadmap()
        self.assertEqual(roadmap["hausdorff_raw_row_view_probe_goal"], "Goal3026")
        self.assertIn("raw_row_view_faster_than_old_adaptive_rt", roadmap["hausdorff_raw_row_view_probe_status"])
        self.assertIn("still_slower_than_cupy", roadmap["hausdorff_raw_row_view_probe_status"])
        validation = rt.validate_v2_6_roadmap(repo_root=REPO_ROOT)
        self.assertEqual("accept", validation["status"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal3028_hausdorff_raw_row_view_larger_scale_probe_2026-06-02.md"
ARTIFACTS = (
    REPO_ROOT / "docs" / "reports" / "goal3028_hausdorff_raw_row_view_larger_scale_probe_2026-06-02.json",
    REPO_ROOT / "docs" / "reports" / "goal3028_hausdorff_raw_row_view_32768_probe_2026-06-02.json",
    REPO_ROOT / "docs" / "reports" / "goal3028_hausdorff_raw_row_view_65536_probe_2026-06-02.json",
)


class Goal3028HausdorffRawRowViewLargerScaleProbeTest(unittest.TestCase):
    def _rows_by_point(self) -> dict[int, dict[str, dict[str, object]]]:
        by_point: dict[int, dict[str, dict[str, object]]] = {}
        for artifact in ARTIFACTS:
            data = json.loads(artifact.read_text(encoding="utf-8"))
            self.assertEqual(data["source_dirty"], [])
            self.assertEqual(data["gpu"], "NVIDIA L4, 565.57.01")
            self.assertEqual(data["cuda_prefix"], "/usr/local/cuda-12.6")
            self.assertEqual(data["warmup"], 1)
            self.assertEqual(data["repeats"], 3)
            self.assertTrue(data["promote_raw_row_view_path"])
            for field in (
                "release_authorized",
                "public_speedup_claim_authorized",
                "rt_core_speedup_claim_authorized",
                "whole_app_speedup_claim_authorized",
                "true_zero_copy_claim_authorized",
                "app_specific_native_engine_logic_authorized",
            ):
                self.assertFalse(data[field])
            for row in data["rows"]:
                by_point.setdefault(int(row["points"]), {})[str(row["method"])] = row
        return by_point

    def test_report_records_larger_scale_curve_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3028",
            "No native Hausdorff-specific ABI or kernel was added",
            "0.8209693399485448x",
            "4.743426599986384x",
            "no crossover appears",
            "generic device-resident active-set",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

    def test_artifacts_show_raw_rt_beats_old_rt_but_not_cupy(self) -> None:
        by_point = self._rows_by_point()
        self.assertEqual(set(by_point), {8192, 16384, 32768, 65536})
        previous_raw_vs_cupy = None
        for point_count in (8192, 16384, 32768, 65536):
            rows = by_point[point_count]
            old = rows["rtdl_rt_grouped_adaptive_nearest_witness"]
            raw = rows["rtdl_rt_grouped_adaptive_raw_nearest_witness"]
            cupy = rows["cupy_grouped_grid_rawkernel"]
            self.assertTrue(old["rt_core_accelerated"])
            self.assertTrue(raw["rt_core_accelerated"])
            self.assertFalse(cupy["rt_core_accelerated"])
            self.assertAlmostEqual(raw["distance"], old["distance"])
            self.assertAlmostEqual(raw["distance"], cupy["distance"])
            self.assertEqual(raw["source_index"], old["source_index"])
            self.assertEqual(raw["target_index"], old["target_index"])
            raw_vs_old = float(raw["median_elapsed_sec"]) / float(old["median_elapsed_sec"])
            raw_vs_cupy = float(raw["median_elapsed_sec"]) / float(cupy["median_elapsed_sec"])
            self.assertLess(raw_vs_old, 1.0)
            self.assertGreater(raw_vs_cupy, 1.0)
            if previous_raw_vs_cupy is not None:
                self.assertLess(raw_vs_cupy, previous_raw_vs_cupy)
            previous_raw_vs_cupy = raw_vs_cupy

    def test_v2_6_roadmap_indexes_goal3028_probe(self) -> None:
        roadmap = rt.v2_6_roadmap()
        self.assertEqual(roadmap["hausdorff_raw_row_view_larger_scale_goal"], "Goal3028")
        self.assertIn("gap_narrows_but_no_crossover", roadmap["hausdorff_raw_row_view_larger_scale_status"])
        validation = rt.validate_v2_6_roadmap(repo_root=REPO_ROOT)
        self.assertEqual("accept", validation["status"])


if __name__ == "__main__":
    unittest.main()

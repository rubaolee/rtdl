from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal3031_hausdorff_vectorized_row_view_l4_pod_2026-06-02.md"
ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal3031_hausdorff_vectorized_row_view_l4_pod_2026-06-02.json"
README = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "hausdorff_xhd" / "README.md"


class Goal3031HausdorffVectorizedRowViewL4PodTest(unittest.TestCase):
    def _artifact(self) -> dict[str, object]:
        return json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_report_records_vectorized_row_view_scope_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3031",
            "structured NumPy view",
            "No native Hausdorff-specific ABI",
            "0.7806494678294922x",
            "0.7345100917854029x",
            "dense CuPy grouped-grid reference still wins",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

    def test_artifact_is_clean_source_and_claim_boundary_closed(self) -> None:
        data = self._artifact()

        self.assertEqual(data["source_commit"], "f1ac3efb4177c3bd7edf0044da2491645dcb43cb")
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

    def test_vectorized_raw_beats_old_rt_but_not_cupy(self) -> None:
        data = self._artifact()
        rows_by_point: dict[int, dict[str, dict[str, object]]] = {}
        for row in data["rows"]:
            rows_by_point.setdefault(int(row["points"]), {})[str(row["method"])] = row

        self.assertEqual(set(rows_by_point), {4096, 8192, 16384})
        for point_count in (4096, 8192, 16384):
            rows = rows_by_point[point_count]
            old = rows["rtdl_rt_grouped_adaptive_nearest_witness"]
            raw = rows["rtdl_rt_grouped_adaptive_raw_nearest_witness"]
            cupy = rows["cupy_grouped_grid_rawkernel"]
            self.assertTrue(old["rt_core_accelerated"])
            self.assertTrue(raw["rt_core_accelerated"])
            self.assertFalse(cupy["rt_core_accelerated"])
            self.assertAlmostEqual(float(raw["distance"]), float(old["distance"]))
            self.assertAlmostEqual(float(raw["distance"]), float(cupy["distance"]))
            self.assertEqual(raw["source_index"], old["source_index"])
            self.assertEqual(raw["target_index"], old["target_index"])
            self.assertLess(float(raw["median_elapsed_sec"]) / float(old["median_elapsed_sec"]), 1.0)
            self.assertGreater(float(raw["median_elapsed_sec"]) / float(cupy["median_elapsed_sec"]), 1.0)

    def test_roadmap_and_tutorial_index_goal3031(self) -> None:
        roadmap = rt.v2_6_roadmap()
        validation = rt.validate_v2_6_roadmap(repo_root=REPO_ROOT)
        readme = README.read_text(encoding="utf-8")

        self.assertEqual(roadmap["hausdorff_vectorized_row_view_goal"], "Goal3030")
        self.assertEqual(roadmap["hausdorff_vectorized_row_view_pod_goal"], "Goal3031")
        self.assertIn("still_slower_than_cupy", roadmap["hausdorff_vectorized_row_view_pod_status"])
        self.assertIn("vectorized host reducer", readme)
        self.assertEqual("accept", validation["status"])


if __name__ == "__main__":
    unittest.main()

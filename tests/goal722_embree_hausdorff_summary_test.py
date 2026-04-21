from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

import rtdsl as rt
from examples import rtdl_hausdorff_distance_app


ROOT = Path(__file__).resolve().parents[1]


class Goal722EmbreeHausdorffSummaryTest(unittest.TestCase):
    def test_native_sources_export_directed_hausdorff_summary(self):
        required = {
            "src/native/embree/rtdl_embree_prelude.h": [
                "RtdlDirectedHausdorffRow",
                "rtdl_embree_run_directed_hausdorff_2d",
            ],
            "src/native/embree/rtdl_embree_api.cpp": [
                "rtdl_embree_run_directed_hausdorff_2d",
                "KnnRowsQueryState state",
                "RtdlDirectedHausdorffRow best",
            ],
            "src/rtdsl/embree_runtime.py": [
                "_RtdlDirectedHausdorffRow",
                "directed_hausdorff_2d_embree",
                "rtdl_embree_run_directed_hausdorff_2d",
            ],
            "examples/rtdl_hausdorff_distance_app.py": [
                "embree_result_mode",
                "directed_summary",
                "directed_hausdorff_2d_embree",
            ],
        }
        for relative_path, needles in required.items():
            text = (ROOT / relative_path).read_text(encoding="utf-8")
            for needle in needles:
                self.assertIn(needle, text, relative_path)

    def test_embree_directed_summary_matches_row_path_and_oracle(self):
        try:
            rows_result = rtdl_hausdorff_distance_app.run_app("embree", copies=8)
            summary_result = rtdl_hausdorff_distance_app.run_app(
                "embree",
                copies=8,
                embree_result_mode="directed_summary",
            )
        except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
            self.skipTest(f"Embree backend unavailable in this environment: {exc}")

        self.assertTrue(summary_result["matches_oracle"])
        self.assertEqual(summary_result["hausdorff_distance"], rows_result["hausdorff_distance"])
        self.assertEqual(summary_result["witness_direction"], rows_result["witness_direction"])
        self.assertEqual(summary_result["directed_a_to_b"]["row_count"], 32)
        self.assertEqual(summary_result["directed_b_to_a"]["row_count"], 32)

    def test_direct_helper_rejects_empty_sets(self):
        try:
            with self.assertRaises(RuntimeError):
                rt.directed_hausdorff_2d_embree([], [])
        except (OSError, subprocess.CalledProcessError) as exc:
            self.skipTest(f"Embree backend unavailable in this environment: {exc}")


if __name__ == "__main__":
    unittest.main()

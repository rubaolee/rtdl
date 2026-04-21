from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal717EmbreePreparedFixedRadiusSummaryTest(unittest.TestCase):
    def test_native_sources_export_prepared_fixed_radius_count_threshold(self):
        required = {
            "src/native/embree/rtdl_embree_prelude.h": [
                "RtdlEmbreeFixedRadiusCountThreshold2D",
                "rtdl_embree_fixed_radius_count_threshold_2d_create",
                "rtdl_embree_fixed_radius_count_threshold_2d_run",
                "rtdl_embree_fixed_radius_count_threshold_2d_destroy",
            ],
            "src/native/embree/rtdl_embree_api.cpp": [
                "PreparedFixedRadiusCountThreshold2DImpl",
                "rtcCommitScene(holder.scene)",
                "rtdl_embree_fixed_radius_count_threshold_2d_run",
                "rtcPointQuery(impl->holder.scene",
            ],
            "src/native/embree/rtdl_embree_scene.cpp": [
                "FixedRadiusCountThresholdQueryState",
                "seen_neighbor_ids",
                "state->seen_neighbor_ids->insert(search_point.id)",
            ],
            "src/rtdsl/embree_runtime.py": [
                "PreparedEmbreeFixedRadiusCountThreshold2D",
                "prepare_embree_fixed_radius_count_threshold_2d",
                "rtdl_embree_fixed_radius_count_threshold_2d_create",
                "rtdl_embree_fixed_radius_count_threshold_2d_run",
                "rtdl_embree_fixed_radius_count_threshold_2d_destroy",
            ],
        }
        for relative_path, needles in required.items():
            text = (ROOT / relative_path).read_text(encoding="utf-8")
            for needle in needles:
                self.assertIn(needle, text, relative_path)

    def test_prepared_summary_matches_one_shot_and_reuses_handle(self):
        points = (
            {"id": 1, "x": 0.0, "y": 0.0},
            {"id": 2, "x": 0.1, "y": 0.0},
            {"id": 3, "x": 3.0, "y": 3.0},
            {"id": 4, "x": 3.2, "y": 3.0},
            {"id": 5, "x": 9.0, "y": 9.0},
        )
        try:
            expected = rt.fixed_radius_count_threshold_2d_embree(
                points,
                points,
                radius=0.25,
                threshold=2,
            )
            with rt.prepare_embree_fixed_radius_count_threshold_2d(points) as prepared:
                first = prepared.run(points, radius=0.25, threshold=2)
                second = prepared.run(points, radius=0.25, threshold=1)
        except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
            self.skipTest(f"Embree backend unavailable in this environment: {exc}")

        self.assertEqual(first, expected)
        self.assertEqual(
            second,
            rt.fixed_radius_count_threshold_2d_embree(points, points, radius=0.25, threshold=1),
        )
        self.assertEqual([row["query_id"] for row in first], [1, 2, 3, 4, 5])
        self.assertEqual([row["threshold_reached"] for row in first], [1, 1, 1, 1, 0])


if __name__ == "__main__":
    unittest.main()

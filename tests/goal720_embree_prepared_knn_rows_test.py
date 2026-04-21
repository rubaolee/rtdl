from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

import rtdsl as rt
from examples.rtdl_facility_knn_assignment import K
from examples.rtdl_facility_knn_assignment import facility_knn_assignment
from examples.rtdl_facility_knn_assignment import make_facility_knn_case


ROOT = Path(__file__).resolve().parents[1]


class Goal720EmbreePreparedKnnRowsTest(unittest.TestCase):
    def test_native_sources_export_prepared_knn_rows(self):
        required = {
            "src/native/embree/rtdl_embree_prelude.h": [
                "RtdlEmbreeKnnRows2D",
                "rtdl_embree_knn_rows_2d_create",
                "rtdl_embree_knn_rows_2d_run",
                "rtdl_embree_knn_rows_2d_destroy",
            ],
            "src/native/embree/rtdl_embree_api.cpp": [
                "PreparedKnnRows2DImpl",
                "rtcCommitScene(holder.scene)",
                "rtdl_embree_knn_rows_2d_run",
                "rtcPointQuery(impl->holder.scene",
            ],
            "src/rtdsl/embree_runtime.py": [
                "PreparedEmbreeKnnRows2D",
                "prepare_embree_knn_rows_2d",
                "rtdl_embree_knn_rows_2d_create",
                "rtdl_embree_knn_rows_2d_run",
                "rtdl_embree_knn_rows_2d_destroy",
            ],
        }
        for relative_path, needles in required.items():
            text = (ROOT / relative_path).read_text(encoding="utf-8")
            for needle in needles:
                self.assertIn(needle, text, relative_path)

    def test_prepared_knn_rows_matches_one_shot_and_reuses_handle(self):
        case = make_facility_knn_case(copies=3)
        try:
            expected = tuple(rt.run_embree(facility_knn_assignment, **case))
            with rt.prepare_embree_knn_rows_2d(case["depots"]) as prepared:
                first = prepared.run(case["customers"], k=K)
                second = prepared.run(case["customers"], k=1)
        except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
            self.skipTest(f"Embree backend unavailable in this environment: {exc}")

        self.assertEqual(first, expected)
        self.assertEqual(len(second), len(case["customers"]))
        self.assertTrue(all(row["neighbor_rank"] == 1 for row in second))
        self.assertEqual(
            [row["query_id"] for row in second],
            [point.id for point in case["customers"]],
        )


if __name__ == "__main__":
    unittest.main()

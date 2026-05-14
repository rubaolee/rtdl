from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2037_embree_cpu_partner_all_thread_runner.py"


class Goal2037EmbreeCpuPartnerAllThreadRunnerTest(unittest.TestCase):
    def test_runner_declares_all_thread_environment_and_boundaries(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for token in (
            "OMP_NUM_THREADS",
            "TBB_NUM_THREADS",
            "MKL_NUM_THREADS",
            "OPENBLAS_NUM_THREADS",
            "NUMEXPR_NUM_THREADS",
            "RTDL_EMBREE_THREADS",
            "true_host_zero_copy_for_every_row_authorized",
            "[goal2037-embree-cpu]",
        ):
            self.assertIn(token, text)

    def test_runner_has_full_app_surface_and_cpu_partner_classification(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for app in (
            "database_analytics",
            "graph_analytics",
            "service_coverage_gaps",
            "event_hotspot_screening",
            "facility_knn_assignment",
            "road_hazard_screening",
            "segment_polygon_hitcount",
            "segment_polygon_anyhit_rows",
            "polygon_pair_overlap_area_rows",
            "polygon_set_jaccard",
            "hausdorff_distance",
            "ann_candidate_search",
            "outlier_detection",
            "dbscan_clustering",
            "robot_collision_screening",
            "barnes_hut_force_app",
        ):
            self.assertIn(app, text)
        self.assertIn("numpy", text)
        self.assertIn("numba", text)

    def test_runner_help_works(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertIn("Embree CPU-partner", completed.stdout)
        self.assertIn("--scale", completed.stdout)
        self.assertIn("--repeats", completed.stdout)


if __name__ == "__main__":
    unittest.main()

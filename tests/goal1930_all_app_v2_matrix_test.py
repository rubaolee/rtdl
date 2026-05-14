from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1930_all_app_v2_matrix.py"
REPORT = ROOT / "docs" / "reports" / "goal1930_all_app_v2_matrix_2026-05-13.md"
JSON_REPORT = ROOT / "docs" / "reports" / "goal1930_all_app_v2_matrix_2026-05-13.json"


class Goal1930AllAppV2MatrixTest(unittest.TestCase):
    def test_script_generates_all_sixteen_app_rows(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--output-json",
                "scratch/goal1930_all_app_v2_matrix_test.json",
                "--output-md",
                "scratch/goal1930_all_app_v2_matrix_test.md",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout[-2000:])
        payload = json.loads((ROOT / "scratch/goal1930_all_app_v2_matrix_test.json").read_text(encoding="utf-8"))
        rows = payload["rows"]
        self.assertEqual(payload["row_count"], 16)
        self.assertEqual(len(rows), 16)
        self.assertEqual(
            {
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
            },
            {row["app"] for row in rows},
        )

    def test_matrix_marks_control_rows_and_blocks_release_claims(self) -> None:
        payload = json.loads(JSON_REPORT.read_text(encoding="utf-8"))

        control_apps = {
            row["app"]
            for row in payload["rows"]
            if row["comparison_status"] == "evidence-only-control"
        }
        self.assertEqual(control_apps, set())
        bounded_apps = {
            row["app"]
            for row in payload["rows"]
            if row["comparison_status"] == "pod-evidence-collected-bounded"
        }
        self.assertEqual(
            bounded_apps,
            {
                "database_analytics",
                "graph_analytics",
                "polygon_pair_overlap_area_rows",
                "polygon_set_jaccard",
            },
        )
        self.assertFalse(payload["release_claim_boundary"]["v2_0_release_authorized"])
        self.assertFalse(payload["release_claim_boundary"]["all_apps_have_measured_v2_speedup"])
        self.assertFalse(payload["release_claim_boundary"]["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["release_claim_boundary"]["control_rows_are_release_speedup_evidence"])

    def test_report_explains_final_batch_and_evidence_only_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: all-app-rows-classified-final-pod-batch-needed", text)
        self.assertIn("evidence-only controls", text)
        self.assertIn("goal1925_fixed_radius_family_v2_partner_perf.py", text)
        self.assertIn("goal1928_robot_collision_v2_partner_perf.py", text)
        self.assertIn("goal1856_segment_polygon_v2_partner_perf.py", text)
        self.assertIn("must not collapse implemented rows and control rows", text)


if __name__ == "__main__":
    unittest.main()

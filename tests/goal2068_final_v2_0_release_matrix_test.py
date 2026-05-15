import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2068_final_v2_0_release_matrix.py"
MATRIX = ROOT / "docs" / "reports" / "goal2068_final_v2_0_release_matrix.json"
REPORT = ROOT / "docs" / "reports" / "goal2068_final_v2_0_release_matrix.md"


class Goal2068FinalV20ReleaseMatrixTest(unittest.TestCase):
    def test_script_generates_final_named_matrix(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--output-json",
                "scratch/goal2068_final_v2_0_release_matrix_test.json",
                "--output-md",
                "scratch/goal2068_final_v2_0_release_matrix_test.md",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout[-2000:])
        payload = json.loads((ROOT / "scratch/goal2068_final_v2_0_release_matrix_test.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal2068")
        self.assertEqual(payload["row_count"], 16)
        self.assertEqual(payload["status"], "final-v2-0-release-matrix-candidate")

    def test_matrix_reflects_goal2066_updates_and_boundaries(self):
        payload = json.loads(MATRIX.read_text(encoding="utf-8"))
        rows = {row["app"]: row for row in payload["rows"]}
        self.assertEqual(payload["counts_by_comparison_status"]["pod-evidence-collected-mixed"], 1)
        self.assertEqual(payload["mixed_apps"], ["segment_polygon_anyhit_rows"])
        self.assertEqual(rows["robot_collision_screening"]["comparison_status"], "pod-evidence-collected")
        self.assertIn("goal2066_robot_collision", rows["robot_collision_screening"]["v2_evidence"])
        self.assertIn("goal2066_segment_polygon_hitcount", rows["segment_polygon_hitcount"]["v2_evidence"])
        self.assertIn("4096", rows["polygon_pair_overlap_area_rows"]["analysis_hint"])
        self.assertIn("OOM", rows["polygon_pair_overlap_area_rows"]["analysis_hint"])
        self.assertFalse(payload["release_claim_boundary"]["all_apps_have_measured_v2_speedup"])
        self.assertFalse(payload["release_claim_boundary"]["v2_0_release_authorized"])

    def test_ratio_summary_is_grounded(self):
        payload = json.loads(MATRIX.read_text(encoding="utf-8"))
        ratios = payload["measured_ratio_summary"]
        self.assertLess(ratios["robot_collision_screening"]["scale_65536x8192_ratio"], 0.1)
        self.assertLess(ratios["road_hazard_screening"]["scale_12288_prepared_reuse_ratio"], 0.1)
        self.assertLess(ratios["segment_polygon_hitcount"]["scale_131072_prepared_reuse_ratio"], 0.01)
        self.assertGreater(ratios["segment_polygon_anyhit_rows"]["scale_4096_row_materialization_ratio"], 1.0)
        self.assertGreater(ratios["polygon_pair_overlap_area_rows"]["scale_3072_ratio"], 1.0)

    def test_report_blocks_release_claims(self):
        text = REPORT.read_text(encoding="utf-8")
        required = [
            "release-hardening artifact, not release authorization",
            "robot_collision_screening` moves from mixed to positive",
            "full witness-row materialization is `1.562x`",
            "4096 OptiX candidate discovery OOMs",
            "final Claude v2.0 release review missing",
            "all-app speedup",
            "package-install readiness",
        ]
        for phrase in required:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

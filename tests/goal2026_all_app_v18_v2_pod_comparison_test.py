from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2026_all_app_v18_v2_pod_comparison_2026-05-14.md"
JSON_REPORT = ROOT / "docs" / "reports" / "goal2026_all_app_v18_v2_pod_comparison_2026-05-14.json"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2026_all_app_v18_v2_pod_comparison_936aff2f_retry2"


class Goal2026AllAppV18V2PodComparisonTest(unittest.TestCase):
    def test_report_has_all_sixteen_rows_and_keeps_release_blocked(self) -> None:
        payload = json.loads(JSON_REPORT.read_text(encoding="utf-8"))

        self.assertEqual(payload["row_count"], 16)
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["claim_boundary"]["v2_0_release_authorized"])
        self.assertFalse(payload["claim_boundary"]["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["broad_rt_core_speedup_claim_authorized"])

    def test_fresh_pod_artifacts_are_recorded_with_blockers(self) -> None:
        payload = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
        steps = payload["fresh_pod_steps"]

        self.assertEqual(steps["database_control_cupy"], "0")
        self.assertEqual(steps["graph_control_cupy"], "0")
        self.assertEqual(steps["polygon_control_cupy_extent"], "0")
        self.assertEqual(steps["road_hazard_cupy"], "0")
        self.assertEqual(steps["robot_collision_cupy"], "0")
        self.assertEqual(steps["segment_hitcount_cupy"], "0")
        self.assertEqual(steps["fixed_radius_family_cupy"], "1")
        blockers = "\n".join(item["reason"] for item in payload["fresh_pod_blockers"])
        self.assertIn("rejected generated OptiX PTX", blockers)
        self.assertIn("output_capacity=count overflowed", blockers)

    def test_latest_table_uses_fresh_rows_where_they_supersede_matrix(self) -> None:
        payload = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
        rows = {row["app"]: row for row in payload["rows"]}

        self.assertEqual(rows["database_analytics"]["evidence_basis"], "fresh-goal2026-pod-rerun")
        self.assertEqual(rows["graph_analytics"]["evidence_basis"], "fresh-goal2026-pod-rerun")
        self.assertEqual(rows["polygon_pair_overlap_area_rows"]["evidence_basis"], "fresh-goal2026-pod-rerun")
        self.assertEqual(rows["polygon_set_jaccard"]["evidence_basis"], "fresh-goal2026-pod-rerun")
        self.assertLess(rows["graph_analytics"]["ratio"], 0.0001)
        self.assertLess(rows["polygon_pair_overlap_area_rows"]["ratio"], 0.25)
        self.assertLess(rows["polygon_set_jaccard"]["ratio"], 0.25)

    def test_report_explains_why_some_current_rows_use_accepted_prior_artifacts(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("latest accepted artifacts", text)
        self.assertIn("fixed-radius family failed before timing", text)
        self.assertIn("older prepared-reuse harness", text)
        self.assertIn("accepted large Goal1940 artifact", text)
        self.assertIn("not a v2.0 release authorization", text)

    def test_fresh_artifact_files_are_present(self) -> None:
        for name in (
            "database_control_cupy_100000.json",
            "graph_control_cupy_1000.json",
            "polygon_control_cupy_extent_8192.json",
            "road_hazard_cupy_4096.json",
            "robot_collision_cupy_1048576x16384.json",
            "segment_polygon_anyhit_cupy_2048.json",
            "fixed_radius_family_cupy.log",
            "segment_polygon_anyhit_cupy_1048576_capacity1048576.log",
        ):
            self.assertTrue((ARTIFACT_DIR / name).exists(), name)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5417_figure5_level_b_same_pod_matrix_plan.json"
)


class Goal5417Figure5LevelBSamePodMatrixPlanTest(unittest.TestCase):
    def test_plan_is_not_execution_or_figure5_claim(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(payload["matched"])
        self.assertEqual(
            "figure5_level_b_same_pod_matrix_plan_ready__no_execution_yet",
            payload["status"],
        )
        scope = payload["matrix_scope"]
        self.assertEqual("Level-B same-source / bounded representative matrix", scope["level"])
        self.assertFalse(scope["figure5_reproduction_claimed"])
        self.assertFalse(scope["full_figure5_matrix_claimed"])
        self.assertFalse(scope["exact_paper_dataset_reproduction_claimed"])
        boundary = payload["claim_boundary"]
        self.assertTrue(boundary["matrix_plan_claimed"])
        self.assertFalse(boundary["same_pod_execution_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["full_xhd_paper_reproduction_claimed"])

    def test_primary_graphics_candidates_are_value_matched_and_dragon_asian_excluded(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        included = {row["case_id"]: row for row in payload["primary_graphics_candidates"]}
        self.assertEqual({"dragon_happy", "thai_happy_scaled", "thai_asian_scaled"}, set(included))
        for row in included.values():
            self.assertTrue(row["include"])
            self.assertEqual("graphics", row["category"])
            self.assertLessEqual(row["author_paper_log_abs_diff"], 1e-6)
            self.assertLessEqual(row["prior_rtdl_author_abs_diff"], 1e-6)
            self.assertIn("cell-mbr-fast-scalar", row["planned_rtdl_routes"])
        excluded = {row["case_id"]: row for row in payload["excluded_candidates"]}
        self.assertIn("dragon_asian_scaled", excluded)
        self.assertIn("does not match", excluded["dragon_asian_scaled"]["reason"])

    def test_secondary_geo_candidates_are_bounded_not_full_figure5(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        geo = {row["case_id"]: row for row in payload["secondary_bounded_geo_candidates"]}
        self.assertEqual({"county_zcta_bounded", "water_bg_bounded"}, set(geo))
        for row in geo.values():
            self.assertEqual("geo_bounded", row["category"])
            self.assertTrue(row["include"])
            self.assertLessEqual(row["prior_abs_diff"], row["tolerance"])
            self.assertIn("Bounded geo fixture only", row["notes"])

    def test_denominator_columns_keep_timing_apart(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        columns = payload["planned_denominator_columns"]
        for required in (
            "author_running_avg_time_ms",
            "author_reported_time_ms",
            "author_process_wall_sec",
            "rtdl_route_wall_sec",
            "rtdl_process_wall_sec",
            "rtdl_input_load_sec",
            "per_source_witness_exact",
            "cold_or_warm_process",
            "ratio_authorized",
        ):
            self.assertIn(required, columns)

    def test_execution_plan_requires_pod_wrapper_later(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        execution = payload["execution_plan"]
        self.assertFalse(execution["goal5417_executes_pod"])
        self.assertTrue(execution["pod_required_for_goal5418"])
        self.assertFalse(execution["naked_ssh_allowed"])
        self.assertIn("scripts/current_pod_ssh.py", execution["pod_wrapper_required"])
        self.assertIn("run_xhd_goal5298_author_graphics_precheck.py", execution["author_graphics_runner"])
        self.assertIn("run_xhd_rtdl_hd_exec.py", execution["rtdl_hd_exec_runner"])

    def test_forbidden_summaries_block_overclaim(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        forbidden = "\n".join(payload["forbidden_summaries"]).lower()
        for phrase in (
            "figure 5 reproduced",
            "ratio x",
            "exact paper inputs",
            "bounded geo fixtures prove geo figure 5",
            "fast-scalar route proves exact per-source witnesses",
        ):
            self.assertIn(phrase, forbidden)


if __name__ == "__main__":
    unittest.main()

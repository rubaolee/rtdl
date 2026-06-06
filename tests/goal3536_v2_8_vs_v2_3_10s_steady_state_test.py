from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3536_v2_8_vs_v2_3_10s_steady_state.py"
FINAL_ARTIFACT = ROOT / "docs" / "reports" / "goal3536_v2_8_vs_v2_3_10s_steady_state_a5000" / "summary_final.json"
REPORT = ROOT / "docs" / "reports" / "goal3536_v2_8_vs_v2_3_10s_steady_state_a5000_2026-06-06.md"


class Goal3536V28VsV23TenSecondSteadyStateTest(unittest.TestCase):
    def test_dry_run_plans_raydb_count_and_sum_separately(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = pathlib.Path(tmpdir) / "summary.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--v23-root",
                    str(ROOT),
                    "--v28-root",
                    str(ROOT),
                    "--only-app",
                    "raydb_style",
                    "--artifact-dir",
                    str(pathlib.Path(tmpdir) / "artifacts"),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=120,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr[-2000:])
            payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3536.v2_8_vs_v2_3_10s_steady_state.v1")
        self.assertTrue(payload["dry_run"])
        self.assertFalse(payload["claim_boundary"]["release_authorized"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertIn("target_met_by_observed_pair_count", payload["summary"])
        self.assertIn("observed_target_misses", payload["summary"])
        cases = {row["case_id"] for row in payload["comparisons"]}
        self.assertEqual(
            {"raydb_optix_partner_resident_count", "raydb_optix_partner_resident_sum"},
            cases,
        )
        for row in payload["comparisons"]:
            self.assertIn("v23_observed_measured_sec", row)
            self.assertIn("v28_observed_measured_sec", row)
            self.assertIn("v23_target_met_by_observed_sum", row)
            self.assertIn("v28_target_met_by_observed_sum", row)
        for row in payload["rows"]:
            self.assertEqual(row["plan"]["method"], "internal_repeat_knob")
            self.assertEqual(row["plan"]["repeat_flag"], "--repeat")
            self.assertTrue(row["plan"]["target_met_by_plan"])

    def test_v2_9_repeat_hooks_plan_former_partial_rows_as_internal_repeats(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = pathlib.Path(tmpdir) / "summary.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--v23-root",
                    str(ROOT),
                    "--v28-root",
                    str(ROOT),
                    "--seed-artifact",
                    str(FINAL_ARTIFACT),
                    "--only-case",
                    "hausdorff_optix_threshold",
                    "--only-case",
                    "spatial_rayjoin_optix_prepared_full_route",
                    "--only-case",
                    "robot_collision_optix_prepared_device_buffers",
                    "--only-case",
                    "barnes_hut_optix_node_coverage",
                    "--only-case",
                    "librts_optix_aabb_index",
                    "--artifact-dir",
                    str(pathlib.Path(tmpdir) / "artifacts"),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=120,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr[-2000:])
            payload = json.loads(output.read_text(encoding="utf-8"))
        methods = {row["plan"]["method"] for row in payload["rows"]}
        self.assertEqual({"internal_repeat_knob"}, methods)
        case_ids = {row["case_id"] for row in payload["rows"]}
        self.assertEqual(
            {
                "hausdorff_optix_threshold",
                "spatial_rayjoin_optix_prepared_full_route",
                "robot_collision_optix_prepared_device_buffers",
                "barnes_hut_optix_node_coverage",
                "librts_optix_aabb_index",
            },
            case_ids,
        )
        for row in payload["rows"]:
            self.assertTrue(row["plan"]["target_met_by_plan"])
            self.assertIn(row["plan"]["repeat_flag"], {"--repeat", "--repeats"})
            self.assertGreaterEqual(row["plan"]["planned_repeat"], row["plan"]["base_repeat"])

    def test_script_documents_boundary_and_uses_goal2626_registry(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        for phrase in (
            "goal2626_benchmark_embree_optix_baseline.py",
            "target_met_by_plan",
            "target_met_by_observed_pair_count",
            "observed_target_misses",
            "repeat-safety-factor",
            "internal_repeat_knob",
            "wrapper_repeat_subprocess",
            "public_speedup_claim_authorized",
            "Rows without a repeat knob are reported as partial diagnostics",
        ):
            self.assertIn(phrase, text)

    def test_a5000_final_artifact_has_six_target_compliant_rows_and_clean_boundaries(self) -> None:
        payload = json.loads(FINAL_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3536.v2_8_vs_v2_3_10s_steady_state.v1")
        self.assertFalse(payload["claim_boundary"]["release_authorized"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertEqual(payload["summary"]["row_count"], 11)
        target_rows = [
            row
            for row in payload["comparisons"]
            if row["v23_target_met_by_observed_sum"] and row["v28_target_met_by_observed_sum"]
        ]
        self.assertEqual(6, len(target_rows))
        target_cases = {row["case_id"] for row in target_rows}
        self.assertIn("raydb_optix_partner_resident_count", target_cases)
        self.assertIn("raydb_optix_partner_resident_sum", target_cases)
        self.assertIn("rtnn_optix_prepared_3d_ranked_summary", target_cases)
        by_case = {row["case_id"]: row for row in payload["comparisons"]}
        self.assertLess(by_case["raydb_optix_partner_resident_count"]["v28_speedup_vs_v23"], 1.1)
        self.assertGreater(by_case["raydb_optix_partner_resident_count"]["v28_speedup_vs_v23"], 0.9)
        self.assertLess(by_case["raydb_optix_partner_resident_sum"]["v28_speedup_vs_v23"], 1.1)
        self.assertGreater(by_case["raydb_optix_partner_resident_sum"]["v28_speedup_vs_v23"], 0.9)
        self.assertTrue(payload["merged_from"]["rtnn_repair_packet"].replace("\\", "/").endswith("rtnn_repair/summary.json"))

    def test_report_explains_raydb_short_run_correction_and_partial_rows(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "previous 7.2x was not stable under long run",
            "Target-compliant subset: 6 rows",
            "10s evidence",
            "Rows without a repeat hook",
            "Barnes-Hut remains a real weak row",
            "does not authorize any public release or speedup wording",
        ):
            self.assertIn(phrase, text)

    def test_markdown_rendering_separates_plan_and_observed_targets(self) -> None:
        module = __import__(
            "scripts.goal3536_v2_8_vs_v2_3_10s_steady_state",
            fromlist=["render_markdown"],
        )
        payload = {
            "target_measured_sec": 10.0,
            "scale": "standard",
            "gpu": "test gpu",
            "summary": {
                "row_count": 1,
                "ratio_count": 1,
                "target_met_by_plan_pair_count": 1,
                "target_met_by_observed_pair_count": 0,
                "observed_target_miss_count": 1,
            },
            "comparisons": [
                {
                    "app_id": "example",
                    "case_id": "example_case",
                    "v23_primary_metric_sec": 1.0,
                    "v28_primary_metric_sec": 2.0,
                    "v28_speedup_vs_v23": 0.5,
                    "v23_target_met_by_plan": True,
                    "v28_target_met_by_plan": True,
                    "v23_target_met_by_observed_sum": True,
                    "v28_target_met_by_observed_sum": False,
                }
            ],
        }
        text = module.render_markdown(payload)
        self.assertIn("Target plan met?", text)
        self.assertIn("Target observed met?", text)
        self.assertIn("| example | example_case | 1 | 2 | 0.500x | True/True | True/False |", text)


if __name__ == "__main__":
    unittest.main()

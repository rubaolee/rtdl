from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3542_v2_9_repeat_resident_hook_coverage_2026-06-06.md"
GOAL3536_SCRIPT = ROOT / "scripts" / "goal3536_v2_8_vs_v2_3_10s_steady_state.py"
GOAL2626_SCRIPT = ROOT / "scripts" / "goal2626_benchmark_embree_optix_baseline.py"
FINAL_ARTIFACT = ROOT / "docs" / "reports" / "goal3536_v2_8_vs_v2_3_10s_steady_state_a5000" / "summary_final.json"


class Goal3542V29RepeatResidentHookCoverageTest(unittest.TestCase):
    def test_report_records_scope_and_release_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "first v2.9 performance-lane action",
            "resident hot-query loops",
            "current tree for both lanes",
            "same-contract v2.3 evidence checkout",
            "internal_repeat_knob",
            "does not add app-specific native engine logic",
            "does not authorize",
            "post-review pod/A5000 rerun",
        ):
            self.assertIn(phrase, text)

    def test_app_sources_expose_repeat_protocol_for_former_partial_rows(self) -> None:
        paths = [
            ROOT / "examples" / "v2_0" / "research_benchmarks" / "hausdorff_xhd" / "rtdl_hausdorff_distance_app.py",
            ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "rtdl_rayjoin_v2_spatial_join_app.py",
            ROOT / "examples" / "v2_0" / "apps" / "simulation" / "rtdl_barnes_hut_force_app.py",
            ROOT / "examples" / "v2_0" / "research_benchmarks" / "barnes_hut" / "rtdl_barnes_hut_benchmark_app.py",
            ROOT / "examples" / "v2_0" / "research_benchmarks" / "librts_spatial_index" / "rtdl_librts_spatial_index_benchmark_app.py",
        ]
        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertIn("--repeat", text, path)
            self.assertIn("--warmup", text, path)
            self.assertRegex(text, r"query_repeat|repeat_protocol", path)

    def test_registry_wires_repeat_flags_and_prepared_query_metrics(self) -> None:
        text = GOAL2626_SCRIPT.read_text(encoding="utf-8")
        for case_id in (
            "hausdorff_optix_threshold",
            "spatial_rayjoin_optix_prepared_full_route",
            "barnes_hut_optix_node_coverage",
            "librts_optix_aabb_index",
        ):
            start = text.index(f'case_id="{case_id}"')
            chunk = text[start : start + 1200]
            self.assertIn('"--repeat"', chunk, case_id)
            self.assertIn('"--warmup"', chunk, case_id)
        self.assertIn('primary_metric_path=("run_phases", "query_median_sec")', text)

    def test_claude_review_hygiene_items_are_addressed(self) -> None:
        rayjoin = (
            ROOT
            / "examples"
            / "v2_0"
            / "research_benchmarks"
            / "spatial_rayjoin"
            / "rtdl_rayjoin_v2_spatial_join_app.py"
        ).read_text(encoding="utf-8")
        self.assertIn("stability_value", rayjoin)
        self.assertIn("repeat changed result identity", rayjoin)
        librts = (
            ROOT
            / "examples"
            / "v2_0"
            / "research_benchmarks"
            / "librts_spatial_index"
            / "rtdl_librts_spatial_index_benchmark_app.py"
        ).read_text(encoding="utf-8")
        self.assertIn("query_summed_median_sec", librts)

    def test_planner_dry_run_marks_all_five_rows_as_internal_repeats(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = pathlib.Path(tmpdir) / "summary.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(GOAL3536_SCRIPT),
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
            payload = __import__("json").loads(output.read_text(encoding="utf-8"))
        self.assertEqual(10, len(payload["rows"]))
        for row in payload["rows"]:
            self.assertEqual("internal_repeat_knob", row["plan"]["method"])
            self.assertTrue(row["plan"]["target_met_by_plan"])
            self.assertIn(row["plan"]["repeat_flag"], {"--repeat", "--repeats"})

    def test_artificial_high_setup_shortcut_is_removed(self) -> None:
        text = GOAL3536_SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("high_setup_extreme_repeat", text)
        self.assertIn("partial_base_repeat_wall_guard", text)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v4_goal4669_full_app_level_pod_benchmark.py"
SPEC = importlib.util.spec_from_file_location("v4_goal4669_full_app_level_pod_benchmark", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class V4Goal4669FullAppRunnerTest(unittest.TestCase):
    def test_runner_promotes_hausdorff_to_fifth_full_app_row(self) -> None:
        self.assertEqual(
            (
                "rt_dbscan",
                "raydb_style",
                "triangle_counting",
                "librts_spatial_index",
                "hausdorff_xhd",
            ),
            runner.APP_ORDER,
        )

    def test_serious_commands_bind_hausdorff_denominators(self) -> None:
        profile = runner._profile_values("serious")
        root = Path("/repo")
        v2 = runner._commands(root, "v2_14", profile, Path("/tmp/k4.edgebin"))["hausdorff_xhd"]
        v3 = runner._commands(root, "v3_0_2", profile, Path("/tmp/k4.edgebin"))["hausdorff_xhd"]
        v4 = runner._commands(root, "v4_current", profile, Path("/tmp/k4.edgebin"))["hausdorff_xhd"]
        probe = runner._hausdorff_command(root, "v4_current", profile, correctness_probe=True)

        self.assertIn("examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py", v2)
        self.assertIn("--backend", v2)
        self.assertIn("embree", v2)
        self.assertIn("--embree-result-mode", v2)
        self.assertIn("directed_summary", v2)
        self.assertIn("65536", v2)

        for command in (v3, v4):
            self.assertIn("optix_device_max_nearest", command)
            self.assertIn("--partner", command)
            self.assertIn("cupy", command)
            self.assertIn("--repeat", command)
            self.assertIn("9", command)
            self.assertIn("--warmup", command)
            self.assertIn("5", command)
            self.assertIn("65536", command)

        self.assertIn("--coordinate-normalization-span", probe)
        self.assertIn("262144", probe)
        self.assertIn("1000000.0", probe)

    def test_v4_raydb_command_uses_device_output_frontdoor_only_for_v4(self) -> None:
        profile = runner._profile_values("serious")
        root = Path("/repo")
        v2 = runner._commands(root, "v2_14", profile, Path("/tmp/k4.edgebin"))["raydb_style"]
        v3 = runner._commands(root, "v3_0_2", profile, Path("/tmp/k4.edgebin"))["raydb_style"]
        v4 = runner._commands(root, "v4_current", profile, Path("/tmp/k4.edgebin"))["raydb_style"]

        self.assertIn("paper_rt_optix_prepared_grouped_reduction", v2)
        self.assertIn("paper_rt_optix_prepared_grouped_reduction", v3)
        self.assertIn("paper_rt_v4_cupy_device_grouped_reduction", v4)
        self.assertNotIn("paper_rt_v4_cupy_device_grouped_reduction", v2)
        self.assertNotIn("paper_rt_v4_cupy_device_grouped_reduction", v3)
        self.assertIn("--summary-only-iterations", v4)

    def test_hausdorff_metric_extraction_records_hot_primary_prepare_and_parity(self) -> None:
        payload = {
            "backend": "optix_device_max_nearest",
            "copies": 65536,
            "matches_oracle": True,
            "coordinate_normalization_used": False,
            "run_phases": {
                "hot_device_sec": 0.002,
                "optix_device_max_nearest_directed_summary_sec": 6.5,
                "scene_prepare_sec": 3.4,
                "materialize_sec": 0.0002,
            },
        }

        metrics = runner._extract_metrics("hausdorff_xhd", payload)

        self.assertTrue(metrics["json_parse_ok"])
        self.assertTrue(metrics["correctness_parity"])
        self.assertEqual(0.002, metrics["hot_sec"])
        self.assertEqual(6.5, metrics["primary_wall_sec"])
        self.assertEqual(3.4, metrics["prepare_sec"])
        self.assertEqual("optix_device_max_nearest", metrics["route"])
        self.assertEqual(262144, metrics["points_per_side"])

    def test_analysis_requires_hausdorff_correctness_probe_for_frozen_bar(self) -> None:
        versions = {
            "v2_14": {"label": "V2", "tag_native_optix_build": False, "optix_library_note": "compat"},
            "v3_0_2": {"label": "V3", "tag_native_optix_build": False, "optix_library_note": "compat"},
            "v4_current": {"label": "V4", "tag_native_optix_build": True, "optix_library_note": "native"},
        }

        def row(version: str, app: str, payload: dict[str, object]) -> dict[str, object]:
            path = ROOT / "future" / "v4" / "evidence" / f"tmp_goal4669_{version}_{app}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(__import__("json").dumps(payload), encoding="utf-8")
            return {
                "version": version,
                "app": app,
                "stdout_json": str(path),
                "returncode": 0,
                "command": [],
                "cwd": "",
                "stderr": "",
                "timed_out": False,
                "error": None,
                "runner_elapsed_sec": 0.0,
                "started_unix": 0.0,
                "ended_unix": 0.0,
            }

        executions = [
            row(
                "v2_14",
                "hausdorff_xhd",
                {
                    "backend": "embree",
                    "copies": 65536,
                    "matches_oracle": True,
                    "run_phases": {"native_directed_summary_sec": 100.0},
                },
            ),
            row(
                "v3_0_2",
                "hausdorff_xhd",
                {
                    "backend": "optix_device_max_nearest",
                    "copies": 65536,
                    "matches_oracle": True,
                    "run_phases": {
                        "hot_device_sec": 0.004,
                        "optix_device_max_nearest_directed_summary_sec": 8.0,
                        "scene_prepare_sec": 4.0,
                    },
                },
            ),
            row(
                "v4_current",
                "hausdorff_xhd",
                {
                    "backend": "optix_device_max_nearest",
                    "copies": 65536,
                    "matches_oracle": True,
                    "run_phases": {
                        "hot_device_sec": 0.002,
                        "optix_device_max_nearest_directed_summary_sec": 6.0,
                        "scene_prepare_sec": 3.5,
                    },
                },
            ),
            row(
                "v4_current",
                "hausdorff_xhd_correctness_1m",
                {
                    "backend": "optix_device_max_nearest",
                    "copies": 262144,
                    "matches_oracle": True,
                    "coordinate_normalization_used": True,
                    "run_phases": {
                        "hot_device_sec": 0.006,
                        "optix_device_max_nearest_directed_summary_sec": 34.0,
                        "scene_prepare_sec": 11.0,
                    },
                },
            ),
        ]

        analysis = runner._analyze(executions, versions)
        rows = {row["app"]: row for row in analysis["app_scorecard"]}

        self.assertIn("hausdorff_xhd", rows)
        self.assertTrue(rows["hausdorff_xhd"]["coordinate_normalized_1m_correctness_probe_passed"])
        self.assertTrue(rows["hausdorff_xhd"]["hausdorff_frozen_bar_passed"])
        self.assertGreater(rows["hausdorff_xhd"]["v4_vs_v3_0_2_hot_speedup"], 1.20)


if __name__ == "__main__":
    unittest.main()

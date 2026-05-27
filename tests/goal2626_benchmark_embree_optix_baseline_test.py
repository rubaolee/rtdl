from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2626_benchmark_embree_optix_baseline.py"


class Goal2626BenchmarkEmbreeOptixBaselineTest(unittest.TestCase):
    def test_manifest_covers_current_promoted_benchmark_apps(self) -> None:
        sys.path.insert(0, str(ROOT))
        from scripts import goal2626_benchmark_embree_optix_baseline as runner

        cases = runner.build_cases("quick", ROOT / "scratch" / "goal2626_test")
        app_ids = {case.app_id for case in cases}
        self.assertEqual(set(runner.PROMOTED_BENCHMARK_APPS), app_ids)
        for app_id in runner.PROMOTED_BENCHMARK_APPS:
            self.assertIn("embree", {case.backend for case in cases if case.app_id == app_id})
            self.assertIn("optix", {case.backend for case in cases if case.app_id == app_id})

    def test_former_optix_only_rows_now_have_embree_commands(self) -> None:
        sys.path.insert(0, str(ROOT))
        from scripts import goal2626_benchmark_embree_optix_baseline as runner

        cases = {
            case.case_id: case
            for case in runner.build_cases("quick", ROOT / "scratch" / "goal2626_test")
        }
        for case_id in (
            "rt_dbscan_embree_fixed_radius_rows",
            "librts_embree_aabb_index",
            "rtnn_embree_prepared_3d_ranked_summary",
        ):
            self.assertIn(case_id, cases)
            self.assertTrue(cases[case_id].supported)
            self.assertIsNotNone(cases[case_id].command)
            self.assertIsNone(cases[case_id].unsupported_reason)

    def test_raydb_optix_row_uses_partner_resident_warm_query_path(self) -> None:
        sys.path.insert(0, str(ROOT))
        from scripts import goal2626_benchmark_embree_optix_baseline as runner

        cases = {
            case.case_id: case
            for case in runner.build_cases("quick", ROOT / "scratch" / "goal2626_test")
        }
        case = cases["raydb_optix_partner_resident_count"]
        assert case.command is not None
        self.assertEqual(case.backend, "optix")
        self.assertIn("optix_partner_resident_experimental", case.command)
        self.assertIn("--warmup", case.command)
        self.assertIn("--repeat", case.command)
        self.assertEqual(("metadata", "timings", "query_median_sec"), case.primary_metric_path)
        self.assertIn("partner-resident grouped-i64 dispatcher", case.notes)

    def test_triangle_counting_uses_generic_rt_graph_2a1_path(self) -> None:
        sys.path.insert(0, str(ROOT))
        from scripts import goal2626_benchmark_embree_optix_baseline as runner

        cases = {
            case.case_id: case
            for case in runner.build_cases("quick", ROOT / "scratch" / "goal2626_test")
        }
        embree = cases["triangle_counting_embree_rt_graph_2a1"]
        optix = cases["triangle_counting_optix_rt_graph_2a1_partner"]
        assert embree.command is not None
        assert optix.command is not None
        self.assertIn("rt_graph_2a1_generic_rt", embree.command)
        self.assertIn("rt_graph_2a1_generic_rt", optix.command)
        self.assertIn("--edge-file", embree.command)
        self.assertIn("--edge-file", optix.command)
        self.assertIn("--partner", optix.command)
        self.assertIn("cupy", optix.command)
        self.assertIn("--warmup", embree.command)
        self.assertIn("--repeat", embree.command)
        self.assertIn("--warmup", optix.command)
        self.assertIn("--repeat", optix.command)
        self.assertEqual(("timing_ms", "query_median_ms"), embree.primary_metric_path)
        self.assertEqual(("timing_ms", "query_median_ms"), optix.primary_metric_path)
        self.assertIn("host-indexed fallback", optix.notes)

    def test_ratios_only_for_same_app_and_comparison_group(self) -> None:
        sys.path.insert(0, str(ROOT))
        from scripts import goal2626_benchmark_embree_optix_baseline as runner

        rows = [
            {
                "status": "ok",
                "app_id": "app_a",
                "comparison_group": "same",
                "backend": "embree",
                "primary_metric_sec": 4.0,
                "primary_metric_source": "x",
            },
            {
                "status": "ok",
                "app_id": "app_a",
                "comparison_group": "same",
                "backend": "optix",
                "primary_metric_sec": 2.0,
                "primary_metric_source": "y",
            },
            {
                "status": "ok",
                "app_id": "app_a",
                "comparison_group": "different",
                "backend": "optix",
                "primary_metric_sec": 1.0,
                "primary_metric_source": "z",
            },
        ]
        ratios = runner.compute_ratios(rows)
        self.assertEqual(1, len(ratios))
        self.assertEqual("same", ratios[0]["comparison_group"])
        self.assertEqual(2.0, ratios[0]["optix_speedup_vs_embree"])

    def test_workload_suite_metric_uses_total_elapsed_time(self) -> None:
        sys.path.insert(0, str(ROOT))
        from scripts import goal2626_benchmark_embree_optix_baseline as runner

        metric, source, _ = runner._choose_primary_metric(
            {
                "workloads": {
                    "first": {"elapsed_sec": 1.25},
                    "second": {"elapsed_sec": 2.75},
                }
            },
            hint=(),
            wall_median_sec=99.0,
        )
        self.assertEqual(4.0, metric)
        self.assertEqual("workloads.total_elapsed_sec", source)

    def test_dry_run_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact_dir = Path(tmp) / "artifacts"
            completed = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--scale",
                    "quick",
                    "--dry-run",
                    "--only-app",
                    "hausdorff_xhd",
                    "--artifact-dir",
                    str(artifact_dir),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads((artifact_dir / "summary.json").read_text(encoding="utf-8"))
            self.assertTrue(payload["dry_run"])
            self.assertEqual({"hausdorff_xhd"}, {row["app_id"] for row in payload["rows"]})
            self.assertTrue((artifact_dir / "summary.md").exists())


if __name__ == "__main__":
    unittest.main()

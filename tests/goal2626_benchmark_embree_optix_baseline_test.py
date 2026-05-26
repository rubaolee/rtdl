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

    def test_unsupported_rows_have_reasons_and_no_command(self) -> None:
        sys.path.insert(0, str(ROOT))
        from scripts import goal2626_benchmark_embree_optix_baseline as runner

        unsupported = [
            case
            for case in runner.build_cases("quick", ROOT / "scratch" / "goal2626_test")
            if not case.supported
        ]
        self.assertGreaterEqual(len(unsupported), 1)
        for case in unsupported:
            self.assertIsNone(case.command)
            self.assertTrue(case.unsupported_reason)
            self.assertIn(case.backend, {"embree", "optix"})

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

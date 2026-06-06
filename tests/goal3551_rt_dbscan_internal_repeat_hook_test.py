from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
REGISTRY = ROOT / "scripts" / "goal2626_benchmark_embree_optix_baseline.py"
HARNESS = ROOT / "scripts" / "goal3536_v2_8_vs_v2_3_10s_steady_state.py"
SEED = (
    ROOT
    / "docs"
    / "reports"
    / "goal3548_v2_9_repeat_hook_10s_rerun_a5000_compact_calibrated3"
    / "summary.json"
)


class Goal3551RTDBSCANInternalRepeatHookTest(unittest.TestCase):
    def test_grouped_stream_app_exposes_repeat_protocol_without_claims(self) -> None:
        app = APP.read_text(encoding="utf-8")
        start = app.index('elif mode == "optix_rt_core_grouped_stream_cupy_components_3d"')
        end = app.index('elif mode == "optix_rt_core_flags_cupy_microcell_graph_components_3d"')
        grouped = app[start:end]

        self.assertIn("repeat: int = 1", app)
        self.assertIn("warmup: int = 0", app)
        self.assertIn('parser.add_argument("--repeat"', app)
        self.assertIn('parser.add_argument("--warmup"', app)
        self.assertIn("prepared_query_runs", grouped)
        self.assertIn('"prepared_query_repeat_protocol"', grouped)
        self.assertIn('"signatures_stable"', grouped)
        self.assertIn("statistics.median", grouped)
        self.assertIn("elapsed_override", grouped)
        self.assertIn('"rt_core_accelerated": True', grouped)
        self.assertNotIn("paper_speedup_claim_authorized\": True", grouped)

    def test_goal2626_registry_marks_rt_dbscan_as_repeatable(self) -> None:
        registry = REGISTRY.read_text(encoding="utf-8")
        start = registry.index('case_id="rt_dbscan_optix_grouped_stream"')
        end = registry.index('case_id="robot_collision_embree_prepared_buffers"')
        case = registry[start:end]

        self.assertIn('"--warmup"', case)
        self.assertIn('"--repeat"', case)
        self.assertIn('"3"', case)
        self.assertIn('"optix_rt_core_grouped_stream_blocked_cupy_column_signature_3d"', case)

    def test_goal3536_dry_run_plans_rt_dbscan_as_internal_repeat(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "summary.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(HARNESS),
                    "--dry-run",
                    "--v23-root",
                    str(ROOT),
                    "--v28-root",
                    str(ROOT),
                    "--seed-artifact",
                    str(SEED),
                    "--only-case",
                    "rt_dbscan_optix_grouped_stream",
                    "--artifact-dir",
                    str(Path(tmpdir) / "artifacts"),
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

        self.assertEqual(payload["summary"]["row_count"], 1)
        self.assertEqual(payload["summary"]["target_met_by_plan_pair_count"], 1)
        for row in payload["rows"]:
            self.assertEqual(row["plan"]["method"], "internal_repeat_knob")
            self.assertEqual(row["plan"]["repeat_flag"], "--repeat")
            self.assertGreaterEqual(row["plan"]["planned_repeat"], row["plan"]["base_repeat"])


if __name__ == "__main__":
    unittest.main()


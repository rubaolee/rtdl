from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal979DeferredCpuTimingRepairTest(unittest.TestCase):
    def test_repaired_artifacts_have_positive_cpu_oracle_query_timing(self) -> None:
        for path in (
            "docs/reports/goal835_baseline_hausdorff_distance_directed_threshold_prepared_cpu_oracle_same_semantics_2026-04-23.json",
            "docs/reports/goal835_baseline_ann_candidate_search_candidate_threshold_prepared_cpu_oracle_same_semantics_2026-04-23.json",
            "docs/reports/goal835_baseline_barnes_hut_force_app_node_coverage_prepared_cpu_oracle_same_semantics_2026-04-23.json",
        ):
            payload = json.loads((ROOT / path).read_text(encoding="utf-8"))
            self.assertGreater(payload["phase_seconds"]["native_query"], 0.0, path)
            self.assertIn("goal979_timing_repair", payload["validation"], path)
            self.assertTrue(payload["validation"]["goal979_timing_repair"]["summary_matches_existing"], path)
            self.assertFalse(payload["authorizes_public_speedup_claim"], path)

    def test_dry_run_cli_does_not_write_baselines_but_reports_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal979.json"
            output_md = Path(tmpdir) / "goal979.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal979_deferred_cpu_timing_repair.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "ok")
            self.assertFalse(payload["write"])
            self.assertEqual(len(payload["rows"]), 3)
            self.assertTrue(output_md.exists())
            self.assertIn("Goal979", output_md.read_text(encoding="utf-8"))
            self.assertIn('"status": "ok"', completed.stdout)


if __name__ == "__main__":
    unittest.main()

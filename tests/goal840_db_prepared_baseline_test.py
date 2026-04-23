from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal840DbPreparedBaselineTest(unittest.TestCase):
    def test_build_cpu_sales_risk_artifact_matches_goal836_contract(self) -> None:
        module = __import__("scripts.goal840_db_prepared_baseline", fromlist=["build_db_baseline_artifact"])
        artifact = module.build_db_baseline_artifact(
            backend="cpu",
            scenario="sales_risk",
            copies=20,
            iterations=2,
        )
        self.assertEqual(artifact["app"], "database_analytics")
        self.assertEqual(artifact["path_name"], "prepared_db_session_sales_risk")
        self.assertEqual(artifact["baseline_name"], "cpu_oracle_compact_summary")
        self.assertTrue(artifact["correctness_parity"])
        self.assertEqual(artifact["benchmark_scale"], {"copies": 20, "iterations": 2})
        self.assertEqual(
            set(artifact["required_phase_coverage"]),
            {
                "input_pack_or_table_build",
                "backend_prepare",
                "native_query",
                "copyback_or_materialization",
                "python_summary_postprocess",
            },
        )
        self.assertIn("prepared_session_section", artifact["summary"])

    def test_build_embree_regional_dashboard_artifact_validates_against_cpu(self) -> None:
        module = __import__("scripts.goal840_db_prepared_baseline", fromlist=["build_db_baseline_artifact"])
        artifact = module.build_db_baseline_artifact(
            backend="embree",
            scenario="regional_dashboard",
            copies=20,
            iterations=2,
        )
        self.assertEqual(artifact["baseline_name"], "embree_compact_summary")
        self.assertTrue(artifact["correctness_parity"])
        self.assertEqual(artifact["validation"]["reference_backend"], "cpu")
        self.assertEqual(artifact["summary"]["prepared_session_section"]["backend"], "embree")

    def test_cli_writes_artifact_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "artifact.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal840_db_prepared_baseline.py",
                    "--backend",
                    "cpu",
                    "--scenario",
                    "sales_risk",
                    "--copies",
                    "20",
                    "--iterations",
                    "2",
                    "--output-json",
                    str(output_json),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            self.assertIn(str(output_json.resolve()), completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "ok")


if __name__ == "__main__":
    unittest.main()

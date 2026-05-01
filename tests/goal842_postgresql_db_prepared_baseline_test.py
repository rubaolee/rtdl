from __future__ import annotations

import json
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest import mock
from contextlib import redirect_stdout


ROOT = Path(__file__).resolve().parents[1]


def _fake_connection():
    module = __import__("rtdsl", fromlist=["FakePostgresqlConnection"])
    return module.FakePostgresqlConnection()


class Goal842PostgresqlDbPreparedBaselineTest(unittest.TestCase):
    def test_build_sales_risk_artifact_matches_goal836_contract(self) -> None:
        module = __import__(
            "scripts.goal842_postgresql_db_prepared_baseline",
            fromlist=["build_postgresql_db_baseline_artifact"],
        )
        with mock.patch("scripts.goal842_postgresql_db_prepared_baseline.rt.connect_postgresql", return_value=_fake_connection()):
            artifact = module.build_postgresql_db_baseline_artifact(
                scenario="sales_risk",
                copies=20,
                iterations=2,
                dsn="fake",
            )
        self.assertEqual(artifact["app"], "database_analytics")
        self.assertEqual(artifact["path_name"], "prepared_db_session_sales_risk")
        self.assertEqual(artifact["baseline_name"], "postgresql_same_semantics_on_linux_when_available")
        self.assertTrue(artifact["correctness_parity"])
        self.assertEqual(artifact["benchmark_scale"], {"copies": 20, "iterations": 2})
        self.assertEqual(artifact["summary"]["prepared_session_section"]["backend"], "postgresql")

    def test_build_regional_dashboard_artifact_validates_against_cpu(self) -> None:
        module = __import__(
            "scripts.goal842_postgresql_db_prepared_baseline",
            fromlist=["build_postgresql_db_baseline_artifact"],
        )
        with mock.patch("scripts.goal842_postgresql_db_prepared_baseline.rt.connect_postgresql", return_value=_fake_connection()):
            artifact = module.build_postgresql_db_baseline_artifact(
                scenario="regional_dashboard",
                copies=20,
                iterations=2,
                dsn="fake",
            )
        self.assertTrue(artifact["correctness_parity"])
        self.assertEqual(artifact["validation"]["reference_backend"], "cpu")
        self.assertEqual(artifact["summary"]["prepared_session_section"]["backend"], "postgresql")

    def test_cli_writes_artifact_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "artifact.json"
            module = __import__(
                "scripts.goal842_postgresql_db_prepared_baseline",
                fromlist=["main"],
            )
            stdout = StringIO()
            with mock.patch("scripts.goal842_postgresql_db_prepared_baseline.rt.connect_postgresql", return_value=_fake_connection()):
                with redirect_stdout(stdout):
                    rc = module.main(
                        [
                            "--scenario",
                            "sales_risk",
                            "--copies",
                            "20",
                            "--iterations",
                            "2",
                            "--dsn",
                            "fake",
                            "--output-json",
                            str(output_json),
                        ]
                    )
            self.assertEqual(rc, 0)
            self.assertIn(str(output_json.resolve()), stdout.getvalue())
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "ok")


if __name__ == "__main__":
    unittest.main()

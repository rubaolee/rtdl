from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_json(*args: str) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONPATH": "src:."},
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


class Goal756PreparedDbAppSessionTest(unittest.TestCase):
    def test_unified_prepared_session_matches_one_shot_summary(self) -> None:
        from examples import rtdl_database_analytics_app as db_app

        one_shot = db_app.run_app("cpu", scenario="all", copies=3, output_mode="summary")
        with db_app.prepare_session("cpu", scenario="all", copies=3) as session:
            prepared = session.run(output_mode="summary")

        self.assertEqual(prepared["execution_mode"], "prepared_session")
        self.assertEqual(one_shot["sections"]["regional_dashboard"]["summary"], prepared["sections"]["regional_dashboard"]["summary"])
        self.assertEqual(one_shot["sections"]["sales_risk"]["summary"], prepared["sections"]["sales_risk"]["summary"])
        self.assertIn("prepare_session_sec", prepared["prepared_session"])

    def test_session_rejects_run_after_close(self) -> None:
        from examples import rtdl_database_analytics_app as db_app

        session = db_app.prepare_session("cpu", scenario="sales_risk", copies=1)
        session.close()
        with self.assertRaisesRegex(RuntimeError, "closed"):
            session.run(output_mode="summary")

    def test_cli_prepared_session_mode_reports_iterations_and_timing(self) -> None:
        payload = run_json(
            "examples/rtdl_database_analytics_app.py",
            "--backend",
            "cpu",
            "--scenario",
            "sales_risk",
            "--copies",
            "2",
            "--output-mode",
            "summary",
            "--execution-mode",
            "prepared_session",
            "--session-iterations",
            "3",
        )
        self.assertEqual(payload["execution_mode"], "prepared_session")
        self.assertEqual(payload["session_iterations"], 3)
        self.assertIn("session_run_timing_sec", payload)
        self.assertEqual(payload["sections"]["sales_risk"]["row_counts"]["scan"], 8)

    def test_cli_rejects_non_positive_session_iterations(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "examples/rtdl_database_analytics_app.py",
                "--execution-mode",
                "prepared_session",
                "--session-iterations",
                "0",
            ],
            cwd=REPO_ROOT,
            env={**os.environ, "PYTHONPATH": "src:."},
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("--session-iterations must be positive", completed.stderr)


if __name__ == "__main__":
    unittest.main()

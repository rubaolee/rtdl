from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


class Goal859SpatialSummaryBaselineTest(unittest.TestCase):
    def test_service_cpu_artifact_matches_contract(self) -> None:
        module = __import__("scripts.goal859_spatial_summary_baseline", fromlist=["build_artifact"])
        artifact = module.build_artifact(
            app_name="service_coverage_gaps",
            backend="cpu",
            copies=4,
            iterations=2,
        )
        self.assertEqual(artifact["app"], "service_coverage_gaps")
        self.assertEqual(artifact["path_name"], "prepared_gap_summary")
        self.assertEqual(artifact["baseline_name"], "cpu_oracle_summary")
        self.assertTrue(artifact["correctness_parity"])
        self.assertIn("optix_query", artifact["phase_seconds"])

    def test_event_embree_artifact_matches_contract(self) -> None:
        module = __import__("scripts.goal859_spatial_summary_baseline", fromlist=["build_artifact"])
        artifact = module.build_artifact(
            app_name="event_hotspot_screening",
            backend="embree",
            copies=4,
            iterations=2,
        )
        self.assertEqual(artifact["app"], "event_hotspot_screening")
        self.assertEqual(artifact["path_name"], "prepared_count_summary")
        self.assertEqual(artifact["baseline_name"], "embree_summary_path")
        self.assertTrue(artifact["correctness_parity"])
        self.assertIn("python_postprocess", artifact["phase_seconds"])

    def test_cli_writes_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "artifact.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal859_spatial_summary_baseline.py",
                    "--app",
                    "service_coverage_gaps",
                    "--backend",
                    "cpu",
                    "--copies",
                    "2",
                    "--iterations",
                    "2",
                    "--output-json",
                    str(output_path),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            artifact = json.loads(output_path.read_text(encoding="utf-8"))
            stdout_payload = json.loads(completed.stdout)

        self.assertEqual(artifact["app"], "service_coverage_gaps")
        self.assertEqual(stdout_payload["baseline_name"], "cpu_oracle_summary")
        self.assertEqual(artifact["status"], "ok")

    def test_service_scipy_parity_compares_against_cpu_reference_summary(self) -> None:
        module = __import__("scripts.goal859_spatial_summary_baseline", fromlist=["_profile_service_scipy"])

        fake_case = {
            "households": (),
            "clinics": (),
        }
        fake_rows = ()
        fake_summary = {
            "household_count": 0,
            "clinic_count": 0,
            "covered_household_count": 0,
            "uncovered_household_count": 0,
            "uncovered_household_ids": [],
        }
        fake_payload = dict(fake_summary)

        with mock.patch.object(module.service_app, "make_service_coverage_case", return_value=fake_case), \
             mock.patch.object(module.service_app, "_run_rows", return_value=fake_rows), \
             mock.patch.object(module, "_service_summary_from_rows", return_value=fake_summary), \
             mock.patch.object(module.service_app, "run_case", return_value=fake_payload):
            artifact = module.build_artifact(
                app_name="service_coverage_gaps",
                backend="scipy",
                copies=2,
                iterations=1,
            )

        self.assertTrue(artifact["correctness_parity"])
        self.assertEqual(artifact["baseline_name"], "scipy_baseline_when_available")

    def test_rejects_bad_arguments(self) -> None:
        module = __import__("scripts.goal859_spatial_summary_baseline", fromlist=["build_artifact"])
        with self.assertRaisesRegex(ValueError, "iterations must be positive"):
            module.build_artifact(
                app_name="service_coverage_gaps",
                backend="cpu",
                copies=2,
                iterations=0,
            )
        with self.assertRaisesRegex(ValueError, "unsupported app/backend combination"):
            module.build_artifact(
                app_name="service_coverage_gaps",
                backend="bogus",
                copies=2,
                iterations=1,
            )


if __name__ == "__main__":
    unittest.main()

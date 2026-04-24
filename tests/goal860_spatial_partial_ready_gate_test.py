from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal860SpatialPartialReadyGateTest(unittest.TestCase):
    def test_gate_reports_spatial_rows_only(self) -> None:
        module = __import__("scripts.goal860_spatial_partial_ready_gate", fromlist=["build_spatial_gate"])
        payload = module.build_spatial_gate()
        self.assertEqual(payload["row_count"], 2)
        apps = {row["app"] for row in payload["rows"]}
        self.assertEqual(apps, {"service_coverage_gaps", "event_hotspot_screening"})

    def test_gate_tracks_optional_scipy_separately(self) -> None:
        module = __import__("scripts.goal860_spatial_partial_ready_gate", fromlist=["build_spatial_gate"])
        rows = {row["app"]: row for row in module.build_spatial_gate()["rows"]}
        for app in ("service_coverage_gaps", "event_hotspot_screening"):
            with self.subTest(app=app):
                self.assertEqual(len(rows[app]["required_checks"]), 2)
                self.assertEqual(len(rows[app]["optional_checks"]), 1)
                self.assertEqual(rows[app]["optional_checks"][0]["baseline"], "scipy_baseline_when_available")

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "gate.json"
            output_md = Path(tmpdir) / "gate.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal860_spatial_partial_ready_gate.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            output_md_exists = output_md.exists()

        self.assertIn("Goal860 Spatial Partial-Ready Gate", completed.stdout)
        self.assertEqual(payload["row_count"], 2)
        self.assertTrue(output_md_exists)


if __name__ == "__main__":
    unittest.main()

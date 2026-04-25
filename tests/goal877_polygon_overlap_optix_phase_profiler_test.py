from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import goal877_polygon_overlap_optix_phase_profiler as goal877


ROOT = Path(__file__).resolve().parents[1]


def _candidate_pairs(*_args, **_kwargs):
    return {(1, 10), (2, 11)}


class Goal877PolygonOverlapOptixPhaseProfilerTest(unittest.TestCase):
    def test_dry_run_records_schema_without_optix(self) -> None:
        payload = goal877.run_profile(app="pair_overlap", mode="dry-run", copies=1)
        self.assertEqual(payload["status"], "pass")
        self.assertIsNone(payload["phases"]["optix_candidate_discovery_sec"])
        self.assertIsNone(payload["parity_vs_cpu"])
        self.assertIn("candidate discovery", payload["boundary"])

    def test_pair_overlap_mocked_optix_phase_parity(self) -> None:
        with mock.patch.object(goal877.pair_app, "_positive_candidate_pairs_optix", side_effect=_candidate_pairs):
            payload = goal877.run_profile(app="pair_overlap", mode="optix", copies=1)
        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["parity_vs_cpu"])
        self.assertIsNotNone(payload["phases"]["optix_candidate_discovery_sec"])
        self.assertFalse(payload["optix_metadata"]["rt_core_accelerated"])
        self.assertTrue(payload["optix_metadata"]["rt_core_candidate_discovery_active"])

    def test_jaccard_mocked_optix_phase_parity(self) -> None:
        with mock.patch.object(goal877.jaccard_app, "_positive_candidate_pairs_optix", side_effect=_candidate_pairs):
            payload = goal877.run_profile(app="jaccard", mode="optix", copies=1)
        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["parity_vs_cpu"])
        self.assertIsNotNone(payload["phases"]["cpu_exact_refinement_sec"])

    def test_pair_overlap_summary_analytic_chunks_without_cpu_reference(self) -> None:
        with mock.patch.object(goal877.pair_app, "_positive_candidate_pairs_optix", side_effect=_candidate_pairs):
            payload = goal877.run_profile(
                app="pair_overlap",
                mode="optix",
                copies=2,
                output_mode="summary",
                validation_mode="analytic_summary",
                chunk_copies=1,
            )
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["output_mode"], "summary")
        self.assertEqual(payload["validation_mode"], "analytic_summary")
        self.assertEqual(payload["chunk_count"], 2)
        self.assertIsNone(payload["phases"]["cpu_reference_sec"])
        self.assertTrue(payload["parity_vs_cpu"])
        self.assertEqual(payload["optix_digest"]["summary"]["overlap_pair_count"], 4)

    def test_jaccard_summary_analytic_chunks_without_cpu_reference(self) -> None:
        with mock.patch.object(goal877.jaccard_app, "_positive_candidate_pairs_optix", side_effect=_candidate_pairs):
            payload = goal877.run_profile(
                app="jaccard",
                mode="optix",
                copies=2,
                output_mode="summary",
                validation_mode="analytic_summary",
                chunk_copies=1,
            )
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["chunk_count"], 2)
        self.assertTrue(payload["parity_vs_cpu"])
        self.assertEqual(payload["optix_digest"]["summary"]["intersection_area"], 10)
        self.assertAlmostEqual(payload["optix_digest"]["summary"]["jaccard_similarity"], 5 / 19)

    def test_cli_writes_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "profile.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal877_polygon_overlap_optix_phase_profiler.py",
                    "--app",
                    "pair_overlap",
                    "--mode",
                    "dry-run",
                    "--output-json",
                    str(output_json),
                ],
                cwd=ROOT,
                env={**os.environ, "PYTHONPATH": "src:."},
                check=True,
                capture_output=True,
                text=True,
            )
            stdout = json.loads(completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(stdout["output_json"], str(output_json))
            self.assertEqual(payload["status"], "pass")


if __name__ == "__main__":
    unittest.main()

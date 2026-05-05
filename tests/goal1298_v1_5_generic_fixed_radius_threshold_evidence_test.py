from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.goal1298_v1_5_generic_fixed_radius_threshold_evidence import make_fixed_radius_case
from scripts.goal1298_v1_5_generic_fixed_radius_threshold_evidence import run_evidence


ROOT = Path(__file__).resolve().parents[1]


class Goal1298V15GenericFixedRadiusThresholdEvidenceTest(unittest.TestCase):
    def test_case_has_one_threshold_reached_query_per_copy(self) -> None:
        case = make_fixed_radius_case(3)

        self.assertEqual(len(case["query_points"]), 6)
        self.assertEqual(len(case["search_points"]), 6)
        self.assertEqual([point.id for point in case["query_points"]], [1, 2, 11, 12, 21, 22])

    def test_cpu_only_evidence_payload_passes_parity(self) -> None:
        payload = run_evidence(copies=4, radius=1.0, threshold=2, backends=("cpu",))

        self.assertTrue(payload["all_parity_checks_passed"])
        self.assertEqual(payload["expected_threshold_reached_count"], 4)
        self.assertEqual(payload["results"]["cpu_direct"]["threshold_reached_count"], 4)
        self.assertTrue(payload["parity"]["cpu_matches_expected"])

    def test_cli_writes_cpu_only_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "goal1298.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1298_v1_5_generic_fixed_radius_threshold_evidence.py",
                    "--copies",
                    "2",
                    "--backends",
                    "cpu",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )

            self.assertIn("all_parity_checks_passed", completed.stdout)
            payload = json.loads(output.read_text())
            self.assertTrue(payload["all_parity_checks_passed"])
            self.assertEqual(payload["expected_threshold_reached_count"], 2)


if __name__ == "__main__":
    unittest.main()

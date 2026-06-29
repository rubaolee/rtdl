from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V4Goal4806RayJoinNumbaCandidateProbeTest(unittest.TestCase):
    def test_dry_run_writes_measured_candidate_schema_without_perf_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_json = root / "candidate_measurements.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/rayjoin_section57_numba_candidate_probe.py",
                    "--dry-run",
                    "--dataset-root",
                    str(root / "missing_inputs"),
                    "--pairs",
                    "county_zipcode",
                    "--output-json",
                    str(output_json),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            payload = json.loads(completed.stdout)
            file_payload = json.loads(output_json.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.v4.rayjoin.section57_numba_measured_candidates.v1")
        self.assertEqual(file_payload["schema"], payload["schema"])
        self.assertEqual(payload["status"], "dry_run")
        self.assertEqual(payload["rows"], [])
        self.assertEqual(payload["planned_pairs"][0]["pair_id"], "county_zipcode")
        self.assertIn("v4_numba_post_traversal_segmented_counts", payload["planned_pairs"][0]["candidate_plans"])


if __name__ == "__main__":
    unittest.main()

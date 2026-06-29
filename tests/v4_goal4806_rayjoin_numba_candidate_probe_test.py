from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V4Goal4806RayJoinNumbaCandidateProbeTest(unittest.TestCase):
    def test_real_probe_uses_exact_device_columns_not_candidate_stream(self) -> None:
        script = (ROOT / "scripts" / "rayjoin_section57_numba_candidate_probe.py").read_text(encoding="utf-8")
        self.assertIn("prepared.exact_device_columns_prepared_left(", script)
        self.assertIn('with _rayjoin_lsi_predicate_env("optix"):', script)
        self.assertIn('"primitive_source": "exact_device_columns_prepared_left"', script)
        self.assertIn('"intersection_point_x"', script)
        self.assertIn('"intersection_point_columns_present"', script)
        self.assertNotIn("prepared.candidate_device_columns(", script)

    def test_stage_count_pass_without_full_hash_is_not_selector_pass(self) -> None:
        from scripts.rayjoin_section57_numba_candidate_probe import _candidate_status_from_stage

        status, hash_confirmed = _candidate_status_from_stage(
            stage_counts_pass=True,
            topology_geometry_hash_match_confirmed=False,
        )

        self.assertEqual(status, "stage_count_pass_full_overlay_hash_not_confirmed")
        self.assertFalse(hash_confirmed)

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

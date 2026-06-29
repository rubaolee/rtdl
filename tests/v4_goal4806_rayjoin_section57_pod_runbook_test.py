from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V4Goal4806RayJoinSection57PodRunbookTest(unittest.TestCase):
    def test_preflight_only_writes_machine_readable_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_dir = root / "out"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/rayjoin_section57_pod_runbook.py",
                    "--preflight-only",
                    "--dataset-root",
                    str(root / "missing_inputs"),
                    "--query-exec",
                    str(root / "missing_author" / "query_exec"),
                    "--polyover-exec",
                    str(root / "missing_author" / "polyover_exec"),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            payload = json.loads(completed.stdout)
            preflight = json.loads((output_dir / "section57_preflight.json").read_text(encoding="utf-8"))
            runbook = json.loads((output_dir / "section57_pod_runbook.json").read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.rayjoin.section57_pod_runbook.v1")
        self.assertEqual(payload["status"], "preflight_only_blocked")
        self.assertEqual(runbook["schema"], payload["schema"])
        self.assertFalse(payload["ready_for_performance_run"])
        self.assertIn("missing_exact_section57_cdb_inputs", payload["blockers"])
        self.assertIn("missing_rayjoin_author_binaries", payload["blockers"])
        self.assertEqual(preflight["schema"], "rtdl.rayjoin.section57_preflight.v1")
        self.assertTrue(preflight["section57_device_columns"]["static_components_declared"])
        self.assertEqual(
            preflight["section57_device_columns"]["end_to_end_composition_status"],
            "components_present_pod_validation_required",
        )

    def test_dry_run_continues_after_blocked_preflight_without_measuring(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_dir = root / "out"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/rayjoin_section57_pod_runbook.py",
                    "--dry-run",
                    "--dataset-root",
                    str(root / "missing_inputs"),
                    "--query-exec",
                    str(root / "missing_author" / "query_exec"),
                    "--polyover-exec",
                    str(root / "missing_author" / "polyover_exec"),
                    "--output-dir",
                    str(output_dir),
                    "--pairs",
                    "county_zipcode",
                    "--implementations",
                    "author_rt,v4_numba",
                    "--v4-numba-section57-device-columns-ready",
                    "--v4-numba-measurements",
                    str(root / "candidate_measurements.json"),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            payload = json.loads(completed.stdout)
            run_payload = json.loads((output_dir / "section57_overlay_run.json").read_text(encoding="utf-8"))
            summary_payload = json.loads((output_dir / "section57_overlay_summary.json").read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "dry_run_complete")
        self.assertEqual(payload["steps"][-1]["step"], "run")
        self.assertEqual(run_payload["schema"], "rtdl.rayjoin.section57_overlay_matrix.run.v1")
        self.assertTrue(any(row["status"] == "dry_run" for row in run_payload["attempts"]))
        self.assertEqual(summary_payload["coverage"]["overlay_pairs_total"], 1)
        self.assertEqual(summary_payload["coverage"]["overlay_pairs_complete"], 0)
        run_command = next(
            row["command"]
            for row in run_payload["attempts"]
            if row.get("implementation") == "v4_numba"
        )
        self.assertIn("--section57-device-columns-ready", run_command)
        self.assertIn("--v4-numba-measurements", run_command)


if __name__ == "__main__":
    unittest.main()

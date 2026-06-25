from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v4_point_group_nearest_witness_device_outputs_validation.py"


class V4PointGroupNearestWitnessDeviceOutputsValidationTest(unittest.TestCase):
    def test_dry_run_records_measured_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "point_group_gate.json"
            md_out = Path(tmp) / "point_group_gate.md"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--query-counts",
                    "16,32",
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            )
            payload = json.loads(json_out.read_text(encoding="utf-8"))
            stdout_payload = json.loads(proc.stdout)
            markdown = md_out.read_text(encoding="utf-8")

        self.assertEqual("dry_run", payload["status"])
        self.assertEqual("dry_run", stdout_payload["status"])
        self.assertEqual("measured_surface_dry_run", payload["surface_status"])
        self.assertEqual([16, 32], payload["query_counts"])
        self.assertFalse(payload["release_claim_authorized"])
        self.assertFalse(payload["broad_v4_speedup_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertIn("not a release authorization", markdown)


if __name__ == "__main__":
    unittest.main()

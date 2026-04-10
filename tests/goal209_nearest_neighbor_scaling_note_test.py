from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.internal.rtdl_v0_4_nearest_neighbor_scaling_note import run_scaling_note


class Goal209NearestNeighborScalingNoteTest(unittest.TestCase):
    def test_run_scaling_note_returns_contract_shaped_payload(self):
        payload = run_scaling_note(repeats=1, case_names=("fixture",))
        self.assertEqual(payload["repeats"], 1)
        self.assertEqual(len(payload["cases"]), 2)
        workloads = {entry["workload"] for entry in payload["cases"]}
        self.assertEqual(workloads, {"fixed_radius_neighbors", "knn_rows"})
        for entry in payload["cases"]:
            self.assertEqual(entry["case"], "fixture")
            self.assertGreater(entry["query_count"], 0)
            self.assertGreater(entry["search_count"], 0)
            self.assertTrue(entry["results"])
            for result in entry["results"]:
                self.assertTrue(result["parity_ok"])
                self.assertGreaterEqual(result["rows"], 0)
                self.assertGreaterEqual(result["median_ms"], 0.0)

    def test_cli_writes_json_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "scaling.json"
            command = [
                sys.executable,
                str(ROOT / "examples" / "internal" / "rtdl_v0_4_nearest_neighbor_scaling_note.py"),
                "--repeats",
                "1",
                "--case",
                "fixture",
                "--output",
                str(output),
            ]
            subprocess.run(command, check=True, cwd=ROOT)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["repeats"], 1)
            self.assertEqual(len(payload["cases"]), 2)


if __name__ == "__main__":
    unittest.main()

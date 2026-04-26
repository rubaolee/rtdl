from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal982GraphSameScaleTimingRepairTest(unittest.TestCase):
    def test_collects_positive_embree_native_query_timing(self) -> None:
        module = __import__(
            "scripts.goal982_graph_same_scale_timing_repair",
            fromlist=["collect"],
        )
        payload = module.collect(copies=256, repeats=1, write=False)
        report = payload["report"]
        artifact = payload["artifact"]
        self.assertEqual(report["status"], "ok")
        self.assertGreater(report["phase_seconds"]["native_query"], 0.0)
        self.assertFalse(report["public_speedup_claim_authorized"])
        self.assertTrue(artifact["correctness_parity"])
        self.assertEqual(artifact["phase_seconds"]["native_query"], report["phase_seconds"]["native_query"])

    def test_cli_writes_report_without_mutating_baseline_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal982.json"
            output_md = Path(tmpdir) / "goal982.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal982_graph_same_scale_timing_repair.py",
                    "--copies",
                    "256",
                    "--repeats",
                    "1",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "ok")
            self.assertFalse(payload["wrote_artifact"])
            self.assertIn("public_speedup_claim_authorized", completed.stdout)
            self.assertIn("Graph Same-Scale Timing Repair", output_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

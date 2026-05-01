from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal980GraphBaselineCorrectnessAuditTest(unittest.TestCase):
    def test_audit_confirms_graph_embree_correctness_repair(self) -> None:
        module = __import__(
            "scripts.goal980_graph_baseline_correctness_audit",
            fromlist=["audit"],
        )
        payload = module.audit((1, 2, 16))
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["mismatch_count"], 0)
        self.assertFalse(payload["public_speedup_claim_authorized"])
        rows = {row["copies"]: row for row in payload["rows"]}
        self.assertEqual(rows[1]["status"], "ok")
        self.assertEqual(rows[2]["status"], "ok")
        self.assertEqual(rows[16]["status"], "ok")
        self.assertEqual(rows[2]["mismatches"], {})
        self.assertEqual(rows[16]["mismatches"], {})

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal980.json"
            output_md = Path(tmpdir) / "goal980.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal980_graph_baseline_correctness_audit.py",
                    "--copies",
                    "1",
                    "--copies",
                    "2",
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
            self.assertTrue(output_md.exists())
            self.assertIn("graph local correctness check passed", output_md.read_text(encoding="utf-8"))
            self.assertIn('"public_speedup_claim_authorized": false', completed.stdout)


if __name__ == "__main__":
    unittest.main()

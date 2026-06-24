from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v4_catalog_regression_gate.py"


class V4CatalogRegressionGateTest(unittest.TestCase):
    def test_dry_run_gate_executes_all_catalog_examples(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "catalog.json"
            md_out = tmp_path / "catalog.md"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--mode",
                    "dry-run",
                    "--copies",
                    "16",
                    "--ray-count",
                    "16",
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

        self.assertEqual("passed", payload["status"])
        self.assertEqual("passed", stdout_payload["status"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["tier3_callback_claim_authorized"])
        self.assertEqual(7, len(payload["examples"]))
        self.assertTrue(all(row["passed"] for row in payload["examples"]))
        names = {row["name"] for row in payload["examples"]}
        self.assertIn("fixed_radius", names)
        self.assertIn("v4_frontdoor_quickstart", names)
        self.assertIn("operator_callback_planning_complex_callback", names)
        self.assertIn("Status: generated development gate", markdown)


if __name__ == "__main__":
    unittest.main()


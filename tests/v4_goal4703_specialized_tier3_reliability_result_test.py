from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4_maintainer as v4


SCRIPT = ROOT / "scripts" / "v4_goal4703_specialized_tier3_reliability_matrix_pod.py"


class V4Goal4703SpecializedTier3ReliabilityResultTest(unittest.TestCase):
    def test_result_contract_classifies_pass_and_fail_without_authorization(self) -> None:
        validation = v4.validate_v4_goal4703_specialized_tier3_reliability_result_contract()
        self.assertEqual("passed", validation["status"])
        self.assertEqual("pass_reliability_gate_not_public_support", validation["passing_example"]["classification"])
        self.assertEqual(
            "fail_reliability_gate_repair_before_public_support",
            validation["failing_example"]["classification"],
        )
        self.assertFalse(validation["passing_example"]["tier3_public_support_authorized"])

    def test_dry_run_script_emits_contract_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "goal4703.json"
            md_out = tmp_path / "goal4703.md"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
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

        self.assertEqual("dry_run_contract_passed", payload["status"])
        self.assertEqual("dry_run_contract_passed", stdout_payload["status"])
        self.assertEqual(20, payload["protocol"]["total_attempts"])
        self.assertIn("Reliability Matrix", markdown)


if __name__ == "__main__":
    unittest.main()

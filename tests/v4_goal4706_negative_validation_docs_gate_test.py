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

import rtdsl.v4 as v4


SCRIPT = ROOT / "scripts" / "v4_goal4706_negative_validation_docs_gate.py"
EXAMPLE = ROOT / "future" / "v4" / "examples" / "v4_specialized_tier3_scalar_callback_candidate_example.py"


class V4Goal4706NegativeValidationDocsGateTest(unittest.TestCase):
    def test_negative_validation_rejects_before_compile(self) -> None:
        validation = v4.validate_v4_goal4706_negative_validation_docs_gate()
        gate = validation["gate"]
        self.assertEqual("passed", validation["status"])
        self.assertEqual("compile_cache_ready_not_executed", gate["accepted_example_status"])
        self.assertGreaterEqual(len(gate["negative_rows"]), 5)
        for row in gate["negative_rows"]:
            self.assertEqual("rejected_before_compile", row["stage"])
            self.assertFalse(row["internal_compile_allowed"])
            self.assertTrue(row["error_code"].startswith("RTDL_V4_TIER3_CALLBACK_REJECTED"))

    def test_example_runs_without_public_support(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(EXAMPLE)],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        payload = json.loads(proc.stdout)
        self.assertEqual("compile_cache_ready_not_executed", payload["compile_stage"])
        self.assertTrue(payload["internal_compile_allowed"])
        self.assertFalse(payload["tier3_public_support_authorized"])

    def test_script_emits_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "negative.json"
            md_out = tmp_path / "negative.md"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
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

        self.assertEqual("passed", payload["validation_status"])
        self.assertEqual("passed", stdout_payload["validation_status"])
        self.assertIn("Negative Rows", markdown)


if __name__ == "__main__":
    unittest.main()

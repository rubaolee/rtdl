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


SCRIPT = ROOT / "scripts" / "v4_goal4704_specialized_tier3_support_wording.py"


class V4Goal4704SpecializedTier3SupportWordingTest(unittest.TestCase):
    def test_wording_gate_preserves_public_support_boundary(self) -> None:
        validation = v4.validate_v4_goal4704_specialized_tier3_support_wording()
        gate = validation["gate"]
        self.assertEqual("passed", validation["status"])
        self.assertIn("not public support and not release wording", gate["allowed_internal_wording"])
        self.assertIn("V4 supports arbitrary callbacks", gate["prohibited_public_wording"])
        self.assertFalse(gate["tier3_public_support_authorized"])
        self.assertFalse(gate["performance_claim_authorized"])

    def test_claim_boundary_exposes_candidate_but_not_public_support(self) -> None:
        boundary = v4.claim_boundary_v4()
        self.assertEqual(
            "specialized_numba_scalar_callback_support_candidate",
            boundary["tier3_specialized_callback_candidate_label"],
        )
        self.assertFalse(boundary["tier3_callback_claim_authorized"])
        self.assertFalse(boundary["tier3_specialized_callback_public_support_authorized"])

    def test_script_emits_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "wording.json"
            md_out = tmp_path / "wording.md"
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
        self.assertIn("Prohibited Public Wording", markdown)


if __name__ == "__main__":
    unittest.main()

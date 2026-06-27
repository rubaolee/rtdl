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


SCRIPT = ROOT / "scripts" / "v4_goal4696_tier3_productization_decision.py"


class V4Goal4696Tier3ProductizationDecisionTest(unittest.TestCase):
    def test_decision_is_constrained_candidate_not_public_support(self) -> None:
        validation = v4.validate_v4_goal4696_tier3_productization_decision()
        decision = validation["decision"]

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertEqual("module_specialized_direct_device_callback", decision["productization_candidate"])
        self.assertIn("arbitrary_python_callback", decision["rejected_callback_shapes"])
        self.assertIn("action_or_side_effect_callback", decision["rejected_callback_shapes"])
        self.assertIn("at least one app-route validation using the specialized callback path", decision["required_before_public_support"])
        self.assertFalse(decision["tier3_public_support_authorized"])

    def test_decision_script_emits_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "decision.json"
            md_out = tmp_path / "decision.md"
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
        self.assertIn("not public Tier-3 support", markdown)


if __name__ == "__main__":
    unittest.main()

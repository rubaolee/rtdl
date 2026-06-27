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


SCRIPT = ROOT / "scripts" / "v4_goal4692_tier3_support_decision.py"


class V4Goal4692Tier3SupportDecisionTest(unittest.TestCase):
    def test_decision_blocks_direct_callable_support_and_selects_next_track(self) -> None:
        validation = v4.validate_v4_goal4692_tier3_support_decision()
        decision = validation["decision"]

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertGreater(decision["measured_direct_callable_ratio"], 1.50)
        self.assertLess(decision["measured_direct_callable_ratio"], 2.00)
        self.assertEqual("module_specialized_direct_device_callback_in_hit_program", decision["selected_next_track"])
        self.assertFalse(decision["direct_callable_public_support_authorized"])
        self.assertFalse(decision["tier3_public_support_authorized"])
        self.assertFalse(decision["release_authorized"])

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
        self.assertIn("module-specialized direct device callback", markdown)
        self.assertFalse(payload["decision"]["release_authorized"])


if __name__ == "__main__":
    unittest.main()

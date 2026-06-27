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


SCRIPT = ROOT / "scripts" / "v4_goal4710_custom_scored_app_protocol.py"


class V4Goal4710CustomScoredAppProtocolTest(unittest.TestCase):
    def test_protocol_freezes_bars_and_denominators(self) -> None:
        validation = v4.validate_v4_goal4710_custom_scored_app_protocol()
        protocol = validation["protocol"]
        self.assertEqual("passed", validation["status"])
        self.assertIn("affine_score", protocol["primary_callbacks"])
        self.assertIn("weighted_sum", protocol["control_callbacks"])
        self.assertTrue(protocol["pod_authorized_for_next_goal"])
        self.assertFalse(protocol["app_level_speed_claim_authorized"])
        self.assertTrue(any(">=1.50x" in item for item in protocol["pass_conditions"]))
        self.assertTrue(any("V2/V3 denominator discovery" in item for item in protocol["kill_conditions"]))

    def test_script_emits_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "protocol.json"
            md_out = tmp_path / "protocol.md"
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
        self.assertIn("Custom Scored App Protocol", markdown)


if __name__ == "__main__":
    unittest.main()

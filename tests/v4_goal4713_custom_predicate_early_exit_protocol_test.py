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

from rtdsl.v4_goal4713_custom_predicate_early_exit_protocol import (
    validate_v4_goal4713_custom_predicate_early_exit_protocol,
)


SCRIPT = ROOT / "scripts" / "v4_goal4713_custom_predicate_early_exit_protocol.py"


class V4Goal4713CustomPredicateEarlyExitProtocolTest(unittest.TestCase):
    def test_protocol_freezes_cost_model_and_bars(self) -> None:
        validation = validate_v4_goal4713_custom_predicate_early_exit_protocol()
        self.assertEqual("passed", validation["status"])
        protocol = validation["protocol"]
        primary = {row["name"] for row in protocol["primary_regimes"]}
        self.assertIn("dense_early_accept_k32", primary)
        self.assertTrue(any(row["candidate_hits_per_ray"] >= 32 for row in protocol["primary_regimes"]))
        self.assertTrue(any(">=1.50x" in item for item in protocol["pass_conditions"]))
        self.assertTrue(any("early termination" in item for item in protocol["kill_conditions"]))
        self.assertFalse(protocol["pod_authorized"])
        self.assertFalse(protocol["formal_high_performance_authorized"])

    def test_script_emits_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "goal4713.json"
            md_out = tmp_path / "goal4713.md"
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
        self.assertEqual("passed", payload["status"])
        self.assertEqual("passed", stdout_payload["status"])
        self.assertIn("Custom Predicate Early-Exit Protocol", markdown)


if __name__ == "__main__":
    unittest.main()

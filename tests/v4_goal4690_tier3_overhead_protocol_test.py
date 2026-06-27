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


SCRIPT = ROOT / "scripts" / "v4_goal4690_tier3_overhead_protocol.py"


class V4Goal4690Tier3OverheadProtocolTest(unittest.TestCase):
    def test_protocol_freezes_numeric_bars_and_baselines(self) -> None:
        validation = v4.validate_v4_goal4690_tier3_overhead_protocol()
        protocol = validation["protocol"]

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertEqual(1_000_000, protocol["inner_iterations"])
        self.assertEqual(5, protocol["warmup_launches"])
        self.assertEqual(30, protocol["measured_launches"])
        self.assertEqual(1.50, protocol["pass_ratio_max"])
        self.assertEqual(2.00, protocol["hard_kill_ratio_min"])
        self.assertIn("direct_device_function_loop_same_numba_callback", protocol["baseline_variants"])
        self.assertIn("optix_direct_callable_loop_same_numba_callback", protocol["measured_variants"])
        self.assertFalse(protocol["performance_claim_authorized"])

    def test_protocol_script_emits_json_and_markdown(self) -> None:
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
        self.assertIn("direct_callable_loop_median_ms", markdown)
        self.assertFalse(payload["protocol"]["release_authorized"])


if __name__ == "__main__":
    unittest.main()

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


SCRIPT = ROOT / "scripts" / "v4_goal4691_tier3_overhead_measurement.py"


class V4Goal4691Tier3OverheadMeasurementTest(unittest.TestCase):
    def test_classification_thresholds(self) -> None:
        self.assertEqual("pass_overhead_gate_not_support", v4.classify_v4_goal4691_overhead_ratio(1.50))
        self.assertEqual("yellow_overhead_between_pass_and_kill", v4.classify_v4_goal4691_overhead_ratio(1.51))
        self.assertEqual("yellow_overhead_between_pass_and_kill", v4.classify_v4_goal4691_overhead_ratio(2.00))
        self.assertEqual("hard_kill_overhead_too_high", v4.classify_v4_goal4691_overhead_ratio(2.01))
        self.assertEqual("blocked_no_ratio", v4.classify_v4_goal4691_overhead_ratio(None))

    def test_contract_validation_passes(self) -> None:
        validation = v4.validate_v4_goal4691_tier3_overhead_measurement_contract()

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertFalse(validation["release_authorized"])
        self.assertFalse(validation["tier3_public_support_authorized"])

    def test_dry_run_script_passes_contract_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "probe.json"
            md_out = tmp_path / "probe.md"
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

        self.assertEqual("dry_run_contract_passed", payload["status"])
        self.assertEqual("dry_run_contract_passed", stdout_payload["status"])
        self.assertFalse(payload["performance_claim_authorized"])


if __name__ == "__main__":
    unittest.main()

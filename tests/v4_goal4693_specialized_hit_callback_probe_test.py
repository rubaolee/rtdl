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


SCRIPT = ROOT / "scripts" / "v4_goal4693_specialized_hit_callback_probe.py"


class V4Goal4693SpecializedHitCallbackProbeTest(unittest.TestCase):
    def test_contract_validation_passes(self) -> None:
        validation = v4.validate_v4_goal4693_specialized_hit_callback_probe_contract()

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertTrue(validation["uses_optix_trace"])
        self.assertTrue(validation["uses_hit_program"])
        self.assertFalse(validation["uses_sbt_direct_callable"])
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
        self.assertFalse(payload["uses_sbt_direct_callable"])


if __name__ == "__main__":
    unittest.main()

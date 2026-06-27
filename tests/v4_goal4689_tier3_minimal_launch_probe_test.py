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


SCRIPT = ROOT / "scripts" / "v4_goal4689_tier3_minimal_launch_probe.py"


class V4Goal4689Tier3MinimalLaunchProbeTest(unittest.TestCase):
    def test_contract_validation_passes_and_blocks_claims(self) -> None:
        validation = v4.validate_v4_goal4689_tier3_minimal_launch_probe_contract()

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertEqual(5.0, validation["expected_output"])
        self.assertFalse(validation["pod_authorized"])
        self.assertFalse(validation["tier3_public_support_authorized"])
        self.assertFalse(validation["release_authorized"])
        self.assertFalse(validation["performance_claim_authorized"])

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
        self.assertFalse(payload["pipeline_launch_attempted"])
        self.assertFalse(payload["tier3_public_support_authorized"])

    def test_launch_wrapper_uses_optix_direct_call(self) -> None:
        scripts_dir = ROOT / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        import v4_goal4689_tier3_minimal_launch_probe as script

        source = script.goal4689_launch_wrapper_source("rtdl_user_scalar_reduce")

        self.assertIn("optixDirectCall<void>(0)", source)
        self.assertIn("__direct_callable__rtdl_tier3_scalar_reduce", source)
        self.assertIn("rtdl_user_scalar_reduce", source)


if __name__ == "__main__":
    unittest.main()

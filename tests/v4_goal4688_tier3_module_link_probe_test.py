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
from rtdsl.v4_goal4688_tier3_module_link_probe import compose_goal4688_combined_ptx


SCRIPT = ROOT / "scripts" / "v4_goal4688_tier3_module_link_probe.py"


class V4Goal4688Tier3ModuleLinkProbeTest(unittest.TestCase):
    def test_combined_ptx_has_single_header_and_both_bodies(self) -> None:
        callback = ".version 8.0\n.target sm_75\n.address_size 64\n\n.visible .func callback_func(){ret;}\n"
        wrapper = ".version 8.0\n.target sm_75\n.address_size 64\n\n.extern .func callback_func();\n.visible .entry __raygen__rtdl_tier3_probe(){ret;}\n"
        combined = compose_goal4688_combined_ptx(callback, wrapper)

        self.assertEqual(1, combined.count(".version"))
        self.assertIn("callback_func", combined)
        self.assertIn("__raygen__rtdl_tier3_probe", combined)
        self.assertNotIn(".extern .func callback_func", combined)

    def test_contract_validation_passes(self) -> None:
        validation = v4.validate_v4_goal4688_tier3_module_link_probe_contract()

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertFalse(validation["pod_authorized"])
        self.assertFalse(validation["tier3_public_support_authorized"])
        self.assertFalse(validation["raw_optix_callback_authorized"])
        self.assertFalse(validation["release_authorized"])

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
        self.assertFalse(payload["optix_module_link_attempted"])
        self.assertFalse(payload["pipeline_launch_attempted"])


if __name__ == "__main__":
    unittest.main()

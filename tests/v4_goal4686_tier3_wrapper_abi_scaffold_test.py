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


SCRIPT = ROOT / "scripts" / "v4_goal4686_tier3_wrapper_abi_scaffold.py"


class V4Goal4686Tier3WrapperAbiScaffoldTest(unittest.TestCase):
    def test_goal4686_scaffold_contains_semantic_optix_entries(self) -> None:
        scaffold = v4.v4_goal4686_tier3_wrapper_abi_scaffold().as_dict()
        source = scaffold["wrapper_source"]

        self.assertEqual("goal4686_tier3_wrapper_abi_local_scaffold_complete_no_pod", scaffold["status"])
        self.assertIn("__direct_callable__rtdl_tier3_scalar_reduce", source)
        self.assertIn("__raygen__rtdl_tier3_probe", source)
        self.assertIn("__miss__rtdl_tier3_probe", source)
        self.assertIn("__closesthit__rtdl_tier3_probe", source)
        self.assertIn("rtdl_user_scalar_reduce", source)
        self.assertFalse(scaffold["old_bare_ptx_success_path_allowed"])

    def test_goal4686_validation_passes_and_blocks_claims(self) -> None:
        validation = v4.validate_v4_goal4686_tier3_wrapper_abi_scaffold()
        scaffold = validation["scaffold"]

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertFalse(scaffold["pod_authorized"])
        self.assertFalse(scaffold["tier3_public_support_authorized"])
        self.assertFalse(scaffold["raw_optix_callback_authorized"])
        self.assertFalse(scaffold["release_authorized"])
        self.assertFalse(scaffold["public_speedup_claim_authorized"])
        self.assertFalse(scaffold["whole_app_speedup_claim_authorized"])
        self.assertFalse(scaffold["app_identity_kernel_authorized"])

    def test_goal4686_dry_run_script_emits_json_md_and_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "scaffold.json"
            md_out = tmp_path / "scaffold.md"
            source_out = tmp_path / "wrapper.cu"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                    "--source-out",
                    str(source_out),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            )
            payload = json.loads(json_out.read_text(encoding="utf-8"))
            stdout_payload = json.loads(proc.stdout)
            markdown = md_out.read_text(encoding="utf-8")
            source = source_out.read_text(encoding="utf-8")

        self.assertEqual("passed", payload["validation_status"])
        self.assertEqual("passed", stdout_payload["validation_status"])
        self.assertTrue(payload["dry_run_only"])
        self.assertFalse(payload["pod_authorized"])
        self.assertIn("not Tier-3 support", markdown)
        self.assertIn("__direct_callable__rtdl_tier3_scalar_reduce", source)


if __name__ == "__main__":
    unittest.main()

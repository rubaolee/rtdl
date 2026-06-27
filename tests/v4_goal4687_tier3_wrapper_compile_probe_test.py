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
from rtdsl.v4_goal4687_tier3_wrapper_compile_probe import extract_numba_callback_symbol_from_ptx
from rtdsl.v4_goal4687_tier3_wrapper_compile_probe import specialize_semantic_wrapper_source


SCRIPT = ROOT / "scripts" / "v4_goal4687_tier3_wrapper_compile_probe.py"


class V4Goal4687Tier3WrapperCompileProbeTest(unittest.TestCase):
    def test_symbol_extraction_from_numba_like_ptx(self) -> None:
        ptx = """
.visible .func  (.param .b64 func_retval0) _ZN8__main__21_custom_scalar_reduce_sample(
    .param .b64 _ZN8__main__21_custom_scalar_reduce_sample_param_0
)
{
    ret;
}
"""
        probe = extract_numba_callback_symbol_from_ptx(ptx)

        self.assertEqual("symbol_extracted", probe.status)
        self.assertEqual("_ZN8__main__21_custom_scalar_reduce_sample", probe.symbol)
        self.assertTrue(probe.c_identifier_compatible)

    def test_specialized_wrapper_replaces_placeholder_with_symbol(self) -> None:
        source = specialize_semantic_wrapper_source("_ZN8__main__21_custom_scalar_reduce_sample")

        self.assertIn("_ZN8__main__21_custom_scalar_reduce_sample", source)
        self.assertNotIn("rtdl_user_scalar_reduce", source)
        self.assertIn("__direct_callable__rtdl_tier3_scalar_reduce", source)
        self.assertIn("__raygen__rtdl_tier3_probe", source)

    def test_contract_validation_passes_without_pod(self) -> None:
        validation = v4.validate_v4_goal4687_tier3_wrapper_compile_probe_contract()

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
            markdown = md_out.read_text(encoding="utf-8")

        self.assertEqual("dry_run_contract_passed", payload["status"])
        self.assertEqual("dry_run_contract_passed", stdout_payload["status"])
        self.assertFalse(payload["wrapper_compile_attempted"])
        self.assertFalse(payload["optix_module_link_attempted"])
        self.assertIn("not Tier-3 support", markdown)


if __name__ == "__main__":
    unittest.main()

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


SCRIPT = ROOT / "scripts" / "v4_goal4698_specialized_tier3_compile_cache.py"


class V4Goal4698SpecializedTier3CompileCacheTest(unittest.TestCase):
    def test_compile_cache_validation_passes_and_cache_is_stable(self) -> None:
        validation = v4.validate_v4_goal4698_specialized_tier3_compile_cache()
        accepted = validation["accepted_plan"]
        changed = validation["changed_ptx_plan"]

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertEqual("compile_cache_ready_not_executed", accepted["stage"])
        self.assertTrue(accepted["internal_compile_allowed"])
        self.assertIsNotNone(accepted["cache_key"])
        self.assertNotEqual(accepted["cache_key"], changed["cache_key"])
        self.assertFalse(accepted["tier3_public_support_authorized"])
        self.assertFalse(accepted["release_authorized"])

    def test_rejected_and_incomplete_callbacks_fail_before_compile(self) -> None:
        validation = v4.validate_v4_goal4698_specialized_tier3_compile_cache()
        rejected = validation["rejected_plan"]
        incomplete = validation["incomplete_plan"]

        self.assertEqual("rejected_before_compile", rejected["stage"])
        self.assertIn("RTDL_V4_TIER3_CALLBACK_REJECTED", rejected["error_code"])
        self.assertFalse(rejected["internal_compile_allowed"])
        self.assertEqual("compile_input_incomplete", incomplete["stage"])
        self.assertEqual("RTDL_V4_TIER3_COMPILE_INPUT_INCOMPLETE", incomplete["error_code"])

    def test_compile_failure_classification_is_stage_specific(self) -> None:
        failure = v4.classify_v4_goal4698_compile_failure("optix_module_create", "bad module")

        self.assertEqual("classified_compile_failure", failure["status"])
        self.assertEqual("optix_module_create", failure["stage"])
        self.assertEqual("RTDL_V4_TIER3_COMPILE_STAGE_FAILED_OPTIX_MODULE_CREATE", failure["error_code"])
        self.assertFalse(failure["tier3_public_support_authorized"])

    def test_script_emits_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "compile_cache.json"
            md_out = tmp_path / "compile_cache.md"
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
        self.assertIn("not public Tier-3 support", markdown)


if __name__ == "__main__":
    unittest.main()

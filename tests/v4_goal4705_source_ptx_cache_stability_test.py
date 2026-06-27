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


SCRIPT = ROOT / "scripts" / "v4_goal4705_source_ptx_cache_stability_pod.py"


class V4Goal4705SourcePtxCacheStabilityTest(unittest.TestCase):
    def test_canonicalizer_normalizes_numba_env_version_only(self) -> None:
        ptx1 = ".common .global .align 8 .u64 _ZN08NumbaEnv33callbackB2v1B96;\n.visible .func f(){ret;}\n"
        ptx2 = ".common .global .align 8 .u64 _ZN08NumbaEnv33callbackB2v2B96;\n.visible .func f(){ret;}\n"
        ptx3 = ptx2 + "// real content change\n"
        self.assertEqual(
            v4.canonicalize_v4_goal4698_callback_ptx_for_cache(ptx1),
            v4.canonicalize_v4_goal4698_callback_ptx_for_cache(ptx2),
        )
        self.assertNotEqual(
            v4.canonicalize_v4_goal4698_callback_ptx_for_cache(ptx2),
            v4.canonicalize_v4_goal4698_callback_ptx_for_cache(ptx3),
        )

    def test_result_contract_classifies_cache_stability(self) -> None:
        validation = v4.validate_v4_goal4705_source_ptx_cache_stability_contract()
        self.assertEqual("passed", validation["status"])
        self.assertEqual(
            "pass_source_level_cache_stability_gate_not_public_support",
            validation["passing_example"]["classification"],
        )
        self.assertFalse(validation["passing_example"]["tier3_public_support_authorized"])

    def test_dry_run_script_emits_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "cache.json"
            md_out = tmp_path / "cache.md"
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
        self.assertIn("Source-Level PTX Cache Stability", markdown)


if __name__ == "__main__":
    unittest.main()

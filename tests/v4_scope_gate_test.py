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
from rtdsl.v4_scope import validate_v4_0_scope_gate
from rtdsl.v4_scope import v4_0_scope_gate


SCRIPT = ROOT / "scripts" / "v4_scope_gate.py"
DOC = ROOT / "future" / "v4" / "v4_0_scope_gate.md"


class V4ScopeGateTest(unittest.TestCase):
    def test_scope_gate_defines_v4_0_and_deferred_v4x(self) -> None:
        gate = v4_0_scope_gate()
        payload = gate.as_dict()

        self.assertEqual("v4_0_development_scope_defined_not_release", payload["status"])
        self.assertEqual(3, len(payload["included_surfaces"]))
        self.assertIn("tier2_fused_generic_rt_operators", payload["included_capabilities"])
        self.assertIn("tier3_numba_ptx_generation_spike_only", payload["deferred_capabilities"])
        self.assertIn("tier3_numba_bare_ptx_direct_optix_module_link_blocked", payload["deferred_capabilities"])
        self.assertIn("tier3_wrapper_direct_callable_abi", payload["deferred_capabilities"])
        self.assertIn("embedding_c_abi", payload["deferred_capabilities"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["tier3_callback_claim_authorized"])
        self.assertFalse(payload["raw_optix_callback_claim_authorized"])
        self.assertFalse(payload["embedding_c_abi_claim_authorized"])

    def test_scope_gate_validation_passes_current_payload(self) -> None:
        result = validate_v4_0_scope_gate()

        self.assertEqual("passed", result["status"])
        self.assertEqual((), result["missing_or_invalid"])
        self.assertFalse(result["release_authorized"])

    def test_scope_gate_is_reachable_from_unified_frontdoor(self) -> None:
        gate = v4.v4_0_scope_gate()
        result = v4.validate_v4_0_scope_gate(gate)

        self.assertEqual("passed", result["status"])
        self.assertFalse(gate.release_authorized)

    def test_scope_gate_script_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "scope.json"
            md_out = tmp_path / "scope.md"
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--json-out", str(json_out), "--md-out", str(md_out)],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            )
            payload = json.loads(json_out.read_text(encoding="utf-8"))
            stdout_payload = json.loads(proc.stdout)
            markdown = md_out.read_text(encoding="utf-8")

        self.assertEqual("passed", payload["validation"]["status"])
        self.assertEqual("passed", stdout_payload["validation"]["status"])
        self.assertFalse(payload["gate"]["release_authorized"])
        self.assertIn("Status: generated development gate", markdown)

    def test_scope_doc_records_non_claims(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("Deferred To V4.x", text)
        self.assertIn("tier3_numba_bare_ptx_direct_optix_module_link_blocked", text)
        self.assertIn("Tier-3 callback/PTX support", text)
        self.assertIn("embedding/C-ABI", text)
        self.assertIn("release authorized: `False`", text)


if __name__ == "__main__":
    unittest.main()

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


SCRIPT = ROOT / "scripts" / "v4_goal4697_specialized_tier3_api_contract.py"


class V4Goal4697SpecializedTier3ApiContractTest(unittest.TestCase):
    def test_contract_accepts_only_constrained_numba_scalar_candidate(self) -> None:
        validation = v4.validate_v4_goal4697_specialized_tier3_api_contract()
        contract = validation["contract"]
        accepted = validation["plans"]["accepted"]

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertEqual("module_specialized_direct_device_callback", contract["candidate_surface"])
        self.assertEqual("tier3_specialized_candidate_contract_accepted_not_public_support", accepted["status"])
        self.assertTrue(accepted["internal_productization_compile_path_allowed"])
        self.assertFalse(accepted["tier3_public_support_authorized"])
        self.assertFalse(accepted["release_authorized"])

    def test_contract_rejects_disallowed_callback_shapes(self) -> None:
        validation = v4.validate_v4_goal4697_specialized_tier3_api_contract()
        plans = validation["plans"]

        self.assertEqual("rejected_goal4697_arbitrary_python_callback", plans["rejected_python"]["status"])
        self.assertEqual("rejected_goal4697_action_or_side_effect_callback", plans["rejected_action"]["status"])
        self.assertEqual("rejected_goal4697_external_memory_mutation_callback", plans["rejected_external_memory"]["status"])
        self.assertEqual("rejected_goal4697_dynamic_sbt_direct_callable_hot_path", plans["rejected_sbt"]["status"])
        self.assertEqual("rejected_goal4697_non_scalar_callback_signature", plans["rejected_non_scalar"]["status"])
        for plan in plans.values():
            self.assertFalse(plan["raw_optix_callback_authorized"])
            self.assertFalse(plan["release_authorized"])

    def test_explicit_planner_keeps_public_support_false(self) -> None:
        plan = v4.plan_v4_goal4697_specialized_tier3_callback_contract(
            callback_shape="custom-score",
            callback_language="numba",
            numba_cabi_device_function=True,
        )

        self.assertTrue(plan.accepted)
        self.assertEqual("custom_score", plan.callback_shape)
        self.assertEqual("module_specialized_direct_device_callback", plan.internal_candidate_surface)
        self.assertTrue(plan.app_route_validation_required)
        self.assertFalse(plan.tier3_public_support_authorized)
        self.assertFalse(plan.performance_claim_authorized)

    def test_decision_script_emits_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "contract.json"
            md_out = tmp_path / "contract.md"
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

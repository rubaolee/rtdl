from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4_operator_catalog as catalog


PROTOCOL = ROOT / "future" / "v4" / "tier3_callback_spike_protocol_2026-06-24.md"


class V4Tier3CallbackSpikeProtocolTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = PROTOCOL.read_text(encoding="utf-8")

    def test_protocol_is_spike_only_and_names_the_accepted_shape(self) -> None:
        self.assertIn(catalog.V4_TIER3_CALLBACK_SPIKE_PROTOCOL_STATUS, self.text)
        self.assertIn("`scalar per-hit reduce only`", self.text)
        self.assertIn("Numba CUDA device function only", self.text)
        self.assertIn("one fixed tuple of at most four scalar values", self.text)
        self.assertIn("must not be documented as supported", self.text)

    def test_protocol_has_falsifiable_numeric_gates(self) -> None:
        self.assertIn("compile reliability floor: `>= 95%`", self.text)
        self.assertIn("correctness parity: `100%`", self.text)
        self.assertIn("overhead ceiling: median callback route time `<= 1.50x`", self.text)
        self.assertIn("no tested size may exceed `2.00x`", self.text)
        self.assertIn("warmup count: `>= 2`", self.text)
        self.assertIn("repeat count: `>= 10`", self.text)

    def test_protocol_rejects_action_shaped_callbacks(self) -> None:
        for phrase in (
            "shared mutation",
            "global memory mutation outside the fixed RTDL-owned output state",
            "dynamic allocation",
            "variable-length output",
            "recursion",
            "spawned action logic",
            "direct OptiX API calls",
            "raw OptiX callbacks as the public API",
            "application-identity kernels",
        ):
            self.assertIn(phrase, self.text)

    def test_protocol_preserves_non_authorization_boundary(self) -> None:
        for phrase in (
            "V4 release",
            "V4 release-candidate status",
            "measured-catalog promotion",
            "Tier-3 callback support",
            "raw OptiX callback support",
            "public true-zero-copy wording",
            "broad V4 speedup claims",
            "whole-application speedup claims",
            "C ABI / embedding / non-Python-host work",
            "app-specific native kernels",
        ):
            self.assertIn(phrase, self.text)

    def test_planner_marks_scalar_callbacks_as_protocol_only(self) -> None:
        plan = catalog.plan_v4_operator_request(
            "custom-force-score",
            callback_shape="custom_scalar_reduce",
            numba_device_function=True,
            partner="torch",
        )

        self.assertEqual("tier3_spike_only_not_v4_0_release_surface", plan.status)
        self.assertEqual(catalog.V4_TIER3_CALLBACK_SPIKE_PROTOCOL_STATUS, plan.tier3_protocol_status)
        self.assertEqual(catalog.V4_TIER3_CALLBACK_SPIKE_PROTOCOL_DOC, plan.tier3_protocol_doc)
        self.assertIsNone(plan.api_surface)
        self.assertTrue(plan.tier3_spike_authorized)
        self.assertFalse(plan.tier3_callback_claim_authorized)
        self.assertFalse(plan.raw_optix_callback_claim_authorized)
        self.assertFalse(plan.release_claim_authorized)

        as_dict = plan.as_dict()
        self.assertEqual(catalog.V4_TIER3_CALLBACK_SPIKE_PROTOCOL_STATUS, as_dict["tier3_protocol_status"])
        self.assertEqual(catalog.V4_TIER3_CALLBACK_SPIKE_PROTOCOL_DOC, as_dict["tier3_protocol_doc"])

    def test_planner_marks_action_callbacks_as_rejected_by_protocol_boundary(self) -> None:
        plan = catalog.plan_v4_operator_request(
            "custom-collision-response",
            callback_shape="custom_action",
            mutates_shared_state=True,
            variable_length_output=True,
            dynamic_allocation=True,
            partner="torch",
        )

        self.assertEqual("rejected_action_shaped_callback_deferred", plan.status)
        self.assertEqual(catalog.V4_TIER3_ACTION_CALLBACK_REJECTED_STATUS, plan.tier3_protocol_status)
        self.assertEqual(catalog.V4_TIER3_CALLBACK_SPIKE_PROTOCOL_DOC, plan.tier3_protocol_doc)
        self.assertIsNone(plan.api_surface)
        self.assertFalse(plan.tier3_spike_authorized)
        self.assertFalse(plan.tier3_callback_claim_authorized)
        self.assertFalse(plan.raw_optix_callback_claim_authorized)
        self.assertFalse(plan.app_specific_native_kernel_authorized)


if __name__ == "__main__":
    unittest.main()

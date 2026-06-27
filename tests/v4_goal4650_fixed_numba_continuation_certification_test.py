from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl import v4
from rtdsl import v4_operator_catalog as catalog
from rtdsl.v4_numba_fixed_continuation_certification import (
    V4_GOAL4650_NUMBA_FIXED_CANDIDATE_ID,
)
from rtdsl.v4_numba_fixed_continuation_certification import (
    validate_v4_goal4650_numba_fixed_certification,
)
from rtdsl.v4_partner_promotion_contract import v4_partner_promotion_candidate_allowed


EVIDENCE_JSON = ROOT / "future" / "v4" / "evidence" / (
    "v4_goal4650_fixed_numba_continuation_certification_2026-06-25.json"
)


class V4Goal4650FixedNumbaContinuationCertificationTest(unittest.TestCase):
    def test_certification_reuses_goal4635_component_union_evidence(self) -> None:
        record = validate_v4_goal4650_numba_fixed_certification()

        self.assertEqual(v4.V4_GOAL4650_NUMBA_FIXED_CERTIFICATION_STATUS, record["status"])
        self.assertEqual("Goal4635", record["source_goal"])
        self.assertEqual(V4_GOAL4650_NUMBA_FIXED_CANDIDATE_ID, record["candidate_id"])
        self.assertEqual("numba", record["partner"])
        self.assertEqual("fixed_radius_graph_component_union_3d", record["operator"])
        self.assertEqual("v4_fixed_radius_graph_component_union_3d_device_arrays", record["api_surface"])
        self.assertEqual("FIXED_RADIUS_GRAPH_COMPONENT_UNION_3D", record["generic_primitive"])
        self.assertEqual("rt_dbscan", record["target_coverage_row"])
        self.assertEqual("component_union", record["continuation_class"])
        self.assertIn(
            "future/v4/evidence/v4_goal4635_component_union_pod_gate_embree_2026-06-25/summary.json",
            record["evidence"],
        )

    def test_certification_is_fixed_operator_only_not_arbitrary_callback_support(self) -> None:
        record = validate_v4_goal4650_numba_fixed_certification()

        self.assertTrue(record["fixed_operator_only"])
        self.assertFalse(record["arbitrary_callback_supported"])
        self.assertEqual(
            ("fixed_radius_graph_component_union_3d(device columns) -> component labels",),
            record["accepted_signatures"],
        )
        boundaries = record["claim_boundaries"]
        self.assertFalse(boundaries["arbitrary_numba_callback_claim_authorized"])
        self.assertFalse(boundaries["tier3_callback_claim_authorized"])
        self.assertFalse(boundaries["raw_optix_callback_claim_authorized"])
        self.assertFalse(boundaries["release_claim_authorized"])
        self.assertFalse(boundaries["whole_app_speedup_claim_authorized"])

    def test_certification_clears_numeric_bars_and_correctness_gate(self) -> None:
        record = validate_v4_goal4650_numba_fixed_certification()
        gates = record["certification_gates"]

        self.assertEqual("pass", gates["status"])
        self.assertEqual((), gates["failed_checks"])
        self.assertTrue(gates["correctness_parity_passed"])
        self.assertTrue(gates["legacy_no_regression"])
        self.assertTrue(gates["component_signature_shortcut_blocked"])
        self.assertFalse(gates["host_materialization_in_hot_path"])
        self.assertGreaterEqual(gates["runner_vs_embree_hot_speedup"], gates["runner_vs_embree_hot_floor"])
        self.assertGreaterEqual(gates["runner_vs_embree_wall_speedup"], gates["runner_vs_embree_wall_floor"])
        self.assertGreaterEqual(gates["runner_vs_legacy_wall_speedup"], gates["runner_vs_legacy_wall_floor"])
        self.assertGreaterEqual(gates["runner_vs_embree_hot_speedup"], gates["representative_speedup_floor"])
        self.assertGreaterEqual(gates["runner_vs_legacy_wall_speedup"], gates["partner_parity_floor"])

    def test_goal4648_candidate_gate_allows_only_numba_fixed_candidate(self) -> None:
        self.assertTrue(
            v4_partner_promotion_candidate_allowed(
                V4_GOAL4650_NUMBA_FIXED_CANDIDATE_ID,
                partner="numba",
            )
        )
        self.assertFalse(
            v4_partner_promotion_candidate_allowed(
                V4_GOAL4650_NUMBA_FIXED_CANDIDATE_ID,
                partner="cupy",
            )
        )
        self.assertFalse(
            v4_partner_promotion_candidate_allowed(
                V4_GOAL4650_NUMBA_FIXED_CANDIDATE_ID,
                partner="torch",
            )
        )

    def test_planner_exposes_numba_component_union_and_fails_closed_for_others(self) -> None:
        numba_plan = v4.plan_operator_request_v4("component_union", partner="numba")
        self.assertEqual("tier2_measured_ready", numba_plan.status)
        self.assertEqual("v4_fixed_radius_graph_component_union_3d_device_arrays", numba_plan.api_surface)
        self.assertTrue(numba_plan.measured_partner)
        self.assertFalse(numba_plan.release_claim_authorized)
        self.assertFalse(numba_plan.whole_app_speedup_claim_authorized)

        for partner in ("torch", "cupy"):
            plan = v4.plan_operator_request_v4("component_union", partner=partner)
            self.assertEqual("tier2_declared_unmeasured_partner", plan.status)
            self.assertIsNone(plan.api_surface)
            self.assertFalse(plan.measured_partner)
            self.assertIn("measured for numba only", plan.guidance)

    def test_tier3_custom_numba_callback_remains_spike_only(self) -> None:
        scalar_plan = catalog.plan_v4_operator_request(
            "custom-force-score",
            callback_shape="custom_scalar_reduce",
            numba_device_function=True,
            partner="torch",
        )
        self.assertEqual("tier3_spike_only_not_v4_0_release_surface", scalar_plan.status)
        self.assertEqual(catalog.V4_TIER3_CALLBACK_SPIKE_PROTOCOL_STATUS, scalar_plan.tier3_protocol_status)
        self.assertTrue(scalar_plan.tier3_spike_authorized)
        self.assertFalse(scalar_plan.tier3_callback_claim_authorized)
        self.assertFalse(scalar_plan.raw_optix_callback_claim_authorized)

        action_plan = catalog.plan_v4_operator_request(
            "custom-collision-response",
            callback_shape="custom_action",
            mutates_shared_state=True,
            variable_length_output=True,
            dynamic_allocation=True,
            partner="torch",
        )
        self.assertEqual("rejected_action_shaped_callback_deferred", action_plan.status)
        self.assertEqual(catalog.V4_TIER3_ACTION_CALLBACK_REJECTED_STATUS, action_plan.tier3_protocol_status)
        self.assertFalse(action_plan.tier3_spike_authorized)
        self.assertFalse(action_plan.tier3_callback_claim_authorized)
        self.assertFalse(action_plan.raw_optix_callback_claim_authorized)

    def test_checked_in_evidence_json_matches_generated_certification_keys(self) -> None:
        generated = validate_v4_goal4650_numba_fixed_certification()
        checked_in = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))

        required_keys = (
            "contract_status",
            "planner_api_surface",
            "telemetry_required",
            "coverage_effect",
        )
        for key in required_keys:
            self.assertIn(key, checked_in)
            if isinstance(generated[key], tuple):
                self.assertEqual(list(generated[key]), checked_in[key])
            else:
                self.assertEqual(generated[key], checked_in[key])

        self.assertEqual(generated["status"], checked_in["status"])
        self.assertEqual(generated["candidate_id"], checked_in["candidate_id"])
        self.assertEqual(generated["api_surface"], checked_in["api_surface"])
        self.assertEqual(generated["claim_boundaries"], checked_in["claim_boundaries"])
        self.assertIn("compile_time_seconds", checked_in["telemetry_required"])
        self.assertEqual("rt_dbscan", checked_in["coverage_effect"]["row"])


if __name__ == "__main__":
    unittest.main()

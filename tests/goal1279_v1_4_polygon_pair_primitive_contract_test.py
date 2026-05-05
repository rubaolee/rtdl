from __future__ import annotations

import unittest
from unittest import mock

from examples import rtdl_polygon_pair_overlap_area_rows as pair_app
import rtdsl as rt


def _candidate_pairs(*_args, **_kwargs):
    return {(1, 10), (2, 11)}


class Goal1279V14PolygonPairPrimitiveContractTest(unittest.TestCase):
    def test_contract_helper_defines_candidate_discovery_scope(self) -> None:
        contract = rt.polygon_pair_primitive_contract(
            backend="optix",
            output_mode="summary",
            candidate_row_count=2,
        )

        self.assertEqual(contract["app_row"], "polygon_pair_overlap_area_rows")
        self.assertEqual(contract["primitive"], "ANY_HIT")
        self.assertEqual(contract["candidate_primitive"], "ANY_HIT")
        self.assertEqual(contract["future_area_primitive"], "REDUCE_FLOAT(SUM)")
        self.assertEqual(contract["future_area_primitive_status"], "deferred_until_generic_float_reduction_contract")
        self.assertEqual(contract["backend_scope"], ("embree", "optix"))
        self.assertEqual(contract["backend_contract_role"], "nvidia_rt_target")
        self.assertTrue(contract["same_contract_baseline_required"])
        self.assertTrue(contract["goal1270_diagnostic_split_preserved"])
        self.assertEqual(contract["exact_area_continuation"], "app_specific_native_cpp")
        self.assertIn("not a generic area-reduction", contract["claim_boundary"])

    def test_optix_summary_attaches_candidate_contract_without_claiming_area_primitive(self) -> None:
        with mock.patch.object(pair_app, "_positive_candidate_pairs_optix", side_effect=_candidate_pairs):
            payload = pair_app.run_case("optix", copies=1, output_mode="summary")

        contract = payload["primitive_contract"]
        self.assertEqual(payload["backend_mode"], "optix_native_assisted")
        self.assertEqual(payload["candidate_row_count"], 2)
        self.assertTrue(payload["rt_core_candidate_discovery_active"])
        self.assertFalse(payload["rt_core_accelerated"])
        self.assertEqual(contract["backend"], "optix")
        self.assertEqual(contract["primitive"], "ANY_HIT")
        self.assertEqual(contract["future_area_primitive"], "REDUCE_FLOAT(SUM)")
        self.assertEqual(contract["exact_area_continuation"], "app_specific_native_cpp")

    def test_embree_summary_attaches_cpu_rt_baseline_contract(self) -> None:
        with mock.patch.object(pair_app, "_positive_candidate_pairs_embree", side_effect=_candidate_pairs):
            payload = pair_app.run_case("embree", copies=1, output_mode="summary")

        contract = payload["primitive_contract"]
        self.assertEqual(payload["backend_mode"], "embree_native_assisted")
        self.assertEqual(contract["backend"], "embree")
        self.assertEqual(contract["backend_contract_role"], "cpu_rt_baseline_and_fallback")
        self.assertTrue(contract["active_v1_4_backend"])
        self.assertTrue(contract["same_contract_baseline_required"])
        self.assertEqual(contract["candidate_row_count"], 2)

    def test_cpu_path_is_marked_materializing_not_v1_4_candidate_discovery(self) -> None:
        payload = pair_app.run_case("cpu_python_reference", copies=1, output_mode="summary")
        contract = payload["primitive_contract"]

        self.assertEqual(contract["backend"], "cpu_python_reference")
        self.assertFalse(contract["active_v1_4_backend"])
        self.assertEqual(contract["primitive"], "row_materialization")
        self.assertEqual(contract["candidate_primitive"], "not_applicable")
        self.assertIsNone(contract["candidate_row_count"])


if __name__ == "__main__":
    unittest.main()

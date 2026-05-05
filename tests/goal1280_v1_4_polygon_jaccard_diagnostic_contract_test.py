from __future__ import annotations

import unittest
from unittest import mock

from examples import rtdl_polygon_set_jaccard as jaccard_app
import rtdsl as rt


def _candidate_pairs(*_args, **_kwargs):
    return {(1, 10), (2, 11)}


class Goal1280V14PolygonJaccardDiagnosticContractTest(unittest.TestCase):
    def test_contract_helper_preserves_slower_diagnostic_status(self) -> None:
        contract = rt.polygon_jaccard_diagnostic_contract(
            backend="optix",
            output_mode="summary",
            candidate_row_count=2,
        )

        self.assertEqual(contract["app_row"], "polygon_set_jaccard")
        self.assertEqual(contract["status"], "optix_still_slower_with_reason")
        self.assertEqual(contract["primitive"], "ANY_HIT")
        self.assertEqual(contract["experimental_collection_primitive"], "COLLECT_K_BOUNDED")
        self.assertEqual(contract["future_score_primitive"], "REDUCE_FLOAT(SUM)")
        self.assertEqual(contract["future_score_primitive_status"], "pod_verified_generic_non_public")
        self.assertFalse(contract["public_wording_allowed"])
        self.assertTrue(contract["chunk_policy_required_for_public_evidence"])
        self.assertEqual(contract["migration_status"], "diagnostic_metadata_only")
        self.assertIn("native bounded collection is routed", contract["claim_boundary"])
        self.assertIn("Public wording remains blocked", contract["claim_boundary"])

    def test_optix_summary_attaches_non_promoting_diagnostic_contract(self) -> None:
        collection = rt.collect_k_bounded_candidate_pairs(_candidate_pairs(), k=2) | {
            "backend": "optix",
            "native_collection_backend": "test_native_collection",
        }
        with mock.patch.object(jaccard_app, "_collect_candidate_pairs_bounded", return_value=collection):
            payload = jaccard_app.run_case("optix", copies=1, output_mode="summary")

        contract = payload["primitive_contract"]
        self.assertEqual(payload["backend_mode"], "optix_native_assisted")
        self.assertTrue(payload["rt_core_candidate_discovery_active"])
        self.assertFalse(payload["rt_core_accelerated"])
        self.assertEqual(contract["backend"], "optix")
        self.assertEqual(contract["status"], "optix_still_slower_with_reason")
        self.assertEqual(contract["candidate_row_count"], 2)
        self.assertFalse(contract["public_wording_allowed"])
        self.assertEqual(
            contract["exact_score_continuation"],
            "backend_neutral_native_polygon_pair_area_summary",
        )

    def test_embree_summary_attaches_baseline_diagnostic_contract(self) -> None:
        collection = rt.collect_k_bounded_candidate_pairs(_candidate_pairs(), k=2) | {
            "backend": "embree",
            "native_collection_backend": "test_native_collection",
        }
        with mock.patch.object(jaccard_app, "_collect_candidate_pairs_bounded", return_value=collection):
            payload = jaccard_app.run_case("embree", copies=1, output_mode="summary")

        contract = payload["primitive_contract"]
        self.assertEqual(payload["backend_mode"], "embree_native_assisted")
        self.assertEqual(contract["backend"], "embree")
        self.assertEqual(contract["backend_contract_role"], "cpu_rt_baseline_and_fallback")
        self.assertTrue(contract["same_contract_baseline_required"])
        self.assertEqual(contract["status"], "optix_still_slower_with_reason")

    def test_cpu_path_is_not_active_v1_4_jaccard_candidate_discovery(self) -> None:
        payload = jaccard_app.run_case("cpu_python_reference", copies=1, output_mode="summary")
        contract = payload["primitive_contract"]

        self.assertEqual(contract["backend"], "cpu_python_reference")
        self.assertFalse(contract["active_v1_4_backend"])
        self.assertEqual(contract["primitive"], "row_materialization")
        self.assertEqual(contract["candidate_primitive"], "not_applicable")
        self.assertFalse(contract["public_wording_allowed"])


if __name__ == "__main__":
    unittest.main()

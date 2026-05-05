from __future__ import annotations

import unittest

from examples import rtdl_polygon_set_jaccard as jaccard_app
import rtdsl as rt


class Goal1310V15JaccardCollectKBoundedContractTest(unittest.TestCase):
    def test_collect_k_bounded_contract_is_fail_closed_and_non_public(self) -> None:
        (contract,) = rt.validate_v1_5_collect_k_bounded_contracts()

        self.assertEqual(contract["app"], "polygon_set_jaccard")
        self.assertEqual(contract["collection_primitive"], "COLLECT_K_BOUNDED")
        self.assertEqual(contract["status"], "experimental_diagnostic_only")
        self.assertEqual(contract["overflow_policy"], "no_silent_truncation")
        self.assertEqual(contract["failure_mode"], "fail_closed_overflow")
        self.assertFalse(contract["truncation_allowed"])
        self.assertTrue(contract["complete_candidate_coverage_required"])
        self.assertFalse(contract["score_reduction_allowed_on_overflow"])
        self.assertFalse(contract["public_wording_allowed"])

    def test_jaccard_primitive_contract_embeds_bounded_collection_policy(self) -> None:
        contract = rt.polygon_jaccard_diagnostic_contract(
            backend="optix",
            output_mode="summary",
            candidate_row_count=2,
        )

        policy = contract["bounded_collection_policy"]
        self.assertEqual(policy["collection_primitive"], "COLLECT_K_BOUNDED")
        self.assertEqual(policy["status"], "experimental_diagnostic_only")
        self.assertEqual(policy["overflow_policy"], "no_silent_truncation")
        self.assertEqual(policy["failure_mode"], "fail_closed_overflow")
        self.assertFalse(policy["truncation_allowed"])
        self.assertTrue(policy["complete_candidate_coverage_required"])
        self.assertFalse(policy["score_reduction_allowed_on_overflow"])
        self.assertFalse(contract["public_wording_allowed"])
        self.assertEqual(contract["future_score_primitive_status"], "blocked_by_collect_k_bounded_runtime")
        self.assertEqual(contract["migration_status"], "diagnostic_metadata_only")

    def test_jaccard_summary_payload_keeps_diagnostic_boundary(self) -> None:
        payload = jaccard_app.run_case("cpu_python_reference", copies=1, output_mode="summary")
        contract = payload["primitive_contract"]

        self.assertFalse(payload["rt_core_accelerated"])
        self.assertEqual(contract["status"], "optix_still_slower_with_reason")
        self.assertEqual(contract["bounded_collection_policy"]["failure_mode"], "fail_closed_overflow")
        self.assertFalse(contract["public_wording_allowed"])

    def test_inventory_records_policy_defined_but_runtime_still_blocked(self) -> None:
        inventory = rt.validate_v1_5_generic_migration_inventory()
        by_row = {(row["app"], row["subpath"]): row for row in inventory}
        row = by_row[("polygon_set_jaccard", "chunked_candidate_scoring")]

        self.assertEqual(row["goal"], "Goal1310")
        self.assertEqual(row["status"], "diagnostic_blocked")
        self.assertEqual(row["generic_primitive"], "COLLECT_K_BOUNDED")
        self.assertIn("native fail-closed bounded collection implementation", row["remaining_app_specific_work"])
        self.assertIn("no silent truncation", row["boundary"])
        self.assertFalse(row["public_wording_authorized"])


if __name__ == "__main__":
    unittest.main()

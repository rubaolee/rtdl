from pathlib import Path
import unittest

from rtdsl.segment_pair_contracts import (
    SEGMENT_PAIR_CONTRACT_VERSION,
    SEGMENT_PAIR_TYPED_OUTPUT_RESIDENCY_VERSION,
    segment_pair_left_id_dense_count_output_residency_contract,
    validate_segment_pair_contract_cases,
    validate_segment_pair_output_residency_contract,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3627_segment_pair_typed_output_residency_contract_2026-06-06.md"


class Goal3627SegmentPairTypedOutputResidencyContractTest(unittest.TestCase):
    def test_device_resident_output_descriptors_keep_claims_blocked(self):
        contract = segment_pair_left_id_dense_count_output_residency_contract(
            group_capacity=128,
            counts_device_ptr=111,
            overflow_device_ptr=222,
            ambiguous_count_device_ptr=333,
            stream_ordering="same_stream",
        )
        validation = validate_segment_pair_output_residency_contract(contract)

        self.assertTrue(validation["valid"], validation)
        self.assertEqual(contract["version"], SEGMENT_PAIR_TYPED_OUTPUT_RESIDENCY_VERSION)
        self.assertEqual(contract["primitive_contract_version"], SEGMENT_PAIR_CONTRACT_VERSION)
        self.assertTrue(contract["all_columns_device_resident"])
        self.assertFalse(contract["fallback_required"])
        self.assertFalse(contract["true_zero_copy_authorized"])
        self.assertFalse(contract["public_speedup_claim_authorized"])
        self.assertFalse(contract["release_authorized"])

        columns = {column["name"]: column for column in contract["columns"]}
        self.assertEqual(set(columns), {
            "segment_pair_left_id_counts",
            "segment_pair_overflow_status",
            "segment_pair_ambiguous_count",
        })
        for column in columns.values():
            with self.subTest(column=column["name"]):
                self.assertTrue(column["data_ptr_observed"])
                self.assertEqual(column["device"], "cuda:0")
                self.assertFalse(column["fallback_required"])
                self.assertFalse(column["true_zero_copy_authorized"])
                self.assertFalse(column["public_speedup_claim_authorized"])
                self.assertIn("neutral_buffer_seam", column)
                self.assertFalse(column["neutral_buffer_seam"]["zero_copy_claim_authorized"])

    def test_host_reference_output_path_is_explicit_fallback(self):
        contract = segment_pair_left_id_dense_count_output_residency_contract(group_capacity=16)
        validation = validate_segment_pair_output_residency_contract(contract)

        self.assertTrue(validation["valid"], validation)
        self.assertFalse(contract["all_columns_device_resident"])
        self.assertTrue(contract["fallback_required"])
        for column in contract["columns"]:
            with self.subTest(column=column["name"]):
                self.assertFalse(column["data_ptr_observed"])
                self.assertTrue(column["fallback_required"])
                self.assertEqual(column["fallback_reason"], "host_reference")
                self.assertTrue(column["host_materialized_before_handoff"])
                self.assertFalse(column["true_zero_copy_authorized"])

    def test_invalid_contracts_fail_closed(self):
        with self.assertRaises(ValueError):
            segment_pair_left_id_dense_count_output_residency_contract(group_capacity=0)

        contract = segment_pair_left_id_dense_count_output_residency_contract(group_capacity=4)
        bad = dict(contract)
        bad["true_zero_copy_authorized"] = True
        validation = validate_segment_pair_output_residency_contract(bad)
        self.assertFalse(validation["valid"])
        self.assertIn("true_zero_copy_authorized must remain false", validation["errors"])

    def test_report_and_predicate_contract_stay_aligned(self):
        predicate_summary = validate_segment_pair_contract_cases()
        report = REPORT.read_text(encoding="utf-8")

        self.assertTrue(predicate_summary["valid"], predicate_summary)
        self.assertIn("segment_pair_left_id_dense_count_output_residency_contract", report)
        self.assertIn("segment_pair_ambiguous_count", report)
        self.assertIn("Do not invent a second residency seam", report)
        self.assertIn("does not prove true zero-copy", report)


if __name__ == "__main__":
    unittest.main()

from pathlib import Path
import unittest

from rtdsl.segment_pair_contracts import (
    Segment2DContractInput,
    segment_pair_contract_adversarial_cases,
    segment_pair_left_id_dense_counts_reference,
    validate_segment_pair_dense_count_reference,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3629_segment_pair_dense_count_reference_oracle_2026-06-06.md"


class Goal3629SegmentPairDenseCountReferenceOracleTest(unittest.TestCase):
    def test_reference_counts_by_left_index_and_records_ambiguity(self):
        left = (
            Segment2DContractInput(0.0, 0.0, 1.0, 1.0),
            Segment2DContractInput(0.0, 0.0, 1.0, 0.0),
            Segment2DContractInput(10.0, 0.0, 12.0, 0.0),
        )
        right = (
            Segment2DContractInput(0.5, 0.25, 0.5, 0.75),
            Segment2DContractInput(0.5, -1.0, 0.5, 0.0),
            Segment2DContractInput(11.0, 0.0, 13.0, 0.0),
        )

        reference = segment_pair_left_id_dense_counts_reference(left, right)

        self.assertEqual(reference.counts, (1, 1, 0))
        self.assertEqual(reference.hit_pair_count, 2)
        self.assertGreaterEqual(reference.ambiguous_pair_count, 2)
        self.assertIn("non_collinear_endpoint_inclusive_hit", reference.decision_reasons)
        self.assertIn("denominator_degenerate_or_collinear", reference.decision_reasons)

    def test_reference_can_use_larger_group_capacity(self):
        case = segment_pair_contract_adversarial_cases()[0]
        reference = segment_pair_left_id_dense_counts_reference((case.left,), (case.right,), group_capacity=4)

        self.assertEqual(reference.group_capacity, 4)
        self.assertEqual(reference.counts, (1, 0, 0, 0))

    def test_reference_rejects_too_small_group_capacity(self):
        cases = segment_pair_contract_adversarial_cases()
        with self.assertRaises(ValueError):
            segment_pair_left_id_dense_counts_reference(
                tuple(case.left for case in cases),
                tuple(case.right for case in cases),
                group_capacity=1,
            )

    def test_built_in_reference_validation_and_report_boundaries(self):
        summary = validate_segment_pair_dense_count_reference()
        report = REPORT.read_text(encoding="utf-8")

        self.assertTrue(summary["valid"], summary)
        self.assertEqual(summary["errors"], ())
        self.assertIn("segment_pair_left_id_dense_count_reference", summary["reference"]["contract"])
        self.assertFalse(summary["reference"]["release_authorized"])
        self.assertFalse(summary["reference"]["public_speedup_claim_authorized"])
        self.assertIn("same-contract oracle", report)
        self.assertIn("does not prove backend conformance", report)
        self.assertIn("does not authorize public claims", report)


if __name__ == "__main__":
    unittest.main()

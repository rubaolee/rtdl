import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4194_predicate_aware_boundary_union_reference_contract_2026-06-09.md"
)
MODULE = ROOT / "src" / "rtdsl" / "predicate_aware_boundary_union.py"


class Goal4194PredicateAwareBoundaryUnionReferenceTest(unittest.TestCase):
    def test_reference_assigns_boundary_items_with_lowest_root_policy(self) -> None:
        result = rt.predicate_aware_boundary_union_reference(
            point_count=6,
            predicate_flags=(True, True, True, False, True, False),
            candidate_pairs=((0, 1), (1, 2), (1, 3), (3, 4), (3, 5)),
        )

        self.assertEqual(result["contract"], rt.PREDICATE_AWARE_BOUNDARY_UNION_REFERENCE_VERSION)
        self.assertEqual(result["status"], rt.PREDICATE_AWARE_BOUNDARY_UNION_REFERENCE_STATUS)
        self.assertEqual(result["component_labels"], (0, 0, 0, 0, 4, -1))
        self.assertEqual(result["component_sizes"], (1, 4))
        self.assertEqual(result["component_count"], 2)
        self.assertEqual(result["true_true_pair_count"], 2)
        self.assertEqual(result["boundary_pair_count"], 2)
        self.assertEqual(result["ignored_false_false_pair_count"], 1)
        self.assertEqual(result["boundary_assigned_count"], 1)
        self.assertEqual(result["unassigned_count"], 1)
        self.assertEqual(result["boundary_candidate_component_counts"], ((3, 2),))
        self.assertEqual(result["boundary_assignment_policy"], "lowest_component_root")
        self.assertFalse(result["policy_metadata"]["native_engine_app_specific_logic"])
        self.assertFalse(result["policy_metadata"]["route_promotion_authorized"])

    def test_reference_is_deterministic_for_candidate_pair_order(self) -> None:
        flags = (True, True, True, False, True, False)
        first = rt.predicate_aware_boundary_union_reference(
            point_count=6,
            predicate_flags=flags,
            candidate_pairs=((0, 1), (1, 2), (1, 3), (3, 4), (3, 5)),
        )
        reordered = rt.predicate_aware_boundary_union_reference(
            point_count=6,
            predicate_flags=flags,
            candidate_pairs=((3, 5), (4, 3), (2, 1), (3, 1), (1, 0)),
        )

        self.assertEqual(first["component_labels"], reordered["component_labels"])
        self.assertEqual(first["component_sizes"], reordered["component_sizes"])
        self.assertEqual(
            first["boundary_candidate_component_counts"],
            reordered["boundary_candidate_component_counts"],
        )

    def test_reference_fails_closed_for_invalid_inputs(self) -> None:
        with self.assertRaisesRegex(ValueError, "policy"):
            rt.predicate_aware_boundary_union_reference(
                point_count=1,
                predicate_flags=(True,),
                candidate_pairs=(),
                boundary_assignment_policy="ambiguous",
            )
        with self.assertRaisesRegex(ValueError, "length"):
            rt.predicate_aware_boundary_union_reference(
                point_count=2,
                predicate_flags=(True,),
                candidate_pairs=(),
            )
        with self.assertRaisesRegex(ValueError, "out of range"):
            rt.predicate_aware_boundary_union_reference(
                point_count=2,
                predicate_flags=(True, True),
                candidate_pairs=((0, 2),),
            )

    def test_reference_is_exported_and_keeps_app_terms_out_of_module(self) -> None:
        self.assertIn("lowest_component_root", rt.PREDICATE_AWARE_BOUNDARY_UNION_POLICIES)
        self.assertIsNotNone(rt.predicate_aware_boundary_union_reference)

        text = MODULE.read_text(encoding="utf-8").lower()
        self.assertNotIn("dbscan", text)
        self.assertNotIn("epsilon", text)
        self.assertNotIn("min-points", text)

    def test_report_records_candidate_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal4194", report)
        self.assertIn("reference contract", report)
        self.assertIn("lowest-root", report)
        self.assertIn("does not promote", report)
        self.assertIn("does not authorize release", report)


if __name__ == "__main__":
    unittest.main()

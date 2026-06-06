from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.primitive_discovery import find_primitive
from rtdsl.segment_pair_contracts import (
    SEGMENT_PAIR_CONTRACT_VERSION,
    SEGMENT_PAIR_STRICT_DENOMINATOR_EPSILON,
    Segment2DContractInput,
    segment_pair_contract_adversarial_cases,
    segment_pair_intersection_strict_v0,
    validate_segment_pair_contract_cases,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3625_segment_pair_intersection_contract_foundation_2026-06-06.md"
CATALOG = ROOT / "docs" / "rtdl_primitive_catalog.md"


class Goal3625SegmentPairIntersectionContractFoundationTest(unittest.TestCase):
    def test_executable_contract_covers_adversarial_cases(self):
        summary = validate_segment_pair_contract_cases()

        self.assertTrue(summary["valid"], summary)
        self.assertEqual(summary["version"], SEGMENT_PAIR_CONTRACT_VERSION)
        self.assertEqual(summary["case_count"], 7)
        self.assertEqual(summary["failures"], ())
        self.assertFalse(summary["public_api_specification"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        for category in (
            "proper",
            "endpoint",
            "outside",
            "parallel",
            "collinear",
            "near_parallel",
            "degenerate",
        ):
            self.assertIn(category, summary["categories"])

    def test_endpoint_inclusive_and_collinear_excluded_semantics(self):
        endpoint = segment_pair_intersection_strict_v0(
            Segment2DContractInput(0.0, 0.0, 1.0, 0.0),
            Segment2DContractInput(1.0, 0.0, 1.0, 1.0),
        )
        self.assertTrue(endpoint.hit)
        self.assertFalse(endpoint.ambiguous)
        self.assertEqual(endpoint.reason, "non_collinear_endpoint_inclusive_hit")
        self.assertAlmostEqual(endpoint.t, 1.0)
        self.assertAlmostEqual(endpoint.u, 0.0)

        collinear = segment_pair_intersection_strict_v0(
            Segment2DContractInput(0.0, 0.0, 2.0, 0.0),
            Segment2DContractInput(1.0, 0.0, 3.0, 0.0),
        )
        self.assertFalse(collinear.hit)
        self.assertTrue(collinear.ambiguous)
        self.assertEqual(collinear.reason, "denominator_degenerate_or_collinear")

    def test_near_parallel_threshold_is_absolute_v0(self):
        self.assertEqual(SEGMENT_PAIR_STRICT_DENOMINATOR_EPSILON, 1.0e-7)
        case = next(case for case in segment_pair_contract_adversarial_cases() if case.name == "near_parallel_below_abs_epsilon")
        decision = segment_pair_intersection_strict_v0(case.left, case.right)

        self.assertFalse(decision.hit)
        self.assertTrue(decision.ambiguous)
        self.assertEqual(decision.reason, "denominator_degenerate_or_collinear")

    def test_primitive_hierarchy_and_discovery_expose_candidate(self):
        node = rt.find_primitive_hierarchy_node("rows.segment_pair_intersection_rows_2d")

        self.assertEqual(node.status, "candidate_behavior")
        self.assertEqual(node.layer, "row_emission")
        self.assertIn("shape:segment_pair", node.capability_tags)
        self.assertIn("intent:intersection", node.capability_tags)
        self.assertIn("segment_pair_left_id_dense_count", node.aliases)
        self.assertIn("rows.segment_pair_intersection_rows_2d", rt.primitive_layer_map()["row_emission"])

        matches = find_primitive(intent="intersection", shape="segment_pair", dim="2d", output="rows")
        self.assertEqual(matches[0].node_id, "rows.segment_pair_intersection_rows_2d")
        self.assertIn("segment_pair", matches[0].title.lower())

        validation = rt.validate_primitive_hierarchy(require_discovery_metadata=True)
        self.assertTrue(validation["valid"], validation)

    def test_catalog_and_report_are_bounded(self):
        catalog = CATALOG.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("SEGMENT_PAIR_INTERSECTION_ROWS_2D", catalog)
        self.assertIn("rows.segment_pair_intersection_rows_2d", catalog)
        self.assertIn("Goal3625 is a contract foundation only", report)
        self.assertIn("not a public API specification", report)
        self.assertIn("not public speedup wording", report)
        self.assertIn("Claude review", report)


if __name__ == "__main__":
    unittest.main()

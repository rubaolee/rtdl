from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal2794_v2_5_continuation_determinism_policy_2026-05-31.md"
REVIEW = REPO_ROOT / "docs" / "reviews" / "goal2794_gemini_review_continuation_determinism_policy_2026-05-31.md"
CONSENSUS = REPO_ROOT / "docs" / "reports" / "goal2794_v2_5_continuation_determinism_policy_consensus_2026-05-31.md"


class Goal2794V25DeterminismPolicyTest(unittest.TestCase):
    def test_policy_covers_every_continuation_operation_once(self) -> None:
        policies = rt.v2_5_continuation_determinism_policies()
        validation = rt.validate_v2_5_continuation_determinism_policies(policies)
        operations = tuple(row["operation"] for row in policies["rows"])

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(policies["operation_count"], len(rt.V2_5_PARTNER_CONTINUATION_OPERATION_NAMES))
        self.assertEqual(set(operations), set(rt.V2_5_PARTNER_CONTINUATION_OPERATION_NAMES))
        self.assertEqual(len(operations), len(set(operations)))

    def test_claim_flags_fail_closed_at_policy_and_row_level(self) -> None:
        policies = rt.v2_5_continuation_determinism_policies()
        claim_fields = (
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "release_readiness_authorized",
            "rt_traversal_replacement_allowed",
        )

        for field in claim_fields:
            self.assertIs(policies[field], False)
        for row in policies["rows"]:
            for field in claim_fields:
                self.assertIs(row[field], False)

        mutated = dict(policies)
        mutated["public_speedup_claim_authorized"] = True
        self.assertEqual(rt.validate_v2_5_continuation_determinism_policies(mutated)["status"], "reject")

    def test_score_witness_operations_publish_item_id_tie_breaks(self) -> None:
        argmin = rt.plan_v2_5_continuation_determinism("grouped_argmin_f64")
        argmax = rt.plan_v2_5_continuation_determinism("grouped_argmax_f64")
        topk = rt.plan_v2_5_continuation_determinism("grouped_topk_f64")

        self.assertEqual(argmin["tie_break_policy"], "lowest_score_then_lowest_item_id")
        self.assertEqual(argmax["tie_break_policy"], "highest_score_then_lowest_item_id")
        self.assertIn("lowest_item_id_per_rank", topk["tie_break_policy"])
        self.assertIn("deduplicate_items_by_lowest_score", topk["tie_break_policy"])

    def test_float_reductions_publish_tolerance_or_order_policy(self) -> None:
        for operation in ("segmented_sum_f64", "grouped_vector_sum_f64x2"):
            row = rt.plan_v2_5_continuation_determinism(operation)
            self.assertIn("tolerance", row["tolerance_policy"])
            self.assertIn("reduction_order", row["tolerance_policy"])

    def test_bounded_and_event_stream_overflow_fail_closed(self) -> None:
        bounded = rt.plan_v2_5_continuation_determinism("bounded_collect_finalize_i64")
        hit_stream = rt.plan_v2_5_continuation_determinism("hit_stream_grouped_ray_id_primitive_i64")

        self.assertIn("fail_closed", bounded["overflow_policy"])
        self.assertIn("fails_closed", hit_stream["overflow_policy"])
        self.assertEqual(hit_stream["output_order_policy"], "dense_ray_id_group_order")
        self.assertIn("producer_event_row_order", hit_stream["tie_break_policy"])

    def test_policy_is_explain_surface_not_contract_first_star_export(self) -> None:
        self.assertTrue(hasattr(rt, "v2_5_continuation_determinism_policies"))
        self.assertTrue(hasattr(rt, "validate_v2_5_continuation_determinism_policies"))
        self.assertNotIn("v2_5_continuation_determinism_policies", rt.__all__)
        self.assertNotIn("validate_v2_5_continuation_determinism_policies", rt.__all__)

    def test_unknown_operation_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            rt.plan_v2_5_continuation_determinism("custom_app_specific_ranker")

    def test_report_review_and_consensus_are_present(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Goal2794", report)
        self.assertIn("determinism", report.lower())
        self.assertIn("grouped_argmin_f64", report)
        self.assertIn("## verdict", review.lower())
        self.assertIn("accept", review.lower())
        self.assertIn("accept-with-boundary", consensus.lower())
        self.assertIn(str(REVIEW.relative_to(REPO_ROOT)).replace("\\", "/"), consensus)


if __name__ == "__main__":
    unittest.main()

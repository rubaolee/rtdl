import unittest
from pathlib import Path

import rtdsl as rt
from examples.v2_0.research_benchmarks.librts_spatial_index import (
    rtdl_librts_spatial_index_benchmark_app as librts,
)
from examples.v2_0.research_benchmarks.spatial_rayjoin import (
    rtdl_rayjoin_v2_spatial_join_app as rayjoin,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2736_tier_a_primitive_first_plan_alignment_2026-05-30.md"


class Goal2736TierAPrimitiveFirstPlanAlignmentTest(unittest.TestCase):
    def test_spatial_rayjoin_plan_is_primitive_first_not_forced_triton(self) -> None:
        payload = rayjoin.v2_5_plan_payload()
        plan = payload["v2_5_primitive_first_plan"]
        boundary = payload["claim_boundary"]

        self.assertEqual(plan["selected_path"], "prepared_generic_rtdl_count_or_parity")
        self.assertFalse(plan["typed_hit_stream_forced"])
        self.assertFalse(plan["partner_continuation_required"])
        self.assertIn("compact-mask", plan["partner_continuation_reserved_for"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["true_zero_copy_authorized"])
        self.assertFalse(boundary["triton_speedup_claim_authorized"])
        self.assertTrue(boundary["primitive_first_plan_only"])

    def test_librts_plan_is_primitive_first_aabb_query(self) -> None:
        payload = librts.v2_5_plan_payload()
        plan = payload["v2_5_primitive_first_plan"]
        boundary = payload["claim_boundary"]

        self.assertEqual(plan["selected_path"], "prepared_generic_aabb_index_query_2d")
        self.assertEqual(plan["selected_primitives"], ("AABB_INDEX_QUERY_2D",))
        self.assertFalse(plan["typed_hit_stream_forced"])
        self.assertFalse(plan["partner_continuation_required"])
        self.assertIn("grouped summaries", plan["partner_continuation_reserved_for"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["true_zero_copy_authorized"])
        self.assertFalse(boundary["triton_speedup_claim_authorized"])
        self.assertTrue(boundary["primitive_first_plan_only"])

    def test_manifest_splits_tier_a_count_from_no_partner_baseline(self) -> None:
        validation = rt.validate_v2_5_tiered_benchmark_manifest()
        manifest = rt.v2_5_tiered_benchmark_manifest()
        rows = {row["app_id"]: row for row in manifest["apps"]}

        self.assertEqual(validation["status"], "accept")

        spatial = rows["spatial_rayjoin"]
        self.assertEqual(spatial["tier"], "A")
        self.assertIn("primitive_first_rt_count_or_parity", spatial["benchmark_track"])
        self.assertIn("Tier A count/parity", spatial["parity_target"])
        self.assertIn("deferred Tier B", spatial["next_action"])
        self.assertIn("segmented_count_i64", spatial["required_partner_operations"])

        librts_row = rows["librts_spatial_index"]
        self.assertEqual(librts_row["tier"], "C")
        self.assertIn("rt_core", librts_row["benchmark_track"])
        self.assertIn("no-regression", librts_row["parity_target"])
        self.assertEqual(librts_row["required_partner_operations"], ())

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Tier A Primitive-First Plan Alignment", text)
        self.assertIn("Spatial RayJoin", text)
        self.assertIn("LibRTS-style AABB index query", text)
        self.assertIn("not pod evidence and not a speedup claim", text)


if __name__ == "__main__":
    unittest.main()

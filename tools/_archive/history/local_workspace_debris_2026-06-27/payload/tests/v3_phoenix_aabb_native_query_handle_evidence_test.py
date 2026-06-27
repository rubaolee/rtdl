from __future__ import annotations

import unittest

from scripts import v3_phoenix_aabb_native_query_handle_evidence as evidence


class V3PhoenixAabbNativeQueryHandleEvidenceTest(unittest.TestCase):
    def test_native_query_handle_evidence_is_m7_candidate_not_release(self) -> None:
        payload = evidence.build_payload()

        self.assertEqual(
            payload["status"],
            "aabb_native_query_handle_m7_candidate_pending_external_review",
        )
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertTrue(payload["m7_candidate_reopen_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)
        self.assertEqual(payload["failed_checks"], [])
        self.assertEqual(
            {row["grid_count"] for row in payload["observed_rows"]},
            {32_768, 65_536},
        )
        for row in payload["observed_rows"]:
            self.assertGreaterEqual(
                row["optix_over_embree_cold_plus_collect_wall_speedup"],
                evidence.MATERIAL_WALL_SPEEDUP_FLOOR,
            )
            self.assertGreater(row["optix_over_embree_query_total_speedup"], 1.0)
            self.assertTrue(row["optix_native_cache_observed"])
            self.assertTrue(row["matches_cpu_reference"])
            self.assertTrue(row["complete_candidate_coverage"])
            self.assertEqual(
                row["optix_cache_stats"]["native_range_intersection_misses"],
                1,
            )
            self.assertGreater(
                row["optix_cache_stats"]["native_range_intersection_hits"],
                1,
            )

    def test_markdown_keeps_boundary_wording(self) -> None:
        markdown = evidence.render_markdown(evidence.build_payload())

        self.assertIn("generic engine change", markdown)
        self.assertIn("M7 promotion authorized: `False`", markdown)
        self.assertIn("Broad V3-over-V2 claim authorized: `False`", markdown)
        self.assertIn("1.719x", markdown)
        self.assertIn("1.637x", markdown)


if __name__ == "__main__":
    unittest.main()

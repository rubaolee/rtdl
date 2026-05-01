from __future__ import annotations

import unittest

from scripts.goal1201_optix_slower_investigation_intake import build_intake
from scripts.goal1201_optix_slower_investigation_intake import to_markdown


class Goal1201OptixSlowerInvestigationIntakeTest(unittest.TestCase):
    def test_intake_records_expected_failed_labels(self) -> None:
        payload = build_intake()
        self.assertEqual(payload["status_summary"]["failed_count"], 5)
        self.assertIn("polygon_jaccard_optix_8192_chunk_64", payload["status_summary"]["failed_labels"])
        self.assertIn("db_embree_100000", payload["status_summary"]["failed_labels"])
        self.assertIn("db_optix_100000", payload["status_summary"]["failed_labels"])

    def test_jaccard_is_blocked_by_stability_failure(self) -> None:
        payload = build_intake()
        rows = {row["chunk_copies"]: row for row in payload["polygon_set_jaccard"]}
        self.assertEqual(rows[64]["status"], "failed")
        self.assertIsNone(rows[64]["chunk_policy"])
        self.assertEqual(
            payload["decisions"]["polygon_set_jaccard"],
            "blocked_existing_artifact_has_chunk64_failure_future_runs_must_use_public_safe_chunk_policy",
        )

    def test_road_hazard_reproduced_but_below_public_floor(self) -> None:
        payload = build_intake()
        road = payload["road_hazard_screening"]
        self.assertGreater(road["ratio_embree_over_optix"], 1.0)
        self.assertFalse(road["timing_floor_met"])
        self.assertFalse(road["public_positive_ratio_safe"])
        self.assertEqual(payload["public_positive_candidates_from_this_batch"], [])

    def test_hausdorff_has_normalized_repair_but_no_same_scale_pair(self) -> None:
        payload = build_intake()
        haus = payload["hausdorff_distance"]
        self.assertFalse(haus["same_scale_pair_available"])
        self.assertGreater(haus["normalized_optix_over_embree_throughput"], 1.0)
        self.assertEqual(payload["decisions"]["hausdorff_distance"], "normalized_repair_evidence_collected_same_scale_still_missing")

    def test_markdown_preserves_non_claim_boundary(self) -> None:
        text = to_markdown(build_intake())
        self.assertIn("does not authorize public docs", text)
        self.assertIn("public positive candidates from this batch: `none`", text)
        self.assertIn("Database", text)
        self.assertIn("Polygon Jaccard", text)

    def test_graph_records_kernel_and_total_ratios_separately(self) -> None:
        payload = build_intake()
        row = payload["graph_analytics"][-1]
        self.assertIsNotNone(row["optix_anyhit_kernel_sec"])
        self.assertIsNotNone(row["ratio_embree_over_optix_kernel"])
        self.assertEqual(
            payload["decisions"]["graph_analytics"],
            "rt_subpaths_completed_but_total_pack_prepare_dominated",
        )


if __name__ == "__main__":
    unittest.main()

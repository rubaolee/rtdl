from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ARTIFACT_ROOT = Path("docs/reports/goal1311_v1_5_jaccard_generic_fail_closed_collection_pod_results")


class Goal1312V15JaccardOptixSlowerReasonTest(unittest.TestCase):
    def test_pod_artifacts_explain_optix_slower_reason(self) -> None:
        embree = json.loads((ARTIFACT_ROOT / "embree_summary_128.json").read_text())
        optix = json.loads((ARTIFACT_ROOT / "optix_summary_128.json").read_text())

        reason = rt.validate_polygon_set_jaccard_optix_slower_reason(
            rt.polygon_set_jaccard_optix_slower_reason(
                embree_payload=embree,
                optix_payload=optix,
            )
        )

        self.assertTrue(reason["same_exact_summary"])
        self.assertEqual(reason["embree_candidate_row_count"], 384)
        self.assertEqual(reason["optix_candidate_row_count"], 256)
        self.assertGreater(reason["optix_candidate_discovery_sec"], reason["embree_candidate_discovery_sec"])
        self.assertGreater(reason["observed_pipeline_slowdown"], 1.0)
        self.assertIn("not a monolithic GPU Jaccard kernel", reason["reason"])
        self.assertIn("no positive Jaccard speedup wording", reason["claim_boundary"])

    def test_inventory_no_longer_has_vague_slower_reason_blocker(self) -> None:
        inventory = rt.validate_v1_5_generic_migration_inventory()
        by_row = {(row["app"], row["subpath"]): row for row in inventory}
        row = by_row[("polygon_set_jaccard", "chunked_candidate_scoring")]

        self.assertEqual(row["status"], "pod_verified_generic")
        self.assertNotIn("optix_still_slower_with_reason", row["remaining_app_specific_work"])
        self.assertIn("OptiX remains slower than Embree", row["boundary"])


if __name__ == "__main__":
    unittest.main()

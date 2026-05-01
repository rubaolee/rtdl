from __future__ import annotations

import unittest

from scripts.goal1197_optix_slower_app_investigation_manifest import build_manifest
from scripts.goal1197_optix_slower_app_investigation_manifest import to_markdown


class Goal1197OptixSlowerAppInvestigationManifestTest(unittest.TestCase):
    def test_manifest_targets_only_optix_slower_rows(self) -> None:
        payload = build_manifest()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(payload["slower_app_count"], 4)
        self.assertEqual(
            payload["slower_apps"],
            [
                "database_analytics",
                "graph_analytics",
                "polygon_pair_overlap_area_rows",
                "polygon_set_jaccard",
            ],
        )
        for row in payload["rows"]:
            self.assertLess(row["observed_ratio_embree_over_optix"], 1.0)
        self.assertEqual(payload["control_apps"], ["road_hazard_screening"])
        self.assertEqual(payload["same_scale_repair_apps"], ["hausdorff_distance"])

    def test_each_row_has_phase_fields_scales_and_decision_rules(self) -> None:
        payload = build_manifest()
        for row in payload["rows"]:
            with self.subTest(app=row["app"]):
                self.assertGreaterEqual(len(row["scales"]), 3)
                self.assertTrue(row["phase_fields"])
                self.assertIn("If", row["decision_rule"])
                self.assertTrue(any("optix" in command["label"] for command in row["commands"]))

    def test_jaccard_requires_stability_before_future_positive_wording(self) -> None:
        payload = build_manifest()
        jaccard = next(row for row in payload["rows"] if row["app"] == "polygon_set_jaccard")
        self.assertIn("nondeterministic", jaccard["hypothesis"])
        self.assertIn("fails parity", jaccard["decision_rule"])
        self.assertIn("stability", jaccard["decision_rule"])

    def test_polygon_pair_scale_sweep_holds_chunk_size_constant(self) -> None:
        payload = build_manifest()
        pair = next(row for row in payload["rows"] if row["app"] == "polygon_pair_overlap_area_rows")
        self.assertEqual({scale["chunk_copies"] for scale in pair["scales"]}, {100})
        self.assertIn("chunk_copies is held constant", pair["decision_rule"])

    def test_markdown_preserves_pod_batch_and_non_claim_boundaries(self) -> None:
        text = to_markdown(build_manifest())
        self.assertIn("Do not restart a pod per app", text)
        self.assertIn("does not authorize", text)
        self.assertIn("Positive Controls", text)
        self.assertIn("Same-Scale Repair Targets", text)
        self.assertIn("Embree copies=2000 and OptiX copies=1200000", text)


if __name__ == "__main__":
    unittest.main()

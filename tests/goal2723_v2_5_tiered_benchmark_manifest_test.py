from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2723_v2_5_tiered_benchmark_manifest_after_raydb_prepared_evidence_2026-05-30.md"


class Goal2723V25TieredBenchmarkManifestTest(unittest.TestCase):
    def test_manifest_covers_all_ten_apps_with_reviewed_tiers(self) -> None:
        manifest = rt.v2_5_tiered_benchmark_manifest()
        validation = rt.validate_v2_5_tiered_benchmark_manifest()

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(manifest["benchmark_app_count"], 10)
        self.assertEqual(manifest["tier_counts"], {"A": 3, "B": 4, "C": 3})
        self.assertTrue(manifest["same_contract_required"])
        self.assertTrue(manifest["phase_separated_timing_required"])
        self.assertTrue(manifest["sm70_plus_pod_required_for_triton_perf"])
        self.assertFalse(manifest["public_speedup_claim_authorized"])
        self.assertFalse(manifest["true_zero_copy_claim_authorized"])

        app_ids = {row["app_id"] for row in manifest["apps"]}
        self.assertEqual(
            app_ids,
            {
                "raydb_style",
                "triangle_counting",
                "spatial_rayjoin",
                "librts_spatial_index",
                "rt_dbscan",
                "rtnn",
                "barnes_hut",
                "hausdorff_xhd",
                "contact_manifold",
                "robot_collision",
            },
        )

    def test_raydb_row_records_prepared_goal2720_goal2722_evidence(self) -> None:
        manifest = rt.v2_5_tiered_benchmark_manifest()
        rows = {row["app_id"]: row for row in manifest["apps"]}
        raydb = rows["raydb_style"]

        self.assertEqual(raydb["tier"], "A")
        self.assertEqual(
            raydb["canonical_harness_status"],
            "ready_with_goal2720_goal2722_goal2727_prepared_pod_evidence",
        )
        self.assertIn("Goal2727 prepared fused-opponent", raydb["pod_evidence_status"])
        self.assertIn("primitive-first explain output", raydb["next_action"])
        self.assertIn("segmented_count_i64", raydb["required_partner_operations"])
        self.assertIn("segmented_max_f64", raydb["required_partner_operations"])

    def test_tier_c_rows_are_not_partner_parity_requirements(self) -> None:
        manifest = rt.v2_5_tiered_benchmark_manifest()
        tier_c = [row for row in manifest["apps"] if row["tier"] == "C"]

        self.assertEqual(
            {row["app_id"] for row in tier_c},
            {"contact_manifold", "robot_collision", "librts_spatial_index"},
        )
        for row in tier_c:
            with self.subTest(app_id=row["app_id"]):
                self.assertIn("no-regression", row["parity_target"])
                self.assertNotIn("partner parity", row["parity_target"])
                self.assertIn("rt_core", row["benchmark_track"])

    def test_tier_b_rows_name_fallback_or_new_generic_continuation_work(self) -> None:
        manifest = rt.v2_5_tiered_benchmark_manifest()
        rows = {row["app_id"]: row for row in manifest["apps"]}

        self.assertIn("fallback", rows["rt_dbscan"]["next_action"])
        self.assertIn("grouped_components_or_fallback", rows["rt_dbscan"]["required_partner_operations"])
        self.assertIn("bounded_topk_or_ranked_summary", rows["rtnn"]["required_partner_operations"])
        self.assertIn("grouped_vector_sum", rows["barnes_hut"]["required_partner_operations"])
        self.assertIn("grouped_argmax_witness", rows["hausdorff_xhd"]["required_partner_operations"])

    def test_spatial_rayjoin_and_librts_tier_labels_are_split_precisely(self) -> None:
        manifest = rt.v2_5_tiered_benchmark_manifest()
        rows = {row["app_id"]: row for row in manifest["apps"]}
        spatial = rows["spatial_rayjoin"]
        librts = rows["librts_spatial_index"]

        self.assertEqual(spatial["tier"], "A")
        self.assertIn("Tier A count/parity", spatial["parity_target"])
        self.assertIn("deferred Tier B", spatial["next_action"])
        self.assertIn("rows_overlay_deferred_tier_b", spatial["benchmark_track"])

        self.assertEqual(librts["tier"], "C")
        self.assertEqual(librts["required_partner_operations"], ())
        self.assertIn("no-regression", librts["parity_target"])
        self.assertIn("no_partner_parity", librts["benchmark_track"])

    def test_report_and_public_api_record_manifest_boundary(self) -> None:
        self.assertIn("v2_5_tiered_benchmark_manifest", rt.__all__)
        self.assertIn("validate_v2_5_tiered_benchmark_manifest", rt.__all__)
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("v2.5 Tiered Benchmark Manifest", text)
        self.assertIn("not partner parity", text)
        self.assertIn("no public speedup", text)
        self.assertIn("same-contract command", text)


if __name__ == "__main__":
    unittest.main()

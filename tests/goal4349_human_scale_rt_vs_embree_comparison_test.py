import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "docs" / "reports" / "goal4349_human_scale_rt_vs_embree_comparison_2026-06-12.json"
RUNNER = ROOT / "scripts" / "rtdl_human_scale_rt_vs_embree_comparison.py"


class Goal4349HumanScaleRtVsEmbreeComparisonTest(unittest.TestCase):
    def test_packet_is_accepted_and_human_scale(self) -> None:
        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["validation"]["status"], "accept")
        self.assertEqual(len(payload["rows"]), 11)
        apps = {row["app"] for row in payload["rows"]}
        self.assertEqual(
            apps,
            {
                "barnes_hut",
                "contact_manifold",
                "hausdorff_xhd",
                "librts_spatial_index",
                "raydb_style",
                "robot_collision",
                "rt_dbscan",
                "rtnn",
                "spatial_rayjoin_lsi",
                "spatial_rayjoin_pip",
                "triangle_counting",
            },
        )
        for row in payload["rows"]:
            self.assertGreaterEqual(row["optix_total_sec"], 1.0, row["app"])
            self.assertLessEqual(row["optix_total_sec"], 10.0, row["app"])
            self.assertGreaterEqual(row["embree_total_sec"], 1.0, row["app"])
            self.assertLessEqual(row["embree_total_sec"], 10.0, row["app"])
            self.assertGreater(row["speedup_embree_per_iter_div_optix_per_iter"], 0.0, row["app"])
            self.assertTrue(row["correct"], row["app"])

    def test_raydb_uses_prepared_embree_backend_surface(self) -> None:
        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        raydb = next(row for row in payload["rows"] if row["app"] == "raydb_style")
        self.assertEqual(raydb["comparison_status"], "clean_backend_swap_prepared_phase")
        self.assertEqual(raydb["contract"], "prepared_ray_triangle_grouped_i64_reduction_count")
        self.assertEqual(raydb["best_embree_threads"], 64)
        self.assertGreater(raydb["speedup_embree_per_iter_div_optix_per_iter"], 10.0)

    def test_rows_have_reasonability_review_and_public_claim_scope(self) -> None:
        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        for row in payload["rows"]:
            self.assertIn("reasonability_verdict", row, row["app"])
            self.assertIn("only_material_diff_claim", row, row["app"])
            self.assertIn("speedup_explanation", row, row["app"])
            self.assertIn("public_wording", row, row["app"])
            self.assertIn("divided by", row["speedup_explanation"], row["app"])
            self.assertTrue(row["public_wording"], row["app"])

    def test_stale_output_rows_were_replaced_by_current_prepared_surfaces(self) -> None:
        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        rows = {row["app"]: row for row in payload["rows"]}
        for app in ("rtnn", "spatial_rayjoin_lsi", "spatial_rayjoin_pip"):
            self.assertEqual(rows[app]["comparison_status"], "clean_backend_swap_prepared_phase")
            self.assertNotIn("no_output_surface_differs", rows[app]["only_material_diff_claim"])
        self.assertLess(rows["spatial_rayjoin_pip"]["speedup_embree_per_iter_div_optix_per_iter"], 1.0)
        self.assertIn("Embree is faster", rows["spatial_rayjoin_pip"]["speedup_explanation"])
        self.assertEqual(
            rows["robot_collision"]["comparison_status"],
            "clean_backend_swap_traversal_phase_only",
        )
        self.assertEqual(
            rows["triangle_counting"]["comparison_status"],
            "clean_backend_swap_prepared_phase",
        )
        self.assertIn(
            "yes_for_prepared_weighted_any_hit_summary",
            rows["triangle_counting"]["only_material_diff_claim"],
        )

    def test_runner_records_duration_bounded_protocol(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertIn("duration_bounded_throughput", source)
        self.assertIn("raydb_embree_t64_r240", source)
        self.assertIn("rayjoin_lsi_optix_r5000", source)
        self.assertIn("RTDL_RAYJOIN_PUBLIC_COUNTY_CDB", source)
        self.assertIn("rtnn_optix_r40", source)


if __name__ == "__main__":
    unittest.main()

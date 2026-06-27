import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTE_MAP = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_p0_route_capability_map_2026-06-20.json"


EXPECTED_APPS = {
    "barnes_hut",
    "contact_manifold",
    "hausdorff_xhd",
    "librts_spatial_index",
    "raydb_style",
    "robot_collision",
    "rt_dbscan",
    "rtnn",
    "spatial_rayjoin",
    "triangle_counting",
}


class V3PhoenixRouteCapabilityMapTest(unittest.TestCase):
    def payload(self):
        return json.loads(ROUTE_MAP.read_text(encoding="utf-8"))

    def test_route_map_exists_and_is_not_release_authorization(self):
        payload = self.payload()
        self.assertEqual(payload["status"], "active_planning_not_release")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertEqual(payload["phoenix_m7_qualified_release_rows"], 0)
        self.assertEqual(payload["summary"]["m7_qualified_rows"], 0)

    def test_all_ratio_rows_have_generic_capabilities(self):
        payload = self.payload()
        allowed = set(payload["allowed_generic_capabilities"])
        rows = payload["rows"]
        self.assertEqual(len(rows), 19)
        self.assertEqual(payload["summary"]["row_count"], 19)
        self.assertEqual({row["app_id"] for row in rows}, EXPECTED_APPS)
        self.assertEqual(payload["summary"]["rows_without_generic_capability"], 0)
        self.assertEqual(
            payload["summary"]["p0_or_blocked_rows"],
            len([row for row in rows if row["priority"].startswith("P0")]),
        )
        for row in rows:
            self.assertIn(row["generic_capability"], allowed)
            self.assertIn(row["release_evidence_status"], {"not_m7_qualified", "blocked_by_paired_regression"})
            self.assertNotEqual(row["claim_boundary"], "")

    def test_broad_geomean_denominator_is_preserved(self):
        rule = self.payload()["broad_v2_v3_denominator_rule"]
        self.assertEqual(rule["original_same_metric_comparison_rows"], 46)
        self.assertAlmostEqual(rule["original_v3_geomean_speedup_vs_v2_14"], 1.012314056248152)
        self.assertFalse(rule["broad_v3_faster_than_v2_claim_authorized"])
        self.assertTrue(rule["subset_geomean_must_be_labeled_subset"])
        self.assertTrue(rule["removed_or_demoted_rows_do_not_change_broad_denominator"])

        downstream = self.payload()["downstream_reference_rule"]
        self.assertTrue(downstream["must_state_not_release_evidence"])
        self.assertTrue(downstream["must_state_phoenix_m7_qualified_release_rows_zero"])
        self.assertTrue(downstream["must_preserve_46_row_broad_denominator"])
        self.assertTrue(downstream["must_label_subset_geomeans_as_subset"])
        self.assertEqual(
            set(downstream["p1_subset_rows_may_not_replace_broad_geomean"]),
            {"threshold_summary", "aabb_candidate_stream", "collision_flag_stream"},
        )

    def test_p0_rows_include_goal4392_capability_frontiers(self):
        rows = self.payload()["rows"]
        p0_rows = {row["comparison_group"]: row for row in rows if row["priority"].startswith("P0")}
        for required in [
            "dbscan_cluster_signature",
            "raydb_grouped_count",
            "raydb_grouped_sum",
            "rayjoin_overlay_seed_authored_tiled_x2048",
            "triangle_count_rt_graph_2a1_cliques_80000",
            "rtnn_clustered_65536_ranked_summary",
            "barnes_hut_node_coverage_bodies_32768",
        ]:
            self.assertIn(required, p0_rows)

        capabilities = {row["generic_capability"] for row in p0_rows.values()}
        self.assertIn("component_union", capabilities)
        self.assertIn("grouped_reduction", capabilities)
        self.assertIn("point_location_topology_stream", capabilities)
        self.assertIn("prepared_graph_chunk", capabilities)
        self.assertIn("ranked_summary", capabilities)
        self.assertIn("aggregate_frontier", capabilities)

    def test_barnes_hut_is_blocked_by_paired_regression(self):
        rows = self.payload()["rows"]
        barnes = [row for row in rows if row["app_id"] == "barnes_hut"]
        self.assertTrue(barnes)
        self.assertTrue(all(row["priority"] == "P0_blocked" for row in barnes))
        self.assertTrue(all(row["release_evidence_status"] == "blocked_by_paired_regression" for row in barnes))


if __name__ == "__main__":
    unittest.main()

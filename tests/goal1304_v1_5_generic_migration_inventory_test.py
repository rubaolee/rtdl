from __future__ import annotations

import unittest

import rtdsl as rt


class Goal1304V15GenericMigrationInventoryTest(unittest.TestCase):
    def test_inventory_validates_and_has_expected_completed_rows(self) -> None:
        inventory = rt.validate_v1_5_generic_migration_inventory()
        by_row = {(row["app"], row["subpath"]): row for row in inventory}

        expected_completed = {
            ("graph_analytics", "visibility_edges_reusable_batches"),
            ("service_coverage_gaps", "gap_summary_prepared"),
            ("event_hotspot_screening", "count_summary_prepared"),
            ("ann_candidate_search", "candidate_threshold_prepared"),
            ("facility_knn_assignment", "coverage_threshold_prepared"),
            ("outlier_detection", "density_count"),
            ("dbscan_clustering", "core_count"),
            ("barnes_hut_force_app", "node_coverage_prepared"),
            ("hausdorff_distance", "directed_threshold_prepared"),
            ("robot_collision_screening", "prepared_count"),
        }
        self.assertLessEqual(expected_completed, set(by_row))
        for key in expected_completed:
            self.assertEqual(by_row[key]["status"], "pod_verified_generic")
            self.assertFalse(by_row[key]["public_wording_authorized"])

    def test_inventory_keeps_deferred_app_specific_work_explicit(self) -> None:
        inventory = rt.v1_5_generic_migration_inventory()
        by_row = {(row["app"], row["subpath"]): row for row in inventory}

        self.assertEqual(
            by_row[("robot_collision_screening", "prepared_pose_flags")]["status"],
            "deferred_app_specific",
        )
        self.assertIn(
            "define grouped count-to-boolean result layout",
            by_row[("robot_collision_screening", "prepared_pose_flags")]["remaining_app_specific_work"],
        )
        self.assertEqual(
            by_row[("database_analytics", "sales_risk_compact_summary")]["summary_primitive"],
            "REDUCE_INT(COUNT), REDUCE_INT(SUM)",
        )
        self.assertEqual(
            by_row[("polygon_pair_overlap_area_rows", "candidate_discovery_and_exact_area")]["summary_primitive"],
            "REDUCE_FLOAT(SUM)",
        )
        self.assertEqual(
            by_row[("polygon_set_jaccard", "chunked_candidate_scoring")]["status"],
            "diagnostic_blocked",
        )

    def test_inventory_has_no_frozen_backend_scope_or_public_wording(self) -> None:
        frozen = {"vulkan", "hiprt", "apple_rt"}
        for row in rt.validate_v1_5_generic_migration_inventory():
            with self.subTest(app=row["app"], subpath=row["subpath"]):
                self.assertFalse(set(row["backend_scope"]) & frozen)
                self.assertFalse(row["public_wording_authorized"])

    def test_blockers_name_grouped_reductions_and_public_wording_gate(self) -> None:
        blockers = "\n".join(rt.v1_5_generic_migration_blockers())
        self.assertIn("grouped REDUCE_INT(COUNT)", blockers)
        self.assertIn("grouped integer COUNT/SUM", blockers)
        self.assertIn("REDUCE_FLOAT(SUM)", blockers)
        self.assertIn("COLLECT_K_BOUNDED", blockers)
        self.assertIn("3-AI consensus", blockers)


if __name__ == "__main__":
    unittest.main()

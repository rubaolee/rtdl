from __future__ import annotations

import unittest

import rtdsl as rt
import rtdsl.v1_5_migration_inventory as inventory_module


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
            ("robot_collision_screening", "prepared_pose_flags"),
            ("database_analytics", "sales_risk_compact_summary"),
            ("polygon_pair_overlap_area_rows", "candidate_discovery_and_exact_area"),
            ("polygon_set_jaccard", "chunked_candidate_scoring"),
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
            "pod_verified_generic",
        )
        self.assertEqual(
            by_row[("robot_collision_screening", "prepared_pose_flags")]["remaining_app_specific_work"],
            (),
        )
        self.assertEqual(
            by_row[("database_analytics", "sales_risk_compact_summary")]["status"],
            "pod_verified_generic",
        )
        self.assertEqual(
            by_row[("database_analytics", "sales_risk_compact_summary")]["remaining_app_specific_work"],
            (),
        )
        self.assertEqual(
            by_row[("database_analytics", "sales_risk_compact_summary")]["summary_primitive"],
            "REDUCE_INT(COUNT), REDUCE_INT(SUM)",
        )
        self.assertEqual(
            by_row[("polygon_pair_overlap_area_rows", "candidate_discovery_and_exact_area")]["status"],
            "pod_verified_generic",
        )
        self.assertEqual(
            by_row[("polygon_pair_overlap_area_rows", "candidate_discovery_and_exact_area")][
                "remaining_app_specific_work"
            ],
            (),
        )
        self.assertEqual(
            by_row[("polygon_pair_overlap_area_rows", "candidate_discovery_and_exact_area")]["summary_primitive"],
            "REDUCE_FLOAT(SUM)",
        )
        self.assertEqual(
            by_row[("polygon_set_jaccard", "chunked_candidate_scoring")]["status"],
            "pod_verified_generic",
        )
        self.assertEqual(
            by_row[("polygon_set_jaccard", "chunked_candidate_scoring")]["remaining_app_specific_work"],
            (),
        )

    def test_inventory_has_no_frozen_backend_scope_or_public_wording(self) -> None:
        frozen = {"vulkan", "hiprt", "apple_rt"}
        for row in rt.validate_v1_5_generic_migration_inventory():
            with self.subTest(app=row["app"], subpath=row["subpath"]):
                self.assertFalse(set(row["backend_scope"]) & frozen)
                self.assertFalse(row["public_wording_authorized"])
                self.assertTrue(
                    "public speedup wording" in row["boundary"]
                    or "public wording" in row["boundary"]
                )

    def test_inventory_uses_only_declared_v1_5_primitive_sets(self) -> None:
        generic_primitives = set(rt.V1_5_STABLE_GENERIC_PRIMITIVES) | set(
            rt.V1_5_EXPERIMENTAL_GENERIC_PRIMITIVES
        )
        summary_primitives = set(rt.V1_5_STABLE_SUMMARY_PRIMITIVES)

        for row in rt.validate_v1_5_generic_migration_inventory():
            with self.subTest(app=row["app"], subpath=row["subpath"]):
                self.assertIn(row["generic_primitive"], generic_primitives)
                for primitive in row["summary_primitive"].split(","):
                    self.assertIn(primitive.strip(), summary_primitives)

    def test_inventory_rejects_unknown_generic_or_summary_primitives(self) -> None:
        good_row = dict(rt.validate_v1_5_generic_migration_inventory()[0])

        bad_generic = dict(good_row)
        bad_generic["generic_primitive"] = "UNBOUNDED_MAGIC_TRAVERSAL"
        with self.assertRaisesRegex(ValueError, "invalid v1.5 generic primitive"):
            inventory_module._validate_v1_5_generic_migration_inventory_rows((bad_generic,))

        bad_summary = dict(good_row)
        bad_summary["summary_primitive"] = "GROUPED_BOOL_FLAGS"
        with self.assertRaisesRegex(ValueError, "invalid v1.5 summary primitive"):
            inventory_module._validate_v1_5_generic_migration_inventory_rows((bad_summary,))

        bad_boundary = dict(good_row)
        bad_boundary["boundary"] = "visibility any-hit count only"
        with self.assertRaisesRegex(ValueError, "boundary must block public wording"):
            inventory_module._validate_v1_5_generic_migration_inventory_rows((bad_boundary,))

    def test_blockers_name_only_remaining_scope_and_public_wording_gates(self) -> None:
        blockers = "\n".join(rt.v1_5_generic_migration_blockers())
        self.assertIn("remaining_app_specific_work", blockers)
        self.assertIn("whole-app speedup wording remains blocked", blockers)
        self.assertIn("3-AI consensus", blockers)
        self.assertNotIn("prepared_pose_flags requires", blockers)
        self.assertNotIn("database compact summaries require", blockers)
        self.assertNotIn("polygon exact area and Jaccard scoring require", blockers)


if __name__ == "__main__":
    unittest.main()

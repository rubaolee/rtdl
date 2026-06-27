from __future__ import annotations

import unittest

import rtdsl.v4 as v4
from rtdsl.v4_app_compatibility import validate_v4_app_compatibility_catalog
from rtdsl.v4_goal4749_final_rt_core_protocol import APP_ORDER


class V4Goal4751AppCompatibilityCatalogTest(unittest.TestCase):
    def test_catalog_validates_all_apps(self) -> None:
        validation = validate_v4_app_compatibility_catalog()

        self.assertEqual("passed", validation["status"], validation["errors"])
        self.assertEqual(10, validation["row_count"])
        self.assertEqual([], validation["repair_required_apps"])

    def test_frontdoor_exposes_app_compatibility_catalog(self) -> None:
        rows = v4.v4_app_compatibility_rows()
        apps = [row["app"] for row in rows]

        self.assertEqual(list(APP_ORDER), apps)
        boundary = v4.claim_boundary_v4()
        self.assertEqual("v4_0_app_compatibility_superset_catalog_goal4751_in_progress", boundary["app_compatibility_status"])
        self.assertEqual(10, boundary["app_compatibility_row_count"])
        self.assertEqual((), boundary["app_compatibility_repair_required_apps"])

    def test_robot_contact_spatial_are_inherited_compatibility_rows_not_no_route(self) -> None:
        for app in ("robot_collision", "contact_manifold", "spatial_rayjoin"):
            with self.subTest(app=app):
                plan = v4.plan_v4_app_compatibility(app)
                self.assertEqual("compatibility_route_protocol_ready", plan.status)
                self.assertEqual("runnable_protocol_template", plan.v4_route_status)
                self.assertEqual("", plan.blocker)
                self.assertNotIn("no_v4_route", plan.v4_route_status)
                self.assertFalse(plan.release_claim_authorized)
                self.assertFalse(plan.v4_new_speed_claim_authorized)
                self.assertFalse(plan.inherited_compatibility_counts_as_speed)

    def test_runnable_apps_keep_support_but_not_speed_claims(self) -> None:
        for app in (
            "rt_dbscan",
            "raydb_style",
            "triangle_counting",
            "librts_spatial_index",
            "hausdorff_xhd",
            "rtnn",
            "robot_collision",
            "contact_manifold",
            "spatial_rayjoin",
            "barnes_hut",
        ):
            with self.subTest(app=app):
                plan = v4.plan_v4_app_compatibility(app)
                self.assertEqual("compatibility_route_protocol_ready", plan.status)
                self.assertEqual("runnable_protocol_template", plan.v4_route_status)
                self.assertFalse(plan.release_claim_authorized)
                self.assertFalse(plan.v4_new_speed_claim_authorized)
                self.assertFalse(plan.inherited_compatibility_counts_as_speed)

    def test_unknown_app_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            v4.plan_v4_app_compatibility("made_up_app")


if __name__ == "__main__":
    unittest.main()

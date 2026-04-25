import unittest
from pathlib import Path

import rtdsl as rt


class Goal803RtCoreAppMaturityContractTest(unittest.TestCase):
    def test_every_public_app_has_rt_core_maturity_row(self) -> None:
        maturity = rt.rt_core_app_maturity_matrix()
        self.assertEqual(set(maturity), set(rt.public_apps()))
        for app, row in maturity.items():
            with self.subTest(app=app):
                self.assertEqual(row.app, app)
                self.assertIn(row.current_status, rt.RT_CORE_APP_MATURITY_STATUSES)
                self.assertIn(row.target_status, rt.RT_CORE_APP_MATURITY_STATUSES)
                self.assertTrue(row.required_action.strip())
                self.assertTrue(row.cloud_policy.strip())

    def test_current_real_rt_core_claim_candidates_are_only_prepared_paths(self) -> None:
        maturity = rt.rt_core_app_maturity_matrix()
        ready = [
            app
            for app, row in maturity.items()
            if row.current_status == "rt_core_ready"
        ]
        self.assertEqual(
            ready,
            [
                "service_coverage_gaps",
                "event_hotspot_screening",
                "outlier_detection",
                "dbscan_clustering",
                "robot_collision_screening",
            ],
        )
        partial = {
            app
            for app, row in maturity.items()
            if row.current_status == "rt_core_partial_ready"
        }
        self.assertIn("facility_knn_assignment", partial)
        self.assertIn("ann_candidate_search", partial)
        self.assertIn("barnes_hut_force_app", partial)

    def test_every_general_app_targets_rt_core_or_is_engine_specific(self) -> None:
        for app, row in rt.rt_core_app_maturity_matrix().items():
            with self.subTest(app=app):
                if app in {"apple_rt_demo", "hiprt_ray_triangle_hitcount"}:
                    self.assertEqual(row.target_status, "not_nvidia_rt_core_target")
                else:
                    self.assertEqual(row.target_status, "rt_core_ready")

    def test_cloud_policy_rejects_per_app_pod_restarts(self) -> None:
        for app, row in rt.rt_core_app_maturity_matrix().items():
            with self.subTest(app=app):
                self.assertNotIn("restart per app", row.cloud_policy.lower())
                if row.current_status != "rt_core_ready":
                    policy = row.cloud_policy.lower()
                    self.assertTrue(
                        "no " in policy
                        or "cloud only after" in policy
                        or "cloud only in a focused" in policy
                        or "never include" in policy
                    )

    def test_public_api_is_exported(self) -> None:
        for symbol in (
            "rt_core_app_maturity",
            "rt_core_app_maturity_matrix",
            "RT_CORE_APP_MATURITY_STATUSES",
        ):
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, rt.__all__)

    def test_doc_records_contract(self) -> None:
        text = (Path(__file__).resolve().parents[1] / "docs" / "app_engine_support_matrix.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "RT-Core App Maturity Contract",
            "rtdsl.rt_core_app_maturity_matrix()",
            "rt_core_ready",
            "needs_rt_core_redesign",
            "needs_optix_app_surface",
            "not_nvidia_rt_core_target",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

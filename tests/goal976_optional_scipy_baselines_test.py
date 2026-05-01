from __future__ import annotations

import unittest


class Goal976OptionalScipyBaselinesTest(unittest.TestCase):
    def test_collector_targets_remaining_optional_scipy_baselines(self) -> None:
        module = __import__("scripts.goal976_optional_scipy_baselines", fromlist=["_artifact_path", "load_goal835_row"])
        targets = (
            (
                "outlier_detection",
                "prepared_fixed_radius_density_summary",
                "scipy_or_reference_neighbor_baseline_when_used_in_app_report",
            ),
            (
                "dbscan_clustering",
                "prepared_fixed_radius_core_flags",
                "scipy_or_reference_neighbor_baseline_when_used_in_app_report",
            ),
            (
                "service_coverage_gaps",
                "prepared_gap_summary",
                "scipy_baseline_when_available",
            ),
            (
                "event_hotspot_screening",
                "prepared_count_summary",
                "scipy_baseline_when_available",
            ),
        )
        for app, path_name, baseline in targets:
            with self.subTest(app=app, path_name=path_name, baseline=baseline):
                row = module.load_goal835_row(app=app, path_name=path_name, baseline_name=baseline)
                artifact_path = module._artifact_path(app, path_name, baseline)
                self.assertIn(baseline, row["required_baselines"])
                self.assertEqual(artifact_path.name, f"goal835_baseline_{app}_{path_name}_{baseline}_2026-04-23.json")

    def test_fixed_radius_scipy_artifact_schema_without_importing_scipy(self) -> None:
        module = __import__("scripts.goal976_optional_scipy_baselines", fromlist=["_outlier_summary", "_dbscan_summary"])
        self.assertEqual(
            module._outlier_summary(
                (
                    {"point_id": 1, "is_outlier": False},
                    {"point_id": 2, "is_outlier": True},
                )
            ),
            {"point_count": 2, "threshold_reached_count": 1, "outlier_count": 1},
        )
        self.assertEqual(
            module._dbscan_summary(
                (
                    {"point_id": 1, "is_core": True},
                    {"point_id": 2, "is_core": False},
                )
            ),
            {"point_count": 2, "threshold_reached_count": 1, "core_count": 1},
        )


if __name__ == "__main__":
    unittest.main()

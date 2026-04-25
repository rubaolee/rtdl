from __future__ import annotations

import unittest

from scripts.goal901_pre_cloud_app_closure_gate import run_gate


class Goal901PreCloudAppClosureGateTest(unittest.TestCase):
    def test_gate_is_valid_and_covers_all_nvidia_target_apps(self) -> None:
        payload = run_gate()

        self.assertTrue(payload["valid"], payload["errors"])
        self.assertEqual(payload["counts"]["public_app_count"], 18)
        self.assertEqual(payload["counts"]["nvidia_target_app_count"], 16)
        self.assertEqual(payload["counts"]["non_nvidia_app_count"], 2)
        self.assertEqual(payload["counts"]["active_entry_count"], 8)
        self.assertEqual(payload["counts"]["deferred_entry_count"], 9)
        self.assertEqual(payload["counts"]["full_batch_entry_count"], 17)
        self.assertEqual(payload["counts"]["full_batch_unique_command_count"], 16)
        self.assertEqual(payload["errors"]["missing_cloud_coverage"], [])
        self.assertEqual(payload["errors"]["unsupported_artifact_apps"], [])

    def test_gate_records_expected_non_nvidia_apps_and_duplicate_output(self) -> None:
        payload = run_gate()

        self.assertEqual(payload["apps"]["non_nvidia"], ["apple_rt_demo", "hiprt_ray_triangle_hitcount"])
        duplicates = payload["duplicate_output_paths"]
        self.assertIn("docs/reports/goal759_outlier_dbscan_fixed_radius_rtx.json", duplicates)
        self.assertEqual(
            duplicates["docs/reports/goal759_outlier_dbscan_fixed_radius_rtx.json"],
            ["prepared_fixed_radius_core_flags", "prepared_fixed_radius_density_summary"],
        )

    def test_gate_boundary_requires_cloud_for_next_material_evidence(self) -> None:
        payload = run_gate()

        self.assertIn("does not start cloud", payload["boundary"])
        self.assertIn("does not", payload["boundary"])
        self.assertIn("requires a real RTX cloud run", payload["next_step_if_valid"])


if __name__ == "__main__":
    unittest.main()

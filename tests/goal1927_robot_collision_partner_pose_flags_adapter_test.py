from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
PARTNER_ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
APP_ADAPTER = ROOT / "src" / "rtdsl" / "app_adapters" / "robot_collision.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
REPORT = ROOT / "docs" / "reports" / "goal1927_robot_collision_partner_pose_flags_adapter_2026-05-13.md"


class Goal1927RobotCollisionPartnerPoseFlagsAdapterTest(unittest.TestCase):
    def test_adapter_reduces_generic_ray_flags_to_partner_pose_flags(self) -> None:
        text = APP_ADAPTER.read_text(encoding="utf-8")

        self.assertIn("def allocate_robot_collision_pose_partner_device_output_columns", text)
        self.assertIn("def robot_collision_pose_flags_optix_prepared_partner_device_columns", text)
        self.assertIn("prepared_scene.write_device_any_hit_flags", text)
        self.assertIn("_scatter_ray_flags_to_pose_flags", text)
        self.assertIn("partner_group_any_by_key", text)
        self.assertIn('"native_engine_row_contract": "generic_ray_primitive_any_hit_flags"', text)
        self.assertIn('"app_flag_materialization": "partner_gpu_pose_flags_from_native_any_hit_ray_flags"', text)
        self.assertIn('"app_flag_host_materialization": False', text)
        self.assertIn('"v2_0_release_authorized": False', text)
        self.assertIn('"whole_app_speedup_claim_authorized": False', text)

    def test_adapter_is_not_in_shared_partner_adapters_module(self) -> None:
        text = PARTNER_ADAPTERS.read_text(encoding="utf-8")

        self.assertNotIn("def allocate_robot_collision_pose_partner_device_output_columns", text)
        self.assertNotIn("def robot_collision_pose_flags_optix_prepared_partner_device_columns", text)

    def test_adapter_is_publicly_imported(self) -> None:
        text = INIT.read_text(encoding="utf-8")

        self.assertIn("allocate_robot_collision_pose_partner_device_output_columns", text)
        self.assertIn("robot_collision_pose_flags_optix_prepared_partner_device_columns", text)

    def test_report_preserves_scope_and_next_pod_work(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: adapter-ready-pod-needed", text)
        self.assertIn("robot_collision_screening", text)
        self.assertIn("generic_ray_primitive_any_hit_flags", text)
        self.assertIn("does not authorize v2.0 release", text)
        self.assertIn("does not claim whole-app acceleration", text)
        self.assertIn("Torch and CuPy", text)


if __name__ == "__main__":
    unittest.main()

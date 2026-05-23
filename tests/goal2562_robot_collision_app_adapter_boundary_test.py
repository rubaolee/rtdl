from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.app_adapters import robot_collision as robot_adapter


ROOT = Path(__file__).resolve().parents[1]
PARTNER_ADAPTERS = ROOT / "src/rtdsl/partner_adapters.py"
APP_ADAPTER = ROOT / "src/rtdsl/app_adapters/robot_collision.py"
INIT = ROOT / "src/rtdsl/__init__.py"
REPORT = ROOT / "docs/reports/goal2562_robot_collision_app_adapter_boundary_2026-05-23.md"


class Goal2562RobotCollisionAppAdapterBoundaryTest(unittest.TestCase):
    def test_robot_collision_adapter_lives_in_app_adapter_namespace(self) -> None:
        shared_text = PARTNER_ADAPTERS.read_text(encoding="utf-8")
        app_text = APP_ADAPTER.read_text(encoding="utf-8")

        self.assertNotIn("robot_collision_pose_flags_optix_prepared_partner_device_columns", shared_text)
        self.assertNotIn("allocate_robot_collision_pose_partner_device_output_columns", shared_text)
        self.assertIn("robot_collision_pose_flags_optix_prepared_partner_device_columns", app_text)
        self.assertIn("allocate_robot_collision_pose_partner_device_output_columns", app_text)
        self.assertIn("partner_group_any_by_key", app_text)

    def test_top_level_compatibility_exports_remain(self) -> None:
        self.assertIs(
            rt.robot_collision_pose_flags_optix_prepared_partner_device_columns,
            robot_adapter.robot_collision_pose_flags_optix_prepared_partner_device_columns,
        )
        self.assertIs(
            rt.allocate_robot_collision_pose_partner_device_output_columns,
            robot_adapter.allocate_robot_collision_pose_partner_device_output_columns,
        )
        init_text = INIT.read_text(encoding="utf-8")
        self.assertIn("from .app_adapters import robot_collision_pose_flags_optix_prepared_partner_device_columns", init_text)
        self.assertIn("from .app_adapters import allocate_robot_collision_pose_partner_device_output_columns", init_text)

    def test_report_records_app_adapter_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2562", text)
        self.assertIn("shared partner adapter module no longer carries robot-collision-specific\nfunctions", text)
        self.assertIn("top-level `rtdsl` exports remain", text)


if __name__ == "__main__":
    unittest.main()

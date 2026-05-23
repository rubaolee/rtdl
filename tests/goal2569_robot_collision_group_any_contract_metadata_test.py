from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_ADAPTER = ROOT / "src/rtdsl/app_adapters/robot_collision.py"
REPORT = ROOT / "docs/reports/goal2569_robot_collision_group_any_contract_metadata_2026-05-23.md"


class Goal2569RobotCollisionGroupAnyContractMetadataTest(unittest.TestCase):
    def test_robot_adapter_uses_shared_group_any_contract_metadata(self) -> None:
        text = APP_ADAPTER.read_text(encoding="utf-8")
        self.assertIn("GroupedReductionSpec", text)
        self.assertIn("GroupedReductionCapacityStatus", text)
        self.assertIn('operation="group_any"', text)
        self.assertIn('group_keys=("pose_index",)', text)
        self.assertIn('"grouped_reduction_contract": grouped_reduction_spec.to_metadata()', text)
        self.assertIn(
            '"grouped_reduction_capacity_status": grouped_reduction_capacity_status.to_metadata()',
            text,
        )

    def test_robot_adapter_remains_app_scoped_not_shared_partner_core(self) -> None:
        text = APP_ADAPTER.read_text(encoding="utf-8")
        self.assertIn('"adapter": "robot_collision_pose_flags_optix_prepared_partner_device_columns"', text)
        self.assertIn('"native_engine_row_contract": "generic_ray_primitive_any_hit_flags"', text)
        self.assertIn("partner_group_any_by_key", text)

    def test_report_records_group_any_bridge_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2569", text)
        self.assertIn("group_any", text)
        self.assertIn("GroupedReductionSpec", text)
        self.assertIn("app-adapter metadata only", text)
        self.assertIn("does not move robot semantics into native engines", text)


if __name__ == "__main__":
    unittest.main()

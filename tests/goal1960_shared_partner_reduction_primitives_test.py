from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
REPORT = ROOT / "docs" / "reports" / "goal1960_shared_partner_reduction_primitives_2026-05-14.md"


class Goal1960SharedPartnerReductionPrimitivesTest(unittest.TestCase):
    def test_partner_adapter_exposes_shared_reduction_primitives(self) -> None:
        text = ADAPTERS.read_text(encoding="utf-8")

        for name in (
            "partner_group_count_by_key",
            "partner_group_sum_by_key",
            "partner_group_any_by_key",
            "partner_unique_pair_keys",
        ):
            self.assertIn(f"def {name}", text)
        self.assertIn("torch.bincount", text)
        self.assertIn("cupy.bincount", text)
        self.assertIn("scatter_add_", text)
        self.assertIn("cupy.add.at", text)

    def test_robot_collision_reuses_group_any_primitive(self) -> None:
        text = ADAPTERS.read_text(encoding="utf-8")

        self.assertIn("def _scatter_ray_flags_to_pose_flags", text)
        self.assertIn("partner_group_any_by_key(", text)
        self.assertIn("generic_ray_primitive_any_hit_flags", text)

    def test_public_init_exports_partner_reduction_primitives(self) -> None:
        text = INIT.read_text(encoding="utf-8")

        for name in (
            "partner_group_count_by_key",
            "partner_group_sum_by_key",
            "partner_group_any_by_key",
            "partner_unique_pair_keys",
        ):
            self.assertIn(f"from .partner_adapters import {name}", text)
            self.assertIn(f'"{name}"', text)

    def test_report_names_design_problem_and_unsolved_app_semantics(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("one-off reduction logic", text)
        self.assertIn("small partner reduction algebra", text)
        self.assertIn("generic graph traversal", text)
        self.assertIn("exact directed Hausdorff max-distance", text)
        self.assertIn("full DBSCAN cluster expansion", text)
        self.assertIn("Barnes-Hut force-vector accumulation", text)


if __name__ == "__main__":
    unittest.main()


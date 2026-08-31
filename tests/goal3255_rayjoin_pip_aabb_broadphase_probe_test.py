from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3255_rayjoin_pip_aabb_broadphase_probe.py"


class Goal3255RayJoinPipAabbBroadphaseProbeTest(unittest.TestCase):
    def test_probe_uses_existing_generic_aabb_and_closed_shape_primitives(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("prepare_optix_aabb_index_2d", text)
        self.assertIn("prepare_optix_aabb_point_queries_2d", text)
        self.assertIn("count_prepared_queries", text)
        self.assertIn("prepare_point_closed_shape_membership_2d_optix", text)
        self.assertIn("count_device_filtered", text)

    def test_probe_keeps_aabb_broadphase_semantics_bounded(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("aabb_broadphase_is_exact_membership", text)
        self.assertIn("aabb_broadphase_can_replace_closed_shape_count", text)
        self.assertIn("False", text)
        self.assertIn("candidate-to-predicate continuation", text)

    def test_polygon_aabb_helper_preserves_input_identifier_and_bounds(self) -> None:
        spec = importlib.util.spec_from_file_location("goal3255_probe", SCRIPT)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        self.assertIsNotNone(spec.loader)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        polygon = rt.Polygon(
            id=17,
            vertices=((2.0, 4.0), (-1.0, 6.0), (3.5, -2.0)),
        )
        box = module._polygon_aabb(polygon)
        self.assertEqual(box.id, 17)
        self.assertEqual(box.min_x, -1.0)
        self.assertEqual(box.min_y, -2.0)
        self.assertEqual(box.max_x, 3.5)
        self.assertEqual(box.max_y, 6.0)


if __name__ == "__main__":
    unittest.main()

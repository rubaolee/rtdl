from __future__ import annotations

import unittest

import rtdsl as rt
import rtdsl.primitives as primitives


class Goal2326PublicPrimitiveContractTest(unittest.TestCase):
    def test_contract_first_symbols_are_public(self) -> None:
        for name in [
            "ExecutionPolicy",
            "ExecutionReport",
            "ExecutionResult",
            "run",
            "primitives",
            "any_hit",
            "hit_count",
            "nearest",
            "within_radius",
            "shape_any_hit_rows",
            "shape_pair_overlap_rows",
        ]:
            self.assertTrue(hasattr(rt, name), name)

    def test_primitive_facade_is_generic_not_app_namespace(self) -> None:
        exported = set(primitives.__all__)
        for name in [
            "any_hit",
            "hit_count",
            "closest_hit",
            "nearest",
            "bounded_nearest",
            "within_radius",
            "intersections",
            "shape_hit_count",
            "shape_any_hit_rows",
            "shape_pair_overlap_rows",
            "shape_set_similarity",
        ]:
            self.assertIn(name, exported)

        forbidden_fragments = (
            "road",
            "hazard",
            "rayjoin",
            "hausdorff",
            "dbscan",
            "facility",
            "robot",
            "pose",
            "geo_",
        )
        bad = sorted(
            name
            for name in exported
            if any(fragment in name.lower() for fragment in forbidden_fragments)
        )
        self.assertEqual(bad, [])

    def test_no_core_domain_namespace_facade(self) -> None:
        for name in ["geo", "robotics", "road_hazard_priority", "rayjoin", "hausdorff"]:
            self.assertFalse(hasattr(rt, name), name)

    def test_dir_teaches_contract_first_surface(self) -> None:
        names = set(dir(rt))
        for name in [
            "ExecutionPolicy",
            "ExecutionReport",
            "run",
            "any_hit",
            "hit_count",
            "nearest",
            "shape_any_hit_rows",
        ]:
            self.assertIn(name, names)
        forbidden_fragments = (
            "road",
            "hazard",
            "rayjoin",
            "hausdorff",
            "dbscan",
            "facility",
            "robot",
            "pose",
            "app_",
        )
        bad = sorted(
            name
            for name in names
            if any(fragment in name.lower() for fragment in forbidden_fragments)
        )
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()

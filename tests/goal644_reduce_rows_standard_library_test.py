from __future__ import annotations

import unittest

import rtdsl as rt


class Goal644ReduceRowsStandardLibraryTest(unittest.TestCase):
    def test_grouped_count_preserves_first_seen_group_order(self) -> None:
        rows = (
            {"pose_id": 2, "link_id": 10, "blocked": 1},
            {"pose_id": 1, "link_id": 20, "blocked": 0},
            {"pose_id": 2, "link_id": 30, "blocked": 0},
        )

        self.assertEqual(
            rt.reduce_rows(rows, group_by="pose_id", op="count", output_field="link_rows"),
            (
                {"pose_id": 2, "link_rows": 2},
                {"pose_id": 1, "link_rows": 1},
            ),
        )

    def test_grouped_any_reduces_boolean_like_rows(self) -> None:
        rows = (
            {"pose_id": 1, "link_id": 10, "blocked": 0},
            {"pose_id": 1, "link_id": 20, "blocked": 1},
            {"pose_id": 2, "link_id": 10, "blocked": 0},
        )

        self.assertEqual(
            rt.reduce_rows(rows, group_by="pose_id", op="any", value="blocked", output_field="pose_collides"),
            (
                {"pose_id": 1, "pose_collides": 1},
                {"pose_id": 2, "pose_collides": 0},
            ),
        )

    def test_multi_field_group_sum_min_max(self) -> None:
        rows = (
            {"body_id": 1, "axis": "x", "force": 2.5, "distance": 4.0},
            {"body_id": 1, "axis": "x", "force": -0.5, "distance": 2.0},
            {"body_id": 1, "axis": "y", "force": 3.0, "distance": 5.0},
        )

        self.assertEqual(
            rt.reduce_rows(rows, group_by=("body_id", "axis"), op="sum", value="force"),
            (
                {"body_id": 1, "axis": "x", "sum_force": 2.0},
                {"body_id": 1, "axis": "y", "sum_force": 3.0},
            ),
        )
        self.assertEqual(
            rt.reduce_rows(rows, group_by="body_id", op="min", value="distance"),
            ({"body_id": 1, "min_distance": 2.0},),
        )
        self.assertEqual(
            rt.reduce_rows(rows, group_by="body_id", op="max", value="distance"),
            ({"body_id": 1, "max_distance": 5.0},),
        )

    def test_empty_input_semantics_are_bounded_and_explicit(self) -> None:
        self.assertEqual(rt.reduce_rows((), group_by="pose_id", op="count"), ())
        self.assertEqual(rt.reduce_rows((), op="count"), ({"count": 0},))
        self.assertEqual(rt.reduce_rows((), op="any", value="blocked"), ({"any_blocked": 0},))
        self.assertEqual(rt.reduce_rows((), op="sum", value="weight"), ({"sum_weight": 0},))
        with self.assertRaisesRegex(ValueError, "has no identity"):
            rt.reduce_rows((), op="max", value="distance")

    def test_argument_validation_prevents_silent_filter_or_schema_errors(self) -> None:
        rows = ({"probe_id": 1, "distance": 2.0},)

        with self.assertRaisesRegex(ValueError, "requires a non-empty value field"):
            rt.reduce_rows(rows, group_by="probe_id", op="max")
        with self.assertRaisesRegex(ValueError, "does not accept a value field"):
            rt.reduce_rows(rows, group_by="probe_id", op="count", value="distance")
        with self.assertRaisesRegex(ValueError, "missing required field"):
            rt.reduce_rows(rows, group_by="missing", op="count")
        with self.assertRaisesRegex(TypeError, "mapping objects"):
            rt.reduce_rows((("not", "a", "row"),), op="count")

    def test_app_style_any_hit_rows_reduce_to_collision_flags(self) -> None:
        edge_hits = (
            {"pose_id": 100, "link_id": 1, "ray_id": 10, "any_hit": 0},
            {"pose_id": 100, "link_id": 2, "ray_id": 11, "any_hit": 1},
            {"pose_id": 200, "link_id": 1, "ray_id": 12, "any_hit": 0},
            {"pose_id": 200, "link_id": 2, "ray_id": 13, "any_hit": 0},
        )

        self.assertEqual(
            rt.reduce_rows(edge_hits, group_by="pose_id", op="any", value="any_hit", output_field="pose_blocked"),
            (
                {"pose_id": 100, "pose_blocked": 1},
                {"pose_id": 200, "pose_blocked": 0},
            ),
        )


if __name__ == "__main__":
    unittest.main()

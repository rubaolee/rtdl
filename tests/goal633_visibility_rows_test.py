import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class Goal633VisibilityRowsTest(unittest.TestCase):
    def test_visibility_rows_2d_detects_blocker_between_observer_and_target(self) -> None:
        observers = (rt.Point(id=1, x=0.0, y=0.0),)
        targets = (rt.Point(id=2, x=10.0, y=0.0),)
        blockers = (
            rt.Triangle(id=10, x0=5.0, y0=-1.0, x1=5.0, y1=1.0, x2=6.0, y2=0.0),
        )

        rows = rt.visibility_rows_cpu(observers, targets, blockers)

        self.assertEqual(rows, ({"observer_id": 1, "target_id": 2, "visible": 0},))

    def test_visibility_rows_2d_ignores_blocker_behind_target(self) -> None:
        observers = (rt.Point(id=1, x=0.0, y=0.0),)
        targets = (rt.Point(id=2, x=10.0, y=0.0),)
        blockers = (
            rt.Triangle(id=11, x0=12.0, y0=-1.0, x1=12.0, y1=1.0, x2=13.0, y2=0.0),
        )

        rows = rt.visibility_rows_cpu(observers, targets, blockers)

        self.assertEqual(rows, ({"observer_id": 1, "target_id": 2, "visible": 1},))

    def test_visibility_rows_cardinality_is_observer_target_matrix(self) -> None:
        observers = (
            rt.Point(id=1, x=0.0, y=0.0),
            rt.Point(id=2, x=0.0, y=2.0),
        )
        targets = (
            rt.Point(id=10, x=10.0, y=0.0),
            rt.Point(id=11, x=10.0, y=2.0),
        )

        rows = rt.visibility_rows_cpu(observers, targets, blockers=())

        self.assertEqual(
            rows,
            (
                {"observer_id": 1, "target_id": 10, "visible": 1},
                {"observer_id": 1, "target_id": 11, "visible": 1},
                {"observer_id": 2, "target_id": 10, "visible": 1},
                {"observer_id": 2, "target_id": 11, "visible": 1},
            ),
        )

    def test_visibility_rows_3d_uses_finite_segment_not_infinite_ray(self) -> None:
        observers = (rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),)
        targets = (rt.Point3D(id=2, x=10.0, y=0.0, z=0.0),)
        blocker_between = (
            rt.Triangle3D(id=20, x0=5.0, y0=-1.0, z0=-1.0, x1=5.0, y1=1.0, z1=-1.0, x2=5.0, y2=0.0, z2=1.0),
        )
        blocker_behind = (
            rt.Triangle3D(id=21, x0=12.0, y0=-1.0, z0=-1.0, x1=12.0, y1=1.0, z1=-1.0, x2=12.0, y2=0.0, z2=1.0),
        )

        self.assertEqual(rt.visibility_rows_cpu(observers, targets, blocker_between)[0]["visible"], 0)
        self.assertEqual(rt.visibility_rows_cpu(observers, targets, blocker_behind)[0]["visible"], 1)

    def test_visibility_rows_rejects_mixed_dimensions_and_zero_length(self) -> None:
        with self.assertRaisesRegex(ValueError, "one dimensionality"):
            rt.visibility_rows_cpu((rt.Point(id=1, x=0.0, y=0.0),), (rt.Point3D(id=2, x=1.0, y=0.0, z=0.0),), ())

        with self.assertRaisesRegex(ValueError, "distinct observer and target"):
            rt.visibility_rows_cpu((rt.Point(id=1, x=0.0, y=0.0),), (rt.Point(id=2, x=0.0, y=0.0),), ())

        with self.assertRaisesRegex(ValueError, "blocker triangles must match"):
            rt.visibility_rows_cpu(
                (rt.Point(id=1, x=0.0, y=0.0),),
                (rt.Point(id=2, x=1.0, y=0.0),),
                (rt.Triangle3D(id=20, x0=0.5, y0=-1.0, z0=-1.0, x1=0.5, y1=1.0, z1=-1.0, x2=0.5, y2=0.0, z2=1.0),),
            )


if __name__ == "__main__":
    unittest.main()

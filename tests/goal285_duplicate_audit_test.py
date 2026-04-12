import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class Goal285DuplicateAuditTest(unittest.TestCase):
    def test_find_exact_cross_package_matches_reports_exact_duplicate(self) -> None:
        query_points = (
            rt.Point3D(id=1, x=1.0, y=2.0, z=3.0),
            rt.Point3D(id=2, x=4.0, y=5.0, z=6.0),
        )
        search_points = (
            rt.Point3D(id=10, x=7.0, y=8.0, z=9.0),
            rt.Point3D(id=11, x=1.0, y=2.0, z=3.0),
        )
        matches = rt.find_exact_cross_package_matches(query_points, search_points)
        self.assertEqual(
            matches,
            (
                rt.ExactCrossPackageMatch(
                    query_id=1,
                    search_id=11,
                    x=1.0,
                    y=2.0,
                    z=3.0,
                ),
            ),
        )


if __name__ == "__main__":
    unittest.main()

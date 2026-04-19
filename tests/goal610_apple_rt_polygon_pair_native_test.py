from __future__ import annotations

import platform
import unittest

import rtdsl as rt


def apple_rt_available() -> bool:
    if platform.system() != "Darwin":
        return False
    try:
        rt.apple_rt_context_probe()
        return True
    except Exception:
        return False


@rt.kernel(backend="rtdl", precision="float_approx")
def polygon_overlap_kernel():
    left = rt.input("left", rt.Polygons, layout=rt.Polygon2DLayout, role="probe")
    right = rt.input("right", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.polygon_pair_overlap_area_rows(exact=False))
    return rt.emit(
        hits,
        fields=["left_polygon_id", "right_polygon_id", "intersection_area", "left_area", "right_area", "union_area"],
    )


@rt.kernel(backend="rtdl", precision="float_approx")
def polygon_jaccard_kernel():
    left = rt.input("left", rt.Polygons, layout=rt.Polygon2DLayout, role="probe")
    right = rt.input("right", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.polygon_set_jaccard(exact=False))
    return rt.emit(hits, fields=["intersection_area", "left_area", "right_area", "union_area", "jaccard_similarity"])


def _square(polygon_id: int, x0: float, y0: float, x1: float, y1: float) -> rt.Polygon:
    return rt.Polygon(id=polygon_id, vertices=((x0, y0), (x1, y0), (x1, y1), (x0, y1)))


def _assert_rows_almost_equal(testcase: unittest.TestCase, actual, expected) -> None:
    actual = tuple(sorted(actual, key=lambda row: tuple((key, row[key]) for key in sorted(row))))
    expected = tuple(sorted(expected, key=lambda row: tuple((key, row[key]) for key in sorted(row))))
    testcase.assertEqual(len(actual), len(expected))
    for actual_row, expected_row in zip(actual, expected):
        testcase.assertEqual(set(actual_row), set(expected_row))
        for key, expected_value in expected_row.items():
            actual_value = actual_row[key]
            if isinstance(expected_value, float):
                testcase.assertAlmostEqual(float(actual_value), expected_value, places=5)
            else:
                testcase.assertEqual(actual_value, expected_value)


@unittest.skipUnless(apple_rt_available(), "Apple RT backend is not available")
class Goal610AppleRtPolygonPairNativeTest(unittest.TestCase):
    def _case(self) -> dict[str, tuple[rt.Polygon, ...]]:
        return {
            "left": (
                _square(10, 0.0, 0.0, 3.0, 3.0),
                _square(11, 10.0, 10.0, 11.0, 11.0),
            ),
            "right": (
                _square(20, 2.0, 2.0, 5.0, 5.0),
                _square(21, 1.0, 1.0, 2.0, 2.0),
            ),
        }

    def test_overlap_native_only_matches_cpu_reference(self) -> None:
        case = self._case()
        _assert_rows_almost_equal(
            self,
            rt.run_apple_rt(polygon_overlap_kernel, native_only=True, **case),
            rt.run_cpu_python_reference(polygon_overlap_kernel, **case),
        )

    def test_jaccard_native_only_matches_cpu_reference(self) -> None:
        case = self._case()
        _assert_rows_almost_equal(
            self,
            rt.run_apple_rt(polygon_jaccard_kernel, native_only=True, **case),
            rt.run_cpu_python_reference(polygon_jaccard_kernel, **case),
        )

    def test_direct_helpers_match_cpu(self) -> None:
        case = self._case()
        _assert_rows_almost_equal(
            self,
            rt.polygon_pair_overlap_area_rows_apple_rt(case["left"], case["right"]),
            rt.polygon_pair_overlap_area_rows_cpu(case["left"], case["right"]),
        )
        _assert_rows_almost_equal(
            self,
            rt.polygon_set_jaccard_apple_rt(case["left"], case["right"]),
            rt.polygon_set_jaccard_cpu(case["left"], case["right"]),
        )


if __name__ == "__main__":
    unittest.main()

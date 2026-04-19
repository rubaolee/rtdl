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
def overlay_kernel():
    left = rt.input("left", rt.Polygons, layout=rt.Polygon2DLayout, role="probe")
    right = rt.input("right", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.overlay_compose())
    return rt.emit(hits, fields=["left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"])


def _square(polygon_id: int, x0: float, y0: float, x1: float, y1: float) -> rt.Polygon:
    return rt.Polygon(id=polygon_id, vertices=((x0, y0), (x1, y0), (x1, y1), (x0, y1)))


@unittest.skipUnless(apple_rt_available(), "Apple RT backend is not available")
class Goal611AppleRtOverlayComposeNativeTest(unittest.TestCase):
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

    def test_native_only_matches_cpu_reference(self) -> None:
        case = self._case()
        self.assertEqual(
            rt.run_apple_rt(overlay_kernel, native_only=True, **case),
            rt.run_cpu_python_reference(overlay_kernel, **case),
        )

    def test_direct_helper_matches_cpu(self) -> None:
        case = self._case()
        self.assertEqual(
            rt.overlay_compose_apple_rt(case["left"], case["right"]),
            rt.overlay_compose_cpu(case["left"], case["right"]),
        )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

import rtdsl as rt
from rtdsl.hiprt_runtime import hiprt_context_probe
from rtdsl.hiprt_runtime import overlay_compose_hiprt


@rt.kernel(backend="rtdl", precision="float_approx")
def overlay_kernel():
    left = rt.input("left", rt.Polygons, role="probe")
    right = rt.input("right", rt.Polygons, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.overlay_compose())
    return rt.emit(hits, fields=["left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"])


def hiprt_available() -> bool:
    try:
        hiprt_context_probe()
        return True
    except Exception:
        return False


def square(poly_id: int, x0: float, y0: float, size: float) -> rt.Polygon:
    return rt.Polygon(
        id=poly_id,
        vertices=((x0, y0), (x0 + size, y0), (x0 + size, y0 + size), (x0, y0 + size)),
    )


@unittest.skipUnless(hiprt_available(), "HIPRT runtime is not available")
class Goal556HiprtOverlayTest(unittest.TestCase):
    def _case(self):
        return {
            "left": (
                square(1, 0.0, 0.0, 2.0),
                square(2, 5.0, 5.0, 1.0),
            ),
            "right": (
                square(10, 1.0, -1.0, 2.0),
                square(20, 0.25, 0.25, 0.5),
                square(30, 8.0, 8.0, 1.0),
            ),
        }

    def test_direct_helper_matches_cpu_reference(self) -> None:
        case = self._case()
        self.assertEqual(
            overlay_compose_hiprt(case["left"], case["right"]),
            rt.run_cpu_python_reference(overlay_kernel, **case),
        )

    def test_run_hiprt_matches_cpu_reference(self) -> None:
        case = self._case()
        self.assertEqual(
            rt.run_hiprt(overlay_kernel, **case),
            rt.run_cpu_python_reference(overlay_kernel, **case),
        )

    def test_empty_inputs_return_empty_rows(self) -> None:
        case = self._case()
        self.assertEqual(rt.run_hiprt(overlay_kernel, left=(), right=case["right"]), ())
        self.assertEqual(rt.run_hiprt(overlay_kernel, left=case["left"], right=()), ())


if __name__ == "__main__":
    unittest.main()

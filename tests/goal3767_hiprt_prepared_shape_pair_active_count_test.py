import pathlib
import unittest

import rtdsl as rt
from rtdsl import hiprt_runtime


ROOT = pathlib.Path(__file__).resolve().parents[1]
HIPRT_CORE = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_core.cpp"
HIPRT_API = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_api.cpp"


def _native_prepared_shape_pair_available() -> bool:
    try:
        rt.hiprt_context_probe()
        lib = hiprt_runtime._hiprt_lib()
    except Exception:
        return False
    return (
        getattr(lib, "rtdl_hiprt_prepare_shape_pair_relation_active_count", None) is not None
        and getattr(lib, "rtdl_hiprt_count_prepared_shape_pair_relation_active", None) is not None
        and getattr(lib, "rtdl_hiprt_destroy_prepared_shape_pair_relation_active_count", None) is not None
    )


def _box(polygon_id: int, x0: float, y0: float, x1: float, y1: float):
    return rt.Polygon(id=polygon_id, vertices=((x0, y0), (x1, y0), (x1, y1), (x0, y1)))


class Goal3767HiprtPreparedShapePairActiveCountPortableTest(unittest.TestCase):
    def test_new_symbols_are_generic_prepared_shape_pair_active_count(self) -> None:
        api = HIPRT_API.read_text(encoding="utf-8")
        core = HIPRT_CORE.read_text(encoding="utf-8")
        self.assertIn("rtdl_hiprt_prepare_shape_pair_relation_active_count", api)
        self.assertIn("rtdl_hiprt_count_prepared_shape_pair_relation_active", api)
        self.assertIn("rtdl_hiprt_destroy_prepared_shape_pair_relation_active_count", api)
        self.assertIn("RtdlShapePairActiveCount2DKernel", core)
        self.assertIn("PreparedShapePairActiveCount2D", core)
        self.assertNotIn("rayjoin", api.lower())
        self.assertNotIn("rayjoin", core.lower())

    def test_python_exports_prepared_shape_pair_active_count_handle(self) -> None:
        self.assertIn("prepare_hiprt_shape_pair_active_count_2d", rt.__all__)
        self.assertIn("PreparedHiprtShapePairActiveCount2D", rt.__all__)

    def test_empty_prepared_right_is_portable_without_native_symbols(self) -> None:
        with rt.prepare_hiprt_shape_pair_active_count_2d(()) as prepared:
            self.assertEqual(prepared.count((_box(1, 0.0, 0.0, 1.0, 1.0),)), 0)


@unittest.skipUnless(_native_prepared_shape_pair_available(), "HIPRT prepared shape-pair active-count symbols unavailable")
class Goal3767HiprtPreparedShapePairActiveCountNativeTest(unittest.TestCase):
    def test_prepared_active_count_matches_relation_flags(self) -> None:
        left = (
            _box(1, 0.0, 0.0, 2.0, 2.0),
            _box(2, 10.0, 10.0, 12.0, 12.0),
        )
        right = (
            _box(10, 1.0, 1.0, 3.0, 3.0),
            _box(11, 0.25, 0.25, 0.75, 0.75),
            _box(12, 20.0, 20.0, 21.0, 21.0),
        )
        rows = hiprt_runtime.overlay_compose_hiprt(left, right)
        expected = sum(1 for row in rows if row["requires_lsi"] or row["requires_pip"])
        with rt.prepare_hiprt_shape_pair_active_count_2d(right) as prepared:
            self.assertEqual(prepared.count(left), expected)
            self.assertEqual(prepared.count(()), 0)


if __name__ == "__main__":
    unittest.main()

import pathlib
import unittest
import json

import rtdsl as rt
from rtdsl import hiprt_runtime


ROOT = pathlib.Path(__file__).resolve().parents[1]
HIPRT_CORE = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_core.cpp"
HIPRT_API = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_api.cpp"
REPORT = ROOT / "docs" / "reports" / "goal3766_hiprt_prepared_segment_pair_exact_count_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3766_hiprt_prepared_segment_pair_exact_count_a5000.json"


def _native_prepared_segment_pair_available() -> bool:
    try:
        rt.hiprt_context_probe()
        lib = hiprt_runtime._hiprt_lib()
    except Exception:
        return False
    return (
        getattr(lib, "rtdl_hiprt_prepare_segment_pair_intersection", None) is not None
        and getattr(lib, "rtdl_hiprt_count_prepared_segment_pair_intersection", None) is not None
        and getattr(lib, "rtdl_hiprt_destroy_prepared_segment_pair_intersection", None) is not None
    )


class Goal3766HiprtPreparedSegmentPairCountPortableTest(unittest.TestCase):
    def test_new_symbols_are_generic_prepared_segment_pair_count(self) -> None:
        api = HIPRT_API.read_text(encoding="utf-8")
        core = HIPRT_CORE.read_text(encoding="utf-8")
        self.assertIn("rtdl_hiprt_prepare_segment_pair_intersection", api)
        self.assertIn("rtdl_hiprt_count_prepared_segment_pair_intersection", api)
        self.assertIn("rtdl_hiprt_destroy_prepared_segment_pair_intersection", api)
        self.assertIn("RtdlSegmentPairIntersectionCount2DKernel", core)
        self.assertIn("PreparedSegmentPairIntersection2D", core)
        self.assertNotIn("rayjoin", api.lower())
        self.assertNotIn("rayjoin", core.lower())

    def test_python_exports_prepared_segment_pair_count_handle(self) -> None:
        self.assertIn("prepare_hiprt_segment_pair_intersection_2d", rt.__all__)
        self.assertIn("PreparedHiprtSegmentPairIntersection2D", rt.__all__)

    def test_empty_prepared_right_is_portable_without_native_symbols(self) -> None:
        with rt.prepare_hiprt_segment_pair_intersection_2d(()) as prepared:
            left = (rt.Segment(1, 0.0, 0.0, 1.0, 1.0),)
            self.assertEqual(prepared.count(left), 0)

    def test_report_and_artifact_record_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3766", report)
        self.assertIn("not AMD hardware", report)
        self.assertIn("evidence and does not authorize", report)
        self.assertIn("prepared_shape_pair_active_count", report)
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["source_commit"], "6968b19c")
        self.assertFalse(artifact["scoped_source_dirty"])
        self.assertTrue(artifact["sample_matches_row_path"])
        for key, value in artifact["claim_boundary"].items():
            self.assertFalse(value, key)


@unittest.skipUnless(_native_prepared_segment_pair_available(), "HIPRT prepared segment-pair count symbols unavailable")
class Goal3766HiprtPreparedSegmentPairCountNativeTest(unittest.TestCase):
    def test_prepared_count_matches_row_path(self) -> None:
        left = (
            rt.Segment(10, 0.0, 0.0, 2.0, 0.0),
            rt.Segment(11, 0.0, 0.5, 2.0, 0.5),
            rt.Segment(12, 0.0, 2.0, 2.0, 2.0),
        )
        right = (
            rt.Segment(20, 1.0, -1.0, 1.0, 1.0),
            rt.Segment(21, 1.5, -1.0, 1.5, 0.25),
            rt.Segment(22, 3.0, 3.0, 4.0, 4.0),
        )
        row_count = len(hiprt_runtime.segment_intersection_hiprt(left, right))
        with rt.prepare_hiprt_segment_pair_intersection_2d(right) as prepared:
            self.assertEqual(prepared.count(left), row_count)
            self.assertEqual(prepared.count(()), 0)


if __name__ == "__main__":
    unittest.main()

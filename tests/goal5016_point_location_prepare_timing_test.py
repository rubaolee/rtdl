import unittest
import ctypes
from pathlib import Path

import rtdsl.optix_runtime as optix


ROOT = Path(__file__).resolve().parents[1]


class _FakeTimingSymbol:
    def __init__(self, values):
        self.values = values
        self.argtypes = None
        self.restype = None

    def __call__(self, *args):
        for arg, value in zip(args, self.values):
            arg._obj.value = value
        return 0


class Goal5016PointLocationPrepareTimingTest(unittest.TestCase):
    def test_native_exports_prepare_extended_timing_api(self):
        source = (ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp").read_text(
            encoding="utf-8"
        )
        self.assertIn("rtdl_optix_rayjoin_cdb_point_location_get_last_extended_phase_timings", source)
        self.assertIn("rtdl_optix_directed_segment_point_location_get_last_extended_phase_timings", source)
        self.assertIn("g_optix_last_rayjoin_cdb_prepare_range_build_s", source)
        self.assertIn("g_optix_last_rayjoin_cdb_prepare_accel_build_s", source)
        self.assertIn("reset_rayjoin_cdb_point_location_prepare_timings", source)

    def test_prelude_declares_prepare_extended_timing_api(self):
        source = (ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h").read_text(
            encoding="utf-8"
        )
        self.assertIn("rtdl_optix_rayjoin_cdb_point_location_get_last_extended_phase_timings", source)
        self.assertIn("rtdl_optix_directed_segment_point_location_get_last_extended_phase_timings", source)
        self.assertIn("prepare_duplicate_canonicalize_out", source)

    def test_python_timing_bridge_returns_prepare_extended_breakdown(self):
        class FakeLib:
            pass

        lib = FakeLib()
        setattr(
            lib,
            optix.OPTIX_DIRECTED_SEGMENT_POINT_LOCATION_TIMINGS_SYMBOL,
            _FakeTimingSymbol([0.1, 0.2, 0.3, 11, 7, 7]),
        )
        setattr(
            lib,
            optix.OPTIX_DIRECTED_SEGMENT_POINT_LOCATION_EXTENDED_TIMINGS_SYMBOL,
            _FakeTimingSymbol([1.0, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 123, 45, 7]),
        )

        timings = optix._get_last_rayjoin_cdb_point_location_phase_timings_from_library(lib)

        self.assertEqual("prepare", timings["mode"])
        self.assertEqual(11, timings["point_count"])
        extended = timings["extended"]
        self.assertEqual("rtdl.optix.directed_segment_point_location.extended_phase_timings.v1", extended["schema"])
        self.assertEqual("prepare", extended["mode"])
        self.assertEqual(1.0, extended["prepare_total"])
        self.assertEqual(0.14, extended["prepare_duplicate_canonicalize"])
        self.assertEqual(0.16, extended["prepare_range_build"])
        self.assertEqual(0.18, extended["prepare_accel_build"])
        self.assertEqual(123, extended["prepare_segment_count"])
        self.assertEqual(45, extended["prepare_range_count"])

    def test_prepared_handle_uses_own_prepare_extended_timing(self):
        class FakeLib:
            pass

        lib = FakeLib()
        setattr(
            lib,
            optix.OPTIX_DIRECTED_SEGMENT_POINT_LOCATION_TIMINGS_SYMBOL,
            _FakeTimingSymbol([0.2, 0.3, 0.4, 22, 8, 5]),
        )
        setattr(
            lib,
            optix.OPTIX_DIRECTED_SEGMENT_POINT_LOCATION_EXTENDED_TIMINGS_SYMBOL,
            _FakeTimingSymbol([9.0, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 999, 888, 5]),
        )
        own_prepare = {
            "extended": {
                "schema": "rtdl.optix.directed_segment_point_location.extended_phase_timings.v1",
                "mode": "prepare",
                "prepare_total": 1.25,
                "prepare_segment_count": 123,
                "prepare_range_count": 45,
            }
        }
        prepared = optix.PreparedOptixRayjoinCdbPointLocation2D(
            library=lib,
            prepared_handle=ctypes.c_void_p(1),
            segment_count=123,
            prepare_phase_timings=own_prepare,
        )

        timings = prepared.last_phase_timings()

        self.assertEqual("face_ids_device_points", timings["mode"])
        self.assertEqual(22, timings["point_count"])
        self.assertEqual(1.25, timings["extended"]["prepare_total"])
        self.assertEqual(123, timings["extended"]["prepare_segment_count"])
        self.assertEqual(45, timings["extended"]["prepare_range_count"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"


class Goal3251ClosedShapeDeviceFilteredCountTest(unittest.TestCase):
    def test_native_device_filtered_count_is_separate_from_exact_count(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")

        exact_start = text.index("static void count_prepared_point_closed_shape_membership_2d_optix")
        device_start = text.index(
            "static void count_prepared_point_closed_shape_membership_device_filtered_2d_optix"
        )
        exact_body = text[exact_start:device_start]
        device_body = text[device_start:text.index("struct ShapePairRelationFlagComputation", device_start)]

        self.assertIn("count_exact_hits", exact_body)
        self.assertIn("exact_point_in_polygon", exact_body)
        self.assertIn("download(chunk_rows.data()", exact_body)

        self.assertIn("reset_closed_shape_membership_phase_timings(3u)", device_body)
        self.assertIn("lp.device_prefilter = 1u", device_body)
        self.assertIn("lp.output         = nullptr", device_body)
        self.assertIn("lp.output_capacity = 0u", device_body)
        self.assertIn("g_optix_last_closed_shape_candidate_count_s", device_body)
        self.assertIn("*count_out = total_count", device_body)
        self.assertNotIn("exact_point_in_polygon", device_body)
        self.assertNotIn("download(chunk_rows.data()", device_body)

    def test_c_abi_and_python_wrapper_are_generic(self) -> None:
        symbol = "rtdl_optix_count_prepared_point_closed_shape_membership_device_filtered_2d"

        self.assertIn(symbol, API.read_text(encoding="utf-8"))
        self.assertIn(symbol, PRELUDE.read_text(encoding="utf-8"))

        runtime = RUNTIME.read_text(encoding="utf-8")
        self.assertIn(symbol, runtime)
        self.assertIn("def count_device_filtered(self, points) -> int:", runtime)
        self.assertIn("``count`` remains the exact host-refined authority", runtime)
        self.assertIn('"device_filtered_count"', runtime)

        start = runtime.index("def count_device_filtered(self, points) -> int:")
        end = runtime.index("def last_phase_timings", start)
        body = runtime[start:end].lower()
        for forbidden in ("rayjoin", "county", "soil", "pip"):
            self.assertNotIn(forbidden, body)


if __name__ == "__main__":
    unittest.main()

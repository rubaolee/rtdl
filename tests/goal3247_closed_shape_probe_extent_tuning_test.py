from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal3247ClosedShapeProbeExtentTuningTest(unittest.TestCase):
    def test_default_closed_shape_probe_extent_remains_unchanged(self) -> None:
        core = CORE.read_text(encoding="utf-8")

        self.assertIn("const float query_half_extent = 0.5f", core)
        self.assertIn("Bounded vertical probe through the point", core)
        self.assertIn("2.0f * query_half_extent", core)

    def test_optix_pipeline_accepts_explicit_probe_extent_override(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        start = workloads.index("static void ensure_pip_pipeline()")
        end = workloads.index("static void run_pip_optix(", start)
        body = workloads[start:end]

        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_QUERY_HALF_EXTENT", body)
        self.assertIn("std::strtod(raw_extent, &end)", body)
        self.assertIn("!std::isfinite(extent) || extent <= 0.0", body)
        self.assertIn("const float query_half_extent = %.9gf;", body)
        self.assertIn("const float query_half_extent = 0.5f;", body)
        self.assertIn("src.replace(pos, needle.size(), replacement)", body)
        self.assertIn("compile_to_ptx(src.c_str(), \"pip_kernel.cu\")", body)

    def test_override_is_generic_and_not_rayjoin_specific(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        start = workloads.index("static void ensure_pip_pipeline()")
        end = workloads.index("static void run_pip_optix(", start)
        body = workloads[start:end].lower()

        for forbidden in ("rayjoin", "pip count", "county", "soil", "brazil"):
            self.assertNotIn(forbidden, body)


if __name__ == "__main__":
    unittest.main()

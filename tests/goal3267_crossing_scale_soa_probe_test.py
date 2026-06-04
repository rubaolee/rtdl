from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal3267CrossingScaleSoAProbeTest(unittest.TestCase):
    def test_kernel_uses_optional_split_crossing_scale_without_changing_default(self) -> None:
        text = CORE.read_text(encoding="utf-8")

        self.assertIn("const float* edge_crossing_scale;", text)
        self.assertIn("const uint32_t edge_crossing_scale_enabled = 0u;", text)
        self.assertIn("edge_crossing_scale_enabled != 0u && params.edge_crossing_scale != nullptr", text)
        self.assertIn("params.edge_crossing_scale[off + i]", text)
        self.assertIn("(ax - bx) / ((ay - by) != 0.0f ? (ay - by) : 1.0e-20f)", text)

    def test_host_prepares_one_float_per_edge_and_gates_it_off_by_default(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_USE_CROSSING_SCALE_LAYOUT", text)
        self.assertIn("use_prepared_closed_shape_crossing_scale_layout", text)
        self.assertIn("edge_crossing_scale_enabled = 1u", text)
        self.assertIn("failed to specialize closed-shape membership crossing-scale layout", text)
        self.assertIn("std::vector<float> right_edge_crossing_scale;", text)
        self.assertIn("DevPtr d_right_edge_crossing_scale;", text)
        self.assertIn("right_edge_crossing_scale[off + i] = crossing_scale;", text)
        self.assertIn("upload(d_right_edge_crossing_scale.ptr", text)
        self.assertIn("lp.edge_crossing_scale = nullptr;", text)
        self.assertEqual(
            text.count("lp.edge_crossing_scale = use_prepared_closed_shape_crossing_scale_layout()"),
            3,
        )


if __name__ == "__main__":
    unittest.main()

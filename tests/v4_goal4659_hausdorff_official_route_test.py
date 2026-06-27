from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

SUMMARY = ROOT / "future" / "v4" / "evidence" / "v4_goal4659_hausdorff_v4_route_20260625" / "summary.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4659_hausdorff_official_v4_route_evidence_2026-06-25.md"
APP = ROOT / "examples" / "current" / "research_benchmarks" / "hausdorff_xhd" / "rtdl_hausdorff_distance_app.py"
PARTNER_ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"


class V4Goal4659HausdorffOfficialRouteTest(unittest.TestCase):
    def test_hausdorff_route_uses_official_v4_point_group_surface(self) -> None:
        text = APP.read_text(encoding="utf-8")

        self.assertIn("import rtdsl.v4_point_group as pg_v4", text)
        self.assertIn("prepare_point_group_nearest_witness_2d_device_arrays_v4", text)
        self.assertIn('partner == "torch"', text)
        self.assertIn('partner="torch"', text)
        self.assertIn("coordinate_normalization_span", text)
        self.assertIn("_run_optix_device_max_nearest_directed_chunked_normalized", text)
        self.assertNotIn("hausdorff_native_kernel", text)

    def test_generic_torch_global_argmax_is_not_app_specific(self) -> None:
        text = PARTNER_ADAPTERS.read_text(encoding="utf-8")
        start = text.index("def global_argmax_u32_f64_partner_columns")
        section = text[start : text.index("from .numba_partner_continuation", start)]

        self.assertIn('if partner == "torch":', section)
        self.assertIn("torch_masked_reduce", section)
        self.assertIn("generic_global_argmax_u32_f64", section)
        self.assertNotIn("hausdorff", section.lower())

    def test_evidence_keeps_hot_win_and_correctness_boundary_separate(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        ratios = payload["ratios"]
        boundary = payload["correctness_boundary"]

        self.assertEqual(
            "goal4659_hausdorff_v4_official_route_correctness_repair_measured_not_release",
            payload["status"],
        )
        self.assertGreater(
            ratios["points262144_v4_hot_vs_v3_0_2_cupy_old_over_v4"],
            1.20,
        )
        self.assertEqual("pass", boundary["points_per_side_262144"])
        self.assertIn("fail", boundary["points_per_side_1048576_unnormalized"])
        self.assertTrue(
            boundary["points_per_side_1048576_v4_coordinate_normalized"].startswith("pass_with_span_1000000")
        )
        self.assertEqual(1000000.0, payload["coordinate_normalization_span_sweep"]["primary_passing_span"])
        self.assertIn("correctness_repair_not_speed_claim", " ".join(ratios.keys()))
        self.assertFalse(payload["claim_boundary"]["release_authorized"])
        self.assertFalse(payload["claim_boundary"]["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["v4_coordinate_normalization_speed_claim_authorized"])

    def test_report_forbids_unrestricted_exact_hausdorff_claim(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("1,048,576 points/side", text)
        self.assertIn("coordinate-normalized V4 passes correctness", text)
        self.assertIn("correctness repair, not a speed claim", text)
        self.assertIn("float32_computed_float64_output", text)
        self.assertIn("Do not promote this as a broad app-level V4 speed claim", text)


if __name__ == "__main__":
    unittest.main()

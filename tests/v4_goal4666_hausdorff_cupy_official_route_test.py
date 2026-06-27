from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


V4_POINT_GROUP = ROOT / "src" / "rtdsl" / "v4_point_group.py"
PARTNER_ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
HAUSDORFF_APP = (
    ROOT
    / "examples"
    / "current"
    / "research_benchmarks"
    / "hausdorff_xhd"
    / "rtdl_hausdorff_distance_app.py"
)
SUMMARY = ROOT / "future" / "v4" / "evidence" / "v4_goal4666_hausdorff_cupy_official_20260625" / "summary.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4666_hausdorff_cupy_official_route_evidence_2026-06-25.md"


class V4Goal4666HausdorffCupyOfficialRouteTest(unittest.TestCase):
    def test_cupy_remains_claim_bounded_until_pod_measured(self) -> None:
        from rtdsl import v4_point_group as pg_v4

        boundary = pg_v4.point_group_nearest_witness_2d_device_array_claim_boundary_v4(
            partner="cupy"
        )

        self.assertEqual("cupy", boundary["partner"])
        self.assertFalse(boundary["measured_partner"])
        self.assertEqual(
            "declared_unmeasured_not_performance_ready",
            boundary["partner_claim_status"],
        )
        self.assertFalse(boundary["release_claim_authorized"])
        self.assertFalse(boundary["broad_v4_speedup_claim_authorized"])
        self.assertFalse(boundary["whole_app_speedup_claim_authorized"])
        self.assertFalse(boundary["true_zero_copy_authorized"])

    def test_v4_point_group_no_longer_rejects_cupy_front_door(self) -> None:
        text = V4_POINT_GROUP.read_text(encoding="utf-8")

        self.assertNotIn("CuPy output allocation is declared but unmeasured", text)
        self.assertNotIn("CuPy is declared but unmeasured for this V4 candidate", text)
        self.assertIn("import cupy", text)
        self.assertIn('"query_ids": cupy.empty', text)
        self.assertIn("partner = _require_partner(partner)", text)

    def test_generic_global_argmax_supports_cupy(self) -> None:
        text = PARTNER_ADAPTERS.read_text(encoding="utf-8")

        self.assertIn('if partner == "cupy":', text)
        self.assertIn('partner="cupy"', text)
        self.assertIn('reduction_strategy = "cupy_rawkernel_single_block_reduce"', text)
        self.assertIn('reduction_strategy = "cupy_rawkernel_multiblock_reduce"', text)
        self.assertIn('"rawkernel_row_threshold": rawkernel_row_threshold', text)
        self.assertIn("rtdl_cupy_global_argmax_u32_f64", text)
        self.assertIn("rtdl_cupy_global_argmax_u32_f64_blocks", text)
        self.assertIn("rtdl_cupy_global_argmax_u32_f64_final", text)
        self.assertIn("global_argmax_u32_f64 currently supports partner='numba', partner='torch', or partner='cupy'", text)
        self.assertIn('"host_row_materialization_used": False', text)
        self.assertIn("synchronize: bool = True", text)
        self.assertIn('"partner_synchronized_before_return": bool(synchronize)', text)

    def test_hausdorff_cupy_uses_official_v4_session_not_app_local_reducer(self) -> None:
        text = HAUSDORFF_APP.read_text(encoding="utf-8")

        self.assertNotIn("_cupy_global_argmax_u32_f64_with_neighbor", text)
        self.assertNotIn("hausdorff_app_cupy_global_argmax_u32_f64", text)
        self.assertIn('if partner in {"torch", "cupy"}:', text)
        self.assertIn("pg_v4.prepare_point_group_nearest_witness_2d_device_arrays_v4", text)
        self.assertIn("partner=partner", text)
        self.assertIn('partner="cupy"', text)
        self.assertIn("rt.global_argmax_u32_f64_partner_columns", text)
        self.assertIn("synchronize=False", text)
        self.assertIn('neighbor_ids[row_index : row_index + 1]', text)

    def test_goal4666_summary_records_mixed_result_not_release_evidence(self) -> None:
        import json

        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual(
            "goal4666_hausdorff_cupy_official_route_complete_no_release_authorization",
            summary["status"],
        )
        self.assertEqual(
            "official_cupy_route_productized__large_row_passes_hot_prepare__focused_bar_not_reopened",
            summary["decision"]["label"],
        )
        self.assertFalse(summary["decision"]["may_count_as_formal_high_performance_v4_evidence"])
        self.assertFalse(summary["decision"]["may_trigger_full_all_app_rerun"])
        self.assertFalse(summary["claim_boundary"]["release_authorized"])
        self.assertFalse(summary["claim_boundary"]["formal_high_performance_v4_authorized"])
        self.assertFalse(summary["claim_boundary"]["whole_app_speedup_claim_authorized"])

        rows = {row["points_per_side"]: row for row in summary["rows"]}
        self.assertFalse(rows[65536]["passes_v4_vs_v3_hot_bar_1_20x"])
        self.assertFalse(rows[65536]["passes_prepare_floor_0_80x"])
        self.assertTrue(rows[262144]["passes_v4_vs_v3_hot_bar_1_20x"])
        self.assertTrue(rows[262144]["passes_prepare_floor_0_80x"])
        self.assertEqual(
            "global_argmax_u32_f64_partner_columns",
            rows[262144]["v4_official_cupy"]["consumer_adapter"],
        )
        self.assertIn(
            rows[262144]["v4_official_cupy"]["consumer_reduction_strategy"],
            {
                "cupy_masked_reduce",
                "cupy_rawkernel_single_block_reduce",
                "cupy_masked_reduce_single_sync",
                "cupy_rawkernel_multiblock_reduce",
            },
        )

    def test_goal4666_report_forbids_all_app_and_release_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("does not authorize formal", text)
        self.assertIn("Do not rerun all-app", text)
        self.assertIn("not as formal V4 high-performance evidence", text)
        self.assertIn("app-local CuPy reducer has been removed", text)


if __name__ == "__main__":
    unittest.main()

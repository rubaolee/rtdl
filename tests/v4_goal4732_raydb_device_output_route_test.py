from __future__ import annotations

import unittest
from pathlib import Path
import json
import inspect

import numpy as np

from examples.current.research_benchmarks.raydb_style import (
    rtdl_raydb_style_benchmark_app as raydb,
)


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "future" / "v4" / "evidence" / "v4_goal4732_raydb_device_output_route_repair_2026-06-26.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4732_raydb_device_output_route_repair_2026-06-26.md"
CALL_FOR_REVIEW = (
    ROOT / "future" / "v4" / "reviews" / "call_for_review_v4_goal4732_raydb_device_output_route_repair_2026-06-26.md"
)
REVIEW_DEBT = (
    ROOT / "future" / "v4" / "reviews" / "v4_goal4732_raydb_device_output_route_repair_review_debt_2026-06-26.md"
)
FOCUSED_POD = ROOT / "future" / "v4" / "evidence" / "v4_goal4732_raydb_focused_20260626" / "summary.json"


class V4Goal4732RaydbDeviceOutputRouteTest(unittest.TestCase):
    def test_v4_backend_is_registered_without_replacing_v2_baseline(self) -> None:
        self.assertIn(raydb.PAPER_RT_OPTIX_PREPARED_GROUPED_REDUCTION_BACKEND, raydb.BACKENDS)
        self.assertIn(raydb.PAPER_RT_V4_TORCH_DEVICE_GROUPED_REDUCTION_BACKEND, raydb.BACKENDS)
        self.assertIn(raydb.PAPER_RT_V4_CUPY_DEVICE_GROUPED_REDUCTION_BACKEND, raydb.BACKENDS)
        self.assertNotEqual(
            raydb.PAPER_RT_OPTIX_PREPARED_GROUPED_REDUCTION_BACKEND,
            raydb.PAPER_RT_V4_TORCH_DEVICE_GROUPED_REDUCTION_BACKEND,
        )

    def test_device_output_rows_match_generic_grouped_row_shape(self) -> None:
        rows = raydb._paper_rows_from_v4_grouped_output_columns(
            {
                "group_counts": np.asarray([2, 0, 3], dtype=np.uint64),
                "group_sums": np.asarray([10, 0, 21], dtype=np.uint64),
                "group_mins": np.asarray([4, np.iinfo(np.uint64).max, 5], dtype=np.uint64),
                "group_maxs": np.asarray([6, 0, 9], dtype=np.uint64),
            },
            reduction="sum_count",
            group_keys=("region_id",),
            group_tuples=((100,), (101,), (102,)),
        )

        self.assertEqual(
            [
                {"region_id": 100, "sum": 10, "count": 2},
                {"region_id": 102, "sum": 21, "count": 3},
            ],
            rows,
        )

    def test_v4_backend_rejects_unsupported_reduction_before_cuda(self) -> None:
        fixture = raydb.make_benchmark_fixture(
            fixture_kind="generated",
            generated_rows=8,
            generated_groups=2,
        )
        plan = raydb.make_plan("sum")
        with self.assertRaisesRegex(ValueError, "unsupported paper RT result mode"):
            raydb._run_paper_rt_v4_torch_device_grouped_reduction_result_mode(
                fixture=fixture,
                plan=plan,
                mode="stats",
                copies=1,
                repeat=1,
                warmup=0,
            )

    def test_summary_only_v4_route_keeps_row_materialization_out_of_hot_path(self) -> None:
        source = inspect.getsource(raydb._run_paper_rt_v4_torch_device_grouped_reduction_result_mode)
        self.assertIn("if summary_only_iterations:", source)
        self.assertIn("rows_done = device_done", source)
        self.assertIn("result_materialization_after_hot_path_sec", source)
        self.assertIn('"group_rows_downloaded_to_host_in_hot_path": not bool(summary_only_iterations)', source)
        self.assertIn('"host_materialization_in_hot_path": not bool(summary_only_iterations)', source)

    def test_goal4732_files_record_debt_and_non_authorization(self) -> None:
        for path in (EVIDENCE, REPORT, CALL_FOR_REVIEW, REVIEW_DEBT):
            self.assertTrue(path.exists(), path)
            text = path.read_text(encoding="utf-8")
            self.assertIn("Goal4732", text)
            self.assertIn("no", text.lower())
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("paper_rt_v4_torch_device_grouped_reduction", report)
        self.assertIn("paper_rt_v4_cupy_device_grouped_reduction", report)
        self.assertIn("v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays", report)
        self.assertIn("POD", report)
        self.assertIn("rerun", report)

    def test_focused_pod_rerun_is_route_repair_not_speed_win(self) -> None:
        self.assertTrue(FOCUSED_POD.exists(), FOCUSED_POD)
        payload = json.loads(FOCUSED_POD.read_text(encoding="utf-8"))
        analysis = payload["analysis"]
        self.assertTrue(analysis["v4_route_metadata_pass"])
        self.assertGreaterEqual(analysis["v4_vs_v2_14_hot"], 0.98)
        self.assertLess(analysis["v4_vs_v2_14_hot"], 1.20)
        self.assertLess(analysis["v4_vs_v3_0_2_hot"], 0.98)
        self.assertFalse(analysis["release_claim_authorized"])
        v4 = payload["rows"]["v4_current"]
        self.assertEqual("paper_rt_v4_cupy_device_grouped_reduction", v4["backend"])
        self.assertEqual(
            "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
            v4["adapter"],
        )
        self.assertEqual("cupy", v4["adapter_partner"])
        self.assertTrue(v4["native_direct_device_output_columns"])
        self.assertTrue(v4["host_row_bridge_bypassed"])
        self.assertFalse(v4["group_rows_downloaded_to_host_in_hot_path"])


if __name__ == "__main__":
    unittest.main()

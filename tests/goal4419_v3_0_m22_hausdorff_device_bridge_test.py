from __future__ import annotations

from pathlib import Path
import json
import unittest

from examples import rtdl_hausdorff_distance_app as app


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_distance_app.py"
RUNNER = ROOT / "scripts/v3_0_m22_hausdorff_device_bridge_measure.py"
REPORT = ROOT / "docs/reports/goal4419_v3_0_m22_hausdorff_device_bridge_2026-06-15.md"
EVIDENCE_JSON = ROOT / "docs/reports/goal4419_v3_0_m22_hausdorff_device_bridge_65536_2026-06-15.json"


class Goal4419V30M22HausdorffDeviceBridgeTest(unittest.TestCase):
    def test_app_exposes_optix_device_max_nearest_without_native_app_specialization(self) -> None:
        source = APP.read_text(encoding="utf-8")
        self.assertIn('"optix_device_max_nearest"', source)
        self.assertIn("prepare_optix_point_group_nearest_witness_2d", source)
        self.assertIn("write_device_nearest_witness_columns_from_device_query_columns", source)
        self.assertIn("global_argmax_u32_f64_partner_columns", source)
        self.assertIn("validate_non_empty_on_host=False", source)
        self.assertIn("generic_point_group_nearest_witness_2d_device_columns", source)
        self.assertIn("generic_global_argmax_u32_f64", source)
        self.assertIn('"app_specific_native_engine_logic_allowed": False', source)

    def test_require_rt_core_accepts_device_bridge_and_still_rejects_row_mode(self) -> None:
        app._enforce_rt_core_requirement("optix_device_max_nearest", "rows", True)
        with self.assertRaisesRegex(RuntimeError, "directed_threshold_prepared"):
            app._enforce_rt_core_requirement("optix", "rows", True)

    def test_runner_records_both_required_partners_and_numba_toolchain(self) -> None:
        runner = RUNNER.read_text(encoding="utf-8")
        self.assertIn('for partner in ("cupy", "numba")', runner)
        self.assertIn('"optix_device_max_nearest"', runner)
        self.assertIn("--numba-cuda-home", runner)
        self.assertIn("runner_numba_cuda_home", runner)

    def test_report_and_pod_artifact_capture_m22_boundaries_if_present(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Hausdorff app device bridge", report)
        self.assertIn("CuPy and Numba", report)
        self.assertIn("not a public speedup claim", report)
        self.assertIn("generic prepared point-group nearest-witness", report)
        if not EVIDENCE_JSON.exists():
            self.skipTest("M22 pod evidence JSON has not been generated on this checkout")
        payload = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
        self.assertTrue(payload["comparison"]["all_match_oracle"])
        self.assertTrue(payload["comparison"]["distance_match"])
        rows = {row["partner"]: row for row in payload["rows"]}
        self.assertEqual({"cupy", "numba"}, set(rows))
        for row in rows.values():
            self.assertEqual(row["backend"], "optix_device_max_nearest")
            self.assertTrue(row["rt_core_accelerated"])
            self.assertTrue(row["native_continuation_active"])
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])
            self.assertFalse(row["claim_boundary"]["app_specific_native_engine_logic_allowed"])
            for direction in ("directed_a_to_b", "directed_b_to_a"):
                directed = row[direction]
                self.assertTrue(directed["prepared_query_columns_used"])
                self.assertTrue(directed["device_output_columns_used"])
                self.assertTrue(directed["device_result_materialization_after_hot_window"])
                self.assertFalse(directed["host_query_upload_in_hot_window"])
                self.assertFalse(directed["host_row_materialization_before_consumer"])


if __name__ == "__main__":
    unittest.main()

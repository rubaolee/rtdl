from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
PROBE = ROOT / "scripts" / "goal3310_rayjoin_pip_batch_scalar_count_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3318_prepared_point_batch_executor_2026-06-04.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3318_rayjoin_pip_batch_executor_auto_stream_2026-06-04.json"
EXPECTED_COMMIT = "c037f510b89a2effd4eff32d025da1a3c053a0b1"


class Goal3318PreparedPointBatchExecutorSurfaceTest(unittest.TestCase):
    def test_native_executor_exports_are_generic(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        for symbol in (
            "rtdl_optix_prepare_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_executor_2d",
            "rtdl_optix_run_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_executor_2d",
            "rtdl_optix_destroy_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_executor_2d",
        ):
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, prelude)
                self.assertIn(symbol, api)
                self.assertNotIn("rayjoin", symbol.lower())

    def test_native_executor_reuses_streams_and_params(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        start = text.index("struct PreparedPointClosedShapeMembershipPreparedPointsBatchExecutor2D")
        end = text.index("struct PreparedPointClosedShapeMembershipPreparedPointsBatchGraph2D", start)
        body = text[start:end]
        self.assertIn("std::unique_ptr<DevPtr> d_counts", body)
        self.assertIn("std::unique_ptr<DevPtr> d_params", body)
        self.assertIn("std::vector<CUstream> streams", body)
        self.assertIn("upload(d_params->ptr, params.data(), request_count)", body)
        self.assertIn("cuStreamCreate", body)
        self.assertIn("request_index % executor->stream_count", body)
        self.assertIn("reset_closed_shape_membership_phase_timings(11u)", body)
        self.assertNotIn("cuStreamCreate", body[body.index("static void run_point_closed_shape"):])
        self.assertNotIn("upload_async(request_params", body[body.index("static void run_point_closed_shape"):])
        self.assertNotIn("rayjoin", body.lower())

    def test_python_runtime_exposes_context_managed_executor(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        self.assertIn("class PreparedOptixPointClosedShapeBatchCountExecutor2D", runtime)
        self.assertIn("def prepare_device_filtered_prepared_points_batch_executor", runtime)
        self.assertIn("stream_count_requested", runtime)
        self.assertIn("stream_count_effective", runtime)
        self.assertIn("prepared_points_device_filtered_batch_executor_run", runtime)
        self.assertIn("true_zero_copy_claim_authorized", runtime)
        self.assertIn("PreparedOptixPointClosedShapeBatchCountExecutor2D", init)

    def test_probe_can_measure_executor_path(self) -> None:
        probe = PROBE.read_text(encoding="utf-8")
        self.assertIn("--batch-executor", probe)
        self.assertIn('"batch_executor"', probe)
        self.assertIn("executor prepared", probe)
        self.assertIn("prepared.prepare_device_filtered_prepared_points_batch_executor", probe)

    def test_report_records_executor_boundary_and_result(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3318 - Reusable Prepared Point Batch Count Executor", text)
        self.assertIn("c037f510b89a2effd4eff32d025da1a3c053a0b1", text)
        self.assertIn("0.034875", text)
        self.assertIn("6.78x", text)
        self.assertIn("contains no RayJoin-specific native logic", text)
        self.assertIn("rtdl_beats_rayjoin_claim_authorized`: false", text)

    def test_executor_artifact_is_exact_and_claim_boundary_clean(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["rtdl_commit"], EXPECTED_COMMIT)
        self.assertEqual(data["batch_stream_count"], "auto")
        self.assertTrue(data["batch_executor"])
        self.assertEqual(data["exact_count"], 1430)
        self.assertEqual(data["gpu"], "NVIDIA RTX A5000, 580.126.09")
        expected_effective = {
            1: 1,
            4: 1,
            8: 4,
            16: 8,
            32: 8,
            64: 16,
        }
        rows = {row["request_count"]: row for row in data["batch_rows"]}
        self.assertEqual(set(rows), set(expected_effective))
        for request_count, effective_streams in expected_effective.items():
            row = rows[request_count]
            self.assertTrue(row["batch_executor"])
            self.assertEqual(row["batch_stream_count_effective"], effective_streams)
            self.assertEqual(row["count_first"], 1430)
            self.assertEqual(row["count_last"], 1430)
            self.assertEqual(row["native_modes"], ["prepared_points_device_filtered_batch_executor_run"])
        self.assertLess(rows[32]["per_request_ms_median"], 0.035)
        self.assertLess(rows[64]["per_request_ms_median"], 0.034)
        for authorized in data["claim_boundary"].values():
            self.assertIs(authorized, False)


if __name__ == "__main__":
    unittest.main()

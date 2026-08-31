from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
PROBE = ROOT / "scripts" / "goal3310_rayjoin_pip_batch_scalar_count_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3310_prepared_point_batch_scalar_count_2026-06-04.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3310_rayjoin_pip_batch_probe_2026-06-04.json"


class Goal3310PreparedPointBatchScalarCountTest(unittest.TestCase):
    def test_native_exports_generic_batch_count_symbol(self) -> None:
        symbol = (
            "rtdl_optix_count_prepared_point_closed_shape_membership_"
            "device_filtered_prepared_points_batch_2d"
        )
        self.assertIn(symbol, PRELUDE.read_text(encoding="utf-8"))
        self.assertIn(symbol, API.read_text(encoding="utf-8"))
        runtime = RUNTIME.read_text(encoding="utf-8")
        self.assertIn("OPTIX_CLOSED_SHAPE_MEMBERSHIP_DEVICE_FILTERED_PREPARED_POINTS_BATCH_COUNT_SYMBOL", runtime)
        self.assertIn(symbol, runtime)

    def test_native_batch_path_queues_launches_before_single_sync(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        start = text.index(
            "static void count_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_2d_optix"
        )
        end = text.index(
            "static void run_prepared_point_closed_shape_membership_candidate_device_columns_2d_optix",
            start,
        )
        body = text[start:end]
        self.assertIn("request_count", body)
        self.assertIn("DevPtr d_counts(sizeof(uint32_t) * request_count)", body)
        self.assertIn("DevPtr d_params(sizeof(PipLaunchParams) * request_count)", body)
        self.assertIn("cuMemsetD32Async", body)
        self.assertIn("upload_async(d_params.ptr, params.data(), request_count, stream)", body)
        self.assertIn("optixLaunch", body)
        self.assertIn("if (stream_count <= 1u)", body)
        self.assertIn("for (CUstream stream : streams)", body)
        self.assertNotIn("rayjoin", body.lower())

    def test_python_method_and_phase_label_are_exposed(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        self.assertIn("def count_device_filtered_prepared_points_batch", runtime)
        self.assertIn("request_count must be non-negative", runtime)
        self.assertIn("prepared_points_device_filtered_batch_count", runtime)
        self.assertIn("if mode_value == 9", runtime)

    def test_probe_script_is_progress_logged_and_claim_bounded(self) -> None:
        probe = PROBE.read_text(encoding="utf-8")
        self.assertIn("[goal3310] batch", probe)
        self.assertIn("request_counts", probe)
        self.assertIn("per_request_ms_median", probe)
        self.assertIn("repeated-query throughput evidence only", probe)
        self.assertIn('"rtdl_beats_rayjoin_claim_authorized": False', probe)
        self.assertIn('"true_zero_copy_claim_authorized": False', probe)

    def test_report_and_artifact_keep_throughput_boundary(self) -> None:
        import json

        report = REPORT.read_text(encoding="utf-8")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertIn("repeated-query throughput improves", report)
        self.assertIn("not a RayJoin-beating result", report)
        self.assertIn("one-shot RayJoin latency comparisons", report)
        self.assertFalse(any(artifact["claim_boundary"].values()))
        self.assertEqual(artifact["rtdl_commit"], "7181367f7a772d1fcff60f9378ea90824297ea63")
        self.assertEqual(artifact["exact_count"], 1430)
        rows = {row["request_count"]: row for row in artifact["batch_rows"]}
        self.assertIn(32, rows)
        self.assertLess(rows[32]["per_request_ms_median"], artifact["single_ms_median"])
        self.assertEqual(rows[32]["count_first"], 1430)
        self.assertEqual(rows[32]["native_modes"], ["prepared_points_device_filtered_batch_count"])


if __name__ == "__main__":
    unittest.main()

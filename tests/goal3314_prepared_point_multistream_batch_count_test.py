from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
PROBE = ROOT / "scripts" / "goal3310_rayjoin_pip_batch_scalar_count_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3314_multistream_batch_scalar_count_2026-06-04.md"
ARTIFACT_PREFIX = "goal3314_rayjoin_pip_batch_stream"
EXPECTED_COMMIT = "0cfc510d19c3026eef8cf409d29ecaa4eabe8d6b"


class Goal3314PreparedPointMultistreamBatchCountTest(unittest.TestCase):
    def test_native_batch_path_has_opt_in_stream_pool(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_BATCH_STREAM_COUNT", text)
        self.assertIn("prepared_closed_shape_batch_stream_count", text)
        self.assertIn('std::string(raw) == "auto"', text)
        self.assertIn("request_count >= 64u", text)
        self.assertIn("request_count >= 16u", text)
        self.assertIn("request_count >= 8u", text)

        start = text.index(
            "static void count_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_2d_optix"
        )
        end = text.index("struct PreparedPointClosedShapeMembershipPreparedPointsBatchGraph2D", start)
        body = text[start:end]
        self.assertIn("std::vector<CUstream> streams", body)
        self.assertIn("cuStreamCreate", body)
        self.assertIn("request_index % stream_count", body)
        self.assertIn("cuStreamSynchronize(stream)", body)
        self.assertIn("cuStreamDestroy(stream)", body)
        self.assertNotIn("rayjoin", body.lower())

    def test_probe_script_exposes_stream_count_without_changing_claim_boundary(self) -> None:
        probe = PROBE.read_text(encoding="utf-8")
        self.assertIn("--batch-stream-count", probe)
        self.assertIn("positive integer or auto", probe)
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_BATCH_STREAM_COUNT", probe)
        self.assertIn('"rtdl_beats_rayjoin_claim_authorized": False', probe)
        self.assertIn("repeated-query throughput evidence only", probe)

    def test_report_records_bounded_pod_evidence(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3314 - Multi-Stream Prepared Point Batch Scalar Count Evidence", text)
        self.assertIn("0cfc510d19c3026eef8cf409d29ecaa4eabe8d6b", text)
        self.assertIn("0.036487", text)
        self.assertIn("6.48x", text)
        self.assertIn("It does not prove a one-shot RayJoin speedup", text)
        self.assertIn("rtdl_beats_rayjoin_claim_authorized`: false", text)

    def test_pod_artifacts_are_exact_and_claim_boundary_clean(self) -> None:
        artifacts = {
            1: ROOT / "docs" / "reports" / f"{ARTIFACT_PREFIX}1_2026-06-04.json",
            2: ROOT / "docs" / "reports" / f"{ARTIFACT_PREFIX}2_2026-06-04.json",
            4: ROOT / "docs" / "reports" / f"{ARTIFACT_PREFIX}4_2026-06-04.json",
            8: ROOT / "docs" / "reports" / f"{ARTIFACT_PREFIX}8_2026-06-04.json",
            16: ROOT / "docs" / "reports" / f"{ARTIFACT_PREFIX}16_2026-06-04.json",
            32: ROOT / "docs" / "reports" / f"{ARTIFACT_PREFIX}32_2026-06-04.json",
        }
        for stream_count, path in artifacts.items():
            with self.subTest(stream_count=stream_count):
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(data["rtdl_commit"], EXPECTED_COMMIT)
                self.assertEqual(data["batch_stream_count"], stream_count)
                self.assertEqual(data["exact_count"], 1430)
                self.assertEqual(data["gpu"], "NVIDIA RTX A5000, 580.126.09")
                self.assertTrue(data["scalar_count_pipeline"])
                self.assertEqual(
                    data["interpretation"],
                    "Batch rows are repeated-query throughput evidence only; they do not replace one-shot RayJoin latency comparisons.",
                )
                self.assertTrue(data["batch_rows"])
                for row in data["batch_rows"]:
                    self.assertEqual(row["count_first"], 1430)
                    self.assertEqual(row["count_last"], 1430)
                    self.assertEqual(row["native_modes"], ["prepared_points_device_filtered_batch_count"])
                for authorized in data["claim_boundary"].values():
                    self.assertIs(authorized, False)

    def test_multistream_rows_show_repeated_query_throughput_gain(self) -> None:
        stream1 = json.loads(
            (ROOT / "docs" / "reports" / f"{ARTIFACT_PREFIX}1_2026-06-04.json").read_text(encoding="utf-8")
        )
        stream8 = json.loads(
            (ROOT / "docs" / "reports" / f"{ARTIFACT_PREFIX}8_2026-06-04.json").read_text(encoding="utf-8")
        )
        stream16 = json.loads(
            (ROOT / "docs" / "reports" / f"{ARTIFACT_PREFIX}16_2026-06-04.json").read_text(encoding="utf-8")
        )
        single_req32 = next(row for row in stream1["batch_rows"] if row["request_count"] == 32)
        stream8_req32 = next(row for row in stream8["batch_rows"] if row["request_count"] == 32)
        stream16_req64 = next(row for row in stream16["batch_rows"] if row["request_count"] == 64)

        self.assertLess(stream8_req32["per_request_ms_median"], 0.05)
        self.assertLess(stream16_req64["per_request_ms_median"], 0.04)
        self.assertGreater(
            single_req32["per_request_ms_median"] / stream8_req32["per_request_ms_median"],
            6.0,
        )


if __name__ == "__main__":
    unittest.main()

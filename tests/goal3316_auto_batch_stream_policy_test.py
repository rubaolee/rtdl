from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
PROBE = ROOT / "scripts" / "goal3310_rayjoin_pip_batch_scalar_count_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3316_auto_batch_stream_policy_2026-06-04.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3316_rayjoin_pip_batch_auto_stream_2026-06-04.json"
EXPECTED_COMMIT = "8e28f485ed93da0d467b980e483d382f23000271"


class Goal3316AutoBatchStreamPolicyTest(unittest.TestCase):
    def test_native_auto_policy_is_explicit_and_conservative(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn('std::string(raw) == "auto"', text)
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_BATCH_STREAM_COUNT must be a positive integer or auto", text)
        self.assertIn("request_count >= 64u", text)
        self.assertIn("request_count >= 16u", text)
        self.assertIn("request_count >= 8u", text)
        self.assertIn("return 1u;", text)

    def test_probe_accepts_auto_and_records_effective_stream_count(self) -> None:
        text = PROBE.read_text(encoding="utf-8")
        self.assertIn("_parse_batch_stream_count", text)
        self.assertIn("_effective_batch_stream_count", text)
        self.assertIn('"batch_stream_count_effective"', text)
        self.assertIn("batch stream count must be a positive integer or auto", text)

    def test_report_documents_review_debt_closure_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3316 - Auto Batch Stream Policy", text)
        self.assertIn("Goal3315's Claude review", text)
        self.assertIn("The default remains one stream.", text)
        self.assertIn("0.035896", text)
        self.assertIn("6.59x", text)
        self.assertIn("does not authorize RayJoin paper reproduction", text)

    def test_auto_artifact_is_exact_and_claim_boundary_clean(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["rtdl_commit"], EXPECTED_COMMIT)
        self.assertEqual(data["batch_stream_count"], "auto")
        self.assertEqual(data["exact_count"], 1430)
        self.assertEqual(data["gpu"], "NVIDIA RTX A5000, 580.126.09")
        self.assertTrue(data["scalar_count_pipeline"])
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
            self.assertEqual(row["batch_stream_count_effective"], effective_streams)
            self.assertEqual(row["count_first"], 1430)
            self.assertEqual(row["count_last"], 1430)
            self.assertEqual(row["native_modes"], ["prepared_points_device_filtered_batch_count"])
        self.assertLess(rows[32]["per_request_ms_median"], 0.04)
        self.assertLess(rows[64]["per_request_ms_median"], 0.035)
        for authorized in data["claim_boundary"].values():
            self.assertIs(authorized, False)


if __name__ == "__main__":
    unittest.main()


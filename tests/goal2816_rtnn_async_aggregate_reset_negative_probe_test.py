from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal2816_rtnn_async_aggregate_reset_negative_probe_2026-05-31.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2816_rtnn_async_aggregate_reset_negative_probe_pod"
ARTIFACT_32768 = ARTIFACT_DIR / "rtnn_async_reset_median_f32_32768.json"
ARTIFACT_65536 = ARTIFACT_DIR / "rtnn_async_reset_median_f32_65536.json"
ASYNC_COMMIT = "b760861b394db709a01804c97f6ccd91a25b3ac2"


class Goal2816RtnnAsyncAggregateResetNegativeProbeTest(unittest.TestCase):
    def test_async_reset_probe_artifacts_are_recorded_but_code_is_not_retained(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("cuMemsetD8(d_aggregate", workloads)
        self.assertNotIn("cuMemsetD8Async(d_aggregate", workloads)
        for artifact in (ARTIFACT_32768, ARTIFACT_65536):
            payload = json.loads(artifact.read_text(encoding="utf-8"))
            with self.subTest(artifact=artifact.name):
                self.assertEqual(payload["status"], "pass")
                self.assertEqual(payload["source_commit"], ASYNC_COMMIT)
                self.assertEqual(payload["source_dirty"], [])
                for row in payload["rows"]:
                    self.assertTrue(row["ranked_aggregate_matches_cupy_grid"])

    def test_report_explains_negative_result_without_claiming_regression(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        lower_report = report.lower()
        collapsed = " ".join(report.split())

        self.assertIn("negative probe", lower_report)
        self.assertIn("not retained", report)
        self.assertIn("No public RTDL-beats-CuPy claim is authorized", report)
        self.assertIn("larger batched or graph-captured execution contract", collapsed)


if __name__ == "__main__":
    unittest.main()

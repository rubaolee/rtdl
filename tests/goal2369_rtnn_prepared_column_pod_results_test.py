from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2368_rtnn_prepared_column_pod"
REPORT = ROOT / "docs" / "reports" / "goal2369_rtnn_prepared_column_pod_results_2026-05-19.md"


def _load(name: str) -> dict:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


class Goal2369RtnnPreparedColumnPodResultsTest(unittest.TestCase):
    def test_all_pod_artifacts_are_present_and_successful(self) -> None:
        expected = [
            "rtdl_records_run_optix_3d_65536_r002_k50.json",
            "rtdl_packed_run_optix_3d_65536_r002_k50.json",
            "rtdl_packed_prepared_optix_3d_65536_r002_k50.json",
            "rtdl_records_run_optix_3d_262144_r002_k50.json",
            "rtdl_packed_run_optix_3d_262144_r002_k50.json",
            "rtdl_packed_prepared_optix_3d_262144_r002_k50.json",
        ]
        for name in expected:
            payload = _load(name)
            self.assertTrue(payload["ok"], name)
            self.assertEqual(payload["phase_timings"]["mode"], "uniform_cell_compact")
            self.assertFalse(payload["claim_boundary"]["rtdl_speedup_claim_authorized"])
            self.assertFalse(payload["claim_boundary"]["broad_rt_core_speedup_claim_authorized"])

    def test_packed_columns_are_the_current_large_performance_win(self) -> None:
        records_65 = _load("rtdl_records_run_optix_3d_65536_r002_k50.json")
        packed_65 = _load("rtdl_packed_run_optix_3d_65536_r002_k50.json")
        prepared_65 = _load("rtdl_packed_prepared_optix_3d_65536_r002_k50.json")
        records_262 = _load("rtdl_records_run_optix_3d_262144_r002_k50.json")
        packed_262 = _load("rtdl_packed_run_optix_3d_262144_r002_k50.json")
        prepared_262 = _load("rtdl_packed_prepared_optix_3d_262144_r002_k50.json")

        self.assertEqual(records_65["row_count"], packed_65["row_count"])
        self.assertEqual(records_65["row_count"], prepared_65["row_count"])
        self.assertEqual(records_262["row_count"], packed_262["row_count"])
        self.assertEqual(records_262["row_count"], prepared_262["row_count"])

        self.assertGreater(records_65["elapsed_sec"] / packed_65["elapsed_sec"], 50.0)
        self.assertGreater(records_262["elapsed_sec"] / packed_262["elapsed_sec"], 20.0)
        self.assertLess(packed_65["elapsed_sec"] / prepared_65["elapsed_sec"], 1.05)
        self.assertLess(packed_262["elapsed_sec"] / prepared_262["elapsed_sec"], 1.05)
        self.assertTrue(prepared_262["claim_boundary"]["prepared_execution_reuses_python_packed_inputs"])

    def test_report_states_current_prepared_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("packed-column path is the real performance fix", text)
        self.assertIn("does not yet build and retain", text)
        self.assertIn("native device-resident 3D neighbor search structure", text)
        self.assertIn("does not authorize RTNN paper equivalence", text)
        self.assertIn("prepared_bounded_neighbor_search_3d", text)


if __name__ == "__main__":
    unittest.main()

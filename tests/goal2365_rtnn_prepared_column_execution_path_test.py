from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal2365_rtnn_prepared_column_execution_path_2026-05-19.md"
LOCAL_SMOKE = ROOT / "docs" / "reports" / "goal2365_local_linux_prepared_smoke_4096.json"


class Goal2365RtnnPreparedColumnExecutionPathTest(unittest.TestCase):
    def test_runner_exposes_packed_plus_prepared_execution_mode(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("--input-mode", text)
        self.assertIn("packed-columns", text)
        self.assertIn("--execution-mode", text)
        self.assertIn("prepared-optix", text)
        self.assertIn("rt.prepare_optix(_goal2348_current_fixed_radius_neighbors_3d).bind", text)
        self.assertIn('"execution_mode": execution_mode', text)
        self.assertIn('"execution_prepare_sec": execution_prepare_sec', text)
        self.assertIn('"prepared_execution_reuses_python_packed_inputs"', text)
        self.assertIn("prepare_error = repr(exc)", text)
        self.assertIn("for run_index in range(repeat if ok else 0)", text)

    def test_report_keeps_prepared_path_as_v2_x_design_not_release_claim(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("packed columns plus prepared execution", text)
        self.assertIn("separate preparation cost from repeated execution", text)
        self.assertIn("does not claim RTNN paper equivalence", text)
        self.assertIn("does not claim RT-core acceleration", text)
        self.assertIn("prepared_bounded_neighbor_search_3d", text)

    def test_local_linux_smoke_artifact_records_prepared_path_boundary(self) -> None:
        payload = json.loads(LOCAL_SMOKE.read_text(encoding="utf-8"))
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["input_mode"], "packed-columns")
        self.assertEqual(payload["execution_mode"], "prepared-optix")
        self.assertGreater(payload["execution_prepare_sec"], 0.0)
        self.assertEqual(payload["phase_timings"]["mode"], "uniform_cell_compact")
        self.assertFalse(payload["claim_boundary"]["rtdl_speedup_claim_authorized"])
        self.assertTrue(payload["claim_boundary"]["prepared_execution_reuses_python_packed_inputs"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal2368_rtnn_prepared_column_pod_runner.sh"
REPORT = ROOT / "docs" / "reports" / "goal2368_rtnn_prepared_column_pod_packet_2026-05-19.md"


class Goal2368RtnnPreparedColumnPodPacketTest(unittest.TestCase):
    def test_runner_covers_three_modes_at_two_scales_with_timeouts(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("STEP_TIMEOUT_SECONDS", text)
        self.assertIn("run_step", text)
        self.assertIn("for count in 65536 262144", text)
        self.assertIn("--input-mode records", text)
        self.assertIn("--execution-mode run-optix", text)
        self.assertIn("--input-mode packed-columns", text)
        self.assertIn("--execution-mode prepared-optix", text)
        self.assertIn("rtdl_records_run_optix_3d_${count}_r002_k50.json", text)
        self.assertIn("rtdl_packed_run_optix_3d_${count}_r002_k50.json", text)
        self.assertIn("rtdl_packed_prepared_optix_3d_${count}_r002_k50.json", text)

    def test_report_keeps_packet_claim_boundary_precise(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("records` + `run-optix", text)
        self.assertIn("packed-columns` + `prepared-optix", text)
        self.assertIn("does not authorize RTNN paper equivalence", text)
        self.assertIn("do not silently hang", text)


if __name__ == "__main__":
    unittest.main()

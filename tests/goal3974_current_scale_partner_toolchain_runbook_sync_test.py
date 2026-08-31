import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "docs" / "audit" / "runbooks" / "rtx_cloud_single_session_runbook.md"
REPORT = ROOT / "docs" / "reports" / "goal3974_current_scale_partner_toolchain_runbook_sync_2026-06-08.md"


class Goal3974CurrentScalePartnerToolchainRunbookSyncTest(unittest.TestCase):
    def test_runbook_records_driver_550_numba_cupy_partner_setup(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")
        for fragment in [
            "Current v2.x Partner Toolchain On Driver 550 Pods",
            "numba==0.60.0",
            "nvidia-cuda-nvcc-cu12==12.4.131",
            "cupy-cuda12x",
            "PTX `.version 8.7`",
            "PTX `8.4`",
            "NUMBA_CUDA_PREFIX=/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc",
            "Keep RTDL OptiX build variables separate from the Numba compiler package",
            "goal3828_current_benchmark_scale_profile_runner.py",
            "goal3971_current_head_scale_profile_after_loader_closeout_2026-06-08/summary.json",
        ]:
            self.assertIn(fragment, text)

    def test_runbook_includes_partner_smoke_before_long_packet(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")
        self.assertIn("@cuda.jit", text)
        self.assertIn("assert d.copy_to_host().tolist() == [1, 2, 3, 4, 5, 6, 7, 8]", text)
        self.assertIn("assert int(cp.sum(cp.arange(8, dtype=cp.int32)).get()) == 28", text)

    def test_report_records_scope_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "Goal3971 proved",
            "driver-550 pods need a driver-compatible Numba CUDA compiler path",
            "does not authorize release",
            "app-specific\nnative-engine logic",
        ]:
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()

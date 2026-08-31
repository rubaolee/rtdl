from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal3020_l4_optix_readiness_and_ptx_toolchain_blocker_2026-06-01.md"


class Goal3020L4OptixReadinessAndPtxToolchainBlockerTest(unittest.TestCase):
    def test_report_records_build_success_and_ptx_blocker(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "NVIDIA L4, 565.57.01",
            "/usr/local/cuda-12.8/bin/nvcc",
            "OptiX SDK",
            "build/librtdl_optix.so",
            "libnvrtc.so.12",
            "rtdl_rt_grouped_reduced_nearest_witness",
            "unsupported toolchain",
            "RTDL algorithm failure",
            "driver/toolkit compatibility blocker",
            "compatible CUBIN instead of PTX",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

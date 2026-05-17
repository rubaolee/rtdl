from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
OPTIX_WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
OPTIX_CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"


class Goal2165SegmentPairIntersectionCountFirstOutputTest(unittest.TestCase):
    def test_native_launch_uses_count_first_candidate_output(self) -> None:
        text = OPTIX_WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("launch_candidate_pass", text)
        self.assertIn("const uint32_t gpu_count = launch_candidate_pass(0, 0)", text)
        self.assertIn("DevPtr d_output(sizeof(GpuSegmentPairIntersectionRecord) * gpu_count)", text)
        self.assertNotIn(
            "DevPtr d_output(sizeof(GpuSegmentPairIntersectionRecord) * capacity)",
            text,
        )

    def test_kernel_can_count_without_output_buffer(self) -> None:
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")
        core = OPTIX_CORE.read_text(encoding="utf-8")

        self.assertIn("lp.output = output_capacity == 0", workloads)
        self.assertIn("if (slot < params.output_capacity)", core)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "src/native/optix/rtdl_optix_core.cpp"
REPORT = ROOT / "docs/reports/goal3697_segment_pair_precision_guard_native_candidate_policy_2026-06-07.md"


class Goal3697SegmentPairPrecisionGuardNativeCandidatePolicyTest(unittest.TestCase):
    def test_optix_segment_pair_conservative_candidate_uses_precision_guard_slack(self) -> None:
        source = CORE.read_text(encoding="utf-8")
        block = source.split("static __forceinline__ __device__ bool seg_intersect_conservative_candidate", 1)[1].split(
            "extern \"C\" __global__ void __raygen__segment_pair_intersection_probe",
            1,
        )[0]

        self.assertIn("const float slack = 1.0e-3f;", block)
        self.assertIn("host-side exact refinement remains the", block)
        self.assertIn("endpoint-near float32 rounding", block)
        self.assertIn("t < -slack", block)
        self.assertIn("u < -slack", block)

    def test_report_states_static_scope_and_pod_gate(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("generic OptiX candidate-policy repair", report)
        self.assertIn("host-side exact refinement remains the final authority", report)
        self.assertIn("no app-specific branch", report)
        self.assertIn("static/native-policy implementation note until pod evidence", report)
        self.assertIn("missing count `0`", report)
        self.assertIn("does not authorize", report)


if __name__ == "__main__":
    unittest.main()

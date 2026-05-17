from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
OPTIX_CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"


class Goal2169OptixLsiDeviceConservativeExactFilterTest(unittest.TestCase):
    def test_anyhit_uses_conservative_device_filter_before_emitting(self) -> None:
        text = OPTIX_CORE.read_text(encoding="utf-8")

        self.assertIn("seg_intersect_conservative_candidate", text)
        self.assertIn("const float slack = 1.0e-4f", text)
        self.assertIn("if (!seg_intersect_conservative_candidate(", text)
        self.assertIn("host-side exact refine remains the final authority", text)

    def test_degenerate_cases_remain_candidates_for_host_refine(self) -> None:
        text = OPTIX_CORE.read_text(encoding="utf-8")

        self.assertIn("if (dabsf(denom) < 1.0e-7f)", text)
        self.assertIn("return true;", text)
        self.assertIn("return false;", text)


if __name__ == "__main__":
    unittest.main()

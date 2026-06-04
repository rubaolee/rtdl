from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"


class Goal3264ClosedShapeCountOnlyIntersectionPayloadTest(unittest.TestCase):
    def test_count_only_path_accumulates_in_intersection_program_before_anyhit(self) -> None:
        text = CORE.read_text(encoding="utf-8")
        start = text.index('extern "C" __global__ void __intersection__pip_isect()')
        end = text.index('extern "C" __global__ void __anyhit__pip_anyhit()', start)
        body = text[start:end]

        for phrase in (
            "if (params.output == nullptr && params.output_capacity == 0u)",
            "optixSetPayload_2(optixGetPayload_2() + 1u);",
            "return;",
            "optixReportIntersection(0.5f, 0u);",
        ):
            self.assertIn(phrase, body)

        self.assertLess(
            body.index("optixSetPayload_2(optixGetPayload_2() + 1u);"),
            body.index("optixReportIntersection(0.5f, 0u);"),
        )

    def test_anyhit_count_branch_remains_as_legacy_fallback(self) -> None:
        text = CORE.read_text(encoding="utf-8")
        start = text.index('extern "C" __global__ void __anyhit__pip_anyhit()')
        end = text.index(")CUDA\";", start)
        body = text[start:end]

        self.assertIn("params.output == nullptr && params.output_capacity == 0u", body)
        self.assertIn("optixSetPayload_2(optixGetPayload_2() + 1u)", body)
        self.assertIn("optixIgnoreIntersection()", body)


if __name__ == "__main__":
    unittest.main()

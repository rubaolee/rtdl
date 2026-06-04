from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal3254ClosedShapePerProbeCountAccumulationTest(unittest.TestCase):
    def test_count_only_closed_shape_path_accumulates_hits_per_probe_payload(self) -> None:
        text = CORE.read_text(encoding="utf-8")

        raygen_start = text.index('extern "C" __global__ void __raygen__pip_probe()')
        miss_start = text.index('extern "C" __global__ void __miss__pip_miss()', raygen_start)
        raygen = text[raygen_start:miss_start]
        self.assertIn("params.output == nullptr && params.output_capacity == 0u && p2 != 0u", raygen)
        self.assertIn("atomicAdd(params.output_count, p2)", raygen)

        anyhit_start = text.index('extern "C" __global__ void __anyhit__pip_anyhit()')
        end = text.index(")CUDA\";", anyhit_start)
        anyhit = text[anyhit_start:end]
        self.assertIn("params.output == nullptr && params.output_capacity == 0u", anyhit)
        self.assertIn("optixSetPayload_2(optixGetPayload_2() + 1u)", anyhit)
        self.assertIn("optixIgnoreIntersection()", anyhit)

    def test_device_filtered_count_still_uses_count_only_positive_path(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        start = text.index("static void count_prepared_point_closed_shape_membership_device_filtered_2d_optix")
        end = text.index("struct ShapePairRelationFlagComputation", start)
        body = text[start:end]

        self.assertIn("lp.output         = nullptr", body)
        self.assertIn("lp.output_capacity = 0u", body)
        self.assertIn("lp.positive_only  = 1u", body)
        self.assertIn("lp.device_prefilter = 1u", body)


if __name__ == "__main__":
    unittest.main()

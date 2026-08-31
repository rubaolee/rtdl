import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
RUNNER = ROOT / "scripts" / "goal3722_rayjoin_lsi_direct_intersection_route_probe.py"


class Goal3722RayJoinLsiDirectIntersectionRouteProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prelude = PRELUDE.read_text(encoding="utf-8")
        cls.api = API.read_text(encoding="utf-8")
        cls.workloads = WORKLOADS.read_text(encoding="utf-8")
        cls.runtime = RUNTIME.read_text(encoding="utf-8")
        cls.runner = RUNNER.read_text(encoding="utf-8")

    def test_direct_intersection_abi_is_declared_and_bound(self):
        symbol = "rtdl_optix_count_prepared_segment_pair_intersection_prepared_left_direct_intersection"
        self.assertIn(symbol, self.prelude)
        self.assertIn(f'extern "C" int {symbol}', self.api)
        self.assertIn("OPTIX_SEGMENT_PAIR_COUNT_PREPARED_LEFT_DIRECT_INTERSECTION_SYMBOL", self.runtime)
        self.assertIn("def count_prepared_left_direct_intersection", self.runtime)
        registration = self.runtime.split(
            "optional_count_prepared_segment_pair_prepared_left_direct_intersection",
            1,
        )[1].split("optional_segment_pair_candidate_device_columns", 1)[0]
        self.assertIn("ctypes.POINTER(ctypes.c_size_t)", registration)
        self.assertIn("restype = ctypes.c_int", registration)

    def test_native_route_uses_intersection_program_without_anyhit(self):
        self.assertIn("kSegmentPairDirectIntersectionExactCountKernelSrc", self.workloads)
        kernel = self.workloads.split("kSegmentPairDirectIntersectionExactCountKernelSrc", 1)[1].split(
            "struct SegmentFirstHitLaunchParams",
            1,
        )[0]
        self.assertIn("__intersection__segment_pair_direct_intersection_exact_count_isect", kernel)
        self.assertIn("exact_segment_intersection_device", kernel)
        self.assertIn("atomicAdd(params.exact_count", kernel)
        self.assertNotIn("__anyhit__", kernel)
        ensure_block = self.workloads.split("ensure_segment_pair_direct_intersection_exact_count_pipeline", 1)[1].split(
            "static void ensure_segment_pair_ambiguity_count_kernel",
            1,
        )[0]
        self.assertIn("nullptr,\n            nullptr,\n            1", ensure_block)

    def test_python_front_door_is_diagnostic_and_claim_bounded(self):
        method = self.runtime.split("def count_prepared_left_direct_intersection", 1)[1].split(
            "def candidate_device_columns",
            1,
        )[0]
        self.assertIn("diagnostic route, not public default", method)
        self.assertIn('"diagnostic_only": True', method)
        self.assertIn('"rtdl_beats_rayjoin_claim_authorized": False', method)
        self.assertIn('"release_authorized": False', method)
        self.assertNotIn("RayJoin", method)
        self.assertIn("count_prepared_left_direct_intersection", self.runtime)

    def test_runner_compares_direct_intersection_existing_route_and_rayjoin(self):
        self.assertIn("SCHEMA = \"rtdl.goal3722.rayjoin_lsi_direct_intersection_route_probe.v1\"", self.runner)
        self.assertIn("existing_anyhit_exact_count", self.runner)
        self.assertIn("direct_intersection_exact_count", self.runner)
        self.assertIn("prepared.count_prepared_left_direct_intersection(prepared_left)", self.runner)
        self.assertIn("direct_intersection_speedup_vs_existing_anyhit", self.runner)
        self.assertIn("direct_intersection_speedup_vs_rayjoin", self.runner)
        self.assertIn('"diagnostic_only": True', self.runner)
        self.assertIn('"rtdl_beats_rayjoin_claim_authorized": False', self.runner)


if __name__ == "__main__":
    unittest.main()

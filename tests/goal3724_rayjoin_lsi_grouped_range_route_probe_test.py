import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
RUNNER = ROOT / "scripts" / "goal3724_rayjoin_lsi_grouped_range_route_probe.py"


class Goal3724RayJoinLsiGroupedRangeRouteProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prelude = PRELUDE.read_text(encoding="utf-8")
        cls.api = API.read_text(encoding="utf-8")
        cls.workloads = WORKLOADS.read_text(encoding="utf-8")
        cls.runtime = RUNTIME.read_text(encoding="utf-8")
        cls.runner = RUNNER.read_text(encoding="utf-8")

    def test_grouped_range_abi_is_declared_and_bound(self):
        symbol = (
            "rtdl_optix_count_prepared_segment_pair_intersection_prepared_left_"
            "grouped_range_direct_intersection"
        )
        self.assertIn(symbol, self.prelude)
        self.assertIn(f'extern "C" int {symbol}', self.api)
        self.assertIn("OPTIX_SEGMENT_PAIR_COUNT_PREPARED_LEFT_GROUPED_RANGE_DIRECT_INTERSECTION_SYMBOL", self.runtime)
        self.assertIn("def count_prepared_left_grouped_range_direct_intersection", self.runtime)
        registration = self.runtime.split(
            "optional_count_prepared_segment_pair_prepared_left_grouped_range_direct_intersection",
            1,
        )[1].split("optional_segment_pair_candidate_device_columns", 1)[0]
        self.assertIn("ctypes.POINTER(ctypes.c_size_t)", registration)
        self.assertIn("restype = ctypes.c_int", registration)

    def test_native_route_uses_generic_segment_ranges(self):
        self.assertIn("struct SegmentPairGroupRange", self.workloads)
        self.assertIn("ensure_segment_pair_grouped_ranges", self.workloads)
        self.assertIn("RTDL_OPTIX_SEGMENT_PAIR_GROUPED_RANGE_MAX_SIZE", self.workloads)
        self.assertIn("RTDL_OPTIX_SEGMENT_PAIR_GROUPED_RANGE_AREA_ENLARGE", self.workloads)
        self.assertIn("size_t max_segments_per_group = 1;", self.workloads)
        self.assertIn("float area_enlarge_limit = 1.5f;", self.workloads)
        self.assertIn("kSegmentPairGroupedRangeDirectIntersectionExactCountKernelSrc", self.workloads)
        kernel = self.workloads.split(
            "kSegmentPairGroupedRangeDirectIntersectionExactCountKernelSrc",
            1,
        )[1].split("struct SegmentFirstHitLaunchParams", 1)[0]
        self.assertIn("__intersection__segment_pair_grouped_range_direct_intersection_exact_count_isect", kernel)
        self.assertIn("for (unsigned int ridx = range.begin; ridx < range.end; ++ridx)", kernel)
        self.assertIn("exact_segment_intersection_device(left, right)", kernel)
        self.assertNotIn("RayJoin", kernel)

    def test_python_front_door_is_diagnostic_and_claim_bounded(self):
        method = self.runtime.split("def count_prepared_left_grouped_range_direct_intersection", 1)[1].split(
            "def candidate_device_columns",
            1,
        )[0]
        self.assertIn("diagnostic route, not public default", method)
        self.assertIn("right_group_count", method)
        self.assertIn('"diagnostic_only": True', method)
        self.assertIn('"rtdl_beats_rayjoin_claim_authorized": False', method)
        self.assertIn('"release_authorized": False', method)
        self.assertIn("count_prepared_left_grouped_range_direct_intersection", self.runtime)

    def test_runner_uses_rayjoin_like_orientation_without_app_specific_native_logic(self):
        self.assertIn("SCHEMA = \"rtdl.goal3724.rayjoin_lsi_grouped_range_route_probe.v1\"", self.runner)
        self.assertIn("query rays are soil edges", self.runner)
        self.assertIn("base set is county edges", self.runner)
        self.assertIn("grouped_range_speedup_vs_existing_anyhit", self.runner)
        self.assertIn("right_group_compression_ratio", self.runner)
        self.assertIn("--group-max-size", self.runner)
        self.assertIn("--group-area-enlarge", self.runner)
        self.assertIn('parser.add_argument("--group-max-size", type=int, default=1)', self.runner)
        self.assertIn('parser.add_argument("--group-area-enlarge", type=float, default=1.5)', self.runner)
        self.assertIn("grouping_policy", self.runner)
        self.assertIn('"diagnostic_only": True', self.runner)
        self.assertIn('"rtdl_beats_rayjoin_claim_authorized": False', self.runner)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
RUNNER = ROOT / "scripts" / "goal3718_rayjoin_lsi_native_repeated_count_diagnostic.py"


class Goal3718SegmentPairPreparedLeftRepeatedCountDiagnosticTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prelude = PRELUDE.read_text(encoding="utf-8")
        cls.api = API.read_text(encoding="utf-8")
        cls.workloads = WORKLOADS.read_text(encoding="utf-8")
        cls.runtime = RUNTIME.read_text(encoding="utf-8")
        cls.runner = RUNNER.read_text(encoding="utf-8")

    def test_native_abi_declares_repeated_prepared_left_exact_count(self):
        symbol = "rtdl_optix_count_prepared_segment_pair_intersection_prepared_left_repeated"
        self.assertIn(symbol, self.prelude)
        self.assertIn("size_t repeat_count", self.prelude)
        self.assertIn("double* total_seconds_out", self.prelude)
        self.assertIn("double* min_seconds_out", self.prelude)
        self.assertIn("double* max_seconds_out", self.prelude)

    def test_api_export_routes_to_generic_repeated_helper(self):
        symbol = "rtdl_optix_count_prepared_segment_pair_intersection_prepared_left_repeated"
        self.assertIn(f'extern "C" int {symbol}', self.api)
        export_block = self.api.split(f'extern "C" int {symbol}', 1)[1].split(
            'extern "C" int rtdl_optix_prepared_segment_pair_candidate_device_columns',
            1,
        )[0]
        self.assertIn("count_prepared_segment_pair_intersection_prepared_left_repeated_optix", export_block)
        self.assertIn("repeat_count", export_block)
        self.assertNotIn("RayJoin", export_block)

    def test_native_helper_reuses_existing_exact_prepared_left_count_and_checks_stability(self):
        helper = self.workloads.split(
            "static void count_prepared_segment_pair_intersection_prepared_left_repeated_optix",
            1,
        )[1].split("static void run_prepared_segment_first_hit_optix", 1)[0]
        self.assertIn("count_prepared_segment_pair_intersection_prepared_left_optix", helper)
        self.assertIn("repeat_count == 0", helper)
        self.assertIn("current_count != stable_count", helper)
        self.assertIn("total_seconds", helper)
        self.assertIn("min_seconds", helper)
        self.assertIn("max_seconds", helper)
        self.assertNotIn("RayJoin", helper)

    def test_python_front_door_is_diagnostic_and_claim_bounded(self):
        self.assertIn("OPTIX_SEGMENT_PAIR_COUNT_PREPARED_LEFT_REPEATED_SYMBOL", self.runtime)
        self.assertIn("def count_prepared_left_repeated", self.runtime)
        method = self.runtime.split("def count_prepared_left_repeated", 1)[1].split(
            "def candidate_device_columns",
            1,
        )[0]
        self.assertIn("repeat_count must be positive", method)
        self.assertIn("SEGMENT_PAIR_PREPARED_LEFT_REPEATED_EXACT_COUNT_V1", method)
        self.assertIn('"diagnostic_only": True', method)
        self.assertIn('"public_speedup_claim_authorized": False', method)
        self.assertNotIn("RayJoin", method)

    def test_python_runtime_registers_repeated_symbol_argtypes(self):
        registration = self.runtime.split(
            "optional_count_prepared_segment_pair_prepared_left_repeated",
            1,
        )[1].split("optional_segment_pair_candidate_device_columns", 1)[0]
        self.assertIn("OPTIX_SEGMENT_PAIR_COUNT_PREPARED_LEFT_REPEATED_SYMBOL", registration)
        self.assertIn("ctypes.POINTER(ctypes.c_double)", registration)
        self.assertIn("ctypes.POINTER(ctypes.c_size_t)", registration)
        self.assertIn("restype = ctypes.c_int", registration)

    def test_runner_compares_python_front_door_native_repeated_and_rayjoin(self):
        self.assertIn("SCHEMA = \"rtdl.goal3718.rayjoin_lsi_native_repeated_count_diagnostic.v1\"", self.runner)
        self.assertIn("prepared.count_prepared_left(prepared_left)", self.runner)
        self.assertIn("prepared.count_prepared_left_repeated(prepared_left, repeat)", self.runner)
        self.assertIn("_run_rayjoin_query", self.runner)
        self.assertIn("python_front_door_over_native_repeated_ratio", self.runner)
        self.assertIn("native_repeated_speedup_vs_rayjoin", self.runner)
        self.assertIn('"diagnostic_only": True', self.runner)
        self.assertIn('"rtdl_beats_rayjoin_claim_authorized": False', self.runner)
        self.assertNotIn("paper_reproduction_claim_authorized\": True", self.runner)


if __name__ == "__main__":
    unittest.main()

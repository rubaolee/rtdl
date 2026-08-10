import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
CUDA_HELPER = REPO / "src" / "native" / "optix" / "rtdl_optix_cuda_helpers.cu"
OPTIX_RUNTIME = REPO / "src" / "rtdsl" / "optix_runtime.py"
RAYJOIN_APP = REPO / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"


class Goal5019NativeLexsortBridgeTest(unittest.TestCase):
    def test_native_helper_is_generic_thrust_lexsort(self):
        source = CUDA_HELPER.read_text(encoding="utf-8")
        self.assertIn("#include <thrust/sort.h>", source)
        self.assertIn("rtdl_cuda_sort_i64_f64_i64_i64_lex", source)
        self.assertIn("RtdlLexsortI64F64I64I64Compare", source)
        self.assertNotIn("rayjoin", source[source.index("rtdl_cuda_sort_i64_f64_i64_i64_lex") :])

    def test_runtime_wrapper_is_generic_and_optional(self):
        source = OPTIX_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("def run_cuda_lexsort_i64_f64_i64_i64_device", source)
        self.assertIn("_find_optional_backend_symbol(lib, \"rtdl_cuda_sort_i64_f64_i64_i64_lex\")", source)
        helper = source[source.index("def run_cuda_lexsort_i64_f64_i64_i64_device") :]
        helper = helper[: helper.index("\ndef _coerce_list")]
        self.assertIn("device_resident", helper)
        self.assertIn('"input_key_columns_mutated_in_place": True', helper)
        self.assertNotIn("rayjoin_overlay", helper)

    def test_rayjoin_app_keeps_native_lexsort_opt_in_with_fallback(self):
        source = RAYJOIN_APP.read_text(encoding="utf-8")
        self.assertIn("--native-lexsort", source)
        self.assertIn("native_lexsort_enabled", source)
        self.assertIn("native_sort_count = int(valid_count)", source)
        self.assertIn("count=native_sort_count", source)
        self.assertIn('"device_sort_native_count": int(valid_count) if native_lexsort else None', source)
        self.assertIn("sort_map1_device_columnar_native_lexsort_sec", source)
        self.assertIn("sort_map1_device_columnar_copy_order_to_host_sec", source)
        self.assertIn("sort_map1_device_columnar_host_run_start_table_sec", source)
        self.assertIn("segment_device_arrays=device_segment_arrays_right", source)
        self.assertIn("sort_map1_device_columnar_segment_xy_reused", source)
        self.assertIn("_bitonic_sort_device(out_edge, out_dist, out_tie, out_order)", source)
        self.assertIn("sort_backend_side0", source)
        self.assertIn("native_thrust_lexsort_i64_f64_i64_i64", source)


if __name__ == "__main__":
    unittest.main()

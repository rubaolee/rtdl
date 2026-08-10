import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"


class Goal5033DescriptorConsumerNativeLexsortTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = APP.read_text(encoding="utf-8")

    def test_device_descriptor_consumer_uses_generic_native_lexsort(self):
        source_prefix = self.source[: self.source.index("def descriptor_pair_count_projected_device")]
        helper = self.source[
            self.source.index("def descriptor_pair_count_projected_device") :
            self.source.index("def _build_projected_descriptor_carrier_device_side")
        ]
        self.assertIn("from rtdsl import device_order_by", source_prefix)
        self.assertIn("_run_public_device_order_by_native_lexsort", helper)
        self.assertIn("public_device_order_by_used", self.source)
        self.assertNotIn("run_cuda_lexsort_i64_f64_i64_i64_device", helper)
        self.assertIn("_reduce_sorted_descriptor_pairs_with_order_single_kernel", helper)
        self.assertIn("native_thrust_lexsort_i64_f64_i64_i64_descriptor_pair_scan", helper)
        self.assertNotIn("rayjoin_overlay", helper)
        self.assertNotIn("output_chain", helper)

    def test_legacy_numba_bitonic_path_remains_as_fallback(self):
        helper = self.source[
            self.source.index("def descriptor_pair_count_projected_device") :
            self.source.index("def _build_projected_descriptor_carrier_device_side")
        ]
        self.assertIn("numba_cuda_device_pair_sort_scan_fallback", helper)
        self.assertIn("_bitonic_sort_pairs_device", helper)
        self.assertIn("native_lexsort_descriptor_pair_scan_error", helper)

    def test_ordered_reducer_keeps_lengths_unsorted_and_gathers_by_order(self):
        reducer = self.source[
            self.source.index("def _reduce_sorted_descriptor_pairs_with_order_single_kernel") :
            self.source.index("def _sum_two_i64_single_kernel")
        ]
        self.assertIn("lengths[int(order[index])]", reducer)
        self.assertIn("a = int(label_a[index])", reducer)
        self.assertIn("b = int(label_b[index])", reducer)

    def test_read_only_consumer_sorts_private_key_snapshots(self):
        helper = self.source[
            self.source.index("def descriptor_pair_count_projected_device") :
            self.source.index("def _build_projected_descriptor_carrier_device_side")
        ]
        self.assertIn("sorted_label_a = cuda.device_array", helper)
        self.assertIn("sorted_label_b = cuda.device_array", helper)
        self.assertIn(
            "sorted_label_a.copy_to_device(carrier_label_a[:valid_count])",
            helper,
        )
        self.assertIn(
            "sorted_label_b.copy_to_device(carrier_label_b[:valid_count])",
            helper,
        )
        sort_call = helper[
            helper.index("_run_public_device_order_by_native_lexsort(") :
            helper.index("_reduce_sorted_descriptor_pairs_with_order_single_kernel")
        ]
        self.assertIn("sorted_label_a", sort_call)
        self.assertIn("sorted_label_b", sort_call)
        self.assertNotIn("carrier_label_a,", sort_call)
        self.assertNotIn("carrier_label_b,", sort_call)


if __name__ == "__main__":
    unittest.main()

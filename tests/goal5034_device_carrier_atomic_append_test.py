import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"


class Goal5034DeviceCarrierAtomicAppendTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = APP.read_text(encoding="utf-8")

    def test_device_carrier_uses_atomic_append_builder(self):
        self.assertIn("def _carrier_side_atomic_append_kernel", self.source)
        self.assertIn("def _build_projected_descriptor_carrier_device_atomic_append_side", self.source)
        self.assertIn("_build_projected_descriptor_carrier_device_atomic_append_side(", self.source)
        self.assertIn("cuda.atomic.add(counters, 0, 1)", self.source)
        self.assertIn("device_resident_carrier_atomic_append_used", self.source)

    def test_device_carrier_no_longer_requires_prefix_for_binary_ordering(self):
        build_body = self.source.split("def build_projected_descriptor_carrier_columnar_device", 1)[1].split(
            "def descriptor_pair_count_projected", 1
        )[0]
        self.assertNotIn("_exclusive_prefix_sum_i64_single_kernel", build_body)
        self.assertNotIn("_carrier_side_count_kernel", build_body)
        self.assertNotIn("_carrier_side_fill_kernel", build_body)

    def test_atomic_append_stays_app_layer(self):
        build_body = self.source.split("def build_projected_descriptor_carrier_columnar_device", 1)[1].split(
            "def descriptor_pair_count_projected", 1
        )[0]
        self.assertNotIn("rayjoin_overlay", build_body)
        self.assertNotIn("output_chain", build_body)
        self.assertIn('"rtdl_core_change": False', self.source)

    def test_concurrent_side_append_is_flagged_binary_route_only(self):
        self.assertIn("--device-carrier-concurrent-sides", self.source)
        self.assertIn("concurrent_side_kernels=False", self.source)
        self.assertIn("cuda.stream()", self.source)
        self.assertIn("_carrier_side_atomic_append_kernel[blocks, threads, stream]", self.source)
        self.assertIn("device_resident_carrier_concurrent_side_append_kernels_sec", self.source)
        self.assertIn("device_carrier_concurrent_sides_used", self.source)
        self.assertIn("--device-carrier-concurrent-sides requires --device-resident-carrier", self.source)

    def test_descriptor_consumer_can_read_carrier_prefix_directly(self):
        consumer_body = self.source.split("def descriptor_pair_count_projected_device", 1)[1].split(
            "def _build_projected_descriptor_carrier_device_side", 1
        )[0]
        self.assertIn('carrier_label_a = carrier["label_a_device"]', consumer_body)
        self.assertIn('carrier_label_b = carrier["label_b_device"]', consumer_body)
        self.assertIn('carrier_lengths = carrier["group_length_device"]', consumer_body)
        self.assertIn("native_lexsort_direct_carrier_prefix", consumer_body)
        self.assertIn("downstream_consumer_native_lexsort_direct_carrier_prefix", self.source)
        self.assertNotIn("rayjoin_overlay", consumer_body)


if __name__ == "__main__":
    unittest.main()

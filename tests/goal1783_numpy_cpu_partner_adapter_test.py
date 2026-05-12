from __future__ import annotations

import importlib.util
import unittest

import rtdsl as rt


class Goal1783NumPyCpuPartnerAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        if importlib.util.find_spec("numpy") is None:
            self.skipTest("NumPy is not installed in this dev environment")
        import numpy as np

        self.np = np

    def test_numpy_is_registered_as_cpu_embree_partner(self) -> None:
        self.assertIn("numpy", rt.partner.registered())
        contract = rt.v2_0_partner_protocol_contract()
        self.assertEqual(contract.cpu_reference_partner, "numpy")
        self.assertEqual(rt.validate_v2_0_partner_protocol_contract()["status"], "accept")

    def test_auto_prefers_numpy_adapter_over_generic_dlpack(self) -> None:
        array = self.np.arange(6, dtype=self.np.float32).reshape(2, 3)
        ctx = rt.partner.auto(array)
        descriptor = ctx.tensor(array)
        self.assertEqual(ctx.name, "numpy")
        self.assertEqual(descriptor.source_protocol, "numpy")
        self.assertEqual(descriptor.device_type, "cpu")
        self.assertEqual(descriptor.device_id, 0)
        self.assertEqual(descriptor.dtype, "float32")
        self.assertEqual(descriptor.shape, (2, 3))
        self.assertEqual(descriptor.strides, array.strides)
        self.assertEqual(descriptor.data_ptr, int(array.__array_interface__["data"][0]))
        self.assertIs(descriptor.owner, array)

    def test_numpy_descriptor_preserves_non_contiguous_host_strides(self) -> None:
        base = self.np.arange(12, dtype=self.np.float64).reshape(3, 4)
        view = base[:, ::2]
        descriptor = rt.partner.use("numpy").tensor(view)
        self.assertEqual(descriptor.source_protocol, "numpy")
        self.assertEqual(descriptor.shape, (3, 2))
        self.assertEqual(descriptor.strides, view.strides)
        self.assertEqual(descriptor.data_ptr, int(view.__array_interface__["data"][0]))

    def test_numpy_output_allocation_is_cpu_only(self) -> None:
        output = rt.partner.use("numpy").empty((4,), dtype="float32", device="cpu")
        self.assertEqual(output.shape, (4,))
        self.assertEqual(str(output.dtype), "float32")
        self.assertTrue(output.flags["C_CONTIGUOUS"])
        with self.assertRaisesRegex(ValueError, "device_type='cpu'"):
            rt.partner.use("numpy").empty((4,), dtype="float32", device="cuda:0")


if __name__ == "__main__":
    unittest.main()

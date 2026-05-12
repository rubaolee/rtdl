from __future__ import annotations

import importlib.util
import unittest

import rtdsl as rt


def _has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


class Goal1781RealFrameworkPartnerAvailabilityTest(unittest.TestCase):
    def test_pytorch_reference_cpu_tensor_export_and_allocation_when_available(self) -> None:
        if not _has_module("torch"):
            self.skipTest("PyTorch is not installed in this dev environment")

        import torch

        tensor = torch.arange(6, dtype=torch.float32).reshape(2, 3)
        ctx = rt.partner.auto(tensor)
        descriptor = ctx.tensor(tensor)
        self.assertEqual(ctx.name, "torch")
        self.assertEqual(descriptor.source_protocol, "torch")
        self.assertEqual(descriptor.device_type, "cpu")
        self.assertEqual(descriptor.device_id, 0)
        self.assertEqual(descriptor.dtype, "torch.float32")
        self.assertEqual(descriptor.shape, (2, 3))
        self.assertIs(descriptor.owner, tensor)

        output = rt.partner.use("torch").empty((4,), dtype="float32", device="cpu")
        self.assertEqual(tuple(output.shape), (4,))
        self.assertEqual(str(output.dtype), "torch.float32")
        self.assertEqual(output.device.type, "cpu")

    def test_pytorch_reference_rejects_grad_enabled_tensor_when_available(self) -> None:
        if not _has_module("torch"):
            self.skipTest("PyTorch is not installed in this dev environment")

        import torch

        tensor = torch.ones(3, dtype=torch.float32, requires_grad=True)
        with self.assertRaisesRegex(ValueError, "grad-enabled PyTorch tensors"):
            rt.partner.auto(tensor).tensor(tensor)

    def test_pytorch_cuda_descriptor_when_cuda_available(self) -> None:
        if not _has_module("torch"):
            self.skipTest("PyTorch is not installed in this dev environment")

        import torch

        if not torch.cuda.is_available():
            self.skipTest("PyTorch is installed, but CUDA is not available in this dev environment")

        tensor = torch.arange(8, dtype=torch.float32, device="cuda:0")
        descriptor = rt.partner.auto(tensor).tensor(tensor)
        self.assertEqual(descriptor.source_protocol, "torch")
        self.assertEqual(descriptor.device_type, "cuda")
        self.assertEqual(descriptor.device_id, 0)
        self.assertGreater(int(descriptor.data_ptr or 0), 0)

    def test_cupy_conformance_cuda_export_and_allocation_when_available(self) -> None:
        if not _has_module("cupy"):
            self.skipTest("CuPy is not installed in this dev environment")

        import cupy

        try:
            device_count = int(cupy.cuda.runtime.getDeviceCount())
        except Exception as exc:  # pragma: no cover - depends on local CUDA runtime.
            self.skipTest(f"CuPy is installed, but CUDA device query failed: {type(exc).__name__}: {exc}")
        if device_count <= 0:
            self.skipTest("CuPy is installed, but no CUDA devices are visible")

        tensor = cupy.arange(6, dtype=cupy.float32).reshape(2, 3)
        ctx = rt.partner.auto(tensor)
        descriptor = ctx.tensor(tensor)
        self.assertEqual(ctx.name, "cupy")
        self.assertEqual(descriptor.source_protocol, "cupy")
        self.assertEqual(descriptor.device_type, "cuda")
        self.assertEqual(descriptor.device_id, 0)
        self.assertIn("float32", descriptor.dtype)
        self.assertEqual(descriptor.shape, (2, 3))
        self.assertGreater(int(descriptor.data_ptr or 0), 0)

        output = rt.partner.use("cupy").empty((4,), dtype="float32", device="cuda:0")
        self.assertEqual(tuple(output.shape), (4,))
        self.assertIn("float32", str(output.dtype))

    def test_cupy_conformance_cpu_allocation_rejected_even_when_uninstalled(self) -> None:
        if not _has_module("cupy"):
            self.skipTest("CuPy is not installed in this dev environment")
        with self.assertRaisesRegex(ValueError, "device_type='cuda'"):
            rt.partner.use("cupy").empty((1,), dtype="float32", device="cpu")


if __name__ == "__main__":
    unittest.main()

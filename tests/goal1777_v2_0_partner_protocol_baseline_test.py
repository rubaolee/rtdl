from __future__ import annotations

import sys
import types
import unittest

import rtdsl as rt


class _DLPackLike:
    dtype = "float32"
    shape = (2, 3)
    strides = (3, 1)

    def __dlpack__(self):
        return object()

    def __dlpack_device__(self):
        return (2, 0)

    def data_ptr(self):
        return 1111


class _CpuDLPackLike(_DLPackLike):
    def __dlpack_device__(self):
        return (1, 0)


class _TorchLike(_DLPackLike):
    __module__ = "torch"
    requires_grad = False


class _GradTorchLike(_TorchLike):
    requires_grad = True


class _CuPyLike:
    __module__ = "cupy"
    dtype = "float32"
    shape = (2, 3)
    strides = (3, 1)
    __cuda_array_interface__ = {"data": (2222, False), "shape": (2, 3), "typestr": "<f4", "version": 3}

    def __dlpack__(self):
        return object()

    def __dlpack_device__(self):
        return (2, 0)


class _FakeTorch(types.SimpleNamespace):
    float32 = "torch.float32"

    def __init__(self) -> None:
        super().__init__()
        self.calls = []

    def empty(self, shape, *, dtype, device):
        self.calls.append((tuple(shape), dtype, device))
        return {"shape": tuple(shape), "dtype": dtype, "device": device}


class _FakeCuPyDevice:
    def __init__(self, module, device_id: int) -> None:
        self.module = module
        self.device_id = device_id

    def __enter__(self):
        self.module.active_devices.append(self.device_id)
        return self

    def __exit__(self, exc_type, exc, tb):
        self.module.active_devices.pop()
        return False


class _FakeCuPy(types.SimpleNamespace):
    def __init__(self) -> None:
        super().__init__()
        self.calls = []
        self.active_devices = []
        self.cuda = types.SimpleNamespace(Device=lambda device_id: _FakeCuPyDevice(self, device_id))

    def empty(self, shape, *, dtype):
        device_id = self.active_devices[-1] if self.active_devices else 0
        self.calls.append((tuple(shape), dtype, device_id))
        return {"shape": tuple(shape), "dtype": dtype, "device": f"cuda:{device_id}"}


class Goal1777V20PartnerProtocolBaselineTest(unittest.TestCase):
    def test_v2_0_contract_is_protocol_first_with_torch_reference_and_cupy_conformance(self) -> None:
        contract = rt.v2_0_partner_protocol_contract()
        self.assertEqual(contract.version, "rtdl.partner.v2.0")
        self.assertEqual(contract.selection_order, ("protocol", "torch", "cupy"))
        self.assertEqual(contract.reference_partner, "torch")
        self.assertEqual(contract.conformance_partner, "cupy")
        self.assertEqual(contract.cpu_reference_partner, "numpy")
        self.assertEqual(contract.engine_boundary, "python-adapter-only")
        self.assertEqual(contract.stream_policy, "stream_handle_reserved_zero")
        self.assertEqual(contract.zero_copy_claim, "measured_evidence_required")
        self.assertEqual(rt.validate_v2_0_partner_protocol_contract()["status"], "accept")

    def test_contract_validation_rejects_pytorch_or_native_engine_drift(self) -> None:
        bad = rt.RtdlPartnerProtocolContract(
            selection_order=("protocol", "cupy", "torch"),
            reference_partner="cupy",
            conformance_partner="torch",
            cpu_reference_partner="arrow",
            engine_boundary="native-framework-link",
        )
        result = rt.validate_v2_0_partner_protocol_contract(bad)
        self.assertEqual(result["status"], "reject")
        self.assertTrue(any("PyTorch" in error for error in result["errors"]))
        self.assertTrue(any("native engine" in error for error in result["errors"]))
        self.assertTrue(any("NumPy" in error for error in result["errors"]))

    def test_torch_reference_output_allocation_uses_framework_device_spelling(self) -> None:
        fake_torch = _FakeTorch()
        old_torch = sys.modules.get("torch")
        sys.modules["torch"] = fake_torch
        try:
            adapter = rt.PyTorchAdapter()
            cpu = adapter.allocate_output(
                rt.RtdlOutputSpec(dtype="float32", shape=(2,), device_type="cpu", device_id=0)
            )
            cuda = adapter.allocate_output(
                rt.RtdlOutputSpec(dtype="float32", shape=(3,), device_type="cuda", device_id=1)
            )
        finally:
            if old_torch is None:
                sys.modules.pop("torch", None)
            else:
                sys.modules["torch"] = old_torch
        self.assertEqual(cpu["device"], "cpu")
        self.assertEqual(cuda["device"], "cuda:1")
        self.assertEqual(fake_torch.calls, [((2,), "torch.float32", "cpu"), ((3,), "torch.float32", "cuda:1")])

    def test_cupy_conformance_output_allocation_is_cuda_only_and_honors_device_id(self) -> None:
        fake_cupy = _FakeCuPy()
        old_cupy = sys.modules.get("cupy")
        sys.modules["cupy"] = fake_cupy
        try:
            adapter = rt.CuPyAdapter()
            with self.assertRaisesRegex(ValueError, "device_type='cuda'"):
                adapter.allocate_output(rt.RtdlOutputSpec(dtype="float32", shape=(1,), device_type="cpu"))
            cuda = adapter.allocate_output(
                rt.RtdlOutputSpec(dtype="float32", shape=(4,), device_type="cuda", device_id=2)
            )
        finally:
            if old_cupy is None:
                sys.modules.pop("cupy", None)
            else:
                sys.modules["cupy"] = old_cupy
        self.assertEqual(cuda["device"], "cuda:2")
        self.assertEqual(fake_cupy.calls, [((4,), "float32", 2)])

    def test_reference_and_conformance_export_paths_preserve_protocol_metadata(self) -> None:
        torch_descriptor = rt.PyTorchAdapter().export_tensor(_TorchLike())
        cupy_descriptor = rt.CuPyAdapter().export_tensor(_CuPyLike())
        self.assertEqual(torch_descriptor.source_protocol, "torch")
        self.assertEqual(torch_descriptor.device_type, "cuda")
        self.assertEqual(torch_descriptor.data_ptr, 1111)
        self.assertEqual(cupy_descriptor.source_protocol, "cupy")
        self.assertEqual(cupy_descriptor.device_type, "cuda")
        self.assertEqual(cupy_descriptor.data_ptr, 2222)
        with self.assertRaisesRegex(ValueError, "grad-enabled PyTorch tensors"):
            rt.PyTorchAdapter().export_tensor(_GradTorchLike())

    def test_descriptor_and_output_spec_validation_guards_are_pinned(self) -> None:
        invalid_descriptors = (
            {"device_type": "tpu", "device_id": 0, "dtype": "float32", "shape": (1,)},
            {"device_type": "cuda", "device_id": -1, "dtype": "float32", "shape": (1,)},
            {"device_type": "cuda", "device_id": 0, "dtype": "float32", "shape": (-1,)},
            {"device_type": "cuda", "device_id": 0, "dtype": "float32", "shape": (1,), "strides": (1, 1)},
            {"device_type": "cuda", "device_id": 0, "dtype": "float32", "shape": (1,), "byte_offset": -4},
            {"device_type": "cuda", "device_id": 0, "dtype": "float32", "shape": (1,), "stream_handle": 3},
        )
        for kwargs in invalid_descriptors:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    rt.RtdlTensorDescriptor(data_ptr=None, **kwargs)

        invalid_specs = (
            {"dtype": "float32", "shape": (1,), "device_type": "tpu"},
            {"dtype": "float32", "shape": (-1,), "device_type": "cuda"},
            {"dtype": "float32", "shape": (1,), "device_type": "cuda", "fallback_policy": "silent"},
            {"dtype": "float32", "shape": (1,), "device_type": "cuda", "required_alignment_bytes": 0},
        )
        for kwargs in invalid_specs:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    rt.RtdlOutputSpec(**kwargs)

    def test_dlpack_integer_device_normalization_and_auto_fallback_are_pinned(self) -> None:
        cpu_ctx = rt.partner.auto(_CpuDLPackLike())
        generic_ctx = rt.partner.auto(_DLPackLike())
        self.assertEqual(cpu_ctx.name, "dlpack")
        self.assertEqual(generic_ctx.name, "dlpack")
        self.assertEqual(cpu_ctx.tensor(_CpuDLPackLike()).device_type, "cpu")
        self.assertEqual(generic_ctx.tensor(_DLPackLike()).device_type, "cuda")
        self.assertEqual(rt.partner.auto(_TorchLike()).name, "torch")
        self.assertEqual(rt.partner.auto(_CuPyLike()).name, "cupy")


if __name__ == "__main__":
    unittest.main()

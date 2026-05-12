from __future__ import annotations

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


class _TorchLike(_DLPackLike):
    __module__ = "torch"
    requires_grad = False

    def data_ptr(self):
        return 4321


class _GradTorchLike(_TorchLike):
    __module__ = "torch"
    requires_grad = True


class _CuPyLike(_DLPackLike):
    __module__ = "cupy"
    __cuda_array_interface__ = {"data": (8765, False), "shape": (2, 3), "typestr": "<f4", "version": 3}


class _Adapter:
    name = "fake"

    def __init__(self) -> None:
        self.outputs = []

    def can_export(self, obj) -> bool:
        return getattr(obj, "fake_partner", False)

    def export_tensor(self, obj, *, access="read", stream=None):
        return rt.RtdlTensorDescriptor(
            data_ptr=1234,
            device_type="cpu",
            device_id=0,
            dtype="int32",
            shape=(1,),
            access_mode=access,
            owner=obj,
            source_protocol="fake",
        )

    def allocate_output(self, spec, *, stream=None):
        self.outputs.append(spec)
        return {"shape": spec.shape, "dtype": spec.dtype, "device": f"{spec.device_type}:{spec.device_id}"}

    def import_output(self, descriptor):
        return descriptor


class _FakeTensor:
    fake_partner = True


class Goal1675PartnerProtocolSubstrateTest(unittest.TestCase):
    def test_dlpack_adapter_exports_generic_descriptor_without_framework_dependency(self) -> None:
        ctx = rt.partner.auto(_DLPackLike())
        descriptor = ctx.tensor(_DLPackLike())
        self.assertEqual(ctx.name, "dlpack")
        self.assertEqual(descriptor.device_type, "cuda")
        self.assertEqual(descriptor.device_id, 0)
        self.assertEqual(descriptor.dtype, "float32")
        self.assertEqual(descriptor.shape, (2, 3))
        self.assertEqual(descriptor.strides, (3, 1))
        self.assertEqual(descriptor.source_protocol, "dlpack")

    def test_known_framework_adapters_are_detected_without_importing_frameworks(self) -> None:
        torch_ctx = rt.partner.auto(_TorchLike())
        cupy_ctx = rt.partner.auto(_CuPyLike())
        self.assertEqual(torch_ctx.name, "torch")
        torch_descriptor = torch_ctx.tensor(_TorchLike())
        self.assertEqual(torch_descriptor.source_protocol, "torch")
        self.assertEqual(torch_descriptor.data_ptr, 4321)
        self.assertEqual(cupy_ctx.name, "cupy")
        cupy_descriptor = cupy_ctx.tensor(_CuPyLike())
        self.assertEqual(cupy_descriptor.source_protocol, "cupy")
        self.assertEqual(cupy_descriptor.data_ptr, 8765)

    def test_torch_adapter_rejects_grad_enabled_tensors(self) -> None:
        with self.assertRaisesRegex(ValueError, "grad-enabled PyTorch tensors"):
            rt.partner.auto(_GradTorchLike()).tensor(_GradTorchLike())

    def test_registry_prefers_explicit_adapter_before_generic_dlpack(self) -> None:
        adapter = _Adapter()
        rt.partner.register(adapter)
        ctx = rt.partner.use("fake", fallback="copy")
        descriptor = ctx.tensor(_FakeTensor(), access="readwrite")
        self.assertEqual(descriptor.source_protocol, "fake")
        self.assertEqual(descriptor.access_mode, "readwrite")
        out = ctx.empty((4,), dtype="uint8", device="cpu:0")
        self.assertEqual(out["shape"], (4,))
        self.assertEqual(adapter.outputs[-1].fallback_policy, "copy")

    def test_none_partner_and_invalid_fallback_are_rejected_explicitly(self) -> None:
        with self.assertRaisesRegex(TypeError, "partner='none'"):
            rt.partner.use("none").tensor(object())
        with self.assertRaisesRegex(ValueError, "fallback"):
            rt.partner.use("none", fallback="silent")

    def test_descriptor_validation_keeps_v1_7_stream_reserved(self) -> None:
        with self.assertRaisesRegex(ValueError, "stream_handle"):
            rt.RtdlTensorDescriptor(
                data_ptr=None,
                device_type="cuda",
                device_id=0,
                dtype="float32",
                shape=(1,),
                stream_handle=7,
            )


if __name__ == "__main__":
    unittest.main()

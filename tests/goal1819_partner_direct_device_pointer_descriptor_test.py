from __future__ import annotations

import unittest

import rtdsl as rt


class _CudaDLPackLike:
    dtype = "float32"
    shape = (4,)
    strides = (1,)

    def __dlpack__(self):
        return object()

    def __dlpack_device__(self):
        return (2, 0)

    def data_ptr(self):
        return 0xCAFE


class _CpuDLPackLike(_CudaDLPackLike):
    def __dlpack_device__(self):
        return (1, 0)


class _MissingPointerCudaLike(_CudaDLPackLike):
    def data_ptr(self):
        return 0


class _TorchCudaLike(_CudaDLPackLike):
    __module__ = "torch"
    requires_grad = False


class Goal1819PartnerDirectDevicePointerDescriptorTest(unittest.TestCase):
    def test_contract_records_direct_device_handoff_as_descriptor_only(self) -> None:
        contract = rt.v2_0_partner_protocol_contract()
        result = rt.validate_v2_0_partner_protocol_contract(contract)
        self.assertEqual(result["status"], "accept")
        self.assertEqual(
            contract.direct_device_handoff_status,
            "descriptor_only_claims_blocked",
        )
        self.assertEqual(
            result["direct_device_handoff_status"],
            "descriptor_only_claims_blocked",
        )

    def test_cuda_partner_pointer_metadata_is_observable_but_not_authorized(self) -> None:
        handoff = rt.prepare_direct_device_pointer_handoff(_TorchCudaLike())
        self.assertIsInstance(handoff, rt.RtdlDevicePointerHandoff)
        self.assertEqual(handoff.data_ptr, 0xCAFE)
        self.assertEqual(handoff.device_type, "cuda")
        self.assertEqual(handoff.device_id, 0)
        self.assertEqual(handoff.source_protocol, "torch")
        self.assertEqual(handoff.transfer_mode, "device_descriptor_only")
        self.assertTrue(handoff.direct_device_pointer_observed)
        self.assertFalse(handoff.direct_device_handoff_authorized)
        self.assertFalse(handoff.true_zero_copy_authorized)
        metadata = handoff.to_metadata()
        self.assertEqual(metadata["device"], "cuda:0")
        self.assertEqual(metadata["data_ptr"], 0xCAFE)
        self.assertFalse(metadata["direct_device_handoff_authorized"])
        self.assertFalse(metadata["true_zero_copy_authorized"])

    def test_descriptor_only_gate_rejects_cpu_missing_pointer_and_stream_claims(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires a CUDA partner tensor"):
            rt.prepare_direct_device_pointer_handoff(_CpuDLPackLike())
        with self.assertRaisesRegex(ValueError, "non-zero data_ptr"):
            rt.prepare_direct_device_pointer_handoff(_MissingPointerCudaLike())
        with self.assertRaisesRegex(ValueError, "stream_handle"):
            rt.prepare_direct_device_pointer_handoff(_CudaDLPackLike(), stream=7)
        with self.assertRaisesRegex(ValueError, "not authorized"):
            rt.RtdlDevicePointerHandoff(
                descriptor=rt.RtdlTensorDescriptor(
                    data_ptr=1,
                    device_type="cuda",
                    device_id=0,
                    dtype="float32",
                    shape=(1,),
                ),
                data_ptr=1,
                device_type="cuda",
                device_id=0,
                dtype="float32",
                shape=(1,),
                strides=None,
                byte_offset=0,
                access_mode="read",
                stream_handle=0,
                source_protocol="test",
                direct_device_handoff_authorized=True,
            )


if __name__ == "__main__":
    unittest.main()

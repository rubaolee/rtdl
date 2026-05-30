from __future__ import annotations

import unittest

import rtdsl as rt


class _FakeCuPyColumn:
    __module__ = "cupy.fake"

    dtype = "int64"
    shape = (3,)
    strides = (1,)

    @property
    def __cuda_array_interface__(self):
        return {
            "shape": self.shape,
            "typestr": "<i8",
            "data": (0xCAFE, False),
            "version": 3,
        }

    def __dlpack__(self):
        return object()

    def __dlpack_device__(self):
        return (2, 0)

    def data_ptr(self):
        return 0xCAFE


class _FakeDLPackColumn:
    dtype = "float64"
    shape = (2,)
    strides = (1,)

    @property
    def __cuda_array_interface__(self):
        return {
            "shape": self.shape,
            "typestr": "<f8",
            "data": (0xBEEF, False),
            "version": 3,
        }

    def __dlpack__(self):
        return object()

    def __dlpack_device__(self):
        return (2, 0)


class _FakeCudaArrayColumn:
    @property
    def __cuda_array_interface__(self):
        return {
            "shape": (4,),
            "typestr": "<u4",
            "data": (0x1234, False),
            "version": 3,
        }


class _FakeHostArray:
    @property
    def __array_interface__(self):
        return {
            "shape": (5,),
            "typestr": "<f8",
            "data": (0x5678, False),
            "version": 3,
        }


class Goal2692NeutralBufferSeamLifetimeContractTest(unittest.TestCase):
    def test_contract_is_partner_neutral_and_claim_bounded(self) -> None:
        contract = rt.describe_v2_5_neutral_buffer_seam_contract()

        self.assertEqual(contract["contract_version"], rt.V2_5_NEUTRAL_BUFFER_SEAM_VERSION)
        self.assertEqual(contract["api_maturity"], "experimental_contract_no_native_promotion")
        self.assertIn("registered_partner_adapter", contract["protocol_priority"])
        self.assertIn("dlpack", contract["protocol_priority"])
        self.assertIn("cuda_array_interface", contract["protocol_priority"])
        self.assertTrue(contract["no_partner_forced"])
        self.assertTrue(contract["multi_partner_composition_allowed"])
        self.assertTrue(contract["torch_is_not_the_neutral_protocol"])
        self.assertFalse(contract["native_device_output_promotion_ready"])
        self.assertFalse(contract["true_zero_copy_public_claim_authorized"])
        self.assertFalse(contract["public_speedup_claim_authorized"])

    def test_registered_partner_adapter_wins_over_generic_protocols(self) -> None:
        column = _FakeCuPyColumn()

        self.assertEqual(rt.classify_neutral_buffer_protocol(column), "cupy")
        descriptor = rt.neutral_buffer_descriptor_from_object(
            "group_ids",
            column,
            producer="cupy_union_find",
            consumer="triton_segmented_sum",
        )
        metadata = descriptor.to_metadata()

        self.assertEqual(metadata["buffer"]["source_protocol"], "cupy")
        self.assertEqual(metadata["transfer_status"], "borrowed_device_pointer_unmeasured")
        self.assertEqual(metadata["copy_status"], "borrowed_pointer_unmeasured")
        self.assertTrue(metadata["direct_device_pointer_observed"])
        self.assertFalse(metadata["zero_copy_claim_authorized"])
        self.assertFalse(metadata["native_device_output_promotion_ready"])

    def test_generic_dlpack_precedes_raw_cuda_array_interface(self) -> None:
        column = _FakeDLPackColumn()

        self.assertEqual(rt.classify_neutral_buffer_protocol(column), "dlpack")
        descriptor = rt.neutral_buffer_descriptor_from_object(
            "values",
            column,
            producer="torch_or_other_dlpack",
            consumer="cupy_rawkernel",
        )
        metadata = descriptor.to_metadata()

        self.assertEqual(metadata["buffer"]["source_protocol"], "dlpack")
        self.assertEqual(metadata["buffer"]["device"], "cuda:0")
        self.assertEqual(metadata["buffer"]["dtype"], "float64")
        self.assertFalse(metadata["zero_copy_claim_authorized"])

    def test_cuda_array_interface_fallback_and_host_reference(self) -> None:
        device_descriptor = rt.neutral_buffer_descriptor_from_object(
            "row_ids",
            _FakeCudaArrayColumn(),
            producer="native_optix_future",
            consumer="raw_cuda",
            lifetime_state="producer_retained",
            native_producer=True,
        )
        device_metadata = device_descriptor.to_metadata()
        self.assertEqual(device_metadata["buffer"]["source_protocol"], "cuda_array_interface")
        self.assertEqual(device_metadata["buffer"]["dtype"], "uint32")
        self.assertEqual(device_metadata["transfer_status"], "borrowed_device_pointer_unmeasured")
        self.assertFalse(device_metadata["zero_copy_claim_authorized"])

        host_descriptor = rt.neutral_buffer_descriptor_from_object(
            "host_reference",
            _FakeHostArray(),
            producer="cpu_reference",
            consumer="numpy",
        )
        host_metadata = host_descriptor.to_metadata()
        self.assertEqual(host_metadata["buffer"]["source_protocol"], "array_interface")
        self.assertEqual(host_metadata["transfer_status"], "host_reference")
        self.assertFalse(host_metadata["device_resident"])

    def test_zero_copy_claim_requires_measured_evidence(self) -> None:
        column = _FakeCudaArrayColumn()

        with self.assertRaisesRegex(ValueError, "zero_copy_measured requires"):
            rt.neutral_buffer_descriptor_from_object(
                "row_ids",
                column,
                producer="native_optix_future",
                consumer="cupy",
                transfer_status="zero_copy_measured",
                lifetime_state="producer_retained",
                native_producer=True,
            )

        descriptor = rt.neutral_buffer_descriptor_from_object(
            "row_ids",
            column,
            producer="native_optix_future",
            consumer="cupy",
            transfer_status="zero_copy_measured",
            lifetime_state="producer_retained",
            native_producer=True,
            measured_same_pointer=True,
            measured_no_host_stage=True,
            measured_evidence={"probe": "synthetic_same_pointer_fixture"},
        )
        metadata = descriptor.to_metadata()
        self.assertTrue(metadata["zero_copy_claim_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertFalse(metadata["native_device_output_promotion_ready"])

    def test_lifetime_state_machine_fails_closed(self) -> None:
        plan = rt.neutral_buffer_lifetime_plan(
            producer="native_optix_future",
            consumer="triton",
            state="producer_retained",
        )
        borrowed = plan.transition("partner_borrowed", event="handoff_begin")
        returned = borrowed.transition("producer_retained", event="continuation_complete")

        self.assertEqual(borrowed.state, "partner_borrowed")
        self.assertEqual(returned.state, "producer_retained")
        self.assertFalse(returned.requires_native_state_machine)
        with self.assertRaisesRegex(ValueError, "invalid neutral buffer lifetime transition"):
            rt.validate_neutral_buffer_lifetime_transition(
                "released",
                "partner_borrowed",
                event="handoff_begin",
            )

        pending = rt.neutral_buffer_lifetime_plan(
            producer="native_optix_future",
            consumer="triton",
            state="native_owned_pending_state_machine",
            retain_until="state_machine_defined",
        )
        self.assertTrue(pending.requires_native_state_machine)

    def test_experimental_symbols_are_importable_but_not_star_exports(self) -> None:
        for name in (
            "describe_v2_5_neutral_buffer_seam_contract",
            "neutral_buffer_descriptor_from_object",
            "neutral_buffer_lifetime_plan",
            "validate_neutral_buffer_lifetime_transition",
        ):
            self.assertTrue(hasattr(rt, name))
            self.assertNotIn(name, rt.__all__)


if __name__ == "__main__":
    unittest.main()

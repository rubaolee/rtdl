from __future__ import annotations

import unittest

import rtdsl as rt


class _FakeCudaDevice:
    type = "cuda"
    index = 0


class _FakeCudaInt64Column:
    dtype = "int64"
    shape = (2,)
    device = _FakeCudaDevice()

    def __init__(self, values) -> None:
        self._values = tuple(values)

    @property
    def __cuda_array_interface__(self):
        return {
            "shape": self.shape,
            "typestr": "<i8",
            "data": (0xE000, False),
            "version": 3,
        }

    def data_ptr(self):
        return 0xE000

    def tolist(self):
        return list(self._values)

    def __iter__(self):
        return iter(self._values)


class _FakeCudaFloat64Column:
    dtype = "float64"
    shape = (2,)
    device = _FakeCudaDevice()

    def __init__(self, values) -> None:
        self._values = tuple(values)

    @property
    def __cuda_array_interface__(self):
        return {
            "shape": self.shape,
            "typestr": "<f8",
            "data": (0xF000, False),
            "version": 3,
        }

    def data_ptr(self):
        return 0xF000

    def tolist(self):
        return list(self._values)

    def __iter__(self):
        return iter(self._values)


def _device_hit_columns() -> rt.RtdlHitStreamColumnHandoff:
    return rt.prepare_generic_device_resident_hit_stream_columns(
        ray_ids=_FakeCudaInt64Column((0, 1)),
        primitive_ids=_FakeCudaInt64Column((0, 1)),
        row_count=2,
        capacity=2,
        backend="optix",
    )


def _device_payload_columns() -> rt.RtdlTypedPrimitivePayloadColumns:
    return rt.RtdlTypedPrimitivePayloadColumns(
        primitive_group_ids=_FakeCudaInt64Column((3, 4)),
        primitive_values=_FakeCudaFloat64Column((10.0, 20.0)),
        primitive_count=2,
        group_count=5,
        source_mode="typed_payload_columns",
        group_id_bounds_validation="caller_asserted",
    )


class Goal2700ExplicitHitStreamGatherPartnerTest(unittest.TestCase):
    def test_default_auto_path_remains_python_reference_for_non_torch_columns(self) -> None:
        continuation_inputs, metadata = rt.gather_typed_payload_columns_for_hit_stream(
            _device_hit_columns(),
            _device_payload_columns(),
        )

        self.assertEqual(continuation_inputs["group_ids"], (3, 4))
        self.assertEqual(metadata["requested_gather_partner"], "auto")
        self.assertEqual(metadata["selected_gather_partner"], "python_reference")
        self.assertFalse(metadata["explicit_partner_choice"])
        self.assertEqual(metadata["gather_mode"], "python_reference_columns")

    def test_python_reference_can_be_explicit_for_device_shaped_columns(self) -> None:
        continuation_inputs, metadata = rt.gather_typed_payload_columns_for_hit_stream(
            _device_hit_columns(),
            _device_payload_columns(),
            partner="python_reference",
        )

        self.assertEqual(continuation_inputs["values"], (10.0, 20.0))
        self.assertEqual(metadata["requested_gather_partner"], "python_reference")
        self.assertEqual(metadata["selected_gather_partner"], "python_reference")
        self.assertTrue(metadata["explicit_partner_choice"])
        self.assertFalse(metadata["allow_explicit_copy"])
        self.assertFalse(metadata["true_zero_copy_authorized"])

    def test_triton_gather_fails_closed_without_torch_carrier_or_explicit_copy(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires existing torch tensor carrier"):
            rt.gather_typed_payload_columns_for_hit_stream(
                _device_hit_columns(),
                _device_payload_columns(),
                partner="triton",
            )

    def test_descriptor_only_partners_do_not_execute_gather(self) -> None:
        with self.assertRaisesRegex(ValueError, "descriptor/planning-only"):
            rt.gather_typed_payload_columns_for_hit_stream(
                _device_hit_columns(),
                _device_payload_columns(),
                partner="cupy",
            )
        with self.assertRaisesRegex(ValueError, "descriptor/planning-only"):
            rt.gather_typed_payload_columns_for_hit_stream(
                _device_hit_columns(),
                _device_payload_columns(),
                partner="numba",
            )

    def test_unknown_gather_partner_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported hit-stream gather partner"):
            rt.gather_typed_payload_columns_for_hit_stream(
                _device_hit_columns(),
                _device_payload_columns(),
                partner="mystery_partner",
            )


if __name__ == "__main__":
    unittest.main()

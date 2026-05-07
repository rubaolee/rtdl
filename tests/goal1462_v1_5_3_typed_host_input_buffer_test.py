import ctypes
import unittest

import rtdsl as rt


class Goal1462V153TypedHostInputBufferTest(unittest.TestCase):
    def test_prepare_typed_contiguous_host_input_buffer(self) -> None:
        descriptor = rt.prepare_collect_k_i64_host_input_buffer(
            ((2, 20), (1, 10), (1, 10)),
            row_width=2,
        )
        validated = rt.validate_collect_k_i64_host_input_buffer(descriptor)

        self.assertEqual(validated["status"], "typed_contiguous_host_input_buffer_prepared")
        self.assertEqual(validated["shape"], (3, 2))
        self.assertEqual(validated["flat_value_count"], 6)
        self.assertEqual(validated["copy_boundary"], "typed_contiguous_host_buffer")
        self.assertIs(validated["materialized_nested_python_rows_present"], False)
        self.assertIs(validated["typed_contiguous_host_buffer_path"], True)
        self.assertEqual(
            [validated["ctypes_buffer"][index] for index in range(validated["flat_value_count"])],
            [2, 20, 1, 10, 1, 10],
        )
        self.assertEqual(
            ctypes.addressof(validated["ctypes_buffer"]),
            validated["buffer_address"],
        )

    def test_typed_input_buffer_keeps_public_claims_blocked(self) -> None:
        descriptor = rt.validate_collect_k_i64_host_input_buffer(
            rt.prepare_collect_k_i64_host_input_buffer((1, 2), row_width=1)
        )

        for flag in (
            "true_zero_copy_authorized",
            "public_speedup_wording_authorized",
            "whole_app_speedup_claim_authorized",
            "stable_public_primitive_authorized",
            "release_action_authorized",
        ):
            with self.subTest(flag=flag):
                self.assertIs(descriptor[flag], False)
        self.assertIn("still copies user rows into ctypes host storage", descriptor["claim_boundary"])
        self.assertIn("partner tensor handoff", descriptor["claim_boundary"])

    def test_typed_input_buffer_rejects_bad_width(self) -> None:
        with self.assertRaisesRegex(ValueError, "row width mismatch"):
            rt.prepare_collect_k_i64_host_input_buffer(((1, 2),), row_width=1)

        with self.assertRaisesRegex(ValueError, "row_width must be positive"):
            rt.prepare_collect_k_i64_host_input_buffer(((1, 2),), row_width=0)


if __name__ == "__main__":
    unittest.main()

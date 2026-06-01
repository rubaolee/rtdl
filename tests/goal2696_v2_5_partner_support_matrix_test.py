from __future__ import annotations

import unittest

import rtdsl as rt


class Goal2696V25PartnerSupportMatrixTest(unittest.TestCase):
    def test_matrix_covers_every_partner_operation_cell(self) -> None:
        matrix = rt.v2_5_partner_support_matrix()
        validation = rt.validate_v2_5_partner_support_matrix(matrix)
        expected_count = len(rt.V2_5_ALLOWED_PARTNERS) * len(rt.V2_5_PARTNER_CONTINUATION_OPERATION_NAMES)

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(matrix["cell_count"], expected_count)
        self.assertEqual(len(matrix["cells"]), expected_count)
        self.assertTrue(matrix["no_partner_forced"])
        self.assertTrue(matrix["unsupported_cells_fail_closed"])
        self.assertFalse(matrix["rt_traversal_replacement_allowed"])
        self.assertFalse(matrix["public_speedup_claim_authorized"])
        self.assertFalse(matrix["true_zero_copy_claim_authorized"])
        self.assertEqual(matrix["cupy_preview_operations"], rt.V2_5_CUPY_PREVIEW_OPERATIONS)

    def test_reference_cells_are_universal_and_triton_cells_are_operation_specific(self) -> None:
        for operation in rt.V2_5_PARTNER_CONTINUATION_OPERATION_NAMES:
            reference = rt.plan_v2_5_partner_support(operation, "reference")
            triton = rt.plan_v2_5_partner_support(operation, "triton")

            self.assertEqual(reference["partner"], rt.V2_5_REFERENCE_PARTNER)
            self.assertEqual(reference["status"], rt.V2_5_SUPPORT_STATUS_REFERENCE)
            self.assertTrue(reference["supported"])
            self.assertFalse(reference["requires_neutral_buffer_seam"])

            self.assertEqual(triton["partner"], rt.V2_5_PRIMARY_PARTNER)
            if operation in rt.V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS:
                self.assertEqual(triton["status"], rt.V2_5_SUPPORT_STATUS_PREVIEW)
                self.assertTrue(triton["supported"])
                self.assertTrue(triton["requires_cuda"])
                self.assertTrue(triton["requires_sm70_plus"])
            else:
                self.assertEqual(triton["status"], rt.V2_5_SUPPORT_STATUS_UNSUPPORTED)
                self.assertFalse(triton["supported"])
                self.assertIn("not implemented", triton["notes"])
            self.assertTrue(triton["requires_neutral_buffer_seam"])
            self.assertFalse(triton["promoted_performance_path"])
            self.assertFalse(triton["public_speedup_claim_authorized"])
            self.assertFalse(triton["true_zero_copy_claim_authorized"])

    def test_numba_preview_is_explicitly_narrow_and_other_cells_fail_closed(self) -> None:
        for operation in rt.V2_5_PARTNER_CONTINUATION_OPERATION_NAMES:
            numba = rt.plan_v2_5_partner_support(operation, "numba")
            if operation in rt.V2_5_NUMBA_PREVIEW_OPERATIONS:
                self.assertEqual(numba["status"], rt.V2_5_SUPPORT_STATUS_PREVIEW)
                self.assertTrue(numba["supported"])
                self.assertTrue(numba["requires_cuda"])
            else:
                self.assertEqual(numba["status"], rt.V2_5_SUPPORT_STATUS_UNSUPPORTED)
                self.assertFalse(numba["supported"])
                self.assertIn("not implemented", numba["notes"])

    def test_cupy_conformance_cells_are_descriptor_only_except_explicit_previews(self) -> None:
        for operation in rt.V2_5_PARTNER_CONTINUATION_OPERATION_NAMES:
            cupy = rt.plan_v2_5_partner_support(operation, "cupy")

            self.assertEqual(cupy["partner"], rt.V2_5_CONFORMANCE_PARTNER)
            if operation in rt.V2_5_CUPY_PREVIEW_OPERATIONS:
                self.assertEqual(cupy["status"], rt.V2_5_SUPPORT_STATUS_PREVIEW)
                self.assertIn("preview", cupy["notes"].lower())
            else:
                self.assertEqual(cupy["status"], rt.V2_5_SUPPORT_STATUS_DESCRIPTOR)
            self.assertTrue(cupy["supported"])
            self.assertTrue(cupy["requires_neutral_buffer_seam"])
            self.assertTrue(cupy["requires_cuda"])
            self.assertFalse(cupy["promoted_performance_path"])
            self.assertFalse(cupy["rt_traversal_replacement_allowed"])

    def test_support_matrix_symbols_are_experimental_not_star_exports(self) -> None:
        for name in (
            "v2_5_partner_support_matrix",
            "validate_v2_5_partner_support_matrix",
            "plan_v2_5_partner_support",
        ):
            self.assertTrue(hasattr(rt, name))
            self.assertNotIn(name, rt.__all__)


if __name__ == "__main__":
    unittest.main()

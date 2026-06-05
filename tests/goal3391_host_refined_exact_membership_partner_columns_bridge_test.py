from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3391_host_refined_exact_membership_partner_columns_bridge_2026-06-04.md"


def _cupy_or_skip(test_case):
    try:
        import cupy as cp  # type: ignore
    except Exception as exc:
        test_case.skipTest(f"CuPy is not available: {exc}")
    return cp


def _host_tuple(cp_module, array):
    return tuple(int(value) for value in cp_module.asnumpy(array).tolist())


class Goal3391HostRefinedExactMembershipPartnerColumnsBridgeTest(unittest.TestCase):
    def test_materializes_exact_rows_as_sorted_cupy_columns_with_boundaries(self):
        cp = _cupy_or_skip(self)
        actual = rt.materialize_closed_shape_membership_rows_as_cupy_columns(
            (
                {"point_id": 2, "shape_id": 30, "membership": 1},
                {"point_id": 1, "shape_id": 20, "membership": 1},
                {"point_id": 1, "shape_id": 10, "membership": 1},
            ),
            source_protocol="host_refined_optix_exact_rows",
        )

        self.assertEqual(_host_tuple(cp, actual["point_id"]), (1, 1, 2))
        self.assertEqual(_host_tuple(cp, actual["shape_id"]), (10, 20, 30))
        self.assertEqual(_host_tuple(cp, actual["membership"]), (1, 1, 1))
        self.assertEqual(actual["row_count"], 3)
        self.assertEqual(actual["source_protocol"], "host_refined_optix_exact_rows")
        self.assertEqual(actual["output_residency"], "partner_device_after_host_refine_upload")
        self.assertTrue(actual["host_refined_rows_materialized"])
        self.assertFalse(actual["native_exact_device_row_stream_produced"])
        self.assertFalse(actual["true_zero_copy_claim_authorized"])
        self.assertFalse(actual["release_authorized"])
        self.assertFalse(actual["public_speedup_claim_authorized"])
        self.assertFalse(actual["rt_core_speedup_claim_authorized"])

    def test_accepts_generic_left_right_row_names_and_default_membership(self):
        cp = _cupy_or_skip(self)
        actual = rt.materialize_closed_shape_membership_rows_as_cupy_columns(
            (
                {"left_id": 5, "right_id": 7},
                {"left_id": 4, "right_id": 8},
            ),
            sort_output=False,
        )

        self.assertEqual(_host_tuple(cp, actual["point_id"]), (5, 4))
        self.assertEqual(_host_tuple(cp, actual["shape_id"]), (7, 8))
        self.assertEqual(_host_tuple(cp, actual["membership"]), (1, 1))
        self.assertEqual(actual["source_protocol"], "host_refined_exact_rows")

    def test_report_frames_bridge_not_final_native_primitive(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Host-Refined Exact Membership Partner Columns Bridge", text)
        self.assertIn("native_exact_device_row_stream_produced = false", text)
        self.assertIn("does not authorize release", text)
        self.assertIn("generic exact closed-shape relation stream", text)


if __name__ == "__main__":
    unittest.main()

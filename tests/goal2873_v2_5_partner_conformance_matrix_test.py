from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2873_v2_5_partner_conformance_matrix_2026-05-31.md"


class Goal2873V25PartnerConformanceMatrixTest(unittest.TestCase):
    def test_conformance_matrix_covers_every_support_cell(self) -> None:
        support = rt.v2_5_partner_support_matrix()
        matrix = rt.v2_5_partner_conformance_matrix()
        validation = rt.validate_v2_5_partner_conformance_matrix(matrix)
        expected_count = len(rt.V2_5_ALLOWED_PARTNERS) * len(rt.V2_5_PARTNER_CONTINUATION_OPERATION_NAMES)

        self.assertEqual("accept", validation["status"])
        self.assertEqual(expected_count, matrix["cell_count"])
        self.assertEqual(support["cell_count"], matrix["cell_count"])
        self.assertFalse(matrix["release_conformance_complete"])
        self.assertTrue(matrix["preview_runtime_conformance_complete"])
        self.assertEqual(0, matrix["release_blocker_count"])
        self.assertEqual(0, matrix["runtime_conformance_gap_count"])
        self.assertFalse(matrix["public_speedup_claim_authorized"])
        self.assertFalse(matrix["broad_rt_core_claim_authorized"])
        self.assertFalse(matrix["whole_app_speedup_claim_authorized"])
        self.assertFalse(matrix["true_zero_copy_claim_authorized"])
        self.assertFalse(matrix["triton_preview_auto_selection_authorized"])

    def test_high_risk_triton_tie_break_rows_point_to_goal2872(self) -> None:
        for operation in ("grouped_argmin_f64", "grouped_argmax_f64", "grouped_topk_f64"):
            cell = rt.plan_v2_5_partner_conformance(operation, "triton")

            self.assertEqual(rt.V2_5_CONFORMANCE_STATUS_POD_RUNTIME, cell["conformance_status"])
            self.assertEqual("Goal2872", cell["evidence_goal"])
            self.assertIn("tests.goal2872_triton_tie_break_conformance_smoke_test", cell["test_modules"])
            self.assertFalse(cell["release_blocker"])

    def test_numba_preview_rows_now_point_to_goal2875_pod_runtime_evidence(self) -> None:
        for operation in ("segmented_count_i64", "segmented_sum_f64"):
            cell = rt.plan_v2_5_partner_conformance(operation, "numba")

            self.assertEqual(rt.V2_5_SUPPORT_STATUS_PREVIEW, cell["support_status"])
            self.assertEqual(rt.V2_5_CONFORMANCE_STATUS_POD_RUNTIME, cell["conformance_status"])
            self.assertEqual("Goal2875", cell["evidence_goal"])
            self.assertFalse(cell["release_blocker"])
            self.assertFalse(cell["public_speedup_claim_authorized"])

    def test_cupy_conformance_is_descriptor_only_except_hit_stream_preview(self) -> None:
        for operation in rt.V2_5_PARTNER_CONTINUATION_OPERATION_NAMES:
            cell = rt.plan_v2_5_partner_conformance(operation, "cupy")
            if operation == "hit_stream_grouped_ray_id_primitive_i64":
                self.assertEqual(rt.V2_5_CONFORMANCE_STATUS_POD_RUNTIME, cell["conformance_status"])
                self.assertEqual("Goal2771/Goal2772", cell["evidence_goal"])
                self.assertIn(
                    "tests.goal2772_hit_stream_event_ordered_grouped_richer_reductions_test",
                    cell["test_modules"],
                )
            else:
                self.assertEqual(rt.V2_5_SUPPORT_STATUS_DESCRIPTOR, cell["support_status"])
                self.assertEqual(rt.V2_5_CONFORMANCE_STATUS_DESCRIPTOR, cell["conformance_status"])
                self.assertFalse(cell["release_blocker"])

    def test_readiness_packet_indexes_goal2873_and_core_validation(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        path = "docs/reports/goal2873_v2_5_partner_conformance_matrix_2026-05-31.md"

        self.assertEqual("accept", validation["status"])
        self.assertTrue(packet["required_report_presence"][path])
        self.assertEqual("accept", packet["core_validations"]["partner_conformance_matrix"]["status"])

    def test_report_records_review_feedback_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2873",
            "partner x operation",
            "Goal2872",
            "Numba",
            "CuPy",
            "not a v2.5 release authorization",
            "not a public speedup claim",
        ):
            self.assertIn(phrase, text)

    def test_matrix_symbols_are_experimental_not_star_exports(self) -> None:
        for name in (
            "v2_5_partner_conformance_matrix",
            "validate_v2_5_partner_conformance_matrix",
            "plan_v2_5_partner_conformance",
        ):
            self.assertTrue(hasattr(rt, name))
            self.assertNotIn(name, rt.__all__)


if __name__ == "__main__":
    unittest.main()
